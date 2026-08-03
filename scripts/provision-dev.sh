#!/usr/bin/env bash
# ============================================================
# CLIPZ Development Environment — Fly.io Provisioning Script
# Run AFTER flyctl auth is configured and email verified.
# ============================================================
set -euo pipefail

echo "=== CLIPZ Dev Environment Provisioning ==="
echo ""

# 1. Create the API app
echo "[1/4] Creating Fly app: clipz-api-dev"
flyctl apps create clipz-api-dev --org personal 2>/dev/null || echo "  App already exists"

# 2. Create PostgreSQL database
echo "[2/4] Creating PostgreSQL database"
flyctl postgres create \
  --name clipz-dev-db \
  --org personal \
  --region iad \
  --initial-cluster-size 1 \
  --vm-size shared-cpu-1x \
  --volume-size 10 \
  --auth-param connection_limit=50 2>/dev/null || echo "  Database already exists, attaching..."

# 3. Attach DB to the app
echo "  Attaching database to clipz-api-dev..."
flyctl postgres attach clipz-dev-db --app clipz-api-dev 2>/dev/null || echo "  Already attached"

# 4. Create Tigris object storage bucket
echo "[3/4] Creating Tigris storage bucket"
flyctl storage create \
  --name clipz-dev-storage \
  --org personal \
  --region iad \
  --public 2>/dev/null || echo "  Bucket already exists"

# 5. Set environment variables
echo "[4/4] Setting environment variables"
flyctl secrets set \
  --app clipz-api-dev \
  ENVIRONMENT=development \
  APP_ENV=development \
  LOG_LEVEL=DEBUG \
  CORS_ORIGINS="https://clipz-os.higgsfield.app,http://localhost:3000,http://localhost:5173,https://clipz-api-dev.fly.dev"

echo ""
echo "=== Provisioning Complete ==="
echo ""
echo "Deploy your app with:"
echo "  flyctl deploy --config fly.dev.toml --app clipz-api-dev"
echo ""
echo "Your development URL will be:"
echo "  https://clipz-api-dev.fly.dev"
echo "  https://clipz-api-dev.fly.dev/deploy  (dashboard)"
echo "  https://clipz-api-dev.fly.dev/docs    (Swagger)"