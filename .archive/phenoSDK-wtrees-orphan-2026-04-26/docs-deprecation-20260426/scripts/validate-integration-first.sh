#!/bin/bash
# validate-integration-first.sh
# Quick validation script for integration-first patterns (Phases 1-3)

set -e

echo "════════════════════════════════════════════════════════════"
echo "Pheno-SDK Integration-First Validation (Phases 1-3)"
echo "════════════════════════════════════════════════════════════"
echo ""

FAILED=0
PASSED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    PASSED=$((PASSED + 1))
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    FAILED=$((FAILED + 1))
}

warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

section() {
    echo ""
    echo "────────────────────────────────────────────────────────────"
    echo "$1"
    echo "────────────────────────────────────────────────────────────"
}

# =============================================================================
# Phase 1: Core Baselines
# =============================================================================

section "Phase 1.1: Unified Registry (adapter-kit)"

if python -c "from adapter_kit import Registry; print('OK')" 2>/dev/null | grep -q "OK"; then
    pass "Registry imports successfully"
else
    fail "Registry import failed"
fi

if python -c "from adapter_kit.plugin_registry import RegistryItem; print('OK')" 2>/dev/null | grep -q "OK"; then
    pass "RegistryItem imports successfully"
else
    fail "RegistryItem import failed"
fi

# Test basic registry functionality
if python -c "
from adapter_kit import Registry

reg = Registry[str]('test')
reg.register('key', 'value')
assert reg.get('key') == 'value', 'Registry get failed'
print('OK')
" 2>/dev/null | grep -q "OK"; then
    pass "Registry basic operations work"
else
    fail "Registry basic operations failed"
fi

# Check legacy APIs still available (backward compat)
if python -c "from adapter_kit.registry import ClassRegistry; print('OK')" 2>/dev/null | grep -q "OK"; then
    pass "Legacy ClassRegistry still available (backward compat)"
else
    warn "Legacy ClassRegistry not available"
fi

section "Phase 1.3: Observability Helpers (observability-kit)"

if python -c "from observability_kit.helpers import configure_otel, configure_structlog, get_logger; print('OK')" 2>/dev/null | grep -q "OK"; then
    pass "Observability helpers import successfully"
else
    fail "Observability helpers import failed"
fi

# Test graceful degradation (without OTEL SDK)
if python -c "
from observability_kit.helpers import configure_structlog, get_logger

configure_structlog('test-service')
logger = get_logger(__name__)
logger.info('test')
print('OK')
" 2>/dev/null | grep -q "OK"; then
    pass "Structlog works without OTEL SDK (graceful degradation)"
else
    fail "Structlog graceful degradation failed"
fi

section "Phase 1.4: CLI Typer Wrappers (cli-builder-kit)"

if python -c "from cli_builder import make_typer_app; print('OK')" 2>/dev/null | grep -q "OK"; then
    pass "make_typer_app imports successfully"
else
    warn "make_typer_app import failed (Typer may not be installed)"
fi

# =============================================================================
# Phase 2: Early Adoption
# =============================================================================

section "Phase 2: Integration Validation"

if [ -f "pheno_cli/pheno_cli/typer_main.py" ]; then
    if python -c "from pheno_cli.typer_main import app; print('OK')" 2>/dev/null | grep -q "OK"; then
        pass "pheno_cli Typer integration works"
    else
        warn "pheno_cli Typer integration failed (dependencies may be missing)"
    fi
else
    warn "pheno_cli not found"
fi

if [ -f "examples/stack/fastapi_pheno_example.py" ]; then
    if python -c "import sys; sys.path.insert(0, 'examples/stack'); from fastapi_pheno_example import create_app; print('OK')" 2>/dev/null | grep -q "OK"; then
        pass "FastAPI example imports successfully"
    else
        warn "FastAPI example import failed (dependencies may be missing)"
    fi
else
    warn "FastAPI example not found"
fi

# =============================================================================
# Phase 3: Extended Integrations
# =============================================================================

