package services

import (
	"context"
	"testing"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/kooshapari/tracertm-backend/internal/tx"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

type linkServiceTestEnv struct {
	db          *gorm.DB
	ctx         context.Context
	linkRepo    repository.LinkRepository
	itemRepo    repository.ItemRepository
	projectRepo repository.ProjectRepository
	itemService ItemService
	linkService LinkService
}

func setupLinkServiceTestEnv(t *testing.T) *linkServiceTestEnv {
	t.Helper()

	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	require.NoError(t, err)

	err = db.AutoMigrate(&models.Item{}, &models.Link{}, &models.Project{})
	require.NoError(t, err)

	linkRepo := repository.NewLinkRepository(db)
	itemRepo := repository.NewItemRepository(db)
	projectRepo := repository.NewProjectRepository(db)

	itemService := NewItemService(itemRepo, linkRepo, nil, nil)
	linkService := NewLinkServiceImpl(linkRepo, itemService, nil, nil)

	ctx := context.Background()

	project := &models.Project{
		ID:   "proj-1",
		Name: "Test Project",
	}
	err = projectRepo.Create(ctx, project)
	require.NoError(t, err)

	item1 := &models.Item{
		ID:        "item-1",
		ProjectID: "proj-1",
		Type:      "requirement",
		Title:     "Test Item 1",
		Status:    "active",
	}
	item2 := &models.Item{
		ID:        "item-2",
		ProjectID: "proj-1",
		Type:      "task",
		Title:     "Test Item 2",
		Status:    "active",
	}
	err = itemRepo.Create(ctx, item1)
	require.NoError(t, err)
	err = itemRepo.Create(ctx, item2)
	require.NoError(t, err)

	return &linkServiceTestEnv{
		db:          db,
		ctx:         ctx,
		linkRepo:    linkRepo,
		itemRepo:    itemRepo,
		projectRepo: projectRepo,
		itemService: itemService,
		linkService: linkService,
	}
}

// TestLinkServiceTransactionSupport tests that LinkService operations
// use transactions when available in context
func TestLinkServiceTransactionSupport(t *testing.T) {
	env := setupLinkServiceTestEnv(t)

	t.Run("Transaction committed - link should be created", func(t *testing.T) {
		runLinkTxCommit(t, env)
	})

	t.Run("Transaction rolled back - link should not exist", func(t *testing.T) {
		runLinkTxRollback(t, env)
	})

	t.Run("Multi-link atomic operation", func(t *testing.T) {
		runLinkTxMultiAtomic(t, env)
	})

	t.Run("Update and Delete operations support transactions", func(t *testing.T) {
		runLinkTxUpdateDelete(t, env)
	})
}

// TestLinkServiceWithoutTransaction tests that LinkService works
// correctly without transactions (backward compatibility)
func TestLinkServiceWithoutTransaction(t *testing.T) {
	env := setupLinkServiceTestEnv(t)

	t.Run("Operations work without transaction context", func(t *testing.T) {
		runLinkNoTransactionOps(t, env)
	})
}

func runLinkTxCommit(t *testing.T, env *linkServiceTestEnv) {
	txDB := env.db.Begin()
	require.NoError(t, txDB.Error)

	txCtx := tx.WithTransaction(env.ctx, txDB)

	link := &models.Link{
		ID:       "link-1",
		SourceID: "item-1",
		TargetID: "item-2",
		Type:     "depends-on",
	}
	err := env.linkService.CreateLink(txCtx, link)
	assert.NoError(t, err)

	retrievedLink, err := env.linkService.GetLink(txCtx, "link-1")
	assert.NoError(t, err)
	assert.NotNil(t, retrievedLink)
	assert.Equal(t, "item-1", retrievedLink.SourceID)

	err = txDB.Commit().Error
	assert.NoError(t, err)

	retrievedLink, err = env.linkService.GetLink(env.ctx, "link-1")
	assert.NoError(t, err)
	assert.NotNil(t, retrievedLink)
	assert.Equal(t, "link-1", retrievedLink.ID)
}

func runLinkTxRollback(t *testing.T, env *linkServiceTestEnv) {
	txDB := env.db.Begin()
	require.NoError(t, txDB.Error)

	txCtx := tx.WithTransaction(env.ctx, txDB)

	link := &models.Link{
		ID:       "link-2",
		SourceID: "item-1",
		TargetID: "item-2",
		Type:     "relates-to",
	}
	err := env.linkService.CreateLink(txCtx, link)
	assert.NoError(t, err)

	retrievedLink, err := env.linkService.GetLink(txCtx, "link-2")
	assert.NoError(t, err)
	assert.NotNil(t, retrievedLink)

	err = txDB.Rollback().Error
	assert.NoError(t, err)

	retrievedLink, err = env.linkService.GetLink(env.ctx, "link-2")
	assert.Error(t, err)
	assert.Nil(t, retrievedLink)
}

func runLinkTxMultiAtomic(t *testing.T, env *linkServiceTestEnv) {
	item3 := &models.Item{
		ID:        "item-3",
		ProjectID: "proj-1",
		Type:      "task",
		Title:     "Test Item 3",
		Status:    "active",
	}
	err := env.itemRepo.Create(env.ctx, item3)
	require.NoError(t, err)

	txDB := env.db.Begin()
	require.NoError(t, txDB.Error)

	txCtx := tx.WithTransaction(env.ctx, txDB)

	link3 := &models.Link{
		ID:       "link-3",
		SourceID: "item-1",
		TargetID: "item-3",
		Type:     "depends-on",
	}
	link4 := &models.Link{
		ID:       "link-4",
		SourceID: "item-2",
		TargetID: "item-3",
		Type:     "depends-on",
	}

	err = env.linkService.CreateLink(txCtx, link3)
	assert.NoError(t, err)

	err = env.linkService.CreateLink(txCtx, link4)
	assert.NoError(t, err)

	retrievedLink3, err := env.linkService.GetLink(txCtx, "link-3")
	assert.NoError(t, err)
	assert.NotNil(t, retrievedLink3)

	retrievedLink4, err := env.linkService.GetLink(txCtx, "link-4")
	assert.NoError(t, err)
	assert.NotNil(t, retrievedLink4)

	err = txDB.Rollback().Error
	assert.NoError(t, err)

	retrievedLink3, err = env.linkService.GetLink(env.ctx, "link-3")
	assert.Error(t, err)
	assert.Nil(t, retrievedLink3)

	retrievedLink4, err = env.linkService.GetLink(env.ctx, "link-4")
	assert.Error(t, err)
	assert.Nil(t, retrievedLink4)
}

func runLinkTxUpdateDelete(t *testing.T, env *linkServiceTestEnv) {
	link := &models.Link{
		ID:       "link-5",
		SourceID: "item-1",
		TargetID: "item-2",
		Type:     "relates-to",
	}
	err := env.linkService.CreateLink(env.ctx, link)
	require.NoError(t, err)

	txDB := env.db.Begin()
	require.NoError(t, txDB.Error)

	txCtx := tx.WithTransaction(env.ctx, txDB)

	link.Type = "depends-on"
	err = env.linkService.UpdateLink(txCtx, link)
	assert.NoError(t, err)

	retrievedLink, err := env.linkService.GetLink(txCtx, "link-5")
	assert.NoError(t, err)
	assert.Equal(t, "depends-on", retrievedLink.Type)

	err = txDB.Rollback().Error
	assert.NoError(t, err)

	retrievedLink, err = env.linkService.GetLink(env.ctx, "link-5")
	assert.NoError(t, err)
	assert.Equal(t, "relates-to", retrievedLink.Type)

	txDB = env.db.Begin()
	require.NoError(t, txDB.Error)

	txCtx = tx.WithTransaction(env.ctx, txDB)

	err = env.linkService.DeleteLink(txCtx, "link-5")
	assert.NoError(t, err)

	retrievedLink, err = env.linkService.GetLink(txCtx, "link-5")
	assert.Error(t, err)
	assert.Nil(t, retrievedLink)

	err = txDB.Rollback().Error
	assert.NoError(t, err)

	retrievedLink, err = env.linkService.GetLink(env.ctx, "link-5")
	assert.NoError(t, err)
	assert.NotNil(t, retrievedLink)
	assert.Equal(t, "link-5", retrievedLink.ID)
}

func runLinkNoTransactionOps(t *testing.T, env *linkServiceTestEnv) {
	link := &models.Link{
		ID:       "link-no-tx",
		SourceID: "item-1",
		TargetID: "item-2",
		Type:     "depends-on",
	}
	err := env.linkService.CreateLink(env.ctx, link)
	assert.NoError(t, err)

	retrievedLink, err := env.linkService.GetLink(env.ctx, "link-no-tx")
	assert.NoError(t, err)
	assert.NotNil(t, retrievedLink)
	assert.Equal(t, "item-1", retrievedLink.SourceID)

	link.Type = "relates-to"
	err = env.linkService.UpdateLink(env.ctx, link)
	assert.NoError(t, err)

	retrievedLink, err = env.linkService.GetLink(env.ctx, "link-no-tx")
	assert.NoError(t, err)
	assert.Equal(t, "relates-to", retrievedLink.Type)

	err = env.linkService.DeleteLink(env.ctx, "link-no-tx")
	assert.NoError(t, err)

	retrievedLink, err = env.linkService.GetLink(env.ctx, "link-no-tx")
	assert.Error(t, err)
	assert.Nil(t, retrievedLink)
}
