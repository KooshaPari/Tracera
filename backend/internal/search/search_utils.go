package search

import (
	"context"
	"errors"
	"fmt"
	"strings"

	"github.com/kooshapari/tracertm-backend/internal/embeddings"
)

// hybridSearch combines full-text and vector search results
func (s *Engine) hybridSearch(ctx context.Context, req *Request) ([]Result, int, error) {
	// Perform both searches
	ftResults, _, err := s.fullTextSearch(ctx, req)
	if err != nil {
		return nil, 0, fmt.Errorf("full-text search failed: %w", err)
	}

	vecResults, _, err := s.vectorSearch(ctx, req)
	if err != nil {
		return nil, 0, fmt.Errorf("vector search failed: %w", err)
	}

	// Merge and deduplicate results
	merged := s.mergeResults(ftResults, vecResults, searchFullTextWeight, searchVectorWeight) // 60% full-text, 40% vector

	// Apply limit
	if len(merged) > req.Limit {
		merged = merged[:req.Limit]
	}

	return merged, len(merged), nil
}

// mergeResults combines and deduplicates results from multiple search types
func (s *Engine) mergeResults(ftResults, vecResults []Result, ftWeight, vecWeight float64) []Result {
	// Create a map to deduplicate by ID
	resultMap := make(map[string]Result)

	// Add full-text results with weighted score
	for _, result := range ftResults {
		result.Score *= ftWeight
		resultMap[result.ID] = result
	}

	// Add or merge vector results with weighted score
	for _, result := range vecResults {
		if existing, exists := resultMap[result.ID]; exists {
			// Combine scores
			existing.Score += result.Score * vecWeight
			resultMap[result.ID] = existing
		} else {
			result.Score *= vecWeight
			resultMap[result.ID] = result
		}
	}

	// Convert map to slice
	results := make([]Result, 0, len(resultMap))
	for _, result := range resultMap {
		results = append(results, result)
	}

	// Sort by combined score
	// Note: In production, use sort.Slice for proper sorting
	return results
}

