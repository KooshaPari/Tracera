//go:build !integration && !e2e

package services

import (
	"context"
	"encoding/json"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
	"github.com/stretchr/testify/suite"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// ============================================================================
// Mock Repositories
// ============================================================================

type MockCodeEntityRepository struct {
	mock.Mock
}

func (m *MockCodeEntityRepository) Create(ctx context.Context, entity *models.CodeEntity) error {
	args := m.Called(ctx, entity)
	return args.Error(0)
}

func (m *MockCodeEntityRepository) GetByID(ctx context.Context, id string) (*models.CodeEntity, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*models.CodeEntity)
	return val, args.Error(1)
}

func (m *MockCodeEntityRepository) GetByProjectID(
	ctx context.Context, projectID string, limit, offset int,
) ([]*models.CodeEntity, error) {
	args := m.Called(ctx, projectID, limit, offset)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.CodeEntity)
	return val, args.Error(1)
}

func (m *MockCodeEntityRepository) List(ctx context.Context, filter repository.CodeEntityFilter) ([]*models.CodeEntity, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.CodeEntity)
	return val, args.Error(1)
}

func (m *MockCodeEntityRepository) Update(ctx context.Context, entity *models.CodeEntity) error {
	args := m.Called(ctx, entity)
	return args.Error(0)
}

func (m *MockCodeEntityRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockCodeEntityRepository) DeleteByProjectID(ctx context.Context, projectID string) error {
	args := m.Called(ctx, projectID)
	return args.Error(0)
}

func (m *MockCodeEntityRepository) Search(
	ctx context.Context, projectID, query string, limit, offset int,
) ([]*models.CodeEntity, error) {
	args := m.Called(ctx, projectID, query, limit, offset)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.CodeEntity)
	return val, args.Error(1)
}

func (m *MockCodeEntityRepository) GetByType(ctx context.Context, projectID string, entityType string) ([]*models.CodeEntity, error) {
	args := m.Called(ctx, projectID, entityType)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.CodeEntity)
	return val, args.Error(1)
}

func (m *MockCodeEntityRepository) GetByFilePath(ctx context.Context, projectID, filePath string) ([]*models.CodeEntity, error) {
	args := m.Called(ctx, projectID, filePath)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.CodeEntity)
	return val, args.Error(1)
}

func (m *MockCodeEntityRepository) Count(ctx context.Context, projectID string) (int64, error) {
	args := m.Called(ctx, projectID)
	val, _ := args.Get(0).(int64)
	return val, args.Error(1)
}

func (m *MockCodeEntityRepository) GetStats(ctx context.Context, projectID string) (*models.CodeIndexStats, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*models.CodeIndexStats)
	return val, args.Error(1)
}

func (m *MockCodeEntityRepository) BatchCreate(ctx context.Context, entities []*models.CodeEntity) error {
	args := m.Called(ctx, entities)
	return args.Error(0)
}

func (m *MockCodeEntityRepository) BatchDelete(ctx context.Context, ids []string) error {
	args := m.Called(ctx, ids)
	return args.Error(0)
}

type MockCodeEntityRelationshipRepository struct {
	mock.Mock
}

func (m *MockCodeEntityRelationshipRepository) Create(ctx context.Context, rel *models.CodeEntityRelationship) error {
	args := m.Called(ctx, rel)
	return args.Error(0)
}

func (m *MockCodeEntityRelationshipRepository) GetByID(ctx context.Context, id string) (*models.CodeEntityRelationship, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*models.CodeEntityRelationship)
	return val, args.Error(1)
}

func (m *MockCodeEntityRelationshipRepository) GetBySourceID(
	ctx context.Context, sourceID string,
) ([]*models.CodeEntityRelationship, error) {
	args := m.Called(ctx, sourceID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.CodeEntityRelationship)
	return val, args.Error(1)
}

func (m *MockCodeEntityRelationshipRepository) GetByTargetID(
	ctx context.Context, targetID string,
) ([]*models.CodeEntityRelationship, error) {
	args := m.Called(ctx, targetID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.CodeEntityRelationship)
	return val, args.Error(1)
}

