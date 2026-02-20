#!/usr/bin/env bash
# Injects [LIFECYCLE] START/STOP lines into the process stream so dev logs show restarts clearly.
# Usage: with-lifecycle.sh <SERVICE_NAME> <command> [args...]
# Stdout/stderr go to process-compose log; START at begin, STOP with exit code on exit.

set -e
SERVICE_NAME="${1:?missing SERVICE_NAME}"
shift

PORT_CLEAR_MODE="${PORT_CLEAR_MODE:-}"
PORT_CLEAR_PORTS="${PORT_CLEAR_PORTS:-}"
PORT_CLEAR_MATCH_REGEX="${PORT_CLEAR_MATCH_REGEX:-}"

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CLEAR_PORT="${ROOT}/scripts/shell/clear-port.sh"
GUARD_PORT="${ROOT}/scripts/shell/guard-port.sh"
ENV_WATCH="${ENV_WATCH:-1}"
WATCH_FILES="${WATCH_FILES:-}"
RUN_WITH_WATCH="${ROOT}/scripts/shell/run-with-config-watch.sh"

if [[ -n "$PORT_CLEAR_MODE" ]]; then
  case "$PORT_CLEAR_MODE" in
    kill|guard)
      ;;
    *)
      echo "[LIFECYCLE] PORT-CLEAR error: unsupported PORT_CLEAR_MODE='$PORT_CLEAR_MODE' for $SERVICE_NAME" >&2
      exit 1
      ;;
  esac

  if [[ -z "$PORT_CLEAR_PORTS" ]]; then
    echo "[LIFECYCLE] PORT-CLEAR error: PORT_CLEAR_PORTS is required for $SERVICE_NAME" >&2
    exit 1
  fi

  if [[ "$PORT_CLEAR_MODE" == "kill" ]]; then
    if [[ ! -x "$CLEAR_PORT" ]]; then
      echo "[LIFECYCLE] PORT-CLEAR error: clear-port.sh not found or not executable at ${CLEAR_PORT} for $SERVICE_NAME" >&2
      exit 1
    fi
  else
    if [[ -z "$PORT_CLEAR_MATCH_REGEX" ]]; then
      echo "[LIFECYCLE] PORT-CLEAR error: PORT_CLEAR_MATCH_REGEX is required for $SERVICE_NAME" >&2
      exit 1
    fi
    if [[ ! -x "$GUARD_PORT" ]]; then
      echo "[LIFECYCLE] PORT-CLEAR error: guard-port.sh not found or not executable at ${GUARD_PORT} for $SERVICE_NAME" >&2
      exit 1
    fi
  fi

  IFS=',' read -ra _ports <<< "$PORT_CLEAR_PORTS"
  for _port in "${_ports[@]}"; do
    _port="${_port//[[:space:]]/}"
    if ! [[ "$_port" =~ ^[0-9]+$ ]]; then
      echo "[LIFECYCLE] PORT-CLEAR error: invalid port '$_port' for $SERVICE_NAME" >&2
      exit 1
    fi

    if [[ "$PORT_CLEAR_MODE" == "kill" ]]; then
      "$CLEAR_PORT" "$_port" "$SERVICE_NAME"
    else
      "$GUARD_PORT" "$SERVICE_NAME" "$_port" "$PORT_CLEAR_MATCH_REGEX"
    fi
  done
fi

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
echo "[LIFECYCLE] START $SERVICE_NAME $(ts)"
trap 'echo "[LIFECYCLE] STOP $SERVICE_NAME $(ts) exit=$?"' EXIT

if [[ -z "$WATCH_FILES" && "$ENV_WATCH" == "1" ]]; then
  if [[ -f "${ROOT}/.env" ]]; then
    WATCH_FILES="${ROOT}/.env"
  fi
fi

if [[ -n "$WATCH_FILES" && -x "$RUN_WITH_WATCH" ]]; then
  IFS=',' read -ra _watch_paths <<< "$WATCH_FILES"
  exec "$RUN_WITH_WATCH" "${_watch_paths[@]}" -- "$@"
fi

exec "$@"
