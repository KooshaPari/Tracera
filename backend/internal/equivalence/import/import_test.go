package importer

import (
	"bytes"
	"encoding/json"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/equivalence"
	"github.com/kooshapari/tracertm-backend/internal/equivalence/export"
)

func TestValidatorBasicValidation(t *testing.T) {
	validator := NewValidator()

	projectID := uuid.New()
	conceptID := uuid.New()

	data := &export.Data{
		Version:    "1.0.0",
		ExportedAt: time.Now(),
		ProjectID:  projectID,
		CanonicalConcepts: []export.CanonicalConcept{
			{
				ID:         conceptID,
				ProjectID:  projectID,
				Name:       "TestConcept",
				Slug:       "test-concept",
				Confidence: 0.95,
				Source:     "explicit_annotation",
				CreatedAt:  time.Now(),
			},
		},
	}

	errors := validator.ValidateExportData(data)
	assert.Empty(t, errors)
}

func TestValidatorMissingVersion(t *testing.T) {
	validator := NewValidator()
	projectID := uuid.New()

	data := &export.Data{
		Version:    "",
		ExportedAt: time.Now(),
		ProjectID:  projectID,
	}

	errors := validator.ValidateExportData(data)
	require.NotEmpty(t, errors)
	assert.Equal(t, "version", errors[0].Field)
}

func TestValidatorInvalidConfidence(t *testing.T) {
	validator := NewValidator()

	projectID := uuid.New()
	conceptID := uuid.New()

	data := &export.Data{
		Version:    "1.0.0",
		ExportedAt: time.Now(),
		ProjectID:  projectID,
		CanonicalConcepts: []export.CanonicalConcept{
			{
				ID:         conceptID,
				ProjectID:  projectID,
				Name:       "TestConcept",
				Slug:       "test-concept",
				Confidence: 1.5, // Invalid
				Source:     "explicit_annotation",
				CreatedAt:  time.Now(),
			},
		},
	}

	errors := validator.ValidateExportData(data)
	require.NotEmpty(t, errors)
	assert.Equal(t, "confidence", errors[0].Field)
}

func TestValidatorReferentialIntegrity(t *testing.T) {
	validator := NewValidator()

	projectID := uuid.New()
	conceptID := uuid.New()
	nonExistentID := uuid.New()

	data := &export.Data{
		Version:    "1.0.0",
		ExportedAt: time.Now(),
		ProjectID:  projectID,
		CanonicalConcepts: []export.CanonicalConcept{
			{
				ID:         conceptID,
				ProjectID:  projectID,
				Name:       "TestConcept",
				Slug:       "test-concept",
				Confidence: 0.95,
				Source:     "explicit_annotation",
				CreatedAt:  time.Now(),
			},
		},
		Projections: []export.CanonicalProjection{
			{
				ID:          uuid.New(),
				ProjectID:   projectID,
				CanonicalID: nonExistentID, // Non-existent
				ItemID:      uuid.New(),
				Perspective: "code",
				Confidence:  0.9,
				Provenance:  "api_contract",
				Status:      "confirmed",
				CreatedAt:   time.Now(),
			},
		},
	}

	errors := validator.ValidateExportData(data)
	require.NotEmpty(t, errors)
	assert.NotEmpty(t, errors)
}

func TestJSONImporterParse(t *testing.T) {
	projectID := uuid.New()
	conceptID := uuid.New()

	exportData := &export.Data{
		Version:    "1.0.0",
		ExportedAt: time.Now(),
		ProjectID:  projectID,
		CanonicalConcepts: []export.CanonicalConcept{
			{
				ID:         conceptID,
				ProjectID:  projectID,
				Name:       "Test",
				Slug:       "test",
				Confidence: 0.9,
				Source:     "explicit_annotation",
				CreatedAt:  time.Now(),
			},
		},
	}

	data, err := json.Marshal(exportData)
	require.NoError(t, err)

	validator := NewValidator()
	resolver := NewConflictResolver(ResolutionSkip)
	importer := NewJSONImporter(validator, resolver)

	parsed, err := importer.ParseJSON(bytes.NewReader(data))
	require.NoError(t, err)
	assert.Equal(t, projectID, parsed.ProjectID)
	assert.Len(t, parsed.CanonicalConcepts, 1)
}

