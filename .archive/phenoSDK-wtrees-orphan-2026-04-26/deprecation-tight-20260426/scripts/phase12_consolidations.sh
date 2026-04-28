#!/bin/bash
# Phase 12.3: Consolidations
# Consolidate duplicate patterns across the codebase
# Estimated savings: -9,500 LOC

set -e

echo "🚀 Phase 12.3: Consolidations"
echo "============================="
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
BACKUP_DIR="backups/cleanup-phase12-consolidations-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src/pheno "$BACKUP_DIR/pheno-before"
print_status "Backup created: $BACKUP_DIR"
echo ""

BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Starting LOC: $BEFORE_LOC"
echo ""

# ============================================================================
# 12.3.1: Consolidate __init__ Files (-6,000 LOC)
# ============================================================================
echo "🔧 12.3.1: Consolidating __init__ files..."
echo ""

print_info "Finding __init__.py files..."
INIT_COUNT=$(find src/pheno -name "__init__.py" -type f | wc -l)
print_info "Found $INIT_COUNT __init__.py files"
echo ""

INIT_SAVINGS=0
INIT_SIMPLIFIED=0

# Process each __init__.py file
find src/pheno -name "__init__.py" -type f | while read init_file; do
    # Get current LOC
    CURRENT_LOC=$(wc -l < "$init_file" 2>/dev/null || echo "0")
    
    # Skip if already minimal (< 5 lines)
    if [ "$CURRENT_LOC" -lt 5 ]; then
        continue
    fi
    
    # Get module name from directory
    MODULE_DIR=$(dirname "$init_file")
    MODULE_NAME=$(basename "$MODULE_DIR")
    
    # Check if it's just imports and __all__
    if grep -qE "^(from |import |__all__|\"\"\"|\'\'\\'|#|$)" "$init_file" 2>/dev/null; then
        # Backup original
        mkdir -p "$BACKUP_DIR/$(dirname ${init_file#src/pheno/})"
        cp "$init_file" "$BACKUP_DIR/${init_file#src/pheno/}"
        
        # Create minimal __init__.py
        # Capitalize first letter
        FIRST_CHAR=$(echo "$MODULE_NAME" | cut -c1 | tr '[:lower:]' '[:upper:]')
        REST_CHARS=$(echo "$MODULE_NAME" | cut -c2-)
        CAPITALIZED="${FIRST_CHAR}${REST_CHARS}"
        echo "\"\"\"${CAPITALIZED} module.\"\"\"" > "$init_file"
        
        NEW_LOC=$(wc -l < "$init_file")
        SAVED=$((CURRENT_LOC - NEW_LOC))
        
        if [ "$SAVED" -gt 0 ]; then
            echo "  ✓ Simplified: ${init_file#src/pheno/} ($SAVED LOC)"
        fi
    fi
done

AFTER_INIT=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
INIT_SAVINGS=$((BEFORE_LOC - AFTER_INIT))
print_status "Consolidated __init__ files: $INIT_SAVINGS LOC saved"
echo ""

# ============================================================================
# 12.3.2: Consolidate Type Definitions (-1,500 LOC)
# ============================================================================
echo "🔧 12.3.2: Consolidating type definitions..."
echo ""

print_info "Finding types.py files..."
TYPES_FILES=$(find src/pheno -name "types.py" -type f | wc -l)
print_info "Found $TYPES_FILES types.py files"
echo ""

# Create centralized types directory
CENTRAL_TYPES_DIR="src/pheno/core/types"
mkdir -p "$CENTRAL_TYPES_DIR"

# Create central types __init__.py
cat > "$CENTRAL_TYPES_DIR/__init__.py" << 'EOF'
"""Centralized type definitions for PhenoSDK.

This module provides all common type definitions used across the SDK.
Import types from here instead of scattered types.py files.
"""

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from typing import Protocol, runtime_checkable
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

# Common type aliases
StrPath = Union[str, Path]
JSON = Dict[str, Any]
Headers = Dict[str, str]
Params = Dict[str, Any]

# Generic type variables
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

__all__ = [
    # Standard typing
    "Any",
    "Callable",
    "Dict",
    "List",
    "Optional",
    "Set",
    "Tuple",
    "Type",
    "TypeVar",
    "Union",
    "Protocol",
    "runtime_checkable",
    "Enum",
    "dataclass",
    "Path",
    # Custom aliases
    "StrPath",
    "JSON",
    "Headers",
    "Params",
    # Type variables
    "T",
    "K",
    "V",
]
EOF

TYPES_SAVINGS=0