func (m *MockCodeEntityRelationshipRepository) List(
	ctx context.Context, filter repository.CodeEntityRelationshipFilter,
) ([]*models.CodeEntityRelationship, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.CodeEntityRelationship)
	return val, args.Error(1)
}

func (m *MockCodeEntityRelationshipRepository) Update(ctx context.Context, rel *models.CodeEntityRelationship) error {
	args := m.Called(ctx, rel)
	return args.Error(0)
}

func (m *MockCodeEntityRelationshipRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockCodeEntityRelationshipRepository) DeleteByProjectID(ctx context.Context, projectID string) error {
	args := m.Called(ctx, projectID)
	return args.Error(0)
}

func (m *MockCodeEntityRelationshipRepository) GetRelationships(
	ctx context.Context, entityID string,
) ([]*models.CodeEntityRelationship, error) {
	args := m.Called(ctx, entityID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.CodeEntityRelationship)
	return val, args.Error(1)
}

func (m *MockCodeEntityRelationshipRepository) BatchCreate(ctx context.Context, relationships []*models.CodeEntityRelationship) error {
	args := m.Called(ctx, relationships)
	return args.Error(0)
}

type MockCache struct {
	mock.Mock
}

func (m *MockCache) Get(ctx context.Context, key string, dest interface{}) error {
	args := m.Called(ctx, key)
	if args.Error(1) != nil {
		return args.Error(1)
	}

	if args.Get(0) == nil {
		return nil
	}

	// Handle different destination types
	jsonStr := args.String(0)
	if d, ok := dest.(*string); ok {
		*d = jsonStr
		return nil
	}

	// Unmarshal JSON into dest for non-string types
	return json.Unmarshal([]byte(jsonStr), dest)
}

func (m *MockCache) Set(ctx context.Context, key string, value interface{}) error {
	args := m.Called(ctx, key, value)
	return args.Error(0)
}

func (m *MockCache) Delete(ctx context.Context, keys ...string) error {
	args := m.Called(ctx, keys)
	return args.Error(0)
}

func (m *MockCache) InvalidatePattern(ctx context.Context, pattern string) error {
	args := m.Called(ctx, pattern)
	return args.Error(0)
}

func (m *MockCache) Close() error {
	args := m.Called()
	return args.Error(0)
}

// ============================================================================
// Test Suite
// ============================================================================

type CodeIndexServiceTestSuite struct {
	suite.Suite
	entityRepo       *MockCodeEntityRepository
	relationshipRepo *MockCodeEntityRelationshipRepository
	cache            *MockCache
	service          CodeIndexService
}

func (suite *CodeIndexServiceTestSuite) SetupTest() {
	suite.entityRepo = new(MockCodeEntityRepository)
	suite.relationshipRepo = new(MockCodeEntityRelationshipRepository)
	suite.cache = new(MockCache)
	suite.service = NewCodeIndexServiceImpl(suite.entityRepo, suite.relationshipRepo, suite.cache)
}

func TestCodeIndexServiceTestSuite(t *testing.T) {
	suite.Run(t, new(CodeIndexServiceTestSuite))
}

// ============================================================================
// Test: IndexCodeEntity
// ============================================================================

func (suite *CodeIndexServiceTestSuite) TestIndexCodeEntity_Success() {
	entity := &models.CodeEntity{
		ID:         "entity-1",
		ProjectID:  "project-1",
		Name:       "UserService",
		EntityType: "class",
		FilePath:   "src/services/user.go",
		Language:   "go",
		LineNumber: 10,
	}

	suite.entityRepo.On("Create", mock.Anything, entity).Return(nil)
	suite.cache.On("Delete", mock.Anything, mock.Anything).Return(nil)

	err := suite.service.IndexCodeEntity(context.Background(), entity)

	suite.Require().NoError(err)
	suite.entityRepo.AssertExpectations(suite.T())
}

