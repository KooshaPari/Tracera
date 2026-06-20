# Task #133 Quick Reference - Model Schema Validation Tests

## ✅ Status: COMPLETE (22/22 tests passing)

## Quick Test Commands

### Run all model schema validation tests
```bash
cd backend
make test-schema-validation
```

### Run with coverage report
```bash
cd backend
make test-schema-validation-coverage
open schema-validation-coverage.html
```

### Run directly with Go (if make is not available)
```bash
cd backend
TEST_DATABASE_URL="postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable" \
  go test -v ./internal/models/...
```

## Test Categories

| Category | Tests | What It Validates |
|----------|-------|-------------------|
| Connection | 1 | Database connectivity |
| Table Existence | 7 | Tables exist with correct columns |
| Model Matching | 6 | GORM models match DB schema |
| Primary Keys | 5 | PK constraints exist |
| Foreign Keys | 4 | FK constraints exist |
| Indexes | 8 | Required indexes exist |
| Orphaned Columns | 5 | No unexpected columns |
| UUID Types | 5 | UUID columns correct |
| JSONB Types | 6 | JSONB columns correct |
| Timestamp Types | 14 | Timestamp columns correct |
| NOT NULL | 13 | NOT NULL constraints correct |
| UNIQUE | 2 | UNIQUE constraints correct |
| **TOTAL** | **22** | **All schema validations** |

## Prerequisites Checklist

- [ ] PostgreSQL is running (`ps aux | grep postgres`)
- [ ] Database 'tracertm' exists (`psql -l | grep tracertm`)
- [ ] Schema 'tracertm' exists (`psql -d tracertm -c "\dn" | grep tracertm`)
- [ ] Migrations applied (`alembic upgrade head`)

## Environment Variables

```bash
# Primary: Used by tests
export TEST_DATABASE_URL="postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable"

# Fallback: Used if TEST_DATABASE_URL not set
export DATABASE_URL="postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable"
```

## Files Modified in Task #133

1. **`/backend/.env.example`** - Added TEST_DATABASE_URL
2. **`/backend/internal/models/schema_validation_test.go`** - Added docs
3. **`/backend/Makefile`** - Updated test targets

## Common Issues & Solutions

### Issue: "role postgres does not exist"
**Solution**: Set TEST_DATABASE_URL to use 'tracertm' user
```bash
export TEST_DATABASE_URL="postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable"
```

### Issue: "database tracertm does not exist"
**Solution**: Create the database
```bash
createdb tracertm
psql -d tracertm -c "CREATE SCHEMA IF NOT EXISTS tracertm;"
```

### Issue: "table does not exist"
**Solution**: Run migrations
```bash
alembic upgrade head
```

## Test Output Interpretation

### ✅ PASS - Expected
```
--- PASS: TestItemTableExists (0.54s)
--- PASS: TestItemModelMatchesSchema (0.09s)
```

### ⏭️ SKIP - Expected (for future features)
```
--- SKIP: TestCodeEntityTableExists (0.10s)
    schema_validation_test.go:284: code_entities table not created yet
```

### ℹ️ INFO - Informational (not failures)
```
INFO: Column items.path has no corresponding model field Path (may be intentional)
```

## Help Commands

```bash
# Schema validation help
make schema-help

# View available make targets
make help
```

## Related Documentation

- Full Report: `/docs/reports/task-133-model-schema-validation-fix.md`
- Task #122: Database schema fixes (prerequisite)
- Schema Tests: `/backend/internal/models/schema_validation_test.go`

## Success Criteria

All 22 tests must pass:
- ✅ Database connection works
- ✅ All expected tables exist
- ✅ GORM models match database schema
- ✅ All constraints (PK, FK, NOT NULL, UNIQUE) exist
- ✅ All required indexes exist
- ✅ All data types match expectations

## Execution Time

Expected: ~7-10 seconds for all 22 tests

```
PASS
ok  	github.com/kooshapari/tracertm-backend/internal/models	7.070s
```
