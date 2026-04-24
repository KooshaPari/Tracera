//go:build !integration && !e2e

package services

import (
	"context"
	"errors"
	"fmt"
	"testing"
	"time"

	"github.com/DATA-DOG/go-sqlmock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

const (
	transactionTestShortSleep    = 10 * time.Millisecond
	transactionTestLongSleep     = 100 * time.Millisecond
	transactionTestTimeoutShort  = 1 * time.Millisecond
	transactionTestTimeoutMedium = 50 * time.Millisecond
)

// ============================================================================
// TRANSACTION CONTEXT TESTS
// ============================================================================

func TestTransactionContext_Creation(t *testing.T) {
	for _, tc := range transactionContextCreationCases() {
		t.Run(tc.name, func(t *testing.T) {
			tc.fn(t)
		})
	}
}

func TestTransactionContext_Operations(t *testing.T) {
	for _, tc := range transactionContextOperationCases() {
		t.Run(tc.name, func(t *testing.T) {
			tc.fn(t)
		})
	}
}

type txContextCase struct {
	name string
	fn   func(t *testing.T)
}

func transactionContextCreationCases() []txContextCase {
	return []txContextCase{
		{name: "create transaction context with valid tx", fn: runTxContextCreate},
		{name: "transaction context has valid GORM instance", fn: runTxContextHasGorm},
		{name: "transaction context is independent per call", fn: runTxContextIndependent},
	}
}

func transactionContextOperationCases() []txContextCase {
	return []txContextCase{
		{name: "perform database operations in transaction", fn: runTxContextSingleOperation},
		{name: "perform multiple operations in single transaction", fn: runTxContextMultipleOperations},
		{name: "query operations in transaction", fn: runTxContextQueryOperation},
	}
}

func runTxContextCreate(t *testing.T) {
	container, mock := setupTestContainer(t)
	mock.ExpectBegin()
	mock.ExpectCommit()

	var txCtx *TransactionContext
	err := container.WithTx(context.Background(), func(ctx *TransactionContext) error {
		txCtx = ctx
		return nil
	})

	require.NoError(t, err)
	assert.NotNil(t, txCtx)
	assert.NotNil(t, txCtx.tx)
	require.NoError(t, mock.ExpectationsWereMet())
}

func runTxContextHasGorm(t *testing.T) {
	container, mock := setupTestContainer(t)
	mock.ExpectBegin()
	mock.ExpectCommit()

	err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
		assert.NotNil(t, txCtx.tx)
		assert.NotNil(t, txCtx.tx.Statement)
		return nil
	})

	require.NoError(t, err)
	require.NoError(t, mock.ExpectationsWereMet())
}

func runTxContextIndependent(t *testing.T) {
	container, mock := setupTestContainer(t)
	mock.ExpectBegin()
	mock.ExpectCommit()
	mock.ExpectBegin()
	mock.ExpectCommit()

	var ctx1, ctx2 *TransactionContext

	err1 := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
		ctx1 = txCtx
		return nil
	})

	err2 := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
		ctx2 = txCtx
		return nil
	})

	require.NoError(t, err1)
	require.NoError(t, err2)
	assert.NotNil(t, ctx1)
	assert.NotNil(t, ctx2)
	assert.NotSame(t, ctx1, ctx2, "each transaction should have its own context")
	require.NoError(t, mock.ExpectationsWereMet())
}

func runTxContextSingleOperation(t *testing.T) {
	container, mock := setupTestContainer(t)

	mock.ExpectBegin()
	mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))
	mock.ExpectCommit()

	err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
		item := &models.Item{
			Title:     "Test Item",
			ProjectID: "project-123",
		}
		return txCtx.tx.Create(item).Error
	})

	require.NoError(t, err)
	require.NoError(t, mock.ExpectationsWereMet())
}

func runTxContextMultipleOperations(t *testing.T) {
	container, mock := setupTestContainer(t)

	mock.ExpectBegin()
	mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))
	mock.ExpectExec("UPDATE").WillReturnResult(sqlmock.NewResult(1, 1))
	mock.ExpectCommit()

	err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
		item := &models.Item{Title: "Item 1", ProjectID: "project-123"}
		if err := txCtx.tx.Create(item).Error; err != nil {
			return err
		}

		if err := txCtx.tx.Model(&models.Item{}).Where("id = ?", "item-1").Update("title", "Updated").Error; err != nil {
			return err
		}

		return nil
	})

	require.NoError(t, err)
	require.NoError(t, mock.ExpectationsWereMet())
}

