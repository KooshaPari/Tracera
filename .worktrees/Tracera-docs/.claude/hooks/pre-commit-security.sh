#!/usr/bin/env bash
set -u
set -o pipefail

log() {
  printf '[pre-commit-security] %s\n' "$*"
}

fail() {
  log "ERROR: $*"
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    missing+=("$cmd")
  fi
}

run_check() {
  local name="$1"
  shift
  log "Running ${name}..."
  if "$@"; then
    log "${name}: OK"
  else
    log "${name}: FAIL"
    failures+=("$name")
  fi
}

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  fail "Not inside a git repository."
  exit 2
fi

missing=()
require_cmd trivy
require_cmd ggshield
require_cmd git
git_secrets_cmd=()
if command -v git-secrets >/dev/null 2>&1; then
  git_secrets_cmd=(git-secrets)
elif git secrets --version >/dev/null 2>&1; then
  git_secrets_cmd=(git secrets)
else
  missing+=("git-secrets")
fi

if [ "${#missing[@]}" -gt 0 ]; then
  fail "Missing required tools: ${missing[*]}"
  fail "Install dependencies before committing."
  exit 2
fi

failures=()

run_check "Trivy filesystem scan (CRITICAL/HIGH)" \
  trivy fs --exit-code 1 --severity CRITICAL,HIGH --no-progress --quiet .

run_check "GitGuardian secret detection" \
  ggshield secret scan repo .

run_check "git-secrets scan" \
  "${git_secrets_cmd[@]}" --scan -r .

if [ "${#failures[@]}" -gt 0 ]; then
  fail "Security checks failed: ${failures[*]}"
  exit 1
fi

log "All security checks passed."
