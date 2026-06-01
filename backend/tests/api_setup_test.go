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

// Deterministic UUIDs for link handler API tests (CreateLink validates UUID format).
const (
	testLinkProjectID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
	testLinkItem1ID   = "11111111-1111-1111-1111-111111111111"
	testLinkItem2ID   = "22222222-2222-2222-2222-222222222222"
	testLinkItem3ID   = "33333333-3333-3333-3333-333333333333"
)

func seedLinkTestItems(t *testing.T, db *gorm.DB) {
	t.Helper()
	migrateAPITestDB(t, db)
	items := []models.Item{
		{ID: testLinkItem1ID, ProjectID: testLinkProjectID, Title: "Item 1", Type: "requirement", Status: "open"},
		{ID: testLinkItem2ID, ProjectID: testLinkProjectID, Title: "Item 2", Type: "requirement", Status: "open"},
		{ID: testLinkItem3ID, ProjectID: testLinkProjectID, Title: "Item 3", Type: "requirement", Status: "open"},
	}
	for i := range items {
		if err := db.Create(&items[i]).Error; err != nil {
			t.Fatalf("seed link test items: %v", err)
		}
	}
}

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
