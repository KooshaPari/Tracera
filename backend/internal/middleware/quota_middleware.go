package middleware

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"strconv"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
)

const (
	quotaDefaultResetOffset  = 24 * time.Hour
	quotaThrottleDelay       = 5 * time.Second
	quotaDefaultDailyLimit   = 10000
	quotaDefaultMonthlyLimit = 100000
	quotaDefaultGracePercent = 0.05
	monthsInYear             = 12
)

// QuotaPeriod defines the quota reset period
type QuotaPeriod string

// Supported quota periods.
const (
	QuotaPeriodDaily   QuotaPeriod = "daily"
	QuotaPeriodMonthly QuotaPeriod = "monthly"
)

// QuotaAction defines what happens when quota is exceeded
type QuotaAction string

// Supported actions when quota is exceeded.
const (
	QuotaActionReject   QuotaAction = "reject"   // Reject requests
	QuotaActionThrottle QuotaAction = "throttle" // Slow down requests
	QuotaActionBill     QuotaAction = "bill"     // Allow but track for billing
)

// QuotaConfig configures usage quota limits
type QuotaConfig struct {
	// Redis client for distributed quota tracking
	Redis *redis.Client

	// Default quota per period
	DefaultDailyQuota   int64
	DefaultMonthlyQuota int64

	// Action when quota exceeded
	OverageAction QuotaAction

	// Custom quota resolver (e.g., from database based on subscription tier)
	QuotaResolver func(ctx context.Context, userID, apiKeyID string) (daily, monthly int64, err error)

	// Enable quota headers
	AddHeaders bool

	// Grace percentage (allow requests up to grace% over quota before enforcing)
	GracePercentage float64
}

// QuotaMiddleware implements usage quota tracking and enforcement
type QuotaMiddleware struct {
	config QuotaConfig
}

// NewQuotaMiddleware creates a new quota middleware
func NewQuotaMiddleware(config QuotaConfig) *QuotaMiddleware {
	// Set defaults
	if config.DefaultDailyQuota == 0 {
		config.DefaultDailyQuota = quotaDefaultDailyLimit // 10k requests per day
	}
	if config.DefaultMonthlyQuota == 0 {
		config.DefaultMonthlyQuota = quotaDefaultMonthlyLimit // 100k requests per month
	}
	if config.OverageAction == "" {
		config.OverageAction = QuotaActionReject
	}
	if config.GracePercentage == 0 {
		config.GracePercentage = quotaDefaultGracePercent // 5% grace
	}
	config.AddHeaders = true

	return &QuotaMiddleware{
		config: config,
	}
}

// Middleware returns the Echo middleware function
func (m *QuotaMiddleware) Middleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			allowed, err := m.applyQuota(c)
			if err != nil {
				return err
			}
			if !allowed {
				return nil
			}
			return next(c)
		}
	}
}

// quotaCheckResult holds the result of a single period quota check.
type quotaCheckResult struct {
	usage     int64
	remaining int64
	resetTime time.Time
}

// checkAndReportQuota checks one quota period and optionally sets response headers.
func (m *QuotaMiddleware) checkAndReportQuota(
	ctx context.Context, c echo.Context, userID, apiKeyID, label string, period QuotaPeriod, quota int64,
) quotaCheckResult {
	usage, remaining, resetTime, err := m.checkQuota(ctx, userID, apiKeyID, period, quota)
	if err != nil {
		c.Logger().Warnf("Failed to check %s quota: %v", label, err)
	} else if m.config.AddHeaders {
		m.addQuotaHeaders(c, label, quota, remaining, resetTime)
	}
	return quotaCheckResult{usage: usage, remaining: remaining, resetTime: resetTime}
}

