# Database Schema Validation Testing Guide

## Quick Start

### Running All Schema Validation Tests

```bash
cd backend
TEST_DATABASE_URL="postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable" \
  go test -v ./internal/models -run "Test.*"
```

### Using Environment File

Create or use the existing `.env.test` file:

```bash
# backend/.env.test
TEST_DATABASE_URL=postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable
```

Then run tests:

```bash
cd backend
source .env.test
go test -v ./internal/models -run "Test.*"
```

## Test Categories

### 1. Basic Schema Tests

**Table Existence**:
- `TestItemTableExists`
- `TestLinkTableExists`
- `TestProjectTableExists`
- `TestAgentTableExists`
- `TestViewTableExists`
- `TestProfileTableExists`
- `TestCodeEntityTableExists` (skipped if not migrated)

**Model Matching**:
- `TestItemModelMatchesSchema`
- `TestLinkModelMatchesSchema`
- `TestProjectModelMatchesSchema`
- `TestAgentModelMatchesSchema`
- `TestProfileModelMatchesSchema`

### 2. Constraint Tests

**Primary Keys**:
```bash
go test -v ./internal/models -run "TestPrimaryKeyConstraints"
```

**Foreign Keys**:
```bash
go test -v ./internal/models -run "TestForeignKeyConstraints"
```

**NOT NULL Constraints**:
```bash
go test -v ./internal/models -run "TestNotNullConstraints"
```

**Unique Constraints**:
```bash
go test -v ./internal/models -run "TestUniqueConstraints"
```

### 3. Type Consistency Tests

**UUID Types**:
```bash
go test -v ./internal/models -run "TestUUIDTypeConsistency"
```

**JSONB Types**:
```bash
go test -v ./internal/models -run "TestJSONBTypeConsistency"
```

**Timestamp Types**:
```bash
go test -v ./internal/models -run "TestTimestampTypeConsistency"
```

### 4. Index Tests

```bash
go test -v ./internal/models -run "TestIndexesExist"
```

### 5. Orphaned Columns Check

```bash
go test -v ./internal/models -run "TestNoOrphanedColumns"
```

## Running Specific Tests

### Single Test

```bash
TEST_DATABASE_URL="postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable" \
  go test -v ./internal/models -run "TestItemTableExists"
```

### Specific Subtest

```bash
TEST_DATABASE_URL="postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable" \
  go test -v ./internal/models -run "TestNotNullConstraints/items.project_id"
```

### Multiple Tests

```bash
TEST_DATABASE_URL="postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable" \
  go test -v ./internal/models -run "Test(Item|Link)"
```

## Continuous Integration

### GitHub Actions Example

```yaml
- name: Run Schema Validation Tests
  env:
    TEST_DATABASE_URL: postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable
  run: |
    cd backend
    go test -v ./internal/models -run "Test.*"
```

### Make Target

Add to `Makefile`:

```makefile
.PHONY: test-schema
test-schema:
	@echo "Running schema validation tests..."
	cd backend && \
	TEST_DATABASE_URL="postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable" \
	go test -v ./internal/models -run "Test.*"
```

Then run:

```bash
make test-schema
```

## Test Output Interpretation

### Success

```
PASS
ok  	github.com/kooshapari/tracertm-backend/internal/models	4.873s
```

### Partial Failure

```
--- FAIL: TestNotNullConstraints (0.24s)
    --- FAIL: TestNotNullConstraints/items.project_id (0.02s)
        schema_validation_test.go:546: Column should NOT be nullable
FAIL
FAIL	github.com/kooshapari/tracertm-backend/internal/models	6.403s
```

### Expected Skip

```
--- SKIP: TestCodeEntityTableExists (0.06s)
    schema_validation_test.go:284: code_entities table not created yet - this is expected if not migrated
```

## Troubleshooting

### Database Connection Issues

**Error**: `FATAL: role "postgres" does not exist`

**Solution**: Ensure `TEST_DATABASE_URL` is set correctly:
```bash
export TEST_DATABASE_URL="postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable"
```

### Schema Not Found

**Error**: Table columns query returns empty

**Solution**: Check database schema:
```bash
psql -U tracertm -d tracertm -c "\dt"
```

### Multiple Schema Conflicts

**Error**: Getting duplicate columns from different schemas

**Solution**: The test now filters by `table_schema = 'tracertm'` to avoid `public` schema conflicts.

## Adding New Schema Tests

### Test Template

```go
func TestNewTableExists(t *testing.T) {
    db := setupTestDB(t)
    defer cleanupTestDB(t, db)

    columns := getTableColumns(t, db, "new_table")
    require.NotEmpty(t, columns, "new_table should exist")

    assertColumnExists(t, columns, "id", "uuid")
    assertColumnExists(t, columns, "name", "character varying")
    // Add more column checks...
}
```

### Model Matching Template

```go
func TestNewModelMatchesSchema(t *testing.T) {
    db := setupTestDB(t)
    defer cleanupTestDB(t, db)

    columns := getTableColumns(t, db, "new_table")
    model := NewModel{}
    modelFields := getModelFields(model)

    for fieldName, fieldType := range modelFields {
        dbColumn := toSnakeCase(fieldName)
        column, exists := columns[dbColumn]
        assert.True(t, exists, "Field %s should have column %s", fieldName, dbColumn)
        if exists {
            assertTypeMatch(t, fieldName, fieldType, column)
        }
    }
}
```

## Current Test Coverage

| Category | Tests | Status |
|----------|-------|--------|
| Database Connection | 1 | ✅ PASS |
| Table Existence | 7 | ✅ 6 PASS, 1 SKIP |
| Model Matching | 5 | ✅ PASS |
| Primary Keys | 5 | ✅ PASS |
| Foreign Keys | 4 | ✅ PASS |
| Indexes | 8 | ✅ PASS |
| Orphaned Columns | 5 | ✅ PASS |
| UUID Consistency | 5 | ✅ PASS |
| JSONB Consistency | 6 | ✅ PASS |
| Timestamp Consistency | 14 | ✅ PASS |
| NOT NULL Constraints | 14 | ✅ PASS |
| Unique Constraints | 2 | ✅ PASS |
| **TOTAL** | **21** | **100% (20 pass, 1 skip)** |

## Best Practices

1. **Always Run Tests After Schema Changes**: Any migration or direct SQL changes should be followed by schema validation tests

2. **Use TEST_DATABASE_URL**: Never run tests against production database

3. **Check for Schema Drift**: Regularly compare GORM models with actual database schema

4. **Document Expected Skips**: If a test is expected to skip (like `TestCodeEntityTableExists`), document why

5. **Add Tests for New Tables**: When adding new tables, add corresponding validation tests

6. **Verify Constraints**: Don't just check columns exist - verify constraints, indexes, and foreign keys

## Related Documentation

- [Schema Validation Fix Report](../reports/SCHEMA_VALIDATION_FIX_REPORT.md)
- [Database Migration Guide](../guides/DEPLOYMENT_GUIDE.md)
- [Alembic Migration Files](../../alembic/versions/)

## Support

For issues with schema validation tests:

1. Check this guide for troubleshooting steps
2. Review the test output carefully
3. Verify database connection and schema
4. Check migration files for any pending changes
5. Consult the schema validation fix report for historical context