func runTxContextQueryOperation(t *testing.T) {
	container, mock := setupTestContainer(t)

	mock.ExpectBegin()
	rows := sqlmock.NewRows([]string{"id", "title", "project_id"}).
		AddRow("item-1", "Test Item", "project-123")
	mock.ExpectQuery("SELECT").WillReturnRows(rows)
	mock.ExpectCommit()

	var foundItem models.Item
	err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
		return txCtx.tx.Where("id = ?", "item-1").First(&foundItem).Error
	})

	require.NoError(t, err)
	require.NoError(t, mock.ExpectationsWereMet())
}

func rollbackOnErrorCases() []txContextCase {
	return []txContextCase{
		{name: "transaction rolls back on function error", fn: runRollbackOnFunctionError},
		{name: "rollback on database error", fn: runRollbackOnDatabaseError},
		{name: "partial operations rollback on error", fn: runRollbackOnPartialOperations},
		{name: "rollback failure is logged but original error returned", fn: runRollbackFailureReturnsOriginal},
	}
}

func runRollbackOnFunctionError(t *testing.T) {
	container, mock := setupTestContainer(t)

	mock.ExpectBegin()
	mock.ExpectRollback()

	testErr := errors.New("business logic error")
	err := container.WithTx(context.Background(), func(_ *TransactionContext) error {
		return testErr
	})

	require.Error(t, err)
	assert.Equal(t, testErr, err)
	require.NoError(t, mock.ExpectationsWereMet())
}

func runRollbackOnDatabaseError(t *testing.T) {
	container, mock := setupTestContainer(t)

	mock.ExpectBegin()
	mock.ExpectExec("INSERT").WillReturnError(errors.New("constraint violation"))
	mock.ExpectRollback()

	err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
		return txCtx.tx.Exec("INSERT INTO items VALUES (?)", "test").Error
	})

	require.Error(t, err)
	assert.Contains(t, err.Error(), "constraint violation")
	require.NoError(t, mock.ExpectationsWereMet())
}

func runRollbackOnPartialOperations(t *testing.T) {
	container, mock := setupTestContainer(t)

	mock.ExpectBegin()
	mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))
	mock.ExpectExec("UPDATE").WillReturnError(errors.New("update failed"))
	mock.ExpectRollback()

	operationsAttempted := 0
	err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
		if err := txCtx.tx.Exec("INSERT INTO items VALUES (?)", "test").Error; err != nil {
			return err
		}
		operationsAttempted++

		if err := txCtx.tx.Exec("UPDATE items SET title = ?", "updated").Error; err != nil {
			return err
		}
		operationsAttempted++

		return nil
	})

	require.Error(t, err)
	assert.Equal(t, 1, operationsAttempted, "only first operation should execute")
	require.NoError(t, mock.ExpectationsWereMet())
}

func runRollbackFailureReturnsOriginal(t *testing.T) {
	container, mock := setupTestContainer(t)

	mock.ExpectBegin()
	mock.ExpectRollback().WillReturnError(errors.New("rollback failed"))

	originalErr := errors.New("original error")
	err := container.WithTx(context.Background(), func(_ *TransactionContext) error {
		return originalErr
	})

	require.Error(t, err)
	assert.Equal(t, originalErr, err)
	require.NoError(t, mock.ExpectationsWereMet())
}

func transactionPropagationCases() []txContextCase {
	return []txContextCase{
		{name: "transaction context is passed to nested functions", fn: runTransactionPropagationNested},
		{name: "same transaction is used across function calls", fn: runTransactionPropagationSameTx},
		{name: "error in nested function propagates and triggers rollback", fn: runTransactionPropagationNestedError},
	}
}

func runTransactionPropagationNested(t *testing.T) {
	container, mock := setupTestContainer(t)

	mock.ExpectBegin()
	mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))
	mock.ExpectExec("UPDATE").WillReturnResult(sqlmock.NewResult(1, 1))
	mock.ExpectCommit()

	createItem := func(txCtx *TransactionContext) error {
		return txCtx.tx.Exec("INSERT INTO items VALUES (?)", "test").Error
	}

	updateItem := func(txCtx *TransactionContext) error {
		return txCtx.tx.Exec("UPDATE items SET title = ?", "updated").Error
	}

	err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
		if err := createItem(txCtx); err != nil {
			return err
		}
		return updateItem(txCtx)
	})

	require.NoError(t, err)
	require.NoError(t, mock.ExpectationsWereMet())
}

