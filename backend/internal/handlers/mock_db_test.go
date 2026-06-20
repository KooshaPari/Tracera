//go:build !integration && !e2e
// +build !integration,!e2e

package handlers

import (
	"context"
	"errors"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"

	"github.com/kooshapari/tracertm-backend/internal/db"
)

// MockQueries is a test implementation of db.Querier interface
// It provides in-memory storage for testing CRUD operations
type MockQueries struct {
	mu                     sync.RWMutex
	projects               map[string]db.Project
	items                  map[string]db.GetItemRow
	links                  map[string]db.Link
	agents                 map[string]db.Agent
	nextID                 int
	CreateProjectFunc      func(_ context.Context, arg db.CreateProjectParams) (db.Project, error)
	GetProjectFunc         func(_ context.Context, id pgtype.UUID) (db.Project, error)
	ListProjectsFunc       func(_ context.Context, arg db.ListProjectsParams) ([]db.Project, error)
	UpdateProjectFunc      func(_ context.Context, arg db.UpdateProjectParams) (db.Project, error)
	DeleteProjectFunc      func(_ context.Context, id pgtype.UUID) error
	CreateItemFunc         func(_ context.Context, arg db.CreateItemParams) (db.CreateItemRow, error)
	GetItemFunc            func(_ context.Context, id pgtype.UUID) (db.GetItemRow, error)
	ListItemsByProjectFunc func(_ context.Context, arg db.ListItemsByProjectParams) ([]db.ListItemsByProjectRow, error)
	UpdateItemFunc         func(_ context.Context, arg db.UpdateItemParams) (db.UpdateItemRow, error)
	DeleteItemFunc         func(_ context.Context, id pgtype.UUID) error
	CreateLinkFunc         func(_ context.Context, arg db.CreateLinkParams) (db.Link, error)
	GetLinkFunc            func(_ context.Context, id pgtype.UUID) (db.Link, error)
	ListLinksBySourceFunc  func(_ context.Context, sourceID pgtype.UUID) ([]db.Link, error)
	UpdateLinkFunc         func(_ context.Context, arg db.UpdateLinkParams) (db.Link, error)
	DeleteLinkFunc         func(_ context.Context, id pgtype.UUID) error
	GetAncestorsFunc       func(_ context.Context, targetID pgtype.UUID) ([]db.GetAncestorsRow, error)
	GetDescendantsFunc     func(_ context.Context, sourceID pgtype.UUID) ([]db.GetDescendantsRow, error)
}

// timeToTimestamp converts time.Time to pgtype.Timestamp
func timeToTimestamp(t time.Time) pgtype.Timestamp {
	var ts pgtype.Timestamp
	if err := ts.Scan(t); err != nil {
		panic(err)
	}
	return ts
}

// NewMockQueries creates a new MockQueries instance with initialized storage
func NewMockQueries() *MockQueries {
	return &MockQueries{
		projects: make(map[string]db.Project),
		items:    make(map[string]db.GetItemRow),
		links:    make(map[string]db.Link),
		agents:   make(map[string]db.Agent),
		nextID:   1,
	}
}

// CreateProject creates a project in mock storage
func (m *MockQueries) CreateProject(ctx context.Context, arg db.CreateProjectParams) (db.Project, error) {
	if m.CreateProjectFunc != nil {
		return m.CreateProjectFunc(ctx, arg)
	}

	m.mu.Lock()
	defer m.mu.Unlock()

	projectID := pgtype.UUID{}
	if err := projectID.Scan(uuid.New().String()); err != nil {
		return db.Project{}, err
	}

	now := time.Now()
	nowTS := pgtype.Timestamp{}
	if err := nowTS.Scan(now); err != nil {
		return db.Project{}, err
	}

	project := db.Project{
		ID:          projectID,
		Name:        arg.Name,
		Description: arg.Description,
		Metadata:    arg.Metadata,
		CreatedAt:   nowTS,
		UpdatedAt:   nowTS,
		DeletedAt:   pgtype.Timestamp{Valid: false},
	}

	m.projects[projectID.String()] = project
	return project, nil
}

// GetProject retrieves a project from mock storage
func (m *MockQueries) GetProject(ctx context.Context, id pgtype.UUID) (db.Project, error) {
	if m.GetProjectFunc != nil {
		return m.GetProjectFunc(ctx, id)
	}

	m.mu.RLock()
	defer m.mu.RUnlock()

	if project, ok := m.projects[id.String()]; ok {
		return project, nil
	}
	return db.Project{}, errors.New("project not found")
}

