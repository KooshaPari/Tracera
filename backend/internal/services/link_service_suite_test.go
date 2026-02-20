//go:build !integration && !e2e

package services

import (
	"testing"

	"github.com/stretchr/testify/suite"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

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

	suite.Require().NoError(err)
}

func (suite *LinkServiceTestSuite) TestLinkService_Create_GraphUpdate() {
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

	suite.Require().NoError(err)
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

	suite.Require().NoError(err)
	suite.NotNil(result)
	suite.Equal(expectedLink.ID, result.ID)
	suite.Equal(expectedLink.Type, result.Type)
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

	suite.Require().NoError(err)
}

func (suite *LinkServiceTestSuite) TestLinkService_Delete_GraphSync() {
	linkID := "link-123"

	suite.linkRepo.On("Delete", suite.ctx, linkID).Return(nil)

	err := suite.service.DeleteLink(suite.ctx, linkID)

	suite.Require().NoError(err)
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

	suite.Require().NoError(err)
	suite.NotNil(result)
	suite.Equal(itemID, result.ItemID)
	suite.Len(result.Dependencies, 2)
	suite.Len(result.Dependents, 1)
	suite.Len(result.Items, 3)
	suite.Equal("Dependency 1", result.Items["item-2"].Title)
}

func (suite *LinkServiceTestSuite) TestLinkService_GetImpact_Success() {
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

	suite.Require().NoError(err)
	suite.NotNil(result)
	suite.Len(result.Dependents, 2)
	suite.Len(result.Items, 2)
	suite.Contains(result.Items, "item-2")
	suite.Contains(result.Items, "item-3")
}

func (suite *LinkServiceTestSuite) TestLinkService_List_WithFilters() {
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

	suite.linkRepo.On("List", suite.ctx, filter).Return(expectedLinks, nil)

	result, err := suite.service.ListLinks(suite.ctx, filter)

	suite.Require().NoError(err)
	suite.NotNil(result)
	suite.Len(result, 2)
	suite.Equal(expectedLinks[0].ID, result[0].ID)
}
