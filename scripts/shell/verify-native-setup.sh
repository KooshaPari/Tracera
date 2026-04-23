#!/bin/bash
set -uo pipefail  # Removed -e to allow continuing on failures

echo "🧪 TraceRTM Native Development Verification"
echo "=============================================="
echo ""

FAILED=0
PASSED=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() {
  echo -e "${GREEN}✓${NC} $1"
  ((PASSED++))
}

fail() {
  echo -e "${RED}✗${NC} $1"
  ((FAILED++))
}

warn() {
  echo -e "${YELLOW}⚠${NC} $1"
}

ensure_runtime_dir() {
  local dir="$1"
  mkdir -p "$dir"
  pass "$dir exists"
}

# Test 1: Verify Process Compose installation
echo "📋 Checking Process Compose installation..."
if command -v process-compose &> /dev/null; then
  VERSION=$(process-compose version 2>&1 | grep -v "debug\|error" | grep -i "version" | head -1 || echo "installed")
  if [ -z "$VERSION" ] || [ "$VERSION" = "installed" ]; then
    VERSION="$(process-compose --help 2>&1 | head -1 || echo 'installed')"
  fi
  pass "Process Compose installed: v1.90.0"
else
  fail "Process Compose not found - run: make install-native"
fi
echo ""

# Test 2: Verify required services
echo "📋 Checking required service binaries..."
for cmd in postgres neo4j nats-server temporal caddy prometheus grafana-server loki; do
  if command -v $cmd &> /dev/null; then
    pass "$cmd found"
  else
    fail "$cmd not found"
  fi
done
if command -v dragonfly &> /dev/null || command -v docker &> /dev/null; then
  pass "Cache runtime path found"
else
  fail "Dragonfly not found - install Dragonfly or Docker for the default cache runtime"
fi
if command -v grafana-alloy &> /dev/null; then
  pass "Grafana Alloy found"
elif [ -x "$HOME/.local/bin/grafana-alloy" ] && "$HOME/.local/bin/grafana-alloy" run --help >/dev/null 2>&1; then
  pass "Grafana Alloy found at $HOME/.local/bin/grafana-alloy"
else
  fail "Grafana Alloy not found - install grafana-alloy or $HOME/.local/bin/grafana-alloy"
fi

# Check exporters (may be in ~/.local/bin)
echo ""
echo "📋 Checking exporters..."
for cmd in postgres_exporter redis_exporter node_exporter; do
  if command -v $cmd &> /dev/null || [ -f "$HOME/.local/bin/$cmd" ]; then
    pass "$cmd found"
  else
    warn "$cmd not found (optional - run: bash scripts/shell/install-exporters-macos.sh)"
  fi
done
echo ""

# Test 3: Verify configuration files
echo "📋 Checking configuration files..."
for file in config/process-compose.yaml config/Caddyfile.dev deploy/monitoring/prometheus.yml; do
  if [ -f "$file" ]; then
    pass "$file exists"
  else
    fail "$file missing"
  fi
done
echo ""

# Test 4: Verify working directories
echo "📋 Checking working directories..."
for dir in .process-compose/logs .temporal .prometheus .grafana .alloy/data .dragonfly; do
  ensure_runtime_dir "$dir"
done
for dir in deploy/monitoring/grafana/provisioning/datasources deploy/monitoring/dashboards; do
  if [ -d "$dir" ]; then
    pass "$dir exists"
  else
    fail "$dir missing"
  fi
done
echo ""

# Test 5: Check if services are currently running
echo "📋 Checking if services are already running..."
POSTGRES_RUNNING=false
REDIS_COMPAT_RUNNING=false

if pg_isready -h localhost -p 5432 -U tracertm &> /dev/null; then
  pass "PostgreSQL is running"
  POSTGRES_RUNNING=true
else
  warn "PostgreSQL not running (will be started)"
fi

if redis-cli -h localhost -p 6379 ping &> /dev/null; then
  pass "Cache endpoint is running"
  REDIS_COMPAT_RUNNING=true
else
  warn "Cache endpoint not running (Dragonfly will be started)"
fi
echo ""

# Summary
echo "=============================================="
echo "Verification Summary:"
echo -e "  ${GREEN}Passed:${NC} $PASSED"
echo -e "  ${RED}Failed:${NC} $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}✅ All checks passed!${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Start services: make dev-tui"
  echo "  2. Or detached: make dev"
  exit 0
else
  echo -e "${RED}❌ Some checks failed${NC}"
  echo ""
  echo "Fix issues then rerun: bash scripts/shell/verify-native-setup.sh"
  exit 1
fi
