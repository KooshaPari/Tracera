#!/usr/bin/env bash
# Guarded hot-reload runner.
# - Watches files for changes.
# - Runs a guard command on change; if it fails, keeps current process running.
# - If guard passes, restarts the service.
# - If the service exits, only restarts when the guard passes (or immediately if guard passes).
#
# Usage:
#   hot-reload-guard.sh --name SERVICE --watch PATH [--watch PATH ...] \
#     [--guard "cmd"] [--debounce-ms 500] [--exts "go,mod"] -- <command> [args...]
#
# Notes:
# - Requires watchexec for efficient file watching; falls back to polling.
# - Guard command should be fast and deterministic (e.g., "go build ./...").

set -euo pipefail

SERVICE_NAME=""
GUARD_CMD=""
DEBOUNCE_MS="${HOT_RELOAD_GUARD_DEBOUNCE_MS:-500}"
POLL_MS="${HOT_RELOAD_GUARD_POLL_MS:-2000}"
EXTS="${HOT_RELOAD_GUARD_EXTS:-}"
WATCH_PATHS=()
CMD=()

log() { echo "[$SERVICE_NAME] $*"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)
      SERVICE_NAME="$2"
      shift 2
      ;;
    --watch)
      WATCH_PATHS+=("$2")
      shift 2
      ;;
    --guard)
      GUARD_CMD="$2"
      shift 2
      ;;
    --debounce-ms)
      DEBOUNCE_MS="$2"
      shift 2
      ;;
    --exts)
      EXTS="$2"
      shift 2
      ;;
    --)
      shift
      CMD=("$@")
      break
      ;;
    *)
      echo "hot-reload-guard.sh: unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$SERVICE_NAME" ]]; then
  echo "hot-reload-guard.sh: --name is required" >&2
  exit 1
fi

if [[ ${#WATCH_PATHS[@]} -eq 0 ]]; then
  echo "hot-reload-guard.sh: at least one --watch path is required" >&2
  exit 1
fi

if [[ ${#CMD[@]} -eq 0 ]]; then
  echo "hot-reload-guard.sh: missing command after --" >&2
  exit 1
fi

child_pid=""

run_guard() {
  if [[ -z "$GUARD_CMD" ]]; then
    return 0
  fi
  log "Guard check: $GUARD_CMD"
  if bash -c "$GUARD_CMD"; then
    return 0
  fi
  log "⚠️  Hot-reload guard blocked restart; guard failed. Waiting for a safe change."
  return 1
}

start_child() {
  if ! run_guard; then
    return 1
  fi
  log "Starting: ${CMD[*]}"
  "${CMD[@]}" &
  child_pid=$!
  return 0
}

stop_child() {
  if [[ -z "$child_pid" ]]; then
    return 0
  fi
  if kill -0 "$child_pid" >/dev/null 2>&1; then
    log "Stopping PID $child_pid"
    kill -TERM "$child_pid" >/dev/null 2>&1 || true
    for _ in {1..10}; do
      sleep 0.5
      if ! kill -0 "$child_pid" >/dev/null 2>&1; then
        child_pid=""
        return 0
      fi
    done
    log "Force killing PID $child_pid"
    kill -KILL "$child_pid" >/dev/null 2>&1 || true
  fi
  child_pid=""
}

monitor_child() {
  while true; do
    if [[ -z "$child_pid" ]]; then
      sleep 1
      continue
    fi
    if ! kill -0 "$child_pid" >/dev/null 2>&1; then
      log "⚠️  Process exited; waiting for a safe change before restart."
      child_pid=""
    fi
    sleep 1
  done
}

snapshot_hash() {
  python - "$EXTS" "${WATCH_PATHS[@]}" <<'PY'
import hashlib
import os
import sys

exts = sys.argv[1]
paths = sys.argv[2:]
ext_set = set()
if exts:
    ext_set = {f".{e.strip()}" if not e.strip().startswith(".") else e.strip() for e in exts.split(",") if e.strip()}

def should_include(path: str) -> bool:
    if not ext_set:
        return True
    _, ext = os.path.splitext(path)
    return ext in ext_set

hasher = hashlib.sha256()
for base in paths:
    if not os.path.exists(base):
        continue
    if os.path.isfile(base):
        if should_include(base):
            try:
                st = os.stat(base)
                hasher.update(f"{base}:{st.st_mtime_ns}".encode())
            except OSError:
                pass
        continue
    for root, _, files in os.walk(base):
        for name in files:
            path = os.path.join(root, name)
            if not should_include(path):
                continue
            try:
                st = os.stat(path)
                hasher.update(f"{path}:{st.st_mtime_ns}".encode())
            except OSError:
                pass

print(hasher.hexdigest())
PY
}

watch_loop() {
  if command -v watchexec >/dev/null 2>&1; then
    log "Watching with watchexec (debounce ${DEBOUNCE_MS}ms)"
    local opts=()
    for p in "${WATCH_PATHS[@]}"; do
      opts+=(-w "$p")
    done
    if [[ -n "$EXTS" ]]; then
      opts+=(--exts "$EXTS")
    fi
    watchexec --emit-events-to=stdio --debounce "${DEBOUNCE_MS}ms" "${opts[@]}" -- \
      cat | while read -r _; do
        if run_guard; then
          stop_child
          start_child || true
        fi
      done
    return
  fi

  log "watchexec not found; polling every ${POLL_MS}ms"
  local last_hash
  last_hash="$(snapshot_hash || true)"
  while true; do
    sleep "$(python - <<PY
print(${POLL_MS}/1000)
PY
)"
    local new_hash
    new_hash="$(snapshot_hash || true)"
    if [[ "$new_hash" != "$last_hash" ]]; then
      last_hash="$new_hash"
      if run_guard; then
        stop_child
        start_child || true
      fi
    fi
  done
}

start_child || true
monitor_child &
watch_loop
