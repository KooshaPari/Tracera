#!/usr/bin/env bash
# Injects [LIFECYCLE] START/STOP lines into the process stream so dev logs show restarts clearly.
# Usage: with-lifecycle.sh <SERVICE_NAME> <command> [args...]
# Stdout/stderr go to process-compose log; START at begin, STOP with exit code on exit.

set -e
SERVICE_NAME="${1:?missing SERVICE_NAME}"
shift
ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
echo "[LIFECYCLE] START $SERVICE_NAME $(ts)"
trap 'echo "[LIFECYCLE] STOP $SERVICE_NAME $(ts) exit=$?"' EXIT
exec "$@"
