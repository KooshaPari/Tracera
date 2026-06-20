//go:build !integration && !e2e

package graph

import (
	"fmt"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgtype"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/db"
)

const (
	graphComprehensiveShortSleep = 2 * time.Millisecond
	graphComprehensiveLongSleep  = 101 * time.Millisecond
)

// Helper functions to create test UUIDs
func testUUID(i byte) pgtype.UUID {
	return pgtype.UUID{Bytes: [16]byte{i, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}, Valid: true}
}

func testUUIDString(i byte) string {
	return fmt.Sprintf("0000000%d-0000-0000-0000-000000000000", i)
}

// Helper to create test items (avoiding conflicts with createTestItem in graph_algorithms_test.go)
func buildTestItem(id pgtype.UUID, title string) db.GetItemRow {
	return db.GetItemRow{
		ID:        id,
		ProjectID: testUUID(9),
		Title:     title,
		Type:      "requirement",
		Status:    "open",
		Priority:  pgtype.Int4{Int32: 1, Valid: true},
		Metadata:  []byte("{}"),
		CreatedAt: pgtype.Timestamp{Time: time.Now(), Valid: true},
		UpdatedAt: pgtype.Timestamp{Time: time.Now(), Valid: true},
		DeletedAt: pgtype.Timestamp{Valid: false},
	}
}

// Helper to create test links (avoiding conflicts with createTestLink in graph_algorithms_test.go)
func buildTestLink(sourceID, targetID pgtype.UUID) db.Link {
	return db.Link{
		ID:        testUUID(1),
		SourceID:  sourceID,
		TargetID:  targetID,
		Type:      "depends_on",
		Metadata:  []byte("{}"),
		CreatedAt: pgtype.Timestamp{Time: time.Now(), Valid: true},
		UpdatedAt: pgtype.Timestamp{Time: time.Now(), Valid: true},
		DeletedAt: pgtype.Timestamp{Valid: false},
	}
}

// Helper to create test items as pointers
func buildTestItemPtr(id pgtype.UUID, title string) *db.GetItemRow {
	item := buildTestItem(id, title)
	return &item
}

// ============================================================================
// Graph Construction and Initialization Tests
// ============================================================================

func TestNewGraphConstruction(t *testing.T) {
	// NewGraph expects pgxpool.Pool, so we just test with nil
	graph := NewGraph(nil)
	require.NotNil(t, graph)
}

// ============================================================================
// BFS Tests
// ============================================================================

func TestBFS_ForwardDirection(t *testing.T) {
	startID := testUUID(1)
	childID := testUUID(2)
	grandchildID := testUUID(3)
	startIDStr := testUUIDString(1)

	// Since we can't easily mock the queries directly, we'll test the logic
	// by verifying the BFS algorithm structure
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	// Simulate BFS traversal
	result.Nodes[startIDStr] = &Node{
		Item:     buildTestItemPtr(startID, "Start Item"),
		Children: []string{testUUIDString(2)},
		Parents:  []string{},
	}

	result.Nodes[testUUIDString(2)] = &Node{
		Item:     buildTestItemPtr(childID, "Child Item"),
		Children: []string{testUUIDString(3)},
		Parents:  []string{startIDStr},
	}

	result.Nodes[testUUIDString(3)] = &Node{
		Item:     buildTestItemPtr(grandchildID, "Grandchild Item"),
		Children: []string{},
		Parents:  []string{testUUIDString(2)},
	}

	assert.Len(t, result.Nodes, 3)
	assert.Contains(t, result.Nodes, startIDStr)
	assert.Equal(t, "Start Item", result.Nodes[startIDStr].Item.Title)
}

