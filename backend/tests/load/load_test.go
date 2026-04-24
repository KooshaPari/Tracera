package load

import (
	"context"
	"os"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/events"
	"github.com/kooshapari/tracertm-backend/internal/graph"
	"github.com/kooshapari/tracertm-backend/internal/search"
	"github.com/kooshapari/tracertm-backend/internal/websocket"
)

// TestConcurrentEventStorage tests concurrent event storage
func TestConcurrentEventStorage(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping load test in short mode")
	}

	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		t.Skip("DATABASE_URL not set")
	}

	pool, err := pgxpool.New(context.Background(), databaseURL)
	require.NoError(t, err)
	defer pool.Close()

	store := events.NewPostgresEventStore(pool)
	projectID := "test-load-" + uuid.New().String()

	const (
		goroutines = 100
		eventsEach = 100
	)

	start := time.Now()
	var wg sync.WaitGroup
	var successCount, errorCount int64

	for i := 0; i < goroutines; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()

			entityID := uuid.New().String()
			for j := 0; j < eventsEach; j++ {
				event := events.NewEvent(
					projectID,
					entityID,
					events.EntityTypeItem,
					events.EventTypeUpdated,
					map[string]interface{}{"index": j, "goroutine": id},
				)

				err := store.Store(event)
				if err != nil {
					atomic.AddInt64(&errorCount, 1)
				} else {
					atomic.AddInt64(&successCount, 1)
				}
			}
		}(i)
	}

	wg.Wait()
	duration := time.Since(start)

	totalEvents := goroutines * eventsEach
	eventsPerSecond := float64(successCount) / duration.Seconds()

	t.Logf("Concurrent Event Storage:")
	t.Logf("  Total Events: %d", totalEvents)
	t.Logf("  Successful: %d", successCount)
	t.Logf("  Failed: %d", errorCount)
	t.Logf("  Duration: %v", duration)
	t.Logf("  Events/sec: %.2f", eventsPerSecond)

	require.Greater(t, successCount, int64(float64(totalEvents)*0.95), "95%+ success rate expected")
}

// TestBulkEventReplay tests replaying large event sequences
func TestBulkEventReplay(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping load test in short mode")
	}

	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		t.Skip("DATABASE_URL not set")
	}

	pool, err := pgxpool.New(context.Background(), databaseURL)
	require.NoError(t, err)
	defer pool.Close()

	store := events.NewPostgresEventStore(pool)
	projectID := "test-replay-" + uuid.New().String()
	entityID := uuid.New().String()

	// Create large event sequence
	const eventCount = 1000
	eventList := make([]*events.Event, eventCount)
	for i := 0; i < eventCount; i++ {
		eventList[i] = events.NewEvent(
			projectID,
			entityID,
			events.EntityTypeItem,
			events.EventTypeUpdated,
			map[string]interface{}{
				"step":  i,
				"value": i * 10,
			},
		)
	}

	// Store events
	start := time.Now()
	err = store.StoreMany(eventList)
	require.NoError(t, err)
	storeDuration := time.Since(start)

	// Replay events
	start = time.Now()
	state, err := store.Replay(entityID)
	require.NoError(t, err)
	replayDuration := time.Since(start)

	t.Logf("Bulk Event Replay:")
	t.Logf("  Events: %d", eventCount)
	t.Logf("  Store Duration: %v", storeDuration)
	t.Logf("  Replay Duration: %v", replayDuration)
	t.Logf("  Final State: step=%v, value=%v", state["step"], state["value"])

	require.NotNil(t, state)
	require.Equal(t, float64(eventCount-1), state["step"])
}

