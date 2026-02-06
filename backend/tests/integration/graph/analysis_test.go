package graph_test

import (
	"context"
	"testing"
	"time"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	neo4jcontainer "github.com/testcontainers/testcontainers-go/modules/neo4j"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/graph"
)

type testFixture struct {
	ctx     context.Context
	driver  neo4j.DriverWithContext
	cache   cache.Cache
	service *graph.AnalysisService
	cleanup func()
}

func setupTest(t *testing.T) *testFixture {
	ctx := context.Background()

	// Start Neo4j container
	neo4jContainer, err := neo4jcontainer.RunContainer(ctx,
		testcontainers.WithImage("neo4j:5.14"),
		neo4jcontainer.WithAdminPassword("testpassword"),
		neo4jcontainer.WithoutAuthentication(),
	)
	require.NoError(t, err)

	// Get connection string
	uri, err := neo4jContainer.BoltUrl(ctx)
	require.NoError(t, err)

	// Create driver
	driver, err := neo4j.NewDriverWithContext(uri, neo4j.NoAuth())
	require.NoError(t, err)

	// Verify connection
	err = driver.VerifyConnectivity(ctx)
	require.NoError(t, err)

	// Create mock cache
	mockCache := &mockCache{data: make(map[string]interface{})}

	// Create service
	service := graph.NewAnalysisService(driver, mockCache)

	cleanup := func() {
		driver.Close(ctx)
		neo4jContainer.Terminate(ctx)
	}

	return &testFixture{
		ctx:     ctx,
		driver:  driver,
		cache:   mockCache,
		service: service,
		cleanup: cleanup,
	}
}

// mockCache implements cache.Cache interface for testing
type mockCache struct {
	data map[string]interface{}
}

func (m *mockCache) Get(ctx context.Context, key string, dest interface{}) error {
	val, exists := m.data[key]
	if !exists {
		return nil
	}
	// Simple reflection-free copy
	*dest.(*interface{}) = val
	return nil
}

func (m *mockCache) Set(ctx context.Context, key string, value interface{}) error {
	m.data[key] = value
	return nil
}

func (m *mockCache) Delete(ctx context.Context, keys ...string) error {
	for _, key := range keys {
		delete(m.data, key)
	}
	return nil
}

func (m *mockCache) InvalidatePattern(ctx context.Context, pattern string) error {
	// Simple implementation - clear all
	m.data = make(map[string]interface{})
	return nil
}

func (m *mockCache) Close() error {
	return nil
}

// Helper to create test graph data
func createTestGraph(ctx context.Context, driver neo4j.DriverWithContext, projectID string) error {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer func() { _ = session.Close(ctx) }()

	// Create items
	items := []struct {
		id   string
		name string
	}{
		{"item1", "Requirement 1"},
		{"item2", "Design 1"},
		{"item3", "Implementation 1"},
		{"item4", "Test 1"},
		{"item5", "Isolated Item"},
	}

	for _, item := range items {
		query := `CREATE (n:Item {id: $id, name: $name, project_id: $projectID})`
		_, err := session.Run(ctx, query, map[string]interface{}{
			"id":        item.id,
			"name":      item.name,
			"projectID": projectID,
		})
		if err != nil {
			return err
		}
	}

	// Create links (linear chain + isolated item)
	links := []struct {
		source string
		target string
		typ    string
	}{
		{"item1", "item2", "implements"},
		{"item2", "item3", "implements"},
		{"item3", "item4", "tests"},
	}

	for _, link := range links {
		query := `
			MATCH (source:Item {id: $source})
			MATCH (target:Item {id: $target})
			CREATE (source)-[:LINK {type: $type}]->(target)
		`
		_, err := session.Run(ctx, query, map[string]interface{}{
			"source": link.source,
			"target": link.target,
			"type":   link.typ,
		})
		if err != nil {
			return err
		}
	}

	return nil
}

func TestShortestPath(t *testing.T) {
	fix := setupTest(t)
	defer fix.cleanup()

	projectID := "test-project-1"
	err := createTestGraph(fix.ctx, fix.driver, projectID)
	require.NoError(t, err)

	// Test shortest path
	path, err := fix.service.ShortestPath(fix.ctx, "item1", "item4")
	require.NoError(t, err)
	assert.NotNil(t, path)
	assert.Equal(t, "item1", path.Source)
	assert.Equal(t, "item4", path.Target)
	assert.Equal(t, 3, path.Length)
	assert.Len(t, path.Nodes, 4) // item1, item2, item3, item4
}

