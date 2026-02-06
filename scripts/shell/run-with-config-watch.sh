#!/usr/bin/env bash
# Run a command and restart it when watched config files change.
# Uses watchexec (https://github.com/watchexec/watchexec-cli) when available.
#
# Usage: run-with-config-watch.sh <path1> [path2 ...] -- <command> [args...]
# Example: run-with-config-watch.sh monitoring/grafana.ini -- grafana server --config monitoring/grafana.ini --homepath /opt/homebrew/share/grafana
#
# Install watchexec for config reload: brew install watchexec (macOS) or cargo install watchexec-cli

set -e

args=()
watch_paths=()
seen_dash=0

for arg in "$@"; do
  if [[ "$arg" == "--" ]]; then
    seen_dash=1
    continue
  fi
  if (( ! seen_dash )); then
    watch_paths+=("$arg")
  else
    args+=("$arg")
  fi
done

if (( ${#args[@]} == 0 )); then
  echo "run-with-config-watch.sh: missing command after --" >&2
  exit 1
fi

if command -v watchexec &>/dev/null && (( ${#watch_paths[@]} > 0 )); then
  watch_opts=()
  for p in "${watch_paths[@]}"; do
    watch_opts+=(-w "$p")
  done
  if [[ -n "${WATCH_DEBOUNCE_MS:-}" ]]; then
    watch_opts+=(--debounce "${WATCH_DEBOUNCE_MS}ms")
  fi
  if [[ -n "${WATCH_POLL_MS:-}" ]]; then
    watch_opts+=(--poll "${WATCH_POLL_MS}ms")
  fi
  exec watchexec "${watch_opts[@]}" --restart -- "${args[@]}"
else
  if (( ${#watch_paths[@]} > 0 )) && ! command -v watchexec &>/dev/null; then
    echo "run-with-config-watch.sh: watchexec not found; running without config watch (install: brew install watchexec)" >&2
  fi
  if [[ "${WATCH_HOLD_ON_MISSING:-0}" == "1" ]]; then
    echo "run-with-config-watch.sh: holding process (no watchexec available)." >&2
    exec sh -c 'while true; do sleep 3600; done'
  fi
  exec "${args[@]}"
fi
