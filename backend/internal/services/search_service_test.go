package services

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/search"
)

// mockSearchEngine implements a mock search.Engine for testing
type mockSearchEngine struct {
	searchFunc             func(ctx context.Context, req *search.Request) (*search.Response, error)
	suggestFunc            func(ctx context.Context, prefix string, projectID string, limit int) ([]string, error)
	getExtensionStatusFunc func(ctx context.Context) (*search.ExtensionStatus, error)
	healthCheckFunc        func(ctx context.Context) error
}

func (m *mockSearchEngine) Search(ctx context.Context, req *search.Request) (*search.Response, error) {
	if m.searchFunc != nil {
		return m.searchFunc(ctx, req)
	}
	return &search.Response{Results: []search.Result{}}, nil
}

func (m *mockSearchEngine) Suggest(ctx context.Context, prefix string, projectID string, limit int) ([]string, error) {
	if m.suggestFunc != nil {
		return m.suggestFunc(ctx, prefix, projectID, limit)
	}
	return []string{}, nil
}

func (m *mockSearchEngine) GetExtensionStatus(ctx context.Context) (*search.ExtensionStatus, error) {
	if m.getExtensionStatusFunc != nil {
		return m.getExtensionStatusFunc(ctx)
	}
	return &search.ExtensionStatus{
		PgTrgm:        true,
		FuzzyStrMatch: true,
		Unaccent:      true,
		Vector:        true,
	}, nil
}

func (m *mockSearchEngine) HealthCheck(ctx context.Context) error {
	if m.healthCheckFunc != nil {
		return m.healthCheckFunc(ctx)
	}
	return nil
}

// mockIndexer implements a mock search.Indexer for testing
type mockIndexer struct {
	queueIndexFunc  func(itemID string, priority int) error
	queueDeleteFunc func(itemID string) error
	reindexAllFunc  func(ctx context.Context) error
	statsFunc       func() search.IndexerStats
}

func (m *mockIndexer) QueueIndex(itemID string, priority int) error {
	if m.queueIndexFunc != nil {
		return m.queueIndexFunc(itemID, priority)
	}
	return nil
}

func (m *mockIndexer) QueueDelete(itemID string) error {
	if m.queueDeleteFunc != nil {
		return m.queueDeleteFunc(itemID)
	}
	return nil
}

func (m *mockIndexer) ReindexAll(ctx context.Context) error {
	if m.reindexAllFunc != nil {
		return m.reindexAllFunc(ctx)
	}
	return nil
}

func (m *mockIndexer) Stats() search.IndexerStats {
	if m.statsFunc != nil {
		return m.statsFunc()
	}
	return search.IndexerStats{
		TotalJobs:     100,
		CompletedJobs: 95,
		FailedJobs:    5,
		QueueSize:     10,
	}
}

// Test service creation
func TestNewSearchService(t *testing.T) {
	engine := &mockSearchEngine{}
	indexer := &mockIndexer{}

	service := NewSearchService(engine, indexer, nil, nil, nil, nil)

	assert.NotNil(t, service, "Service should not be nil")
}

// Test SearchItems with successful results
func TestSearchItems_Success(t *testing.T) {
	now := time.Now()
	expectedResults := []search.Result{
		{
			ID:          "item-1",
			ProjectID:   "project-1",
			Title:       "Test Item 1",
			Description: "Test Description 1",
			Type:        "requirement",
			Status:      "open",
			Priority:    "high",
			Score:       0.95,
			CreatedAt:   now,
			UpdatedAt:   now,
		},
	}

	engine := &mockSearchEngine{
		searchFunc: func(_ context.Context, req *search.Request) (*search.Response, error) {
			return &search.Response{
				Results:    expectedResults,
				TotalCount: len(expectedResults),
				Query:      req.Query,
				SearchType: req.Type,
			}, nil
		},
	}

	indexer := &mockIndexer{}
	service := NewSearchService(engine, indexer, nil, nil, nil, nil)

	filters := SearchFilters{
		ProjectID: "project-1",
		Limit:     20,
		Offset:    0,
	}

	items, err := service.SearchItems(context.Background(), "test query", filters)

	require.NoError(t, err)
	assert.Len(t, items, 1)
	assert.Equal(t, "item-1", items[0].ID)
	assert.Equal(t, "Test Item 1", items[0].Title)
}

