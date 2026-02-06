//go:build !integration && !e2e

package services

import (
	"context"
	"errors"
	"testing"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"
)

// LinkServiceTestSuite provides test suite setup for link service tests
type LinkServiceTestSuite struct {
	suite.Suite
	linkRepo *MockLinkRepository
	itemRepo *MockItemRepository
	service  LinkService
	ctx      context.Context
}

func (suite *LinkServiceTestSuite) SetupTest() {
	suite.linkRepo = new(MockLinkRepository)
	suite.itemRepo = new(MockItemRepository)
	suite.ctx = context.Background()
	suite.service = NewLinkService(suite.linkRepo, suite.itemRepo, nil)
}

func (suite *LinkServiceTestSuite) TearDownTest() {
	suite.linkRepo.AssertExpectations(suite.T())
	suite.itemRepo.AssertExpectations(suite.T())
}

func TestLinkServiceSuite(t *testing.T) {
	suite.Run(t, new(LinkServiceTestSuite))
}

func (suite *LinkServiceTestSuite) TestLinkService_Create_Success() {
	sourceItem := &models.Item{
		ID:        testItem1ID,
		ProjectID: testProjectIDValue,
		Title:     "Source Item",
	}
	targetItem := &models.Item{
		ID:        "item-2",
		ProjectID: testProjectIDValue,
		Title:     "Target Item",
	}

	link := &models.Link{
		SourceID: sourceItem.ID,
		TargetID: targetItem.ID,
		Type:     "depends_on",
	}

	suite.itemRepo.On("GetByID", suite.ctx, sourceItem.ID).Return(sourceItem, nil)
	suite.itemRepo.On("GetByID", suite.ctx, targetItem.ID).Return(targetItem, nil)
	suite.linkRepo.On("Create", suite.ctx, link).Return(nil)

	err := suite.service.CreateLink(suite.ctx, link)

	assert.NoError(suite.T(), err)
}

func (suite *LinkServiceTestSuite) TestLinkService_Create_GraphUpdate() {
	// Tests that creating a link properly updates the graph by verifying
	// both source and target items exist before creating the link
	sourceItem := &models.Item{ID: testItem1ID, ProjectID: testProjectIDValue}
	targetItem := &models.Item{ID: "item-2", ProjectID: testProjectIDValue}

	link := &models.Link{
		SourceID: sourceItem.ID,
		TargetID: targetItem.ID,
		Type:     "implements",
	}

	suite.itemRepo.On("GetByID", suite.ctx, sourceItem.ID).Return(sourceItem, nil)
	suite.itemRepo.On("GetByID", suite.ctx, targetItem.ID).Return(targetItem, nil)
	suite.linkRepo.On("Create", suite.ctx, link).Return(nil)

	err := suite.service.CreateLink(suite.ctx, link)

	assert.NoError(suite.T(), err)
	// Verify both items were checked (graph validation)
	suite.itemRepo.AssertCalled(suite.T(), "GetByID", suite.ctx, sourceItem.ID)
	suite.itemRepo.AssertCalled(suite.T(), "GetByID", suite.ctx, targetItem.ID)
}

func (suite *LinkServiceTestSuite) TestLinkService_Get_Success() {
	linkID := "link-123"
	expectedLink := &models.Link{
		ID:       linkID,
		SourceID: testItem1ID,
		TargetID: "item-2",
		Type:     "depends_on",
	}

	suite.linkRepo.On("GetByID", suite.ctx, linkID).Return(expectedLink, nil)

	result, err := suite.service.GetLink(suite.ctx, linkID)

	assert.NoError(suite.T(), err)
	assert.NotNil(suite.T(), result)
	assert.Equal(suite.T(), expectedLink.ID, result.ID)
	assert.Equal(suite.T(), expectedLink.Type, result.Type)
}

func (suite *LinkServiceTestSuite) TestLinkService_Update_Success() {
	link := &models.Link{
		ID:       "link-123",
		SourceID: testItem1ID,
		TargetID: "item-2",
		Type:     "tests",
	}

	suite.linkRepo.On("Update", suite.ctx, link).Return(nil)

	err := suite.service.UpdateLink(suite.ctx, link)

	assert.NoError(suite.T(), err)
}

func (suite *LinkServiceTestSuite) TestLinkService_Delete_GraphSync() {
	// Tests that deleting a link properly maintains graph synchronization
	linkID := "link-123"

	suite.linkRepo.On("Delete", suite.ctx, linkID).Return(nil)

	err := suite.service.DeleteLink(suite.ctx, linkID)

	assert.NoError(suite.T(), err)
	// Verify link was deleted (graph sync)
	suite.linkRepo.AssertCalled(suite.T(), "Delete", suite.ctx, linkID)
}

