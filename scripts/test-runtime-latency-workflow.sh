#!/usr/bin/env bash
set -euo pipefail

# Keep the hosted smoke aligned with the lifecycle guarantees in
# scripts/runtime-smoke.sh: select a dynamic loopback port, retain the server
# through latency measurement, and print its log when readiness fails.
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workflow="${root}/.github/workflows/runtime-latency-smoke.yml"

fail() { echo "runtime latency workflow contract: $*" >&2; exit 1; }

[[ -f "${workflow}" ]] || fail "workflow is missing"
grep -Fq 'port="$(python3 -c' "${workflow}" || fail "workflow must select a dynamic loopback port"
grep -Fq 'TRACERA_BIND_ADDR="127.0.0.1:${port}"' "${workflow}" || fail "workflow must bind the server to its dynamic port"
grep -Fq 'log_path="${RUNNER_TEMP:-/tmp}/tracera-latency.log"' "${workflow}" || fail "workflow must keep a diagnosable server log"
grep -Fq 'kill -0 "${pid}"' "${workflow}" || fail "workflow must detect an exited server during readiness"
grep -Fq 'cat "${log_path}" >&2' "${workflow}" || fail "workflow must print the server log on readiness failure"
! grep -Fq '127.0.0.1:18080' "${workflow}" || fail "workflow must not hard-code port 18080"

echo "runtime latency workflow contract: PASS"
