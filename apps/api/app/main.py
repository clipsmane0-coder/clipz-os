import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestIDMiddleware
from app.api.v1.routes import router
from app.auth.routes import router as auth_router
from app.routers.deploy import router as deploy_router

setup_logging(settings.log_level)
logger = logging.getLogger("clipz")

app = FastAPI(
    title="CLIPZ API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID middleware
app.add_middleware(RequestIDMiddleware)

# API routes
app.include_router(router)

# Auth routes
app.include_router(auth_router)

# Deployment dashboard
app.include_router(deploy_router)


@app.on_event("startup")
async def run_migrations():
    """Run Alembic migrations on startup."""
    import os
    import subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = "/app"
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd="/app",
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        logger.info(f"Migrations: exit={result.returncode}")
        if result.stdout:
            logger.info(f"Migration stdout: {result.stdout.strip()}")
        if result.stderr:
            logger.warning(f"Migration stderr: {result.stderr.strip()}")
    except Exception as e:
        logger.warning(f"Migration skipped: {e}")


# HTTPException handler — preserves structured error envelope
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # If the detail is already our structured error format, pass it through
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    # Otherwise wrap into structured format
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
                "details": {},
                "retryable": False,
            },
            "meta": {"request_id": getattr(request.state, "request_id", "unknown")},
        },
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return await http_exception_handler(request, exc)
    logger.error(f"Unhandled exception: {exc}", exc_info=True,
                 extra={"request_id": getattr(request.state, "request_id", "unknown")})
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "details": {},
                "retryable": False,
            },
            "meta": {"request_id": getattr(request.state, "request_id", "unknown")},
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.api_host, port=settings.api_port, reload=True)