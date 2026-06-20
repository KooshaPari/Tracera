package traceability

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Test service creation
func TestMatrixService_Creation(t *testing.T) {
	cache := newMockCache()
	service := NewMatrixService(nil, cache)

	require.NotNil(t, service)
	assert.NotNil(t, service.cache)
	assert.Equal(t, cache, service.cache)
}

// Test coverage thresholds constants
func TestCoverageThresholds_Constants(t *testing.T) {
	assert.Equal(t, 50, coverageCriticallyLow)
	assert.Equal(t, 80, coverageBelowTarget)
	assert.Equal(t, 2, coverageFullyTraced)
	assert.Equal(t, 100, coveragePercentScale)
}

// Test matrix item trace count variations
func TestMatrixItem_TraceCountVariations(t *testing.T) {
	tests := []int{0, 1, 5, 10, 100}

	for _, count := range tests {
		item := MatrixItem{
			ItemID:     "test",
			Title:      "Test",
			Type:       "requirement",
			TraceCount: count,
		}
		assert.Equal(t, count, item.TraceCount)
	}
}

// Test link bidirectional flag variations
func TestLink_BidirectionalVariations(t *testing.T) {
	tests := []bool{true, false}

	for _, bidir := range tests {
		link := Link{
			SourceID:      "src",
			TargetID:      "tgt",
			LinkType:      "TRACES_TO",
			Bidirectional: bidir,
		}
		assert.Equal(t, bidir, link.Bidirectional)
	}
}

// Test gap with expected links
func TestGap_ExpectedLinks(t *testing.T) {
	expectedLinks := []string{"link-1", "link-2", "link-3"}
	gap := Gap{
		ItemID:        "item-1",
		Title:         "Test Gap",
		Type:          "requirement",
		ExpectedLinks: expectedLinks,
	}

	assert.Equal(t, expectedLinks, gap.ExpectedLinks)
	assert.Len(t, gap.ExpectedLinks, 3)
}

// Test change impact documentation updates
func TestChangeImpact_DocsToUpdate(t *testing.T) {
	docs := []string{"doc1.md", "doc2.md", "doc3.md"}
	impact := ChangeImpact{
		ItemID:       "changed-item",
		DocsToUpdate: docs,
	}

	assert.Equal(t, docs, impact.DocsToUpdate)
	assert.Len(t, impact.DocsToUpdate, 3)
}

// Test validation issue with all fields
func TestValidationIssue_AllFields(t *testing.T) {
	issue := ValidationIssue{
		Severity:   "error",
		ItemID:     "item-1",
		Message:    "Test message",
		Suggestion: "Test suggestion",
	}

	assert.Equal(t, "error", issue.Severity)
	assert.Equal(t, "item-1", issue.ItemID)
	assert.NotEmpty(t, issue.Message)
	assert.NotEmpty(t, issue.Suggestion)
}

// Test item traceability coverage statuses
func TestItemTraceability_CoverageStatuses(t *testing.T) {
	statuses := []struct {
		upstream       []Link
		downstream     []Link
		expectedStatus string
	}{
		{[]Link{}, []Link{}, "none"},
		{[]Link{{SourceID: "s", TargetID: "t"}}, []Link{}, "partial"},
		{[]Link{}, []Link{{SourceID: "s", TargetID: "t"}}, "partial"},
		{[]Link{{SourceID: "s1", TargetID: "t1"}}, []Link{{SourceID: "s2", TargetID: "t2"}}, "full"},
	}

	service := &MatrixService{}

	for _, tc := range statuses {
		result := service.determineCoverageStatus(tc.upstream, tc.downstream)
		assert.Equal(t, tc.expectedStatus, result)
	}
}

// Test error handling in get cached functions
func TestGetCached_ErrorPropagates(t *testing.T) {
	service := &MatrixService{
		db:    nil,
		cache: newMockCache(),
	}

	ctx := context.Background()

	// Test getCachedOrCompute
	result, err := service.getCachedOrCompute(ctx, "key", func() (*Matrix, error) {
		return nil, assert.AnError
	})
	require.Error(t, err)
	assert.Nil(t, result)

	// Test getCachedOrComputeCoverage
	result2, err := service.getCachedOrComputeCoverage(ctx, "key", func() (*CoverageReport, error) {
		return nil, assert.AnError
	})
	require.Error(t, err)
	assert.Nil(t, result2)

	// Test getCachedOrComputeGaps
	result3, err := service.getCachedOrComputeGaps(ctx, "key", func() (*GapAnalysis, error) {
		return nil, assert.AnError
	})
	require.Error(t, err)
	assert.Nil(t, result3)

	// Test getCachedOrComputeValidation
	result4, err := service.getCachedOrComputeValidation(ctx, "key", func() (*ValidationReport, error) {
		return nil, assert.AnError
	})
	require.Error(t, err)
	assert.Nil(t, result4)
}

// Test recommendation generation with empty input
func TestGenerateRecommendations_EmptyInput(t *testing.T) {
	service := &MatrixService{}

	// Empty coverage report
	report := &CoverageReport{
		Overall: &CoverageMetrics{CoveragePercent: 85.0},
		ByType:  map[string]*CoverageMetrics{},
	}
	recs := service.generateCoverageRecommendations(report, nil)
	assert.NotEmpty(t, recs)

	// Empty gap analysis
	analysis := &GapAnalysis{
		MissingForward:  []Gap{},
		MissingBackward: []Gap{},
		Orphaned:        []string{},
	}
	gapRecs := service.generateGapRecommendations(analysis)
	assert.NotEmpty(t, gapRecs)
}

