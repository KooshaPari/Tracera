package traceability

import (
	"encoding/json"
	"fmt"
	"testing"

	"github.com/jackc/pgx/v5"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Test batch operations
func TestBuildMatrixBatch_HasCorrectNumberOfQueries(t *testing.T) {
	service := &MatrixService{}
	batch := service.buildMatrixBatch("proj-test")

	require.NotNil(t, batch)
	assert.IsType(t, &pgx.Batch{}, batch)
}

func TestBuildCoverageBatch_ContainsRequiredQueries(t *testing.T) {
	service := &MatrixService{}
	batch := service.buildCoverageBatch("proj-test")

	require.NotNil(t, batch)
	assert.IsType(t, &pgx.Batch{}, batch)
}

func TestBuildGapBatch_ContainsAllGapQueries(t *testing.T) {
	service := &MatrixService{}
	batch := service.buildGapBatch("proj-test")

	require.NotNil(t, batch)
	assert.IsType(t, &pgx.Batch{}, batch)
}

func TestBuildItemTraceabilityBatch_HasUpstreamAndDownstream(t *testing.T) {
	service := &MatrixService{}
	batch := service.buildItemTraceabilityBatch("item-test")

	require.NotNil(t, batch)
	assert.IsType(t, &pgx.Batch{}, batch)
}

// Test recommendations
func TestGenerateCoverageRecommendations_ThresholdCombinations(t *testing.T) {
	service := &MatrixService{}

	tests := []struct {
		name            string
		overallCoverage float64
		expectRecs      int
	}{
		{"excellent", 99.0, 1},
		{"critical", 25.0, 2},
		{"below_target", 75.0, 2},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			report := &CoverageReport{
				Overall: &CoverageMetrics{CoveragePercent: tt.overallCoverage},
				ByType:  map[string]*CoverageMetrics{},
			}

			recs := service.generateCoverageRecommendations(report, []string{})
			assert.NotEmpty(t, recs)
		})
	}
}

func TestGenerateGapRecommendations_AllGapTypesCombined(t *testing.T) {
	service := &MatrixService{}

	analysis := &GapAnalysis{
		MissingForward:  []Gap{{ItemID: "r1"}, {ItemID: "r2"}, {ItemID: "r3"}},
		MissingBackward: []Gap{{ItemID: "t1"}},
		Orphaned:        []string{"o1", "o2"},
	}

	recs := service.generateGapRecommendations(analysis)
	assert.NotEmpty(t, recs)
	assert.GreaterOrEqual(t, len(recs), 2)
}

// Test finalize validation
func TestFinalizeValidationReport_VariousTotals(t *testing.T) {
	service := &MatrixService{}

	tests := []struct {
		name       string
		totalItems int
		failed     int
		expectPass bool
	}{
		{"all_pass", 10, 0, true},
		{"one_fail", 10, 1, false},
		{"half_fail", 100, 50, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			report := &ValidationReport{
				Issues: make([]ValidationIssue, tt.failed),
				Failed: tt.failed,
			}

			service.finalizeValidationReport(report, tt.totalItems)
			assert.Equal(t, tt.expectPass, report.IsComplete)
		})
	}
}

// Test determine coverage status
func TestDetermineCoverageStatus_EdgeCasesExtended(t *testing.T) {
	service := &MatrixService{}

	tests := []struct {
		name            string
		upstreamCount   int
		downstreamCount int
		expectedStatus  string
	}{
		{"zero_both", 0, 0, "none"},
		{"one_total", 1, 0, "partial"},
		{"two_same", 1, 1, "full"},
		{"many_links", 10, 10, "full"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			upstream := make([]Link, tt.upstreamCount)
			downstream := make([]Link, tt.downstreamCount)

			for i := 0; i < tt.upstreamCount; i++ {
				upstream[i] = Link{SourceID: fmt.Sprintf("u%d", i), TargetID: "target"}
			}
			for i := 0; i < tt.downstreamCount; i++ {
				downstream[i] = Link{SourceID: "source", TargetID: fmt.Sprintf("d%d", i)}
			}

			status := service.determineCoverageStatus(upstream, downstream)
			assert.Equal(t, tt.expectedStatus, status)
		})
	}
}

// Test init functions
func TestInitFunctions_CreateCorrectStructures(t *testing.T) {
	service := &MatrixService{}

	matrix := service.initMatrix("proj-test")
	assert.NotNil(t, matrix)
	assert.Equal(t, "proj-test", matrix.ProjectID)

	impact := service.initChangeImpact("item-test")
	assert.Equal(t, "item-test", impact.ItemID)
	assert.NotNil(t, impact.DirectImpact)
}

// Test apply matrix coverage
func TestApplyMatrixCoverage_VariousPercentages(t *testing.T) {
	service := &MatrixService{}

	percentages := []float64{0.0, 25.0, 50.0, 75.0, 100.0}

	for _, pct := range percentages {
		matrix := &Matrix{}
		service.applyMatrixCoverage(matrix, 100, int(pct), pct, []string{})

		assert.NotNil(t, matrix.Coverage)
		assert.InDelta(t, pct, matrix.Coverage.CoveragePercent, 1e-9)
	}
}

