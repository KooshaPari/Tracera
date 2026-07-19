#!/usr/bin/env bash
set -euo pipefail

# Contract test for the deployment gate.  The checked-in stack is private by
# default: private mode must pass, while public mode must fail closed until an
# operator enables a real auth directive.  No credentials or network access
# are needed.
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
gate="$root/scripts/verify-deployment-security.sh"

"$gate" --mode private
if "$gate" --mode public >/tmp/tracera-public-security-gate.log 2>&1; then
  echo "DEPLOYMENT SECURITY TEST FAIL: public mode unexpectedly passed without auth" >&2
  cat /tmp/tracera-public-security-gate.log >&2
  exit 1
fi
grep -q "active Caddy auth directive" /tmp/tracera-public-security-gate.log \
  || { cat /tmp/tracera-public-security-gate.log >&2; exit 1; }

# Validate the checked-in Caddy syntax when the local tool is available. The
# hostname placeholder requires an environment value during adaptation.
if command -v caddy >/dev/null 2>&1; then
  TRACERA_PUBLIC_HOSTNAME=tracera.example.test \
    caddy validate --config "$root/deploy/selfhost/Caddyfile" >/dev/null
fi
echo "deployment security contract test passed"
