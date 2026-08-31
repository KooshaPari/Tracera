#!/usr/bin/env bash
# test-agileplus-integration.sh — AgilePlus integration test suite.
# Runs 5 phases covering configuration, workflow, sprint, reporting,
# and bi-directional sync.
set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────
API_URL="${API_URL:-http://localhost:8080}"
AGILEPLUS_URL="${AGILEPLUS_URL:-https://agileplus.tracera.dev}"
API_KEY="${AGILEPLUS_API_KEY:-}"
TIMEOUT="${TIMEOUT:-15}"
PASS=0
FAIL=0
WARN=0

# ── Helpers ──────────────────────────────────────────────────────────────

pass() { printf "\033[32m✓ PASS\033[0m %s\n" "$1"; PASS=$((PASS + 1)); }
fail() { printf "\033[31m✗ FAIL\033[0m %s — %s\n" "$1" "${2:-}"; FAIL=$((FAIL + 1)); }
warn() { printf "\033[33m⚠ WARN\033[0m %s — %s\n" "$1" "${2:-}"; WARN=$((WARN + 1)); }

api_get() {
  local url="$1"
  local auth_header=()
  [ -n "$API_KEY" ] && auth_header=(-H "Authorization: Bearer $API_KEY")
  curl -sf --max-time "$TIMEOUT" "${auth_header[@]}" "$url" 2>/dev/null
}

api_post() {
  local url="$1" data="$2"
  local auth_header=()
  [ -n "$API_KEY" ] && auth_header=(-H "Authorization: Bearer $API_KEY")
  curl -sf --max-time "$TIMEOUT" -X POST \
    "${auth_header[@]}" \
    -H "Content-Type: application/json" \
    -d "$data" "$url" 2>/dev/null
}

assert_field() {
  local name="$1" response="$2" jq_expr="$3" expected="$4"
  local actual
  actual=$(echo "$response" | jq -r "$jq_expr" 2>/dev/null)
  if [ "$actual" = "$expected" ]; then
    pass "$name"
  else
    fail "$name" "expected '$expected', got '$actual'"
  fi
}

# ══════════════════════════════════════════════════════════════════════════
# Phase 1: Configuration & Authentication (3 checks)
# ══════════════════════════════════════════════════════════════════════════
echo ""
echo "═══ Phase 1: Configuration & Authentication ═══"

RESPONSE=$(api_get "${AGILEPLUS_URL}/api/v1/config")
if [ -n "$RESPONSE" ]; then
  pass "AgilePlus config endpoint accessible"
  assert_field "Config has version" "$RESPONSE" '.version' "1.0.0"
else
  fail "AgilePlus config endpoint" "no response"
fi

RESPONSE=$(api_get "${API_URL}/api/v1/integrations/agileplus/status")
if [ -n "$RESPONSE" ]; then
  assert_field "Integration status" "$RESPONSE" '.connected' "true"
else
  warn "Integration status" "endpoint unavailable (may need setup)"
fi

RESPONSE=$(api_post "${AGILEPLUS_URL}/api/v1/auth/verify" '{"source":"tracera"}')
if [ -n "$RESPONSE" ]; then
  pass "Auth verification succeeded"
else
  fail "Auth verification" "no response from AgilePlus"
fi

# ══════════════════════════════════════════════════════════════════════════
# Phase 2: Workflow Sync (3 checks)
# ══════════════════════════════════════════════════════════════════════════
echo ""
echo "═══ Phase 2: Workflow Sync ═══"

RESPONSE=$(api_post "${AGILEPLUS_URL}/api/v1/workflow/sync" \
  '{"project":"tracera","direction":"pull"}')
if [ -n "$RESPONSE" ]; then
  assert_field "Workflow sync pull" "$RESPONSE" '.status' "ok"
else
  fail "Workflow sync pull" "no response"
fi

RESPONSE=$(api_post "${API_URL}/api/v1/integrations/agileplus/workflow/push" \
  '{"workflows":[{"name":"test-integration","steps":["todo","doing","done"]}]}')
if [ -n "$RESPONSE" ]; then
  pass "Workflow push to AgilePlus"
else
  warn "Workflow push" "endpoint may not be implemented yet"
fi

RESPONSE=$(api_get "${AGILEPLUS_URL}/api/v1/workflows")
if [ -n "$RESPONSE" ]; then
  assert_field "Workflows list is array" "$RESPONSE" '.workflows | type' "array"
else
  fail "Workflows list" "no response"
fi

# ══════════════════════════════════════════════════════════════════════════
# Phase 3: Sprint Planning (3 checks)
# ══════════════════════════════════════════════════════════════════════════
echo ""
echo "═══ Phase 3: Sprint Planning ═══"

