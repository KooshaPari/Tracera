package codeindex

import (
	"context"
	"fmt"
	"strings"
	"sync"

	"github.com/google/uuid"
)

const (
	manualMappingConfidence    = 1.0
	confidenceDepthPenalty     = 0.1
	minDepthConfidence         = 0.5
	relatedEntityConfidence    = 0.95
	referenceEdgeConfidence    = 0.9
	confidenceRangeHigh        = 0.9
	confidenceRangeMedium      = 0.7
	confidenceRangeLow         = 0.5
	confidenceRangeHighLabel   = "0.9-1.0"
	confidenceRangeMediumLabel = "0.7-0.9"
	confidenceRangeLowLabel    = "0.5-0.7"
	confidenceRangeMinLabel    = "<0.5"
	confidenceAverageDivisor   = 2.0
)

// CodeEntityLinker links parsed code entities to canonical concepts
// This bridges code-level entities with high-level business concepts
type CodeEntityLinker struct {
	entities          map[uuid.UUID]*ParsedEntity
	canonicalMappings map[uuid.UUID][]CanonicalMapping // entityID -> canonical concepts
	referenceResolver *ReferenceResolver
	mu                sync.RWMutex
}

// CanonicalMapping represents the linkage between a code entity and a canonical concept
type CanonicalMapping struct {
	CanonicalID      uuid.UUID
	EntityID         uuid.UUID
	Confidence       float64 // 0-1, how strongly linked
	Source           string  // "manual", "inferred", "pattern", "semantic"
	DetectedPatterns []string
	Description      string
}

// EntityPattern defines a pattern for matching entities to canonical concepts
type EntityPattern struct {
	Name          string
	Description   string
	Priority      int // Higher = checked first
	MatchRules    []MatchRule
	CanonicalsMap map[string]uuid.UUID // pattern match -> canonical ID
}

// MatchRule defines a single rule for pattern matching
type MatchRule struct {
	Type       string // "name_contains", "name_regex", "annotation", "hierarchy", "calls"
	Pattern    string
	Negate     bool
	Confidence float64
}

// NewCodeEntityLinker creates a new code entity linker
func NewCodeEntityLinker(resolver *ReferenceResolver) *CodeEntityLinker {
	return &CodeEntityLinker{
		entities:          make(map[uuid.UUID]*ParsedEntity),
		canonicalMappings: make(map[uuid.UUID][]CanonicalMapping),
		referenceResolver: resolver,
	}
}

// AddEntity registers a code entity for linking
func (cel *CodeEntityLinker) AddEntity(entity *ParsedEntity) {
	cel.mu.Lock()
	defer cel.mu.Unlock()
	cel.entities[entity.ID] = entity
}

// LinkToCanonical creates an explicit manual link from entity to canonical concept
func (cel *CodeEntityLinker) LinkToCanonical(
	_ context.Context,
	entityID uuid.UUID,
	canonicalID uuid.UUID,
	confidence float64,
) error {
	cel.mu.Lock()
	defer cel.mu.Unlock()

	if _, ok := cel.entities[entityID]; !ok {
		return fmt.Errorf("entity not found: %s", entityID)
	}

	mapping := CanonicalMapping{
		CanonicalID: canonicalID,
		EntityID:    entityID,
		Confidence:  confidence,
		Source:      "manual",
	}

	cel.canonicalMappings[entityID] = append(cel.canonicalMappings[entityID], mapping)
	return nil
}

// InferCanonicalLinks uses patterns to infer canonical concept links
func (cel *CodeEntityLinker) InferCanonicalLinks(_ context.Context, patterns []*EntityPattern) error {
	cel.mu.Lock()
	defer cel.mu.Unlock()

	for entityID, entity := range cel.entities {
		cel.inferMappingsForEntity(entityID, entity, patterns)
	}

	return nil
}

func (cel *CodeEntityLinker) inferMappingsForEntity(
	entityID uuid.UUID,
	entity *ParsedEntity,
	patterns []*EntityPattern,
) {
	for _, pattern := range patterns {
		if !cel.matchesPattern(entity, pattern) {
			continue
		}
		cel.addPatternMappings(entityID, entity, pattern)
	}
}

func (cel *CodeEntityLinker) addPatternMappings(
	entityID uuid.UUID,
	entity *ParsedEntity,
	pattern *EntityPattern,
) {
	for _, rule := range pattern.MatchRules {
		if rule.Pattern == "" {
			continue
		}
		cel.appendCanonicalMappings(entityID, entity, pattern, rule)
	}
}

