package equivalence

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/require"
)

// MockRepository implements the Repository interface for testing
type MockRepository struct {
	suggestions map[uuid.UUID]*Suggestion
	links       map[uuid.UUID]*Link
	concepts    map[uuid.UUID]*CanonicalConcept
	projections map[uuid.UUID][]CanonicalProjection
}

func NewMockRepository() *MockRepository {
	return &MockRepository{
		suggestions: make(map[uuid.UUID]*Suggestion),
		links:       make(map[uuid.UUID]*Link),
		concepts:    make(map[uuid.UUID]*CanonicalConcept),
		projections: make(map[uuid.UUID][]CanonicalProjection),
	}
}

// Suggestion methods
func (m *MockRepository) SaveSuggestion(_ context.Context, s *Suggestion) error {
	m.suggestions[s.ID] = s
	return nil
}

func (m *MockRepository) GetSuggestion(_ context.Context, id uuid.UUID) (*Suggestion, error) {
	if s, ok := m.suggestions[id]; ok {
		return s, nil
	}
	return nil, errors.New("suggestion not found")
}

func (m *MockRepository) ListSuggestions(_ context.Context, projectID uuid.UUID, _, _ int) ([]Suggestion, error) {
	var result []Suggestion
	for _, s := range m.suggestions {
		if s.ProjectID == projectID {
			result = append(result, *s)
		}
	}
	return result, nil
}

func (m *MockRepository) DeleteSuggestion(_ context.Context, id uuid.UUID) error {
	delete(m.suggestions, id)
	return nil
}

// Link methods
func (m *MockRepository) SaveLink(_ context.Context, link *Link) error {
	m.links[link.ID] = link
	return nil
}

func (m *MockRepository) GetLink(_ context.Context, id uuid.UUID) (*Link, error) {
	if l, ok := m.links[id]; ok {
		return l, nil
	}
	return nil, errors.New("link not found")
}

func (m *MockRepository) GetLinksByItem(_ context.Context, itemID uuid.UUID) ([]Link, error) {
	var result []Link
	for _, l := range m.links {
		if l.SourceItemID == itemID || l.TargetItemID == itemID {
			result = append(result, *l)
		}
	}
	return result, nil
}

func (m *MockRepository) ListLinksByProject(_ context.Context, filter Filter, _, _ int) ([]Link, int64, error) {
	var result []Link
	for _, l := range m.links {
		if l.ProjectID == filter.ProjectID {
			result = append(result, *l)
		}
	}
	return result, int64(len(result)), nil
}

func (m *MockRepository) UpdateLinkStatus(_ context.Context, id uuid.UUID, status Status, _ uuid.UUID) error {
	if l, ok := m.links[id]; ok {
		l.Status = status
		return nil
	}
	return errors.New("link not found")
}

// Concept methods
func (m *MockRepository) SaveConcept(_ context.Context, c *CanonicalConcept) error {
	m.concepts[c.ID] = c
	return nil
}

func (m *MockRepository) GetConcept(_ context.Context, id uuid.UUID) (*CanonicalConcept, error) {
	if c, ok := m.concepts[id]; ok {
		return c, nil
	}
	return nil, errors.New("concept not found")
}

func (m *MockRepository) ListConcepts(_ context.Context, projectID uuid.UUID) ([]CanonicalConcept, error) {
	var result []CanonicalConcept
	for _, c := range m.concepts {
		if c.ProjectID == projectID {
			result = append(result, *c)
		}
	}
	return result, nil
}

func (m *MockRepository) SearchConceptsByEmbedding(
	_ context.Context,
	_ uuid.UUID,
	_ []float32,
	_ int,
) ([]CanonicalConcept, error) {
	return []CanonicalConcept{}, nil
}

// Projection methods
func (m *MockRepository) SaveProjection(_ context.Context, p *CanonicalProjection) error {
	m.projections[p.CanonicalID] = append(m.projections[p.CanonicalID], *p)
	return nil
}

