package equivalence

import (
	"context"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestNamingStrategyName returns correct strategy type
func TestNamingStrategyName(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()

	// Act
	name := strategy.Name()

	// Assert
	assert.Equal(t, StrategyNamingPattern, name)
}

// TestNamingStrategyDefaultConfidence returns 0.7
func TestNamingStrategyDefaultConfidence(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()

	// Act
	confidence := strategy.DefaultConfidence()

	// Assert
	assert.InEpsilon(t, 0.7, confidence, 1e-9)
}

// TestNamingStrategyRequiresEmbeddings returns false
func TestNamingStrategyRequiresEmbeddings(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()

	// Act
	requires := strategy.RequiresEmbeddings()

	// Assert
	assert.False(t, requires)
}

// TestNamingDetectExactMatch finds items with identical titles
func TestNamingDetectExactMatch(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, StrategyNamingPattern, result.Strategy)
	assert.Len(t, result.Links, 1)
	assert.InEpsilon(t, 0.7, result.Links[0].Confidence, 1e-9)
}

// TestNamingDetectCamelCaseMatch matches CamelCase variations
func TestNamingDetectCamelCaseMatch(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserData",
		Type:      "function",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "user_data", // snake_case version
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	// "UserData" -> "user data", "user_data" -> "user data"
	// Both normalize to same value, so should match
	require.Len(t, result.Links, 1)
	assert.Greater(t, result.Links[0].Confidence, 0.0)
}

// TestNamingDetectSnakeCaseMatch matches snake_case variations
func TestNamingDetectSnakeCaseMatch(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "user_service",
		Type:      "function",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "user_service",
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Len(t, result.Links, 1)
	assert.InEpsilon(t, 0.7, result.Links[0].Confidence, 1e-9)
}

// TestNamingDetectKebabCaseMatch matches kebab-case variations
func TestNamingDetectKebabCaseMatch(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "user-service",
		Type:      "function",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "user-service",
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Len(t, result.Links, 1)
}

// TestNamingDetectMixedCaseConversion converts mixed naming patterns
func TestNamingDetectMixedCaseConversion(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "user_service",
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Len(t, result.Links, 1)
	// Both normalize to "user service"
	assert.InEpsilon(t, 0.7, result.Links[0].Confidence, 1e-9)
}

// TestNamingDetectRemovesSuffixes removes common role suffixes
func TestNamingDetectRemovesSuffixes(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserHandler",
		Type:      "function",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserController",
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	// Both should normalize to "user" after removing " handler" and " controller" suffixes
	assert.Len(t, result.Links, 1)
}

// TestNamingDetectEmptySourceTitle returns no matches
func TestNamingDetectEmptySourceTitle(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "",
		Type:      "function",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Empty(t, result.Links)
}

// TestNamingDetectEmptyCandidateTitle skips empty titles
func TestNamingDetectEmptyCandidateTitle(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "",
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Empty(t, result.Links)
}

// TestNamingDetectExcludesSelfMatch excludes source item from results
func TestNamingDetectExcludesSelfMatch(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()
	itemID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        itemID,
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{sourceItem}, // Include source itself
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Empty(t, result.Links) // Should not match self
}

// TestNamingDetectPluralization handles common pluralization rules
func TestNamingDetectPluralization(t *testing.T) {
	tests := []struct {
		name        string
		source      string
		target      string
		expectMatch bool
	}{
		{"singular_plural_s", "User", "Users", true},
		{"ies_to_y", "Category", "Categories", true},
		{"es_suffix", "Process", "Processes", true},
		{"ss_suffix", "Class", "Classes", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Arrange
			strategy := NewNamingStrategy()
			projectID := uuid.New()

			sourceItem := &StrategyItemInfo{
				ID:        uuid.New(),
				ProjectID: projectID,
				Title:     tt.source,
				Type:      "function",
			}

			targetItem := &StrategyItemInfo{
				ID:        uuid.New(),
				ProjectID: projectID,
				Title:     tt.target,
				Type:      "function",
			}

			req := &StrategyDetectionRequest{
				ProjectID:     projectID,
				SourceItem:    sourceItem,
				CandidatePool: []*StrategyItemInfo{targetItem},
			}

			// Act
			result, err := strategy.Detect(context.Background(), req)

			// Assert
			require.NoError(t, err)
			if tt.expectMatch {
				assert.NotEmpty(t, result.Links, "expected match for %s -> %s", tt.source, tt.target)
			}
		})
	}
}

// TestNamingDetectLowSimilarityNoMatch rejects low similarity scores
func TestNamingDetectLowSimilarityNoMatch(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserAuthentication",
		Type:      "function",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "ProductCatalog",
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Empty(t, result.Links) // No match due to low similarity
}

