package journey

import (
	"math"
	"time"
)

// Scorer provides scoring and ranking functionality for journeys
type Scorer interface {
	ScoreJourney(journey *DerivedJourney) *ScoringMetrics
	RankJourneys(journeys []*DerivedJourney) []*DerivedJourney
	CompareJourneys(j1, j2 *DerivedJourney) int
}

// scorer implements Scorer
type scorer struct {
	frequencyWeight    float64
	importanceWeight   float64
	completenessWeight float64
	uniquenessWeight   float64
	recencyWeight      float64
}

const (
	defaultFrequencyWeight    = 0.25
	defaultImportanceWeight   = 0.25
	defaultCompletenessWeight = 0.20
	defaultUniquenessWeight   = 0.15
	defaultRecencyWeight      = 0.15

	frequencyBaseScore   = 0.2
	frequencyScoreSpan   = 0.8
	frequencyLogBase     = 100.0
	importanceBaseScore  = 0.5
	importanceMax        = 1.0
	importanceMaxLength  = 0.3
	importancePathFactor = 10.0

	callChainBonus = 0.2
	dataPathBonus  = 0.15
	userFlowBonus  = 0.1
	testTraceBonus = 0.05

	maxCompletenessSteps  = 10.0
	completenessLinkBase  = 0.7
	completenessLinkBonus = 0.3

	uniquenessBaseScore      = 0.5
	uniquenessMaxFactor      = 0.3
	uniquenessVariationBase  = 10.0
	uniquenessLengthBase     = 20.0
	uniquenessCallChainBonus = 0.05

	recencyNeutralScore = 0.5
	recencyWindowHours  = 336.0
	recencyMinScore     = 0.1

	scoreMin              = 0.0
	scoreMax              = 1.0
	userFactorDivisor     = 100.0
	userFactorMax         = 0.2
	dataPathMultiplier    = 1.1
	callChainDepthDivisor = 20.0
	callChainDepthMax     = 0.3
	testTraceMultiplier   = 0.9
	medianEvenDivisor     = 2.0
)

// NewScorer creates a new journey scorer
func NewScorer() Scorer {
	return &scorer{
		frequencyWeight:    defaultFrequencyWeight,
		importanceWeight:   defaultImportanceWeight,
		completenessWeight: defaultCompletenessWeight,
		uniquenessWeight:   defaultUniquenessWeight,
		recencyWeight:      defaultRecencyWeight,
	}
}

// ScoreJourney calculates a comprehensive score for a journey
func (s *scorer) ScoreJourney(journey *DerivedJourney) *ScoringMetrics {
	metrics := &ScoringMetrics{}

	// Calculate individual component scores
	metrics.FrequencyScore = s.scoreFrequency(journey)
	metrics.ImportanceScore = s.scoreImportance(journey)
	metrics.CompletenessScore = s.scoreCompleteness(journey)
	metrics.UniquenessScore = s.scoreUniqueness(journey)
	metrics.RecencyScore = s.scoreRecency(journey)

	// Calculate weighted total score
	metrics.TotalScore = (metrics.FrequencyScore * s.frequencyWeight) +
		(metrics.ImportanceScore * s.importanceWeight) +
		(metrics.CompletenessScore * s.completenessWeight) +
		(metrics.UniquenessScore * s.uniquenessWeight) +
		(metrics.RecencyScore * s.recencyWeight)

	// Normalize to 0-1 range
	if metrics.TotalScore > scoreMax {
		metrics.TotalScore = scoreMax
	}

	return metrics
}

// scoreFrequency scores based on how often a journey occurs
func (s *scorer) scoreFrequency(journey *DerivedJourney) float64 {
	frequency := float64(journey.Metadata.Frequency)

	// Logarithmic scale: frequent journeys score higher
	// frequency=1 -> 0.2, frequency=10 -> 0.7, frequency=100 -> 1.0
	if frequency <= 0 {
		return scoreMin
	}

	logFreq := math.Log10(frequency+1) / math.Log10(frequencyLogBase)
	if logFreq > scoreMax {
		logFreq = scoreMax
	}

	return frequencyBaseScore + (logFreq * frequencyScoreSpan)
}