func (m *MockRepository) GetProjectionsByItem(_ context.Context, _ uuid.UUID) ([]CanonicalProjection, error) {
	return []CanonicalProjection{}, nil
}

func (m *MockRepository) GetProjectionsByConcept(
	_ context.Context,
	conceptID uuid.UUID,
) ([]CanonicalProjection, error) {
	return m.projections[conceptID], nil
}

func (m *MockRepository) GetProjection(_ context.Context, id uuid.UUID) (*CanonicalProjection, error) {
	// Find projection by ID across all concepts
	for _, projections := range m.projections {
		for i, p := range projections {
			if p.ID == id {
				return &projections[i], nil
			}
		}
	}
	return nil, errors.New("projection not found")
}

func (m *MockRepository) DeleteProjection(_ context.Context, id uuid.UUID) error {
	// Remove projection from all concept projections maps
	for conceptID := range m.projections {
		filtered := make([]CanonicalProjection, 0)
		for _, p := range m.projections[conceptID] {
			if p.ID != id {
				filtered = append(filtered, p)
			}
		}
		m.projections[conceptID] = filtered
	}
	return nil
}

// Test helper function to create a test suggestion
func createTestSuggestion(
	id uuid.UUID,
	projectID uuid.UUID,
	sourceID uuid.UUID,
	targetID uuid.UUID,
	strategies []StrategyType,
	evidence []Evidence,
) *Suggestion {
	return &Suggestion{
		ID:              id,
		ProjectID:       projectID,
		SourceItemID:    sourceID,
		SourceItemTitle: "Source Item",
		SourceItemType:  "Type1",
		TargetItemID:    targetID,
		TargetItemTitle: "Target Item",
		TargetItemType:  "Type2",
		SuggestedType:   "same_as",
		Confidence:      0.9,
		Strategies:      strategies,
		Evidence:        evidence,
		CreatedAt:       time.Now(),
	}
}

// ============================================================================
// TESTS FOR determineProvenance FUNCTION
// ============================================================================

// TestDetermineProvenance_WithStrategies tests the function when strategies are present
func TestDetermineProvenance_WithStrategies(t *testing.T) {
	projectID := uuid.New()
	sourceID := uuid.New()
	targetID := uuid.New()
	suggestionID := uuid.New()

	suggestion := createTestSuggestion(
		suggestionID,
		projectID,
		sourceID,
		targetID,
		[]StrategyType{StrategyNamingPattern, StrategySemanticSimilarity},
		[]Evidence{},
	)

	result := determineProvenance(suggestion)

	if result != StrategyNamingPattern {
		t.Errorf("expected %q, got %q", StrategyNamingPattern, result)
	}
}

// TestDetermineProvenance_EmptyStrategies_WithEvidence tests fallback to evidence
func TestDetermineProvenance_EmptyStrategies_WithEvidence(t *testing.T) {
	projectID := uuid.New()
	sourceID := uuid.New()
	targetID := uuid.New()
	suggestionID := uuid.New()

	evidence := []Evidence{
		{
			Strategy:    StrategyAPIContract,
			Confidence:  0.5,
			Description: "Lower confidence",
		},
		{
			Strategy:    StrategySemanticSimilarity,
			Confidence:  0.8,
			Description: "Higher confidence",
		},
	}

	suggestion := createTestSuggestion(
		suggestionID,
		projectID,
		sourceID,
		targetID,
		[]StrategyType{}, // Empty strategies - should use evidence
		evidence,
	)

	result := determineProvenance(suggestion)

	if result != StrategySemanticSimilarity {
		t.Errorf("expected %q (highest confidence evidence), got %q", StrategySemanticSimilarity, result)
	}
}

// TestDetermineProvenance_EmptyStrategies_EmptyEvidence tests default fallback
func TestDetermineProvenance_EmptyStrategies_EmptyEvidence(t *testing.T) {
	projectID := uuid.New()
	sourceID := uuid.New()
	targetID := uuid.New()
	suggestionID := uuid.New()

	suggestion := createTestSuggestion(
		suggestionID,
		projectID,
		sourceID,
		targetID,
		[]StrategyType{}, // Empty strategies
		[]Evidence{},     // Empty evidence
	)

	result := determineProvenance(suggestion)

	if result != StrategyNamingPattern {
		t.Errorf("expected default %q, got %q", StrategyNamingPattern, result)
	}
}