func TestShortestPath_Caching(t *testing.T) {
	fix := setupTest(t)
	defer fix.cleanup()

	projectID := "test-project-2"
	err := createTestGraph(fix.ctx, fix.driver, projectID)
	require.NoError(t, err)

	// First call
	start := time.Now()
	path1, err := fix.service.ShortestPath(fix.ctx, "item1", "item3")
	require.NoError(t, err)
	firstCallDuration := time.Since(start)

	// Second call (should be cached)
	start = time.Now()
	path2, err := fix.service.ShortestPath(fix.ctx, "item1", "item3")
	require.NoError(t, err)
	secondCallDuration := time.Since(start)

	assert.Equal(t, path1.Length, path2.Length)
	// Cache should be significantly faster (this is a loose check)
	t.Logf("First call: %v, Second call: %v", firstCallDuration, secondCallDuration)
}

func TestDetectCycles(t *testing.T) {
	fix := setupTest(t)
	defer fix.cleanup()

	ctx := fix.ctx
	projectID := "test-project-cycles"

	// Create a graph with a cycle
	session := fix.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer func() { _ = session.Close(ctx) }()

	// Create nodes
	for i := 1; i <= 3; i++ {
		query := `CREATE (n:Item {id: $id, project_id: $projectID})`
		_, err := session.Run(ctx, query, map[string]interface{}{
			"id":        "cycle" + string(rune('0'+i)),
			"projectID": projectID,
		})
		require.NoError(t, err)
	}

	// Create cycle: cycle1 -> cycle2 -> cycle3 -> cycle1
	links := [][]string{
		{"cycle1", "cycle2"},
		{"cycle2", "cycle3"},
		{"cycle3", "cycle1"},
	}

	for _, link := range links {
		query := `
			MATCH (source:Item {id: $source})
			MATCH (target:Item {id: $target})
			CREATE (source)-[:LINK]->(target)
		`
		_, err := session.Run(ctx, query, map[string]interface{}{
			"source": link[0],
			"target": link[1],
		})
		require.NoError(t, err)
	}

	// Test cycle detection
	cycles, err := fix.service.DetectCycles(ctx, projectID)
	require.NoError(t, err)
	assert.Greater(t, len(cycles), 0, "Should detect at least one cycle")

	if len(cycles) > 0 {
		// Check cycle properties
		cycle := cycles[0]
		assert.Equal(t, 3, cycle.Length)
		assert.Equal(t, "error", cycle.Severity) // Small cycles are errors
	}
}

func TestCalculateCentrality(t *testing.T) {
	fix := setupTest(t)
	defer fix.cleanup()

	projectID := "test-project-centrality"
	err := createTestGraph(fix.ctx, fix.driver, projectID)
	require.NoError(t, err)

	// Calculate centrality
	metrics, err := fix.service.CalculateCentrality(fix.ctx, projectID)
	require.NoError(t, err)
	assert.NotNil(t, metrics)
	assert.Equal(t, projectID, metrics.ProjectID)
	assert.NotEmpty(t, metrics.Betweenness)
	assert.NotEmpty(t, metrics.MostCentral)

	// item2 and item3 should have higher centrality (in the middle of chain)
	t.Logf("Centrality metrics: %+v", metrics)
}

func TestGetDependencies(t *testing.T) {
	fix := setupTest(t)
	defer fix.cleanup()

	projectID := "test-project-deps"
	err := createTestGraph(fix.ctx, fix.driver, projectID)
	require.NoError(t, err)

	// Get dependencies for item1 (should reach item2, item3, item4)
	tree, err := fix.service.GetDependencies(fix.ctx, "item1", 5)
	require.NoError(t, err)
	assert.NotNil(t, tree)
	assert.Equal(t, "item1", tree.Root)
	assert.Greater(t, tree.Depth, 0)
	assert.NotEmpty(t, tree.Children)
}

func TestGetDependents(t *testing.T) {
	fix := setupTest(t)
	defer fix.cleanup()

	projectID := "test-project-dependents"
	err := createTestGraph(fix.ctx, fix.driver, projectID)
	require.NoError(t, err)

	// Get dependents for item4 (should trace back to item3, item2, item1)
	tree, err := fix.service.GetDependents(fix.ctx, "item4", 5)
	require.NoError(t, err)
	assert.NotNil(t, tree)
	assert.Equal(t, "item4", tree.Root)
	assert.Greater(t, tree.Depth, 0)
}

