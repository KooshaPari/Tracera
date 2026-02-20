//go:build !integration && !e2e

package graph

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// ===== IMPACT ANALYSIS TESTS =====

// TestImpactAnalysisDirectDependencies tests analyzing direct dependencies
func TestImpactAnalysisDirectDependencies(t *testing.T) {
	// Mock graph structure: A -> B, A -> C
	nodes := map[string]*Node{
		"A": {
			Children: []string{"B", "C"},
			Parents:  []string{},
		},
		"B": {
			Children: []string{},
			Parents:  []string{"A"},
		},
		"C": {
			Children: []string{},
			Parents:  []string{"A"},
		},
	}

	sourceNode := nodes["A"]
	directDeps := len(sourceNode.Children)

	assert.Equal(t, 2, directDeps)
	assert.Contains(t, sourceNode.Children, "B")
	assert.Contains(t, sourceNode.Children, "C")
}

// TestImpactAnalysisTransitiveDependencies tests analyzing transitive dependencies
func TestImpactAnalysisTransitiveDependencies(t *testing.T) {
	// Mock graph: A -> B -> C -> D
	nodes := map[string]*Node{
		"A": {Children: []string{"B"}},
		"B": {Children: []string{"C"}},
		"C": {Children: []string{"D"}},
		"D": {Children: []string{}},
	}

	// Compute transitive closure using BFS
	visited := make(map[string]bool)
	queue := []string{"A"}
	transitiveDeps := []string{}

	for len(queue) > 0 {
		current := queue[0]
		queue = queue[1:]

		if visited[current] {
			continue
		}
		visited[current] = true

		if current != "A" {
			transitiveDeps = append(transitiveDeps, current)
		}

		if node, exists := nodes[current]; exists {
			queue = append(queue, node.Children...)
		}
	}

	assert.Len(t, transitiveDeps, 3)
	assert.Contains(t, transitiveDeps, "B")
	assert.Contains(t, transitiveDeps, "C")
	assert.Contains(t, transitiveDeps, "D")
}

// TestImpactAnalysisCyclicDependencies tests detecting cyclic dependencies
func TestImpactAnalysisCyclicDependencies(t *testing.T) {
	// Mock graph with cycle: A -> B -> C -> A
	nodes := map[string]*Node{
		"A": {Children: []string{"B"}},
		"B": {Children: []string{"C"}},
		"C": {Children: []string{"A"}},
	}

	// Detect cycle using DFS
	visited := make(map[string]bool)
	recStack := make(map[string]bool)
	var detectCycle func(node string) bool
	detectCycle = func(node string) bool {
		visited[node] = true
		recStack[node] = true

		if n, exists := nodes[node]; exists {
			for _, child := range n.Children {
				if !visited[child] {
					if detectCycle(child) {
						return true
					}
				} else if recStack[child] {
					return true
				}
			}
		}

		recStack[node] = false
		return false
	}

	hasCycle := detectCycle("A")
	assert.True(t, hasCycle, "Should detect cycle in graph")
}

// ===== DEPENDENCY ANALYSIS TESTS =====

func collectDependencies(nodes map[string]*Node, start string, next func(*Node) []string) []string {
	visited := make(map[string]bool)
	queue := []string{start}
	deps := []string{}

	for len(queue) > 0 {
		current := queue[0]
		queue = queue[1:]

		if visited[current] {
			continue
		}
		visited[current] = true

		if current != start {
			deps = append(deps, current)
		}

		if node, exists := nodes[current]; exists {
			queue = append(queue, next(node)...)
		}
	}

	return deps
}

// TestDependencyAnalysisUpstreamOnly tests analyzing upstream dependencies
func TestDependencyAnalysisUpstreamOnly(t *testing.T) {
	// Mock graph: A -> B -> C
	nodes := map[string]*Node{
		"A": {Children: []string{"B"}, Parents: []string{}},
		"B": {Children: []string{"C"}, Parents: []string{"A"}},
		"C": {Children: []string{}, Parents: []string{"B"}},
	}

	// Get upstream dependencies of C
	upstream := collectDependencies(nodes, "C", func(node *Node) []string {
		return node.Parents
	})

	assert.Len(t, upstream, 2)
	assert.Contains(t, upstream, "A")
	assert.Contains(t, upstream, "B")
}

