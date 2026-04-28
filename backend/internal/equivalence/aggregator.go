package equivalence

import (
	"sort"
	"time"

	"github.com/google/uuid"
)

const (
	agreementBoostPerStrategy       = 0.1
	explicitConfidenceThreshold     = 1.0
	nonExplicitConfidenceCap        = 0.99
	highConfidenceConflictThreshold = 0.8
	linkTypePriorityDefault         = 100
	linkTypePriorityImplements      = 1
	linkTypePrioritySameAs          = 2
	linkTypePriorityRepresents      = 3
	linkTypePriorityManifestsAs     = 4
	linkTypePriorityTests           = 5
	linkTypePriorityDocuments       = 6
	linkTypePriorityRelatesTo       = 7
)

// ConfidenceAggregator merges equivalence results from multiple strategies
type ConfidenceAggregator struct {
	// Weights for combining confidence scores
	strategyWeights map[StrategyType]float64
	// Boost factor when multiple strategies agree
	agreementBoost float64
}

// NewConfidenceAggregator creates a new confidence aggregator
func NewConfidenceAggregator() *ConfidenceAggregator {
	return &ConfidenceAggregator{
		strategyWeights: map[StrategyType]float64{
			StrategyExplicitAnnotation: strategyConfidenceExplicit,
			StrategyManualLink:         strategyConfidenceExplicit,
			StrategyAPIContract:        strategyConfidenceHigh,
			StrategySharedCanonical:    strategyConfidenceHigh,
			StrategyNamingPattern:      strategyConfidenceMedium,
			StrategySemanticSimilarity: strategyConfidenceLow,
			StrategyStructural:         strategyConfidenceFallback,
		},
		agreementBoost: agreementBoostPerStrategy, // Boost per additional agreeing strategy
	}
}

// Aggregate combines equivalence links from multiple strategies into suggestions
func (aggregator *ConfidenceAggregator) Aggregate(
	source *StrategyItemInfo,
	links []Link,
	minConfidence float64,
) []Suggestion {
	// Group links by target item
	byTarget := make(map[uuid.UUID][]Link)
	for _, link := range links {
		byTarget[link.TargetItemID] = append(byTarget[link.TargetItemID], link)
	}

	suggestions := make([]Suggestion, 0, len(byTarget))

	for targetID, targetLinks := range byTarget {
		if len(targetLinks) == 0 {
			continue
		}

		// Calculate combined confidence
		confidence := aggregator.combineConfidence(targetLinks)
		if confidence < minConfidence {
			continue
		}

		allEvidence, strategies := collectEvidenceAndStrategies(targetLinks)

		// Determine the most appropriate link type
		linkType := aggregator.determineLinkType(targetLinks)

		suggestion := Suggestion{
			ID:              uuid.New(),
			ProjectID:       source.ProjectID,
			SourceItemID:    source.ID,
			SourceItemTitle: source.Title,
			SourceItemType:  source.Type,
			TargetItemID:    targetID,
			TargetItemTitle: "", // Will be populated by service
			TargetItemType:  "", // Will be populated by service
			SuggestedType:   linkType,
			Confidence:      confidence,
			Strategies:      strategies,
			Evidence:        allEvidence,
			CreatedAt:       time.Now(),
		}

		suggestions = append(suggestions, suggestion)
	}

	// Sort by confidence descending
	sort.Slice(suggestions, func(i, j int) bool {
		return suggestions[i].Confidence > suggestions[j].Confidence
	})

	return suggestions
}

func collectEvidenceAndStrategies(targetLinks []Link) ([]Evidence, []StrategyType) {
	totalEvidence := 0
	for _, link := range targetLinks {
		totalEvidence += len(link.Evidence)
	}

	allEvidence := make([]Evidence, 0, totalEvidence)
	strategies := make([]StrategyType, 0, len(targetLinks))
	strategySet := make(map[StrategyType]bool)

	for _, link := range targetLinks {
		allEvidence = append(allEvidence, link.Evidence...)
		if !strategySet[link.Provenance] {
			strategies = append(strategies, link.Provenance)
			strategySet[link.Provenance] = true
		}
	}

	return allEvidence, strategies
}

