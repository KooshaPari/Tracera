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

// DataFlowDetector detects data flow paths through the system
type DataFlowDetector interface {
	DetectDataPaths(ctx context.Context, projectID string) ([]*DerivedJourney, error)
}

// dataFlowDetector implements DataFlowDetector
type dataFlowDetector struct {
	itemRepo repository.ItemRepository
	linkRepo repository.LinkRepository
	config   *DetectionConfig
}

const (
	dataPathScoreBase              = 0.6
	dataPathLengthWeight           = 0.3
	dataPathCompletenessBonus      = 0.1
	dataPathImportanceBase         = 0.5
	dataPathImportanceLongBonus    = 0.3
	dataPathImportanceMediumBonus  = 0.2
	dataPathImportanceLongMinNodes = 5
	dataPathImportanceMidMinNodes  = 3
	dataPathCompletenessDivisor    = 10
	dataPathProcessingOffset       = 2
)

// NewDataFlowDetector creates a new data flow detector
func NewDataFlowDetector(
	itemRepo repository.ItemRepository,
	linkRepo repository.LinkRepository,
	config *DetectionConfig,
) DataFlowDetector {
	return &dataFlowDetector{
		itemRepo: itemRepo,
		linkRepo: linkRepo,
		config:   config,
	}
}

// DetectDataPaths traces data flow from inputs through processing to storage
func (d *dataFlowDetector) DetectDataPaths(ctx context.Context, projectID string) ([]*DerivedJourney, error) {
	// Get all items for the project
	items, err := d.itemRepo.GetByProjectID(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch items: %w", err)
	}

	if len(items) == 0 {
		return []*DerivedJourney{}, nil
	}

	// Classify items by data flow role
	inputNodes := d.classifyInputNodes(items)
	storageNodes := d.classifyStorageNodes(items)

	// Build data flow graph
	dataFlowGraph := d.buildDataFlowGraph(ctx, items)

	// Find data paths from inputs to storage
	paths := d.findDataPaths(inputNodes, storageNodes, dataFlowGraph)

	// Convert paths to journeys
	journeys := d.pathsToJourneys(paths, projectID)

	return journeys, nil
}

// classifyInputNodes identifies items that represent data inputs
func (d *dataFlowDetector) classifyInputNodes(items []*models.Item) map[string]*models.Item {
	inputs := make(map[string]*models.Item)

	for _, item := range items {
		// Check item type and title for input indicators
		if d.isInputType(item.Type) || d.isInputTitle(item.Title) {
			inputs[item.ID] = item
		}
	}

	return inputs
}

// classifyStorageNodes identifies items that represent data storage
func (d *dataFlowDetector) classifyStorageNodes(items []*models.Item) map[string]*models.Item {
	storage := make(map[string]*models.Item)

	for _, item := range items {
		if d.isStorageType(item.Type) || d.isStorageTitle(item.Title) {
			storage[item.ID] = item
		}
	}

	return storage
}

// isInputType checks if item type indicates data input
func (d *dataFlowDetector) isInputType(itemType string) bool {
	inputTypes := map[string]bool{
		"input":      true,
		"api":        true,
		"request":    true,
		"endpoint":   true,
		"stream":     true,
		"source":     true,
		"event":      true,
		"form":       true,
		"datasource": true,
	}
	return inputTypes[itemType]
}

// isInputTitle checks if item title indicates data input
func (d *dataFlowDetector) isInputTitle(title string) bool {
	indicators := []string{"input", "request", "api", "upload", "import", "read", "receive"}
	for _, ind := range indicators {
		if len(title) > len(ind) && (title[:len(ind)] == ind || title[len(title)-len(ind):] == ind) {
			return true
		}
	}
	return false
}

// isProcessingType checks if item type indicates processing
func (d *dataFlowDetector) isProcessingType(itemType string) bool {
	processingTypes := map[string]bool{
		"service":     true,
		"function":    true,
		"transformer": true,
		"processor":   true,
		"handler":     true,
		"middleware":  true,
		"validator":   true,
		"converter":   true,
		"aggregator":  true,
		"filter":      true,
	}
	return processingTypes[itemType]
}

