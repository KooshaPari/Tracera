package graph

import (
	"context"
	"fmt"
	"log/slog"
	"strconv"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"

	"github.com/kooshapari/tracertm-backend/internal/cache"
)

const (
	cycleSeverityErrorMaxLength = 3
	graphPercentScale           = 100.0
	graphPairEdgeDivisor        = 2
	impactLevelDirect           = 1
	impactLevelIndirect         = 2
)

// AnalysisService provides high-performance graph analysis operations
type AnalysisService struct {
	driver neo4j.DriverWithContext
	cache  cache.Cache
}

// NewAnalysisService creates a new graph analysis service
func NewAnalysisService(driver neo4j.DriverWithContext, cache cache.Cache) *AnalysisService {
	return &AnalysisService{
		driver: driver,
		cache:  cache,
	}
}

func (s *AnalysisService) setCache(ctx context.Context, cacheKey string, value interface{}) {
	if s.cache == nil {
		return
	}
	if err := s.cache.Set(ctx, cacheKey, value); err != nil {
		slog.Error("failed to set graph cache for", "error", cacheKey, "error", err)
	}
}

func closeSession(ctx context.Context, session neo4j.SessionWithContext) {
	if session == nil {
		return
	}
	if err := session.Close(ctx); err != nil {
		slog.Error("failed to close neo4j session", "error", err)
	}
}

// ShortestPath finds the shortest path between two items
func (s *AnalysisService) ShortestPath(ctx context.Context, sourceID, targetID string) (*Path, error) {
	cacheKey := "graph:path:" + sourceID + ":" + targetID

	if cached := s.getCachedPath(ctx, cacheKey); cached != nil {
		return cached, nil
	}

	session := s.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer closeSession(ctx, session)

	path, err := s.queryShortestPath(ctx, session, sourceID, targetID)
	if err != nil {
		return nil, err
	}

	// Cache for 5 minutes
	s.setCache(ctx, cacheKey, path)

	return path, nil
}

func (s *AnalysisService) getCachedPath(ctx context.Context, cacheKey string) *Path {
	if s.cache == nil {
		return nil
	}
	var cached Path
	if err := s.cache.Get(ctx, cacheKey, &cached); err == nil && cached.Source != "" {
		return &cached
	}
	return nil
}