section "Phase 3.1: gRPC Kit"

if python -c "from grpc_kit import create_server, create_channel, GrpcServerConfig, GrpcClientConfig; print('OK')" 2>/dev/null | grep -q "OK"; then
    pass "gRPC kit imports successfully"
else
    warn "gRPC kit import failed (grpcio may not be installed)"
fi

if python -c "from grpc_kit.interceptors import ServerTelemetryInterceptor, ClientTelemetryInterceptor; print('OK')" 2>/dev/null | grep -q "OK"; then
    pass "gRPC interceptors import successfully"
else
    warn "gRPC interceptors import failed"
fi

section "Phase 3.3: Vector-Kit Provider Matrix"

if python -c "from vector_kit import VectorStore, Document, SearchResult, InMemoryVectorStore; print('OK')" 2>/dev/null | grep -q "OK"; then
    pass "Vector-kit base types import successfully"
else
    fail "Vector-kit base types import failed"
fi

if python -c "from vector_kit import QdrantVectorStore, ChromaVectorStore, FAISSVectorStore, PineconeVectorStore, WeaviateVectorStore, PgVectorStore; print('OK')" 2>/dev/null | grep -q "OK"; then
    pass "All vector provider stubs import successfully"
else
    fail "Vector provider stubs import failed"
fi

# Test InMemory store functionality
if python -c "
import asyncio
import numpy as np
from vector_kit import InMemoryVectorStore, Document

async def test():
    store = InMemoryVectorStore()
    docs = [
        Document(id='1', text='test1', vector=np.random.rand(10)),
        Document(id='2', text='test2', vector=np.random.rand(10)),
    ]
    await store.add_documents(docs)
    query = np.random.rand(10)
    results = await store.search(query, k=2)
    assert len(results) == 2, f'Expected 2 results, got {len(results)}'
    print('OK')

asyncio.run(test())
" 2>/dev/null | grep -q "OK"; then
    pass "InMemoryVectorStore functional test passed"
else
    fail "InMemoryVectorStore functional test failed"
fi

# =============================================================================
# Documentation
# =============================================================================

section "Documentation Completeness"

DOCS=(
    "docs/adr/0001-pheno-sdk-integration-layer.md"
    "docs/adr/0002-unified-plugin-registry.md"
    "docs/adr/0003-grpc-kit.md"
    "docs/guides/getting-started-v2.md"
    "docs/guides/migration-v1-to-v2.md"
    "docs/guides/auth-consolidation.md"
    "docs/guides/quality-gates.md"
    "vector-kit/docs/VECTOR_STORE_MATRIX.md"
    "workflow-kit/docs/LOCAL_VS_DURABLE.md"
    "docs/implementation-summary-pr1-4.md"
    "docs/implementation-summary-phase2.md"
    "docs/implementation-summary-phase3.md"
    "docs/implementation-summary-phase4.md"
    "docs/IMPLEMENTATION_COMPLETE.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        pass "$(basename $doc) exists"
    else
        fail "$(basename $doc) missing"
    fi
done

# =============================================================================
# Summary
# =============================================================================

echo ""
echo "════════════════════════════════════════════════════════════"
echo "Validation Summary"
echo "════════════════════════════════════════════════════════════"
echo ""
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo ""
    echo "Integration-First patterns (Phases 1-3) are validated!"
    echo ""
    echo "Next steps:"
    echo "  1. Run full CI: .github/workflows/integration-first-ci.yml"
    echo "  2. Review: docs/IMPLEMENTATION_COMPLETE.md"
    echo "  3. Adopt: docs/guides/getting-started-v2.md"
    echo ""
    exit 0
else
    echo -e "${RED}❌ SOME CHECKS FAILED${NC}"
    echo ""
    echo "Some validations failed. This may be due to:"
    echo "  - Missing optional dependencies (grpcio, typer, etc.)"
    echo "  - Environment setup issues"
    echo ""
    echo "See above for details."
    echo ""
    exit 1
fi