func (suite *CodeIndexServiceTestSuite) TestIndexCodeEntity_ValidationError_MissingID() {
	entity := &models.CodeEntity{
		ProjectID:  "project-1",
		Name:       "UserService",
		EntityType: "class",
		FilePath:   "src/services/user.go",
		Language:   "go",
	}

	err := suite.service.IndexCodeEntity(context.Background(), entity)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "validation failed")
	suite.Contains(err.Error(), "ID is required")
}

func (suite *CodeIndexServiceTestSuite) TestIndexCodeEntity_ValidationError_MissingProjectID() {
	entity := &models.CodeEntity{
		ID:         "entity-1",
		Name:       "UserService",
		EntityType: "class",
		FilePath:   "src/services/user.go",
		Language:   "go",
	}

	err := suite.service.IndexCodeEntity(context.Background(), entity)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "project ID is required")
}

func (suite *CodeIndexServiceTestSuite) TestIndexCodeEntity_RepositoryError() {
	entity := &models.CodeEntity{
		ID:         "entity-1",
		ProjectID:  "project-1",
		Name:       "UserService",
		EntityType: "class",
		FilePath:   "src/services/user.go",
		Language:   "go",
		LineNumber: 10,
	}

	suite.entityRepo.On("Create", mock.Anything, entity).Return(errors.New("database error"))

	err := suite.service.IndexCodeEntity(context.Background(), entity)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "failed to index code entity")
	suite.entityRepo.AssertExpectations(suite.T())
}

// ============================================================================
// Test: GetCodeEntity
// ============================================================================

func (suite *CodeIndexServiceTestSuite) TestGetCodeEntity_Success_CacheMiss() {
	entity := &models.CodeEntity{
		ID:         "entity-1",
		ProjectID:  "project-1",
		Name:       "UserService",
		EntityType: "class",
		FilePath:   "src/services/user.go",
		Language:   "go",
		LineNumber: 10,
	}

	suite.cache.On("Get", mock.Anything, "code_entity:entity-1").Return("", errors.New("cache miss"))
	suite.entityRepo.On("GetByID", mock.Anything, "entity-1").Return(entity, nil)
	suite.cache.On("Set", mock.Anything, mock.Anything, mock.Anything, mock.Anything).Return(nil)

	result, err := suite.service.GetCodeEntity(context.Background(), "entity-1")

	suite.Require().NoError(err)
	suite.Equal(entity.ID, result.ID)
	suite.Equal(entity.Name, result.Name)
	suite.entityRepo.AssertExpectations(suite.T())
}

func (suite *CodeIndexServiceTestSuite) TestGetCodeEntity_Success_CacheHit() {
	entity := &models.CodeEntity{
		ID:         "entity-1",
		ProjectID:  "project-1",
		Name:       "UserService",
		EntityType: "class",
		FilePath:   "src/services/user.go",
		Language:   "go",
		LineNumber: 10,
	}

	entityJSON, err := json.Marshal(entity)
	suite.Require().NoError(err)
	suite.cache.On("Get", mock.Anything, "code_entity:entity-1").Return(string(entityJSON), nil)

	result, err := suite.service.GetCodeEntity(context.Background(), "entity-1")

	suite.Require().NoError(err)
	suite.Equal(entity.ID, result.ID)
	suite.Equal(entity.Name, result.Name)
	// Repository should not be called on cache hit
	suite.entityRepo.AssertNotCalled(suite.T(), "GetByID", mock.Anything, mock.Anything)
}

func (suite *CodeIndexServiceTestSuite) TestGetCodeEntity_EmptyID() {
	result, err := suite.service.GetCodeEntity(context.Background(), "")

	suite.Require().Error(err)
	suite.Nil(result)
	suite.Contains(err.Error(), "entity ID is required")
}