func (cel *CodeEntityLinker) appendCanonicalMappings(
	entityID uuid.UUID,
	entity *ParsedEntity,
	pattern *EntityPattern,
	rule MatchRule,
) {
	for patternMatch, canonicalID := range pattern.CanonicalsMap {
		if !strings.Contains(entity.Name, patternMatch) {
			continue
		}
		mapping := CanonicalMapping{
			CanonicalID:      canonicalID,
			EntityID:         entityID,
			Confidence:       rule.Confidence,
			Source:           "pattern",
			DetectedPatterns: []string{pattern.Name},
			Description:      "Matched pattern: " + pattern.Name,
		}
		cel.canonicalMappings[entityID] = append(cel.canonicalMappings[entityID], mapping)
	}
}

// matchesPattern checks if an entity matches a pattern
func (cel *CodeEntityLinker) matchesPattern(entity *ParsedEntity, pattern *EntityPattern) bool {
	for _, rule := range pattern.MatchRules {
		if !cel.ruleMatches(entity, rule) {
			return false
		}
	}

	return true
}

func (cel *CodeEntityLinker) ruleMatches(entity *ParsedEntity, rule MatchRule) bool {
	matches := cel.ruleBaseMatch(entity, rule)
	if rule.Negate {
		return !matches
	}
	return matches
}

func (cel *CodeEntityLinker) ruleBaseMatch(entity *ParsedEntity, rule MatchRule) bool {
	switch rule.Type {
	case "name_contains":
		return strings.Contains(entity.Name, rule.Pattern)
	case "name_regex":
		// Simple regex match (could use regexp for more complex patterns)
		return strings.Contains(entity.Name, rule.Pattern)
	case "annotation":
		return cel.hasAnnotation(entity, rule.Pattern)
	case "hierarchy":
		return entity.ParentName == rule.Pattern
	case "calls":
		return cel.hasCallTarget(entity, rule.Pattern)
	default:
		return false
	}
}

func (cel *CodeEntityLinker) hasAnnotation(entity *ParsedEntity, pattern string) bool {
	for _, annotation := range entity.Annotations {
		if annotation.Name == pattern {
			return true
		}
	}
	return false
}

func (cel *CodeEntityLinker) hasCallTarget(entity *ParsedEntity, targetName string) bool {
	for _, call := range entity.Calls {
		if call.TargetName == targetName {
			return true
		}
	}
	return false
}

// GetCanonicalForEntity returns the canonical concepts linked to an entity
func (cel *CodeEntityLinker) GetCanonicalForEntity(entityID uuid.UUID) []CanonicalMapping {
	cel.mu.RLock()
	defer cel.mu.RUnlock()
	return cel.canonicalMappings[entityID]
}

// GetEntitiesForCanonical returns all entities linked to a canonical concept
func (cel *CodeEntityLinker) GetEntitiesForCanonical(canonicalID uuid.UUID) []*ParsedEntity {
	cel.mu.RLock()
	defer cel.mu.RUnlock()

	entities := make([]*ParsedEntity, 0)
	for _, mappings := range cel.canonicalMappings {
		for _, mapping := range mappings {
			if mapping.CanonicalID == canonicalID {
				if entity, ok := cel.entities[mapping.EntityID]; ok {
					entities = append(entities, entity)
				}
			}
		}
	}
	return entities
}

// LinkCallChainToCanonical links an entire call chain to a canonical concept
func (cel *CodeEntityLinker) LinkCallChainToCanonical(
	_ context.Context,
	chain *CallChainResolution,
	canonicalID uuid.UUID,
) error {
	cel.mu.Lock()
	defer cel.mu.Unlock()

	// Link entry point
	if chain.EntryPoint != nil {
		mapping := CanonicalMapping{
			CanonicalID: canonicalID,
			EntityID:    chain.EntryPoint.ID,
			Confidence:  manualMappingConfidence,
			Source:      "manual",
			Description: "Entry point of linked call chain",
		}
		cel.canonicalMappings[chain.EntryPoint.ID] = append(cel.canonicalMappings[chain.EntryPoint.ID], mapping)
	}

	// Link steps with decreasing confidence
	for index, step := range chain.Steps {
		if step.Entity != nil {
			// Decrease confidence by depth.
			confidence := manualMappingConfidence - (float64(index) * confidenceDepthPenalty)
			if confidence < minDepthConfidence {
				confidence = minDepthConfidence // Minimum confidence
			}

			mapping := CanonicalMapping{
				CanonicalID: canonicalID,
				EntityID:    step.Entity.ID,
				Confidence:  confidence,
				Source:      "pattern",
				Description: fmt.Sprintf("Called in chain at depth %d", index),
			}
			cel.canonicalMappings[step.Entity.ID] = append(cel.canonicalMappings[step.Entity.ID], mapping)
		}
	}

	return nil
}

