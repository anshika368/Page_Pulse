# Page Pulse

A production-grade, fault-tolerant URL audit tool with a warm, 90s retro-vintage interface.

- **Frontend**: Next.js 15 (App Router), TypeScript strict mode, Tailwind CSS.
- **Backend**: FastAPI, Pydantic v2, `httpx`, BeautifulSoup4.
- **Testing**: `pytest`, `pytest-mock`, `pytest-asyncio` with fully mocked external HTTP calls.

## What It Does

Page Pulse audits any public URL and returns a structured report covering:

- HTTP status code and response time
- SSL certificate validity and expiration
- SEO meta tags (title, description, canonical, Open Graph, Twitter Card, favicon, robots)
- Heading structure (H1–H6)
- Internal and external link counts
- Image alt-text coverage
- Approximate page word count and page weight
- Composite quality score and actionable issue list

The design goal is **defensibility**: every edge case is handled gracefully so the service and the UI never crash on bad input, slow hosts, or malformed responses.

---

## Setup Instructions

### 1. Backend (FastAPI)

```bash
cd backend
python -m pip install -r test-requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

### 2. Frontend (Next.js)

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

### 3. Run the Test Suite

```bash
cd backend
python -m pytest tests/ -v
```

All external HTTP calls are mocked, so the suite runs offline and completes in under a second.

---

## API Contract

### Canonical Endpoint

```
POST /api/audit
```

`/audit` is kept as a backward-compatible alias, but `/api/audit` is the documented contract for new integrations.

### Request

```http
POST /api/audit
Content-Type: application/json
Accept: application/json

{
  "url": "https://example.com"
}
```

### Success Response — `200 OK`

```json
{
  "url": "https://example.com",
  "final_url": "https://example.com/",
  "timestamp": "2026-07-25T09:07:43.575752Z",
  "status": "ok",
  "status_code": 200,
  "http_status": 200,
  "response_time_ms": 492.11,
  "page_title": "Example Domain",
  "meta_description": null,
  "h1_count": 1,
  "images_missing_alt_text": 0,
  "approximate_word_count": 18,
  "ssl": {
    "valid": true,
    "expires_in_days": 35,
    "issuer": "US SSL Corporation Cloudflare TLS Issuing ECC CA 3"
  },
  "seo": {
    "title": "Example Domain",
    "description": null,
    "title_length": 14,
    "description_length": 0,
    "has_canonical": false,
    "has_open_graph": false,
    "has_twitter_card": false,
    "has_favicon": true,
    "robots_meta": null
  },
  "headings": {
    "h1": 1,
    "h2": 0,
    "h3": 0,
    "h4": 0,
    "h5": 0,
    "h6": 0
  },
  "links": {
    "internal": 0,
    "external": 1,
    "total": 1
  },
  "images": {
    "total": 0,
    "without_alt": 0
  },
  "performance": {
    "page_size_kb": 0.55,
    "approximate_word_count": 18
  },
  "score": 90,
  "issues": [
    "Title length is 14 chars (ideal: 30–60).",
    "Missing meta description.",
    "Missing canonical link tag."
  ],
  "raw_headers": {}
}
```

### Error Responses

All error responses use the same JSON shape:

```json
{
  "detail": "Human-readable explanation",
  "status": "error | timeout | unreachable"
}
```

| Status | Scenario | Example Trigger |
|--------|----------|-----------------|
| `400 Bad Request` | Invalid or malformed URL | `"url": "not-a-valid-url"` |
| `408 Request Timeout` | Upstream server did not respond in time | Simulated slow host |
| `422 Unprocessable Entity` | Response is not HTML (e.g., PDF) | `Content-Type: application/pdf` |
| `503 Service Unavailable` | DNS failure or unreachable host | Non-existent domain |
| `500 Internal Server Error` | Unexpected server failure | Covered by a catch-all handler |

---

## Design Decisions & Reasoning

### Decision 1: Choosing FastAPI for the Backend

I chose **FastAPI** because the core workload is **highly concurrent external network I/O**: DNS lookups, TLS handshakes, HTTP fetches, and HTML parsing. FastAPI’s native `async`/`await` support lets the server hold many in-flight audit requests without blocking threads, which keeps memory usage low and response times predictable under load.

Combined with Pydantic v2 for strict request validation, FastAPI rejects malformed input before any network call is attempted. This is a deliberate reliability win: bad URLs are caught at the edge, so the parser never wastes cycles or crashes on garbage input. For a tool meant to be useful at scale — and one that will inevitably be pointed at broken, slow, or hostile URLs — this concurrency + validation pairing is the right foundation.

### Decision 2: Strict Decoupling and Client-Side Resilience

The frontend and backend are intentionally **loosely coupled through a narrow, well-typed API contract**. The Next.js client wraps every request in a custom `AuditFetchError` and renders a dedicated `ErrorDisplay` component whenever the backend returns a non-2xx response. This means:

- If the parser hits a timeout, the UI shows a friendly message, not a stack trace.
- If the user pastes a malformed URL, the input is validated both client-side and server-side.
- If the backend goes down, the page itself does not crash; the user sees a clean error card and can retry.

This defensibility matters because the tool is built for **tech-for-good**: it should work reliably for users regardless of what URL they paste in. A brittle UI that breaks on edge cases would undermine trust in the product.

### Decision 3: The 90s Retro Aesthetic UI

Enterprise tools do not have to be sterile. The 90s retro-vintage aesthetic — warm cream and amber tones, a subtle film-grain overlay, serif headings paired with monospace data readouts — was chosen to make Page Pulse **memorable, human, and engaging** in a sea of identical gray dashboards.

The visual design is also functional: high-contrast cards, clear typography hierarchy, and a restrained color palette keep the report readable. The goal was to prove that accessibility and personality can coexist. A tool that feels crafted invites users to trust it and return to it.

---

## Testing Philosophy

The `backend/tests/` directory contains a `pytest` suite that is **fully deterministic**.

- `FakeHttpxResponse` and `FakeAsyncClient` replace `httpx.AsyncClient` via `pytest-mock`.
- External HTTP calls, TLS handshakes, and slow responses are simulated without touching the internet.
- Tests cover the happy path, invalid URLs, unreachable hosts, timeouts, non-HTML responses, and empty HTML documents.

Run the suite with:

```bash
cd backend
python -m pytest tests/ -v
```

---

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI app, routes, exception handlers
│   ├── models.py            # Pydantic request/response models
│   ├── audit_service.py     # Core audit logic and scoring
│   ├── tests/               # pytest suite with mocked HTTP
│   ├── requirements.txt     # Runtime dependencies
│   ├── test-requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── src/app/             # Next.js App Router pages, layout, styles
│   ├── src/components/      # UI components (form, report, loading, error, footer)
│   ├── src/lib/             # API client and utilities
│   ├── src/types/           # TypeScript types
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.ts
└── README.md
```

---

## Environment Variables

Create `frontend/.env.local` if your backend is not on the default origin:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

---

## AI Collaboration Note

In the spirit of transparency and modern development workflows, AI tools were utilized to accelerate the generation of boilerplate test setups and to refine the Markdown formatting in this documentation. However, the architectural decisions, the strict fault-tolerance logic, and the UI design direction are entirely my own.
