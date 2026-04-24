package graph

import (
	"context"
	"fmt"
	"log/slog"

	"github.com/jackc/pgx/v5/pgtype"

	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/uuidutil"
)

// cycleDetectionState maintains state for cycle detection
type cycleDetectionState struct {
	cycles   []*CycleResult
	visited  map[string]bool
	recStack map[string]bool
	parent   map[string]string
}

// extractCyclePath extracts the cycle path from the current traversal path
func extractCyclePath(path []string, targetID string) ([]string, bool) {
	cycleStart := -1
	for i, id := range path {
		if id == targetID {
			cycleStart = i
			break
		}
	}

	if cycleStart < 0 {
		return nil, false
	}

	cyclePath := make([]string, len(path)-cycleStart, len(path)-cycleStart+1)
	copy(cyclePath, path[cycleStart:])
	cyclePath = append(cyclePath, targetID) // close the cycle
	return cyclePath, true
}

// fetchCycleLinks fetches all links that form the cycle
func (g *Graph) fetchCycleLinks(ctx context.Context, cyclePath []string) ([]db.Link, error) {
	links := []db.Link{}

	for i := 0; i < len(cyclePath)-1; i++ {
		sourceUUID, err := uuidutil.StringToUUID(cyclePath[i])
		if err != nil {
			continue
		}
		targetUUID, err := uuidutil.StringToUUID(cyclePath[i+1])
		if err != nil {
			continue
		}

		cycleLink, err := g.queries.GetLinkBySourceAndTarget(ctx, db.GetLinkBySourceAndTargetParams{
			SourceID: sourceUUID,
			TargetID: targetUUID,
		})
		if err == nil {
			links = append(links, cycleLink)
		}
	}

	return links, nil
}

// fetchCycleItems fetches all items that participate in the cycle
func (g *Graph) fetchCycleItems(ctx context.Context, cyclePath []string) ([]db.GetItemRow, error) {
	items := []db.GetItemRow{}

	uniqueIDs := make(map[string]bool)
	for _, id := range cyclePath {
		uniqueIDs[id] = true
	}

	cycleUUIDs := make([]pgtype.UUID, 0, len(uniqueIDs))
	for id := range uniqueIDs {
		uuid, err := uuidutil.StringToUUID(id)
		if err == nil {
			cycleUUIDs = append(cycleUUIDs, uuid)
		}
	}

	if len(cycleUUIDs) == 0 {
		return items, nil
	}

	cycleItems, err := g.queries.ListItemsByIDs(ctx, cycleUUIDs)
	if err != nil {
		return items, err
	}

	for _, item := range cycleItems {
		items = append(items, db.GetItemRowFromIDsRow(item))
	}

	return items, nil
}

// createCycleResult creates a complete CycleResult with links and items
func (g *Graph) createCycleResult(ctx context.Context, cyclePath []string) (*CycleResult, error) {
	cycle := &CycleResult{
		Cycle: cyclePath,
		Links: []db.Link{},
		Items: []db.GetItemRow{},
	}

	links, err := g.fetchCycleLinks(ctx, cyclePath)
	if err == nil {
		cycle.Links = links
	}

	items, err := g.fetchCycleItems(ctx, cyclePath)
	if err == nil {
		cycle.Items = items
	}

	return cycle, nil
}

// initCycleDetectionState initializes the cycle detection state
func initCycleDetectionState() *cycleDetectionState {
	return &cycleDetectionState{
		cycles:   []*CycleResult{},
		visited:  make(map[string]bool),
		recStack: make(map[string]bool),
		parent:   make(map[string]string),
	}
}

// runCycleDFS performs DFS for cycle detection on a single node
func (g *Graph) runCycleDFS(ctx context.Context, state *cycleDetectionState, path []string, itemID string) {
	state.visited[itemID] = true
	state.recStack[itemID] = true
	path = append(path, itemID)

	// Get outgoing links
	itemUUID, err := uuidutil.StringToUUID(itemID)
	if err != nil {
		slog.Warn("invalid UUID in cycle detection", "item_id", itemID, "error", err)
		return
	}
	outgoingLinks, err := g.queries.ListLinksBySource(ctx, itemUUID)
	if err != nil {
		slog.Warn("failed to list links in cycle detection", "item_id", itemID, "error", err)
		return
	}

	// Process each neighbor
	for _, link := range outgoingLinks {
		targetID := uuidutil.UUIDToString(link.TargetID)

		if !state.visited[targetID] {
			state.parent[targetID] = itemID
			g.runCycleDFS(ctx, state, path, targetID)
			continue
		}

		if state.recStack[targetID] {
			cyclePath, ok := extractCyclePath(path, targetID)
			if ok {
				cycle, err := g.createCycleResult(ctx, cyclePath)
				if err != nil {
					slog.Warn("failed to create cycle result", "error", err)
					continue
				}
				state.cycles = append(state.cycles, cycle)
			}
		}
	}

	state.recStack[itemID] = false
}

// DetectCycles detects all cycles in the graph (for a project)
func (g *Graph) DetectCycles(ctx context.Context, projectID string) ([]*CycleResult, error) {
	if projectID == "" {
		return []*CycleResult{}, nil
	}

	// Fetch all items in the project
	projectUUID, err := uuidutil.StringToUUID(projectID)
	if err != nil {
		return nil, fmt.Errorf("invalid project ID: %w", err)
	}

	items, err := g.queries.ListItemsByProject(ctx, db.ListItemsByProjectParams{
		ProjectID: projectUUID,
		Limit:     graphQueriesProjectItemLimit,
		Offset:    0,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to fetch items: %w", err)
	}

	state := initCycleDetectionState()

	// Run DFS from each unvisited node
	for _, item := range items {
		itemID := uuidutil.UUIDToString(item.ID)
		if !state.visited[itemID] {
			g.runCycleDFS(ctx, state, []string{}, itemID)
		}
	}

	return state.cycles, nil
}
