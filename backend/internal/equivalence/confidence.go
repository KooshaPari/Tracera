package equivalence

import (
	"fmt"
	"math"
	"sort"
	"strings"
)

const (
	strategyWeightExplicit  = 1.0
	strategyWeightHigh      = 0.9
	strategyWeightMedium    = 0.7
	strategyWeightLow       = 0.6
	strategyWeightFallback  = 0.5
	agreementBoostPerSignal = 0.05
	agreementBoostMax       = 0.15
	minConfidenceThreshold  = 0.3
	maxConfidenceCap        = 0.99
	highConfidenceThreshold = 0.7
	autoConfirmThreshold    = 0.95
	highConfidenceMinCount  = 2
)

// ConfidenceScore represents a scored equivalence with supporting evidence
type ConfidenceScore struct {
	// Base scores
	Score     float64 // 0-1, final combined confidence
	RawScores map[StrategyType]float64
	BaseScore float64
	Boosts    []ScoreBoost

	// Agreement metrics
	AgreementCount int
	MaxRawScore    float64
	MinRawScore    float64

	// Evidence
	Evidence []Evidence
}

// ScoreBoost represents a confidence boost from a factor
type ScoreBoost struct {
	Factor  string // "agreement", "certainty", "recency"
	Amount  float64
	Reason  string
	Applied bool
}

// ConfidenceScorer computes final confidence from multiple strategies
type ConfidenceScorer struct {
	// Strategy weights - base confidence multipliers
	strategyWeights map[StrategyType]float64

	// Boost parameters
	agreementBoostPerSignal float64 // Per additional agreeing strategy
	maxAgreementBoost       float64 // Cap on agreement boost

	// Modulation factors
	minConfidenceThreshold float64 // Reject if below
	maxConfidence          float64 // Cap final score
}

// NewConfidenceScorer creates a new confidence scorer with defaults
func NewConfidenceScorer() *ConfidenceScorer {
	return &ConfidenceScorer{
		strategyWeights: map[StrategyType]float64{
			StrategyExplicitAnnotation: strategyWeightExplicit,
			StrategyManualLink:         strategyWeightExplicit,
			StrategyAPIContract:        strategyWeightHigh,
			StrategySharedCanonical:    strategyWeightHigh,
			StrategyNamingPattern:      strategyWeightMedium,
			StrategySemanticSimilarity: strategyWeightLow,
			StrategyStructural:         strategyWeightFallback,
		},
		agreementBoostPerSignal: agreementBoostPerSignal, // 5% boost per additional agreeing strategy
		maxAgreementBoost:       agreementBoostMax,       // Max 15% total boost from agreement
		minConfidenceThreshold:  minConfidenceThreshold,  // Reject matches below 30%
		maxConfidence:           maxConfidenceCap,        // Cap at 99% for non-explicit matches
	}
}

// ComputeConfidence calculates a final confidence score from evidence
func (cs *ConfidenceScorer) ComputeConfidence(evidence []Evidence) *ConfidenceScore {
	result := &ConfidenceScore{
		RawScores:   make(map[StrategyType]float64),
		Boosts:      make([]ScoreBoost, 0),
		Evidence:    evidence,
		MaxRawScore: 0.0,
		MinRawScore: 1.0,
	}

	if len(evidence) == 0 {
		result.Score = 0.0
		return result
	}

	// Collect raw scores by strategy
	strategyScores := make(map[StrategyType][]float64)
	for _, ev := range evidence {
		strategyScores[ev.Strategy] = append(strategyScores[ev.Strategy], ev.Confidence)
		result.RawScores[ev.Strategy] = ev.Confidence
		result.MaxRawScore = math.Max(result.MaxRawScore, ev.Confidence)
		result.MinRawScore = math.Min(result.MinRawScore, ev.Confidence)
	}

	// If any strategy has 1.0 confidence (explicit), return 1.0
	if result.MaxRawScore >= explicitConfidenceThreshold {
		result.Score = explicitConfidenceThreshold
		result.BaseScore = explicitConfidenceThreshold
		return result
	}

	// Calculate base score: weighted average of strategy scores
	baseScore := cs.computeWeightedAverage(strategyScores)
	result.BaseScore = baseScore
	result.AgreementCount = len(strategyScores)

	// Apply boosts
	finalScore := baseScore
	finalScore += cs.applyAgreementBoost(len(strategyScores), &result.Boosts)

	// Cap at maximum
	if finalScore > cs.maxConfidence {
		finalScore = cs.maxConfidence
		result.Boosts = append(result.Boosts, ScoreBoost{
			Factor:  "max_cap",
			Amount:  cs.maxConfidence - finalScore,
			Reason:  "Non-explicit matches capped at 99%",
			Applied: true,
		})
	}

	result.Score = math.Max(0.0, finalScore)
	return result
}

