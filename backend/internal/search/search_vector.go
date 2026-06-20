package search

import (
	"context"
	"errors"
	"fmt"
	"strings"

	"github.com/kooshapari/tracertm-backend/internal/embeddings"
)

// vectorSearch performs semantic search using pgvector embeddings
func (s *Engine) vectorSearch(ctx context.Context, req *Request) ([]Result, int, error) {
	queryEmbedding, err := s.getQueryEmbedding(ctx, req)
	if err != nil {
		return nil, 0, err
	}
	if queryEmbedding == nil {
		return s.fullTextSearch(ctx, req)
	}

	embeddingStr := vectorToString(queryEmbedding)
	results, err := s.executeVectorQuery(ctx, req, embeddingStr)
	if err != nil {
		return nil, 0, err
	}

	totalCount, err := s.getSearchCount(ctx, req)
	if err != nil {
		return results, len(results), err
	}

	return results, totalCount, nil
}

func (s *Engine) getQueryEmbedding(ctx context.Context, req *Request) (embeddings.EmbeddingVector, error) {
	if s.embeddingProvider == nil {
		return nil, nil
	}

	embResp, err := s.embeddingProvider.Embed(ctx, &embeddings.EmbeddingRequest{
		Texts:     []string{req.Query},
		Model:     "",
		InputType: "query",
	})
	if err != nil {
		return nil, fmt.Errorf("failed to generate query embedding: %w", err)
	}

	if len(embResp.Embeddings) == 0 {
		return nil, errors.New("no embedding generated for query")
	}

	return embResp.Embeddings[0], nil
}

func (s *Engine) executeVectorQuery(ctx context.Context, req *Request, embeddingStr string) ([]Result, error) {
	query := vectorSearchQuery()
	projectIDParam, itemTypesParam, statusParam := buildFuzzySearchParams(req)

	rows, err := s.pool.Query(ctx, query,
		embeddingStr, projectIDParam, itemTypesParam, statusParam,
		req.IncludeDeleted, req.MinScore, req.Limit, req.Offset,
	)
	if err != nil {
		return nil, fmt.Errorf("vector query execution failed: %w", err)
	}
	defer rows.Close()

	return scanFuzzySearchRows(rows, 0)
}

func vectorSearchQuery() string {
	return `
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
}

// vectorToString converts an embedding vector to PostgreSQL vector format
func vectorToString(vec embeddings.EmbeddingVector) string {
	if len(vec) == 0 {
		return "[]"
	}
	var buf strings.Builder
	buf.WriteString("[")
	for i, val := range vec {
		if i > 0 {
			buf.WriteString(",")
		}
		buf.WriteString(fmt.Sprintf("%f", val))
	}
	buf.WriteString("]")
	return buf.String()
}
