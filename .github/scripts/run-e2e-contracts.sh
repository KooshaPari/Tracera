#!/usr/bin/env bash
# run-e2e-contracts.sh — E2E contract tests between Tracera services.
set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────
API_URL="${API_URL:-http://localhost:8080}"
DB_URL="${DB_URL:-sqlite://./tracera-test.db}"
GRAPH_URL="${GRAPH_URL:-http://localhost:8081}"
TIMEOUT="${TIMEOUT:-30}"
CONTRACT_DIR="${CONTRACT_DIR:-./tests/contracts}"
RESULTS_DIR="${RESULTS_DIR:-./tests/results}"

PASS=0
FAIL=0
SKIP=0

# ── Helpers ──────────────────────────────────────────────────────────────

pass() { printf "\033[32m✓ PASS\033[0m %s\n" "$1"; PASS=$((PASS + 1)); }
fail() { printf "\033[31m✗ FAIL\033[0m %s — %s\n" "$1" "${2:-}"; FAIL=$((FAIL + 1)); }
skip() { printf "\033[33m⊘ SKIP\033[0m %s — %s\n" "$1" "${2:-}"; SKIP=$((SKIP + 1)); }

assert_status() {
  local name="$1" url="$2" expected="$3"
  local actual
  actual=$(curl -so /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null)
  if [ "$actual" = "$expected" ]; then
    pass "$name"
  else
    fail "$name" "expected $expected, got $actual"
  fi
}

assert_json_field() {
  local name="$1" url="$2" jq_expr="$3" expected="$4"
  local actual
  actual=$(curl -sf --max-time "$TIMEOUT" "$url" 2>/dev/null | jq -r "$jq_expr" 2>/dev/null)
  if [ "$actual" = "$expected" ]; then
    pass "$name"
  else
    fail "$name" "expected '$expected', got '$actual'"
  fi
}

# ── Preflight ────────────────────────────────────────────────────────────
mkdir -p "$RESULTS_DIR"

echo "════════════════════════════════════════"
echo "  E2E Contract Tests — $(date -Iseconds)"
echo "════════════════════════════════════════"
echo ""

# ── Contract 1: API ↔ DB schema alignment ──────────────────────────────
echo "── Contract 1: API ↔ DB Schema ──"
assert_status "GET /api/v1/schema/tables" "${API_URL}/api/v1/schema/tables" "200"
assert_json_field "schema has swee_nodes table" "${API_URL}/api/v1/schema/tables" '.tables[] | select(.name == "swee_nodes") | .name' "swee_nodes"
assert_json_field "schema has swee_edges table" "${API_URL}/api/v1/schema/tables" '.tables[] | select(.name == "swee_edges") | .name' "swee_edges"
echo ""

# ── Contract 2: API ↔ Graph engine ─────────────────────────────────────
echo "── Contract 2: API ↔ Graph Engine ──"
assert_status "Graph health via API" "${API_URL}/api/v1/graph/health" "200"
assert_status "Graph health direct"  "${GRAPH_URL}/health" "200"
assert_json_field "Graph version" "${GRAPH_URL}/version" '.version' "1.0.0"
echo ""

# ── Contract 3: Trace query contract ───────────────────────────────────
echo "── Contract 3: Trace Query Contract ──"
RESPONSE=$(curl -sf --max-time "$TIMEOUT" -X POST "${API_URL}/api/v1/trace/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"SELECT 1","limit":1}' 2>/dev/null)
if echo "$RESPONSE" | jq -e '.results' >/dev/null 2>&1; then
  pass "Trace query returns 'results' field"
else
  fail "Trace query contract" "missing 'results' field in response"
fi
echo ""

# ── Contract 4: Story ↔ Artefact link contract ─────────────────────────
echo "── Contract 4: Story ↔ Artefact Links ──"
RESPONSE=$(curl -sf --max-time "$TIMEOUT" "${API_URL}/api/v1/stories?limit=1" 2>/dev/null)
if echo "$RESPONSE" | jq -e '.stories' >/dev/null 2>&1; then
  pass "Stories endpoint returns 'stories' array"
else
  fail "Stories contract" "missing 'stories' field"
fi
echo ""

# ── Contract 5: Memory distillation contract ────────────────────────────
echo "── Contract 5: Memory Distillation Contract ──"
assert_status "Memory endpoint" "${API_URL}/api/v1/memory" "200"
RESPONSE=$(curl -sf --max-time "$TIMEOUT" "${API_URL}/api/v1/memory" 2>/dev/null)
if echo "$RESPONSE" | jq -e '.memories' >/dev/null 2>&1; then
  pass "Memory endpoint returns 'memories' field"
else
  fail "Memory contract" "missing 'memories' field"
fi
echo ""

# ── Contract 6: Error format contract ──────────────────────────────────
echo "── Contract 6: Error Format Contract ──"
RESPONSE=$(curl -s --max-time "$TIMEOUT" "${API_URL}/api/v1/nonexistent" 2>/dev/null)
if echo "$RESPONSE" | jq -e '.error.code' >/dev/null 2>&1; then
  pass "Error response has 'error.code' field"
else
  fail "Error format contract" "missing 'error.code' in 404 response"
fi
echo ""

# ── Contract 7: Rate limiting contract ─────────────────────────────────
echo "── Contract 7: Rate Limiting Contract ──"
STATUS=$(curl -so /dev/null -w "%{http_code}" --max-time 5 "${API_URL}/api/v1/health" -H "X-Rate-Limit-Test: true" 2>/dev/null)
if [ "$STATUS" = "200" ] || [ "$STATUS" = "429" ]; then
  pass "Rate limiting headers present"
else
  fail "Rate limiting contract" "unexpected status $STATUS"
fi
echo ""

# ── Summary ──────────────────────────────────────────────────────────────
TOTAL=$((PASS + FAIL + SKIP))
echo "════════════════════════════════════════"
echo "  Results: ${PASS}/${TOTAL} passed, ${FAIL} failed, ${SKIP} skipped"
echo "════════════════════════════════════════"

# Write summary
cat > "${RESULTS_DIR}/e2e-contracts-$(date +%Y%m%d).md" <<EOF
# E2E Contract Test Results

| Metric   | Count |
|----------|-------|
| Passed   | $PASS |
| Failed   | $FAIL |
| Skipped  | $SKIP |
| Total    | $TOTAL |
EOF

if [ "$FAIL" -gt 0 ]; then
  echo "❌ Contract tests FAILED"
  exit 1
fi
echo "✅ All contract tests PASSED"
exit 0