// computeWeightedAverage calculates weighted average confidence
func (cs *ConfidenceScorer) computeWeightedAverage(strategyScores map[StrategyType][]float64) float64 {
	if len(strategyScores) == 0 {
		return 0.0
	}

	// For each strategy, use the average of its evidence
	var weightedSum, totalWeight float64
	for strategy, scores := range strategyScores {
		weight := cs.strategyWeights[strategy]
		if weight == 0 {
			weight = strategyWeightFallback // Unknown strategy
		}

		// Average the strategy's scores
		avgScore := 0.0
		for _, s := range scores {
			avgScore += s
		}
		avgScore /= float64(len(scores))

		weightedSum += avgScore * weight
		totalWeight += weight
	}

	if totalWeight == 0 {
		return 0.0
	}

	return weightedSum / totalWeight
}

// applyAgreementBoost adds confidence when multiple strategies agree
func (cs *ConfidenceScorer) applyAgreementBoost(numStrategies int, boosts *[]ScoreBoost) float64 {
	if numStrategies <= 1 {
		return 0.0
	}

	// Each additional strategy beyond the first adds boost
	boost := float64(numStrategies-1) * cs.agreementBoostPerSignal
	if boost > cs.maxAgreementBoost {
		boost = cs.maxAgreementBoost
	}

	*boosts = append(*boosts, ScoreBoost{
		Factor:  "agreement",
		Amount:  boost,
		Reason:  "Multiple strategies found the same equivalence",
		Applied: true,
	})

	return boost
}

// ConflictReconciler resolves competing equivalence suggestions.
type ConflictReconciler struct {
	scorer *ConfidenceScorer
}

// NewConflictReconciler creates a new reconciler
func NewConflictReconciler() *ConflictReconciler {
	return &ConflictReconciler{
		scorer: NewConfidenceScorer(),
	}
}

// ResolveConflict picks the best match among competing suggestions
func (cr *ConflictReconciler) ResolveConflict(suggestions []Suggestion) *Suggestion {
	if len(suggestions) == 0 {
		return nil
	}
	if len(suggestions) == 1 {
		return &suggestions[0]
	}

	// Sort by confidence descending
	sort.Slice(suggestions, func(i, j int) bool {
		if suggestions[i].Confidence != suggestions[j].Confidence {
			return suggestions[i].Confidence > suggestions[j].Confidence
		}
		// Tiebreaker: more strategies is better
		return len(suggestions[i].Strategies) > len(suggestions[j].Strategies)
	})

	return &suggestions[0]
}

// IsConflict checks if suggestions represent a genuine conflict
func (cr *ConflictReconciler) IsConflict(suggestions []Suggestion) bool {
	if len(suggestions) <= 1 {
		return false
	}

	// Conflict if we have 2+ high-confidence (>0.7) suggestions for the same source
	highConfCount := 0
	for _, s := range suggestions {
		if s.Confidence >= highConfidenceThreshold {
			highConfCount++
		}
	}

	return highConfCount >= highConfidenceMinCount
}