// getSearchCount returns the total count of search results
func (s *Engine) getSearchCount(ctx context.Context, req *Request) (int, error) {
	query := `
		SELECT COUNT(*)
		FROM items
		WHERE
			($1 = '' OR search_vector @@ plainto_tsquery('english', $1))
			AND ($2 = '' OR project_id = $2::uuid)
			AND ($3::text[] IS NULL OR type = ANY($3))
			AND ($4::text[] IS NULL OR status = ANY($4))
			AND (deleted_at IS NULL OR $5 = true)
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

	var count int
	queryParam := req.Query
	if req.Type == TypeVector {
		queryParam = "" // Vector search doesn't use text query for counting
	}

	err := s.pool.QueryRow(ctx, query,
		queryParam,
		projectIDParam,
		itemTypesParam,
		statusParam,
		req.IncludeDeleted,
	).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("count query failed: %w", err)
	}

	return count, nil
}

// Suggest provides search suggestions based on partial input with fuzzy matching
func (s *Engine) Suggest(ctx context.Context, prefix string, projectID string, limit int) ([]string, error) {
	if limit <= 0 {
		limit = searchSuggestionDefaultLimit
	}
	if limit > searchSuggestionMaxLimit {
		limit = searchSuggestionMaxLimit
	}

	// Try fuzzy suggestions first using pg_trgm word_similarity
	query := `
		SELECT DISTINCT title, word_similarity($1, title) AS sim
		FROM items
		WHERE
			(title ILIKE $1 || '%' OR title % $1)
			AND ($2 = '' OR project_id = $2::uuid)
			AND deleted_at IS NULL
		ORDER BY sim DESC, title
		LIMIT $3
	`

	var projectIDParam interface{} = projectID
	if projectID == "" {
		projectIDParam = ""
	}

	rows, err := s.pool.Query(ctx, query, prefix, projectIDParam, limit)
	if err != nil {
		// Fall back to simple ILIKE if pg_trgm isn't available
		return s.suggestSimple(ctx, prefix, projectID, limit)
	}
	defer rows.Close()

	var suggestions []string
	for rows.Next() {
		var title string
		var sim float64
		if err := rows.Scan(&title, &sim); err != nil {
			return nil, fmt.Errorf("row scan failed: %w", err)
		}
		suggestions = append(suggestions, title)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("rows iteration failed: %w", err)
	}

	return suggestions, nil
}

// suggestSimple is a fallback for suggestions without pg_trgm
func (s *Engine) suggestSimple(ctx context.Context, prefix string, projectID string, limit int) ([]string, error) {
	query := `
		SELECT DISTINCT title
		FROM items
		WHERE
			title ILIKE $1
			AND ($2 = '' OR project_id = $2::uuid)
			AND deleted_at IS NULL
		ORDER BY title
		LIMIT $3
	`

	var projectIDParam interface{} = projectID
	if projectID == "" {
		projectIDParam = ""
	}

	rows, err := s.pool.Query(ctx, query, prefix+"%", projectIDParam, limit)
	if err != nil {
		return nil, fmt.Errorf("suggestion query failed: %w", err)
	}
	defer rows.Close()

	var suggestions []string
	for rows.Next() {
		var title string
		if err := rows.Scan(&title); err != nil {
			return nil, fmt.Errorf("row scan failed: %w", err)
		}
		suggestions = append(suggestions, title)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("rows iteration failed: %w", err)
	}

	return suggestions, nil
}

// ExtensionStatus holds the status of each search extension
type ExtensionStatus struct {
	PgTrgm        bool `json:"pg_trgm"` // Trigram fuzzy matching
	FuzzyStrMatch bool `json:"fuzzystrmatch"`
	Unaccent      bool `json:"unaccent"` // Accent-insensitive search
	Vector        bool `json:"vector"`   // pgvector for semantic search
}

// HealthCheck verifies search functionality is working
func (s *Engine) HealthCheck(ctx context.Context) error {
	status, err := s.GetExtensionStatus(ctx)
	if err != nil {
		return fmt.Errorf("failed to check extensions: %w", err)
	}

	// At minimum we need pg_trgm or vector for effective search
	if !status.PgTrgm && !status.Vector {
		return errors.New("neither pg_trgm nor vector extensions are available - search will be limited")
	}

	return nil
}

// GetExtensionStatus returns the status of all search-related PostgreSQL extensions
func (s *Engine) GetExtensionStatus(ctx context.Context) (*ExtensionStatus, error) {
	status := &ExtensionStatus{}

	// Check all extensions in one query
	query := `
		SELECT
			EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm') AS pg_trgm,
			EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'fuzzystrmatch') AS fuzzystrmatch,
			EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'unaccent') AS unaccent,
			EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector') AS vector
	`

	err := s.pool.QueryRow(ctx, query).Scan(
		&status.PgTrgm,
		&status.FuzzyStrMatch,
		&status.Unaccent,
		&status.Vector,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to query extensions: %w", err)
	}

	return status, nil
}

// rerankResults applies reranking to search results
func (s *Engine) rerankResults(ctx context.Context, query string, results []Result) ([]Result, error) {
	if s.reranker == nil {
		return results, nil
	}

	// Convert search results to documents for reranking
	documents := make([]embeddings.Document, len(results))
	for i, result := range results {
		documents[i] = embeddings.Document{
			ID:   result.ID,
			Text: result.Title + "\n\n" + result.Description,
			Metadata: map[string]interface{}{
				"original_score": result.Score,
				"type":           result.Type,
				"status":         result.Status,
			},
		}
	}

	// Perform reranking
	rerankResp, err := s.reranker.Rerank(ctx, &embeddings.RerankRequest{
		Query:           query,
		Documents:       documents,
		Model:           "",
		TopK:            0,
		ReturnDocuments: false, // We already have the documents
	})
	if err != nil {
		return results, err
	}

	// Create new results array in reranked order
	reranked := make([]Result, 0, len(rerankResp.Results))
	for _, rr := range rerankResp.Results {
		if rr.Index < len(results) {
			result := results[rr.Index]
			// Update score with reranked score
			result.Score = rr.RelevanceScore
			reranked = append(reranked, result)
		}
	}

	return reranked, nil
}

// BuildSearchQuery constructs a tsquery from user input
func BuildSearchQuery(input string) string {
	// Clean and prepare the input for PostgreSQL full-text search
	// Remove special characters, handle phrases, etc.
	cleaned := strings.TrimSpace(input)
	words := strings.Fields(cleaned)

	if len(words) == 0 {
		return ""
	}

	// Join words with & for AND search
	return strings.Join(words, " & ")
}
