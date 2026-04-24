package traceability

import "time"

// Matrix represents a complete traceability matrix for a project.
type Matrix struct {
	ProjectID    string           `json:"project_id"`
	GeneratedAt  time.Time        `json:"generated_at"`
	Requirements []MatrixItem     `json:"requirements"`
	TestCases    []MatrixItem     `json:"test_cases"`
	Links        []Link           `json:"links"`
	Coverage     *CoverageMetrics `json:"coverage"`
}

// MatrixItem represents an item in the traceability matrix
type MatrixItem struct {
	ItemID     string            `json:"item_id"`
	Title      string            `json:"title"`
	Type       string            `json:"type"`
	Status     string            `json:"status"`
	TraceCount int               `json:"trace_count"`
	Metadata   map[string]string `json:"metadata"`
}

// Link represents a link between items in the matrix.
type Link struct {
	SourceID      string `json:"source_id"`
	TargetID      string `json:"target_id"`
	LinkType      string `json:"link_type"`
	Bidirectional bool   `json:"bidirectional"`
}

// CoverageMetrics contains coverage statistics
type CoverageMetrics struct {
	TotalRequirements  int      `json:"total_requirements"`
	TracedRequirements int      `json:"traced_requirements"`
	CoveragePercent    float64  `json:"coverage_percent"`
	UntracedItems      []string `json:"untraced_items"`
}

// CoverageReport provides a detailed coverage analysis
type CoverageReport struct {
	ProjectID       string                      `json:"project_id"`
	Overall         *CoverageMetrics            `json:"overall"`
	ByType          map[string]*CoverageMetrics `json:"by_type"`
	Recommendations []string                    `json:"recommendations"`
}

// GapAnalysis identifies missing traceability links
type GapAnalysis struct {
	ProjectID       string   `json:"project_id"`
	MissingForward  []Gap    `json:"missing_forward"`  // Requirements without tests
	MissingBackward []Gap    `json:"missing_backward"` // Tests without requirements
	Orphaned        []string `json:"orphaned"`         // No links at all
	Recommendations []string `json:"recommendations"`
}

// Gap represents a missing traceability link
type Gap struct {
	ItemID        string   `json:"item_id"`
	Title         string   `json:"title"`
	Type          string   `json:"type"`
	ExpectedLinks []string `json:"expected_links"`
}

// ItemTraceability shows traceability for a specific item
type ItemTraceability struct {
	ItemID          string `json:"item_id"`
	UpstreamLinks   []Link `json:"upstream_links"`
	DownstreamLinks []Link `json:"downstream_links"`
	CoverageStatus  string `json:"coverage_status"` // "full", "partial", "none"
}

// ValidationReport contains validation results for traceability completeness
type ValidationReport struct {
	ProjectID  string            `json:"project_id"`
	IsComplete bool              `json:"is_complete"`
	Score      float64           `json:"score"` // 0-100
	Issues     []ValidationIssue `json:"issues"`
	Passed     int               `json:"passed"`
	Failed     int               `json:"failed"`
}

// ValidationIssue represents a validation problem
type ValidationIssue struct {
	Severity   string `json:"severity"` // "error", "warning", "info"
	ItemID     string `json:"item_id"`
	Message    string `json:"message"`
	Suggestion string `json:"suggestion,omitempty"`
}

// ChangeImpact analyzes the impact of changes to an item
type ChangeImpact struct {
	ItemID         string   `json:"item_id"`
	DirectImpact   []string `json:"direct_impact"`
	IndirectImpact []string `json:"indirect_impact"`
	TestsToRun     []string `json:"tests_to_run"`
	DocsToUpdate   []string `json:"docs_to_update"`
}
