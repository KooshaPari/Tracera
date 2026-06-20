// Package search provides search utilities and cross-perspective search.
package search

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"strings"
	"sync"
	"time"
)

const (
	crossSearchDefaultLimit           = 10
	crossSearchMaxLimit               = 100
	crossSearchDefaultMinScore        = 0.1
	crossSearchDefaultFuzzyThreshold  = 0.3
	crossSearchSuggestionDefaultLimit = 10
	crossSearchSuggestionMaxLimit     = 50
)

// CrossPerspectiveSearchRequest represents a unified search across perspectives
type CrossPerspectiveSearchRequest struct {
	Query               string   `json:"query"`
	ProjectID           string   `json:"project_id"`
	Perspectives        []string `json:"perspectives,omitempty"`    // Filter by specific perspectives
	Status              []string `json:"status,omitempty"`          // Filter by status
	Types               []string `json:"types,omitempty"`           // Filter by type
	DimensionKey        string   `json:"dimension_key,omitempty"`   // Dimension filter key
	DimensionValue      string   `json:"dimension_value,omitempty"` // Dimension filter value
	IncludeEquivalences bool     `json:"include_equivalences"`      // Include equivalent items
	Limit               int      `json:"limit,omitempty"`           // Results per perspective
	Offset              int      `json:"offset,omitempty"`          // Pagination offset
	MinScore            float64  `json:"min_score,omitempty"`       // Minimum relevance score
	EnableFuzzy         bool     `json:"enable_fuzzy,omitempty"`    // Enable fuzzy matching
	FuzzyThreshold      float64  `json:"fuzzy_threshold,omitempty"` // Fuzzy similarity threshold
	SortBy              string   `json:"sort_by,omitempty"`         // relevance, recent, popular
}

// PerspectiveResults represents search results for a single perspective
type PerspectiveResults struct {
	Perspective string   `json:"perspective"`
	Results     []Result `json:"results"`
	Count       int      `json:"count"`
	Total       int      `json:"total"` // Total before limit
}

// CrossPerspectiveSearchResponse represents unified search results
type CrossPerspectiveSearchResponse struct {
	Query                string               `json:"query"`
	ProjectID            string               `json:"project_id"`
	PerspectiveGroups    []PerspectiveResults `json:"perspective_groups"`
	TotalCount           int                  `json:"total_count"`
	PerspectivesSearched int                  `json:"perspectives_searched"`
	Duration             string               `json:"duration"`
	CacheHit             bool                 `json:"cache_hit"`
	ExecutedAt           string               `json:"executed_at"`
}

// CrossPerspectiveSearcher handles unified cross-perspective searches
type CrossPerspectiveSearcher struct {
	engine *Engine
	cache  *Cache
}

// NewCrossPerspectiveSearcher creates a new cross-perspective searcher
func NewCrossPerspectiveSearcher(engine *Engine, cache *Cache) *CrossPerspectiveSearcher {
	return &CrossPerspectiveSearcher{
		engine: engine,
		cache:  cache,
	}
}

// Search performs a unified search across all perspectives
func (cs *CrossPerspectiveSearcher) Search(
	ctx context.Context,
	req *CrossPerspectiveSearchRequest,
) (*CrossPerspectiveSearchResponse, error) {
	if strings.TrimSpace(req.Query) == "" {
		return nil, errors.New("query cannot be empty")
	}

	applyCrossSearchDefaults(req)
	cacheKey := cs.generateCacheKey(req)

	if cached, found := cs.getCachedResponse(cacheKey); found {
		return cached, nil
	}

	perspectives := resolvePerspectives(req)
	response := newCrossPerspectiveResponse(req)

	for _, perspective := range perspectives {
		if err := cs.appendPerspectiveResults(ctx, req, perspective, response); err != nil {
			slog.Error("Error searching perspective", "error", perspective, "error", err)
		}
	}

	response.PerspectivesSearched = len(response.PerspectiveGroups)
	cs.cacheResponse(cacheKey, response)

	return response, nil
}

func applyCrossSearchDefaults(req *CrossPerspectiveSearchRequest) {
	if req.Limit <= 0 {
		req.Limit = crossSearchDefaultLimit
	}
	if req.Limit > crossSearchMaxLimit {
		req.Limit = crossSearchMaxLimit
	}
	if req.MinScore == 0 {
		req.MinScore = crossSearchDefaultMinScore
	}
	if req.FuzzyThreshold == 0 {
		req.FuzzyThreshold = crossSearchDefaultFuzzyThreshold
	}
}

