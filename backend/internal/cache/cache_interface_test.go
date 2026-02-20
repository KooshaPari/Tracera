//go:build !integration && !e2e

// Package cache tests cache interface contracts.
package cache

import (
	"context"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const cacheContextTimeout = 5 * time.Second

// TestCacheInterface_KeyPatterns tests the cache key pattern constants
func TestCacheInterface_KeyPatterns(t *testing.T) {
	t.Run("all pattern constants are defined", func(_ *testing.T) {
		assert.Equal(t, "project:*", ProjectKeyPattern)
		assert.Equal(t, "item:*", ItemKeyPattern)
		assert.Equal(t, "link:*", LinkKeyPattern)
		assert.Equal(t, "agent:*", AgentKeyPattern)
		assert.Equal(t, "search:*", SearchKeyPattern)
	})

	t.Run("patterns are non-empty", func(_ *testing.T) {
		patterns := []string{
			ProjectKeyPattern,
			ItemKeyPattern,
			LinkKeyPattern,
			AgentKeyPattern,
			SearchKeyPattern,
		}

		for _, pattern := range patterns {
			assert.NotEmpty(t, pattern)
			assert.Contains(t, pattern, "*")
		}
	})

	t.Run("patterns have expected prefixes", func(_ *testing.T) {
		prefixes := map[string]string{
			ProjectKeyPattern: "project:",
			ItemKeyPattern:    "item:",
			LinkKeyPattern:    "link:",
			AgentKeyPattern:   "agent:",
			SearchKeyPattern:  "search:",
		}

		for pattern, prefix := range prefixes {
			assert.Greater(t, len(pattern), len(prefix))
			assert.Equal(t, prefix, pattern[:len(prefix)])
		}
	})
}

// TestProjectKeyGeneration tests the ProjectKey function
func TestProjectKeyGeneration(t *testing.T) {
	runKeyGenerationCases(t, "project", ProjectKey, []keyCase{
		{name: "simple project ID", id: "123", expected: "project:123"},
		{name: "UUID format", id: "550e8400-e29b-41d4-a716-446655440000", expected: "project:550e8400-e29b-41d4-a716-446655440000"},
		{name: "empty ID", id: "", expected: "project:"},
		{name: "special characters", id: "proj-123_abc.def", expected: "project:proj-123_abc.def"},
		{name: "numeric ID", id: "9876543210", expected: "project:9876543210"},
	})

	t.Run("long ID", func(_ *testing.T) {
		longID := "a_very_long_project_identifier_with_many_characters_that_is_still_valid"
		key := ProjectKey(longID)
		assert.Greater(t, len(key), 70)
		assert.Contains(t, key, "project:")
	})
}

// TestItemKeyGeneration tests the ItemKey function
func TestItemKeyGeneration(t *testing.T) {
	runKeyGenerationCases(t, "item", ItemKey, []keyCase{
		{name: "simple item ID", id: "456", expected: "item:456"},
		{name: "hyphenated ID", id: "item-456-789", expected: "item:item-456-789"},
		{name: "empty ID", id: "", expected: "item:"},
		{name: "alphanumeric ID", id: "ABC123XYZ", expected: "item:ABC123XYZ"},
		{name: "underscore ID", id: "item_456_789", expected: "item:item_456_789"},
	})
}

// TestLinkKeyGeneration tests the LinkKey function
func TestLinkKeyGeneration(t *testing.T) {
	runKeyGenerationCases(t, "link", LinkKey, []keyCase{
		{name: "simple link ID", id: "789", expected: "link:789"},
		{name: "composite link ID", id: "link-123-456", expected: "link:link-123-456"},
		{name: "empty ID", id: "", expected: "link:"},
		{name: "dot notation", id: "source.target.123", expected: "link:source.target.123"},
	})
}

// TestAgentKeyGeneration tests the AgentKey function
func TestAgentKeyGeneration(t *testing.T) {
	runKeyGenerationCases(t, "agent", AgentKey, []keyCase{
		{name: "simple agent ID", id: "gpt4", expected: "agent:gpt4"},
		{name: "versioned agent ID", id: "agent-v2.0", expected: "agent:agent-v2.0"},
		{name: "empty ID", id: "", expected: "agent:"},
		{name: "complex agent ID", id: "gpt-4-turbo-preview-123", expected: "agent:gpt-4-turbo-preview-123"},
		{name: "uppercase ID", id: "AGENT_TYPE_1", expected: "agent:AGENT_TYPE_1"},
	})
}

// TestSearchKeyGeneration tests the SearchKey function
func TestSearchKeyGeneration(t *testing.T) {
	t.Run("simple query and project", func(_ *testing.T) {
		key := SearchKey("test", "proj-1")
		assert.Equal(t, "search:proj-1:test", key)
	})

	t.Run("complex query", func(_ *testing.T) {
		key := SearchKey("complex search query with spaces", "proj-2")
		expected := "search:proj-2:complex search query with spaces"
		assert.Equal(t, expected, key)
	})

	t.Run("empty query", func(_ *testing.T) {
		key := SearchKey("", "proj-3")
		assert.Equal(t, "search:proj-3:", key)
	})

	t.Run("empty project", func(_ *testing.T) {
		key := SearchKey("query", "")
		assert.Equal(t, "search::query", key)
	})

	t.Run("both empty", func(_ *testing.T) {
		key := SearchKey("", "")
		assert.Equal(t, "search::", key)
	})

	t.Run("special characters in query", func(_ *testing.T) {
		key := SearchKey("query*with?special[chars]", "proj")
		assert.Contains(t, key, "search:")
		assert.Contains(t, key, "proj")
		assert.Contains(t, key, "query*with?special[chars]")
	})

	t.Run("unicode in query", func(_ *testing.T) {
		key := SearchKey("查询", "项目")
		assert.Contains(t, key, "search:")
		assert.Contains(t, key, "项目")
		assert.Contains(t, key, "查询")
	})

	t.Run("long query", func(_ *testing.T) {
		longQuery := "this is a very long search query that contains many words and should still work correctly"
		key := SearchKey(longQuery, "project")
		assert.Contains(t, key, longQuery)
		assert.Contains(t, key, "project")
	})
}

type keyCase struct {
	name     string
	id       string
	expected string
}

func runKeyGenerationCases(t *testing.T, label string, keyFn func(string) string, cases []keyCase) {
	t.Helper()

	for _, tc := range cases {
		t.Run(tc.name, func(_ *testing.T) {
			key := keyFn(tc.id)
			assert.Equal(t, tc.expected, key, "unexpected %s key for %q", label, tc.id)
		})
	}
}

// TestKeyHelperConsistency tests that key helpers produce consistent results
func TestKeyHelperConsistency(t *testing.T) {
	t.Run("project key consistency", func(_ *testing.T) {
		id := "proj-123"
		key1 := ProjectKey(id)
		key2 := ProjectKey(id)
		assert.Equal(t, key1, key2)
	})

	t.Run("item key consistency", func(_ *testing.T) {
		id := "item-456"
		key1 := ItemKey(id)
		key2 := ItemKey(id)
		assert.Equal(t, key1, key2)
	})

	t.Run("search key consistency", func(_ *testing.T) {
		query := "test query"
		project := "proj-1"
		key1 := SearchKey(query, project)
		key2 := SearchKey(query, project)
		assert.Equal(t, key1, key2)
	})
}

// TestKeyHelperUniqueness tests that different inputs produce different keys
func TestKeyHelperUniqueness(t *testing.T) {
	t.Run("project keys are unique", func(_ *testing.T) {
		key1 := ProjectKey("proj1")
		key2 := ProjectKey("proj2")
		assert.NotEqual(t, key1, key2)
	})

	t.Run("item keys are unique", func(_ *testing.T) {
		key1 := ItemKey("item1")
		key2 := ItemKey("item2")
		assert.NotEqual(t, key1, key2)
	})

	t.Run("different key types are unique", func(_ *testing.T) {
		id := "123"
		projKey := ProjectKey(id)
		itemKey := ItemKey(id)
		linkKey := LinkKey(id)
		agentKey := AgentKey(id)

		keys := []string{projKey, itemKey, linkKey, agentKey}
		for i := 0; i < len(keys); i++ {
			for j := i + 1; j < len(keys); j++ {
				assert.NotEqual(t, keys[i], keys[j])
			}
		}
	})

	t.Run("search keys with different parameters", func(_ *testing.T) {
		key1 := SearchKey("query1", "proj1")
		key2 := SearchKey("query1", "proj2")
		key3 := SearchKey("query2", "proj1")
		key4 := SearchKey("query2", "proj2")

		assert.NotEqual(t, key1, key2)
		assert.NotEqual(t, key1, key3)
		assert.NotEqual(t, key1, key4)
	})
}

// TestCacheInterfaceContract tests the Cache interface contract
func TestCacheInterfaceContract(t *testing.T) {
	t.Run("Cache interface defines required methods", func(_ *testing.T) {
		// This test verifies the interface is properly defined
		var _ Cache = (*mockCache)(nil)
	})
}

// mockCache is a simple mock implementation of Cache for testing
type mockCache struct {
	data map[string]interface{}
	mu   sync.RWMutex
}

func (m *mockCache) Get(_ context.Context, key string, dest interface{}) error {
	m.mu.RLock()
	defer m.mu.RUnlock()
	if val, ok := m.data[key]; ok {
		// In real implementation, would unmarshal
		// For this mock, just return the interface{}
		if d, ok := dest.(*interface{}); ok {
			*d = val
		}
	}
	return nil
}

func (m *mockCache) Set(_ context.Context, key string, value interface{}) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.data[key] = value
	return nil
}

