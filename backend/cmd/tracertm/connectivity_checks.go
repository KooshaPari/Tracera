package main

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"strings"
	"time"

	"github.com/redis/go-redis/v9"
)

// testConnectivity tests critical service connectivity
func (cfg *EnvConfig) testConnectivity() error {
	var errs []string
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Test Database
	dbCtx, dbCancel := context.WithTimeout(ctx, 5*time.Second)
	if err := testDatabaseConnection(dbCtx, cfg.DatabaseURL); err != nil {
		errs = append(errs, fmt.Sprintf("Database connectivity failed: %v (DATABASE_URL: %s)", err, cfg.DatabaseURL))
	}
	dbCancel()

	// Test Redis
	redisCtx, redisCancel := context.WithTimeout(ctx, 5*time.Second)
	if err := testRedisConnection(redisCtx, cfg.RedisURL); err != nil {
		errs = append(errs, fmt.Sprintf("Redis connectivity failed: %v (REDIS_URL: %s)", err, cfg.RedisURL))
	}
	redisCancel()

	// Test NATS
	natsCtx, natsCancel := context.WithTimeout(ctx, 5*time.Second)
	if err := testNatsConnection(natsCtx, cfg.NatsURL); err != nil {
		errs = append(errs, fmt.Sprintf("NATS connectivity failed: %v (NATS_URL: %s)", err, cfg.NatsURL))
	}
	natsCancel()

	if len(errs) > 0 {
		return errors.New(strings.Join(errs, "\n"))
	}

	return nil
}

// testDatabaseConnection verifies database connectivity
func testDatabaseConnection(ctx context.Context, databaseURL string) error {
	db, err := sql.Open("pgx", databaseURL)
	if err != nil {
		return fmt.Errorf("failed to open database connection: %w", err)
	}
	defer func() {
		if closeErr := db.Close(); closeErr != nil {
			fmt.Printf("warning: database close error: %v\n", closeErr)
		}
	}()

	if err := db.PingContext(ctx); err != nil {
		return fmt.Errorf("database ping failed: %w", err)
	}

	return nil
}

// testRedisConnection verifies Redis connectivity
func testRedisConnection(ctx context.Context, redisURL string) error {
	client := redis.NewClient(&redis.Options{
		Addr: parseRedisURL(redisURL),
	})
	defer func() {
		if closeErr := client.Close(); closeErr != nil {
			fmt.Printf("warning: redis close error: %v\n", closeErr)
		}
	}()

	if err := client.Ping(ctx).Err(); err != nil {
		return fmt.Errorf("redis ping failed: %w", err)
	}

	return nil
}

// testNatsConnection verifies NATS connectivity
func testNatsConnection(_ context.Context, natsURL string) error {
	// NATS connection is tested when initializing the client
	// For now, just validate the URL format
	if !isValidNatsURL(natsURL) {
		return fmt.Errorf("invalid NATS URL format: %s", natsURL)
	}
	return nil
}

func parseRedisURL(redisURL string) string {
	// Extract host:port from redis://host:port
	urlStr := strings.TrimPrefix(redisURL, "redis://")
	urlStr = strings.TrimPrefix(urlStr, "rediss://")
	return urlStr
}
