package graph

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5/pgtype"

	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/uuidutil"
)

// TopologicalSort performs a topological sort on the graph
// Returns sorted item IDs and whether the sort was successful (no cycles)
func (g *Graph) TopologicalSort(ctx context.Context, projectID string) ([]string, bool, error) {
	if projectID == "" {
		return []string{}, true, nil
	}

	projectUUID, err := uuidutil.StringToUUID(projectID)
	if err != nil {
		return nil, false, fmt.Errorf("invalid project ID: %w", err)
	}

	items, err := g.listProjectItems(ctx, projectUUID)
	if err != nil {
		return nil, false, fmt.Errorf("failed to fetch items: %w", err)
	}

	state := initTopoState(items)
	if err := g.buildTopoAdjacency(ctx, state); err != nil {
		return nil, false, err
	}

	sorted := topoSort(state)
	success := len(sorted) == len(items)
	return sorted, success, nil
}

type topoState struct {
	inDegree  map[string]int
	adjacency map[string][]string
	itemUUIDs []pgtype.UUID
}

func (g *Graph) listProjectItems(ctx context.Context, projectUUID pgtype.UUID) ([]db.ListItemsByProjectRow, error) {
	return g.queries.ListItemsByProject(ctx, db.ListItemsByProjectParams{
		ProjectID: projectUUID,
		Limit:     graphQueriesProjectItemLimit,
		Offset:    0,
	})
}

func initTopoState(items []db.ListItemsByProjectRow) *topoState {
	state := &topoState{
		inDegree:  make(map[string]int),
		adjacency: make(map[string][]string),
		itemUUIDs: make([]pgtype.UUID, 0, len(items)),
	}

	for _, item := range items {
		itemID := uuidutil.UUIDToString(item.ID)
		state.inDegree[itemID] = 0
		state.adjacency[itemID] = []string{}
		state.itemUUIDs = append(state.itemUUIDs, item.ID)
	}

	return state
}

func (g *Graph) buildTopoAdjacency(ctx context.Context, state *topoState) error {
	if len(state.itemUUIDs) == 0 {
		return nil
	}

	links, err := g.queries.ListLinksBetweenItems(ctx, state.itemUUIDs)
	if err != nil {
		return fmt.Errorf("failed to fetch links: %w", err)
	}

	for _, link := range links {
		sourceID := uuidutil.UUIDToString(link.SourceID)
		targetID := uuidutil.UUIDToString(link.TargetID)
		state.adjacency[sourceID] = append(state.adjacency[sourceID], targetID)
		state.inDegree[targetID]++
	}

	return nil
}

func topoSort(state *topoState) []string {
	queue := make([]string, 0)
	for id, degree := range state.inDegree {
		if degree == 0 {
			queue = append(queue, id)
		}
	}

	sorted := make([]string, 0, len(state.inDegree))
	for len(queue) > 0 {
		current := queue[0]
		queue = queue[1:]
		sorted = append(sorted, current)

		for _, neighbor := range state.adjacency[current] {
			state.inDegree[neighbor]--
			if state.inDegree[neighbor] == 0 {
				queue = append(queue, neighbor)
			}
		}
	}

	return sorted
}
