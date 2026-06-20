package services

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// CacheMock implements cache.Cache interface for testing
type CacheMock struct {
	mu        sync.RWMutex
	data      map[string][]byte
	failOn    string // Fail operations on this key
	failCount int    // Number of times to fail before succeeding
	calls     int    // Track number of calls
}

func NewCacheMock() *CacheMock {
	return &CacheMock{
		data: make(map[string][]byte),
	}
}

func (m *CacheMock) Get(_ context.Context, key string, dest interface{}) error {
	m.mu.Lock()
	m.calls++
	failOn := m.failOn
	failCount := m.failCount
	if m.failOn == key && m.failCount > 0 {
		m.failCount--
	}
	data, ok := m.data[key]
	m.mu.Unlock()

	if failOn == key && failCount > 0 {
		return fmt.Errorf("mock error for key %s", key)
	}

	if !ok {
		// Return error to indicate key not found (consistent with Redis behavior)
		return errors.New("key not found")
	}

	return json.Unmarshal(data, dest)
}

func (m *CacheMock) Set(_ context.Context, key string, value interface{}) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.calls++

	if m.failOn == key && m.failCount > 0 {
		m.failCount--
		return fmt.Errorf("mock error for key %s", key)
	}

	data, err := json.Marshal(value)
	if err != nil {
		return err
	}

	m.data[key] = data
	return nil
}

func (m *CacheMock) Delete(_ context.Context, keys ...string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.calls++

	for _, key := range keys {
		if m.failOn == key && m.failCount > 0 {
			m.failCount--
			return fmt.Errorf("mock error for key %s", key)
		}
		delete(m.data, key)
	}
	return nil
}

const failTestKey = "fail:key"

func (m *CacheMock) InvalidatePattern(_ context.Context, pattern string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.calls++

	if m.failOn == pattern && m.failCount > 0 {
		m.failCount--
		return fmt.Errorf("mock error for pattern %s", pattern)
	}

	// Simple pattern matching for mock
	toDelete := []string{}
	for key := range m.data {
		if matchesPattern(key, pattern) {
			toDelete = append(toDelete, key)
		}
	}

	for _, key := range toDelete {
		delete(m.data, key)
	}

	return nil
}

func (m *CacheMock) Close() error {
	return nil
}

// Simple pattern matching helper
func matchesPattern(key, pattern string) bool {
	// Simple wildcard matching for testing
	if pattern == "*" {
		return true
	}
	// Match prefix patterns like "item:*"
	if len(pattern) > 0 && pattern[len(pattern)-1] == '*' {
		prefix := pattern[:len(pattern)-1]
		return len(key) >= len(prefix) && key[:len(prefix)] == prefix
	}
	return key == pattern
}

// ============================================================================
// Interface Compliance
// ============================================================================

func TestCacheServiceImpl_ImplementsInterface(_ *testing.T) {
	// Verify CacheServiceImpl implements CacheService interface
	var _ CacheService = (*CacheServiceImpl)(nil)
}

// ============================================================================
// Test Generic Cache Operations
// ============================================================================

func TestCacheService_Get(t *testing.T) {
	tests := []struct {
		name      string
		setup     func(*CacheMock)
		key       string
		wantValue string
		wantErr   bool
	}{
		{
			name: "successful get",
			setup: func(m *CacheMock) {
				m.data["test:key"] = []byte(`"test-value"`)
			},
			key:       "test:key",
			wantValue: "test-value",
			wantErr:   false,
		},
		{
			name:      "key not found returns empty",
			setup:     func(_ *CacheMock) {},
			key:       "nonexistent",
			wantValue: "",
			wantErr:   false,
		},
		{
			name: "get failure",
			setup: func(m *CacheMock) {
				m.failOn = failTestKey
				m.failCount = 1
			},
			key:     failTestKey,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cache := NewCacheMock()
			tt.setup(cache)
			svc := NewCacheServiceImpl(cache, 5*time.Minute)

			got, err := svc.Get(context.Background(), tt.key)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				assert.Equal(t, tt.wantValue, got)
			}
		})
	}
}