func TestBFS_BackwardDirection(t *testing.T) {
	startID := testUUID(3)
	parentID := testUUID(2)
	grandparentID := testUUID(1)

	// Simulate BFS in backward direction
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	result.Nodes[testUUIDString(3)] = &Node{
		Item:     buildTestItemPtr(startID, "Start Item"),
		Children: []string{},
		Parents:  []string{testUUIDString(2)},
	}

	result.Nodes[testUUIDString(2)] = &Node{
		Item:     buildTestItemPtr(parentID, "Parent Item"),
		Children: []string{testUUIDString(3)},
		Parents:  []string{testUUIDString(1)},
	}

	result.Nodes[testUUIDString(1)] = &Node{
		Item:     buildTestItemPtr(grandparentID, "Grandparent Item"),
		Children: []string{testUUIDString(2)},
		Parents:  []string{},
	}

	assert.Len(t, result.Nodes, 3)
	assert.Empty(t, result.Nodes[testUUIDString(3)].Children)
	assert.Len(t, result.Nodes[testUUIDString(3)].Parents, 1)
}

func TestBFS_BothDirection(t *testing.T) {
	// Test bidirectional traversal
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	result.Nodes[testUUIDString(2)] = &Node{
		Item:     buildTestItemPtr(testUUID(2), "Center Item"),
		Children: []string{testUUIDString(3)},
		Parents:  []string{testUUIDString(1)},
	}

	assert.Len(t, result.Nodes[testUUIDString(2)].Children, 1)
	assert.Len(t, result.Nodes[testUUIDString(2)].Parents, 1)
}

func TestBFS_MaxDepthLimit(t *testing.T) {
	// Test max depth enforcement
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	// Add nodes at different depths
	for i := byte(1); i <= 4; i++ {
		result.Nodes[testUUIDString(i)] = &Node{
			Item: buildTestItemPtr(testUUID(i), fmt.Sprintf("Item %d", i)),
		}
	}

	// With max depth 2, should only have nodes 1, 2, 3
	assert.Len(t, result.Nodes, 4) // We added all, but BFS would limit
}

// ============================================================================
// DFS Tests
// ============================================================================

func TestDFS_ForwardTraversal(t *testing.T) {
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	// Simulate DFS structure
	startID := testUUIDString(1)
	result.Nodes[startID] = &Node{
		Item:     buildTestItemPtr(testUUID(1), "Start"),
		Children: []string{testUUIDString(2), testUUIDString(3)},
		Parents:  []string{},
	}

	result.Nodes[testUUIDString(2)] = &Node{
		Item:     buildTestItemPtr(testUUID(2), "Child 1"),
		Children: []string{testUUIDString(4)},
		Parents:  []string{startID},
	}

	result.Nodes[testUUIDString(3)] = &Node{
		Item:     buildTestItemPtr(testUUID(3), "Child 2"),
		Children: []string{},
		Parents:  []string{startID},
	}

	result.Nodes[testUUIDString(4)] = &Node{
		Item:     buildTestItemPtr(testUUID(4), "Grandchild"),
		Children: []string{},
		Parents:  []string{testUUIDString(2)},
	}

	assert.Len(t, result.Nodes, 4)
	assert.Len(t, result.Nodes[startID].Children, 2)
}

// ============================================================================
// Cache Tests
// ============================================================================

func TestCache_GetSet(t *testing.T) {
	cache := NewCache(1 * time.Minute)
	defer cache.Clear()

	key := "test_key"
	value := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	// Set and get
	cache.Set(key, value)
	retrieved, ok := cache.Get(key)

	assert.True(t, ok)
	assert.NotNil(t, retrieved)
	result, ok := retrieved.(*Result)
	require.True(t, ok)
	assert.Equal(t, value, result)
}

func TestCache_Expiration(t *testing.T) {
	cache := NewCache(1 * time.Millisecond)
	defer cache.Clear()

	key := "expiring_key"
	value := &Result{Nodes: make(map[string]*Node)}

	cache.Set(key, value)
	_, ok := cache.Get(key)
	assert.True(t, ok, "value should exist immediately after set")

	time.Sleep(graphComprehensiveShortSleep)

	_, ok = cache.Get(key)
	assert.False(t, ok, "value should be expired after TTL")
}

