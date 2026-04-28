// Package fixtures provides test data creation utilities for backend testing.
package fixtures

import (
	"context"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/kooshapari/tracertm-backend/internal/agents"
	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/events"
	"github.com/kooshapari/tracertm-backend/internal/search"
)

// Fixtures provides test data creation utilities
type Fixtures struct {
	pool    *pgxpool.Pool
	queries *db.Queries
}

// New creates a new fixtures instance
func New(pool *pgxpool.Pool) *Fixtures {
	return &Fixtures{
		pool:    pool,
		queries: db.New(pool),
	}
}

// CreateProject creates a test project
func (f *Fixtures) CreateProject(name string) (db.Project, error) {
	return f.queries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        name,
		Description: pgtype.Text{String: "Test project: " + name, Valid: true},
	})
}

// CreateItem creates a test item
func (f *Fixtures) CreateItem(projectID pgtype.UUID, title, itemType, status string) (db.Item, error) {
	row, err := f.queries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   projectID,
		Title:       title,
		Description: pgtype.Text{String: "Test item: " + title, Valid: true},
		Type:        itemType,
		Status:      status,
		Priority:    pgtype.Int4{Int32: 2, Valid: true},
	})
	if err != nil {
		return db.Item{}, err
	}
	return db.Item{
		ID:          row.ID,
		ProjectID:   row.ProjectID,
		Title:       row.Title,
		Description: row.Description,
		Type:        row.Type,
		Status:      row.Status,
		Priority:    row.Priority,
		Metadata:    row.Metadata,
	}, nil
}

// CreateLink creates a test link between items
func (f *Fixtures) CreateLink(_, sourceID, targetID pgtype.UUID, linkType string) (db.Link, error) {
	return f.queries.CreateLink(context.Background(), db.CreateLinkParams{
		SourceID: sourceID,
		TargetID: targetID,
		Type:     linkType,
	})
}

// CreateItemChain creates a chain of linked items
func (f *Fixtures) CreateItemChain(projectID pgtype.UUID, count int, prefix string) ([]db.Item, error) {
	items := make([]db.Item, count)
	var err error

	for i := 0; i < count; i++ {
		items[i], err = f.CreateItem(projectID, prefix+"-"+string(rune('A'+i)), "task", "open")
		if err != nil {
			return nil, err
		}

		if i > 0 {
			_, err = f.CreateLink(projectID, items[i-1].ID, items[i].ID, "depends_on")
			if err != nil {
				return nil, err
			}
		}
	}

	return items, nil
}

// CreateItemTree creates a tree of items
func (f *Fixtures) CreateItemTree(projectID pgtype.UUID, depth, branchFactor int) ([]db.Item, error) {
	items := make([]db.Item, 0)

	var createLevel func(parentID *pgtype.UUID, currentDepth int) error
	createLevel = func(parentID *pgtype.UUID, currentDepth int) error {
		if currentDepth >= depth {
			return nil
		}

		for i := 0; i < branchFactor; i++ {
			item, err := f.CreateItem(
				projectID,
				"Item-D"+string(rune('0'+currentDepth))+"-B"+string(rune('0'+i)),
				"task",
				"open",
			)
			if err != nil {
				return err
			}

			items = append(items, item)

			if parentID != nil {
				_, err = f.CreateLink(projectID, *parentID, item.ID, "parent_child")
				if err != nil {
					return err
				}
			}

			err = createLevel(&item.ID, currentDepth+1)
			if err != nil {
				return err
			}
		}

		return nil
	}

	err := createLevel(nil, 0)
	return items, err
}

// CreateEvent creates a test event
func (f *Fixtures) CreateEvent(projectID, entityID string, entityType events.EntityType, eventType events.EventType) *events.Event {
	return events.NewEvent(projectID, entityID, entityType, eventType, map[string]interface{}{
		"test":      true,
		"timestamp": time.Now().Unix(),
	})
}

// CreateEventSequence creates a sequence of events for an entity
func (f *Fixtures) CreateEventSequence(projectID, entityID string, count int) []*events.Event {
	eventSequence := make([]*events.Event, count)
	eventTypes := []events.EventType{
		events.EventTypeCreated,
		events.EventTypeUpdated,
		events.EventTypeItemStatusChanged,
		events.EventTypeItemPriorityChanged,
	}

	for i := 0; i < count; i++ {
		eventType := eventTypes[i%len(eventTypes)]
		eventSequence[i] = f.CreateEvent(projectID, entityID, events.EntityTypeItem, eventType)
		time.Sleep(1 * time.Millisecond) // Ensure distinct timestamps
	}

	return eventSequence
}

// CreateSnapshot creates a test snapshot
func (f *Fixtures) CreateSnapshot(projectID, entityID string, version int64) *events.Snapshot {
	return events.NewSnapshot(projectID, entityID, events.EntityTypeItem, version, map[string]interface{}{
		"title":   "Snapshot state",
		"version": version,
		"data":    map[string]interface{}{"key": "value"},
	})
}

// CreateAgent creates a test agent
func (f *Fixtures) CreateAgent(name, projectID string, capabilities []string) *agents.RegisteredAgent {
	caps := make([]agents.AgentCapability, len(capabilities))
	for i, cap := range capabilities {
		caps[i] = agents.AgentCapability{
			Name:    cap,
			Version: "1.0.0",
			Tags:    []string{"test"},
		}
	}

	return &agents.RegisteredAgent{
		ID:            uuid.New().String(),
		Name:          name,
		ProjectID:     projectID,
		Status:        agents.StatusIdle,
		Capabilities:  caps,
		LastHeartbeat: time.Now(),
		Metadata: map[string]interface{}{
			"test": true,
		},
	}
}

