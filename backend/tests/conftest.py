"""
Shared pytest fixtures for the Page Pulse backend test suite.

These fixtures provide deterministic mock responses so the suite never relies
on live external HTTP calls. This keeps CI fast, stable, and offline-capable.
"""

from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    """Return a FastAPI TestClient wired to the Page Pulse app."""
    return TestClient(app)


class FakeHttpxResponse:
    """
    A minimal stand-in for httpx.Response used by the mock AsyncClient.

    Only the attributes accessed by `audit_service.run_audit` are implemented,
    which keeps the mock small and focused.
    """

    def __init__(
        self,
        status_code: int = 200,
        text: str = "",
        headers: dict[str, str] | None = None,
        url: str = "https://example.com",
    ) -> None:
        self.status_code = status_code
        self.text = text
        self.headers = httpx.Headers(headers or {"content-type": "text/html; charset=utf-8"})
        self.url = url


class FakeAsyncClient:
    """
    Async context-manager replacement for httpx.AsyncClient.

    `__aenter__` returns `self` so callers can do `async with client: ...` and
    then call `client.get(url)` exactly like the real httpx API.
    """

    def __init__(self, response: FakeHttpxResponse | Exception, delay: float = 0.0) -> None:
        self._response = response
        self._delay = delay

    async def __aenter__(self) -> "FakeAsyncClient":
        if self._delay:
            import asyncio

            await asyncio.sleep(self._delay)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def get(self, url: str, **kwargs) -> FakeHttpxResponse:
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


@pytest.fixture
def fake_client_factory():
    """Return a callable that builds a FakeAsyncClient for any response."""

    def _make(response: FakeHttpxResponse | Exception, delay: float = 0.0):
        return FakeAsyncClient(response, delay)

    return _make