func (suite *CodeIndexServiceTestSuite) TestGetCodeEntity_NotFound() {
	suite.cache.On("Get", mock.Anything, "code_entity:nonexistent").Return("", errors.New("cache miss"))
	suite.entityRepo.On("GetByID", mock.Anything, "nonexistent").Return(nil, errors.New("not found"))

	result, err := suite.service.GetCodeEntity(context.Background(), "nonexistent")

	suite.Require().Error(err)
	suite.Nil(result)
	suite.Contains(err.Error(), "failed to get code entity")
}

// ============================================================================
// Test: ListCodeEntities
// ============================================================================

func (suite *CodeIndexServiceTestSuite) TestListCodeEntities_Success() {
	entities := []*models.CodeEntity{
		{ID: "entity-1", ProjectID: "project-1", Name: "UserService", EntityType: "class", FilePath: "user.go", Language: "go"},
		{ID: "entity-2", ProjectID: "project-1", Name: "CreateUser", EntityType: "function", FilePath: "user.go", Language: "go"},
	}

	filter := CodeEntityFilter{
		ProjectID: "project-1",
		Limit:     50,
		Offset:    0,
	}

	repoFilter := repository.CodeEntityFilter{
		ProjectID: "project-1",
		Limit:     50,
		Offset:    0,
	}

	suite.cache.On("Get", mock.Anything, "code_entities:project:project-1:page:0").Return("", errors.New("cache miss"))
	suite.entityRepo.On("List", mock.Anything, repoFilter).Return(entities, nil)
	suite.cache.On("Set", mock.Anything, mock.Anything, mock.Anything, mock.Anything).Return(nil)

	result, err := suite.service.ListCodeEntities(context.Background(), filter)

	suite.Require().NoError(err)
	suite.Len(result, 2)
	suite.Equal("entity-1", result[0].ID)
	suite.Equal("entity-2", result[1].ID)
}

func (suite *CodeIndexServiceTestSuite) TestListCodeEntities_MissingProjectID() {
	filter := CodeEntityFilter{
		Limit:  50,
		Offset: 0,
	}

	result, err := suite.service.ListCodeEntities(context.Background(), filter)

	suite.Require().Error(err)
	suite.Nil(result)
	suite.Contains(err.Error(), "project ID is required")
}

// ============================================================================
// Test: UpdateCodeEntity
// ============================================================================

func (suite *CodeIndexServiceTestSuite) TestUpdateCodeEntity_Success() {
	entity := &models.CodeEntity{
		ID:         "entity-1",
		ProjectID:  "project-1",
		Name:       "UserService",
		EntityType: "class",
		FilePath:   "src/services/user.go",
		Language:   "go",
		LineNumber: 10,
	}

	suite.entityRepo.On("Update", mock.Anything, entity).Return(nil)
	suite.cache.On("Delete", mock.Anything, mock.Anything).Return(nil)

	err := suite.service.UpdateCodeEntity(context.Background(), entity)

	suite.Require().NoError(err)
	suite.entityRepo.AssertExpectations(suite.T())
}

func (suite *CodeIndexServiceTestSuite) TestUpdateCodeEntity_ValidationError() {
	entity := &models.CodeEntity{
		ID:        "entity-1",
		ProjectID: "project-1",
		// Missing required fields
	}

	err := suite.service.UpdateCodeEntity(context.Background(), entity)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "validation failed")
}

// ============================================================================
// Test: DeleteCodeEntity
// ============================================================================

func (suite *CodeIndexServiceTestSuite) TestDeleteCodeEntity_Success() {
	entity := &models.CodeEntity{
		ID:         "entity-1",
		ProjectID:  "project-1",
		Name:       "UserService",
		EntityType: "class",
		FilePath:   "src/services/user.go",
		Language:   "go",
	}

	relationships := []*models.CodeEntityRelationship{
		{ID: "rel-1", SourceID: "entity-1", TargetID: "entity-2", RelationType: "calls"},
	}

	suite.entityRepo.On("GetByID", mock.Anything, "entity-1").Return(entity, nil)
	suite.entityRepo.On("Delete", mock.Anything, "entity-1").Return(nil)
	suite.relationshipRepo.On("GetRelationships", mock.Anything, "entity-1").Return(relationships, nil)
	suite.relationshipRepo.On("Delete", mock.Anything, "rel-1").Return(nil)
	suite.cache.On("Delete", mock.Anything, mock.Anything).Return(nil)

	err := suite.service.DeleteCodeEntity(context.Background(), "entity-1")

	suite.Require().NoError(err)
	suite.entityRepo.AssertExpectations(suite.T())
	suite.relationshipRepo.AssertExpectations(suite.T())
}

