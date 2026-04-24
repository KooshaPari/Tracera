package traceability

import (
	"encoding/json"
	"fmt"

	"github.com/jackc/pgx/v5"
)

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
