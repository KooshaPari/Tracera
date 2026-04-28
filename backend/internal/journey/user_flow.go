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

// UserFlowDetector detects user navigation flows through the system
type UserFlowDetector interface {
	DetectUserFlows(ctx context.Context, projectID string) ([]*DerivedJourney, error)
}

// userFlowDetector implements UserFlowDetector
type userFlowDetector struct {
	itemRepo repository.ItemRepository
	linkRepo repository.LinkRepository
	config   *DetectionConfig
}

const (
	userFlowPathLimit          = 100
	userFlowHighOutDegreeMin   = 2
	userFlowMinGroupKeyNodes   = 2
	userFlowScoreBase          = 0.5
	userFlowLengthWeight       = 0.3
	userFlowFrequencyDivisor   = 10.0
	userFlowFrequencyWeight    = 0.2
	userFlowFrequencyFactorMax = 1.0
)

// NewUserFlowDetector creates a new user flow detector
func NewUserFlowDetector(
	itemRepo repository.ItemRepository,
	linkRepo repository.LinkRepository,
	config *DetectionConfig,
) UserFlowDetector {
	return &userFlowDetector{
		itemRepo: itemRepo,
		linkRepo: linkRepo,
		config:   config,
	}
}

// DetectUserFlows identifies common navigation patterns through UI pages
func (d *userFlowDetector) DetectUserFlows(ctx context.Context, projectID string) ([]*DerivedJourney, error) {
	// Get all items for the project
	items, err := d.itemRepo.GetByProjectID(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch items: %w", err)
	}

	if len(items) == 0 {
		return []*DerivedJourney{}, nil
	}

	// Build graph of user flows
	flows := d.buildUserFlowGraph(ctx, items)

	// Find paths in the graph
	paths := d.findUserFlowPaths(flows)

	// Convert paths to journeys
	journeys := d.pathsToJourneys(paths, projectID)

	return journeys, nil
}

// buildUserFlowGraph constructs a graph of user navigation flows
func (d *userFlowDetector) buildUserFlowGraph(ctx context.Context, items []*models.Item) map[string][]*models.Link {
	graph := make(map[string][]*models.Link)

	for _, item := range items {
		// Get outgoing links from this item
		links, err := d.linkRepo.GetBySourceID(ctx, item.ID)
		if err != nil {
			continue
		}
		if len(links) > 0 {
			// Filter for navigation-related links
			navLinks := d.filterNavigationLinks(links)
			if len(navLinks) > 0 {
				graph[item.ID] = navLinks
			}
		}
	}

	return graph
}

// filterNavigationLinks selects links that represent user navigation
func (d *userFlowDetector) filterNavigationLinks(links []*models.Link) []*models.Link {
	navLinkTypes := map[string]bool{
		"navigates_to":    true,
		"flows_to":        true,
		"leads_to":        true,
		"transitions_to":  true,
		"page_navigation": true,
		"ui_flow":         true,
	}

	var filtered []*models.Link
	for _, link := range links {
		// Check if link type indicates navigation
		if navLinkTypes[link.Type] {
			filtered = append(filtered, link)
		}
		// Also include generic links between page-like items
		if link.Type == "depends_on" || link.Type == "relates_to" {
			filtered = append(filtered, link)
		}
	}

	return filtered
}

// findUserFlowPaths discovers common user navigation sequences
func (d *userFlowDetector) findUserFlowPaths(graph map[string][]*models.Link) []*Path {
	paths := make([]*Path, 0)
	visited := make(map[string]bool)

	// For each node in the graph, explore paths starting from it
	for startID := range graph {
		d.exploreUserFlowPaths(startID, graph, visited, &paths)
	}

	// Find nodes with no incoming edges (potential start points)
	hasIncoming := make(map[string]bool)
	for _, links := range graph {
		for _, link := range links {
			hasIncoming[link.TargetID] = true
		}
	}

	// Start paths from nodes with high out-degree
	for nodeID, links := range graph {
		if len(links) >= userFlowHighOutDegreeMin && !visited[nodeID] {
			d.exploreUserFlowPaths(nodeID, graph, visited, &paths)
		}
	}

	return paths
}

// exploreUserFlowPaths recursively explores paths from a start node
func (d *userFlowDetector) exploreUserFlowPaths(
	nodeID string,
	graph map[string][]*models.Link,
	visited map[string]bool,
	paths *[]*Path,
) {
	if visited[nodeID] || len(*paths) > userFlowPathLimit {
		return // Prevent infinite recursion and explosion
	}

	visited[nodeID] = true

	// Get links from current node
	links, ok := graph[nodeID]
	if !ok || len(links) == 0 {
		return
	}

	// Explore each link
	for _, link := range links {
		path := &Path{
			Nodes:     []string{nodeID, link.TargetID},
			Links:     []string{link.ID},
			Type:      UserFlow,
			Frequency: 1,
		}

		// Extend path to maximum length
		d.extendUserFlowPath(path, graph, visited, paths)

		// Add the path if it meets minimum length
		if len(path.Nodes) >= d.config.MinPathLength && len(path.Nodes) <= d.config.MaxPathLength {
			*paths = append(*paths, path)
		}
	}
}

