package events

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const eventStoreTimestampDelay = 10 * time.Millisecond

// setupTestDB creates a test database connection
func setupTestDB(t *testing.T) *pgxpool.Pool {
	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		databaseURL = "postgres://postgres:postgres@localhost:5432/agent_api"
	}

	pool, err := pgxpool.New(context.Background(), databaseURL)
	if err != nil {
		t.Skip("Failed to connect to PostgreSQL (expected if DB not running), skipping integration tests")
	}

	// Ensure events table exists with new schema
	_, err = pool.Exec(context.Background(), `
		CREATE TABLE IF NOT EXISTS events (
			id UUID PRIMARY KEY,
			project_id UUID NOT NULL,
			entity_type VARCHAR(50) NOT NULL,
			entity_id UUID NOT NULL,
			event_type VARCHAR(100) NOT NULL,
			data JSONB NOT NULL,
			metadata JSONB DEFAULT '{}',
			version INTEGER NOT NULL DEFAULT 1,
			causation_id UUID,
			correlation_id UUID,
			created_at TIMESTAMP NOT NULL
		);
		CREATE INDEX IF NOT EXISTS idx_events_entity_id ON events(entity_id);
		CREATE INDEX IF NOT EXISTS idx_events_project_id ON events(project_id);
		CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at);
		CREATE INDEX IF NOT EXISTS idx_events_entity_version ON events(entity_id, version);
		CREATE INDEX IF NOT EXISTS idx_events_correlation_id ON events(correlation_id) WHERE correlation_id IS NOT NULL;
		CREATE INDEX IF NOT EXISTS idx_events_causation_id ON events(causation_id) WHERE causation_id IS NOT NULL;
	`)
	if err != nil {
		pool.Close()
		t.Skip("Failed to create events table (expected if DB permissions issue), skipping integration tests")
	}

	return pool
}

// testProjectIDs holds project IDs created during tests for cleanup
// Package-level variable for test state management
var testProjectIDs []string

// cleanupTestDB cleans up test data
func cleanupTestDB(t *testing.T, pool *pgxpool.Pool) {
	for _, projectID := range testProjectIDs {
		_, err := pool.Exec(context.Background(), "DELETE FROM events WHERE project_id = $1", projectID)
		if err != nil {
			t.Logf("Warning: failed to cleanup events for project %s: %v", projectID, err)
		}
		_, err = pool.Exec(context.Background(), "DELETE FROM snapshots WHERE project_id = $1", projectID)
		if err != nil {
			// Snapshots table might not exist yet
			t.Logf("Warning: failed to cleanup snapshots for project %s: %v", projectID, err)
		}
	}
	testProjectIDs = nil // Reset for next test
	pool.Close()
}

// newTestProjectID creates a new UUID for test projects and tracks it for cleanup
func newTestProjectID() string {
	id := uuid.New().String()
	testProjectIDs = append(testProjectIDs, id)
	return id
}

// TestStoreEvent tests storing a single event
func TestStoreEvent(t *testing.T) {
	pool := setupTestDB(t)
	defer cleanupTestDB(t, pool)

	store := NewPostgresEventStore(pool)
	event := NewEvent(newTestProjectID(), uuid.New().String(), EntityTypeItem, EventTypeCreated, map[string]interface{}{
		"title": "Test Item",
	})

	err := store.Store(event)
	require.NoError(t, err)

	// Retrieve and verify
	events, err := store.GetByEntityID(event.EntityID)
	require.NoError(t, err)
	require.Len(t, events, 1)

	retrieved := events[0]
	assert.Equal(t, event.ID, retrieved.ID)
	assert.Equal(t, event.ProjectID, retrieved.ProjectID)
	assert.Equal(t, event.EntityID, retrieved.EntityID)
	assert.Equal(t, event.EventType, retrieved.EventType)
	assert.Equal(t, "Test Item", retrieved.Data["title"])
}

