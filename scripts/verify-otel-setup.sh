#!/bin/bash

# OpenTelemetry Setup Verification Script
# This script verifies that OpenTelemetry instrumentation is properly configured
# in the TraceRTM Go backend.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "🔍 Verifying OpenTelemetry Setup..."
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
        return 1
    fi
}

# 1. Check if OpenTelemetry dependencies are in go.mod
echo "1️⃣  Checking OpenTelemetry dependencies..."
cd "$BACKEND_DIR"

if grep -q "go.opentelemetry.io/otel" go.mod; then
    check_status "OTel core package found"
else
    echo -e "${RED}✗ OTel core package not found${NC}"
    exit 1
fi

if grep -q "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc" go.mod; then
    check_status "OTel OTLP gRPC exporter found"
else
    echo -e "${RED}✗ OTel OTLP gRPC exporter not found${NC}"
    exit 1
fi

if grep -q "go.opentelemetry.io/contrib/instrumentation/github.com/labstack/echo/otelecho" go.mod; then
    check_status "OTel Echo instrumentation found"
else
    echo -e "${RED}✗ OTel Echo instrumentation not found${NC}"
    exit 1
fi

echo ""

# 2. Check if tracing package exists and has required files
echo "2️⃣  Checking tracing package structure..."

TRACING_PACKAGE="$BACKEND_DIR/internal/tracing"

if [ -d "$TRACING_PACKAGE" ]; then
    check_status "Tracing package directory exists"
else
    echo -e "${RED}✗ Tracing package directory not found${NC}"
    exit 1
fi

required_files=(
    "tracer.go"
    "middleware.go"
    "grpc.go"
    "helpers.go"
    "context.go"
)

for file in "${required_files[@]}"; do
    if [ -f "$TRACING_PACKAGE/$file" ]; then
        check_status "File: $file"
    else
        echo -e "${RED}✗ File not found: $file${NC}"
        exit 1
    fi
done

echo ""

# 3. Check if gRPC server has tracing imports and instrumentation
echo "3️⃣  Checking gRPC server instrumentation..."

GRPC_SERVER="$BACKEND_DIR/internal/grpc/server.go"

if grep -q '"github.com/kooshapari/tracertm-backend/internal/tracing"' "$GRPC_SERVER"; then
    check_status "Tracing import in gRPC server"
else
    echo -e "${YELLOW}⚠ Tracing import not found in gRPC server${NC}"
fi

if grep -q "tracing.UnaryServerInterceptor()" "$GRPC_SERVER"; then
    check_status "Unary interceptor registered"
else
    echo -e "${RED}✗ Unary interceptor not registered${NC}"
    exit 1
fi

if grep -q "tracing.StreamServerInterceptor()" "$GRPC_SERVER"; then
    check_status "Stream interceptor registered"
else
    echo -e "${RED}✗ Stream interceptor not registered${NC}"
    exit 1
fi

echo ""

# 4. Check if tracer is initialized
echo "4️⃣  Checking tracer initialization..."

if grep -q "InitTracer" "$BACKEND_DIR/internal/infrastructure/infrastructure.go"; then
    check_status "Tracer initialization in infrastructure"
else
    echo -e "${RED}✗ Tracer initialization not found${NC}"
    exit 1
fi

echo ""

# 5. Verify Go code compiles
echo "5️⃣  Verifying Go code compilation..."

cd "$BACKEND_DIR"

if go build ./internal/tracing > /tmp/tracing_build.log 2>&1; then
    check_status "Tracing package compiles successfully"
else
    echo -e "${RED}✗ Compilation errors in tracing package${NC}"
    cat /tmp/tracing_build.log
    exit 1
fi

if go build ./internal/grpc > /tmp/grpc_build.log 2>&1; then
    check_status "gRPC package compiles successfully"
else
    echo -e "${RED}✗ Compilation errors in gRPC package${NC}"
    cat /tmp/grpc_build.log
    exit 1
fi

echo ""

# 6. Run tracing tests
echo "6️⃣  Running tracing tests..."

if go test -v ./internal/tracing/... -timeout 10s 2>&1 | grep -q "FAIL"; then
    echo -e "${RED}✗ Some tracing tests failed${NC}"
    exit 1
else
    TEST_COUNT=$(go test -v ./internal/tracing/... -timeout 10s 2>&1 | grep "^=== RUN" | wc -l)
    check_status "All tracing tests pass ($TEST_COUNT tests)"
fi

echo ""

# 7. Check documentation
echo "7️⃣  Checking documentation..."

DOC_FILE="$PROJECT_ROOT/docs/guides/OTEL_GO_SETUP.md"

if [ -f "$DOC_FILE" ]; then
    check_status "Setup guide exists"

    if grep -q "OpenTelemetry" "$DOC_FILE"; then
        check_status "Setup guide contains OpenTelemetry content"
    fi
else
    echo -e "${YELLOW}⚠ Setup guide not found at $DOC_FILE${NC}"
fi

echo ""

# 8. Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ OpenTelemetry Setup Verification Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Print next steps
echo "📋 Next Steps:"
echo ""
echo "1. Start the shared collector stack (optional, for viewing traces):"
echo "   make dev"
echo ""
echo "2. Set environment variables:"
echo "   export PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT=127.0.0.1:4317"
echo "   export TRACING_ENVIRONMENT=development"
echo ""
echo "3. Start the backend:"
echo "   cd backend && go run main.go"
echo ""
echo "4. Make API requests to generate traces:"
echo "   curl http://localhost:8080/api/v1/health"
echo ""
echo "5. View traces in Grafana:"
echo "   http://localhost:3000"
echo ""
echo "📖 Documentation:"
echo "   $DOC_FILE"
echo ""