// extendUserFlowPath extends a path by following subsequent links
func (d *userFlowDetector) extendUserFlowPath(
	path *Path,
	graph map[string][]*models.Link,
	visited map[string]bool,
	paths *[]*Path,
) {
	currentNode := path.Nodes[len(path.Nodes)-1]
	links, ok := graph[currentNode]
	if !ok || len(links) == 0 || len(path.Nodes) >= d.config.MaxPathLength {
		return
	}

	// Extend with first link (greedy approach)
	for _, link := range links {
		if !d.config.AllowCycles && d.pathContainsNode(path, link.TargetID) {
			continue
		}

		path.Nodes = append(path.Nodes, link.TargetID)
		path.Links = append(path.Links, link.ID)
		d.extendUserFlowPath(path, graph, visited, paths)
		break // Only take first path to avoid explosion
	}
}

// pathContainsNode checks if a path already contains a node
func (d *userFlowDetector) pathContainsNode(path *Path, nodeID string) bool {
	for _, id := range path.Nodes {
		if id == nodeID {
			return true
		}
	}
	return false
}

// pathsToJourneys converts JourneyPaths to DerivedJourney objects
func (d *userFlowDetector) pathsToJourneys(paths []*Path, projectID string) []*DerivedJourney {
	journeyMap := make(map[string]*DerivedJourney)

	// Group similar paths if configured
	for _, path := range paths {
		key := d.generatePathKey(path)
		if d.config.GroupSimilar {
			key = d.generateGroupKey(path)
		}

		if journey, exists := journeyMap[key]; exists {
			journey.Metadata.Frequency++
		} else {
			journey := &DerivedJourney{
				ID:        uuid.New().String(),
				ProjectID: projectID,
				Name:      d.generateJourneyName(path),
				Type:      UserFlow,
				NodeIDs:   path.Nodes,
				Links:     d.pathLinksToJourneyLinks(path),
				Score:     d.calculateInitialScore(path),
				CreatedAt: time.Now(),
				UpdatedAt: time.Now(),
				Metadata: Metadata{
					Frequency:    1,
					Completeness: float64(len(path.Nodes)) / float64(d.config.MaxPathLength),
					Description:  d.generateJourneyDescription(path),
					Tags:         []string{"user_flow", "navigation"},
					LastDetected: time.Now(),
				},
			}
			journeyMap[key] = journey
		}
	}

	// Convert map to slice
	journeys := make([]*DerivedJourney, 0, len(journeyMap))
	for _, journey := range journeyMap {
		if journey.Metadata.Frequency >= d.config.MinFrequency {
			journeys = append(journeys, journey)
		}
	}

	return journeys
}

// generatePathKey creates a unique key for a path
func (d *userFlowDetector) generatePathKey(path *Path) string {
	var builder strings.Builder
	for i, nodeID := range path.Nodes {
		if i > 0 {
			builder.WriteString("->")
		}
		builder.WriteString(nodeID)
	}
	return builder.String()
}

// generateGroupKey creates a grouping key for similar paths
func (d *userFlowDetector) generateGroupKey(path *Path) string {
	// Group by first and last node, simplified structure
	if len(path.Nodes) < userFlowMinGroupKeyNodes {
		return path.Nodes[0]
	}
	return path.Nodes[0] + "::" + path.Nodes[len(path.Nodes)-1]
}

// generateJourneyName creates a human-readable name for a journey
func (d *userFlowDetector) generateJourneyName(path *Path) string {
	if len(path.Nodes) == 0 {
		return "Empty Journey"
	}
	if len(path.Nodes) == 1 {
		return "User visits " + path.Nodes[0]
	}
	return "User flow: " + path.Nodes[0] + " → ... → " + path.Nodes[len(path.Nodes)-1]
}

// generateJourneyDescription creates a detailed description
func (d *userFlowDetector) generateJourneyDescription(path *Path) string {
	return fmt.Sprintf("User navigation pattern with %d steps", len(path.Nodes))
}

// pathLinksToJourneyLinks converts path links to journey links
func (d *userFlowDetector) pathLinksToJourneyLinks(path *Path) []Link {
	journeyLinks := make([]Link, 0)
	for i := 0; i < len(path.Nodes)-1; i++ {
		journeyLinks = append(journeyLinks, Link{
			SourceID: path.Nodes[i],
			TargetID: path.Nodes[i+1],
			Type:     "user_navigation",
			Weight:   1,
		})
	}
	return journeyLinks
}

// calculateInitialScore calculates an initial score for a path
func (d *userFlowDetector) calculateInitialScore(path *Path) float64 {
	score := userFlowScoreBase

	// Reward longer paths
	pathLengthFactor := float64(len(path.Nodes)) / float64(d.config.MaxPathLength)
	score += pathLengthFactor * userFlowLengthWeight

	// Reward more frequent paths
	frequencyFactor := float64(path.Frequency) / userFlowFrequencyDivisor
	if frequencyFactor > userFlowFrequencyFactorMax {
		frequencyFactor = userFlowFrequencyFactorMax
	}
	score += frequencyFactor * userFlowFrequencyWeight

	return score
}
