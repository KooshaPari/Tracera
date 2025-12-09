# Atlas Implementation Guide for TraceRTM

## Quick Start (15 minutes)

### 1. Install Atlas
```bash
go install ariga.io/atlas/cmd/atlas@latest
```

### 2. Create Migrations Directory
```bash
mkdir -p backend/migrations
```

### 3. Create Schema File
Create `backend/schema.hcl`:

```hcl
variable "db_url" {
  type = string
}

data "sql" "schema" {
  url = var.db_url
  query = <<-SQL
    SELECT * FROM information_schema.tables WHERE table_schema = 'public'
  SQL
}

table "profiles" {
  schema = schema.public
  column "id" {
    null = false
    type = uuid
    default = sql("gen_random_uuid()")
  }
  column "workos_id" {
    null = false
    type = varchar(255)
  }
  column "email" {
    null = false
    type = varchar(255)
  }
  column "created_at" {
    null = false
    type = timestamp
    default = sql("now()")
  }
  primary_key {
    columns = [column.id]
  }
  index "idx_workos_id" {
    columns = [column.workos_id]
    unique = true
  }
}

table "projects" {
  schema = schema.public
  column "id" {
    null = false
    type = uuid
    default = sql("gen_random_uuid()")
  }
  column "profile_id" {
    null = false
    type = uuid
  }
  column "name" {
    null = false
    type = varchar(255)
  }
  column "created_at" {
    null = false
    type = timestamp
    default = sql("now()")
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "fk_profile" {
    columns = [column.profile_id]
    ref_columns = [table.profiles.column.id]
    on_delete = CASCADE
  }
}

# Add more tables following the same pattern
```

### 4. Create atlas.hcl Configuration
```hcl
env "local" {
  src = "file://schema.hcl"
  dev = "docker://postgres/15/dev?search_path=public"
  url = "postgresql://user:pass@localhost:5432/tracertm"
  migration {
    dir = "file://migrations"
    format = "sql"
  }
}

env "prod" {
  src = "file://schema.hcl"
  url = "postgresql://user:pass@prod-db:5432/tracertm"
  migration {
    dir = "file://migrations"
    format = "sql"
  }
}
```

### 5. Generate First Migration
```bash
cd backend
atlas migrate diff --env local --name init
```

### 6. Apply Migration
```bash
atlas migrate apply --env local
```

### 7. Check Status
```bash
atlas migrate status --env local
```

## Integration with Go

### Add to main.go
```go
import "ariga.io/atlas/sql/migrate"

func runMigrations(ctx context.Context, db *sql.DB) error {
    dir, err := migrate.NewLocalDir("migrations")
    if err != nil {
        return err
    }
    
    m, err := migrate.NewMigrator(db, dir)
    if err != nil {
        return err
    }
    
    return m.Migrate(ctx)
}
```

### Call in main()
```go
func main() {
    // ... setup code ...
    
    if err := runMigrations(context.Background(), db); err != nil {
        log.Fatal(err)
    }
    
    // ... rest of app ...
}
```

## Common Commands

```bash
# Generate migration from schema changes
atlas migrate diff --env local --name add_users_table

# Apply migrations
atlas migrate apply --env local

# Check migration status
atlas migrate status --env local

# Lint migrations
atlas migrate lint --env local

# Rollback last migration
atlas migrate down --env local

# Inspect current schema
atlas schema inspect -u "postgresql://user:pass@localhost:5432/tracertm"

# Validate schema
atlas schema validate --env local
```

## Advantages of Atlas

✅ **Auto-generates migrations** from schema changes
✅ **Schema-as-code** (HCL or SQL)
✅ **Detects drift** between code and database
✅ **Powerful CLI** with many features
✅ **Works with sqlc** (can generate from sqlc schema)
✅ **Supports multiple databases**
✅ **Diff detection** (what changed?)
✅ **Rollback planning** (shows what will be rolled back)

## Next Steps

1. Install Atlas
2. Create schema.hcl with all tables
3. Create atlas.hcl configuration
4. Generate first migration
5. Test locally
6. Integrate with main.go
7. Deploy to Supabase

## Resources

- Atlas Docs: https://atlasgo.io/
- Atlas GitHub: https://github.com/ariga/atlas
- Schema HCL Reference: https://atlasgo.io/guides/ddl