// TestLargeGraphTraversal tests graph operations on large graphs
func TestLargeGraphTraversal(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping load test in short mode")
	}

	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		t.Skip("DATABASE_URL not set")
	}

	pool, err := pgxpool.New(context.Background(), databaseURL)
	require.NoError(t, err)
	defer pool.Close()

	ctx := context.Background()
	queries := db.New(pool)
	graphEngine := graph.NewGraph(pool)

	// Create project
	projectID := pgtype.UUID{Bytes: uuid.New(), Valid: true}
	_, err = queries.CreateProject(ctx, db.CreateProjectParams{
		Name:        "test-large-graph-" + uuid.New().String(),
		Description: pgtype.Text{String: "Large graph test", Valid: true},
	})
	require.NoError(t, err)

	// Create large graph: 100 items in a chain
	const itemCount = 100
	items := make([]pgtype.UUID, itemCount)

	start := time.Now()
	for i := 0; i < itemCount; i++ {
		item, err := queries.CreateItem(ctx, db.CreateItemParams{
			ProjectID:   projectID,
			Title:       "Item-" + string(rune('A'+i%26)),
			Description: pgtype.Text{String: "Test item", Valid: true},
			Type:        "task",
			Status:      "open",
			Priority:    pgtype.Int4{Int32: 2, Valid: true},
		})
		require.NoError(t, err)
		items[i] = item.ID

		if i > 0 {
			_, err = queries.CreateLink(ctx, db.CreateLinkParams{
				SourceID: items[i-1],
				TargetID: items[i],
				Type:     "depends_on",
			})
			require.NoError(t, err)
		}
	}
	createDuration := time.Since(start)

	// Test BFS
	start = time.Now()
	bfsResult, err := graphEngine.BFS(ctx, items[0].String(), "forward", 0)
	require.NoError(t, err)
	bfsDuration := time.Since(start)

	// Test DFS
	start = time.Now()
	dfsResult, err := graphEngine.DFS(ctx, items[0].String(), "forward", 0)
	require.NoError(t, err)
	dfsDuration := time.Since(start)

	// Test pathfinding
	start = time.Now()
	path, err := graphEngine.FindPath(ctx, items[0].String(), items[itemCount-1].String())
	require.NoError(t, err)
	pathDuration := time.Since(start)

	t.Logf("Large Graph Traversal (%d items):", itemCount)
	t.Logf("  Create Duration: %v", createDuration)
	t.Logf("  BFS Duration: %v (found %d nodes)", bfsDuration, len(bfsResult.Nodes))
	t.Logf("  DFS Duration: %v (found %d nodes)", dfsDuration, len(dfsResult.Nodes))
	t.Logf("  Path Duration: %v (length %d)", pathDuration, len(path.Path))

	require.Equal(t, itemCount, len(bfsResult.Nodes))
	require.Equal(t, itemCount, len(dfsResult.Nodes))
	require.True(t, path.Found)

	// Cleanup
	_ = queries.DeleteProject(ctx, projectID)
}

// TestConcurrentSearch tests concurrent search requests
func TestConcurrentSearch(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping load test in short mode")
	}

	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		t.Skip("DATABASE_URL not set")
	}

	pool, err := pgxpool.New(context.Background(), databaseURL)
	require.NoError(t, err)
	defer pool.Close()

	// Create test project with searchable items
	queries := db.New(pool)
	projectID := pgtype.UUID{Bytes: uuid.New(), Valid: true}
	_, err = queries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "test-search-" + uuid.New().String(),
		Description: pgtype.Text{String: "Search test", Valid: true},
	})
	require.NoError(t, err)

	// Create items
	for i := 0; i < 100; i++ {
		_, err := queries.CreateItem(context.Background(), db.CreateItemParams{
			ProjectID:   projectID,
			Title:       "Test item " + uuid.New().String(),
			Description: pgtype.Text{String: "Description with authentication keyword", Valid: true},
			Type:        "task",
			Status:      "open",
			Priority:    pgtype.Int4{Int32: 2, Valid: true},
		})
		require.NoError(t, err)
	}

	engine := search.NewSearchEngine(pool)

	const concurrentSearches = 100
	var wg sync.WaitGroup
	var successCount, errorCount int64

	start := time.Now()

	for i := 0; i < concurrentSearches; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()

			req := &search.Request{
				Query:     "authentication",
				Type:      search.TypeFullText,
				ProjectID: projectID.String(),
				Limit:     20,
			}

			_, err := engine.Search(context.Background(), req)
			if err != nil {
				atomic.AddInt64(&errorCount, 1)
			} else {
				atomic.AddInt64(&successCount, 1)
			}
		}()
	}

	wg.Wait()
	duration := time.Since(start)

	searchesPerSecond := float64(successCount) / duration.Seconds()

	t.Logf("Concurrent Search:")
	t.Logf("  Total Searches: %d", concurrentSearches)
	t.Logf("  Successful: %d", successCount)
	t.Logf("  Failed: %d", errorCount)
	t.Logf("  Duration: %v", duration)
	t.Logf("  Searches/sec: %.2f", searchesPerSecond)

	require.Greater(t, successCount, int64(float64(concurrentSearches)*0.95))

	// Cleanup
	_ = queries.DeleteProject(context.Background(), projectID)
}

// TestWebSocketBroadcastLoad tests broadcasting to many clients
func TestWebSocketBroadcastLoad(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping load test in short mode")
	}

	hub := websocket.NewHub()
	projectID := uuid.New().String()

	// Create many clients
	const clientCount = 1000
	clients := make([]*websocket.Client, clientCount)

	for i := 0; i < clientCount; i++ {
		clients[i] = &websocket.Client{
			ID:        uuid.New().String(),
			ProjectID: projectID,
			Send:      make(chan *websocket.Message, 256),
			Hub:       hub,
		}

		// Drain messages in background
		go func(c *websocket.Client) {
			for range c.Send {
			}
		}(clients[i])
	}

	// Register all clients
	hub.Mu.Lock()
	hub.Clients[projectID] = make(map[*websocket.Client]bool)
	for _, client := range clients {
		hub.Clients[projectID][client] = true
	}
	hub.Mu.Unlock()

	// Broadcast many messages
	const messageCount = 1000
	start := time.Now()

	for i := 0; i < messageCount; i++ {
		msg := &websocket.Message{
			Type: "test",
			Data: map[string]interface{}{
				"index": i,
			},
			Timestamp: time.Now(),
		}

		hub.Mu.RLock()
		for client := range hub.Clients[projectID] {
			select {
			case client.Send <- msg:
			default:
			}
		}
		hub.Mu.RUnlock()
	}

	duration := time.Since(start)

	totalMessages := clientCount * messageCount
	messagesPerSecond := float64(totalMessages) / duration.Seconds()

	t.Logf("WebSocket Broadcast Load:")
	t.Logf("  Clients: %d", clientCount)
	t.Logf("  Messages: %d", messageCount)
	t.Logf("  Total Deliveries: %d", totalMessages)
	t.Logf("  Duration: %v", duration)
	t.Logf("  Messages/sec: %.2f", messagesPerSecond)
}

