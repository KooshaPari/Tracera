package services

import (
	"context"
	"testing"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

// testContextKey is a custom type for context keys in tests (avoids revive context-keys-type).
type testContextKey string

// setupTestDB creates an in-memory SQLite database for testing
func setupTransactionContextTestDB(t *testing.T) *gorm.DB {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open database: %v", err)
	}
	return db
}

func TestWithTransaction(t *testing.T) {
	db := setupTransactionContextTestDB(t)

	tests := []struct {
		name string
		ctx  context.Context
		tx   *gorm.DB
		want bool
	}{
		{
			name: "Add transaction to background context",
			ctx:  context.Background(),
			tx:   db,
			want: true,
		},
		{
			name: "Add transaction to existing context",
			ctx:  context.WithValue(context.Background(), testContextKey("key"), "value"),
			tx:   db,
			want: true,
		},
		{
			name: "Handle nil context",
			ctx:  nil,
			tx:   db,
			want: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctx := WithTransaction(tt.ctx, tt.tx)
			if ctx == nil {
				t.Error("WithTransaction returned nil context")
				return
			}

			tx, ok := GetTransaction(ctx)
			if ok != tt.want {
				t.Errorf("GetTransaction() ok = %v, want %v", ok, tt.want)
			}
			if tt.want && tx != tt.tx {
				t.Error("GetTransaction returned different transaction")
			}
		})
	}
}

func TestGetTransaction(t *testing.T) {
	db := setupTransactionContextTestDB(t)

	tests := []struct {
		name    string
		ctx     context.Context
		wantOk  bool
		wantNil bool
	}{
		{
			name:    "Get transaction from context with transaction",
			ctx:     WithTransaction(context.Background(), db),
			wantOk:  true,
			wantNil: false,
		},
		{
			name:    "Get transaction from context without transaction",
			ctx:     context.Background(),
			wantOk:  false,
			wantNil: true,
		},
		{
			name:    "Get transaction from nil context",
			ctx:     nil,
			wantOk:  false,
			wantNil: true,
		},
		{
			name:    "Get transaction from context with wrong value type",
			ctx:     context.WithValue(context.Background(), TransactionKey, "not a transaction"),
			wantOk:  false,
			wantNil: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tx, ok := GetTransaction(tt.ctx)
			if ok != tt.wantOk {
				t.Errorf("GetTransaction() ok = %v, want %v", ok, tt.wantOk)
			}
			if (tx == nil) != tt.wantNil {
				t.Errorf("GetTransaction() tx nil = %v, want nil = %v", tx == nil, tt.wantNil)
			}
		})
	}
}