// TestDetermineProvenance_SingleStrategy tests single strategy case
func TestDetermineProvenance_SingleStrategy(t *testing.T) {
	projectID := uuid.New()
	sourceID := uuid.New()
	targetID := uuid.New()
	suggestionID := uuid.New()

	suggestion := createTestSuggestion(
		suggestionID,
		projectID,
		sourceID,
		targetID,
		[]StrategyType{StrategyExplicitAnnotation},
		[]Evidence{},
	)

	result := determineProvenance(suggestion)

	if result != StrategyExplicitAnnotation {
		t.Errorf("expected %q, got %q", StrategyExplicitAnnotation, result)
	}
}

// TestDetermineProvenance_EvidenceWithZeroConfidence tests edge case
func TestDetermineProvenance_EvidenceWithZeroConfidence(t *testing.T) {
	projectID := uuid.New()
	sourceID := uuid.New()
	targetID := uuid.New()
	suggestionID := uuid.New()

	evidence := []Evidence{
		{
			Strategy:    StrategyAPIContract,
			Confidence:  0.0, // Zero confidence
			Description: "No confidence",
		},
		{
			Strategy:    StrategySemanticSimilarity,
			Confidence:  0.0, // Also zero
			Description: "No confidence either",
		},
	}

	suggestion := createTestSuggestion(
		suggestionID,
		projectID,
		sourceID,
		targetID,
		[]StrategyType{}, // Empty strategies
		evidence,
	)

	result := determineProvenance(suggestion)

	// When all evidence has zero confidence, none satisfy the maxConf > condition
	// So it falls back to default
	if result != StrategyNamingPattern {
		t.Errorf("expected default %q, got %q", StrategyNamingPattern, result)
	}
}

// ============================================================================
// TESTS FOR ConfirmSuggestion METHOD
// ============================================================================

// TestConfirmSuggestion_WithStrategies tests confirmation with non-empty strategies
func TestConfirmSuggestion_WithStrategies(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	projectID := uuid.New()
	sourceID := uuid.New()
	targetID := uuid.New()
	suggestionID := uuid.New()
	userID := uuid.New()

	suggestion := createTestSuggestion(
		suggestionID,
		projectID,
		sourceID,
		targetID,
		[]StrategyType{StrategyNamingPattern},
		[]Evidence{},
	)

	require.NoError(t, repo.SaveSuggestion(ctx, suggestion))

	link, err := service.ConfirmSuggestion(ctx, suggestionID, userID)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if link == nil {
		t.Fatal("expected link, got nil")
	}

	if link.Provenance != StrategyNamingPattern {
		t.Errorf("expected provenance %q, got %q", StrategyNamingPattern, link.Provenance)
	}

	if link.Status != StatusConfirmed {
		t.Errorf("expected status %q, got %q", StatusConfirmed, link.Status)
	}

	if link.ConfirmedBy == nil || *link.ConfirmedBy != userID {
		t.Error("expected ConfirmedBy to be set to userID")
	}

	// Suggestion should be deleted
	_, err = repo.GetSuggestion(ctx, suggestionID)
	if err == nil {
		t.Error("expected suggestion to be deleted")
	}
}

