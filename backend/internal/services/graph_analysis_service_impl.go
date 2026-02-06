package services

import (
	"context"
	"errors"
	"fmt"
	"strings"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/nats-io/nats.go"
)

const (
	linkTypeDependsOn = "depends_on"
	linkTypeBlocks    = "blocks"
	linkTypeRequires  = "requires"
	complexityLow     = "low"
	complexityMedium  = "medium"
	complexityHigh    = "high"
	complexityLowMax  = 5
	complexityMedMax  = 15
	impactLowMax      = 3
	impactMedMax      = 10
	maxGraphDepth     = 3
)

// Ensure GraphAnalysisServiceImpl implements GraphAnalysisService interface
var _ GraphAnalysisService = (*GraphAnalysisServiceImpl)(nil)

// GraphAnalysisServiceImpl implements the GraphAnalysisService interface
type GraphAnalysisServiceImpl struct {
	itemRepo repository.ItemRepository
	linkRepo repository.LinkRepository
	cache    cache.Cache
	natsConn *nats.Conn
}

// NewGraphAnalysisServiceImpl creates a new graph analysis service implementation
func NewGraphAnalysisServiceImpl(
	itemRepo repository.ItemRepository,
	linkRepo repository.LinkRepository,
	cache cache.Cache,
	natsConn *nats.Conn,
) GraphAnalysisService {
	if itemRepo == nil {
		panic("itemRepo cannot be nil")
	}
	if linkRepo == nil {
		panic("linkRepo cannot be nil")
	}

	return &GraphAnalysisServiceImpl{
		itemRepo: itemRepo,
		linkRepo: linkRepo,
		cache:    cache,
		natsConn: natsConn,
	}
}

// ============================================================================
// DEPENDENCY ANALYSIS
// ============================================================================

// AnalyzeItemDependencies analyzes dependencies for a given item
func (s *GraphAnalysisServiceImpl) AnalyzeItemDependencies(ctx context.Context, itemID string) (*DependencyAnalysis, error) {
	if itemID == "" {
		return nil, errors.New("itemID cannot be empty")
	}

	// Verify item exists
	item, err := s.itemRepo.GetByID(ctx, itemID)
	if err != nil {
		return nil, fmt.Errorf("failed to get item: %w", err)
	}
	if item == nil {
		return nil, fmt.Errorf("item not found: %s", itemID)
	}

	// Get direct dependents (items that depend on this item)
	directDependents, err := s.getDirectDependents(ctx, itemID)
	if err != nil {
		return nil, fmt.Errorf("failed to get direct dependents: %w", err)
	}

	// Get transitive dependencies (all items this item depends on, recursively)
	transitiveDeps, err := s.getTransitiveDependencies(ctx, itemID, make(map[string]bool))
	if err != nil {
		return nil, fmt.Errorf("failed to get transitive dependencies: %w", err)
	}

	// Calculate complexity based on dependency counts
	complexity := s.calculateComplexity(len(directDependents), len(transitiveDeps))

	analysis := &DependencyAnalysis{
		ItemID:           itemID,
		DirectDependents: len(directDependents),
		TransitiveDeps:   len(transitiveDeps),
		Complexity:       complexity,
	}

	return analysis, nil
}

// getDirectDependents returns items that directly depend on the given item
func (s *GraphAnalysisServiceImpl) getDirectDependents(ctx context.Context, itemID string) ([]string, error) {
	// Get all links where this item is the target (other items depend on this one)
	links, err := s.linkRepo.GetByTargetID(ctx, itemID)
	if err != nil {
		return nil, err
	}

	dependents := make([]string, 0, len(links))
	seen := make(map[string]bool)

	for _, link := range links {
		// Filter for dependency type links
		if link.Type == linkTypeDependsOn || link.Type == linkTypeBlocks || link.Type == linkTypeRequires {
			if !seen[link.SourceID] {
				dependents = append(dependents, link.SourceID)
				seen[link.SourceID] = true
			}
		}
	}

	return dependents, nil
}

// getTransitiveDependencies recursively finds all dependencies of an item
func (s *GraphAnalysisServiceImpl) getTransitiveDependencies(ctx context.Context, itemID string, visited map[string]bool) ([]string, error) {
	// Prevent cycles
	if visited[itemID] {
		return []string{}, nil
	}
	visited[itemID] = true

	// Get direct dependencies (items this item depends on)
	links, err := s.linkRepo.GetBySourceID(ctx, itemID)
	if err != nil {
		return nil, err
	}

	allDeps := make([]string, 0)
	seen := make(map[string]bool)

	for _, link := range links {
		// Filter for dependency type links
		if link.Type == linkTypeDependsOn || link.Type == linkTypeBlocks || link.Type == linkTypeRequires {
			if !seen[link.TargetID] && !visited[link.TargetID] {
				allDeps = append(allDeps, link.TargetID)
				seen[link.TargetID] = true

				// Recursively get transitive dependencies
				transitive, err := s.getTransitiveDependencies(ctx, link.TargetID, visited)
				if err != nil {
					return nil, err
				}

				for _, dep := range transitive {
					if !seen[dep] {
						allDeps = append(allDeps, dep)
						seen[dep] = true
					}
				}
			}
		}
	}

	return allDeps, nil
}

