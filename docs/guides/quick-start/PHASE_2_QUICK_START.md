# MCP Phase 2 Optimization - Quick Start Guide

## 🚀 Quick Start

### Use Optimized Tools (v2)

```python
from tracertm.mcp.tools.items_optimized import (
    create_item_optimized,
    get_item_optimized,
    query_items_optimized,
)

# Create item (88% fewer tokens)
item = await create_item_optimized(
    title="New Feature",
    view="FEATURE",
    item_type="epic",
)

# Get item (minimal response)
item = await get_item_optimized("abc12345")

# Query items
items = await query_items_optimized(view="FEATURE", limit=50)
```

### Use Streaming for Large Queries

```python
from tracertm.mcp.tools.streaming_v2 import stream_items, get_items_batch

# Get first batch (75% fewer tokens)
batch1 = await stream_items(view="FEATURE", batch_size=50)

# Get more if needed
if batch1["has_more"]:
    batch2 = await get_items_batch(batch=2, view="FEATURE", batch_size=50)
```

## 📊 Performance Gains

| Metric | Improvement |
|--------|-------------|
| **Single Item** | 88.3% fewer tokens |
| **List Queries** | 84.2% fewer tokens |
| **Compression** | 98.4% size reduction |
| **Streaming** | 74.8% initial savings |

## 🔧 Key Features

### 1. Lean Responses

```python
# Before (v1): 290 tokens
{
  "ok": True,
  "action": "get",
  "data": { /* full item */ },
  "actor": { /* 7 fields */ }
}

# After (v2): 34 tokens
{
  "id": "abc12345",
  "title": "Feature",
  "view": "FEATURE",
  "type": "epic",
  "status": "active"
}
```

### 2. Smart Errors

```python
# Errors include helpful suggestions
{
  "ok": False,
  "error": "Item not found: abc123",
  "category": "not_found",
  "suggestions": [
    "Check the item ID or use query_items() to search",
    "Item IDs support prefix matching"
  ]
}
```

### 3. Short IDs

```python
# Full UUID (36 chars): "12345678-1234-1234-1234-123456789012"
# Short ID (8 chars):    "12345678"
# 77% reduction, still unique within project
```

## 🛠️ Available Tools

### Optimized Item Tools (v2)

- `create_item_optimized()` - Create with lean response
- `get_item_optimized()` - Get with minimal fields
- `query_items_optimized()` - Query with optimization
- `update_item_optimized()` - Update with lean response
- `delete_item_optimized()` - Delete with confirmation
- `summarize_view_optimized()` - Summary without samples

### Streaming Tools

- `stream_items()` - Stream items in batches
- `get_items_batch()` - Get specific batch
- `stream_links()` - Stream links in batches
- `get_links_batch()` - Get specific link batch
- `stream_matrix()` - Stream traceability matrix
- `get_matrix_batch()` - Get matrix batch

## 📈 When to Use What

| Use Case | Tool | Benefit |
|----------|------|---------|
| Get single item | `get_item_optimized()` | 88% fewer tokens |
| Query <50 items | `query_items_optimized()` | 84% fewer tokens |
| Query >50 items | `stream_items()` | 75% initial savings |
| Large datasets | Use compression | 98% reduction |

## 🔄 Migration Path

```python
# Step 1: Try v2 alongside v1
v1_result = await query_items(view="FEATURE")
v2_result = await query_items_optimized(view="FEATURE")

# Step 2: Update client code
# Before: result["data"]["items"]
# After:  result["items"]

# Step 3: Switch to v2
result = await query_items_optimized(...)  # Production
```

## 🧪 Test It

```bash
# Run benchmarks
python src/tracertm/mcp/benchmarks/token_benchmark.py

# Expected: 77.2% average token reduction
```

## 📚 Full Documentation

See: `src/tracertm/mcp/PHASE_2_OPTIMIZATION_COMPLETE.md`
