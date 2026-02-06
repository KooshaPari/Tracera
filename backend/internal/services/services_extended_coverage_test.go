//go:build !integration && !e2e

package services

import (
	"context"
	"errors"
	"testing"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func newItemServiceWithMocks() (*MockItemRepository, *MockLinkRepository, ItemService) {
	mockRepo := new(MockItemRepository)
	mockLinkRepo := new(MockLinkRepository)
	service := NewItemService(mockRepo, mockLinkRepo, nil, nil)
	return mockRepo, mockLinkRepo, service
}

func newLinkServiceWithMocks() (*MockLinkRepository, *MockItemRepository, LinkService) {
	mockRepo := new(MockLinkRepository)
	mockItemRepo := new(MockItemRepository)
	service := NewLinkService(mockRepo, mockItemRepo, nil)
	return mockRepo, mockItemRepo, service
}

// TestItemService_CreateItem_Extended tests CreateItem with more edge cases
func TestItemService_CreateItem_Extended(t *testing.T) {
	for _, tc := range itemCreateExtendedCases() {
		t.Run(tc.name, func(t *testing.T) {
			runCreateItemCase(t, tc)
		})
	}
}

type createItemCase struct {
	name           string
	item           *models.Item
	repoErr        error
	expectCreate   bool
	expectErr      string
	expectStatus   string
	expectPriority models.Priority
}

func itemCreateExtendedCases() []createItemCase {
	return []createItemCase{
		{
			name:      "empty title",
			item:      &models.Item{Title: "", ProjectID: "project-1"},
			expectErr: "item title is required",
		},
		{
			name:      "empty project ID",
			item:      &models.Item{Title: "Test Item", ProjectID: ""},
			expectErr: "project ID is required",
		},
		{
			name:           "default status and priority",
			item:           &models.Item{Title: "Test Item", ProjectID: "project-1", Status: "", Priority: 0},
			expectCreate:   true,
			expectStatus:   "todo",
			expectPriority: models.PriorityMedium,
		},
		{
			name:         "repository error",
			item:         &models.Item{Title: "Test Item", ProjectID: "project-1"},
			repoErr:      errors.New("database error"),
			expectCreate: true,
			expectErr:    "failed to create item",
		},
	}
}

func runCreateItemCase(t *testing.T, tc createItemCase) {
	mockRepo, _, service := newItemServiceWithMocks()
	ctx := context.Background()

	if tc.expectCreate {
		mockRepo.On("Create", ctx, tc.item).Return(tc.repoErr)
	}

	err := service.CreateItem(ctx, tc.item)
	if tc.expectErr != "" {
		assert.Error(t, err)
		assert.Contains(t, err.Error(), tc.expectErr)
	} else {
		require.NoError(t, err)
	}

	if tc.expectStatus != "" {
		assert.Equal(t, tc.expectStatus, tc.item.Status)
		assert.Equal(t, tc.expectPriority, tc.item.Priority)
	}

	if tc.expectCreate {
		mockRepo.AssertExpectations(t)
	} else {
		mockRepo.AssertNotCalled(t, "Create")
	}
}

// TestItemService_GetItemStats_Extended tests GetItemStats with more edge cases
func TestItemService_GetItemStats_Extended(t *testing.T) {
	t.Run("repository error", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		ctx := context.Background()
		projectID := "project-1"
		projectIDPtr := &projectID

		mockRepo.On("List", ctx, repository.ItemFilter{ProjectID: projectIDPtr}).Return(nil, errors.New("repository error"))

		stats, err := service.GetItemStats(ctx, projectID)
		assert.Error(t, err)
		assert.Nil(t, stats)
		mockRepo.AssertExpectations(t)
	})

	t.Run("empty project ID", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		ctx := context.Background()
		projectID := ""
		projectIDPtr := &projectID

		mockRepo.On("List", ctx, repository.ItemFilter{ProjectID: projectIDPtr}).Return(nil, errors.New("repository error"))

		stats, err := service.GetItemStats(ctx, projectID)
		assert.Error(t, err)
		assert.Nil(t, stats)
		mockRepo.AssertExpectations(t)
	})
}