// TestDependencyAnalysisDownstreamOnly tests analyzing downstream dependencies
func TestDependencyAnalysisDownstreamOnly(t *testing.T) {
	// Mock graph: A -> B -> C
	nodes := map[string]*Node{
		"A": {Children: []string{"B"}, Parents: []string{}},
		"B": {Children: []string{"C"}, Parents: []string{"A"}},
		"C": {Children: []string{}, Parents: []string{"B"}},
	}

	// Get downstream dependencies of A
	downstream := collectDependencies(nodes, "A", func(node *Node) []string {
		return node.Children
	})

	assert.Len(t, downstream, 2)
	assert.Contains(t, downstream, "B")
	assert.Contains(t, downstream, "C")
}

// TestDependencyAnalysisBothDirections tests analyzing dependencies in both directions
func TestDependencyAnalysisBothDirections(t *testing.T) {
	// Mock graph: A -> B -> C -> D
	nodes := map[string]*Node{
		"A": {Children: []string{"B"}, Parents: []string{}},
		"B": {Children: []string{"C"}, Parents: []string{"A"}},
		"C": {Children: []string{"D"}, Parents: []string{"B"}},
		"D": {Children: []string{}, Parents: []string{"C"}},
	}

	startNode := "B"

	// Get upstream
	upstreamVisited := make(map[string]bool)
	upstreamQueue := []string{startNode}
	upstream := []string{}

	for len(upstreamQueue) > 0 {
		current := upstreamQueue[0]
		upstreamQueue = upstreamQueue[1:]

		if upstreamVisited[current] {
			continue
		}
		upstreamVisited[current] = true

		if current != startNode {
			upstream = append(upstream, current)
		}

		if node, exists := nodes[current]; exists {
			upstreamQueue = append(upstreamQueue, node.Parents...)
		}
	}

	// Get downstream
	downstreamVisited := make(map[string]bool)
	downstreamQueue := []string{startNode}
	downstream := []string{}

	for len(downstreamQueue) > 0 {
		current := downstreamQueue[0]
		downstreamQueue = downstreamQueue[1:]

		if downstreamVisited[current] {
			continue
		}
		downstreamVisited[current] = true

		if current != startNode {
			downstream = append(downstream, current)
		}

		if node, exists := nodes[current]; exists {
			downstreamQueue = append(downstreamQueue, node.Children...)
		}
	}

	assert.Len(t, upstream, 1)
	assert.Contains(t, upstream, "A")
	assert.Len(t, downstream, 2)
	assert.Contains(t, downstream, "C")
	assert.Contains(t, downstream, "D")
}

// ===== CRITICAL PATH TESTS =====

// TestCriticalPathLinear tests finding critical path in linear graph
func TestCriticalPathLinear(t *testing.T) {
	// Mock graph: A -> B -> C -> D
	nodes := map[string]*Node{
		"A": {Children: []string{"B"}},
		"B": {Children: []string{"C"}},
		"C": {Children: []string{"D"}},
		"D": {Children: []string{}},
	}

	// Find longest path using DFS
	var longestPath []string
	var currentPath []string
	visited := make(map[string]bool)

	var dfs func(node string)
	dfs = func(node string) {
		visited[node] = true
		currentPath = append(currentPath, node)

		if len(currentPath) > len(longestPath) {
			longestPath = make([]string, len(currentPath))
			copy(longestPath, currentPath)
		}

		if n, exists := nodes[node]; exists {
			for _, child := range n.Children {
				if !visited[child] {
					dfs(child)
				}
			}
		}

		currentPath = currentPath[:len(currentPath)-1]
		visited[node] = false
	}

	dfs("A")

	assert.Len(t, longestPath, 4)
	assert.Equal(t, []string{"A", "B", "C", "D"}, longestPath)
}

