package equivalence

import (
	"context"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestAnnotationStrategyName returns correct strategy type
func TestAnnotationStrategyName(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()

	// Act
	name := strategy.Name()

	// Assert
	assert.Equal(t, StrategyExplicitAnnotation, name)
}

// TestAnnotationStrategyDefaultConfidence returns 1.0
func TestAnnotationStrategyDefaultConfidence(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()

	// Act
	confidence := strategy.DefaultConfidence()

	// Assert
	assert.InEpsilon(t, 1.0, confidence, 1e-9)
}

// TestAnnotationStrategyRequiresEmbeddings returns false
func TestAnnotationStrategyRequiresEmbeddings(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()

	// Act
	requires := strategy.RequiresEmbeddings()

	// Assert
	assert.False(t, requires)
}

// TestAnnotationDetectExplicitImplements finds @trace-implements annotations
func TestAnnotationDetectExplicitImplements(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	targetID := uuid.New()
	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "implements",
					"reference": targetID.String(),
					"raw":       "@trace-implements " + targetID.String(),
				},
			},
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        targetID,
		ProjectID: projectID,
		Title:     "GetUsers",
		Type:      "requirement",
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
	assert.InEpsilon(t, 1.0, result.Links[0].Confidence, 1e-9)
	assert.Equal(t, StatusAuto, result.Links[0].Status) // Auto-confirmed
}

// TestAnnotationDetectCanonical finds @canonical annotations
func TestAnnotationDetectCanonical(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "canonical",
					"reference": "UserConcept",
					"raw":       "@canonical UserConcept",
				},
			},
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserConcept",
		Type:      "canonical",
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

// TestAnnotationDetectSameAs finds @same-as annotations
func TestAnnotationDetectSameAs(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "same_as",
					"reference": "UserAuthService",
					"raw":       "@same-as UserAuthService",
				},
			},
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserAuthService",
		Type:      "service",
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

// TestAnnotationDetectRelatesTo finds @relates-to annotations
func TestAnnotationDetectRelatesTo(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "Authentication",
		Type:      "requirement",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "relates_to",
					"reference": "Security",
					"raw":       "@relates-to Security",
				},
			},
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "Security",
		Type:      "requirement",
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

// TestAnnotationDetectTests finds @test annotations
func TestAnnotationDetectTests(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserServiceTest",
		Type:      "test",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "tests",
					"reference": "UserService",
					"raw":       "@tests UserService",
				},
			},
		},
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
}

// TestAnnotationDetectDocuments finds @documents annotations
func TestAnnotationDetectDocuments(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "API Documentation",
		Type:      "document",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "documents",
					"reference": "UserEndpoint",
					"raw":       "@documents UserEndpoint",
				},
			},
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserEndpoint",
		Type:      "endpoint",
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

// TestAnnotationDetectNoAnnotations returns empty when no annotations
func TestAnnotationDetectNoAnnotations(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
		Metadata:  map[string]any{}, // No annotations
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

// TestAnnotationDetectExcludesSelfMatch excludes self-matching
func TestAnnotationDetectExcludesSelfMatch(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()
	itemID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        itemID,
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "implements",
					"reference": itemID.String(),
					"raw":       "@trace-implements " + itemID.String(),
				},
			},
		},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{sourceItem}, // Include source
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Empty(t, result.Links) // Should not match self
}

// TestAnnotationDetectContextCancellation handles cancelled context
func TestAnnotationDetectContextCancellation(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "implements",
					"reference": "UserEndpoint",
					"raw":       "@trace-implements UserEndpoint",
				},
			},
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserEndpoint",
		Type:      "endpoint",
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

// TestAnnotationDetectFromDescription extracts annotations from description
func TestAnnotationDetectFromDescription(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:          uuid.New(),
		ProjectID:   projectID,
		Title:       "UserService",
		Type:        "function",
		Description: "This service implements UserFetching. @trace-implements UserFetching",
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserFetching",
		Type:      "requirement",
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

// TestAnnotationDetectFromComments extracts annotations from comments metadata
func TestAnnotationDetectFromComments(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
		Metadata: map[string]any{
			"comments": "// @canonical UserConcept",
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserConcept",
		Type:      "concept",
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

// TestAnnotationDetectMultipleAnnotations handles multiple annotations
func TestAnnotationDetectMultipleAnnotations(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "implements",
					"reference": "GetUsers",
					"raw":       "@trace-implements GetUsers",
				},
				map[string]interface{}{
					"type":      "relates_to",
					"reference": "UserManagement",
					"raw":       "@relates-to UserManagement",
				},
			},
		},
	}

	candidates := []*StrategyItemInfo{
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "GetUsers",
			Type:      "endpoint",
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "UserManagement",
			Type:      "requirement",
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
	assert.Len(t, result.Links, 2)
}