func resolvePerspectives(req *CrossPerspectiveSearchRequest) []string {
	if len(req.Perspectives) > 0 {
		return req.Perspectives
	}

	return []string{
		"feature", "code", "test", "api", "database",
		"wireframe", "documentation", "deployment",
		"architecture", "configuration", "dataflow",
		"dependency", "domain", "infrastructure", "journey",
		"monitoring", "performance", "security",
	}
}

func newCrossPerspectiveResponse(req *CrossPerspectiveSearchRequest) *CrossPerspectiveSearchResponse {
	return &CrossPerspectiveSearchResponse{
		Query:                req.Query,
		ProjectID:            req.ProjectID,
		PerspectiveGroups:    make([]PerspectiveResults, 0),
		TotalCount:           0,
		PerspectivesSearched: 0,
		Duration:             "",
		CacheHit:             false,
		ExecutedAt:           getCurrentTimestamp(),
	}
}

func (cs *CrossPerspectiveSearcher) getCachedResponse(cacheKey string) (*CrossPerspectiveSearchResponse, bool) {
	if cs.cache == nil {
		return nil, false
	}

	if cached, found := cs.cache.Get(cacheKey); found {
		if resp, ok := cached.(*CrossPerspectiveSearchResponse); ok {
			resp.CacheHit = true
			return resp, true
		}
	}

	return nil, false
}

func (cs *CrossPerspectiveSearcher) appendPerspectiveResults(
	ctx context.Context,
	req *CrossPerspectiveSearchRequest,
	perspective string,
	response *CrossPerspectiveSearchResponse,
) error {
	results, total, err := cs.searchPerspective(ctx, req, perspective)
	if err != nil {
		return err
	}
	if len(results) == 0 {
		return nil
	}

	response.PerspectiveGroups = append(response.PerspectiveGroups, PerspectiveResults{
		Perspective: perspective,
		Results:     results,
		Count:       len(results),
		Total:       total,
	})
	response.TotalCount += len(results)

	return nil
}

func (cs *CrossPerspectiveSearcher) cacheResponse(cacheKey string, response *CrossPerspectiveSearchResponse) {
	if cs.cache == nil {
		return
	}

	cs.cache.Set(cacheKey, response, cacheTTL)
}

// searchPerspective searches a single perspective
func (cs *CrossPerspectiveSearcher) searchPerspective(
	ctx context.Context,
	req *CrossPerspectiveSearchRequest,
	perspective string,
) ([]Result, int, error) {
	// Check if engine is available
	if cs.engine == nil {
		return nil, 0, errors.New("search engine is not available")
	}

	// Build search request for this perspective
	searchReq := &Request{
		Query:               req.Query,
		Type:                TypeFullText,
		ProjectID:           req.ProjectID,
		ItemTypes:           req.Types,
		Status:              req.Status,
		Limit:               req.Limit,
		Offset:              req.Offset,
		MinScore:            req.MinScore,
		IncludeDeleted:      false,
		FuzzyThreshold:      req.FuzzyThreshold,
		EnableTypoTolerance: req.EnableFuzzy,
	}

	// Execute search
	response, err := cs.engine.Search(ctx, searchReq)
	if err != nil {
		return nil, 0, err
	}

	// Apply perspective filter
	filtered := filterByPerspective(response.Results, perspective)

	// Apply dimension filter if specified
	if req.DimensionKey != "" && req.DimensionValue != "" {
		filtered = filterByDimension(filtered, req.DimensionKey, req.DimensionValue)
	}

	return filtered, len(filtered), nil
}

// GetSuggestions returns auto-complete suggestions for a query
func (cs *CrossPerspectiveSearcher) GetSuggestions(
	ctx context.Context,
	projectID string,
	query string,
	limit int,
) ([]string, error) {
	if limit <= 0 {
		limit = crossSearchSuggestionDefaultLimit
	}
	if limit > crossSearchSuggestionMaxLimit {
		limit = crossSearchSuggestionMaxLimit
	}

	cacheKey := "suggestions:" + projectID + ":" + query

	// Check cache
	if cs.cache != nil {
		if cached, found := cs.cache.Get(cacheKey); found {
			if suggestions, ok := cached.([]string); ok {
				return suggestions, nil
			}
		}
	}

	// Query for suggestions
	sql := `
		SELECT DISTINCT title
		FROM items
		WHERE project_id = $1::uuid
			AND (
				title ILIKE $2 || '%'
				OR description ILIKE $2 || '%'
			)
		ORDER BY title
		LIMIT $3
	`

	rows, err := cs.engine.pool.Query(ctx, sql, projectID, query, limit)
	if err != nil {
		return nil, fmt.Errorf("query failed: %w", err)
	}
	defer rows.Close()

	suggestions := make([]string, 0)
	for rows.Next() {
		var title string
		if err := rows.Scan(&title); err != nil {
			continue
		}
		suggestions = append(suggestions, title)
	}

	// Cache suggestions
	if cs.cache != nil {
		cs.cache.Set(cacheKey, suggestions, cacheTTL)
	}

	return suggestions, nil
}