// ListProjects lists all projects with pagination
func (m *MockQueries) ListProjects(ctx context.Context, arg db.ListProjectsParams) ([]db.Project, error) {
	if m.ListProjectsFunc != nil {
		return m.ListProjectsFunc(ctx, arg)
	}

	m.mu.RLock()
	defer m.mu.RUnlock()

	var projects []db.Project
	for _, p := range m.projects {
		projects = append(projects, p)
	}

	// Apply pagination
	if int(arg.Offset) >= len(projects) {
		return []db.Project{}, nil
	}

	end := int(arg.Offset) + int(arg.Limit)
	if end > len(projects) {
		end = len(projects)
	}

	return projects[arg.Offset:end], nil
}

// UpdateProject updates a project in mock storage
func (m *MockQueries) UpdateProject(ctx context.Context, arg db.UpdateProjectParams) (db.Project, error) {
	if m.UpdateProjectFunc != nil {
		return m.UpdateProjectFunc(ctx, arg)
	}

	m.mu.Lock()
	defer m.mu.Unlock()

	project, ok := m.projects[arg.ID.String()]
	if !ok {
		return db.Project{}, errors.New("project not found")
	}

	project.Name = arg.Name
	project.Description = arg.Description
	project.Metadata = arg.Metadata
	project.UpdatedAt = timeToTimestamp(time.Now())

	m.projects[arg.ID.String()] = project
	return project, nil
}

// DeleteProject deletes a project from mock storage
func (m *MockQueries) DeleteProject(ctx context.Context, id pgtype.UUID) error {
	if m.DeleteProjectFunc != nil {
		return m.DeleteProjectFunc(ctx, id)
	}

	m.mu.Lock()
	defer m.mu.Unlock()

	if _, ok := m.projects[id.String()]; !ok {
		return errors.New("project not found")
	}

	delete(m.projects, id.String())
	return nil
}

// CreateItem creates an item in mock storage
func (m *MockQueries) CreateItem(ctx context.Context, arg db.CreateItemParams) (db.CreateItemRow, error) {
	if m.CreateItemFunc != nil {
		return m.CreateItemFunc(ctx, arg)
	}

	m.mu.Lock()
	defer m.mu.Unlock()

	itemID := pgtype.UUID{}
	if err := itemID.Scan(uuid.New().String()); err != nil {
		return db.CreateItemRow{}, err
	}

	now := time.Now()
	row := db.CreateItemRow{
		ID:          itemID,
		ProjectID:   arg.ProjectID,
		Title:       arg.Title,
		Description: arg.Description,
		Type:        arg.Type,
		Status:      arg.Status,
		Priority:    arg.Priority,
		Metadata:    arg.Metadata,
		CreatedAt:   timeToTimestamp(now),
		UpdatedAt:   timeToTimestamp(now),
		DeletedAt:   pgtype.Timestamp{Valid: false},
	}

	// Store as GetItemRow
	itemRow := db.GetItemRow{
		ID:          itemID,
		ProjectID:   arg.ProjectID,
		Title:       arg.Title,
		Description: arg.Description,
		Type:        arg.Type,
		Status:      arg.Status,
		Priority:    arg.Priority,
		Metadata:    arg.Metadata,
		CreatedAt:   timeToTimestamp(now),
		UpdatedAt:   timeToTimestamp(now),
		DeletedAt:   pgtype.Timestamp{Valid: false},
	}
	m.items[itemID.String()] = itemRow

	return row, nil
}

// GetItem retrieves an item from mock storage
func (m *MockQueries) GetItem(ctx context.Context, id pgtype.UUID) (db.GetItemRow, error) {
	if m.GetItemFunc != nil {
		return m.GetItemFunc(ctx, id)
	}

	m.mu.RLock()
	defer m.mu.RUnlock()

	if item, ok := m.items[id.String()]; ok {
		return item, nil
	}
	return db.GetItemRow{}, errors.New("item not found")
}

// ListItemsByProject lists items for a project with pagination
func (m *MockQueries) ListItemsByProject(ctx context.Context, arg db.ListItemsByProjectParams) ([]db.ListItemsByProjectRow, error) {
	if m.ListItemsByProjectFunc != nil {
		return m.ListItemsByProjectFunc(ctx, arg)
	}

	m.mu.RLock()
	defer m.mu.RUnlock()

	var items []db.ListItemsByProjectRow
	for _, item := range m.items {
		if item.ProjectID == arg.ProjectID {
			row := db.ListItemsByProjectRow(item)
			items = append(items, row)
		}
	}

	// Apply pagination
	if int(arg.Offset) >= len(items) {
		return []db.ListItemsByProjectRow{}, nil
	}

	end := int(arg.Offset) + int(arg.Limit)
	if end > len(items) {
		end = len(items)
	}

	return items[arg.Offset:end], nil
}