func TestJSONImporterValidation(t *testing.T) {
	projectID := uuid.New()
	conceptID := uuid.New()

	exportData := &export.Data{
		Version:    "1.0.0",
		ExportedAt: time.Now(),
		ProjectID:  projectID,
		CanonicalConcepts: []export.CanonicalConcept{
			{
				ID:         conceptID,
				ProjectID:  projectID,
				Name:       "Test",
				Slug:       "test",
				Confidence: 0.9,
				Source:     "explicit_annotation",
				CreatedAt:  time.Now(),
			},
		},
	}

	data, err := json.Marshal(exportData)
	require.NoError(t, err)

	validator := NewValidator()
	resolver := NewConflictResolver(ResolutionSkip)
	importer := NewJSONImporter(validator, resolver)

	result, err := importer.Import(bytes.NewReader(data))
	require.NoError(t, err)
	assert.True(t, result.Valid)
	assert.Empty(t, result.Errors)
}

func TestYAMLImporterParse(t *testing.T) {
	projectID := uuid.New()
	conceptID := uuid.New()

	yaml := `
version: "1.0.0"
exportedAt: 2024-01-01T00:00:00Z
projectId: ` + projectID.String() + `
canonicalConcepts:
  - id: ` + conceptID.String() + `
    projectId: ` + projectID.String() + `
    name: TestConcept
    slug: test-concept
    confidence: 0.95
    source: explicit_annotation
    createdAt: 2024-01-01T00:00:00Z
    version: 1
`

	validator := NewValidator()
	resolver := NewConflictResolver(ResolutionSkip)
	importer := NewYAMLImporter(validator, resolver)

	parsed, err := importer.ParseYAML(bytes.NewReader([]byte(yaml)))
	require.NoError(t, err)
	assert.Equal(t, projectID, parsed.ProjectID)
}

func TestConflictResolverDetection(t *testing.T) {
	projectID := uuid.New()
	conceptID := uuid.New()

	resolver := NewConflictResolver(ResolutionSkip)

	existing := []equivalence.CanonicalConcept{
		{
			ID:         conceptID,
			ProjectID:  projectID,
			Name:       "ExistingName",
			Slug:       "existing",
			Confidence: 0.95,
			Source:     equivalence.StrategyExplicitAnnotation,
			CreatedAt:  time.Now(),
			Version:    1,
		},
	}

	resolver.LoadExisting(existing, nil)

	importData := &export.Data{
		Version:    "1.0.0",
		ExportedAt: time.Now(),
		ProjectID:  projectID,
		CanonicalConcepts: []export.CanonicalConcept{
			{
				ID:         conceptID,
				ProjectID:  projectID,
				Name:       "DifferentName",
				Slug:       "existing",
				Confidence: 0.95,
				Source:     "explicit_annotation",
				CreatedAt:  time.Now(),
			},
		},
	}

	conflicts := resolver.DetectConflicts(importData)
	require.NotEmpty(t, conflicts)
	assert.Equal(t, ConflictConflictingData, conflicts[0].Type)
}

func TestConflictResolverReplace(t *testing.T) {
	projectID := uuid.New()
	conceptID := uuid.New()

	resolver := NewConflictResolver(ResolutionReplace)

	conflict := Conflict{
		Type:        ConflictConflictingData,
		Severity:    "warning",
		ItemID:      conceptID,
		ItemType:    "concept",
		Field:       "name",
		ExistingVal: "Old",
		ImportedVal: "New",
		Resolution:  ResolutionReplace,
	}

	importData := &export.Data{
		Version:    "1.0.0",
		ExportedAt: time.Now(),
		ProjectID:  projectID,
		CanonicalConcepts: []export.CanonicalConcept{
			{
				ID:        conceptID,
				ProjectID: projectID,
				Name:      "New",
				Slug:      "new",
				Source:    "explicit_annotation",
				CreatedAt: time.Now(),
			},
		},
	}

	resolved, unresolved, err := resolver.ResolveConflicts([]Conflict{conflict}, importData)
	require.NoError(t, err)
	assert.NotNil(t, resolved)
	assert.Len(t, unresolved, 1)
}

