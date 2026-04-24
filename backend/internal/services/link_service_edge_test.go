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

func TestLinkService_Create_SelfLink(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	itemID := testItem1ID
	link := &models.Link{
		SourceID: itemID,
		TargetID: itemID,
		Type:     "self_reference",
	}

	itemRepo.On("GetByID", mock.Anything, itemID).Return(&models.Item{ID: itemID}, nil).Times(2)
	linkRepo.On("Create", mock.Anything, mock.MatchedBy(func(l *models.Link) bool {
		return l.SourceID == itemID && l.TargetID == itemID
	})).Return(nil)

	err := service.CreateLink(context.Background(), link)
	require.NoError(t, err)
}

func TestLinkService_Create_DuplicatePrevention(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	sourceID := testItem1ID
	targetID := "item-2"
	link := &models.Link{
		SourceID: sourceID,
		TargetID: targetID,
		Type:     "depends_on",
	}

	itemRepo.On("GetByID", mock.Anything, mock.Anything).Return(&models.Item{ID: sourceID}, nil)
	linkRepo.On("Create", mock.Anything, mock.Anything).Return(errors.New("duplicate link"))

	err := service.CreateLink(context.Background(), link)
	require.Error(t, err)
}

func TestLinkService_ListLinks_EmptyResults(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	filter := repository.LinkFilter{Limit: 10}
	linkRepo.On("List", mock.Anything, filter).Return([]*models.Link{}, nil)

	result, err := service.ListLinks(context.Background(), filter)
	require.NoError(t, err)
	assert.Empty(t, result)
}

func TestLinkService_GetDependencies_CircularReference(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	itemID := testItem1ID
	link1 := &models.Link{ID: "link-1", SourceID: itemID, TargetID: "item-2", Type: "depends_on"}
	link2 := &models.Link{ID: "link-2", SourceID: "item-2", TargetID: itemID, Type: "depends_on"}

	itemRepo.On("GetByID", mock.Anything, "item-2").Return(&models.Item{ID: "item-2"}, nil)
	linkRepo.On("GetBySourceID", mock.Anything, itemID).Return([]*models.Link{link1}, nil)
	linkRepo.On("GetByTargetID", mock.Anything, itemID).Return([]*models.Link{link2}, nil)

	result, err := service.GetItemDependencies(context.Background(), itemID)
	require.NoError(t, err)
	assert.NotNil(t, result)
}