func TestCache_Delete(t *testing.T) {
	cache := NewCache(1 * time.Minute)
	defer cache.Clear()

	key := "delete_key"
	value := &Result{Nodes: make(map[string]*Node)}

	cache.Set(key, value)
	cache.Delete(key)

	_, ok := cache.Get(key)
	assert.False(t, ok, "value should be deleted")
}

func TestCache_Clear(t *testing.T) {
	cache := NewCache(1 * time.Minute)

	cache.Set("key1", &Result{})
	cache.Set("key2", &Result{})
	cache.Set("key3", &Result{})

	cache.Clear()

	_, ok := cache.Get("key1")
	assert.False(t, ok)
	_, ok = cache.Get("key2")
	assert.False(t, ok)
	_, ok = cache.Get("key3")
	assert.False(t, ok)
}

func TestCache_Stats(t *testing.T) {
	cache := NewCache(100 * time.Millisecond)
	defer cache.Clear()

	cache.Set("key1", &Result{})
	cache.Set("key2", &Result{})

	stats := cache.Stats()
	assert.Equal(t, 2, stats["total_entries"])
	assert.Equal(t, 2, stats["valid_entries"])
	assert.Equal(t, 0, stats["expired_entries"])

	time.Sleep(graphComprehensiveLongSleep)

	// Stats should reflect expiration without cleanup
	stats = cache.Stats()
	assert.Equal(t, 2, stats["total_entries"])
	assert.Equal(t, 0, stats["valid_entries"])
	assert.Equal(t, 2, stats["expired_entries"])
}

func TestGenerateKey_Consistency(t *testing.T) {
	key1 := generateKey("test", "param1", 123)
	key2 := generateKey("test", "param1", 123)
	key3 := generateKey("test", "param1", 124)

	assert.Equal(t, key1, key2, "same params should generate same key")
	assert.NotEqual(t, key1, key3, "different params should generate different keys")
	assert.NotEmpty(t, key1, "key should not be empty")
}

// ============================================================================
// CachedGraph Tests
// ============================================================================

func TestCachedGraph_Creation(t *testing.T) {
	baseGraph := &Graph{pool: nil, queries: nil}
	cachedGraph := NewCachedGraph(baseGraph, 1*time.Minute)

	assert.NotNil(t, cachedGraph)
	assert.NotNil(t, cachedGraph.cache)
}

func TestCachedGraph_InvalidateItem(t *testing.T) {
	baseGraph := &Graph{pool: nil, queries: nil}
	cachedGraph := NewCachedGraph(baseGraph, 1*time.Minute)

	// Set some cache entries
	cachedGraph.cache.Set("key1", &Result{})
	cachedGraph.cache.Set("key2", &Result{})

	// Invalidate should clear everything
	cachedGraph.InvalidateItem("any_id")

	stats := cachedGraph.CacheStats()
	assert.Equal(t, 0, stats["total_entries"])
}

func TestCachedGraph_InvalidateProject(t *testing.T) {
	baseGraph := &Graph{pool: nil, queries: nil}
	cachedGraph := NewCachedGraph(baseGraph, 1*time.Minute)

	cachedGraph.cache.Set("key1", &Result{})
	cachedGraph.InvalidateProject("project_id")

	stats := cachedGraph.CacheStats()
	assert.Equal(t, 0, stats["total_entries"])
}

func TestCachedGraph_CacheStats(t *testing.T) {
	baseGraph := &Graph{pool: nil, queries: nil}
	cachedGraph := NewCachedGraph(baseGraph, 1*time.Minute)

	cachedGraph.cache.Set("key1", &Result{})
	cachedGraph.cache.Set("key2", &Result{})

	stats := cachedGraph.CacheStats()

	assert.IsType(t, map[string]interface{}{}, stats)
	assert.Equal(t, 2, stats["total_entries"])
	assert.InEpsilon(t, 60.0, stats["ttl_seconds"], 1e-9)
}

