// Package graph provides graph analysis and traversal utilities.
package graph

import (
	"context"
	"errors"
	"fmt"

	"github.com/jackc/pgx/v5/pgtype"

	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/uuidutil"
)

// Graph traversal direction constants
const (
	traversalDirectionForward  = "forward"
	traversalDirectionBackward = "backward"
	traversalDirectionBoth     = "both"
)

// TransitiveClosureResult represents the transitive closure of a graph
type TransitiveClosureResult struct {
	ReachabilityMatrix map[string]map[string]bool `json:"reachability_matrix"` // [source][target] = reachable
	Paths              map[string][]string        `json:"paths"`               // All reachable nodes from each node
	Distance           map[string]map[string]int  `json:"distance"`            // Shortest distance between nodes
}

// ComputeTransitiveClosure computes the transitive closure for a project
// This shows all reachability relationships in the graph
func (g *Graph) ComputeTransitiveClosure(ctx context.Context, projectID string) (*TransitiveClosureResult, error) {
	if projectID == "" {
		return nil, errors.New("project ID is required")
	}

	fullGraph, err := g.GetFullGraph(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to get full graph: %w", err)
	}

	result := newTransitiveClosureResult(fullGraph.Nodes)
	applyDirectEdges(result, fullGraph.Edges)

	nodeIDs := collectNodeIDs(fullGraph.Nodes)
	computeTransitiveClosure(result, nodeIDs)
	buildReachablePaths(result, fullGraph.Nodes)

	return result, nil
}

func newTransitiveClosureResult(nodes map[string]*Node) *TransitiveClosureResult {
	result := &TransitiveClosureResult{
		ReachabilityMatrix: make(map[string]map[string]bool),
		Paths:              make(map[string][]string),
		Distance:           make(map[string]map[string]int),
	}

	for nodeID := range nodes {
		result.ReachabilityMatrix[nodeID] = make(map[string]bool)
		result.Distance[nodeID] = make(map[string]int)
		result.Paths[nodeID] = []string{}
		result.ReachabilityMatrix[nodeID][nodeID] = true
		result.Distance[nodeID][nodeID] = 0
	}

	return result
}

func applyDirectEdges(result *TransitiveClosureResult, edges []db.Link) {
	for _, link := range edges {
		sourceID := uuidutil.UUIDToString(link.SourceID)
		targetID := uuidutil.UUIDToString(link.TargetID)
		result.ReachabilityMatrix[sourceID][targetID] = true
		result.Distance[sourceID][targetID] = 1
	}
}

func collectNodeIDs(nodes map[string]*Node) []string {
	nodeIDs := make([]string, 0, len(nodes))
	for nodeID := range nodes {
		nodeIDs = append(nodeIDs, nodeID)
	}
	return nodeIDs
}

func computeTransitiveClosure(result *TransitiveClosureResult, nodeIDs []string) {
	for _, k := range nodeIDs {
		for _, i := range nodeIDs {
			if !result.ReachabilityMatrix[i][k] {
				continue
			}
			propagateReachability(result, nodeIDs, i, k)
		}
	}
}

// propagateReachability updates reachability from i through k to all reachable j nodes.
func propagateReachability(result *TransitiveClosureResult, nodeIDs []string, sourceID, viaID string) {
	for _, j := range nodeIDs {
		if result.ReachabilityMatrix[viaID][j] && !result.ReachabilityMatrix[sourceID][j] {
			result.ReachabilityMatrix[sourceID][j] = true
			updateDistance(result.Distance, sourceID, viaID, j)
		}
	}
}

func updateDistance(distance map[string]map[string]int, sourceID string, viaID string, targetID string) {
	distIK, okIK := distance[sourceID][viaID]
	distKJ, okKJ := distance[viaID][targetID]
	if okIK && okKJ {
		newDist := distIK + distKJ
		if oldDist, exists := distance[sourceID][targetID]; !exists || newDist < oldDist {
			distance[sourceID][targetID] = newDist
		}
	}
}

