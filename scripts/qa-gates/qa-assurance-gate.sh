#!/usr/bin/env bash
set -euo pipefail

violations=()

if ! find tests -type f -name 'test_*.py' -print -quit | grep -q .; then
  violations+=("no Python test files found under tests/")
fi

if [[ -f "Cargo.toml" ]] && ! find . -path './target' -prune -o -type f -name '*.rs' -print -quit | grep -q .; then
  violations+=("Cargo.toml exists but no Rust source files were found")
fi

if [[ -f "pyproject.toml" ]] && ! find . \
  -path './.venv' -prune -o \
  -path './target' -prune -o \
  -type f -name '*.py' -print -quit | grep -q .; then
  violations+=("pyproject.toml exists but no Python source files were found")
fi

if (( ${#violations[@]} > 0 )); then
  printf 'qa-assurance-gate violations:\n' >&2
  printf ' - %s\n' "${violations[@]}" >&2
  exit 1
fi

echo "qa-assurance-gate passed"
