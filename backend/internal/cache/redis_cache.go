package cache

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/redis/go-redis/v9"
)

const (
	redisCacheDefaultPoolSize     = 10
	redisCacheDefaultMinIdleConns = 2
	redisCachePingTimeout         = 5 * time.Second
)

// RedisCacheConfig configures a Redis-backed cache.
type RedisCacheConfig struct {
	// RedisURL is the Redis connection URL (for example, "redis://user:pass@host:6379/0").
	RedisURL string
	// DefaultTTL is the default time-to-live applied to writes (for example via Set).
	DefaultTTL time.Duration
	// KeyPrefix is prepended to every key written/read by this cache instance.
	KeyPrefix string
	// EnableMetrics enables in-memory metrics collection for cache operations.
	EnableMetrics bool
	// PoolSize is the Redis client's connection pool size; non-positive values use a default.
	PoolSize int
	// MinIdleConns is the minimum number of idle connections to keep; non-positive values use a default.
	MinIdleConns int
}

// RedisCache provides caching functionality using Redis.
type RedisCache struct {
	client     *redis.Client
	defaultTTL time.Duration
	keyPrefix  string
	metrics    *Metrics
}

func normalizeRedisCacheConfig(cfg *RedisCacheConfig) {
	if cfg.PoolSize <= 0 {
		cfg.PoolSize = redisCacheDefaultPoolSize
	}
	if cfg.MinIdleConns < 0 {
		cfg.MinIdleConns = 0
	}
	if cfg.MinIdleConns == 0 {
		cfg.MinIdleConns = redisCacheDefaultMinIdleConns
	}
}

func validateRedisAddr(addr string) error {
	if addr == "" || addr == ":" || addr == "localhost:" {
		return errors.New("failed to parse Redis URL: empty address")
	}
	return nil
}

// NewRedisCache constructs a Redis-backed cache from cfg and returns a connected
// RedisCache instance (it pings Redis during initialization).
func NewRedisCache(cfg RedisCacheConfig) (*RedisCache, error) {
	opt, err := redis.ParseURL(cfg.RedisURL)
	if err != nil {
		return nil, fmt.Errorf("failed to parse Redis URL: %w", err)
	}
	if err := validateRedisAddr(opt.Addr); err != nil {
		return nil, err
	}

	normalizeRedisCacheConfig(&cfg)

	opt.PoolSize = cfg.PoolSize
	opt.MinIdleConns = cfg.MinIdleConns

	rc := &RedisCache{
		client:     redis.NewClient(opt),
		defaultTTL: cfg.DefaultTTL,
		keyPrefix:  cfg.KeyPrefix,
	}
	if cfg.EnableMetrics {
		rc.metrics = &Metrics{}
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisCachePingTimeout)
	defer cancel()

	if err := rc.client.Ping(ctx).Err(); err != nil {
		if closeErr := rc.client.Close(); closeErr != nil {
			slog.Error("failed to close Redis client", "error", closeErr)
		}
		return nil, fmt.Errorf("failed to connect to Redis: %w", err)
	}

	return rc, nil
}

func (rc *RedisCache) prefixedKey(key string) string {
	if rc.keyPrefix == "" {
		return key
	}
	return rc.keyPrefix + key
}

func (rc *RedisCache) recordGetRequest() {
	if rc.metrics == nil {
		return
	}
	rc.metrics.TotalRequests++
}

func (rc *RedisCache) recordGetMiss(start time.Time) {
	if rc.metrics == nil {
		return
	}
	rc.metrics.Misses++
	rc.metrics.GetLatencyTotal += time.Since(start).Nanoseconds()
}

func (rc *RedisCache) recordGetError(start time.Time) {
	if rc.metrics == nil {
		return
	}
	rc.metrics.Errors++
	rc.metrics.Misses++
	rc.metrics.GetLatencyTotal += time.Since(start).Nanoseconds()
}

func (rc *RedisCache) recordGetHit(start time.Time, bytesRead int) {
	if rc.metrics == nil {
		return
	}
	rc.metrics.Hits++
	rc.metrics.BytesRead += int64(bytesRead)
	rc.metrics.GetLatencyTotal += time.Since(start).Nanoseconds()
}

func (rc *RedisCache) recordUnmarshalError() {
	if rc.metrics == nil {
		return
	}
	rc.metrics.Errors++
}

