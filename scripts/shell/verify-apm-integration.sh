#!/usr/bin/env bash
set -euo pipefail

# Verify APM Integration Script
# Tests that OpenTelemetry tracing is properly configured and working

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Verifying APM Integration..."
echo ""

# Check 1: Environment configuration
echo "1. Checking environment configuration..."
if [ -f "$PROJECT_ROOT/.env" ]; then
    if grep -q "TRACING_ENABLED=true" "$PROJECT_ROOT/.env"; then
        echo -e "${GREEN}✓${NC} TRACING_ENABLED=true in .env"
    else
        echo -e "${YELLOW}⚠${NC} TRACING_ENABLED not set to true in .env"
        echo "  Set TRACING_ENABLED=true to enable APM"
    fi

    if grep -q "JAEGER_ENDPOINT" "$PROJECT_ROOT/.env"; then
        endpoint=$(grep "JAEGER_ENDPOINT" "$PROJECT_ROOT/.env" | cut -d= -f2)
        echo -e "${GREEN}✓${NC} JAEGER_ENDPOINT configured: $endpoint"
    else
        echo -e "${YELLOW}⚠${NC} JAEGER_ENDPOINT not configured"
        echo "  Add JAEGER_ENDPOINT=localhost:4317 to .env"
    fi
else
    echo -e "${YELLOW}⚠${NC} No .env file found"
    echo "  Copy .env.example to .env and configure"
fi
echo ""

# Check 2: Python observability module
echo "2. Checking Python observability module..."
if [ -d "$PROJECT_ROOT/src/tracertm/observability" ]; then
    echo -e "${GREEN}✓${NC} Observability module exists"

    required_files=(
        "__init__.py"
        "tracing.py"
        "instrumentation.py"
    )

    for file in "${required_files[@]}"; do
        if [ -f "$PROJECT_ROOT/src/tracertm/observability/$file" ]; then
            echo -e "${GREEN}  ✓${NC} $file present"
        else
            echo -e "${RED}  ✗${NC} $file missing"
        fi
    done
else
    echo -e "${RED}✗${NC} Observability module not found"
fi
echo ""

# Check 3: Go tracing module
echo "3. Checking Go tracing module..."
if [ -d "$PROJECT_ROOT/backend/internal/tracing" ]; then
    echo -e "${GREEN}✓${NC} Tracing module exists"

    required_files=(
        "tracer.go"
        "middleware.go"
        "database.go"
        "helpers.go"
    )

    for file in "${required_files[@]}"; do
        if [ -f "$PROJECT_ROOT/backend/internal/tracing/$file" ]; then
            echo -e "${GREEN}  ✓${NC} $file present"
        else
            echo -e "${YELLOW}  ⚠${NC} $file missing (may be optional)"
        fi
    done
else
    echo -e "${RED}✗${NC} Go tracing module not found"
fi
echo ""

# Check 4: Jaeger configuration
echo "4. Checking Jaeger configuration..."
if grep -q "jaeger:" "$PROJECT_ROOT/config/process-compose.yaml"; then
    echo -e "${GREEN}✓${NC} Jaeger configured in config/process-compose.yaml"
else
    echo -e "${RED}✗${NC} Jaeger not found in config/process-compose.yaml"
fi

if [ -f "$PROJECT_ROOT/scripts/shell/jaeger-if-not-running.sh" ]; then
    echo -e "${GREEN}✓${NC} Jaeger startup script exists"
else
    echo -e "${YELLOW}⚠${NC} Jaeger startup script missing"
fi
echo ""

# Check 5: Grafana dashboards
echo "5. Checking Grafana dashboards..."
if [ -f "$PROJECT_ROOT/deploy/monitoring/dashboards/apm-performance.json" ]; then
    echo -e "${GREEN}✓${NC} APM Performance dashboard exists"
else
    echo -e "${RED}✗${NC} APM Performance dashboard missing"
fi

if [ -f "$PROJECT_ROOT/deploy/monitoring/dashboards/distributed-tracing.json" ]; then
    echo -e "${GREEN}✓${NC} Distributed Tracing dashboard exists"
else
    echo -e "${RED}✗${NC} Distributed Tracing dashboard missing"
fi

if [ -f "$PROJECT_ROOT/deploy/monitoring/grafana/provisioning/datasources/jaeger.yml" ]; then
    echo -e "${GREEN}✓${NC} Jaeger data source configured"
else
    echo -e "${RED}✗${NC} Jaeger data source configuration missing"
fi
echo ""

# Check 6: Documentation
echo "6. Checking documentation..."
if [ -f "$PROJECT_ROOT/docs/guides/APM_INTEGRATION_GUIDE.md" ]; then
    echo -e "${GREEN}✓${NC} APM Integration Guide exists"
else
    echo -e "${RED}✗${NC} APM Integration Guide missing"
fi

if [ -f "$PROJECT_ROOT/docs/reference/APM_QUICK_REFERENCE.md" ]; then
    echo -e "${GREEN}✓${NC} APM Quick Reference exists"
else
    echo -e "${RED}✗${NC} APM Quick Reference missing"
fi
echo ""

# Check 7: Python dependencies
echo "7. Checking Python dependencies..."
if [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
    required_deps=(
        "opentelemetry-instrumentation-fastapi"
        "opentelemetry-instrumentation-sqlalchemy"
        "opentelemetry-exporter-otlp-proto-grpc"
    )

    for dep in "${required_deps[@]}"; do
        if grep -q "$dep" "$PROJECT_ROOT/pyproject.toml"; then
            echo -e "${GREEN}  ✓${NC} $dep configured"
        else
            echo -e "${RED}  ✗${NC} $dep missing"
        fi
    done
else
    echo -e "${RED}✗${NC} pyproject.toml not found"
fi
echo ""

# Check 8: Service health (if running)
echo "8. Checking service health (if running)..."

# Check Jaeger
if command -v curl &> /dev/null; then
    if curl -s http://localhost:16686 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Jaeger UI is accessible (http://localhost:16686)"
    else
        echo -e "${YELLOW}⚠${NC} Jaeger UI not accessible (service may not be running)"
        echo "  Start with: make dev"
    fi

    # Check Prometheus
    if curl -s http://localhost:9090/-/ready > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Prometheus is accessible (http://localhost:9090)"
    else
        echo -e "${YELLOW}⚠${NC} Prometheus not accessible (service may not be running)"
    fi

    # Check Grafana
    if curl -s http://localhost:3001 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Grafana is accessible (http://localhost:3001)"
    else
        echo -e "${YELLOW}⚠${NC} Grafana not accessible (service may not be running)"
    fi
else
    echo -e "${YELLOW}⚠${NC} curl not available, skipping service health checks"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "APM Integration Verification Complete!"
echo ""
echo "To use APM:"
echo "  1. Start services: make dev"
echo "  2. View traces: http://localhost:16686"
echo "  3. View dashboards: http://localhost:3001"
echo ""
echo "Documentation:"
echo "  - Integration Guide: docs/guides/APM_INTEGRATION_GUIDE.md"
echo "  - Quick Reference: docs/reference/APM_QUICK_REFERENCE.md"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