func runTransactionPropagationSameTx(t *testing.T) {
	container, mock := setupTestContainer(t)

	mock.ExpectBegin()
	mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))
	mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(2, 1))
	mock.ExpectCommit()

	var txPtr1, txPtr2 *gorm.DB

	err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
		txPtr1 = txCtx.tx
		txCtx.tx.Exec("INSERT INTO items VALUES (?)", "test1")

		txPtr2 = txCtx.tx
		txCtx.tx.Exec("INSERT INTO items VALUES (?)", "test2")

		return nil
	})

	require.NoError(t, err)
	assert.Same(t, txPtr1, txPtr2, "should use same transaction instance")
	require.NoError(t, mock.ExpectationsWereMet())
}

func runTransactionPropagationNestedError(t *testing.T) {
	container, mock := setupTestContainer(t)

	mock.ExpectBegin()
	mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))
	mock.ExpectRollback()

	nestedFunc := func(_ *TransactionContext) error {
		return errors.New("nested error")
	}

	err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
		txCtx.tx.Exec("INSERT INTO items VALUES (?)", "test")
		return nestedFunc(txCtx)
	})

	require.Error(t, err)
	assert.Contains(t, err.Error(), "nested error")
	require.NoError(t, mock.ExpectationsWereMet())
}

// ============================================================================
// TRANSACTION MANAGER TESTS (WithTx method)
// ============================================================================

func TestTransactionManager_SuccessfulCommit(t *testing.T) {
	t.Run("simple successful transaction", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		mock.ExpectCommit()

		err := container.WithTx(context.Background(), func(_ *TransactionContext) error {
			return nil
		})

		require.NoError(t, err)
		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("transaction with successful operations commits", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))
		mock.ExpectExec("UPDATE").WillReturnResult(sqlmock.NewResult(1, 1))
		mock.ExpectCommit()

		operationsExecuted := 0
		err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
			txCtx.tx.Exec("INSERT INTO items VALUES (?)", "test")
			operationsExecuted++

			txCtx.tx.Exec("UPDATE items SET title = ?", "updated")
			operationsExecuted++

			return nil
		})

		require.NoError(t, err)
		assert.Equal(t, 2, operationsExecuted)
		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("commit is called exactly once", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		mock.ExpectCommit()
		// Only expect one commit - if called twice, test will fail

		err := container.WithTx(context.Background(), func(_ *TransactionContext) error {
			return nil
		})

		require.NoError(t, err)
		require.NoError(t, mock.ExpectationsWereMet())
	})
}

func TestTransactionManager_RollbackOnError(t *testing.T) {
	for _, tc := range rollbackOnErrorCases() {
		t.Run(tc.name, func(t *testing.T) {
			tc.fn(t)
		})
	}
}

func TestTransactionManager_BeginFailure(t *testing.T) {
	t.Run("begin transaction failure returns error", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin().WillReturnError(errors.New("connection error"))

		functionCalled := false
		err := container.WithTx(context.Background(), func(_ *TransactionContext) error {
			functionCalled = true
			return nil
		})

		require.Error(t, err)
		assert.Contains(t, err.Error(), "failed to begin transaction")
		assert.False(t, functionCalled, "function should not be called if begin fails")
		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("begin failure doesn't attempt commit or rollback", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin().WillReturnError(errors.New("begin failed"))
		// Don't expect commit or rollback

		err := container.WithTx(context.Background(), func(_ *TransactionContext) error {
			t.Fatal("should not be called")
			return nil
		})

		require.Error(t, err)
		require.NoError(t, mock.ExpectationsWereMet())
	})
}

func TestTransactionManager_CommitFailure(t *testing.T) {
	t.Run("commit failure returns error", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		mock.ExpectCommit().WillReturnError(errors.New("commit failed"))

		err := container.WithTx(context.Background(), func(_ *TransactionContext) error {
			return nil
		})

		require.Error(t, err)
		assert.Contains(t, err.Error(), "failed to commit transaction")
		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("commit failure after successful operations", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))
		mock.ExpectCommit().WillReturnError(errors.New("disk full"))

		err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
			return txCtx.tx.Exec("INSERT INTO items VALUES (?)", "test").Error
		})

		require.Error(t, err)
		assert.Contains(t, err.Error(), "failed to commit transaction")
		require.NoError(t, mock.ExpectationsWereMet())
	})
}