// Get reads a JSON-encoded value from Redis into dest.
//
// Behavior note: a cache miss is not treated as an error; dest is left unchanged and nil is returned.
func (rc *RedisCache) Get(ctx context.Context, key string, dest interface{}) error {
	start := time.Now()
	rc.recordGetRequest()

	val, err := rc.client.Get(ctx, rc.prefixedKey(key)).Bytes()
	if err != nil {
		if errors.Is(err, redis.Nil) {
			rc.recordGetMiss(start)
			return nil
		}
		rc.recordGetError(start)
		return err
	}

	rc.recordGetHit(start, len(val))

	if err := json.Unmarshal(val, dest); err != nil {
		rc.recordUnmarshalError()
		return fmt.Errorf("failed to unmarshal: %w", err)
	}

	return nil
}

// Set writes value to Redis using the cache's default TTL.
func (rc *RedisCache) Set(ctx context.Context, key string, value interface{}) error {
	return rc.SetWithTTL(ctx, key, value, rc.defaultTTL)
}

// SetWithTTL writes value to Redis with an explicit TTL.
func (rc *RedisCache) SetWithTTL(ctx context.Context, key string, value interface{}, ttl time.Duration) error {
	start := time.Now()
	if rc.metrics != nil {
		rc.metrics.Sets++
		rc.metrics.KeyCount++
	}

	data, err := json.Marshal(value)
	if err != nil {
		if rc.metrics != nil {
			rc.metrics.Errors++
		}
		return err
	}
	if rc.metrics != nil {
		rc.metrics.BytesWritten += int64(len(data))
	}

	err = rc.client.Set(ctx, rc.prefixedKey(key), data, ttl).Err()
	if rc.metrics != nil {
		rc.metrics.SetLatencyTotal += time.Since(start).Nanoseconds()
		if err != nil {
			rc.metrics.Errors++
		}
	}
	return err
}

// Delete removes one or more keys from Redis.
func (rc *RedisCache) Delete(ctx context.Context, keys ...string) error {
	if len(keys) == 0 {
		return nil
	}

	start := time.Now()

	prefixed := make([]string, 0, len(keys))
	for _, k := range keys {
		prefixed = append(prefixed, rc.prefixedKey(k))
	}

	err := rc.client.Del(ctx, prefixed...).Err()
	if rc.metrics != nil {
		rc.metrics.Deletes += int64(len(keys))
		rc.metrics.KeyCount -= int64(len(keys))
		rc.metrics.DeleteLatencyTotal += time.Since(start).Nanoseconds()
		if err != nil {
			rc.metrics.Errors++
		}
	}
	return err
}

// InvalidatePattern deletes keys matching the given Redis glob-style pattern.
//
// This uses SCAN to avoid blocking Redis.
func (rc *RedisCache) InvalidatePattern(ctx context.Context, pattern string) error {
	if pattern == "" {
		return nil
	}

	// Use SCAN to avoid blocking Redis.
	var cursor uint64
	for {
		keys, next, err := rc.client.Scan(ctx, cursor, rc.prefixedKey(pattern), 500).Result()
		if err != nil {
			return err
		}
		if len(keys) > 0 {
			if err := rc.client.Del(ctx, keys...).Err(); err != nil {
				return err
			}
		}
		cursor = next
		if cursor == 0 {
			break
		}
	}

	return nil
}

// TTL returns the remaining time-to-live for key.
func (rc *RedisCache) TTL(ctx context.Context, key string) (time.Duration, error) {
	ttl, err := rc.client.TTL(ctx, rc.prefixedKey(key)).Result()
	if err != nil {
		return 0, err
	}
	return ttl, nil
}

func rawMessageFromMGetValue(value interface{}) (json.RawMessage, bool) {
	switch v := value.(type) {
	case string:
		return json.RawMessage([]byte(v)), true
	case []byte:
		return json.RawMessage(v), true
	default:
		return nil, false
	}
}

// GetMany fetches multiple keys and returns a map of key to raw JSON value.
//
// Missing keys are omitted from the returned map.
func (rc *RedisCache) GetMany(ctx context.Context, keys []string) (map[string]json.RawMessage, error) {
	if len(keys) == 0 {
		return map[string]json.RawMessage{}, nil
	}

	prefixed := make([]string, 0, len(keys))
	for _, k := range keys {
		prefixed = append(prefixed, rc.prefixedKey(k))
	}

	vals, err := rc.client.MGet(ctx, prefixed...).Result()
	if err != nil {
		if rc.metrics != nil {
			rc.metrics.Errors++
		}
		return nil, err
	}

	out := make(map[string]json.RawMessage, len(keys))
	for idx, val := range vals {
		if val == nil {
			continue
		}
		raw, ok := rawMessageFromMGetValue(val)
		if !ok {
			continue
		}
		out[keys[idx]] = raw
	}

	return out, nil
}

