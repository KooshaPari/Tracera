#!/usr/bin/env bash
# Emit PR-scoped unit test paths (one per line) for pytest.
set -euo pipefail

base="${1:?base ref required}"
git fetch --no-tags --depth=1 origin "$base" 2>/dev/null || true

shopt -s globstar nullglob
declare -A seen=()
tests=()

add_test() {
  local f="$1"
  [[ -n "$f" && -f "$f" && -z "${seen[$f]+x}" ]] || return
  seen[$f]=1
  tests+=("$f")
}

while IFS= read -r f; do
  case "$f" in
    tests/unit/*/test_*.py | tests/unit/test_*.py)
      add_test "$f"
      ;;
  esac
done < <(git diff --name-only "$base"...HEAD -- '*.py' || true)

if ((${#tests[@]} == 0)); then
  tests=(
    tests/unit/api/test_trace_matrix_export.py
    tests/unit/services/test_perf_optimizations.py
  )
fi

printf '%s\n' "${tests[@]}"
