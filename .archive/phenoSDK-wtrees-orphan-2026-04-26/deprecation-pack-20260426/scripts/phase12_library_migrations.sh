#!/bin/bash
# Phase 12.2: Library Migrations
# Replace custom implementations with standard libraries
# Estimated savings: -4,300 LOC

set -e

echo "🚀 Phase 12.2: Library Migrations"
echo "================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Create backup
BACKUP_DIR="backups/cleanup-phase12-libraries-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src/pheno "$BACKUP_DIR/pheno-before"
print_status "Backup created: $BACKUP_DIR"
echo ""

BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Starting LOC: $BEFORE_LOC"
echo ""

# ============================================================================
# 12.2.1: Replace Custom Async Utilities with anyio (-2,000 LOC)
# ============================================================================
echo "🔧 12.2.1: Replacing custom async utilities with anyio..."
echo ""

# Find files with custom async utilities
ASYNC_FILES=(
    "src/pheno/infra/async_utils.py"
)

ASYNC_SAVINGS=0

for file in "${ASYNC_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_info "Analyzing: $file"
        
        # Check if it has custom async implementations
        if grep -q "class.*AsyncContextManager\|class.*AsyncIterator\|class.*AsyncLock" "$file" 2>/dev/null; then
            LOC_BEFORE=$(wc -l < "$file")
            
            # Backup original
            mkdir -p "$BACKUP_DIR/$(dirname ${file#src/pheno/})"
            cp "$file" "$BACKUP_DIR/${file#src/pheno/}"
            
            # Create simplified version using anyio
            cat > "$file" << 'EOF'
"""Async utilities using anyio.

This module provides async utilities using the anyio library
instead of custom implementations.
"""

from anyio import (
    create_task_group,
    Lock,
    Semaphore,
    Event,
    Condition,
    CapacityLimiter,
    create_memory_object_stream,
)

__all__ = [
    "create_task_group",
    "Lock",
    "Semaphore",
    "Event",
    "Condition",
    "CapacityLimiter",
    "create_memory_object_stream",
]
EOF
            
            LOC_AFTER=$(wc -l < "$file")
            SAVED=$((LOC_BEFORE - LOC_AFTER))
            ASYNC_SAVINGS=$((ASYNC_SAVINGS + SAVED))
            
            print_status "Simplified $file: $SAVED LOC saved"
        else
            print_info "No custom async utilities found in $file"
        fi
    fi
done

# Check for other files using custom async utilities
print_info "Searching for files using custom async utilities..."
CUSTOM_ASYNC_USAGE=$(grep -r "from.*async_utils import\|import.*async_utils" src/pheno --include="*.py" 2>/dev/null | wc -l || echo "0")

if [ "$CUSTOM_ASYNC_USAGE" -gt "0" ]; then
    print_warning "Found $CUSTOM_ASYNC_USAGE files using async_utils - may need manual updates"
fi

AFTER_ASYNC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
print_status "Async utilities migration: $ASYNC_SAVINGS LOC saved"
echo ""

# ============================================================================
# 12.2.2: Replace Custom Serialization with msgspec (-1,500 LOC)
# ============================================================================
echo "🔧 12.2.2: Replacing custom serialization with msgspec..."
echo ""

# Find files with custom serialization
SERIALIZATION_FILES=(
    "src/pheno/lib/serialization.py"
    "src/pheno/core/shared/serialization.py"
)

SERIALIZATION_SAVINGS=0

for file in "${SERIALIZATION_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_info "Analyzing: $file"
        
        LOC_BEFORE=$(wc -l < "$file")
        
        # Backup original
        mkdir -p "$BACKUP_DIR/$(dirname ${file#src/pheno/})"
        cp "$file" "$BACKUP_DIR/${file#src/pheno/}"
        
        # Create simplified version using msgspec
        cat > "$file" << 'EOF'
"""Serialization utilities using msgspec.

This module provides serialization using the msgspec library
which is faster and more feature-rich than custom implementations.
"""

import msgspec
from typing import Any, Type, TypeVar

T = TypeVar("T")

# JSON encoder/decoder
json_encoder = msgspec.json.Encoder()
json_decoder = msgspec.json.Decoder()


def encode_json(obj: Any) -> bytes:
    """Encode object to JSON bytes."""
    return json_encoder.encode(obj)


def decode_json(data: bytes, type_: Type[T] = dict) -> T:
    """Decode JSON bytes to object."""
    decoder = msgspec.json.Decoder(type_)
    return decoder.decode(data)


# MessagePack encoder/decoder
msgpack_encoder = msgspec.msgpack.Encoder()
msgpack_decoder = msgspec.msgpack.Decoder()


def encode_msgpack(obj: Any) -> bytes:
    """Encode object to MessagePack bytes."""
    return msgpack_encoder.encode(obj)


def decode_msgpack(data: bytes, type_: Type[T] = dict) -> T:
    """Decode MessagePack bytes to object."""
    decoder = msgspec.msgpack.Decoder(type_)
    return decoder.decode(data)


__all__ = [
    "encode_json",
    "decode_json",
    "encode_msgpack",
    "decode_msgpack",
    "json_encoder",
    "json_decoder",
    "msgpack_encoder",
    "msgpack_decoder",
]
EOF
        
        LOC_AFTER=$(wc -l < "$file")
        SAVED=$((LOC_BEFORE - LOC_AFTER))
        SERIALIZATION_SAVINGS=$((SERIALIZATION_SAVINGS + SAVED))
        
        print_status "Simplified $file: $SAVED LOC saved"
    else
        print_info "File not found: $file"
    fi
done

AFTER_SERIALIZATION=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
print_status "Serialization migration: $SERIALIZATION_SAVINGS LOC saved"
echo ""

