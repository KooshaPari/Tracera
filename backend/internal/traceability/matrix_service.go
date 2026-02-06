// Package traceability provides services for traceability matrices.
package traceability

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/kooshapari/tracertm-backend/internal/cache"
)

// Coverage thresholds for traceability metrics
const (
	coverageCriticallyLow = 50
	coverageBelowTarget   = 80
	coverageFullyTraced   = 2
	coveragePercentScale  = 100
)

// MatrixService handles traceability matrix operations
type MatrixService struct {
	db    *pgxpool.Pool
	cache cache.Cache
}

// NewMatrixService creates a new MatrixService instance
func NewMatrixService(db *pgxpool.Pool, cacheImpl cache.Cache) *MatrixService {
	return &MatrixService{
		db:    db,
		cache: cacheImpl,
	}
}

// GenerateMatrix generates a complete traceability matrix for a project
func (s *MatrixService) GenerateMatrix(ctx context.Context, projectID string) (*Matrix, error) {
	cacheKey := "traceability:matrix:" + projectID

	return s.getCachedOrCompute(ctx, cacheKey, func() (*Matrix, error) {
		batch := s.buildMatrixBatch(projectID)

		// Execute batch
		br := s.db.SendBatch(ctx, batch)
		defer func() { _ = br.Close() }()

		matrix := s.initMatrix(projectID)

		if err := s.scanMatrixRequirements(br, matrix); err != nil {
			return nil, err
		}
		if err := s.scanMatrixTestCases(br, matrix); err != nil {
			return nil, err
		}
		if err := s.scanMatrixLinks(br, matrix); err != nil {
			return nil, err
		}
		total, traced, percent, err := s.scanMatrixCoverage(br)
		if err != nil {
			return nil, err
		}
		untracedItems, err := s.scanMatrixUntraced(br)
		if err != nil {
			return nil, err
		}
		s.applyMatrixCoverage(matrix, total, traced, percent, untracedItems)

		return matrix, nil
	})
}

// GetCoverageReport generates a coverage report for a project
func (s *MatrixService) GetCoverageReport(ctx context.Context, projectID string) (*CoverageReport, error) {
	cacheKey := "traceability:coverage:" + projectID

	return s.getCachedOrComputeCoverage(ctx, cacheKey, func() (*CoverageReport, error) {
		batch := s.buildCoverageBatch(projectID)

		br := s.db.SendBatch(ctx, batch)
		defer func() { _ = br.Close() }()

		overall, err := s.scanCoverageOverall(br)
		if err != nil {
			return nil, err
		}
		byType, err := s.scanCoverageByType(br)
		if err != nil {
			return nil, err
		}
		untracedItems, err := s.scanCoverageUntraced(br)
		if err != nil {
			return nil, err
		}

		report := s.buildCoverageReport(projectID, overall, byType, untracedItems)
		return report, nil
	})
}

// GetGapAnalysis identifies gaps in traceability
func (s *MatrixService) GetGapAnalysis(ctx context.Context, projectID string) (*GapAnalysis, error) {
	cacheKey := "traceability:gaps:" + projectID

	return s.getCachedOrComputeGaps(ctx, cacheKey, func() (*GapAnalysis, error) {
		batch := s.buildGapBatch(projectID)

		br := s.db.SendBatch(ctx, batch)
		defer func() { _ = br.Close() }()

		missingForward, err := s.scanGapForward(br)
		if err != nil {
			return nil, err
		}
		missingBackward, err := s.scanGapBackward(br)
		if err != nil {
			return nil, err
		}
		orphaned, err := s.scanGapOrphaned(br)
		if err != nil {
			return nil, err
		}

		analysis := &GapAnalysis{
			ProjectID:       projectID,
			MissingForward:  missingForward,
			MissingBackward: missingBackward,
			Orphaned:        orphaned,
		}
		analysis.Recommendations = s.generateGapRecommendations(analysis)

		return analysis, nil
	})
}