// TestConfirmSuggestion_EmptyStrategies_FallbackToEvidence tests the crash fix
func TestConfirmSuggestion_EmptyStrategies_FallbackToEvidence(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	projectID := uuid.New()
	sourceID := uuid.New()
	targetID := uuid.New()
	suggestionID := uuid.New()
	userID := uuid.New()

	// This was causing the crash: empty Strategies array
	evidence := []Evidence{
		{
			Strategy:    StrategySemanticSimilarity,
			Confidence:  0.85,
			Description: "Semantic match",
		},
	}

	suggestion := createTestSuggestion(
		suggestionID,
		projectID,
		sourceID,
		targetID,
		[]StrategyType{}, // Empty - would have caused panic with suggestion.Strategies[0]
		evidence,
	)

	require.NoError(t, repo.SaveSuggestion(ctx, suggestion))

	// This should NOT crash anymore
	link, err := service.ConfirmSuggestion(ctx, suggestionID, userID)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if link == nil {
		t.Fatal("expected link, got nil")
	}

	if link.Provenance != StrategySemanticSimilarity {
		t.Errorf("expected provenance %q (from evidence), got %q", StrategySemanticSimilarity, link.Provenance)
	}
}

// TestConfirmSuggestion_EmptyStrategies_EmptyEvidence_DefaultFallback tests default
func TestConfirmSuggestion_EmptyStrategies_EmptyEvidence_DefaultFallback(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	projectID := uuid.New()
	sourceID := uuid.New()
	targetID := uuid.New()
	suggestionID := uuid.New()
	userID := uuid.New()

	suggestion := createTestSuggestion(
		suggestionID,
		projectID,
		sourceID,
		targetID,
		[]StrategyType{}, // Empty
		[]Evidence{},     // Empty
	)

	require.NoError(t, repo.SaveSuggestion(ctx, suggestion))

	link, err := service.ConfirmSuggestion(ctx, suggestionID, userID)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if link == nil {
		t.Fatal("expected link, got nil")
	}

	// Should fall back to default strategy
	if link.Provenance != StrategyNamingPattern {
		t.Errorf("expected provenance %q (default), got %q", StrategyNamingPattern, link.Provenance)
	}
}

// TestConfirmSuggestion_NotFound tests error handling for non-existent suggestion
func TestConfirmSuggestion_NotFound(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	nonExistentID := uuid.New()
	userID := uuid.New()

	_, err := service.ConfirmSuggestion(ctx, nonExistentID, userID)
	if err == nil {
		t.Fatal("expected error for non-existent suggestion")
	}
}

// TestConfirmSuggestion_PreservesAllFields tests that all fields are preserved
func TestConfirmSuggestion_PreservesAllFields(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	projectID := uuid.New()
	sourceID := uuid.New()
	targetID := uuid.New()
	suggestionID := uuid.New()
	userID := uuid.New()

	evidence := []Evidence{
		{
			Strategy:    StrategyAPIContract,
			Confidence:  0.9,
			Description: "API contract match",
		},
	}

	suggestion := createTestSuggestion(
		suggestionID,
		projectID,
		sourceID,
		targetID,
		[]StrategyType{}, // Empty - test fallback
		evidence,
	)

	require.NoError(t, repo.SaveSuggestion(ctx, suggestion))

	link, err := service.ConfirmSuggestion(ctx, suggestionID, userID)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if link.ProjectID != projectID {
		t.Errorf("expected ProjectID %v, got %v", projectID, link.ProjectID)
	}

	if link.SourceItemID != sourceID {
		t.Errorf("expected SourceItemID %v, got %v", sourceID, link.SourceItemID)
	}

	if link.TargetItemID != targetID {
		t.Errorf("expected TargetItemID %v, got %v", targetID, link.TargetItemID)
	}

	if link.Confidence != suggestion.Confidence {
		t.Errorf("expected Confidence %f, got %f", suggestion.Confidence, link.Confidence)
	}

	if len(link.Evidence) != len(evidence) {
		t.Errorf("expected %d evidence items, got %d", len(evidence), len(link.Evidence))
	}
}