func (suite *LinkServiceTestSuite) TestLinkService_GetDependencies_Success() {
	itemID := testItem1ID

	dependencies := []*models.Link{
		{ID: "link-1", SourceID: itemID, TargetID: "item-2", Type: "depends_on"},
		{ID: "link-2", SourceID: itemID, TargetID: "item-3", Type: "depends_on"},
	}

	dependents := []*models.Link{
		{ID: "link-3", SourceID: "item-4", TargetID: itemID, Type: "depends_on"},
	}

	relatedItems := map[string]*models.Item{
		"item-2": {ID: "item-2", Title: "Dependency 1"},
		"item-3": {ID: "item-3", Title: "Dependency 2"},
		"item-4": {ID: "item-4", Title: "Dependent 1"},
	}

	suite.linkRepo.On("GetBySourceID", suite.ctx, itemID).Return(dependencies, nil)
	suite.linkRepo.On("GetByTargetID", suite.ctx, itemID).Return(dependents, nil)
	suite.itemRepo.On("GetByID", suite.ctx, "item-2").Return(relatedItems["item-2"], nil)
	suite.itemRepo.On("GetByID", suite.ctx, "item-3").Return(relatedItems["item-3"], nil)
	suite.itemRepo.On("GetByID", suite.ctx, "item-4").Return(relatedItems["item-4"], nil)

	result, err := suite.service.GetItemDependencies(suite.ctx, itemID)

	assert.NoError(suite.T(), err)
	assert.NotNil(suite.T(), result)
	assert.Equal(suite.T(), itemID, result.ItemID)
	assert.Len(suite.T(), result.Dependencies, 2)
	assert.Len(suite.T(), result.Dependents, 1)
	assert.Len(suite.T(), result.Items, 3)
	assert.Equal(suite.T(), "Dependency 1", result.Items["item-2"].Title)
}

func (suite *LinkServiceTestSuite) TestLinkService_GetImpact_Success() {
	// Tests impact analysis by getting all dependents
	itemID := testItem1ID

	dependents := []*models.Link{
		{ID: "link-1", SourceID: "item-2", TargetID: itemID, Type: "depends_on"},
		{ID: "link-2", SourceID: "item-3", TargetID: itemID, Type: "implements"},
	}

	relatedItems := map[string]*models.Item{
		"item-2": {ID: "item-2", Title: "Impacted Item 1"},
		"item-3": {ID: "item-3", Title: "Impacted Item 2"},
	}

	suite.linkRepo.On("GetBySourceID", suite.ctx, itemID).Return([]*models.Link{}, nil)
	suite.linkRepo.On("GetByTargetID", suite.ctx, itemID).Return(dependents, nil)
	suite.itemRepo.On("GetByID", suite.ctx, "item-2").Return(relatedItems["item-2"], nil)
	suite.itemRepo.On("GetByID", suite.ctx, "item-3").Return(relatedItems["item-3"], nil)

	result, err := suite.service.GetItemDependencies(suite.ctx, itemID)

	assert.NoError(suite.T(), err)
	assert.NotNil(suite.T(), result)
	assert.Len(suite.T(), result.Dependents, 2)
	assert.Len(suite.T(), result.Items, 2)
	// Verify impact analysis includes all dependent items
	assert.Contains(suite.T(), result.Items, "item-2")
	assert.Contains(suite.T(), result.Items, "item-3")
}

// Additional unit tests without test suite

func TestLinkService_Create_ValidationError_NoSourceID(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	link := &models.Link{
		SourceID: "", // Empty source
		TargetID: "item-2",
		Type:     "depends_on",
	}

	err := service.CreateLink(context.Background(), link)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "source and target IDs are required")
}

func TestLinkService_Create_ValidationError_NoTargetID(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	link := &models.Link{
		SourceID: testItem1ID,
		TargetID: "", // Empty target
		Type:     "depends_on",
	}

	err := service.CreateLink(context.Background(), link)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "source and target IDs are required")
}

func TestLinkService_Create_ValidationError_NoType(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	link := &models.Link{
		SourceID: testItem1ID,
		TargetID: "item-2",
		Type:     "", // Empty type
	}

	err := service.CreateLink(context.Background(), link)

	assert.Error(t, err)
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

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "source item not found")
	itemRepo.AssertExpectations(t)
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

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "target item not found")
	itemRepo.AssertExpectations(t)
}