func (s *AnalysisService) queryShortestPath(
	ctx context.Context,
	session neo4j.SessionWithContext,
	sourceID string,
	targetID string,
) (*Path, error) {
	query := `
		MATCH path = shortestPath((source:Item {id: $sourceID})-[*]-(target:Item {id: $targetID}))
		RETURN
			[node IN nodes(path) | node.id] AS nodes,
			[rel IN relationships(path) | type(rel)] AS link_types,
			length(path) AS length
	`

	result, err := session.Run(ctx, query, map[string]interface{}{
		"sourceID": sourceID,
		"targetID": targetID,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to execute shortest path query: %w", err)
	}

	record, err := result.Single(ctx)
	if err != nil {
		return nil, fmt.Errorf("no path found between %s and %s", sourceID, targetID)
	}

	nodes, _ := record.Get("nodes")
	linkTypes, _ := record.Get("link_types")
	length, _ := record.Get("length")

	nodeList := asStringList(nodes)
	linkTypeList := asStringList(linkTypes)
	pathLength := extractPathLength(length)

	path := &Path{
		Source:    sourceID,
		Target:    targetID,
		Nodes:     nodeList,
		Length:    pathLength,
		LinkTypes: linkTypeList,
	}

	return path, nil
}

func asStringList(value interface{}) []string {
	nodeList := make([]string, 0)
	nodeSlice, ok := value.([]interface{})
	if !ok {
		return nodeList
	}
	for _, item := range nodeSlice {
		if itemStr, ok := item.(string); ok {
			nodeList = append(nodeList, itemStr)
		}
	}
	return nodeList
}

func extractPathLength(value interface{}) int {
	length, ok := value.(int64)
	if !ok {
		return 0
	}
	return int(length)
}

// DetectCycles finds all cycles in the project graph
func (s *AnalysisService) DetectCycles(ctx context.Context, projectID string) ([]Cycle, error) {
	cacheKey := "graph:cycles:" + projectID

	// Try cache first
	var cached []Cycle
	if err := s.cache.Get(ctx, cacheKey, &cached); err == nil && len(cached) > 0 {
		return cached, nil
	}

	session := s.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer closeSession(ctx, session)

	query := `
		MATCH (n:Item)-[r*]->(n)
		WHERE n.project_id = $projectID
		RETURN DISTINCT
			[node IN nodes(r) | node.id] AS cycle_nodes,
			length(r) AS cycle_length
		LIMIT 100
	`

	result, err := session.Run(ctx, query, map[string]interface{}{
		"projectID": projectID,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to execute cycle detection query: %w", err)
	}

	cycles := make([]Cycle, 0)
	for result.Next(ctx) {
		if cycle, ok := parseCycleRecord(result.Record()); ok {
			cycles = append(cycles, cycle)
		}
	}

	// Cache for 5 minutes
	s.setCache(ctx, cacheKey, cycles)

	return cycles, nil
}

// parseCycleRecord extracts a Cycle from a Neo4j result record.
func parseCycleRecord(record *neo4j.Record) (Cycle, bool) {
	nodes, _ := record.Get("cycle_nodes")
	length, _ := record.Get("cycle_length")

	nodeList := make([]string, 0)
	if nodeSlice, ok := nodes.([]interface{}); ok {
		for _, n := range nodeSlice {
			if nodeStr, ok := n.(string); ok {
				nodeList = append(nodeList, nodeStr)
			}
		}
	}

	lengthInt, ok := length.(int64)
	if !ok {
		return Cycle{}, false
	}
	cycleLength := int(lengthInt)
	severity := "warning"
	if cycleLength <= cycleSeverityErrorMaxLength {
		severity = "error"
	}

	return Cycle{
		Nodes:    nodeList,
		Length:   cycleLength,
		Severity: severity,
	}, true
}

// CalculateCentrality computes centrality metrics for a project
func (s *AnalysisService) CalculateCentrality(ctx context.Context, projectID string) (*CentralityMetrics, error) {
	cacheKey := "graph:centrality:" + projectID

	if cached := s.getCachedCentrality(ctx, cacheKey); cached != nil {
		return cached, nil
	}

	session := s.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer closeSession(ctx, session)

	// Betweenness centrality (simplified - full GDS requires Neo4j Enterprise)
	betweennessQuery := `
		MATCH (n:Item {project_id: $projectID})
		OPTIONAL MATCH (n)-[r]-()
		WITH n, count(r) as degree
		RETURN n.id as item_id, degree * 1.0 as score
		ORDER BY score DESC
		LIMIT 100
	`

	betweenness := s.runCentralityQuery(ctx, session, betweennessQuery, projectID)

	// Closeness centrality (simplified)
	closenessQuery := `
		MATCH (n:Item {project_id: $projectID})
		OPTIONAL MATCH (n)-[*1..3]-(other:Item)
		WHERE other.project_id = $projectID
		WITH n, count(DISTINCT other) as reachable
		RETURN n.id as item_id, reachable * 1.0 as score
		ORDER BY score DESC
		LIMIT 100
	`

	closeness := s.runCentralityQuery(ctx, session, closenessQuery, projectID)

	// PageRank (simplified - degree-based)
	pageRank := cloneScores(betweenness)

	// Find most central nodes
	mostCentral := buildCentralNodes(betweenness, closeness, pageRank)

	// Sort by combined score (simple average)
	// In production, use proper ranking algorithm

	metrics := &CentralityMetrics{
		ProjectID:   projectID,
		Betweenness: betweenness,
		Closeness:   closeness,
		PageRank:    pageRank,
		MostCentral: mostCentral,
	}

	// Cache for 5 minutes
	s.setCache(ctx, cacheKey, metrics)

	return metrics, nil
}

func (s *AnalysisService) getCachedCentrality(ctx context.Context, cacheKey string) *CentralityMetrics {
	if s.cache == nil {
		return nil
	}
	var cached CentralityMetrics
	if err := s.cache.Get(ctx, cacheKey, &cached); err == nil && cached.ProjectID != "" {
		return &cached
	}
	return nil
}

func (s *AnalysisService) runCentralityQuery(
	ctx context.Context,
	session neo4j.SessionWithContext,
	query string,
	projectID string,
) map[string]float64 {
	results := make(map[string]float64)
	result, err := session.Run(ctx, query, map[string]interface{}{"projectID": projectID})
	if err != nil {
		return results
	}
	for result.Next(ctx) {
		record := result.Record()
		itemID, _ := record.Get("item_id")
		score, _ := record.Get("score")
		id, ok := itemID.(string)
		if !ok {
			continue
		}
		if parsed, ok := toFloat64(score); ok {
			results[id] = parsed
		}
	}
	return results
}

func toFloat64(value interface{}) (float64, bool) {
	switch typed := value.(type) {
	case float64:
		return typed, true
	case int64:
		return float64(typed), true
	case int:
		return float64(typed), true
	default:
		return 0, false
	}
}

func cloneScores(scores map[string]float64) map[string]float64 {
	cloned := make(map[string]float64, len(scores))
	for id, score := range scores {
		cloned[id] = score
	}
	return cloned
}

func buildCentralNodes(
	betweenness map[string]float64,
	closeness map[string]float64,
	pageRank map[string]float64,
) []CentralNode {
	mostCentral := make([]CentralNode, 0, len(betweenness))
	for id := range betweenness {
		mostCentral = append(mostCentral, CentralNode{
			ItemID:           id,
			BetweennessScore: betweenness[id],
			ClosenessScore:   closeness[id],
			PageRankScore:    pageRank[id],
		})
	}
	return mostCentral
}

// GetDependencies retrieves all forward dependencies for an item
func (s *AnalysisService) GetDependencies(ctx context.Context, itemID string, maxDepth int) (*DependencyTree, error) {
	cacheKey := "graph:deps:" + itemID + ":" + strconv.Itoa(maxDepth)

	if cached := s.getCachedDependencyTree(ctx, cacheKey); cached != nil {
		return cached, nil
	}

	session := s.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer closeSession(ctx, session)

	query := `
		MATCH path = (root:Item {id: $itemID})-[*1..$maxDepth]->(dep:Item)
		RETURN DISTINCT
			dep.id AS item_id,
			type(relationships(path)[0]) AS link_type,
			length(path) AS depth
		ORDER BY depth
	`

	tree, err := s.queryDependencies(ctx, session, itemID, maxDepth, query)
	if err != nil {
		return nil, err
	}
	s.setCache(ctx, cacheKey, tree)
	return tree, nil
}

func (s *AnalysisService) getCachedDependencyTree(ctx context.Context, cacheKey string) *DependencyTree {
	if s.cache == nil {
		return nil
	}
	var cached DependencyTree
	if err := s.cache.Get(ctx, cacheKey, &cached); err == nil && cached.Root != "" {
		return &cached
	}
	return nil
}

func (s *AnalysisService) queryDependencies(
	ctx context.Context,
	session neo4j.SessionWithContext,
	itemID string,
	maxDepth int,
	query string,
) (*DependencyTree, error) {
	result, err := session.Run(ctx, query, map[string]interface{}{
		"itemID":   itemID,
		"maxDepth": maxDepth,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to execute dependencies query: %w", err)
	}

	children, maxObservedDepth := parseDependencyRecords(ctx, result, itemID)
	return &DependencyTree{
		Root:     itemID,
		Depth:    maxObservedDepth,
		Children: children,
	}, nil
}

func parseDependencyRecords(
	ctx context.Context,
	result neo4j.ResultWithContext,
	rootID string,
) (map[string][]Dependency, int) {
	children := make(map[string][]Dependency)
	maxObservedDepth := 0

	for result.Next(ctx) {
		record := result.Record()
		depID, _ := record.Get("item_id")
		linkType, _ := record.Get("link_type")
		depth, _ := record.Get("depth")

		id, ok := depID.(string)
		if !ok {
			continue
		}
		depthVal, ok := depth.(int64)
		if !ok {
			continue
		}
		depthInt := int(depthVal)
		if depthInt > maxObservedDepth {
			maxObservedDepth = depthInt
		}

		linkTypeStr, ok := linkType.(string)
		if !ok {
			linkTypeStr = ""
		}
		children[rootID] = append(children[rootID], Dependency{
			ItemID:   id,
			LinkType: linkTypeStr,
			Depth:    depthInt,
		})
	}

	return children, maxObservedDepth
}

// GetDependents retrieves all backward dependencies (what depends on this item)
func (s *AnalysisService) GetDependents(ctx context.Context, itemID string, maxDepth int) (*DependencyTree, error) {
	cacheKey := "graph:dependents:" + itemID + ":" + strconv.Itoa(maxDepth)

	if cached := s.getCachedDependencyTree(ctx, cacheKey); cached != nil {
		return cached, nil
	}

	session := s.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer closeSession(ctx, session)

	query := `
		MATCH path = (dependent:Item)-[*1..$maxDepth]->(root:Item {id: $itemID})
		RETURN DISTINCT
			dependent.id AS item_id,
			type(relationships(path)[0]) AS link_type,
			length(path) AS depth
		ORDER BY depth
	`

	tree, err := s.queryDependencies(ctx, session, itemID, maxDepth, query)
	if err != nil {
		return nil, err
	}
	s.setCache(ctx, cacheKey, tree)
	return tree, nil
}

// AnalyzeImpact analyzes what items would be affected by changes
func (s *AnalysisService) AnalyzeImpact(ctx context.Context, itemIDs []string) (*ImpactReport, error) {
	if len(itemIDs) == 0 {
		return emptyImpactReport(), nil
	}

	cacheKey := "graph:impact:" + fmt.Sprint(itemIDs)

	// Try cache first
	if cached, ok := s.getCachedImpact(ctx, cacheKey); ok {
		return cached, nil
	}

	session := s.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer closeSession(ctx, session)

	// Find direct dependents
	directQuery := `
		MATCH (source:Item)-[r]->(affected:Item)
		WHERE source.id IN $itemIDs
		RETURN DISTINCT affected.id as item_id, 1 as level
	`

	// Find indirect dependents (up to 3 levels)
	indirectQuery := `
		MATCH (source:Item)-[*2..3]->(affected:Item)
		WHERE source.id IN $itemIDs
		RETURN DISTINCT affected.id as item_id, 2 as level
	`

	impactLevels := make(map[string]int)

	directImpact := addImpactIDs(
		s.collectImpactIDs(ctx, session, directQuery, itemIDs),
		impactLevelDirect,
		impactLevels,
		nil,
		false,
	)
	indirectImpact := addImpactIDs(
		s.collectImpactIDs(ctx, session, indirectQuery, itemIDs),
		impactLevelIndirect,
		impactLevels,
		nil,
		true,
	)

	report := &ImpactReport{
		SourceItems:    itemIDs,
		DirectImpact:   directImpact,
		IndirectImpact: indirectImpact,
		TotalAffected:  len(directImpact) + len(indirectImpact),
		ImpactLevels:   impactLevels,
	}

	// Cache for 5 minutes
	s.setCache(ctx, cacheKey, report)

	return report, nil
}

func emptyImpactReport() *ImpactReport {
	return &ImpactReport{
		SourceItems:    []string{},
		DirectImpact:   []string{},
		IndirectImpact: []string{},
		TotalAffected:  0,
		ImpactLevels:   make(map[string]int),
	}
}

func (s *AnalysisService) getCachedImpact(ctx context.Context, cacheKey string) (*ImpactReport, bool) {
	var cached ImpactReport
	if err := s.cache.Get(ctx, cacheKey, &cached); err == nil && len(cached.SourceItems) > 0 {
		return &cached, true
	}
	return nil, false
}

func (s *AnalysisService) collectImpactIDs(
	ctx context.Context,
	session neo4j.SessionWithContext,
	query string,
	itemIDs []string,
) []string {
	result, err := session.Run(ctx, query, map[string]interface{}{
		"itemIDs": itemIDs,
	})
	if err != nil {
		return nil
	}

	ids := make([]string, 0)
	for result.Next(ctx) {
		record := result.Record()
		itemID, _ := record.Get("item_id")
		if id, ok := itemID.(string); ok {
			ids = append(ids, id)
		}
	}
	return ids
}

func addImpactIDs(
	ids []string,
	level int,
	impactLevels map[string]int,
	current []string,
	skipExisting bool,
) []string {
	for _, id := range ids {
		if skipExisting {
			if _, exists := impactLevels[id]; exists {
				continue
			}
		}
		impactLevels[id] = level
		current = append(current, id)
	}
	return current
}

// AnalyzeCoverage analyzes graph coverage (connected vs isolated items)
func (s *AnalysisService) AnalyzeCoverage(ctx context.Context, projectID string) (*CoverageReport, error) {
	cacheKey := "graph:coverage:" + projectID

	// Try cache first
	var cached CoverageReport
	if err := s.cache.Get(ctx, cacheKey, &cached); err == nil && cached.ProjectID != "" {
		return &cached, nil
	}

	session := s.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer closeSession(ctx, session)

	// Count total items
	totalQuery := `
		MATCH (n:Item {project_id: $projectID})
		RETURN count(n) as total
	`

	// Find isolated items (no relationships)
	isolatedQuery := `
		MATCH (n:Item {project_id: $projectID})
		WHERE NOT (n)--()
		RETURN n.id as item_id
	`

	var totalItems int
	result, err := session.Run(ctx, totalQuery, map[string]interface{}{"projectID": projectID})
	if err == nil {
		if result.Next(ctx) {
			record := result.Record()
			total, _ := record.Get("total")
			if totalVal, ok := total.(int64); ok {
				totalItems = int(totalVal)
			}
		}
	}

	isolatedItems := make([]string, 0)
	result, err = session.Run(ctx, isolatedQuery, map[string]interface{}{"projectID": projectID})
	if err == nil {
		for result.Next(ctx) {
			record := result.Record()
			itemID, _ := record.Get("item_id")
			if id, ok := itemID.(string); ok {
				isolatedItems = append(isolatedItems, id)
			}
		}
	}

	connectedItems := totalItems - len(isolatedItems)
	coveragePercent := 0.0
	if totalItems > 0 {
		coveragePercent = float64(connectedItems) / float64(totalItems) * graphPercentScale
	}

	report := &CoverageReport{
		ProjectID:       projectID,
		TotalItems:      totalItems,
		ConnectedItems:  connectedItems,
		IsolatedItems:   isolatedItems,
		CoveragePercent: coveragePercent,
	}

	// Cache for 5 minutes
	s.setCache(ctx, cacheKey, report)

	return report, nil
}

// GetMetrics computes overall graph statistics
func (s *AnalysisService) GetMetrics(ctx context.Context, projectID string) (*Metrics, error) {
	cacheKey := "graph:metrics:" + projectID
	// Try cache first
	var cached Metrics
	if err := s.cache.Get(ctx, cacheKey, &cached); err == nil {
		return &cached, nil
	}

	session := s.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer closeSession(ctx, session)

	query := `
		MATCH (n:Item {project_id: $projectID})
		OPTIONAL MATCH (n)-[r]-()
		WITH count(DISTINCT n) as nodes, count(DISTINCT r)/2 as edges, avg(count(r)) as avg_degree
		RETURN nodes, edges, avg_degree
	`

	result, err := session.Run(ctx, query, map[string]interface{}{"projectID": projectID})
	if err != nil {
		return nil, fmt.Errorf("failed to compute graph metrics: %w", err)
	}

	var nodes, edges int64
	var avgDegree float64

	if result.Next(ctx) {
		record := result.Record()
		n, _ := record.Get("nodes")
		e, _ := record.Get("edges")
		ad, _ := record.Get("avg_degree")

		if nVal, ok := n.(int64); ok {
			nodes = nVal
		}
		if eVal, ok := e.(int64); ok {
			edges = eVal
		}
		if ad != nil {
			if adVal, ok := ad.(float64); ok {
				avgDegree = adVal
			}
		}
	}

	// Calculate density
	density := 0.0
	if nodes > 1 {
		maxEdges := nodes * (nodes - 1) / graphPairEdgeDivisor
		density = float64(edges) / float64(maxEdges)
	}

	metrics := &Metrics{
		ProjectID:           projectID,
		TotalNodes:          int(nodes),
		TotalEdges:          int(edges),
		Density:             density,
		AvgDegree:           avgDegree,
		MaxDepth:            0, // Would require separate BFS query
		ConnectedComponents: 0, // Would require component detection
	}

	// Cache for 5 minutes
	s.setCache(ctx, cacheKey, metrics)

	return metrics, nil
}

// InvalidateCache clears all graph analysis caches for a project
func (s *AnalysisService) InvalidateCache(ctx context.Context, projectID string) error {
	patterns := []string{
		"graph:*:" + projectID,
		"graph:*:" + projectID + ":*",
	}

	for _, pattern := range patterns {
		if err := s.cache.InvalidatePattern(ctx, pattern); err != nil {
			return err
		}
	}

	return nil
}
