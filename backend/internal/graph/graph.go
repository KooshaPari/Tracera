package graph

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5/pgtype"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/uuidutil"
)

const graphFullProjectItemLimit = 10000

// Graph represents a directed graph of items and their links
type Graph struct {
	queries *db.Queries
	pool    *pgxpool.Pool
}

// NewGraph creates a new graph instance
func NewGraph(pool *pgxpool.Pool) *Graph {
	return &Graph{
		queries: db.New(pool),
		pool:    pool,
	}
}

// Node represents a node in the graph with its item and adjacency information
type Node struct {
	Item     *db.GetItemRow `json:"item"`
	Children []string       `json:"children"` // outgoing edges
	Parents  []string       `json:"parents"`  // incoming edges
}

// Result represents the result of a graph traversal
type Result struct {
	Nodes map[string]*Node `json:"nodes"`
	Edges []db.Link        `json:"edges"`
	Path  []string         `json:"path,omitempty"`
}

// BFS performs breadth-first search starting from the given item ID
// direction: "forward" (follow outgoing links), "backward" (follow incoming links), "both"
func (g *Graph) BFS(ctx context.Context, startID string, direction string, maxDepth int) (*Result, error) {
	return g.BFSFiltered(ctx, startID, direction, maxDepth, nil)
}

// DFS performs depth-first search starting from the given item ID
// direction: "forward" (follow outgoing links), "backward" (follow incoming links), "both"
func (g *Graph) DFS(ctx context.Context, startID string, direction string, maxDepth int) (*Result, error) {
	return g.DFSFiltered(ctx, startID, direction, maxDepth, nil)
}

// GetAncestors returns all ancestors of the given item (items that link to it)
func (g *Graph) GetAncestors(ctx context.Context, itemID string, maxDepth int) (*Result, error) {
	return g.BFS(ctx, itemID, "backward", maxDepth)
}

// GetDescendants returns all descendants of the given item (items it links to)
func (g *Graph) GetDescendants(ctx context.Context, itemID string, maxDepth int) (*Result, error) {
	return g.BFS(ctx, itemID, "forward", maxDepth)
}

// GetSubgraph returns a subgraph containing the specified item IDs and their interconnections
func (g *Graph) GetSubgraph(ctx context.Context, itemIDs []string) (*Result, error) {
	result := &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}

	// Convert string IDs to UUIDs
	uuids := make([]pgtype.UUID, 0, len(itemIDs))
	idSet := make(map[string]bool)
	for _, id := range itemIDs {
		uuid, err := uuidutil.StringToUUID(id)
		if err != nil {
			continue
		}
		uuids = append(uuids, uuid)
		idSet[id] = true
	}

	if len(uuids) == 0 {
		return result, nil
	}

	// Fetch all items
	items, err := g.queries.ListItemsByIDs(ctx, uuids)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch items: %w", err)
	}

	// Initialize nodes - convert ListItemsByIDsRow to GetItemRow
	for _, item := range items {
		itemID := uuidutil.UUIDToString(item.ID)
		itemRow := db.GetItemRowFromIDsRow(item)
		result.Nodes[itemID] = &Node{
			Item:     &itemRow,
			Children: []string{},
			Parents:  []string{},
		}
	}

	// Fetch all links between the specified items
	links, err := g.queries.ListLinksBetweenItems(ctx, uuids)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch links: %w", err)
	}

	// Populate edges and adjacency
	for _, link := range links {
		sourceID := uuidutil.UUIDToString(link.SourceID)
		targetID := uuidutil.UUIDToString(link.TargetID)
		result.Edges = append(result.Edges, link)
		if node, exists := result.Nodes[sourceID]; exists {
			node.Children = append(node.Children, targetID)
		}
		if node, exists := result.Nodes[targetID]; exists {
			node.Parents = append(node.Parents, sourceID)
		}
	}

	return result, nil
}

// GetFullGraph returns the complete graph for a project
func (g *Graph) GetFullGraph(ctx context.Context, projectID string) (*Result, error) {
	result := newGraphResult()

	if projectID == "" {
		return result, nil
	}

	projectUUID, err := projectUUIDFromString(projectID)
	if err != nil {
		return nil, fmt.Errorf("invalid project ID: %w", err)
	}

	items, err := g.fetchProjectItems(ctx, projectUUID)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch items: %w", err)
	}

	itemUUIDs := buildGraphNodes(result, items)
	allLinks := g.fetchLinksForItems(ctx, itemUUIDs)
	populateGraphEdges(result, allLinks)

	return result, nil
}

func newGraphResult() *Result {
	return &Result{
		Nodes: make(map[string]*Node),
		Edges: []db.Link{},
	}
}

func projectUUIDFromString(projectID string) (pgtype.UUID, error) {
	return uuidutil.StringToUUID(projectID)
}

func (g *Graph) fetchProjectItems(ctx context.Context, projectUUID pgtype.UUID) ([]db.ListItemsByProjectRow, error) {
	return g.queries.ListItemsByProject(ctx, db.ListItemsByProjectParams{
		ProjectID: projectUUID,
		Limit:     graphFullProjectItemLimit,
		Offset:    0,
	})
}

func buildGraphNodes(result *Result, items []db.ListItemsByProjectRow) []pgtype.UUID {
	itemUUIDs := make([]pgtype.UUID, 0, len(items))
	for _, item := range items {
		itemID := uuidutil.UUIDToString(item.ID)
		itemUUIDs = append(itemUUIDs, item.ID)
		itemRow := db.GetItemRowFromProjectRow(item)
		result.Nodes[itemID] = &Node{
			Item:     &itemRow,
			Children: []string{},
			Parents:  []string{},
		}
	}
	return itemUUIDs
}

func (g *Graph) fetchLinksForItems(ctx context.Context, itemUUIDs []pgtype.UUID) []db.Link {
	if len(itemUUIDs) == 0 {
		return nil
	}

	allLinks := make([]db.Link, 0)
	sourceLinks, err := g.queries.ListLinksBySourceIDs(ctx, itemUUIDs)
	if err == nil {
		allLinks = append(allLinks, sourceLinks...)
	}

	targetLinks, err := g.queries.ListLinksByTargetIDs(ctx, itemUUIDs)
	if err == nil {
		allLinks = appendUniqueLinks(allLinks, targetLinks)
	}

	return allLinks
}

func appendUniqueLinks(existing []db.Link, add []db.Link) []db.Link {
	linkMap := make(map[string]db.Link, len(existing))
	for _, link := range existing {
		linkID := uuidutil.UUIDToString(link.ID)
		linkMap[linkID] = link
	}
	for _, link := range add {
		linkID := uuidutil.UUIDToString(link.ID)
		if _, exists := linkMap[linkID]; !exists {
			existing = append(existing, link)
		}
	}
	return existing
}

func populateGraphEdges(result *Result, links []db.Link) {
	for _, link := range links {
		sourceID := uuidutil.UUIDToString(link.SourceID)
		targetID := uuidutil.UUIDToString(link.TargetID)
		result.Edges = append(result.Edges, link)
		if node, exists := result.Nodes[sourceID]; exists {
			node.Children = append(node.Children, targetID)
		}
		if node, exists := result.Nodes[targetID]; exists {
			node.Parents = append(node.Parents, sourceID)
		}
	}
}