// TestBulkConfirm_WithEmptyStrategiesInSome tests bulk confirm with mixed suggestions
func TestBulkConfirm_WithEmptyStrategiesInSome(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	projectID := uuid.New()
	userID := uuid.New()

	// Create multiple suggestions with different strategy configurations
	sugg1ID := uuid.New()
	sugg2ID := uuid.New()

	sugg1 := createTestSuggestion(
		sugg1ID,
		projectID,
		uuid.New(),
		uuid.New(),
		[]StrategyType{StrategyNamingPattern}, // Has strategy
		[]Evidence{},
	)

	sugg2 := createTestSuggestion(
		sugg2ID,
		projectID,
		uuid.New(),
		uuid.New(),
		[]StrategyType{}, // Empty strategy - would crash with old code
		[]Evidence{
			{Strategy: StrategySemanticSimilarity, Confidence: 0.85, Description: "Test"},
		},
	)

	require.NoError(t, repo.SaveSuggestion(ctx, sugg1))
	require.NoError(t, repo.SaveSuggestion(ctx, sugg2))

	links, err := service.BulkConfirm(ctx, []uuid.UUID{sugg1ID, sugg2ID}, userID)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if len(links) != 2 {
		t.Errorf("expected 2 links, got %d", len(links))
	}

	if links[0].Provenance != StrategyNamingPattern {
		t.Errorf("first link: expected provenance %q, got %q", StrategyNamingPattern, links[0].Provenance)
	}

	if links[1].Provenance != StrategySemanticSimilarity {
		t.Errorf("second link: expected provenance %q, got %q", StrategySemanticSimilarity, links[1].Provenance)
	}
}

// ============================================================================
// TESTS FOR NEW SERVICE METHODS
// ============================================================================

// TestGetEquivalenceByID_Success tests successful retrieval of an equivalence
func TestGetEquivalenceByID_Success(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	linkID := uuid.New()
	projectID := uuid.New()
	sourceID := uuid.New()
	targetID := uuid.New()

	link := &Link{
		ID:           linkID,
		ProjectID:    projectID,
		SourceItemID: sourceID,
		TargetItemID: targetID,
		LinkType:     "same_as",
		Confidence:   0.95,
		Provenance:   StrategyNamingPattern,
		Status:       StatusConfirmed,
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}

	require.NoError(t, repo.SaveLink(ctx, link))

	retrieved, err := service.GetEquivalenceByID(ctx, linkID)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if retrieved == nil {
		t.Fatal("expected link, got nil")
	}

	if retrieved.ID != linkID {
		t.Errorf("expected ID %v, got %v", linkID, retrieved.ID)
	}

	if retrieved.SourceItemID != sourceID {
		t.Errorf("expected SourceItemID %v, got %v", sourceID, retrieved.SourceItemID)
	}
}

// TestGetEquivalenceByID_NotFound tests error when equivalence doesn't exist
func TestGetEquivalenceByID_NotFound(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	linkID := uuid.New()

	_, err := service.GetEquivalenceByID(ctx, linkID)
	if err == nil {
		t.Fatal("expected error, got nil")
	}
}

// TestConfirmEquivalenceByID_Success tests confirming an equivalence by ID
func TestConfirmEquivalenceByID_Success(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	linkID := uuid.New()
	projectID := uuid.New()
	sourceID := uuid.New()
	targetID := uuid.New()
	userID := uuid.New()

	link := &Link{
		ID:           linkID,
		ProjectID:    projectID,
		SourceItemID: sourceID,
		TargetItemID: targetID,
		LinkType:     "same_as",
		Confidence:   0.95,
		Provenance:   StrategyNamingPattern,
		Status:       StatusSuggested,
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}

	require.NoError(t, repo.SaveLink(ctx, link))

	confirmed, err := service.ConfirmEquivalenceByID(ctx, linkID, userID)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if confirmed.Status != StatusConfirmed {
		t.Errorf("expected status %v, got %v", StatusConfirmed, confirmed.Status)
	}

	if confirmed.ConfirmedBy == nil || *confirmed.ConfirmedBy != userID {
		t.Errorf("expected ConfirmedBy %v, got %v", userID, confirmed.ConfirmedBy)
	}
}

