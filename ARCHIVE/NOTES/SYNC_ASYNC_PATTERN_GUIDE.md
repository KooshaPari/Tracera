# Sync/Async Integration Pattern Guide

## Quick Reference for Testing Sync Services with AsyncSession

### The Problem

When you have a **sync service** that needs a `Session` but your tests use `AsyncSession`:

```python
# ❌ WRONG - This won't work
service = BulkOperationService(db_session)  # TypeError: expected Session, got AsyncSession
```

### The Solution

Use `AsyncSession.run_sync()` to execute sync operations:

```python
# ✅ CORRECT
def run_sync_operation(sync_session: Session):
    service = BulkOperationService(sync_session)
    return service.operation(...)

result = await db_session.run_sync(run_sync_operation)
```

---

## Pattern Templates

### Template 1: Simple Sync Service Call

```python
@pytest.mark.asyncio
async def test_sync_service(db_session: AsyncSession):
    """Test a sync service from async test."""

    # Define sync operation as inner function
    def run_operation(sync_session: Session):
        service = SyncService(sync_session)
        return service.do_something(args)

    # Execute via run_sync
    result = await db_session.run_sync(run_operation)

    # Continue with async assertions
    assert result is not None
```

### Template 2: With Setup and Verification

```python
@pytest.mark.asyncio
async def test_with_setup(db_session: AsyncSession, test_project: Project):
    """Test with async setup and sync execution."""

    # Async setup
    item_repo = ItemRepository(db_session)
    item = await item_repo.create(...)
    await db_session.commit()

    # Sync operation
    def run_bulk_operation(sync_session: Session):
        service = BulkOperationService(sync_session)
        return service.bulk_update_items(
            project_id=test_project.id,
            filters={"status": "todo"},
            updates={"status": "done"}
        )

    result = await db_session.run_sync(run_bulk_operation)

    # Async verification
    await db_session.commit()
    updated_item = await item_repo.get_by_id(item.id)
    assert updated_item.status == "done"
```

### Template 3: Multiple Sync Calls

```python
@pytest.mark.asyncio
async def test_multiple_sync_calls(db_session: AsyncSession):
    """Multiple sync operations in one test."""

    # First sync operation
    def preview_operation(sync_session: Session):
        service = BulkOperationService(sync_session)
        return service.bulk_update_preview(...)

    preview = await db_session.run_sync(preview_operation)
    assert preview["total_count"] > 0

    # Second sync operation
    def execute_operation(sync_session: Session):
        service = BulkOperationService(sync_session)
        return service.bulk_update_items(...)

    result = await db_session.run_sync(execute_operation)
    assert result["items_updated"] == preview["total_count"]
```

---

## Common Mistakes and Fixes

### ❌ Mistake 1: Trying to Access sync_session Attribute

```python
# WRONG - sync_session attribute doesn't exist
service = BulkOperationService(db_session.sync_session)
```

**Fix**:
```python
# RIGHT - Use run_sync with a function that receives sync session
def operation(sync_session: Session):
    service = BulkOperationService(sync_session)
    return service.method()

result = await db_session.run_sync(operation)
```

### ❌ Mistake 2: Lambda That Ignores Session

```python
# WRONG - Lambda receives session but doesn't use it
def my_operation():
    service = BulkOperationService(???)  # Where does session come from?
    return service.method()

result = await db_session.run_sync(lambda session: my_operation())
```

**Fix**:
```python
# RIGHT - Function receives and uses session parameter
def my_operation(sync_session: Session):
    service = BulkOperationService(sync_session)
    return service.method()

result = await db_session.run_sync(my_operation)
```

### ❌ Mistake 3: Passing AsyncSession to Sync Service

```python
# WRONG - BulkOperationService expects Session, not AsyncSession
service = BulkOperationService(db_session)  # TypeError
```

**Fix**:
```python
# RIGHT - Wrap in run_sync
def operation(sync_session: Session):
    service = BulkOperationService(sync_session)
    return service.method()

result = await db_session.run_sync(operation)
```

### ❌ Mistake 4: Forgetting Await on run_sync

```python
# WRONG - run_sync returns coroutine, must be awaited
result = db_session.run_sync(operation)  # Gets coroutine object, not result
```

**Fix**:
```python
# RIGHT - Always await run_sync
result = await db_session.run_sync(operation)
```

---

## How It Works

### Under the Hood

When you call `await db_session.run_sync(function)`:

