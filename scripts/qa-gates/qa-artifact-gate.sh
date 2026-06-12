#!/usr/bin/env bash
set -euo pipefail

violations=()

required_paths=(
  ".github/workflows"
  "docs"
  "tests"
  "pyproject.toml"
  "Cargo.toml"
)

for path in "${required_paths[@]}"; do
  if [[ ! -e "${path}" ]]; then
    violations+=("missing required QA artifact path: ${path}")
  fi
done

if [[ ! -f ".github/workflows/governance-gates.yml" ]]; then
  violations+=("missing governance gate workflow")
fi

if (( ${#violations[@]} > 0 )); then
  printf 'qa-artifact-gate violations:\n' >&2
  printf ' - %s\n' "${violations[@]}" >&2
  exit 1
fi

echo "qa-artifact-gate passed"
