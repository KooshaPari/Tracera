package graph

import (
	"context"
	"os"
	"testing"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/uuidutil"
)

// setupGraphTestDB creates a test database with sample graph data
func setupGraphTestDB(t *testing.T) (*pgxpool.Pool, string) {
	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		t.Skip("DATABASE_URL not set, skipping graph integration tests")
	}

	pool, err := pgxpool.New(context.Background(), databaseURL)
	require.NoError(t, err)

	// Create a test project
	ctx := context.Background()

	queries := db.New(pool)
	project, err := queries.CreateProject(ctx, db.CreateProjectParams{
		Name:        "test-graph-" + uuid.New().String(),
		Description: pgtype.Text{String: "Test graph project", Valid: true},
	})
	require.NoError(t, err)

	return pool, uuidutil.UUIDToString(project.ID)
}

// cleanupGraphTestDB removes test data
func cleanupGraphTestDB(t *testing.T, pool *pgxpool.Pool, projectID string) {
	t.Helper()
	ctx := context.Background()
	queries := db.New(pool)

	projectUUID, err := uuidutil.StringToUUID(projectID)
	if err == nil {
		require.NoError(t, queries.DeleteProject(ctx, projectUUID))
	}
	pool.Close()
}

// createTestItem creates a test item
func createTestItem(t *testing.T, queries *db.Queries, projectID, title string) string {
	projectUUID, err := uuidutil.StringToUUID(projectID)
	require.NoError(t, err)

	item, err := queries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   projectUUID,
		Title:       title,
		Description: pgtype.Text{String: "Test item", Valid: true},
		Type:        "task",
		Status:      "open",
		Priority:    pgtype.Int4{Int32: 2, Valid: true}, // medium = 2
	})
	require.NoError(t, err)

	return uuidutil.UUIDToString(item.ID)
}

// createTestLink creates a link between items
func createTestLink(t *testing.T, queries *db.Queries, _ string, sourceID, targetID string) {
	sourceUUID, err := uuidutil.StringToUUID(sourceID)
	require.NoError(t, err)

	targetUUID, err := uuidutil.StringToUUID(targetID)
	require.NoError(t, err)

	_, err = queries.CreateLink(context.Background(), db.CreateLinkParams{
		SourceID: sourceUUID,
		TargetID: targetUUID,
		Type:     "depends_on",
	})
	require.NoError(t, err)
}

type graphTestItems struct {
	itemA string
	itemB string
	itemC string
	itemD string
}

func createTestItemsABCD(t *testing.T, queries *db.Queries, projectID string) graphTestItems {
	return graphTestItems{
		itemA: createTestItem(t, queries, projectID, "Item A"),
		itemB: createTestItem(t, queries, projectID, "Item B"),
		itemC: createTestItem(t, queries, projectID, "Item C"),
		itemD: createTestItem(t, queries, projectID, "Item D"),
	}
}

// TestBFS tests breadth-first search
func TestBFS(t *testing.T) {
	t.Skip("Integration test - requires PostgreSQL with proper schema")
	t.Skip("Integration test - requires PostgreSQL with proper schema")
	pool, projectID := setupGraphTestDB(t)
	defer cleanupGraphTestDB(t, pool, projectID)

	queries := db.New(pool)
	graph := NewGraph(pool)

	// Create graph: A -> B -> C
	//                A -> D
	items := createTestItemsABCD(t, queries, projectID)

	createTestLink(t, queries, projectID, items.itemA, items.itemB)
	createTestLink(t, queries, projectID, items.itemB, items.itemC)
	createTestLink(t, queries, projectID, items.itemA, items.itemD)

	// Test forward BFS from A
	result, err := graph.BFS(context.Background(), items.itemA, "forward", 0)
	require.NoError(t, err)

	assert.Contains(t, result.Nodes, items.itemA)
	assert.Contains(t, result.Nodes, items.itemB)
	assert.Contains(t, result.Nodes, items.itemC)
	assert.Contains(t, result.Nodes, items.itemD)

	// Test depth limit
	result, err = graph.BFS(context.Background(), items.itemA, "forward", 1)
	require.NoError(t, err)

	assert.Contains(t, result.Nodes, items.itemA)
	assert.Contains(t, result.Nodes, items.itemB)
	assert.Contains(t, result.Nodes, items.itemD)
	assert.NotContains(t, result.Nodes, items.itemC) // Too deep

	// Test backward BFS from C
	result, err = graph.BFS(context.Background(), items.itemC, "backward", 0)
	require.NoError(t, err)

	assert.Contains(t, result.Nodes, items.itemC)
	assert.Contains(t, result.Nodes, items.itemB)
	assert.Contains(t, result.Nodes, items.itemA)
}

