# Atlas Configuration Template for TraceRTM

## Complete atlas.hcl Configuration

Create `backend/atlas.hcl`:

```hcl
# Atlas Configuration for TraceRTM

# Local Development Environment
env "local" {
  # Schema source
  src = "file://schema.hcl"
  
  # Development database (Docker)
  dev = "docker://postgres/15/dev?search_path=public"
  
  # Local database URL
  url = "postgresql://postgres:postgres@localhost:5432/tracertm_dev"
  
  # Migration configuration
  migration {
    dir = "file://migrations"
    format = "sql"
    # Disable transaction wrapping for certain migrations
    # disable_txn = false
  }
  
  # Lint configuration
  lint {
    # Detect destructive changes
    destructive = true
    # Detect data loss
    data_loss = true
  }
}

# Staging Environment
env "staging" {
  # Schema source
  src = "file://schema.hcl"
  
  # Staging database URL (from environment variable)
  url = getenv("DATABASE_URL_STAGING")
  
  # Migration configuration
  migration {
    dir = "file://migrations"
    format = "sql"
  }
  
  # Lint configuration
  lint {
    destructive = true
    data_loss = true
  }
}

# Production Environment
env "prod" {
  # Schema source
  src = "file://schema.hcl"
  
  # Production database URL (from environment variable)
  url = getenv("DATABASE_URL_PROD")
  
  # Migration configuration
  migration {
    dir = "file://migrations"
    format = "sql"
    # Require approval for production migrations
    # auto_approve = false
  }
  
  # Lint configuration
  lint {
    destructive = true
    data_loss = true
  }
}

# Supabase Environment
env "supabase" {
  # Schema source
  src = "file://schema.hcl"
  
  # Supabase database URL
  url = getenv("SUPABASE_DATABASE_URL")
  
  # Migration configuration
  migration {
    dir = "file://migrations"
    format = "sql"
  }
  
  # Lint configuration
  lint {
    destructive = true
    data_loss = true
  }
}
```

## Environment Variables

Create `.env.local`:

```bash
# Local Development
DATABASE_URL_LOCAL=postgresql://postgres:postgres@localhost:5432/tracertm_dev

# Staging
DATABASE_URL_STAGING=postgresql://user:pass@staging-db.supabase.co:5432/postgres

# Production
DATABASE_URL_PROD=postgresql://user:pass@prod-db.supabase.co:5432/postgres

# Supabase
SUPABASE_DATABASE_URL=postgresql://postgres:password@db.supabase.co:5432/postgres
```

## Common Commands

### Local Development

```bash
# Generate migration from schema changes
atlas migrate diff --env local --name add_users_table

# Apply migrations
atlas migrate apply --env local

# Check migration status
atlas migrate status --env local

# Lint migrations
atlas migrate lint --env local

# Inspect current schema
atlas schema inspect --env local

# Validate schema
atlas schema validate --env local
```

### Staging

```bash
# Generate migration
atlas migrate diff --env staging --name add_feature

# Apply migrations
atlas migrate apply --env staging

# Check status
atlas migrate status --env staging
```

### Production

```bash
# Generate migration
atlas migrate diff --env prod --name add_feature

# Lint before applying
atlas migrate lint --env prod

# Apply migrations (with caution!)
atlas migrate apply --env prod

# Check status
atlas migrate status --env prod
```

### Supabase

```bash
# Generate migration
atlas migrate diff --env supabase --name init

# Apply migrations
atlas migrate apply --env supabase

# Check status
atlas migrate status --env supabase
```

## Docker Setup for Local Development

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: tracertm_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start with:
```bash
docker-compose up -d
```

## Makefile Integration

Add to `backend/Makefile`:

```makefile
# Atlas migrations
.PHONY: migrate-diff
migrate-diff:
	atlas migrate diff --env local --name $(NAME)

.PHONY: migrate-apply
migrate-apply:
	atlas migrate apply --env local

.PHONY: migrate-status
migrate-status:
	atlas migrate status --env local

.PHONY: migrate-lint
migrate-lint:
	atlas migrate lint --env local

.PHONY: schema-inspect
schema-inspect:
	atlas schema inspect --env local

.PHONY: schema-validate
schema-validate:
	atlas schema validate --env local

.PHONY: migrate-prod
migrate-prod:
	atlas migrate apply --env prod

.PHONY: migrate-staging
migrate-staging:
	atlas migrate apply --env staging
```

## Next Steps

1. Create `backend/atlas.hcl` with this configuration
2. Create `backend/schema.hcl` with schema definition
3. Create `.env.local` with database URLs
4. Run `docker-compose up -d` to start PostgreSQL
5. Run `atlas migrate diff --env local --name init`
6. Review generated migration
7. Run `atlas migrate apply --env local`
8. Test with your application

## Resources

- Atlas Docs: https://atlasgo.io/
- Configuration Reference: https://atlasgo.io/guides/config
- Environment Variables: https://atlasgo.io/guides/config#env

