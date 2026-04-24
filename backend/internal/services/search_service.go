package services

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"strconv"
	"strings"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/search"
)

const maxSearchItemIDs = 100

// SearchService handles business logic for search operations
type SearchService interface {
	// Search operations
	Search(ctx context.Context, req *SearchServiceRequest) (*SearchServiceResponse, error)
	SearchItems(ctx context.Context, query string, filters SearchFilters) ([]search.Result, error)
	SearchProjects(ctx context.Context, query string) ([]search.Result, error)
	SearchItemsAdvanced(ctx context.Context, query string, searchType search.Type, filters SearchFilters) ([]search.Result, error)
	Suggest(ctx context.Context, prefix, projectID string, limit int) ([]string, error)
	SuggestItems(ctx context.Context, prefix, projectID string, limit int) ([]string, error)

	// Index operations
	IndexItem(ctx context.Context, itemID string) error
	BatchIndex(ctx context.Context, itemIDs []string) (*BatchIndexResult, error)
	DeleteIndex(ctx context.Context, itemID string) error
	ReindexAll(ctx context.Context) error

	// Health and stats
	GetIndexStats(ctx context.Context) (*IndexStatsResponse, error)
	GetSearchHealth(ctx context.Context) (*SearchHealthResponse, error)
}

// SearchServiceRequest represents a service-level search request
type SearchServiceRequest struct {
	Query               string
	Type                search.Type
	ProjectID           string
	ItemTypes           []string
	Status              []string
	Limit               int
	Offset              int
	MinScore            float64
	IncludeDeleted      bool
	FuzzyThreshold      float64
	EnableTypoTolerance bool
}

// SearchServiceResponse represents a service-level search response
type SearchServiceResponse struct {
	Results    []search.Result
	TotalCount int
	Query      string
	Type       search.Type
}

// BatchIndexResult represents batch indexing results
type BatchIndexResult struct {
	Queued int
	Failed int
	Total  int
}

// IndexStatsResponse represents index statistics
type IndexStatsResponse struct {
	TotalJobs      int64
	CompletedJobs  int64
	FailedJobs     int64
	QueueSize      int
	ProcessingRate float64
	LastIndexedAt  time.Time
	LastError      string
}

// SearchHealthResponse represents search health status
type SearchHealthResponse struct {
	Status       string
	Extensions   map[string]bool
	Capabilities map[string]bool
	SearchTypes  []string
}

// searchEngineForService is the subset of search operations the service needs (allows mocks in tests)
type searchEngineForService interface {
	Search(ctx context.Context, req *search.Request) (*search.Response, error)
	Suggest(ctx context.Context, prefix, projectID string, limit int) ([]string, error)
	GetExtensionStatus(ctx context.Context) (*search.ExtensionStatus, error)
	HealthCheck(ctx context.Context) error
}

// searchIndexerForService is the subset of indexer operations the service needs (allows mocks in tests)
type searchIndexerForService interface {
	QueueIndex(itemID string, priority int) error
	QueueDelete(itemID string) error
	ReindexAll(ctx context.Context) error
	Stats() search.IndexerStats
}

// searchService implements SearchService
type searchService struct {
	engine              searchEngineForService
	indexer             searchIndexerForService
	cache               cache.Cache
	publisher           *nats.EventPublisher
	realtimeBroadcaster interface{}
	authProvider        interface{}
}

// NewSearchService creates a new search service
func NewSearchService(
	engine searchEngineForService,
	indexer searchIndexerForService,
	redisCache cache.Cache,
	eventPublisher *nats.EventPublisher,
	realtimeBroadcaster interface{},
	authProvider interface{},
) SearchService {
	return &searchService{
		engine:              engine,
		indexer:             indexer,
		cache:               redisCache,
		publisher:           eventPublisher,
		realtimeBroadcaster: realtimeBroadcaster,
		authProvider:        authProvider,
	}
}

