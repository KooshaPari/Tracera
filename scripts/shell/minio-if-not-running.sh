#!/usr/bin/env bash
# Start MinIO server only if not already running (avoids "address already in use"
# when MinIO was started by brew or a previous process-compose run).

set -e
MINIO_PORT="${MINIO_PORT:-9000}"
MINIO_DATA_DIR="${MINIO_DATA_DIR:-.minio/data}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

bash "$ROOT/scripts/shell/guard-port.sh" "MinIO" "$MINIO_PORT" "minio"

mkdir -p "$MINIO_DATA_DIR"
exec minio server "$MINIO_DATA_DIR"
