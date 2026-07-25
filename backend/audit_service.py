from __future__ import annotations

import asyncio
import re
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from models import (
    AuditReport,
    AuditStatus,
    Headings,
    Images,
    Links,
    Performance,
    SeoMeta,
    SslInfo,
)

DEFAULT_TIMEOUT = 15.0
MAX_BODY_BYTES = 2 * 1024 * 1024  # 2 MB


@dataclass(frozen=True)
class AuditOptions:
    timeout_seconds: float = DEFAULT_TIMEOUT
    follow_redirects: bool = True


class AuditError(Exception):
    def __init__(self, message: str, status: AuditStatus, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.status_code = status_code


def _hostname(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc or parsed.path or url


def _is_internal_link(href: str, base_netloc: str) -> bool:
    parsed = urlparse(href)
    return not parsed.netloc or parsed.netloc.lower() == base_netloc.lower()


def _extract_ssl_info(url: str) -> SslInfo:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return SslInfo(valid=False)

    hostname = parsed.hostname
    port = parsed.port or 443
    ctx = ssl.create_default_context()
    try:
        with ctx.wrap_socket(
            ssl.socket(),
            server_hostname=hostname,
        ) as sock:
            sock.settimeout(5)
            sock.connect((hostname, port))
            cert = sock.getpeercert()

        not_after_str = cert.get("notAfter")
        issuer_components = cert.get("issuer", ())
        issuer = " ".join(item[0][1] for item in issuer_components if item)

        expires_in_days: int | None = None
        if not_after_str:
            not_after = ssl.cert_time_to_seconds(not_after_str)
            expires_in_days = max(
                0,
                int(
                    (datetime.fromtimestamp(not_after, tz=timezone.utc) - datetime.now(timezone.utc)).total_seconds()
                    // 86400
                ),
            )

        return SslInfo(valid=True, expires_in_days=expires_in_days, issuer=issuer or None)
    except Exception:
        return SslInfo(valid=False)


def _parse_html(body: str, final_url: str, headers: dict[str, Any]) -> dict[str, Any]:
    soup = BeautifulSoup(body, "html.parser")
    parsed_base = urlparse(final_url)
    base_netloc = parsed_base.netloc

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    meta_desc = soup.find("meta", attrs={"name": "description"})
    description = meta_desc.get("content", "") if meta_desc else None

    canonical = soup.find("link", attrs={"rel": "canonical"})
    robots = soup.find("meta", attrs={"name": "robots"})

    og_tags = soup.find_all("meta", property=re.compile(r"^og:"))
    twitter_tags = soup.find_all("meta", attrs={"name": re.compile(r"^twitter:")})
    favicon = soup.find("link", attrs={"rel": re.compile(r"icon", re.I)})

    headings: dict[str, int] = {f"h{i}": 0 for i in range(1, 7)}
    for level in range(1, 7):
        headings[f"h{level}"] = len(soup.find_all(f"h{level}"))

    links_internal = 0
    links_external = 0
    for a in soup.find_all("a", href=True):
        absolute = urljoin(final_url, a["href"])
        if _is_internal_link(absolute, base_netloc):
            links_internal += 1
        else:
            links_external += 1

    images_total = 0
    images_without_alt = 0
    for img in soup.find_all("img"):
        images_total += 1
        if not img.get("alt"):
            images_without_alt += 1

    page_size_kb = round(len(body.encode("utf-8")) / 1024, 2)

    # Approximate visible word count by stripping tags and counting whitespace-separated tokens.
    visible_text = soup.get_text(separator=" ", strip=True)
    approximate_word_count = len([w for w in visible_text.split() if w.strip()])

    seo = SeoMeta(
        title=title,
        description=description,
        title_length=len(title) if title else 0,
        description_length=len(description) if description else 0,
        has_canonical=bool(canonical and canonical.get("href")),
        has_open_graph=bool(og_tags),
        has_twitter_card=bool(twitter_tags),
        has_favicon=bool(favicon),
        robots_meta=robots.get("content") if robots else None,
    )

    return {
        "seo": seo,
        "headings": Headings(**headings),
        "links": Links(
            internal=links_internal,
            external=links_external,
            total=links_internal + links_external,
        ),
        "images": Images(total=images_total, without_alt=images_without_alt),
        "approximate_word_count": approximate_word_count,
        "performance": Performance(
            page_size_kb=page_size_kb,
            approximate_word_count=approximate_word_count,
        ),
    }


def _compute_score(report: AuditReport) -> int:
    score = 50
    seo = report.seo

    if seo.title and 30 <= seo.title_length <= 60:
        score += 10
    elif seo.title:
        score += 5

    if seo.description and 50 <= seo.description_length <= 160:
        score += 10
    elif seo.description:
        score += 5

    if seo.has_canonical:
        score += 5
    if seo.has_open_graph:
        score += 5
    if seo.has_favicon:
        score += 5

    if report.headings.h1 == 1:
        score += 5
    if report.headings.h2 > 0:
        score += 5

    if report.images.total == 0 or report.images.without_alt == 0:
        score += 5
    else:
        score += max(0, 5 - report.images.without_alt)

    if report.status_code and report.status_code < 400:
        score += 5

    if report.ssl.valid:
        score += 10

    if report.performance.page_size_kb and report.performance.page_size_kb < 1500:
        score += 5

    return max(0, min(100, score))


def _collect_issues(report: AuditReport) -> list[str]:
    issues: list[str] = []
    seo = report.seo

    if not seo.title:
        issues.append("Missing <title> tag.")
    elif seo.title_length < 30 or seo.title_length > 60:
        issues.append(f"Title length is {seo.title_length} chars (ideal: 30–60).")

    if not seo.description:
        issues.append("Missing meta description.")
    elif seo.description_length < 50 or seo.description_length > 160:
        issues.append(f"Meta description length is {seo.description_length} chars (ideal: 50–160).")

    if report.headings.h1 == 0:
        issues.append("No H1 heading found.")
    elif report.headings.h1 > 1:
        issues.append(f"Multiple H1 headings found ({report.headings.h1}).")

    if report.images.without_alt > 0:
        issues.append(f"{report.images.without_alt} image(s) missing alt text.")

    if not seo.has_canonical:
        issues.append("Missing canonical link tag.")

    if not report.ssl.valid and report.url.startswith("https://"):
        issues.append("SSL certificate appears invalid or could not be verified.")

    return issues


async def run_audit(url: str, options: AuditOptions | None = None) -> AuditReport:
    options = options or AuditOptions()
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.hostname:
        raise AuditError("Invalid URL format.", AuditStatus.ERROR, 400)

    report = AuditReport(url=url)

    try:
        async with httpx.AsyncClient(
            timeout=options.timeout_seconds,
            follow_redirects=options.follow_redirects,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "User-Agent": "PagePulseBot/1.0 (+https://digitalheroesco.com)",
            },
            max_redirects=5,
        ) as client:
            start = asyncio.get_event_loop().time()
            response = await client.get(url)
            elapsed = asyncio.get_event_loop().time() - start
    except httpx.TimeoutException:
        raise AuditError("The request timed out.", AuditStatus.TIMEOUT, 408)
    except httpx.NetworkError:
        raise AuditError("Could not reach the host. Check the URL and try again.", AuditStatus.UNREACHABLE, 503)
    except httpx.InvalidURL:
        raise AuditError("Invalid URL.", AuditStatus.ERROR, 400)
    except Exception as exc:
        raise AuditError(f"Unexpected error: {str(exc)}", AuditStatus.ERROR, 500)

    report.status_code = response.status_code
    report.http_status = response.status_code
    report.response_time_ms = round(elapsed * 1000, 2)
    report.final_url = str(response.url)
    report.raw_headers = dict(response.headers)

    if response.status_code >= 400:
        report.status = AuditStatus.ERROR
        report.issues.append(f"HTTP status code {response.status_code} returned.")

    body = response.text[:MAX_BODY_BYTES]
    content_type = response.headers.get("content-type", "").lower()

    if "text/html" not in content_type:
        # The audit engine is a web-page parser. Non-HTML payloads (PDFs,
        # images, JSON) are treated as a client-level error so we fail fast
        # and never feed garbage into the HTML parser.
        raise AuditError(
            "Response is not HTML. Page Pulse can only audit HTML pages.",
            AuditStatus.ERROR,
            422,
        )

    parsed_data = _parse_html(body, report.final_url or url, dict(response.headers))
    report.seo = parsed_data["seo"]
    report.headings = parsed_data["headings"]
    report.links = parsed_data["links"]
    report.images = parsed_data["images"]
    report.performance = parsed_data["performance"]

    # Populate required flat fields for easy consumption by the frontend and tests.
    report.page_title = parsed_data["seo"].title
    report.meta_description = parsed_data["seo"].description
    report.h1_count = parsed_data["headings"].h1
    report.images_missing_alt_text = parsed_data["images"].without_alt
    report.approximate_word_count = parsed_data["approximate_word_count"]

    report.ssl = _extract_ssl_info(report.final_url or url)
    report.score = _compute_score(report)
    report.issues = _collect_issues(report)
    if not report.issues and response.status_code < 400:
        report.issues.append("Looking good — no major issues detected.")

    return report
