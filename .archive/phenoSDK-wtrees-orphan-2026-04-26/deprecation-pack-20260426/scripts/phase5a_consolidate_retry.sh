#!/bin/bash
# Phase 5a: Consolidate Retry Logic
# Replace custom retry implementations with tenacity

set -e

echo "🔧 Phase 5a: Consolidate Retry Logic"
echo "====================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="backups/cleanup-phase5a-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src/pheno/resilience "$BACKUP_DIR/"
cp -r src/pheno/dev/http "$BACKUP_DIR/"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Count LOC before
BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Before: $BEFORE_LOC LOC"
echo ""

# Delete custom retry files
echo "🗑️  Deleting custom retry implementations..."
echo ""

FILES_TO_DELETE=(
    "src/pheno/resilience/retry.py"
    "src/pheno/dev/http/retries.py"
)

DELETED_LOC=0

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        DELETED_LOC=$((DELETED_LOC + LOC))
        rm "$file"
        echo "  ✓ Deleted: $file ($LOC LOC)"
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Deleted $DELETED_LOC LOC"
echo ""

# Update resilience/__init__.py
echo "📝 Updating src/pheno/resilience/__init__.py..."
cat > src/pheno/resilience/__init__.py << 'EOF'
"""
Resilience patterns and utilities.

For retry logic, use tenacity directly or pheno.utils.retry:
    from pheno.utils.retry import standard_retry, db_retry, api_retry
    from tenacity import retry, stop_after_attempt, wait_exponential
"""

from .bulkhead import Bulkhead, BulkheadConfig
from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from .error_handling import ErrorCategorizer, ErrorHandler
from .health import (
    HealthCheck,
    HealthChecker,
    HealthConfig,
    HealthMonitor,
    HealthStatus,
)

__all__ = [
    "Bulkhead",
    "BulkheadConfig",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "ErrorCategorizer",
    "ErrorHandler",
    "HealthCheck",
    "HealthChecker",
    "HealthConfig",
    "HealthMonitor",
    "HealthStatus",
]
EOF
print_status "Updated resilience/__init__.py"
echo ""

# Count LOC after
AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 After: $AFTER_LOC LOC"
echo ""

# Calculate savings
SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Phase 5a Complete!"
echo "===================="
echo ""
echo "Summary:"
echo "  Deleted: $DELETED_LOC LOC"
echo "  Before: $BEFORE_LOC LOC"
echo "  After: $AFTER_LOC LOC"
echo "  Savings: $SAVINGS LOC"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Note: Update imports to use:"
echo "  from pheno.utils.retry import standard_retry, db_retry, api_retry"
echo "  from tenacity import retry, stop_after_attempt, wait_exponential"

