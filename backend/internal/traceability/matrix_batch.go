package traceability

import "github.com/jackc/pgx/v5"

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
