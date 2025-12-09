# Atlas Step-by-Step Implementation for TraceRTM

## Phase 1: Setup (5 minutes)

### Step 1: Install Atlas
```bash
go install ariga.io/atlas/cmd/atlas@latest
```

Verify installation:
```bash
atlas version
```

### Step 2: Create Migrations Directory
```bash
mkdir -p backend/migrations
```

### Step 3: Create schema.hcl
Copy content from `ATLAS_SCHEMA_TEMPLATE.md` to `backend/schema.hcl`

### Step 4: Create atlas.hcl
Copy content from `ATLAS_CONFIG_TEMPLATE.md` to `backend/atlas.hcl`

### Step 5: Create .env.local
```bash
cat > backend/.env.local << 'EOF'
DATABASE_URL_LOCAL=postgresql://postgres:postgres@localhost:5432/tracertm_dev
DATABASE_URL_STAGING=postgresql://user:pass@staging-db.supabase.co:5432/postgres
DATABASE_URL_PROD=postgresql://user:pass@prod-db.supabase.co:5432/postgres
SUPABASE_DATABASE_URL=postgresql://postgres:password@db.supabase.co:5432/postgres
EOF
```

## Phase 2: Local Testing (10 minutes)

### Step 6: Start PostgreSQL
```bash
docker-compose up -d
```

### Step 7: Generate First Migration
```bash
cd backend
atlas migrate diff --env local --name init
```

This creates `backend/migrations/20250101000000_init.sql`

### Step 8: Review Migration
```bash
cat migrations/20250101000000_init.sql
```

### Step 9: Apply Migration
```bash
atlas migrate apply --env local
```

### Step 10: Verify Migration
```bash
atlas migrate status --env local
```

## Phase 3: Integration with Go (10 minutes)

### Step 11: Add Atlas to go.mod
```bash
go get ariga.io/atlas/sql/migrate
```

### Step 12: Create Migration Helper
Create `backend/internal/db/migrations.go`:

```go
package db

import (
    "context"
    "database/sql"
    "embed"
    "fmt"
    
    "ariga.io/atlas/sql/migrate"
    "ariga.io/atlas/sql/sqltool"
)

//go:embed migrations/*.sql
var migrations embed.FS

func RunMigrations(ctx context.Context, db *sql.DB) error {
    dir, err := sqltool.NewGoFS(migrations)
    if err != nil {
        return fmt.Errorf("failed to create migration dir: %w", err)
    }
    
    m, err := migrate.NewMigrator(db, dir)
    if err != nil {
        return fmt.Errorf("failed to create migrator: %w", err)
    }
    
    return m.Migrate(ctx)
}
```

### Step 13: Update main.go
```go
import "your-module/internal/db"

func main() {
    // ... setup database connection ...
    
    if err := db.RunMigrations(context.Background(), dbConn); err != nil {
        log.Fatal(err)
    }
    
    // ... rest of app ...
}
```

## Phase 4: Schema Changes (5 minutes)

### Step 14: Make Schema Change
Edit `backend/schema.hcl` to add a new table or column

### Step 15: Generate Migration
```bash
atlas migrate diff --env local --name add_new_feature
```

### Step 16: Review and Apply
```bash
cat migrations/20250101000001_add_new_feature.sql
atlas migrate apply --env local
```

## Phase 5: Deployment (10 minutes)

### Step 17: Lint Migrations
```bash
atlas migrate lint --env prod
```

### Step 18: Apply to Staging
```bash
atlas migrate apply --env staging
```

### Step 19: Test on Staging
- Run integration tests
- Verify data integrity
- Check performance

### Step 20: Apply to Production
```bash
atlas migrate apply --env prod
```

## Common Workflows

### Adding a New Table
1. Edit `schema.hcl` - add table definition
2. Run `atlas migrate diff --env local --name add_table_name`
3. Review migration
4. Run `atlas migrate apply --env local`
5. Test
6. Deploy to staging/prod

### Adding a Column
1. Edit `schema.hcl` - add column to table
2. Run `atlas migrate diff --env local --name add_column_name`
3. Review migration
4. Run `atlas migrate apply --env local`
5. Test
6. Deploy to staging/prod

### Modifying a Column
1. Edit `schema.hcl` - modify column definition
2. Run `atlas migrate diff --env local --name modify_column_name`
3. Review migration (may require data migration)
4. Run `atlas migrate apply --env local`
5. Test
6. Deploy to staging/prod

### Creating an Index
1. Edit `schema.hcl` - add index to table
2. Run `atlas migrate diff --env local --name add_index_name`
3. Review migration
4. Run `atlas migrate apply --env local`
5. Test
6. Deploy to staging/prod

## Troubleshooting

### Migration Failed
```bash
# Check status
atlas migrate status --env local

# Inspect schema
atlas schema inspect --env local

# Validate schema
atlas schema validate --env local
```

### Rollback Migration
```bash
# Check available migrations
atlas migrate status --env local

# Rollback last migration
atlas migrate down --env local
```

### Schema Drift
```bash
# Detect drift
atlas schema inspect --env local

# Fix drift
atlas migrate diff --env local --name fix_drift
```

## Next Steps

1. Follow Phase 1: Setup (5 min)
2. Follow Phase 2: Local Testing (10 min)
3. Follow Phase 3: Integration with Go (10 min)
4. Follow Phase 4: Schema Changes (5 min)
5. Follow Phase 5: Deployment (10 min)

**Total Time: ~40 minutes**

## Resources

- Atlas Docs: https://atlasgo.io/
- Migration Guide: https://atlasgo.io/guides/migration
- Schema Reference: https://atlasgo.io/guides/ddl