// Test SearchItems with empty query
func TestSearchItems_EmptyQuery(t *testing.T) {
	engine := &mockSearchEngine{}
	indexer := &mockIndexer{}
	service := NewSearchService(engine, indexer, nil, nil, nil, nil)

	filters := SearchFilters{}

	items, err := service.SearchItems(context.Background(), "", filters)

	require.Error(t, err)
	assert.Nil(t, items)
	// Empty query should fail
}

// Test SearchItems with filters
func TestSearchItems_WithFilters(t *testing.T) {
	engine := &mockSearchEngine{
		searchFunc: func(_ context.Context, req *search.Request) (*search.Response, error) {
			assert.Equal(t, "test", req.Query)
			assert.Equal(t, "project-1", req.ProjectID)
			assert.Equal(t, []string{"open"}, req.Status)
			assert.Equal(t, []string{"requirement"}, req.ItemTypes)
			assert.Equal(t, 10, req.Limit)
			return &search.Response{Results: []search.Result{}}, nil
		},
	}

	indexer := &mockIndexer{}
	service := NewSearchService(engine, indexer, nil, nil, nil, nil)

	filters := SearchFilters{
		ProjectID: "project-1",
		Status:    "open",
		Type:      "requirement",
		Limit:     10,
	}

	_, err := service.SearchItems(context.Background(), "test", filters)

	require.NoError(t, err)
}

// Test SearchProjects
func TestSearchProjects_Success(t *testing.T) {
	engine := &mockSearchEngine{}
	indexer := &mockIndexer{}
	service := NewSearchService(engine, indexer, nil, nil, nil, nil)

	projects, err := service.SearchProjects(context.Background(), "test")

	require.NoError(t, err)
	assert.NotNil(t, projects)
}

// Test IndexItem success
func TestIndexItem_Success(t *testing.T) {
	queuedItemID := ""

	engine := &mockSearchEngine{}
	indexer := &mockIndexer{
		queueIndexFunc: func(itemID string, _ int) error {
			queuedItemID = itemID
			return nil
		},
	}
	service := NewSearchService(engine, indexer, nil, nil, nil, nil)

	err := service.IndexItem(context.Background(), "item-1")

	require.NoError(t, err)
	assert.Equal(t, "item-1", queuedItemID)
}

// Test IndexItem with empty ID
func TestIndexItem_EmptyID(t *testing.T) {
	engine := &mockSearchEngine{}
	indexer := &mockIndexer{}
	service := NewSearchService(engine, indexer, nil, nil, nil, nil)

	err := service.IndexItem(context.Background(), "")

	require.Error(t, err)
	assert.Contains(t, err.Error(), "item ID is required")
}

// Test advanced search with different types
func TestSearchItemsAdvanced_AllTypes(t *testing.T) {
	searchTypes := []search.Type{
		search.TypeFullText,
		search.TypeVector,
		search.TypeHybrid,
		search.TypeFuzzy,
		search.TypePhonetic,
	}

	for _, searchType := range searchTypes {
		t.Run(string(searchType), func(t *testing.T) {
			engine := &mockSearchEngine{
				searchFunc: func(_ context.Context, req *search.Request) (*search.Response, error) {
					assert.Equal(t, searchType, req.Type)
					return &search.Response{Results: []search.Result{}}, nil
				},
			}

			indexer := &mockIndexer{}
			service, ok := NewSearchService(engine, indexer, nil, nil, nil, nil).(*searchService)
			require.True(t, ok)

			_, err := service.SearchItemsAdvanced(context.Background(), "test", searchType, SearchFilters{})
			require.NoError(t, err)
		})
	}
}