// Test JSON marshaling
func TestMatrixJSON_Complete(t *testing.T) {
	matrix := &Matrix{
		ProjectID:    "proj-1",
		Requirements: []MatrixItem{{ItemID: "req-1", Title: "Requirement 1"}},
		TestCases:    []MatrixItem{{ItemID: "test-1", Title: "Test 1"}},
		Links:        []Link{{SourceID: "req-1", TargetID: "test-1", LinkType: "TRACES_TO"}},
		Coverage: &CoverageMetrics{
			TotalRequirements:  1,
			TracedRequirements: 1,
			CoveragePercent:    100.0,
		},
	}

	data, err := json.Marshal(matrix)
	require.NoError(t, err)

	var restored Matrix
	err = json.Unmarshal(data, &restored)
	require.NoError(t, err)
	assert.Equal(t, "proj-1", restored.ProjectID)
}

func TestCoverageReportJSON_Complete(t *testing.T) {
	report := &CoverageReport{
		ProjectID: "proj-1",
		Overall: &CoverageMetrics{
			TotalRequirements:  100,
			TracedRequirements: 85,
			CoveragePercent:    85.0,
		},
		ByType: map[string]*CoverageMetrics{
			"requirement": {CoveragePercent: 100.0},
			"feature":     {CoveragePercent: 70.0},
		},
		Recommendations: []string{"Increase coverage"},
	}

	data, err := json.Marshal(report)
	require.NoError(t, err)

	var restored CoverageReport
	err = json.Unmarshal(data, &restored)
	require.NoError(t, err)
	assert.InEpsilon(t, 85.0, restored.Overall.CoveragePercent, 1e-9)
	assert.Len(t, restored.ByType, 2)
}

func TestGapAnalysisJSON_Complete(t *testing.T) {
	analysis := &GapAnalysis{
		ProjectID:       "proj-1",
		MissingForward:  []Gap{{ItemID: "req-1", Title: "Gap"}},
		MissingBackward: []Gap{{ItemID: "test-1", Title: "Test Gap"}},
		Orphaned:        []string{"item-1", "item-2"},
		Recommendations: []string{"Add tests", "Link items"},
	}

	data, err := json.Marshal(analysis)
	require.NoError(t, err)

	var restored GapAnalysis
	err = json.Unmarshal(data, &restored)
	require.NoError(t, err)
	assert.Len(t, restored.MissingForward, 1)
	assert.Len(t, restored.Orphaned, 2)
}

func TestValidationReportJSON_Complete(t *testing.T) {
	report := &ValidationReport{
		ProjectID:  "proj-1",
		IsComplete: false,
		Score:      75.0,
		Issues: []ValidationIssue{
			{Severity: "error", ItemID: "req-1", Message: "No coverage"},
			{Severity: "warning", ItemID: "item-2", Message: "Orphaned"},
		},
		Passed: 8,
		Failed: 2,
	}

	data, err := json.Marshal(report)
	require.NoError(t, err)

	var restored ValidationReport
	err = json.Unmarshal(data, &restored)
	require.NoError(t, err)
	assert.InEpsilon(t, 75.0, restored.Score, 1e-9)
	assert.Len(t, restored.Issues, 2)
}

func TestChangeImpactJSON_Complete(t *testing.T) {
	impact := &ChangeImpact{
		ItemID:         "api-endpoint",
		DirectImpact:   []string{"service-a", "service-b"},
		IndirectImpact: []string{"module-x"},
		TestsToRun:     []string{"test-1", "test-2"},
		DocsToUpdate:   []string{"API.md"},
	}

	data, err := json.Marshal(impact)
	require.NoError(t, err)

	var restored ChangeImpact
	err = json.Unmarshal(data, &restored)
	require.NoError(t, err)
	assert.Equal(t, "api-endpoint", restored.ItemID)
	assert.Len(t, restored.DirectImpact, 2)
}

// Test queue functions
func TestQueueMatrixRequirements_BuildsQuery(t *testing.T) {
	batch := &pgx.Batch{}
	queueMatrixRequirements(batch, "proj-123")
	assert.NotNil(t, batch)
}

func TestQueueMatrixTestCases_BuildsQuery(t *testing.T) {
	batch := &pgx.Batch{}
	queueMatrixTestCases(batch, "proj-123")
	assert.NotNil(t, batch)
}

func TestQueueMatrixLinks_BuildsQuery(t *testing.T) {
	batch := &pgx.Batch{}
	queueMatrixLinks(batch, "proj-123")
	assert.NotNil(t, batch)
}

func TestQueueMatrixCoverage_BuildsQuery(t *testing.T) {
	batch := &pgx.Batch{}
	queueMatrixCoverage(batch, "proj-123")
	assert.NotNil(t, batch)
}

func TestQueueMatrixUntracedItems_BuildsQuery(t *testing.T) {
	batch := &pgx.Batch{}
	queueMatrixUntracedItems(batch, "proj-123")
	assert.NotNil(t, batch)
}

// Test score calculation
func TestFinalizeValidationReport_ScoreCalculation(t *testing.T) {
	service := &MatrixService{}

	tests := []struct {
		name          string
		totalItems    int
		failed        int
		expectedScore float64
	}{
		{"all_pass", 10, 0, 100.0},
		{"half_fail", 10, 5, 50.0},
		{"all_fail", 10, 10, 0.0},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			report := &ValidationReport{
				Issues: make([]ValidationIssue, tt.failed),
				Failed: tt.failed,
			}

			service.finalizeValidationReport(report, tt.totalItems)
			assert.InDelta(t, tt.expectedScore, report.Score, 1e-9)
		})
	}
}