// GetItemTraceability gets traceability information for a specific item
func (s *MatrixService) GetItemTraceability(ctx context.Context, itemID string) (*ItemTraceability, error) {
	cacheKey := "traceability:item:" + itemID

	var result ItemTraceability
	err := s.cache.Get(ctx, cacheKey, &result)
	if err == nil {
		return &result, nil
	}

	batch := s.buildItemTraceabilityBatch(itemID)

	br := s.db.SendBatch(ctx, batch)
	defer func() { _ = br.Close() }()

	resultPtr, err := s.scanItemTraceability(br, itemID)
	if err != nil {
		return nil, err
	}
	result = *resultPtr

	// Cache for 5 minutes
	if err := s.cache.Set(ctx, cacheKey, result); err != nil {
		log.Printf("Failed to cache item traceability: %v", err)
	}

	return &result, nil
}

// ValidateCompleteness validates traceability completeness for a project
func (s *MatrixService) ValidateCompleteness(ctx context.Context, projectID string) (*ValidationReport, error) {
	cacheKey := "traceability:validation:" + projectID

	return s.getCachedOrComputeValidation(ctx, cacheKey, func() (*ValidationReport, error) {
		report := &ValidationReport{
			ProjectID: projectID,
			Issues:    []ValidationIssue{},
		}

		issues, failed, err := s.fetchUntracedRequirementIssues(ctx, projectID)
		if err != nil {
			return nil, err
		}
		report.Issues = append(report.Issues, issues...)
		report.Failed = failed

		orphanedIssues, err := s.fetchOrphanedIssues(ctx, projectID)
		if err != nil {
			return nil, err
		}
		report.Issues = append(report.Issues, orphanedIssues...)

		totalItems, err := s.countProjectItems(ctx, projectID)
		if err != nil {
			return nil, err
		}
		s.finalizeValidationReport(report, totalItems)

		return report, nil
	})
}

// GetChangeImpact analyzes the impact of changes to an item
func (s *MatrixService) GetChangeImpact(ctx context.Context, itemID string) (*ChangeImpact, error) {
	cacheKey := "traceability:impact:" + itemID

	var result ChangeImpact
	err := s.cache.Get(ctx, cacheKey, &result)
	if err == nil {
		return &result, nil
	}

	result = s.initChangeImpact(itemID)
	directImpact, directTests, err := s.fetchDirectImpact(ctx, itemID)
	if err != nil {
		return nil, err
	}
	result.DirectImpact = directImpact
	result.TestsToRun = append(result.TestsToRun, directTests...)

	indirectImpact, indirectTests, err := s.fetchIndirectImpact(ctx, directImpact, itemID)
	if err != nil {
		return nil, err
	}
	result.IndirectImpact = indirectImpact
	result.TestsToRun = append(result.TestsToRun, indirectTests...)

	// Cache for 5 minutes
	if err := s.cache.Set(ctx, cacheKey, result); err != nil {
		log.Printf("Failed to cache change impact: %v", err)
	}

	return &result, nil
}

// Helper methods

func (s *MatrixService) buildMatrixBatch(projectID string) *pgx.Batch {
	batch := &pgx.Batch{}

	queueMatrixRequirements(batch, projectID)
	queueMatrixTestCases(batch, projectID)
	queueMatrixLinks(batch, projectID)
	queueMatrixCoverage(batch, projectID)
	queueMatrixUntracedItems(batch, projectID)

	return batch
}

func queueMatrixRequirements(batch *pgx.Batch, projectID string) {
	batch.Queue(`
		SELECT id, title, type, status, metadata
		FROM items
		WHERE project_id = $1
		  AND type IN ('requirement', 'feature', 'epic')
		  AND deleted_at IS NULL
		ORDER BY created_at
	`, projectID)
}

func queueMatrixTestCases(batch *pgx.Batch, projectID string) {
	batch.Queue(`
		SELECT id, title, type, status, metadata
		FROM items
		WHERE project_id = $1
		  AND type IN ('test_case', 'test_suite')
		  AND deleted_at IS NULL
		ORDER BY created_at
	`, projectID)
}

func queueMatrixLinks(batch *pgx.Batch, projectID string) {
	batch.Queue(`
		SELECT l.source_id, l.target_id, l.type,
		       EXISTS(SELECT 1 FROM links l2
		              WHERE l2.source_id = l.target_id
		                AND l2.target_id = l.source_id) AS bidirectional
		FROM links l
		JOIN items i1 ON l.source_id = i1.id
		WHERE i1.project_id = $1
		  AND l.type IN ('TRACES_TO', 'VALIDATES', 'IMPLEMENTS', 'TESTS')
		ORDER BY l.created_at
	`, projectID)
}