// FindRelatedEntities finds other entities related to a given entity
// (either calling it, called by it, or sharing canonical mappings)
func (cel *CodeEntityLinker) FindRelatedEntities(_ context.Context, entityID uuid.UUID) []*RelatedEntity {
	cel.mu.RLock()
	defer cel.mu.RUnlock()

	entity, ok := cel.entities[entityID]
	if !ok {
		return nil
	}

	related := make([]*RelatedEntity, 0)
	seen := make(map[uuid.UUID]bool)

	cel.appendCalledEntities(entity, seen, &related)
	cel.appendCallingEntities(entityID, seen, &related)
	cel.appendSharedCanonicals(entityID, seen, &related)

	return related
}

func (cel *CodeEntityLinker) appendCalledEntities(
	entity *ParsedEntity,
	seen map[uuid.UUID]bool,
	related *[]*RelatedEntity,
) {
	for _, call := range entity.Calls {
		if call.TargetID == nil {
			continue
		}
		target, ok := cel.entities[*call.TargetID]
		if !ok {
			continue
		}
		cel.addRelatedEntity(*call.TargetID, target, "calls", relatedEntityConfidence, seen, related)
	}
}

func (cel *CodeEntityLinker) appendCallingEntities(
	entityID uuid.UUID,
	seen map[uuid.UUID]bool,
	related *[]*RelatedEntity,
) {
	for otherID, other := range cel.entities {
		if otherID == entityID || seen[otherID] {
			continue
		}
		if !cel.callsEntity(other, entityID) {
			continue
		}
		cel.addRelatedEntity(otherID, other, "called_by", relatedEntityConfidence, seen, related)
	}
}

func (cel *CodeEntityLinker) callsEntity(entity *ParsedEntity, targetID uuid.UUID) bool {
	for _, call := range entity.Calls {
		if call.TargetID != nil && *call.TargetID == targetID {
			return true
		}
	}
	return false
}

func (cel *CodeEntityLinker) appendSharedCanonicals(
	entityID uuid.UUID,
	seen map[uuid.UUID]bool,
	related *[]*RelatedEntity,
) {
	for _, mapping := range cel.canonicalMappings[entityID] {
		cel.appendSharedCanonicalForMapping(entityID, mapping, seen, related)
	}
}

func (cel *CodeEntityLinker) appendSharedCanonicalForMapping(
	entityID uuid.UUID,
	mapping CanonicalMapping,
	seen map[uuid.UUID]bool,
	related *[]*RelatedEntity,
) {
	for otherID, otherMappings := range cel.canonicalMappings {
		if otherID == entityID || seen[otherID] {
			continue
		}
		if !cel.hasSharedCanonical(mapping.CanonicalID, otherMappings) {
			continue
		}
		otherEntity, ok := cel.entities[otherID]
		if !ok {
			continue
		}
		confidence := cel.averageConfidence(mapping.Confidence, otherMappings, mapping.CanonicalID)
		cel.addRelatedEntity(otherID, otherEntity, "shares_canonical", confidence, seen, related)
	}
}

func (cel *CodeEntityLinker) hasSharedCanonical(canonicalID uuid.UUID, mappings []CanonicalMapping) bool {
	for _, mapping := range mappings {
		if mapping.CanonicalID == canonicalID {
			return true
		}
	}
	return false
}

func (cel *CodeEntityLinker) averageConfidence(
	base float64,
	mappings []CanonicalMapping,
	canonicalID uuid.UUID,
) float64 {
	for _, mapping := range mappings {
		if mapping.CanonicalID == canonicalID {
			return (base + mapping.Confidence) / confidenceAverageDivisor
		}
	}
	return base
}

func (cel *CodeEntityLinker) addRelatedEntity(
	entityID uuid.UUID,
	entity *ParsedEntity,
	relationship string,
	confidence float64,
	seen map[uuid.UUID]bool,
	related *[]*RelatedEntity,
) {
	if seen[entityID] {
		return
	}
	*related = append(*related, &RelatedEntity{
		Entity:       entity,
		Relationship: relationship,
		Confidence:   confidence,
	})
	seen[entityID] = true
}

// RelatedEntity represents an entity related to another
type RelatedEntity struct {
	Entity       *ParsedEntity
	Relationship string // "calls", "called_by", "shares_canonical", etc.
	Confidence   float64
}

// BuildSemanticGraph builds a semantic graph of entities based on canonical mappings
func (cel *CodeEntityLinker) BuildSemanticGraph() *SemanticGraph {
	cel.mu.RLock()
	defer cel.mu.RUnlock()

	graph := newSemanticGraph()
	cel.populateConcepts(graph)
	cel.populateNodes(graph)
	cel.populateEdges(graph)
	return graph
}

func newSemanticGraph() *SemanticGraph {
	return &SemanticGraph{
		Nodes:    make([]*SemanticNode, 0),
		Edges:    make([]*SemanticEdge, 0),
		Concepts: make(map[uuid.UUID]*ConceptNode),
	}
}