// UpdateItem updates an item in mock storage
func (m *MockQueries) UpdateItem(_ context.Context, arg db.UpdateItemParams) (db.UpdateItemRow, error) {
	m.mu.Lock()
	defer m.mu.Unlock()

	item, ok := m.items[arg.ID.String()]
	if !ok {
		return db.UpdateItemRow{}, errors.New("item not found")
	}

	item.Title = arg.Title
	item.Description = arg.Description
	item.Type = arg.Type
	item.Status = arg.Status
	item.Priority = arg.Priority
	item.Metadata = arg.Metadata
	item.UpdatedAt = timeToTimestamp(time.Now())

	m.items[arg.ID.String()] = item

	return db.UpdateItemRow(item), nil
}

// DeleteItem deletes an item from mock storage
func (m *MockQueries) DeleteItem(ctx context.Context, id pgtype.UUID) error {
	if m.DeleteItemFunc != nil {
		return m.DeleteItemFunc(ctx, id)
	}

	m.mu.Lock()
	defer m.mu.Unlock()

	if _, ok := m.items[id.String()]; !ok {
		return errors.New("item not found")
	}

	delete(m.items, id.String())
	return nil
}

// CreateLink creates a link in mock storage
func (m *MockQueries) CreateLink(ctx context.Context, arg db.CreateLinkParams) (db.Link, error) {
	if m.CreateLinkFunc != nil {
		return m.CreateLinkFunc(ctx, arg)
	}

	m.mu.Lock()
	defer m.mu.Unlock()

	linkID := pgtype.UUID{}
	if err := linkID.Scan(uuid.New().String()); err != nil {
		return db.Link{}, err
	}

	now := time.Now()
	link := db.Link{
		ID:        linkID,
		SourceID:  arg.SourceID,
		TargetID:  arg.TargetID,
		Type:      arg.Type,
		Metadata:  arg.Metadata,
		CreatedAt: timeToTimestamp(now),
		UpdatedAt: timeToTimestamp(now),
		DeletedAt: pgtype.Timestamp{Valid: false},
	}

	m.links[linkID.String()] = link
	return link, nil
}

// GetLink retrieves a link from mock storage
func (m *MockQueries) GetLink(ctx context.Context, id pgtype.UUID) (db.Link, error) {
	if m.GetLinkFunc != nil {
		return m.GetLinkFunc(ctx, id)
	}

	m.mu.RLock()
	defer m.mu.RUnlock()

	if link, ok := m.links[id.String()]; ok {
		return link, nil
	}
	return db.Link{}, errors.New("link not found")
}

// ListLinksBySource lists links by source ID
func (m *MockQueries) ListLinksBySource(ctx context.Context, sourceID pgtype.UUID) ([]db.Link, error) {
	if m.ListLinksBySourceFunc != nil {
		return m.ListLinksBySourceFunc(ctx, sourceID)
	}

	m.mu.RLock()
	defer m.mu.RUnlock()

	var links []db.Link
	for _, link := range m.links {
		if link.SourceID == sourceID {
			links = append(links, link)
		}
	}
	return links, nil
}

// UpdateLink updates a link in mock storage
func (m *MockQueries) UpdateLink(_ context.Context, arg db.UpdateLinkParams) (db.Link, error) {
	m.mu.Lock()
	defer m.mu.Unlock()

	link, ok := m.links[arg.ID.String()]
	if !ok {
		return db.Link{}, errors.New("link not found")
	}

	link.Type = arg.Type
	link.Metadata = arg.Metadata
	link.UpdatedAt = timeToTimestamp(time.Now())

	m.links[arg.ID.String()] = link
	return link, nil
}

// DeleteLink deletes a link from mock storage
func (m *MockQueries) DeleteLink(ctx context.Context, id pgtype.UUID) error {
	if m.DeleteLinkFunc != nil {
		return m.DeleteLinkFunc(ctx, id)
	}

	m.mu.Lock()
	defer m.mu.Unlock()

	if _, ok := m.links[id.String()]; !ok {
		return errors.New("link not found")
	}

	delete(m.links, id.String())
	return nil
}

// GetAncestors retrieves ancestor items
func (m *MockQueries) GetAncestors(ctx context.Context, targetID pgtype.UUID) ([]db.GetAncestorsRow, error) {
	if m.GetAncestorsFunc != nil {
		return m.GetAncestorsFunc(ctx, targetID)
	}

	m.mu.RLock()
	defer m.mu.RUnlock()

	var ancestors []db.GetAncestorsRow
	// Find all links pointing to targetID
	for _, link := range m.links {
		if link.TargetID == targetID {
			ancestor := db.GetAncestorsRow{
				ItemID:   link.SourceID,
				LinkType: link.Type,
				Depth:    1,
			}
			ancestors = append(ancestors, ancestor)
		}
	}
	return ancestors, nil
}