func queueMatrixCoverage(batch *pgx.Batch, projectID string) {
	batch.Queue(`
		WITH traced AS (
			SELECT DISTINCT i.id
			FROM items i
			JOIN links l ON i.id = l.source_id OR i.id = l.target_id
			WHERE i.project_id = $1
			  AND i.type IN ('requirement', 'feature', 'epic')
			  AND i.deleted_at IS NULL
		)
		SELECT
			COUNT(DISTINCT i.id) AS total,
			COUNT(DISTINCT t.id) AS traced,
			ROUND(COALESCE(COUNT(DISTINCT t.id)::numeric / NULLIF(COUNT(DISTINCT i.id), 0) * 100, 0), 2) AS percent
		FROM items i
		LEFT JOIN traced t ON i.id = t.id
		WHERE i.project_id = $1
		  AND i.type IN ('requirement', 'feature', 'epic')
		  AND i.deleted_at IS NULL
	`, projectID)
}

func queueMatrixUntracedItems(batch *pgx.Batch, projectID string) {
	batch.Queue(`
		SELECT i.id
		FROM items i
		WHERE i.project_id = $1
		  AND i.type IN ('requirement', 'feature', 'epic')
		  AND i.deleted_at IS NULL
		  AND NOT EXISTS (
			  SELECT 1 FROM links l
			  WHERE l.source_id = i.id OR l.target_id = i.id
		  )
		ORDER BY i.created_at
	`, projectID)
}

func (s *MatrixService) initMatrix(projectID string) *Matrix {
	return &Matrix{
		ProjectID:    projectID,
		GeneratedAt:  time.Now(),
		Requirements: []MatrixItem{},
		TestCases:    []MatrixItem{},
		Links:        []Link{},
	}
}

func (s *MatrixService) scanMatrixRequirements(br pgx.BatchResults, matrix *Matrix) error {
	rows, err := br.Query()
	if err != nil {
		return fmt.Errorf("failed to query requirements: %w", err)
	}
	matrix.Requirements, err = s.scanMatrixItems(rows)
	if err != nil {
		return fmt.Errorf("failed to scan requirements: %w", err)
	}
	return nil
}

func (s *MatrixService) scanMatrixTestCases(br pgx.BatchResults, matrix *Matrix) error {
	rows, err := br.Query()
	if err != nil {
		return fmt.Errorf("failed to query test cases: %w", err)
	}
	matrix.TestCases, err = s.scanMatrixItems(rows)
	if err != nil {
		return fmt.Errorf("failed to scan test cases: %w", err)
	}
	return nil
}

func (s *MatrixService) scanMatrixLinks(br pgx.BatchResults, matrix *Matrix) error {
	rows, err := br.Query()
	if err != nil {
		return fmt.Errorf("failed to query links: %w", err)
	}
	matrix.Links, err = s.scanLinks(rows)
	if err != nil {
		return fmt.Errorf("failed to scan links: %w", err)
	}
	return nil
}

func (s *MatrixService) scanMatrixCoverage(br pgx.BatchResults) (int, int, float64, error) {
	var total, traced int
	var percent float64
	if err := br.QueryRow().Scan(&total, &traced, &percent); err != nil {
		return 0, 0, 0, fmt.Errorf("failed to scan coverage metrics: %w", err)
	}
	return total, traced, percent, nil
}

func (s *MatrixService) scanMatrixUntraced(br pgx.BatchResults) ([]string, error) {
	rows, err := br.Query()
	if err != nil {
		return nil, fmt.Errorf("failed to query untraced items: %w", err)
	}
	untracedItems, err := s.scanStringList(rows)
	if err != nil {
		return nil, fmt.Errorf("failed to scan untraced items: %w", err)
	}
	return untracedItems, nil
}

func (s *MatrixService) applyMatrixCoverage(matrix *Matrix, total, traced int, percent float64, untraced []string) {
	matrix.Coverage = &CoverageMetrics{
		TotalRequirements:  total,
		TracedRequirements: traced,
		CoveragePercent:    percent,
		UntracedItems:      untraced,
	}
}

