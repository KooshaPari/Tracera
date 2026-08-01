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
grep -q 'Fail production deployment when Vercel secrets are unavailable' "$vercel" \
  || fail "Vercel production deploy must fail closed when secrets are missing"
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
latency="$workflows/runtime-latency-smoke.yml"
[[ -f "$latency" ]] || fail "runtime latency workflow is missing"
grep -q 'toolchain: stable' "$latency" \
  || fail "runtime latency workflow must select an explicit Rust toolchain"

echo "workflow security gate passed"
