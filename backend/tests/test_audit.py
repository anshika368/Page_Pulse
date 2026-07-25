"""
Production-grade pytest suite for the Page Pulse audit parser.

All external HTTP traffic is mocked via `pytest-mock` so the suite is:
- Deterministic
- Fast
- Safe to run in CI without internet access
- Free from flaky live-network dependencies
"""

from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

# Import the fake helpers from conftest by name for type clarity.
from tests.conftest import FakeAsyncClient, FakeHttpxResponse


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def _html_page(
    title: str = "Example Domain",
    description: str = "A short description for testing.",
    h1_text: str = "Welcome",
    body_text: str = "This is a sample paragraph used to verify word counting.",
    images: list[tuple[str, str | None]] | None = None,
) -> str:
    """Build a minimal, deterministic HTML document for parser tests."""
    images = images or []
    img_tags = "\n".join(
        f'  <img src="{src}" alt="{alt or ""}" />' for src, alt in images
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <link rel="canonical" href="https://example.com/" />
  <link rel="icon" href="/favicon.ico" />
  <meta property="og:title" content="{title}" />
  <meta name="twitter:card" content="summary" />
</head>
<body>
  <h1>{h1_text}</h1>
  <p>{body_text}</p>
  <a href="/internal">Internal</a>
  <a href="https://external.com">External</a>
{img_tags}
</body>
</html>
"""


# -----------------------------------------------------------------------------
# Happy Path
# -----------------------------------------------------------------------------


def test_audit_valid_url_returns_expected_fields(client: TestClient, mocker):
    """
    A valid, well-formed HTML page should produce a complete audit report
    with correct types for every requested field.
    """
    html = _html_page(
        title="Page Pulse Test",
        description="Testing the parser with a controlled HTML document.",
        h1_text="Hello Page Pulse",
        body_text="One two three four five six seven eight nine ten.",
        images=[("/a.jpg", "A photo"), ("/b.jpg", None), ("/c.jpg", None)],
    )
    response = FakeHttpxResponse(
        status_code=200,
        text=html,
        headers={"content-type": "text/html; charset=utf-8"},
        url="https://example.com/",
    )

    # Patch httpx.AsyncClient so it behaves like our fake client.
    mocker.patch("httpx.AsyncClient", return_value=FakeAsyncClient(response))
    # Patch SSL extraction to avoid real TLS handshake during unit tests.
    mocker.patch("audit_service._extract_ssl_info", return_value=mocker.MagicMock(valid=True, expires_in_days=42, issuer="Mock CA"))

    resp = client.post("/api/audit", json={"url": "https://example.com"})

    assert resp.status_code == 200
    data = resp.json()

    # Core flat fields requested in Task B.
    assert data["http_status"] == 200
    assert isinstance(data["response_time_ms"], float)
    assert data["response_time_ms"] >= 0
    assert data["page_title"] == "Page Pulse Test"
    assert data["meta_description"] == "Testing the parser with a controlled HTML document."
    assert data["h1_count"] == 1
    assert data["images_missing_alt_text"] == 2
    assert data["approximate_word_count"] >= 11  # title + h1 + paragraph words plus link labels

    # Structured sub-models should also be populated.
    assert data["seo"]["title"] == "Page Pulse Test"
    assert data["seo"]["description"] == "Testing the parser with a controlled HTML document."
    assert data["seo"]["has_canonical"] is True
    assert data["seo"]["has_favicon"] is True
    assert data["headings"]["h1"] == 1
    assert data["images"]["total"] == 3
    assert data["images"]["without_alt"] == 2
    assert data["links"]["internal"] == 1
    assert data["links"]["external"] == 1
    assert data["links"]["total"] == 2
    assert data["performance"]["page_size_kb"] > 0
    assert data["performance"]["approximate_word_count"] >= 11
    assert data["ssl"]["valid"] is True
    assert 0 <= data["score"] <= 100


def test_audit_non_html_response(client: TestClient, mocker):
    """
    If the upstream server returns a non-HTML payload (e.g., PDF), the parser
    should not crash. It should return a partial report and a clear issue.
    """
    response = FakeHttpxResponse(
        status_code=200,
        text="%PDF-1.4 fake pdf content",
        headers={"content-type": "application/pdf"},
        url="https://example.com/report.pdf",
    )
    mocker.patch("httpx.AsyncClient", return_value=FakeAsyncClient(response))
    mocker.patch("audit_service._extract_ssl_info", return_value=mocker.MagicMock(valid=False, expires_in_days=None, issuer=None))

    resp = client.post("/api/audit", json={"url": "https://example.com/report.pdf"})

    # Non-HTML is treated as a client error: the parser cannot audit it.
    assert resp.status_code == 422
    body = resp.json()
    assert body["status"] == "error"
    assert "html" in body["detail"].lower()


# -----------------------------------------------------------------------------
# Failure Cases
# -----------------------------------------------------------------------------


def test_audit_invalid_url_returns_400(client: TestClient):
    """
    A malformed URL must be rejected by Pydantic validation before any network
    call is attempted, returning a structured 400 Bad Request.
    """
    resp = client.post("/api/audit", json={"url": "not-a-valid-url"})

    assert resp.status_code == 400
    body = resp.json()
    assert body["status"] == "error"
    assert "detail" in body
    assert isinstance(body["detail"], str)


def test_audit_unreachable_host_returns_503(client: TestClient, mocker):
    """
    A domain that cannot be resolved or reached should produce a graceful 503
    with a structured JSON error message, not a stack trace.
    """
    mocker.patch(
        "httpx.AsyncClient",
        return_value=FakeAsyncClient(httpx.NetworkError("Cannot reach host")),
    )

    resp = client.post("/api/audit", json={"url": "https://this-domain-does-not-exist-12345.invalid"})

    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "unreachable"
    assert "detail" in body
    assert isinstance(body["detail"], str)


def test_audit_timeout_returns_408(client: TestClient, mocker):
    """
    A slow upstream host that exceeds the configured timeout must return a 408
    Request Timeout. The parser should abort cleanly without hanging or crashing.
    """
    mocker.patch(
        "httpx.AsyncClient",
        return_value=FakeAsyncClient(httpx.TimeoutException("Request took too long")),
    )

    resp = client.post("/api/audit", json={"url": "https://slow.example.com"})

    assert resp.status_code == 408
    body = resp.json()
    assert body["status"] == "timeout"
    assert "detail" in body


# -----------------------------------------------------------------------------
# Edge Cases
# -----------------------------------------------------------------------------


def test_audit_missing_url_field_returns_400(client: TestClient):
    """
    Omitting the required `url` field is treated as an invalid request. Our
    custom validation handler returns a structured 400 Bad Request so the UI
    can surface a friendly message instead of a raw 422 schema error.
    """
    resp = client.post("/api/audit", json={})

    assert resp.status_code == 400
    body = resp.json()
    assert body["status"] == "error"
    assert "detail" in body


def test_audit_empty_page_still_returns_report(client: TestClient, mocker):
    """
    Even a completely empty HTML document should not crash; the parser should
    return a report with zeroed fields and a low score.
    """
    response = FakeHttpxResponse(
        status_code=200,
        text="",
        headers={"content-type": "text/html; charset=utf-8"},
        url="https://empty.example.com",
    )
    mocker.patch("httpx.AsyncClient", return_value=FakeAsyncClient(response))
    mocker.patch("audit_service._extract_ssl_info", return_value=mocker.MagicMock(valid=False, expires_in_days=None, issuer=None))

    resp = client.post("/api/audit", json={"url": "https://empty.example.com"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["page_title"] is None
    assert data["meta_description"] is None
    assert data["h1_count"] == 0
    assert data["approximate_word_count"] == 0
