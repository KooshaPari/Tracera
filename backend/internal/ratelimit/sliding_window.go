// Package ratelimit provides sliding-window and adaptive rate limiting.
package ratelimit

import (
	"context"
	"errors"
	"fmt"
	"strconv"
	"time"

	"github.com/redis/go-redis/v9"
)

// SlidingWindowLimiter implements the sliding window rate limiting algorithm
// This provides more accurate rate limiting compared to fixed window approaches
// by considering the timestamp of each request within a sliding time window.
type SlidingWindowLimiter struct {
	redis  *redis.Client
	window time.Duration
	limit  int64
}

// NewSlidingWindowLimiter creates a new sliding window rate limiter
func NewSlidingWindowLimiter(redis *redis.Client, window time.Duration, limit int64) *SlidingWindowLimiter {
	return &SlidingWindowLimiter{
		redis:  redis,
		window: window,
		limit:  limit,
	}
}

// Allow checks if a request should be allowed based on the sliding window algorithm
// Returns: allowed (bool), remaining (int), resetTime (time.Time), error
func (sw *SlidingWindowLimiter) Allow(ctx context.Context, key string) (bool, int, time.Time, error) {
	now := time.Now()
	windowStart := now.Add(-sw.window)

	redisKey := "ratelimit:sliding:" + key

	// Lua script for atomic sliding window check
	// This ensures thread-safety and eliminates race conditions
	script := `
		local key = KEYS[1]
		local now = tonumber(ARGV[1])
		local window_start = tonumber(ARGV[2])
		local limit = tonumber(ARGV[3])
		local ttl = tonumber(ARGV[4])

		-- Remove old entries outside the sliding window
		redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

		-- Count current entries in the window
		local current = redis.call('ZCARD', key)

		if current < limit then
			-- Add new request timestamp
			local unique_key = tostring(now) .. ":" .. tostring(math.random(1000000))
			redis.call('ZADD', key, now, unique_key)
			redis.call('EXPIRE', key, ttl)
			local remaining = limit - current - 1
			return {1, remaining, now + (ttl * 1000)}
		else
			-- Get the oldest timestamp to calculate when a slot opens up
			local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
			local reset_time = now + (ttl * 1000)
			if #oldest > 0 then
				reset_time = tonumber(oldest[2]) + (ttl * 1000)
			end
			return {0, 0, reset_time}
		end
	`

	result, err := sw.redis.Eval(ctx, script,
		[]string{redisKey},
		now.UnixMilli(),
		windowStart.UnixMilli(),
		sw.limit,
		int(sw.window.Seconds()),
	).Result()
	if err != nil {
		return false, 0, now, fmt.Errorf("sliding window check failed: %w", err)
	}

	values, ok := result.([]interface{})
	if !ok || len(values) != 3 {
		return false, 0, now, errors.New("unexpected Redis response format")
	}

	allowedVal, ok := values[0].(int64)
	if !ok {
		return false, 0, now, errors.New("unexpected type for allowed field")
	}
	remainingVal, ok := values[1].(int64)
	if !ok {
		return false, 0, now, errors.New("unexpected type for remaining field")
	}
	resetVal, ok := values[2].(int64)
	if !ok {
		return false, 0, now, errors.New("unexpected type for reset field")
	}

	return allowedVal == 1, int(remainingVal), time.UnixMilli(resetVal), nil
}

// AllowN checks if N requests should be allowed (for bulk operations)
func (sw *SlidingWindowLimiter) AllowN(ctx context.Context, key string, n int) (bool, int, time.Time, error) {
	now := time.Now()
	windowStart := now.Add(-sw.window)

	redisKey := "ratelimit:sliding:" + key

	script := `
		local key = KEYS[1]
		local now = tonumber(ARGV[1])
		local window_start = tonumber(ARGV[2])
		local limit = tonumber(ARGV[3])
		local ttl = tonumber(ARGV[4])
		local requested = tonumber(ARGV[5])

		-- Remove old entries outside the sliding window
		redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

		-- Count current entries in the window
		local current = redis.call('ZCARD', key)

		if current + requested <= limit then
			-- Add N request timestamps
			for i = 1, requested do
				local unique_key = tostring(now) .. ":" .. tostring(i) .. ":" .. tostring(math.random(1000000))
				redis.call('ZADD', key, now, unique_key)
			end
			redis.call('EXPIRE', key, ttl)
			local remaining = limit - current - requested
			return {1, remaining, now + (ttl * 1000)}
		else
			local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
			local reset_time = now + (ttl * 1000)
			if #oldest > 0 then
				reset_time = tonumber(oldest[2]) + (ttl * 1000)
			end
			return {0, 0, reset_time}
		end
	`

	result, err := sw.redis.Eval(ctx, script,
		[]string{redisKey},
		now.UnixMilli(),
		windowStart.UnixMilli(),
		sw.limit,
		int(sw.window.Seconds()),
		n,
	).Result()
	if err != nil {
		return false, 0, now, fmt.Errorf("sliding window bulk check failed: %w", err)
	}

	values, ok := result.([]interface{})
	if !ok || len(values) != 3 {
		return false, 0, now, errors.New("unexpected Redis response format")
	}

	allowedVal, ok := values[0].(int64)
	if !ok {
		return false, 0, now, errors.New("unexpected type for allowed field")
	}
	remainingVal, ok := values[1].(int64)
	if !ok {
		return false, 0, now, errors.New("unexpected type for remaining field")
	}
	resetVal, ok := values[2].(int64)
	if !ok {
		return false, 0, now, errors.New("unexpected type for reset field")
	}

	return allowedVal == 1, int(remainingVal), time.UnixMilli(resetVal), nil
}

// GetUsage returns the current usage count within the sliding window
func (sw *SlidingWindowLimiter) GetUsage(ctx context.Context, key string) (int64, error) {
	now := time.Now()
	windowStart := now.Add(-sw.window)

	redisKey := "ratelimit:sliding:" + key

	// Remove old entries
	_, err := sw.redis.ZRemRangeByScore(ctx, redisKey, "-inf", strconv.FormatInt(windowStart.UnixMilli(), 10)).Result()
	if err != nil {
		return 0, fmt.Errorf("failed to clean old entries: %w", err)
	}

	// Count current entries
	count, err := sw.redis.ZCard(ctx, redisKey).Result()
	if err != nil {
		return 0, fmt.Errorf("failed to get usage count: %w", err)
	}

	return count, nil
}

// Reset clears all rate limit data for a key
func (sw *SlidingWindowLimiter) Reset(ctx context.Context, key string) error {
	redisKey := "ratelimit:sliding:" + key
	return sw.redis.Del(ctx, redisKey).Err()
}

// GetLimit returns the configured limit
func (sw *SlidingWindowLimiter) GetLimit() int64 {
	return sw.limit
}

// GetWindow returns the configured window duration
func (sw *SlidingWindowLimiter) GetWindow() time.Duration {
	return sw.window
}
