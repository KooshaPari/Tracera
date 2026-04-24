// Package features defines feature flag evaluation and defaults.
package features

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/redis/go-redis/v9"
)

// FlagStore manages feature flags in Redis
type FlagStore struct {
	redis *redis.Client
}

const flagPrefix = "feature:flag:"

// Feature flag value constants
const (
	flagValueTrue  = "true"
	flagValueFalse = "false"
)

// Common feature flags
const (
	FlagNATSEvents          = "nats_events"
	FlagCrossBackendCalls   = "cross_backend_calls"
	FlagSharedCache         = "shared_cache"
	FlagPythonSpecAnalytics = "python_spec_analytics"
	FlagGoGraphAnalysis     = "go_graph_analysis"
	FlagEnhancedLogging     = "enhanced_logging"
	FlagMetricsCollection   = "metrics_collection"
	FlagDistributedTracing  = "distributed_tracing"
)

// NewFlagStore creates a new feature flag store
func NewFlagStore(redis *redis.Client) *FlagStore {
	return &FlagStore{redis: redis}
}

// IsEnabled checks if a feature flag is enabled
// Returns false by default if flag doesn't exist or error occurs
func (fs *FlagStore) IsEnabled(ctx context.Context, flagName string) bool {
	val, err := fs.redis.Get(ctx, flagPrefix+flagName).Result()
	if err != nil {
		// Default to disabled if flag doesn't exist or error
		return false
	}
	return val == flagValueTrue
}

// SetFlag sets a feature flag value
func (fs *FlagStore) SetFlag(ctx context.Context, flagName string, enabled bool) error {
	value := flagValueFalse
	if enabled {
		value = flagValueTrue
	}
	return fs.redis.Set(ctx, flagPrefix+flagName, value, 0).Err()
}

// EnableFlag enables a feature flag
func (fs *FlagStore) EnableFlag(ctx context.Context, flagName string) error {
	return fs.SetFlag(ctx, flagName, true)
}

// DisableFlag disables a feature flag
func (fs *FlagStore) DisableFlag(ctx context.Context, flagName string) error {
	return fs.SetFlag(ctx, flagName, false)
}

// GetFlag returns the flag value and whether it exists
func (fs *FlagStore) GetFlag(ctx context.Context, flagName string) (bool, bool, error) {
	val, err := fs.redis.Get(ctx, flagPrefix+flagName).Result()
	if errors.Is(err, redis.Nil) {
		return false, false, nil // Flag doesn't exist
	}
	if err != nil {
		return false, false, err
	}
	return val == flagValueTrue, true, nil
}

// DeleteFlag removes a feature flag
func (fs *FlagStore) DeleteFlag(ctx context.Context, flagName string) error {
	return fs.redis.Del(ctx, flagPrefix+flagName).Err()
}

// ListFlags returns all feature flags and their values
func (fs *FlagStore) ListFlags(ctx context.Context) (map[string]bool, error) {
	pattern := flagPrefix + "*"
	flags := make(map[string]bool)
	var cursor uint64
	for {
		keys, nextCursor, err := fs.redis.Scan(ctx, cursor, pattern, 100).Result()
		if err != nil {
			return nil, err
		}
		for _, key := range keys {
			val, err := fs.redis.Get(ctx, key).Result()
			if err != nil {
				continue
			}
			// Remove prefix from key
			flagName := key[len(flagPrefix):]
			flags[flagName] = val == flagValueTrue
		}
		if nextCursor == 0 {
			break
		}
		cursor = nextCursor
	}

	return flags, nil
}

// SetFlagWithTTL sets a flag with an expiration time
func (fs *FlagStore) SetFlagWithTTL(ctx context.Context, flagName string, enabled bool, ttl time.Duration) error {
	value := flagValueFalse
	if enabled {
		value = flagValueTrue
	}
	return fs.redis.Set(ctx, flagPrefix+flagName, value, ttl).Err()
}

// InitializeDefaultFlags sets up default feature flags if they don't exist
func (fs *FlagStore) InitializeDefaultFlags(ctx context.Context) error {
	defaults := map[string]bool{
		FlagNATSEvents:          true,
		FlagCrossBackendCalls:   true,
		FlagSharedCache:         true,
		FlagPythonSpecAnalytics: true,
		FlagGoGraphAnalysis:     true,
		FlagEnhancedLogging:     false,
		FlagMetricsCollection:   true,
		FlagDistributedTracing:  true,
	}

	for flag, defaultValue := range defaults {
		// Only set if flag doesn't exist
		_, exists, err := fs.GetFlag(ctx, flag)
		if err != nil {
			return fmt.Errorf("error checking flag %s: %w", flag, err)
		}
		if !exists {
			if err := fs.SetFlag(ctx, flag, defaultValue); err != nil {
				return fmt.Errorf("error setting default flag %s: %w", flag, err)
			}
		}
	}

	return nil
}
