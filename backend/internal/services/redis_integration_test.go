//go:build integration

package services

import (
	"context"
	"testing"
	"time"

	redisclient "github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	redisIntegrationTimeout     = 30 * time.Second
	redisIntegrationTTL         = 100 * time.Millisecond
	redisIntegrationExpireSleep = 150 * time.Millisecond
)

// TestRedisIntegration_BasicSetGet tests basic set/get operations
func TestRedisIntegration_BasicSetGet(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisIntegrationTimeout)
	defer cancel()

	rc := SetupRedisContainer(ctx, t)
	defer func() { _ = rc.Close(ctx) }()

	testCases := []struct {
		key   string
		value string
	}{
		{"key1", "value1"},
		{"key2", "value2"},
		{"cache:item:123", "item-data"},
		{"cache:project:abc", "project-data"},
	}

	for _, tc := range testCases {
		t.Run(tc.key, func(t *testing.T) {
			err := rc.Client.Set(ctx, tc.key, tc.value, 0).Err()
			require.NoError(t, err)

			result, err := rc.Client.Get(ctx, tc.key).Result()
			require.NoError(t, err)
			assert.Equal(t, tc.value, result)
		})
	}
}

// TestRedisIntegration_Expiration tests key expiration
func TestRedisIntegration_Expiration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisIntegrationTimeout)
	defer cancel()

	rc := SetupRedisContainer(ctx, t)
	defer func() { _ = rc.Close(ctx) }()

	// Set key with 100ms expiration
	key := "expiring_key"
	value := "temporary_value"

	err := rc.Client.Set(ctx, key, value, redisIntegrationTTL).Err()
	require.NoError(t, err)

	// Key should exist initially
	result, err := rc.Client.Get(ctx, key).Result()
	require.NoError(t, err)
	assert.Equal(t, value, result)

	// Wait for expiration
	time.Sleep(redisIntegrationExpireSleep)

	// Key should be gone
	_, err = rc.Client.Get(ctx, key).Result()
	assert.Error(t, err)
}

// TestRedisIntegration_Delete tests key deletion
func TestRedisIntegration_Delete(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisIntegrationTimeout)
	defer cancel()

	rc := SetupRedisContainer(ctx, t)
	defer func() { _ = rc.Close(ctx) }()

	key := "delete_test"
	value := "test_value"

	// Set key
	err := rc.Client.Set(ctx, key, value, 0).Err()
	require.NoError(t, err)

	// Verify it exists
	result, err := rc.Client.Get(ctx, key).Result()
	require.NoError(t, err)
	assert.Equal(t, value, result)

	// Delete key
	deleted, err := rc.Client.Del(ctx, key).Result()
	require.NoError(t, err)
	assert.Equal(t, int64(1), deleted)

	// Verify it's gone
	_, err = rc.Client.Get(ctx, key).Result()
	assert.Error(t, err)
}

// TestRedisIntegration_Increment tests integer operations
func TestRedisIntegration_Increment(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisIntegrationTimeout)
	defer cancel()

	rc := SetupRedisContainer(ctx, t)
	defer func() { _ = rc.Close(ctx) }()

	key := "counter"

	// Initialize counter
	err := rc.Client.Set(ctx, key, "0", 0).Err()
	require.NoError(t, err)

	// Increment multiple times
	for i := 1; i <= 5; i++ {
		result, err := rc.Client.Incr(ctx, key).Result()
		require.NoError(t, err)
		assert.Equal(t, int64(i), result)
	}

	// Verify final value
	result, err := rc.Client.Get(ctx, key).Result()
	require.NoError(t, err)
	assert.Equal(t, "5", result)
}