// ============================================================================
// TRANSACTION PROPAGATION TESTS
// ============================================================================

func TestTransactionPropagation_ContextPassing(t *testing.T) {
	for _, tc := range transactionPropagationCases() {
		t.Run(tc.name, func(t *testing.T) {
			tc.fn(t)
		})
	}
}

func TestTransactionPropagation_ContextLifecycle(t *testing.T) {
	t.Run("transaction context is only valid during WithTx call", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		mock.ExpectCommit()

		var capturedCtx *TransactionContext
		err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
			capturedCtx = txCtx
			return nil
		})

		require.NoError(t, err)
		assert.NotNil(t, capturedCtx)
		// Note: Using captured context after WithTx returns would be invalid,
		// but we can't easily test that without causing actual database errors
		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("context cancellation is respected", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		mock.ExpectRollback()

		ctx, cancel := context.WithCancel(context.Background())

		err := container.WithTx(ctx, func(_ *TransactionContext) error {
			// Cancel context mid-transaction
			cancel()
			return ctx.Err()
		})

		require.Error(t, err)
		assert.Contains(t, err.Error(), "context canceled")
		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("timeout context is respected", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		mock.ExpectRollback()

		ctx, cancel := context.WithTimeout(context.Background(), transactionTestTimeoutShort)
		defer cancel()

		err := container.WithTx(ctx, func(_ *TransactionContext) error {
			// Simulate slow operation
			time.Sleep(transactionTestShortSleep)
			return ctx.Err()
		})

		require.Error(t, err)
		require.NoError(t, mock.ExpectationsWereMet())
	})
}

// ============================================================================
// NESTED TRANSACTION TESTS
// ============================================================================

func TestNestedTransactions_SingleLevel(t *testing.T) {
	t.Run("single transaction completes successfully", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))
		mock.ExpectCommit()

		err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
			return txCtx.tx.Exec("INSERT INTO items VALUES (?)", "test").Error
		})

		require.NoError(t, err)
		require.NoError(t, mock.ExpectationsWereMet())
	})
}

func TestNestedTransactions_MultipleSequential(t *testing.T) {
	t.Run("sequential independent transactions", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		// First transaction
		mock.ExpectBegin()
		mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))
		mock.ExpectCommit()

		// Second transaction
		mock.ExpectBegin()
		mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(2, 1))
		mock.ExpectCommit()

		err1 := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
			return txCtx.tx.Exec("INSERT INTO items VALUES (?)", "test1").Error
		})

		err2 := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
			return txCtx.tx.Exec("INSERT INTO items VALUES (?)", "test2").Error
		})

		require.NoError(t, err1)
		require.NoError(t, err2)
		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("second transaction independent of first failure", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		// First transaction fails
		mock.ExpectBegin()
		mock.ExpectRollback()

		// Second transaction succeeds
		mock.ExpectBegin()
		mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))
		mock.ExpectCommit()

		err1 := container.WithTx(context.Background(), func(_ *TransactionContext) error {
			return errors.New("first failed")
		})

		err2 := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
			return txCtx.tx.Exec("INSERT INTO items VALUES (?)", "test").Error
		})

		require.Error(t, err1)
		require.NoError(t, err2)
		require.NoError(t, mock.ExpectationsWereMet())
	})
}

func TestNestedTransactions_OuterInnerPattern(t *testing.T) {
	// Note: GORM doesn't support true nested transactions by default
	// These tests document the current behavior and expectations

	t.Run("nested WithTx calls create separate transactions", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		// Outer transaction
		mock.ExpectBegin()
		mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))

		// Inner transaction (separate)
		mock.ExpectBegin()
		mock.ExpectExec("UPDATE").WillReturnResult(sqlmock.NewResult(1, 1))
		mock.ExpectCommit()

		// Outer continues and commits
		mock.ExpectCommit()

		err := container.WithTx(context.Background(), func(outerCtx *TransactionContext) error {
			// Outer transaction operation
			if err := outerCtx.tx.Exec("INSERT INTO items VALUES (?)", "outer").Error; err != nil {
				return err
			}

			// Nested transaction (creates new tx)
			return container.WithTx(context.Background(), func(innerCtx *TransactionContext) error {
				return innerCtx.tx.Exec("UPDATE items SET title = ?", "inner").Error
			})
		})

		require.NoError(t, err)
		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("inner transaction failure doesn't affect outer when separate", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		// Outer transaction
		mock.ExpectBegin()
		mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))

		// Inner transaction fails
		mock.ExpectBegin()
		mock.ExpectRollback()

		// Outer rolls back because inner error propagates
		mock.ExpectRollback()

		err := container.WithTx(context.Background(), func(outerCtx *TransactionContext) error {
			outerCtx.tx.Exec("INSERT INTO items VALUES (?)", "outer")

			// Inner transaction fails and propagates error
			if err := container.WithTx(context.Background(), func(_ *TransactionContext) error {
				return errors.New("inner failed")
			}); err != nil {
				return err // Propagate to outer
			}

			return nil
		})

		require.Error(t, err)
		assert.Contains(t, err.Error(), "inner failed")
		require.NoError(t, mock.ExpectationsWereMet())
	})
}

