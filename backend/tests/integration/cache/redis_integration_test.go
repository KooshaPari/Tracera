//go:build integration

package cache_test

import (
	"context"
	"fmt"
	"sync"
	"testing"
	"time"

	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

var (
	testRedisClient *redis.Client
	redisURL        = "redis://localhost:6379/15" // Use DB 15 for testing
	setupOnce       sync.Once
	teardownOnce    sync.Once
)

func setupTestRedis(t *testing.T) *redis.Client {
	setupOnce.Do(func() {
		opt, err := redis.ParseURL(redisURL)
		require.NoError(t, err)

		client := redis.NewClient(opt)

		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()

		err = client.Ping(ctx).Err()
		require.NoError(t, err)

		// Clear test database
		err = client.FlushDB(ctx).Err()
		require.NoError(t, err)

		testRedisClient = client
		t.Logf("✅ Test Redis initialized successfully")
	})

	return testRedisClient
}

func teardownTestRedis(t *testing.T) {
	teardownOnce.Do(func() {
		if testRedisClient != nil {
			ctx := context.Background()
			_ = testRedisClient.FlushDB(ctx).Err()
			_ = testRedisClient.Close()
			t.Logf("✅ Test Redis cleaned up")
		}
	})
}

// TestRedis_SetGet_Success tests basic set and get operations
func TestRedis_SetGet_Success(t *testing.T) {
	client := setupTestRedis(t)
	defer teardownTestRedis(t)

	ctx := context.Background()

	t.Run("String_Value", func(t *testing.T) {
		key := "test:string"
		value := "test value"

		err := client.Set(ctx, key, value, 10*time.Second).Err()
		require.NoError(t, err)

		result, err := client.Get(ctx, key).Result()
		require.NoError(t, err)
		assert.Equal(t, value, result)
	})

	t.Run("JSON_Value", func(t *testing.T) {
		key := "test:json"
		value := `{"id":"123","name":"Test Item","active":true}`

		err := client.Set(ctx, key, value, 10*time.Second).Err()
		require.NoError(t, err)

		result, err := client.Get(ctx, key).Result()
		require.NoError(t, err)
		assert.JSONEq(t, value, result)
	})

	t.Run("Integer_Value", func(t *testing.T) {
		key := "test:counter"
		value := 42

		err := client.Set(ctx, key, value, 10*time.Second).Err()
		require.NoError(t, err)

		result, err := client.Get(ctx, key).Int()
		require.NoError(t, err)
		assert.Equal(t, value, result)
	})

	t.Run("NonExistent_Key", func(t *testing.T) {
		key := "test:nonexistent"

		result, err := client.Get(ctx, key).Result()
		assert.Error(t, err)
		assert.Equal(t, redis.Nil, err)
		assert.Empty(t, result)
	})

	t.Run("Overwrite_Existing", func(t *testing.T) {
		key := "test:overwrite"

		err := client.Set(ctx, key, "original", 10*time.Second).Err()
		require.NoError(t, err)

		err = client.Set(ctx, key, "updated", 10*time.Second).Err()
		require.NoError(t, err)

		result, err := client.Get(ctx, key).Result()
		require.NoError(t, err)
		assert.Equal(t, "updated", result)
	})
}

// TestRedis_Expiration_TTL tests key expiration and TTL management
func TestRedis_Expiration_TTL(t *testing.T) {
	client := setupTestRedis(t)
	defer teardownTestRedis(t)

	ctx := context.Background()

	t.Run("Auto_Expiration", func(t *testing.T) {
		key := "test:expire"
		value := "expires soon"
		ttl := 2 * time.Second

		err := client.Set(ctx, key, value, ttl).Err()
		require.NoError(t, err)

		// Verify key exists
		result, err := client.Get(ctx, key).Result()
		require.NoError(t, err)
		assert.Equal(t, value, result)

		// Check TTL
		remainingTTL, err := client.TTL(ctx, key).Result()
		require.NoError(t, err)
		assert.Greater(t, remainingTTL, time.Duration(0))
		assert.LessOrEqual(t, remainingTTL, ttl)

		// Wait for expiration
		time.Sleep(3 * time.Second)

		// Verify key expired
		result, err = client.Get(ctx, key).Result()
		assert.Error(t, err)
		assert.Equal(t, redis.Nil, err)
	})

	t.Run("Update_TTL", func(t *testing.T) {
		key := "test:ttl:update"
		value := "test value"

		err := client.Set(ctx, key, value, 10*time.Second).Err()
		require.NoError(t, err)

		// Update TTL
		ok, err := client.Expire(ctx, key, 30*time.Second).Result()
		require.NoError(t, err)
		assert.True(t, ok)

		// Verify new TTL
		ttl, err := client.TTL(ctx, key).Result()
		require.NoError(t, err)
		assert.Greater(t, ttl, 15*time.Second)
	})

	t.Run("Persist_Key", func(t *testing.T) {
		key := "test:persist"
		value := "persistent value"

		err := client.Set(ctx, key, value, 10*time.Second).Err()
		require.NoError(t, err)

		// Remove expiration
		ok, err := client.Persist(ctx, key).Result()
		require.NoError(t, err)
		assert.True(t, ok)

		// Verify no TTL
		ttl, err := client.TTL(ctx, key).Result()
		require.NoError(t, err)
		assert.Equal(t, time.Duration(-1), ttl) // -1 means no expiration
	})

	t.Run("Zero_TTL", func(t *testing.T) {
		key := "test:zero:ttl"
		value := "no expiration"

		err := client.Set(ctx, key, value, 0).Err()
		require.NoError(t, err)

		// Verify no TTL
		ttl, err := client.TTL(ctx, key).Result()
		require.NoError(t, err)
		assert.Equal(t, time.Duration(-1), ttl)
	})
}

// TestRedis_Delete_Success tests key deletion
func TestRedis_Delete_Success(t *testing.T) {
	client := setupTestRedis(t)
	defer teardownTestRedis(t)

	ctx := context.Background()

	t.Run("Single_Key", func(t *testing.T) {
		key := "test:delete:single"
		value := "to be deleted"

		err := client.Set(ctx, key, value, 0).Err()
		require.NoError(t, err)

		// Delete key
		deleted, err := client.Del(ctx, key).Result()
		require.NoError(t, err)
		assert.Equal(t, int64(1), deleted)

		// Verify deletion
		result, err := client.Get(ctx, key).Result()
		assert.Error(t, err)
		assert.Equal(t, redis.Nil, err)
	})

	t.Run("Multiple_Keys", func(t *testing.T) {
		keys := []string{"test:delete:1", "test:delete:2", "test:delete:3"}

		// Set multiple keys
		for _, key := range keys {
			err := client.Set(ctx, key, "value", 0).Err()
			require.NoError(t, err)
		}

		// Delete all keys
		deleted, err := client.Del(ctx, keys...).Result()
		require.NoError(t, err)
		assert.Equal(t, int64(3), deleted)

		// Verify all deleted
		for _, key := range keys {
			result, err := client.Get(ctx, key).Result()
			assert.Error(t, err)
			assert.Equal(t, redis.Nil, err)
			_ = result
		}
	})

	t.Run("NonExistent_Key", func(t *testing.T) {
		key := "test:delete:nonexistent"

		deleted, err := client.Del(ctx, key).Result()
		require.NoError(t, err)
		assert.Equal(t, int64(0), deleted)
	})
}

// TestRedis_Clear_AllKeys tests clearing all keys from database
func TestRedis_Clear_AllKeys(t *testing.T) {
	client := setupTestRedis(t)
	defer teardownTestRedis(t)

	ctx := context.Background()

	// Set multiple keys
	for i := 0; i < 10; i++ {
		key := fmt.Sprintf("test:clear:%d", i)
		err := client.Set(ctx, key, fmt.Sprintf("value %d", i), 0).Err()
		require.NoError(t, err)
	}

	// Verify keys exist
	keys, err := client.Keys(ctx, "test:clear:*").Result()
	require.NoError(t, err)
	assert.Len(t, keys, 10)

	// Clear database
	err = client.FlushDB(ctx).Err()
	require.NoError(t, err)

	// Verify all keys deleted
	keys, err = client.Keys(ctx, "test:clear:*").Result()
	require.NoError(t, err)
	assert.Empty(t, keys)
}

// TestRedis_PatternInvalidation tests pattern-based key invalidation
func TestRedis_PatternInvalidation(t *testing.T) {
	client := setupTestRedis(t)
	defer teardownTestRedis(t)

	ctx := context.Background()

	t.Run("Wildcard_Pattern", func(t *testing.T) {
		// Set keys with different prefixes
		prefixes := []string{"project", "item", "link"}
		for _, prefix := range prefixes {
			for i := 0; i < 5; i++ {
				key := fmt.Sprintf("%s:%d", prefix, i)
				err := client.Set(ctx, key, "value", 0).Err()
				require.NoError(t, err)
			}
		}

		// Invalidate project:* pattern
		pattern := "project:*"
		iter := client.Scan(ctx, 0, pattern, 0).Iterator()
		var keysToDelete []string
		for iter.Next(ctx) {
			keysToDelete = append(keysToDelete, iter.Val())
		}
		require.NoError(t, iter.Err())

		if len(keysToDelete) > 0 {
			deleted, err := client.Del(ctx, keysToDelete...).Result()
			require.NoError(t, err)
			assert.Equal(t, int64(5), deleted)
		}

		// Verify project keys deleted
		keys, err := client.Keys(ctx, "project:*").Result()
		require.NoError(t, err)
		assert.Empty(t, keys)

		// Verify other keys still exist
		keys, err = client.Keys(ctx, "item:*").Result()
		require.NoError(t, err)
		assert.Len(t, keys, 5)
	})

	t.Run("Complex_Pattern", func(t *testing.T) {
		// Set keys with UUID-like patterns
		for i := 0; i < 10; i++ {
			key := fmt.Sprintf("cache:user:%d:profile", i)
			err := client.Set(ctx, key, "profile data", 0).Err()
			require.NoError(t, err)
		}

		// Invalidate cache:user:*:profile pattern
		pattern := "cache:user:*:profile"
		iter := client.Scan(ctx, 0, pattern, 0).Iterator()
		var keysToDelete []string
		for iter.Next(ctx) {
			keysToDelete = append(keysToDelete, iter.Val())
		}
		require.NoError(t, iter.Err())

		if len(keysToDelete) > 0 {
			deleted, err := client.Del(ctx, keysToDelete...).Result()
			require.NoError(t, err)
			assert.Equal(t, int64(10), deleted)
		}
	})
}

// TestRedis_ConnectionPool_Health tests connection pool behavior
func TestRedis_ConnectionPool_Health(t *testing.T) {
	client := setupTestRedis(t)
	defer teardownTestRedis(t)

	ctx := context.Background()

	t.Run("Concurrent_Operations", func(t *testing.T) {
		var wg sync.WaitGroup
		errors := make(chan error, 100)

		// 50 concurrent set operations
		for i := 0; i < 50; i++ {
			wg.Add(1)
			go func(idx int) {
				defer wg.Done()
				key := fmt.Sprintf("test:concurrent:set:%d", idx)
				err := client.Set(ctx, key, fmt.Sprintf("value %d", idx), 10*time.Second).Err()
				if err != nil {
					errors <- err
				}
			}(i)
		}

		// 50 concurrent get operations
		for i := 0; i < 50; i++ {
			wg.Add(1)
			go func(idx int) {
				defer wg.Done()
				key := fmt.Sprintf("test:concurrent:get:%d", idx%25)
				// Set the key first to ensure it exists
				_ = client.Set(ctx, key, fmt.Sprintf("value %d", idx), 10*time.Second).Err()
				_, err := client.Get(ctx, key).Result()
				if err != nil && err != redis.Nil {
					errors <- err
				}
			}(i)
		}

		wg.Wait()
		close(errors)

		// Verify no errors
		for err := range errors {
			t.Errorf("Concurrent operation error: %v", err)
		}
	})

	t.Run("Pool_Stats", func(t *testing.T) {
		stats := client.PoolStats()
		assert.NotNil(t, stats)
		t.Logf("Pool Stats - Hits: %d, Misses: %d, Timeouts: %d, TotalConns: %d, IdleConns: %d",
			stats.Hits, stats.Misses, stats.Timeouts, stats.TotalConns, stats.IdleConns)
	})

	t.Run("Ping_Health", func(t *testing.T) {
		result, err := client.Ping(ctx).Result()
		require.NoError(t, err)
		assert.Equal(t, "PONG", result)
	})

	t.Run("Pipeline_Operations", func(t *testing.T) {
		pipe := client.Pipeline()

		// Queue multiple operations
		set1 := pipe.Set(ctx, "test:pipe:1", "value1", 0)
		set2 := pipe.Set(ctx, "test:pipe:2", "value2", 0)
		get1 := pipe.Get(ctx, "test:pipe:1")

		// Execute pipeline
		_, err := pipe.Exec(ctx)
		require.NoError(t, err)

		// Check results
		assert.NoError(t, set1.Err())
		assert.NoError(t, set2.Err())
		result, err := get1.Result()
		require.NoError(t, err)
		assert.Equal(t, "value1", result)
	})

	t.Run("Transaction_Operations", func(t *testing.T) {
		key := "test:tx:counter"
		client.Set(ctx, key, 0, 0)

		// Transaction with optimistic locking
		err := client.Watch(ctx, func(tx *redis.Tx) error {
			val, err := tx.Get(ctx, key).Int()
			if err != nil && err != redis.Nil {
				return err
			}

			_, err = tx.TxPipelined(ctx, func(pipe redis.Pipeliner) error {
				pipe.Set(ctx, key, val+1, 0)
				return nil
			})
			return err
		}, key)

		require.NoError(t, err)

		// Verify increment
		result, err := client.Get(ctx, key).Int()
		require.NoError(t, err)
		assert.Equal(t, 1, result)
	})
}