// GetDescendants retrieves descendant items
func (m *MockQueries) GetDescendants(ctx context.Context, sourceID pgtype.UUID) ([]db.GetDescendantsRow, error) {
	if m.GetDescendantsFunc != nil {
		return m.GetDescendantsFunc(ctx, sourceID)
	}

	m.mu.RLock()
	defer m.mu.RUnlock()

	var descendants []db.GetDescendantsRow
	// Find all links originating from sourceID
	for _, link := range m.links {
		if link.SourceID == sourceID {
			descendant := db.GetDescendantsRow{
				ItemID:   link.TargetID,
				LinkType: link.Type,
				Depth:    1,
			}
			descendants = append(descendants, descendant)
		}
	}
	return descendants, nil
}

// Stub implementations for methods not used in handlers
func (m *MockQueries) CreateAgent(_ context.Context, _ db.CreateAgentParams) (db.Agent, error) {
	return db.Agent{}, errors.New("not implemented")
}

func (m *MockQueries) DeleteAgent(_ context.Context, _ pgtype.UUID) error {
	return errors.New("not implemented")
}

func (m *MockQueries) GetAgent(_ context.Context, _ pgtype.UUID) (db.Agent, error) {
	return db.Agent{}, errors.New("not implemented")
}

func (m *MockQueries) ListAgentsByProject(_ context.Context, _ pgtype.UUID) ([]db.Agent, error) {
	return []db.Agent{}, errors.New("not implemented")
}

func (m *MockQueries) UpdateAgent(_ context.Context, _ db.UpdateAgentParams) (db.Agent, error) {
	return db.Agent{}, errors.New("not implemented")
}

func (m *MockQueries) GetLinkBySourceAndTarget(_ context.Context, _ db.GetLinkBySourceAndTargetParams) (db.Link, error) {
	return db.Link{}, errors.New("not implemented")
}

func (m *MockQueries) ListItemsByIDs(_ context.Context, _ []pgtype.UUID) ([]db.ListItemsByIDsRow, error) {
	return []db.ListItemsByIDsRow{}, errors.New("not implemented")
}

func (m *MockQueries) ListItemsByProjectAndType(
	_ context.Context, _ db.ListItemsByProjectAndTypeParams,
) ([]db.ListItemsByProjectAndTypeRow, error) {
	return []db.ListItemsByProjectAndTypeRow{}, errors.New("not implemented")
}

func (m *MockQueries) ListItemsByProjectIDs(_ context.Context, _ pgtype.UUID) ([]db.ListItemsByProjectIDsRow, error) {
	return []db.ListItemsByProjectIDsRow{}, errors.New("not implemented")
}

func (m *MockQueries) ListLinksBetweenItems(_ context.Context, _ []pgtype.UUID) ([]db.Link, error) {
	return []db.Link{}, errors.New("not implemented")
}

func (m *MockQueries) ListLinksBySourceIDs(_ context.Context, _ []pgtype.UUID) ([]db.Link, error) {
	return []db.Link{}, errors.New("not implemented")
}

func (m *MockQueries) ListLinksByTarget(_ context.Context, _ pgtype.UUID) ([]db.Link, error) {
	return []db.Link{}, errors.New("not implemented")
}

func (m *MockQueries) ListLinksByTargetIDs(_ context.Context, _ []pgtype.UUID) ([]db.Link, error) {
	return []db.Link{}, errors.New("not implemented")
}

func (m *MockQueries) SearchItems(_ context.Context, _ db.SearchItemsParams) ([]db.SearchItemsRow, error) {
	return []db.SearchItemsRow{}, errors.New("not implemented")
}

func (m *MockQueries) SearchItemsByEmbedding(_ context.Context, _ db.SearchItemsByEmbeddingParams) ([]db.SearchItemsByEmbeddingRow, error) {
	return []db.SearchItemsByEmbeddingRow{}, errors.New("not implemented")
}

func (m *MockQueries) SearchItemsByType(_ context.Context, _ db.SearchItemsByTypeParams) ([]db.SearchItemsByTypeRow, error) {
	return []db.SearchItemsByTypeRow{}, errors.New("not implemented")
}

func (m *MockQueries) GetImpactAnalysis(_ context.Context, _ pgtype.UUID) ([]db.GetImpactAnalysisRow, error) {
	return []db.GetImpactAnalysisRow{}, errors.New("not implemented")
}

func (m *MockQueries) GetOrphanItems(_ context.Context, _ pgtype.UUID) ([]db.GetOrphanItemsRow, error) {
	return []db.GetOrphanItemsRow{}, errors.New("not implemented")
}

// MockRealtimeBroadcaster methods removed - see test_helpers.go for the actual implementation