// TestRedisIntegration_Lists tests list operations
func TestRedisIntegration_Lists(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisIntegrationTimeout)
	defer cancel()

	rc := SetupRedisContainer(ctx, t)
	defer func() { _ = rc.Close(ctx) }()

	key := "mylist"

	// Push items
	err := rc.Client.RPush(ctx, key, "item1", "item2", "item3").Err()
	require.NoError(t, err)

	// Get list length
	length, err := rc.Client.LLen(ctx, key).Result()
	require.NoError(t, err)
	assert.Equal(t, int64(3), length)

	// Get list items
	items, err := rc.Client.LRange(ctx, key, 0, -1).Result()
	require.NoError(t, err)
	assert.Equal(t, []string{"item1", "item2", "item3"}, items)

	// Pop item
	item, err := rc.Client.LPop(ctx, key).Result()
	require.NoError(t, err)
	assert.Equal(t, "item1", item)
}

// TestRedisIntegration_Hashes tests hash operations
func TestRedisIntegration_Hashes(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisIntegrationTimeout)
	defer cancel()

	rc := SetupRedisContainer(ctx, t)
	defer func() { _ = rc.Close(ctx) }()

	key := "myhash"

	// Set hash fields
	err := rc.Client.HSet(ctx, key, "field1", "value1", "field2", "value2").Err()
	require.NoError(t, err)

	// Get single field
	value, err := rc.Client.HGet(ctx, key, "field1").Result()
	require.NoError(t, err)
	assert.Equal(t, "value1", value)

	// Get all fields
	all, err := rc.Client.HGetAll(ctx, key).Result()
	require.NoError(t, err)
	assert.Len(t, all, 2)
	assert.Equal(t, "value1", all["field1"])
	assert.Equal(t, "value2", all["field2"])
}

// TestRedisIntegration_Sets tests set operations
func TestRedisIntegration_Sets(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisIntegrationTimeout)
	defer cancel()

	rc := SetupRedisContainer(ctx, t)
	defer func() { _ = rc.Close(ctx) }()

	key := "myset"

	// Add members
	err := rc.Client.SAdd(ctx, key, "member1", "member2", "member3").Err()
	require.NoError(t, err)

	// Get set cardinality
	cardinality, err := rc.Client.SCard(ctx, key).Result()
	require.NoError(t, err)
	assert.Equal(t, int64(3), cardinality)

	// Check membership
	isMember, err := rc.Client.SIsMember(ctx, key, "member1").Result()
	require.NoError(t, err)
	assert.True(t, isMember)
}

// TestRedisIntegration_MultipleKeys tests operations on multiple keys
func TestRedisIntegration_MultipleKeys(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisIntegrationTimeout)
	defer cancel()

	rc := SetupRedisContainer(ctx, t)
	defer func() { _ = rc.Close(ctx) }()

	// Set multiple keys
	keys := map[string]string{
		"key1": "value1",
		"key2": "value2",
		"key3": "value3",
	}

	for key, value := range keys {
		err := rc.Client.Set(ctx, key, value, 0).Err()
		require.NoError(t, err)
	}

	// Get multiple keys
	results, err := rc.Client.MGet(ctx, "key1", "key2", "key3").Result()
	require.NoError(t, err)
	assert.Len(t, results, 3)

	// Delete multiple keys
	deleted, err := rc.Client.Del(ctx, "key1", "key2", "key3").Result()
	require.NoError(t, err)
	assert.Equal(t, int64(3), deleted)
}

// TestRedisIntegration_Pipeline tests pipeline operations
func TestRedisIntegration_Pipeline(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisIntegrationTimeout)
	defer cancel()

	rc := SetupRedisContainer(ctx, t)
	defer func() { _ = rc.Close(ctx) }()

	// Use pipeline for multiple commands
	pipe := rc.Client.Pipeline()

	pipe.Set(ctx, "key1", "value1", 0)
	pipe.Set(ctx, "key2", "value2", 0)
	pipe.Get(ctx, "key1")
	pipe.Get(ctx, "key2")

	_, err := pipe.Exec(ctx)
	require.NoError(t, err)

	// Verify results
	val1, err := rc.Client.Get(ctx, "key1").Result()
	require.NoError(t, err)
	assert.Equal(t, "value1", val1)

	val2, err := rc.Client.Get(ctx, "key2").Result()
	require.NoError(t, err)
	assert.Equal(t, "value2", val2)
}

