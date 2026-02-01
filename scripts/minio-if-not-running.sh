#!/usr/bin/env bash
# Start MinIO server only if not already running (avoids "address already in use"
# when MinIO was started by brew or a previous process-compose run).

set -e
MINIO_PORT="${MINIO_PORT:-9000}"
MINIO_DATA_DIR="${MINIO_DATA_DIR:-.minio/data}"

if command -v lsof >/dev/null 2>&1; then
  if lsof -Pi :"$MINIO_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "MinIO already running on port $MINIO_PORT; holding process for process-compose."
    exec sh -c 'while true; do sleep 3600; done'
  fi
fi

mkdir -p "$MINIO_DATA_DIR"
exec minio server "$MINIO_DATA_DIR"
