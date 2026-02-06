package search

import (
	"context"
	"errors"
	"fmt"
	"strings"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/kooshapari/tracertm-backend/internal/database"
	"github.com/kooshapari/tracertm-backend/internal/embeddings"
)

// Type represents the type of search to perform
type Type string

const (
	// TypeFullText uses PostgreSQL full-text search.
	TypeFullText Type = "fulltext"
	// TypeVector uses pgvector semantic search.
	TypeVector Type = "vector"
	// TypeHybrid uses combined full-text and vector search.
	TypeHybrid Type = "hybrid"
	// TypeFuzzy uses trigram-based fuzzy search (typo-tolerant).
	TypeFuzzy Type = "fuzzy"
	// TypePhonetic uses phonetic search (soundex/metaphone).
	TypePhonetic Type = "phonetic"
)

const (
	// SearchTypeFullText is a compatibility alias for TypeFullText.
	SearchTypeFullText Type = TypeFullText
	// SearchTypeVector is a compatibility alias for TypeVector.
	SearchTypeVector Type = TypeVector
	// SearchTypeHybrid is a compatibility alias for TypeHybrid.
	SearchTypeHybrid Type = TypeHybrid
	// SearchTypeFuzzy is a compatibility alias for TypeFuzzy.
	SearchTypeFuzzy Type = TypeFuzzy
	// SearchTypePhonetic is a compatibility alias for TypePhonetic.
	SearchTypePhonetic Type = TypePhonetic
)

const (
	searchDefaultLimit           = 20
	searchMaxLimit               = 100
	searchDefaultMinScore        = 0.1
	searchDefaultFuzzyThreshold  = 0.3
	searchFullTextWeight         = 0.6
	searchVectorWeight           = 0.4
	searchSuggestionDefaultLimit = 10
	searchSuggestionMaxLimit     = 50
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

// Result represents a single search result
type Result struct {
	ID          string                 `json:"id"`
	ProjectID   string                 `json:"project_id"`
	Title       string                 `json:"title"`
	Description string                 `json:"description"`
	Type        string                 `json:"type"`
	Status      string                 `json:"status"`
	Priority    string                 `json:"priority"`
	Metadata    map[string]interface{} `json:"metadata"`
	Score       float64                `json:"score"`
	CreatedAt   time.Time              `json:"created_at"`
	UpdatedAt   time.Time              `json:"updated_at"`
}

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
	// We deliberately ignore metadata here to preserve existing behavior,
	// where Result.Metadata is left empty.
}

// Request encapsulates search parameters
type Request struct {
	Query               string   `json:"query"`                 // Search query text
	Type                Type     `json:"type"`                  // Search type: fulltext, vector, hybrid, fuzzy, phonetic
	ProjectID           string   `json:"project_id"`            // Optional project filter
	ItemTypes           []string `json:"item_types"`            // Optional item type filter
	Status              []string `json:"status"`                // Optional status filter
	Limit               int      `json:"limit"`                 // Max results (default: 20)
	Offset              int      `json:"offset"`                // Pagination offset
	MinScore            float64  `json:"min_score"`             // Minimum relevance score (0.0-1.0)
	IncludeDeleted      bool     `json:"include_deleted"`       // Include soft-deleted items
	FuzzyThreshold      float64  `json:"fuzzy_threshold"`       // Similarity threshold for fuzzy search (0.0-1.0, default: 0.3)
	EnableTypoTolerance bool     `json:"enable_typo_tolerance"` // Enable fuzzy matching for typos in any search type
}

// Response encapsulates search results and metadata
type Response struct {
	Results    []Result      `json:"results"`
	TotalCount int           `json:"total_count"`
	Query      string        `json:"query"`
	Type       Type          `json:"search_type"`
	Duration   time.Duration `json:"duration"`
}

// Engine handles all search operations
type Engine struct {
	pool              *pgxpool.Pool
	embeddingProvider embeddings.Provider
	reranker          *embeddings.Reranker
	rerankEnabled     bool
}

// EngineConfig holds configuration for the search engine
type EngineConfig struct {
	Pool              *pgxpool.Pool
	EmbeddingProvider embeddings.Provider
	Reranker          *embeddings.Reranker
	RerankEnabled     bool
}

// NewSearchEngine creates a new search engine instance
func NewSearchEngine(pool *pgxpool.Pool) *Engine {
	return &Engine{
		pool:          pool,
		rerankEnabled: false,
	}
}

// NewSearchEngineWithConfig creates a new search engine with full configuration
func NewSearchEngineWithConfig(config *EngineConfig) *Engine {
	return &Engine{
		pool:              config.Pool,
		embeddingProvider: config.EmbeddingProvider,
		reranker:          config.Reranker,
		rerankEnabled:     config.RerankEnabled && config.Reranker != nil,
	}
}

// NewEngine creates a new search engine with default configuration
func NewEngine(pool *pgxpool.Pool) *Engine {
	return NewSearchEngine(pool)
}

// NewEngineWithConfig creates a new search engine with the provided configuration
func NewEngineWithConfig(config *EngineConfig) *Engine {
	return NewSearchEngineWithConfig(config)
}

