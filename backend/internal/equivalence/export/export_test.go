package export

import (
	"bytes"
	"encoding/json"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/equivalence"
)

func TestJSONExporterBasic(t *testing.T) {
	exporter := NewJSONExporter(WithPrettyPrint(true))

	projectID := uuid.New()
	conceptID := uuid.New()

	concepts := []equivalence.CanonicalConcept{
		{
			ID:         conceptID,
			ProjectID:  projectID,
			Name:       "UserAuthentication",
			Slug:       "user-authentication",
			Domain:     "security",
			Category:   "auth",
			Tags:       []string{"critical", "auth"},
			Confidence: 0.95,
			Source:     equivalence.StrategyExplicitAnnotation,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
			Version:    1,
		},
	}

	var buf bytes.Buffer
	err := exporter.Export(&buf, concepts, nil, nil, projectID, "TestProject")
	require.NoError(t, err)

	// Parse and verify
	var data Data
	err = json.Unmarshal(buf.Bytes(), &data)
	require.NoError(t, err)

	assert.Equal(t, FormatVersion, data.Version)
	assert.Equal(t, projectID, data.ProjectID)
	assert.Len(t, data.CanonicalConcepts, 1)
	assert.Equal(t, "UserAuthentication", data.CanonicalConcepts[0].Name)
	assert.Equal(t, 1, data.Statistics.CanonicalConceptCount)
}

func TestJSONExporterEmbeddings(t *testing.T) {
	for _, tc := range jsonEmbeddingCases() {
		t.Run(tc.name, func(t *testing.T) {
			data := exportConceptEmbeddings(t, tc.includeEmbeddings)
			assertEmbeddingExpectation(t, data, tc.expectEmbedding, tc.expectEmbeddingName)
		})
	}
}

func TestYAMLExporterBasic(t *testing.T) {
	exporter := NewYAMLExporter()

	projectID := uuid.New()
	conceptID := uuid.New()

	concepts := []equivalence.CanonicalConcept{
		{
			ID:         conceptID,
			ProjectID:  projectID,
			Name:       "UserAuthentication",
			Slug:       "user-authentication",
			Domain:     "security",
			Confidence: 0.95,
			Source:     equivalence.StrategyExplicitAnnotation,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
			Version:    1,
		},
	}

	var buf bytes.Buffer
	err := exporter.Export(&buf, concepts, nil, nil, projectID, "TestProject")
	require.NoError(t, err)

	// Verify YAML structure
	content := buf.String()
	assert.Contains(t, content, "version:")
	assert.Contains(t, content, "projectId:")
	assert.Contains(t, content, "UserAuthentication")
}

func TestExportWithCompleteData(t *testing.T) {
	data := exportCompleteData(t)
	assertCompleteDataStats(t, data)
}

type jsonEmbeddingCase struct {
	name                string
	includeEmbeddings   bool
	expectEmbedding     bool
	expectEmbeddingName string
}

func jsonEmbeddingCases() []jsonEmbeddingCase {
	return []jsonEmbeddingCase{
		{
			name:                "with embeddings",
			includeEmbeddings:   true,
			expectEmbedding:     true,
			expectEmbeddingName: "text-embedding-3-small",
		},
		{
			name:                "without embeddings",
			includeEmbeddings:   false,
			expectEmbedding:     false,
			expectEmbeddingName: "",
		},
	}
}

func exportConceptEmbeddings(t *testing.T, includeEmbeddings bool) Data {
	t.Helper()
	exporter := NewJSONExporter(
		WithEmbeddings(includeEmbeddings),
		WithPrettyPrint(true),
	)

	projectID := uuid.New()
	conceptID := uuid.New()

	concepts := []equivalence.CanonicalConcept{
		{
			ID:             conceptID,
			ProjectID:      projectID,
			Name:           "UserAuth",
			Slug:           "user-auth",
			Embedding:      []float32{0.1, 0.2, 0.3},
			EmbeddingModel: "text-embedding-3-small",
			Confidence:     0.9,
			Source:         equivalence.StrategySemanticSimilarity,
			CreatedAt:      time.Now(),
			UpdatedAt:      time.Now(),
			Version:        1,
		},
	}

	var buf bytes.Buffer
	err := exporter.Export(&buf, concepts, nil, nil, projectID, "TestProject")
	require.NoError(t, err)

	var data Data
	err = json.Unmarshal(buf.Bytes(), &data)
	require.NoError(t, err)
	return data
}

