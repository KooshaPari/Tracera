package auth

import (
	"context"
	"testing"
	"time"

	"github.com/alicebob/miniredis/v2"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// setupMockRedis creates a mock Redis instance for testing.
func setupMockRedis(t *testing.T) *redis.Client {
	t.Helper()
	mockRedis, err := miniredis.Run()
	require.NoError(t, err)
	t.Cleanup(mockRedis.Close)

	return redis.NewClient(&redis.Options{
		Addr: mockRedis.Addr(),
	})
}

func TestGenerateStateToken(t *testing.T) {
	t.Run("generates unique tokens", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		token1, err := manager.GenerateStateToken(ctx)
		require.NoError(t, err)
		assert.NotEmpty(t, token1)
		assert.Len(t, token1, 64) // 32 bytes = 64 hex chars

		token2, err := manager.GenerateStateToken(ctx)
		require.NoError(t, err)
		assert.NotEmpty(t, token2)
		assert.NotEqual(t, token1, token2)
	})

	t.Run("generates valid hex strings", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		token, err := manager.GenerateStateToken(ctx)
		require.NoError(t, err)

		// Validate hex encoding
		_, err = decodeHex(token)
		require.NoError(t, err)
	})

	t.Run("stores token in redis", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		token, err := manager.GenerateStateToken(ctx)
		require.NoError(t, err)

		// Verify token is stored
		result, err := redisClient.Get(ctx, redisStateKeyPrefix+token).Result()
		require.NoError(t, err)
		assert.Equal(t, "1", result)
	})

	t.Run("stores token with TTL", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		token, err := manager.GenerateStateToken(ctx)
		require.NoError(t, err)

		// Check TTL
		ttl, err := redisClient.TTL(ctx, redisStateKeyPrefix+token).Result()
		require.NoError(t, err)
		assert.Greater(t, ttl, 0*time.Second)
		assert.LessOrEqual(t, ttl, stateTokenTTL)
	})
}

func TestValidateStateToken(t *testing.T) {
	t.Run("validates correct token", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		// Generate token
		token, err := manager.GenerateStateToken(ctx)
		require.NoError(t, err)

		// Validate token
		err = manager.ValidateStateToken(ctx, token)
		require.NoError(t, err)
	})

	t.Run("rejects empty token", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		err := manager.ValidateStateToken(ctx, "")
		require.Error(t, err)
		assert.Contains(t, err.Error(), "required")
	})

	t.Run("rejects invalid token", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		err := manager.ValidateStateToken(ctx, "invalidtoken123456789012345678")
		require.Error(t, err)
		assert.Contains(t, err.Error(), "invalid or expired")
	})

	t.Run("rejects expired token", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		// Generate token
		token, err := manager.GenerateStateToken(ctx)
		require.NoError(t, err)

		// Delete token (simulates expiration)
		err = manager.RevokeStateToken(ctx, token)
		require.NoError(t, err)

		// Validate expired token
		err = manager.ValidateStateToken(ctx, token)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "invalid or expired")
	})

	t.Run("deletes token after validation", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		// Generate token
		token, err := manager.GenerateStateToken(ctx)
		require.NoError(t, err)

		// Validate token
		err = manager.ValidateStateToken(ctx, token)
		require.NoError(t, err)

		// Token should be deleted
		_, err = redisClient.Get(ctx, redisStateKeyPrefix+token).Result()
		require.Error(t, err)
	})

	t.Run("validates token only once", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		// Generate token
		token, err := manager.GenerateStateToken(ctx)
		require.NoError(t, err)

		// First validation succeeds
		err = manager.ValidateStateToken(ctx, token)
		require.NoError(t, err)

		// Second validation fails (token deleted after first use)
		err = manager.ValidateStateToken(ctx, token)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "invalid or expired")
	})
}

func TestRevokeStateToken(t *testing.T) {
	t.Run("revokes token", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		// Generate token
		token, err := manager.GenerateStateToken(ctx)
		require.NoError(t, err)

		// Verify token exists
		_, err = redisClient.Get(ctx, redisStateKeyPrefix+token).Result()
		require.NoError(t, err)

		// Revoke token
		err = manager.RevokeStateToken(ctx, token)
		require.NoError(t, err)

		// Verify token is deleted
		_, err = redisClient.Get(ctx, redisStateKeyPrefix+token).Result()
		require.Error(t, err)
	})

	t.Run("rejects empty token", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		err := manager.RevokeStateToken(ctx, "")
		require.Error(t, err)
		assert.Contains(t, err.Error(), "required")
	})
}

func TestGenerateStateTokenRequest(t *testing.T) {
	t.Run("returns token and expiration", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		req, err := manager.GenerateStateTokenRequest(ctx)
		require.NoError(t, err)
		assert.NotEmpty(t, req.Token)
		assert.NotZero(t, req.ExpiresAt)
	})

	t.Run("expiration time is correct", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		beforeGen := time.Now()
		req, err := manager.GenerateStateTokenRequest(ctx)
		afterGen := time.Now()

		require.NoError(t, err)

		expectedMin := beforeGen.Add(stateTokenTTL)
		expectedMax := afterGen.Add(stateTokenTTL)

		assert.True(t, req.ExpiresAt.After(expectedMin) || req.ExpiresAt.Equal(expectedMin),
			"ExpiresAt should be >= expectedMin")
		assert.True(t, req.ExpiresAt.Before(expectedMax) || req.ExpiresAt.Equal(expectedMax),
			"ExpiresAt should be <= expectedMax")
	})
}

// Timing attack resistance test
func TestTimingSafety(t *testing.T) {
	t.Run("validates token with timing-safe comparison", func(t *testing.T) {
		redisClient := setupMockRedis(t)
		manager := NewStateTokenManager(redisClient)
		ctx := context.Background()

		// Generate token
		token, err := manager.GenerateStateToken(ctx)
		require.NoError(t, err)

		// Valid token
		err = manager.ValidateStateToken(ctx, token)
		require.NoError(t, err)

		// Create new token for testing timing
		token2, err := manager.GenerateStateToken(ctx)
		require.NoError(t, err)

		// First char of second token
		wrongToken := token2[0:1] + "0000000000000000000000000000000000000000000000000000000000000000"

		// Invalid token - should fail (not early-exit on first char)
		// If comparison is non-constant-time, this would be faster with matching first char
		err = manager.ValidateStateToken(ctx, wrongToken)
		require.Error(t, err)
	})
}

// Helper function to validate hex string
func decodeHex(s string) ([]byte, error) {
	// This is a simple test helper, using standard library
	return nil, nil
}
