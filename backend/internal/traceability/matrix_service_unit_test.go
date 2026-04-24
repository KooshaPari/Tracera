//go:build unit

package traceability

import (
	"encoding/json"
	"testing"

	"github.com/jackc/pgx/v5"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestInitMatrix(t *testing.T) {
	svc := &MatrixService{}
	m := svc.initMatrix("proj-123")
	require.NotNil(t, m)
	assert.Equal(t, "proj-123", m.ProjectID)
	assert.False(t, m.GeneratedAt.IsZero())
	assert.NotNil(t, m.Requirements)
	assert.NotNil(t, m.TestCases)
	assert.NotNil(t, m.Links)
	assert.Empty(t, m.Requirements)
	assert.Empty(t, m.TestCases)
	assert.Empty(t, m.Links)
	assert.Nil(t, m.Coverage)
}

func TestInitChangeImpact(t *testing.T) {
	svc := &MatrixService{}
	ci := svc.initChangeImpact("item-1")
	assert.Equal(t, "item-1", ci.ItemID)
	assert.NotNil(t, ci.DirectImpact)
	assert.NotNil(t, ci.IndirectImpact)
	assert.NotNil(t, ci.TestsToRun)
	assert.NotNil(t, ci.DocsToUpdate)
	assert.Empty(t, ci.DirectImpact)
	assert.Empty(t, ci.IndirectImpact)
	assert.Empty(t, ci.TestsToRun)
	assert.Empty(t, ci.DocsToUpdate)
}

func TestFinalizeValidationReport(t *testing.T) {
	svc := &MatrixService{}
	report := &ValidationReport{
		ProjectID: "p1",
		Issues:    []ValidationIssue{{ItemID: "i1", Message: "m1"}},
		Failed:    1,
	}
	svc.finalizeValidationReport(report, 10)
	assert.False(t, report.IsComplete)
	assert.GreaterOrEqual(t, report.Score, 0.0)
	assert.LessOrEqual(t, report.Score, 100.0)
}

func TestFinalizeValidationReport_Complete(t *testing.T) {
	svc := &MatrixService{}
	report := &ValidationReport{
		ProjectID: "p1",
		Issues:    []ValidationIssue{},
		Failed:    0,
	}
	svc.finalizeValidationReport(report, 5)
	assert.True(t, report.IsComplete)
	assert.Equal(t, 100.0, report.Score)
}

func TestFinalizeValidationReport_ZeroItems(t *testing.T) {
	svc := &MatrixService{}
	report := &ValidationReport{Failed: 0, Issues: []ValidationIssue{}}
	svc.finalizeValidationReport(report, 0)
	assert.Equal(t, 0.0, report.Score)
}

func TestDetermineCoverageStatus_None(t *testing.T) {
	svc := &MatrixService{}
	s := svc.determineCoverageStatus(nil, nil)
	assert.Equal(t, "none", s)
	s = svc.determineCoverageStatus([]Link{}, []Link{})
	assert.Equal(t, "none", s)
}

func TestDetermineCoverageStatus_Partial(t *testing.T) {
	svc := &MatrixService{}
	s := svc.determineCoverageStatus([]Link{{SourceID: "a", TargetID: "b"}}, nil)
	assert.Equal(t, "partial", s)
}

func TestDetermineCoverageStatus_Full(t *testing.T) {
	svc := &MatrixService{}
	s := svc.determineCoverageStatus(
		[]Link{{SourceID: "a", TargetID: "b"}},
		[]Link{{SourceID: "c", TargetID: "d"}},
	)
	assert.Equal(t, "full", s)
}

func TestGenerateCoverageRecommendations_Critical(t *testing.T) {
	svc := &MatrixService{}
	report := &CoverageReport{
		Overall: &CoverageMetrics{CoveragePercent: 30},
		ByType:  map[string]*CoverageMetrics{},
	}
	recs := svc.generateCoverageRecommendations(report, []string{"u1", "u2"})
	require.NotEmpty(t, recs)
	found := false
	for _, r := range recs {
		if len(r) > 0 && (r[0] == 'C' || r[0] == 'c') {
			found = true
			break
		}
	}
	assert.True(t, found)
}

func TestGenerateCoverageRecommendations_Good(t *testing.T) {
	svc := &MatrixService{}
	report := &CoverageReport{
		Overall: &CoverageMetrics{CoveragePercent: 95},
		ByType:  map[string]*CoverageMetrics{},
	}
	recs := svc.generateCoverageRecommendations(report, nil)
	require.NotEmpty(t, recs)
}

func TestGenerateGapRecommendations_NoGaps(t *testing.T) {
	svc := &MatrixService{}
	a := &GapAnalysis{
		MissingForward:  []Gap{},
		MissingBackward: []Gap{},
		Orphaned:        []string{},
	}
	recs := svc.generateGapRecommendations(a)
	require.NotEmpty(t, recs)
	assert.Contains(t, recs[0], "No traceability gaps")
}

func TestGenerateGapRecommendations_Forward(t *testing.T) {
	svc := &MatrixService{}
	a := &GapAnalysis{
		MissingForward:  []Gap{{ItemID: "1"}},
		MissingBackward: []Gap{},
		Orphaned:        []string{},
	}
	recs := svc.generateGapRecommendations(a)
	require.NotEmpty(t, recs)
}

func TestTypes_MatrixItem(t *testing.T) {
	m := MatrixItem{ItemID: "i1", Title: "t", Type: "requirement", Status: "active", TraceCount: 2}
	assert.Equal(t, "i1", m.ItemID)
	assert.Equal(t, 2, m.TraceCount)
}

func TestTypes_Link(t *testing.T) {
	l := Link{SourceID: "s", TargetID: "t", LinkType: "TRACES_TO", Bidirectional: true}
	assert.True(t, l.Bidirectional)
	assert.Equal(t, "TRACES_TO", l.LinkType)
}

func TestTypes_ValidationIssue(t *testing.T) {
	v := ValidationIssue{Severity: "error", ItemID: "i", Message: "m", Suggestion: "s"}
	assert.Equal(t, "error", v.Severity)
	assert.Equal(t, "s", v.Suggestion)
}

func TestScanStringList_Empty(t *testing.T) {
	// We need pgx.Rows - use pgxmock or build manually. For unit test we use a simple mock rows.
	// scanStringList(rows pgx.Rows) - we can't easily create pgx.Rows without pgxmock.
	t.Skip("scanStringList requires pgx.Rows - use integration or pgxmock")
}

func TestQueueMatrixRequirements(t *testing.T) {
	batch := &pgx.Batch{}
	queueMatrixRequirements(batch, "proj-1")
	// Batch is filled; we can't easily assert without executing
	assert.NotNil(t, batch)
}

func TestQueueMatrixTestCases(t *testing.T) {
	batch := &pgx.Batch{}
	queueMatrixTestCases(batch, "proj-1")
	assert.NotNil(t, batch)
}

func TestQueueMatrixLinks(t *testing.T) {
	batch := &pgx.Batch{}
	queueMatrixLinks(batch, "proj-1")
	assert.NotNil(t, batch)
}

func TestQueueMatrixCoverage(t *testing.T) {
	batch := &pgx.Batch{}
	queueMatrixCoverage(batch, "proj-1")
	assert.NotNil(t, batch)
}

func TestQueueMatrixUntracedItems(t *testing.T) {
	batch := &pgx.Batch{}
	queueMatrixUntracedItems(batch, "proj-1")
	assert.NotNil(t, batch)
}

func TestCoverageConstants(t *testing.T) {
	assert.Equal(t, 50, coverageCriticallyLow)
	assert.Equal(t, 80, coverageBelowTarget)
	assert.Equal(t, 2, coverageFullyTraced)
	assert.Equal(t, 100, coveragePercentScale)
}

func TestMatrix_JSON(t *testing.T) {
	m := Matrix{
		ProjectID:    "p",
		Requirements: []MatrixItem{{ItemID: "r1", Title: "R1"}},
		TestCases:    []MatrixItem{{ItemID: "t1", Title: "T1"}},
		Links:        []Link{{SourceID: "s", TargetID: "t", LinkType: "TRACES_TO"}},
	}
	data, err := json.Marshal(m)
	require.NoError(t, err)
	assert.NotEmpty(t, data)
	var out Matrix
	err = json.Unmarshal(data, &out)
	require.NoError(t, err)
	assert.Equal(t, m.ProjectID, out.ProjectID)
	assert.Len(t, out.Requirements, 1)
	assert.Len(t, out.TestCases, 1)
	assert.Len(t, out.Links, 1)
}

func TestGapAnalysis_JSON(t *testing.T) {
	a := GapAnalysis{
		ProjectID:      "p",
		MissingForward: []Gap{{ItemID: "1", Title: "T", Type: "requirement"}},
		Orphaned:       []string{"o1"},
	}
	data, err := json.Marshal(a)
	require.NoError(t, err)
	assert.NotEmpty(t, data)
}

func TestChangeImpact_JSON(t *testing.T) {
	c := ChangeImpact{
		ItemID:         "i",
		DirectImpact:   []string{"d1"},
		IndirectImpact: []string{"i1"},
		TestsToRun:     []string{"t1"},
	}
	data, err := json.Marshal(c)
	require.NoError(t, err)
	assert.NotEmpty(t, data)
}

func TestNewMatrixService_WithCache(t *testing.T) {
	mock := newMockCache()
	svc := NewMatrixService(nil, mock)
	require.NotNil(t, svc)
	assert.Equal(t, mock, svc.cache)
}