// TestCriticalPathComplexGraph tests finding critical path in complex graph
func TestCriticalPathComplexGraph(t *testing.T) {
	// Mock graph with branching: A -> B -> D (path length 3)
	//                            A -> C (path length 2)
	nodes := map[string]*Node{
		"A": {Children: []string{"B", "C"}},
		"B": {Children: []string{"D"}},
		"C": {Children: []string{}},
		"D": {Children: []string{}},
	}

	var longestPath []string
	var currentPath []string
	visited := make(map[string]bool)

	var dfs func(node string)
	dfs = func(node string) {
		visited[node] = true
		currentPath = append(currentPath, node)

		if len(currentPath) > len(longestPath) {
			longestPath = make([]string, len(currentPath))
			copy(longestPath, currentPath)
		}

		if n, exists := nodes[node]; exists {
			for _, child := range n.Children {
				if !visited[child] {
					dfs(child)
				}
			}
		}

		currentPath = currentPath[:len(currentPath)-1]
		visited[node] = false
	}

	dfs("A")

	assert.Len(t, longestPath, 3)
	assert.Equal(t, "A", longestPath[0])
	assert.Equal(t, "D", longestPath[2])
}

// ===== CYCLE DETECTION TESTS =====

// TestCycleDetectionNoCycle tests cycle detection on acyclic graph
func TestCycleDetectionNoCycle(t *testing.T) {
	// Mock acyclic graph: A -> B -> C
	nodes := map[string]*Node{
		"A": {Children: []string{"B"}},
		"B": {Children: []string{"C"}},
		"C": {Children: []string{}},
	}

	visited := make(map[string]bool)
	recStack := make(map[string]bool)

	var detectCycle func(node string) bool
	detectCycle = func(node string) bool {
		visited[node] = true
		recStack[node] = true

		if n, exists := nodes[node]; exists {
			for _, child := range n.Children {
				if !visited[child] {
					if detectCycle(child) {
						return true
					}
				} else if recStack[child] {
					return true
				}
			}
		}

		recStack[node] = false
		return false
	}

	hasCycle := detectCycle("A")
	assert.False(t, hasCycle, "Acyclic graph should not have cycles")
}

// TestCycleDetectionSimpleCycle tests detecting simple cycle
func TestCycleDetectionSimpleCycle(t *testing.T) {
	// Mock graph with cycle: A -> B -> A
	nodes := map[string]*Node{
		"A": {Children: []string{"B"}},
		"B": {Children: []string{"A"}},
	}

	visited := make(map[string]bool)
	recStack := make(map[string]bool)

	var detectCycle func(node string) bool
	detectCycle = func(node string) bool {
		visited[node] = true
		recStack[node] = true

		if n, exists := nodes[node]; exists {
			for _, child := range n.Children {
				if !visited[child] {
					if detectCycle(child) {
						return true
					}
				} else if recStack[child] {
					return true
				}
			}
		}

		recStack[node] = false
		return false
	}

	hasCycle := detectCycle("A")
	assert.True(t, hasCycle, "Should detect simple cycle")
}

// TestCycleDetectionComplexCycle tests detecting complex cycle
func TestCycleDetectionComplexCycle(t *testing.T) {
	// Mock graph: A -> B -> C -> D -> B (cycle at B)
	nodes := map[string]*Node{
		"A": {Children: []string{"B"}},
		"B": {Children: []string{"C"}},
		"C": {Children: []string{"D"}},
		"D": {Children: []string{"B"}},
	}

	visited := make(map[string]bool)
	recStack := make(map[string]bool)
	cycleNodes := []string{}

	var detectCycle func(node string) bool
	detectCycle = func(node string) bool {
		visited[node] = true
		recStack[node] = true

		if n, exists := nodes[node]; exists {
			for _, child := range n.Children {
				if !visited[child] {
					if detectCycle(child) {
						return true
					}
				} else if recStack[child] {
					cycleNodes = append(cycleNodes, child)
					return true
				}
			}
		}

		recStack[node] = false
		return false
	}

	hasCycle := detectCycle("A")
	assert.True(t, hasCycle, "Should detect complex cycle")
	assert.Contains(t, cycleNodes, "B")
}

// ===== TOPOLOGICAL SORT TESTS =====