// isProcessingTitle checks if item title indicates processing
func (d *dataFlowDetector) isProcessingTitle(title string) bool {
	indicators := []string{"process", "transform", "convert", "validate", "handle", "filter", "map"}
	for _, ind := range indicators {
		if len(title) > len(ind) && (title[:len(ind)] == ind || title[len(title)-len(ind):] == ind) {
			return true
		}
	}
	return false
}

// isStorageType checks if item type indicates storage
func (d *dataFlowDetector) isStorageType(itemType string) bool {
	storageTypes := map[string]bool{
		"database":   true,
		"table":      true,
		"cache":      true,
		"storage":    true,
		"repository": true,
		"store":      true,
		"file":       true,
		"index":      true,
		"queue":      true,
	}
	return storageTypes[itemType]
}

// isStorageTitle checks if item title indicates storage
func (d *dataFlowDetector) isStorageTitle(title string) bool {
	indicators := []string{"storage", "database", "cache", "store", "save", "persist", "index"}
	for _, ind := range indicators {
		if len(title) > len(ind) && (title[:len(ind)] == ind || title[len(title)-len(ind):] == ind) {
			return true
		}
	}
	return false
}

// buildDataFlowGraph constructs a graph of data dependencies
func (d *dataFlowDetector) buildDataFlowGraph(ctx context.Context, items []*models.Item) map[string][]*models.Link {
	graph := make(map[string][]*models.Link)

	for _, item := range items {
		if !d.isProcessingType(item.Type) &&
			!d.isProcessingTitle(item.Title) &&
			!d.isStorageType(item.Type) &&
			!d.isStorageTitle(item.Title) {
			continue
		}
		// Get all links from this item
		links, err := d.linkRepo.GetBySourceID(ctx, item.ID)
		if err != nil {
			continue
		}
		if len(links) > 0 {
			// Filter for data flow related links
			dataFlowLinks := d.filterDataFlowLinks(links)
			if len(dataFlowLinks) > 0 {
				graph[item.ID] = dataFlowLinks
			}
		}
	}

	return graph
}

// filterDataFlowLinks selects links that represent data flow
func (d *dataFlowDetector) filterDataFlowLinks(links []*models.Link) []*models.Link {
	dataFlowTypes := map[string]bool{
		"flows_to":      true,
		"writes_to":     true,
		"reads_from":    true,
		"transforms_to": true,
		"pipes_to":      true,
		"feeds":         true,
		"consumes":      true,
		"produces":      true,
		"stores":        true,
		"retrieves":     true,
		"depends_on":    true,
	}

	var filtered []*models.Link
	for _, link := range links {
		if dataFlowTypes[link.Type] {
			filtered = append(filtered, link)
		}
	}

	return filtered
}

// findDataPaths discovers data flow paths from inputs to storage
func (d *dataFlowDetector) findDataPaths(
	inputs map[string]*models.Item,
	storage map[string]*models.Item,
	graph map[string][]*models.Link,
) []*Path {
	paths := make([]*Path, 0)

	// For each input node, find paths to storage
	for inputID := range inputs {
		d.findPathsBFS(inputID, storage, graph, &paths)
	}

	return paths
}

// expandBFSNeighbors enqueues unvisited neighbors and records their parent/link mappings.
func expandBFSNeighbors(
	graph map[string][]*models.Link, current string, visited map[string]bool,
	queue *[]string, parentMap, linkMap map[string]string,
) {
	if links, ok := graph[current]; ok {
		for _, link := range links {
			if !visited[link.TargetID] {
				parentMap[link.TargetID] = current
				linkMap[link.TargetID] = link.ID
				*queue = append(*queue, link.TargetID)
			}
		}
	}
}

// findPathsBFS uses breadth-first search to find data paths
func (d *dataFlowDetector) findPathsBFS(
	startID string,
	targets map[string]*models.Item,
	graph map[string][]*models.Link,
	paths *[]*Path,
) {
	visited := make(map[string]bool)
	queue := []string{startID}
	parentMap := make(map[string]string)
	linkMap := make(map[string]string)

	for len(queue) > 0 {
		current := queue[0]
		queue = queue[1:]

		if visited[current] {
			continue
		}
		visited[current] = true

		// Check if we reached a target
		if _, isTarget := targets[current]; isTarget && current != startID {
			path := d.reconstructPath(startID, current, parentMap, linkMap)
			if len(path.Nodes) >= d.config.MinPathLength && len(path.Nodes) <= d.config.MaxPathLength {
				path.Type = DataPath
				*paths = append(*paths, path)
			}
			continue
		}

		expandBFSNeighbors(graph, current, visited, &queue, parentMap, linkMap)
	}
}