// TestDFS tests depth-first search
func TestDFS(t *testing.T) {
	t.Skip("Integration test - requires PostgreSQL with proper schema")
	pool, projectID := setupGraphTestDB(t)
	defer cleanupGraphTestDB(t, pool, projectID)

	queries := db.New(pool)
	graph := NewGraph(pool)

	// Create tree: A -> B -> C
	//                   B -> D
	items := createTestItemsABCD(t, queries, projectID)

	createTestLink(t, queries, projectID, items.itemA, items.itemB)
	createTestLink(t, queries, projectID, items.itemB, items.itemC)
	createTestLink(t, queries, projectID, items.itemB, items.itemD)

	// Test DFS
	result, err := graph.DFS(context.Background(), items.itemA, "forward", 0)
	require.NoError(t, err)

	assert.Len(t, result.Nodes, 4)
	assert.Contains(t, result.Nodes, items.itemA)
	assert.Contains(t, result.Nodes, items.itemB)
	assert.Contains(t, result.Nodes, items.itemC)
	assert.Contains(t, result.Nodes, items.itemD)
}

// TestFindPath tests pathfinding
func TestFindPath(t *testing.T) {
	t.Skip("Integration test - requires PostgreSQL with proper schema")
	pool, projectID := setupGraphTestDB(t)
	defer cleanupGraphTestDB(t, pool, projectID)

	queries := db.New(pool)
	graph := NewGraph(pool)

	// Create path: A -> B -> C -> D
	items := createTestItemsABCD(t, queries, projectID)

	createTestLink(t, queries, projectID, items.itemA, items.itemB)
	createTestLink(t, queries, projectID, items.itemB, items.itemC)
	createTestLink(t, queries, projectID, items.itemC, items.itemD)

	// Find path from A to D
	result, err := graph.FindPath(context.Background(), items.itemA, items.itemD)
	require.NoError(t, err)

	assert.True(t, result.Found)
	assert.Equal(t, []string{items.itemA, items.itemB, items.itemC, items.itemD}, result.Path)
	assert.Len(t, result.Links, 3)
	assert.Len(t, result.Items, 4)
}

// TestFindPathNoPath tests pathfinding when no path exists
func TestFindPathNoPath(t *testing.T) {
	t.Skip("Integration test - requires PostgreSQL with proper schema")
	pool, projectID := setupGraphTestDB(t)
	defer cleanupGraphTestDB(t, pool, projectID)

	queries := db.New(pool)
	graph := NewGraph(pool)

	// Create disconnected items
	items := createTestItemsABCD(t, queries, projectID)

	// Try to find path (should fail)
	result, err := graph.FindPath(context.Background(), items.itemA, items.itemB)
	require.NoError(t, err)

	assert.False(t, result.Found)
	assert.Empty(t, result.Path)
}

