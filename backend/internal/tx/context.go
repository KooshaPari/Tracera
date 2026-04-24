// Package tx provides transaction context helpers for GORM.
// Package tx provides transaction context helpers.
package tx

import (
	"context"

	"gorm.io/gorm"
)

// transactionKeyType is a custom type for the transaction context key
// to avoid collisions with other context keys
type transactionKeyType string

// TransactionKey is the context key for storing GORM transactions
const TransactionKey transactionKeyType = "gorm:transaction"

// WithTransaction adds a GORM transaction to the context
// This allows the transaction to be propagated through service method calls
//
// Example usage:
//
//	tx := db.Begin()
//	txCtx := tx.WithTransaction(ctx, tx)
//	err := service.CreateItem(txCtx, item)
//	if err != nil {
//	    tx.Rollback()
//	    return err
//	}
//	tx.Commit()
func WithTransaction(ctx context.Context, tx *gorm.DB) context.Context {
	if ctx == nil {
		ctx = context.Background()
	}
	return context.WithValue(ctx, TransactionKey, tx)
}

// GetTransaction retrieves the GORM transaction from the context
// Returns the transaction and true if found, or nil and false if not present
//
// Example usage:
//
//	if tx, ok := tx.GetTransaction(ctx); ok {
//	    // Use the transaction
//	    err := tx.Create(&item).Error
//	} else {
//	    // Use the regular DB connection
//	    err := db.Create(&item).Error
//	}
func GetTransaction(ctx context.Context) (*gorm.DB, bool) {
	if ctx == nil {
		return nil, false
	}

	tx, ok := ctx.Value(TransactionKey).(*gorm.DB)
	return tx, ok
}

// IsInTransaction checks if the context contains a transaction
// Returns true if a transaction is present, false otherwise
func IsInTransaction(ctx context.Context) bool {
	if ctx == nil {
		return false
	}

	_, ok := ctx.Value(TransactionKey).(*gorm.DB)
	return ok
}

// GetDB returns the appropriate database connection from the context
// If a transaction is present, it returns the transaction DB
// Otherwise, it returns the provided fallback DB
//
// This is a convenience method for repository methods that need to
// support both transactional and non-transactional operations
//
// Example usage:
//
//	func (r *itemRepository) Create(ctx context.Context, item *models.Item) error {
//	    db := tx.GetDB(ctx, r.db)
//	    return db.WithContext(ctx).Create(item).Error
//	}
func GetDB(ctx context.Context, fallback *gorm.DB) *gorm.DB {
	if tx, ok := GetTransaction(ctx); ok {
		return tx
	}
	return fallback
}
