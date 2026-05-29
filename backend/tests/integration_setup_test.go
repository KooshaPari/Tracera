//go:build integration

package tests

import (
	"context"
	"os"
	"testing"

	"github.com/google/uuid"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/handlers"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/kooshapari/tracertm-backend/internal/services"
)

var (
	testDB          *gorm.DB
	testProject     *models.Project
	testItemService services.ItemService
	testLinkService services.LinkService
	testItemHandler *handlers.ItemHandler
	testLinkHandler *handlers.LinkHandler
)

func TestMain(m *testing.M) {
	var err error
	testDB, err = gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{})
	if err != nil {
		panic(err)
	}
	if err := testDB.AutoMigrate(&models.Item{}, &models.Link{}, &models.Project{}); err != nil {
		panic(err)
	}

	testProject = &models.Project{
		ID:          uuid.New().String(),
		Name:        "Integration Test Project",
		Description: "Project for legacy integration tests",
	}
	itemRepo := repository.NewItemRepository(testDB)
	linkRepo := repository.NewLinkRepository(testDB)
	projectRepo := repository.NewProjectRepository(testDB)
	if err := projectRepo.Create(context.Background(), testProject); err != nil {
		panic(err)
	}

	testItemService = services.NewItemServiceImpl(itemRepo, linkRepo, nil, nil)
	testLinkService = services.NewLinkServiceImpl(linkRepo, testItemService, nil, nil)

	binder := &handlers.TestBinder{}
	testItemHandler = handlers.NewItemHandler(nil, nil, nil, nil, binder)
	testItemHandler.SetItemService(testItemService)
	testLinkHandler = handlers.NewLinkHandler(testLinkService, testItemService, binder)

	os.Exit(m.Run())
}

func createTestItem() *models.Item {
	ctx := context.Background()
	item := &models.Item{
		Title:       "Test Item",
		Type:        "requirement",
		Description: "Test content",
		ProjectID:   testProject.ID,
		Status:      "open",
	}
	if err := testItemService.CreateItem(ctx, item); err != nil {
		panic(err)
	}
	return item
}

func createTestLink(sourceID, targetID, linkType string) *models.Link {
	ctx := context.Background()
	link := &models.Link{
		SourceID: sourceID,
		TargetID: targetID,
		Type:     linkType,
	}
	if err := testLinkService.CreateLink(ctx, link); err != nil {
		panic(err)
	}
	return link
}
