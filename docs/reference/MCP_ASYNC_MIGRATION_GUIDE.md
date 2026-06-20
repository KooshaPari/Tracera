# MCP Async Migration Quick Reference

## Converting MCP Tools to Async Database

### Step-by-Step Migration Pattern

#### 1. Update Imports

**Before**:
```python
from tracertm.mcp.tools.base import (
    get_session,
    require_project,
    wrap_success,
)
```

**After**:
```python
from sqlalchemy import select  # Add for modern syntax
from tracertm.mcp.tools.base_async import (
    get_mcp_session,
    require_project,
    wrap_success,
)
```

#### 2. Convert Database Queries

##### Pattern A: Simple Query

**Before (sync)**:
```python
with get_session() as session:
    items = session.query(Item).all()
```

**After (async)**:
```python
async with get_mcp_session() as session:
    result = await session.execute(select(Item))
    items = result.scalars().all()
```

##### Pattern B: Filtered Query

**Before (sync)**:
```python
with get_session() as session:
    item = session.query(Item).filter(
        Item.id == item_id,
        Item.deleted_at.is_(None)
    ).first()
```

**After (async)**:
```python
async with get_mcp_session() as session:
    result = await session.execute(
        select(Item).filter(
            Item.id == item_id,
            Item.deleted_at.is_(None)
        )
    )
    item = result.scalar_one_or_none()
```

##### Pattern C: Aggregate Query

**Before (sync)**:
```python
with get_session() as session:
    count = session.query(func.count(Item.id)).scalar()
```

**After (async)**:
```python
async with get_mcp_session() as session:
    result = await session.execute(
        select(func.count(Item.id))
    )
    count = result.scalar()
```

##### Pattern D: Create/Update

**Before (sync)**:
```python
with get_session() as session:
    item = Item(id="123", name="Test")
    session.add(item)
    session.commit()
```

**After (async)**:
```python
async with get_mcp_session() as session:
    item = Item(id="123", name="Test")
    session.add(item)
    await session.commit()  # Note: await commit()
```

#### 3. Update Helper Function Calls

**Before**:
```python
project_id = require_project()
set_current_project(project_id)
```

**After**:
```python
project_id = await require_project()
await set_current_project(project_id)
```

---

## SQLAlchemy 2.0 Cheat Sheet

### Query Result Extraction

| Old Method (.query) | New Method (select) | Result |
|-------------------|---------------------|--------|
| `.first()` | `result.scalar_one_or_none()` | Single row or None |
| `.one()` | `result.scalar_one()` | Single row (raises if 0 or 2+) |
| `.all()` | `result.scalars().all()` | List of rows |
| `.scalar()` | `result.scalar()` | Single value (first column) |
| `.count()` | `select(func.count(...))` then `.scalar()` | Integer count |

### Common Patterns

```python
# Get single item (may be None)
result = await session.execute(select(Item).filter(Item.id == id))
item = result.scalar_one_or_none()

# Get all items
result = await session.execute(select(Item))
items = result.scalars().all()

# Get scalar value (count, sum, etc.)
result = await session.execute(select(func.count(Item.id)))
count = result.scalar()

# Filter with multiple conditions
result = await session.execute(
    select(Item).filter(
        Item.project_id == project_id,
        Item.status == "active",
        Item.deleted_at.is_(None)
    )
)
items = result.scalars().all()

# Joins
result = await session.execute(
    select(Item).join(Project).filter(Project.name == "MyProject")
)
items = result.scalars().all()

# Order by
result = await session.execute(
    select(Item).order_by(Item.created_at.desc())
)
items = result.scalars().all()
```

---

## Testing Your Converted Tool

### Basic Test Structure

```python
import pytest
from tracertm.mcp.database_adapter import get_mcp_session, reset_engine

@pytest.fixture(autouse=True)
async def cleanup():
    """Reset engine after each test."""
    yield
    await reset_engine()

@pytest.mark.asyncio
async def test_my_tool_function():
    """Test your converted function."""
    # Create test data
    async with get_mcp_session() as session:
        project = Project(id="test-1", name="Test")
        session.add(project)
        await session.commit()

    # Test your tool
    result = await my_tool_function(project_id="test-1")

    # Assertions
    assert result["ok"] is True
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Forgetting `await`

**Error**:
```python
result = session.execute(query)  # ❌ Missing await
```

**Fix**:
```python
result = await session.execute(query)  # ✅
```

### Pitfall 2: Using `.query()` in Async

**Error**:
```python
items = session.query(Item).all()  # ❌ .query() is sync-only
```

**Fix**:
```python
result = await session.execute(select(Item))  # ✅
items = result.scalars().all()
```

### Pitfall 3: Not Awaiting Commit

**Error**:
```python
session.commit()  # ❌ commit() is async
```

**Fix**:
```python
await session.commit()  # ✅
```

### Pitfall 4: Wrong Result Extraction

**Error**:
```python
result = await session.execute(select(Item))
item = result.first()  # ❌ No .first() on result
```

**Fix**:
```python
result = await session.execute(select(Item))
item = result.scalar_one_or_none()  # ✅
```

---

## Migration Checklist

For each tool function:

- [ ] Change `def` to `async def`
- [ ] Replace `from base import` with `from base_async import`
- [ ] Change `get_session()` to `get_mcp_session()`
- [ ] Add `await` before all database operations
- [ ] Convert `.query()` to `select()`
- [ ] Update result extraction (`.first()` → `.scalar_one_or_none()`)
- [ ] Add `await` before `require_project()` calls
- [ ] Add `await` before `set_current_project()` calls
- [ ] Test the converted function

---

## Example: Complete Before/After

### Before (Sync)

```python
from tracertm.mcp.tools.base import get_session, require_project
from tracertm.models.item import Item

@mcp.tool()
async def get_item(item_id: str) -> dict:
    project_id = require_project()

    with get_session() as session:
        item = session.query(Item).filter(
            Item.project_id == project_id,
            Item.id == item_id
        ).first()

        if not item:
            raise ToolError(f"Item not found: {item_id}")

        return {"id": item.id, "title": item.title}
```

### After (Async)

```python
from sqlalchemy import select
from tracertm.mcp.tools.base_async import get_mcp_session, require_project
from tracertm.models.item import Item

@mcp.tool()
async def get_item(item_id: str) -> dict:
    project_id = await require_project()

    async with get_mcp_session() as session:
        result = await session.execute(
            select(Item).filter(
                Item.project_id == project_id,
                Item.id == item_id
            )
        )
        item = result.scalar_one_or_none()

        if not item:
            raise ToolError(f"Item not found: {item_id}")

        return {"id": item.id, "title": item.title}
```

---

## Benefits Recap

- ✅ **Shared Connection Pool**: 50% reduction in database connections
- ✅ **RLS Context**: Automatic user context setting for security
- ✅ **Better Performance**: Connection reuse, optimized pool settings
- ✅ **Modern Syntax**: SQLAlchemy 2.0 select() syntax
- ✅ **Type Safety**: Full async typing support
- ✅ **Consistency**: All database access through single adapter

---

*Quick Reference for MCP FastAPI Integration Phase 1*
*Last Updated: 2026-01-30*