// TestRejectEquivalenceByID_Success tests rejecting an equivalence by ID
func TestRejectEquivalenceByID_Success(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	linkID := uuid.New()
	projectID := uuid.New()
	sourceID := uuid.New()
	targetID := uuid.New()
	userID := uuid.New()

	link := &Link{
		ID:           linkID,
		ProjectID:    projectID,
		SourceItemID: sourceID,
		TargetItemID: targetID,
		LinkType:     "same_as",
		Confidence:   0.95,
		Provenance:   StrategyNamingPattern,
		Status:       StatusSuggested,
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}

	require.NoError(t, repo.SaveLink(ctx, link))

	err := service.RejectEquivalenceByID(ctx, linkID, userID)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	// Verify status was updated
	retrieved, err := repo.GetLink(ctx, linkID)
	require.NoError(t, err)
	if retrieved.Status != StatusRejected {
		t.Errorf("expected status %v, got %v", StatusRejected, retrieved.Status)
	}
}

// TestGetCanonicalConcept_Success tests retrieving a canonical concept
func TestGetCanonicalConcept_Success(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	conceptID := uuid.New()
	projectID := uuid.New()
	userID := uuid.New()

	concept := &CanonicalConcept{
		ID:        conceptID,
		ProjectID: projectID,
		Name:      "Test Concept",
		Domain:    "Architecture",
		Category:  "Component",
		Tags:      []string{"tag1", "tag2"},
		CreatedBy: &userID,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		Version:   1,
	}

	require.NoError(t, repo.SaveConcept(ctx, concept))

	retrieved, err := service.GetCanonicalConcept(ctx, conceptID)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if retrieved == nil {
		t.Fatal("expected concept, got nil")
	}

	if retrieved.Name != "Test Concept" {
		t.Errorf("expected Name %q, got %q", "Test Concept", retrieved.Name)
	}
}

// TestGetCanonicalConcept_NotFound tests error when concept doesn't exist
func TestGetCanonicalConcept_NotFound(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	conceptID := uuid.New()

	_, err := service.GetCanonicalConcept(ctx, conceptID)
	if err == nil {
		t.Fatal("expected error, got nil")
	}
}

// TestUpdateCanonicalConcept_Success tests updating a canonical concept
func TestUpdateCanonicalConcept_Success(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	conceptID := uuid.New()
	projectID := uuid.New()
	userID := uuid.New()

	concept := &CanonicalConcept{
		ID:        conceptID,
		ProjectID: projectID,
		Name:      "Original Name",
		Domain:    "Architecture",
		Category:  "Component",
		Tags:      []string{"tag1"},
		CreatedBy: &userID,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		Version:   1,
	}

	require.NoError(t, repo.SaveConcept(ctx, concept))

	updated := &CanonicalConcept{
		ID:        conceptID,
		ProjectID: projectID,
		Name:      "Updated Name",
		Domain:    "Design",
		Category:  "Interface",
		Tags:      []string{"tag1", "tag2"},
		CreatedBy: &userID,
		CreatedAt: concept.CreatedAt,
		UpdatedAt: time.Now(),
		Version:   1,
	}

	result, err := service.UpdateCanonicalConcept(ctx, conceptID, updated)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if result.Name != "Updated Name" {
		t.Errorf("expected Name %q, got %q", "Updated Name", result.Name)
	}

	if result.Version != 2 {
		t.Errorf("expected Version 2, got %d", result.Version)
	}
}

