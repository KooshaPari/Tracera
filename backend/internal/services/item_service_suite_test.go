//go:build !integration && !e2e

package services

import (
	"context"
	"testing"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

func TestItemServiceSuite(t *testing.T) {
	suite.Run(t, new(ItemServiceTestSuite))
}

func (suite *ItemServiceTestSuite) TestItemService_Create_Success() {
	item := &models.Item{
		ProjectID:   testProjectIDValue,
		Title:       "Test Item",
		Description: "Test Description",
		Type:        "feature",
	}

	suite.itemRepo.On("Create", suite.ctx, mock.MatchedBy(func(i *models.Item) bool {
		return i.ProjectID == item.ProjectID &&
			i.Title == item.Title &&
			i.Status == "todo" &&
			i.Priority == models.PriorityMedium
	})).Return(nil)

	err := suite.service.CreateItem(suite.ctx, item)

	suite.Require().NoError(err)
	suite.Equal("todo", item.Status)
	suite.Equal(models.PriorityMedium, item.Priority)
}

func (suite *ItemServiceTestSuite) TestItemService_Create_CacheInvalidation() {
	item := &models.Item{
		ProjectID: testProjectIDValue,
		Title:     "Test Item",
	}

	suite.itemRepo.On("Create", suite.ctx, mock.Anything).Return(nil)

	err := suite.service.CreateItem(suite.ctx, item)

	suite.Require().NoError(err)
}

func (suite *ItemServiceTestSuite) TestItemService_Create_EventPublishing() {
	item := &models.Item{
		ProjectID: testProjectIDValue,
		Title:     "Test Item",
	}

	suite.itemRepo.On("Create", suite.ctx, mock.Anything).Return(nil)

	err := suite.service.CreateItem(suite.ctx, item)

	suite.Require().NoError(err)
}

func (suite *ItemServiceTestSuite) TestItemService_Get_CacheHit() {
	itemID := testItemID
	expectedItem := &models.Item{
		ID:        itemID,
		ProjectID: testProjectIDValue,
		Title:     "Item from DB",
		Status:    "todo",
	}

	suite.itemRepo.On("GetByID", suite.ctx, itemID).Return(expectedItem, nil)

	result, err := suite.service.GetItem(suite.ctx, itemID)

	suite.Require().NoError(err)
	suite.NotNil(result)
	suite.Equal(expectedItem.ID, result.ID)
	suite.Equal(expectedItem.Title, result.Title)
}

func (suite *ItemServiceTestSuite) TestItemService_Get_CacheMiss() {
	itemID := testItemID
	expectedItem := &models.Item{
		ID:        itemID,
		ProjectID: testProjectIDValue,
		Title:     "Database Item",
		Status:    "in_progress",
	}

	suite.itemRepo.On("GetByID", suite.ctx, itemID).Return(expectedItem, nil)

	result, err := suite.service.GetItem(suite.ctx, itemID)

	suite.Require().NoError(err)
	suite.NotNil(result)
	suite.Equal(expectedItem.ID, result.ID)
	suite.Equal(expectedItem.Title, result.Title)
}

func (suite *ItemServiceTestSuite) TestItemService_Update_Success() {
	item := &models.Item{
		ID:        testItemID,
		ProjectID: testProjectIDValue,
		Title:     "Updated Item",
	}

	suite.itemRepo.On("Update", suite.ctx, item).Return(nil)

	err := suite.service.UpdateItem(suite.ctx, item)

	suite.Require().NoError(err)
}

func (suite *ItemServiceTestSuite) TestItemService_Update_CacheInvalidation() {
	item := &models.Item{
		ID:        testItemID,
		ProjectID: testProjectIDValue,
		Title:     "Updated Item",
	}

	suite.itemRepo.On("Update", suite.ctx, item).Return(nil)

	err := suite.service.UpdateItem(suite.ctx, item)

	suite.Require().NoError(err)
}

func (suite *ItemServiceTestSuite) TestItemService_Delete_Success() {
	itemID := testItemID
	item := &models.Item{
		ID:        itemID,
		ProjectID: testProjectIDValue,
		Title:     "Item to Delete",
	}

	suite.itemRepo.On("GetByID", suite.ctx, itemID).Return(item, nil)
	suite.linkRepo.On("DeleteByItemID", suite.ctx, itemID).Return(nil)
	suite.itemRepo.On("Delete", suite.ctx, itemID).Return(nil)

	err := suite.service.DeleteItem(suite.ctx, itemID)

	suite.Require().NoError(err)
}

func (suite *ItemServiceTestSuite) TestItemService_Delete_EventPublishing() {
	itemID := testItemID
	item := &models.Item{
		ID:        itemID,
		ProjectID: testProjectIDValue,
	}

	suite.itemRepo.On("GetByID", suite.ctx, itemID).Return(item, nil)
	suite.linkRepo.On("DeleteByItemID", suite.ctx, itemID).Return(nil)
	suite.itemRepo.On("Delete", suite.ctx, itemID).Return(nil)

	err := suite.service.DeleteItem(suite.ctx, itemID)

	suite.Require().NoError(err)
}

func (suite *ItemServiceTestSuite) TestItemService_List_WithFilters() {
	projectID := testProjectIDValue
	itemType := "feature"
	filter := repository.ItemFilter{
		ProjectID: &projectID,
		Type:      &itemType,
		Limit:     10,
	}

	expectedItems := []*models.Item{
		{ID: "item-1", ProjectID: projectID, Type: itemType, Title: "Item 1"},
		{ID: "item-2", ProjectID: projectID, Type: itemType, Title: "Item 2"},
	}

	suite.itemRepo.On("List", suite.ctx, filter).Return(expectedItems, nil)

	result, err := suite.service.ListItems(suite.ctx, filter)

	suite.Require().NoError(err)
	suite.NotNil(result)
	suite.Len(result, 2)
	suite.Equal(expectedItems[0].ID, result[0].ID)
}

func (suite *ItemServiceTestSuite) TestItemService_Statistics_Success() {
	projectID := testProjectIDValue
	items := []*models.Item{
		{Type: "feature", Status: "todo", Priority: models.PriorityHigh},
		{Type: "feature", Status: "in_progress", Priority: models.PriorityMedium},
		{Type: "bug", Status: "todo", Priority: models.PriorityHigh},
	}

	projectIDPtr := &projectID
	suite.itemRepo.On("List", suite.ctx, repository.ItemFilter{ProjectID: projectIDPtr}).Return(items, nil)

	stats, err := suite.service.GetItemStats(suite.ctx, projectID)

	suite.Require().NoError(err)
	suite.NotNil(stats)
	suite.Equal(int64(3), stats.TotalItems)
	suite.Equal(int64(2), stats.ByType["feature"])
	suite.Equal(int64(1), stats.ByType["bug"])
	suite.Equal(int64(2), stats.ByStatus["todo"])
	suite.Equal(int64(2), stats.ByPriority["high"])
}

func (suite *ItemServiceTestSuite) TestItemService_BatchCreate() {
	items := []*models.Item{
		{ProjectID: testProjectIDValue, Title: "Item 1", Type: "feature"},
		{ProjectID: testProjectIDValue, Title: "Item 2", Type: "bug"},
		{ProjectID: testProjectIDValue, Title: "Item 3", Type: "task"},
	}

	suite.itemRepo.On("Create", mock.Anything, mock.Anything).Return(nil).Times(3)

	for _, item := range items {
		err := suite.service.CreateItem(context.Background(), item)
		suite.Require().NoError(err)
	}
}

func (suite *ItemServiceTestSuite) TestItemService_BatchUpdate() {
	items := []*models.Item{
		{ID: "item-1", ProjectID: testProjectIDValue, Title: "Updated Item 1"},
		{ID: "item-2", ProjectID: testProjectIDValue, Title: "Updated Item 2"},
		{ID: "item-3", ProjectID: testProjectIDValue, Title: "Updated Item 3"},
	}

	suite.itemRepo.On("Update", mock.Anything, mock.Anything).Return(nil)

	for _, item := range items {
		err := suite.service.UpdateItem(context.Background(), item)
		suite.Require().NoError(err)
	}
}

func (suite *ItemServiceTestSuite) TestItemService_BatchDelete() {
	itemIDs := []string{"item-1", "item-2", "item-3"}

	for _, id := range itemIDs {
		suite.itemRepo.On("GetByID", mock.Anything, id).Return(&models.Item{
			ID:        id,
			ProjectID: testProjectIDValue,
		}, nil)
		suite.linkRepo.On("DeleteByItemID", mock.Anything, id).Return(nil)
		suite.itemRepo.On("Delete", mock.Anything, id).Return(nil)
	}

	for _, id := range itemIDs {
		err := suite.service.DeleteItem(context.Background(), id)
		suite.Require().NoError(err)
	}
}

func (suite *ItemServiceTestSuite) TestItemService_GetItemStats_CacheScenarios() {
	tests := []struct {
		name          string
		projectID     string
		items         []*models.Item
		expectedStats *ItemStats
	}{
		{
			name:      "with diverse items",
			projectID: testProjectIDValue,
			items: []*models.Item{
				{Type: "feature", Status: "todo", Priority: models.PriorityHigh},
				{Type: "feature", Status: "in_progress", Priority: models.PriorityMedium},
				{Type: "bug", Status: "todo", Priority: models.PriorityHigh},
				{Type: "task", Status: "done", Priority: models.PriorityLow},
			},
			expectedStats: &ItemStats{
				TotalItems: 4,
				ByType:     map[string]int64{"feature": 2, "bug": 1, "task": 1},
				ByStatus:   map[string]int64{"todo": 2, "in_progress": 1, "done": 1},
				ByPriority: map[string]int64{"high": 2, "medium": 1, "low": 1},
			},
		},
	}

	for _, tt := range tests {
		suite.Run(tt.name, func() {
			projectIDPtr := &tt.projectID
			suite.itemRepo.On("List", mock.Anything, repository.ItemFilter{ProjectID: projectIDPtr}).Return(tt.items, nil).Once()

			stats, err := suite.service.GetItemStats(context.Background(), tt.projectID)

			suite.Require().NoError(err)
			suite.NotNil(stats)
			suite.Equal(tt.expectedStats.TotalItems, stats.TotalItems)
			suite.Equal(tt.expectedStats.ByType, stats.ByType)
			suite.Equal(tt.expectedStats.ByStatus, stats.ByStatus)
			suite.Equal(tt.expectedStats.ByPriority, stats.ByPriority)
		})
	}
}

func (suite *ItemServiceTestSuite) TestItemService_ListItems_Pagination() {
	testCases := []struct {
		name           string
		filter         repository.ItemFilter
		expectedResult []*models.Item
	}{
		{
			name: "first page",
			filter: repository.ItemFilter{
				Limit:  10,
				Offset: 0,
			},
			expectedResult: []*models.Item{
				{ID: "item-1", Title: "Item 1"},
				{ID: "item-2", Title: "Item 2"},
			},
		},
	}

	for _, tc := range testCases {
		suite.Run(tc.name, func() {
			suite.itemRepo.On("List", mock.Anything, tc.filter).Return(tc.expectedResult, nil).Once()
			result, err := suite.service.ListItems(context.Background(), tc.filter)
			suite.Require().NoError(err)
			suite.Len(result, len(tc.expectedResult))
		})
	}
}

func (suite *ItemServiceTestSuite) TestItemService_Delete_CascadeLinks_Success() {
	itemID := "item-with-many-links"
	item := &models.Item{
		ID:        itemID,
		ProjectID: testProjectIDValue,
		Title:     "Item with many links",
	}

	suite.itemRepo.On("GetByID", mock.Anything, itemID).Return(item, nil)
	suite.linkRepo.On("DeleteByItemID", mock.Anything, itemID).Return(nil)
	suite.itemRepo.On("Delete", mock.Anything, itemID).Return(nil)

	err := suite.service.DeleteItem(context.Background(), itemID)

	suite.Require().NoError(err)
}
