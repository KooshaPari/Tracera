#!/usr/bin/env bash
set -euo pipefail

# Deterministic, offline regression test for the credential-drift diagnostic.
# It mocks only docker/curl and never contacts or mutates a live stack.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/tracera-health-test.XXXXXX")"
trap 'rm -rf "${tmp_dir}"' EXIT INT TERM
mkdir -p "${tmp_dir}/bin"
touch "${tmp_dir}/compose.yml" "${tmp_dir}/env"

cat >"${tmp_dir}/bin/docker" <<'EOF'
#!/usr/bin/env bash
if printf '%s\n' "$*" | grep -Fq ' ps '; then
  if [[ "${TRACERA_LEGACY_LOCAL_STACK:-0}" == "1" ]]; then
    printf '%s\n' frontend postgres tracera-server
  else
    printf '%s\n' postgres tracera-server
  fi
  exit 0
fi
if printf '%s\n' "$*" | grep -Fq ' logs '; then
  printf '%s\n' 'ERROR: password authentication failed for user "tracera"'
  exit 0
fi
exit 0
EOF
cat >"${tmp_dir}/bin/curl" <<'EOF'
#!/usr/bin/env bash
if [[ "${MOCK_CURL_FAIL:-0}" == "1" ]]; then
  exit 22
fi
case "$*" in
  */health*) printf '%s\n' '{"status":"ok"}' ;;
  */ready*) printf '%s\n' '{"status":"ready"}' ;;
  *) printf '%s\n' '200' ;;
esac
exit 0
EOF
chmod 755 "${tmp_dir}/bin/docker" "${tmp_dir}/bin/curl"

canonical_output="$({
  PATH="${tmp_dir}/bin:${PATH}" \
    TRACERA_COMPOSE_FILE="${tmp_dir}/compose.yml" \
    TRACERA_ENV_FILE="${tmp_dir}/env" \
    TRACERA_LEGACY_LOCAL_STACK=0 \
    "${repo_root}/scripts/local-stack-health.sh"
} 2>&1)"
[[ "$?" -eq 0 ]] || { printf '%s\n' "${canonical_output}" >&2; exit 1; }
printf '%s\n' "${canonical_output}" | grep -Fq 'local stack health: PASS'

set +e
output="$({
  PATH="${tmp_dir}/bin:${PATH}" \
    TRACERA_COMPOSE_FILE="${tmp_dir}/compose.yml" \
    TRACERA_ENV_FILE="${tmp_dir}/env" \
    TRACERA_LEGACY_LOCAL_STACK=1 \
    MOCK_CURL_FAIL=1 \
    "${repo_root}/scripts/local-stack-health.sh"
} 2>&1)"
status=$?
set -e

[[ "${status}" -ne 0 ]] || { echo "health test: expected failure" >&2; exit 1; }
printf '%s\n' "${output}" | grep -Fq 'likely PostgreSQL credential drift detected.'
printf '%s\n' "${output}" | grep -Fq "'<value from .env.local>'"
! printf '%s\n' "${output}" | grep -Eiq 'password authentication failed|DATABASE_URL=.*:'
echo "local-stack-health test: PASS (secret-free drift hint)"
