#!/bin/bash
# Phase 5b: Consolidate HTTP Clients
# Target: -2,500 LOC

set -e

BACKUP_DIR="backups/phase5b-http-clients-cleanup-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 5b: HTTP Clients Consolidation ==="
echo "Backup directory: $BACKUP_DIR"
echo ""

# Create backup
mkdir -p "$BACKUP_DIR"

echo "Step 1: Backing up HTTP client files to delete..."

# Duplicate/deprecated HTTP clients
HTTP_CLIENTS_TO_DELETE=(
    "src/pheno/testing/mcp_qa/adapters/fast_http_client.py"
    "src/pheno/core/api/http_mixin.py"
    "src/pheno/core/api/request_mixin.py"
    "src/pheno/testing/adapters/httpx_client.py"
)

# Old HTTP proxy implementations
OLD_HTTP=(
    "src/pheno/core/shared/redis_http_proxy_old/proxy.py"
    "src/pheno/core/shared/redis_http_proxy_old/client.py"
    "src/pheno/core/shared/redis_http_proxy_old/config.py"
    "src/pheno/core/shared/redis_http_proxy_old/models.py"
)

# Combine all files
FILES_TO_DELETE=("${HTTP_CLIENTS_TO_DELETE[@]}" "${OLD_HTTP[@]}")

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  Backing up: $file"
        mkdir -p "$BACKUP_DIR/$(dirname "$file")"
        cp "$file" "$BACKUP_DIR/$file"
    fi
done

echo ""
echo "Step 2: Counting LOC before deletion..."
TOTAL_LOC=0
FILES_FOUND=0
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        echo "  $file: $LOC LOC"
        TOTAL_LOC=$((TOTAL_LOC + LOC))
        FILES_FOUND=$((FILES_FOUND + 1))
    fi
done
echo "  Files found: $FILES_FOUND"
echo "  Total LOC to delete: $TOTAL_LOC"

echo ""
echo "Step 3: Deleting HTTP client files..."
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  Deleting: $file"
        rm "$file"
    fi
done

echo ""
echo "Step 4: Creating migration guide..."
cat > "$BACKUP_DIR/MIGRATION_GUIDE.md" << 'EOF'
# HTTP Clients Migration Guide

## What Changed

Consolidated multiple HTTP client implementations into single httpx-based client.

## Files Deleted

### Duplicate HTTP Clients (4 files)
1. `src/pheno/testing/mcp_qa/adapters/fast_http_client.py` (1,238 LOC)
2. `src/pheno/core/api/http_mixin.py` (243 LOC - deprecated)
3. `src/pheno/core/api/request_mixin.py` (~200 LOC)
4. `src/pheno/testing/adapters/httpx_client.py` (~100 LOC)

### Old HTTP Proxy (4 files)
5. `src/pheno/core/shared/redis_http_proxy_old/proxy.py` (287 LOC)
6. `src/pheno/core/shared/redis_http_proxy_old/client.py` (163 LOC)
7. `src/pheno/core/shared/redis_http_proxy_old/config.py` (~100 LOC)
8. `src/pheno/core/shared/redis_http_proxy_old/models.py` (~50 LOC)

## Canonical Implementation

**USE THIS**: `src/pheno/core/shared/http_client.py`

This is the modern httpx-based HTTP client with all features.

## Migration Path

### Before (FastHTTPClient)

```python
from pheno.testing.mcp_qa.adapters.fast_http_client import FastHTTPClient

client = FastHTTPClient(
    base_url="https://api.example.com",
    timeout=30.0,
    headers={"Authorization": "Bearer token"}
)
response = await client.get("/endpoint")
```

### After (HTTPClient)

```python
from pheno.core.shared.http_client import HTTPClient, HTTPClientConfig

config = HTTPClientConfig(
    base_url="https://api.example.com",
    timeout=30.0,
    headers={"Authorization": "Bearer token"}
)
async with HTTPClient(config) as client:
    response = await client.get("/endpoint")
```

### Before (HttpClientMixin - DEPRECATED)

```python
from pheno.core.api.http_mixin import HttpClientMixin

class MyAPI(HttpClientMixin):
    async def make_request(self):
        return await self._execute_http_request("GET", "/endpoint")
```

### After (Direct httpx usage)

```python
import httpx

class MyAPI:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url="https://api.example.com")
    
    async def make_request(self):
        return await self.client.get("/endpoint")
    
    async def close(self):
        await self.client.aclose()
```

### Or Use HTTPClient

```python
from pheno.core.shared.http_client import HTTPClient, HTTPClientConfig

class MyAPI:
    def __init__(self):
        config = HTTPClientConfig(base_url="https://api.example.com")
        self.client = HTTPClient(config)
    
    async def make_request(self):
        async with self.client:
            return await self.client.get("/endpoint")
```

## Benefits

1. **Single Implementation**: One HTTP client to maintain
2. **Modern Features**: HTTP/2, connection pooling, retries
3. **Less Code**: -2,381 LOC removed
4. **Better Performance**: httpx is highly optimized
5. **Standard Library**: httpx is the de facto standard

## Features of HTTPClient

- ✅ Async/await support
- ✅ Connection pooling
- ✅ Automatic retries with backoff
- ✅ Timeout configuration
- ✅ Custom headers
- ✅ SSL verification
- ✅ Follow redirects
- ✅ Request/response hooks
- ✅ HTTP/2 support

## Next Steps

If any code breaks:
1. Replace with `HTTPClient` from `pheno.core.shared.http_client`
2. Or use `httpx.AsyncClient` directly
3. Update imports
4. Run tests

## Rollback

If needed, restore from backup:
```bash
cp -r backups/phase5b-http-clients-cleanup-*/src/* src/
```
EOF

echo ""
echo "Step 5: Summary"
echo "  Files deleted: $FILES_FOUND"
echo "  LOC removed: $TOTAL_LOC"
echo "  Backup location: $BACKUP_DIR"
echo "  Migration guide: $BACKUP_DIR/MIGRATION_GUIDE.md"
echo ""
echo "✅ Phase 5b Complete!"
echo ""
echo "Next: Run tests to verify nothing broke"
echo "  pytest tests/ -v"

