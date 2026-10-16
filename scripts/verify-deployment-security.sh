#!/usr/bin/env bash
set -euo pipefail

# Secret-free deployment boundary gate.
#
# private:
#   Validates the local self-host topology, including the exact host-loopback
#   origin used by the separately managed shared Cloudflare connector.
#
# public:
#   Additionally validates the Caddy-published hostname path. It does NOT claim
#   to validate Cloudflare Access policy state; live-service-smoke.yml qualifies
#   the Access-protected Tracera hostnames with machine credentials.
mode="private"
if [[ "${1:-}" == "--mode" ]]; then
  mode="${2:?usage: $0 [--mode private|public]}"
fi
if [[ "$mode" != "private" && "$mode" != "public" ]]; then
  echo "error: mode must be private or public" >&2
  exit 2
fi

if [[ "$mode" == "public" ]]; then
  public_hostname="${TRACERA_PUBLIC_HOSTNAME:-}"
  [[ -n "$public_hostname" ]] \
    || { echo "public mode requires TRACERA_PUBLIC_HOSTNAME" >&2; exit 1; }
  [[ "$public_hostname" =~ ^[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?$ ]] \
    || { echo "public mode requires a DNS-safe TRACERA_PUBLIC_HOSTNAME" >&2; exit 1; }
  [[ "$public_hostname" != *example* && "$public_hostname" != localhost && "$public_hostname" != *.local ]] \
    || { echo "public mode rejects placeholder/local TRACERA_PUBLIC_HOSTNAME" >&2; exit 1; }
fi

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
compose="$root/deploy/selfhost/docker-compose.selfhost.yml"
caddy="$root/deploy/selfhost/Caddyfile"

fail() {
  echo "DEPLOYMENT SECURITY FAIL: $*" >&2
  exit 1
}

grep -qE '^      TRACERA_BIND_ADDR: 0\.0\.0\.0:8080$' "$compose" \
  || fail "self-host server must bind to container port 8080"

python3 "$root/scripts/verify-selfhost-loopback-port.py" \
  || fail "self-host backend must publish exactly one mapping: 127.0.0.1:8080:8080"

grep -qE '^[[:space:]]*reverse_proxy[[:space:]]+tracera-server:8080$' "$caddy" \
  || fail "Caddy must continue proxying tracera-server"
grep -qE '^[[:space:]]*header[[:space:]]+\{' "$caddy" \
  || fail "Caddy security headers block is missing"
grep -qE '^      - "443:443"$' "$compose" \
  || fail "Caddy must publish HTTPS port 443 at its ingress boundary"

if [[ "$mode" == "public" ]]; then
  grep -qE '^[[:space:]]*(forward_auth|basic_auth|jwt)[[:space:]]' "$caddy" \
    || fail "public mode requires an active Caddy auth directive (forward_auth/basic_auth/jwt)"
  grep -qE '^[^[:space:]].*[[:space:]]\{$' "$caddy" \
    || fail "public mode requires an explicit Caddy site listener"
fi

echo "deployment security gate passed (mode=$mode)"
