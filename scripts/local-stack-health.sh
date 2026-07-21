#!/usr/bin/env bash
set -euo pipefail

# Read-only health probe for the local Compose deployment.  It never starts,
# stops, or restarts services and never sources the env file (so values cannot
# execute as shell code).
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
compose_file="${TRACERA_COMPOSE_FILE:-${repo_root}/docker-compose.local.yml}"
env_file="${TRACERA_ENV_FILE:-${repo_root}/.env.local}"
local_port="${TRACERA_LOCAL_PORT:-18081}"
local_url="${TRACERA_LOCAL_URL:-http://127.0.0.1:${local_port}}"
tailnet_url="${TRACERA_TAILSCALE_URL:-}"
timeout_seconds="${TRACERA_HEALTH_TIMEOUT_SECONDS:-5}"

die() { echo "local stack health: FAIL: $*" >&2; exit 1; }

command -v docker >/dev/null 2>&1 || die "docker is required"
[[ -f "${compose_file}" ]] || die "compose file not found: ${compose_file}"
[[ -f "${env_file}" ]] || die "env file not found: ${env_file} (copy .env.example first)"
[[ "${timeout_seconds}" =~ ^[1-9][0-9]*$ ]] || die "timeout must be a positive integer"

compose=(docker compose --env-file "${env_file}" -f "${compose_file}")
mapfile -t running < <("${compose[@]}" ps --services --filter status=running 2>/dev/null | sort)
expected=(frontend postgres tracera-server)
for service in "${expected[@]}"; do
  printf '%s\n' "${running[@]}" | grep -Fxq "${service}" || \
    die "Compose service is not running: ${service}"
done

check_http() {
  local base="$1" label="$2"
  local health ready index
  health="$(curl --silent --show-error --fail --max-time "${timeout_seconds}" "${base%/}/health")" || \
    die "${label} /health request failed"
  [[ "${health}" == *'"status":"ok"'* ]] || die "${label} /health returned unexpected payload"
  ready="$(curl --silent --show-error --fail --max-time "${timeout_seconds}" "${base%/}/ready")" || \
    die "${label} /ready request failed"
  [[ "${ready}" == *'"status":"ready"'* ]] || die "${label} /ready returned unexpected payload"
  index="$(curl --silent --output /dev/null --write-out '%{http_code}' --max-time "${timeout_seconds}" "${base%/}/")" || \
    die "${label} frontend request failed"
  [[ "${index}" == "200" ]] || die "${label} frontend returned HTTP ${index}"
  echo "local stack health: ${label} PASS (/health, /ready, frontend)"
}

check_http "${local_url}" "local"
if [[ -n "${tailnet_url}" ]]; then
  check_http "${tailnet_url}" "tailscale"
fi

echo "local stack health: PASS (services=${running[*]})"
