package equivalence

import (
	"math"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

// TestNewConfidenceScorer creates a scorer with default weights
func TestNewConfidenceScorer(t *testing.T) {
	// Act
	scorer := NewConfidenceScorer()

	// Assert
	assert.NotNil(t, scorer)
	assert.Len(t, scorer.strategyWeights, 7)
	assert.InEpsilon(t, 0.05, scorer.agreementBoostPerSignal, 1e-9)
	assert.InEpsilon(t, 0.15, scorer.maxAgreementBoost, 1e-9)
	assert.InEpsilon(t, 0.3, scorer.minConfidenceThreshold, 1e-9)
	assert.InEpsilon(t, 0.99, scorer.maxConfidence, 1e-9)
}

// TestComputeConfidenceEmptyEvidence returns 0 for empty evidence
func TestComputeConfidenceEmptyEvidence(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()

	// Act
	result := scorer.ComputeConfidence([]Evidence{})

	// Assert
	assert.InDelta(t, 0.0, result.Score, 1e-9)
	assert.Empty(t, result.RawScores)
}

// TestComputeConfidenceSingleStrategy scores single strategy correctly
func TestComputeConfidenceSingleStrategy(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()
	evidence := []Evidence{
		{
			Strategy:   StrategyNamingPattern,
			Confidence: 0.7,
		},
	}

	// Act
	result := scorer.ComputeConfidence(evidence)

	// Assert
	assert.InEpsilon(t, 0.7, result.BaseScore, 1e-9)
	assert.InEpsilon(t, 0.7, result.Score, 1e-9)
	assert.Equal(t, 1, result.AgreementCount)
}

// TestComputeConfidenceExplicitAnnotation returns 1.0 for explicit matches
func TestComputeConfidenceExplicitAnnotation(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()
	evidence := []Evidence{
		{
			Strategy:   StrategyExplicitAnnotation,
			Confidence: 1.0,
		},
	}

	// Act
	result := scorer.ComputeConfidence(evidence)

	// Assert
	assert.InEpsilon(t, 1.0, result.Score, 1e-9)
	assert.InEpsilon(t, 1.0, result.BaseScore, 1e-9)
}

// TestComputeConfidenceMultipleStrategies boosts score with multiple agreeing strategies
func TestComputeConfidenceMultipleStrategies(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()
	evidence := []Evidence{
		{
			Strategy:   StrategyNamingPattern,
			Confidence: 0.7,
		},
		{
			Strategy:   StrategySemanticSimilarity,
			Confidence: 0.6,
		},
		{
			Strategy:   StrategyAPIContract,
			Confidence: 0.9,
		},
	}

	// Act
	result := scorer.ComputeConfidence(evidence)

	// Assert
	assert.Equal(t, 3, result.AgreementCount)
	// Score should be boosted by agreement
	assert.Greater(t, result.Score, result.BaseScore)
	// Should have agreement boost
	assert.NotEmpty(t, result.Boosts)
}

// TestComputeConfidenceWeightedAverage respects strategy weights
func TestComputeConfidenceWeightedAverage(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()

	// High weight strategy with medium confidence
	evidence1 := []Evidence{
		{
			Strategy:   StrategyExplicitAnnotation, // Weight 1.0
			Confidence: 0.8,
		},
		{
			Strategy:   StrategySemanticSimilarity, // Weight 0.6
			Confidence: 0.2,
		},
	}

	// Act
	result1 := scorer.ComputeConfidence(evidence1)

	// Reverse weights with same confidence values
	evidence2 := []Evidence{
		{
			Strategy:   StrategySemanticSimilarity, // Weight 0.6
			Confidence: 0.8,
		},
		{
			Strategy:   StrategyStructural, // Weight 0.5
			Confidence: 0.2,
		},
	}

	result2 := scorer.ComputeConfidence(evidence2)

	// Assert
	// Different strategy weights should produce different base scores
	assert.NotEqual(t, result1.BaseScore, result2.BaseScore)
	// Result1 should be higher due to higher weight on first evidence
	assert.Greater(t, result1.BaseScore, result2.BaseScore)
}

// TestComputeConfidenceAgreementBoost applies boost for multiple strategies
func TestComputeConfidenceAgreementBoost(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()

	singleEvidence := []Evidence{
		{
			Strategy:   StrategyNamingPattern,
			Confidence: 0.7,
		},
	}

	multipleEvidence := []Evidence{
		{
			Strategy:   StrategyNamingPattern,
			Confidence: 0.7,
		},
		{
			Strategy:   StrategySemanticSimilarity,
			Confidence: 0.7,
		},
	}

	// Act
	singleResult := scorer.ComputeConfidence(singleEvidence)
	multipleResult := scorer.ComputeConfidence(multipleEvidence)

	// Assert
	// Multiple strategies should have higher score due to agreement boost
	assert.Greater(t, multipleResult.Score, singleResult.Score)
	// Should have at least one boost applied
	assert.NotEmpty(t, multipleResult.Boosts)
}

// TestComputeConfidenceMaxAgreementBoostCap caps agreement boost
func TestComputeConfidenceMaxAgreementBoostCap(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()

	// Create evidence with many strategies
	evidence := []Evidence{
		{Strategy: StrategyExplicitAnnotation, Confidence: 0.8},
		{Strategy: StrategyAPIContract, Confidence: 0.8},
		{Strategy: StrategyNamingPattern, Confidence: 0.8},
		{Strategy: StrategySemanticSimilarity, Confidence: 0.8},
		{Strategy: StrategyStructural, Confidence: 0.8},
		{Strategy: StrategyManualLink, Confidence: 0.8},
		{Strategy: StrategySharedCanonical, Confidence: 0.8},
	}

	// Act
	result := scorer.ComputeConfidence(evidence)

	// Assert
	// Should not exceed maxConfidence
	assert.LessOrEqual(t, result.Score, scorer.maxConfidence)
	// Should have applied agreement boost (capped at maxAgreementBoost)
	hasAgreementBoost := false
	for _, boost := range result.Boosts {
		if boost.Factor == "agreement" {
			hasAgreementBoost = true
			// With 7 strategies, boost would be 6 * 0.05 = 0.30, but capped at 0.15
			assert.LessOrEqual(t, boost.Amount, scorer.maxAgreementBoost)
		}
	}
	assert.True(t, hasAgreementBoost)
}

// TestComputeConfidenceMaxConfidenceCap caps final score at 0.99
func TestComputeConfidenceMaxConfidenceCap(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()
	evidence := []Evidence{
		{Strategy: StrategyAPIContract, Confidence: 0.99},
		{Strategy: StrategyNamingPattern, Confidence: 0.99},
		{Strategy: StrategySemanticSimilarity, Confidence: 0.99},
	}

	// Act
	result := scorer.ComputeConfidence(evidence)

	// Assert
	assert.LessOrEqual(t, result.Score, 0.99)
}

// TestComputeConfidenceMinimumScore does not go below zero
func TestComputeConfidenceMinimumScore(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()
	evidence := []Evidence{
		{Strategy: StrategyStructural, Confidence: 0.01},
	}

	// Act
	result := scorer.ComputeConfidence(evidence)

	// Assert
	assert.GreaterOrEqual(t, result.Score, 0.0)
}

// TestNewConflictReconciler creates reconciler with scorer
func TestNewConflictReconciler(t *testing.T) {
	// Act
	reconciler := NewConflictReconciler()

	// Assert
	assert.NotNil(t, reconciler)
	assert.NotNil(t, reconciler.scorer)
}

// TestResolveConflictSingleSuggestion returns the suggestion
func TestResolveConflictSingleSuggestion(t *testing.T) {
	// Arrange
	reconciler := NewConflictReconciler()
	suggestions := []Suggestion{
		{
			SourceItemID: uuid.New(),
			TargetItemID: uuid.New(),
			Confidence:   0.8,
			Strategies:   []StrategyType{StrategyNamingPattern},
		},
	}

	// Act
	result := reconciler.ResolveConflict(suggestions)

	// Assert
	assert.NotNil(t, result)
	assert.Equal(t, suggestions[0].TargetItemID, result.TargetItemID)
}

// TestResolveConflictEmptySuggestions returns nil
func TestResolveConflictEmptySuggestions(t *testing.T) {
	// Arrange
	reconciler := NewConflictReconciler()

	// Act
	result := reconciler.ResolveConflict([]Suggestion{})

	// Assert
	assert.Nil(t, result)
}

// TestResolveConflictSelectsHighestConfidence picks highest confidence
func TestResolveConflictSelectsHighestConfidence(t *testing.T) {
	// Arrange
	reconciler := NewConflictReconciler()
	id1 := uuid.New()
	id2 := uuid.New()
	id3 := uuid.New()

	suggestions := []Suggestion{
		{
			SourceItemID: uuid.New(),
			TargetItemID: id1,
			Confidence:   0.7,
			Strategies:   []StrategyType{StrategyNamingPattern},
		},
		{
			SourceItemID: uuid.New(),
			TargetItemID: id2,
			Confidence:   0.9,
			Strategies:   []StrategyType{StrategyAPIContract},
		},
		{
			SourceItemID: uuid.New(),
			TargetItemID: id3,
			Confidence:   0.8,
			Strategies:   []StrategyType{StrategySemanticSimilarity},
		},
	}

	// Act
	result := reconciler.ResolveConflict(suggestions)

	// Assert
	assert.Equal(t, id2, result.TargetItemID)
	assert.InEpsilon(t, 0.9, result.Confidence, 1e-9)
}

// TestResolveConflictBreaksTieByStrategyCount uses strategy count as tiebreaker
func TestResolveConflictBreaksTieByStrategyCount(t *testing.T) {
	// Arrange
	reconciler := NewConflictReconciler()
	id1 := uuid.New()
	id2 := uuid.New()

	suggestions := []Suggestion{
		{
			SourceItemID: uuid.New(),
			TargetItemID: id1,
			Confidence:   0.8,
			Strategies: []StrategyType{
				StrategyNamingPattern,
			},
		},
		{
			SourceItemID: uuid.New(),
			TargetItemID: id2,
			Confidence:   0.8,
			Strategies: []StrategyType{
				StrategyNamingPattern,
				StrategySemanticSimilarity,
				StrategyAPIContract,
			},
		},
	}

	// Act
	result := reconciler.ResolveConflict(suggestions)

	// Assert
	assert.Equal(t, id2, result.TargetItemID) // More strategies wins tiebreak
}

// TestIsConflictDetectsMultipleHighConfidence identifies conflicts
func TestIsConflictDetectsMultipleHighConfidence(t *testing.T) {
	// Arrange
	reconciler := NewConflictReconciler()

	suggestions := []Suggestion{
		{
			SourceItemID: uuid.New(),
			TargetItemID: uuid.New(),
			Confidence:   0.8,
		},
		{
			SourceItemID: uuid.New(),
			TargetItemID: uuid.New(),
			Confidence:   0.85,
		},
	}

	// Act
	isConflict := reconciler.IsConflict(suggestions)

	// Assert
	assert.True(t, isConflict)
}

// TestIsConflictIgnoresLowConfidence ignores low confidence matches
func TestIsConflictIgnoresLowConfidence(t *testing.T) {
	// Arrange
	reconciler := NewConflictReconciler()

	suggestions := []Suggestion{
		{
			SourceItemID: uuid.New(),
			TargetItemID: uuid.New(),
			Confidence:   0.8,
		},
		{
			SourceItemID: uuid.New(),
			TargetItemID: uuid.New(),
			Confidence:   0.4, // Below threshold
		},
	}

	// Act
	isConflict := reconciler.IsConflict(suggestions)

	// Assert
	assert.False(t, isConflict)
}

// TestResolveMultipleMatches picks best and marks if needs review
func TestResolveMultipleMatches(t *testing.T) {
	// Arrange
	reconciler := NewConflictReconciler()
	sourceID := uuid.New()
	id1 := uuid.New()
	id2 := uuid.New()

	suggestions := []Suggestion{
		{
			SourceItemID: sourceID,
			TargetItemID: id1,
			Confidence:   0.9,
		},
		{
			SourceItemID: sourceID,
			TargetItemID: id2,
			Confidence:   0.85,
		},
	}

	// Act
	resolution := reconciler.ResolveMultipleMatches(suggestions)

	// Assert
	assert.NotNil(t, resolution)
	assert.Equal(t, sourceID.String(), resolution.SourceItemID)
	assert.NotNil(t, resolution.Selected)
	assert.Equal(t, id1, resolution.Selected.TargetItemID)
	assert.True(t, resolution.RequiresReview)
}

// TestResolveMultipleMatchesSingleSuggestion marks as single match
func TestResolveMultipleMatchesSingleSuggestion(t *testing.T) {
	// Arrange
	reconciler := NewConflictReconciler()

	suggestions := []Suggestion{
		{
			SourceItemID: uuid.New(),
			TargetItemID: uuid.New(),
			Confidence:   0.8,
		},
	}

	// Act
	resolution := reconciler.ResolveMultipleMatches(suggestions)

	// Assert
	assert.False(t, resolution.RequiresReview)
	assert.Contains(t, resolution.Reason, "Single match")
}

// TestNewConfidenceValidator creates validator with defaults
func TestNewConfidenceValidator(t *testing.T) {
	// Act
	validator := NewConfidenceValidator()

	// Assert
	assert.NotNil(t, validator)
	assert.InEpsilon(t, 0.3, validator.minThreshold, 1e-9)
	assert.InEpsilon(t, 0.7, validator.requiresReviewMin, 1e-9)
	assert.InEpsilon(t, 0.95, validator.autoConfirmMin, 1e-9)
}

// TestValidateScoreBelowMinimum rejects below minimum threshold
func TestValidateScoreBelowMinimum(t *testing.T) {
	// Arrange
	validator := NewConfidenceValidator()
	score := &ConfidenceScore{
		Score: 0.2, // Below 0.3
	}

	// Act
	result := validator.ValidateScore(score)

	// Assert
	assert.False(t, result.Valid)
	assert.Equal(t, "insufficient", result.Status)
}

// TestValidateScoreModerateConfidence requires review
func TestValidateScoreModerateConfidence(t *testing.T) {
	// Arrange
	validator := NewConfidenceValidator()
	score := &ConfidenceScore{
		Score: 0.5, // Between minThreshold and requiresReviewMin
	}

	// Act
	result := validator.ValidateScore(score)

	// Assert
	assert.True(t, result.Valid)
	assert.Equal(t, "review_required", result.Status)
}

// TestValidateScoreGoodConfidence suggests review
func TestValidateScoreGoodConfidence(t *testing.T) {
	// Arrange
	validator := NewConfidenceValidator()
	score := &ConfidenceScore{
		Score: 0.8, // Between requiresReviewMin and autoConfirmMin
	}

	// Act
	result := validator.ValidateScore(score)

	// Assert
	assert.True(t, result.Valid)
	assert.Equal(t, "review_suggested", result.Status)
}

// TestValidateScoreVeryHighConfidence auto-confirms
func TestValidateScoreVeryHighConfidence(t *testing.T) {
	// Arrange
	validator := NewConfidenceValidator()
	score := &ConfidenceScore{
		Score: 0.97, // Above autoConfirmMin
	}

	// Act
	result := validator.ValidateScore(score)

	// Assert
	assert.True(t, result.Valid)
	assert.Equal(t, "auto_confirm", result.Status)
}

// TestScoringExplanation provides human-readable explanation
func TestScoringExplanation(t *testing.T) {
	// Arrange
	score := &ConfidenceScore{
		Score: 0.85,
		RawScores: map[StrategyType]float64{
			StrategyNamingPattern:      0.7,
			StrategySemanticSimilarity: 0.6,
		},
		Boosts: []ScoreBoost{
			{
				Factor:  "agreement",
				Amount:  0.05,
				Applied: true,
			},
		},
	}

	// Act
	explanation := score.Explanation()

	// Assert
	assert.NotEmpty(t, explanation)
	assert.Contains(t, explanation, "Strategy scores")
	assert.Contains(t, explanation, "Boosts")
	assert.Contains(t, explanation, "Final")
}

// TestConfidenceScorerWithUnknownStrategy uses default weight
func TestConfidenceScorerWithUnknownStrategy(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()
	evidence := []Evidence{
		{
			Strategy:   StrategyType("unknown_strategy"),
			Confidence: 0.5,
		},
	}

	// Act
	result := scorer.ComputeConfidence(evidence)

	// Assert
	// Should use default weight of 0.5
	assert.Greater(t, result.Score, 0.0)
	assert.LessOrEqual(t, result.Score, 0.5)
}

// TestConfidenceScorerMultipleEvidenceSameStrategy averages strategy evidence
func TestConfidenceScorerMultipleEvidenceSameStrategy(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()
	evidence := []Evidence{
		{
			Strategy:   StrategyNamingPattern,
			Confidence: 0.8,
		},
		{
			Strategy:   StrategyNamingPattern,
			Confidence: 0.6,
		},
	}

	// Act
	result := scorer.ComputeConfidence(evidence)

	// Assert
	// Should average to 0.7
	assert.Greater(t, result.BaseScore, 0.6)
	assert.Less(t, result.BaseScore, 0.8)
}

// TestConflictDetectionEmptyList returns no conflicts
func TestConflictDetectionEmptyList(t *testing.T) {
	// Arrange
	aggregator := NewConfidenceAggregator()

	// Act
	conflicts := aggregator.DetectConflicts([]Suggestion{})

	// Assert
	assert.Empty(t, conflicts)
}

// TestConflictDetectionSingleSuggestion returns no conflicts
func TestConflictDetectionSingleSuggestion(t *testing.T) {
	// Arrange
	aggregator := NewConfidenceAggregator()
	suggestions := []Suggestion{
		{
			SourceItemID: uuid.New(),
			TargetItemID: uuid.New(),
			Confidence:   0.9,
		},
	}

	// Act
	conflicts := aggregator.DetectConflicts(suggestions)

	// Assert
	assert.Empty(t, conflicts)
}

// TestConflictDetectionMultipleHighConfidence detects conflicts
func TestConflictDetectionMultipleHighConfidence(t *testing.T) {
	// Arrange
	aggregator := NewConfidenceAggregator()
	sourceID := uuid.New()

	suggestions := []Suggestion{
		{
			SourceItemID: sourceID,
			TargetItemID: uuid.New(),
			Confidence:   0.9,
		},
		{
			SourceItemID: sourceID,
			TargetItemID: uuid.New(),
			Confidence:   0.85,
		},
	}

	// Act
	conflicts := aggregator.DetectConflicts(suggestions)

	// Assert
	assert.Len(t, conflicts, 1)
	assert.Equal(t, "multiple_targets", conflicts[0].Type)
	assert.Len(t, conflicts[0].Suggestions, 2)
}

// TestScoreBoostTracking logs all applied boosts
func TestScoreBoostTracking(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()
	evidence := []Evidence{
		{Strategy: StrategyNamingPattern, Confidence: 0.7},
		{Strategy: StrategySemanticSimilarity, Confidence: 0.6},
	}

	// Act
	result := scorer.ComputeConfidence(evidence)

	// Assert
	assert.NotNil(t, result.Boosts)
	for _, boost := range result.Boosts {
		assert.NotEmpty(t, boost.Factor)
		assert.NotEmpty(t, boost.Reason)
		assert.True(t, boost.Applied)
	}
}

// TestAgreementBoostPerSignal calculates correctly
func TestAgreementBoostPerSignal(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()
	evidence := []Evidence{
		{Strategy: StrategyNamingPattern, Confidence: 0.5},
		{Strategy: StrategySemanticSimilarity, Confidence: 0.5},
		{Strategy: StrategyAPIContract, Confidence: 0.5},
	}

	// Act
	result := scorer.ComputeConfidence(evidence)

	// Assert
	// Base average is 0.5, agreement boost is 2 * 0.05 = 0.10
	expectedScore := math.Min(0.5+0.10, scorer.maxConfidence)
	assert.InDelta(t, expectedScore, result.Score, 0.001)
}

// TestConfidenceEdgeCaseNaNHandling handles NaN safely
func TestConfidenceEdgeCaseNaNHandling(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()
	evidence := []Evidence{
		{Strategy: StrategyNamingPattern, Confidence: math.NaN()},
	}

	// Act - should not panic
	result := scorer.ComputeConfidence(evidence)

	// Assert
	assert.NotNil(t, result)
}

// TestConfidenceEdgeCaseInfinityHandling handles infinity safely
func TestConfidenceEdgeCaseInfinityHandling(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()
	evidence := []Evidence{
		{Strategy: StrategyNamingPattern, Confidence: math.Inf(1)},
	}

	// Act - should not panic
	result := scorer.ComputeConfidence(evidence)

	// Assert
	assert.NotNil(t, result)
	// Infinity >= 1.0 triggers early return with score = 1.0 (explicit match path)
	assert.InEpsilon(t, 1.0, result.Score, 1e-9)
}

// TestNewConfidenceScorerStrategyWeights validates initial weights
func TestNewConfidenceScorerStrategyWeights(t *testing.T) {
	// Arrange
	scorer := NewConfidenceScorer()

	// Assert - verify all strategy weights are present
	expectedStrategies := []StrategyType{
		StrategyExplicitAnnotation,
		StrategyManualLink,
		StrategyAPIContract,
		StrategySharedCanonical,
		StrategyNamingPattern,
		StrategySemanticSimilarity,
		StrategyStructural,
	}

	for _, s := range expectedStrategies {
		assert.Greater(t, scorer.strategyWeights[s], 0.0)
	}
}
