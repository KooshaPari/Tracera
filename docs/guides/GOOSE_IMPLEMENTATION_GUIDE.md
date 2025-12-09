# Goose Implementation Guide for TraceRTM

## Step 1: Install Goose

```bash
go install github.com/pressly/goose/v3/cmd/goose@latest

# Verify installation
goose --version
```

## Step 2: Create Migrations Directory

```bash
mkdir -p backend/migrations
```

## Step 3: Create Initial Migration

```bash
cd backend
goose -dir migrations create init sql
```

Creates: `backend/migrations/00001_init.sql`

## Step 4: Write Initial Migration

Edit `backend/migrations/00001_init.sql`:

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
    full_name VARCHAR(255),
    avatar_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_profiles_auth_id ON profiles(auth_id);
CREATE INDEX idx_profiles_workos_user_id ON profiles(workos_user_id);
CREATE INDEX idx_profiles_email ON profiles(email);

-- +goose Down
DROP INDEX IF EXISTS idx_profiles_email;
DROP INDEX IF EXISTS idx_profiles_workos_user_id;
DROP INDEX IF EXISTS idx_profiles_auth_id;
DROP TABLE IF EXISTS profiles;
DROP EXTENSION IF EXISTS "vector";
DROP EXTENSION IF EXISTS "pg_trgm";
DROP EXTENSION IF EXISTS "uuid-ossp";
```

## Step 5: Create Go Migration Helper

Create `backend/internal/db/migrations.go`:

```go
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
    
    if err := goose.SetDialect("postgres"); err != nil {
        return err
    }
    
    goose.SetBaseFS(embedMigrations)
    
    if err := goose.UpContext(ctx, conn.Conn().PgConn(), "migrations"); err != nil {
        return err
    }
    
    return nil
}
```

## Step 6: Integrate with main.go

```go
package main

import (
    "context"
    "github.com/kooshapari/tracertm-backend/internal/db"
)

func main() {
    // ... setup pool ...
    
    // Run migrations
    if err := db.RunMigrations(context.Background(), pool); err != nil {
        log.Fatalf("Failed to run migrations: %v", err)
    }
    
    // ... rest of app ...
}
```

## Step 7: Test Locally

```bash
# Set environment variables
export GOOSE_DRIVER=postgres
export GOOSE_DBSTRING="postgresql://user:password@localhost:5432/tracertm"
export GOOSE_MIGRATION_DIR=backend/migrations

# Check status
goose status

# Run migrations
goose up

# Verify
goose version
```

## Step 8: Create Additional Migrations

```bash
# Create new migration
goose -dir backend/migrations create add_projects_table sql

# Edit the file and add your schema
```

## Step 9: Add to Makefile

```makefile
.PHONY: db-migrate db-rollback db-status

db-migrate:
	@echo 'Running migrations...'
	goose -dir backend/migrations up

db-rollback:
	@echo 'Rolling back last migration...'
	goose -dir backend/migrations down

db-status:
	@echo 'Migration status:'
	goose -dir backend/migrations status
```

## Step 10: CI/CD Integration

Add to your deployment script:

```bash
#!/bin/bash
set -e

# Run migrations before deployment
goose -dir backend/migrations up

# Start application
./tracertm-backend
```

## Common Workflows

### Create New Migration
```bash
goose -dir backend/migrations create add_column_to_users sql
```

### Check Status
```bash
goose -dir backend/migrations status
```

### Rollback One
```bash
goose -dir backend/migrations down
```

### Rollback All
```bash
goose -dir backend/migrations down-to 0
```

### Run Specific Number
```bash
goose -dir backend/migrations up 2
```

## Best Practices

1. **Always write Down migrations** - Test rollbacks
2. **Use IF EXISTS/IF NOT EXISTS** - Make idempotent
3. **Keep migrations small** - One logical change per file
4. **Test locally first** - Before production
5. **Commit migrations** - Version control them
6. **Document changes** - Add comments in SQL
7. **Use transactions** - Default behavior, safe

## Troubleshooting

### Migration fails
```bash
# Check status
goose status

# Check logs
goose -v status
```

### Need to fix migration
```bash
# Rollback
goose down

# Edit migration file
# Re-run
goose up
```

### Reset database
```bash
# Rollback all
goose down-to 0

# Re-run all
goose up
```

