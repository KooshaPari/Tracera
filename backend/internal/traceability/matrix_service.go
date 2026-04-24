// Package traceability provides services for traceability matrices.
package traceability

import (
	"context"
	"fmt"
	"log/slog"
	"time"

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
		defer func() {
			if cerr := br.Close(); cerr != nil {
				slog.Warn("failed to close batch result", "error", cerr)
			}
		}()

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
		defer func() {
			if cerr := br.Close(); cerr != nil {
				slog.Warn("failed to close batch result", "error", cerr)
			}
		}()

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
		defer func() {
			if cerr := br.Close(); cerr != nil {
				slog.Warn("failed to close batch result", "error", cerr)
			}
		}()

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
	defer func() {
		if cerr := br.Close(); cerr != nil {
			slog.Warn("failed to close batch result", "error", cerr)
		}
	}()

	resultPtr, err := s.scanItemTraceability(br, itemID)
	if err != nil {
		return nil, err
	}
	result = *resultPtr

	// Cache for 5 minutes
	if err := s.cache.Set(ctx, cacheKey, result); err != nil {
		slog.Error("Failed to cache item traceability", "error", err)
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
		slog.Error("Failed to cache change impact", "error", err)
	}

	return &result, nil
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

func (s *MatrixService) applyMatrixCoverage(matrix *Matrix, total, traced int, percent float64, untraced []string) {
	matrix.Coverage = &CoverageMetrics{
		TotalRequirements:  total,
		TracedRequirements: traced,
		CoveragePercent:    percent,
		UntracedItems:      untraced,
	}
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