func assertEmbeddingExpectation(t *testing.T, data Data, expectEmbedding bool, expectEmbeddingName string) {
	t.Helper()
	if expectEmbedding {
		assert.NotNil(t, data.CanonicalConcepts[0].Embedding)
	} else {
		assert.Nil(t, data.CanonicalConcepts[0].Embedding)
	}
	assert.Equal(t, expectEmbeddingName, data.CanonicalConcepts[0].EmbeddingModel)
}

func exportCompleteData(t *testing.T) Data {
	t.Helper()
	exporter := NewJSONExporter(WithPrettyPrint(true))

	projectID := uuid.New()
	conceptID := uuid.New()
	itemID1 := uuid.New()
	itemID2 := uuid.New()
	linkID := uuid.New()

	concepts := buildCompleteConcepts(projectID, conceptID)
	projections := buildCompleteProjections(projectID, conceptID, itemID1)
	links := buildCompleteLinks(projectID, conceptID, itemID1, itemID2, linkID)

	var buf bytes.Buffer
	err := exporter.Export(&buf, concepts, projections, links, projectID, "TestProject")
	require.NoError(t, err)

	var data Data
	err = json.Unmarshal(buf.Bytes(), &data)
	require.NoError(t, err)
	return data
}

func buildCompleteConcepts(projectID uuid.UUID, conceptID uuid.UUID) []equivalence.CanonicalConcept {
	return []equivalence.CanonicalConcept{
		{
			ID:         conceptID,
			ProjectID:  projectID,
			Name:       "UserAuth",
			Slug:       "user-auth",
			Confidence: 0.95,
			Source:     equivalence.StrategyExplicitAnnotation,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
			Version:    1,
		},
	}
}

func buildCompleteProjections(projectID uuid.UUID, conceptID uuid.UUID, itemID uuid.UUID) []equivalence.CanonicalProjection {
	return []equivalence.CanonicalProjection{
		{
			ID:          uuid.New(),
			ProjectID:   projectID,
			CanonicalID: conceptID,
			ItemID:      itemID,
			Perspective: "code",
			Confidence:  0.9,
			Provenance:  equivalence.StrategyAPIContract,
			Status:      equivalence.StatusConfirmed,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		},
	}
}

func buildCompleteLinks(
	projectID uuid.UUID,
	conceptID uuid.UUID,
	itemID1 uuid.UUID,
	itemID2 uuid.UUID,
	linkID uuid.UUID,
) []equivalence.Link {
	return []equivalence.Link{
		{
			ID:           linkID,
			ProjectID:    projectID,
			SourceItemID: itemID1,
			TargetItemID: itemID2,
			CanonicalID:  &conceptID,
			LinkType:     "same_as",
			Confidence:   0.92,
			Provenance:   equivalence.StrategyNamingPattern,
			Status:       equivalence.StatusConfirmed,
			Evidence: []equivalence.Evidence{
				{
					Strategy:    equivalence.StrategyNamingPattern,
					Confidence:  0.92,
					Description: "Naming pattern match",
					DetectedAt:  time.Now(),
				},
			},
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		},
	}
}

func assertCompleteDataStats(t *testing.T, data Data) {
	t.Helper()
	assert.Equal(t, 1, data.Statistics.CanonicalConceptCount)
	assert.Equal(t, 1, data.Statistics.ProjectionCount)
	assert.Equal(t, 1, data.Statistics.EquivalenceLinkCount)
	assert.Equal(t, 1, data.Statistics.ConfirmedCount)
	assert.Equal(t, 1, data.Statistics.PerspectiveCount)
	assert.NotNil(t, data.Statistics.StrategyBreakdown)
}