1. AsyncSession creates a sync Session internally
2. Calls `function(sync_session)`
3. Sync operations execute in the sync session
4. Results are returned to the async context
5. Transactions are properly managed

```
AsyncSession (async test)
    ↓
run_sync(function)
    ↓
Internal Sync Session
    ↓
function(sync_session) executes
    ↓
BulkOperationService operates on sync_session
    ↓
Result returned to async context
```

### Transaction Flow

```python
# Async context (AsyncSession)
await db_session.run_sync(operation)  # Enter sync context
    ↓
    # Sync context (Session)
    def operation(sync_session):
        service = BulkOperationService(sync_session)
        service.update(...)  # Uses sync session's transaction
        return result
    ↓
# Back to async context
await db_session.commit()  # Commits the transaction
```

**Key Point**: Both async and sync operations share the same underlying transaction.

---

## Service Type Reference

### Sync Services (use Session)

Use `run_sync` pattern:

```python
# BulkOperationService
def operation(sync_session: Session):
    service = BulkOperationService(sync_session)
    return service.bulk_update_items(...)

result = await db_session.run_sync(operation)
```

**Characteristics**:
- Takes `Session` in `__init__`
- Uses `.query()`, `.filter()`, `.all()` (sync ORM methods)
- No `async`/`await` in method definitions

### Async Services (use AsyncSession)

Use directly with `await`:

```python
# ExportImportService, TraceabilityService
service = ExportImportService(db_session)  # AsyncSession
result = await service.export_to_json(...)  # await async method
```

**Characteristics**:
- Takes `AsyncSession` in `__init__`
- Uses `await session.execute()`, `await session.commit()`
- Methods defined with `async def`

### Static Services (no session)

Call directly:

```python
# VisualizationService
result = VisualizationService.render_tree(items)  # No session needed
```

**Characteristics**:
- No session parameter
- Pure functions or class methods
- No database access

---

## Type Hints for Clarity

Always use explicit type hints:

```python
# ✅ GOOD - Clear what type of session is expected
def sync_operation(sync_session: Session) -> dict[str, Any]:
    service = BulkOperationService(sync_session)
    return service.operation()

# ❌ BAD - Unclear what session type is needed
def operation(session):
    service = BulkOperationService(session)
    return service.operation()
```

Import the correct types:

```python
from sqlalchemy.orm import Session  # For sync services
from sqlalchemy.ext.asyncio import AsyncSession  # For async services
```

---

## Testing Checklist

When writing integration tests:

- [ ] Identify if service is sync or async
- [ ] Use `AsyncSession` in test signature
- [ ] For **sync services**:
  - [ ] Define inner function with `sync_session: Session` parameter
  - [ ] Create service inside the inner function
  - [ ] Pass function to `run_sync` (no lambda)
  - [ ] Await the `run_sync` call
- [ ] For **async services**:
  - [ ] Create service with `db_session` (AsyncSession)
  - [ ] Await all async method calls
  - [ ] Use `await db_session.commit()` for transactions

---

## Real-World Example: BulkOperationService Test

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from tracertm.services.bulk_operation_service import BulkOperationService

@pytest.mark.asyncio
async def test_bulk_update_preview(
    db_session: AsyncSession,
    test_project: Project,
    test_items: list[Item]
):
    """Test bulk update preview functionality."""

    # Define sync operation
    def run_bulk_preview(sync_session: Session):
        # Create sync service with sync session
        service = BulkOperationService(sync_session)

        # Call sync method
        return service.bulk_update_preview(
            project_id=test_project.id,
            filters={"status": "todo"},
            updates={"status": "in_progress"},
            limit=5
        )

    # Execute sync operation from async context
    result = await db_session.run_sync(run_bulk_preview)

    # Async assertions
    assert result["total_count"] > 0
    assert len(result["sample_items"]) <= 5
```

---

## Summary

**For Sync Services**:
```python
def operation(sync_session: Session):
    service = SyncService(sync_session)
    return service.method()

result = await db_session.run_sync(operation)
```

**For Async Services**:
```python
service = AsyncService(db_session)
result = await service.method()
```

**Key Points**:
1. Define sync operation as a function with `sync_session` parameter
2. Pass function reference to `run_sync` (not lambda)
3. Always await `run_sync`
4. Use type hints for clarity
5. Share transaction context between sync and async operations

**Remember**: The sync session is provided automatically by `run_sync` - you just need to accept it as a parameter!