func (suite *CodeIndexServiceTestSuite) TestDeleteCodeEntity_EmptyID() {
	err := suite.service.DeleteCodeEntity(context.Background(), "")

	suite.Require().Error(err)
	suite.Contains(err.Error(), "entity ID is required")
}

// ============================================================================
// Test: IndexCodeEntities (Batch)
// ============================================================================

func (suite *CodeIndexServiceTestSuite) TestIndexCodeEntities_Success() {
	entities := []*models.CodeEntity{
		{ID: "entity-1", ProjectID: "project-1", Name: "Service1", EntityType: "class", FilePath: "s1.go", Language: "go"},
		{ID: "entity-2", ProjectID: "project-1", Name: "Service2", EntityType: "class", FilePath: "s2.go", Language: "go"},
	}

	suite.entityRepo.On("BatchCreate", mock.Anything, entities).Return(nil)
	suite.cache.On("Delete", mock.Anything, mock.Anything).Return(nil)

	err := suite.service.IndexCodeEntities(context.Background(), entities)

	suite.Require().NoError(err)
	suite.entityRepo.AssertExpectations(suite.T())
}

func (suite *CodeIndexServiceTestSuite) TestIndexCodeEntities_EmptyList() {
	err := suite.service.IndexCodeEntities(context.Background(), []*models.CodeEntity{})

	suite.Require().Error(err)
	suite.Contains(err.Error(), "entities list cannot be empty")
}

func (suite *CodeIndexServiceTestSuite) TestIndexCodeEntities_ValidationError() {
	entities := []*models.CodeEntity{
		{ID: "entity-1", ProjectID: "project-1", Name: "Service1", EntityType: "class", FilePath: "s1.go", Language: "go"},
		{ID: "entity-2", ProjectID: "project-1", Name: "Service2"}, // Missing required fields
	}

	err := suite.service.IndexCodeEntities(context.Background(), entities)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "validation failed for entity at index 1")
}

// ============================================================================
// Test: SearchCodeEntities
// ============================================================================

func (suite *CodeIndexServiceTestSuite) TestSearchCodeEntities_Success() {
	entities := []*models.CodeEntity{
		{ID: "entity-1", ProjectID: "project-1", Name: "UserService", EntityType: "class", FilePath: "user.go", Language: "go"},
	}

	suite.entityRepo.On("Search", mock.Anything, "project-1", "User", 10, 0).Return(entities, nil)

	result, err := suite.service.SearchEntities(context.Background(), "project-1", "User", 10, 0)

	suite.Require().NoError(err)
	suite.Len(result, 1)
	suite.Equal("UserService", result[0].Name)
}

func (suite *CodeIndexServiceTestSuite) TestSearchCodeEntities_MissingProjectID() {
	result, err := suite.service.SearchEntities(context.Background(), "", "User", 10, 0)

	suite.Require().Error(err)
	suite.Nil(result)
	suite.Contains(err.Error(), "project ID is required")
}

func (suite *CodeIndexServiceTestSuite) TestSearchCodeEntities_EmptyQuery() {
	result, err := suite.service.SearchEntities(context.Background(), "project-1", "", 10, 0)

	suite.Require().Error(err)
	suite.Nil(result)
	suite.Contains(err.Error(), "search query is required")
}

// ============================================================================
// Test: GetCodeEntitiesByType
// ============================================================================