func TestStatisticsCalculation(t *testing.T) {
	projectID := uuid.New()
	conceptID := uuid.New()

	concepts := []equivalence.CanonicalConcept{
		{
			ID:        conceptID,
			ProjectID: projectID,
			Name:      "Test1",
			Slug:      "test-1",
			Domain:    "security",
			Source:    equivalence.StrategyExplicitAnnotation,
			CreatedAt: time.Now(),
			Version:   1,
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Name:      "Test2",
			Slug:      "test-2",
			Domain:    "performance",
			Source:    equivalence.StrategySemanticSimilarity,
			CreatedAt: time.Now(),
			Version:   1,
		},
	}

	links := []equivalence.Link{
		{
			ID:           uuid.New(),
			ProjectID:    projectID,
			SourceItemID: uuid.New(),
			TargetItemID: uuid.New(),
			LinkType:     "same_as",
			Confidence:   1.0,
			Provenance:   equivalence.StrategyManualLink,
			Status:       equivalence.StatusConfirmed,
			CreatedAt:    time.Now(),
		},
		{
			ID:           uuid.New(),
			ProjectID:    projectID,
			SourceItemID: uuid.New(),
			TargetItemID: uuid.New(),
			LinkType:     "represents",
			Confidence:   0.8,
			Provenance:   equivalence.StrategyNamingPattern,
			Status:       equivalence.StatusSuggested,
			CreatedAt:    time.Now(),
		},
	}

	stats := calculateStatistics(concepts, nil, links)

	assert.Equal(t, 2, stats.CanonicalConceptCount)
	assert.Equal(t, 2, stats.EquivalenceLinkCount)
	assert.Equal(t, 1, stats.ConfirmedCount)
	assert.Equal(t, 1, stats.SuggestedCount)
	assert.Greater(t, stats.AverageConfidence, 0.0)
	assert.Equal(t, 1, stats.DomainBreakdown["security"])
	assert.Equal(t, 1, stats.DomainBreakdown["performance"])
}

func TestExportEmptyData(t *testing.T) {
	exporter := NewJSONExporter()
	projectID := uuid.New()

	var buf bytes.Buffer
	err := exporter.Export(&buf, nil, nil, nil, projectID, "TestProject")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "no data to export")
}

func TestExportRoundTrip(t *testing.T) {
	exporter := NewJSONExporter(WithPrettyPrint(true))

	projectID := uuid.New()
	conceptID := uuid.New()

	originalConcepts := []equivalence.CanonicalConcept{
		{
			ID:          conceptID,
			ProjectID:   projectID,
			Name:        "TestConcept",
			Slug:        "test-concept",
			Description: "A test concept",
			Domain:      "testing",
			Category:    "example",
			Tags:        []string{"test", "example"},
			Confidence:  0.95,
			Source:      equivalence.StrategyExplicitAnnotation,
			CreatedAt:   time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC),
			UpdatedAt:   time.Date(2024, 1, 2, 0, 0, 0, 0, time.UTC),
			Version:     1,
		},
	}

	var buf bytes.Buffer
	err := exporter.Export(&buf, originalConcepts, nil, nil, projectID, "TestProject")
	require.NoError(t, err)

	var data Data
	err = json.Unmarshal(buf.Bytes(), &data)
	require.NoError(t, err)

	assert.Equal(t, originalConcepts[0].Name, data.CanonicalConcepts[0].Name)
	assert.Equal(t, originalConcepts[0].Slug, data.CanonicalConcepts[0].Slug)
	assert.Equal(t, originalConcepts[0].Description, data.CanonicalConcepts[0].Description)
	assert.InEpsilon(t, originalConcepts[0].Confidence, data.CanonicalConcepts[0].Confidence, 1e-9)
}