// reconstructPath reconstructs a path from parent map
func (d *dataFlowDetector) reconstructPath(start, end string, parentMap, linkMap map[string]string) *Path {
	path := &Path{
		Nodes: []string{},
		Links: []string{},
		Type:  DataPath,
	}

	current := end
	for current != start && current != "" {
		path.Nodes = append([]string{current}, path.Nodes...)
		if linkID, ok := linkMap[current]; ok {
			path.Links = append([]string{linkID}, path.Links...)
		}
		current = parentMap[current]
	}
	path.Nodes = append([]string{start}, path.Nodes...)

	return path
}

// pathsToJourneys converts JourneyPaths to DerivedJourney objects
func (d *dataFlowDetector) pathsToJourneys(paths []*Path, projectID string) []*DerivedJourney {
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
				Type:      DataPath,
				NodeIDs:   path.Nodes,
				Links:     d.pathLinksToJourneyLinks(path),
				Score:     d.calculateInitialScore(path),
				CreatedAt: time.Now(),
				UpdatedAt: time.Now(),
				Metadata: Metadata{
					Frequency:    1,
					Importance:   d.calculateDataPathImportance(path),
					Completeness: float64(len(path.Nodes)) / float64(dataPathCompletenessDivisor),
					Description:  d.generateJourneyDescription(path),
					Tags:         []string{"data_path", "data_flow"},
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
func (d *dataFlowDetector) generatePathKey(path *Path) string {
	var builder strings.Builder
	for i, nodeID := range path.Nodes {
		if i > 0 {
			builder.WriteString("->")
		}
		builder.WriteString(nodeID)
	}
	return builder.String()
}

// generateJourneyName creates a human-readable name for a journey
func (d *dataFlowDetector) generateJourneyName(path *Path) string {
	if len(path.Nodes) == 0 {
		return "Empty Data Path"
	}
	if len(path.Nodes) == 1 {
		return "Data in " + path.Nodes[0]
	}
	return "Data path: " + path.Nodes[0] + " → ... → " + path.Nodes[len(path.Nodes)-1]
}

// generateJourneyDescription creates a detailed description
func (d *dataFlowDetector) generateJourneyDescription(path *Path) string {
	return fmt.Sprintf("Data flow from input through %d processing steps to storage", len(path.Nodes)-dataPathProcessingOffset)
}

// pathLinksToJourneyLinks converts path links to journey links
func (d *dataFlowDetector) pathLinksToJourneyLinks(path *Path) []Link {
	journeyLinks := make([]Link, 0)
	for i := 0; i < len(path.Nodes)-1; i++ {
		journeyLinks = append(journeyLinks, Link{
			SourceID: path.Nodes[i],
			TargetID: path.Nodes[i+1],
			Type:     "data_flow",
			Weight:   1,
		})
	}
	return journeyLinks
}

// calculateInitialScore calculates an initial score for a path
func (d *dataFlowDetector) calculateInitialScore(path *Path) float64 {
	score := dataPathScoreBase

	// Reward longer paths (more complex flows)
	pathLengthFactor := float64(len(path.Nodes)) / float64(d.config.MaxPathLength)
	score += pathLengthFactor * dataPathLengthWeight

	// Reward completeness (from input to storage)
	score += dataPathCompletenessBonus

	return score
}

// calculateDataPathImportance determines the importance of a data path
func (d *dataFlowDetector) calculateDataPathImportance(path *Path) float64 {
	// Base importance on path length and coverage
	importance := dataPathImportanceBase

	// Longer paths indicate more critical flows
	if len(path.Nodes) > dataPathImportanceLongMinNodes {
		importance += dataPathImportanceLongBonus
	} else if len(path.Nodes) > dataPathImportanceMidMinNodes {
		importance += dataPathImportanceMediumBonus
	}

	return importance
}