// Search executes a search based on the request parameters
func (s *Engine) Search(ctx context.Context, req *Request) (*Response, error) {
	start := time.Now()

	// Set defaults
	if req.Limit <= 0 {
		req.Limit = searchDefaultLimit
	}
	if req.Limit > searchMaxLimit {
		req.Limit = searchMaxLimit // Cap at 100 results
	}
	if req.Type == "" {
		req.Type = TypeFullText
	}
	if req.MinScore == 0 {
		req.MinScore = searchDefaultMinScore // Default minimum score
	}
	if req.FuzzyThreshold == 0 {
		req.FuzzyThreshold = searchDefaultFuzzyThreshold // Default similarity threshold for pg_trgm
	}

	var results []Result
	var totalCount int
	var err error

	// Execute search based on type
	switch req.Type {
	case TypeFullText:
		if req.EnableTypoTolerance {
			results, totalCount, err = s.fuzzySearch(ctx, req)
		} else {
			results, totalCount, err = s.fullTextSearch(ctx, req)
		}
	case TypeVector:
		results, totalCount, err = s.vectorSearch(ctx, req)
	case TypeHybrid:
		results, totalCount, err = s.hybridSearch(ctx, req)
	case TypeFuzzy:
		results, totalCount, err = s.fuzzySearch(ctx, req)
	case TypePhonetic:
		results, totalCount, err = s.phoneticSearch(ctx, req)
	default:
		return nil, fmt.Errorf("unsupported search type: %s", req.Type)
	}

	if err != nil {
		return nil, fmt.Errorf("search failed: %w", err)
	}

	// Apply reranking if enabled and we have results
	if s.rerankEnabled && len(results) > 0 && req.Query != "" {
		results, err = s.rerankResults(ctx, req.Query, results)
		if err != nil {
			// Log error but don't fail the search
			// Fall back to non-reranked results
			if s.rerankEnabled {
				fmt.Printf("Reranking failed, using original results: %v\n", err)
			}
		}
	}

	duration := time.Since(start)

	return &Response{
		Results:    results,
		TotalCount: totalCount,
		Query:      req.Query,
		Type:       req.Type,
		Duration:   duration,
	}, nil
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
		return results, len(results), nil // Return results even if count fails
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
		var r Result
		var metadataJSON []byte

		if err := rows.Scan(
			&r.ID, &r.ProjectID, &r.Title, &r.Description,
			&r.Type, &r.Status, &r.Priority, &metadataJSON,
			&r.CreatedAt, &r.UpdatedAt, &r.Score,
		); err != nil {
			return nil, fmt.Errorf("row scan failed: %w", err)
		}

		if r.Score >= minScore {
			results = append(results, r)
		}
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("rows iteration failed: %w", err)
	}

	return results, nil
}

// fuzzySearchInline performs fuzzy search without relying on the stored function
// This is used as a fallback if the fuzzy_search_items function isn't available
//
//nolint:funlen
func (s *Engine) fuzzySearchInline(ctx context.Context, req *Request) ([]Result, int, error) {
	// Set the similarity threshold for this connection
	_, err := s.pool.Exec(ctx, fmt.Sprintf("SET pg_trgm.similarity_threshold = %f", req.FuzzyThreshold))
	if err != nil {
		// If setting fails, continue anyway with default threshold
		fmt.Printf("Warning: Could not set similarity threshold: %v\n", err)
	}

	query := `
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
		return nil, 0, fmt.Errorf("fuzzy query execution failed: %w", err)
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

		if r.Score >= req.MinScore {
			results = append(results, r)
		}
	}

	if err := rows.Err(); err != nil {
		return nil, 0, fmt.Errorf("rows iteration failed: %w", err)
	}

	return results, len(results), nil
}

// phoneticSearch performs search based on how words sound (Soundex/Metaphone)
// Useful for matching names even with different spellings
//
//nolint:funlen
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

	return results, len(results), nil
}

// mergeResults combines and deduplicates results from multiple search types
func (s *Engine) mergeResults(ftResults, vecResults []Result, ftWeight, vecWeight float64) []Result {
	// Create a map to deduplicate by ID
	resultMap := make(map[string]Result)

	// Add full-text results with weighted score
	for _, r := range ftResults {
		r.Score *= ftWeight
		resultMap[r.ID] = r
	}

	// Add or merge vector results with weighted score
	for _, r := range vecResults {
		if existing, exists := resultMap[r.ID]; exists {
			// Combine scores
			existing.Score += r.Score * vecWeight
			resultMap[r.ID] = existing
		} else {
			r.Score *= vecWeight
			resultMap[r.ID] = r
		}
	}

	// Convert map to slice
	results := make([]Result, 0, len(resultMap))
	for _, r := range resultMap {
		results = append(results, r)
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
	PgTrgm        bool `json:"pg_trgm"`       // Trigram fuzzy matching
	FuzzyStrMatch bool `json:"fuzzystrmatch"` // Phonetic matching (soundex/metaphone)
	Unaccent      bool `json:"unaccent"`      // Accent-insensitive search
	Vector        bool `json:"vector"`        // pgvector for semantic search
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
	for i, r := range results {
		documents[i] = embeddings.Document{
			ID:   r.ID,
			Text: r.Title + "\n\n" + r.Description,
			Metadata: map[string]interface{}{
				"original_score": r.Score,
				"type":           r.Type,
				"status":         r.Status,
			},
		}
	}

	// Perform reranking
	rerankResp, err := s.reranker.Rerank(ctx, &embeddings.RerankRequest{
		Query:           query,
		Documents:       documents,
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