// TestDeleteCanonicalConcept_WithProjections tests deletion error when projections exist
func TestDeleteCanonicalConcept_WithProjections(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	conceptID := uuid.New()
	projectID := uuid.New()
	userID := uuid.New()

	concept := &CanonicalConcept{
		ID:        conceptID,
		ProjectID: projectID,
		Name:      "Test Concept",
		CreatedBy: &userID,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		Version:   1,
	}

	require.NoError(t, repo.SaveConcept(ctx, concept))

	// Add a projection for this concept
	projection := &CanonicalProjection{
		ID:          uuid.New(),
		ProjectID:   projectID,
		CanonicalID: conceptID,
		ItemID:      uuid.New(),
		Perspective: "code",
		Confidence:  0.9,
		Provenance:  StrategyManualLink,
		Status:      StatusConfirmed,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	require.NoError(t, repo.SaveProjection(ctx, projection))

	// Try to delete - should fail because projections exist
	err := service.DeleteCanonicalConcept(ctx, conceptID)
	if err == nil {
		t.Fatal("expected error when deleting concept with projections, got nil")
	}
}

// TestGetConceptProjections_Success tests retrieving projections for a concept
func TestGetConceptProjections_Success(t *testing.T) {
	ctx, service, conceptID := setupConceptProjectionsTest(t)
	projections, err := service.GetConceptProjections(ctx, conceptID)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	assertConceptProjections(t, projections)
}

func setupConceptProjectionsTest(t *testing.T) (context.Context, *serviceImpl, uuid.UUID) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	conceptID := uuid.New()
	projectID := uuid.New()
	userID := uuid.New()

	concept := &CanonicalConcept{
		ID:        conceptID,
		ProjectID: projectID,
		Name:      "Test Concept",
		CreatedBy: &userID,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		Version:   1,
	}
	require.NoError(t, repo.SaveConcept(ctx, concept))

	proj1 := &CanonicalProjection{
		ID:          uuid.New(),
		ProjectID:   projectID,
		CanonicalID: conceptID,
		ItemID:      uuid.New(),
		Perspective: "code",
		Confidence:  0.9,
		Provenance:  StrategyManualLink,
		Status:      StatusConfirmed,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	proj2 := &CanonicalProjection{
		ID:          uuid.New(),
		ProjectID:   projectID,
		CanonicalID: conceptID,
		ItemID:      uuid.New(),
		Perspective: "requirements",
		Confidence:  0.85,
		Provenance:  StrategyManualLink,
		Status:      StatusConfirmed,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	require.NoError(t, repo.SaveProjection(ctx, proj1))
	require.NoError(t, repo.SaveProjection(ctx, proj2))

	return ctx, service, conceptID
}

func assertConceptProjections(t *testing.T, projections []CanonicalProjection) {
	if len(projections) != 2 {
		t.Errorf("expected 2 projections, got %d", len(projections))
	}

	perspectives := make(map[string]bool)
	for _, p := range projections {
		perspectives[p.Perspective] = true
	}

	if !perspectives["code"] || !perspectives["requirements"] {
		t.Errorf("expected code and requirements perspectives, got %v", perspectives)
	}
}

// TestGetConceptProjections_EmptyResult tests retrieving projections when none exist
func TestGetConceptProjections_EmptyResult(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	conceptID := uuid.New()
	projectID := uuid.New()
	userID := uuid.New()

	concept := &CanonicalConcept{
		ID:        conceptID,
		ProjectID: projectID,
		Name:      "Test Concept",
		CreatedBy: &userID,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		Version:   1,
	}

	require.NoError(t, repo.SaveConcept(ctx, concept))

	projections, err := service.GetConceptProjections(ctx, conceptID)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if len(projections) != 0 {
		t.Errorf("expected 0 projections, got %d", len(projections))
	}
}

// TestCreateCanonicalConcept_Success tests creating a new canonical concept
func TestCreateCanonicalConcept_Success(t *testing.T) {
	ctx := context.Background()
	repo := NewMockRepository()
	service := &serviceImpl{repo: repo}

	projectID := uuid.New()
	userID := uuid.New()

	req := &CreateCanonicalConceptRequest{
		ProjectID:   projectID,
		Name:        "New Concept",
		Description: "A test concept",
		Domain:      "Architecture",
		Category:    "Component",
		Tags:        []string{"tag1", "tag2"},
	}

	concept, err := service.CreateCanonicalConcept(ctx, req, userID)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if concept == nil {
		t.Fatal("expected concept, got nil")
	}

	if concept.Name != "New Concept" {
		t.Errorf("expected Name %q, got %q", "New Concept", concept.Name)
	}

	if concept.ProjectID != projectID {
		t.Errorf("expected ProjectID %v, got %v", projectID, concept.ProjectID)
	}

	if *concept.CreatedBy != userID {
		t.Errorf("expected CreatedBy %v, got %v", userID, concept.CreatedBy)
	}
}
