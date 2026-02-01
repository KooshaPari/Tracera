# Atoms.Tech Deep Dive Analysis
## Production Patterns for PM Traceability System

**Research Date:** 2025-11-20
**Source:** atoms.tech codebase (hexagonal refactor)
**Key Metric:** 68% file reduction (248→80 files), 61% code reduction (56K→22K LOC)

---

## Executive Summary

atoms.tech demonstrates **production-grade hexagonal architecture** with:
- **Zero-dependency domain layer** for pure business logic
- **Optimistic concurrency control** for multi-agent coordination
- **Event sourcing** with complete audit trails
- **CQRS pattern** separating commands from queries
- **FastMCP integration** with nested agent patterns
- **98%+ test coverage** using layered fixtures

**Critical for Trace:** Adopt hexagonal architecture, optimistic locking, and YAML+Pydantic config from day one.

---

## 1. Hexagonal Architecture

### Layer Separation

```
Domain (0 dependencies)
  ↑
Application (depends on Domain)
  ↑
Adapters (depends on Application + Domain)
```

**Directory Structure:**
```
src/tracertm/
├── domain/              # Pure Python - zero external deps
│   ├── models/          # Entities (no SQLAlchemy)
│   ├── services/        # Business logic
│   └── ports/           # Abstract interfaces (Protocol)
├── application/
│   ├── commands/        # Write operations
│   ├── queries/         # Read operations
│   └── workflows/       # Orchestration
└── adapters/
    ├── primary/         # MCP, CLI (inbound)
    └── secondary/       # PostgreSQL, NATS (outbound)
```

### Code Example

```python
# domain/models/item.py - Pure domain entity
from dataclasses import dataclass
from datetime import datetime

class Item:
    """Domain entity - no infrastructure dependencies."""

    def __init__(self, id: str, title: str, project_id: str):
        self._id = id
        self._title = title
        self._project_id = project_id
        self._version = 1
        self._events = []

    def update_title(self, new_title: str) -> None:
        """Business rule: Title must be 3+ chars."""
        if len(new_title) < 3:
            raise ValueError("Title must be at least 3 characters")

        old_title = self._title
        self._title = new_title
        self._version += 1
        self._events.append(ItemTitleChanged(old_title, new_title))

# domain/ports/repositories.py - Abstract interface
from typing import Protocol

class ItemRepository(Protocol):
    async def get(self, id: str) -> Optional[Item]: ...
    async def save(self, item: Item) -> None: ...

# adapters/secondary/postgres/item_repository.py - Implementation
from sqlalchemy.ext.asyncio import AsyncSession

class PostgresItemRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, id: str) -> Optional[Item]:
        # Map SQLAlchemy model → Domain entity
        pass
```

**Recommendation:** Adopt this separation for trace's item/link/project models.

---

## 2. Optimistic Concurrency Control

### Version-Based Locking

```python
# Critical for multi-agent coordination
class Item(Base):
    id = Column(String, primary_key=True)
    version = Column(Integer, default=1, nullable=False)

async def update(item_id: str, expected_version: int, **updates):
    item = await get_item(item_id)

    if item.version != expected_version:
        raise ConcurrencyError(
            f"Version mismatch: expected {expected_version}, got {item.version}"
        )

    # Apply updates + increment version
    for k, v in updates.items():
        setattr(item, k, v)
    item.version += 1
    await session.flush()
    return item

# With retry logic
async def update_with_retry(operation, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await operation()
        except ConcurrencyError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff
```

**Recommendation:** Essential for trace's 1-1000 concurrent agents (NFR-P5).

---

## 3. YAML + Pydantic Configuration

### Hierarchical Config Pattern

```python
from pydantic import BaseModel, Field
import yaml

class Config(BaseModel):
    database_url: str
    current_project: Optional[str] = None
    max_agents: int = Field(1000, ge=1, le=10000)

    @classmethod
    def load(cls, path: Path) -> "Config":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)  # Pydantic validation
```

```yaml
# config.yaml
database:
  url: postgresql://...
  pool_size: 20

current_project: null
max_agents: 1000
log_level: INFO
```

**Benefits:**
- Human-readable (YAML)
- Type-safe (Pydantic validation)
- Environment overrides (env vars > YAML)

**Recommendation:** Replace env-only config with YAML+Pydantic hierarchy.

---

## 4. FastMCP Server Patterns

### Tool Registration

