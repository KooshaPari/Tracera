#!/usr/bin/env bash
set -euo pipefail

cd backend

# Run golangci-lint in smaller chunks to reduce peak memory usage.
base_dir="$(pwd)"
cache_dir="${base_dir}/.gocache"
mkdir -p "${cache_dir}"
lint_cache_dir="${cache_dir}/golangci-lint"
mkdir -p "${lint_cache_dir}"
go list -f '{{.Dir}}' ./... \
  | while IFS= read -r pkg; do
      [ -z "${pkg}" ] && continue
      if [[ "${pkg}" == "${base_dir}" ]]; then
        rel="."
      elif [[ "${pkg}" == "${base_dir}/"* ]]; then
        rel="${pkg#${base_dir}/}"
      else
        rel="${pkg}"
      fi
      if [[ "${rel}" == "." ]]; then
        continue
      fi
      if [[ "${rel}" == "docs" ]]; then
        continue
      fi
      if [[ "${rel}" == "cmd/build" ]]; then
        continue
      fi
      if [[ "${rel}" == "cmd/ngs-nats-test" ]]; then
        continue
      fi
      if [[ "${rel}" == "internal/docindex" ]]; then
        continue
      fi
      if [[ "${rel}" == "internal/codeindex/sync" ]]; then
        continue
      fi
      if [[ "${rel}" == "internal/embeddings" ]]; then
        continue
      fi
      if [[ "${rel}" == "internal/graph" ]]; then
        continue
      fi
      echo "Linting ${rel}"
  env GOTOOLCHAIN=go1.25.7 GOFLAGS="-buildvcs=false" GOMAXPROCS=1 GOGC=5 GOMEMLIMIT=256MiB GOCACHE="${cache_dir}" \
    GOLANGCI_LINT_CACHE="${lint_cache_dir}" \
        golangci-lint run --timeout=10m --concurrency=1 --tests=false \
        --allow-parallel-runners --max-issues-per-linter=1 --max-same-issues=1 \
        "./${rel}"
    done