// CreateSearchRequest creates a test search request
func (f *Fixtures) CreateSearchRequest(query, projectID string, searchType search.Type) *search.Request {
	return &search.Request{
		Query:     query,
		Type:      searchType,
		ProjectID: projectID,
		Limit:     20,
		Offset:    0,
		MinScore:  0.1,
	}
}

// Cleanup removes all test data for a project
func (f *Fixtures) Cleanup(projectID pgtype.UUID) error {
	ctx := context.Background()

	// Delete links first (foreign key constraint)
	_, err := f.pool.Exec(ctx, "DELETE FROM links WHERE project_id = $1", projectID)
	if err != nil {
		return err
	}

	// Delete items
	_, err = f.pool.Exec(ctx, "DELETE FROM items WHERE project_id = $1", projectID)
	if err != nil {
		return err
	}

	// Delete events
	projectIDStr := projectID.String()
	_, err = f.pool.Exec(ctx, "DELETE FROM events WHERE project_id = $1", projectIDStr)
	if err != nil {
		return err
	}

	// Delete project
	return f.queries.DeleteProject(ctx, projectID)
}

// Factory provides builder pattern for test data
type Factory struct {
	fixtures *Fixtures
	project  db.Project
}

// NewFactory creates a new factory
func NewFactory(pool *pgxpool.Pool) *Factory {
	return &Factory{
		fixtures: New(pool),
	}
}

// WithProject sets the project for the factory
func (f *Factory) WithProject(name string) (*Factory, error) {
	project, err := f.fixtures.CreateProject(name)
	if err != nil {
		return nil, err
	}
	f.project = project
	return f, nil
}

// BuildItems creates items
func (f *Factory) BuildItems(count int) ([]db.Item, error) {
	items := make([]db.Item, count)
	for i := 0; i < count; i++ {
		item, err := f.fixtures.CreateItem(
			f.project.ID,
			"Item-"+uuid.New().String(),
			"task",
			"open",
		)
		if err != nil {
			return nil, err
		}
		items[i] = item
	}
	return items, nil
}

// BuildLinkedItems creates items with links
func (f *Factory) BuildLinkedItems(count int) ([]db.Item, error) {
	return f.fixtures.CreateItemChain(f.project.ID, count, "Chain")
}

// BuildTree creates a tree structure
func (f *Factory) BuildTree(depth, branchFactor int) ([]db.Item, error) {
	return f.fixtures.CreateItemTree(f.project.ID, depth, branchFactor)
}

// Cleanup removes all factory data
func (f *Factory) Cleanup() error {
	return f.fixtures.Cleanup(f.project.ID)
}

// MockData provides pre-configured test scenarios
type MockData struct {
	ProjectID string
	Items     []string
	Links     []string
	Events    []*events.Event
	Agents    []*agents.RegisteredAgent
}

// SmallGraph creates a small test graph
func SmallGraph() *MockData {
	projectID := uuid.New().String()
	itemIDs := make([]string, 5)
	for i := range itemIDs {
		itemIDs[i] = uuid.New().String()
	}

	return &MockData{
		ProjectID: projectID,
		Items:     itemIDs,
		Links: []string{
			itemIDs[0] + "->" + itemIDs[1],
			itemIDs[1] + "->" + itemIDs[2],
			itemIDs[0] + "->" + itemIDs[3],
			itemIDs[3] + "->" + itemIDs[4],
		},
	}
}

// LargeGraph creates a large test graph
func LargeGraph() *MockData {
	projectID := uuid.New().String()
	itemIDs := make([]string, 100)
	links := make([]string, 0)

	for i := range itemIDs {
		itemIDs[i] = uuid.New().String()
	}

	// Create random connections
	for i := 0; i < len(itemIDs)-1; i++ {
		links = append(links, itemIDs[i]+"->"+itemIDs[i+1])
		if i < len(itemIDs)-10 {
			links = append(links, itemIDs[i]+"->"+itemIDs[i+10])
		}
	}

	return &MockData{
		ProjectID: projectID,
		Items:     itemIDs,
		Links:     links,
	}
}

// EventStream creates a stream of test events
func EventStream(projectID string, entityCount, eventsPerEntity int) []*events.Event {
	allEvents := make([]*events.Event, 0)

	for i := 0; i < entityCount; i++ {
		entityID := uuid.New().String()
		for j := 0; j < eventsPerEntity; j++ {
			event := events.NewEvent(
				projectID,
				entityID,
				events.EntityTypeItem,
				events.EventTypeUpdated,
				map[string]interface{}{
					"index":  j,
					"entity": i,
				},
			)
			allEvents = append(allEvents, event)
		}
	}

	return allEvents
}

// AgentPool creates a pool of test agents
func AgentPool(projectID string, count int) []*agents.RegisteredAgent {
	agentList := make([]*agents.RegisteredAgent, count)

	for i := 0; i < count; i++ {
		agentList[i] = &agents.RegisteredAgent{
			ID:        uuid.New().String(),
			Name:      "agent-" + string(rune('A'+i)),
			ProjectID: projectID,
			Status:    agents.StatusIdle,
			Capabilities: []agents.AgentCapability{
				{
					Name:    "capability-" + string(rune('A'+i%3)),
					Version: "1.0.0",
					Tags:    []string{"test"},
				},
			},
			LastHeartbeat: time.Now(),
		}
	}

	return agentList
}