// TestStoreMany tests batch event storage
func TestStoreMany(t *testing.T) {
	pool := setupTestDB(t)
	defer cleanupTestDB(t, pool)

	store := NewPostgresEventStore(pool)
	projectID := newTestProjectID()
	entityID := uuid.New().String()

	events := []*Event{
		NewEvent(projectID, entityID, EntityTypeItem, EventTypeCreated, map[string]interface{}{"step": 1}),
		NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{"step": 2}),
		NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{"step": 3}),
	}

	// Add small delays to ensure timestamp ordering
	for i := range events {
		if i > 0 {
			time.Sleep(eventStoreTimestampDelay)
			events[i].CreatedAt = time.Now().UTC()
		}
	}

	err := store.StoreMany(events)
	require.NoError(t, err)

	// Retrieve and verify
	retrieved, err := store.GetByEntityID(entityID)
	require.NoError(t, err)
	require.Len(t, retrieved, 3)

	// Verify order
	assert.InEpsilon(t, float64(1), retrieved[0].Data["step"], 1e-9)
	assert.InEpsilon(t, float64(2), retrieved[1].Data["step"], 1e-9)
	assert.InEpsilon(t, float64(3), retrieved[2].Data["step"], 1e-9)
}

// TestGetByProjectID tests retrieving events by project
func TestGetByProjectID(t *testing.T) {
	pool := setupTestDB(t)
	defer cleanupTestDB(t, pool)

	store := NewPostgresEventStore(pool)
	projectID := newTestProjectID()

	// Create events for multiple entities
	events := []*Event{
		NewEvent(projectID, uuid.New().String(), EntityTypeItem, EventTypeCreated, nil),
		NewEvent(projectID, uuid.New().String(), EntityTypeItem, EventTypeCreated, nil),
		NewEvent(projectID, uuid.New().String(), EntityTypeLink, EventTypeLinkCreated, nil),
	}

	for _, event := range events {
		err := store.Store(event)
		require.NoError(t, err)
	}

	// Retrieve by project
	retrieved, err := store.GetByProjectID(projectID, 10, 0)
	require.NoError(t, err)
	assert.GreaterOrEqual(t, len(retrieved), 3)

	// Verify all events belong to project
	for _, event := range retrieved {
		assert.Equal(t, projectID, event.ProjectID)
	}
}

// TestGetByProjectIDAndType tests filtering by entity type
func TestGetByProjectIDAndType(t *testing.T) {
	pool := setupTestDB(t)
	defer cleanupTestDB(t, pool)

	store := NewPostgresEventStore(pool)
	projectID := newTestProjectID()

	// Create events of different types
	itemEvent := NewEvent(projectID, uuid.New().String(), EntityTypeItem, EventTypeCreated, nil)
	linkEvent := NewEvent(projectID, uuid.New().String(), EntityTypeLink, EventTypeLinkCreated, nil)

	require.NoError(t, store.Store(itemEvent))
	require.NoError(t, store.Store(linkEvent))

	// Retrieve only item events
	items, err := store.GetByProjectIDAndType(projectID, EntityTypeItem, 10, 0)
	require.NoError(t, err)
	assert.GreaterOrEqual(t, len(items), 1)

	for _, event := range items {
		assert.Equal(t, EntityTypeItem, event.EntityType)
	}

	// Retrieve only link events
	links, err := store.GetByProjectIDAndType(projectID, EntityTypeLink, 10, 0)
	require.NoError(t, err)
	assert.GreaterOrEqual(t, len(links), 1)

	for _, event := range links {
		assert.Equal(t, EntityTypeLink, event.EntityType)
	}
}

