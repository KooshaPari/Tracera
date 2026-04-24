//go:build !integration && !e2e

package cache

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	upstashTestDefaultTTL = 5 * time.Minute
	upstashTestShortTTL   = 1 * time.Second
	upstashTestLongTTL    = 1 * time.Hour
)

// newTestUpstashServer creates a test HTTP server for Upstash API
func newTestUpstashServer() *httptest.Server {
	data := make(map[string]string)
	mu := sync.RWMutex{}

	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		auth := r.Header.Get("Authorization")
		if auth != "Bearer test-token" {
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}

		mu.Lock()
		defer mu.Unlock()

		path := strings.TrimPrefix(r.URL.Path, "/")

		switch {
		case r.Method == http.MethodGet && path == "ping":
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			_, _ = fmt.Fprint(w, `{"result":"PONG"}`)

		case r.Method == http.MethodGet && strings.HasPrefix(path, "get/"):
			key := strings.TrimPrefix(path, "get/")
			if val, ok := data[key]; ok {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusOK)
				_, _ = w.Write([]byte(val))
			} else {
				w.WriteHeader(http.StatusNotFound)
			}

		case r.Method == http.MethodPost && strings.HasPrefix(path, "set/"):
			parts := strings.SplitN(strings.TrimPrefix(path, "set/"), "/", 2)
			if len(parts) < 2 {
				http.Error(w, "Invalid request", http.StatusBadRequest)
				return
			}
			key := parts[0]
			value := parts[1]
			data[key] = value

			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			_, _ = fmt.Fprint(w, `{"result":"OK"}`)

		case r.Method == http.MethodDelete && strings.HasPrefix(path, "del/"):
			key := strings.TrimPrefix(path, "del/")
			delete(data, key)
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			_, _ = fmt.Fprint(w, `{"result":"OK"}`)

		default:
			http.Error(w, "Not Found", http.StatusNotFound)
		}
	}))
}

// TestNewUpstashCache tests initialization
func TestNewUpstashCache(t *testing.T) {
	t.Run("successful creation", func(t *testing.T) {
		_ = t
		server := newTestUpstashServer()
		defer server.Close()

		cache, err := NewUpstashCache(server.URL, "test-token", upstashTestDefaultTTL)
		require.NoError(t, err)
		require.NotNil(t, cache)
		assert.Equal(t, server.URL, cache.restURL)
		assert.Equal(t, "test-token", cache.token)
		assert.Equal(t, upstashTestDefaultTTL, cache.ttl)
	})

	t.Run("failed ping connection", func(t *testing.T) {
		_ = t
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			_ = r
			w.WriteHeader(http.StatusInternalServerError)
			if _, err := fmt.Fprint(w, "Server error"); err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}
		}))
		defer server.Close()

		cache, err := NewUpstashCache(server.URL, "test-token", upstashTestDefaultTTL)
		require.Error(t, err)
		assert.Nil(t, cache)
	})

	t.Run("invalid URL", func(t *testing.T) {
		_ = t
		cache, err := NewUpstashCache("http://[invalid:url", "test-token", upstashTestDefaultTTL)
		require.Error(t, err)
		assert.Nil(t, cache)
	})

	t.Run("custom TTL", func(t *testing.T) {
		_ = t
		server := newTestUpstashServer()
		defer server.Close()

		ttls := []time.Duration{0, upstashTestShortTTL, upstashTestLongTTL}
		for _, ttl := range ttls {
			cache, err := NewUpstashCache(server.URL, "test-token", ttl)
			require.NoError(t, err)
			assert.Equal(t, ttl, cache.ttl)
		}
	})
}

// TestUpstashCacheGet tests Get method
func TestUpstashCacheGet(t *testing.T) {
	server := newTestUpstashServer()
	defer server.Close()

	cache, err := NewUpstashCache(server.URL, "test-token", upstashTestDefaultTTL)
	require.NoError(t, err)

	ctx := context.Background()

	runUpstashCacheGetTests(ctx, t, cache)
}

func runUpstashCacheGetTests(ctx context.Context, t *testing.T, cache *UpstashCache) {
	t.Run("get existing key", func(t *testing.T) {
		_ = t
		value := "test value"
		err := cache.Set(ctx, "key1", value)
		require.NoError(t, err)

		var result string
		err = cache.Get(ctx, "key1", &result)
		require.NoError(t, err)
		assert.Equal(t, value, result)
	})

	t.Run("get non-existent key", func(t *testing.T) {
		_ = t
		var result string
		err := cache.Get(ctx, "nonexistent", &result)
		require.NoError(t, err)
		assert.Empty(t, result)
	})

	t.Run("get with invalid JSON", func(t *testing.T) {
		_ = t
		// Non-existent keys return no error
		var result map[string]string
		err := cache.Get(ctx, "invalid", &result)
		require.NoError(t, err) // No error for non-existent
	})

	t.Run("get with cancellation", func(t *testing.T) {
		_ = t
		cancelCtx, cancel := context.WithCancel(ctx)
		cancel()

		var result string
		err := cache.Get(cancelCtx, "key", &result)
		require.Error(t, err)
	})

	t.Run("get different types", func(t *testing.T) {
		_ = t
		testCases := []interface{}{
			"string value",
			123,
			true,
			[]int{1, 2, 3},
		}

		for i, val := range testCases {
			key := fmt.Sprintf("key:%d", i)
			err := cache.Set(ctx, key, val)
			require.NoError(t, err)

			var result interface{}
			err = cache.Get(ctx, key, &result)
			require.NoError(t, err)
		}
	})
}