func TestCacheService_Set(t *testing.T) {
	tests := []struct {
		name    string
		setup   func(*CacheMock)
		key     string
		value   string
		ttl     time.Duration
		wantErr bool
	}{
		{
			name:    "successful set",
			setup:   func(_ *CacheMock) {},
			key:     "test:key",
			value:   "test-value",
			ttl:     5 * time.Minute,
			wantErr: false,
		},
		{
			name:    "set with zero TTL uses default",
			setup:   func(_ *CacheMock) {},
			key:     "test:key",
			value:   "test-value",
			ttl:     0,
			wantErr: false,
		},
		{
			name: "set failure",
			setup: func(m *CacheMock) {
				m.failOn = failTestKey
				m.failCount = 1
			},
			key:     failTestKey,
			value:   "value",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cache := NewCacheMock()
			tt.setup(cache)
			svc := NewCacheServiceImpl(cache, 5*time.Minute)

			err := svc.Set(context.Background(), tt.key, tt.value, tt.ttl)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				// Verify value was stored
				var got string
				require.NoError(t, cache.Get(context.Background(), tt.key, &got))
				assert.Equal(t, tt.value, got)
			}
		})
	}
}

func TestCacheService_Delete(t *testing.T) {
	tests := []struct {
		name    string
		setup   func(*CacheMock)
		key     string
		wantErr bool
	}{
		{
			name: "successful delete",
			setup: func(m *CacheMock) {
				m.data["test:key"] = []byte(`"value"`)
			},
			key:     "test:key",
			wantErr: false,
		},
		{
			name:    "delete nonexistent key",
			setup:   func(_ *CacheMock) {},
			key:     "nonexistent",
			wantErr: false,
		},
		{
			name: "delete failure",
			setup: func(m *CacheMock) {
				m.failOn = failTestKey
				m.failCount = 1
			},
			key:     failTestKey,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cache := NewCacheMock()
			tt.setup(cache)
			svc := NewCacheServiceImpl(cache, 5*time.Minute)

			err := svc.Delete(context.Background(), tt.key)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				// Verify key was deleted
				_, exists := cache.data[tt.key]
				assert.False(t, exists)
			}
		})
	}
}

func TestCacheService_InvalidatePattern(t *testing.T) {
	tests := []struct {
		name          string
		setup         func(*CacheMock)
		pattern       string
		wantDeleted   []string
		wantRemaining []string
		wantErr       bool
	}{
		{
			name: "invalidate with wildcard",
			setup: func(m *CacheMock) {
				m.data["item:1"] = []byte(`"value1"`)
				m.data["item:2"] = []byte(`"value2"`)
				m.data["project:1"] = []byte(`"value3"`)
			},
			pattern:       "item:*",
			wantDeleted:   []string{"item:1", "item:2"},
			wantRemaining: []string{"project:1"},
			wantErr:       false,
		},
		{
			name: "invalidate all",
			setup: func(m *CacheMock) {
				m.data["key1"] = []byte(`"value1"`)
				m.data["key2"] = []byte(`"value2"`)
			},
			pattern:       "*",
			wantDeleted:   []string{"key1", "key2"},
			wantRemaining: []string{},
			wantErr:       false,
		},
		{
			name: "invalidate pattern failure",
			setup: func(m *CacheMock) {
				m.failOn = "fail:*"
				m.failCount = 1
			},
			pattern: "fail:*",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cache := NewCacheMock()
			tt.setup(cache)
			svc := NewCacheServiceImpl(cache, 5*time.Minute)

			err := svc.InvalidatePattern(context.Background(), tt.pattern)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				assertKeysDeleted(t, cache, tt.wantDeleted)
				assertKeysPresent(t, cache, tt.wantRemaining)
			}
		})
	}
}

func assertKeysDeleted(t *testing.T, cache *CacheMock, keys []string) {
	t.Helper()
	for _, key := range keys {
		_, exists := cache.data[key]
		assert.False(t, exists, "expected key %s to be deleted", key)
	}
}

func assertKeysPresent(t *testing.T, cache *CacheMock, keys []string) {
	t.Helper()
	for _, key := range keys {
		_, exists := cache.data[key]
		assert.True(t, exists, "expected key %s to remain", key)
	}
}

func TestCacheService_GetMulti(t *testing.T) {
	cache := NewCacheMock()
	cache.data["key1"] = []byte(`"value1"`)
	cache.data["key2"] = []byte(`"value2"`)

	svc := NewCacheServiceImpl(cache, 5*time.Minute)

	t.Run("get multiple keys", func(t *testing.T) {
		result, err := svc.GetMulti(context.Background(), []string{"key1", "key2", "key3"})
		require.NoError(t, err)
		assert.Len(t, result, 2)
		assert.Equal(t, "value1", result["key1"])
		assert.Equal(t, "value2", result["key2"])
	})

	t.Run("empty keys list", func(t *testing.T) {
		result, err := svc.GetMulti(context.Background(), []string{})
		require.NoError(t, err)
		assert.Empty(t, result)
	})
}