// TriggerReindex triggers a full re-indexing of items
func (cs *CrossPerspectiveSearcher) TriggerReindex(
	_ context.Context,
	_ string,
) error {
	// This would typically be handled by the Indexer
	// For now, we just return a placeholder
	return errors.New("reindexing not yet implemented")
}

// generateCacheKey generates a cache key for a search request
func (cs *CrossPerspectiveSearcher) generateCacheKey(req *CrossPerspectiveSearchRequest) string {
	perspStr := strings.Join(req.Perspectives, ",")
	statusStr := strings.Join(req.Status, ",")
	typesStr := strings.Join(req.Types, ",")

	key := fmt.Sprintf(
		"cross_search:%s:%s:%s:%s:%s:%s:%s:%v",
		req.ProjectID,
		req.Query,
		perspStr,
		statusStr,
		typesStr,
		req.DimensionKey,
		req.DimensionValue,
		req.Limit,
	)

	return key
}

// filterByPerspective filters results by perspective
func filterByPerspective(results []Result, perspective string) []Result {
	filtered := make([]Result, 0)

	for _, r := range results {
		// Check if metadata contains perspective field
		if meta, ok := r.Metadata["perspective"]; ok {
			if metaStr, ok := meta.(string); ok && metaStr == perspective {
				filtered = append(filtered, r)
			}
		}
	}

	return filtered
}

// filterByDimension filters results by dimension key-value pair
func filterByDimension(results []Result, key string, value string) []Result {
	filtered := make([]Result, 0)

	for _, r := range results {
		if meta, ok := r.Metadata["dimensions"]; ok {
			if dims, ok := meta.(map[string]interface{}); ok {
				if dimValue, ok := dims[key]; ok && dimValue == value {
					filtered = append(filtered, r)
				}
			}
		}
	}

	return filtered
}

// getCurrentTimestamp returns the current timestamp in ISO format with milliseconds
func getCurrentTimestamp() string {
	return time.Now().UTC().Format("2006-01-02T15:04:05.000Z")
}

// Cache provides caching for search results
type Cache struct {
	data map[string]CacheEntry
	ttl  map[string]int64
	mu   sync.RWMutex
}

// CacheEntry represents a cached search result
type CacheEntry struct {
	data      interface{}
	timestamp int64
}

const (
	cacheTTL = 300 // 5 minutes in seconds
)

// NewCache creates a new search cache
func NewCache() *Cache {
	return &Cache{
		data: make(map[string]CacheEntry),
		ttl:  make(map[string]int64),
	}
}

// Set stores a value in the cache
func (sc *Cache) Set(key string, value interface{}, ttl int) {
	sc.mu.Lock()
	defer sc.mu.Unlock()

	now := time.Now().Unix()
	sc.data[key] = CacheEntry{data: value, timestamp: now}
	sc.ttl[key] = now + int64(ttl)
}

// Get retrieves a value from the cache
func (sc *Cache) Get(key string) (interface{}, bool) {
	sc.mu.RLock()

	entry, found := sc.data[key]
	if !found {
		sc.mu.RUnlock()
		return nil, false
	}

	// Check if expired
	if expiration, ok := sc.ttl[key]; ok {
		if time.Now().Unix() >= expiration {
			sc.mu.RUnlock()
			sc.Delete(key)
			return nil, false
		}
	}

	defer sc.mu.RUnlock()
	return entry.data, true
}

// Delete removes a value from the cache
func (sc *Cache) Delete(key string) {
	sc.mu.Lock()
	defer sc.mu.Unlock()

	delete(sc.data, key)
	delete(sc.ttl, key)
}

// Clear clears the entire cache
func (sc *Cache) Clear() {
	sc.mu.Lock()
	defer sc.mu.Unlock()

	sc.data = make(map[string]CacheEntry)
	sc.ttl = make(map[string]int64)
}

// Size returns the number of items in the cache
func (sc *Cache) Size() int {
	sc.mu.RLock()
	defer sc.mu.RUnlock()

	return len(sc.data)
}