func buildReachablePaths(result *TransitiveClosureResult, nodes map[string]*Node) {
	for sourceID := range nodes {
		reachable := make([]string, 0)
		for targetID := range nodes {
			if sourceID != targetID && result.ReachabilityMatrix[sourceID][targetID] {
				reachable = append(reachable, targetID)
			}
		}
		result.Paths[sourceID] = reachable
	}
}

// BFSFiltered performs BFS with link type filtering
func (g *Graph) BFSFiltered(ctx context.Context, startID string, direction string, maxDepth int, linkTypes []string) (*Result, error) {
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	// Check if start item exists
	startUUID, err := uuidutil.StringToUUID(startID)
	if err != nil {
		return nil, fmt.Errorf("invalid start item ID: %w", err)
	}

	_, err = g.queries.GetItem(ctx, startUUID)
	if err != nil {
		return nil, fmt.Errorf("start item not found: %w", err)
	}

	state := newBFSState(result, direction, maxDepth, linkTypes)
	if err := g.bfsFiltered(ctx, state, startID); err != nil {
		return nil, err
	}

	return result, nil
}

type bfsTraversalItem struct {
	itemID string
	depth  int
}

type bfsTraversalState struct {
	result         *Result
	visited        map[string]bool
	linkTypeFilter map[string]bool
	filterEnabled  bool
	direction      string
	maxDepth       int
}

func newBFSState(result *Result, direction string, maxDepth int, linkTypes []string) *bfsTraversalState {
	linkTypeFilter := make(map[string]bool)
	for _, lt := range linkTypes {
		linkTypeFilter[lt] = true
	}
	return &bfsTraversalState{
		result:         result,
		visited:        make(map[string]bool),
		linkTypeFilter: linkTypeFilter,
		filterEnabled:  len(linkTypes) > 0,
		direction:      direction,
		maxDepth:       maxDepth,
	}
}

// expandBFSNode expands a single BFS node in both applicable directions and returns new queue items.
func (g *Graph) expandBFSNode(
	ctx context.Context, state *bfsTraversalState, current bfsTraversalItem, currentUUID pgtype.UUID,
) ([]bfsTraversalItem, error) {
	var next []bfsTraversalItem
	if shouldTraverseForward(state.direction) {
		outgoing, err := g.collectBFSLinks(
			ctx, state, current, currentUUID,
			g.queries.ListLinksBySource,
			func(link db.Link) string { return uuidutil.UUIDToString(link.TargetID) },
			func(node *Node, id string) { node.Children = append(node.Children, id) },
		)
		if err != nil {
			return nil, err
		}
		next = append(next, outgoing...)
	}
	if shouldTraverseBackward(state.direction) {
		incoming, err := g.collectBFSLinks(
			ctx, state, current, currentUUID,
			g.queries.ListLinksByTarget,
			func(link db.Link) string { return uuidutil.UUIDToString(link.SourceID) },
			func(node *Node, id string) { node.Parents = append(node.Parents, id) },
		)
		if err != nil {
			return nil, err
		}
		next = append(next, incoming...)
	}
	return next, nil
}

func (g *Graph) bfsFiltered(ctx context.Context, state *bfsTraversalState, startID string) error {
	queue := []bfsTraversalItem{{itemID: startID, depth: 0}}
	for len(queue) > 0 {
		current := queue[0]
		queue = queue[1:]
		if state.shouldSkip(current) {
			continue
		}
		state.visited[current.itemID] = true

		currentUUID, err := uuidutil.StringToUUID(current.itemID)
		if err != nil {
			continue
		}
		item, err := g.queries.GetItem(ctx, currentUUID)
		if err != nil {
			continue
		}
		ensureNode(state.result, current.itemID, item)

		next, err := g.expandBFSNode(ctx, state, current, currentUUID)
		if err != nil {
			return err
		}
		queue = append(queue, next...)
	}
	return nil
}