func TestImportResultValidation(t *testing.T) {
	projectID := uuid.New()
	conceptID := uuid.New()

	// Valid data
	data := &export.Data{
		Version:    "1.0.0",
		ExportedAt: time.Now(),
		ProjectID:  projectID,
		CanonicalConcepts: []export.CanonicalConcept{
			{
				ID:         conceptID,
				ProjectID:  projectID,
				Name:       "Test",
				Slug:       "test",
				Confidence: 0.9,
				Source:     "explicit_annotation",
				CreatedAt:  time.Now(),
			},
		},
	}

	jsonBytes, err := json.Marshal(data)
	require.NoError(t, err)

	validator := NewValidator()
	resolver := NewConflictResolver(ResolutionSkip)
	importer := NewJSONImporter(validator, resolver)

	result, err := importer.Import(bytes.NewReader(jsonBytes))
	require.NoError(t, err)

	assert.True(t, result.Valid)
	assert.NotNil(t, result.Data)
}

func TestConflictSummary(t *testing.T) {
	conflicts := []Conflict{
		{Type: ConflictConceptExists, Severity: "error"},
		{Type: ConflictConflictingData, Severity: "warning"},
		{Type: ConflictLinkExists, Severity: "info"},
	}

	summary := SummarizeConflicts(conflicts)
	assert.NotEmpty(t, summary)
	assert.Contains(t, summary, "1 errors")
	assert.Contains(t, summary, "1 warnings")
}

func TestValidatorNilData(t *testing.T) {
	validator := NewValidator()
	errors := validator.ValidateExportData(nil)
	require.NotEmpty(t, errors)
}

func TestValidatorMissingRequiredFields(t *testing.T) {
	validator := NewValidator()

	data := &export.Data{
		Version:    "1.0.0",
		ExportedAt: time.Now(),
		ProjectID:  uuid.Nil, // Missing
	}

	errors := validator.ValidateExportData(data)
	require.NotEmpty(t, errors)
	assert.Equal(t, "project_id", errors[0].Field)
}

func TestValidatorConceptHierarchy(t *testing.T) {
	validator := NewValidator()

	projectID := uuid.New()
	parentID := uuid.New()
	childID := uuid.New()

	data := &export.Data{
		Version:    "1.0.0",
		ExportedAt: time.Now(),
		ProjectID:  projectID,
		CanonicalConcepts: []export.CanonicalConcept{
			{
				ID:        parentID,
				ProjectID: projectID,
				Name:      "Parent",
				Slug:      "parent",
				Source:    "explicit_annotation",
				CreatedAt: time.Now(),
			},
			{
				ID:              childID,
				ProjectID:       projectID,
				Name:            "Child",
				Slug:            "child",
				ParentConceptID: &parentID,
				Source:          "explicit_annotation",
				CreatedAt:       time.Now(),
			},
		},
	}

	errors := validator.ValidateExportData(data)
	assert.Empty(t, errors)
}

func TestRoundTripExportImport(t *testing.T) {
	// Export
	projectID := uuid.New()
	conceptID := uuid.New()

	originalConcepts := []equivalence.CanonicalConcept{
		{
			ID:          conceptID,
			ProjectID:   projectID,
			Name:        "TestConcept",
			Slug:        "test-concept",
			Description: "A test concept",
			Confidence:  0.95,
			Source:      equivalence.StrategyExplicitAnnotation,
			CreatedAt:   time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC),
			UpdatedAt:   time.Date(2024, 1, 2, 0, 0, 0, 0, time.UTC),
			Version:     1,
		},
	}

	var exportBuf bytes.Buffer
	exporter := export.NewJSONExporter()
	err := exporter.Export(&exportBuf, originalConcepts, nil, nil, projectID, "TestProject")
	require.NoError(t, err)

	// Import
	validator := NewValidator()
	resolver := NewConflictResolver(ResolutionSkip)
	importer := NewJSONImporter(validator, resolver)

	result, err := importer.Import(bytes.NewReader(exportBuf.Bytes()))
	require.NoError(t, err)
	assert.True(t, result.Valid)

	// Verify data integrity
	assert.Len(t, result.Data.CanonicalConcepts, 1)
	imported := result.Data.CanonicalConcepts[0]
	assert.Equal(t, originalConcepts[0].Name, imported.Name)
	assert.Equal(t, originalConcepts[0].Slug, imported.Slug)
	assert.InEpsilon(t, originalConcepts[0].Confidence, imported.Confidence, 1e-9)
}
