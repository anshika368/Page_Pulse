from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from audit_service import AuditError, run_audit
from models import AuditRequest, AuditReport, AuditStatus


# -----------------------------------------------------------------------------
# Note on route naming
# -----------------------------------------------------------------------------
# The canonical audit endpoint is /api/audit. We keep /audit as a backward-
# compatible alias so existing clients continue to work, but /api/audit is the
# documented contract and should be used for new integrations.
# -----------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Page Pulse Audit API",
    description="Production-grade URL audit service.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AuditError)
async def audit_error_handler(request: Request, exc: AuditError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "status": exc.status.value,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    message = "Invalid request."
    for error in exc.errors():
        if error.get("loc") == ("body", "url"):
            message = "Invalid URL. Please enter a valid website address."
            break
    return JSONResponse(
        status_code=400,
        content={
            "detail": message,
            "status": AuditStatus.ERROR.value,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected server error occurred.",
            "status": "error",
        },
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "page-pulse-audit"}


@app.post("/api/audit", response_model=AuditReport)
@app.post("/audit", response_model=AuditReport)
async def audit(payload: AuditRequest) -> AuditReport:
    return await run_audit(payload.url)