func (state *bfsTraversalState) shouldSkip(item bfsTraversalItem) bool {
	if state.visited[item.itemID] {
		return true
	}
	return state.maxDepth > 0 && item.depth > state.maxDepth
}

func (state *bfsTraversalState) shouldEnqueue(nextID string, depth int) bool {
	if state.visited[nextID] {
		return false
	}
	return state.maxDepth == 0 || depth < state.maxDepth
}

func (g *Graph) collectBFSLinks(
	ctx context.Context,
	state *bfsTraversalState,
	current bfsTraversalItem,
	currentUUID pgtype.UUID,
	listFn func(context.Context, pgtype.UUID) ([]db.Link, error),
	neighborID func(db.Link) string,
	appendNeighbor func(*Node, string),
) ([]bfsTraversalItem, error) {
	links, err := listFn(ctx, currentUUID)
	if err != nil {
		return nil, err
	}
	next := make([]bfsTraversalItem, 0)
	for _, link := range links {
		if state.filterEnabled && !state.linkTypeFilter[link.Type] {
			continue
		}
		neighbor := neighborID(link)
		appendNeighbor(state.result.Nodes[current.itemID], neighbor)
		state.result.Edges = append(state.result.Edges, link)
		if state.shouldEnqueue(neighbor, current.depth) {
			next = append(next, bfsTraversalItem{itemID: neighbor, depth: current.depth + 1})
		}
	}
	return next, nil
}

// DFSFiltered performs DFS with link type filtering
func (g *Graph) DFSFiltered(ctx context.Context, startID string, direction string, maxDepth int, linkTypes []string) (*Result, error) {
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	startUUID, err := uuidutil.StringToUUID(startID)
	if err != nil {
		return nil, fmt.Errorf("invalid start item ID: %w", err)
	}

	_, err = g.queries.GetItem(ctx, startUUID)
	if err != nil {
		return nil, fmt.Errorf("start item not found: %w", err)
	}

	state := newDFSFilterState(result, direction, maxDepth, linkTypes)
	if err := g.dfsFiltered(ctx, state, startID, 0); err != nil {
		return nil, err
	}

	return result, nil
}

type dfsTraversalState struct {
	result         *Result
	visited        map[string]bool
	linkTypeFilter map[string]bool
	filterEnabled  bool
	direction      string
	maxDepth       int
}

func newDFSFilterState(result *Result, direction string, maxDepth int, linkTypes []string) *dfsTraversalState {
	linkTypeFilter := make(map[string]bool)
	for _, lt := range linkTypes {
		linkTypeFilter[lt] = true
	}
	return &dfsTraversalState{
		result:         result,
		visited:        make(map[string]bool),
		linkTypeFilter: linkTypeFilter,
		filterEnabled:  len(linkTypes) > 0,
		direction:      direction,
		maxDepth:       maxDepth,
	}
}

func (g *Graph) dfsFiltered(ctx context.Context, state *dfsTraversalState, itemID string, depth int) error {
	if state.visited[itemID] || state.depthExceeded(depth) {
		return nil
	}
	state.visited[itemID] = true

	itemUUID, err := uuidutil.StringToUUID(itemID)
	if err != nil {
		return err
	}

	item, err := g.queries.GetItem(ctx, itemUUID)
	if err != nil {
		return err
	}
	ensureNode(state.result, itemID, item)

	if shouldTraverseForward(state.direction) {
		if err := g.processOutgoing(ctx, state, itemID, itemUUID, depth); err != nil {
			return err
		}
	}
	if shouldTraverseBackward(state.direction) {
		if err := g.processIncoming(ctx, state, itemID, itemUUID, depth); err != nil {
			return err
		}
	}
	return nil
}

func (state *dfsTraversalState) depthExceeded(depth int) bool {
	return state.maxDepth > 0 && depth > state.maxDepth
}