// TestDetectCycles tests cycle detection
func TestDetectCycles(t *testing.T) {
	t.Skip("Integration test - requires PostgreSQL with proper schema")
	pool, projectID := setupGraphTestDB(t)
	defer cleanupGraphTestDB(t, pool, projectID)

	queries := db.New(pool)
	graph := NewGraph(pool)

	// Create cycle: A -> B -> C -> A
	itemA := createTestItem(t, queries, projectID, "Item A")
	itemB := createTestItem(t, queries, projectID, "Item B")
	itemC := createTestItem(t, queries, projectID, "Item C")

	createTestLink(t, queries, projectID, itemA, itemB)
	createTestLink(t, queries, projectID, itemB, itemC)
	createTestLink(t, queries, projectID, itemC, itemA) // Creates cycle

	// Detect cycles
	cycles, err := graph.DetectCycles(context.Background(), projectID)
	require.NoError(t, err)

	assert.NotEmpty(t, cycles)

	// Verify cycle contains our items
	if len(cycles) > 0 {
		cycle := cycles[0]
		assert.Contains(t, cycle.Cycle, itemA)
		assert.Contains(t, cycle.Cycle, itemB)
		assert.Contains(t, cycle.Cycle, itemC)
	}
}

// TestTopologicalSort tests topological sorting
func TestTopologicalSort(t *testing.T) {
	t.Skip("Integration test - requires PostgreSQL with proper schema")
	pool, projectID := setupGraphTestDB(t)
	defer cleanupGraphTestDB(t, pool, projectID)

	queries := db.New(pool)
	graph := NewGraph(pool)

	// Create DAG: A -> B -> D
	//             A -> C -> D
	itemA := createTestItem(t, queries, projectID, "Item A")
	itemB := createTestItem(t, queries, projectID, "Item B")
	itemC := createTestItem(t, queries, projectID, "Item C")
	itemD := createTestItem(t, queries, projectID, "Item D")

	createTestLink(t, queries, projectID, itemA, itemB)
	createTestLink(t, queries, projectID, itemA, itemC)
	createTestLink(t, queries, projectID, itemB, itemD)
	createTestLink(t, queries, projectID, itemC, itemD)

	// Topological sort
	sorted, success, err := graph.TopologicalSort(context.Background(), projectID)
	require.NoError(t, err)
	assert.True(t, success)

	// Find positions in sorted order
	positions := make(map[string]int)
	for i, id := range sorted {
		positions[id] = i
	}

	// Verify ordering: A before B, A before C, B before D, C before D
	assert.Less(t, positions[itemA], positions[itemB])
	assert.Less(t, positions[itemA], positions[itemC])
	assert.Less(t, positions[itemB], positions[itemD])
	assert.Less(t, positions[itemC], positions[itemD])
}

// TestTopologicalSortWithCycleDetection tests topological sort fails with cycles
func TestTopologicalSortWithCycleDetection(t *testing.T) {
	t.Skip("Integration test - requires PostgreSQL with proper schema")
	pool, projectID := setupGraphTestDB(t)
	defer cleanupGraphTestDB(t, pool, projectID)

	queries := db.New(pool)
	graph := NewGraph(pool)

	// Create cycle
	itemA := createTestItem(t, queries, projectID, "Item A")
	itemB := createTestItem(t, queries, projectID, "Item B")

	createTestLink(t, queries, projectID, itemA, itemB)
	createTestLink(t, queries, projectID, itemB, itemA) // Creates cycle

	// Topological sort should fail
	_, success, err := graph.TopologicalSort(context.Background(), projectID)
	require.NoError(t, err)
	assert.False(t, success)
}

// TestGetAncestors tests ancestor retrieval
func TestGetAncestors(t *testing.T) {
	runTraversalTest(
		t,
		func(items graphTestItems, queries *db.Queries, projectID string) {
			createTestLink(t, queries, projectID, items.itemA, items.itemB)
			createTestLink(t, queries, projectID, items.itemB, items.itemC)
			createTestLink(t, queries, projectID, items.itemC, items.itemD)
		},
		func(items graphTestItems) string { return items.itemD },
		func(ctx context.Context, graph *Graph, start string) (*Result, error) {
			return graph.GetAncestors(ctx, start, 0)
		},
		func(items graphTestItems) []string {
			return []string{items.itemD, items.itemC, items.itemB, items.itemA}
		},
	)
}

