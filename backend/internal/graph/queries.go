package graph

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5/pgtype"
	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/uuidutil"
)

const graphQueriesProjectItemLimit = 10000

// PathResult represents a path between two items
type PathResult struct {
	Path  []string        `json:"path"`  // ordered list of item IDs
	Links []db.Link       `json:"links"` // links connecting the path
	Items []db.GetItemRow `json:"items"` // items in the path
	Found bool            `json:"found"` // whether a path was found
}

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
		result, _ := g.createPathResult(ctx, pathCopy)
		state.paths = append(state.paths, result)
		return
	}

	visited[itemID] = true

	// Get outgoing links
	itemUUID, _ := uuidutil.StringToUUID(itemID)
	outgoingLinks, _ := g.queries.ListLinksBySource(ctx, itemUUID)

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

// CycleResult represents a detected cycle in the graph
type CycleResult struct {
	Cycle []string        `json:"cycle"` // cycle path (first and last elements are the same)
	Links []db.Link       `json:"links"` // links forming the cycle
	Items []db.GetItemRow `json:"items"` // items in the cycle
}

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
	itemUUID, _ := uuidutil.StringToUUID(itemID)
	outgoingLinks, _ := g.queries.ListLinksBySource(ctx, itemUUID)

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
				cycle, _ := g.createCycleResult(ctx, cyclePath)
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

// GetImpactAnalysis returns all items that would be affected by changes to the given item
// This includes all descendants (direct and indirect)
func (g *Graph) GetImpactAnalysis(ctx context.Context, itemID string, maxDepth int) (*Result, error) {
	return g.GetDescendants(ctx, itemID, maxDepth)
}

// GetDependencyAnalysis returns all items that the given item depends on
// This includes all ancestors (direct and indirect)
func (g *Graph) GetDependencyAnalysis(ctx context.Context, itemID string, maxDepth int) (*Result, error) {
	return g.GetAncestors(ctx, itemID, maxDepth)
}

// GetOrphanItems returns items with no incoming or outgoing links
func (g *Graph) GetOrphanItems(ctx context.Context, projectID string) ([]db.GetItemRow, error) {
	if projectID == "" {
		return []db.GetItemRow{}, nil
	}

	projectUUID, err := uuidutil.StringToUUID(projectID)
	if err != nil {
		return nil, fmt.Errorf("invalid project ID: %w", err)
	}

	// Use the GetOrphanItems query
	orphans, err := g.queries.GetOrphanItems(ctx, projectUUID)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch orphan items: %w", err)
	}

	// Convert GetOrphanItemsRow to GetItemRow
	result := make([]db.GetItemRow, 0, len(orphans))
	for _, item := range orphans {
		result = append(result, db.GetItemRowFromOrphanRow(item))
	}

	return result, nil
}