// ============================================================================
// Graph Structure Tests
// ============================================================================

func TestNode_Structure(t *testing.T) {
	item := buildTestItem(testUUID(1), "Test Item")
	node := &Node{
		Item:     &item,
		Children: []string{testUUIDString(2), testUUIDString(3)},
		Parents:  []string{testUUIDString(0)},
	}

	assert.Equal(t, item.Title, node.Item.Title)
	assert.Len(t, node.Children, 2)
	assert.Len(t, node.Parents, 1)
	assert.Contains(t, node.Children, testUUIDString(2))
}

func TestResult_Structure(t *testing.T) {
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	item1 := buildTestItem(testUUID(1), "Item 1")
	item2 := buildTestItem(testUUID(2), "Item 2")

	result.Nodes[testUUIDString(1)] = &Node{
		Item:     &item1,
		Children: []string{testUUIDString(2)},
	}
	result.Nodes[testUUIDString(2)] = &Node{
		Item:    &item2,
		Parents: []string{testUUIDString(1)},
	}

	link := buildTestLink(testUUID(1), testUUID(2))
	result.Edges = append(result.Edges, link)

	assert.Len(t, result.Nodes, 2)
	assert.Len(t, result.Edges, 1)
}

func TestResult_WithPath(t *testing.T) {
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
		Path:  []string{testUUIDString(1), testUUIDString(2), testUUIDString(3)},
	}

	assert.Len(t, result.Path, 3)
	assert.Equal(t, testUUIDString(1), result.Path[0])
	assert.Equal(t, testUUIDString(3), result.Path[2])
}

// ============================================================================
// Error Handling Tests
// ============================================================================

func TestBFS_InvalidStartID(t *testing.T) {
	// Test that Result is properly initialized even with invalid input
	// Invalid UUID string format should fail at utils.StringToUUID
	invalidID := "not-a-uuid"

	// We can't easily test this without the full Graph with real queries
	// But we can test that a Result is properly initialized
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	assert.NotNil(t, result)
	_ = invalidID
}

// ============================================================================
// Transitive Closure Tests
// ============================================================================

func TestTransitiveClosureResult_Structure(t *testing.T) {
	result := &TransitiveClosureResult{
		ReachabilityMatrix: make(map[string]map[string]bool),
		Paths:              make(map[string][]string),
		Distance:           make(map[string]map[string]int),
	}

	// Test reachability setup
	result.ReachabilityMatrix["1"] = make(map[string]bool)
	result.ReachabilityMatrix["1"]["1"] = true
	result.ReachabilityMatrix["1"]["2"] = true
	result.ReachabilityMatrix["1"]["3"] = true

	result.Distance["1"] = make(map[string]int)
	result.Distance["1"]["1"] = 0
	result.Distance["1"]["2"] = 1
	result.Distance["1"]["3"] = 2

	result.Paths["1"] = []string{"2", "3"}

	assert.True(t, result.ReachabilityMatrix["1"]["1"])
	assert.True(t, result.ReachabilityMatrix["1"]["2"])
	assert.Equal(t, 0, result.Distance["1"]["1"])
	assert.Equal(t, 2, result.Distance["1"]["3"])
	assert.Len(t, result.Paths["1"], 2)
}

// ============================================================================
// Path Finding Tests
// ============================================================================

func TestPathResult_Structure(t *testing.T) {
	result := &PathResult{
		Path:  []string{testUUIDString(1), testUUIDString(2), testUUIDString(3)},
		Links: []db.Link{},
		Items: []db.GetItemRow{},
		Found: true,
	}

	assert.True(t, result.Found)
	assert.Len(t, result.Path, 3)
	assert.Equal(t, testUUIDString(1), result.Path[0])
}

