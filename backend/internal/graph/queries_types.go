package graph

import (
	"github.com/kooshapari/tracertm-backend/internal/db"
)

const graphQueriesProjectItemLimit = 10000

// PathResult represents a path between two items
type PathResult struct {
	Path  []string        `json:"path"`  // ordered list of item IDs
	Links []db.Link       `json:"links"` // links connecting the path
	Items []db.GetItemRow `json:"items"` // items in the path
	Found bool            `json:"found"` // whether a path was found
}

// CycleResult represents a detected cycle in the graph
type CycleResult struct {
	Cycle []string        `json:"cycle"` // cycle path (first and last elements are the same)
	Links []db.Link       `json:"links"` // links forming the cycle
	Items []db.GetItemRow `json:"items"` // items in the cycle
}