func (m *QuotaMiddleware) applyQuota(c echo.Context) (bool, error) {
	if shouldSkipQuota(c) {
		return true, nil
	}

	ctx := c.Request().Context()
	userID := getUserIdentifier(c)
	apiKeyID := getAPIKeyIdentifier(c)

	if userID == "" && apiKeyID == "" {
		return true, nil
	}

	dailyQuota, monthlyQuota, err := m.getQuotas(ctx, userID, apiKeyID)
	if err != nil {
		c.Logger().Warnf("Failed to get quotas: %v", err)
		return true, nil
	}

	daily := m.checkAndReportQuota(ctx, c, userID, apiKeyID, "Daily", QuotaPeriodDaily, dailyQuota)
	monthly := m.checkAndReportQuota(ctx, c, userID, apiKeyID, "Monthly", QuotaPeriodMonthly, monthlyQuota)

	dailyLimit := int64(float64(dailyQuota) * (1.0 + m.config.GracePercentage))
	monthlyLimit := int64(float64(monthlyQuota) * (1.0 + m.config.GracePercentage))

	if daily.usage >= dailyLimit {
		return false, m.handleQuotaExceeded(c, "daily", daily.resetTime)
	}
	if monthly.usage >= monthlyLimit {
		return false, m.handleQuotaExceeded(c, "monthly", monthly.resetTime)
	}

	go m.incrementUsage(context.Background(), userID, apiKeyID)

	return true, nil
}

// getQuotas retrieves the quota limits for a user or API key
func (m *QuotaMiddleware) getQuotas(ctx context.Context, userID, apiKeyID string) (daily, monthly int64, err error) {
	// Use custom resolver if provided
	if m.config.QuotaResolver != nil {
		return m.config.QuotaResolver(ctx, userID, apiKeyID)
	}

	// Use default quotas
	return m.config.DefaultDailyQuota, m.config.DefaultMonthlyQuota, nil
}

// checkQuota checks and returns the current usage for a quota period
func (m *QuotaMiddleware) checkQuota(
	ctx context.Context, userID, apiKeyID string, period QuotaPeriod, limit int64,
) (usage, remaining int64, resetTime time.Time, err error) {
	key := m.getQuotaKey(userID, apiKeyID, period)

	// Get current usage
	usageStr, err := m.config.Redis.Get(ctx, key).Result()
	if err != nil && !errors.Is(err, redis.Nil) {
		return 0, limit, m.getResetTime(period), fmt.Errorf("failed to get quota: %w", err)
	}

	usage = 0
	if usageStr != "" {
		usage, err = strconv.ParseInt(usageStr, 10, 64)
		if err != nil {
			return 0, limit, m.getResetTime(period), fmt.Errorf("failed to parse quota usage: %w", err)
		}
	}

	remaining = limit - usage
	if remaining < 0 {
		remaining = 0
	}

	resetTime = m.getResetTime(period)

	return usage, remaining, resetTime, nil
}

// incrementUsage increments the usage counter for both daily and monthly quotas
func (m *QuotaMiddleware) incrementUsage(ctx context.Context, userID, apiKeyID string) {
	// Increment daily quota
	dailyKey := m.getQuotaKey(userID, apiKeyID, QuotaPeriodDaily)
	dailyTTL := time.Until(getNextMidnight())
	if err := m.config.Redis.Incr(ctx, dailyKey).Err(); err != nil {
		slog.Warn("failed to increment daily quota", "key", dailyKey, "error", err)
	}
	if err := m.config.Redis.Expire(ctx, dailyKey, dailyTTL).Err(); err != nil {
		slog.Warn("failed to set daily quota TTL", "key", dailyKey, "error", err)
	}

	// Increment monthly quota
	monthlyKey := m.getQuotaKey(userID, apiKeyID, QuotaPeriodMonthly)
	monthlyTTL := time.Until(getNextMonthStart())
	if err := m.config.Redis.Incr(ctx, monthlyKey).Err(); err != nil {
		slog.Warn("failed to increment monthly quota", "key", monthlyKey, "error", err)
	}
	if err := m.config.Redis.Expire(ctx, monthlyKey, monthlyTTL).Err(); err != nil {
		slog.Warn("failed to set monthly quota TTL", "key", monthlyKey, "error", err)
	}
}

// getQuotaKey generates a Redis key for quota tracking
func (m *QuotaMiddleware) getQuotaKey(userID, apiKeyID string, period QuotaPeriod) string {
	identifier := userID
	if apiKeyID != "" {
		identifier = "apikey:" + apiKeyID
	}

	now := time.Now()
	var periodKey string

	switch period {
	case QuotaPeriodDaily:
		periodKey = now.Format("2006-01-02")
	case QuotaPeriodMonthly:
		periodKey = now.Format("2006-01")
	}

	return "quota:" + identifier + ":" + string(period) + ":" + periodKey
}