func TestLinkService_List_WithFilters(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	sourceID := testItem1ID
	linkType := "depends_on"
	filter := repository.LinkFilter{
		SourceID: &sourceID,
		Type:     &linkType,
		Limit:    10,
	}

	expectedLinks := []*models.Link{
		{ID: "link-1", SourceID: sourceID, TargetID: "item-2", Type: linkType},
		{ID: "link-2", SourceID: sourceID, TargetID: "item-3", Type: linkType},
	}

	linkRepo.On("List", mock.Anything, filter).Return(expectedLinks, nil)

	result, err := service.ListLinks(context.Background(), filter)

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Len(t, result, 2)
	assert.Equal(t, expectedLinks[0].ID, result[0].ID)
	linkRepo.AssertExpectations(t)
}

func TestLinkService_GetLink_NotFound(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	linkRepo.On("GetByID", mock.Anything, "nonexistent").Return(nil, errors.New("link not found"))

	result, err := service.GetLink(context.Background(), "nonexistent")

	assert.Error(t, err)
	assert.Nil(t, result)
	linkRepo.AssertExpectations(t)
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

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "failed to update link")
	linkRepo.AssertExpectations(t)
}

func TestLinkService_Delete_Error(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	linkRepo.On("Delete", mock.Anything, "link-123").Return(errors.New("delete failed"))

	err := service.DeleteLink(context.Background(), "link-123")

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "failed to delete link")
	linkRepo.AssertExpectations(t)
}

func TestLinkService_GetDependencies_EmptyGraph(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	itemID := testItem1ID

	linkRepo.On("GetBySourceID", mock.Anything, itemID).Return([]*models.Link{}, nil)
	linkRepo.On("GetByTargetID", mock.Anything, itemID).Return([]*models.Link{}, nil)

	result, err := service.GetItemDependencies(context.Background(), itemID)

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, itemID, result.ItemID)
	assert.Len(t, result.Dependencies, 0)
	assert.Len(t, result.Dependents, 0)
	assert.Len(t, result.Items, 0)
	linkRepo.AssertExpectations(t)
}

// Edge Case Tests for LinkService

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
	assert.NoError(t, err)
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
	assert.Error(t, err)
}

func TestLinkService_Create_MissingSourceItem(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	link := &models.Link{
		SourceID: "nonexistent",
		TargetID: "item-2",
		Type:     "depends_on",
	}

	itemRepo.On("GetByID", mock.Anything, "nonexistent").Return(nil, errors.New("not found"))

	err := service.CreateLink(context.Background(), link)
	assert.Error(t, err)
}

func TestLinkService_Create_MissingTargetItem(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	link := &models.Link{
		SourceID: testItem1ID,
		TargetID: "nonexistent",
		Type:     "depends_on",
	}

	itemRepo.On("GetByID", mock.Anything, testItem1ID).Return(&models.Item{ID: testItem1ID}, nil)
	itemRepo.On("GetByID", mock.Anything, "nonexistent").Return(nil, errors.New("not found"))

	err := service.CreateLink(context.Background(), link)
	assert.Error(t, err)
}

func TestLinkService_GetLink_NotFoundEdgeCase(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	linkRepo.On("GetByID", mock.Anything, "nonexistent").Return(nil, errors.New("not found"))

	result, err := service.GetLink(context.Background(), "nonexistent")
	assert.Error(t, err)
	assert.Nil(t, result)
}

func TestLinkService_ListLinks_EmptyResultsEdgeCase(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	filter := repository.LinkFilter{Limit: 10}
	linkRepo.On("List", mock.Anything, filter).Return([]*models.Link{}, nil)

	result, err := service.ListLinks(context.Background(), filter)
	assert.NoError(t, err)
	assert.Empty(t, result)
}

func TestLinkService_ListLinks_RepositoryErrorEdgeCase(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	filter := repository.LinkFilter{Limit: 10}
	linkRepo.On("List", mock.Anything, filter).Return(nil, errors.New("database error"))

	result, err := service.ListLinks(context.Background(), filter)
	assert.Error(t, err)
	assert.Nil(t, result)
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
	assert.NoError(t, err)
	assert.NotNil(t, result)
}

func TestLinkService_GetDependencies_SourceError(t *testing.T) {
	linkRepo := new(MockLinkRepository)
	itemRepo := new(MockItemRepository)
	service := NewLinkService(linkRepo, itemRepo, nil)

	itemID := testItem1ID
	linkRepo.On("GetBySourceID", mock.Anything, itemID).Return(nil, errors.New("database error"))

	result, err := service.GetItemDependencies(context.Background(), itemID)
	assert.Error(t, err)
	assert.Nil(t, result)
}