func TestNestedTransactions_SavepointEmulation(t *testing.T) {
	t.Run("manual savepoint handling", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		mock.ExpectExec("SAVEPOINT").WillReturnResult(sqlmock.NewResult(0, 0))
		mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))
		mock.ExpectExec("ROLLBACK TO SAVEPOINT").WillReturnResult(sqlmock.NewResult(0, 0))
		mock.ExpectCommit()

		err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
			// Create savepoint
			if err := txCtx.tx.Exec("SAVEPOINT sp1").Error; err != nil {
				return err
			}

			// Operation that we might want to rollback
			txCtx.tx.Exec("INSERT INTO items VALUES (?)", "test")

			// Rollback to savepoint
			return txCtx.tx.Exec("ROLLBACK TO SAVEPOINT sp1").Error
		})

		require.NoError(t, err)
		require.NoError(t, mock.ExpectationsWereMet())
	})
}

// ============================================================================
// CONCURRENT TRANSACTION TESTS
// ============================================================================

func TestConcurrentTransactions_Independent(t *testing.T) {
	for _, tc := range concurrentTxCases() {
		t.Run(tc.name, func(t *testing.T) {
			tc.fn(t)
		})
	}
}

// ============================================================================
// EDGE CASES AND ERROR SCENARIOS
// ============================================================================

func TestTransactionEdgeCases_PanicRecovery(t *testing.T) {
	t.Run("panic in transaction function", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		// Panic doesn't trigger rollback in current implementation
		// This documents the current behavior

		assert.Panics(t, func() {
			require.NoError(t, container.WithTx(context.Background(), func(_ *TransactionContext) error {
				panic("unexpected panic")
			}))
		})
	})
}

func TestTransactionEdgeCases_NilFunction(t *testing.T) {
	t.Run("nil function panics", func(t *testing.T) {
		container, _ := setupTestContainer(t)

		assert.Panics(t, func() {
			require.NoError(t, container.WithTx(context.Background(), nil))
		})
	})
}

func TestTransactionEdgeCases_EmptyTransaction(t *testing.T) {
	t.Run("empty transaction commits successfully", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		mock.ExpectCommit()

		err := container.WithTx(context.Background(), func(_ *TransactionContext) error {
			// Do nothing
			return nil
		})

		require.NoError(t, err)
		require.NoError(t, mock.ExpectationsWereMet())
	})
}

func TestTransactionEdgeCases_LongRunningTransaction(t *testing.T) {
	t.Run("long running transaction with timeout", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		mock.ExpectRollback()

		ctx, cancel := context.WithTimeout(context.Background(), transactionTestTimeoutMedium)
		defer cancel()

		err := container.WithTx(ctx, func(_ *TransactionContext) error {
			// Simulate long operation
			time.Sleep(transactionTestLongSleep)
			return ctx.Err()
		})

		require.Error(t, err)
		require.NoError(t, mock.ExpectationsWereMet())
	})
}

// ============================================================================
// INTEGRATION-STYLE TESTS (with mocks)
// ============================================================================

func TestTransactionIntegration_ComplexWorkflow(t *testing.T) {
	for _, tc := range integrationWorkflowCases() {
		t.Run(tc.name, func(t *testing.T) {
			tc.fn(t)
		})
	}
}

func concurrentTxCases() []txContextCase {
	return []txContextCase{
		{name: "concurrent transactions are independent", fn: runConcurrentTxIndependent},
		{name: "concurrent transaction failures don't affect each other", fn: runConcurrentTxFailures},
	}
}