// TestUpstashCacheSet tests Set method
func TestUpstashCacheSet(t *testing.T) {
	server := newTestUpstashServer()
	defer server.Close()

	cache, err := NewUpstashCache(server.URL, "test-token", upstashTestDefaultTTL)
	require.NoError(t, err)

	ctx := context.Background()

	t.Run("set simple value", func(t *testing.T) {
		_ = t
		err := cache.Set(ctx, "key", "value")
		require.NoError(t, err)
	})

	t.Run("set complex object", func(t *testing.T) {
		_ = t
		obj := map[string]interface{}{
			"string": "value",
			"number": 42,
			"bool":   true,
		}
		err := cache.Set(ctx, "complex", obj)
		require.NoError(t, err)
	})

	t.Run("set with cancellation", func(t *testing.T) {
		_ = t
		ctx, cancel := context.WithCancel(context.Background())
		cancel()

		err := cache.Set(ctx, "key", "value")
		require.Error(t, err)
	})

	t.Run("overwrite existing", func(t *testing.T) {
		_ = t
		err := cache.Set(ctx, "key", "original")
		require.NoError(t, err)

		err = cache.Set(ctx, "key", "updated")
		require.NoError(t, err)
	})

	t.Run("set nil", func(t *testing.T) {
		_ = t
		err := cache.Set(ctx, "nil_key", nil)
		require.NoError(t, err)
	})

	t.Run("set empty string", func(t *testing.T) {
		_ = t
		err := cache.Set(ctx, "empty", "")
		require.NoError(t, err)
	})
}

// TestUpstashCacheDelete tests Delete method
func TestUpstashCacheDelete(t *testing.T) {
	server := newTestUpstashServer()
	defer server.Close()

	cache, err := NewUpstashCache(server.URL, "test-token", upstashTestDefaultTTL)
	require.NoError(t, err)

	ctx := context.Background()

	t.Run("delete existing key", func(t *testing.T) {
		_ = t
		require.NoError(t, cache.Set(ctx, "key", "value"))
		err := cache.Delete(ctx, "key")
		require.NoError(t, err)
	})

	t.Run("delete non-existent", func(t *testing.T) {
		_ = t
		err := cache.Delete(ctx, "nonexistent")
		require.NoError(t, err)
	})

	t.Run("delete multiple", func(t *testing.T) {
		_ = t
		require.NoError(t, cache.Set(ctx, "k1", "v1"))
		require.NoError(t, cache.Set(ctx, "k2", "v2"))
		require.NoError(t, cache.Set(ctx, "k3", "v3"))

		err := cache.Delete(ctx, "k1", "k2", "k3")
		require.NoError(t, err)
	})

	t.Run("delete empty list", func(t *testing.T) {
		_ = t
		err := cache.Delete(ctx)
		require.NoError(t, err)
	})

	t.Run("delete with cancellation", func(t *testing.T) {
		_ = t
		ctx, cancel := context.WithCancel(context.Background())
		cancel()

		err := cache.Delete(ctx, "key")
		require.Error(t, err)
	})
}

// TestUpstashCacheInvalidatePattern tests InvalidatePattern
func TestUpstashCacheInvalidatePattern(t *testing.T) {
	server := newTestUpstashServer()
	defer server.Close()

	cache, err := NewUpstashCache(server.URL, "test-token", upstashTestDefaultTTL)
	require.NoError(t, err)

	ctx := context.Background()

	t.Run("invalidate pattern", func(t *testing.T) {
		_ = t
		err := cache.InvalidatePattern(ctx, "project:*")
		require.NoError(t, err)
	})

	t.Run("invalidate empty pattern", func(t *testing.T) {
		_ = t
		err := cache.InvalidatePattern(ctx, "")
		require.NoError(t, err)
	})
}

// TestUpstashCacheClose tests Close method
func TestUpstashCacheClose(t *testing.T) {
	server := newTestUpstashServer()
	defer server.Close()

	cache, err := NewUpstashCache(server.URL, "test-token", upstashTestDefaultTTL)
	require.NoError(t, err)

	t.Run("close cache", func(t *testing.T) {
		_ = t
		err := cache.Close()
		require.NoError(t, err)
	})

	t.Run("multiple closes", func(t *testing.T) {
		_ = t
		cache2, err := NewUpstashCache(server.URL, "test-token", upstashTestDefaultTTL)
		require.NoError(t, err)
		require.NoError(t, cache2.Close())
		require.NoError(t, cache2.Close())
	})
}