// TestTopologicalSortSuccess tests successful topological sort
func TestTopologicalSortSuccess(t *testing.T) {
	// Mock DAG: A -> B, A -> C, B -> D, C -> D
	nodes := map[string]*Node{
		"A": {Children: []string{"B", "C"}},
		"B": {Children: []string{"D"}},
		"C": {Children: []string{"D"}},
		"D": {Children: []string{}},
	}

	// Kahn's algorithm for topological sort
	inDegree := make(map[string]int)
	for nodeID := range nodes {
		inDegree[nodeID] = 0
	}

	for _, node := range nodes {
		for _, child := range node.Children {
			inDegree[child]++
		}
	}

	queue := []string{}
	for nodeID, degree := range inDegree {
		if degree == 0 {
			queue = append(queue, nodeID)
		}
	}

	sorted := []string{}
	for len(queue) > 0 {
		current := queue[0]
		queue = queue[1:]
		sorted = append(sorted, current)

		if node, exists := nodes[current]; exists {
			for _, child := range node.Children {
				inDegree[child]--
				if inDegree[child] == 0 {
					queue = append(queue, child)
				}
			}
		}
	}

	assert.Len(t, sorted, 4)
	assert.Equal(t, "A", sorted[0])
	assert.Equal(t, "D", sorted[3])
}

// TestTopologicalSortWithCycle tests topological sort failure with cycle
func TestTopologicalSortWithCycle(t *testing.T) {
	// Mock graph with cycle: A -> B -> C -> A
	nodes := map[string]*Node{
		"A": {Children: []string{"B"}},
		"B": {Children: []string{"C"}},
		"C": {Children: []string{"A"}},
	}

	inDegree := make(map[string]int)
	for nodeID := range nodes {
		inDegree[nodeID] = 0
	}

	for _, node := range nodes {
		for _, child := range node.Children {
			inDegree[child]++
		}
	}

	queue := []string{}
	for nodeID, degree := range inDegree {
		if degree == 0 {
			queue = append(queue, nodeID)
		}
	}

	sorted := []string{}
	for len(queue) > 0 {
		current := queue[0]
		queue = queue[1:]
		sorted = append(sorted, current)

		if node, exists := nodes[current]; exists {
			for _, child := range node.Children {
				inDegree[child]--
				if inDegree[child] == 0 {
					queue = append(queue, child)
				}
			}
		}
	}

	// Should not sort all nodes due to cycle
	assert.Less(t, len(sorted), len(nodes), "Should not complete topological sort with cycle")
}

// ===== TRANSITIVE CLOSURE TESTS =====

// TestTransitiveClosureComputation tests computing transitive closure
func TestTransitiveClosureComputation(t *testing.T) {
	// Mock graph: A -> B -> C
	edges := map[string][]string{
		"A": {"B"},
		"B": {"C"},
		"C": {},
	}

	nodes := []string{"A", "B", "C"}
	reach := make(map[string]map[string]bool)

	// Initialize reachability matrix
	for _, node := range nodes {
		reach[node] = make(map[string]bool)
		reach[node][node] = true // self-reachable
	}

	// Direct edges
	for from, toList := range edges {
		for _, to := range toList {
			reach[from][to] = true
		}
	}

	// Floyd-Warshall for transitive closure
	for _, k := range nodes {
		for _, i := range nodes {
			for _, j := range nodes {
				if reach[i][k] && reach[k][j] {
					reach[i][j] = true
				}
			}
		}
	}

	// A should reach B and C transitively
	assert.True(t, reach["A"]["B"])
	assert.True(t, reach["A"]["C"])
	assert.False(t, reach["C"]["A"])
}

// ===== GRAPH METRICS TESTS =====

// TestGraphDensity tests calculating graph density
func TestGraphDensity(t *testing.T) {
	// Mock graph with 4 nodes and 3 edges
	numNodes := 4
	numEdges := 3

	// Density = E / (N * (N-1)) for directed graph
	maxEdges := numNodes * (numNodes - 1)
	density := float64(numEdges) / float64(maxEdges)

	assert.InDelta(t, 0.25, density, 0.01)
}

// TestGraphConnectivity tests checking graph connectivity
func TestGraphConnectivity(t *testing.T) {
	// Weakly connected graph: A -> B, C -> D (two components)
	nodes := map[string]*Node{
		"A": {Children: []string{"B"}},
		"B": {Children: []string{}},
		"C": {Children: []string{"D"}},
		"D": {Children: []string{}},
	}

	visited := make(map[string]bool)
	var dfs func(node string)
	dfs = func(node string) {
		visited[node] = true
		if n, exists := nodes[node]; exists {
			for _, child := range n.Children {
				if !visited[child] {
					dfs(child)
				}
			}
		}
	}

	dfs("A")
	component1Size := len(visited)

	assert.Equal(t, 2, component1Size)
	assert.False(t, visited["C"])
	assert.False(t, visited["D"])
}

