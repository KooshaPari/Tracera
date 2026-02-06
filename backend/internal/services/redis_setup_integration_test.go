//go:build integration

package services

import (
	"context"
	"testing"
	"time"

	redisclient "github.com/redis/go-redis/v9"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/modules/redis"
	"github.com/testcontainers/testcontainers-go/wait"
)

const (
	redisSetupStartupTimeout = 10 * time.Second
	redisSetupTestTimeout    = 30 * time.Second
)

// RedisContainer wraps a Redis test container
type RedisContainer struct {
	Container *redis.RedisContainer
	Client    *redisclient.Client
	URL       string
}

// SetupRedisContainer creates and initializes a Redis test container
func SetupRedisContainer(ctx context.Context, t *testing.T) *RedisContainer {
	// Create Redis container
	redisContainer, err := redis.RunContainer(ctx,
		testcontainers.WithImage("redis:7-alpine"),
		testcontainers.WithWaitStrategy(
			wait.ForLog("Ready to accept connections").
				WithStartupTimeout(redisSetupStartupTimeout),
		),
	)
	if err != nil {
		t.Fatalf("Failed to start Redis container: %v", err)
	}

	// Get connection URL
	url, err := redisContainer.ConnectionString(ctx)
	if err != nil {
		t.Fatalf("Failed to get connection string: %v", err)
	}

	// Create Redis client
	opts, err := redisclient.ParseURL(url)
	if err != nil {
		t.Fatalf("Failed to parse Redis URL: %v", err)
	}

	client := redisclient.NewClient(opts)

	// Test connection
	if err := client.Ping(ctx).Err(); err != nil {
		t.Fatalf("Failed to ping Redis: %v", err)
	}

	return &RedisContainer{
		Container: redisContainer,
		Client:    client,
		URL:       url,
	}
}

// Close cleans up the container and client
func (rc *RedisContainer) Close(ctx context.Context) error {
	if rc.Client != nil {
		rc.Client.Close()
	}
	if rc.Container != nil {
		return rc.Container.Terminate(ctx)
	}
	return nil
}

// Flush clears all data from Redis
func (rc *RedisContainer) Flush(ctx context.Context) error {
	return rc.Client.FlushAll(ctx).Err()
}

// TestRedisContainer tests the Redis container setup
func TestRedisContainer(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisSetupTestTimeout)
	defer cancel()

	rc := SetupRedisContainer(ctx, t)
	defer func() { _ = rc.Close(ctx) }()

	// Test basic set/get
	key := "test_key"
	value := "test_value"

	if err := rc.Client.Set(ctx, key, value, 0).Err(); err != nil {
		t.Fatalf("Failed to set key: %v", err)
	}

	result, err := rc.Client.Get(ctx, key).Result()
	if err != nil {
		t.Fatalf("Failed to get key: %v", err)
	}

	if result != value {
		t.Fatalf("Expected %q, got %q", value, result)
	}
}
