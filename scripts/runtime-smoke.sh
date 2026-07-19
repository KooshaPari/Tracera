#!/usr/bin/env bash
set -euo pipefail

# Secret-free local runtime smoke.  Uses an ephemeral SQLite database and the
# checked-in frontend bundle; no network or production credentials required.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
server_bin="${TRACERA_SERVER_BIN:-${repo_root}/target/debug/tracera-server}"
frontend_dist="${TRACERA_FRONTEND_DIST:-${repo_root}/frontend/dist}"
if [[ -n "${TRACERA_SMOKE_PORT:-}" ]]; then
  port="${TRACERA_SMOKE_PORT}"
else
  # Ask the kernel for a free loopback port to avoid colliding with a local
  # developer server or another parallel smoke invocation.
  port="$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')"
fi
tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/tracera-runtime-smoke.XXXXXX")"
db_path="${tmp_dir}/tracera.db"
log_path="${tmp_dir}/server.log"
pid=""

cleanup() {
  if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
    kill "${pid}" 2>/dev/null || true
    wait "${pid}" 2>/dev/null || true
  fi
  rm -rf "${tmp_dir}"
}
trap cleanup EXIT INT TERM

[[ -x "${server_bin}" ]] || { echo "runtime smoke: missing executable: ${server_bin}" >&2; exit 1; }
[[ -f "${frontend_dist}/index.html" ]] || { echo "runtime smoke: missing frontend bundle: ${frontend_dist}/index.html" >&2; exit 1; }

# SQLx's absolute SQLite form is sqlite:///absolute/path (the path already
# begins with '/', so do not add a fourth slash).
DATABASE_URL="sqlite://${db_path}?mode=rwc" \
TRACERA_BIND_ADDR="127.0.0.1:${port}" \
TRACERA_FRONTEND_DIST="${frontend_dist}" \
RUST_LOG="tracera_server=warn" \
  "${server_bin}" >"${log_path}" 2>&1 &
pid="$!"

for _ in $(seq 1 50); do
  if curl --silent --show-error --fail "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.1
done

if ! health="$(curl --silent --show-error --fail "http://127.0.0.1:${port}/health")"; then
  echo "runtime smoke: server did not become ready (log: ${log_path})" >&2
  cat "${log_path}" >&2
  exit 1
fi
ready="$(curl --silent --show-error --fail "http://127.0.0.1:${port}/ready")"
evidence="$(curl --silent --show-error --fail "http://127.0.0.1:${port}/evidence")"
index_status="$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' "http://127.0.0.1:${port}/")"
headers="$(curl --silent --show-error --dump-header - "http://127.0.0.1:${port}/health")"

[[ "${health}" == *'"status":"ok"'* ]] || { echo "runtime smoke: /health failed: ${health}" >&2; exit 1; }
[[ "${ready}" == *'"status":"ready"'* ]] || { echo "runtime smoke: /ready failed: ${ready}" >&2; exit 1; }
[[ "${evidence}" == '[]' || "${evidence}" == *'"items"'* ]] || { echo "runtime smoke: /evidence failed: ${evidence}" >&2; exit 1; }
[[ "${index_status}" == "200" ]] || { echo "runtime smoke: frontend fallback returned ${index_status}" >&2; exit 1; }
printf '%s\n' "${headers}" | grep -Eiq '^x-content-type-options:[[:space:]]*nosniff' || {
  echo "runtime smoke: security header missing" >&2
  exit 1
}

echo "runtime smoke: PASS (health, ready, evidence, frontend, headers; db=${db_path})"
