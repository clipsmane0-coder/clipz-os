# ============================================================
# CLIPZ Backend API — Multi-stage Dockerfile
# Build context: repo root (apps/api/Dockerfile)
# ============================================================

# ---- Build stage ----
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Runtime stage ----
FROM python:3.12-slim

# Install FFmpeg and FFprobe (required for media ingestion)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local

# Ensure local Python binaries are in PATH
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app

# Copy application code
COPY apps/api/ .

# Environment
ENV PYTHONPATH=/app
ENV APP_ENV=production

# Build args — injected at deploy time
ARG GIT_COMMIT
ARG DEPLOY_TIME
ENV GIT_COMMIT=${GIT_COMMIT:-unknown}
ENV DEPLOY_TIME=${DEPLOY_TIME:-unknown}

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; resp = urllib.request.urlopen('http://localhost:8000/api/v1/health'); assert resp.status == 200" || exit 1

# Default: run the API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]