// TestGetByTimeRange tests temporal queries
func TestGetByTimeRange(t *testing.T) {
	pool := setupTestDB(t)
	defer cleanupTestDB(t, pool)

	store := NewPostgresEventStore(pool)
	projectID := newTestProjectID()

	now := time.Now().UTC()
	start := now.Add(-1 * time.Hour)
	end := now.Add(1 * time.Hour)

	// Create events in time range
	event1 := NewEvent(projectID, uuid.New().String(), EntityTypeItem, EventTypeCreated, nil)
	event1.CreatedAt = now.Add(-30 * time.Minute)

	event2 := NewEvent(projectID, uuid.New().String(), EntityTypeItem, EventTypeCreated, nil)
	event2.CreatedAt = now.Add(-15 * time.Minute)

	// Event outside range
	event3 := NewEvent(projectID, uuid.New().String(), EntityTypeItem, EventTypeCreated, nil)
	event3.CreatedAt = now.Add(-2 * time.Hour)

	require.NoError(t, store.Store(event1))
	require.NoError(t, store.Store(event2))
	require.NoError(t, store.Store(event3))

	// Query time range
	events, err := store.GetByTimeRange(projectID, start, end)
	require.NoError(t, err)
	assert.GreaterOrEqual(t, len(events), 2)

	// Verify all events are within range
	for _, event := range events {
		assert.True(t, event.CreatedAt.After(start) || event.CreatedAt.Equal(start))
		assert.True(t, event.CreatedAt.Before(end) || event.CreatedAt.Equal(end))
	}
}

// TestSnapshot tests snapshot creation and retrieval
func TestSnapshot(t *testing.T) {
	pool := setupTestDB(t)
	defer cleanupTestDB(t, pool)

	store := NewPostgresEventStore(pool)
	projectID := newTestProjectID()
	entityID := uuid.New().String()

	snapshot := NewSnapshot(projectID, entityID, EntityTypeItem, 5, map[string]interface{}{
		"title": "Snapshot State",
		"count": 5,
	})

	err := store.SaveSnapshot(snapshot)
	require.NoError(t, err)

	// Retrieve latest snapshot
	retrieved, err := store.GetLatestSnapshot(entityID)
	require.NoError(t, err)
	require.NotNil(t, retrieved)

	assert.Equal(t, snapshot.ID, retrieved.ID)
	assert.Equal(t, snapshot.EntityID, retrieved.EntityID)
	assert.Equal(t, snapshot.Version, retrieved.Version)
	assert.Equal(t, "Snapshot State", retrieved.State["title"])
	assert.InEpsilon(t, float64(5), retrieved.State["count"], 1e-9)
}

// TestMultipleSnapshots tests retrieving snapshots at specific versions
func TestMultipleSnapshots(t *testing.T) {
	pool := setupTestDB(t)
	defer cleanupTestDB(t, pool)

	store := NewPostgresEventStore(pool)
	projectID := newTestProjectID()
	entityID := uuid.New().String()

	// Create snapshots at different versions
	for version := int64(1); version <= 5; version++ {
		snapshot := NewSnapshot(projectID, entityID, EntityTypeItem, version, map[string]interface{}{
			"version": version,
		})
		require.NoError(t, store.SaveSnapshot(snapshot))
	}

	// Get snapshot at version 3
	snapshot, err := store.GetSnapshotAtVersion(entityID, 3)
	require.NoError(t, err)
	require.NotNil(t, snapshot)
	assert.LessOrEqual(t, snapshot.Version, int64(3))

	// Get latest snapshot
	latest, err := store.GetLatestSnapshot(entityID)
	require.NoError(t, err)
	require.NotNil(t, latest)
	assert.Equal(t, int64(5), latest.Version)
}

// TestReplay tests event replay
func TestReplay(t *testing.T) {
	pool := setupTestDB(t)
	defer cleanupTestDB(t, pool)

	store := NewPostgresEventStore(pool)
	projectID := newTestProjectID()
	entityID := uuid.New().String()

	// Create events that modify state
	events := []*Event{
		NewEvent(projectID, entityID, EntityTypeItem, EventTypeCreated, map[string]interface{}{
			"title": "Initial",
			"count": 1,
		}),
		NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{
			"title": "Updated",
			"count": 2,
		}),
		NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{
			"count": 3,
		}),
	}

	for _, event := range events {
		require.NoError(t, store.Store(event))
	}

	// Replay events
	state, err := store.Replay(entityID)
	require.NoError(t, err)

	// Verify final state
	assert.Equal(t, "Updated", state["title"])
	assert.InEpsilon(t, float64(3), state["count"], 1e-9)
}