func (suite *CodeIndexServiceTestSuite) TestGetCodeEntitiesByType_Success() {
	entities := []*models.CodeEntity{
		{ID: "entity-1", ProjectID: "project-1", Name: "Service1", EntityType: "class", FilePath: "s1.go", Language: "go"},
		{ID: "entity-2", ProjectID: "project-1", Name: "Service2", EntityType: "class", FilePath: "s2.go", Language: "go"},
	}

	suite.cache.On("Get", mock.Anything, "code_entities:project:project-1:type:class").Return("", errors.New("cache miss"))
	suite.entityRepo.On("GetByType", mock.Anything, "project-1", "class").Return(entities, nil)
	suite.cache.On("Set", mock.Anything, mock.Anything, mock.Anything, mock.Anything).Return(nil)

	result, err := suite.service.GetCodeEntitiesByType(context.Background(), "project-1", "class")

	suite.Require().NoError(err)
	suite.Len(result, 2)
}

func (suite *CodeIndexServiceTestSuite) TestGetCodeEntitiesByType_MissingEntityType() {
	result, err := suite.service.GetCodeEntitiesByType(context.Background(), "project-1", "")

	suite.Require().Error(err)
	suite.Nil(result)
	suite.Contains(err.Error(), "entity type is required")
}

// ============================================================================
// Test: GetCodeEntitiesByFile
// ============================================================================

func (suite *CodeIndexServiceTestSuite) TestGetCodeEntitiesByFile_Success() {
	entities := []*models.CodeEntity{
		{ID: "entity-1", ProjectID: "project-1", Name: "Service1", EntityType: "class", FilePath: "user.go", Language: "go"},
	}

	suite.cache.On("Get", mock.Anything, "code_entities:project:project-1:file:user.go").Return("", errors.New("cache miss"))
	suite.entityRepo.On("GetByFilePath", mock.Anything, "project-1", "user.go").Return(entities, nil)
	suite.cache.On("Set", mock.Anything, mock.Anything, mock.Anything, mock.Anything).Return(nil)

	result, err := suite.service.GetCodeEntitiesByFile(context.Background(), "project-1", "user.go")

	suite.Require().NoError(err)
	suite.Len(result, 1)
}

func (suite *CodeIndexServiceTestSuite) TestGetCodeEntitiesByFile_MissingFilePath() {
	result, err := suite.service.GetCodeEntitiesByFile(context.Background(), "project-1", "")

	suite.Require().Error(err)
	suite.Nil(result)
	suite.Contains(err.Error(), "file path is required")
}

// ============================================================================
// Test: CreateRelationship
// ============================================================================

func (suite *CodeIndexServiceTestSuite) TestCreateRelationship_Success() {
	relationship := &models.CodeEntityRelationship{
		ID:           "rel-1",
		ProjectID:    "project-1",
		SourceID:     "entity-1",
		TargetID:     "entity-2",
		RelationType: "calls",
	}

	sourceEntity := &models.CodeEntity{
		ID: "entity-1", ProjectID: "project-1", Name: "Service1",
		EntityType: "class", FilePath: "s1.go", Language: "go",
	}
	targetEntity := &models.CodeEntity{
		ID: "entity-2", ProjectID: "project-1", Name: "Service2",
		EntityType: "class", FilePath: "s2.go", Language: "go",
	}

	suite.entityRepo.On("GetByID", mock.Anything, "entity-1").Return(sourceEntity, nil)
	suite.entityRepo.On("GetByID", mock.Anything, "entity-2").Return(targetEntity, nil)
	suite.relationshipRepo.On("Create", mock.Anything, relationship).Return(nil)
	suite.cache.On("Delete", mock.Anything, mock.Anything).Return(nil)

	err := suite.service.CreateRelationship(context.Background(), relationship)

	suite.Require().NoError(err)
	suite.relationshipRepo.AssertExpectations(suite.T())
}

