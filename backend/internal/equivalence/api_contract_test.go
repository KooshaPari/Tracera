package equivalence

import (
	"context"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestAPIContractStrategyName returns correct strategy type
func TestAPIContractStrategyName(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()

	// Act
	name := strategy.Name()

	// Assert
	assert.Equal(t, StrategyAPIContract, name)
}

// TestAPIContractStrategyDefaultConfidence returns 0.9
func TestAPIContractStrategyDefaultConfidence(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()

	// Act
	confidence := strategy.DefaultConfidence()

	// Assert
	assert.InEpsilon(t, 0.9, confidence, 1e-9)
}

// TestAPIContractStrategyRequiresEmbeddings returns false
func TestAPIContractStrategyRequiresEmbeddings(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()

	// Act
	requires := strategy.RequiresEmbeddings()

	// Assert
	assert.False(t, requires)
}

// TestAPIContractDetectExactMatch finds identical endpoints
func TestAPIContractDetectExactMatch(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GetUsers",
		Type:      "function",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GET /users",
		Type:      "route",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
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
	assert.InEpsilon(t, 0.9, result.Links[0].Confidence, 1e-9)
	assert.Equal(t, "exact", result.Links[0].Evidence[0].Details["match_type"])
}

// TestAPIContractDetectPatternMatch matches endpoints with parameter placeholders
func TestAPIContractDetectPatternMatch(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GetUserByID",
		Type:      "function",
		Metadata: map[string]any{
			"endpoint": "/api/users/:id",
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GET /users/{id}",
		Type:      "route",
		Metadata: map[string]any{
			"endpoint": "/api/users/{id}",
		},
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
	assert.Equal(t, "pattern", result.Links[0].Evidence[0].Details["match_type"])
}

// TestAPIContractDetectResourceMatch matches function names to endpoint resources
func TestAPIContractDetectResourceMatch(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "getUsers",
		Type:      "function",
		Metadata: map[string]any{
			"endpoint": "getUsers",
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GET /api/users",
		Type:      "route",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
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
	assert.Equal(t, "resource", result.Links[0].Evidence[0].Details["match_type"])
}

// TestAPIContractDetectNoEndpointMetadata returns empty when no endpoint
func TestAPIContractDetectNoEndpointMetadata(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
		Metadata:  map[string]any{}, // No endpoint
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "route",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
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

// TestAPIContractDetectCandidateNoEndpoint skips candidates without endpoints
func TestAPIContractDetectCandidateNoEndpoint(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GetUsers",
		Type:      "function",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "class",
		Metadata:  map[string]any{}, // No endpoint
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

// TestAPIContractDetectVersionIgnored ignores API version prefixes
func TestAPIContractDetectVersionIgnored(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GetUsers",
		Type:      "function",
		Metadata: map[string]any{
			"endpoint": "/api/v1/users",
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GET /users",
		Type:      "route",
		Metadata: map[string]any{
			"endpoint": "/api/v2/users",
		},
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
	assert.Len(t, result.Links, 1) // Should match despite version difference
}

// TestAPIContractDetectCaseInsensitive matches endpoints case-insensitively
func TestAPIContractDetectCaseInsensitive(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GetUsers",
		Type:      "function",
		Metadata: map[string]any{
			"endpoint": "/API/USERS",
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GET /users",
		Type:      "route",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
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

// TestAPIContractDetectNoMatch finds no match for different endpoints
func TestAPIContractDetectNoMatch(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GetUsers",
		Type:      "function",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GET /products",
		Type:      "route",
		Metadata: map[string]any{
			"endpoint": "/api/products",
		},
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

// TestAPIContractDetectExcludesSelfMatch excludes self-matching
func TestAPIContractDetectExcludesSelfMatch(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()
	itemID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        itemID,
		ProjectID: projectID,
		Title:     "GetUsers",
		Type:      "function",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{sourceItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Empty(t, result.Links)
}

// TestAPIContractDetectContextCancellation handles cancelled context
func TestAPIContractDetectContextCancellation(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GetUsers",
		Type:      "function",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GET /users",
		Type:      "route",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
	}

	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	_, err := strategy.Detect(ctx, req)

	// Assert
	require.Error(t, err)
	assert.Equal(t, context.Canceled, err)
}

// TestAPIContractDetectRouteMetadata extracts from route metadata
func TestAPIContractDetectRouteMetadata(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "FetchUsers",
		Type:      "function",
		Metadata: map[string]any{
			"route": "/api/users",
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GET /users",
		Type:      "route",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
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

// TestAPIContractDetectCodeRefMetadata extracts from code reference
func TestAPIContractDetectCodeRefMetadata(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserHandler",
		Type:      "function",
		Metadata:  map[string]any{},
		CodeRef: &StrategyCodeRef{
			SymbolName: "/api/users",
			SymbolType: "route_handler",
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GET /users",
		Type:      "route",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
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

// TestAPIContractDetectMultipleCandidates scans all candidates
func TestAPIContractDetectMultipleCandidates(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "FetchData",
		Type:      "function",
		Metadata: map[string]any{
			"endpoint": "/api/data",
		},
	}

	candidates := []*StrategyItemInfo{
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "GET /data",
			Type:      "route",
			Metadata: map[string]any{
				"endpoint": "/api/data",
			},
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "GET /users",
			Type:      "route",
			Metadata: map[string]any{
				"endpoint": "/api/users",
			},
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "POST /data",
			Type:      "route",
			Metadata: map[string]any{
				"endpoint": "/api/data",
			},
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
	assert.Equal(t, 3, result.ItemsScanned)
	assert.Len(t, result.Links, 2) // Both /api/data matches
}

// TestAPIContractNormalizeEndpoint validates endpoint normalization
func TestAPIContractNormalizeEndpoint(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string
	}{
		{"exact", "users", "users"},
		{"with_api_prefix", "/api/users", "users"},
		{"with_v1_prefix", "/api/v1/users", "users"},
		{"with_v2_prefix", "/api/v2/users", "users"},
		{"with_trailing_slash", "/api/users/", "users"},
		{"case_insensitive", "/API/USERS", "users"},
		{"with_leading_slash", "/users", "users"},
	}

	strategy := NewAPIContractStrategy()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Act
			result := strategy.normalizeEndpoint(tt.input)

			// Assert
			assert.Equal(t, tt.expected, result)
		})
	}
}

// TestAPIContractPatternMatch validates pattern matching
func TestAPIContractPatternMatch(t *testing.T) {
	tests := []struct {
		name        string
		a           string
		b           string
		expectMatch bool
	}{
		{"exact_match", "users", "users", true},
		{"param_colon", "users/:id", "users/{id}", true},
		{"uuid_param", "users/550e8400-e29b-41d4-a716-446655440000", "users/{id}", true},
		{"numeric_param", "users/123", "users/{id}", true},
		{"different_resources", "users/id", "products/id", false},
	}

	strategy := NewAPIContractStrategy()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Act
			match := strategy.patternMatch(tt.a, tt.b)

			// Assert
			assert.Equal(t, tt.expectMatch, match)
		})
	}
}

// TestAPIContractResourceMatch validates resource matching
func TestAPIContractResourceMatch(t *testing.T) {
	tests := []struct {
		name        string
		a           string
		b           string
		expectMatch bool
	}{
		{"getUsers_users", "getUsers", "users", true},
		{"fetchData_data", "fetchData", "data", true},
		{"postItem_item", "postItem", "item", true},
		{"listProducts_products", "listProducts", "products", true},
		{"deleteUser_user", "deleteUser", "user", true},
		{"different", "getUsers", "products", false},
	}

	strategy := NewAPIContractStrategy()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Act
			match := strategy.resourceMatch(tt.a, tt.b)

			// Assert
			assert.Equal(t, tt.expectMatch, match)
		})
	}
}

// TestAPIContractDetectEvidence validates evidence details
func TestAPIContractDetectEvidence(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GetUsers",
		Type:      "function",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GET /users",
		Type:      "route",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
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
	assert.Equal(t, StrategyAPIContract, link.Evidence[0].Strategy)
	assert.Contains(t, link.Evidence[0].Details, "source_endpoint")
	assert.Contains(t, link.Evidence[0].Details, "target_endpoint")
	assert.Contains(t, link.Evidence[0].Details, "match_type")
}

// TestAPIContractDetectLinkType sets correct link type
func TestAPIContractDetectLinkType(t *testing.T) {
	// Arrange
	strategy := NewAPIContractStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GetUsers",
		Type:      "function",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GET /users",
		Type:      "route",
		Metadata: map[string]any{
			"endpoint": "/api/users",
		},
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
	assert.Equal(t, "implements", result.Links[0].LinkType)
}