func TestCacheService_SetMulti(t *testing.T) {
	cache := NewCacheMock()
	svc := NewCacheServiceImpl(cache, 5*time.Minute)

	t.Run("set multiple values", func(t *testing.T) {
		items := map[string]string{
			"key1": "value1",
			"key2": "value2",
			"key3": "value3",
		}

		err := svc.SetMulti(context.Background(), items, 5*time.Minute)
		require.NoError(t, err)

		// Verify all were set
		for key, want := range items {
			var got string
			require.NoError(t, cache.Get(context.Background(), key, &got))
			assert.Equal(t, want, got)
		}
	})

	t.Run("empty items map", func(t *testing.T) {
		err := svc.SetMulti(context.Background(), map[string]string{}, 5*time.Minute)
		require.NoError(t, err)
	})
}

func TestCacheService_Exists(t *testing.T) {
	cache := NewCacheMock()
	cache.data["existing"] = []byte(`"value"`)

	svc := NewCacheServiceImpl(cache, 5*time.Minute)

	t.Run("key exists", func(t *testing.T) {
		exists, err := svc.Exists(context.Background(), "existing")
		require.NoError(t, err)
		assert.True(t, exists)
	})

	t.Run("key does not exist", func(t *testing.T) {
		exists, err := svc.Exists(context.Background(), "nonexistent")
		require.NoError(t, err)
		assert.False(t, exists)
	})
}

func TestCacheService_Expire(t *testing.T) {
	cache := NewCacheMock()
	svc := NewCacheServiceImpl(cache, 5*time.Minute)

	t.Run("expire not supported", func(t *testing.T) {
		err := svc.Expire(context.Background(), "key", 10*time.Minute)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "not supported")
	})
}

// ============================================================================
// Test Entity-Specific Operations
// ============================================================================

func TestCacheService_Item(t *testing.T) {
	cache := NewCacheMock()
	svc := NewCacheServiceImpl(cache, 5*time.Minute)
	ctx := context.Background()

	item := &models.Item{
		ID:          "item-123",
		ProjectID:   "proj-1",
		Title:       "Test Item",
		Description: "Test Description",
		Type:        "feature",
		Status:      "open",
	}

	t.Run("set and get item", func(t *testing.T) {
		err := svc.SetItem(ctx, item)
		require.NoError(t, err)

		got, err := svc.GetItem(ctx, item.ID)
		require.NoError(t, err)
		assert.Equal(t, item.ID, got.ID)
		assert.Equal(t, item.Title, got.Title)
	})

	t.Run("get nonexistent item", func(t *testing.T) {
		got, err := svc.GetItem(ctx, "nonexistent")
		require.NoError(t, err)
		assert.Nil(t, got)
	})

	t.Run("invalidate item", func(t *testing.T) {
		err := svc.InvalidateItem(ctx, item.ID)
		require.NoError(t, err)

		got, err := svc.GetItem(ctx, item.ID)
		require.NoError(t, err)
		assert.Nil(t, got)
	})
}

func TestCacheService_Project(t *testing.T) {
	cache := NewCacheMock()
	svc := NewCacheServiceImpl(cache, 5*time.Minute)
	ctx := context.Background()

	project := &models.Project{
		ID:          "proj-123",
		Name:        "Test Project",
		Description: "Test Description",
	}

	t.Run("set and get project", func(t *testing.T) {
		err := svc.SetProject(ctx, project)
		require.NoError(t, err)

		got, err := svc.GetProject(ctx, project.ID)
		require.NoError(t, err)
		assert.Equal(t, project.ID, got.ID)
		assert.Equal(t, project.Name, got.Name)
	})

	t.Run("get nonexistent project", func(t *testing.T) {
		got, err := svc.GetProject(ctx, "nonexistent")
		require.NoError(t, err)
		assert.Nil(t, got)
	})

	t.Run("invalidate project", func(t *testing.T) {
		err := svc.InvalidateProject(ctx, project.ID)
		require.NoError(t, err)

		got, err := svc.GetProject(ctx, project.ID)
		require.NoError(t, err)
		assert.Nil(t, got)
	})
}