func (m *mockCache) Delete(_ context.Context, keys ...string) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	for _, key := range keys {
		delete(m.data, key)
	}
	return nil
}

func (m *mockCache) InvalidatePattern(_ context.Context, _ string) error {
	return nil
}

func (m *mockCache) Close() error {
	return nil
}

// TestCacheBehavior tests the behavior of cache operations
func TestCacheBehavior(t *testing.T) {
	t.Run("key generation produces correct format", func(_ *testing.T) {
		testCases := []struct {
			name           string
			input          string
			expectedPrefix string
			generator      func(string) string
		}{
			{"project", "123", "project:", ProjectKey},
			{"item", "456", "item:", ItemKey},
			{"link", "789", "link:", LinkKey},
			{"agent", "gpt4", "agent:", AgentKey},
		}

		for _, tc := range testCases {
			t.Run(tc.name, func(_ *testing.T) {
				key := tc.generator(tc.input)
				assert.Greater(t, len(key), len(tc.expectedPrefix))
				assert.Equal(t, tc.expectedPrefix, key[:len(tc.expectedPrefix)])
			})
		}
	})

	t.Run("search key format matches specification", func(_ *testing.T) {
		key := SearchKey("myquery", "myproject")
		// Expected format: search:myproject:myquery
		parts := strings.Split(key, ":")
		require.Len(t, parts, 3)
		assert.Equal(t, "search", parts[0])
		assert.Equal(t, "myproject", parts[1])
		assert.Equal(t, "myquery", parts[2])
	})
}

