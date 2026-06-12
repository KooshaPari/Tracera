#!/usr/bin/env bash
set -euo pipefail

violations=()

temporal_docs="$(find . \
  -path './.git' -prune -o \
  -path './.venv' -prune -o \
  -path './target' -prune -o \
  -type f -name '*.md' \
  | grep -E '(^|/)(SUMMARY|STATUS|FINAL|COMPLETE|CHECKLIST|REPORT|.*(_OLD|_NEW|_DRAFT|_FINAL|_V[0-9]+)\.md$)' || true)"

if [[ -n "${temporal_docs}" ]]; then
  violations+=("temporal markdown artifacts found: ${temporal_docs//$'\n'/, }")
fi

tracked_files="$(git ls-files '*.py' '*.rs' '*.toml' '*.md')"
placeholder_hits=""
if [[ -n "${tracked_files}" ]]; then
  placeholder_hits="$(printf '%s\n' "${tracked_files}" \
    | grep -Ev '(^|/)(node_modules|target|\.venv|\.mypy_cache|\.pytest_cache)/' \
    | xargs grep -nE 'TODO:|FIXME:|HACK:|not implemented' || true)"
fi

if [[ -n "${placeholder_hits}" ]]; then
  violations+=("temporary implementation markers found")
  printf '%s\n' "${placeholder_hits}" >&2
fi

if (( ${#violations[@]} > 0 )); then
  printf 'antipattern-detect violations:\n' >&2
  printf ' - %s\n' "${violations[@]}" >&2
  exit 1
fi

echo "antipattern-detect passed"