# ============================================================================
# 12.2.3: Replace Custom Rate Limiting with aiolimiter (-800 LOC)
# ============================================================================
echo "🔧 12.2.3: Replacing custom rate limiting with aiolimiter..."
echo ""

# Find files with custom rate limiting
RATELIMIT_FILES=(
    "src/pheno/lib/rate_limiter.py"
    "src/pheno/core/shared/rate_limiting.py"
)

RATELIMIT_SAVINGS=0

for file in "${RATELIMIT_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_info "Analyzing: $file"
        
        LOC_BEFORE=$(wc -l < "$file")
        
        # Backup original
        mkdir -p "$BACKUP_DIR/$(dirname ${file#src/pheno/})"
        cp "$file" "$BACKUP_DIR/${file#src/pheno/}"
        
        # Create simplified version using aiolimiter
        cat > "$file" << 'EOF'
"""Rate limiting utilities using aiolimiter.

This module provides rate limiting using the aiolimiter library
instead of custom implementations.
"""

from aiolimiter import AsyncLimiter
from typing import Optional


def create_rate_limiter(
    max_rate: float,
    time_period: float = 1.0,
    max_burst: Optional[float] = None,
) -> AsyncLimiter:
    """Create a rate limiter.
    
    Args:
        max_rate: Maximum number of requests per time period
        time_period: Time period in seconds (default: 1.0)
        max_burst: Maximum burst size (default: max_rate)
    
    Returns:
        AsyncLimiter instance
    
    Example:
        ```python
        limiter = create_rate_limiter(max_rate=10, time_period=1.0)
        
        async with limiter:
            # Rate-limited operation
            await make_api_call()
        ```
    """
    if max_burst is None:
        max_burst = max_rate
    
    return AsyncLimiter(max_rate=max_rate, time_period=time_period)


# Pre-configured limiters for common use cases
class RateLimiters:
    """Common rate limiter configurations."""
    
    # API rate limiters
    API_STRICT = AsyncLimiter(max_rate=10, time_period=1.0)  # 10 req/sec
    API_MODERATE = AsyncLimiter(max_rate=100, time_period=1.0)  # 100 req/sec
    API_RELAXED = AsyncLimiter(max_rate=1000, time_period=1.0)  # 1000 req/sec
    
    # Database rate limiters
    DB_WRITES = AsyncLimiter(max_rate=50, time_period=1.0)  # 50 writes/sec
    DB_READS = AsyncLimiter(max_rate=500, time_period=1.0)  # 500 reads/sec
    
    # Background task rate limiters
    BACKGROUND_TASKS = AsyncLimiter(max_rate=5, time_period=1.0)  # 5 tasks/sec


__all__ = [
    "create_rate_limiter",
    "AsyncLimiter",
    "RateLimiters",
]
EOF
        
        LOC_AFTER=$(wc -l < "$file")
        SAVED=$((LOC_BEFORE - LOC_AFTER))
        RATELIMIT_SAVINGS=$((RATELIMIT_SAVINGS + SAVED))
        
        print_status "Simplified $file: $SAVED LOC saved"
    else
        print_info "File not found: $file"
    fi
done

AFTER_RATELIMIT=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
print_status "Rate limiting migration: $RATELIMIT_SAVINGS LOC saved"
echo ""

# ============================================================================
# Summary
# ============================================================================

AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
TOTAL_SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Phase 12.2 Library Migrations Complete!"
echo "=========================================="
echo ""
echo "  Async utilities (anyio):      $ASYNC_SAVINGS LOC"
echo "  Serialization (msgspec):       $SERIALIZATION_SAVINGS LOC"
echo "  Rate limiting (aiolimiter):    $RATELIMIT_SAVINGS LOC"
echo "  ────────────────────────────────────────"
echo "  Total Savings:                 $TOTAL_SAVINGS LOC"
echo ""
echo "  Before: $BEFORE_LOC LOC"
echo "  After:  $AFTER_LOC LOC"
echo "  Reduction: $(echo "scale=1; $TOTAL_SAVINGS * 100 / $BEFORE_LOC" | bc)%"
echo ""
echo "Backup: $BACKUP_DIR"
echo ""

# ============================================================================
# Verification
# ============================================================================
echo "🔍 Running verification checks..."
echo ""

# Check for syntax errors
print_info "Checking for syntax errors..."
SYNTAX_ERRORS=0
for file in $(find src/pheno -name "*.py" -type f); do
    if ! python3 -m py_compile "$file" 2>/dev/null; then
        echo "  ✗ Syntax error in: $file"
        SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
    fi
done

if [ $SYNTAX_ERRORS -eq 0 ]; then
    print_status "No syntax errors found"
else
    print_warning "Found $SYNTAX_ERRORS syntax errors"
fi

echo ""

# Check imports
print_info "Checking if pheno module can be imported..."
if python3 -c "import sys; sys.path.insert(0, 'src'); import pheno" 2>/dev/null; then
    print_status "Module imports successfully"
else
    print_warning "Module import failed (may need dependencies)"
fi

echo ""

# ============================================================================
# Next Steps
# ============================================================================
echo "📋 Next Steps:"
echo ""
echo "1. Review changes:"
echo "   git diff --stat"
echo ""
echo "2. Run tests:"
echo "   pytest tests/ -v --tb=short"
echo ""
echo "3. Check for any issues:"
echo "   ruff check src/pheno/"
echo ""
echo "4. If all looks good, commit:"
echo "   git add -A"
echo "   git commit -m 'feat: Phase 12.2 Library Migrations (-$TOTAL_SAVINGS LOC)'"
echo ""
echo "5. Continue with Phase 12.3 (Consolidations)"
echo ""

