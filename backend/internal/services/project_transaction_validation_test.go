package services

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

// TestTransactionContextIntegration validates that transaction context helpers work correctly
func TestTransactionContextIntegration(t *testing.T) {
	db := setupProjectTestDB(t)
	for _, tc := range transactionContextCases() {
		t.Run(tc.name, func(t *testing.T) {
			tc.fn(t, db)
		})
	}
}

// TestProjectServiceTransactionHelpers validates the transaction helper methods
func TestProjectServiceTransactionHelpers(t *testing.T) {
	db := setupProjectTestDB(t)
	service := &ProjectServiceImpl{db: db}
	for _, tc := range projectTransactionHelperCases() {
		t.Run(tc.name, func(t *testing.T) {
			tc.fn(t, db, service)
		})
	}
}

type transactionContextCase struct {
	name string
	fn   func(t *testing.T, db *gorm.DB)
}

type projectTransactionHelperCase struct {
	name string
	fn   func(t *testing.T, db *gorm.DB, service *ProjectServiceImpl)
}

func setupProjectTestDB(t *testing.T) *gorm.DB {
	t.Helper()
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	if err != nil {
		t.Fatalf("Failed to open database: %v", err)
	}
	return db
}

func transactionContextCases() []transactionContextCase {
	return []transactionContextCase{
		{name: "GetDB returns fallback when no transaction", fn: runGetDBFallback},
		{name: "GetDB returns transaction when present", fn: runGetDBWithTransaction},
		{name: "IsInTransaction returns false when no transaction", fn: runIsInTransactionFalse},
		{name: "IsInTransaction returns true when transaction present", fn: runIsInTransactionTrue},
		{name: "GetTransaction returns transaction when present", fn: runGetTransactionPresent},
		{name: "GetTransaction returns false when no transaction", fn: runGetTransactionAbsent},
		{name: "WithTransaction adds transaction to context", fn: runWithTransactionAdds},
	}
}

func projectTransactionHelperCases() []projectTransactionHelperCase {
	return []projectTransactionHelperCase{
		{name: "getDB returns fallback when no transaction", fn: runProjectGetDBFallback},
		{name: "getDB returns transaction when present", fn: runProjectGetDBWithTransaction},
		{name: "isInTransaction returns correct value", fn: runProjectIsInTransaction},
		{name: "WithTransaction creates transaction when none exists", fn: runProjectWithTransactionCreates},
		{name: "WithTransaction reuses existing transaction", fn: runProjectWithTransactionReuses},
		{name: "WithTransaction rolls back on error", fn: runProjectWithTransactionRollback},
		{name: "WithTransaction commits on success", fn: runProjectWithTransactionCommit},
	}
}

func runGetDBFallback(t *testing.T, db *gorm.DB) {
	ctx := context.Background()
	result := GetDB(ctx, db)
	assert.Equal(t, db, result, "Should return fallback DB when no transaction")
}

func runGetDBWithTransaction(t *testing.T, db *gorm.DB) {
	ctx := context.Background()
	tx := db.Begin()
	defer tx.Rollback()

	txCtx := WithTransaction(ctx, tx)
	result := GetDB(txCtx, db)
	assert.Equal(t, tx, result, "Should return transaction DB when transaction is in context")
}

func runIsInTransactionFalse(t *testing.T, _ *gorm.DB) {
	ctx := context.Background()
	assert.False(t, IsInTransaction(ctx), "Should return false when no transaction")
}

func runIsInTransactionTrue(t *testing.T, db *gorm.DB) {
	ctx := context.Background()
	tx := db.Begin()
	defer tx.Rollback()

	txCtx := WithTransaction(ctx, tx)
	assert.True(t, IsInTransaction(txCtx), "Should return true when transaction is in context")
}

func runGetTransactionPresent(t *testing.T, db *gorm.DB) {
	ctx := context.Background()
	tx := db.Begin()
	defer tx.Rollback()

	txCtx := WithTransaction(ctx, tx)
	result, ok := GetTransaction(txCtx)
	assert.True(t, ok, "Should find transaction")
	assert.Equal(t, tx, result, "Should return correct transaction")
}

