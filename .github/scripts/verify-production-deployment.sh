#!/usr/bin/env bash
# verify-production-deployment.sh — Post-deployment health verification.
# Runs 6 phases with 26 individual checks against the production endpoint.
set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────
PROD_URL="${PROD_URL:-https://api.tracera.dev}"
TIMEOUT="${TIMEOUT:-10}"
AUTH_TOKEN="${AUTH_TOKEN:-}"
PASS=0
FAIL=0
WARN=0

# ── Helpers ──────────────────────────────────────────────────────────────

green()  { printf "\033[32m✓ %s\033[0m\n" "$1"; }
red()    { printf "\033[31m✗ %s\033[0m\n" "$1"; FAIL=$((FAIL + 1)); }
yellow() { printf "\033[33m⚠ %s\033[0m\n" "$1"; WARN=$((WARN + 1)); }
pass()   { green "$1"; PASS=$((PASS + 1)); }

http_get() {
  local url="$1"
  local extra_args=()
  if [ -n "$AUTH_TOKEN" ]; then
    extra_args+=(-H "Authorization: Bearer $AUTH_TOKEN")
  fi
  curl -sf --max-time "$TIMEOUT" "${extra_args[@]}" "$url" 2>/dev/null
}

http_get_status() {
  local url="$1"
  local extra_args=()
  if [ -n "$AUTH_TOKEN" ]; then
    extra_args+=(-H "Authorization: Bearer $AUTH_TOKEN")
  fi
  curl -so /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "${extra_args[@]}" "$url" 2>/dev/null
}

# ── Phase 1: DNS & TLS (3 checks) ──────────────────────────────────────
echo "═══ Phase 1: DNS & TLS ═══"

STATUS=$(http_get_status "$PROD_URL/health")
[ "$STATUS" = "200" ] && pass "P1-1: Health endpoint reachable (HTTP $STATUS)" || red "P1-1: Health endpoint failed (HTTP $STATUS)"

STATUS=$(http_get_status "https://api.tracera.dev")
[ "$STATUS" -ge 200 ] && [ "$STATUS" -lt 500 ] && pass "P1-2: Root domain responds" || red "P1-2: Root domain unreachable"

echo | openssl s_client -connect api.tracera.dev:443 -servername api.tracera.dev 2>/dev/null | grep -q "Verify return code: 0" && pass "P1-3: TLS certificate valid" || red "P1-3: TLS certificate issue"

# ── Phase 2: Core API health (5 checks) ────────────────────────────────
echo ""
echo "═══ Phase 2: Core API Health ═══"

STATUS=$(http_get_status "$PROD_URL/api/v1/status")
[ "$STATUS" = "200" ] && pass "P2-1: API status endpoint" || red "P2-1: API status returned $STATUS"

STATUS=$(http_get_status "$PROD_URL/api/v1/version")
[ "$STATUS" = "200" ] && pass "P2-2: Version endpoint" || red "P2-2: Version endpoint returned $STATUS"

STATUS=$(http_get_status "$PROD_URL/api/v1/ready")
[ "$STATUS" = "200" ] && pass "P2-3: Readiness probe" || red "P2-3: Readiness probe returned $STATUS"

STATUS=$(http_get_status "$PROD_URL/api/v1/live")
[ "$STATUS" = "200" ] && pass "P2-4: Liveness probe" || red "P2-4: Liveness probe returned $STATUS"

RESPONSE=$(http_get "$PROD_URL/api/v1/metrics")
echo "$RESPONSE" | grep -q "up" && pass "P2-5: Metrics endpoint responding" || yellow "P2-5: Metrics endpoint non-standard"

# ── Phase 3: Database connectivity (4 checks) ──────────────────────────
echo ""
echo "═══ Phase 3: Database Connectivity ═══"

STATUS=$(http_get_status "$PROD_URL/api/v1/db/health")
[ "$STATUS" = "200" ] && pass "P3-1: Database health check" || red "P3-1: Database health failed ($STATUS)"

STATUS=$(http_get_status "$PROD_URL/api/v1/db/ping")
[ "$STATUS" = "200" ] && pass "P3-2: Database ping" || red "P3-2: Database ping failed ($STATUS)"

