# Migrations Quick Reference

## Current Status

✅ **Atlas migration system is fully implemented and integrated**

## Files

- `backend/schema.hcl` - Schema definition (HCL format)
- `backend/atlas.hcl` - Configuration for all environments
- `backend/.env.local` - Environment variables
- `backend/internal/db/migrations.go` - Migration runner
- `backend/internal/db/migrations/20250130000000_init.sql` - Initial migration

## Adding a New Migration

### Step 1: Create Migration File
```bash
cd backend/internal/db/migrations
touch YYYYMMDDHHMMSS_description.sql
```

Example: `20250131120000_add_user_preferences.sql`

### Step 2: Write SQL
```sql
-- Add user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  preferences jsonb DEFAULT '{}'::jsonb,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
```

### Step 3: Rebuild and Test
```bash
cd backend
go build -o tracertm-backend
./tracertm-backend  # Runs migrations automatically
```

## Checking Migration Status

### View Applied Migrations
```bash
psql $DATABASE_URL -c "SELECT * FROM schema_migrations ORDER BY version;"
```

### View Migration Files
```bash
ls -la backend/internal/db/migrations/
```

## Environments

### Local Development
```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tracertm_dev
go run main.go
```

### Staging
```bash
export DATABASE_URL_STAGING=postgresql://user:pass@staging.db.com:5432/tracertm
# Deploy application
```

### Production
```bash
export DATABASE_URL_PROD=postgresql://user:pass@prod.db.com:5432/tracertm
# Deploy application
```

### Supabase
```bash
export SUPABASE_DATABASE_URL=postgresql://postgres:pass@db.supabase.co:5432/postgres
# Deploy application
```

## Common Tasks

### Reset Local Database
```bash
dropdb tracertm_dev
createdb tracertm_dev
go run main.go  # Runs all migrations
```

### View Current Schema
```bash
psql $DATABASE_URL -c "\dt"  # List tables
psql $DATABASE_URL -c "\d profiles"  # Describe table
```

### Rollback (Manual)
```bash
# Delete migration record
psql $DATABASE_URL -c "DELETE FROM schema_migrations WHERE version = '20250131120000';"

# Drop table manually
psql $DATABASE_URL -c "DROP TABLE user_preferences;"

# Re-run application to re-apply if needed
```

## Best Practices

1. **Naming**: Use timestamp + descriptive name
   - ✅ `20250131120000_add_user_preferences.sql`
   - ❌ `migration.sql`
   - ❌ `add_table.sql`

2. **Idempotency**: Use `IF NOT EXISTS` / `IF EXISTS`
   ```sql
   CREATE TABLE IF NOT EXISTS ...
   DROP TABLE IF EXISTS ...
   ```

3. **Transactions**: Migrations run in transactions by default
   - Most DDL is transactional
   - Some operations (CREATE DATABASE) cannot be in transactions

4. **Testing**: Always test locally first
   ```bash
   go build && ./tracertm-backend
   ```

5. **Backups**: Always backup production before migrations
   ```bash
   pg_dump $DATABASE_URL > backup.sql
   ```

## Troubleshooting

### Migration Not Running
- Check: File is in `backend/internal/db/migrations/`
- Check: Filename format: `YYYYMMDDHHMMSS_*.sql`
- Check: DATABASE_URL is set
- Check: Application logs for errors

### "Column does not exist"
- Likely: Old database schema
- Solution: Drop and recreate database
- Command: `dropdb tracertm_dev && createdb tracertm_dev`

### "Duplicate key value"
- Likely: Migration already applied
- Check: `SELECT * FROM schema_migrations;`
- If stuck: Delete record and re-run

## Support

For issues or questions:
1. Check application logs
2. Check schema_migrations table
3. Verify DATABASE_URL is correct
4. Test with local database first