// Test matrix type coverage with many items
func TestCoverageMetrics_LargeDataset(t *testing.T) {
	metrics := &CoverageMetrics{
		TotalRequirements:  1000,
		TracedRequirements: 900,
		CoveragePercent:    90.0,
		UntracedItems:      make([]string, 100),
	}

	assert.Equal(t, 1000, metrics.TotalRequirements)
	assert.Equal(t, 900, metrics.TracedRequirements)
	assert.InEpsilon(t, 90.0, metrics.CoveragePercent, 1e-9)
	assert.Len(t, metrics.UntracedItems, 100)
}

// Test multiple validation issue types
func TestValidationReport_MultipleIssueTypes(t *testing.T) {
	report := &ValidationReport{
		ProjectID: "proj-1",
		Issues: []ValidationIssue{
			{Severity: "error", ItemID: "item-1", Message: "Error message"},
			{Severity: "warning", ItemID: "item-2", Message: "Warning message"},
			{Severity: "info", ItemID: "item-3", Message: "Info message"},
		},
	}

	assert.Len(t, report.Issues, 3)

	// Count by severity
	severityMap := make(map[string]int)
	for _, issue := range report.Issues {
		severityMap[issue.Severity]++
	}

	assert.Equal(t, 1, severityMap["error"])
	assert.Equal(t, 1, severityMap["warning"])
	assert.Equal(t, 1, severityMap["info"])
}

// Test large matrix structure
func TestMatrix_LargeStructure(t *testing.T) {
	matrix := &Matrix{
		ProjectID:    "proj-1",
		Requirements: make([]MatrixItem, 100),
		TestCases:    make([]MatrixItem, 150),
		Links:        make([]Link, 200),
	}

	assert.Len(t, matrix.Requirements, 100)
	assert.Len(t, matrix.TestCases, 150)
	assert.Len(t, matrix.Links, 200)
}

// Test apply matrix coverage with no untraced items
func TestApplyMatrixCoverage_NoUntracedItems(t *testing.T) {
	service := &MatrixService{}
	matrix := &Matrix{}

	service.applyMatrixCoverage(matrix, 50, 50, 100.0, []string{})

	assert.NotNil(t, matrix.Coverage)
	assert.Equal(t, 50, matrix.Coverage.TotalRequirements)
	assert.Equal(t, 50, matrix.Coverage.TracedRequirements)
	assert.InEpsilon(t, 100.0, matrix.Coverage.CoveragePercent, 1e-9)
	assert.Empty(t, matrix.Coverage.UntracedItems)
}

// Test apply matrix coverage with all untraced items
func TestApplyMatrixCoverage_AllUntraced(t *testing.T) {
	service := &MatrixService{}
	matrix := &Matrix{}

	untracedItems := []string{"u1", "u2", "u3", "u4", "u5"}
	service.applyMatrixCoverage(matrix, 5, 0, 0.0, untracedItems)

	assert.Equal(t, 5, matrix.Coverage.TotalRequirements)
	assert.Equal(t, 0, matrix.Coverage.TracedRequirements)
	assert.InDelta(t, 0.0, matrix.Coverage.CoveragePercent, 1e-9)
	assert.Len(t, matrix.Coverage.UntracedItems, 5)
}

// Test finalize report with various configurations
func TestFinalizeValidationReport_Configurations(t *testing.T) {
	service := &MatrixService{}

	configs := []struct {
		name       string
		totalItems int
		failed     int
		issues     int
	}{
		{"minimal", 1, 0, 0},
		{"moderate", 50, 10, 15},
		{"large", 1000, 250, 300},
	}

	for _, cfg := range configs {
		t.Run(cfg.name, func(t *testing.T) {
			report := &ValidationReport{
				Issues: make([]ValidationIssue, cfg.issues),
				Failed: cfg.failed,
			}

			service.finalizeValidationReport(report, cfg.totalItems)

			assert.GreaterOrEqual(t, report.Score, 0.0)
			assert.LessOrEqual(t, report.Score, 100.0)
			assert.Equal(t, cfg.failed == 0, report.IsComplete)
		})
	}
}

// Test coverage report with many types
func TestCoverageReport_ManyTypes(t *testing.T) {
	byType := make(map[string]*CoverageMetrics)
	for i := 0; i < 10; i++ {
		byType[string('a'+rune(i))] = &CoverageMetrics{
			TotalRequirements:  10,
			TracedRequirements: 10 - i,
			CoveragePercent:    float64(100-i*10) / 1.0,
		}
	}

	report := &CoverageReport{
		ProjectID: "proj-1",
		Overall: &CoverageMetrics{
			TotalRequirements:  100,
			TracedRequirements: 85,
			CoveragePercent:    85.0,
		},
		ByType: byType,
	}

	assert.Len(t, report.ByType, 10)
}

// Test change impact with many impacts
func TestChangeImpact_ManyImpacts(t *testing.T) {
	directImpact := make([]string, 50)
	for i := 0; i < 50; i++ {
		directImpact[i] = "direct-" + string(rune(i))
	}

	indirectImpact := make([]string, 30)
	for i := 0; i < 30; i++ {
		indirectImpact[i] = "indirect-" + string(rune(i))
	}

	impact := ChangeImpact{
		ItemID:         "key-change",
		DirectImpact:   directImpact,
		IndirectImpact: indirectImpact,
	}

	assert.Len(t, impact.DirectImpact, 50)
	assert.Len(t, impact.IndirectImpact, 30)
}
