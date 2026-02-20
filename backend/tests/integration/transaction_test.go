//go:build integration

package integration

import (
	"fmt"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/tx"
)

func TestServiceIntegration_Transaction_MultiOperation(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Transaction Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	txDB := f.db.Begin()
	txCtx := tx.WithTransaction(f.ctx, txDB)

	item1 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "TX Item 1",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	item2 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "TX Item 2",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	err := f.itemRepo.Create(txCtx, item1)
	require.NoError(t, err)
	err = f.itemRepo.Create(txCtx, item2)
	require.NoError(t, err)

	err = txDB.Commit().Error
	assert.NoError(t, err)

	retrieved1, err := f.itemRepo.GetByID(f.ctx, item1.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved1)

	retrieved2, err := f.itemRepo.GetByID(f.ctx, item2.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved2)
}

func TestServiceIntegration_Transaction_Rollback(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Rollback Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	txDB := f.db.Begin()
	txCtx := tx.WithTransaction(f.ctx, txDB)

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Rollback Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	err := f.itemRepo.Create(txCtx, item)
	require.NoError(t, err)

	txDB.Rollback()

	_, err = f.itemRepo.GetByID(f.ctx, item.ID)
	assert.Error(t, err)
}

func TestServiceIntegration_Transaction_NestedCalls(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Nested TX Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	txDB := f.db.Begin()
	txCtx := tx.WithTransaction(f.ctx, txDB)

	item1 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Nested Item 1",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	item2 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Nested Item 2",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	err := f.itemRepo.Create(txCtx, item1)
	require.NoError(t, err)
	err = f.itemRepo.Create(txCtx, item2)
	require.NoError(t, err)

	link := &models.Link{
		ID:        uuid.New().String(),
		SourceID:  item1.ID,
		TargetID:  item2.ID,
		Type:      "depends_on",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	err = f.linkRepo.Create(txCtx, link)
	require.NoError(t, err)

	err = txDB.Commit().Error
	assert.NoError(t, err)

	_, err = f.itemRepo.GetByID(f.ctx, item1.ID)
	assert.NoError(t, err)
	_, err = f.itemRepo.GetByID(f.ctx, item2.ID)
	assert.NoError(t, err)
	_, err = f.linkRepo.GetByID(f.ctx, link.ID)
	assert.NoError(t, err)
}

func TestServiceIntegration_Transaction_Isolation(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Isolation Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	tx1 := f.db.Begin()
	txCtx1 := tx.WithTransaction(f.ctx, tx1)

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Isolated Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	err := f.itemRepo.Create(txCtx1, item)
	require.NoError(t, err)

	_, err = f.itemRepo.GetByID(f.ctx, item.ID)
	assert.Error(t, err)

	err = tx1.Commit().Error
	assert.NoError(t, err)

	retrieved, err := f.itemRepo.GetByID(f.ctx, item.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved)
}

func TestServiceIntegration_Transaction_BatchOperation(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Batch TX Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	items := make([]*models.Item, 5)
	for i := 0; i < 5; i++ {
		items[i] = &models.Item{
			ID:        uuid.New().String(),
			ProjectID: project.ID,
			Title:     fmt.Sprintf("Batch Item %d", i),
			Type:      "task",
			Status:    "todo",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
	}

	err := f.itemService.CreateBatch(f.ctx, items)
	assert.NoError(t, err)

	for _, item := range items {
		retrieved, err := f.itemRepo.GetByID(f.ctx, item.ID)
		assert.NoError(t, err)
		assert.NotNil(t, retrieved)
	}
}
