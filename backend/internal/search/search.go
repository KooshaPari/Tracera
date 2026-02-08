package search

import (
	"context"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
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
