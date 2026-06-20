package services

import (
	"context"
	"time"

	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/tx"
)

// Re-export transaction functions for backward compatibility
// These are now implemented in the tx package to avoid import cycles

// WithTransaction adds a GORM transaction to the context
func WithTransaction(ctx context.Context, txn *gorm.DB) context.Context {
	return tx.WithTransaction(ctx, txn)
}

// GetTransaction retrieves the GORM transaction from the context
func GetTransaction(ctx context.Context) (*gorm.DB, bool) {
	return tx.GetTransaction(ctx)
}

// IsInTransaction checks if the context contains a transaction
func IsInTransaction(ctx context.Context) bool {
	return tx.IsInTransaction(ctx)
}

// GetDB returns the appropriate database connection from the context
func GetDB(ctx context.Context, fallback *gorm.DB) *gorm.DB {
	return tx.GetDB(ctx, fallback)
}

// TransactionKey is the context key for storing GORM transactions.
// Re-exported from tx package for backward compatibility.
const TransactionKey = tx.TransactionKey

// TransactionContext wraps a context.Context with transaction support.
// Used by ServiceContainer.WithTx so callbacks can access the raw *gorm.DB.
type TransactionContext struct {
	context.Context
	tx *gorm.DB
}

// NewTransactionContext returns a TransactionContext that embeds a context
// with the transaction and holds the same tx for direct access (e.g. in tests).
func NewTransactionContext(ctx context.Context, txn *gorm.DB) *TransactionContext {
	return &TransactionContext{
		Context: WithTransaction(ctx, txn),
		tx:      txn,
	}
}

// ExecuteInTransaction executes a function within a database transaction
// This is a convenience wrapper around GORM's Transaction method
//
// Example usage:
//
//	err := ExecuteInTransaction(ctx, db, func(txCtx context.Context) error {
//	    if err := service.CreateItem(txCtx, item1); err != nil {
//	        return err
//	    }
//	    return service.CreateItem(txCtx, item2)
//	})
func ExecuteInTransaction(ctx context.Context, db *gorm.DB, fn func(context.Context) error) error {
	return db.Transaction(func(txn *gorm.DB) error {
		txCtx := WithTransaction(ctx, txn)
		return fn(txCtx)
	})
}

// ExecuteInTransactionWithTimeout executes a function within a database transaction with a timeout
func ExecuteInTransactionWithTimeout(ctx context.Context, db *gorm.DB, timeout time.Duration, fn func(context.Context) error) error {
	timeoutCtx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	return db.WithContext(timeoutCtx).Transaction(func(txn *gorm.DB) error {
		txCtx := WithTransaction(timeoutCtx, txn)
		return fn(txCtx)
	})
}

// WithTransactionTimeout creates a transaction context with a timeout.
//
// Deprecated: Use context.WithTimeout combined with WithTransaction instead.
func WithTransactionTimeout(ctx context.Context, txn *gorm.DB, _ ...interface{}) (context.Context, context.CancelFunc) {
	txCtx := WithTransaction(ctx, txn)
	return context.WithCancel(txCtx)
}
