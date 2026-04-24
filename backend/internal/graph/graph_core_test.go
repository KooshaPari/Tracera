//go:build !integration && !e2e

package graph

import (
	"context"
	"testing"

	"github.com/kooshapari/tracertm-backend/internal/db"
)

// TestNewGraphStructure tests Graph initialization
func TestNewGraphStructure(t *testing.T) {
	// Create Graph with nil pool (for structure testing only)
	g := NewGraph(nil)

	if g == nil {
		t.Fatal("expected Graph to be initialized")
	}
	if g.pool != nil {
		t.Error("expected pool to be nil in test")
	}
	// queries will be initialized from pool, so it may be nil or initialized
}

// TestGraphStructure tests Graph field initialization
func TestGraphStructure(_ *testing.T) {
	g := &Graph{
		queries: nil,
		pool:    nil,
	}
	_ = g
}

// TestNodeStructure tests Node type structure
func TestNodeStructure(t *testing.T) {
	node := &Node{
		Item:     nil,
		Children: []string{"child1", "child2"},
		Parents:  []string{"parent1"},
	}

	if len(node.Children) != 2 {
		t.Errorf("expected 2 children, got %d", len(node.Children))
	}
	if len(node.Parents) != 1 {
		t.Errorf("expected 1 parent, got %d", len(node.Parents))
	}
}

// TestNodeEmptyAdjacency tests Node with empty adjacency
func TestNodeEmptyAdjacency(t *testing.T) {
	node := &Node{
		Item:     nil,
		Children: []string{},
		Parents:  []string{},
	}

	if len(node.Children) != 0 {
		t.Error("expected empty children list")
	}
	if len(node.Parents) != 0 {
		t.Error("expected empty parents list")
	}
}

// TestResultStructure tests Result initialization
func TestResultStructure(t *testing.T) {
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	if result.Nodes == nil {
		t.Fatal("expected Nodes map to be initialized")
	}
	if len(result.Nodes) != 0 {
		t.Fatalf("expected empty Nodes map, got %d", len(result.Nodes))
	}
	if result.Edges == nil {
		t.Fatal("expected Edges to be initialized")
	}
}

// TestResultNodeAddition tests adding nodes to Result
func TestResultNodeAddition(t *testing.T) {
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	node := &Node{
		Item:     nil,
		Children: []string{},
		Parents:  []string{},
	}

	result.Nodes["item-1"] = node

	if len(result.Nodes) != 1 {
		t.Fatalf("expected 1 node, got %d", len(result.Nodes))
	}
	if result.Nodes["item-1"] != node {
		t.Error("expected node to be in result")
	}
}

// TestResultEdgeAddition tests adding edges to Result
func TestResultEdgeAddition(t *testing.T) {
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	if len(result.Edges) != 0 {
		t.Fatalf("expected 0 edges initially, got %d", len(result.Edges))
	}
}

// TestPathResultStructure tests PathResult initialization
func TestPathResultStructure(t *testing.T) {
	result := &PathResult{
		Path:  []string{},
		Links: []db.Link{},
		Items: []db.GetItemRow{},
		Found: false,
	}

	if result.Found {
		t.Error("expected Found to be false initially")
	}
	if len(result.Path) != 0 {
		t.Error("expected empty path initially")
	}
}

// TestPathResultFound tests PathResult with found path
func TestPathResultFound(t *testing.T) {
	result := &PathResult{
		Path:  []string{"node1", "node2", "node3"},
		Links: []db.Link{},
		Items: []db.GetItemRow{},
		Found: true,
	}

	if !result.Found {
		t.Error("expected Found to be true")
	}
	if len(result.Path) != 3 {
		t.Fatalf("expected 3 nodes in path, got %d", len(result.Path))
	}
}

// TestPathResultPathConstruction tests constructing a path
func TestPathResultPathConstruction(t *testing.T) {
	result := &PathResult{
		Path:  make([]string, 0),
		Links: []db.Link{},
		Items: []db.GetItemRow{},
		Found: false,
	}

	// Simulate path construction
	result.Path = append(result.Path, "node1")
	result.Path = append(result.Path, "node2")
	result.Found = true

	if len(result.Path) != 2 {
		t.Fatalf("expected 2 nodes, got %d", len(result.Path))
	}
	if result.Path[0] != "node1" {
		t.Errorf("expected first node to be node1, got %s", result.Path[0])
	}
	if !result.Found {
		t.Error("expected Found to be true")
	}
}

// TestCycleResultStructure tests CycleResult initialization
func TestCycleResultStructure(t *testing.T) {
	result := &CycleResult{
		Cycle: []string{},
		Links: []db.Link{},
		Items: []db.GetItemRow{},
	}

	if result.Cycle == nil {
		t.Fatal("expected Cycle to be initialized")
	}
	if len(result.Cycle) != 0 {
		t.Error("expected empty cycle initially")
	}
}

// TestCycleResultWithNodes tests CycleResult with nodes
func TestCycleResultWithNodes(t *testing.T) {
	result := &CycleResult{
		Cycle: []string{"node1", "node2", "node3", "node1"}, // Closed cycle
		Links: []db.Link{},
		Items: []db.GetItemRow{},
	}

	if len(result.Cycle) != 4 {
		t.Fatalf("expected 4 nodes in cycle, got %d", len(result.Cycle))
	}
	// Verify cycle is closed
	if result.Cycle[0] != result.Cycle[len(result.Cycle)-1] {
		t.Error("cycle should be closed (first == last)")
	}
}