func (cel *CodeEntityLinker) populateConcepts(graph *SemanticGraph) {
	seenConcepts := make(map[uuid.UUID]bool)
	for _, mappings := range cel.canonicalMappings {
		for _, mapping := range mappings {
			if seenConcepts[mapping.CanonicalID] {
				continue
			}
			graph.Concepts[mapping.CanonicalID] = &ConceptNode{
				ID:       mapping.CanonicalID,
				Entities: make([]*ParsedEntity, 0),
			}
			seenConcepts[mapping.CanonicalID] = true
		}
	}
}

func (cel *CodeEntityLinker) populateNodes(graph *SemanticGraph) {
	for _, entity := range cel.entities {
		graph.Nodes = append(graph.Nodes, &SemanticNode{
			Entity:    entity,
			Canonical: cel.canonicalMappings[entity.ID],
		})

		for _, mapping := range cel.canonicalMappings[entity.ID] {
			graph.Concepts[mapping.CanonicalID].Entities = append(graph.Concepts[mapping.CanonicalID].Entities, entity)
		}
	}
}

func (cel *CodeEntityLinker) populateEdges(graph *SemanticGraph) {
	for _, entity := range cel.entities {
		for _, call := range entity.Calls {
			if call.TargetID != nil {
				graph.Edges = append(graph.Edges, &SemanticEdge{
					SourceID:   entity.ID,
					TargetID:   *call.TargetID,
					Type:       "calls",
					Confidence: relatedEntityConfidence,
				})
			}
		}

		for _, ref := range entity.References {
			if ref.SymbolID != nil {
				graph.Edges = append(graph.Edges, &SemanticEdge{
					SourceID:   entity.ID,
					TargetID:   *ref.SymbolID,
					Type:       "references",
					Confidence: referenceEdgeConfidence,
				})
			}
		}
	}
}

// SemanticGraph represents entities and their relationships
type SemanticGraph struct {
	Nodes    []*SemanticNode
	Edges    []*SemanticEdge
	Concepts map[uuid.UUID]*ConceptNode
}

// SemanticNode represents a node in the semantic graph
type SemanticNode struct {
	Entity    *ParsedEntity
	Canonical []CanonicalMapping
}

// SemanticEdge represents an edge in the semantic graph
type SemanticEdge struct {
	SourceID   uuid.UUID
	TargetID   uuid.UUID
	Type       string // "calls", "references", "extends", etc.
	Confidence float64
}

// ConceptNode represents a canonical concept node
type ConceptNode struct {
	ID       uuid.UUID
	Entities []*ParsedEntity
}

// GetLinkingStatistics returns statistics about entity-canonical linkage
func (cel *CodeEntityLinker) GetLinkingStatistics() *LinkingStats {
	cel.mu.RLock()
	defer cel.mu.RUnlock()

	stats := cel.initializeLinkingStats()
	var totalConfidence float64

	for _, mappings := range cel.canonicalMappings {
		if len(mappings) == 0 {
			stats.UnlinkedEntities++
			continue
		}

		stats.LinkedEntities++
		stats.TotalMappings += len(mappings)
		totalConfidence += cel.processMappingsForStats(mappings, stats)
	}

	if stats.TotalMappings > 0 {
		stats.AverageConfidence = totalConfidence / float64(stats.TotalMappings)
	}

	return stats
}

func (cel *CodeEntityLinker) initializeLinkingStats() *LinkingStats {
	return &LinkingStats{
		TotalEntities:    len(cel.entities),
		MappingsBySource: make(map[string]int),
		ConfidenceRanges: make(map[string]int),
	}
}

func (cel *CodeEntityLinker) processMappingsForStats(mappings []CanonicalMapping, stats *LinkingStats) float64 {
	var confidenceSum float64
	for _, mapping := range mappings {
		stats.MappingsBySource[mapping.Source]++
		confidenceSum += mapping.Confidence
		cel.categorizeConfidence(mapping.Confidence, stats)
	}
	return confidenceSum
}

func (cel *CodeEntityLinker) categorizeConfidence(confidence float64, stats *LinkingStats) {
	switch {
	case confidence >= confidenceRangeHigh:
		stats.ConfidenceRanges[confidenceRangeHighLabel]++
	case confidence >= confidenceRangeMedium:
		stats.ConfidenceRanges[confidenceRangeMediumLabel]++
	case confidence >= confidenceRangeLow:
		stats.ConfidenceRanges[confidenceRangeLowLabel]++
	default:
		stats.ConfidenceRanges[confidenceRangeMinLabel]++
	}
}

// LinkingStats contains statistics about entity linking
type LinkingStats struct {
	TotalEntities     int
	LinkedEntities    int
	UnlinkedEntities  int
	TotalMappings     int
	MappingsBySource  map[string]int
	AverageConfidence float64
	ConfidenceRanges  map[string]int
}