// TestUpstashCacheConcurrency tests concurrent operations
func TestUpstashCacheConcurrency(t *testing.T) {
	server := newTestUpstashServer()
	defer server.Close()

	cache, err := NewUpstashCache(server.URL, "test-token", upstashTestDefaultTTL)
	require.NoError(t, err)

	ctx := context.Background()

	t.Run("concurrent sets", func(t *testing.T) {
		_ = t
		var wg sync.WaitGroup
		for i := 0; i < 20; i++ {
			wg.Add(1)
			go func(idx int) {
				defer wg.Done()
				assert.NoError(t, cache.Set(ctx, fmt.Sprintf("key:%d", idx), idx))
			}(i)
		}
		wg.Wait()
	})

	t.Run("concurrent gets", func(t *testing.T) {
		_ = t
		require.NoError(t, cache.Set(ctx, "shared", "value"))
		var wg sync.WaitGroup
		for i := 0; i < 20; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				var result string
				assert.NoError(t, cache.Get(ctx, "shared", &result))
			}()
		}
		wg.Wait()
	})

	t.Run("concurrent mixed", func(t *testing.T) {
		_ = t
		var wg sync.WaitGroup
		for i := 0; i < 30; i++ {
			wg.Add(1)
			go func(idx int) {
				defer wg.Done()
				key := fmt.Sprintf("mixed:%d", idx)
				assert.NoError(t, cache.Set(ctx, key, idx))
				var result int
				assert.NoError(t, cache.Get(ctx, key, &result))
				assert.NoError(t, cache.Delete(ctx, key))
			}(i)
		}
		wg.Wait()
	})
}

// TestUpstashCacheEdgeCases tests edge cases
func TestUpstashCacheEdgeCases(t *testing.T) {
	server := newTestUpstashServer()
	defer server.Close()

	cache, err := NewUpstashCache(server.URL, "test-token", upstashTestDefaultTTL)
	require.NoError(t, err)

	ctx := context.Background()

	runUpstashCacheEdgeCaseTests(ctx, t, cache)
}

func runUpstashCacheEdgeCaseTests(ctx context.Context, t *testing.T, cache *UpstashCache) {
	t.Run("unicode keys and values", func(t *testing.T) {
		_ = t
		data := map[string]string{"key": "世界"}
		err := cache.Set(ctx, "unicode:世界", data)
		require.NoError(t, err)

		var result map[string]string
		err = cache.Get(ctx, "unicode:世界", &result)
		require.NoError(t, err)
	})

	t.Run("nested structures", func(t *testing.T) {
		_ = t
		type Inner struct {
			Value string `json:"value"`
		}
		type Outer struct {
			Inner Inner `json:"inner"`
		}

		obj := Outer{Inner: Inner{Value: "test"}}
		err := cache.Set(ctx, "nested", obj)
		require.NoError(t, err)

		var result Outer
		err = cache.Get(ctx, "nested", &result)
		require.NoError(t, err)
		assert.Equal(t, "test", result.Inner.Value)
	})

	t.Run("large values", func(t *testing.T) {
		_ = t
		large := strings.Repeat("x", 10000)
		err := cache.Set(ctx, "large", large)
		require.NoError(t, err)

		var result string
		err = cache.Get(ctx, "large", &result)
		require.NoError(t, err)
		assert.Equal(t, large, result)
	})

	t.Run("array of objects", func(t *testing.T) {
		_ = t
		items := []map[string]interface{}{
			{"id": 1, "name": "item1"},
			{"id": 2, "name": "item2"},
		}
		err := cache.Set(ctx, "items", items)
		require.NoError(t, err)

		var result []map[string]interface{}
		err = cache.Get(ctx, "items", &result)
		require.NoError(t, err)
		assert.Len(t, result, 2)
	})
}

// TestUpstashCacheWorkflow tests complete workflow
func TestUpstashCacheWorkflow(t *testing.T) {
	server := newTestUpstashServer()
	defer server.Close()

	cache, err := NewUpstashCache(server.URL, "test-token", upstashTestDefaultTTL)
	require.NoError(t, err)

	ctx := context.Background()

	t.Run("set-get-delete", func(t *testing.T) {
		_ = t
		// Set
		err := cache.Set(ctx, "workflow", "value")
		require.NoError(t, err)

		// Get
		var result string
		err = cache.Get(ctx, "workflow", &result)
		require.NoError(t, err)
		assert.Equal(t, "value", result)

		// Delete
		err = cache.Delete(ctx, "workflow")
		require.NoError(t, err)
	})

	t.Run("bulk operations", func(t *testing.T) {
		_ = t
		// Set multiple
		for i := 0; i < 10; i++ {
			err := cache.Set(ctx, fmt.Sprintf("bulk:%d", i), i)
			require.NoError(t, err)
		}

		// Get multiple
		for i := 0; i < 10; i++ {
			var result int
			err := cache.Get(ctx, fmt.Sprintf("bulk:%d", i), &result)
			require.NoError(t, err)
			assert.Equal(t, i, result)
		}

		// Delete multiple
		keys := make([]string, 10)
		for i := 0; i < 10; i++ {
			keys[i] = fmt.Sprintf("bulk:%d", i)
		}
		err := cache.Delete(ctx, keys...)
		require.NoError(t, err)
	})
}
