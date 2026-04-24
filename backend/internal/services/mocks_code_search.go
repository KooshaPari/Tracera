package services

import (
	"context"
	"encoding/json"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// MockCodeIndexService for testing
type MockCodeIndexService struct {
	// New API methods
	IndexCodeFunc      func(ctx context.Context, req *IndexCodeRequest) (*IndexCodeResponse, error)
	BatchIndexCodeFunc func(ctx context.Context, req *BatchIndexRequest) (*BatchIndexResponse, error)
	ReindexFunc        func(ctx context.Context, projectID string) error
	GetEntityFunc      func(ctx context.Context, entityID string) (*CodeEntityWithRelations, error)
	ListEntitiesFunc   func(ctx context.Context, projectID string, limit, offset int) ([]*models.CodeEntity, error)
	UpdateEntityFunc   func(ctx context.Context, entityID string, description string, metadata json.RawMessage) (*models.CodeEntity, error)
	DeleteEntityFunc   func(ctx context.Context, entityID string) error
	SearchEntitiesFunc func(ctx context.Context, projectID, query string, limit, offset int) ([]*models.CodeEntity, error)
	GetStatsFunc       func(ctx context.Context, projectID string) (*models.CodeIndexStats, error)

	// Legacy API methods
	IndexCodeEntityFunc       func(ctx context.Context, entity *models.CodeEntity) error
	IndexCodeEntitiesFunc     func(ctx context.Context, entities []*models.CodeEntity) error
	GetCodeEntityFunc         func(ctx context.Context, id string) (*models.CodeEntity, error)
	ListCodeEntitiesFunc      func(ctx context.Context, filter CodeEntityFilter) ([]*models.CodeEntity, error)
	UpdateCodeEntityFunc      func(ctx context.Context, entity *models.CodeEntity) error
	DeleteCodeEntityFunc      func(ctx context.Context, id string) error
	GetCodeEntitiesByTypeFunc func(ctx context.Context, projectID, entityType string) ([]*models.CodeEntity, error)
	GetCodeEntitiesByFileFunc func(ctx context.Context, projectID, filePath string) ([]*models.CodeEntity, error)
	CreateRelationshipFunc    func(ctx context.Context, rel *models.CodeEntityRelationship) error
	GetEntityDependenciesFunc func(ctx context.Context, entityID string) ([]*models.CodeEntityRelationship, error)
	GetEntityDependentsFunc   func(ctx context.Context, entityID string) ([]*models.CodeEntityRelationship, error)
	GetCodeIndexStatsFunc     func(ctx context.Context, projectID string) (*models.CodeIndexStats, error)
}

// IndexCode implements CodeIndexService.IndexCode for testing.
func (m *MockCodeIndexService) IndexCode(ctx context.Context, req *IndexCodeRequest) (*IndexCodeResponse, error) {
	if m.IndexCodeFunc != nil {
		return m.IndexCodeFunc(ctx, req)
	}
	return nil, nil
}

// BatchIndexCode implements CodeIndexService.BatchIndexCode for testing.
func (m *MockCodeIndexService) BatchIndexCode(ctx context.Context, req *BatchIndexRequest) (*BatchIndexResponse, error) {
	if m.BatchIndexCodeFunc != nil {
		return m.BatchIndexCodeFunc(ctx, req)
	}
	return nil, nil
}

// Reindex implements CodeIndexService.Reindex for testing.
func (m *MockCodeIndexService) Reindex(ctx context.Context, projectID string) error {
	if m.ReindexFunc != nil {
		return m.ReindexFunc(ctx, projectID)
	}
	return nil
}

// GetEntity implements CodeIndexService.GetEntity for testing.
func (m *MockCodeIndexService) GetEntity(ctx context.Context, entityID string) (*CodeEntityWithRelations, error) {
	if m.GetEntityFunc != nil {
		return m.GetEntityFunc(ctx, entityID)
	}
	return nil, nil
}

// ListEntities implements CodeIndexService.ListEntities for testing.
func (m *MockCodeIndexService) ListEntities(ctx context.Context, projectID string, limit, offset int) ([]*models.CodeEntity, error) {
	if m.ListEntitiesFunc != nil {
		return m.ListEntitiesFunc(ctx, projectID, limit, offset)
	}
	return nil, nil
}

// UpdateEntity implements CodeIndexService.UpdateEntity for testing.
func (m *MockCodeIndexService) UpdateEntity(
	ctx context.Context, entityID, description string, metadata json.RawMessage,
) (*models.CodeEntity, error) {
	if m.UpdateEntityFunc != nil {
		return m.UpdateEntityFunc(ctx, entityID, description, metadata)
	}
	return nil, nil
}

// DeleteEntity implements CodeIndexService.DeleteEntity for testing.
func (m *MockCodeIndexService) DeleteEntity(ctx context.Context, entityID string) error {
	if m.DeleteEntityFunc != nil {
		return m.DeleteEntityFunc(ctx, entityID)
	}
	return nil
}

// SearchEntities implements CodeIndexService.SearchEntities for testing.
func (m *MockCodeIndexService) SearchEntities(
	ctx context.Context, projectID, query string, limit, offset int,
) ([]*models.CodeEntity, error) {
	if m.SearchEntitiesFunc != nil {
		return m.SearchEntitiesFunc(ctx, projectID, query, limit, offset)
	}
	return nil, nil
}

// GetStats implements CodeIndexService.GetStats for testing.
func (m *MockCodeIndexService) GetStats(ctx context.Context, projectID string) (*models.CodeIndexStats, error) {
	if m.GetStatsFunc != nil {
		return m.GetStatsFunc(ctx, projectID)
	}
	return nil, nil
}

// IndexCodeEntity implements CodeIndexService.IndexCodeEntity for testing.
func (m *MockCodeIndexService) IndexCodeEntity(ctx context.Context, entity *models.CodeEntity) error {
	if m.IndexCodeEntityFunc != nil {
		return m.IndexCodeEntityFunc(ctx, entity)
	}
	return nil
}

// GetCodeEntity implements CodeIndexService.GetCodeEntity for testing.
func (m *MockCodeIndexService) GetCodeEntity(ctx context.Context, id string) (*models.CodeEntity, error) {
	if m.GetCodeEntityFunc != nil {
		return m.GetCodeEntityFunc(ctx, id)
	}
	return nil, nil
}

// ListCodeEntities implements CodeIndexService.ListCodeEntities for testing.
func (m *MockCodeIndexService) ListCodeEntities(ctx context.Context, filter CodeEntityFilter) ([]*models.CodeEntity, error) {
	if m.ListCodeEntitiesFunc != nil {
		return m.ListCodeEntitiesFunc(ctx, filter)
	}
	return nil, nil
}

// UpdateCodeEntity implements CodeIndexService.UpdateCodeEntity for testing.
func (m *MockCodeIndexService) UpdateCodeEntity(ctx context.Context, entity *models.CodeEntity) error {
	if m.UpdateCodeEntityFunc != nil {
		return m.UpdateCodeEntityFunc(ctx, entity)
	}
	return nil
}

// DeleteCodeEntity implements CodeIndexService.DeleteCodeEntity for testing.
func (m *MockCodeIndexService) DeleteCodeEntity(ctx context.Context, id string) error {
	if m.DeleteCodeEntityFunc != nil {
		return m.DeleteCodeEntityFunc(ctx, id)
	}
	return nil
}

// IndexCodeEntities implements CodeIndexService.IndexCodeEntities for testing.
func (m *MockCodeIndexService) IndexCodeEntities(ctx context.Context, entities []*models.CodeEntity) error {
	if m.IndexCodeEntitiesFunc != nil {
		return m.IndexCodeEntitiesFunc(ctx, entities)
	}
	return nil
}

// GetCodeEntitiesByType implements CodeIndexService.GetCodeEntitiesByType for testing.
func (m *MockCodeIndexService) GetCodeEntitiesByType(ctx context.Context, projectID, entityType string) ([]*models.CodeEntity, error) {
	if m.GetCodeEntitiesByTypeFunc != nil {
		return m.GetCodeEntitiesByTypeFunc(ctx, projectID, entityType)
	}
	return nil, nil
}

// GetCodeEntitiesByFile implements CodeIndexService.GetCodeEntitiesByFile for testing.
func (m *MockCodeIndexService) GetCodeEntitiesByFile(ctx context.Context, projectID, filePath string) ([]*models.CodeEntity, error) {
	if m.GetCodeEntitiesByFileFunc != nil {
		return m.GetCodeEntitiesByFileFunc(ctx, projectID, filePath)
	}
	return nil, nil
}

// CreateRelationship implements CodeIndexService.CreateRelationship for testing.
func (m *MockCodeIndexService) CreateRelationship(ctx context.Context, rel *models.CodeEntityRelationship) error {
	if m.CreateRelationshipFunc != nil {
		return m.CreateRelationshipFunc(ctx, rel)
	}
	return nil
}

// GetEntityDependencies implements CodeIndexService.GetEntityDependencies for testing.
func (m *MockCodeIndexService) GetEntityDependencies(ctx context.Context, entityID string) ([]*models.CodeEntityRelationship, error) {
	if m.GetEntityDependenciesFunc != nil {
		return m.GetEntityDependenciesFunc(ctx, entityID)
	}
	return nil, nil
}

// GetEntityDependents implements CodeIndexService.GetEntityDependents for testing.
func (m *MockCodeIndexService) GetEntityDependents(ctx context.Context, entityID string) ([]*models.CodeEntityRelationship, error) {
	if m.GetEntityDependentsFunc != nil {
		return m.GetEntityDependentsFunc(ctx, entityID)
	}
	return nil, nil
}

// GetCodeIndexStats implements CodeIndexService.GetCodeIndexStats for testing.
func (m *MockCodeIndexService) GetCodeIndexStats(ctx context.Context, projectID string) (*models.CodeIndexStats, error) {
	if m.GetCodeIndexStatsFunc != nil {
		return m.GetCodeIndexStatsFunc(ctx, projectID)
	}
	return nil, nil
}

// MockSearchService for testing
type MockSearchService struct {
	SearchItemsFunc    func(ctx context.Context, query string, filters SearchFilters) ([]*models.Item, error)
	SearchProjectsFunc func(ctx context.Context, query string) ([]*models.Project, error)
	IndexItemFunc      func(ctx context.Context, item *models.Item) error
	IndexProjectFunc   func(ctx context.Context, project *models.Project) error
}

// SearchItems implements SearchService.SearchItems for testing.
func (m *MockSearchService) SearchItems(ctx context.Context, query string, filters SearchFilters) ([]*models.Item, error) {
	if m.SearchItemsFunc != nil {
		return m.SearchItemsFunc(ctx, query, filters)
	}
	return nil, nil
}

// SearchProjects implements SearchService.SearchProjects for testing.
func (m *MockSearchService) SearchProjects(ctx context.Context, query string) ([]*models.Project, error) {
	if m.SearchProjectsFunc != nil {
		return m.SearchProjectsFunc(ctx, query)
	}
	return nil, nil
}

// IndexItem implements SearchService.IndexItem for testing.
func (m *MockSearchService) IndexItem(ctx context.Context, item *models.Item) error {
	if m.IndexItemFunc != nil {
		return m.IndexItemFunc(ctx, item)
	}
	return nil
}

// IndexProject implements SearchService.IndexProject for testing.
func (m *MockSearchService) IndexProject(ctx context.Context, project *models.Project) error {
	if m.IndexProjectFunc != nil {
		return m.IndexProjectFunc(ctx, project)
	}
	return nil
}
