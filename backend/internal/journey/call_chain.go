// Package journey provides journey detection and analysis.
package journey

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// CallChainDetector detects function call chains and execution paths
type CallChainDetector interface {
	DetectCallChains(ctx context.Context, projectID string) ([]*DerivedJourney, error)
}

// callChainDetector implements CallChainDetector
type callChainDetector struct {
	itemRepo repository.ItemRepository
	linkRepo repository.LinkRepository
	config   *DetectionConfig
}

const (
	callChainTopNodesLimit          = 5
	callChainScoreBase              = 0.5
	callChainDepthWeight            = 0.4
	callChainImportanceBase         = 0.5
	callChainImportanceLongMinNodes = 6
	callChainImportanceMidMinNodes  = 4
	callChainImportanceLongBonus    = 0.4
	callChainImportanceMediumBonus  = 0.2
)

// NewCallChainDetector creates a new call chain detector
func NewCallChainDetector(
	itemRepo repository.ItemRepository,
	linkRepo repository.LinkRepository,
	config *DetectionConfig,
) CallChainDetector {
	return &callChainDetector{
		itemRepo: itemRepo,
		linkRepo: linkRepo,
		config:   config,
	}
}

// DetectCallChains identifies function call sequences and execution paths
func (d *callChainDetector) DetectCallChains(ctx context.Context, projectID string) ([]*DerivedJourney, error) {
	// Get all items for the project
	items, err := d.itemRepo.GetByProjectID(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch items: %w", err)
	}

	if len(items) == 0 {
		return []*DerivedJourney{}, nil
	}

	// Classify items by execution role
	entryPoints := d.findEntryPoints(items)

	// Build call chain graph
	callGraph := d.buildCallGraph(ctx, items)

	// Find call chains from entry points
	paths := d.findCallChains(entryPoints, callGraph)

	// Convert paths to journeys
	journeys := d.pathsToJourneys(paths, projectID)

	return journeys, nil
}

// findEntryPoints identifies items that serve as entry points
func (d *callChainDetector) findEntryPoints(items []*models.Item) map[string]*models.Item {
	entryPoints := make(map[string]*models.Item)

	for _, item := range items {
		if d.isEntryPointType(item.Type) || d.isEntryPointTitle(item.Title) {
			entryPoints[item.ID] = item
		}
	}

	// If no explicit entry points, consider high out-degree nodes
	if len(entryPoints) == 0 {
		outDegrees := make(map[string]int)
		for _, item := range items {
			outDegrees[item.ID] = 0
		}
		// This will be calculated during call graph building
	}

	return entryPoints
}

// isEntryPointType checks if item type indicates entry point
func (d *callChainDetector) isEntryPointType(itemType string) bool {
	entryTypes := map[string]bool{
		"endpoint":    true,
		"route":       true,
		"handler":     true,
		"controller":  true,
		"entrypoint":  true,
		"entry":       true,
		"main":        true,
		"initializer": true,
		"bootstrap":   true,
	}
	return entryTypes[itemType]
}

// isEntryPointTitle checks if item title indicates entry point
func (d *callChainDetector) isEntryPointTitle(title string) bool {
	indicators := []string{"main", "init", "start", "bootstrap", "route", "endpoint", "handler"}
	for _, ind := range indicators {
		if len(title) > len(ind) && (title[:len(ind)] == ind) {
			return true
		}
	}
	return false
}

// isCallableType checks if item type represents a callable
func (d *callChainDetector) isCallableType(itemType string) bool {
	callableTypes := map[string]bool{
		"function":  true,
		"method":    true,
		"service":   true,
		"procedure": true,
		"callback":  true,
		"helper":    true,
		"utility":   true,
		"class":     true,
		"interface": true,
		"module":    true,
	}
	return callableTypes[itemType]
}

// isCallableTitle checks if item title indicates it's callable
func (d *callChainDetector) isCallableTitle(title string) bool {
	// Most titles with action verbs are callable
	verbs := []string{"get", "set", "create", "update", "delete", "process", "handle", "execute", "run", "call"}
	for _, verb := range verbs {
		if len(title) > len(verb) && title[:len(verb)] == verb {
			return true
		}
	}
	return false
}