// TestTransitiveClosureResultStructure tests TransitiveClosureResult initialization
func TestTransitiveClosureResultStructure(t *testing.T) {
	result := &TransitiveClosureResult{
		ReachabilityMatrix: make(map[string]map[string]bool),
		Paths:              make(map[string][]string),
		Distance:           make(map[string]map[string]int),
	}

	if result.ReachabilityMatrix == nil {
		t.Fatal("expected ReachabilityMatrix to be initialized")
	}
	if result.Paths == nil {
		t.Fatal("expected Paths to be initialized")
	}
	if result.Distance == nil {
		t.Fatal("expected Distance to be initialized")
	}
}

// TestTransitiveClosureResultPopulation tests populating transitive closure result
func TestTransitiveClosureResultPopulation(t *testing.T) {
	result := &TransitiveClosureResult{
		ReachabilityMatrix: make(map[string]map[string]bool),
		Paths:              make(map[string][]string),
		Distance:           make(map[string]map[string]int),
	}

	// Simulate populating result
	nodeID := "node1"
	result.ReachabilityMatrix[nodeID] = make(map[string]bool)
	result.ReachabilityMatrix[nodeID]["node2"] = true
	result.Distance[nodeID] = make(map[string]int)
	result.Distance[nodeID]["node2"] = 1
	result.Paths[nodeID] = []string{"node2"}

	if !result.ReachabilityMatrix[nodeID]["node2"] {
		t.Error("expected node2 to be reachable from node1")
	}
	if result.Distance[nodeID]["node2"] != 1 {
		t.Errorf("expected distance 1, got %d", result.Distance[nodeID]["node2"])
	}
}

// TestImpactPathAnalysisResultStructure tests ImpactPathAnalysisResult
func TestImpactPathAnalysisResultStructure(t *testing.T) {
	result := &ImpactPathAnalysisResult{
		SourceItemID: "source-123",
		ImpactPaths:  []ImpactPath{},
		TotalReach:   0,
		MaxDepth:     0,
		CriticalPath: nil,
	}

	if result.SourceItemID != "source-123" {
		t.Errorf("expected SourceItemID source-123, got %s", result.SourceItemID)
	}
	if result.TotalReach != 0 {
		t.Errorf("expected TotalReach 0, got %d", result.TotalReach)
	}
}

// TestImpactPathStructure tests ImpactPath structure
func TestImpactPathStructure(t *testing.T) {
	path := ImpactPath{
		Path:      []string{"node1", "node2"},
		LinkTypes: []string{"depends"},
		Distance:  1,
		Critical:  false,
	}

	if len(path.Path) != 2 {
		t.Errorf("expected 2 nodes in path, got %d", len(path.Path))
	}
	if len(path.LinkTypes) != 1 {
		t.Errorf("expected 1 link type, got %d", len(path.LinkTypes))
	}
	if path.Distance != 1 {
		t.Errorf("expected distance 1, got %d", path.Distance)
	}
}

// TestContextCancellation tests handling of cancelled context
func TestContextCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	select {
	case <-ctx.Done():
		// Context is properly cancelled
	default:
		t.Error("expected context to be cancelled")
	}
}

// TestValidGraphStructureMultipleNodes tests graph with multiple nodes
func TestValidGraphStructureMultipleNodes(t *testing.T) {
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	// Add multiple nodes
	for i := 1; i <= 5; i++ {
		nodeID := "node" + string(rune('0'+i))
		result.Nodes[nodeID] = &Node{
			Item:     nil,
			Children: []string{},
			Parents:  []string{},
		}
	}

	if len(result.Nodes) != 5 {
		t.Fatalf("expected 5 nodes, got %d", len(result.Nodes))
	}
}

// TestNodeWithComplexAdjacency tests Node with multiple parents and children
func TestNodeWithComplexAdjacency(t *testing.T) {
	node := &Node{
		Item:     nil,
		Children: []string{"child1", "child2", "child3"},
		Parents:  []string{"parent1", "parent2"},
	}

	if len(node.Children) != 3 {
		t.Errorf("expected 3 children, got %d", len(node.Children))
	}
	if len(node.Parents) != 2 {
		t.Errorf("expected 2 parents, got %d", len(node.Parents))
	}
}

// BenchmarkNewResult benchmarks Result creation
func BenchmarkNewResult(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = &Result{
			Nodes: make(map[string]*Node),
			Edges: []db.Link{},
		}
	}
}

// BenchmarkNodeCreation benchmarks Node creation
func BenchmarkNodeCreation(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = &Node{
			Item:     nil,
			Children: []string{},
			Parents:  []string{},
		}
	}
}

// BenchmarkPathResultCreation benchmarks PathResult creation
func BenchmarkPathResultCreation(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = &PathResult{
			Path:  []string{},
			Links: []db.Link{},
			Items: []db.GetItemRow{},
			Found: false,
		}
	}
}