// TestGetDescendants tests descendant retrieval
func TestGetDescendants(t *testing.T) {
	runTraversalTest(
		t,
		func(items graphTestItems, queries *db.Queries, projectID string) {
			createTestLink(t, queries, projectID, items.itemA, items.itemB)
			createTestLink(t, queries, projectID, items.itemB, items.itemC)
			createTestLink(t, queries, projectID, items.itemB, items.itemD)
		},
		func(items graphTestItems) string { return items.itemA },
		func(ctx context.Context, graph *Graph, start string) (*Result, error) {
			return graph.GetDescendants(ctx, start, 0)
		},
		func(items graphTestItems) []string {
			return []string{items.itemA, items.itemB, items.itemC, items.itemD}
		},
	)
}

func runTraversalTest(
	t *testing.T,
	linkSetup func(graphTestItems, *db.Queries, string),
	start func(graphTestItems) string,
	traverse func(context.Context, *Graph, string) (*Result, error),
	expected func(graphTestItems) []string,
) {
	t.Helper()
	t.Skip("Integration test - requires PostgreSQL with proper schema")

	pool, projectID := setupGraphTestDB(t)
	defer cleanupGraphTestDB(t, pool, projectID)

	queries := db.New(pool)
	graph := NewGraph(pool)

	items := createTestItemsABCD(t, queries, projectID)
	linkSetup(items, queries, projectID)

	result, err := traverse(context.Background(), graph, start(items))
	require.NoError(t, err)

	for _, nodeID := range expected(items) {
		assert.Contains(t, result.Nodes, nodeID)
	}
}

// TestImpactAnalysis tests impact analysis
func TestImpactAnalysis(t *testing.T) {
	t.Skip("Integration test - requires PostgreSQL with proper schema")
	pool, projectID := setupGraphTestDB(t)
	defer cleanupGraphTestDB(t, pool, projectID)

	queries := db.New(pool)
	graph := NewGraph(pool)

	// Create dependency chain
	itemA := createTestItem(t, queries, projectID, "Item A")
	itemB := createTestItem(t, queries, projectID, "Item B")
	itemC := createTestItem(t, queries, projectID, "Item C")

	createTestLink(t, queries, projectID, itemA, itemB)
	createTestLink(t, queries, projectID, itemB, itemC)

	// Impact analysis: changing A affects B and C
	result, err := graph.GetImpactAnalysis(context.Background(), itemA, 0)
	require.NoError(t, err)

	assert.Contains(t, result.Nodes, itemB)
	assert.Contains(t, result.Nodes, itemC)
}

// TestGetOrphanItems tests finding orphaned items
func TestGetOrphanItems(t *testing.T) {
	t.Skip("Integration test - requires PostgreSQL with proper schema")
	pool, projectID := setupGraphTestDB(t)
	defer cleanupGraphTestDB(t, pool, projectID)

	queries := db.New(pool)
	graph := NewGraph(pool)

	// Create connected items
	itemA := createTestItem(t, queries, projectID, "Item A")
	itemB := createTestItem(t, queries, projectID, "Item B")
	createTestLink(t, queries, projectID, itemA, itemB)

	// Create orphan
	itemOrphan := createTestItem(t, queries, projectID, "Orphan")

	// Find orphans
	orphans, err := graph.GetOrphanItems(context.Background(), projectID)
	require.NoError(t, err)

	// Check if orphan is in results
	found := false
	for _, item := range orphans {
		if uuidutil.UUIDToString(item.ID) == itemOrphan {
			found = true
			break
		}
	}
	assert.True(t, found, "Orphan item should be detected")
}