func (s *MatrixService) buildCoverageBatch(projectID string) *pgx.Batch {
	batch := &pgx.Batch{}

	// Overall coverage
	batch.Queue(`
		WITH traced AS (
			SELECT DISTINCT i.id
			FROM items i
			JOIN links l ON i.id = l.source_id OR i.id = l.target_id
			WHERE i.project_id = $1
			  AND i.type IN ('requirement', 'feature', 'epic')
			  AND i.deleted_at IS NULL
		)
		SELECT
			COUNT(DISTINCT i.id) AS total,
			COUNT(DISTINCT t.id) AS traced,
			ROUND(COALESCE(COUNT(DISTINCT t.id)::numeric / NULLIF(COUNT(DISTINCT i.id), 0) * 100, 0), 2) AS percent
		FROM items i
		LEFT JOIN traced t ON i.id = t.id
		WHERE i.project_id = $1
		  AND i.type IN ('requirement', 'feature', 'epic')
		  AND i.deleted_at IS NULL
	`, projectID)

	// Coverage by type
	batch.Queue(`
		WITH traced AS (
			SELECT DISTINCT i.id, i.type
			FROM items i
			JOIN links l ON i.id = l.source_id OR i.id = l.target_id
			WHERE i.project_id = $1
			  AND i.type IN ('requirement', 'feature', 'epic')
			  AND i.deleted_at IS NULL
		)
		SELECT
			i.type,
			COUNT(DISTINCT i.id) AS total,
			COUNT(DISTINCT t.id) AS traced,
			ROUND(COALESCE(COUNT(DISTINCT t.id)::numeric / NULLIF(COUNT(DISTINCT i.id), 0) * 100, 0), 2) AS percent
		FROM items i
		LEFT JOIN traced t ON i.id = t.id AND i.type = t.type
		WHERE i.project_id = $1
		  AND i.type IN ('requirement', 'feature', 'epic')
		  AND i.deleted_at IS NULL
		GROUP BY i.type
	`, projectID)

	// Untraced items for recommendations
	batch.Queue(`
		SELECT i.id
		FROM items i
		WHERE i.project_id = $1
		  AND i.type IN ('requirement', 'feature', 'epic')
		  AND i.deleted_at IS NULL
		  AND NOT EXISTS (
			  SELECT 1 FROM links l
			  WHERE l.source_id = i.id OR l.target_id = i.id
		  )
		ORDER BY i.created_at
		LIMIT 10
	`, projectID)

	return batch
}

func (s *MatrixService) scanCoverageOverall(br pgx.BatchResults) (*CoverageMetrics, error) {
	var total, traced int
	var percent float64
	if err := br.QueryRow().Scan(&total, &traced, &percent); err != nil {
		return nil, fmt.Errorf("failed to scan overall coverage: %w", err)
	}
	return &CoverageMetrics{
		TotalRequirements:  total,
		TracedRequirements: traced,
		CoveragePercent:    percent,
	}, nil
}

func (s *MatrixService) scanCoverageByType(br pgx.BatchResults) (map[string]*CoverageMetrics, error) {
	rows, err := br.Query()
	if err != nil {
		return nil, fmt.Errorf("failed to query coverage by type: %w", err)
	}
	defer rows.Close()

	byType := make(map[string]*CoverageMetrics)
	for rows.Next() {
		var itemType string
		var typeTotal, typeTraced int
		var typePercent float64

		if err := rows.Scan(&itemType, &typeTotal, &typeTraced, &typePercent); err != nil {
			return nil, fmt.Errorf("failed to scan type coverage: %w", err)
		}
		byType[itemType] = &CoverageMetrics{
			TotalRequirements:  typeTotal,
			TracedRequirements: typeTraced,
			CoveragePercent:    typePercent,
		}
	}

	return byType, rows.Err()
}

func (s *MatrixService) scanCoverageUntraced(br pgx.BatchResults) ([]string, error) {
	rows, err := br.Query()
	if err != nil {
		return nil, fmt.Errorf("failed to query untraced items: %w", err)
	}
	untracedItems, err := s.scanStringList(rows)
	if err != nil {
		return nil, fmt.Errorf("failed to scan untraced items: %w", err)
	}
	return untracedItems, nil
}

func (s *MatrixService) buildCoverageReport(
	projectID string,
	overall *CoverageMetrics,
	byType map[string]*CoverageMetrics,
	untracedItems []string,
) *CoverageReport {
	report := &CoverageReport{
		ProjectID: projectID,
		Overall:   overall,
		ByType:    byType,
	}
	report.Recommendations = s.generateCoverageRecommendations(report, untracedItems)
	return report
}