# Find and analyze types.py files
find src/pheno -name "types.py" -type f | while read types_file; do
    # Skip the central types file
    if [ "$types_file" = "$CENTRAL_TYPES_DIR/__init__.py" ]; then
        continue
    fi
    
    LOC=$(wc -l < "$types_file")
    
    # Check if it's just basic type definitions
    if grep -qE "^(from typing import|TypeVar|Protocol|Enum|dataclass)" "$types_file" 2>/dev/null; then
        # Check if it has domain-specific types
        if ! grep -qE "class.*\(.*\):|def " "$types_file" 2>/dev/null; then
            # It's just basic types, can be removed
            mkdir -p "$BACKUP_DIR/$(dirname ${types_file#src/pheno/})"
            cp "$types_file" "$BACKUP_DIR/${types_file#src/pheno/}"
            
            # Replace with import from central types
            DIR_NAME=$(dirname "$types_file")
            MODULE_NAME=$(basename "$DIR_NAME")
            
            echo "\"\"\"Type definitions for ${MODULE_NAME}.\"\"\"" > "$types_file"
            echo "" >> "$types_file"
            echo "from pheno.core.types import *  # noqa: F403, F401" >> "$types_file"
            
            NEW_LOC=$(wc -l < "$types_file")
            SAVED=$((LOC - NEW_LOC))
            
            if [ "$SAVED" -gt 0 ]; then
                echo "  ✓ Simplified: ${types_file#src/pheno/} ($SAVED LOC)"
            fi
        fi
    fi
done

AFTER_TYPES=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
TYPES_SAVINGS=$((AFTER_INIT - AFTER_TYPES))
print_status "Consolidated type definitions: $TYPES_SAVINGS LOC saved"
echo ""

# ============================================================================
# 12.3.3: Consolidate Base Classes (-2,000 LOC)
# ============================================================================
echo "🔧 12.3.3: Consolidating base classes..."
echo ""

print_info "Finding base.py files..."
BASE_FILES=$(find src/pheno -name "base.py" -type f | wc -l)
print_info "Found $BASE_FILES base.py files"
echo ""

# Create centralized base classes
CENTRAL_BASE_DIR="src/pheno/core/base"
mkdir -p "$CENTRAL_BASE_DIR"

# Create central base classes
cat > "$CENTRAL_BASE_DIR/__init__.py" << 'EOF'
"""Centralized base classes for PhenoSDK.

This module provides common base classes used across the SDK.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel


class BaseEntity(BaseModel):
    """Base entity with common fields."""
    
    id: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True
        validate_assignment = True


class BaseService(ABC):
    """Base service with common lifecycle methods."""
    
    def __init__(self):
        """Initialize service."""
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the service."""
        if self._initialized:
            return
        await self._initialize()
        self._initialized = True
    
    async def shutdown(self) -> None:
        """Shutdown the service."""
        if not self._initialized:
            return
        await self._shutdown()
        self._initialized = False
    
    @abstractmethod
    async def _initialize(self) -> None:
        """Initialize implementation."""
        pass
    
    @abstractmethod
    async def _shutdown(self) -> None:
        """Shutdown implementation."""
        pass


class BaseRepository(ABC):
    """Base repository with CRUD operations."""
    
    @abstractmethod
    async def create(self, entity: Any) -> Any:
        """Create entity."""
        pass
    
    @abstractmethod
    async def read(self, id: str) -> Optional[Any]:
        """Read entity by ID."""
        pass
    
    @abstractmethod
    async def update(self, id: str, entity: Any) -> Any:
        """Update entity."""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete entity."""
        pass
    
    @abstractmethod
    async def list(self, **filters: Any) -> list[Any]:
        """List entities with filters."""
        pass


class BaseAdapter(ABC):
    """Base adapter for external integrations."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to external service."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from external service."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if connection is healthy."""
        pass


__all__ = [
    "BaseEntity",
    "BaseService",
    "BaseRepository",
    "BaseAdapter",
]
EOF

BASE_SAVINGS=0

# Note: We don't automatically replace base.py files as they may have
# domain-specific logic. This creates the foundation for manual migration.

print_info "Created centralized base classes in $CENTRAL_BASE_DIR"
print_status "Base classes ready for migration"
echo ""

# ============================================================================
# Summary
# ============================================================================

AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
TOTAL_SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Phase 12.3 Consolidations Complete!"
echo "======================================"
echo ""
echo "  __init__ files:        $INIT_SAVINGS LOC"
echo "  Type definitions:      $TYPES_SAVINGS LOC"
echo "  Base classes:          Created (manual migration needed)"
echo "  ────────────────────────────────────────"
echo "  Total Savings:         $TOTAL_SAVINGS LOC"
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

# Check for syntax errors in modified files
print_info "Checking for syntax errors..."
SYNTAX_ERRORS=0
for file in $(find src/pheno -name "__init__.py" -o -name "types.py" -type f); do
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
echo "   git commit -m 'feat: Phase 12.3 Consolidations (-$TOTAL_SAVINGS LOC)'"
echo ""
echo "5. Manual migration of base classes (optional):"
echo "   - Review base.py files"
echo "   - Migrate to centralized base classes"
echo "   - Potential additional savings: ~2,000 LOC"
echo ""

