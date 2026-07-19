#!/usr/bin/env bash
set -euo pipefail

# Scan tracked content only.  References to environment variables and GitHub
# secret expressions are intentionally allowed; concrete credentials are not.
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

failures=0
check() {
  local label=$1 pattern=$2
  local hits
  hits=$(git grep -nI -E -e "$pattern" -- . ':!*.lock' ':!docs/audit/**' ':!audit/**' \
    ':!scripts/verify-secret-provenance.sh' || true)
  if [[ -n "$hits" ]]; then
    printf 'secret provenance violation (%s):\n%s\n' "$label" "$hits" >&2
    failures=$((failures + 1))
  fi
}

# High-confidence formats only.  Do not flag placeholders, env interpolation,
# workflow secret references, or ordinary prose mentioning a secret.
check 'private key material' '-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'
check 'GitHub token' 'gh[pousr]_[A-Za-z0-9_]{30,}'
check 'OpenAI key' 'sk-[A-Za-z0-9]{32,}'
check 'AWS access key' 'AKIA[0-9A-Z]{16}'
check 'Google API key' 'AIza[0-9A-Za-z_-]{30,}'
check 'JWT with concrete secret-like payload' 'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}'

if (( failures > 0 )); then
  exit 1
fi
printf 'secret provenance checks passed (tracked high-confidence patterns only)\n'
