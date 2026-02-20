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
)

func TestLinkService_Create_ValidationError_NoSourceID(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	link := &models.Link{
		SourceID: "",
		TargetID: "item-2",
		Type:     "depends_on",
	}

	err := service.CreateLink(context.Background(), link)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "source and target IDs are required")
}

func TestLinkService_Create_ValidationError_NoTargetID(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	link := &models.Link{
		SourceID: testItem1ID,
		TargetID: "",
		Type:     "depends_on",
	}

	err := service.CreateLink(context.Background(), link)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "source and target IDs are required")
}

func TestLinkService_Create_ValidationError_NoType(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	link := &models.Link{
		SourceID: testItem1ID,
		TargetID: "item-2",
		Type:     "",
	}

	err := service.CreateLink(context.Background(), link)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "link type is required")
}

func TestLinkService_Create_SourceItemNotFound(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	link := &models.Link{
		SourceID: "nonexistent",
		TargetID: "item-2",
		Type:     "depends_on",
	}

	itemRepo.On("GetByID", mock.Anything, "nonexistent").Return(nil, errors.New("item not found"))

	err := service.CreateLink(context.Background(), link)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "source item not found")
}

func TestLinkService_Create_TargetItemNotFound(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	sourceItem := &models.Item{ID: testItem1ID}
	link := &models.Link{
		SourceID: testItem1ID,
		TargetID: "nonexistent",
		Type:     "depends_on",
	}

	itemRepo.On("GetByID", mock.Anything, testItem1ID).Return(sourceItem, nil)
	itemRepo.On("GetByID", mock.Anything, "nonexistent").Return(nil, errors.New("item not found"))

	err := service.CreateLink(context.Background(), link)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "target item not found")
}

func TestLinkService_GetLink_NotFound(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	linkRepo.On("GetByID", mock.Anything, "nonexistent").Return(nil, errors.New("link not found"))

	result, err := service.GetLink(context.Background(), "nonexistent")

	require.Error(t, err)
	assert.Nil(t, result)
}

func TestLinkService_Update_Error(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	link := &models.Link{
		ID:       "link-123",
		SourceID: testItem1ID,
		TargetID: "item-2",
		Type:     "depends_on",
	}

	linkRepo.On("Update", mock.Anything, link).Return(errors.New("update failed"))

	err := service.UpdateLink(context.Background(), link)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "failed to update link")
}

func TestLinkService_Delete_Error(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	linkRepo.On("Delete", mock.Anything, "link-123").Return(errors.New("delete failed"))

	err := service.DeleteLink(context.Background(), "link-123")

	require.Error(t, err)
	assert.Contains(t, err.Error(), "failed to delete link")
}

func TestLinkService_GetDependencies_EmptyGraph(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	itemID := testItem1ID

	linkRepo.On("GetBySourceID", mock.Anything, itemID).Return([]*models.Link{}, nil)
	linkRepo.On("GetByTargetID", mock.Anything, itemID).Return([]*models.Link{}, nil)

	result, err := service.GetItemDependencies(context.Background(), itemID)

	require.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, itemID, result.ItemID)
	assert.Empty(t, result.Dependencies)
	assert.Empty(t, result.Dependents)
	assert.Empty(t, result.Items)
}

func TestLinkService_GetDependencies_SourceError(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	itemID := testItem1ID
	linkRepo.On("GetBySourceID", mock.Anything, itemID).Return(nil, errors.New("database error"))

	result, err := service.GetItemDependencies(context.Background(), itemID)
	require.Error(t, err)
	assert.Nil(t, result)
}
