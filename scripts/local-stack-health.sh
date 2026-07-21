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

# PostgreSQL keeps role passwords in the persistent volume.  Changing
# POSTGRES_PASSWORD in .env.local therefore does not update an existing role,
# and the API can answer 502 while all containers appear running.  Inspect
# only a bounded, boolean log signal: never print logs (which may contain
# connection strings or other secrets).
credential_drift_hint() {
  local logs
  logs="$(${compose[@]} logs --no-color --tail=200 tracera-server 2>/dev/null || true)"
  if printf '%s\n' "${logs}" | grep -Eiq \
    'password authentication failed|authentication failed for user|28P01'; then
    cat >&2 <<'EOF'
local stack health: likely PostgreSQL credential drift detected.
The persistent database role password does not match the API's DATABASE_URL.
Read the intended value only from .env.local, then repair the role in place
(never delete the postgres volume):

  docker compose --env-file .env.local -f docker-compose.local.yml exec postgres \
    psql -U tracera -d tracera -c "ALTER ROLE tracera WITH PASSWORD '<value from .env.local>';"

Afterward restart only the Tracera Compose project and rerun this probe.
EOF
  fi
}

command -v docker >/dev/null 2>&1 || die "docker is required"
[[ -f "${compose_file}" ]] || die "compose file not found: ${compose_file}"
[[ -f "${env_file}" ]] || die "env file not found: ${env_file} (copy .env.example first)"
[[ "${timeout_seconds}" =~ ^[1-9][0-9]*$ ]] || die "timeout must be a positive integer"

compose=(docker compose --env-file "${env_file}" -f "${compose_file}")
# Keep this compatible with the system Bash shipped by macOS (3.2); avoid
# mapfile/readarray, which were introduced after that version.
running="$("${compose[@]}" ps --services --filter status=running 2>/dev/null | sort)" || \
  die "unable to inspect Compose service status"
expected=(frontend postgres tracera-server)
for service in "${expected[@]}"; do
  printf '%s\n' "${running}" | grep -Fxq "${service}" || \
    die "Compose service is not running: ${service}"
done

check_http() {
  local base="$1" label="$2"
  local health ready index
  health="$(curl --silent --show-error --fail --max-time "${timeout_seconds}" "${base%/}/health")" || {
    credential_drift_hint
    die "${label} /health request failed"
  }
  if [[ "${health}" != *'"status":"ok"'* ]]; then
    credential_drift_hint
    die "${label} /health returned unexpected payload"
  fi
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

echo "local stack health: PASS (services=${running//$'\n'/ })"
