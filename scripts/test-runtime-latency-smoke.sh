#!/usr/bin/env bash
set -euo pipefail

# Contract test for the standard-library harness. This deliberately uses a
# temporary local HTTP server so it does not require a Tracera process or data.
port="$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')"
python3 -m http.server "${port}" --bind 127.0.0.1 >/dev/null 2>&1 &
pid="$!"
trap 'kill "${pid}" 2>/dev/null || true; wait "${pid}" 2>/dev/null || true' EXIT
for _ in $(seq 1 20); do
  curl --silent --fail "http://127.0.0.1:${port}/" >/dev/null && break
  sleep 0.05
done
result="$(python3 scripts/runtime-latency-smoke.py --base-url "http://127.0.0.1:${port}" --path / --requests 8 --concurrency 2 --warmup 0 --json)"
python3 -c 'import json,sys; d=json.loads(sys.argv[1]); assert d["requests"] == 8; assert d["failures"] == 0; assert d["client_errors"] == 0; assert d["latency_ms"]["p95"] >= 0' "${result}"
echo "runtime latency harness contract: PASS"