func (suite *CodeIndexServiceTestSuite) TestCreateRelationship_ValidationError_SameSourceTarget() {
	relationship := &models.CodeEntityRelationship{
		ID:           "rel-1",
		ProjectID:    "project-1",
		SourceID:     "entity-1",
		TargetID:     "entity-1", // Same as source
		RelationType: "calls",
	}

	err := suite.service.CreateRelationship(context.Background(), relationship)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "source and target cannot be the same entity")
}

func (suite *CodeIndexServiceTestSuite) TestCreateRelationship_SourceNotFound() {
	relationship := &models.CodeEntityRelationship{
		ID:           "rel-1",
		ProjectID:    "project-1",
		SourceID:     "entity-1",
		TargetID:     "entity-2",
		RelationType: "calls",
	}

	suite.entityRepo.On("GetByID", mock.Anything, "entity-1").Return(nil, errors.New("not found"))

	err := suite.service.CreateRelationship(context.Background(), relationship)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "source entity not found")
}

// ============================================================================
// Test: GetEntityDependencies
// ============================================================================

func (suite *CodeIndexServiceTestSuite) TestGetEntityDependencies_Success() {
	relationships := []*models.CodeEntityRelationship{
		{ID: "rel-1", SourceID: "entity-1", TargetID: "entity-2", RelationType: "calls"},
		{ID: "rel-2", SourceID: "entity-1", TargetID: "entity-3", RelationType: "uses"},
	}

	suite.cache.On("Get", mock.Anything, "dependencies:entity-1").Return("", errors.New("cache miss"))
	suite.relationshipRepo.On("GetBySourceID", mock.Anything, "entity-1").Return(relationships, nil)
	suite.cache.On("Set", mock.Anything, mock.Anything, mock.Anything, mock.Anything).Return(nil)

	result, err := suite.service.GetEntityDependencies(context.Background(), "entity-1")

	suite.Require().NoError(err)
	suite.Len(result, 2)
}

func (suite *CodeIndexServiceTestSuite) TestGetEntityDependencies_EmptyID() {
	result, err := suite.service.GetEntityDependencies(context.Background(), "")

	suite.Require().Error(err)
	suite.Nil(result)
	suite.Contains(err.Error(), "entity ID is required")
}

// ============================================================================
// Test: GetEntityDependents
// ============================================================================

func (suite *CodeIndexServiceTestSuite) TestGetEntityDependents_Success() {
	relationships := []*models.CodeEntityRelationship{
		{ID: "rel-1", SourceID: "entity-2", TargetID: "entity-1", RelationType: "calls"},
	}

	suite.relationshipRepo.On("GetByTargetID", mock.Anything, "entity-1").Return(relationships, nil)

	result, err := suite.service.GetEntityDependents(context.Background(), "entity-1")

	suite.Require().NoError(err)
	suite.Len(result, 1)
}

// ============================================================================
// Test: GetCodeIndexStats
// ============================================================================

func (suite *CodeIndexServiceTestSuite) TestGetCodeIndexStats_Success() {
	stats := &models.CodeIndexStats{
		ProjectID:          "project-1",
		TotalEntities:      100,
		EntitiesByType:     map[string]int64{"class": 50, "function": 50},
		EntitiesByLanguage: map[string]int64{"go": 80, "python": 20},
		TotalRelations:     150,
	}

	suite.cache.On("Get", mock.Anything, "code_stats:project-1").Return("", errors.New("cache miss"))
	suite.entityRepo.On("GetStats", mock.Anything, "project-1").Return(stats, nil)
	suite.cache.On("Set", mock.Anything, mock.Anything, mock.Anything, mock.Anything).Return(nil)

	result, err := suite.service.GetStats(context.Background(), "project-1")

	suite.Require().NoError(err)
	suite.Equal(int64(100), result.TotalEntities)
	suite.Equal(int64(150), result.TotalRelations)
}

func (suite *CodeIndexServiceTestSuite) TestGetCodeIndexStats_MissingProjectID() {
	result, err := suite.service.GetStats(context.Background(), "")

	suite.Require().Error(err)
	suite.Nil(result)
	suite.Contains(err.Error(), "project ID is required")
}

