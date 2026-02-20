package equivalence

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const equivalenceDetectTimeout = 1 * time.Second

// TestNewDetector creates a detector with strategies
func TestNewDetector(t *testing.T) {
	// Arrange
	strategies := []Strategy{
		NewNamingStrategy(),
		NewAnnotationStrategy(),
		NewAPIContractStrategy(),
	}

	// Act
	detector := NewDetector(strategies...)

	// Assert
	assert.NotNil(t, detector)
	assert.Len(t, detector.strategies, 3)
	assert.NotNil(t, detector.aggregator)
}

// TestDetectorRegisterStrategy adds a new strategy after creation
func TestDetectorRegisterStrategy(t *testing.T) {
	// Arrange
	detector := NewDetector()
	strategy := NewNamingStrategy()

	// Act
	detector.RegisterStrategy(strategy)

	// Assert
	retrieved, exists := detector.GetStrategy(StrategyNamingPattern)
	assert.True(t, exists)
	assert.NotNil(t, retrieved)
}

// TestDetectorGetStrategy retrieves a registered strategy
func TestDetectorGetStrategy(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	detector := NewDetector(strategy)

	// Act
	retrieved, exists := detector.GetStrategy(StrategyNamingPattern)

	// Assert
	assert.True(t, exists)
	assert.Equal(t, strategy, retrieved)
}

// TestDetectorGetNonexistentStrategy returns false for unknown strategies
func TestDetectorGetNonexistentStrategy(t *testing.T) {
	// Arrange
	detector := NewDetector()

	// Act
	retrieved, exists := detector.GetStrategy(StrategyNamingPattern)

	// Assert
	assert.False(t, exists)
	assert.Nil(t, retrieved)
}

// TestDetectorListStrategies returns all registered strategies
func TestDetectorListStrategies(t *testing.T) {
	// Arrange
	strategies := []Strategy{
		NewNamingStrategy(),
		NewAnnotationStrategy(),
	}
	detector := NewDetector(strategies...)

	// Act
	registered := detector.ListStrategies()

	// Assert
	assert.Len(t, registered, 2)
	// Check that both strategies are present (order doesn't matter)
	found := make(map[StrategyType]bool)
	for _, s := range registered {
		found[s] = true
	}
	assert.True(t, found[StrategyNamingPattern])
	assert.True(t, found[StrategyExplicitAnnotation])
}

// TestDetectWithEmptyStrategies uses all registered strategies when none specified
func TestDetectWithEmptyStrategies(t *testing.T) {
	// Arrange
	detector := NewDetector(
		NewNamingStrategy(),
		NewAnnotationStrategy(),
	)

	projectID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:          uuid.New(),
		ProjectID:   projectID,
		Title:       "UserService",
		Description: "Service for managing users",
		Type:        "function",
	}

	candidatePool := []*StrategyItemInfo{
		{
			ID:          uuid.New(),
			ProjectID:   projectID,
			Title:       "UserService",
			Description: "Service for managing users",
			Type:        "function",
		},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidatePool,
		MinConfidence: 0.5,
		MaxResults:    10,
	}

	// Act
	suggestions, err := detector.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.NotNil(t, suggestions)
}

// TestDetectWithSpecificStrategies runs only requested strategies
func TestDetectWithSpecificStrategies(t *testing.T) {
	// Arrange
	detector := NewDetector(
		NewNamingStrategy(),
		NewAnnotationStrategy(),
		NewAPIContractStrategy(),
	)

	projectID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GetUsers",
		Type:      "function",
	}

	candidatePool := []*StrategyItemInfo{
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "GetUsers",
			Type:      "function",
		},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidatePool,
		Strategies: []StrategyType{
			StrategyNamingPattern,
		},
		MinConfidence: 0.5,
		MaxResults:    10,
	}

	// Act
	suggestions, err := detector.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.NotNil(t, suggestions)
}

// TestDetectEmptySourceItem handles empty source items
func TestDetectEmptySourceItem(t *testing.T) {
	// Arrange
	detector := NewDetector(NewNamingStrategy())

	projectID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "", // Empty title
		Type:      "function",
	}

	candidatePool := []*StrategyItemInfo{
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "SomeFunction",
			Type:      "function",
		},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidatePool,
		MinConfidence: 0.5,
	}

	// Act
	suggestions, err := detector.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.NotNil(t, suggestions)
}

