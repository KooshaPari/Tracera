//go:build !integration

package tx

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

func setupTestDB(t *testing.T) *gorm.DB {
	t.Helper()
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	require.NoError(t, err)
	return db
}

func TestWithTransaction(t *testing.T) {
	db := setupTestDB(t)
	tx := db.Begin()
	defer tx.Rollback()

	ctx := WithTransaction(context.Background(), tx)
	require.NotNil(t, ctx)

	// Should be retrievable
	gotTx, ok := GetTransaction(ctx)
	assert.True(t, ok)
	assert.Equal(t, tx, gotTx)
}

func TestWithTransaction_NilContext(t *testing.T) {
	db := setupTestDB(t)
	tx := db.Begin()
	defer tx.Rollback()

	ctx := WithTransaction(nil, tx) //nolint:staticcheck // SA1012: deliberately testing nil-safety
	require.NotNil(t, ctx)

	gotTx, ok := GetTransaction(ctx)
	assert.True(t, ok)
	assert.Equal(t, tx, gotTx)
}

func TestGetTransaction_NoTransaction(t *testing.T) {
	ctx := context.Background()
	gotTx, ok := GetTransaction(ctx)
	assert.False(t, ok)
	assert.Nil(t, gotTx)
}

func TestGetTransaction_NilContext(t *testing.T) {
	gotTx, ok := GetTransaction(nil) //nolint:staticcheck // SA1012: deliberately testing nil-safety
	assert.False(t, ok)
	assert.Nil(t, gotTx)
}

func TestIsInTransaction(t *testing.T) {
	db := setupTestDB(t)

	t.Run("with transaction", func(t *testing.T) {
		tx := db.Begin()
		defer tx.Rollback()

		ctx := WithTransaction(context.Background(), tx)
		assert.True(t, IsInTransaction(ctx))
	})

	t.Run("without transaction", func(t *testing.T) {
		ctx := context.Background()
		assert.False(t, IsInTransaction(ctx))
	})

	t.Run("nil context", func(t *testing.T) {
		assert.False(t, IsInTransaction(nil)) //nolint:staticcheck // SA1012: deliberately testing nil-safety
	})
}

func TestGetDB_WithTransaction(t *testing.T) {
	db := setupTestDB(t)
	fallback := setupTestDB(t)

	tx := db.Begin()
	defer tx.Rollback()

	ctx := WithTransaction(context.Background(), tx)
	result := GetDB(ctx, fallback)
	assert.Equal(t, tx, result)
}

func TestGetDB_WithoutTransaction(t *testing.T) {
	fallback := setupTestDB(t)

	ctx := context.Background()
	result := GetDB(ctx, fallback)
	assert.Equal(t, fallback, result)
}

func TestGetDB_NilContext(t *testing.T) {
	fallback := setupTestDB(t)

	// With nil context, should return fallback
	result := GetDB(nil, fallback) //nolint:staticcheck // SA1012: deliberately testing nil-safety
	assert.Equal(t, fallback, result)
}

func TestTransactionKey(t *testing.T) {
	assert.Equal(t, TransactionKey, transactionKeyType("gorm:transaction"))
}

func TestGetTransaction_WrongType(t *testing.T) {
	// Store a non-*gorm.DB value with the same key
	ctx := context.WithValue(context.Background(), TransactionKey, "not a gorm.DB")
	gotTx, ok := GetTransaction(ctx)
	assert.False(t, ok)
	assert.Nil(t, gotTx)
}
