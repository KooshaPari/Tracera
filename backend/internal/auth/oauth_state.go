package auth

import (
	"context"
	"crypto/rand"
	"crypto/subtle"
	"encoding/hex"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/redis/go-redis/v9"
)

const (
	// OAuth state token length (in bytes, becomes 64 hex characters)
	stateTokenLength = 32

	// OAuth state token TTL
	stateTokenTTL = 10 * time.Minute

	// Redis key prefix for OAuth state tokens
	redisStateKeyPrefix = "oauth:state:"
)

// StateTokenManager handles OAuth state token generation and validation.
// State tokens prevent CSRF attacks during OAuth authorization flow.
type StateTokenManager struct {
	redis *redis.Client
}

// NewStateTokenManager creates a new state token manager.
func NewStateTokenManager(redisClient *redis.Client) *StateTokenManager {
	return &StateTokenManager{
		redis: redisClient,
	}
}

// GenerateStateToken generates a cryptographically secure random state token
// for use in OAuth authorization requests.
//
// Returns a 64-character hex-encoded string (32 random bytes).
// Tokens are stored in Redis with a 10-minute TTL.
func (manager *StateTokenManager) GenerateStateToken(ctx context.Context) (string, error) {
	// Generate cryptographically secure random bytes
	randomBytes := make([]byte, stateTokenLength)
	_, err := rand.Read(randomBytes)
	if err != nil {
		return "", fmt.Errorf("failed to generate random state token: %w", err)
	}

	// Encode as hex string
	stateToken := hex.EncodeToString(randomBytes)

	// Store in Redis with TTL
	redisKey := redisStateKeyPrefix + stateToken
	if err := manager.redis.Set(ctx, redisKey, "1", stateTokenTTL).Err(); err != nil {
		return "", fmt.Errorf("failed to store state token in redis: %w", err)
	}

	return stateToken, nil
}

// ValidateStateToken validates a received state token against the one stored in Redis.
// Uses timing-safe comparison to prevent timing attacks.
//
// Returns an error if:
// - The token is missing or empty
// - The token is not found in Redis (expired or invalid)
// - The token does not match the stored token
func (manager *StateTokenManager) ValidateStateToken(ctx context.Context, stateToken string) error {
	if stateToken == "" {
		return errors.New("state token is required")
	}

	// Retrieve token from Redis
	redisKey := redisStateKeyPrefix + stateToken
	storedToken, err := manager.redis.Get(ctx, redisKey).Result()
	if errors.Is(err, redis.Nil) {
		// Token not found (expired or never created)
		return errors.New("invalid or expired state token")
	}
	if err != nil {
		return fmt.Errorf("failed to validate state token: %w", err)
	}

	// Use timing-safe comparison to prevent timing attacks
	// Even though we're comparing "1" to "1", this pattern scales to comparing tokens
	if subtle.ConstantTimeCompare([]byte(storedToken), []byte("1")) != 1 {
		return errors.New("state token validation failed")
	}

	// Delete token from Redis after validation (one-time use)
	if err := manager.redis.Del(ctx, redisKey).Err(); err != nil {
		// Log but don't fail - token is already validated
		slog.Error("warning: failed to delete state token from redis", "error", err)
	}

	return nil
}

// RevokeStateToken removes a state token from Redis.
// Used to clean up tokens that are no longer needed.
func (manager *StateTokenManager) RevokeStateToken(ctx context.Context, stateToken string) error {
	if stateToken == "" {
		return errors.New("state token is required")
	}

	redisKey := redisStateKeyPrefix + stateToken
	if err := manager.redis.Del(ctx, redisKey).Err(); err != nil {
		return fmt.Errorf("failed to revoke state token: %w", err)
	}

	return nil
}

// StateTokenRequest holds the response from GenerateStateToken
type StateTokenRequest struct {
	Token     string
	ExpiresAt time.Time
}

// GenerateStateTokenRequest generates a state token and returns it with expiration time.
func (manager *StateTokenManager) GenerateStateTokenRequest(ctx context.Context) (*StateTokenRequest, error) {
	token, err := manager.GenerateStateToken(ctx)
	if err != nil {
		return nil, err
	}

	return &StateTokenRequest{
		Token:     token,
		ExpiresAt: time.Now().Add(stateTokenTTL),
	}, nil
}
