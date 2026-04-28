//go:build integration

package integration

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"os"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/stdlib"
	"github.com/nats-io/nats.go"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/events"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/kooshapari/tracertm-backend/internal/services"
)

// serviceTestFixture holds all dependencies for service integration tests
type serviceTestFixture struct {
	ctx          context.Context
	db           *gorm.DB
	cache        cache.Cache
	natsConn     *nats.Conn
	itemRepo     repository.ItemRepository
	linkRepo     repository.LinkRepository
	projectRepo  repository.ProjectRepository
	agentRepo    repository.AgentRepository
	itemService  services.ItemService
	linkService  services.LinkService
	projectSvc   services.ProjectService
	agentService services.AgentService
	eventStore   events.EventStore
	eventBus     *mockEventBus
	cleanup      func()
}

// setupServiceTests creates a complete test fixture with all service dependencies
func setupServiceTests(t *testing.T) *serviceTestFixture {
	ctx := context.Background()

	// Get database connection string from environment or use default
	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set, skipping integration test")
	}

	// Connect to database with sql.DB
	sqlDB, err := sql.Open("pgx", dbURL)
	require.NoError(t, err, "Failed to open SQL database")

	// Test connection
	err = sqlDB.Ping()
	require.NoError(t, err, "Failed to ping database")

	// Create GORM DB
	gormDB, err := gorm.Open(postgres.New(postgres.Config{
		Conn: sqlDB,
	}), &gorm.Config{})
	require.NoError(t, err, "Failed to open GORM database")

	// Auto-migrate models
	err = gormDB.AutoMigrate(
		&models.Item{},
		&models.Link{},
		&models.Project{},
		&models.Agent{},
		&models.View{},
	)
	require.NoError(t, err, "Failed to auto-migrate models")

	// Create repositories
	itemRepo := repository.NewItemRepository(gormDB)
	linkRepo := repository.NewLinkRepository(gormDB)
	projectRepo := repository.NewProjectRepository(gormDB)
	agentRepo := repository.NewAgentRepository(gormDB)

	// Create mock cache
	mockCache := newMockCache()

	// Create mock NATS connection
	mockNATS := newMockNATS()

	// Create event infrastructure
	eventStore := newMockEventStore()
	eventBus := newMockEventBus()

	// Create services
	itemService := services.NewItemServiceImpl(itemRepo, linkRepo, mockCache, mockNATS)
	linkService := services.NewLinkServiceImpl(linkRepo, itemRepo, mockCache, mockNATS)
	projectSvc := services.NewProjectServiceImpl(projectRepo, itemRepo, mockCache, mockNATS)
	agentService := services.NewAgentServiceImpl(agentRepo, mockCache, mockNATS)

	cleanup := func() {
		// Clean up test data
		gormDB.Exec("TRUNCATE TABLE items, links, projects, agents, views CASCADE")
		if sqlDB != nil {
			_ = sqlDB.Close()
		}
	}

	return &serviceTestFixture{
		ctx:          ctx,
		db:           gormDB,
		cache:        mockCache,
		natsConn:     mockNATS,
		itemRepo:     itemRepo,
		linkRepo:     linkRepo,
		projectRepo:  projectRepo,
		agentRepo:    agentRepo,
		itemService:  itemService,
		linkService:  linkService,
		projectSvc:   projectSvc,
		agentService: agentService,
		eventStore:   eventStore,
		eventBus:     eventBus,
		cleanup:      cleanup,
	}
}

// Mock Implementations

type mockCache struct {
	data map[string][]byte
}

func newMockCache() *mockCache {
	return &mockCache{
		data: make(map[string][]byte),
	}
}

func (c *mockCache) Get(ctx context.Context, key string, dest interface{}) error {
	data, exists := c.data[key]
	if !exists {
		return errors.New("key not found")
	}
	return json.Unmarshal(data, dest)
}

func (c *mockCache) Set(ctx context.Context, key string, value interface{}) error {
	data, err := json.Marshal(value)
	if err != nil {
		return err
	}
	c.data[key] = data
	return nil
}

