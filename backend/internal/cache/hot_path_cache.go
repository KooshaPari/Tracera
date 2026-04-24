package cache

import (
	"context"
	"time"
)

// Hot Path Cache Keys

const (
	// UserProfileKey cache for user profile (1h TTL)
	UserProfileKey = "user:profile:"
	// UserProfileTTL - User profiles cache for 1 hour
	UserProfileTTL = 1 * time.Hour

	// UserProjectsKey cache for user's project list (5m TTL)
	UserProjectsKey = "user:projects:"
	// UserProjectsTTL - Project list cached for 5 minutes
	UserProjectsTTL = 5 * time.Minute

	// DashboardSummaryKey cache for dashboard aggregation (2m TTL)
	DashboardSummaryKey = "user:dashboard:"
	// DashboardSummaryTTL - Dashboard summary cached for 2 minutes
	DashboardSummaryTTL = 2 * time.Minute
)

// Helper functions to generate cache keys

// UserProfileCacheKey generates cache key for user profile.
func UserProfileCacheKey(userID string) string {
	return UserProfileKey + userID
}

// UserProjectsCacheKey generates cache key for projects list.
func UserProjectsCacheKey(userID string) string {
	return UserProjectsKey + userID
}

// DashboardSummaryCacheKey generates cache key for dashboard summary.
func DashboardSummaryCacheKey(userID string) string {
	return DashboardSummaryKey + userID
}

// InvalidateUserCache clears all user-specific caches (optional for Cache interface implementations).
func InvalidateUserCache(ctx context.Context, cache Cache, userID string) error {
	keys := []string{
		UserProfileCacheKey(userID),
		UserProjectsCacheKey(userID),
		DashboardSummaryCacheKey(userID),
	}
	return cache.Delete(ctx, keys...)
}

// InvalidateProjectCaches clears caches affected by project changes.
func InvalidateProjectCaches(ctx context.Context, cache Cache, userID string) error {
	keys := []string{
		UserProjectsCacheKey(userID),
		DashboardSummaryCacheKey(userID),
	}
	return cache.Delete(ctx, keys...)
}
