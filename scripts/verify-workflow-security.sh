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
! grep -R -nE 'gh secret (set|delete)|gh secret [a-z-]+.*--body' "$workflows" \
  || fail "workflows must not mutate repository secrets at runtime"

# A placeholder security step is not an audit and must never be allowed to
# become the only passing check in this workflow.
guard="$workflows/security-guard-hook-audit.yml"
[[ -f "$guard" ]] || fail "security guard workflow is missing"
! grep -qE 'Security guard skipped|Security guard placeholder' "$guard" \
  || fail "security guard workflow contains a fail-open placeholder"

echo "workflow security gate passed"