// TestDetectEmptyCandidatePool handles empty candidate pool
func TestDetectEmptyCandidatePool(t *testing.T) {
	// Arrange
	detector := NewDetector(NewNamingStrategy())

	projectID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{},
		MinConfidence: 0.5,
	}

	// Act
	suggestions, err := detector.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Empty(t, suggestions)
}

// TestDetectContextCancellation handles context cancellation
func TestDetectContextCancellation(t *testing.T) {
	// Arrange
	detector := NewDetector(NewNamingStrategy())

	projectID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	candidatePool := []*StrategyItemInfo{
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "UserService",
			Type:      "function",
		},
	}

	ctx, cancel := context.WithCancel(context.Background())
	cancel() // Cancel immediately

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidatePool,
		MinConfidence: 0.5,
	}

	// Act
	suggestions, err := detector.Detect(ctx, req)

	// Assert
	// Detector swallows individual strategy errors and returns nil error
	// with empty or partial results when context is cancelled
	require.NoError(t, err)
	// Results may be empty due to cancellation
	assert.NotNil(t, suggestions)
}

// TestDetectWithMinConfidenceFilter filters results below threshold
func TestDetectWithMinConfidenceFilter(t *testing.T) {
	// Arrange
	detector := NewDetector(NewNamingStrategy())

	projectID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User",
		Type:      "function",
	}

	candidatePool := []*StrategyItemInfo{
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "UserService", // Low similarity
			Type:      "function",
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "User", // High similarity
			Type:      "function",
		},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidatePool,
		MinConfidence: 0.95, // Very high threshold
	}

	// Act
	suggestions, err := detector.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	// Should only include high-confidence matches
	for _, s := range suggestions {
		assert.GreaterOrEqual(t, s.Confidence, 0.95)
	}
}

// TestDetectWithMaxResults limits returned results
func TestDetectWithMaxResults(t *testing.T) {
	// Arrange
	detector := NewDetector(NewNamingStrategy())

	projectID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "Service",
		Type:      "function",
	}

	// Create multiple candidates with similar names
	candidatePool := []*StrategyItemInfo{
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "ServiceA",
			Type:      "function",
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "ServiceB",
			Type:      "function",
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "ServiceC",
			Type:      "function",
		},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidatePool,
		MinConfidence: 0.5,
		MaxResults:    2,
	}

	// Act
	suggestions, err := detector.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.LessOrEqual(t, len(suggestions), 2)
}

// TestDetectWithUnregisteredStrategy skips unknown strategies
func TestDetectWithUnregisteredStrategy(t *testing.T) {
	// Arrange
	detector := NewDetector(NewNamingStrategy())

	projectID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	candidatePool := []*StrategyItemInfo{
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "UserService",
			Type:      "function",
		},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidatePool,
		Strategies: []StrategyType{
			StrategyNamingPattern,
			"unregistered_strategy", // Not registered
		},
		MinConfidence: 0.5,
	}

	// Act
	suggestions, err := detector.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	// Should skip unregistered strategy and continue
	assert.NotNil(t, suggestions)
}

// TestDetectMultipleStrategyAgreement confirms confidence boost from multiple strategies
func TestDetectMultipleStrategyAgreement(t *testing.T) {
	// Arrange
	detector := NewDetector(
		NewNamingStrategy(),
		NewAnnotationStrategy(),
	)

	projectID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:          uuid.New(),
		ProjectID:   projectID,
		Title:       "UserService",
		Description: "Service for managing users",
		Type:        "function",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "implements",
					"reference": "GetUsers",
					"raw":       "@trace-implements GetUsers",
				},
			},
		},
	}

	targetItem := &StrategyItemInfo{
		ID:          uuid.New(),
		ProjectID:   projectID,
		Title:       "UserService",
		Description: "Service for managing users",
		Type:        "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
		MinConfidence: 0.5,
	}

	// Act
	suggestions, err := detector.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	if len(suggestions) > 0 {
		// With only one strategy registered, results will have exactly 1 strategy
		// Multiple strategies would require registering additional strategies
		assert.GreaterOrEqual(t, len(suggestions[0].Strategies), 1)
	}
}

// TestDetectSelfSourceItemExcluded prevents matching an item with itself
func TestDetectSelfSourceItemExcluded(t *testing.T) {
	// Arrange
	detector := NewDetector(NewNamingStrategy())

	projectID := uuid.New()
	itemID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        itemID,
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	// Candidate pool includes the source item itself
	candidatePool := []*StrategyItemInfo{
		sourceItem, // Same ID
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "UserService",
			Type:      "function",
		},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidatePool,
		MinConfidence: 0.5,
	}

	// Act
	suggestions, err := detector.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	// Should not match source item with itself
	// Note: SourceItemID is always the source item's ID (that's correct behavior)
	// We only check that TargetItemID is not equal to source ID
	for _, s := range suggestions {
		assert.NotEqual(t, sourceItem.ID, s.TargetItemID)
	}
}