// TestGetSubgraph tests subgraph extraction
func TestGetSubgraph(t *testing.T) {
	t.Skip("Integration test - requires PostgreSQL with proper schema")
	pool, projectID := setupGraphTestDB(t)
	defer cleanupGraphTestDB(t, pool, projectID)

	queries := db.New(pool)
	graph := NewGraph(pool)

	// Create graph
	itemA := createTestItem(t, queries, projectID, "Item A")
	itemB := createTestItem(t, queries, projectID, "Item B")
	itemC := createTestItem(t, queries, projectID, "Item C")
	itemD := createTestItem(t, queries, projectID, "Item D")

	createTestLink(t, queries, projectID, itemA, itemB)
	createTestLink(t, queries, projectID, itemB, itemC)
	createTestLink(t, queries, projectID, itemC, itemD)

	// Get subgraph of A, B, C (excluding D)
	result, err := graph.GetSubgraph(context.Background(), []string{itemA, itemB, itemC})
	require.NoError(t, err)

	assert.Contains(t, result.Nodes, itemA)
	assert.Contains(t, result.Nodes, itemB)
	assert.Contains(t, result.Nodes, itemC)
	assert.NotContains(t, result.Nodes, itemD)
}

// TestComplexGraph tests a complex graph scenario
func TestComplexGraph(t *testing.T) {
	t.Skip("Integration test - requires PostgreSQL with proper schema")
	pool, projectID := setupGraphTestDB(t)
	defer cleanupGraphTestDB(t, pool, projectID)

	queries := db.New(pool)
	graph := NewGraph(pool)

	// Create complex graph
	items := make(map[string]string)
	for i := 'A'; i <= 'F'; i++ {
		items[string(i)] = createTestItem(t, queries, projectID, "Item "+string(i))
	}

	// Create links: A->B, A->C, B->D, C->D, D->E, E->F
	createTestLink(t, queries, projectID, items["A"], items["B"])
	createTestLink(t, queries, projectID, items["A"], items["C"])
	createTestLink(t, queries, projectID, items["B"], items["D"])
	createTestLink(t, queries, projectID, items["C"], items["D"])
	createTestLink(t, queries, projectID, items["D"], items["E"])
	createTestLink(t, queries, projectID, items["E"], items["F"])

	// Test various operations
	result, err := graph.BFS(context.Background(), items["A"], "forward", 0)
	require.NoError(t, err)
	assert.Len(t, result.Nodes, 6)

	// Find path A->F
	path, err := graph.FindPath(context.Background(), items["A"], items["F"])
	require.NoError(t, err)
	assert.True(t, path.Found)
	assert.GreaterOrEqual(t, len(path.Path), 4) // At least A->?->?->F

	// Topological sort should succeed (no cycles)
	sorted, success, err := graph.TopologicalSort(context.Background(), projectID)
	require.NoError(t, err)
	assert.True(t, success)
	assert.Len(t, sorted, 6)
}

// BenchmarkBFSAlgorithms benchmarks BFS performance
func BenchmarkBFSAlgorithms(b *testing.B) {
	pool, err := pgxpool.New(context.Background(), os.Getenv("DATABASE_URL"))
	if err != nil {
		b.Skip("DATABASE_URL not set")
	}
	defer func() {
		pool.Close()
	}()

	// Create test graph
	queries := db.New(pool)
	project, err := queries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "bench-" + uuid.New().String(),
		Description: pgtype.Text{String: "Benchmark project", Valid: true},
	})
	require.NoError(b, err)

	// Create chain of 100 items
	var prevID pgtype.UUID
	var startID string
	for i := 0; i < 100; i++ {
		item, err := queries.CreateItem(context.Background(), db.CreateItemParams{
			ProjectID: project.ID,
			Title:     "Item",
			Type:      "task",
			Status:    "open",
			Priority:  pgtype.Int4{Int32: 2, Valid: true},
		})
		require.NoError(b, err)
		if i == 0 {
			startID = uuidutil.UUIDToString(item.ID)
		}
		if i > 0 {
			_, err := queries.CreateLink(context.Background(), db.CreateLinkParams{
				SourceID: prevID,
				TargetID: item.ID,
				Type:     "depends_on",
			})
			require.NoError(b, err)
		}
		prevID = item.ID
	}

	graph := NewGraph(pool)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := graph.BFS(context.Background(), startID, "forward", 0)
		require.NoError(b, err)
	}
}