func (c *mockCache) Delete(ctx context.Context, keys ...string) error {
	for _, key := range keys {
		delete(c.data, key)
	}
	return nil
}

func (c *mockCache) InvalidatePattern(ctx context.Context, pattern string) error {
	c.data = make(map[string][]byte)
	return nil
}

func (c *mockCache) Close() error {
	return nil
}

func (c *mockCache) HasKey(key string) bool {
	_, exists := c.data[key]
	return exists
}

type mockNATS struct {
	events []*mockEvent
}

type mockEvent struct {
	Subject string
	Data    []byte
}

func newMockNATS() *mockNATS {
	return &mockNATS{
		events: make([]*mockEvent, 0),
	}
}

func (m *mockNATS) Publish(subject string, data []byte) error {
	m.events = append(m.events, &mockEvent{
		Subject: subject,
		Data:    data,
	})
	return nil
}

func (m *mockNATS) GetEvents() []*mockEvent {
	return m.events
}

func (m *mockNATS) ClearEvents() {
	m.events = make([]*mockEvent, 0)
}

func (m *mockNATS) Close()       {}
func (m *mockNATS) Flush() error { return nil }
func (m *mockNATS) Drain() error { return nil }

type mockEventStore struct{}

func newMockEventStore() *mockEventStore {
	return &mockEventStore{}
}

func (s *mockEventStore) Store(event *events.Event) error                        { return nil }
func (s *mockEventStore) StoreMany(events []*events.Event) error                 { return nil }
func (s *mockEventStore) GetByEntityID(entityID string) ([]*events.Event, error) { return nil, nil }
func (s *mockEventStore) GetByEntityIDAfterVersion(entityID string, version int64) ([]*events.Event, error) {
	return nil, nil
}

func (s *mockEventStore) GetByProjectID(projectID string, limit, offset int) ([]*events.Event, error) {
	return nil, nil
}

func (s *mockEventStore) GetByProjectIDAndType(projectID string, entityType events.EntityType, limit, offset int) ([]*events.Event, error) {
	return nil, nil
}

func (s *mockEventStore) GetByTimeRange(projectID string, start, end time.Time) ([]*events.Event, error) {
	return nil, nil
}
func (s *mockEventStore) SaveSnapshot(snapshot *events.Snapshot) error { return nil }
func (s *mockEventStore) GetLatestSnapshot(entityID string) (*events.Snapshot, error) {
	return nil, nil
}

func (s *mockEventStore) GetSnapshotAtVersion(entityID string, version int64) (*events.Snapshot, error) {
	return nil, nil
}
func (s *mockEventStore) Replay(entityID string) (map[string]interface{}, error) { return nil, nil }
func (s *mockEventStore) ReplayFromSnapshot(entityID string, snapshotVersion int64) (map[string]interface{}, error) {
	return nil, nil
}

type mockEventBus struct {
	events []*events.Event
}

func newMockEventBus() *mockEventBus {
	return &mockEventBus{
		events: make([]*events.Event, 0),
	}
}

func (b *mockEventBus) Publish(event *events.Event) error {
	b.events = append(b.events, event)
	return nil
}

func (b *mockEventBus) PublishToProject(projectID string, event *events.Event) error {
	return b.Publish(event)
}

func (b *mockEventBus) PublishToEntity(entityID string, event *events.Event) error {
	return b.Publish(event)
}

func (b *mockEventBus) Subscribe(handler func(*events.Event)) error { return nil }
func (b *mockEventBus) SubscribeToProject(projectID string, handler func(*events.Event)) error {
	return nil
}

func (b *mockEventBus) SubscribeToEntity(entityID string, handler func(*events.Event)) error {
	return nil
}

func (b *mockEventBus) SubscribeToEventType(eventType events.EntityType, handler func(*events.Event)) error {
	return nil
}
func (b *mockEventBus) Unsubscribe(subscriptionID string) error { return nil }