// TestImpactPathAnalysisResult tests ImpactPathAnalysisResult structure
func TestImpactPathAnalysisResult(t *testing.T) {
	result := &ImpactPathAnalysisResult{
		SourceItemID: "A",
		ImpactPaths: []ImpactPath{
			{Path: []string{"A", "B", "C"}, Distance: 2, Critical: true},
			{Path: []string{"A", "D"}, Distance: 1, Critical: false},
		},
		TotalReach: 3,
		MaxDepth:   2,
	}

	require.NotNil(t, result)
	assert.Equal(t, "A", result.SourceItemID)
	assert.Len(t, result.ImpactPaths, 2)
	assert.Equal(t, 3, result.TotalReach)
	assert.Equal(t, 2, result.MaxDepth)
	assert.True(t, result.ImpactPaths[0].Critical)
}

// TestTransitiveClosureResult tests TransitiveClosureResult structure
func TestTransitiveClosureResult(t *testing.T) {
	result := &TransitiveClosureResult{
		ReachabilityMatrix: map[string]map[string]bool{
			"A": {"A": true, "B": true, "C": true},
			"B": {"B": true, "C": true},
			"C": {"C": true},
		},
		Paths: map[string][]string{
			"A": {"B", "C"},
			"B": {"C"},
		},
		Distance: map[string]map[string]int{
			"A": {"A": 0, "B": 1, "C": 2},
			"B": {"B": 0, "C": 1},
			"C": {"C": 0},
		},
	}

	require.NotNil(t, result)
	assert.True(t, result.ReachabilityMatrix["A"]["C"])
	assert.Len(t, result.Paths["A"], 2)
	assert.Equal(t, 2, result.Distance["A"]["C"])
}

// BenchmarkBFS benchmarks breadth-first search
func BenchmarkBFS(b *testing.B) {
	// Create a large graph
	nodes := make(map[string]*Node)
	for i := 0; i < 1000; i++ {
		nodeID := string(rune('A' + i%26))
		if _, exists := nodes[nodeID]; !exists {
			nodes[nodeID] = &Node{Children: []string{}}
		}
		if i < 999 {
			nextID := string(rune('A' + (i+1)%26))
			nodes[nodeID].Children = append(nodes[nodeID].Children, nextID)
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		visited := make(map[string]bool)
		queue := []string{"A"}

		for len(queue) > 0 {
			current := queue[0]
			queue = queue[1:]

			if visited[current] {
				continue
			}
			visited[current] = true

			if node, exists := nodes[current]; exists {
				queue = append(queue, node.Children...)
			}
		}
	}
}

// BenchmarkDFS benchmarks depth-first search
func BenchmarkDFS(b *testing.B) {
	nodes := make(map[string]*Node)
	for i := 0; i < 1000; i++ {
		nodeID := string(rune('A' + i%26))
		if _, exists := nodes[nodeID]; !exists {
			nodes[nodeID] = &Node{Children: []string{}}
		}
		if i < 999 {
			nextID := string(rune('A' + (i+1)%26))
			nodes[nodeID].Children = append(nodes[nodeID].Children, nextID)
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		visited := make(map[string]bool)
		var dfs func(node string)
		dfs = func(node string) {
			if visited[node] {
				return
			}
			visited[node] = true

			if n, exists := nodes[node]; exists {
				for _, child := range n.Children {
					dfs(child)
				}
			}
		}
		dfs("A")
	}
}

// BenchmarkTransitiveClosure benchmarks transitive closure computation
func BenchmarkTransitiveClosure(b *testing.B) {
	size := 100
	nodes := make([]string, size)
	for i := 0; i < size; i++ {
		nodes[i] = string(rune('A' + i%26))
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		reach := make(map[string]map[string]bool)

		for _, node := range nodes {
			reach[node] = make(map[string]bool)
			reach[node][node] = true
		}

		// Floyd-Warshall
		for _, k := range nodes {
			for _, i := range nodes {
				for _, j := range nodes {
					if reach[i][k] && reach[k][j] {
						reach[i][j] = true
					}
				}
			}
		}
	}
}
