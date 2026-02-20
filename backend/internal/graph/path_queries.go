package graph

import (
	"context"
	"fmt"
	"log/slog"

	"github.com/jackc/pgx/v5/pgtype"

	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/uuidutil"
)

// populatePathItems fetches and populates items for a given path
func (g *Graph) populatePathItems(ctx context.Context, path []string) ([]db.GetItemRow, error) {
	items := []db.GetItemRow{}

	pathUUIDs := make([]pgtype.UUID, 0, len(path))
	for _, id := range path {
		uuid, err := uuidutil.StringToUUID(id)
		if err == nil {
			pathUUIDs = append(pathUUIDs, uuid)
		}
	}

	if len(pathUUIDs) == 0 {
		return items, nil
	}

	dbItems, err := g.queries.ListItemsByIDs(ctx, pathUUIDs)
	if err != nil {
		return items, err
	}

	itemMap := make(map[string]db.GetItemRow)
	for _, item := range dbItems {
		itemID := uuidutil.UUIDToString(item.ID)
		itemMap[itemID] = db.GetItemRowFromIDsRow(item)
	}

	for _, id := range path {
		if item, exists := itemMap[id]; exists {
			items = append(items, item)
		}
	}

	return items, nil
}

// populatePathLinks fetches and populates links for a given path
func (g *Graph) populatePathLinks(ctx context.Context, path []string) ([]db.Link, error) {
	links := []db.Link{}

	for i := 0; i < len(path)-1; i++ {
		sourceUUID, err := uuidutil.StringToUUID(path[i])
		if err != nil {
			continue
		}
		targetUUID, err := uuidutil.StringToUUID(path[i+1])
		if err != nil {
			continue
		}

		link, err := g.queries.GetLinkBySourceAndTarget(ctx, db.GetLinkBySourceAndTargetParams{
			SourceID: sourceUUID,
			TargetID: targetUUID,
		})
		if err == nil {
			links = append(links, link)
		}
	}

	return links, nil
}

// createPathResult creates a complete PathResult with links and items populated
func (g *Graph) createPathResult(ctx context.Context, path []string) (*PathResult, error) {
	result := &PathResult{
		Path:  path,
		Links: []db.Link{},
		Items: []db.GetItemRow{},
		Found: true,
	}

	links, err := g.populatePathLinks(ctx, path)
	if err == nil {
		result.Links = links
	}

	items, err := g.populatePathItems(ctx, path)
	if err == nil {
		result.Items = items
	}

	return result, nil
}

// validateSourceAndTarget validates that source and target items exist
func (g *Graph) validateSourceAndTarget(ctx context.Context, sourceID, targetID string) (pgtype.UUID, pgtype.UUID, *db.GetItemRow, error) {
	sourceUUID, err := uuidutil.StringToUUID(sourceID)
	if err != nil {
		return pgtype.UUID{}, pgtype.UUID{}, nil, fmt.Errorf("invalid source item ID: %w", err)
	}

	targetUUID, err := uuidutil.StringToUUID(targetID)
	if err != nil {
		return pgtype.UUID{}, pgtype.UUID{}, nil, fmt.Errorf("invalid target item ID: %w", err)
	}

	sourceItem, err := g.queries.GetItem(ctx, sourceUUID)
	if err != nil {
		return pgtype.UUID{}, pgtype.UUID{}, nil, fmt.Errorf("source item not found: %w", err)
	}

	_, err = g.queries.GetItem(ctx, targetUUID)
	if err != nil {
		return pgtype.UUID{}, pgtype.UUID{}, nil, fmt.Errorf("target item not found: %w", err)
	}

	return sourceUUID, targetUUID, &sourceItem, nil
}

// FindPath finds a path between source and target items using BFS
func (g *Graph) FindPath(ctx context.Context, sourceID, targetID string) (*PathResult, error) {
	result := newPathResult()

	// Validate source and target exist
	_, _, sourceItem, err := g.validateSourceAndTarget(ctx, sourceID, targetID)
	if err != nil {
		return nil, err
	}

	// If source equals target, return single-node path
	if sourceID == targetID {
		return singleNodePathResult(sourceID, sourceItem), nil
	}

	path, linkMap := g.findShortestPath(ctx, sourceID, targetID)
	if len(path) == 0 {
		return result, nil
	}

	result.Path = path
	result.Found = true
	result.Links = reconstructLinksFromPath(path, linkMap)

	items, err := g.populatePathItems(ctx, path)
	if err == nil {
		result.Items = items
	}

	return result, nil
}

type pathQueueItem struct {
	itemID string
	path   []string
}

func newPathResult() *PathResult {
	return &PathResult{
		Path:  []string{},
		Links: []db.Link{},
		Items: []db.GetItemRow{},
		Found: false,
	}
}

func singleNodePathResult(sourceID string, sourceItem *db.GetItemRow) *PathResult {
	result := newPathResult()
	result.Path = []string{sourceID}
	result.Items = []db.GetItemRow{*sourceItem}
	result.Found = true
	return result
}