// TestDatabaseConnectionPool tests connection pool under load
func TestDatabaseConnectionPool(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping load test in short mode")
	}

	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		t.Skip("DATABASE_URL not set")
	}

	config, err := pgxpool.ParseConfig(databaseURL)
	require.NoError(t, err)

	// Configure pool
	config.MaxConns = 20
	config.MinConns = 5

	pool, err := pgxpool.NewWithConfig(context.Background(), config)
	require.NoError(t, err)
	defer pool.Close()

	queries := db.New(pool)

	const (
		goroutines  = 50
		queriesEach = 100
	)

	var wg sync.WaitGroup
	var successCount, errorCount int64

	start := time.Now()

	for i := 0; i < goroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()

			for j := 0; j < queriesEach; j++ {
				// Simple query to test connection pool
				_, err := queries.ListProjects(context.Background(), db.ListProjectsParams{
					Limit:  10,
					Offset: 0,
				})

				if err != nil {
					atomic.AddInt64(&errorCount, 1)
				} else {
					atomic.AddInt64(&successCount, 1)
				}
			}
		}()
	}

	wg.Wait()
	duration := time.Since(start)

	totalQueries := goroutines * queriesEach
	queriesPerSecond := float64(successCount) / duration.Seconds()

	t.Logf("Database Connection Pool:")
	t.Logf("  Pool Size: %d-%d", config.MinConns, config.MaxConns)
	t.Logf("  Total Queries: %d", totalQueries)
	t.Logf("  Successful: %d", successCount)
	t.Logf("  Failed: %d", errorCount)
	t.Logf("  Duration: %v", duration)
	t.Logf("  Queries/sec: %.2f", queriesPerSecond)

	stats := pool.Stat()
	t.Logf("  Active Connections: %d", stats.AcquiredConns())
	t.Logf("  Idle Connections: %d", stats.IdleConns())
	t.Logf("  Total Connections: %d", stats.TotalConns())

	require.Greater(t, successCount, int64(float64(totalQueries)*0.95))
}

// BenchmarkEventThroughput benchmarks event storage throughput
func BenchmarkEventThroughput(b *testing.B) {
	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		b.Skip("DATABASE_URL not set")
	}

	pool, err := pgxpool.New(context.Background(), databaseURL)
	if err != nil {
		b.Fatal(err)
	}
	defer pool.Close()

	store := events.NewPostgresEventStore(pool)
	projectID := "bench-" + uuid.New().String()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		event := events.NewEvent(
			projectID,
			uuid.New().String(),
			events.EntityTypeItem,
			events.EventTypeCreated,
			map[string]interface{}{"index": i},
		)
		_ = store.Store(event)
	}

	b.ReportMetric(float64(b.N)/b.Elapsed().Seconds(), "events/sec")
}

// BenchmarkGraphTraversal benchmarks graph traversal performance
func BenchmarkGraphTraversal(b *testing.B) {
	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		b.Skip("DATABASE_URL not set")
	}

	pool, err := pgxpool.New(context.Background(), databaseURL)
	if err != nil {
		b.Fatal(err)
	}
	defer pool.Close()

	// Setup: create graph
	ctx := context.Background()
	queries := db.New(pool)
	graphEngine := graph.NewGraph(pool)

	projectID := pgtype.UUID{Bytes: uuid.New(), Valid: true}
	queries.CreateProject(ctx, db.CreateProjectParams{
		Name:        "bench-graph-" + uuid.New().String(),
		Description: pgtype.Text{String: "Benchmark", Valid: true},
	})

	items := make([]string, 50)
	for i := 0; i < 50; i++ {
		item, _ := queries.CreateItem(ctx, db.CreateItemParams{
			ProjectID: projectID,
			Title:     "Item",
			Type:      "task",
			Status:    "open",
			Priority:  pgtype.Int4{Int32: 2, Valid: true},
		})
		items[i] = item.ID.String()

		if i > 0 {
			parsedSource, _ := uuid.Parse(items[i-1])
			sourceUUID := pgtype.UUID{Bytes: parsedSource, Valid: true}
			parsedTarget, _ := uuid.Parse(items[i])
			targetUUID := pgtype.UUID{Bytes: parsedTarget, Valid: true}
			queries.CreateLink(ctx, db.CreateLinkParams{
				SourceID: sourceUUID,
				TargetID: targetUUID,
				Type:     "depends_on",
			})
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = graphEngine.BFS(ctx, items[0], "forward", 0)
	}
}
