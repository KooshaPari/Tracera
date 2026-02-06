package services

import (
	"context"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// ============================================================================
// MOCK SERVICES FOR TESTING
// ============================================================================

// MockItemService for testing handlers and other services
//
//nolint:dupl
type MockItemService struct {
	OnCreateItem   func(ctx context.Context, item *models.Item) error
	OnCreateBatch  func(ctx context.Context, items []*models.Item) error
	OnGetItem      func(ctx context.Context, id string) (*models.Item, error)
	OnGetWithLinks func(ctx context.Context, id string) (*ItemWithLinks, error)
	OnListItems    func(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error)
	OnCount        func(ctx context.Context, filter repository.ItemFilter) (int64, error)
	OnUpdateItem   func(ctx context.Context, item *models.Item) error
	OnUpdateStatus func(ctx context.Context, id, status string) error
	OnUpdateBatch  func(ctx context.Context, items []*models.Item) error
	OnDeleteItem   func(ctx context.Context, id string) error
	OnDeleteBatch  func(ctx context.Context, ids []string) error
	OnValidate     func(ctx context.Context, item *models.Item) error
	OnItemExists   func(ctx context.Context, id string) (bool, error)
	OnGetItemStats func(ctx context.Context, projectID string) (*ItemStats, error)
}

// CreateItem implements ItemService.CreateItem for testing.
func (m *MockItemService) CreateItem(ctx context.Context, item *models.Item) error {
	if m.OnCreateItem != nil {
		return m.OnCreateItem(ctx, item)
	}
	return nil
}

// CreateBatch implements ItemService.CreateBatch for testing.
func (m *MockItemService) CreateBatch(ctx context.Context, items []*models.Item) error {
	if m.OnCreateBatch != nil {
		return m.OnCreateBatch(ctx, items)
	}
	return nil
}

// GetItem implements ItemService.GetItem for testing.
func (m *MockItemService) GetItem(ctx context.Context, id string) (*models.Item, error) {
	if m.OnGetItem != nil {
		return m.OnGetItem(ctx, id)
	}
	return nil, nil
}

// GetWithLinks implements ItemService.GetWithLinks for testing.
func (m *MockItemService) GetWithLinks(ctx context.Context, id string) (*ItemWithLinks, error) {
	if m.OnGetWithLinks != nil {
		return m.OnGetWithLinks(ctx, id)
	}
	return nil, nil
}

// ListItems implements ItemService.ListItems for testing.
func (m *MockItemService) ListItems(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error) {
	if m.OnListItems != nil {
		return m.OnListItems(ctx, filter)
	}
	return nil, nil
}

// Count implements ItemService.Count for testing.
func (m *MockItemService) Count(ctx context.Context, filter repository.ItemFilter) (int64, error) {
	if m.OnCount != nil {
		return m.OnCount(ctx, filter)
	}
	return 0, nil
}

// UpdateItem implements ItemService.UpdateItem for testing.
func (m *MockItemService) UpdateItem(ctx context.Context, item *models.Item) error {
	if m.OnUpdateItem != nil {
		return m.OnUpdateItem(ctx, item)
	}
	return nil
}

// UpdateStatus implements ItemService.UpdateStatus for testing.
func (m *MockItemService) UpdateStatus(ctx context.Context, id, status string) error {
	if m.OnUpdateStatus != nil {
		return m.OnUpdateStatus(ctx, id, status)
	}
	return nil
}

// UpdateBatch implements ItemService.UpdateBatch for testing.
func (m *MockItemService) UpdateBatch(ctx context.Context, items []*models.Item) error {
	if m.OnUpdateBatch != nil {
		return m.OnUpdateBatch(ctx, items)
	}
	return nil
}

// DeleteItem implements ItemService.DeleteItem for testing.
func (m *MockItemService) DeleteItem(ctx context.Context, id string) error {
	if m.OnDeleteItem != nil {
		return m.OnDeleteItem(ctx, id)
	}
	return nil
}

// DeleteBatch implements ItemService.DeleteBatch for testing.
func (m *MockItemService) DeleteBatch(ctx context.Context, ids []string) error {
	if m.OnDeleteBatch != nil {
		return m.OnDeleteBatch(ctx, ids)
	}
	return nil
}

// Validate implements ItemService.Validate for testing.
func (m *MockItemService) Validate(ctx context.Context, item *models.Item) error {
	if m.OnValidate != nil {
		return m.OnValidate(ctx, item)
	}
	return nil
}

// ItemExists implements ItemService.ItemExists for testing.
func (m *MockItemService) ItemExists(ctx context.Context, id string) (bool, error) {
	if m.OnItemExists != nil {
		return m.OnItemExists(ctx, id)
	}
	return true, nil
}

// GetItemStats implements ItemService.GetItemStats for testing.
func (m *MockItemService) GetItemStats(ctx context.Context, projectID string) (*ItemStats, error) {
	if m.OnGetItemStats != nil {
		return m.OnGetItemStats(ctx, projectID)
	}
	return nil, nil
}

// MockLinkService for testing
type MockLinkService struct {
	CreateLinkFunc          func(ctx context.Context, link *models.Link) error
	GetLinkFunc             func(ctx context.Context, id string) (*models.Link, error)
	ListLinksFunc           func(ctx context.Context, filter repository.LinkFilter) ([]*models.Link, error)
	UpdateLinkFunc          func(ctx context.Context, link *models.Link) error
	DeleteLinkFunc          func(ctx context.Context, id string) error
	GetItemDependenciesFunc func(ctx context.Context, itemID string) (*DependencyGraph, error)
}

// CreateLink implements LinkService.CreateLink for testing.
func (m *MockLinkService) CreateLink(ctx context.Context, link *models.Link) error {
	if m.CreateLinkFunc != nil {
		return m.CreateLinkFunc(ctx, link)
	}
	return nil
}

// GetLink implements LinkService.GetLink for testing.
func (m *MockLinkService) GetLink(ctx context.Context, id string) (*models.Link, error) {
	if m.GetLinkFunc != nil {
		return m.GetLinkFunc(ctx, id)
	}
	return nil, nil
}

// ListLinks implements LinkService.ListLinks for testing.
func (m *MockLinkService) ListLinks(ctx context.Context, filter repository.LinkFilter) ([]*models.Link, error) {
	if m.ListLinksFunc != nil {
		return m.ListLinksFunc(ctx, filter)
	}
	return nil, nil
}

// UpdateLink implements LinkService.UpdateLink for testing.
func (m *MockLinkService) UpdateLink(ctx context.Context, link *models.Link) error {
	if m.UpdateLinkFunc != nil {
		return m.UpdateLinkFunc(ctx, link)
	}
	return nil
}

// DeleteLink implements LinkService.DeleteLink for testing.
func (m *MockLinkService) DeleteLink(ctx context.Context, id string) error {
	if m.DeleteLinkFunc != nil {
		return m.DeleteLinkFunc(ctx, id)
	}
	return nil
}

// GetItemDependencies implements LinkService.GetItemDependencies for testing.
func (m *MockLinkService) GetItemDependencies(ctx context.Context, itemID string) (*DependencyGraph, error) {
	if m.GetItemDependenciesFunc != nil {
		return m.GetItemDependenciesFunc(ctx, itemID)
	}
	return nil, nil
}

// MockProjectService for testing
//
//nolint:dupl
type MockProjectService struct {
	OnCreateProject          func(ctx context.Context, project *models.Project) error
	OnCreateProjectWithItems func(ctx context.Context, project *models.Project, items []*models.Item) error
	OnGetProject             func(ctx context.Context, id string) (*models.Project, error)
	OnListProjects           func(ctx context.Context) ([]*models.Project, error)
	OnUpdateProject          func(ctx context.Context, project *models.Project) error
	OnUpdateProjectAndItems  func(ctx context.Context, project *models.Project, items []*models.Item) error
	OnDeleteProject          func(ctx context.Context, id string) error
	OnDeleteProjectWithItems func(ctx context.Context, projectID string) error
	OnGetProjectStats        func(ctx context.Context, projectID string) (*ProjectStats, error)
}

// CreateProject implements ProjectService.CreateProject for testing.
func (m *MockProjectService) CreateProject(ctx context.Context, project *models.Project) error {
	if m.OnCreateProject != nil {
		return m.OnCreateProject(ctx, project)
	}
	return nil
}

// CreateProjectWithItems implements ProjectService.CreateProjectWithItems for testing.
func (m *MockProjectService) CreateProjectWithItems(ctx context.Context, project *models.Project, items []*models.Item) error {
	if m.OnCreateProjectWithItems != nil {
		return m.OnCreateProjectWithItems(ctx, project, items)
	}
	return nil
}

// UpdateProjectAndItems implements ProjectService.UpdateProjectAndItems for testing.
func (m *MockProjectService) UpdateProjectAndItems(ctx context.Context, project *models.Project, items []*models.Item) error {
	if m.OnUpdateProjectAndItems != nil {
		return m.OnUpdateProjectAndItems(ctx, project, items)
	}
	return nil
}

// DeleteProjectWithItems implements ProjectService.DeleteProjectWithItems for testing.
func (m *MockProjectService) DeleteProjectWithItems(ctx context.Context, projectID string) error {
	if m.OnDeleteProjectWithItems != nil {
		return m.OnDeleteProjectWithItems(ctx, projectID)
	}
	return nil
}

// GetProject implements ProjectService.GetProject for testing.
func (m *MockProjectService) GetProject(ctx context.Context, id string) (*models.Project, error) {
	if m.OnGetProject != nil {
		return m.OnGetProject(ctx, id)
	}
	return nil, nil
}

// ListProjects implements ProjectService.ListProjects for testing.
func (m *MockProjectService) ListProjects(ctx context.Context) ([]*models.Project, error) {
	if m.OnListProjects != nil {
		return m.OnListProjects(ctx)
	}
	return nil, nil
}

// UpdateProject implements ProjectService.UpdateProject for testing.
func (m *MockProjectService) UpdateProject(ctx context.Context, project *models.Project) error {
	if m.OnUpdateProject != nil {
		return m.OnUpdateProject(ctx, project)
	}
	return nil
}

// DeleteProject implements ProjectService.DeleteProject for testing.
func (m *MockProjectService) DeleteProject(ctx context.Context, id string) error {
	if m.OnDeleteProject != nil {
		return m.OnDeleteProject(ctx, id)
	}
	return nil
}

// GetProjectStats implements ProjectService.GetProjectStats for testing.
func (m *MockProjectService) GetProjectStats(ctx context.Context, projectID string) (*ProjectStats, error) {
	if m.OnGetProjectStats != nil {
		return m.OnGetProjectStats(ctx, projectID)
	}
	return nil, nil
}

// MockAgentService for testing
type MockAgentService struct {
	CreateAgentFunc       func(ctx context.Context, agent *models.Agent) error
	GetAgentFunc          func(ctx context.Context, id string) (*models.Agent, error)
	ListAgentsFunc        func(ctx context.Context) ([]*models.Agent, error)
	UpdateAgentFunc       func(ctx context.Context, agent *models.Agent) error
	UpdateAgentStatusFunc func(ctx context.Context, id, status string) error
	DeleteAgentFunc       func(ctx context.Context, id string) error
	NotifyAgentEventFunc  func(ctx context.Context, event *AgentEvent) error
}

// CreateAgent implements AgentService.CreateAgent for testing.
func (m *MockAgentService) CreateAgent(ctx context.Context, agent *models.Agent) error {
	if m.CreateAgentFunc != nil {
		return m.CreateAgentFunc(ctx, agent)
	}
	return nil
}

// GetAgent implements AgentService.GetAgent for testing.
func (m *MockAgentService) GetAgent(ctx context.Context, id string) (*models.Agent, error) {
	if m.GetAgentFunc != nil {
		return m.GetAgentFunc(ctx, id)
	}
	return nil, nil
}

// ListAgents implements AgentService.ListAgents for testing.
func (m *MockAgentService) ListAgents(ctx context.Context) ([]*models.Agent, error) {
	if m.ListAgentsFunc != nil {
		return m.ListAgentsFunc(ctx)
	}
	return nil, nil
}

// UpdateAgent implements AgentService.UpdateAgent for testing.
func (m *MockAgentService) UpdateAgent(ctx context.Context, agent *models.Agent) error {
	if m.UpdateAgentFunc != nil {
		return m.UpdateAgentFunc(ctx, agent)
	}
	return nil
}

// UpdateAgentStatus implements AgentService.UpdateAgentStatus for testing.
func (m *MockAgentService) UpdateAgentStatus(ctx context.Context, id, status string) error {
	if m.UpdateAgentStatusFunc != nil {
		return m.UpdateAgentStatusFunc(ctx, id, status)
	}
	return nil
}

// DeleteAgent implements AgentService.DeleteAgent for testing.
func (m *MockAgentService) DeleteAgent(ctx context.Context, id string) error {
	if m.DeleteAgentFunc != nil {
		return m.DeleteAgentFunc(ctx, id)
	}
	return nil
}

// NotifyAgentEvent implements AgentService.NotifyAgentEvent for testing.
func (m *MockAgentService) NotifyAgentEvent(ctx context.Context, event *AgentEvent) error {
	if m.NotifyAgentEventFunc != nil {
		return m.NotifyAgentEventFunc(ctx, event)
	}
	return nil
}

// MockCodeIndexService for testing
type MockCodeIndexService struct {
	IndexCodeEntityFunc  func(ctx context.Context, entity *models.CodeEntity) error
	GetCodeEntityFunc    func(ctx context.Context, id string) (*models.CodeEntity, error)
	ListCodeEntitiesFunc func(ctx context.Context, filter CodeEntityFilter) ([]*models.CodeEntity, error)
	UpdateCodeEntityFunc func(ctx context.Context, entity *models.CodeEntity) error
	DeleteCodeEntityFunc func(ctx context.Context, id string) error
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

// MockTemporalService for testing
type MockTemporalService struct {
	GetItemVersionFunc   func(ctx context.Context, itemID string, version int) (*models.Item, error)
	ListItemVersionsFunc func(ctx context.Context, itemID string) ([]*VersionInfo, error)
	GetItemAtTimeFunc    func(ctx context.Context, itemID string, timestamp time.Time) (*models.Item, error)
}

// GetItemVersion implements TemporalService.GetItemVersion for testing.
func (m *MockTemporalService) GetItemVersion(ctx context.Context, itemID string, version int) (*models.Item, error) {
	if m.GetItemVersionFunc != nil {
		return m.GetItemVersionFunc(ctx, itemID, version)
	}
	return nil, nil
}

// ListItemVersions implements TemporalService.ListItemVersions for testing.
func (m *MockTemporalService) ListItemVersions(ctx context.Context, itemID string) ([]*VersionInfo, error) {
	if m.ListItemVersionsFunc != nil {
		return m.ListItemVersionsFunc(ctx, itemID)
	}
	return nil, nil
}

// GetItemAtTime implements TemporalService.GetItemAtTime for testing.
func (m *MockTemporalService) GetItemAtTime(ctx context.Context, itemID string, timestamp time.Time) (*models.Item, error) {
	if m.GetItemAtTimeFunc != nil {
		return m.GetItemAtTimeFunc(ctx, itemID, timestamp)
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

// MockGraphAnalysisService for testing
type MockGraphAnalysisService struct {
	AnalyzeItemDependenciesFunc  func(ctx context.Context, itemID string) (*DependencyAnalysis, error)
	GetItemImpactAnalysisFunc    func(ctx context.Context, itemID string) (*ImpactAnalysis, error)
	VisualizeDependencyGraphFunc func(ctx context.Context, itemID string) (string, error)
}

// AnalyzeItemDependencies implements GraphAnalysisService.AnalyzeItemDependencies for testing.
func (m *MockGraphAnalysisService) AnalyzeItemDependencies(ctx context.Context, itemID string) (*DependencyAnalysis, error) {
	if m.AnalyzeItemDependenciesFunc != nil {
		return m.AnalyzeItemDependenciesFunc(ctx, itemID)
	}
	return nil, nil
}

// GetItemImpactAnalysis implements GraphAnalysisService.GetItemImpactAnalysis for testing.
func (m *MockGraphAnalysisService) GetItemImpactAnalysis(ctx context.Context, itemID string) (*ImpactAnalysis, error) {
	if m.GetItemImpactAnalysisFunc != nil {
		return m.GetItemImpactAnalysisFunc(ctx, itemID)
	}
	return nil, nil
}

// VisualizeDependencyGraph implements GraphAnalysisService.VisualizeDependencyGraph for testing.
func (m *MockGraphAnalysisService) VisualizeDependencyGraph(ctx context.Context, itemID string) (string, error) {
	if m.VisualizeDependencyGraphFunc != nil {
		return m.VisualizeDependencyGraphFunc(ctx, itemID)
	}
	return "", nil
}

// MockCacheService for testing
type MockCacheService struct {
	GetFunc               func(ctx context.Context, key string) (string, error)
	SetFunc               func(ctx context.Context, key string, value string, ttl time.Duration) error
	DeleteFunc            func(ctx context.Context, key string) error
	ExpireFunc            func(ctx context.Context, key string, ttl time.Duration) error
	InvalidatePatternFunc func(ctx context.Context, pattern string) error
	GetMultiFunc          func(ctx context.Context, keys []string) (map[string]string, error)
	SetMultiFunc          func(ctx context.Context, items map[string]string, ttl time.Duration) error
	ExistsFunc            func(ctx context.Context, key string) (bool, error)
}

// Get implements CacheService.Get for testing.
func (m *MockCacheService) Get(ctx context.Context, key string) (string, error) {
	if m.GetFunc != nil {
		return m.GetFunc(ctx, key)
	}
	return "", nil
}

// Set implements CacheService.Set for testing.
func (m *MockCacheService) Set(ctx context.Context, key string, value string, ttl time.Duration) error {
	if m.SetFunc != nil {
		return m.SetFunc(ctx, key, value, ttl)
	}
	return nil
}

// Delete implements CacheService.Delete for testing.
func (m *MockCacheService) Delete(ctx context.Context, key string) error {
	if m.DeleteFunc != nil {
		return m.DeleteFunc(ctx, key)
	}
	return nil
}

// Expire implements CacheService.Expire for testing.
func (m *MockCacheService) Expire(ctx context.Context, key string, ttl time.Duration) error {
	if m.ExpireFunc != nil {
		return m.ExpireFunc(ctx, key, ttl)
	}
	return nil
}

// InvalidatePattern implements CacheService.InvalidatePattern for testing.
func (m *MockCacheService) InvalidatePattern(ctx context.Context, pattern string) error {
	if m.InvalidatePatternFunc != nil {
		return m.InvalidatePatternFunc(ctx, pattern)
	}
	return nil
}

// GetMulti implements CacheService.GetMulti for testing.
func (m *MockCacheService) GetMulti(ctx context.Context, keys []string) (map[string]string, error) {
	if m.GetMultiFunc != nil {
		return m.GetMultiFunc(ctx, keys)
	}
	return nil, nil
}

// SetMulti implements CacheService.SetMulti for testing.
func (m *MockCacheService) SetMulti(ctx context.Context, items map[string]string, ttl time.Duration) error {
	if m.SetMultiFunc != nil {
		return m.SetMultiFunc(ctx, items, ttl)
	}
	return nil
}

// Exists implements CacheService.Exists for testing.
func (m *MockCacheService) Exists(ctx context.Context, key string) (bool, error) {
	if m.ExistsFunc != nil {
		return m.ExistsFunc(ctx, key)
	}
	return false, nil
}

// MockEventService for testing
type MockEventService struct {
	PublishItemEventFunc    func(ctx context.Context, event *ItemEvent) error
	PublishLinkEventFunc    func(ctx context.Context, event *LinkEvent) error
	PublishProjectEventFunc func(ctx context.Context, event *ProjectEvent) error
	PublishAgentEventFunc   func(ctx context.Context, event *AgentEventType) error
}

// PublishItemEvent implements EventService.PublishItemEvent for testing.
func (m *MockEventService) PublishItemEvent(ctx context.Context, event *ItemEvent) error {
	if m.PublishItemEventFunc != nil {
		return m.PublishItemEventFunc(ctx, event)
	}
	return nil
}

// PublishLinkEvent implements EventService.PublishLinkEvent for testing.
func (m *MockEventService) PublishLinkEvent(ctx context.Context, event *LinkEvent) error {
	if m.PublishLinkEventFunc != nil {
		return m.PublishLinkEventFunc(ctx, event)
	}
	return nil
}

// PublishProjectEvent implements EventService.PublishProjectEvent for testing.
func (m *MockEventService) PublishProjectEvent(ctx context.Context, event *ProjectEvent) error {
	if m.PublishProjectEventFunc != nil {
		return m.PublishProjectEventFunc(ctx, event)
	}
	return nil
}

// PublishAgentEvent implements EventService.PublishAgentEvent for testing.
func (m *MockEventService) PublishAgentEvent(ctx context.Context, event *AgentEventType) error {
	if m.PublishAgentEventFunc != nil {
		return m.PublishAgentEventFunc(ctx, event)
	}
	return nil
}

// SubscribeToItemEvents implements EventService.SubscribeToItemEvents for testing.
func (m *MockEventService) SubscribeToItemEvents(_ context.Context, _ ItemEventHandler) error {
	return nil
}

// SubscribeToLinkEvents implements EventService.SubscribeToLinkEvents for testing.
func (m *MockEventService) SubscribeToLinkEvents(_ context.Context, _ LinkEventHandler) error {
	return nil
}

// SubscribeToProjectEvents implements EventService.SubscribeToProjectEvents for testing.
func (m *MockEventService) SubscribeToProjectEvents(_ context.Context, _ ProjectEventHandler) error {
	return nil
}

// SubscribeToAgentEvents implements EventService.SubscribeToAgentEvents for testing.
func (m *MockEventService) SubscribeToAgentEvents(_ context.Context, _ AgentEventHandler) error {
	return nil
}