func (g *Graph) findShortestPath(ctx context.Context, sourceID, targetID string) ([]string, map[string]db.Link) {
	queue := []pathQueueItem{{itemID: sourceID, path: []string{sourceID}}}
	visited := make(map[string]bool)
	linkMap := make(map[string]db.Link)

	for len(queue) > 0 {
		current := queue[0]
		queue = queue[1:]

		if visited[current.itemID] {
			continue
		}
		visited[current.itemID] = true

		if current.itemID == targetID {
			return current.path, linkMap
		}

		next, err := g.expandBFSQueue(ctx, current, visited, linkMap)
		if err != nil {
			continue
		}
		queue = append(queue, next...)
	}

	return nil, linkMap
}

func (g *Graph) expandBFSQueue(
	ctx context.Context,
	current pathQueueItem,
	visited map[string]bool,
	linkMap map[string]db.Link,
) ([]pathQueueItem, error) {
	currentUUID, err := uuidutil.StringToUUID(current.itemID)
	if err != nil {
		return nil, err
	}

	outgoingLinks, err := g.queries.ListLinksBySource(ctx, currentUUID)
	if err != nil {
		return nil, err
	}

	next := make([]pathQueueItem, 0, len(outgoingLinks))
	for _, link := range outgoingLinks {
		targetID := uuidutil.UUIDToString(link.TargetID)
		if visited[targetID] {
			continue
		}

		newPath := clonePathAndAppend(current.path, targetID)
		next = append(next, pathQueueItem{itemID: targetID, path: newPath})
		linkMap[current.itemID+"->"+targetID] = link
	}

	return next, nil
}

func clonePathAndAppend(path []string, targetID string) []string {
	newPath := make([]string, len(path), len(path)+1)
	copy(newPath, path)
	return append(newPath, targetID)
}

func reconstructLinksFromPath(path []string, linkMap map[string]db.Link) []db.Link {
	links := make([]db.Link, 0, len(path))
	for i := 0; i < len(path)-1; i++ {
		src, tgt := path[i], path[i+1]
		key := src + "->" + tgt
		if link, exists := linkMap[key]; exists {
			links = append(links, link)
		}
	}
	return links
}

// dfsState maintains state for DFS traversal
type dfsState struct {
	paths    []*PathResult
	maxPaths int
}

func (s *dfsState) shouldContinue() bool {
	return len(s.paths) < s.maxPaths
}

// dfsVisit processes a single node in the DFS traversal
func (g *Graph) dfsVisit(ctx context.Context, state *dfsState, visited map[string]bool, currentPath []string, targetID, itemID string) {
	// Check termination conditions
	if !state.shouldContinue() {
		return
	}

	// Found target - create path result
	if itemID == targetID {
		pathCopy := make([]string, len(currentPath))
		copy(pathCopy, currentPath)
		result, err := g.createPathResult(ctx, pathCopy)
		if err != nil {
			slog.Warn("failed to create path result", "error", err)
			return
		}
		state.paths = append(state.paths, result)
		return
	}

	visited[itemID] = true

	// Get outgoing links
	itemUUID, err := uuidutil.StringToUUID(itemID)
	if err != nil {
		slog.Warn("invalid UUID in path search", "item_id", itemID, "error", err)
		return
	}
	outgoingLinks, err := g.queries.ListLinksBySource(ctx, itemUUID)
	if err != nil {
		slog.Warn("failed to list links in path search", "item_id", itemID, "error", err)
		return
	}

	// Explore each unvisited neighbor
	for _, link := range outgoingLinks {
		nextID := uuidutil.UUIDToString(link.TargetID)
		if !visited[nextID] {
			currentPath = append(currentPath, nextID)
			g.dfsVisit(ctx, state, visited, currentPath, targetID, nextID)
			currentPath = currentPath[:len(currentPath)-1]
		}
	}

	visited[itemID] = false
}

// initDFS initializes DFS traversal state
func (g *Graph) initDFS(sourceID string, maxPaths int) (*dfsState, []string, map[string]bool) {
	state := &dfsState{
		paths:    []*PathResult{},
		maxPaths: maxPaths,
	}
	return state, []string{sourceID}, make(map[string]bool)
}

// FindAllPaths finds all paths between source and target items (up to maxPaths)
func (g *Graph) FindAllPaths(ctx context.Context, sourceID, targetID string, maxPaths int) ([]*PathResult, error) {
	return g.findAllPaths(ctx, sourceID, targetID, maxPaths)
}

func (g *Graph) findAllPaths(ctx context.Context, sourceID, targetID string, maxPaths int) ([]*PathResult, error) {
	// Validate source and target exist
	_, _, sourceItem, err := g.validateSourceAndTarget(ctx, sourceID, targetID)
	if err != nil {
		return nil, err
	}

	// If source equals target
	if sourceID == targetID {
		result := &PathResult{
			Path:  []string{sourceID},
			Items: []db.GetItemRow{*sourceItem},
			Found: true,
		}
		return []*PathResult{result}, nil
	}

	// Initialize DFS state
	state, currentPath, visited := g.initDFS(sourceID, maxPaths)

	// Run DFS
	g.dfsVisit(ctx, state, visited, currentPath, targetID, sourceID)

	return state.paths, nil
}
