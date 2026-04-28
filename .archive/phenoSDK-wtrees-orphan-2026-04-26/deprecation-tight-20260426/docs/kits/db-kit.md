# DB Kit

## At a Glance
- **Purpose:** Provide a unified async database interface with row-level security, multi-tenancy, and caching.
- **Best For:** Applications targeting Supabase, Neon, PlanetScale, Turso, or custom Postgres/MySQL adapters.
- **Key Building Blocks:** `Database` facade, adapter interfaces, tenant context managers, query builder, migration helpers.

## Core Capabilities
- Async CRUD operations (`query`, `get_single`, `insert`, `update`, `delete`, `count`).
- Pluggable adapters (`supabase`, `postgres`, `mysql`, `sqlite`, vector stores) with shared contracts.
- Row-level security by propagating JWT access tokens to providers that support RLS.
- Tenant context propagation to scope queries automatically.
- Query caching layer with configurable TTL and invalidation hooks.
- Migration tooling and schema helpers for applying migrations programmatically.

## Getting Started

### Installation
```
pip install db-kit
# Provider extras
pip install "db-kit[supabase]" "db-kit[postgres]"
```

### Minimal Example
```python
from db_kit import Database

async def list_users() -> list[dict]:
    db = Database.supabase()
    db.set_access_token("user-jwt")
    return await db.query("users", filters={"active": True}, limit=50)
```

## How It Works
- The `Database` facade wraps an adapter implementing `DatabaseAdapter` located in `db_kit.adapters`.
- Adapters translate abstract queries into provider-specific calls (Supabase client, asyncpg, mysqlclient, etc.).
- Tenant metadata is stored via `TenantContext` and applied automatically in adapters that support it.
- Caching uses `QueryCache` (`db_kit.query.cache`) to memoize read operations; invalidation triggers on writes.
- Real-time listeners and database change streams are exposed through `db_kit.realtime`.

## Usage Recipes
- Configure multi-tenancy:
  ```python
  from db_kit import Database

  db = Database.supabase()
  async with db.tenant_context("tenant-123"):
      await db.insert("orders", {"item": "widget"})
  ```
- Run migrations inside deployment workflows using `db_kit.migrations.MigrationRunner`.
- Combine with adapter-kit to inject a `Database` instance per request.
- Chain queries with vector-kit by persisting embeddings and retrieving them with the same tenant context.

## Interoperability
- Works with config-kit to load DSNs, credentials, and connection pool sizes.
- Observability-kit can wrap all database calls via the provided instrumentation middleware.
- Export CDC (change data capture) events to event-kit for downstream processing.

## Operations & Observability
- Metrics: `db_queries_total`, `db_query_latency_seconds`, `db_cache_hits_total` (exposed when instrumentation is enabled).
- Logs: structured logging around slow queries and retries.
- Pooling: configure `pooling.AsyncConnectionPool` for Postgres/MySQL adapters.
- Health checks: `db_kit.healthcheck.verify()` ensures connectivity during startup probes.

## Testing & QA
- Use `db_kit.adapters.in_memory.InMemoryAdapter` or SQLite adapter for fast unit tests.
- Snapshot expected SQL by enabling debug logging on adapters.
- Contract tests ensure custom adapters implement the full interface (see `tests/test_contracts.py`).

## Troubleshooting
- **RLS errors:** confirm `set_access_token` is called with a valid JWT and policies exist for tables.
- **Connection exhaustion:** tune pool size via config-kit and close connections gracefully on shutdown.
- **Cache stale data:** call `db.invalidate_cache(table)` after bulk updates or disable caching per-query.

## Primary API Surface
- `Database.supabase(url=None, anon_key=None)` factory
- `Database(adapter=...)` with custom adapter
- `Database.set_access_token(token)`
- `Database.query(table, filters=None, select=None, order_by=None, limit=None, offset=None)`
- `Database.get_single(table, filters=None, select=None)`
- `Database.insert(table, data, returning=None)`
- `Database.update(table, data, filters, returning=None)`
- `Database.delete(table, filters)`
- `Database.tenant_context(tenant_id)` async context manager
- `MigrationRunner(run_migrations)`

## Additional Resources
- Examples: `db-kit/examples/`
- Tests: `db-kit/tests/`
- Related concepts: [Architecture](../concepts/architecture.md), [Patterns](../concepts/patterns.md), [Testing & Quality](../concepts/testing-quality.md)