func runCacheEntityTests[T any](
	t *testing.T,
	entityName string,
	id string,
	set func() error,
	get func(string) (*T, error),
	invalidate func(string) error,
	assertEntity func(*T),
) {
	t.Helper()

	t.Run("set and get "+entityName, func(t *testing.T) {
		err := set()
		require.NoError(t, err)

		got, err := get(id)
		require.NoError(t, err)
		assertEntity(got)
	})

	t.Run("get nonexistent "+entityName, func(t *testing.T) {
		got, err := get("nonexistent")
		require.NoError(t, err)
		assert.Nil(t, got)
	})

	t.Run("invalidate "+entityName, func(t *testing.T) {
		err := invalidate(id)
		require.NoError(t, err)

		got, err := get(id)
		require.NoError(t, err)
		assert.Nil(t, got)
	})
}

func TestCacheService_EntityCache(t *testing.T) {
	cache := NewCacheMock()
	svc := NewCacheServiceImpl(cache, 5*time.Minute)
	ctx := context.Background()

	t.Run("link", func(t *testing.T) {
		link := &models.Link{
			ID:       "link-123",
			SourceID: "item-1",
			TargetID: "item-2",
			Type:     "depends_on",
		}

		runCacheEntityTests(
			t,
			"link",
			link.ID,
			func() error { return svc.SetLink(ctx, link) },
			func(id string) (*models.Link, error) { return svc.GetLink(ctx, id) },
			func(id string) error { return svc.InvalidateLink(ctx, id) },
			func(got *models.Link) {
				require.NotNil(t, got)
				assert.Equal(t, link.ID, got.ID)
				assert.Equal(t, link.SourceID, got.SourceID)
			},
		)
	})

	t.Run("agent", func(t *testing.T) {
		agent := &models.Agent{
			ID:        "agent-123",
			ProjectID: "proj-1",
			Name:      "Test Agent",
			Status:    "active",
		}

		runCacheEntityTests(
			t,
			"agent",
			agent.ID,
			func() error { return svc.SetAgent(ctx, agent) },
			func(id string) (*models.Agent, error) { return svc.GetAgent(ctx, id) },
			func(id string) error { return svc.InvalidateAgent(ctx, id) },
			func(got *models.Agent) {
				require.NotNil(t, got)
				assert.Equal(t, agent.ID, got.ID)
				assert.Equal(t, agent.Name, got.Name)
			},
		)
	})
}

// ============================================================================
// Test List and Stats Operations
// ============================================================================

func TestCacheService_Items(t *testing.T) {
	cache := NewCacheMock()
	svc := NewCacheServiceImpl(cache, 5*time.Minute)
	ctx := context.Background()

	items := []*models.Item{
		{ID: "item-1", Title: "Item 1"},
		{ID: "item-2", Title: "Item 2"},
	}

	t.Run("set and get items list", func(t *testing.T) {
		err := svc.SetItems(ctx, "items:project:1", items, 5*time.Minute)
		require.NoError(t, err)

		got, err := svc.GetItems(ctx, "items:project:1")
		require.NoError(t, err)
		assert.Len(t, got, 2)
		assert.Equal(t, "item-1", got[0].ID)
	})

	t.Run("get nonexistent items list", func(t *testing.T) {
		got, err := svc.GetItems(ctx, "nonexistent")
		require.NoError(t, err)
		assert.Nil(t, got)
	})
}

func TestCacheService_Stats(t *testing.T) {
	cache := NewCacheMock()
	svc := NewCacheServiceImpl(cache, 5*time.Minute)
	ctx := context.Background()

	stats := &ItemStats{
		TotalItems: 100,
		ByType: map[string]int64{
			"feature": 50,
			"bug":     25,
		},
		ByStatus: map[string]int64{
			"open":   75,
			"closed": 25,
		},
	}

	t.Run("set and get stats", func(t *testing.T) {
		err := svc.SetStats(ctx, "stats:project:1", stats, 5*time.Minute)
		require.NoError(t, err)

		got, err := svc.GetStats(ctx, "stats:project:1")
		require.NoError(t, err)
		assert.Equal(t, int64(100), got.TotalItems)
		assert.Equal(t, int64(50), got.ByType["feature"])
	})

	t.Run("get nonexistent stats", func(t *testing.T) {
		got, err := svc.GetStats(ctx, "nonexistent")
		require.NoError(t, err)
		assert.Nil(t, got)
	})
}

// ============================================================================
// Test Batch Operations
// ============================================================================