// getResetTime returns when the quota will reset
func (m *QuotaMiddleware) getResetTime(period QuotaPeriod) time.Time {
	switch period {
	case QuotaPeriodDaily:
		return getNextMidnight()
	case QuotaPeriodMonthly:
		return getNextMonthStart()
	default:
		return time.Now().Add(quotaDefaultResetOffset)
	}
}

// handleQuotaExceeded handles quota exceeded scenarios based on configuration
func (m *QuotaMiddleware) handleQuotaExceeded(c echo.Context, period string, resetTime time.Time) error {
	switch m.config.OverageAction {
	case QuotaActionReject:
		return c.JSON(http.StatusPaymentRequired, map[string]interface{}{
			"error":       "quota_exceeded",
			"message":     "Your " + period + " quota has been exceeded",
			"period":      period,
			"reset_time":  resetTime.Unix(),
			"retry_after": int(time.Until(resetTime).Seconds()),
		})

	case QuotaActionThrottle:
		// Add significant delay before allowing request
		time.Sleep(quotaThrottleDelay)
		c.Response().Header().Set("X-Quota-Status", "throttled")
		return nil

	case QuotaActionBill:
		// Allow request but mark for billing
		c.Set("quota_overage", true)
		c.Response().Header().Set("X-Quota-Status", "overage")
		return nil

	default:
		return c.JSON(http.StatusPaymentRequired, map[string]interface{}{
			"error":   "quota_exceeded",
			"message": "Your " + period + " quota has been exceeded",
		})
	}
}

// addQuotaHeaders adds quota information to response headers
func (m *QuotaMiddleware) addQuotaHeaders(c echo.Context, period string, limit, remaining int64, resetTime time.Time) {
	prefix := "X-Quota-" + period
	c.Response().Header().Set(prefix+"-Limit", strconv.FormatInt(limit, 10))
	c.Response().Header().Set(prefix+"-Remaining", strconv.FormatInt(remaining, 10))
	c.Response().Header().Set(prefix+"-Reset", strconv.FormatInt(resetTime.Unix(), 10))
}

// shouldSkipQuota determines if quota tracking should be skipped
func shouldSkipQuota(c echo.Context) bool {
	path := c.Request().URL.Path

	// Skip health checks
	if path == rateLimitPathHealth || path == rateLimitPathPython || path == rateLimitPathGo {
		return true
	}

	// Skip static assets
	if matchPath(path, "/static/*") || matchPath(path, "/assets/*") {
		return true
	}

	return false
}

// getUserIdentifier extracts user identifier from request
func getUserIdentifier(c echo.Context) string {
	if userID := c.Get("user_id"); userID != nil {
		return fmt.Sprint(userID)
	}
	return ""
}

// getAPIKeyIdentifier extracts API key identifier from request
func getAPIKeyIdentifier(c echo.Context) string {
	if apiKeyID := c.Get("api_key_id"); apiKeyID != nil {
		return fmt.Sprint(apiKeyID)
	}
	return ""
}

// getNextMidnight returns the next midnight UTC
func getNextMidnight() time.Time {
	now := time.Now().UTC()
	return time.Date(now.Year(), now.Month(), now.Day()+1, 0, 0, 0, 0, time.UTC)
}

// getNextMonthStart returns the start of next month UTC
func getNextMonthStart() time.Time {
	now := time.Now().UTC()
	year, month := now.Year(), now.Month()

	// Move to next month
	month++
	if month > monthsInYear {
		month = time.January
		year++
	}

	return time.Date(year, month, 1, 0, 0, 0, 0, time.UTC)
}

// ResetQuota manually resets quota for a user or API key (admin function)
func (m *QuotaMiddleware) ResetQuota(ctx context.Context, userID, apiKeyID string, period QuotaPeriod) error {
	key := m.getQuotaKey(userID, apiKeyID, period)
	return m.config.Redis.Del(ctx, key).Err()
}

// GetQuotaUsage retrieves current quota usage
func (m *QuotaMiddleware) GetQuotaUsage(ctx context.Context, userID, apiKeyID string, period QuotaPeriod) (int64, error) {
	key := m.getQuotaKey(userID, apiKeyID, period)

	usageStr, err := m.config.Redis.Get(ctx, key).Result()
	if errors.Is(err, redis.Nil) {
		return 0, nil
	}
	if err != nil {
		return 0, err
	}

	return strconv.ParseInt(usageStr, 10, 64)
}
