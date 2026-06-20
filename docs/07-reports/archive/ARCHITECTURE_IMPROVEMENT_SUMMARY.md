# Architecture Improvement: GORM → sqlc + pgx

## Summary

You identified a critical architectural issue: **GORM was not the right choice for TraceRTM's complexity.**

We've now switched to **sqlc + pgx**, which is significantly better for this project.

## The Problem with GORM

1. **Complex Queries**: TraceRTM needs recursive CTEs, graph traversals, and complex joins
2. **Hidden SQL**: GORM abstracts SQL, making optimization difficult
3. **Performance Overhead**: Reflection and ORM overhead not suitable for 1000+ agents
4. **Graph Limitations**: Hard to express complex relationship queries
5. **Compliance Issues**: Opaque query generation bad for traceability system

## The Solution: sqlc + pgx

**sqlc** generates type-safe Go code from explicit SQL queries.
**pgx** is a high-performance PostgreSQL driver.

Together they provide:
- ✅ Compile-time type safety
- ✅ Explicit, auditable SQL
- ✅ Full support for recursive CTEs
- ✅ Direct database access (no ORM overhead)
- ✅ Perfect for graph queries
- ✅ Better performance

## What Changed

### Files Created
1. **backend/schema.sql** - Database schema with all tables and indexes
2. **backend/queries.sql** - SQL queries for sqlc to generate Go code
3. **backend/sqlc.yaml** - sqlc configuration
4. **backend/SQLC_MIGRATION_GUIDE.md** - Comprehensive migration guide
5. **SQLC_DECISION_SUMMARY.md** - Decision rationale

### Files Updated
1. **backend/go.mod** - Replaced GORM with pgx
2. **backend/main.go** - Updated to use pgxpool
3. **backend/internal/database/database.go** - Rewrote for pgx
4. **backend/README.md** - Updated documentation

## Key Features

### Database Schema (schema.sql)
- Projects table
- Items table (Features, Code, Tests, APIs, etc.)
- Links table (60+ link types)
- Agents table (1-1000 concurrent)
- Events table (event sourcing)
- All indexes for performance

### SQL Queries (queries.sql)
- CRUD operations for all entities
- Pagination support
- Filtering by type, status, project
- Ready for recursive CTEs

### Configuration (sqlc.yaml)
- PostgreSQL engine
- Go code generation
- Type-safe queries
- JSON tags for API responses

## Next Steps

1. **Install sqlc**:
   ```bash
   go install github.com/sqlc-dev/sqlc/cmd/sqlc@latest
   ```

2. **Generate code**:
   ```bash
   cd backend
   sqlc generate
   ```

3. **Update handlers** to use generated queries

4. **Test**:
   ```bash
   go test ./... -v
   ```

## Benefits

| Aspect | Before (GORM) | After (sqlc + pgx) |
|--------|---------------|-------------------|
| Complex Queries | ❌ Hard | ✅ Easy |
| Type Safety | ⚠️ Runtime | ✅ Compile-time |
| Performance | ⚠️ Overhead | ✅ Direct |
| Graph Queries | ❌ Limited | ✅ Full |
| Explicit SQL | ❌ Hidden | ✅ Visible |
| Compliance | ⚠️ Opaque | ✅ Auditable |

## Documentation

- **SQLC_DECISION_SUMMARY.md** - Why we made this choice
- **backend/SQLC_MIGRATION_GUIDE.md** - How to migrate
- **backend/README.md** - Setup and usage
- **backend/schema.sql** - Database schema
- **backend/queries.sql** - SQL queries

## References

- [sqlc Documentation](https://docs.sqlc.dev/)
- [pgx Documentation](https://github.com/jackc/pgx)
- [PostgreSQL Recursive CTEs](https://www.postgresql.org/docs/current/queries-with.html)

---

**Status**: ✅ Architecture improved, ready for code generation and handler updates.