// buildCallGraph constructs a graph of function calls
func (d *callChainDetector) buildCallGraph(ctx context.Context, items []*models.Item) map[string][]*models.Link {
	graph := make(map[string][]*models.Link)

	for _, item := range items {
		if !d.isCallableType(item.Type) && !d.isCallableTitle(item.Title) {
			continue
		}
		// Get all links from this item (function calls)
		links, err := d.linkRepo.GetBySourceID(ctx, item.ID)
		if err != nil {
			continue
		}
		if len(links) > 0 {
			// Filter for call-related links
			callLinks := d.filterCallLinks(links)
			if len(callLinks) > 0 {
				graph[item.ID] = callLinks
			}
		}
	}

	return graph
}

// filterCallLinks selects links that represent function calls
func (d *callChainDetector) filterCallLinks(links []*models.Link) []*models.Link {
	callTypes := map[string]bool{
		"calls":       true,
		"invokes":     true,
		"executes":    true,
		"calls_sync":  true,
		"calls_async": true,
		"delegates":   true,
		"triggers":    true,
		"dispatches":  true,
		"sends":       true,
		"receives":    true,
		"depends_on":  true,
	}

	var filtered []*models.Link
	for _, link := range links {
		if callTypes[link.Type] {
			filtered = append(filtered, link)
		}
	}

	return filtered
}

// topNodesByOutDegree returns the top-N nodes from the graph by out-degree.
func topNodesByOutDegree(graph map[string][]*models.Link, limit int) []string {
	outDegrees := make(map[string]int)
	for nodeID, links := range graph {
		outDegrees[nodeID] = len(links)
	}

	topNodes := make([]string, 0, len(outDegrees))
	for nodeID := range outDegrees {
		topNodes = append(topNodes, nodeID)
	}

	for i := 0; i < len(topNodes) && i < limit; i++ {
		for j := i + 1; j < len(topNodes); j++ {
			if outDegrees[topNodes[j]] > outDegrees[topNodes[i]] {
				topNodes[i], topNodes[j] = topNodes[j], topNodes[i]
			}
		}
	}

	if len(topNodes) > limit {
		topNodes = topNodes[:limit]
	}
	return topNodes
}

// findCallChains discovers call sequences using DFS
func (d *callChainDetector) findCallChains(
	entryPoints map[string]*models.Item,
	graph map[string][]*models.Link,
) []*Path {
	paths := make([]*Path, 0)
	visited := make(map[string]bool)

	startNodes := make([]string, 0, len(entryPoints))
	for entryID := range entryPoints {
		startNodes = append(startNodes, entryID)
	}
	if len(startNodes) == 0 {
		startNodes = topNodesByOutDegree(graph, callChainTopNodesLimit)
	}

	for _, nodeID := range startNodes {
		d.dfsCallChain(nodeID, graph, visited, &paths, []string{}, []string{})
	}

	return paths
}

// shouldSkipNode determines if a node should be skipped during DFS traversal
func (d *callChainDetector) shouldSkipNode(nodeID string, visited map[string]bool, currentPath []string) bool {
	if visited[nodeID] || len(currentPath) > d.config.MaxPathLength {
		return true
	}
	if !d.config.AllowCycles && d.pathContains(currentPath, nodeID) {
		return true
	}
	return false
}

// recordPathIfValid records a path if it meets minimum length requirements
func (d *callChainDetector) recordPathIfValid(paths *[]*Path, currentPath []string, currentLinks []string) {
	if len(currentPath) >= d.config.MinPathLength {
		path := &Path{
			Nodes:     append([]string{}, currentPath...),
			Links:     append([]string{}, currentLinks...),
			Type:      CallChain,
			Frequency: 1,
		}
		*paths = append(*paths, path)
	}
}

// dfsCallChain uses depth-first search to find call chains
func (d *callChainDetector) dfsCallChain(
	nodeID string,
	graph map[string][]*models.Link,
	visited map[string]bool,
	paths *[]*Path,
	currentPath []string,
	currentLinks []string,
) {
	if d.shouldSkipNode(nodeID, visited, currentPath) {
		return
	}

	currentPath = append(currentPath, nodeID)

	// Check for target condition (leaf node or sufficient depth)
	links, hasNext := graph[nodeID]
	if !hasNext || len(links) == 0 || len(currentPath) >= d.config.MinPathLength {
		d.recordPathIfValid(paths, currentPath, currentLinks)
	}

	// Continue exploring
	if hasNext && len(currentPath) < d.config.MaxPathLength {
		for _, link := range links {
			currentLinks = append(currentLinks, link.ID)
			d.dfsCallChain(link.TargetID, graph, visited, paths, currentPath, currentLinks)
		}
	}
}