// ConflictResolution represents how a conflict was resolved
type ConflictResolution struct {
	SourceItemID   string
	Candidates     []Suggestion
	Selected       *Suggestion
	Reason         string
	RequiresReview bool // If true, needs human review
}

// ResolveMultipleMatches picks the best match from candidates
func (cr *ConflictReconciler) ResolveMultipleMatches(suggestions []Suggestion) *ConflictResolution {
	resolution := &ConflictResolution{
		Candidates:     suggestions,
		RequiresReview: cr.IsConflict(suggestions),
	}

	if len(suggestions) == 0 {
		return resolution
	}

	if len(suggestions) > 0 {
		resolution.SourceItemID = suggestions[0].SourceItemID.String()
	}

	// Resolve using confidence + agreement
	selected := cr.ResolveConflict(suggestions)
	resolution.Selected = selected

	switch {
	case resolution.RequiresReview:
		resolution.Reason = "Multiple high-confidence matches detected"
	case len(suggestions) > 1:
		resolution.Reason = "Selected best match by confidence score"
	default:
		resolution.Reason = "Single match selected"
	}

	return resolution
}

// ConfidenceValidator checks if a score is acceptable
type ConfidenceValidator struct {
	minThreshold      float64
	requiresReviewMin float64
	autoConfirmMin    float64
}

// NewConfidenceValidator creates a validator with defaults
func NewConfidenceValidator() *ConfidenceValidator {
	return &ConfidenceValidator{
		minThreshold:      minConfidenceThreshold,  // Minimum acceptable confidence
		requiresReviewMin: highConfidenceThreshold, // Below this, needs review
		autoConfirmMin:    autoConfirmThreshold,    // Above this, auto-confirm
	}
}

// ValidateScore checks if a confidence score is acceptable
func (cv *ConfidenceValidator) ValidateScore(score *ConfidenceScore) *ValidationResult {
	result := &ValidationResult{
		Score: score.Score,
		Valid: score.Score >= cv.minThreshold,
	}

	switch {
	case score.Score >= cv.autoConfirmMin:
		result.Status = "auto_confirm"
		result.Reason = "Very high confidence - can be auto-confirmed"
	case score.Score >= cv.requiresReviewMin:
		result.Status = "review_suggested"
		result.Reason = "Good confidence but suggests user review"
	case score.Score >= cv.minThreshold:
		result.Status = "review_required"
		result.Reason = "Moderate confidence - requires user review"
	default:
		result.Status = "insufficient"
		result.Reason = "Below minimum confidence threshold"
		result.Valid = false
	}

	return result
}

// ValidationResult represents the validation outcome
type ValidationResult struct {
	Score  float64 // 0-1
	Valid  bool
	Status string // auto_confirm, review_suggested, review_required, insufficient
	Reason string
}

// Explanation provides details on how confidence was computed.
func (cs *ConfidenceScore) Explanation() string {
	var explanationBuilder strings.Builder

	// Show each strategy's contribution
	if len(cs.RawScores) > 0 {
		explanationBuilder.WriteString("Strategy scores: ")
		for strategy, score := range cs.RawScores {
			explanationBuilder.WriteString(string(strategy))
			explanationBuilder.WriteByte('=')
			explanationBuilder.WriteString(formatScore(score))
			explanationBuilder.WriteByte(' ')
		}
		explanationBuilder.WriteByte('\n')
	}

	// Show boosts applied
	if len(cs.Boosts) > 0 {
		explanationBuilder.WriteString("Boosts: ")
		for _, boost := range cs.Boosts {
			if boost.Applied {
				explanationBuilder.WriteString(boost.Factor)
				explanationBuilder.WriteString("(+")
				explanationBuilder.WriteString(formatScore(boost.Amount))
				explanationBuilder.WriteString(") ")
			}
		}
		explanationBuilder.WriteByte('\n')
	}

	explanationBuilder.WriteString("Final: ")
	explanationBuilder.WriteString(formatScore(cs.Score))

	return explanationBuilder.String()
}

func formatScore(score float64) string {
	return fmt.Sprintf("%.2f", score)
}
