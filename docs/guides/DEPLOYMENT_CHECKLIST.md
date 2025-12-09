# Deployment Checklist - TraceRTM with Atlas Migrations

## Pre-Deployment Verification

### Code Quality
- [ ] Build successful: `go build -o tracertm-backend`
- [ ] No compilation errors
- [ ] Binary size reasonable (~19MB)
- [ ] All tests passing: `go test ./...`

### Migration System
- [ ] `backend/schema.hcl` exists and is valid
- [ ] `backend/atlas.hcl` exists and is valid
- [ ] `backend/internal/db/migrations.go` exists
- [ ] `backend/internal/db/migrations/20250130000000_init.sql` exists
- [ ] Migration files are named correctly (YYYYMMDDHHMMSS_*.sql)
- [ ] All migrations are in `backend/internal/db/migrations/`

### Dependencies
- [ ] `github.com/lib/pq` is in go.mod
- [ ] `go mod tidy` has been run
- [ ] No unused imports
- [ ] All imports are correct

### Documentation
- [ ] IMPLEMENTATION_SUMMARY.md reviewed
- [ ] ATLAS_IMPLEMENTATION_COMPLETE.md reviewed
- [ ] MIGRATIONS_QUICK_REFERENCE.md reviewed
- [ ] ATLAS_MIGRATION_SYSTEM_GUIDE.md reviewed

## Local Testing

### Setup
- [ ] PostgreSQL is running locally
- [ ] Test database created: `createdb tracertm_dev`
- [ ] DATABASE_URL environment variable set
- [ ] `.env.local` file exists with correct URLs

### Testing
- [ ] Application starts: `go run main.go`
- [ ] Migrations run automatically on startup
- [ ] schema_migrations table created
- [ ] All 8 tables created successfully
- [ ] All indexes created
- [ ] All foreign keys created
- [ ] Application responds to requests

### Verification
```bash
# Check migrations applied
psql $DATABASE_URL -c "SELECT * FROM schema_migrations;"

# Check tables created
psql $DATABASE_URL -c "\dt"

# Check specific table
psql $DATABASE_URL -c "\d profiles"
```

## Staging Deployment

### Pre-Deployment
- [ ] Staging database URL obtained
- [ ] Staging database is PostgreSQL 14+
- [ ] Backup of staging database created
- [ ] DATABASE_URL_STAGING environment variable set
- [ ] Team notified of deployment

### Deployment
- [ ] Build binary: `go build -o tracertm-backend`
- [ ] Deploy binary to staging
- [ ] Set DATABASE_URL_STAGING environment variable
- [ ] Start application
- [ ] Check logs for migration errors
- [ ] Verify schema_migrations table
- [ ] Verify all tables created

### Testing
- [ ] Application starts successfully
- [ ] API endpoints respond
- [ ] Database queries work
- [ ] WebSocket connections work
- [ ] No errors in logs

### Rollback Plan
- [ ] If migrations fail, stop application
- [ ] Restore database from backup
- [ ] Fix migration issues
- [ ] Re-deploy

## Production Deployment

### Pre-Deployment
- [ ] Production database URL obtained
- [ ] Production database is PostgreSQL 14+
- [ ] Full backup of production database created
- [ ] DATABASE_URL_PROD environment variable set
- [ ] Maintenance window scheduled
- [ ] Team notified of deployment
- [ ] Rollback plan documented

### Deployment
- [ ] Build binary: `go build -o tracertm-backend`
- [ ] Deploy binary to production
- [ ] Set DATABASE_URL_PROD environment variable
- [ ] Start application
- [ ] Monitor logs for migration errors
- [ ] Verify schema_migrations table
- [ ] Verify all tables created

### Testing
- [ ] Application starts successfully
- [ ] API endpoints respond
- [ ] Database queries work
- [ ] WebSocket connections work
- [ ] No errors in logs
- [ ] Performance is acceptable

### Post-Deployment
- [ ] Monitor application for 24 hours
- [ ] Check error logs regularly
- [ ] Verify database performance
- [ ] Confirm all features working
- [ ] Document any issues

## Supabase Deployment

### Pre-Deployment
- [ ] Supabase project created
- [ ] Database URL obtained
- [ ] SUPABASE_DATABASE_URL environment variable set
- [ ] Backup of Supabase database created

### Deployment
- [ ] Build binary: `go build -o tracertm-backend`
- [ ] Deploy to Supabase
- [ ] Set SUPABASE_DATABASE_URL environment variable
- [ ] Start application
- [ ] Check logs for migration errors
- [ ] Verify schema_migrations table
- [ ] Verify all tables created

### Testing
- [ ] Application starts successfully
- [ ] API endpoints respond
- [ ] Database queries work
- [ ] WebSocket connections work
- [ ] No errors in logs

## Adding New Migrations

### Before Adding
- [ ] Understand the schema change
- [ ] Plan the migration
- [ ] Test locally first
- [ ] Get code review

### Adding Migration
- [ ] Create file: `YYYYMMDDHHMMSS_description.sql`
- [ ] Write SQL migration
- [ ] Use IF EXISTS/IF NOT EXISTS for idempotency
- [ ] Test locally: `go build && ./tracertm-backend`
- [ ] Verify schema_migrations table
- [ ] Verify changes applied

### After Adding
- [ ] Commit to version control
- [ ] Deploy to staging
- [ ] Test on staging
- [ ] Deploy to production
- [ ] Monitor for issues

## Troubleshooting

### Migration Fails
- [ ] Check DATABASE_URL is set correctly
- [ ] Check migration file syntax
- [ ] Check for SQL errors in logs
- [ ] Restore database from backup
- [ ] Fix migration and re-deploy

### Application Won't Start
- [ ] Check DATABASE_URL is set
- [ ] Check database is running
- [ ] Check database credentials
- [ ] Check logs for errors
- [ ] Verify schema_migrations table exists

### Schema Mismatch
- [ ] Check schema_migrations table
- [ ] Verify all migrations applied
- [ ] Check for manual schema changes
- [ ] Restore from backup if needed

## Rollback Procedure

### If Deployment Fails
1. Stop application
2. Restore database from backup
3. Fix issues
4. Re-deploy

### If Issues Found Post-Deployment
1. Stop application
2. Restore database from backup
3. Investigate issues
4. Fix and re-deploy

## Success Criteria

- [ ] Application starts without errors
- [ ] All migrations applied successfully
- [ ] schema_migrations table has all migrations
- [ ] All 8 tables created
- [ ] All indexes created
- [ ] All foreign keys created
- [ ] API endpoints respond
- [ ] Database queries work
- [ ] WebSocket connections work
- [ ] No errors in logs
- [ ] Performance is acceptable

## Sign-Off

- [ ] Developer: _________________ Date: _______
- [ ] QA: _________________ Date: _______
- [ ] DevOps: _________________ Date: _______
- [ ] Product: _________________ Date: _______

---

**Status**: Ready for deployment ✅