// TestRedisIntegration_Transaction tests transaction support
func TestRedisIntegration_Transaction(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisIntegrationTimeout)
	defer cancel()

	rc := SetupRedisContainer(ctx, t)
	defer func() { _ = rc.Close(ctx) }()

	// Set initial value
	rc.Client.Set(ctx, "counter", "0", 0)

	// Use transaction
	err := rc.Client.Watch(ctx, func(tx *redisclient.Tx) error {
		// Increment counter in transaction
		_, err := tx.TxPipelined(ctx, func(pipe redisclient.Pipeliner) error {
			pipe.Incr(ctx, "counter")
			pipe.Incr(ctx, "counter")
			return nil
		})
		return err
	}, "counter")

	require.NoError(t, err)

	// Verify final value
	result, err := rc.Client.Get(ctx, "counter").Result()
	require.NoError(t, err)
	assert.Equal(t, "2", result)
}

// TestRedisIntegration_CacheInvalidationPattern tests cache invalidation
func TestRedisIntegration_CacheInvalidationPattern(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisIntegrationTimeout)
	defer cancel()

	rc := SetupRedisContainer(ctx, t)
	defer func() { _ = rc.Close(ctx) }()

	// Pattern: cache keys with prefixes
	itemKey := "cache:item:123"
	itemData := `{"id":"123","title":"Test Item"}`

	// Cache the item
	err := rc.Client.Set(ctx, itemKey, itemData, 5*time.Minute).Err()
	require.NoError(t, err)

	// Verify it's cached
	result, err := rc.Client.Get(ctx, itemKey).Result()
	require.NoError(t, err)
	assert.Equal(t, itemData, result)

	// Invalidate by key
	deleted, err := rc.Client.Del(ctx, itemKey).Result()
	require.NoError(t, err)
	assert.Equal(t, int64(1), deleted)

	// Verify it's gone
	_, err = rc.Client.Get(ctx, itemKey).Result()
	assert.Error(t, err)
}

// TestRedisIntegration_KeyPatternInvalidation tests pattern-based invalidation
func TestRedisIntegration_KeyPatternInvalidation(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisIntegrationTimeout)
	defer cancel()

	rc := SetupRedisContainer(ctx, t)
	defer func() { _ = rc.Close(ctx) }()

	// Set multiple cache keys with pattern
	itemKeys := []string{
		"cache:item:1",
		"cache:item:2",
		"cache:item:3",
	}

	for _, key := range itemKeys {
		err := rc.Client.Set(ctx, key, "data", 0).Err()
		require.NoError(t, err)
	}

	// Find and delete all matching keys
	keys, err := rc.Client.Keys(ctx, "cache:item:*").Result()
	require.NoError(t, err)
	assert.Len(t, keys, 3)

	// Delete all matched keys
	if len(keys) > 0 {
		deleted, err := rc.Client.Del(ctx, keys...).Result()
		require.NoError(t, err)
		assert.Equal(t, int64(3), deleted)
	}
}

// TestRedisIntegration_ConnectionPooling tests connection pooling
func TestRedisIntegration_ConnectionPooling(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisIntegrationTimeout)
	defer cancel()

	rc := SetupRedisContainer(ctx, t)
	defer func() { _ = rc.Close(ctx) }()

	// Run concurrent operations
	done := make(chan error, 10)
	for i := 0; i < 10; i++ {
		go func(idx int) {
			key := "concurrent:key:" + string(rune(idx))
			err := rc.Client.Set(ctx, key, "value", 0).Err()
			done <- err
		}(i)
	}

	// Collect results
	for i := 0; i < 10; i++ {
		err := <-done
		assert.NoError(t, err)
	}
}
