package search

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5"
)

// fuzzySearch performs typo-tolerant search using PostgreSQL pg_trgm extension
// This uses trigram similarity to match even with spelling mistakes
func (s *Engine) fuzzySearch(ctx context.Context, req *Request) ([]Result, int, error) {
	// Use the fuzzy_search_items function we created in the migration
	// This combines full-text search with trigram similarity
	query := `
		SELECT
			id, project_id, title, description, type, status,
			CAST(priority AS TEXT) as priority,
			metadata, created_at, updated_at,
			combined_score as score
		FROM fuzzy_search_items($1, $2, $3, $4)
		WHERE ($5::text[] IS NULL OR type = ANY($5))
		  AND ($6::text[] IS NULL OR status = ANY($6))
		OFFSET $7
	`

	projectUUID, itemTypesParam, statusParam := buildFuzzySearchParams(req)

	rows, err := s.pool.Query(ctx, query,
		req.Query,
		projectUUID,
		req.FuzzyThreshold,
		req.Limit,
		itemTypesParam,
		statusParam,
		req.Offset,
	)
	if err != nil {
		// If the function doesn't exist, fall back to inline fuzzy query
		return s.fuzzySearchInline(ctx, req)
	}
	defer rows.Close()

	results, err := scanFuzzySearchRows(rows, req.MinScore)
	if err != nil {
		return nil, 0, err
	}

	return results, len(results), nil
}

func buildFuzzySearchParams(req *Request) (interface{}, interface{}, interface{}) {
	var projectUUID interface{}
	if req.ProjectID != "" {
		projectUUID = req.ProjectID
	}

	var itemTypesParam interface{}
	if len(req.ItemTypes) > 0 {
		itemTypesParam = req.ItemTypes
	}

	var statusParam interface{}
	if len(req.Status) > 0 {
		statusParam = req.Status
	}

	return projectUUID, itemTypesParam, statusParam
}

func scanFuzzySearchRows(rows pgx.Rows, minScore float64) ([]Result, error) {
	var results []Result
	for rows.Next() {
		var result Result
		var metadataJSON []byte

		if err := rows.Scan(
			&result.ID, &result.ProjectID, &result.Title, &result.Description,
			&result.Type, &result.Status, &result.Priority, &metadataJSON,
			&result.CreatedAt, &result.UpdatedAt, &result.Score,
		); err != nil {
			return nil, fmt.Errorf("row scan failed: %w", err)
		}

		if result.Score >= minScore {
			results = append(results, result)
		}
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("rows iteration failed: %w", err)
	}

	return results, nil
}

// fuzzySearchInline performs fuzzy search without relying on the stored function
// This is used as a fallback if the fuzzy_search_items function isn't available
func (s *Engine) fuzzySearchInline(ctx context.Context, req *Request) ([]Result, int, error) {
	if err := s.setFuzzyThreshold(ctx, req.FuzzyThreshold); err != nil {
		// If setting fails, continue anyway with default threshold
		_ = err
	}

	query := fuzzyInlineQuery()
	projectIDParam, itemTypesParam, statusParam := buildFuzzySearchParams(req)

	rows, err := s.pool.Query(ctx, query,
		req.Query, projectIDParam, itemTypesParam, statusParam, req.Limit, req.Offset,
	)
	if err != nil {
		return nil, 0, fmt.Errorf("fuzzy query execution failed: %w", err)
	}
	defer rows.Close()

	results, err := scanFuzzySearchRows(rows, req.MinScore)
	if err != nil {
		return nil, 0, err
	}

	return results, len(results), nil
}

func (s *Engine) setFuzzyThreshold(ctx context.Context, threshold float64) error {
	_, err := s.pool.Exec(ctx, fmt.Sprintf("SET pg_trgm.similarity_threshold = %f", threshold))
	return err
}

func fuzzyInlineQuery() string {
	return `
		SELECT
			id, project_id, title, description, type, status,
			CAST(priority AS TEXT) as priority,
			metadata, created_at, updated_at,
			(
				0.5 * COALESCE(ts_rank(search_vector, plainto_tsquery('english', $1)), 0) +
				0.5 * GREATEST(
					COALESCE(similarity(title, $1), 0),
					COALESCE(similarity(description, $1), 0)
				)
			) as score
		FROM items
		WHERE
			deleted_at IS NULL
			AND ($2 = '' OR project_id = $2::uuid)
			AND ($3::text[] IS NULL OR type = ANY($3))
			AND ($4::text[] IS NULL OR status = ANY($4))
			AND (
				search_vector @@ plainto_tsquery('english', $1)
				OR title % $1
				OR description % $1
			)
		ORDER BY score DESC
		LIMIT $5 OFFSET $6
	`
}

// phoneticSearch performs search based on how words sound (Soundex/Metaphone)
// Useful for matching names even with different spellings
func (s *Engine) phoneticSearch(ctx context.Context, req *Request) ([]Result, int, error) {
	query := `
		SELECT
			id, project_id, title, description, type, status,
			CAST(priority AS TEXT) as priority,
			metadata, created_at, updated_at,
			CASE
				WHEN metaphone(title, 10) = metaphone($1, 10) THEN 1.0
				WHEN soundex(title) = soundex($1) THEN 0.8
				ELSE 0.5
			END as score
		FROM items
		WHERE
			deleted_at IS NULL
			AND ($2 = '' OR project_id = $2::uuid)
			AND ($3::text[] IS NULL OR type = ANY($3))
			AND ($4::text[] IS NULL OR status = ANY($4))
			AND (
				metaphone(title, 10) = metaphone($1, 10)
				OR soundex(title) = soundex($1)
			)
		ORDER BY score DESC
		LIMIT $5 OFFSET $6
	`

	var projectIDParam interface{} = req.ProjectID
	if req.ProjectID == "" {
		projectIDParam = ""
	}

	var itemTypesParam interface{}
	if len(req.ItemTypes) > 0 {
		itemTypesParam = req.ItemTypes
	}

	var statusParam interface{}
	if len(req.Status) > 0 {
		statusParam = req.Status
	}

	rows, err := s.pool.Query(ctx, query,
		req.Query,
		projectIDParam,
		itemTypesParam,
		statusParam,
		req.Limit,
		req.Offset,
	)
	if err != nil {
		return nil, 0, fmt.Errorf("phonetic query execution failed: %w", err)
	}
	defer rows.Close()

	var results []Result
	for rows.Next() {
		var result Result
		var metadataJSON []byte

		err := rows.Scan(
			&result.ID, &result.ProjectID, &result.Title, &result.Description,
			&result.Type, &result.Status, &result.Priority, &metadataJSON,
			&result.CreatedAt, &result.UpdatedAt, &result.Score,
		)
		if err != nil {
			return nil, 0, fmt.Errorf("row scan failed: %w", err)
		}

		results = append(results, result)
	}

	if err := rows.Err(); err != nil {
		return nil, 0, fmt.Errorf("rows iteration failed: %w", err)
	}

	return results, len(results), nil
}