func TestCacheService_ItemsBatch(t *testing.T) {
	cache := NewCacheMock()
	svc := NewCacheServiceImpl(cache, 5*time.Minute)
	ctx := context.Background()

	items := []*models.Item{
		{ID: "item-1", Title: "Item 1"},
		{ID: "item-2", Title: "Item 2"},
		{ID: "item-3", Title: "Item 3"},
	}

	t.Run("set and get items batch", func(t *testing.T) {
		err := svc.SetItemsBatch(ctx, items)
		require.NoError(t, err)

		got, err := svc.GetItemsBatch(ctx, []string{"item-1", "item-2", "item-3", "item-4"})
		require.NoError(t, err)
		assert.Len(t, got, 3) // item-4 doesn't exist
		assert.Equal(t, "Item 1", got["item-1"].Title)
		assert.Equal(t, "Item 2", got["item-2"].Title)
	})

	t.Run("empty batch", func(t *testing.T) {
		got, err := svc.GetItemsBatch(ctx, []string{})
		require.NoError(t, err)
		assert.Empty(t, got)
	})
}

func TestCacheService_InvalidateProjectItems(t *testing.T) {
	cache := NewCacheMock()
	svc := NewCacheServiceImpl(cache, 5*time.Minute)
	ctx := context.Background()

	// Set up project items cache
	items := []*models.Item{{ID: "item-1"}}
	require.NoError(t, svc.SetItems(ctx, "items:project:1:page:0", items, 5*time.Minute))

	stats := &ItemStats{TotalItems: 10}
	require.NoError(t, svc.SetStats(ctx, "project:1:stats", stats, 5*time.Minute))

	t.Run("invalidate project items", func(t *testing.T) {
		err := svc.InvalidateProjectItems(ctx, "1")
		require.NoError(t, err)

		// Verify caches were cleared
		gotItems, err := svc.GetItems(ctx, "items:project:1:page:0")
		require.NoError(t, err)
		assert.Nil(t, gotItems)

		gotStats, err := svc.GetStats(ctx, "project:1:stats")
		require.NoError(t, err)
		assert.Nil(t, gotStats)
	})
}

// ============================================================================
// Test Health Check
// ============================================================================

func TestCacheService_HealthCheck(t *testing.T) {
	cache := NewCacheMock()
	svc := NewCacheServiceImpl(cache, 5*time.Minute)

	t.Run("health check success", func(t *testing.T) {
		err := svc.HealthCheck(context.Background())
		require.NoError(t, err)
	})

	t.Run("health check with unavailable cache", func(t *testing.T) {
		svc := NewCacheServiceImpl(nil, 5*time.Minute)
		err := svc.HealthCheck(context.Background())
		require.Error(t, err)
	})
}

// ============================================================================
// Test Edge Cases and Error Handling
// ============================================================================

func TestCacheService_NilCache(t *testing.T) {
	svc := NewCacheServiceImpl(nil, 5*time.Minute)
	ctx := context.Background()

	t.Run("operations with nil cache return errors or handle gracefully", func(t *testing.T) {
		// Get should return error
		_, err := svc.Get(ctx, "key")
		require.Error(t, err)

		// Set should handle gracefully
		err = svc.Set(ctx, "key", "value", 5*time.Minute)
		require.NoError(t, err) // Gracefully handles nil cache

		// Delete should handle gracefully
		err = svc.Delete(ctx, "key")
		require.NoError(t, err)
	})
}

func TestCacheService_InvalidJSON(t *testing.T) {
	cache := NewCacheMock()
	svc := NewCacheServiceImpl(cache, 5*time.Minute)
	ctx := context.Background()

	t.Run("get item with invalid JSON", func(t *testing.T) {
		cache.data["item:bad"] = []byte(`{invalid json`)

		_, err := svc.GetItem(ctx, "bad")
		require.Error(t, err)
	})
}

func TestCacheService_ConcurrentAccess(t *testing.T) {
	cache := NewCacheMock()
	svc := NewCacheServiceImpl(cache, 5*time.Minute)
	ctx := context.Background()

	t.Run("concurrent set and get", func(t *testing.T) {
		done := make(chan bool)

		// Concurrent writers
		for i := 0; i < 10; i++ {
			go func(id int) {
				item := &models.Item{
					ID:    fmt.Sprintf("item-%d", id),
					Title: fmt.Sprintf("Item %d", id),
				}
				assert.NoError(t, svc.SetItem(ctx, item))
				done <- true
			}(i)
		}

		// Wait for all writers
		for i := 0; i < 10; i++ {
			<-done
		}

		// Verify all items were written
		assert.Len(t, cache.data, 10)
	})
}