// Search performs a search operation with caching
func (s *searchService) Search(ctx context.Context, req *SearchServiceRequest) (*SearchServiceResponse, error) {
	// Validate query
	if strings.TrimSpace(req.Query) == "" {
		return nil, errors.New("query parameter is required")
	}

	// Convert to internal search request
	searchReq := &search.Request{
		Query:               req.Query,
		Type:                req.Type,
		ProjectID:           req.ProjectID,
		ItemTypes:           req.ItemTypes,
		Status:              req.Status,
		Limit:               req.Limit,
		Offset:              req.Offset,
		MinScore:            req.MinScore,
		IncludeDeleted:      req.IncludeDeleted,
		FuzzyThreshold:      req.FuzzyThreshold,
		EnableTypoTolerance: req.EnableTypoTolerance,
	}

	// Try to get from cache first
	cacheKey := s.getSearchCacheKey(searchReq)
	var cachedResults *search.Response
	if s.cache != nil {
		if err := s.cache.Get(ctx, cacheKey, &cachedResults); err == nil && cachedResults != nil {
			return &SearchServiceResponse{
				Results:    cachedResults.Results,
				TotalCount: cachedResults.TotalCount,
				Query:      cachedResults.Query,
				Type:       cachedResults.SearchType,
			}, nil
		}
	}

	// Execute search
	results, err := s.engine.Search(ctx, searchReq)
	if err != nil {
		return nil, fmt.Errorf("search failed: %w", err)
	}

	// Cache the results
	if s.cache != nil {
		go func() {
			if err := s.cache.Set(ctx, cacheKey, results); err != nil {
				slog.Error("Failed to cache search results", "error", err)
			}
		}()
	}

	return &SearchServiceResponse{
		Results:    results.Results,
		TotalCount: results.TotalCount,
		Query:      results.Query,
		Type:       results.SearchType,
	}, nil
}

// Suggest returns search suggestions based on a prefix
func (s *searchService) Suggest(ctx context.Context, prefix, projectID string, limit int) ([]string, error) {
	if strings.TrimSpace(prefix) == "" {
		return nil, errors.New("prefix parameter is required")
	}

	suggestions, err := s.engine.Suggest(ctx, prefix, projectID, limit)
	if err != nil {
		return nil, fmt.Errorf("suggestion failed: %w", err)
	}

	return suggestions, nil
}

// IndexItem queues an item for indexing
func (s *searchService) IndexItem(_ context.Context, itemID string) error {
	if itemID == "" {
		return errors.New("item ID is required")
	}

	if err := s.indexer.QueueIndex(itemID, 1); err != nil {
		return fmt.Errorf("failed to queue item for indexing: %w", err)
	}

	return nil
}

// BatchIndex queues multiple items for indexing
func (s *searchService) BatchIndex(_ context.Context, itemIDs []string) (*BatchIndexResult, error) {
	if len(itemIDs) == 0 {
		return nil, errors.New("no item IDs provided")
	}

	if len(itemIDs) > maxSearchItemIDs {
		return nil, errors.New("maximum 100 items can be indexed at once")
	}

	queued := 0
	failed := 0
	for _, itemID := range itemIDs {
		if err := s.indexer.QueueIndex(itemID, 1); err != nil {
			failed++
		} else {
			queued++
		}
	}

	return &BatchIndexResult{
		Queued: queued,
		Failed: failed,
		Total:  len(itemIDs),
	}, nil
}

// DeleteIndex queues an item for index deletion
func (s *searchService) DeleteIndex(_ context.Context, itemID string) error {
	if itemID == "" {
		return errors.New("item ID is required")
	}

	if err := s.indexer.QueueDelete(itemID); err != nil {
		return fmt.Errorf("failed to queue item for index deletion: %w", err)
	}

	return nil
}

// ReindexAll starts a full reindex operation
func (s *searchService) ReindexAll(ctx context.Context) error {
	if err := s.indexer.ReindexAll(ctx); err != nil {
		return fmt.Errorf("failed to start reindexing: %w", err)
	}

	return nil
}

// GetIndexStats returns current indexing statistics
func (s *searchService) GetIndexStats(_ context.Context) (*IndexStatsResponse, error) {
	stats := s.indexer.Stats()

	return &IndexStatsResponse{
		TotalJobs:      stats.TotalJobs,
		CompletedJobs:  stats.CompletedJobs,
		FailedJobs:     stats.FailedJobs,
		QueueSize:      stats.QueueSize,
		ProcessingRate: stats.ProcessingRate,
		LastIndexedAt:  stats.LastIndexedAt,
		LastError:      stats.LastError,
	}, nil
}