// TestAnnotationDetectPartialNameMatch matches partial names
func TestAnnotationDetectPartialNameMatch(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "implements",
					"reference": "User",
					"raw":       "@trace-implements User",
				},
			},
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserManagementEndpoint",
		Type:      "endpoint",
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
	assert.Len(t, result.Links, 1) // Partial match should work
}

// TestAnnotationDetectIDMatch matches by UUID reference
func TestAnnotationDetectIDMatch(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()
	targetID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "implements",
					"reference": targetID.String(),
					"raw":       "@trace-implements " + targetID.String(),
				},
			},
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        targetID,
		ProjectID: projectID,
		Title:     "FetchUsers",
		Type:      "endpoint",
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
	assert.Equal(t, targetID, result.Links[0].TargetItemID)
}

// TestAnnotationParseAnnotationFromText extracts annotations from text
func TestAnnotationParseAnnotationFromText(t *testing.T) {
	tests := []struct {
		name    string
		text    string
		count   int
		hasType string
	}{
		{"implements_basic", "@trace-implements UserFetch", 1, "implements"},
		{"implements_quoted", "@trace-implements \"UserFetch\"", 1, "implements"},
		{"canonical", "@canonical UserConcept", 1, "canonical"},
		{"same_as", "@same-as UserService", 1, "same_as"},
		{"relates_to", "@relates-to Security", 1, "relates_to"},
		{"test", "@test UserServiceTest", 1, "tests"},
		{"document", "@document UserAPI", 1, "documents"},
		{"multiple", "@trace-implements A @canonical B", 2, ""},
		{"no_annotation", "Regular text without annotations", 0, ""},
	}

	strategy := NewAnnotationStrategy()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Act
			annotations := strategy.parseAnnotationsFromText(tt.text)

			// Assert
			assert.Len(t, annotations, tt.count)
			if tt.count > 0 && tt.hasType != "" {
				assert.Equal(t, tt.hasType, annotations[0].Type)
			}
		})
	}
}

// TestAnnotationDetectEvidence validates evidence details
func TestAnnotationDetectEvidence(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
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
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GetUsers",
		Type:      "endpoint",
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
	assert.Equal(t, StrategyExplicitAnnotation, link.Evidence[0].Strategy)
	assert.InEpsilon(t, 1.0, link.Evidence[0].Confidence, 1e-9)
	assert.Contains(t, link.Evidence[0].Details, "annotation_type")
	assert.Contains(t, link.Evidence[0].Details, "reference")
	assert.Contains(t, link.Evidence[0].Details, "raw")
}

// TestAnnotationDetectLinkType sets annotation type as link type
func TestAnnotationDetectLinkType(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "relates_to",
					"reference": "Security",
					"raw":       "@relates-to Security",
				},
			},
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "Security",
		Type:      "requirement",
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
	assert.Equal(t, "relates_to", result.Links[0].LinkType)
}

// TestAnnotationDetectCaseInsensitiveName matches names case-insensitively
func TestAnnotationDetectCaseInsensitiveName(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "implements",
					"reference": "GETUSERS",
					"raw":       "@trace-implements GETUSERS",
				},
			},
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "GetUsers",
		Type:      "endpoint",
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

// TestAnnotationDetectCodeRefMatch matches by code reference symbol name
func TestAnnotationDetectCodeRefMatch(t *testing.T) {
	// Arrange
	strategy := NewAnnotationStrategy()
	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "UserService",
		Type:      "function",
		Metadata: map[string]any{
			"annotations": []interface{}{
				map[string]interface{}{
					"type":      "implements",
					"reference": "getUserById",
					"raw":       "@trace-implements getUserById",
				},
			},
		},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "Get User By ID",
		Type:      "function",
		CodeRef: &StrategyCodeRef{
			SymbolName: "getUserById",
			SymbolType: "function",
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
