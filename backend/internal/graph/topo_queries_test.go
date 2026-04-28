package graph

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestTopoSortLinearChain verifies correct ordering of a simple A->B->C chain.
// Traces to: FR-GRAPH-001 (graph traversal correctness)
func TestTopoSortLinearChain(t *testing.T) {
	state := &topoState{
		inDegree: map[string]int{
			"a": 0,
			"b": 1,
			"c": 1,
		},
		adjacency: map[string][]string{
			"a": {"b"},
			"b": {"c"},
			"c": {},
		},
	}

	sorted := topoSort(state)
	require.Equal(t, 3, len(sorted), "all nodes should appear in the result")
	assert.Equal(t, "a", sorted[0], "a must come first (no in-edges)")
	assert.Equal(t, "b", sorted[1])
	assert.Equal(t, "c", sorted[2])
}

// TestTopoSortDiamondGraph verifies that a diamond dependency (A->{B,C}->D) resolves correctly.
// Traces to: FR-GRAPH-001
func TestTopoSortDiamondGraph(t *testing.T) {
	state := &topoState{
		inDegree: map[string]int{
			"a": 0,
			"b": 1,
			"c": 1,
			"d": 2,
		},
		adjacency: map[string][]string{
			"a": {"b", "c"},
			"b": {"d"},
			"c": {"d"},
			"d": {},
		},
	}

	sorted := topoSort(state)
	require.Equal(t, 4, len(sorted))
	assert.Equal(t, "a", sorted[0], "root node must be first")
	assert.Equal(t, "d", sorted[3], "sink node must be last")
	// b and c may appear in either order in positions 1 and 2.
	middleSet := map[string]bool{sorted[1]: true, sorted[2]: true}
	assert.True(t, middleSet["b"] && middleSet["c"], "b and c must occupy middle positions")
}

// TestTopoSortCycle detects a cycle: A->B->A means topoSort cannot produce all nodes.
// Traces to: FR-GRAPH-001
func TestTopoSortCycle(t *testing.T) {
	state := &topoState{
		inDegree: map[string]int{
			"a": 1,
			"b": 1,
		},
		adjacency: map[string][]string{
			"a": {"b"},
			"b": {"a"},
		},
	}

	sorted := topoSort(state)
	// A cycle means neither node has in-degree 0; the queue starts empty and returns 0 nodes.
	assert.Equal(t, 0, len(sorted), "cyclic graph should produce no sorted output")
}

// TestTopoSortSingleNode verifies a single, isolated node sorts correctly.
// Traces to: FR-GRAPH-001
func TestTopoSortSingleNode(t *testing.T) {
	state := &topoState{
		inDegree:  map[string]int{"solo": 0},
		adjacency: map[string][]string{"solo": {}},
	}

	sorted := topoSort(state)
	require.Equal(t, 1, len(sorted))
	assert.Equal(t, "solo", sorted[0])
}

// TestTopoSortEmptyGraph verifies that an empty graph returns an empty slice without panicking.
// Traces to: FR-GRAPH-001
func TestTopoSortEmptyGraph(t *testing.T) {
	state := &topoState{
		inDegree:  map[string]int{},
		adjacency: map[string][]string{},
	}

	sorted := topoSort(state)
	assert.Empty(t, sorted)
}

// TestTopoSortDisconnectedComponents verifies two independent chains are both fully emitted.
// Traces to: FR-GRAPH-001
func TestTopoSortDisconnectedComponents(t *testing.T) {
	// Chain 1: x -> y
	// Chain 2: p -> q
	state := &topoState{
		inDegree: map[string]int{
			"x": 0,
			"y": 1,
			"p": 0,
			"q": 1,
		},
		adjacency: map[string][]string{
			"x": {"y"},
			"y": {},
			"p": {"q"},
			"q": {},
		},
	}

	sorted := topoSort(state)
	require.Equal(t, 4, len(sorted), "all nodes from both components must appear")

	// Each root must precede its downstream node.
	pos := func(id string) int {
		for i, v := range sorted {
			if v == id {
				return i
			}
		}
		return -1
	}
	assert.Less(t, pos("x"), pos("y"), "x must precede y")
	assert.Less(t, pos("p"), pos("q"), "p must precede q")
}