func TestIsInTransaction(t *testing.T) {
	db := setupTransactionContextTestDB(t)

	tests := []struct {
		name string
		ctx  context.Context
		want bool
	}{
		{
			name: "Context with transaction",
			ctx:  WithTransaction(context.Background(), db),
			want: true,
		},
		{
			name: "Context without transaction",
			ctx:  context.Background(),
			want: false,
		},
		{
			name: "Nil context",
			ctx:  nil,
			want: false,
		},
		{
			name: "Context with wrong value type",
			ctx:  context.WithValue(context.Background(), TransactionKey, "not a transaction"),
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := IsInTransaction(tt.ctx); got != tt.want {
				t.Errorf("IsInTransaction() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestGetDB(t *testing.T) {
	db := setupTransactionContextTestDB(t)
	txDB := db.Begin()
	defer txDB.Rollback()

	tests := []struct {
		name     string
		ctx      context.Context
		fallback *gorm.DB
		want     *gorm.DB
	}{
		{
			name:     "Return transaction from context",
			ctx:      WithTransaction(context.Background(), txDB),
			fallback: db,
			want:     txDB,
		},
		{
			name:     "Return fallback when no transaction",
			ctx:      context.Background(),
			fallback: db,
			want:     db,
		},
		{
			name:     "Return fallback for nil context",
			ctx:      nil,
			fallback: db,
			want:     db,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := GetDB(tt.ctx, tt.fallback)
			if got != tt.want {
				t.Errorf("GetDB() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestTransactionContextKey(t *testing.T) {
	// Verify that the transaction key has the expected value (key is from tx package)
	if TransactionKey != "gorm:transaction" {
		t.Errorf("TransactionKey = %v, want 'gorm:transaction'", TransactionKey)
	}

	// Verify that the key doesn't collide with other keys (use typed key for test)
	ctx := context.WithValue(context.Background(), testContextKey("gorm:transaction"), "string value")
	ctx = WithTransaction(ctx, setupTransactionContextTestDB(t))

	// The transaction should be retrievable
	if !IsInTransaction(ctx) {
		t.Error("Transaction not found in context, key collision possible")
	}

	// The string value should still be retrievable
	if val := ctx.Value(testContextKey("gorm:transaction")); val == nil {
		t.Error("String value overwritten by transaction")
	}
}

func TestTransactionPropagation(t *testing.T) {
	db := setupTransactionContextTestDB(t)
	if err := db.AutoMigrate(&TestModel{}); err != nil {
		t.Fatalf("failed to migrate: %v", err)
	}

	t.Run("Transaction propagation through context", func(t *testing.T) {
		runTransactionPropagation(t, db)
	})

	t.Run("GetDB fallback to regular DB", func(t *testing.T) {
		runGetDBFallbackPropagation(t, db)
	})
}

type TestModel struct {
	ID   uint
	Name string
}

func runTransactionPropagation(t *testing.T, db *gorm.DB) {
	tx := db.Begin()
	defer tx.Rollback()

	ctx := WithTransaction(context.Background(), tx)

	txFromCtx, ok := GetTransaction(ctx)
	if !ok {
		t.Fatal("Failed to get transaction from context")
	}

	record := TestModel{Name: "test"}
	if err := txFromCtx.Create(&record).Error; err != nil {
		t.Fatalf("failed to create record: %v", err)
	}

	var count int64
	if err := txFromCtx.Model(&TestModel{}).Count(&count).Error; err != nil {
		t.Fatalf("failed to count records: %v", err)
	}
	if count != 1 {
		t.Errorf("Expected 1 record in transaction, got %d", count)
	}

	tx.Rollback()

	if err := db.Model(&TestModel{}).Count(&count).Error; err != nil {
		t.Fatalf("failed to count records in main DB: %v", err)
	}
	if count != 0 {
		t.Errorf("Expected 0 records in main DB after rollback, got %d", count)
	}
}

func runGetDBFallbackPropagation(t *testing.T, db *gorm.DB) {
	ctx := context.Background()

	dbFromCtx := GetDB(ctx, db)
	if dbFromCtx != db {
		t.Error("GetDB should return fallback when no transaction in context")
	}

	record := TestModel{Name: "test2"}
	if err := dbFromCtx.Create(&record).Error; err != nil {
		t.Fatalf("failed to create record: %v", err)
	}

	var count int64
	if err := db.Model(&TestModel{}).Count(&count).Error; err != nil {
		t.Fatalf("failed to count records: %v", err)
	}
	if count != 1 {
		t.Errorf("Expected 1 record in main DB, got %d", count)
	}

	db.Where("1=1").Delete(&TestModel{})
}

func TestNestedTransactionContext(t *testing.T) {
	db := setupTransactionContextTestDB(t)
	tx1 := db.Begin()
	tx2 := db.Begin()
	defer tx1.Rollback()
	defer tx2.Rollback()

	// Create nested transaction contexts
	ctx1 := WithTransaction(context.Background(), tx1)
	ctx2 := WithTransaction(ctx1, tx2)

	// The inner context should have the second transaction
	gotTx, ok := GetTransaction(ctx2)
	if !ok {
		t.Fatal("Failed to get transaction from nested context")
	}
	if gotTx != tx2 {
		t.Error("Nested context should contain the most recent transaction")
	}

	// The outer context should still have the first transaction
	gotTx, ok = GetTransaction(ctx1)
	if !ok {
		t.Fatal("Failed to get transaction from outer context")
	}
	if gotTx != tx1 {
		t.Error("Outer context should still contain the original transaction")
	}
}

func TestContextCancellation(t *testing.T) {
	db := setupTransactionContextTestDB(t)
	tx := db.Begin()
	defer tx.Rollback()

	// Create a cancellable context with transaction
	ctx, cancel := context.WithCancel(context.Background())
	txCtx := WithTransaction(ctx, tx)

	// Verify transaction is accessible
	if !IsInTransaction(txCtx) {
		t.Error("Transaction should be accessible before cancellation")
	}

	// Cancel the context
	cancel()

	// Transaction should still be accessible (cancellation doesn't affect stored values)
	if !IsInTransaction(txCtx) {
		t.Error("Transaction should still be accessible after cancellation")
	}

	// But the context should be cancelled
	if txCtx.Err() == nil {
		t.Error("Context should be cancelled")
	}
}
