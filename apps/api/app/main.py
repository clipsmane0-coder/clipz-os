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
from app.arbsense.routes import router as arbsense_router
from app.models import *  # noqa: F401, F403 — ensure all models are loaded for create_all

setup_logging(settings.log_level)
logger = logging.getLogger("clipz")

app = FastAPI(
    title="CLIPZ API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
# Allow all origins — public read-only endpoints (curated list, browse search)
# are accessible from any frontend domain. Auth'd endpoints are protected
# by their own token checks regardless of origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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

# ArbSense eBay arbitrage engine
app.include_router(arbsense_router, prefix="/api/v1")


@app.on_event("startup")
async def create_database_if_not_exists():
    """Ensure the target database exists before the engine connects to it."""
    raw_url = settings.database_url
    if raw_url.startswith("postgresql"):
        try:
            # Replace database name with 'postgres' (always exists) to create target DB
            import asyncpg
            pg_url = raw_url.replace("+asyncpg", "")
            pg_url = pg_url.rsplit("/", 1)[0] + "/postgres"
            conn = await asyncpg.connect(pg_url, ssl=False)
            target_db = raw_url.rsplit("/", 1)[-1].split("?")[0].strip()
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", target_db
            )
            if not exists:
                await conn.execute(f'CREATE DATABASE "{target_db}"')
                logger.info(f"Created database '{target_db}'")
            else:
                logger.info(f"Database '{target_db}' already exists")
            await conn.close()
        except Exception as e:
            logger.warning(f"Database creation check failed: {e}")


@app.on_event("startup")
async def run_migrations():
    """Run Alembic migrations on startup. Falls back to create_all()."""
    import os
    import subprocess
    from app.db.session import engine, Base

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
            logger.info(f"Migration: {result.stdout.strip()}")
        if result.stderr:
            logger.warning(f"Migration: {result.stderr.strip()}")
        if result.returncode == 0:
            return
    except Exception as e:
        logger.warning(f"alembic migration failed: {e}")

    # Fallback: create tables directly
    logger.info("Falling back to create_all()")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created via create_all()")
    except Exception as e:
        logger.error(f"create_all() failed: {e}")


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