// GetSearchHealth returns the health status of search services
func (s *searchService) GetSearchHealth(ctx context.Context) (*SearchHealthResponse, error) {
	// Get extension status
	extStatus, err := s.engine.GetExtensionStatus(ctx)
	if err != nil {
		return &SearchHealthResponse{
			Status:       "unhealthy",
			Extensions:   nil,
			Capabilities: nil,
			SearchTypes:  nil,
		}, err
	}

	// Check overall health
	if err := s.engine.HealthCheck(ctx); err != nil {
		return &SearchHealthResponse{
			Status:       "unhealthy",
			Extensions:   s.convertExtensionStatus(extStatus),
			Capabilities: nil,
			SearchTypes:  nil,
		}, err
	}

	// Determine available search capabilities based on extensions
	capabilities := map[string]bool{
		"fulltext":  true,                    // Always available via PostgreSQL
		"fuzzy":     extStatus.PgTrgm,        // Requires pg_trgm
		"phonetic":  extStatus.FuzzyStrMatch, // Requires fuzzystrmatch
		"accents":   extStatus.Unaccent,      // Requires unaccent
		"vector":    extStatus.Vector,        // Requires pgvector
		"hybrid":    extStatus.Vector,        // Requires pgvector
		"reranking": s.engine != nil,         // Available if engine configured with reranker
	}

	return &SearchHealthResponse{
		Status:       "healthy",
		Extensions:   s.convertExtensionStatus(extStatus),
		Capabilities: capabilities,
		SearchTypes:  []string{"fulltext", "vector", "hybrid", "fuzzy", "phonetic"},
	}, nil
}

// getSearchCacheKey generates a cache key for search results
func (s *searchService) getSearchCacheKey(req *search.Request) string {
	// Create a deterministic cache key from search parameters
	key := "search:" + req.Query + ":" + string(req.Type) + ":" + req.ProjectID
	if len(req.ItemTypes) > 0 {
		key += ":" + strings.Join(req.ItemTypes, ",")
	}
	if len(req.Status) > 0 {
		key += ":" + strings.Join(req.Status, ",")
	}
	key += ":" + strconv.Itoa(req.Limit) + ":" + strconv.Itoa(req.Offset)
	return key
}

// convertExtensionStatus converts search.ExtensionStatus to map
func (s *searchService) convertExtensionStatus(ext *search.ExtensionStatus) map[string]bool {
	if ext == nil {
		return map[string]bool{}
	}
	return map[string]bool{
		"pg_trgm":       ext.PgTrgm,
		"fuzzystrmatch": ext.FuzzyStrMatch,
		"unaccent":      ext.Unaccent,
		"vector":        ext.Vector,
	}
}

// SearchItems searches for items with the given query and filters
func (s *searchService) SearchItems(ctx context.Context, query string, filters SearchFilters) ([]search.Result, error) {
	if query == "" {
		return nil, errors.New("search query cannot be empty")
	}

	var statusSlice []string
	if filters.Status != "" {
		statusSlice = []string{filters.Status}
	}

	var itemTypes []string
	if filters.Type != "" {
		itemTypes = []string{filters.Type}
	}

	limit := filters.Limit
	if limit == 0 {
		limit = 20 // Default limit
	}

	req := &search.Request{
		Query:     query,
		Type:      search.TypeFullText,
		ProjectID: filters.ProjectID,
		ItemTypes: itemTypes,
		Status:    statusSlice,
		Limit:     limit,
		Offset:    filters.Offset,
	}

	results, err := s.engine.Search(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("search failed: %w", err)
	}

	return results.Results, nil
}

// SearchProjects searches for projects with the given query
func (s *searchService) SearchProjects(_ context.Context, _ string) ([]search.Result, error) {
	// Note: This is a simplified implementation
	// Projects might need a different search approach
	return []search.Result{}, nil
}

// SearchItemsAdvanced performs an advanced search with specific search type
func (s *searchService) SearchItemsAdvanced(
	ctx context.Context, query string, searchType search.Type, filters SearchFilters,
) ([]search.Result, error) {
	var statusSlice []string
	if filters.Status != "" {
		statusSlice = []string{filters.Status}
	}

	var itemTypes []string
	if filters.Type != "" {
		itemTypes = []string{filters.Type}
	}

	req := &search.Request{
		Query:     query,
		Type:      searchType,
		ProjectID: filters.ProjectID,
		ItemTypes: itemTypes,
		Status:    statusSlice,
		Limit:     filters.Limit,
		Offset:    filters.Offset,
	}

	results, err := s.engine.Search(ctx, req)
	if err != nil {
		return nil, err
	}

	return results.Results, nil
}

// SuggestItems provides autocomplete suggestions for items
func (s *searchService) SuggestItems(ctx context.Context, prefix, projectID string, limit int) ([]string, error) {
	return s.Suggest(ctx, prefix, projectID, limit)
}