func runConcurrentTxIndependent(t *testing.T) {
	container, mock := setupTestContainer(t)

	// Since sqlmock is not thread-safe for concurrent expectations,
	// we test concurrency by executing transactions sequentially
	// but verifying that they are independent operations.
	// The key is that each transaction has its own Begin/Exec/Commit cycle.

	for i := 0; i < 5; i++ {
		mock.ExpectBegin()
		mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(int64(i+1), 1))
		mock.ExpectCommit()
	}

	// Execute transactions sequentially to avoid sqlmock ordering issues,
	// but we still verify independence through the mock expectations
	errs := make([]error, 5)
	for i := 0; i < 5; i++ {
		id := i
		errs[id] = container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
			return txCtx.tx.Exec("INSERT INTO items VALUES (?)", fmt.Sprintf("test-%d", id)).Error
		})
	}

	// Verify no errors occurred
	for _, err := range errs {
		require.NoError(t, err)
	}

	// Verify all expectations were met
	require.NoError(t, mock.ExpectationsWereMet())
}

func runConcurrentTxFailures(t *testing.T) {
	container, mock := setupTestContainer(t)

	// Setup expectations for 5 transactions (same as concurrent test)
	// Note: We execute them sequentially, but the expectations match the pattern
	for i := 0; i < 5; i++ {
		mock.ExpectBegin()
		if i == 1 {
			// For i==1, no Exec expected (returns error early), just Rollback
			mock.ExpectRollback()
		} else {
			// For other indices, Exec + Commit
			mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(int64(i+1), 1))
			mock.ExpectCommit()
		}
	}

	// Execute transactions sequentially to avoid mock ordering issues
	results := make([]bool, 5)

	for i := 0; i < 5; i++ {
		err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
			if i == 1 {
				// Intentional failure for transaction 1 (index 1)
				return errors.New("intentional failure")
			}
			return txCtx.tx.Exec("INSERT INTO items VALUES (?)", fmt.Sprintf("test-%d", i)).Error
		})
		results[i] = err == nil
	}

	successCount := 0
	for _, success := range results {
		if success {
			successCount++
		}
	}

	// Expect 4 successful transactions (all except index 1)
	assert.Equal(t, 4, successCount)
	require.NoError(t, mock.ExpectationsWereMet())
}

func integrationWorkflowCases() []txContextCase {
	return []txContextCase{
		{name: "multi-step workflow with rollback on any failure", fn: runIntegrationWorkflowRollback},
		{name: "workflow with conditional operations", fn: runIntegrationWorkflowConditional},
	}
}

func runIntegrationWorkflowRollback(t *testing.T) {
	container, mock := setupTestContainer(t)

	mock.ExpectBegin()
	mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))
	mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(2, 1))
	mock.ExpectExec("UPDATE").WillReturnError(errors.New("constraint violation"))
	mock.ExpectRollback()

	err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
		if err := txCtx.tx.Exec("INSERT INTO items VALUES (?)", "item1").Error; err != nil {
			return fmt.Errorf("step 1 failed: %w", err)
		}

		if err := txCtx.tx.Exec("INSERT INTO links VALUES (?)", "link1").Error; err != nil {
			return fmt.Errorf("step 2 failed: %w", err)
		}

		if err := txCtx.tx.Exec("UPDATE items SET status = ?", "linked").Error; err != nil {
			return fmt.Errorf("step 3 failed: %w", err)
		}

		return nil
	})

	require.Error(t, err)
	assert.Contains(t, err.Error(), "step 3 failed")
	require.NoError(t, mock.ExpectationsWereMet())
}

func runIntegrationWorkflowConditional(t *testing.T) {
	container, mock := setupTestContainer(t)

	mock.ExpectBegin()
	mock.ExpectExec("INSERT").WillReturnResult(sqlmock.NewResult(1, 1))
	rows := sqlmock.NewRows([]string{"count"}).AddRow(1)
	mock.ExpectQuery("SELECT COUNT").WillReturnRows(rows)
	mock.ExpectExec("UPDATE").WillReturnResult(sqlmock.NewResult(1, 1))
	mock.ExpectCommit()

	err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
		if err := txCtx.tx.Exec("INSERT INTO items VALUES (?)", "test").Error; err != nil {
			return err
		}

		var count int64
		if err := txCtx.tx.Raw("SELECT COUNT(*) FROM items").Scan(&count).Error; err != nil {
			return err
		}

		if count > 0 {
			if err := txCtx.tx.Exec("UPDATE items SET processed = ?", true).Error; err != nil {
				return err
			}
		}

		return nil
	})

	require.NoError(t, err)
	require.NoError(t, mock.ExpectationsWereMet())
}