// calculateComplexity determines complexity level based on dependency counts
func (s *GraphAnalysisServiceImpl) calculateComplexity(directDependents, transitiveDeps int) string {
	total := directDependents + transitiveDeps

	if total == 0 {
		return complexityLow
	}
	if total <= complexityLowMax {
		return complexityLow
	}
	if total <= complexityMedMax {
		return complexityMedium
	}
	return complexityHigh
}

// ============================================================================
// IMPACT ANALYSIS
// ============================================================================

// GetItemImpactAnalysis analyzes the impact of changes to a given item
func (s *GraphAnalysisServiceImpl) GetItemImpactAnalysis(ctx context.Context, itemID string) (*ImpactAnalysis, error) {
	if itemID == "" {
		return nil, errors.New("itemID cannot be empty")
	}

	// Verify item exists
	item, err := s.itemRepo.GetByID(ctx, itemID)
	if err != nil {
		return nil, fmt.Errorf("failed to get item: %w", err)
	}
	if item == nil {
		return nil, fmt.Errorf("item not found: %s", itemID)
	}

	// Get direct impact (items that directly depend on this item)
	directImpact, err := s.getDirectImpact(ctx, itemID)
	if err != nil {
		return nil, fmt.Errorf("failed to get direct impact: %w", err)
	}

	// Get indirect impact (items that transitively depend on this item)
	indirectImpact, err := s.getIndirectImpact(ctx, itemID, make(map[string]bool))
	if err != nil {
		return nil, fmt.Errorf("failed to get indirect impact: %w", err)
	}

	// Remove items in direct impact from indirect impact to avoid duplicates
	filteredIndirect := make([]string, 0)
	directSet := make(map[string]bool)
	for _, id := range directImpact {
		directSet[id] = true
	}
	for _, id := range indirectImpact {
		if !directSet[id] {
			filteredIndirect = append(filteredIndirect, id)
		}
	}

	// Calculate risk level based on impact counts
	riskLevel := s.calculateRiskLevel(len(directImpact), len(filteredIndirect))

	analysis := &ImpactAnalysis{
		ItemID:         itemID,
		DirectImpact:   directImpact,
		IndirectImpact: filteredIndirect,
		RiskLevel:      riskLevel,
	}

	return analysis, nil
}

// getDirectImpact returns items directly impacted by changes to the given item
func (s *GraphAnalysisServiceImpl) getDirectImpact(ctx context.Context, itemID string) ([]string, error) {
	// Items that depend on this one will be directly impacted
	return s.getDirectDependents(ctx, itemID)
}

// getIndirectImpact recursively finds all items indirectly impacted by changes
func (s *GraphAnalysisServiceImpl) getIndirectImpact(ctx context.Context, itemID string, visited map[string]bool) ([]string, error) {
	// Prevent cycles
	if visited[itemID] {
		return []string{}, nil
	}
	visited[itemID] = true

	// Get direct dependents
	directDependents, err := s.getDirectDependents(ctx, itemID)
	if err != nil {
		return nil, err
	}

	allImpacted := make([]string, 0)
	seen := make(map[string]bool)

	// Add direct dependents
	for _, depID := range directDependents {
		if !seen[depID] {
			allImpacted = append(allImpacted, depID)
			seen[depID] = true
		}
	}

	// Recursively get indirect dependents
	for _, depID := range directDependents {
		if !visited[depID] {
			transitive, err := s.getIndirectImpact(ctx, depID, visited)
			if err != nil {
				return nil, err
			}

			for _, id := range transitive {
				if !seen[id] {
					allImpacted = append(allImpacted, id)
					seen[id] = true
				}
			}
		}
	}

	return allImpacted, nil
}

// calculateRiskLevel determines risk level based on impact counts
func (s *GraphAnalysisServiceImpl) calculateRiskLevel(directImpact, indirectImpact int) string {
	total := directImpact + indirectImpact

	if total == 0 {
		return complexityLow
	}
	if total <= impactLowMax {
		return complexityLow
	}
	if total <= impactMedMax {
		return complexityMedium
	}
	return complexityHigh
}

// ============================================================================
// GRAPH VISUALIZATION
// ============================================================================