func (s *MatrixService) buildGapBatch(projectID string) *pgx.Batch {
	batch := &pgx.Batch{}

	// Requirements without tests (forward gap)
	batch.Queue(`
		SELECT i.id, i.title, i.type
		FROM items i
		WHERE i.project_id = $1
		  AND i.type IN ('requirement', 'feature', 'epic')
		  AND i.deleted_at IS NULL
		  AND NOT EXISTS (
			  SELECT 1 FROM links l
			  WHERE l.source_id = i.id
				AND l.type IN ('TRACES_TO', 'VALIDATES', 'TESTS')
		  )
		ORDER BY i.created_at
	`, projectID)

	// Tests without requirements (backward gap)
	batch.Queue(`
		SELECT i.id, i.title, i.type
		FROM items i
		WHERE i.project_id = $1
		  AND i.type IN ('test_case', 'test_suite')
		  AND i.deleted_at IS NULL
		  AND NOT EXISTS (
			  SELECT 1 FROM links l
			  WHERE l.target_id = i.id
				AND l.type IN ('TRACES_TO', 'VALIDATES', 'TESTS')
		  )
		ORDER BY i.created_at
	`, projectID)

	// Orphaned items (no links at all)
	batch.Queue(`
		SELECT i.id
		FROM items i
		WHERE i.project_id = $1
		  AND i.deleted_at IS NULL
		  AND NOT EXISTS (
			  SELECT 1 FROM links l
			  WHERE l.source_id = i.id OR l.target_id = i.id
		  )
		ORDER BY i.created_at
	`, projectID)

	return batch
}

func (s *MatrixService) scanGapForward(br pgx.BatchResults) ([]Gap, error) {
	rows, err := br.Query()
	if err != nil {
		return nil, fmt.Errorf("failed to query forward gaps: %w", err)
	}
	gaps, err := s.scanGaps(rows)
	if err != nil {
		return nil, fmt.Errorf("failed to scan forward gaps: %w", err)
	}
	return gaps, nil
}

func (s *MatrixService) scanGapBackward(br pgx.BatchResults) ([]Gap, error) {
	rows, err := br.Query()
	if err != nil {
		return nil, fmt.Errorf("failed to query backward gaps: %w", err)
	}
	gaps, err := s.scanGaps(rows)
	if err != nil {
		return nil, fmt.Errorf("failed to scan backward gaps: %w", err)
	}
	return gaps, nil
}

func (s *MatrixService) scanGapOrphaned(br pgx.BatchResults) ([]string, error) {
	rows, err := br.Query()
	if err != nil {
		return nil, fmt.Errorf("failed to query orphaned items: %w", err)
	}
	orphaned, err := s.scanStringList(rows)
	if err != nil {
		return nil, fmt.Errorf("failed to scan orphaned items: %w", err)
	}
	return orphaned, nil
}

func (s *MatrixService) buildItemTraceabilityBatch(itemID string) *pgx.Batch {
	batch := &pgx.Batch{}

	// Upstream links (items linking TO this item)
	batch.Queue(`
		SELECT l.source_id, l.target_id, l.type,
		       EXISTS(SELECT 1 FROM links l2
		              WHERE l2.source_id = l.target_id
		                AND l2.target_id = l.source_id) AS bidirectional
		FROM links l
		WHERE l.target_id = $1
		ORDER BY l.created_at
	`, itemID)

	// Downstream links (items this item links TO)
	batch.Queue(`
		SELECT l.source_id, l.target_id, l.type,
		       EXISTS(SELECT 1 FROM links l2
		              WHERE l2.source_id = l.target_id
		                AND l2.target_id = l.source_id) AS bidirectional
		FROM links l
		WHERE l.source_id = $1
		ORDER BY l.created_at
	`, itemID)

	return batch
}

