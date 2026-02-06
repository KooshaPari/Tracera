package services

import (
	"context"
	"testing"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/kooshapari/tracertm-backend/internal/tx"
	"github.com/stretchr/testify/assert"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

type itemServiceTxEnv struct {
	db       *gorm.DB
	itemRepo repository.ItemRepository
	linkRepo repository.LinkRepository
	service  ItemService
}

func setupItemServiceTxEnv(t *testing.T) *itemServiceTxEnv {
	t.Helper()

	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	assert.NoError(t, err)

	err = db.AutoMigrate(&models.Item{}, &models.Link{})
	assert.NoError(t, err)

	itemRepo := repository.NewItemRepository(db)
	linkRepo := repository.NewLinkRepository(db)
	service := NewItemServiceImpl(itemRepo, linkRepo, nil, nil)

	return &itemServiceTxEnv{
		db:       db,
		itemRepo: itemRepo,
		linkRepo: linkRepo,
		service:  service,
	}
}

// TestItemServiceTransactionSupport verifies that ItemService operations are transaction-aware
func TestItemServiceTransactionSupport(t *testing.T) {
	env := setupItemServiceTxEnv(t)

	t.Run("CreateItem uses transaction from context", func(t *testing.T) {
		runCreateItemWithTx(t, env)
	})

	t.Run("CreateBatch uses transaction from context", func(t *testing.T) {
		runCreateBatchWithTx(t, env)
	})

	t.Run("UpdateBatch uses transaction from context", func(t *testing.T) {
		runUpdateBatchWithTx(t, env)
	})

	t.Run("DeleteBatch uses transaction from context", func(t *testing.T) {
		runDeleteBatchWithTx(t, env)
	})
}

func runCreateItemWithTx(t *testing.T, env *itemServiceTxEnv) {
	ctx := context.Background()
	txDB := env.db.Begin()
	defer txDB.Rollback()

	txCtx := tx.WithTransaction(ctx, txDB)
	item := &models.Item{
		ID:        "test-tx-item-1",
		ProjectID: "test-project-1",
		Title:     "Test Transaction Item",
		Type:      "task",
		Status:    "todo",
		Priority:  models.PriorityMedium,
	}

	err := env.service.CreateItem(txCtx, item)
	assert.NoError(t, err)

	var count int64
	txDB.Model(&models.Item{}).Where("id = ?", item.ID).Count(&count)
	assert.Equal(t, int64(1), count, "Item should exist in transaction")

	env.db.Model(&models.Item{}).Where("id = ?", item.ID).Count(&count)
	assert.Equal(t, int64(0), count, "Item should not exist in main DB before commit")

	txDB.Commit()

	env.db.Model(&models.Item{}).Where("id = ?", item.ID).Count(&count)
	assert.Equal(t, int64(1), count, "Item should exist in main DB after commit")
}

func runCreateBatchWithTx(t *testing.T, env *itemServiceTxEnv) {
	ctx := context.Background()
	txDB := env.db.Begin()
	defer txDB.Rollback()

	txCtx := tx.WithTransaction(ctx, txDB)
	items := []*models.Item{
		{
			ID:        "test-tx-batch-1",
			ProjectID: "test-project-2",
			Title:     "Batch Item 1",
			Type:      "task",
			Status:    "todo",
			Priority:  models.PriorityMedium,
		},
		{
			ID:        "test-tx-batch-2",
			ProjectID: "test-project-2",
			Title:     "Batch Item 2",
			Type:      "task",
			Status:    "todo",
			Priority:  models.PriorityHigh,
		},
	}

	err := env.service.CreateBatch(txCtx, items)
	assert.NoError(t, err)

	var count int64
	txDB.Model(&models.Item{}).Where("project_id = ?", "test-project-2").Count(&count)
	assert.Equal(t, int64(2), count, "Items should exist in transaction")

	env.db.Model(&models.Item{}).Where("project_id = ?", "test-project-2").Count(&count)
	assert.Equal(t, int64(0), count, "Items should not exist in main DB before commit")

	txDB.Commit()

	env.db.Model(&models.Item{}).Where("project_id = ?", "test-project-2").Count(&count)
	assert.Equal(t, int64(2), count, "Items should exist in main DB after commit")
}

func runUpdateBatchWithTx(t *testing.T, env *itemServiceTxEnv) {
	ctx := context.Background()

	item1 := &models.Item{
		ID:        "test-update-batch-1",
		ProjectID: "test-project-3",
		Title:     "Update Batch Item 1",
		Type:      "task",
		Status:    "todo",
		Priority:  models.PriorityMedium,
	}
	item2 := &models.Item{
		ID:        "test-update-batch-2",
		ProjectID: "test-project-3",
		Title:     "Update Batch Item 2",
		Type:      "task",
		Status:    "todo",
		Priority:  models.PriorityMedium,
	}

	err := env.service.CreateItem(ctx, item1)
	assert.NoError(t, err)
	err = env.service.CreateItem(ctx, item2)
	assert.NoError(t, err)

	txDB := env.db.Begin()
	defer txDB.Rollback()

	txCtx := tx.WithTransaction(ctx, txDB)
	item1.Status = "in_progress"
	item2.Status = "done"

	err = env.service.UpdateBatch(txCtx, []*models.Item{item1, item2})
	assert.NoError(t, err)

	var txItem1 models.Item
	txDB.Where("id = ?", item1.ID).First(&txItem1)
	assert.Equal(t, "in_progress", txItem1.Status)

	var mainItem1 models.Item
	env.db.Where("id = ?", item1.ID).First(&mainItem1)
	assert.Equal(t, "todo", mainItem1.Status, "Status should not be updated in main DB before commit")

	txDB.Commit()

	env.db.Where("id = ?", item1.ID).First(&mainItem1)
	assert.Equal(t, "in_progress", mainItem1.Status, "Status should be updated in main DB after commit")
}

func runDeleteBatchWithTx(t *testing.T, env *itemServiceTxEnv) {
	ctx := context.Background()

	item1 := &models.Item{
		ID:        "test-delete-batch-1",
		ProjectID: "test-project-4",
		Title:     "Delete Batch Item 1",
		Type:      "task",
		Status:    "todo",
		Priority:  models.PriorityMedium,
	}
	item2 := &models.Item{
		ID:        "test-delete-batch-2",
		ProjectID: "test-project-4",
		Title:     "Delete Batch Item 2",
		Type:      "task",
		Status:    "todo",
		Priority:  models.PriorityMedium,
	}

	err := env.service.CreateItem(ctx, item1)
	assert.NoError(t, err)
	err = env.service.CreateItem(ctx, item2)
	assert.NoError(t, err)

	var count int64
	env.db.Model(&models.Item{}).Where("project_id = ?", "test-project-4").Where("deleted_at IS NULL").Count(&count)
	assert.Equal(t, int64(2), count)

	txDB := env.db.Begin()
	defer txDB.Rollback()

	txCtx := tx.WithTransaction(ctx, txDB)

	err = env.service.DeleteBatch(txCtx, []string{item1.ID, item2.ID})
	assert.NoError(t, err)

	txDB.Model(&models.Item{}).Where("project_id = ?", "test-project-4").Where("deleted_at IS NULL").Count(&count)
	assert.Equal(t, int64(0), count, "Items should be deleted in transaction")

	env.db.Model(&models.Item{}).Where("project_id = ?", "test-project-4").Where("deleted_at IS NULL").Count(&count)
	assert.Equal(t, int64(2), count, "Items should still exist in main DB before commit")

	txDB.Commit()

	env.db.Model(&models.Item{}).Where("project_id = ?", "test-project-4").Where("deleted_at IS NULL").Count(&count)
	assert.Equal(t, int64(0), count, "Items should be deleted in main DB after commit")
}