// VisualizeDependencyGraph generates a DOT format graph for visualization
func (s *GraphAnalysisServiceImpl) VisualizeDependencyGraph(ctx context.Context, itemID string) (string, error) {
	if itemID == "" {
		return "", errors.New("itemID cannot be empty")
	}

	// Verify item exists
	item, err := s.itemRepo.GetByID(ctx, itemID)
	if err != nil {
		return "", fmt.Errorf("failed to get item: %w", err)
	}
	if item == nil {
		return "", fmt.Errorf("item not found: %s", itemID)
	}

	// Get all related items and links
	visited := make(map[string]bool)
	items, links, err := s.collectGraphData(ctx, itemID, visited, maxGraphDepth) // Max depth of 3 levels
	if err != nil {
		return "", fmt.Errorf("failed to collect graph data: %w", err)
	}

	// Generate DOT format
	dot := s.generateDOT(item, items, links)

	return dot, nil
}

// collectGraphData recursively collects items and links for graph visualization
func (s *GraphAnalysisServiceImpl) collectGraphData(ctx context.Context, itemID string, visited map[string]bool, maxDepth int) (map[string]*models.Item, []*models.Link, error) {
	if maxDepth <= 0 || visited[itemID] {
		return make(map[string]*models.Item), []*models.Link{}, nil
	}
	visited[itemID] = true

	items := make(map[string]*models.Item)
	allLinks := make([]*models.Link, 0)

	// Get current item
	item, err := s.itemRepo.GetByID(ctx, itemID)
	if err != nil {
		return nil, nil, err
	}
	items[itemID] = item

	// Get outgoing links (dependencies)
	outgoingLinks, err := s.linkRepo.GetBySourceID(ctx, itemID)
	if err != nil {
		return nil, nil, err
	}

	// Get incoming links (dependents)
	incomingLinks, err := s.linkRepo.GetByTargetID(ctx, itemID)
	if err != nil {
		return nil, nil, err
	}

	// Combine links
	outgoingLinks = append(outgoingLinks, incomingLinks...)
	allLinks = append(allLinks, outgoingLinks...)

	// Recursively collect related items
	for _, link := range outgoingLinks {
		relatedID := link.TargetID
		if link.TargetID == itemID {
			relatedID = link.SourceID
		}

		if !visited[relatedID] {
			subItems, subLinks, err := s.collectGraphData(ctx, relatedID, visited, maxDepth-1)
			if err != nil {
				return nil, nil, err
			}

			// Merge items
			for id, item := range subItems {
				items[id] = item
			}

			// Merge links
			allLinks = append(allLinks, subLinks...)
		}
	}

	return items, allLinks, nil
}

// generateDOT creates a DOT format string for graph visualization
func (s *GraphAnalysisServiceImpl) generateDOT(rootItem *models.Item, items map[string]*models.Item, links []*models.Link) string {
	var sb strings.Builder

	sb.WriteString("digraph dependencies {\n")
	sb.WriteString("  rankdir=LR;\n")
	sb.WriteString("  node [shape=box, style=filled];\n\n")

	// Add nodes
	for id, item := range items {
		color := "lightblue"
		if id == rootItem.ID {
			color = "lightgreen" // Highlight root item
		}

		// Escape quotes in title
		title := strings.ReplaceAll(item.Title, "\"", "\\\"")
		label := fmt.Sprintf("%s\\n[%s]", title, item.Type)

		sb.WriteString(fmt.Sprintf("  \"%s\" [label=\"%s\", fillcolor=\"%s\"];\n", id, label, color))
	}

	sb.WriteString("\n")

	// Add edges
	seen := make(map[string]bool)
	for _, link := range links {
		// Only include links between items in our graph
		if _, sourceExists := items[link.SourceID]; !sourceExists {
			continue
		}
		if _, targetExists := items[link.TargetID]; !targetExists {
			continue
		}

		// Deduplicate edges
		edgeKey := fmt.Sprintf("%s->%s", link.SourceID, link.TargetID)
		if seen[edgeKey] {
			continue
		}
		seen[edgeKey] = true

		// Determine edge style based on link type
		style := s.getLinkStyle(link.Type)
		label := link.Type

		sb.WriteString(fmt.Sprintf("  \"%s\" -> \"%s\" [label=\"%s\"%s];\n",
			link.SourceID, link.TargetID, label, style))
	}

	sb.WriteString("}\n")

	return sb.String()
}

// getLinkStyle returns DOT style attributes for different link types
func (s *GraphAnalysisServiceImpl) getLinkStyle(linkType string) string {
	switch linkType {
	case linkTypeDependsOn:
		return ", style=solid, color=blue"
	case linkTypeBlocks:
		return ", style=bold, color=red"
	case "implements":
		return ", style=dashed, color=green"
	case "tests":
		return ", style=dotted, color=purple"
	default:
		return ", style=solid, color=gray"
	}
}