func (s *MatrixService) scanItemTraceability(br pgx.BatchResults, itemID string) (*ItemTraceability, error) {
	result := &ItemTraceability{
		ItemID: itemID,
	}

	rows, err := br.Query()
	if err != nil {
		return nil, fmt.Errorf("failed to query upstream links: %w", err)
	}
	result.UpstreamLinks, err = s.scanLinks(rows)
	if err != nil {
		return nil, fmt.Errorf("failed to scan upstream links: %w", err)
	}

	rows, err = br.Query()
	if err != nil {
		return nil, fmt.Errorf("failed to query downstream links: %w", err)
	}
	result.DownstreamLinks, err = s.scanLinks(rows)
	if err != nil {
		return nil, fmt.Errorf("failed to scan downstream links: %w", err)
	}

	result.CoverageStatus = s.determineCoverageStatus(result.UpstreamLinks, result.DownstreamLinks)
	return result, nil
}

func (s *MatrixService) fetchUntracedRequirementIssues(ctx context.Context, projectID string) ([]ValidationIssue, int, error) {
	rows, err := s.db.Query(ctx, `
		SELECT i.id, i.title
		FROM items i
		WHERE i.project_id = $1
		  AND i.type IN ('requirement', 'feature', 'epic')
		  AND i.deleted_at IS NULL
		  AND NOT EXISTS (
			  SELECT 1 FROM links l
			  WHERE l.source_id = i.id
				AND l.type IN ('TRACES_TO', 'VALIDATES', 'TESTS')
		  )
	`, projectID)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to query untraced requirements: %w", err)
	}
	defer rows.Close()

	issues := []ValidationIssue{}
	failed := 0
	for rows.Next() {
		var itemID, title string
		if err := rows.Scan(&itemID, &title); err != nil {
			return nil, 0, err
		}

		issues = append(issues, ValidationIssue{
			Severity:   "error",
			ItemID:     itemID,
			Message:    "Requirement '" + title + "' has no traceability to tests",
			Suggestion: "Create test cases that validate this requirement",
		})
		failed++
	}

	return issues, failed, rows.Err()
}

func (s *MatrixService) fetchOrphanedIssues(ctx context.Context, projectID string) ([]ValidationIssue, error) {
	rows, err := s.db.Query(ctx, `
		SELECT i.id, i.title, i.type
		FROM items i
		WHERE i.project_id = $1
		  AND i.deleted_at IS NULL
		  AND NOT EXISTS (
			  SELECT 1 FROM links l
			  WHERE l.source_id = i.id OR l.target_id = i.id
		  )
	`, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to query orphaned items: %w", err)
	}
	defer rows.Close()

	issues := []ValidationIssue{}
	for rows.Next() {
		var itemID, title, itemType string
		if err := rows.Scan(&itemID, &title, &itemType); err != nil {
			return nil, err
		}

		issues = append(issues, ValidationIssue{
			Severity:   "warning",
			ItemID:     itemID,
			Message:    fmt.Sprintf("%s '%s' is orphaned (no links)", itemType, title),
			Suggestion: "Link this item to related requirements, tests, or other items",
		})
	}

	return issues, rows.Err()
}

func (s *MatrixService) countProjectItems(ctx context.Context, projectID string) (int, error) {
	var totalItems int
	if err := s.db.QueryRow(ctx, `
		SELECT COUNT(*) FROM items
		WHERE project_id = $1 AND deleted_at IS NULL
	`, projectID).Scan(&totalItems); err != nil {
		return 0, fmt.Errorf("failed to count total items: %w", err)
	}
	return totalItems, nil
}

func (s *MatrixService) finalizeValidationReport(report *ValidationReport, totalItems int) {
	report.Passed = totalItems - report.Failed - len(report.Issues) + report.Failed
	report.IsComplete = report.Failed == 0

	if totalItems > 0 {
		report.Score = float64(report.Passed) / float64(totalItems) * coveragePercentScale
	}
}

func (s *MatrixService) initChangeImpact(itemID string) ChangeImpact {
	return ChangeImpact{
		ItemID:         itemID,
		DirectImpact:   []string{},
		IndirectImpact: []string{},
		TestsToRun:     []string{},
		DocsToUpdate:   []string{},
	}
}

func (s *MatrixService) fetchDirectImpact(ctx context.Context, itemID string) ([]string, []string, error) {
	rows, err := s.db.Query(ctx, `
		SELECT l.target_id, i.type
		FROM links l
		JOIN items i ON l.target_id = i.id
		WHERE l.source_id = $1
		  AND i.deleted_at IS NULL
	`, itemID)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to query direct impact: %w", err)
	}
	defer rows.Close()

	directImpact := []string{}
	testsToRun := []string{}
	for rows.Next() {
		var targetID, targetType string
		if err := rows.Scan(&targetID, &targetType); err != nil {
			return nil, nil, err
		}

		directImpact = append(directImpact, targetID)
		if targetType == "test_case" || targetType == "test_suite" {
			testsToRun = append(testsToRun, targetID)
		}
	}

	return directImpact, testsToRun, rows.Err()
}

