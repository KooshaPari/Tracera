package services

import (
	"context"
	"errors"
	"fmt"
	"strings"

	"github.com/nats-io/nats.go"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
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

// isDependencyLink checks if a link is a dependency type link
func isDependencyLink(link *models.Link) bool {
	return link.Type == linkTypeDependsOn || link.Type == linkTypeBlocks || link.Type == linkTypeRequires
}

// addUnseenDependencies adds dependencies to the list if not already seen
func addUnseenDependencies(allDeps []string, seen map[string]bool, transitive []string) []string {
	for _, dep := range transitive {
		if !seen[dep] {
			allDeps = append(allDeps, dep)
			seen[dep] = true
		}
	}
	return allDeps
}

// processDependencyLink processes a single dependency link recursively
func (s *GraphAnalysisServiceImpl) processDependencyLink(
	ctx context.Context,
	link *models.Link,
	visited, seen map[string]bool,
	allDeps []string,
) ([]string, error) {
	if !seen[link.TargetID] && !visited[link.TargetID] {
		allDeps = append(allDeps, link.TargetID)
		seen[link.TargetID] = true

		// Recursively get transitive dependencies
		transitive, err := s.getTransitiveDependencies(ctx, link.TargetID, visited)
		if err != nil {
			return nil, err
		}

		allDeps = addUnseenDependencies(allDeps, seen, transitive)
	}
	return allDeps, nil
}

// getTransitiveDependencies recursively finds all dependencies of an item
func (s *GraphAnalysisServiceImpl) getTransitiveDependencies(
	ctx context.Context, itemID string, visited map[string]bool,
) ([]string, error) {
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
		if isDependencyLink(link) {
			allDeps, err = s.processDependencyLink(ctx, link, visited, seen, allDeps)
			if err != nil {
				return nil, err
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

// addUnseenItems adds items to the list if not already seen
func addUnseenItems(allItems []string, seen map[string]bool, items []string) []string {
	for _, id := range items {
		if !seen[id] {
			allItems = append(allItems, id)
			seen[id] = true
		}
	}
	return allItems
}

// collectTransitiveImpact recursively collects transitive impact from dependents
func (s *GraphAnalysisServiceImpl) collectTransitiveImpact(
	ctx context.Context,
	directDependents []string,
	visited, seen map[string]bool,
	allImpacted []string,
) ([]string, error) {
	for _, depID := range directDependents {
		if !visited[depID] {
			transitive, err := s.getIndirectImpact(ctx, depID, visited)
			if err != nil {
				return nil, err
			}
			allImpacted = addUnseenItems(allImpacted, seen, transitive)
		}
	}
	return allImpacted, nil
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
	allImpacted = addUnseenItems(allImpacted, seen, directDependents)

	// Recursively get indirect dependents
	return s.collectTransitiveImpact(ctx, directDependents, visited, seen, allImpacted)
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

// getAllLinksForItem gets both outgoing and incoming links for an item
func (s *GraphAnalysisServiceImpl) getAllLinksForItem(ctx context.Context, itemID string) ([]*models.Link, error) {
	outgoingLinks, err := s.linkRepo.GetBySourceID(ctx, itemID)
	if err != nil {
		return nil, err
	}
	incomingLinks, err := s.linkRepo.GetByTargetID(ctx, itemID)
	if err != nil {
		return nil, err
	}
	return append(outgoingLinks, incomingLinks...), nil
}

// getRelatedItemID returns the related item ID (the other end of the link)
func getRelatedItemID(link *models.Link, currentItemID string) string {
	if link.TargetID == currentItemID {
		return link.SourceID
	}
	return link.TargetID
}

// mergeGraphData merges sub-graph items and links into the main graph
func mergeGraphData(
	items map[string]*models.Item, allLinks []*models.Link,
	subItems map[string]*models.Item, subLinks []*models.Link,
) (map[string]*models.Item, []*models.Link) {
	for id, item := range subItems {
		items[id] = item
	}
	return items, append(allLinks, subLinks...)
}

// collectGraphData recursively collects items and links for graph visualization
func (s *GraphAnalysisServiceImpl) collectGraphData(
	ctx context.Context, itemID string, visited map[string]bool, maxDepth int,
) (map[string]*models.Item, []*models.Link, error) {
	if maxDepth <= 0 || visited[itemID] {
		return make(map[string]*models.Item), []*models.Link{}, nil
	}
	visited[itemID] = true

	items := make(map[string]*models.Item)

	// Get current item
	item, err := s.itemRepo.GetByID(ctx, itemID)
	if err != nil {
		return nil, nil, err
	}
	items[itemID] = item

	// Get all links (both incoming and outgoing)
	links, err := s.getAllLinksForItem(ctx, itemID)
	if err != nil {
		return nil, nil, err
	}
	allLinks := make([]*models.Link, 0, len(links))
	allLinks = append(allLinks, links...)

	// Recursively collect related items
	for _, link := range links {
		relatedID := getRelatedItemID(link, itemID)

		if !visited[relatedID] {
			subItems, subLinks, err := s.collectGraphData(ctx, relatedID, visited, maxDepth-1)
			if err != nil {
				return nil, nil, err
			}
			items, allLinks = mergeGraphData(items, allLinks, subItems, subLinks)
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