// pathContains checks if path contains a node
func (d *callChainDetector) pathContains(path []string, nodeID string) bool {
	for _, id := range path {
		if id == nodeID {
			return true
		}
	}
	return false
}

// pathsToJourneys converts JourneyPaths to DerivedJourney objects
func (d *callChainDetector) pathsToJourneys(paths []*Path, projectID string) []*DerivedJourney {
	journeyMap := make(map[string]*DerivedJourney)

	for _, path := range paths {
		key := d.generatePathKey(path)

		if journey, exists := journeyMap[key]; exists {
			journey.Metadata.Frequency++
		} else {
			journey := &DerivedJourney{
				ID:        uuid.New().String(),
				ProjectID: projectID,
				Name:      d.generateJourneyName(path),
				Type:      CallChain,
				NodeIDs:   path.Nodes,
				Links:     d.pathLinksToJourneyLinks(path),
				Score:     d.calculateInitialScore(path),
				CreatedAt: time.Now(),
				UpdatedAt: time.Now(),
				Metadata: Metadata{
					Frequency:    1,
					Importance:   d.calculateCallChainImportance(path),
					Completeness: float64(len(path.Nodes)) / float64(d.config.MaxPathLength),
					Description:  d.generateJourneyDescription(path),
					Tags:         []string{"call_chain", "execution"},
					LastDetected: time.Now(),
				},
			}
			journeyMap[key] = journey
		}
	}

	journeys := make([]*DerivedJourney, 0, len(journeyMap))
	for _, journey := range journeyMap {
		if journey.Metadata.Frequency >= d.config.MinFrequency {
			journeys = append(journeys, journey)
		}
	}

	return journeys
}

// generatePathKey creates a unique key for a path
func (d *callChainDetector) generatePathKey(path *Path) string {
	var builder strings.Builder
	for i, nodeID := range path.Nodes {
		if i > 0 {
			builder.WriteString("→")
		}
		builder.WriteString(nodeID)
	}
	return builder.String()
}

// generateJourneyName creates a human-readable name for a journey
func (d *callChainDetector) generateJourneyName(path *Path) string {
	if len(path.Nodes) == 0 {
		return "Empty Call Chain"
	}
	if len(path.Nodes) == 1 {
		return "Call to " + path.Nodes[0]
	}
	return "Call chain: " + path.Nodes[0] + " → ... → " + path.Nodes[len(path.Nodes)-1]
}

// generateJourneyDescription creates a detailed description
func (d *callChainDetector) generateJourneyDescription(path *Path) string {
	return fmt.Sprintf("Function call sequence with %d functions involved", len(path.Nodes))
}

// pathLinksToJourneyLinks converts path links to journey links
func (d *callChainDetector) pathLinksToJourneyLinks(path *Path) []Link {
	journeyLinks := make([]Link, 0)
	for i := 0; i < len(path.Nodes)-1; i++ {
		journeyLinks = append(journeyLinks, Link{
			SourceID: path.Nodes[i],
			TargetID: path.Nodes[i+1],
			Type:     "function_call",
			Weight:   1,
		})
	}
	return journeyLinks
}

// calculateInitialScore calculates an initial score for a path
func (d *callChainDetector) calculateInitialScore(path *Path) float64 {
	score := callChainScoreBase

	// Reward deeper call chains
	depthFactor := float64(len(path.Nodes)) / float64(d.config.MaxPathLength)
	score += depthFactor * callChainDepthWeight

	return score
}

// calculateCallChainImportance determines the importance of a call chain
func (d *callChainDetector) calculateCallChainImportance(path *Path) float64 {
	importance := callChainImportanceBase

	// Longer call chains are typically more important
	if len(path.Nodes) > callChainImportanceLongMinNodes {
		importance += callChainImportanceLongBonus
	} else if len(path.Nodes) > callChainImportanceMidMinNodes {
		importance += callChainImportanceMediumBonus
	}

	return importance
}