// TestNamingDetectContextCancellation handles cancelled context
func TestNamingDetectContextCancellation(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	ctx, cancel := context.WithCancel(context.Background())
	cancel() // Cancel immediately

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(ctx, req)

	// Assert
	require.Error(t, err)
	assert.Equal(t, context.Canceled, err)
	assert.Equal(t, context.Canceled.Error(), result.Error)
}

// TestNamingDetectSpecialCharacters handles special characters
func TestNamingDetectSpecialCharacters(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User@Service#2024",
		Type:      "function",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User@Service#2024",
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	// Should handle special characters gracefully
	assert.NotNil(t, result)
}

// TestNamingDetectWhitespaceHandling handles whitespace variations
func TestNamingDetectWhitespaceHandling(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "  User Service  ",
		Type:      "function",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Len(t, result.Links, 1) // Should trim whitespace and match
}

// TestNamingDetectMultipleCandidates scans all candidates
func TestNamingDetectMultipleCandidates(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User",
		Type:      "function",
	}

	candidates := []*StrategyItemInfo{
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "User",
			Type:      "function",
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "UserService", // normalizes to "user" (suffix removed)
			Type:      "function",
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "UserModel", // normalizes to "user" (suffix removed)
			Type:      "function",
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "Product",
			Type:      "function",
		},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidates,
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Equal(t, 4, result.ItemsScanned) // 4 candidates scanned
	// "User" -> "user", matches "User", "UserService" (-> "user"), "UserModel" (-> "user")
	// Does not match "Product" (-> "product")
	assert.Len(t, result.Links, 3)
}

// TestNamingNormalizeForComparison validates normalization logic
func TestNamingNormalizeForComparison(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string
	}{
		{"camelcase", "UserService", "user"},   // "user service" -> suffix removed -> "user"
		{"snake_case", "user_service", "user"}, // "user service" -> suffix removed -> "user"
		{"kebab-case", "user-service", "user"}, // "user service" -> suffix removed -> "user"
		{"with_suffix", "UserServiceHandler", "user service"},
		// "user service handler" -> remove " handler" -> "user service" (only one pass)
		{"plural", "Users", "user"},                 // "users" -> remove "s" -> "user"
		{"ies_plural", "Categories", "category"},    // "categories" -> "ies" -> "y" -> "category"
		{"es_plural", "Processes", "process"},       // "processes" -> remove "es" -> "process"
		{"with_spaces", "  User Service  ", "user"}, // trim + suffix removal
		{"mixed", "UserService_Handler", "user service"},
		// "user service handler" -> remove " handler" -> "user service" (only one pass)
		{"no_suffix", "UserProfile", "user profile"}, // no matching suffix, stays as is
		{"model_suffix", "UserModel", "user"},        // " model" suffix removed
	}

	strategy := NewNamingStrategy()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Act
			result := strategy.normalizeForComparison(tt.input)

			// Assert
			assert.Equal(t, tt.expected, result, "normalization mismatch for %s", tt.input)
		})
	}
}

// TestNamingCalculateSimilarity validates similarity calculation
func TestNamingCalculateSimilarity(t *testing.T) {
	tests := []struct {
		name     string
		a        string
		b        string
		minScore float64 // Minimum expected similarity
		maxScore float64 // Maximum expected similarity
	}{
		{"exact_match", "user service", "user service", 0.99, 1.0},
		{"partial_match", "user", "user service", 0.3, 0.7},
		{"no_match", "user", "product", 0.0, 0.3},
		{"empty_a", "", "user", 0.0, 0.0},
		{"empty_b", "user", "", 0.0, 0.0},
		{"single_token", "user", "user", 0.99, 1.0},
	}

	strategy := NewNamingStrategy()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Act
			similarity := strategy.calculateSimilarity(tt.a, tt.b)

			// Assert
			assert.GreaterOrEqual(t, similarity, tt.minScore, "similarity too low for %s vs %s", tt.a, tt.b)
			assert.LessOrEqual(t, similarity, tt.maxScore, "similarity too high for %s vs %s", tt.a, tt.b)
		})
	}
}

// TestNamingDetectLowercaseConversion converts to lowercase
func TestNamingDetectLowercaseConversion(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "USERSERVICE",
		Type:      "function",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "userservice",
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Len(t, result.Links, 1) // Should match after lowercase conversion
}

// TestNamingDetectEvidence validates evidence details
func TestNamingDetectEvidence(t *testing.T) {
	// Arrange
	strategy := NewNamingStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Len(t, result.Links, 1)

	link := result.Links[0]
	assert.NotEmpty(t, link.Evidence)
	assert.Equal(t, StrategyNamingPattern, link.Evidence[0].Strategy)
	assert.Contains(t, link.Evidence[0].Details, "similarity")
	assert.Contains(t, link.Evidence[0].Details, "source_normalized")
	assert.Contains(t, link.Evidence[0].Details, "target_normalized")
}
