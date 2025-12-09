# Go Database Migrations Guide - TraceRTM

## Overview

For Go + sqlc + pgx, you have **two excellent options**:

### 1. **Goose** (Recommended for TraceRTM)
- ✅ SQL + Go migrations
- ✅ Embedded migrations support
- ✅ Simple CLI
- ✅ Works with pgx
- ✅ Supabase compatible

### 2. **golang-migrate**
- ✅ Lightweight
- ✅ Multiple sources (file, GitHub, S3)
- ✅ CLI + library
- ✅ Works with pgx

## Setup: Goose (Recommended)

### 1. Install Goose

```bash
go install github.com/pressly/goose/v3/cmd/goose@latest
```

### 2. Create Migrations Directory

```bash
mkdir -p backend/migrations
```

### 3. Create Initial Migration

```bash
goose -dir backend/migrations create init sql
```

This creates: `backend/migrations/00001_init.sql`

### 4. Edit Migration File

```sql
-- +goose Up
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id UUID NOT NULL UNIQUE,
    workos_user_id TEXT UNIQUE,
    workos_org_id TEXT,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- +goose Down
DROP TABLE IF EXISTS profiles;
DROP EXTENSION IF EXISTS "vector";
DROP EXTENSION IF EXISTS "pg_trgm";
DROP EXTENSION IF EXISTS "uuid-ossp";
```

### 5. Run Migrations

```bash
# Using environment variables
export GOOSE_DRIVER=postgres
export GOOSE_DBSTRING="postgresql://user:password@localhost:5432/tracertm"
export GOOSE_MIGRATION_DIR=backend/migrations

goose status
goose up
```

### 6. Integrate with Go Code

```go
package main

import (
    "github.com/pressly/goose/v3"
    "github.com/jackc/pgx/v5/pgxpool"
)

func runMigrations(pool *pgxpool.Pool) error {
    conn, err := pool.Acquire(context.Background())
    if err != nil {
        return err
    }
    defer conn.Release()
    
    if err := goose.SetDialect("postgres"); err != nil {
        return err
    }
    
    if err := goose.UpContext(context.Background(), conn.Conn().PgConn(), "backend/migrations"); err != nil {
        return err
    }
    
    return nil
}
```

## Common Commands

```bash
# Check status
goose status

# Run all pending migrations
goose up

# Run specific number of migrations
goose up 2

# Rollback one migration
goose down

# Rollback to specific version
goose down-to 20250101000000

# Create new migration
goose create add_users_table sql
goose create process_data go

# Check version
goose version
```

## Best Practices

1. **Naming**: Use timestamps + descriptive names
2. **Transactions**: Use `-- +goose NO TRANSACTION` only when necessary
3. **Idempotent**: Use `IF NOT EXISTS` / `IF EXISTS`
4. **Testing**: Test migrations locally before production
5. **Versioning**: Keep migrations in git
6. **Rollback**: Always write Down migrations

## Integration with Supabase

Supabase migrations go in `supabase/migrations/` and are applied via:

```bash
supabase db push
```

For Go code migrations, use Goose in `backend/migrations/`.

## Next Steps

1. Install Goose: `go install github.com/pressly/goose/v3/cmd/goose@latest`
2. Create migrations directory: `mkdir -p backend/migrations`
3. Create first migration: `goose -dir backend/migrations create init sql`
4. Integrate with main.go
5. Test locally