// scoreImportance scores based on how important the journey is
func (s *scorer) scoreImportance(journey *DerivedJourney) float64 {
	// Use explicit importance if available
	if journey.Metadata.Importance > 0 {
		return journey.Metadata.Importance
	}

	// Calculate based on journey characteristics
	importance := importanceBaseScore

	// Journey type impacts importance
	switch journey.Type {
	case CallChain:
		// Call chains are important for execution flow
		importance += callChainBonus
	case DataPath:
		// Data paths are important for system integration
		importance += dataPathBonus
	case UserFlow:
		// User flows are important for UX
		importance += userFlowBonus
	case TestTrace:
		// Test traces are important for quality
		importance += testTraceBonus
	}

	// Longer journeys tend to be more important
	pathLengthFactor := float64(len(journey.NodeIDs)) / importancePathFactor
	if pathLengthFactor > importanceMaxLength {
		pathLengthFactor = importanceMaxLength
	}
	importance += pathLengthFactor

	if importance > importanceMax {
		importance = importanceMax
	}

	return importance
}

// scoreCompleteness scores based on journey completeness
func (s *scorer) scoreCompleteness(journey *DerivedJourney) float64 {
	// Use explicit completeness if available
	if journey.Metadata.Completeness > 0 {
		return journey.Metadata.Completeness
	}

	// Calculate based on path coverage
	// Assuming max 10 steps as reference
	completeness := float64(len(journey.NodeIDs)) / maxCompletenessSteps

	if completeness > importanceMax {
		completeness = importanceMax
	}

	// Bonus for well-connected journeys
	linkDensity := float64(len(journey.Links)) / float64(len(journey.NodeIDs)-1)
	if linkDensity > importanceMax {
		linkDensity = importanceMax
	}

	completeness = (completeness * completenessLinkBase) + (linkDensity * completenessLinkBonus)

	return completeness
}

// scoreUniqueness scores based on how unique or distinctive the journey is
func (s *scorer) scoreUniqueness(journey *DerivedJourney) float64 {
	uniqueness := uniquenessBaseScore

	// Journeys with specific characteristics are more unique
	if journey.Metadata.Variations > 1 {
		// More variations suggests the journey is flexible
		variationFactor := float64(journey.Metadata.Variations) / uniquenessVariationBase
		if variationFactor > uniquenessMaxFactor {
			variationFactor = uniquenessMaxFactor
		}
		uniqueness += variationFactor
	}

	// Longer journeys are naturally less common
	lengthFactor := float64(len(journey.NodeIDs)) / uniquenessLengthBase
	if lengthFactor > uniquenessMaxFactor {
		lengthFactor = uniquenessMaxFactor
	}
	uniqueness += lengthFactor

	// Journey type contributes to uniqueness
	if journey.Type == CallChain {
		uniqueness += uniquenessCallChainBonus
	}

	if uniqueness > importanceMax {
		uniqueness = importanceMax
	}

	return uniqueness
}

// scoreRecency scores based on how recently the journey was detected
func (s *scorer) scoreRecency(journey *DerivedJourney) float64 {
	if journey.Metadata.LastDetected.IsZero() {
		return recencyNeutralScore // Neutral score if unknown
	}

	// Calculate time since last detection
	timeSince := time.Since(journey.Metadata.LastDetected)
	hoursSince := timeSince.Hours()

	// Journeys detected recently score higher
	// 0 hours -> 1.0, 24 hours -> 0.8, 168 hours (1 week) -> 0.5
	recency := scoreMax - (hoursSince / recencyWindowHours) // 336 hours = 2 weeks

	if recency < recencyMinScore {
		recency = recencyMinScore
	}

	return recency
}

// RankJourneys sorts journeys by score (highest first)
func (s *scorer) RankJourneys(journeys []*DerivedJourney) []*DerivedJourney {
	// Score all journeys
	for _, journey := range journeys {
		metrics := s.ScoreJourney(journey)
		journey.Score = metrics.TotalScore
	}

	// Sort in descending order by score
	for i := 0; i < len(journeys); i++ {
		for j := i + 1; j < len(journeys); j++ {
			if journeys[j].Score > journeys[i].Score {
				journeys[i], journeys[j] = journeys[j], journeys[i]
			}
		}
	}

	return journeys
}