// combineConfidence calculates a combined confidence score from multiple strategies
func (aggregator *ConfidenceAggregator) combineConfidence(links []Link) float64 {
	if len(links) == 0 {
		return 0.0
	}

	// If any strategy has confidence 1.0, return 1.0 (explicit match)
	for _, link := range links {
		if link.Confidence >= explicitConfidenceThreshold {
			return explicitConfidenceThreshold
		}
	}

	// Weighted average with agreement boost
	var weightedSum, totalWeight float64
	strategies := make(map[StrategyType]bool)

	for _, link := range links {
		weight := aggregator.strategyWeights[link.Provenance]
		if weight == 0 {
			weight = strategyConfidenceFallback // Default weight
		}
		weightedSum += link.Confidence * weight
		totalWeight += weight
		strategies[link.Provenance] = true
	}

	if totalWeight == 0 {
		return 0.0
	}

	baseConfidence := weightedSum / totalWeight

	// Apply agreement boost (multiple strategies finding the same match)
	numStrategies := len(strategies)
	if numStrategies > 1 {
		boost := float64(numStrategies-1) * aggregator.agreementBoost
		baseConfidence += boost
	}

	// Cap at 0.99 for non-explicit matches
	if baseConfidence > nonExplicitConfidenceCap {
		baseConfidence = nonExplicitConfidenceCap
	}

	return baseConfidence
}

// determineLinkType selects the most appropriate link type from candidates
func (aggregator *ConfidenceAggregator) determineLinkType(links []Link) string {
	// Priority order for link types
	priority := map[string]int{
		"implements":   linkTypePriorityImplements,
		"same_as":      linkTypePrioritySameAs,
		"represents":   linkTypePriorityRepresents,
		"manifests_as": linkTypePriorityManifestsAs,
		"tests":        linkTypePriorityTests,
		"documents":    linkTypePriorityDocuments,
		"relates_to":   linkTypePriorityRelatesTo,
	}

	bestType := links[0].LinkType
	bestPriority := priority[bestType]
	if bestPriority == 0 {
		bestPriority = linkTypePriorityDefault
	}

	for _, link := range links[1:] {
		p := priority[link.LinkType]
		if p == 0 {
			p = linkTypePriorityDefault
		}
		if p < bestPriority {
			bestPriority = p
			bestType = link.LinkType
		}
	}

	return bestType
}

// DetectConflicts identifies conflicting equivalence suggestions
func (aggregator *ConfidenceAggregator) DetectConflicts(suggestions []Suggestion) []Conflict {
	var conflicts []Conflict

	// Check for items mapped to multiple different targets with high confidence
	bySource := make(map[uuid.UUID][]Suggestion)
	for _, s := range suggestions {
		bySource[s.SourceItemID] = append(bySource[s.SourceItemID], s)
	}

	for _, sourceSuggestions := range bySource {
		if len(sourceSuggestions) <= 1 {
			continue
		}

		// Check if multiple high-confidence suggestions exist
		highConf := make([]Suggestion, 0)
		for _, s := range sourceSuggestions {
			if s.Confidence >= highConfidenceConflictThreshold {
				highConf = append(highConf, s)
			}
		}

		if len(highConf) > 1 {
			conflicts = append(conflicts, Conflict{
				Type:        "multiple_targets",
				Suggestions: highConf,
				Description: "Multiple high-confidence equivalences detected for the same source",
			})
		}
	}

	return conflicts
}

// Conflict represents a detected conflict between equivalence suggestions
type Conflict struct {
	Type        string       `json:"type"`
	Suggestions []Suggestion `json:"suggestions"`
	Description string       `json:"description"`
}