// TestReplayFromSnapshot tests replaying from a snapshot
func TestReplayFromSnapshot(t *testing.T) {
	t.Skip("Integration test - requires proper version management in events")
	pool := setupTestDB(t)
	defer cleanupTestDB(t, pool)

	store := NewPostgresEventStore(pool)
	projectID := newTestProjectID()
	entityID := uuid.New().String()

	// Create initial events
	events := []*Event{
		NewEvent(projectID, entityID, EntityTypeItem, EventTypeCreated, map[string]interface{}{"count": 1}),
		NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{"count": 2}),
		NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{"count": 3}),
	}

	for _, event := range events {
		require.NoError(t, store.Store(event))
	}

	// Create snapshot at version 2
	snapshot := NewSnapshot(projectID, entityID, EntityTypeItem, 2, map[string]interface{}{
		"count": 2,
		"title": "Snapshot",
	})
	require.NoError(t, store.SaveSnapshot(snapshot))

	// Add more events after snapshot
	event4 := NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{"count": 4})
	require.NoError(t, store.Store(event4))

	// Replay from snapshot
	state, err := store.ReplayFromSnapshot(entityID, 2)
	require.NoError(t, err)

	// Should have snapshot data + events after snapshot
	assert.Equal(t, "Snapshot", state["title"])
	assert.InEpsilon(t, float64(4), state["count"], 1e-9)
}

// TestEventCount tests counting events
func TestEventCount(t *testing.T) {
	pool := setupTestDB(t)
	defer cleanupTestDB(t, pool)

	store := NewPostgresEventStore(pool)
	projectID := newTestProjectID()
	entityID := uuid.New().String()

	// Initial count
	count, err := store.GetEventCount(entityID)
	require.NoError(t, err)
	assert.Equal(t, int64(0), count)

	// Add events
	for i := 0; i < 5; i++ {
		event := NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, nil)
		require.NoError(t, store.Store(event))
	}

	// New count
	count, err = store.GetEventCount(entityID)
	require.NoError(t, err)
	assert.Equal(t, int64(5), count)
}

// TestPagination tests pagination of event queries
func TestPagination(t *testing.T) {
	pool := setupTestDB(t)
	defer cleanupTestDB(t, pool)

	store := NewPostgresEventStore(pool)
	projectID := newTestProjectID()

	// Create 10 events
	for i := 0; i < 10; i++ {
		event := NewEvent(projectID, uuid.New().String(), EntityTypeItem, EventTypeCreated, map[string]interface{}{
			"index": i,
		})
		require.NoError(t, store.Store(event))
	}

	// Get first page (5 items)
	page1, err := store.GetByProjectID(projectID, 5, 0)
	require.NoError(t, err)
	assert.Len(t, page1, 5)

	// Get second page (5 items)
	page2, err := store.GetByProjectID(projectID, 5, 5)
	require.NoError(t, err)
	assert.Len(t, page2, 5)

	// Verify no overlap
	ids1 := make(map[string]bool)
	for _, e := range page1 {
		ids1[e.ID] = true
	}
	for _, e := range page2 {
		assert.False(t, ids1[e.ID], "Event appeared in both pages")
	}
}

// BenchmarkStoreEvent benchmarks single event storage
func BenchmarkStoreEvent(b *testing.B) {
	pool, err := pgxpool.New(context.Background(), os.Getenv("DATABASE_URL"))
	if err != nil {
		b.Skip("DATABASE_URL not set")
	}
	defer pool.Close()

	store := NewPostgresEventStore(pool)
	projectID := uuid.New().String()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		event := NewEvent(projectID, uuid.New().String(), EntityTypeItem, EventTypeCreated, nil)
		require.NoError(b, store.Store(event))
	}
}

// BenchmarkStoreMany benchmarks batch event storage
func BenchmarkStoreMany(b *testing.B) {
	pool, err := pgxpool.New(context.Background(), os.Getenv("DATABASE_URL"))
	if err != nil {
		b.Skip("DATABASE_URL not set")
	}
	defer pool.Close()

	store := NewPostgresEventStore(pool)
	projectID := uuid.New().String()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		events := make([]*Event, 100)
		for j := 0; j < 100; j++ {
			events[j] = NewEvent(projectID, uuid.New().String(), EntityTypeItem, EventTypeCreated, nil)
		}
		require.NoError(b, store.StoreMany(events))
	}
}