// TestLinkService_GetItemDependencies_Extended tests GetItemDependencies
func TestLinkService_GetItemDependencies_Extended(t *testing.T) {
	t.Run("error getting dependencies", func(t *testing.T) {
		mockRepo := new(MockLinkRepository)
		mockItemRepo := new(MockItemRepository)
		service := NewLinkService(mockRepo, mockItemRepo, nil)

		ctx := context.Background()
		itemID := testItem1ID

		mockRepo.On("GetBySourceID", ctx, itemID).Return(nil, errors.New("repository error"))

		deps, err := service.GetItemDependencies(ctx, itemID)
		assert.Error(t, err)
		assert.Nil(t, deps)
		mockRepo.AssertExpectations(t)
	})

	t.Run("error getting dependents", func(t *testing.T) {
		mockRepo := new(MockLinkRepository)
		mockItemRepo := new(MockItemRepository)
		service := NewLinkService(mockRepo, mockItemRepo, nil)

		ctx := context.Background()
		itemID := testItem1ID

		mockRepo.On("GetBySourceID", ctx, itemID).Return([]*models.Link{}, nil)
		mockRepo.On("GetByTargetID", ctx, itemID).Return(nil, errors.New("repository error"))

		deps, err := service.GetItemDependencies(ctx, itemID)
		assert.Error(t, err)
		assert.Nil(t, deps)
		mockRepo.AssertExpectations(t)
	})

	t.Run("no dependencies", func(t *testing.T) {
		mockRepo := new(MockLinkRepository)
		mockItemRepo := new(MockItemRepository)
		service := NewLinkService(mockRepo, mockItemRepo, nil)

		ctx := context.Background()
		itemID := testItem1ID

		mockRepo.On("GetBySourceID", ctx, itemID).Return([]*models.Link{}, nil)
		mockRepo.On("GetByTargetID", ctx, itemID).Return([]*models.Link{}, nil)

		deps, err := service.GetItemDependencies(ctx, itemID)
		require.NoError(t, err)
		assert.NotNil(t, deps)
		assert.Equal(t, itemID, deps.ItemID)
		assert.Equal(t, 0, len(deps.Dependencies))
		assert.Equal(t, 0, len(deps.Dependents))
		mockRepo.AssertExpectations(t)
	})
}

// TestLinkService_CreateLink_Extended tests CreateLink with more edge cases
func TestLinkService_CreateLink_Extended(t *testing.T) {
	cases := []struct {
		name         string
		link         *models.Link
		sourceItem   *models.Item
		sourceErr    error
		targetItem   *models.Item
		targetErr    error
		expectErr    string
		expectCreate bool
	}{
		{
			name:      "empty source ID",
			link:      &models.Link{SourceID: "", TargetID: "item-2", Type: "depends_on"},
			expectErr: "source and target IDs are required",
		},
		{
			name:      "empty target ID",
			link:      &models.Link{SourceID: testItem1ID, TargetID: "", Type: "depends_on"},
			expectErr: "source and target IDs are required",
		},
		{
			name:      "empty link type",
			link:      &models.Link{SourceID: testItem1ID, TargetID: "item-2", Type: ""},
			expectErr: "link type is required",
		},
		{
			name:      "source item not found",
			link:      &models.Link{SourceID: testNonexistentID, TargetID: "item-2", Type: "depends_on"},
			sourceErr: errors.New("not found"),
			expectErr: "source item not found",
		},
		{
			name:       "target item not found",
			link:       &models.Link{SourceID: testItem1ID, TargetID: testNonexistentID, Type: "depends_on"},
			sourceItem: &models.Item{ID: testItem1ID},
			targetErr:  errors.New("not found"),
			expectErr:  "target item not found",
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			mockRepo, mockItemRepo, service := newLinkServiceWithMocks()
			ctx := context.Background()

			if tc.link.SourceID != "" {
				mockItemRepo.On("GetByID", ctx, tc.link.SourceID).Return(tc.sourceItem, tc.sourceErr)
			}
			if tc.link.TargetID != "" && tc.link.TargetID != tc.link.SourceID && tc.sourceErr == nil {
				mockItemRepo.On("GetByID", ctx, tc.link.TargetID).Return(tc.targetItem, tc.targetErr)
			}

			err := service.CreateLink(ctx, tc.link)
			assert.Error(t, err)
			assert.Contains(t, err.Error(), tc.expectErr)
			mockRepo.AssertNotCalled(t, "Create")
		})
	}
}