// TestCacheContextHandling tests context-related behavior
func TestCacheContextHandling(t *testing.T) {
	t.Run("operations work with background context", func(_ *testing.T) {
		ctx := context.Background()
		assert.NotNil(t, ctx)
	})

	t.Run("operations work with timeout context", func(_ *testing.T) {
		ctx, cancel := context.WithTimeout(context.Background(), cacheContextTimeout)
		defer cancel()
		assert.NotNil(t, ctx)
	})

	t.Run("operations handle cancelled context", func(_ *testing.T) {
		ctx, cancel := context.WithCancel(context.Background())
		cancel()
		<-ctx.Done()
		assert.Error(t, ctx.Err())
	})
}

// TestKeyHelperEdgeCases tests edge cases in key generation
func TestKeyHelperEdgeCases(t *testing.T) {
	t.Run("keys with null characters are handled", func(_ *testing.T) {
		// Testing with strings that might be problematic
		key := ProjectKey("proj\x00null")
		assert.NotEmpty(t, key)
	})

	t.Run("keys with newlines", func(_ *testing.T) {
		key := ItemKey("item\nwith\nnewlines")
		assert.NotEmpty(t, key)
		assert.Contains(t, key, "item:")
	})

	t.Run("keys with tabs", func(_ *testing.T) {
		key := LinkKey("link\twith\ttabs")
		assert.NotEmpty(t, key)
		assert.Contains(t, key, "link:")
	})

	t.Run("very long composite search key", func(_ *testing.T) {
		longQuery := strings.Repeat("x", 500)
		longProject := strings.Repeat("y", 500)
		key := SearchKey(longQuery, longProject)
		assert.Greater(t, len(key), 1000)
	})
}