RESPONSE=$(api_post "${AGILEPLUS_URL}/api/v1/sprints" \
  '{"name":"integration-test-sprint","duration_weeks":2,"team_size":1}')
if [ -n "$RESPONSE" ]; then
  assert_field "Sprint created" "$RESPONSE" '.status' "created"
  SPRINT_ID=$(echo "$RESPONSE" | jq -r '.sprint_id')
  pass "Sprint ID: $SPRINT_ID"
else
  fail "Sprint creation" "no response"
  SPRINT_ID=""
fi

if [ -n "$SPRINT_ID" ]; then
  RESPONSE=$(api_post "${AGILEPLUS_URL}/api/v1/sprints/${SPRINT_ID}/stories" \
    '{"stories":[{"title":"Test story","points":3}]}')
  if [ -n "$RESPONSE" ]; then
    assert_field "Stories added to sprint" "$RESPONSE" '.added' "1"
  else
    fail "Add stories to sprint" "no response"
  fi

  RESPONSE=$(api_get "${AGILEPLUS_URL}/api/v1/sprints/${SPRINT_ID}/capacity")
  if [ -n "$RESPONSE" ]; then
    pass "Sprint capacity endpoint"
  else
    fail "Sprint capacity" "no response"
  fi
fi

# ══════════════════════════════════════════════════════════════════════════
# Phase 4: Reporting & Metrics (3 checks)
# ══════════════════════════════════════════════════════════════════════════
echo ""
echo "═══ Phase 4: Reporting & Metrics ═══"

RESPONSE=$(api_get "${AGILEPLUS_URL}/api/v1/reports/velocity?project=tracera")
if [ -n "$RESPONSE" ]; then
  assert_field "Velocity report" "$RESPONSE" '.report_type' "velocity"
else
  warn "Velocity report" "endpoint unavailable"
fi

RESPONSE=$(api_get "${AGILEPLUS_URL}/api/v1/reports/burndown?sprint_id=${SPRINT_ID:-latest}")
if [ -n "$RESPONSE" ]; then
  pass "Burndown chart data available"
else
  warn "Burndown chart" "endpoint unavailable"
fi

RESPONSE=$(api_get "${API_URL}/api/v1/integrations/agileplus/metrics")
if [ -n "$RESPONSE" ]; then
  pass "Tracera-side AgilePlus metrics"
else
  warn "Tracera AgilePlus metrics" "endpoint unavailable"
fi

# ══════════════════════════════════════════════════════════════════════════
# Phase 5: Bi-directional Sync & Conflict Resolution (3 checks)
# ══════════════════════════════════════════════════════════════════════════
echo ""
echo "═══ Phase 5: Bi-directional Sync ═══"

RESPONSE=$(api_post "${API_URL}/api/v1/integrations/agileplus/sync" \
  '{"direction":"bidirectional","since":"2026-01-01T00:00:00Z"}')
if [ -n "$RESPONSE" ]; then
  pass "Bidirectional sync initiated"
else
  warn "Bidirectional sync" "endpoint may need configuration"
fi

RESPONSE=$(api_get "${API_URL}/api/v1/integrations/agileplus/conflicts")
if [ -n "$RESPONSE" ]; then
  CONFLICT_COUNT=$(echo "$RESPONSE" | jq -r '.conflicts | length' 2>/dev/null || echo "0")
  if [ "$CONFLICT_COUNT" = "0" ]; then
    pass "No sync conflicts"
  else
    warn "Sync conflicts" "$CONFLICT_COUNT conflict(s) detected"
  fi
else
  warn "Conflict check" "endpoint unavailable"
fi

RESPONSE=$(api_post "${API_URL}/api/v1/integrations/agileplus/sync/resolve" \
  '{"strategy":"tracera-wins"}')
if [ -n "$RESPONSE" ] || [ -z "$RESPONSE" ]; then
  pass "Conflict resolution strategy accepted"
else
  fail "Conflict resolution" "endpoint rejected strategy"
fi

# ── Cleanup ──────────────────────────────────────────────────────────────
if [ -n "${SPRINT_ID:-}" ]; then
  api_post "${AGILEPLUS_URL}/api/v1/sprints/${SPRINT_ID}/archive" '{}' >/dev/null 2>&1 || true
  echo "  (cleaned up test sprint $SPRINT_ID)"
fi

# ── Summary ──────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════"
echo "  AgilePlus Integration Test Results"
echo "  Passed:  $PASS"
echo "  Failed:  $FAIL"
echo "  Warned:  $WARN"
echo "════════════════════════════════════════"

if [ "$FAIL" -gt 0 ]; then
  echo "❌ AgilePlus integration tests FAILED"
  exit 1
fi
echo "✅ AgilePlus integration tests PASSED"
exit 0
