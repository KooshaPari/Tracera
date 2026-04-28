# Database Migrations Summary - TraceRTM

## What You Need to Know

### Current Setup
- **Backend**: Go + sqlc + pgx
- **Database**: PostgreSQL 14+ on Supabase
- **Auth**: Supabase (via WorkOS)
- **Schema**: Currently in `backend/schema.sql`

### Migration Challenge
You need a way to:
1. Version control schema changes
2. Apply migrations to production
3. Rollback if needed
4. Integrate with Go code

## Solution: Goose

**Goose** is the best choice because:
- ✅ Native Go support
- ✅ Works with pgx
- ✅ SQL + Go migrations
- ✅ Embedded migrations
- ✅ Simple CLI
- ✅ Active community

## Quick Implementation

### 1. Install
```bash
go install github.com/pressly/goose/v3/cmd/goose@latest
```

### 2. Create Directory
```bash
mkdir -p backend/migrations
```

### 3. Create First Migration
```bash
cd backend
goose -dir migrations create init sql
```

### 4. Edit Migration
```sql
-- +goose Up
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id UUID NOT NULL UNIQUE,
    workos_user_id TEXT UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- +goose Down
DROP TABLE profiles;
DROP EXTENSION IF EXISTS "vector";
DROP EXTENSION IF EXISTS "pg_trgm";
DROP EXTENSION IF EXISTS "uuid-ossp";
```

### 5. Test
```bash
goose -dir migrations up
goose status
```

### 6. Integrate with Go
```go
// backend/internal/db/migrations.go
package db

import (
    "context"
    "embed"
    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/pressly/goose/v3"
)

//go:embed migrations/*.sql
var embedMigrations embed.FS

func RunMigrations(ctx context.Context, pool *pgxpool.Pool) error {
    conn, err := pool.Acquire(ctx)
    if err != nil {
        return err
    }
    defer conn.Release()
    
    goose.SetBaseFS(embedMigrations)
    if err := goose.SetDialect("postgres"); err != nil {
        return err
    }
    
    return goose.UpContext(ctx, conn.Conn().PgConn(), "migrations")
}
```

### 7. Call in main.go
```go
if err := db.RunMigrations(context.Background(), pool); err != nil {
    log.Fatalf("Migrations failed: %v", err)
}
```

## Common Commands

```bash
goose status              # Check status
goose up                  # Run migrations
goose down                # Rollback one
goose down-to 0           # Rollback all
goose create name sql     # Create migration
```

## File Structure

```
backend/
├── migrations/
│   ├── 00001_init.sql
│   ├── 00002_profiles.sql
│   ├── 00003_projects.sql
│   └── 00004_items.sql
├── internal/
│   └── db/
│       └── migrations.go
└── main.go
```

## Integration with Supabase

- **Supabase migrations**: `supabase/migrations/` (auth)
- **Go migrations**: `backend/migrations/` (app schema)
- Both work together on same PostgreSQL database

## Best Practices

1. ✅ Always write Down migrations
2. ✅ Use IF EXISTS / IF NOT EXISTS
3. ✅ Keep migrations small
4. ✅ Test locally first
5. ✅ Commit to git
6. ✅ Use transactions
7. ✅ Document changes

## Documentation Files

1. **GO_MIGRATIONS_GUIDE.md** - Quick start
2. **MIGRATION_TOOLS_COMPARISON.md** - Tool comparison
3. **GOOSE_IMPLEMENTATION_GUIDE.md** - Step-by-step guide
4. **MIGRATIONS_SUMMARY.md** - This file

## Next Steps

1. Install Goose
2. Create migrations directory
3. Create first migration
4. Test locally
5. Integrate with main.go
6. Deploy to Supabase

Ready to implement? Start with `GO_MIGRATIONS_GUIDE.md`!