func (s *MatrixService) fetchIndirectImpact(ctx context.Context, directImpact []string, itemID string) ([]string, []string, error) {
	if len(directImpact) == 0 {
		return []string{}, []string{}, nil
	}

	query := `
		WITH direct AS (
			SELECT unnest($1::text[]) AS item_id
		)
		SELECT DISTINCT l.target_id, i.type
		FROM direct d
		JOIN links l ON d.item_id = l.source_id
		JOIN items i ON l.target_id = i.id
		WHERE i.deleted_at IS NULL
		  AND l.target_id NOT IN (SELECT item_id FROM direct)
		  AND l.target_id != $2
	`

	rows, err := s.db.Query(ctx, query, directImpact, itemID)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to query indirect impact: %w", err)
	}
	defer rows.Close()

	indirectImpact := []string{}
	testsToRun := []string{}
	for rows.Next() {
		var targetID, targetType string
		if err := rows.Scan(&targetID, &targetType); err != nil {
			return nil, nil, err
		}

		indirectImpact = append(indirectImpact, targetID)
		if targetType == "test_case" || targetType == "test_suite" {
			testsToRun = append(testsToRun, targetID)
		}
	}

	return indirectImpact, testsToRun, rows.Err()
}

func (s *MatrixService) getCachedOrCompute(
	ctx context.Context,
	cacheKey string,
	computeFn func() (*Matrix, error),
) (*Matrix, error) {
	// Try cache first
	var cached Matrix
	err := s.cache.Get(ctx, cacheKey, &cached)
	if err == nil {
		return &cached, nil
	}

	// Compute
	result, err := computeFn()
	if err != nil {
		return nil, err
	}

	// Cache for 10 minutes
	if err := s.cache.Set(ctx, cacheKey, result); err != nil {
		log.Printf("Failed to cache result for key %s: %v", cacheKey, err)
	}

	return result, nil
}

func (s *MatrixService) getCachedOrComputeCoverage(
	ctx context.Context,
	cacheKey string,
	computeFn func() (*CoverageReport, error),
) (*CoverageReport, error) {
	// Try cache first
	var cached CoverageReport
	err := s.cache.Get(ctx, cacheKey, &cached)
	if err == nil {
		return &cached, nil
	}

	// Compute
	result, err := computeFn()
	if err != nil {
		return nil, err
	}

	// Cache for 10 minutes
	if err := s.cache.Set(ctx, cacheKey, result); err != nil {
		log.Printf("Failed to cache result for key %s: %v", cacheKey, err)
	}

	return result, nil
}

func (s *MatrixService) getCachedOrComputeGaps(
	ctx context.Context,
	cacheKey string,
	computeFn func() (*GapAnalysis, error),
) (*GapAnalysis, error) {
	// Try cache first
	var cached GapAnalysis
	err := s.cache.Get(ctx, cacheKey, &cached)
	if err == nil {
		return &cached, nil
	}

	// Compute
	result, err := computeFn()
	if err != nil {
		return nil, err
	}

	// Cache for 10 minutes
	if err := s.cache.Set(ctx, cacheKey, result); err != nil {
		log.Printf("Failed to cache result for key %s: %v", cacheKey, err)
	}

	return result, nil
}

func (s *MatrixService) getCachedOrComputeValidation(
	ctx context.Context,
	cacheKey string,
	computeFn func() (*ValidationReport, error),
) (*ValidationReport, error) {
	// Try cache first
	var cached ValidationReport
	err := s.cache.Get(ctx, cacheKey, &cached)
	if err == nil {
		return &cached, nil
	}

	// Compute
	result, err := computeFn()
	if err != nil {
		return nil, err
	}

	// Cache for 10 minutes
	if err := s.cache.Set(ctx, cacheKey, result); err != nil {
		log.Printf("Failed to cache result for key %s: %v", cacheKey, err)
	}

	return result, nil
}

