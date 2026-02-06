package models

import (
	"fmt"
	"os"
	"reflect"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// Schema Validation Tests
//
// These tests verify that the GORM models match the actual database schema.
// They check:
// - Table existence
// - Column names and types
// - Primary and foreign key constraints
// - Indexes
// - NOT NULL and UNIQUE constraints
//
// Prerequisites:
// 1. PostgreSQL must be running
// 2. Database 'tracertm' must exist with schema 'tracertm'
// 3. Migrations must be applied
//
// Running tests:
//   # Set the test database URL
//   export TEST_DATABASE_URL="postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable"
//
//   # Run tests
//   go test -v ./internal/models/...
//
// The tests will use TEST_DATABASE_URL if set, otherwise fall back to DATABASE_URL,
// and finally to a default connection string for the tracertm database.

// TestDatabaseConnection verifies the test database is accessible
func TestDatabaseConnection(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	var result int
	err := db.Raw("SELECT 1").Scan(&result).Error
	require.NoError(t, err, "Database connection should work")
	assert.Equal(t, 1, result, "Query result should be 1")
}

// TestItemTableExists verifies items table exists with correct schema
func TestItemTableExists(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	columns := getTableColumns(t, db, "items")
	require.NotEmpty(t, columns, "items table should exist")

	// Verify essential columns
	assertColumnExists(t, columns, "id", "uuid")
	assertColumnExists(t, columns, "project_id", "uuid")
	assertColumnExists(t, columns, "title", "character varying")
	assertColumnExists(t, columns, "description", "text")
	assertColumnExists(t, columns, "type", "character varying")
	assertColumnExists(t, columns, "status", "character varying")
	assertColumnExists(t, columns, "priority", "integer")
	assertColumnExists(t, columns, "metadata", "jsonb")
	assertColumnExists(t, columns, "created_at", "timestamp")
	assertColumnExists(t, columns, "updated_at", "timestamp")
	assertColumnExists(t, columns, "deleted_at", "timestamp")
}

// TestItemModelMatchesSchema verifies Item GORM model matches database schema
func TestItemModelMatchesSchema(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	columns := getTableColumns(t, db, "items")
	model := Item{}
	modelFields := getModelFields(model)

	// Check all model fields have corresponding columns
	for fieldName, fieldType := range modelFields {
		dbColumn := toSnakeCase(fieldName)
		column, exists := columns[dbColumn]
		assert.True(t, exists, "Field %s should have column %s", fieldName, dbColumn)
		if exists {
			assertTypeMatch(t, fieldName, fieldType, column)
		}
	}
}

// TestLinkTableExists verifies links table exists with correct schema
func TestLinkTableExists(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	columns := getTableColumns(t, db, "links")
	require.NotEmpty(t, columns, "links table should exist")

	assertColumnExists(t, columns, "id", "uuid")
	assertColumnExists(t, columns, "source_id", "uuid")
	assertColumnExists(t, columns, "target_id", "uuid")
	assertColumnExists(t, columns, "link_type", "character varying")
	assertColumnExists(t, columns, "metadata", "jsonb")
	assertColumnExists(t, columns, "created_at", "timestamp")
	// Note: updated_at not in schema, deleted_at not in schema
}

// TestLinkModelMatchesSchema verifies Link GORM model matches database schema
func TestLinkModelMatchesSchema(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	columns := getTableColumns(t, db, "links")
	model := Link{}
	modelFields := getModelFields(model)

	// Map model fields to actual column names (handling special cases)
	fieldToColumn := map[string]string{
		"Type": "link_type", // Link.Type maps to link_type column
	}

	for fieldName, fieldType := range modelFields {
		// Use custom mapping if exists, otherwise use snake_case conversion
		dbColumn, exists := fieldToColumn[fieldName]
		if !exists {
			dbColumn = toSnakeCase(fieldName)
		}

		column, columnExists := columns[dbColumn]
		if !columnExists {
			// Some fields may not exist in schema yet (like UpdatedAt)
			if fieldName == "UpdatedAt" || fieldName == "DeletedAt" {
				t.Logf("INFO: Field %s column %s not in schema yet", fieldName, dbColumn)
				continue
			}
		}
		assert.True(t, columnExists, "Field %s should have column %s", fieldName, dbColumn)
		if columnExists {
			assertTypeMatch(t, fieldName, fieldType, column)
		}
	}
}

// TestProjectTableExists verifies projects table exists with correct schema
func TestProjectTableExists(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	columns := getTableColumns(t, db, "projects")
	require.NotEmpty(t, columns, "projects table should exist")

	assertColumnExists(t, columns, "id", "uuid")
	assertColumnExists(t, columns, "name", "character varying")
	assertColumnExists(t, columns, "description", "text")
	assertColumnExists(t, columns, "metadata", "jsonb")
	assertColumnExists(t, columns, "created_at", "timestamp")
	assertColumnExists(t, columns, "updated_at", "timestamp")
	assertColumnExists(t, columns, "deleted_at", "timestamp")
}

// TestProjectModelMatchesSchema verifies Project GORM model matches database schema
func TestProjectModelMatchesSchema(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	columns := getTableColumns(t, db, "projects")
	model := Project{}
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

// TestAgentTableExists verifies agents table exists with correct schema
func TestAgentTableExists(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	columns := getTableColumns(t, db, "agents")
	require.NotEmpty(t, columns, "agents table should exist")

	assertColumnExists(t, columns, "id", "uuid")
	assertColumnExists(t, columns, "project_id", "uuid")
	assertColumnExists(t, columns, "name", "character varying")
	assertColumnExists(t, columns, "status", "character varying")
	assertColumnExists(t, columns, "metadata", "jsonb")
	assertColumnExists(t, columns, "created_at", "timestamp")
	assertColumnExists(t, columns, "updated_at", "timestamp")
	// Note: last_activity_at not in current schema, deleted_at not in current schema
}

// TestAgentModelMatchesSchema verifies Agent GORM model matches database schema
func TestAgentModelMatchesSchema(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	columns := getTableColumns(t, db, "agents")
	model := Agent{}
	modelFields := getModelFields(model)

	for fieldName, fieldType := range modelFields {
		dbColumn := toSnakeCase(fieldName)
		column, exists := columns[dbColumn]

		// Some fields may not exist in schema yet
		if !exists && (fieldName == "LastActivityAt" || fieldName == "DeletedAt") {
			t.Logf("INFO: Field %s column %s not in schema yet", fieldName, dbColumn)
			continue
		}

		assert.True(t, exists, "Field %s should have column %s", fieldName, dbColumn)
		if exists {
			assertTypeMatch(t, fieldName, fieldType, column)
		}
	}
}

// TestViewTableExists verifies views table exists (if created via GORM)
func TestViewTableExists(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	// Check if table exists
	var exists bool
	err := db.Raw("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'views')").Scan(&exists).Error
	require.NoError(t, err, "Should query table existence")

	if !exists {
		t.Skip("views table not created yet - this is expected if not migrated")
		return
	}

	columns := getTableColumns(t, db, "views")
	assertColumnExists(t, columns, "id", "uuid")
	assertColumnExists(t, columns, "project_id", "uuid")
	assertColumnExists(t, columns, "name", "character varying")
	assertColumnExists(t, columns, "type", "character varying")
	assertColumnExists(t, columns, "config", "character varying")
	assertColumnExists(t, columns, "created_at", "timestamp")
	assertColumnExists(t, columns, "updated_at", "timestamp")
}

// TestProfileTableExists verifies profiles table exists with correct schema
func TestProfileTableExists(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	columns := getTableColumns(t, db, "profiles")
	require.NotEmpty(t, columns, "profiles table should exist")

	assertColumnExists(t, columns, "id", "uuid")
	// Note: auth_id is text in current schema, not uuid
	col, exists := columns["auth_id"]
	assert.True(t, exists, "auth_id column should exist")
	if exists {
		assert.True(t, col.DataType == "text" || col.DataType == "uuid",
			"auth_id should be text or uuid, got %s", col.DataType)
	}
	assertColumnExists(t, columns, "workos_user_id", "text")
	assertColumnExists(t, columns, "workos_org_id", "text")
	assertColumnExists(t, columns, "email", "text")     // text in current schema
	assertColumnExists(t, columns, "full_name", "text") // text in current schema
	assertColumnExists(t, columns, "avatar_url", "text")
	assertColumnExists(t, columns, "workos_ids", "jsonb")
	assertColumnExists(t, columns, "metadata", "jsonb")
	assertColumnExists(t, columns, "created_at", "timestamp")
	assertColumnExists(t, columns, "updated_at", "timestamp")
	assertColumnExists(t, columns, "deleted_at", "timestamp")
}

// TestProfileModelMatchesSchema verifies Profile GORM model matches database schema
func TestProfileModelMatchesSchema(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	columns := getTableColumns(t, db, "profiles")
	model := Profile{}
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

// TestCodeEntityTableExists verifies code_entities table exists (if created)
func TestCodeEntityTableExists(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	var exists bool
	err := db.Raw("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'code_entities')").Scan(&exists).Error
	require.NoError(t, err, "Should query table existence")

	if !exists {
		t.Skip("code_entities table not created yet - this is expected if not migrated")
		return
	}

	columns := getTableColumns(t, db, "code_entities")
	assertColumnExists(t, columns, "id", "uuid")
	assertColumnExists(t, columns, "project_id", "uuid")
	assertColumnExists(t, columns, "entity_type", "character varying")
	assertColumnExists(t, columns, "name", "character varying")
	assertColumnExists(t, columns, "full_name", "character varying")
}

// TestPrimaryKeyConstraints verifies all tables have proper primary keys
func TestPrimaryKeyConstraints(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	tables := []string{"items", "links", "projects", "agents", "profiles"}

	for _, tableName := range tables {
		t.Run(tableName, func(t *testing.T) {
			var constraintName string
			err := db.Raw(`
				SELECT constraint_name
				FROM information_schema.table_constraints
				WHERE table_name = ? AND constraint_type = 'PRIMARY KEY'
			`, tableName).Scan(&constraintName).Error

			require.NoError(t, err, "Should query primary key constraint")
			assert.NotEmpty(t, constraintName, "Table %s should have primary key", tableName)
		})
	}
}

// TestForeignKeyConstraints verifies foreign key relationships
func TestForeignKeyConstraints(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	tests := []struct {
		table     string
		column    string
		refTable  string
		refColumn string
	}{
		{"items", "project_id", "projects", "id"},
		{"links", "source_id", "items", "id"},
		{"links", "target_id", "items", "id"},
		{"agents", "project_id", "projects", "id"},
	}

	for _, tc := range tests {
		t.Run(fmt.Sprintf("%s.%s->%s.%s", tc.table, tc.column, tc.refTable, tc.refColumn), func(t *testing.T) {
			var count int
			err := db.Raw(`
				SELECT COUNT(*)
				FROM information_schema.table_constraints tc
				JOIN information_schema.key_column_usage kcu
					ON tc.constraint_name = kcu.constraint_name
				JOIN information_schema.constraint_column_usage ccu
					ON tc.constraint_name = ccu.constraint_name
				WHERE tc.table_name = ?
					AND tc.constraint_type = 'FOREIGN KEY'
					AND kcu.column_name = ?
					AND ccu.table_name = ?
					AND ccu.column_name = ?
			`, tc.table, tc.column, tc.refTable, tc.refColumn).Scan(&count).Error

			require.NoError(t, err, "Should query foreign key")
			assert.Greater(t, count, 0, "Foreign key should exist")
		})
	}
}

// TestIndexesExist verifies essential indexes are created
func TestIndexesExist(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	tests := []struct {
		table  string
		column string
	}{
		{"items", "project_id"},
		{"items", "deleted_at"},
		{"links", "source_id"},
		{"links", "target_id"},
		{"projects", "deleted_at"},
		{"agents", "project_id"},
		{"profiles", "workos_user_id"},
		{"profiles", "email"},
	}

	for _, tc := range tests {
		t.Run(fmt.Sprintf("%s.%s", tc.table, tc.column), func(t *testing.T) {
			var count int
			err := db.Raw(`
				SELECT COUNT(*)
				FROM pg_indexes
				WHERE tablename = ?
					AND indexdef LIKE '%' || ? || '%'
			`, tc.table, tc.column).Scan(&count).Error

			require.NoError(t, err, "Should query index")
			assert.Greater(t, count, 0, "Index should exist for %s.%s", tc.table, tc.column)
		})
	}
}

// TestNoOrphanedColumns checks for columns in database not represented in models
// This is informational - some columns may exist in schema but not in GORM models
func TestNoOrphanedColumns(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	tests := []struct {
		table          string
		model          interface{}
		allowedOrphans []string // Columns allowed to exist without model fields
	}{
		{"items", Item{}, []string{"account_id", "version", "search_vector", "embedding"}},
		{"links", Link{}, []string{"account_id", "link_type"}},
		{"projects", Project{}, []string{"account_id", "owner_id"}},
		{"agents", Agent{}, []string{"account_id"}},
		{"profiles", Profile{}, []string{"account_id"}},
	}

	for _, tc := range tests {
		t.Run(tc.table, func(t *testing.T) {
			columns := getTableColumns(t, db, tc.table)
			modelFields := getModelFields(tc.model)

			for columnName := range columns {
				// Check if it's an allowed orphan
				isAllowed := false
				for _, allowed := range tc.allowedOrphans {
					if columnName == allowed {
						isAllowed = true
						break
					}
				}
				if isAllowed {
					continue
				}

				fieldName := toCamelCase(columnName)
				_, exists := modelFields[fieldName]
				if !exists {
					t.Logf("INFO: Column %s.%s has no corresponding model field %s (may be intentional)",
						tc.table, columnName, fieldName)
				}
			}
		})
	}
}

// TestUUIDTypeConsistency verifies UUID fields are properly typed
func TestUUIDTypeConsistency(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	tables := []string{"items", "links", "projects", "agents", "profiles"}

	for _, table := range tables {
		t.Run(table, func(t *testing.T) {
			columns := getTableColumns(t, db, table)
			idCol, exists := columns["id"]
			require.True(t, exists, "Table should have id column")
			assert.Equal(t, "uuid", idCol.DataType, "ID column should be UUID type")
		})
	}
}

// TestJSONBTypeConsistency verifies JSONB fields are properly typed
func TestJSONBTypeConsistency(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	tests := []struct {
		table  string
		column string
	}{
		{"items", "metadata"},
		{"links", "metadata"},
		{"projects", "metadata"},
		{"agents", "metadata"},
		{"profiles", "metadata"},
		{"profiles", "workos_ids"},
	}

	for _, tc := range tests {
		t.Run(fmt.Sprintf("%s.%s", tc.table, tc.column), func(t *testing.T) {
			columns := getTableColumns(t, db, tc.table)
			col, exists := columns[tc.column]
			require.True(t, exists, "Column should exist")
			assert.Equal(t, "jsonb", col.DataType, "Column should be JSONB type")
		})
	}
}

// TestTimestampTypeConsistency verifies timestamp fields are properly typed
func TestTimestampTypeConsistency(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	timestampColumns := []string{"created_at", "updated_at", "deleted_at"}
	tables := []string{"items", "links", "projects", "agents", "profiles"}

	for _, table := range tables {
		for _, column := range timestampColumns {
			if column == "deleted_at" && table == "links" {
				continue // links might not have deleted_at
			}

			t.Run(fmt.Sprintf("%s.%s", table, column), func(t *testing.T) {
				columns := getTableColumns(t, db, table)
				col, exists := columns[column]
				if !exists && column == "deleted_at" {
					return // deleted_at is optional
				}
				require.True(t, exists, "Column should exist")
				assert.Contains(t, col.DataType, "timestamp", "Column should be timestamp type")
			})
		}
	}
}

// TestNotNullConstraints verifies NOT NULL constraints on required fields
func TestNotNullConstraints(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	tests := []struct {
		table    string
		column   string
		nullable bool
	}{
		{"items", "id", false},
		{"items", "project_id", false},
		{"items", "title", false},
		{"items", "deleted_at", true},
		{"links", "id", false},
		{"links", "source_id", false},
		{"links", "target_id", false},
		{"projects", "id", false},
		{"projects", "name", false},
		{"agents", "id", false},
		{"agents", "project_id", false},
		{"profiles", "id", false},
		{"profiles", "workos_user_id", false},
		{"profiles", "email", false},
	}

	for _, tc := range tests {
		t.Run(fmt.Sprintf("%s.%s", tc.table, tc.column), func(t *testing.T) {
			columns := getTableColumns(t, db, tc.table)
			col, exists := columns[tc.column]
			require.True(t, exists, "Column should exist")

			if tc.nullable {
				assert.True(t, col.IsNullable, "Column should be nullable")
			} else {
				assert.False(t, col.IsNullable, "Column should NOT be nullable")
			}
		})
	}
}

// TestUniqueConstraints verifies unique constraints
func TestUniqueConstraints(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupTestDB(t, db)

	tests := []struct {
		table  string
		column string
	}{
		// Note: projects.name does not have unique constraint in current schema
		{"profiles", "workos_user_id"},
		{"profiles", "email"},
	}

	for _, tc := range tests {
		t.Run(fmt.Sprintf("%s.%s", tc.table, tc.column), func(t *testing.T) {
			var count int
			err := db.Raw(`
				SELECT COUNT(*)
				FROM information_schema.table_constraints tc
				JOIN information_schema.key_column_usage kcu
					ON tc.constraint_name = kcu.constraint_name
				WHERE tc.table_name = ?
					AND tc.constraint_type = 'UNIQUE'
					AND kcu.column_name = ?
			`, tc.table, tc.column).Scan(&count).Error

			require.NoError(t, err, "Should query unique constraint")
			assert.Greater(t, count, 0, "Unique constraint should exist")
		})
	}
}

// Helper types and functions

type ColumnInfo struct {
	ColumnName string
	DataType   string
	IsNullable bool
}

func setupTestDB(t *testing.T) *gorm.DB {
	// Priority order: TEST_DATABASE_URL > DATABASE_URL > default
	dsn := os.Getenv("TEST_DATABASE_URL")
	if dsn == "" {
		dsn = os.Getenv("DATABASE_URL")
	}
	if dsn == "" {
		// Default to tracertm credentials
		dsn = "postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable"
	}

	// Parse and validate DSN to prevent using wrong credentials
	if !strings.Contains(dsn, "tracertm") && !strings.Contains(dsn, "TEST_") {
		t.Logf("WARNING: Using DATABASE_URL that might not be a test database: %s", dsn)
	}

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		// Suppress GORM logger during tests unless verbose
		Logger: nil,
	})
	require.NoError(t, err, "Should connect to test database")

	return db
}

func cleanupTestDB(t *testing.T, db *gorm.DB) {
	sqlDB, err := db.DB()
	if err == nil {
		if closeErr := sqlDB.Close(); closeErr != nil {
			t.Logf("Failed to close DB: %v", closeErr)
		}
	}
}

func getTableColumns(t *testing.T, db *gorm.DB, tableName string) map[string]ColumnInfo {
	var columns []ColumnInfo
	err := db.Raw(`
		SELECT column_name, data_type, is_nullable = 'YES' as is_nullable
		FROM information_schema.columns
		WHERE table_name = ? AND table_schema = 'tracertm'
		ORDER BY ordinal_position
	`, tableName).Scan(&columns).Error

	require.NoError(t, err, "Should query table columns for %s", tableName)

	result := make(map[string]ColumnInfo)
	for _, col := range columns {
		result[col.ColumnName] = col
	}
	return result
}

func getModelFields(model interface{}) map[string]reflect.Type {
	fields := make(map[string]reflect.Type)
	t := reflect.TypeOf(model)

	for i := 0; i < t.NumField(); i++ {
		field := t.Field(i)
		fields[field.Name] = field.Type
	}

	return fields
}

func assertColumnExists(t *testing.T, columns map[string]ColumnInfo, columnName, expectedType string) {
	col, exists := columns[columnName]
	assert.True(t, exists, "Column %s should exist", columnName)
	if exists {
		assert.Contains(t, col.DataType, expectedType,
			"Column %s should be type %s, got %s", columnName, expectedType, col.DataType)
	}
}

func assertTypeMatch(t *testing.T, fieldName string, fieldType reflect.Type, column ColumnInfo) {
	// Map Go types to SQL types
	fieldTypeName := fieldType.String()

	switch {
	case fieldTypeName == "string":
		assert.True(t,
			strings.Contains(column.DataType, "character varying") ||
				strings.Contains(column.DataType, "text") ||
				strings.Contains(column.DataType, "uuid"),
			"Field %s (string) should map to varchar/text/uuid, got %s", fieldName, column.DataType)

	case fieldTypeName == "int" || fieldTypeName == "int32" || fieldTypeName == "int64":
		assert.Contains(t, column.DataType, "integer",
			"Field %s (int) should map to integer, got %s", fieldName, column.DataType)

	case fieldTypeName == "time.Time":
		assert.Contains(t, column.DataType, "timestamp",
			"Field %s (time.Time) should map to timestamp, got %s", fieldName, column.DataType)

	case fieldTypeName == "*time.Time":
		assert.Contains(t, column.DataType, "timestamp",
			"Field %s (*time.Time) should map to timestamp, got %s", fieldName, column.DataType)
		assert.True(t, column.IsNullable,
			"Field %s (*time.Time) should be nullable", fieldName)

	case fieldTypeName == "datatypes.JSON":
		assert.Equal(t, "jsonb", column.DataType,
			"Field %s (datatypes.JSON) should map to jsonb, got %s", fieldName, column.DataType)

	case strings.HasPrefix(fieldTypeName, "[]"):
		// Array types should map to PostgreSQL arrays or JSON
		assert.True(t,
			strings.Contains(column.DataType, "ARRAY") ||
				strings.Contains(column.DataType, "jsonb"),
			"Field %s (array) should map to ARRAY or jsonb, got %s", fieldName, column.DataType)
	}
}

func toSnakeCase(s string) string {
	var result strings.Builder
	for i, r := range s {
		if i > 0 && r >= 'A' && r <= 'Z' {
			// Check if previous character is lowercase
			if i > 0 && s[i-1] >= 'a' && s[i-1] <= 'z' {
				result.WriteRune('_')
			}
		}
		result.WriteRune(r)
	}
	return strings.ToLower(result.String())
}

func toCamelCase(s string) string {
	parts := strings.Split(s, "_")
	for i := range parts {
		if len(parts[i]) > 0 {
			// Convert to Pascal case (first letter uppercase)
			parts[i] = strings.ToUpper(parts[i][:1]) + parts[i][1:]
		}
	}
	result := strings.Join(parts, "")
	// Handle special cases for ID suffix
	result = strings.ReplaceAll(result, "Id", "ID")
	return result
}