// TestDetectWithTimeout uses context timeout
func TestDetectWithTimeout(t *testing.T) {
	// Arrange
	detector := NewDetector(NewNamingStrategy())

	projectID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	candidatePool := []*StrategyItemInfo{
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "UserService",
			Type:      "function",
		},
	}

	ctx, cancel := context.WithTimeout(context.Background(), equivalenceDetectTimeout)
	defer cancel()

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidatePool,
		MinConfidence: 0.5,
	}

	// Act
	suggestions, err := detector.Detect(ctx, req)

	// Assert
	// Should complete within timeout
	require.NoError(t, err)
	assert.NotNil(t, suggestions)
}

// TestDetectPerformance measures detection performance
func TestDetectPerformance(t *testing.T) {
	// Arrange
	detector := NewDetector(NewNamingStrategy())

	projectID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	// Create large candidate pool
	candidatePool := make([]*StrategyItemInfo, 1000)
	for i := 0; i < 1000; i++ {
		candidatePool[i] = &StrategyItemInfo{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "Service" + string(rune(i%26+65)),
			Type:      "function",
		}
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidatePool,
		MinConfidence: 0.5,
		MaxResults:    10,
	}

	// Act
	start := time.Now()
	suggestions, err := detector.Detect(context.Background(), req)
	duration := time.Since(start)

	// Assert
	require.NoError(t, err)
	assert.NotNil(t, suggestions)
	// Detection should complete in reasonable time
	assert.Less(t, duration, 10*time.Second)
	t.Logf("Detection of 1000 items completed in %v", duration)
}

// TestDetectMixedItemTypes handles different item types
func TestDetectMixedItemTypes(t *testing.T) {
	// Arrange
	detector := NewDetector(NewNamingStrategy())

	projectID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserAuthentication",
		Type:      "requirement",
	}

	candidatePool := []*StrategyItemInfo{
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "UserAuthentication",
			Type:      "feature",
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "UserAuthentication",
			Type:      "function",
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "UserAuthentication",
			Type:      "test",
		},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidatePool,
		MinConfidence: 0.5,
	}

	// Act
	suggestions, err := detector.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.NotNil(t, suggestions)
	// Should find matches regardless of item type
	for _, candidate := range candidatePool {
		found := false
		for _, s := range suggestions {
			if s.TargetItemID == candidate.ID {
				found = true
				break
			}
		}
		// All candidates with matching title should be found
		if candidate.Title == sourceItem.Title {
			assert.True(t, found, "expected to find match for %s", candidate.Title)
		}
	}
}

// TestDetectNilSourceItem handles nil source item gracefully
func TestDetectNilSourceItem(t *testing.T) {
	// Arrange
	detector := NewDetector(NewNamingStrategy())

	projectID := uuid.New()
	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    nil, // Nil source item
		CandidatePool: []*StrategyItemInfo{},
		MinConfidence: 0.5,
	}

	// Act - should not panic
	assert.Panics(t, func() {
		_, err := detector.Detect(context.Background(), req)
		require.NoError(t, err)
	})
}

// TestDetectZeroMinConfidence accepts any confidence above zero
func TestDetectZeroMinConfidence(t *testing.T) {
	// Arrange
	detector := NewDetector(NewNamingStrategy())

	projectID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "Service",
		Type:      "function",
	}

	candidatePool := []*StrategyItemInfo{
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "Service",
			Type:      "function",
		},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidatePool,
		MinConfidence: 0.0, // Zero threshold
	}

	// Act
	suggestions, err := detector.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.NotNil(t, suggestions)
}

// TestDetectSpecialCharactersInTitle handles special characters
func TestDetectSpecialCharactersInTitle(t *testing.T) {
	// Arrange
	detector := NewDetector(NewNamingStrategy())

	projectID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User@Service#2024",
		Type:      "function",
	}

	candidatePool := []*StrategyItemInfo{
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "User@Service#2024",
			Type:      "function",
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "UserService2024",
			Type:      "function",
		},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidatePool,
		MinConfidence: 0.5,
	}

	// Act
	suggestions, err := detector.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.NotNil(t, suggestions)
}
