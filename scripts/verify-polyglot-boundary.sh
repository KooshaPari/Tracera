#!/usr/bin/env bash
set -euo pipefail

# Keep optional language experiments from silently becoming a second runtime.
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fail() { echo "POLYGLOT BOUNDARY FAIL: $*" >&2; exit 1; }

adr="$root/docs/operations/go-zig-mojo-adr.md"
config="$root/sidecar/go/internal/config/config.go"
[[ -f "$adr" ]] || fail "polyglot ADR is missing"
[[ -f "$config" ]] || fail "sidecar configuration is missing"

# Rust remains the only API/data-plane owner until the ADR changes.
grep -q 'Keep Rust as the API-of-record' "$adr" \
  || fail "ADR must keep Rust as API-of-record"
grep -q 'TRACERA_SIDE_CAR_ENABLED=false.*default' "$adr" \
  || fail "ADR must document a disabled sidecar default"
grep -q 'TRACERA_ZIG_OPT_OUT=true' "$adr" \
  || fail "ADR must keep Zig opt-out enabled"
grep -q 'TRACERA_MOJO_EXPERIMENT=disabled' "$adr" \
  || fail "ADR must keep Mojo disabled by default"

# The executable default is part of the safety boundary, not just prose.
grep -q 'boolEnv("TRACERA_SIDE_CAR_ENABLED", false)' "$config" \
  || fail "Go sidecar must default to disabled"

# No deployment surface may opt into the experimental sidecar implicitly.
if grep -R -nE 'TRACERA_SIDE_CAR_ENABLED[=:][[:space:]]*(1|true|yes|on)' \
  "$root/deploy" "$root/.github/workflows" 2>/dev/null; then
  fail "deployment/workflows must not enable the Go sidecar implicitly"
fi

echo "polyglot boundary gate passed (Rust canonical; Go disabled; Zig/Mojo opt-in only)"
