#!/usr/bin/env bash
# run-loadtest.sh — Run k6 load tests against the Tracera API.
set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────
BASE_URL="${BASE_URL:-http://localhost:8080}"
TEST_DIR="${TEST_DIR:-./loadtest}"
RESULTS_DIR="${RESULTS_DIR:-./loadtest/results}"
DURATION="${DURATION:-2m}"
VUS="${VUS:-10}"
THRESHOLD_P95="${THRESHOLD_P95:-500}"

# ── Preflight ────────────────────────────────────────────────────────────
command -v k6 >/dev/null 2>&1 || { echo "Error: k6 not installed. Install from https://k6.io"; exit 1; }
mkdir -p "$RESULTS_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SUMMARY_FILE="${RESULTS_DIR}/loadtest-${TIMESTAMP}.md"

echo "# Load Test Results — $(date -Iseconds)" > "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "- **Base URL:** $BASE_URL" >> "$SUMMARY_FILE"
echo "- **Duration:** $DURATION" >> "$SUMMARY_FILE"
echo "- **Virtual Users:** $VUS" >> "$SUMMARY_FILE"
echo "- **P95 Threshold:** ${THRESHOLD_P95}ms" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

# ── Run each load test scenario ──────────────────────────────────────────
SCENARIOS=(
  "smoke:smoke.js"
  "stress:stress.js"
  "graph-traversal:graph_traversal.js"
  "trace-query:trace_query.js"
)

EXIT_CODE=0
for scenario in "${SCENARIOS[@]}"; do
  NAME="${scenario%%:*}"
  FILE="${scenario##*:}"
  SCRIPT="${TEST_DIR}/${FILE}"

  if [ ! -f "$SCRIPT" ]; then
    echo "⚠ Skipping $NAME — $SCRIPT not found"
    echo "## $NAME — SKIPPED (script not found)" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"
    continue
  fi

  echo "── Running: $NAME ──"
  OUTPUT_JSON="${RESULTS_DIR}/${NAME}-${TIMESTAMP}.json"

  k6 run \
    --env BASE_URL="$BASE_URL" \
    --env DURATION="$DURATION" \
    --env VUS="$VUS" \
    --out json="$OUTPUT_JSON" \
    --summary-export="${RESULTS_DIR}/${NAME}-summary.json" \
    "$SCRIPT" 2>&1 | tee -a "${RESULTS_DIR}/${NAME}-stdout.log"

  k6_EXIT=$?
  if [ $k6_EXIT -ne 0 ]; then
    echo "❌ $NAME failed (exit $k6_EXIT)"
    EXIT_CODE=1
  else
    echo "✓ $NAME passed"
  fi

  # Append summary to markdown report
  echo "## $NAME" >> "$SUMMARY_FILE"
  echo '```' >> "$SUMMARY_FILE"
  if [ -f "${RESULTS_DIR}/${NAME}-summary.json" ]; then
    python3 -c "
  import json
  with open('${RESULTS_DIR}/${NAME}-summary.json') as f:
      data = json.load(f)
  metrics = data.get('metrics', {})
  for key in ['http_req_duration', 'http_req_failed', 'http_reqs']:
      if key in metrics:
          v = metrics[key]
          if 'avg' in v:
              print(f'{key}: avg={v[\"avg\"]:.1f}ms p95={v.get(\"p(95)\", 0):.1f}ms')
          elif 'passes' in v:
              print(f'{key}: passes={v[\"passes\"]} fails={v.get(\"fails\", 0)}')
          elif 'count' in v:
              print(f'{key}: count={v[\"count\"]}')
  " >> "$SUMMARY_FILE" 2>/dev/null || echo "(summary parse failed)" >> "$SUMMARY_FILE"
  fi
  echo '```' >> "$SUMMARY_FILE"
  echo "" >> "$SUMMARY_FILE"
done

echo ""
echo "════════════════════════════════════════"
echo "  Report: $SUMMARY_FILE"
echo "════════════════════════════════════════"
exit $EXIT_CODE
