# CLIPZ Deployment Guide

## Architecture

```
User Browser
    │
    ├── https://clipz-os.higgsfield.app  (Frontend — TanStack Start SSR)
    │
    └── https://clipz-api-dev.fly.dev    (Backend API — Fly.io, Dev)
         │
         ├── FastAPI (Python 3.12)
         ├── PostgreSQL (managed, Fly.io)
         └── Tigris S3 Storage (media files)
```

## Environments

| Environment | Fly App | DB | Storage | Git Branch | URL |
|---|---|---|---|---|---|
| Development | clipz-api-dev | clipz-dev-db | clipz-dev-storage | develop | https://clipz-api-dev.fly.dev |
| Production | clipz-api-prod | clipz-prod-db | clipz-prod-storage | main | (not provisioned) |

## Services Created

| Resource | Name | Type | Purpose |
|---|---|---|---|
| Fly App | clipz-api-dev | Fly Machine (1 shared CPU, 1GB RAM) | FastAPI server |
| PostgreSQL | clipz-dev-db | Managed Postgres (1 node, 10GB) | Application database |
| Tigris Storage | clipz-dev-storage | S3-compatible object storage | Video uploads, thumbnails, artifacts |

## Environment Variables

| Variable | Set In | Purpose |
|---|---|---|
| `ENVIRONMENT` | `fly.dev.toml` + `flyctl secrets` | "development" or "production" |
| `APP_ENV` | `fly.dev.toml` + `flyctl secrets` | Application environment flag |
| `LOG_LEVEL` | `fly.dev.toml` + `flyctl secrets` | "DEBUG" for dev, "INFO" for prod |
| `CORS_ORIGINS` | `fly.dev.toml` + `flyctl secrets` | Comma-separated allowed origins |
| `GIT_COMMIT` | Build arg (injected by CI) | Current git SHA (shown on dashboard) |
| `DEPLOY_TIME` | Build arg (injected by CI) | ISO timestamp of deploy |
| `DATABASE_URL` | Auto-set by `flyctl postgres attach` | PostgreSQL connection string |
| `AWS_ACCESS_KEY_ID` | Auto-set by `flyctl storage create` | Tigris S3 access key |
| `AWS_SECRET_ACCESS_KEY` | Auto-set by `flyctl storage create` | Tigris S3 secret key |
| `AWS_ENDPOINT_URL_S3` | Auto-set by `flyctl storage create` | Tigris S3 endpoint |

## CI/CD Pipeline

### GitHub Actions Workflow: `.github/workflows/deploy-dev.yml`

**Trigger:** Push to `develop` branch (when `apps/api/**` or `fly.dev.toml` changes)

**Steps:**
1. Checkout code
2. Install flyctl
3. Extract git commit SHA and timestamp
4. Deploy to Fly.io with build args:
   - `GIT_COMMIT` = current commit SHA
   - `DEPLOY_TIME` = current UTC timestamp
5. Health check (polls `/api/v1/health` up to 6 times, 10s apart)
6. Notify status

**Required GitHub Secret:**
- `FLY_API_TOKEN` — Personal access token from Fly.io (Settings → API Tokens)

## Deployment Dashboard

After deployment, visit:
- **https://clipz-api-dev.fly.dev/deploy** — HTML status dashboard
- **https://clipz-api-dev.fly.dev/api/v1/health** — JSON health + version info
- **https://clipz-api-dev.fly.dev/docs** — Swagger API documentation

## Initial Setup (one-time)

```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh

# 2. Authenticate
flyctl auth login

# 3. Run provisioning script
bash scripts/provision-dev.sh

# 4. Deploy
flyctl deploy --config fly.dev.toml --app clipz-api-dev

# 5. Verify
curl https://clipz-api-dev.fly.dev/api/v1/health
```

## Adding GPU Workers (Future)

When CLIPZ needs GPU-accelerated AI workers:

```bash
# Create a GPU machine
flyctl machine run . \
  --app clipz-gpu-dev \
  --vm-gpu-kind a100-pcie-40gb \
  --vm-size dedicated-cpu-8x \
  --env QUEUE_NAME=ai-jobs

# Same Docker image, different CMD:
# CMD: python -m app.worker --queue ai-jobs
```

No infrastructure restructuring needed. The GPU machine reads from the same queue and storage as the CPU workers.

## Database Migrations

Database migrations are run automatically via the `release_command` in `fly.dev.toml`:

```toml
[deploy]
  release_command = "cd /app && python -m alembic upgrade head 2>/dev/null; true"
```

This runs BEFORE any new machine starts accepting traffic, ensuring the database schema is up to date before the new code runs.

## Local Development

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload
```