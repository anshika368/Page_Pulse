from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
import re

from pydantic import BaseModel, Field, field_validator


_URL_HOST_PATTERN = re.compile(
    r"^(?:https?://)?(?:[\w-]+(?::[\w-]+)?@)?([\w.-]+)(?::\d{1,5})?(?:/.*)?$",
    re.IGNORECASE,
)


class AuditRequest(BaseModel):
    url: str = Field(..., min_length=1, description="The URL to audit.")

    @field_validator("url")
    @classmethod
    def normalize_url(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith(("http://", "https://")):
            value = f"https://{value}"

        match = _URL_HOST_PATTERN.match(value)
        if not match:
            raise ValueError("Invalid URL format.")

        hostname = match.group(1)
        if not hostname or "." not in hostname or hostname.endswith("."):
            raise ValueError("Invalid URL format.")

        return value


class Headings(BaseModel):
    h1: int = 0
    h2: int = 0
    h3: int = 0
    h4: int = 0
    h5: int = 0
    h6: int = 0


class SeoMeta(BaseModel):
    title: str | None = None
    description: str | None = None
    title_length: int = 0
    description_length: int = 0
    has_canonical: bool = False
    has_open_graph: bool = False
    has_twitter_card: bool = False
    has_favicon: bool = False
    robots_meta: str | None = None


class Links(BaseModel):
    internal: int = 0
    external: int = 0
    total: int = 0


class Images(BaseModel):
    total: int = 0
    without_alt: int = 0


class Performance(BaseModel):
    page_size_kb: float | None = None
    approximate_word_count: int | None = None


class SslInfo(BaseModel):
    valid: bool = False
    expires_in_days: int | None = None
    issuer: str | None = None


class AuditStatus(str, Enum):
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    UNREACHABLE = "unreachable"


class AuditReport(BaseModel):
    url: str
    final_url: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: AuditStatus = AuditStatus.OK
    status_code: int | None = None
    response_time_ms: float | None = None

    # ── Required flat fields per spec ──
    http_status: int = 0
    page_title: str | None = None
    meta_description: str | None = None
    h1_count: int = 0
    images_missing_alt_text: int = 0
    approximate_word_count: int = 0

    ssl: SslInfo = Field(default_factory=SslInfo)
    seo: SeoMeta = Field(default_factory=SeoMeta)
    headings: Headings = Field(default_factory=Headings)
    links: Links = Field(default_factory=Links)
    images: Images = Field(default_factory=Images)
    performance: Performance = Field(default_factory=Performance)
    score: int = 0
    issues: list[str] = Field(default_factory=list)
    raw_headers: dict[str, Any] = Field(default_factory=dict)

    @field_validator("score")
    @classmethod
    def clamp_score(cls, value: int) -> int:
        return max(0, min(100, value))