func runGetTransactionAbsent(t *testing.T, _ *gorm.DB) {
	ctx := context.Background()
	_, ok := GetTransaction(ctx)
	assert.False(t, ok, "Should not find transaction")
}

func runWithTransactionAdds(t *testing.T, db *gorm.DB) {
	ctx := context.Background()
	tx := db.Begin()
	defer tx.Rollback()

	assert.False(t, IsInTransaction(ctx))

	txCtx := WithTransaction(ctx, tx)

	assert.True(t, IsInTransaction(txCtx))
	result, ok := GetTransaction(txCtx)
	assert.True(t, ok)
	assert.Equal(t, tx, result)
}

func runProjectGetDBFallback(t *testing.T, db *gorm.DB, _ *ProjectServiceImpl) {
	ctx := context.Background()
	result := GetDB(ctx, db)
	assert.Equal(t, db, result)
}

func runProjectGetDBWithTransaction(t *testing.T, db *gorm.DB, _ *ProjectServiceImpl) {
	ctx := context.Background()
	tx := db.Begin()
	defer tx.Rollback()

	txCtx := WithTransaction(ctx, tx)
	result := GetDB(txCtx, db)
	assert.Equal(t, tx, result)
}

func runProjectIsInTransaction(t *testing.T, db *gorm.DB, service *ProjectServiceImpl) {
	ctx := context.Background()
	assert.False(t, service.isInTransaction(ctx))

	tx := db.Begin()
	defer tx.Rollback()

	txCtx := WithTransaction(ctx, tx)
	assert.True(t, service.isInTransaction(txCtx))
}

func runProjectWithTransactionCreates(t *testing.T, _ *gorm.DB, service *ProjectServiceImpl) {
	ctx := context.Background()
	executed := false

	err := service.WithTransaction(ctx, func(txCtx context.Context) error {
		executed = true
		assert.True(t, IsInTransaction(txCtx), "Should have transaction in context")
		return nil
	})

	assert.NoError(t, err)
	assert.True(t, executed)
}

func runProjectWithTransactionReuses(t *testing.T, db *gorm.DB, service *ProjectServiceImpl) {
	ctx := context.Background()
	tx := db.Begin()
	defer tx.Rollback()

	txCtx := WithTransaction(ctx, tx)
	executed := false

	err := service.WithTransaction(txCtx, func(innerCtx context.Context) error {
		executed = true
		assert.True(t, IsInTransaction(innerCtx))

		innerTx, ok := GetTransaction(innerCtx)
		assert.True(t, ok)
		assert.Equal(t, tx, innerTx, "Should reuse existing transaction")

		return nil
	})

	assert.NoError(t, err)
	assert.True(t, executed)
}

func runProjectWithTransactionRollback(t *testing.T, db *gorm.DB, service *ProjectServiceImpl) {
	ctx := context.Background()

	type TestTable struct {
		ID   uint
		Name string
	}
	require.NoError(t, db.AutoMigrate(&TestTable{}))

	err := service.WithTransaction(ctx, func(txCtx context.Context) error {
		txDB := GetDB(txCtx, db)
		if err := txDB.Create(&TestTable{Name: "test"}).Error; err != nil {
			return err
		}
		return assert.AnError
	})

	assert.Error(t, err)

	var count int64
	db.Model(&TestTable{}).Count(&count)
	assert.Equal(t, int64(0), count, "Record should not exist after rollback")
}

func runProjectWithTransactionCommit(t *testing.T, db *gorm.DB, service *ProjectServiceImpl) {
	ctx := context.Background()

	type TestTable2 struct {
		ID   uint
		Name string
	}
	require.NoError(t, db.AutoMigrate(&TestTable2{}))

	err := service.WithTransaction(ctx, func(txCtx context.Context) error {
		txDB := GetDB(txCtx, db)
		return txDB.Create(&TestTable2{Name: "committed"}).Error
	})

	assert.NoError(t, err)

	var count int64
	db.Model(&TestTable2{}).Count(&count)
	assert.Equal(t, int64(1), count, "Record should exist after commit")

	var record TestTable2
	err = db.First(&record).Error
	assert.NoError(t, err)
	assert.Equal(t, "committed", record.Name)
}
