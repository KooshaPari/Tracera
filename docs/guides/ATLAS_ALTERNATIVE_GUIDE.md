# Atlas - Alternative Migration Tool for TraceRTM

## What is Atlas?

Atlas is a **schema-as-code** migration tool that takes a declarative approach:

```
Traditional (Goose):  Write migrations → Apply to DB
Atlas:                Define schema → Atlas generates migrations
```

## Key Differences from Goose

### Goose (Versioned Migrations)
```sql
-- +goose Up
CREATE TABLE users (id UUID PRIMARY KEY);

-- +goose Down
DROP TABLE users;
```

### Atlas (Schema-as-Code)
```hcl
table "users" {
  schema = schema.public
  column "id" {
    type = uuid
    primary_key = true
  }
}
```

## Atlas Advantages

### 1. Auto-Generate Migrations
```bash
# Define schema in schema.hcl
# Atlas generates migration automatically
atlas migrate diff --env local
```

### 2. Schema Drift Detection
```bash
# Detect differences between code and database
atlas schema inspect -u "postgresql://..."
```

### 3. Powerful CLI
```bash
atlas migrate lint          # Lint migrations
atlas migrate apply         # Apply migrations
atlas migrate status        # Check status
atlas migrate rollback      # Rollback
```

### 4. Works with sqlc
```bash
# Generate schema from sqlc queries
atlas schema inspect -u "postgresql://..." --format hcl
```

## Atlas Disadvantages

### 1. Steeper Learning Curve
- HCL syntax to learn
- Different mental model
- More configuration

### 2. No Embedded Migrations
- CLI-only approach
- Can't compile into binary
- Requires separate deployment

### 3. Smaller Community
- Less Stack Overflow help
- Fewer examples
- Newer tool

### 4. Overkill for Simple Projects
- More complex setup
- More features than needed
- Overhead for small schemas

## When to Use Atlas

✅ **Use Atlas if:**
- You want auto-generated migrations
- You have complex schema evolution
- You're using Ent ORM
- You need schema drift detection
- You have multiple databases
- You want declarative schema

❌ **Don't use Atlas if:**
- You prefer manual control
- You need embedded migrations
- You want simplicity
- You have simple schema
- You prefer versioned migrations

## Quick Start with Atlas

### 1. Install Atlas
```bash
go install ariga.io/atlas/cmd/atlas@latest
```

### 2. Create Schema File
```bash
# schema.hcl
table "users" {
  schema = schema.public
  column "id" {
    null = false
    type = uuid
    default = sql("gen_random_uuid()")
  }
  column "email" {
    null = false
    type = varchar(255)
  }
  primary_key {
    columns = [column.id]
  }
  index "idx_email" {
    columns = [column.email]
    unique = true
  }
}
```

### 3. Generate Migration
```bash
atlas migrate diff --env local
```

### 4. Apply Migration
```bash
atlas migrate apply --env local
```

### 5. Check Status
```bash
atlas migrate status --env local
```

## Atlas Configuration

### atlas.hcl
```hcl
env "local" {
  src = "file://schema.hcl"
  dev = "docker://postgres/15/dev?search_path=public"
  url = "postgresql://user:pass@localhost:5432/tracertm"
  migration {
    dir = "file://migrations"
  }
}
```

## Atlas vs Goose Comparison

| Aspect | Atlas | Goose |
|--------|-------|-------|
| **Approach** | Declarative | Versioned |
| **Migration Generation** | Auto | Manual |
| **Schema Drift** | Detects | No |
| **Learning Curve** | Medium | Easy |
| **Setup Time** | 15 min | 5 min |
| **Embedded** | No | Yes |
| **Community** | Growing | Large |
| **Complexity** | High | Low |
| **Best For** | Complex schemas | Simple schemas |

## Integration with Go

### Using Atlas CLI
```bash
# In CI/CD or deployment
atlas migrate apply --env prod
```

### Using Atlas Go SDK
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

## Recommendation for TraceRTM

### Start with Goose
- ✅ Simpler to implement
- ✅ Works perfectly with pgx
- ✅ Embedded migrations
- ✅ Large community
- ✅ Production-proven

### Consider Atlas Later
- If you need auto-generated migrations
- If schema becomes complex
- If you want drift detection
- If you're using Ent ORM

## Migration Path: Goose → Atlas

If you start with Goose and want to migrate to Atlas later:

1. Export current schema from database
2. Create schema.hcl from exported schema
3. Generate migrations with Atlas
4. Switch to Atlas for future migrations

This is possible because both tools work with PostgreSQL.

## Conclusion

**For TraceRTM: Start with Goose**

- Simpler
- Faster to implement
- Works great with pgx
- Embedded migrations
- Large community

**Migrate to Atlas later if:**
- Schema becomes complex
- You need auto-generation
- You want drift detection
- You're using Ent ORM

**Decision: Goose now, Atlas later if needed**

