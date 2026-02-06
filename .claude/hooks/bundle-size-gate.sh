#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[bundle-size-gate] %s\n' "$*"
}

fail() {
  log "ERROR: $*"
  exit 1
}

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  fail "Not inside a git repository."
fi

ROOT=$(git rev-parse --show-toplevel)
DIST_DIR="${DIST_DIR:-${ROOT}/dist}"
BASELINE_FILE="${BASELINE_FILE:-${ROOT}/.claude/baselines/bundle-size.json}"
THRESHOLD_PCT="${THRESHOLD_PCT:-5}"

if [ ! -d "$DIST_DIR" ]; then
  fail "Missing dist directory: ${DIST_DIR}"
fi

if ! command -v python3 >/dev/null 2>&1; then
  fail "python3 is required to compute bundle sizes."
fi

python3 - <<'PY' "$DIST_DIR" "$BASELINE_FILE" "$THRESHOLD_PCT"
import json
import os
import sys
import time
import subprocess

DIST_DIR = sys.argv[1]
BASELINE_FILE = sys.argv[2]
THRESHOLD_PCT = float(sys.argv[3])


def dir_size(path: str) -> int:
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                total += os.path.getsize(file_path)
            except OSError:
                pass
    return total

current_total = dir_size(DIST_DIR)

try:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
except Exception:
    commit = "unknown"

os.makedirs(os.path.dirname(BASELINE_FILE), exist_ok=True)

if not os.path.exists(BASELINE_FILE):
    baseline = {
        "version": 1,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "commit": commit,
        "total_bytes": current_total,
        "dist_dir": os.path.abspath(DIST_DIR),
    }
    with open(BASELINE_FILE, "w", encoding="utf-8") as fh:
        json.dump(baseline, fh, indent=2, sort_keys=True)
    print(f"Baseline created at {BASELINE_FILE} with {current_total} bytes.")
    print("Re-run the gate after reviewing the baseline.")
    sys.exit(2)

with open(BASELINE_FILE, "r", encoding="utf-8") as fh:
    baseline = json.load(fh)

baseline_total = int(baseline.get("total_bytes", 0))
if baseline_total <= 0:
    print("Baseline total_bytes is missing or zero. Update the baseline.")
    sys.exit(2)

limit = int(baseline_total * (1 + THRESHOLD_PCT / 100.0))

print(f"Baseline total: {baseline_total} bytes")
print(f"Current total:  {current_total} bytes")
print(f"Threshold:      {THRESHOLD_PCT}% (limit {limit} bytes)")

if current_total > limit:
    delta = current_total - baseline_total
    pct = (delta / baseline_total) * 100.0
    print(f"FAIL: bundle size increased by {delta} bytes ({pct:.2f}%).")
    sys.exit(1)

print("OK: bundle size within threshold.")
PY