func shouldTraverseForward(direction string) bool {
	return direction == traversalDirectionForward || direction == traversalDirectionBoth
}

func shouldTraverseBackward(direction string) bool {
	return direction == traversalDirectionBackward || direction == traversalDirectionBoth
}

func ensureNode(result *Result, itemID string, item db.GetItemRow) {
	if result.Nodes[itemID] != nil {
		return
	}
	result.Nodes[itemID] = &Node{
		Item:     &item,
		Children: []string{},
		Parents:  []string{},
	}
}

func (g *Graph) processOutgoing(
	ctx context.Context,
	state *dfsTraversalState,
	itemID string,
	itemUUID pgtype.UUID,
	depth int,
) error {
	outgoingLinks, err := g.queries.ListLinksBySource(ctx, itemUUID)
	if err != nil {
		return err
	}
	for _, link := range outgoingLinks {
		if state.filterEnabled && !state.linkTypeFilter[link.Type] {
			continue
		}
		targetID := uuidutil.UUIDToString(link.TargetID)
		state.result.Nodes[itemID].Children = append(state.result.Nodes[itemID].Children, targetID)
		state.result.Edges = append(state.result.Edges, link)
		if !state.visited[targetID] {
			if err := g.dfsFiltered(ctx, state, targetID, depth+1); err != nil {
				return err
			}
		}
	}
	return nil
}

func (g *Graph) processIncoming(
	ctx context.Context,
	state *dfsTraversalState,
	itemID string,
	itemUUID pgtype.UUID,
	depth int,
) error {
	incomingLinks, err := g.queries.ListLinksByTarget(ctx, itemUUID)
	if err != nil {
		return err
	}
	for _, link := range incomingLinks {
		if state.filterEnabled && !state.linkTypeFilter[link.Type] {
			continue
		}
		sourceID := uuidutil.UUIDToString(link.SourceID)
		state.result.Nodes[itemID].Parents = append(state.result.Nodes[itemID].Parents, sourceID)
		state.result.Edges = append(state.result.Edges, link)
		if !state.visited[sourceID] {
			if err := g.dfsFiltered(ctx, state, sourceID, depth+1); err != nil {
				return err
			}
		}
	}
	return nil
}

// ImpactPath represents a propagation path through the graph.
type ImpactPath struct {
	Path      []string `json:"path"`       // Propagation path
	LinkTypes []string `json:"link_types"` // Types of links in path
	Distance  int      `json:"distance"`   // Length of path
	Critical  bool     `json:"critical"`   // Whether this is a critical path
}

// ImpactPathAnalysisResult contains impact path analysis results.
type ImpactPathAnalysisResult struct {
	SourceItemID string       `json:"source_item_id"`
	ImpactPaths  []ImpactPath `json:"impact_paths"`
	TotalReach   int          `json:"total_reach"`   // Total unique items reached
	MaxDepth     int          `json:"max_depth"`     // Maximum depth of impact
	CriticalPath *ImpactPath  `json:"critical_path"` // Longest critical path
}

// AnalyzeImpactPaths analyzes all propagation paths from a source item
func (g *Graph) AnalyzeImpactPaths(ctx context.Context, sourceID string, maxPaths int) (*ImpactPathAnalysisResult, error) {
	if maxPaths <= 0 {
		maxPaths = 50
	}

	impactGraph, err := g.GetDescendants(ctx, sourceID, 0)
	if err != nil {
		return nil, fmt.Errorf("failed to get descendants: %w", err)
	}

	result := newImpactPathAnalysisResult(sourceID)
	result.TotalReach = countReachableItems(impactGraph.Nodes, sourceID)

	state := newImpactPathState(result, impactGraph, maxPaths)
	state.dfs(sourceID, 0)
	markCriticalPath(result)

	return result, nil
}

