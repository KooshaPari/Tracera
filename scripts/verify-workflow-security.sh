#!/usr/bin/env bash
set -euo pipefail

# Static CI governance gate. Keep deployment workflows fail-closed and prevent
# workflow code from mutating repository secrets at runtime.
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workflows="$root/.github/workflows"
fail() { echo "WORKFLOW SECURITY FAIL: $*" >&2; exit 1; }

[[ -d "$workflows" ]] || fail "workflow directory is missing"

vercel="$workflows/deploy-vercel.yml"
[[ -f "$vercel" ]] || fail "deploy-vercel workflow is missing"
grep -qE '^permissions:' "$vercel" || fail "Vercel workflow must declare explicit permissions"
grep -qE '^  contents: read$' "$vercel" || fail "Vercel workflow must restrict contents to read"
grep -qE '(if:.*secrets\.VERCEL_TOKEN|HAS_VERCEL_TOKEN:.*secrets\.VERCEL_TOKEN)' "$vercel" \
  || fail "Vercel deployment must be gated on a configured token"
grep -qE '(if:.*secrets\.VERCEL_ORG_ID|HAS_VERCEL_ORG:.*secrets\.VERCEL_ORG_ID)' "$vercel" \
  || fail "Vercel deployment must be gated on a configured org id"
# Vercel production must be gated on secrets. Either an explicit fail-closed
# step ("Fail production deployment when Vercel secrets are unavailable")
# OR the graceful-skip pattern ("Skip when Vercel secrets are unavailable")
# with continue-on-error and a ::notice:: is acceptable. Both patterns
# ensure the actual deploy step never runs when secrets are missing.
if ! grep -q 'Fail production deployment when Vercel secrets are unavailable' "$vercel" \
   && ! grep -qE 'Skip when Vercel secrets are unavailable \(production\)' "$vercel"; then
  fail "Vercel production deploy must fail closed (or skip with notice) when secrets are missing"
fi
# When using the graceful-skip pattern, the skip step must emit a notice,
# exit 0, and the subsequent deploy step must be gated on the same env vars.
if grep -qE 'Skip when Vercel secrets are unavailable \(production\)' "$vercel"; then
  grep -q '::notice title=' "$vercel" \
    || fail "Vercel graceful-skip pattern must emit ::notice:: so the skip is visible"
  grep -q 'continue-on-error: true' "$vercel" \
    || fail "Vercel graceful-skip step must use continue-on-error"
  # The Deploy step must have an explicit `if:` gate referencing the
  # HAS_VERCEL_TOKEN env var (or secrets.VERCEL_TOKEN directly).
  awk '/Deploy to Vercel/{flag=1} flag && /if:/{print; exit}' "$vercel" \
    | grep -qE 'HAS_VERCEL_TOKEN|secrets\.VERCEL_TOKEN' \
    || fail "Vercel Deploy step must be gated on VERCEL_TOKEN presence"
fi
! grep -R -nE 'gh secret (set|delete)|gh secret [a-z-]+.*--body' "$workflows" \
  || fail "workflows must not mutate repository secrets at runtime"

# A placeholder security step is not an audit and must never be allowed to
# become the only passing check in this workflow.
guard="$workflows/security-guard-hook-audit.yml"
[[ -f "$guard" ]] || fail "security guard workflow is missing"
grep -q 'actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683' "$guard" \
  || fail "security guard workflow checkout must be pinned"
! grep -qE 'Security guard skipped|Security guard placeholder' "$guard" \
  || fail "security guard workflow contains a fail-open placeholder"

release="$workflows/release-dist.yml"
[[ -f "$release" ]] || fail "release-dist workflow is missing"
grep -q 'actions/setup-node@v4' "$release" \
  || fail "release workflow must pin Node before manifest generation"
grep -q 'release-manifest-' "$release" \
  || fail "release workflow must publish per-target provenance manifests"
grep -q 'verify-release-manifest.mjs' "$release" \
  || fail "release workflow must verify provenance before upload"
desktop="$workflows/release-desktop.yml"
[[ -f "$desktop" ]] || fail "desktop release workflow is missing"
grep -q 'Verify packaged CLI, compose, and manifest inputs' "$desktop" \
  || fail "desktop release must assert packaged input presence"
grep -q 'crates/tracera-cli/Cargo.toml' "$desktop" \
  || fail "desktop release must check the bundled CLI manifest"
grep -q 'docker-compose.yml' "$desktop" \
  || fail "desktop release must check the bundled compose manifest"
grep -q 'frontend/scripts/release-manifest.mjs' "$desktop" \
  || fail "desktop release must check release-manifest tooling"
grep -q 'frontend/scripts/verify-release-manifest.mjs' "$desktop" \
  || fail "desktop release must check release-manifest verification tooling"
crates="$workflows/release-crates.yml"
[[ -f "$crates" ]] || fail "release-crates workflow is missing"
grep -q 'does not match release tag' "$crates" \
  || fail "crate release must fail closed on tag/version mismatch"

# Cloudflare Worker deploy must be gated on a token and have a trust-boundary
# probe (or hard-fail) that prevents actual deploy when the token lacks scope.
cf="$workflows/deploy-cloudflare.yml"
[[ -f "$cf" ]] || fail "deploy-cloudflare workflow is missing"
grep -qE 'CLOUDFLARE_API_TOKEN' "$cf" \
  || fail "CF workflow must reference CLOUDFLARE_API_TOKEN"
grep -qE 'cf_scope_check|cf_creds_ok|Continue.*deploy only' "$cf" \
  || fail "CF workflow must have a credential scope probe gating the deploy step"

# Render deploy must be gated on RENDER_API_KEY + service ID, with a probe.
render="$workflows/deploy-render.yml"
[[ -f "$render" ]] || fail "deploy-render workflow is missing"
grep -qE 'RENDER_API_KEY' "$render" \
  || fail "Render workflow must reference RENDER_API_KEY"
grep -qE 'RENDER_SERVICE_ID' "$render" \
  || fail "Render workflow must reference RENDER_SERVICE_ID"
grep -qE 'render_creds_ok' "$render" \
  || fail "Render workflow must gate deploy step on a credential probe"

latency="$workflows/runtime-latency-smoke.yml"
[[ -f "$latency" ]] || fail "runtime latency workflow is missing"
grep -q 'toolchain: stable' "$latency" \
  || fail "runtime latency workflow must select an explicit Rust toolchain"

echo "workflow security gate passed"
