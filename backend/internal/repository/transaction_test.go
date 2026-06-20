package repository

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/tx"
)

func setupItemTransactionDB(t *testing.T) *gorm.DB {
	t.Helper()
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	require.NoError(t, err)

	err = db.AutoMigrate(&models.Item{})
	require.NoError(t, err)

	return db
}

func newTestItem(id string, projectID string, title string, status string) *models.Item {
	return &models.Item{
		ID:        id,
		ProjectID: projectID,
		Title:     title,
		Type:      "task",
		Status:    status,
		Priority:  models.PriorityMedium,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
}

func countItem(db *gorm.DB, id string) int64 {
	var count int64
	db.Model(&models.Item{}).Where("id = ?", id).Count(&count)
	return count
}

func countActiveItem(db *gorm.DB, id string) int64 {
	var count int64
	db.Model(&models.Item{}).Where("id = ? AND deleted_at IS NULL", id).Count(&count)
	return count
}

func testItemCreateTransaction(t *testing.T, db *gorm.DB, repo ItemRepository) {
	t.Helper()
	ctx := context.Background()

	txDB := db.Begin()
	defer txDB.Rollback()

	txCtx := tx.WithTransaction(ctx, txDB)

	item := newTestItem("tx-test-1", "project-1", "Transaction Test Item", "todo")

	err := repo.Create(txCtx, item)
	require.NoError(t, err)
	assert.Equal(t, int64(1), countItem(txDB, item.ID), "Item should exist in transaction")

	txDB.Rollback()
	assert.Equal(t, int64(0), countItem(db, item.ID), "Item should not exist after rollback")

	txDB2 := db.Begin()
	txCtx2 := tx.WithTransaction(ctx, txDB2)
	item.ID = "tx-test-1-committed"
	err = repo.Create(txCtx2, item)
	require.NoError(t, err)
	txDB2.Commit()

	assert.Equal(t, int64(1), countItem(db, item.ID), "Item should exist after commit")
}

func testItemUpdateTransaction(t *testing.T, db *gorm.DB, repo ItemRepository) {
	t.Helper()
	ctx := context.Background()

	item := newTestItem("tx-test-2", "project-2", "Initial Title", "todo")
	err := repo.Create(ctx, item)
	require.NoError(t, err)

	txDB := db.Begin()
	txCtx := tx.WithTransaction(ctx, txDB)

	item.Title = "Updated Title"
	item.Status = "in_progress"
	err = repo.Update(txCtx, item)
	require.NoError(t, err)

	txDB.Rollback()

	var mainItem models.Item
	db.Where("id = ?", item.ID).First(&mainItem)
	assert.Equal(t, "Initial Title", mainItem.Title, "Title should not be updated after rollback")
	assert.Equal(t, "todo", mainItem.Status, "Status should not be updated after rollback")

	txDB2 := db.Begin()
	txCtx2 := tx.WithTransaction(ctx, txDB2)
	err = repo.Update(txCtx2, item)
	require.NoError(t, err)
	txDB2.Commit()

	db.Where("id = ?", item.ID).First(&mainItem)
	assert.Equal(t, "Updated Title", mainItem.Title, "Title should be updated after commit")
	assert.Equal(t, "in_progress", mainItem.Status, "Status should be updated after commit")
}

func testItemDeleteTransaction(t *testing.T, db *gorm.DB, repo ItemRepository) {
	t.Helper()
	ctx := context.Background()

	item := newTestItem("tx-test-3", "project-3", "To Be Deleted", "todo")
	err := repo.Create(ctx, item)
	require.NoError(t, err)

	assert.Equal(t, int64(1), countActiveItem(db, item.ID))

	txDB := db.Begin()
	txCtx := tx.WithTransaction(ctx, txDB)
	err = repo.Delete(txCtx, item.ID)
	require.NoError(t, err)
	txDB.Rollback()

	assert.Equal(t, int64(1), countActiveItem(db, item.ID), "Item should still exist after rollback")

	txDB2 := db.Begin()
	txCtx2 := tx.WithTransaction(ctx, txDB2)
	err = repo.Delete(txCtx2, item.ID)
	require.NoError(t, err)
	txDB2.Commit()

	assert.Equal(t, int64(0), countActiveItem(db, item.ID), "Item should be deleted after commit")
}

// TestItemRepositoryTransactionSupport verifies that repository operations use transactions from context
func TestItemRepositoryTransactionSupport(t *testing.T) {
	db := setupItemTransactionDB(t)
	repo := NewItemRepository(db)

	t.Run("Create uses transaction from context", func(t *testing.T) {
		testItemCreateTransaction(t, db, repo)
	})
	t.Run("Update uses transaction from context", func(t *testing.T) {
		testItemUpdateTransaction(t, db, repo)
	})
	t.Run("Delete uses transaction from context", func(t *testing.T) {
		testItemDeleteTransaction(t, db, repo)
	})
}

// TestLinkRepositoryTransactionSupport verifies that link repository operations use transactions
func TestLinkRepositoryTransactionSupport(t *testing.T) {
	// Setup in-memory SQLite database
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	require.NoError(t, err)

	// Auto-migrate models
	err = db.AutoMigrate(&models.Link{})
	require.NoError(t, err)

	repo := NewLinkRepository(db)

	t.Run("DeleteByItemID uses transaction from context", func(t *testing.T) {
		ctx := context.Background()

		// Create links
		link1 := &models.Link{
			ID:       "link-1",
			SourceID: "item-1",
			TargetID: "item-2",
			Type:     "depends_on",
		}
		link2 := &models.Link{
			ID:       "link-2",
			SourceID: "item-2",
			TargetID: "item-3",
			Type:     "blocks",
		}

		err := repo.Create(ctx, link1)
		require.NoError(t, err)
		err = repo.Create(ctx, link2)
		require.NoError(t, err)

		// Start transaction
		txDB := db.Begin()

		txCtx := tx.WithTransaction(ctx, txDB)

		// Delete links for item-2
		err = repo.DeleteByItemID(txCtx, "item-2")
		require.NoError(t, err)

		// Rollback to test transaction isolation
		txDB.Rollback()

		// Verify links still exist after rollback
		var count int64
		db.Model(&models.Link{}).Where("source_id = ? OR target_id = ?", "item-2", "item-2").Count(&count)
		assert.Equal(t, int64(2), count, "Links should still exist after rollback")

		// Now test with commit
		txDB2 := db.Begin()
		txCtx2 := tx.WithTransaction(ctx, txDB2)
		err = repo.DeleteByItemID(txCtx2, "item-2")
		require.NoError(t, err)
		txDB2.Commit()

		// Verify links are deleted after commit
		db.Model(&models.Link{}).Where("source_id = ? OR target_id = ?", "item-2", "item-2").Count(&count)
		assert.Equal(t, int64(0), count, "Links should be deleted after commit")
	})
}
