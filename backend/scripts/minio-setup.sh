#!/usr/bin/env bash
# Local MinIO setup (Homebrew, no Docker).
# Installs MinIO, starts it as a service (brew services), creates bucket via Go (no UI, no mc).

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BUCKET="${S3_BUCKET:-tracertm}"
PORT="${MINIO_PORT:-9000}"
CONSOLE_PORT="${MINIO_CONSOLE_PORT:-9001}"

cd "$BACKEND_DIR"

# Install MinIO via Homebrew if not present
if ! command -v minio &>/dev/null; then
  echo "==> Installing MinIO server (brew install minio)..."
  brew install minio
fi

# Start MinIO as a service (persists across reboots; uses brew default data dir)
echo "==> Starting MinIO as a service (brew services start minio)..."
brew services start minio 2>/dev/null || true

# Wait for MinIO API to be up
minio_up() { curl -sf -o /dev/null "http://127.0.0.1:$PORT/minio/health/live" 2>/dev/null || curl -sf -o /dev/null "http://127.0.0.1:$PORT" 2>/dev/null; }
echo "==> Waiting for MinIO on port $PORT..."
for i in $(seq 1 30); do
  sleep 0.5
  if minio_up; then break; fi
done
if ! minio_up; then
  echo "MinIO did not become ready. Check: brew services list minio"
  exit 1
fi
echo "==> MinIO is up."

# Ensure .env has S3 vars for create-minio-bucket (default MinIO credentials)
if ! grep -q "^S3_ENDPOINT=" .env 2>/dev/null; then
  echo "==> Adding S3 vars to .env..."
  cat >> .env << 'ENVBLOCK'

# MinIO (local) - added by minio-setup
S3_ENDPOINT=http://127.0.0.1:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET=tracertm
S3_REGION=us-east-1
ENVBLOCK
fi

# Create bucket using Go (no UI, no mc)
echo "==> Creating bucket '$BUCKET' (go run ./cmd/create-minio-bucket)..."
go run ./cmd/create-minio-bucket/

echo ""
echo "==> MinIO is running as a service."
echo "    API:    http://127.0.0.1:$PORT"
echo "    Console: http://127.0.0.1:$CONSOLE_PORT (minioadmin / minioadmin)"
echo "    Bucket: $BUCKET"
echo "    Stop:   brew services stop minio"
echo "    Status: brew services list minio"