// Test suggestions
func TestSuggestItems_Success(t *testing.T) {
	expectedSuggestions := []string{"Test Item 1", "Test Item 2"}

	engine := &mockSearchEngine{
		suggestFunc: func(_ context.Context, prefix string, _ string, _ int) ([]string, error) {
			assert.Equal(t, "test", prefix)
			return expectedSuggestions, nil
		},
	}

	indexer := &mockIndexer{}
	service, ok := NewSearchService(engine, indexer, nil, nil, nil, nil).(*searchService)
	require.True(t, ok)

	suggestions, err := service.SuggestItems(context.Background(), "test", "project-1", 10)

	require.NoError(t, err)
	assert.Equal(t, expectedSuggestions, suggestions)
}

// Test health check
func TestGetSearchHealth_Healthy(t *testing.T) {
	engine := &mockSearchEngine{
		getExtensionStatusFunc: func(_ context.Context) (*search.ExtensionStatus, error) {
			return &search.ExtensionStatus{
				PgTrgm: true,
				Vector: true,
			}, nil
		},
		healthCheckFunc: func(_ context.Context) error {
			return nil
		},
	}

	indexer := &mockIndexer{
		statsFunc: func() search.IndexerStats {
			return search.IndexerStats{
				TotalJobs:     100,
				CompletedJobs: 95,
			}
		},
	}

	service, ok := NewSearchService(engine, indexer, nil, nil, nil, nil).(*searchService)
	require.True(t, ok)

	health, err := service.GetSearchHealth(context.Background())

	require.NoError(t, err)
	assert.Equal(t, "healthy", health.Status)
	assert.NotNil(t, health.Extensions)
}

// Test reindex all
func TestReindexAll_Success(t *testing.T) {
	reindexCalled := false

	engine := &mockSearchEngine{}
	indexer := &mockIndexer{
		reindexAllFunc: func(_ context.Context) error {
			reindexCalled = true
			return nil
		},
	}

	service, ok := NewSearchService(engine, indexer, nil, nil, nil, nil).(*searchService)
	require.True(t, ok)

	err := service.ReindexAll(context.Background())

	require.NoError(t, err)
	assert.True(t, reindexCalled)
}

// Test error handling
func TestSearchItems_EngineError(t *testing.T) {
	engine := &mockSearchEngine{
		searchFunc: func(_ context.Context, _ *search.Request) (*search.Response, error) {
			return nil, errors.New("search engine error")
		},
	}

	indexer := &mockIndexer{}
	service := NewSearchService(engine, indexer, nil, nil, nil, nil)

	_, err := service.SearchItems(context.Background(), "test", SearchFilters{})

	require.Error(t, err)
	assert.Contains(t, err.Error(), "search failed")
}

// Test indexer error
func TestIndexItem_IndexerError(t *testing.T) {
	engine := &mockSearchEngine{}
	indexer := &mockIndexer{
		queueIndexFunc: func(_ string, _ int) error {
			return errors.New("queue error")
		},
	}

	service := NewSearchService(engine, indexer, nil, nil, nil, nil)

	err := service.IndexItem(context.Background(), "item-1")

	require.Error(t, err)
	assert.Contains(t, err.Error(), "failed to queue item for indexing")
}

// Test default limit
func TestSearchItems_DefaultLimit(t *testing.T) {
	engine := &mockSearchEngine{
		searchFunc: func(_ context.Context, req *search.Request) (*search.Response, error) {
			assert.Equal(t, 20, req.Limit, "Default limit should be 20")
			return &search.Response{Results: []search.Result{}}, nil
		},
	}

	indexer := &mockIndexer{}
	service := NewSearchService(engine, indexer, nil, nil, nil, nil)

	_, err := service.SearchItems(context.Background(), "test", SearchFilters{Limit: 0})

	require.NoError(t, err)
}
