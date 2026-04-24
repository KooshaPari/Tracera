//go:build !integration && !e2e

package services

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

func TestItemService_Create_ValidationError_NoTitle(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	item := &models.Item{
		ProjectID: testProjectIDValue,
		Title:     "", // Empty title
	}

	err := service.CreateItem(context.Background(), item)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "title is required")
}

func TestItemService_Create_ValidationError_NoProjectID(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	item := &models.Item{
		ProjectID: "", // Empty project ID
		Title:     "Test Item",
	}

	err := service.CreateItem(context.Background(), item)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "project ID is required")
}

func TestItemService_Update_ValidationError(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	item := &models.Item{
		ID:    "", // Empty ID
		Title: "Test Item",
	}

	err := service.UpdateItem(context.Background(), item)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "ID is required")
}

func TestItemService_GetItem_NotFound(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	itemRepo.On("GetByID", mock.Anything, "nonexistent").Return(nil, errors.New("item not found"))

	result, err := service.GetItem(context.Background(), "nonexistent")

	require.Error(t, err)
	assert.Nil(t, result)
	itemRepo.AssertExpectations(t)
}

func TestItemService_Delete_LinkDeletionError(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	item := &models.Item{
		ID:        testItemID,
		ProjectID: testProjectIDValue,
	}

	itemRepo.On("GetByID", mock.Anything, testItemID).Return(item, nil)
	linkRepo.On("DeleteByItemID", mock.Anything, testItemID).Return(errors.New("link deletion failed"))

	err := service.DeleteItem(context.Background(), testItemID)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "failed to delete item links")
	itemRepo.AssertExpectations(t)
	linkRepo.AssertExpectations(t)
}

func TestItemService_Create_RepositoryError(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	item := &models.Item{
		ProjectID: testProjectIDValue,
		Title:     "Test Item",
	}

	itemRepo.On("Create", mock.Anything, mock.Anything).Return(errors.New("database error"))

	err := service.CreateItem(context.Background(), item)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "failed to create item")
}

func TestItemService_GetItem_RepositoryError(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	itemRepo.On("GetByID", mock.Anything, testItemID).Return(nil, errors.New("database error"))

	result, err := service.GetItem(context.Background(), testItemID)
	require.Error(t, err)
	assert.Nil(t, result)
}

func TestItemService_ListItems_RepositoryError(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	filter := repository.ItemFilter{Limit: 10}
	itemRepo.On("List", mock.Anything, filter).Return(nil, errors.New("database error"))

	result, err := service.ListItems(context.Background(), filter)
	require.Error(t, err)
	assert.Nil(t, result)
}

func TestItemService_Update_RepositoryError(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	item := &models.Item{
		ID:        testItemID,
		ProjectID: testProjectIDValue,
		Title:     "Updated Title",
	}

	itemRepo.On("Update", mock.Anything, item).Return(errors.New("database error"))

	err := service.UpdateItem(context.Background(), item)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "failed to update item")
}

func TestItemService_Delete_DeleteError(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	item := &models.Item{
		ID:        testItemID,
		ProjectID: testProjectIDValue,
	}

	itemRepo.On("GetByID", mock.Anything, testItemID).Return(item, nil)
	linkRepo.On("DeleteByItemID", mock.Anything, testItemID).Return(nil)
	itemRepo.On("Delete", mock.Anything, testItemID).Return(errors.New("delete failed"))

	err := service.DeleteItem(context.Background(), testItemID)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "failed to delete item")
}

func TestItemService_GetItemStats_RepositoryError(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	projectID := testProjectIDValue
	projectIDPtr := &projectID
	itemRepo.On("List", mock.Anything, repository.ItemFilter{ProjectID: projectIDPtr}).Return(nil, errors.New("database error"))

	stats, err := service.GetItemStats(context.Background(), projectID)
	require.Error(t, err)
	assert.Nil(t, stats)
}

func TestItemService_Update_OptimisticLocking(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	item := &models.Item{
		ID:        testItemID,
		ProjectID: testProjectIDValue,
		Title:     "Updated Title",
	}

	itemRepo.On("Update", mock.Anything, item).Return(errors.New("version conflict"))

	err := service.UpdateItem(context.Background(), item)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "failed to update item")
}