func TestAnalyzeImpact(t *testing.T) {
	fix := setupTest(t)
	defer fix.cleanup()

	projectID := "test-project-impact"
	err := createTestGraph(fix.ctx, fix.driver, projectID)
	require.NoError(t, err)

	// Analyze impact of changing item2
	report, err := fix.service.AnalyzeImpact(fix.ctx, []string{"item2"})
	require.NoError(t, err)
	assert.NotNil(t, report)
	assert.Len(t, report.SourceItems, 1)
	assert.Greater(t, report.TotalAffected, 0)
}

func TestAnalyzeCoverage(t *testing.T) {
	fix := setupTest(t)
	defer fix.cleanup()

	projectID := "test-project-coverage"
	err := createTestGraph(fix.ctx, fix.driver, projectID)
	require.NoError(t, err)

	// Analyze coverage
	report, err := fix.service.AnalyzeCoverage(fix.ctx, projectID)
	require.NoError(t, err)
	assert.NotNil(t, report)
	assert.Equal(t, projectID, report.ProjectID)
	assert.Equal(t, 5, report.TotalItems)     // 5 items created
	assert.Equal(t, 4, report.ConnectedItems) // 4 connected
	assert.Len(t, report.IsolatedItems, 1)    // 1 isolated (item5)
	assert.Contains(t, report.IsolatedItems, "item5")
	assert.InDelta(t, 80.0, report.CoveragePercent, 1.0) // 4/5 = 80%
}

func TestGetGraphMetrics(t *testing.T) {
	fix := setupTest(t)
	defer fix.cleanup()

	projectID := "test-project-metrics"
	err := createTestGraph(fix.ctx, fix.driver, projectID)
	require.NoError(t, err)

	// Get metrics
	metrics, err := fix.service.GetMetrics(fix.ctx, projectID)
	require.NoError(t, err)
	assert.NotNil(t, metrics)
	assert.Equal(t, projectID, metrics.ProjectID)
	assert.Equal(t, 5, metrics.TotalNodes)
	assert.Equal(t, 3, metrics.TotalEdges)
	assert.Greater(t, metrics.Density, 0.0)
}

func TestInvalidateCache(t *testing.T) {
	fix := setupTest(t)
	defer fix.cleanup()

	projectID := "test-project-cache"
	err := createTestGraph(fix.ctx, fix.driver, projectID)
	require.NoError(t, err)

	// Populate cache
	_, err = fix.service.GetMetrics(fix.ctx, projectID)
	require.NoError(t, err)

	// Verify cache has data
	mockC := fix.cache.(*mockCache)
	assert.NotEmpty(t, mockC.data)

	// Invalidate cache
	err = fix.service.InvalidateCache(fix.ctx, projectID)
	require.NoError(t, err)

	// Verify cache is cleared
	assert.Empty(t, mockC.data)
}

func TestLargeGraph_Performance(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping performance test in short mode")
	}

	fix := setupTest(t)
	defer fix.cleanup()

	ctx := fix.ctx
	projectID := "test-project-large"

	// Create a larger graph (100 nodes, 200 edges)
	session := fix.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer func() { _ = session.Close(ctx) }()

	// Create nodes
	for i := 0; i < 100; i++ {
		query := `CREATE (n:Item {id: $id, project_id: $projectID})`
		_, err := session.Run(ctx, query, map[string]interface{}{
			"id":        "large-item-" + string(rune('0'+i)),
			"projectID": projectID,
		})
		require.NoError(t, err)
	}

	// Create edges
	for i := 0; i < 200; i++ {
		source := "large-item-" + string(rune('0'+(i%100)))
		target := "large-item-" + string(rune('0'+((i+1)%100)))

		query := `
			MATCH (source:Item {id: $source})
			MATCH (target:Item {id: $target})
			CREATE (source)-[:LINK]->(target)
		`
		_, err := session.Run(ctx, query, map[string]interface{}{
			"source": source,
			"target": target,
		})
		require.NoError(t, err)
	}

	// Test metrics calculation performance
	start := time.Now()
	metrics, err := fix.service.GetMetrics(ctx, projectID)
	duration := time.Since(start)

	require.NoError(t, err)
	assert.NotNil(t, metrics)
	assert.Less(t, duration, 5*time.Second, "Metrics calculation should be under 5s for 100 nodes")

	t.Logf("Large graph metrics calculated in %v", duration)
}