type impactPathState struct {
	result           *ImpactPathAnalysisResult
	impactGraph      *Result
	maxPaths         int
	visited          map[string]bool
	currentPath      []string
	currentLinkTypes []string
	edgeTypes        map[string]map[string]string
}

func newImpactPathAnalysisResult(sourceID string) *ImpactPathAnalysisResult {
	return &ImpactPathAnalysisResult{
		SourceItemID: sourceID,
		ImpactPaths:  []ImpactPath{},
		TotalReach:   0,
		MaxDepth:     0,
	}
}

func countReachableItems(nodes map[string]*Node, sourceID string) int {
	count := 0
	for nodeID := range nodes {
		if nodeID != sourceID {
			count++
		}
	}
	return count
}

func newImpactPathState(result *ImpactPathAnalysisResult, impactGraph *Result, maxPaths int) *impactPathState {
	return &impactPathState{
		result:           result,
		impactGraph:      impactGraph,
		maxPaths:         maxPaths,
		visited:          make(map[string]bool),
		currentPath:      []string{result.SourceItemID},
		currentLinkTypes: []string{},
		edgeTypes:        buildEdgeTypeIndex(impactGraph.Edges),
	}
}

func buildEdgeTypeIndex(edges []db.Link) map[string]map[string]string {
	index := make(map[string]map[string]string)
	for _, edge := range edges {
		sourceID := uuidutil.UUIDToString(edge.SourceID)
		targetID := uuidutil.UUIDToString(edge.TargetID)
		if index[sourceID] == nil {
			index[sourceID] = make(map[string]string)
		}
		index[sourceID][targetID] = edge.Type
	}
	return index
}

func (s *impactPathState) dfs(itemID string, depth int) {
	if len(s.result.ImpactPaths) >= s.maxPaths {
		return
	}

	if depth > s.result.MaxDepth {
		s.result.MaxDepth = depth
	}

	node := s.impactGraph.Nodes[itemID]
	if node == nil {
		return
	}

	if len(node.Children) == 0 && depth > 0 {
		s.appendLeafPath()
	}

	s.visited[itemID] = true
	for _, childID := range node.Children {
		if s.visited[childID] {
			continue
		}
		linkType := s.edgeTypeFor(itemID, childID)
		s.push(childID, linkType)
		s.dfs(childID, depth+1)
		s.pop()
	}
	s.visited[itemID] = false
}

func (s *impactPathState) edgeTypeFor(sourceID string, targetID string) string {
	if targets, ok := s.edgeTypes[sourceID]; ok {
		if linkType, exists := targets[targetID]; exists {
			return linkType
		}
	}
	return "unknown"
}

func (s *impactPathState) appendLeafPath() {
	pathCopy := make([]string, len(s.currentPath))
	copy(pathCopy, s.currentPath)
	linkTypesCopy := make([]string, len(s.currentLinkTypes))
	copy(linkTypesCopy, s.currentLinkTypes)

	s.result.ImpactPaths = append(s.result.ImpactPaths, ImpactPath{
		Path:      pathCopy,
		LinkTypes: linkTypesCopy,
		Distance:  len(pathCopy) - 1,
		Critical:  false,
	})
}

func (s *impactPathState) push(childID string, linkType string) {
	s.currentPath = append(s.currentPath, childID)
	s.currentLinkTypes = append(s.currentLinkTypes, linkType)
}

func (s *impactPathState) pop() {
	s.currentPath = s.currentPath[:len(s.currentPath)-1]
	s.currentLinkTypes = s.currentLinkTypes[:len(s.currentLinkTypes)-1]
}

func markCriticalPath(result *ImpactPathAnalysisResult) {
	maxPathLength := 0
	for i := range result.ImpactPaths {
		if result.ImpactPaths[i].Distance > maxPathLength {
			maxPathLength = result.ImpactPaths[i].Distance
			result.CriticalPath = &result.ImpactPaths[i]
			result.ImpactPaths[i].Critical = true
		}
	}
}
