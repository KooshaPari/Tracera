package search

import (
	"context"
	"fmt"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/database"
)

const fullTextSearchQuery = `
	SELECT
		id, project_id, title, description, type, status,
		CAST(priority AS TEXT) as priority,
		metadata, created_at, updated_at,
		ts_rank(search_vector, plainto_tsquery('english', $1)) as score
	FROM items
	WHERE
		search_vector @@ plainto_tsquery('english', $1)
		AND ($2 = '' OR project_id = $2::uuid)
		AND ($3::text[] IS NULL OR type = ANY($3))
		AND ($4::text[] IS NULL OR status = ANY($4))
		AND (deleted_at IS NULL OR $5 = true)
	ORDER BY score DESC, updated_at DESC
	LIMIT $6 OFFSET $7
`

type fullTextRow struct {
	ID          string    `db:"id"`
	ProjectID   string    `db:"project_id"`
	Title       string    `db:"title"`
	Description string    `db:"description"`
	Type        string    `db:"type"`
	Status      string    `db:"status"`
	Priority    string    `db:"priority"`
	CreatedAt   time.Time `db:"created_at"`
	UpdatedAt   time.Time `db:"updated_at"`
	Score       float64   `db:"score"`
}

// fullTextSearch performs PostgreSQL full-text search using tsvector
func (s *Engine) fullTextSearch(ctx context.Context, req *Request) ([]Result, int, error) {
	projectIDParam, itemTypesParam, statusParam := buildFullTextParams(req)
	rows, err := s.fetchFullTextRows(ctx, req, projectIDParam, itemTypesParam, statusParam)
	if err != nil {
		return nil, 0, err
	}

	results := mapFullTextResults(rows, req.MinScore)

	// Get total count
	totalCount, err := s.getSearchCount(ctx, req)
	if err != nil {
		return results, len(results), err
	}

	return results, totalCount, nil
}

func buildFullTextParams(req *Request) (interface{}, interface{}, interface{}) {
	projectIDParam := interface{}(req.ProjectID)
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

	return projectIDParam, itemTypesParam, statusParam
}

func (s *Engine) fetchFullTextRows(
	ctx context.Context,
	req *Request,
	projectIDParam interface{},
	itemTypesParam interface{},
	statusParam interface{},
) ([]fullTextRow, error) {
	var rows []fullTextRow
	if err := database.Select(ctx, s.pool, &rows, fullTextSearchQuery,
		req.Query,
		projectIDParam,
		itemTypesParam,
		statusParam,
		req.IncludeDeleted,
		req.Limit,
		req.Offset,
	); err != nil {
		return nil, fmt.Errorf("query execution failed: %w", err)
	}
	return rows, nil
}

func mapFullTextResults(rows []fullTextRow, minScore float64) []Result {
	results := make([]Result, 0, len(rows))
	for _, row := range rows {
		if row.Score < minScore {
			continue
		}
		results = append(results, Result{
			ID:          row.ID,
			ProjectID:   row.ProjectID,
			Title:       row.Title,
			Description: row.Description,
			Type:        row.Type,
			Status:      row.Status,
			Priority:    row.Priority,
			Score:       row.Score,
			CreatedAt:   row.CreatedAt,
			UpdatedAt:   row.UpdatedAt,
		})
	}
	return results
}