func (s *MatrixService) scanMatrixItems(rows pgx.Rows) ([]MatrixItem, error) {
	defer rows.Close()

	var items []MatrixItem
	for rows.Next() {
		var item MatrixItem
		var metadataJSON []byte

		if err := rows.Scan(&item.ItemID, &item.Title, &item.Type, &item.Status, &metadataJSON); err != nil {
			return nil, err
		}

		// Parse metadata JSON
		if len(metadataJSON) > 0 {
			if err := json.Unmarshal(metadataJSON, &item.Metadata); err != nil {
				item.Metadata = make(map[string]string)
			}
		} else {
			item.Metadata = make(map[string]string)
		}

		items = append(items, item)
	}

	return items, rows.Err()
}

func (s *MatrixService) scanLinks(rows pgx.Rows) ([]Link, error) {
	defer rows.Close()

	var links []Link
	for rows.Next() {
		var link Link

		if err := rows.Scan(&link.SourceID, &link.TargetID, &link.LinkType, &link.Bidirectional); err != nil {
			return nil, err
		}

		links = append(links, link)
	}

	return links, rows.Err()
}

func (s *MatrixService) scanGaps(rows pgx.Rows) ([]Gap, error) {
	defer rows.Close()

	var gaps []Gap
	for rows.Next() {
		var gap Gap

		if err := rows.Scan(&gap.ItemID, &gap.Title, &gap.Type); err != nil {
			return nil, err
		}

		gap.ExpectedLinks = []string{} // Could be populated based on business rules

		gaps = append(gaps, gap)
	}

	return gaps, rows.Err()
}

func (s *MatrixService) scanStringList(rows pgx.Rows) ([]string, error) {
	defer rows.Close()

	var items []string
	for rows.Next() {
		var item string
		if err := rows.Scan(&item); err != nil {
			return nil, err
		}
		items = append(items, item)
	}

	return items, rows.Err()
}

func (s *MatrixService) determineCoverageStatus(upstream, downstream []Link) string {
	totalLinks := len(upstream) + len(downstream)

	if totalLinks == 0 {
		return "none"
	} else if totalLinks >= coverageFullyTraced {
		return "full"
	}
	return "partial"
}

func (s *MatrixService) generateCoverageRecommendations(report *CoverageReport, untracedItems []string) []string {
	recommendations := []string{}

	if report.Overall.CoveragePercent < coverageCriticallyLow {
		recommendations = append(recommendations, fmt.Sprintf("Coverage is critically low (<%d%%). Prioritize creating traceability links.", coverageCriticallyLow))
	} else if report.Overall.CoveragePercent < coverageBelowTarget {
		recommendations = append(recommendations, fmt.Sprintf("Coverage is below target (%d%%). Continue adding traceability links.", coverageBelowTarget))
	}

	if len(untracedItems) > 0 {
		recommendations = append(recommendations, fmt.Sprintf("%d items have no traceability links. Start with the oldest items.", len(untracedItems)))
	}

	for itemType, metrics := range report.ByType {
		if metrics.CoveragePercent < coverageCriticallyLow {
			recommendations = append(recommendations, fmt.Sprintf("%s coverage is critically low (%.1f%%). Focus on this area.", itemType, metrics.CoveragePercent))
		}
	}

	if len(recommendations) == 0 {
		recommendations = append(recommendations, "Traceability coverage is good. Maintain current practices.")
	}

	return recommendations
}

func (s *MatrixService) generateGapRecommendations(analysis *GapAnalysis) []string {
	recommendations := []string{}

	if len(analysis.MissingForward) > 0 {
		recommendations = append(recommendations, fmt.Sprintf("%d requirements lack test coverage. Create test cases for validation.", len(analysis.MissingForward)))
	}

	if len(analysis.MissingBackward) > 0 {
		recommendations = append(recommendations, fmt.Sprintf("%d tests are not linked to requirements. Ensure all tests validate specific requirements.", len(analysis.MissingBackward)))
	}

	if len(analysis.Orphaned) > 0 {
		recommendations = append(recommendations, fmt.Sprintf("%d items are completely orphaned. Link them to the traceability matrix.", len(analysis.Orphaned)))
	}

	if len(recommendations) == 0 {
		recommendations = append(recommendations, "No traceability gaps detected. All items are properly linked.")
	}

	return recommendations
}