// ============================================================================
// Unit Tests (Non-Suite)
// ============================================================================

func TestNewCodeIndexServiceImpl_NilEntityRepo(t *testing.T) {
	assert.Panics(t, func() {
		NewCodeIndexServiceImpl(nil, new(MockCodeEntityRelationshipRepository), new(MockCache))
	})
}

func TestNewCodeIndexServiceImpl_NilRelationshipRepo(t *testing.T) {
	assert.Panics(t, func() {
		NewCodeIndexServiceImpl(new(MockCodeEntityRepository), nil, new(MockCache))
	})
}

func TestValidateCodeEntity_InvalidLineNumbers(t *testing.T) {
	cache := new(MockCache)
	entityRepo := new(MockCodeEntityRepository)
	relationshipRepo := new(MockCodeEntityRelationshipRepository)
	service, ok := NewCodeIndexServiceImpl(entityRepo, relationshipRepo, cache).(*CodeIndexServiceImpl)
	require.True(t, ok)

	entity := &models.CodeEntity{
		ID:            "entity-1",
		ProjectID:     "project-1",
		Name:          "TestService",
		EntityType:    "class",
		FilePath:      "test.go",
		Language:      "go",
		LineNumber:    100,
		EndLineNumber: 50, // End before start
	}

	err := service.validateCodeEntity(entity)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "end line number must be greater than or equal to line number")
}

func TestValidateCodeEntity_NegativeLineNumber(t *testing.T) {
	cache := new(MockCache)
	entityRepo := new(MockCodeEntityRepository)
	relationshipRepo := new(MockCodeEntityRelationshipRepository)
	service, ok := NewCodeIndexServiceImpl(entityRepo, relationshipRepo, cache).(*CodeIndexServiceImpl)
	require.True(t, ok)

	entity := &models.CodeEntity{
		ID:         "entity-1",
		ProjectID:  "project-1",
		Name:       "TestService",
		EntityType: "class",
		FilePath:   "test.go",
		Language:   "go",
		LineNumber: -5,
	}

	err := service.validateCodeEntity(entity)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "line number must be non-negative")
}

func TestValidateRelationship_MissingFields(t *testing.T) {
	cache := new(MockCache)
	entityRepo := new(MockCodeEntityRepository)
	relationshipRepo := new(MockCodeEntityRelationshipRepository)
	service, ok := NewCodeIndexServiceImpl(entityRepo, relationshipRepo, cache).(*CodeIndexServiceImpl)
	require.True(t, ok)

	testCases := []struct {
		name         string
		relationship *models.CodeEntityRelationship
		expectedErr  string
	}{
		{
			name:         "Missing ID",
			relationship: &models.CodeEntityRelationship{ProjectID: "p1", SourceID: "s1", TargetID: "t1", RelationType: "calls"},
			expectedErr:  "relationship ID is required",
		},
		{
			name:         "Missing ProjectID",
			relationship: &models.CodeEntityRelationship{ID: "r1", SourceID: "s1", TargetID: "t1", RelationType: "calls"},
			expectedErr:  "project ID is required",
		},
		{
			name:         "Missing SourceID",
			relationship: &models.CodeEntityRelationship{ID: "r1", ProjectID: "p1", TargetID: "t1", RelationType: "calls"},
			expectedErr:  "source ID is required",
		},
		{
			name:         "Missing TargetID",
			relationship: &models.CodeEntityRelationship{ID: "r1", ProjectID: "p1", SourceID: "s1", RelationType: "calls"},
			expectedErr:  "target ID is required",
		},
		{
			name:         "Missing RelationType",
			relationship: &models.CodeEntityRelationship{ID: "r1", ProjectID: "p1", SourceID: "s1", TargetID: "t1"},
			expectedErr:  "relation type is required",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			err := service.validateRelationship(tc.relationship)
			require.Error(t, err)
			assert.Contains(t, err.Error(), tc.expectedErr)
		})
	}
}
