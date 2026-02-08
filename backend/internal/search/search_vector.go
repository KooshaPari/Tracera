package search

import (
	"context"
	"errors"
	"fmt"
	"strings"

	"github.com/kooshapari/tracertm-backend/internal/embeddings"
)

// vectorSearch performs semantic search using pgvector embeddings
//
//nolint:funlen
func (s *Engine) vectorSearch(ctx context.Context, req *Request) ([]Result, int, error) {
	// Generate embedding for the query using the configured provider
	var queryEmbedding embeddings.EmbeddingVector
	var err error

	if s.embeddingProvider != nil {
		embResp, embErr := s.embeddingProvider.Embed(ctx, &embeddings.EmbeddingRequest{
			Texts:     []string{req.Query},
			InputType: "query",
		})
		if embErr != nil {
			return nil, 0, fmt.Errorf("failed to generate query embedding: %w", embErr)
		}

		if len(embResp.Embeddings) == 0 {
			return nil, 0, errors.New("no embedding generated for query")
		}

		queryEmbedding = embResp.Embeddings[0]
	} else {
		// Fallback to dummy embedding if no provider is configured
		// This allows the system to work without embeddings configured
		return s.fullTextSearch(ctx, req) // Fall back to full-text search
	}

	// Convert embedding to pgvector format
	embeddingStr := vectorToString(queryEmbedding)

	query := `
		SELECT
			id, project_id, title, description, type, status,
			CAST(priority AS TEXT) as priority,
			metadata, created_at, updated_at,
			1 - (embedding <=> $1::vector) as score
		FROM items
		WHERE
			embedding IS NOT NULL
			AND ($2 = '' OR project_id = $2::uuid)
			AND ($3::text[] IS NULL OR type = ANY($3))
			AND ($4::text[] IS NULL OR status = ANY($4))
			AND (deleted_at IS NULL OR $5 = true)
			AND (1 - (embedding <=> $1::vector)) >= $6
		ORDER BY embedding <=> $1::vector
		LIMIT $7 OFFSET $8
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
		embeddingStr,
		projectIDParam,
		itemTypesParam,
		statusParam,
		req.IncludeDeleted,
		req.MinScore,
		req.Limit,
		req.Offset,
	)
	if err != nil {
		return nil, 0, fmt.Errorf("vector query execution failed: %w", err)
	}
	defer rows.Close()

	var results []Result
	for rows.Next() {
		var r Result
		var metadataJSON []byte

		err := rows.Scan(
			&r.ID, &r.ProjectID, &r.Title, &r.Description,
			&r.Type, &r.Status, &r.Priority, &metadataJSON,
			&r.CreatedAt, &r.UpdatedAt, &r.Score,
		)
		if err != nil {
			return nil, 0, fmt.Errorf("row scan failed: %w", err)
		}

		results = append(results, r)
	}

	if err := rows.Err(); err != nil {
		return nil, 0, fmt.Errorf("rows iteration failed: %w", err)
	}

	totalCount, err := s.getSearchCount(ctx, req)
	if err != nil {
		return results, len(results), nil
	}

	return results, totalCount, nil
}

// vectorToString converts an embedding vector to PostgreSQL vector format
func vectorToString(vec embeddings.EmbeddingVector) string {
	if len(vec) == 0 {
		return "[]"
	}
	var b strings.Builder
	b.WriteString("[")
	for i, val := range vec {
		if i > 0 {
			b.WriteString(",")
		}
		b.WriteString(fmt.Sprintf("%f", val))
	}
	b.WriteString("]")
	return b.String()
}