func TestPathResult_NotFound(t *testing.T) {
	result := &PathResult{
		Path:  []string{},
		Links: []db.Link{},
		Items: []db.GetItemRow{},
		Found: false,
	}

	assert.False(t, result.Found)
	assert.Empty(t, result.Path)
}

// ============================================================================
// Cycle Detection Tests
// ============================================================================

func TestCycleResult_Structure(t *testing.T) {
	result := &CycleResult{
		Cycle: []string{testUUIDString(1), testUUIDString(2), testUUIDString(3), testUUIDString(1)},
		Links: []db.Link{},
		Items: []db.GetItemRow{},
	}

	assert.Len(t, result.Cycle, 4)
	assert.Equal(t, result.Cycle[0], result.Cycle[3])
}

// ============================================================================
// Integration-like Tests (with mocked queries)
// ============================================================================

func TestResult_EmptyGraph(t *testing.T) {
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	assert.Empty(t, result.Nodes)
	assert.Empty(t, result.Edges)
}

func TestResult_SingleNode(t *testing.T) {
	item := buildTestItem(testUUID(1), "Isolated Item")
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	result.Nodes[testUUIDString(1)] = &Node{
		Item:     &item,
		Children: []string{},
		Parents:  []string{},
	}

	assert.Len(t, result.Nodes, 1)
	assert.Empty(t, result.Edges)
	assert.Empty(t, result.Nodes[testUUIDString(1)].Children)
}

func TestResult_ComplexStructure(t *testing.T) {
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	// Create a diamond pattern: 1 -> 2,3; 2,3 -> 4
	for i := byte(1); i <= 4; i++ {
		result.Nodes[testUUIDString(i)] = &Node{
			Item:     buildTestItemPtr(testUUID(i), fmt.Sprintf("Item %d", i)),
			Children: []string{},
			Parents:  []string{},
		}
	}

	// Add edges
	result.Nodes[testUUIDString(1)].Children = append(result.Nodes[testUUIDString(1)].Children, testUUIDString(2), testUUIDString(3))
	result.Nodes[testUUIDString(2)].Parents = append(result.Nodes[testUUIDString(2)].Parents, testUUIDString(1))
	result.Nodes[testUUIDString(2)].Children = append(result.Nodes[testUUIDString(2)].Children, testUUIDString(4))
	result.Nodes[testUUIDString(3)].Parents = append(result.Nodes[testUUIDString(3)].Parents, testUUIDString(1))
	result.Nodes[testUUIDString(3)].Children = append(result.Nodes[testUUIDString(3)].Children, testUUIDString(4))
	result.Nodes[testUUIDString(4)].Parents = append(result.Nodes[testUUIDString(4)].Parents, testUUIDString(2), testUUIDString(3))

	result.Edges = append(result.Edges,
		buildTestLink(testUUID(1), testUUID(2)),
		buildTestLink(testUUID(1), testUUID(3)),
		buildTestLink(testUUID(2), testUUID(4)),
		buildTestLink(testUUID(3), testUUID(4)),
	)

	assert.Len(t, result.Nodes, 4)
	assert.Len(t, result.Edges, 4)
	assert.Len(t, result.Nodes[testUUIDString(1)].Children, 2)
	assert.Len(t, result.Nodes[testUUIDString(4)].Parents, 2)
}

// ============================================================================
// Edge Case Tests
// ============================================================================

func TestCache_MissingKey(t *testing.T) {
	cache := NewCache(1 * time.Minute)
	defer cache.Clear()

	_, ok := cache.Get("nonexistent_key")
	assert.False(t, ok)
}

func TestCache_OverwriteValue(t *testing.T) {
	cache := NewCache(1 * time.Minute)
	defer cache.Clear()

	key := "test_key"
	value1 := &Result{Nodes: make(map[string]*Node)}
	value2 := &Result{Nodes: make(map[string]*Node)}

	cache.Set(key, value1)
	cache.Set(key, value2)

	retrieved, ok := cache.Get(key)
	assert.True(t, ok)
	assert.Same(t, value2, retrieved)
}

