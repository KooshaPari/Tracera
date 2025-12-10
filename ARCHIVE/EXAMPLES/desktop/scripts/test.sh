#!/bin/bash

# Test script for TraceRTM Desktop
# Runs both Rust and TypeScript tests

set -e

echo "================================================"
echo "TraceRTM Desktop - Test Suite"
echo "================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

function log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Rust tests
log_info "Running Rust tests..."
cd src-tauri
cargo test --all-features
cd ..

# TypeScript/React tests (if configured)
if [ -f "package.json" ]; then
    log_info "Running TypeScript tests..."
    if grep -q "\"test\":" package.json; then
        npm test
    else
        log_info "No TypeScript tests configured"
    fi
fi

log_info "All tests passed!"
