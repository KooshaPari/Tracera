//go:build !integration && !e2e

package services

import (
	"context"
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

func TestItemService_Create_WithSpecialCharacters(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	item := &models.Item{
		ProjectID:   testProjectIDValue,
		Title:       "Test Item with 特殊文字 and émojis 🚀",
		Description: "Description with <html> & \"quotes\" 'apostrophes'",
		Type:        "feature",
	}

	itemRepo.On("Create", mock.Anything, mock.MatchedBy(func(i *models.Item) bool {
		return i.Title == item.Title && i.Description == item.Description
	})).Return(nil)

	err := service.CreateItem(context.Background(), item)
	require.NoError(t, err)
}

func TestItemService_Create_WithVeryLongTitle(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	longTitle := "This is a very long title that contains many characters to test the handling of edge cases " +
		"and ensure that the system can properly handle inputs that might exceed reasonable length limits " +
		"while still maintaining data integrity and proper validation throughout the system " +
		"without causing any performance degradation or storage issues whatsoever"

	item := &models.Item{
		ProjectID: testProjectIDValue,
		Title:     longTitle,
		Type:      "bug",
	}

	itemRepo.On("Create", mock.Anything, mock.MatchedBy(func(i *models.Item) bool {
		return len(i.Title) > 200
	})).Return(nil)

	err := service.CreateItem(context.Background(), item)
	require.NoError(t, err)
}

func TestItemService_ListItems_EmptyResults(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	filter := repository.ItemFilter{Limit: 10}
	itemRepo.On("List", mock.Anything, filter).Return([]*models.Item{}, nil)

	result, err := service.ListItems(context.Background(), filter)
	require.NoError(t, err)
	assert.Empty(t, result)
}

func TestItemService_GetItemStats_NoItems(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	projectID := testProjectIDValue
	projectIDPtr := &projectID
	itemRepo.On("List", mock.Anything, repository.ItemFilter{ProjectID: projectIDPtr}).Return([]*models.Item{}, nil)

	stats, err := service.GetItemStats(context.Background(), projectID)
	require.NoError(t, err)
	assert.NotNil(t, stats)
	assert.Equal(t, int64(0), stats.TotalItems)
}

func TestItemService_Create_AllDefaults(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	item := &models.Item{
		ProjectID: testProjectIDValue,
		Title:     "Minimal Item",
	}

	itemRepo.On("Create", mock.Anything, mock.MatchedBy(func(i *models.Item) bool {
		return i.Status == "todo" && i.Priority == models.PriorityMedium
	})).Return(nil)

	err := service.CreateItem(context.Background(), item)
	require.NoError(t, err)
	assert.Equal(t, "todo", item.Status)
	assert.Equal(t, models.PriorityMedium, item.Priority)
}

func TestItemService_Concurrent_Creates(t *testing.T) {
	itemRepo := new(MockItemRepository)
	linkRepo := new(MockLinkRepository)
	service := NewItemService(itemRepo, linkRepo, nil, nil)

	itemRepo.On("Create", mock.Anything, mock.Anything).Return(nil)

	const numGoroutines = 10
	done := make(chan bool, numGoroutines)
	errors := make(chan error, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		go func(index int) {
			item := &models.Item{
				ProjectID: testProjectIDValue,
				Title:     fmt.Sprintf("Item %d", index),
			}
			errors <- service.CreateItem(context.Background(), item)
			done <- true
		}(i)
	}

	for i := 0; i < numGoroutines; i++ {
		<-done
		require.NoError(t, <-errors)
	}
}
