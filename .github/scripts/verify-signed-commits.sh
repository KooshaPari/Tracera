#!/usr/bin/env bash
# verify-signed-commits.sh — Verify that commits in a PR are signed.
# Checks GPG/SSH/S-MIME signatures via the GitHub API.
set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────
REPO="${REPO:-$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")}"
PR_NUMBER="${1:-${PR_NUMBER:-}}"
GH_TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
REQUIRE_SIGNED="${REQUIRE_SIGNED:-true}"

if [ -z "$REPO" ]; then
  echo "Error: Could not determine repository. Set REPO or run from a git repo."
  exit 1
fi

if [ -z "$PR_NUMBER" ]; then
  echo "Usage: $0 <pr-number>"
  echo "   or: PR_NUMBER=<n> $0"
  exit 1
fi

PASS=0
FAIL=0
UNSIGNED=0
TOTAL=0

# ── Helpers ──────────────────────────────────────────────────────────────

pass() { printf "\033[32m✓\033[0m %s\n" "$1"; PASS=$((PASS + 1)); }
fail() { printf "\033[31m✗\033[0m %s — %s\n" "$1" "${2:-}"; FAIL=$((FAIL + 1)); }

# ── Fetch PR commits ────────────────────────────────────────────────────
echo "════════════════════════════════════════════════"
echo "  Signed Commit Verification — PR #${PR_NUMBER}"
echo "════════════════════════════════════════════════"
echo ""

COMMITS=$(gh pr view "$PR_NUMBER" \
  --repo "$REPO" \
  --json commits \
  --jq '.commits[] | {oid: .oid, messageHeadline: .messageHeadline, authors: [.authors[].login]}' 2>/dev/null)

if [ -z "$COMMITS" ]; then
  echo "Error: Could not fetch commits for PR #${PR_NUMBER}"
  exit 1
fi

TOTAL=$(echo "$COMMITS" | jq -s 'length')
echo "Found $TOTAL commit(s) to verify."
echo ""

# ── Check each commit ───────────────────────────────────────────────────

echo "$COMMITS" | jq -c '.' | while IFS= read -r commit_json; do
  SHA=$(echo "$commit_json" | jq -r '.oid')
  SHORT_SHA="${SHA:0:8}"
  MSG=$(echo "$commit_json" | jq -r '.messageHeadline')
  AUTHORS=$(echo "$commit_json" | jq -r '.authors | join(", ")')

  # Query GitHub's commit signature verification via API
  VERIFY=$(gh api "repos/${REPO}/commits/${SHA}" \
    --jq '.commit.verification' 2>/dev/null)

  if [ -z "$VERIFY" ]; then
    fail "${SHORT_SHA} — ${MSG}" "API query failed"
    UNSIGNED=$((UNSIGNED + 1))
    continue
  fi

  VERIFIED=$(echo "$VERIFY" | jq -r '.verified')
  REASON=$(echo "$VERIFY" | jq -r '.reason')
  SIGNER=$(echo "$VERIFY" | jq -r '.signer // "unknown"')
  SCHEME=$(echo "$VERIFY" | jq -r '.scheme // "unknown"')

  if [ "$VERIFIED" = "true" ]; then
    pass "${SHORT_SHA} — ${MSG} [signed by ${SIGNER} via ${SCHEME}]"
  else
    if [ "$REASON" = "unsigned" ] || [ "$REASON" = "no_key" ]; then
      fail "${SHORT_SHA} — ${MSG}" "UNSIGNED (reason: ${REASON})"
      UNSIGNED=$((UNSIGNED + 1))
    else
      fail "${SHORT_SHA} — ${MSG}" "verification failed: ${REASON}"
    fi
  fi
done

# ── Summary ──────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════"
echo "  Total commits:    $TOTAL"
echo "  Signed:           $PASS"
echo "  Unsigned/Failed:  $FAIL"
echo "════════════════════════════════════════"

if [ "$REQUIRE_SIGNED" = "true" ] && [ "$FAIL" -gt 0 ]; then
  echo ""
  echo "❌ $FAIL commit(s) are not signed."
  echo "   All commits must be signed (GPG, SSH, or S-MIME) to merge."
  echo "   See: https://docs.github.com/en/authentication/managing-commit-signature-verification"
  exit 1
fi

if [ "$FAIL" -gt 0 ]; then
  echo ""
  echo "⚠ $FAIL unsigned commit(s) detected (non-blocking mode)."
  exit 0
fi

echo ""
echo "✅ All $TOTAL commit(s) are signed."
exit 0