// SetMany writes multiple items to Redis with the given TTL.
func (rc *RedisCache) SetMany(ctx context.Context, items map[string]interface{}, ttl time.Duration) error {
	if len(items) == 0 {
		return nil
	}

	pipe := rc.client.Pipeline()
	for k, v := range items {
		data, err := json.Marshal(v)
		if err != nil {
			return err
		}
		pipe.Set(ctx, rc.prefixedKey(k), data, ttl)
	}

	_, err := pipe.Exec(ctx)
	if err != nil && rc.metrics != nil {
		rc.metrics.Errors++
	}
	return err
}

// Exists returns the count of keys that exist in Redis.
func (rc *RedisCache) Exists(ctx context.Context, keys ...string) (int64, error) {
	if len(keys) == 0 {
		return 0, nil
	}
	prefixed := make([]string, 0, len(keys))
	for _, k := range keys {
		prefixed = append(prefixed, rc.prefixedKey(k))
	}
	count, err := rc.client.Exists(ctx, prefixed...).Result()
	if err != nil && rc.metrics != nil {
		rc.metrics.Errors++
	}
	return count, err
}

// Increment atomically increments the integer value stored at key and returns the new value.
func (rc *RedisCache) Increment(ctx context.Context, key string) (int64, error) {
	val, err := rc.client.Incr(ctx, rc.prefixedKey(key)).Result()
	if err != nil && rc.metrics != nil {
		rc.metrics.Errors++
	}
	return val, err
}

// IncrementWithExpiry increments key and sets its expiry as part of the same pipeline execution.
func (rc *RedisCache) IncrementWithExpiry(ctx context.Context, key string, expiry time.Duration) (int64, error) {
	pipe := rc.client.TxPipeline()
	incr := pipe.Incr(ctx, rc.prefixedKey(key))
	pipe.Expire(ctx, rc.prefixedKey(key), expiry)
	_, err := pipe.Exec(ctx)
	if err != nil {
		if rc.metrics != nil {
			rc.metrics.Errors++
		}
		return 0, err
	}
	return incr.Val(), nil
}

// SetWithTags writes key with TTL and associates it with the provided tags for later invalidation.
func (rc *RedisCache) SetWithTags(
	ctx context.Context,
	key string,
	value interface{},
	ttl time.Duration,
	tags []string,
) error {
	if err := rc.SetWithTTL(ctx, key, value, ttl); err != nil {
		return err
	}
	for _, tag := range tags {
		if tag == "" {
			continue
		}
		tagKey := rc.prefixedKey("tag:" + tag)
		if err := rc.client.SAdd(ctx, tagKey, rc.prefixedKey(key)).Err(); err != nil {
			return err
		}
		if err := rc.client.Expire(ctx, tagKey, ttl).Err(); err != nil {
			// Best-effort: tag TTL isn't required for correctness of the current write path.
			slog.Error("failed to set tag TTL for", "error", tagKey, "error", err)
		}
	}
	return nil
}

func (rc *RedisCache) invalidateTag(ctx context.Context, tag string) error {
	tagKey := rc.prefixedKey("tag:" + tag)

	members, err := rc.client.SMembers(ctx, tagKey).Result()
	if err != nil {
		return err
	}
	if len(members) > 0 {
		if err := rc.client.Del(ctx, members...).Err(); err != nil {
			return err
		}
	}
	return rc.client.Del(ctx, tagKey).Err()
}

// InvalidateTags deletes all keys associated with the provided tags.
func (rc *RedisCache) InvalidateTags(ctx context.Context, tags []string) error {
	for _, tag := range tags {
		if tag == "" {
			continue
		}
		if err := rc.invalidateTag(ctx, tag); err != nil {
			return err
		}
	}
	return nil
}

// GetMetrics returns cache metrics when metrics are enabled, or nil otherwise.
func (rc *RedisCache) GetMetrics() *Metrics {
	return rc.metrics
}

// Close closes the underlying Redis client.
func (rc *RedisCache) Close() error {
	if rc.client == nil {
		return nil
	}
	return rc.client.Close()
}
