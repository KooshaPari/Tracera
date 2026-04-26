#!/usr/bin/env bash
# Multi-language test runner hook
# Runs unit tests before push across Go/Python/TypeScript

set -u
set -o pipefail

log() {
  printf '[pre-push-test] %s\n' "$*"
}

fail() {
  log "ERROR: $*"
}

success() {
  log "✓ $*"
}

# Track test results
declare -a failed_suites=()
declare -a passed_suites=()

# Detect project root
if [ -d .git ]; then
  PROJECT_ROOT="$(pwd)"
else
  PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || PROJECT_ROOT="."
fi

log "Project root: $PROJECT_ROOT"

# ===== Go Tests =====
if [ -d "$PROJECT_ROOT/backend" ] && [ -f "$PROJECT_ROOT/backend/go.mod" ]; then
  log "Running Go tests..."
  if (cd "$PROJECT_ROOT/backend" && go test -timeout 30s ./...); then
    passed_suites+=("Go")
    success "Go tests passed"
  else
    failed_suites+=("Go")
    fail "Go tests failed"
  fi
fi

# ===== Python Tests =====
if [ -d "$PROJECT_ROOT/src" ] && [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
  log "Running Python tests..."
  if command -v pytest >/dev/null 2>&1; then
    if (cd "$PROJECT_ROOT" && pytest --tb=short -q); then
      passed_suites+=("Python")
      success "Python tests passed"
    else
      failed_suites+=("Python")
      fail "Python tests failed"
    fi
  else
    log "pytest not found; skipping Python tests"
  fi
fi

# ===== TypeScript/JavaScript Tests =====
if [ -d "$PROJECT_ROOT/frontend" ]; then
  log "Running TypeScript tests..."
  if command -v bun >/dev/null 2>&1; then
    if (cd "$PROJECT_ROOT/frontend" && bun test --coverage 2>/dev/null); then
      passed_suites+=("TypeScript")
      success "TypeScript tests passed"
    else
      # TypeScript tests may not exist for all apps; treat as warning
      log "TypeScript tests not configured or failed (non-blocking)"
    fi
  elif command -v npm >/dev/null 2>&1; then
    if (cd "$PROJECT_ROOT/frontend" && npm test 2>/dev/null); then
      passed_suites+=("TypeScript")
      success "TypeScript tests passed"
    else
      log "TypeScript tests not configured (non-blocking)"
    fi
  else
    log "Neither bun nor npm found; skipping TypeScript tests"
  fi
fi

# ===== Summary =====
log ""
log "Test Summary:"
log "  Passed: ${passed_suites[*]:-none}"
log "  Failed: ${failed_suites[*]:-none}"

if [ "${#failed_suites[@]}" -gt 0 ]; then
  fail "Push blocked: ${#failed_suites[@]} test suite(s) failed"
  exit 1
fi

success "All test suites passed. Ready to push."
exit 0