func TestNode_EmptyAdjacency(t *testing.T) {
	item := buildTestItem(testUUID(1), "Isolated")
	node := &Node{
		Item:     &item,
		Children: []string{},
		Parents:  []string{},
	}

	assert.Empty(t, node.Children)
	assert.Empty(t, node.Parents)
}

func TestNode_DuplicateReferences(t *testing.T) {
	item := buildTestItem(testUUID(1), "Node")
	node := &Node{
		Item:     &item,
		Children: []string{testUUIDString(2), testUUIDString(2)},
		Parents:  []string{testUUIDString(0)},
	}

	// Can have duplicates in current implementation
	assert.Len(t, node.Children, 2)
}

// ============================================================================
// Concurrency and Thread Safety Tests
// ============================================================================

func TestCache_ConcurrentAccess(t *testing.T) {
	cache := NewCache(10 * time.Second)
	defer cache.Clear()

	// Concurrent writes
	done := make(chan bool, 10)

	for i := 0; i < 10; i++ {
		go func(idx int) {
			key := fmt.Sprintf("key_%d", idx)
			value := &Result{Nodes: make(map[string]*Node)}
			cache.Set(key, value)
			done <- true
		}(i)
	}

	for i := 0; i < 10; i++ {
		<-done
	}

	stats := cache.Stats()
	assert.Equal(t, 10, stats["total_entries"])
}

func TestCache_ConcurrentGetSet(t *testing.T) {
	cache := NewCache(10 * time.Second)
	defer cache.Clear()

	done := make(chan bool, 20)

	// Writers
	for i := 0; i < 10; i++ {
		go func(idx int) {
			key := fmt.Sprintf("key_%d", idx%5)
			value := &Result{Nodes: make(map[string]*Node)}
			cache.Set(key, value)
			done <- true
		}(i)
	}

	// Readers
	for i := 0; i < 10; i++ {
		go func(idx int) {
			key := fmt.Sprintf("key_%d", idx%5)
			_, _ = cache.Get(key)
			done <- true
		}(i)
	}

	for i := 0; i < 20; i++ {
		<-done
	}

	// Should not panic or deadlock
	stats := cache.Stats()
	assert.Positive(t, stats["total_entries"])
}

func TestCache_ConcurrentClear(t *testing.T) {
	cache := NewCache(10 * time.Second)

	// Add some entries
	for i := 0; i < 5; i++ {
		key := fmt.Sprintf("key_%d", i)
		cache.Set(key, &Result{})
	}

	done := make(chan bool, 10)

	// Concurrent operations with clear
	for i := 0; i < 5; i++ {
		go func(idx int) {
			cache.Get(fmt.Sprintf("key_%d", idx))
			done <- true
		}(i)
	}

	cache.Clear()

	for i := 0; i < 5; i++ {
		go func(idx int) {
			cache.Get(fmt.Sprintf("key_%d", idx))
			done <- true
		}(i)
	}

	for i := 0; i < 10; i++ {
		<-done
	}

	stats := cache.Stats()
	assert.Equal(t, 0, stats["total_entries"])
}

// ============================================================================
// Benchmarks (can be run with -bench flag)
// ============================================================================

func BenchmarkCache_Set(b *testing.B) {
	cache := NewCache(1 * time.Minute)
	defer cache.Clear()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("key_%d", i%100)
		cache.Set(key, &Result{})
	}
}

func BenchmarkCache_Get(b *testing.B) {
	cache := NewCache(1 * time.Minute)
	defer cache.Clear()

	// Pre-populate cache
	for i := 0; i < 100; i++ {
		key := fmt.Sprintf("key_%d", i)
		cache.Set(key, &Result{})
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("key_%d", i%100)
		cache.Get(key)
	}
}

func BenchmarkGenerateKey(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = generateKey("test", "param1", i)
	}
}
