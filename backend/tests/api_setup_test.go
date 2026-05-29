//go:build api

package tests

import (
	"testing"

	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/handlers"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/kooshapari/tracertm-backend/internal/services"
)

func migrateAPITestDB(t *testing.T, db *gorm.DB) {
	t.Helper()
	if err := db.AutoMigrate(&models.Item{}, &models.Link{}, &models.Project{}); err != nil {
		t.Fatalf("Failed to migrate test database: %v", err)
	}
}

func newTestItemHandler(t *testing.T, db *gorm.DB) *handlers.ItemHandler {
	t.Helper()
	migrateAPITestDB(t, db)

	itemRepo := repository.NewItemRepository(db)
	linkRepo := repository.NewLinkRepository(db)
	itemService := services.NewItemServiceImpl(itemRepo, linkRepo, nil, nil)

	binder := &handlers.TestBinder{}
	handler := handlers.NewItemHandler(nil, nil, nil, nil, binder)
	handler.SetItemService(itemService)
	return handler
}

func newTestLinkHandler(t *testing.T, db *gorm.DB) *handlers.LinkHandler {
	t.Helper()
	migrateAPITestDB(t, db)

	itemRepo := repository.NewItemRepository(db)
	linkRepo := repository.NewLinkRepository(db)
	itemService := services.NewItemServiceImpl(itemRepo, linkRepo, nil, nil)
	linkService := services.NewLinkServiceImpl(linkRepo, itemService, nil, nil)

	binder := &handlers.TestBinder{}
	return handlers.NewLinkHandler(linkService, itemService, binder)
}