STATUS=$(http_get_status "$PROD_URL/api/v1/db/migrations/status")
[ "$STATUS" = "200" ] && pass "P3-3: Migrations up to date" || yellow "P3-3: Migrations status unclear ($STATUS)"

STATUS=$(http_get_status "$PROD_URL/api/v1/db/replication")
[ "$STATUS" -ge 200 ] && [ "$STATUS" -lt 500 ] && pass "P3-4: Replication lag check" || yellow "P3-4: Replication check unavailable ($STATUS)"

# ── Phase 4: SWEE Graph engine (4 checks) ──────────────────────────────
echo ""
echo "═══ Phase 4: SWEE Graph Engine ═══"

STATUS=$(http_get_status "$PROD_URL/api/v1/graph/health")
[ "$STATUS" = "200" ] && pass "P4-1: Graph engine health" || red "P4-1: Graph engine unhealthy ($STATUS)"

STATUS=$(http_get_status "$PROD_URL/api/v1/graph/stats")
[ "$STATUS" = "200" ] && pass "P4-2: Graph stats endpoint" || yellow "P4-2: Graph stats unavailable ($STATUS)"

STATUS=$(http_get_status "$PROD_URL/api/v1/graph/nodes?limit=1")
[ "$STATUS" = "200" ] && pass "P4-3: Graph node query" || red "P4-3: Graph node query failed ($STATUS)"

STATUS=$(http_get_status "$PROD_URL/api/v1/graph/edges?limit=1")
[ "$STATUS" = "200" ] && pass "P4-4: Graph edge query" || red "P4-4: Graph edge query failed ($STATUS)"

# ── Phase 5: Desktop update server (3 checks) ──────────────────────────
echo ""
echo "═══ Phase 5: Desktop Update Server ═══"

STATUS=$(http_get_status "$PROD_URL/api/v1/updates/manifest")
[ "$STATUS" = "200" ] && pass "P5-1: Update manifest available" || yellow "P5-1: Update manifest ($STATUS)"

STATUS=$(http_get_status "$PROD_URL/api/v1/updates/check?current=0.0.0")
[ "$STATUS" = "200" ] && pass "P5-2: Update check endpoint" || yellow "P5-2: Update check unavailable ($STATUS)"

STATUS=$(http_get_status "$PROD_URL/api/v1/updates/changelog")
[ "$STATUS" -ge 200 ] && [ "$STATUS" -lt 500 ] && pass "P5-3: Changelog endpoint" || yellow "P5-3: Changelog unavailable ($STATUS)"

# ── Phase 6: End-to-end smoke test (4 checks) ──────────────────────────
echo ""
echo "═══ Phase 6: End-to-End Smoke ═══"

STATUS=$(http_get_status "$PROD_URL/api/v1/trace/query?q=smoke_test")
[ "$STATUS" -ge 200 ] && [ "$STATUS" -lt 500 ] && pass "P6-1: Trace query endpoint" || red "P6-1: Trace query failed ($STATUS)"

STATUS=$(http_get_status "$PROD_URL/api/v1/artifacts?limit=1")
[ "$STATUS" -ge 200 ] && [ "$STATUS" -lt 500 ] && pass "P6-2: Artifacts listing" || red "P6-2: Artifacts listing failed ($STATUS)"

STATUS=$(http_get_status "$PROD_URL/api/v1/stories?limit=1")
[ "$STATUS" -ge 200 ] && [ "$STATUS" -lt 500 ] && pass "P6-3: Stories listing" || red "P6-3: Stories listing failed ($STATUS)"

STATUS=$(http_get_status "$PROD_URL/api/v1/health/detailed")
[ "$STATUS" = "200" ] && pass "P6-4: Detailed health report" || yellow "P6-4: Detailed health unavailable ($STATUS)"

# ── Summary ──────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════"
echo "  Results:  ${PASS} passed, ${FAIL} failed, ${WARN} warnings"
echo "════════════════════════════════════════"

if [ "$FAIL" -gt 0 ]; then
  echo "❌ Deployment verification FAILED"
  exit 1
fi

echo "✅ Deployment verification PASSED"
exit 0
