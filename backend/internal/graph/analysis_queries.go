package graph

import (
	"context"
	"fmt"

	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/uuidutil"
)

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