```python
from fastmcp import FastMCP, Context

mcp = FastMCP("tracertm")

@mcp.tool()
async def create_item(
    ctx: Context,
    project_id: str,
    title: str,
    view: str,
    agent_id: str,
) -> dict:
    """Create item with progress reporting."""
    await ctx.report_progress(0, 3, "Validating...")
    validate(title, view)

    await ctx.report_progress(1, 3, "Creating item...")
    item = await service.create_item(project_id, title, view, agent_id)

    await ctx.report_progress(2, 3, "Logging event...")
    await event_log.log("item_created", item.id, agent_id)

    await ctx.report_progress(3, 3, "Complete")
    return {"id": item.id, "version": item.version}

@mcp.resource("rtm://status")
async def project_status() -> str:
    """Expose project status YAML."""
    status = load_status()
    return yaml.dump(status)
```

**Recommendation:** Use for trace's agent-native API (FR36-FR45).

---

## 5. Testing Strategy

### Layered Testing

```python
# tests/unit/domain/ - Zero mocks
def test_item_title_validation():
    item = Item(id="1", title="Test")

    with pytest.raises(ValueError):
        item.update_title("AB")  # Too short

# tests/integration/ - Database
@pytest.mark.asyncio
async def test_repository_optimistic_lock(db_session):
    repo = ItemRepository(db_session)
    item = await repo.create(title="Test")

    with pytest.raises(ConcurrencyError):
        await repo.update(item.id, expected_version=999, title="Updated")

# tests/e2e/ - MCP tools
@pytest.mark.asyncio
async def test_create_item_tool(mcp_client):
    result = await mcp_client.call_tool("create_item", ...)
    assert "id" in result
```

**Coverage:** 98%+ achieved through comprehensive fixtures.

**Recommendation:** Adopt marker-based categorization, layered fixtures.

---

## 6. File Size Discipline

### Decomposition Strategy

**Rule:** ≤500 LOC (target ≤350 LOC)

**Before:**
```
services/item_service.py  (800 LOC)  ❌
```

**After:**
```
services/item_service.py         (320 LOC)  ✅
services/item_query_service.py   (280 LOC)  ✅
services/item_bulk_service.py    (240 LOC)  ✅
```

**Recommendation:** Enforce from start - prevents technical debt.

---

## 7. Production Patterns

### 7.1 Structured Logging

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "agent_id": getattr(record, "agent_id", None),
            "project_id": getattr(record, "project_id", None),
        })

logger.info("Creating item", extra={"agent_id": "A1", "project_id": "P1"})
```

### 7.2 Event Sourcing

```python
class EventRepository:
    async def log(self, project_id: str, event_type: str, data: dict, agent_id: str):
        event = Event(
            id=uuid4(),
            project_id=project_id,
            event_type=event_type,
            data=data,
            agent_id=agent_id,
            timestamp=datetime.utcnow(),
        )
        session.add(event)
```

### 7.3 Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.state = "CLOSED"
        self.failures = 0

    async def call(self, fn, *args):
        if self.state == "OPEN":
            raise Exception("Circuit breaker OPEN")

        try:
            result = await fn(*args)
            self.failures = 0
            return result
        except Exception:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
            raise
```

---

## 8. Recommendations for Trace PM

### Immediate (Week 1-2)
1. ✅ Hexagonal architecture (domain/application/adapters)
2. ✅ Optimistic locking with version column
3. ✅ Event repository for audit trail
4. ✅ YAML + Pydantic configuration
5. ✅ File size discipline (≤350 LOC target)

### Short-term (Week 3-4)
6. ✅ CQRS separation (commands/queries)
7. ✅ Structured logging with JSON formatter
8. ✅ Circuit breaker for external services
9. ✅ Comprehensive test suite (unit/integration/e2e)
10. ✅ FastMCP server with progress reporting

### Medium-term (Month 2)
11. ⚠️ Event sourcing (optional)
12. ⚠️ Saga pattern for complex workflows
13. ⚠️ Performance monitoring with OpenTelemetry
14. ⚠️ Multi-region deployment

### Success Metrics
| Metric | Target |
|--------|--------|
| Test Coverage | 95%+ |
| Domain Dependencies | 0 |
| Avg File Size | ≤350 LOC |
| Concurrency Errors | <0.1% |

---

**Status:** Analysis complete based on atoms.tech hexagonal refactor patterns
**Next:** Apply recommendations to trace architecture design