// CompareJourneys compares two journeys for ranking
// Returns: -1 if j1 < j2, 0 if j1 == j2, 1 if j1 > j2
func (s *scorer) CompareJourneys(j1, j2 *DerivedJourney) int {
	// Compare by score
	if j1.Score > j2.Score {
		return 1
	}
	if j1.Score < j2.Score {
		return -1
	}

	// If scores are equal, compare by frequency
	if j1.Metadata.Frequency > j2.Metadata.Frequency {
		return 1
	}
	if j1.Metadata.Frequency < j2.Metadata.Frequency {
		return -1
	}

	// If frequencies are equal, compare by path length
	if len(j1.NodeIDs) > len(j2.NodeIDs) {
		return 1
	}
	if len(j1.NodeIDs) < len(j2.NodeIDs) {
		return -1
	}

	// If all else is equal
	return 0
}

// ScoreJourneyByType returns a type-specific score
func (s *scorer) ScoreJourneyByType(journey *DerivedJourney) float64 {
	baseScore := s.ScoreJourney(journey).TotalScore

	// Apply type-specific modifiers
	switch journey.Type {
	case UserFlow:
		// User flows: emphasize frequency and user count
		userFactor := float64(journey.Metadata.UserCount) / userFactorDivisor
		if userFactor > userFactorMax {
			userFactor = userFactorMax
		}
		return baseScore * (scoreMax + userFactor)

	case DataPath:
		// Data paths: emphasize importance and completeness
		return baseScore * dataPathMultiplier

	case CallChain:
		// Call chains: emphasize complexity and depth
		depthFactor := float64(len(journey.NodeIDs)) / callChainDepthDivisor
		if depthFactor > callChainDepthMax {
			depthFactor = callChainDepthMax
		}
		return baseScore * (scoreMax + depthFactor)

	case TestTrace:
		// Test traces: emphasize coverage
		return baseScore * testTraceMultiplier

	default:
		return baseScore
	}
}

// CalculateSimilarityScore calculates how similar two journeys are
func (s *scorer) CalculateSimilarityScore(j1, j2 *DerivedJourney) float64 {
	if j1.Type != j2.Type {
		return scoreMin // Different types are not similar
	}

	// Calculate Jaccard similarity on node sets
	set1 := make(map[string]bool)
	set2 := make(map[string]bool)

	for _, id := range j1.NodeIDs {
		set1[id] = true
	}
	for _, id := range j2.NodeIDs {
		set2[id] = true
	}

	intersection := 0
	for id := range set1 {
		if set2[id] {
			intersection++
		}
	}

	union := len(set1) + len(set2) - intersection
	if union == 0 {
		return scoreMin
	}

	return float64(intersection) / float64(union)
}

// FilterJourneysByScore returns only journeys with score >= threshold
func (s *scorer) FilterJourneysByScore(journeys []*DerivedJourney, threshold float64) []*DerivedJourney {
	var filtered []*DerivedJourney
	for _, j := range journeys {
		if j.Score >= threshold {
			filtered = append(filtered, j)
		}
	}
	return filtered
}

// GetTopJourneys returns the N highest-scoring journeys
func (s *scorer) GetTopJourneys(journeys []*DerivedJourney, n int) []*DerivedJourney {
	ranked := s.RankJourneys(journeys)
	if n >= len(ranked) {
		return ranked
	}
	return ranked[:n]
}

// CalculateScoreDistribution analyzes the distribution of scores
func (s *scorer) CalculateScoreDistribution(journeys []*DerivedJourney) map[string]interface{} {
	if len(journeys) == 0 {
		return map[string]interface{}{
			"count":   0,
			"average": scoreMin,
			"min":     scoreMin,
			"max":     scoreMin,
			"median":  scoreMin,
		}
	}

	var scores []float64
	for _, j := range journeys {
		scores = append(scores, j.Score)
	}

	// Sort scores for median calculation
	for i := 0; i < len(scores); i++ {
		for j := i + 1; j < len(scores); j++ {
			if scores[j] < scores[i] {
				scores[i], scores[j] = scores[j], scores[i]
			}
		}
	}

	// Calculate statistics
	sum := scoreMin
	for _, score := range scores {
		sum += score
	}
	average := sum / float64(len(scores))

	var median float64
	if len(scores)%2 == 0 {
		median = (scores[len(scores)/2-1] + scores[len(scores)/2]) / medianEvenDivisor
	} else {
		median = scores[len(scores)/2]
	}

	return map[string]interface{}{
		"count":   len(scores),
		"average": average,
		"min":     scores[0],
		"max":     scores[len(scores)-1],
		"median":  median,
	}
}
