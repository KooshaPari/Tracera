// Package metrics provides service and business metrics collection.
package metrics

import (
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

// BusinessMetrics provides business-level metrics for user engagement,
// feature adoption, and product analytics
type BusinessMetrics struct {
	// User session metrics
	ActiveUsers        *prometheus.GaugeVec     // Current active users (by time window: realtime, daily, weekly, monthly)
	UserSessions       *prometheus.CounterVec   // Total user sessions
	SessionDuration    *prometheus.HistogramVec // Session duration distribution
	UniqueUsersDaily   prometheus.Gauge         // Unique users in last 24 hours
	UniqueUsersWeekly  prometheus.Gauge         // Unique users in last 7 days
	UniqueUsersMonthly prometheus.Gauge         // Unique users in last 30 days

	// API usage metrics
	EndpointUsage   *prometheus.CounterVec   // API endpoint usage (by endpoint, user, status)
	EndpointLatency *prometheus.HistogramVec // Latency per endpoint
	APICallsPerUser *prometheus.HistogramVec // Distribution of API calls per user

	// Feature adoption metrics
	FeatureUsage        *prometheus.CounterVec // Feature usage (by feature, user_id, action)
	FeatureAdoptionRate *prometheus.GaugeVec   // % of users using each feature
	NewFeatureUsers     *prometheus.CounterVec // Users trying feature for first time

	// User journey metrics
	JourneyStarts      *prometheus.CounterVec   // Journey starts (by journey_type)
	JourneyCompletions *prometheus.CounterVec   // Journey completions (by journey_type)
	JourneySteps       *prometheus.CounterVec   // Step completions (by journey_type, step)
	JourneyDuration    *prometheus.HistogramVec // Time to complete journey
	JourneyDropoffs    *prometheus.CounterVec   // Journey dropoffs (by journey_type, step)

	// Content creation metrics
	ItemsCreated     *prometheus.CounterVec // Items created (by type, user)
	LinksCreated     *prometheus.CounterVec // Links created (by type, user)
	ProjectsCreated  *prometheus.CounterVec // Projects created (by user)
	TestCasesCreated *prometheus.CounterVec // Test cases created (by user)
	SpecsCreated     *prometheus.CounterVec // Specifications created (by type, user)

	// Content updates
	ItemsUpdated *prometheus.CounterVec // Items updated
	ItemsDeleted *prometheus.CounterVec // Items deleted
	LinksDeleted *prometheus.CounterVec // Links deleted

	// Search and discovery metrics
	SearchQueries      *prometheus.CounterVec   // Search queries (by query_type, result_count_bucket)
	SearchResultClicks *prometheus.CounterVec   // Search result clicks (by position)
	SearchLatency      *prometheus.HistogramVec // Search latency
	EmptySearchResults *prometheus.CounterVec   // Searches with 0 results

	// Graph interaction metrics
	GraphViews     *prometheus.CounterVec // Graph views (by graph_type)
	NodeExpansions *prometheus.CounterVec // Node expansions in graph
	GraphExports   *prometheus.CounterVec // Graph exports (by format)
	GraphFilters   *prometheus.CounterVec // Graph filter applications

	// Integration usage
	IntegrationSyncs  *prometheus.CounterVec // Integration syncs (by integration_type, status)
	IntegrationErrors *prometheus.CounterVec // Integration errors (by integration_type, error_type)
	GitHubPRs         prometheus.Counter     // GitHub PRs analyzed
	JiraIssues        prometheus.Counter     // Jira issues imported
	FigmaFiles        prometheus.Counter     // Figma files synced

	// Collaboration metrics
	TeamMembers     *prometheus.GaugeVec   // Team members (by team_id)
	CommentsCreated *prometheus.CounterVec // Comments created
	ReactionsAdded  *prometheus.CounterVec // Reactions added (by type)
	MentionsUsed    prometheus.Counter     // @mentions used

	// Performance user experience
	PageLoadTimes *prometheus.HistogramVec // Page load times (by page)
	WebVitalsLCP  *prometheus.HistogramVec // Largest Contentful Paint
	WebVitalsFID  *prometheus.HistogramVec // First Input Delay
	WebVitalsCLS  *prometheus.HistogramVec // Cumulative Layout Shift
	WebVitalsTTFB *prometheus.HistogramVec // Time to First Byte
	WebVitalsINP  *prometheus.HistogramVec // Interaction to Next Paint

	// Error tracking
	JSErrors           *prometheus.CounterVec // JavaScript errors (by component)
	APIErrors          *prometheus.CounterVec // API errors experienced by users
	UserReportedIssues prometheus.Counter     // User-reported issues
}

//nolint:gochecknoglobals // sync.Once singleton for lazy-initialized Prometheus business metrics
var (
	businessMetricsInstance     *BusinessMetrics
	businessMetricsInstanceOnce sync.Once
	businessMetricsNamespace    = defaultMetricsNamespace
)

// GetBusinessMetrics returns the global business metrics instance (lazy-initialized).
func GetBusinessMetrics() *BusinessMetrics {
	businessMetricsInstanceOnce.Do(func() {
		businessMetricsInstance = NewBusinessMetrics(businessMetricsNamespace)
	})
	return businessMetricsInstance
}

// InitializeBusinessMetrics sets the namespace for business metrics.
// This must be called before GetBusinessMetrics() if a custom namespace is desired.
func InitializeBusinessMetrics(namespace string) {
	if namespace != "" {
		businessMetricsNamespace = namespace
	}
}

// NewBusinessMetrics creates and registers all business-level Prometheus metrics
func NewBusinessMetrics(namespace string) *BusinessMetrics {
	if namespace == "" {
		namespace = defaultMetricsNamespace
	}

	bm := &BusinessMetrics{}
	initUserSessionMetrics(bm, namespace)
	initAPIMetrics(bm, namespace)
	initFeatureMetrics(bm, namespace)
	initJourneyMetrics(bm, namespace)
	initContentMetrics(bm, namespace)
	initContentUpdateMetrics(bm, namespace)
	initSearchMetrics(bm, namespace)
	initGraphMetrics(bm, namespace)
	initIntegrationMetrics(bm, namespace)
	initCollaborationMetrics(bm, namespace)
	initPerformanceMetrics(bm, namespace)
	initErrorMetrics(bm, namespace)
	return bm
}

const (
	defaultMetricsNamespace = "tracertm"
	resultBucketMaxSmall    = 10
	resultBucketMaxMedium   = 50
)

func initUserSessionMetrics(bm *BusinessMetrics, namespace string) {
	bm.ActiveUsers = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Subsystem: "users",
			Name:      "active_total",
			Help:      "Currently active users by time window",
		},
		[]string{"window"},
	)

	bm.UserSessions = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "users",
			Name:      "sessions_total",
			Help:      "Total user sessions",
		},
		[]string{"user_id"},
	)

	bm.SessionDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Subsystem: "users",
			Name:      "session_duration_seconds",
			Help:      "User session duration distribution",
			Buckets:   []float64{60, 300, 600, 1800, 3600, 7200, 14400},
		},
		[]string{"user_id"},
	)

	bm.UniqueUsersDaily = promauto.NewGauge(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Subsystem: "users",
			Name:      "unique_daily",
			Help:      "Unique users in last 24 hours",
		},
	)

	bm.UniqueUsersWeekly = promauto.NewGauge(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Subsystem: "users",
			Name:      "unique_weekly",
			Help:      "Unique users in last 7 days",
		},
	)

	bm.UniqueUsersMonthly = promauto.NewGauge(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Subsystem: "users",
			Name:      "unique_monthly",
			Help:      "Unique users in last 30 days",
		},
	)
}

func initAPIMetrics(bm *BusinessMetrics, namespace string) {
	bm.EndpointUsage = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "api",
			Name:      "endpoint_usage_total",
			Help:      "API endpoint usage by endpoint and user",
		},
		[]string{"endpoint", "method", "user_id", "status"},
	)

	bm.EndpointLatency = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Subsystem: "api",
			Name:      "endpoint_latency_seconds",
			Help:      "API endpoint latency distribution",
			Buckets:   prometheus.DefBuckets,
		},
		[]string{"endpoint", "method"},
	)

	bm.APICallsPerUser = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Subsystem: "api",
			Name:      "calls_per_user",
			Help:      "Distribution of API calls per user per hour",
			Buckets:   []float64{1, 5, 10, 25, 50, 100, 250, 500, 1000},
		},
		[]string{"user_id"},
	)
}

func initFeatureMetrics(bm *BusinessMetrics, namespace string) {
	bm.FeatureUsage = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "features",
			Name:      "usage_total",
			Help:      "Feature usage by feature and action",
		},
		[]string{"feature", "action", "user_id"},
	)

	bm.FeatureAdoptionRate = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Subsystem: "features",
			Name:      "adoption_rate",
			Help:      "Percentage of users using each feature",
		},
		[]string{"feature"},
	)

	bm.NewFeatureUsers = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "features",
			Name:      "new_users_total",
			Help:      "Users trying feature for first time",
		},
		[]string{"feature", "user_id"},
	)
}

func initJourneyMetrics(bm *BusinessMetrics, namespace string) {
	bm.JourneyStarts = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "journeys",
			Name:      "starts_total",
			Help:      "Journey starts by type",
		},
		[]string{"journey_type"},
	)

	bm.JourneyCompletions = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "journeys",
			Name:      "completions_total",
			Help:      "Journey completions by type",
		},
		[]string{"journey_type"},
	)

	bm.JourneySteps = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "journeys",
			Name:      "steps_total",
			Help:      "Journey step completions by type and step",
		},
		[]string{"journey_type", "step", "user_id"},
	)

	bm.JourneyDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Subsystem: "journeys",
			Name:      "duration_seconds",
			Help:      "Journey completion duration",
			Buckets:   []float64{60, 300, 600, 1800, 3600, 7200, 14400},
		},
		[]string{"journey_type"},
	)

	bm.JourneyDropoffs = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "journeys",
			Name:      "dropoffs_total",
			Help:      "Journey dropoffs by type and step",
		},
		[]string{"journey_type", "step"},
	)
}

func initContentMetrics(bm *BusinessMetrics, namespace string) {
	bm.ItemsCreated = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "content",
			Name:      "items_created_total",
			Help:      "Items created by type and user",
		},
		[]string{"type", "user_id"},
	)

	bm.LinksCreated = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "content",
			Name:      "links_created_total",
			Help:      "Links created by type and user",
		},
		[]string{"type", "user_id"},
	)

	bm.ProjectsCreated = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "content",
			Name:      "projects_created_total",
			Help:      "Projects created by user",
		},
		[]string{"user_id"},
	)

	bm.TestCasesCreated = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "content",
			Name:      "test_cases_created_total",
			Help:      "Test cases created by user",
		},
		[]string{"user_id"},
	)

	bm.SpecsCreated = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "content",
			Name:      "specs_created_total",
			Help:      "Specifications created by type and user",
		},
		[]string{"type", "user_id"},
	)
}

func initContentUpdateMetrics(bm *BusinessMetrics, namespace string) {
	bm.ItemsUpdated = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "content",
			Name:      "items_updated_total",
			Help:      "Items updated",
		},
		[]string{"type", "user_id"},
	)

	bm.ItemsDeleted = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "content",
			Name:      "items_deleted_total",
			Help:      "Items deleted",
		},
		[]string{"type", "user_id"},
	)

	bm.LinksDeleted = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "content",
			Name:      "links_deleted_total",
			Help:      "Links deleted",
		},
		[]string{"type", "user_id"},
	)
}

func initSearchMetrics(bm *BusinessMetrics, namespace string) {
	bm.SearchQueries = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "search",
			Name:      "queries_total",
			Help:      "Search queries by type and result count bucket",
		},
		[]string{"query_type", "result_bucket"},
	)

	bm.SearchResultClicks = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "search",
			Name:      "result_clicks_total",
			Help:      "Search result clicks by position",
		},
		[]string{"position"},
	)

	bm.SearchLatency = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Subsystem: "search",
			Name:      "latency_seconds",
			Help:      "Search latency distribution",
			Buckets:   []float64{0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5},
		},
		[]string{"query_type"},
	)

	bm.EmptySearchResults = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "search",
			Name:      "empty_results_total",
			Help:      "Searches with zero results by query type",
		},
		[]string{"query_type"},
	)
}

func initGraphMetrics(bm *BusinessMetrics, namespace string) {
	bm.GraphViews = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "graph",
			Name:      "views_total",
			Help:      "Graph views by type",
		},
		[]string{"graph_type"},
	)

	bm.NodeExpansions = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "graph",
			Name:      "node_expansions_total",
			Help:      "Node expansions in graph",
		},
		[]string{"node_type"},
	)

	bm.GraphExports = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "graph",
			Name:      "exports_total",
			Help:      "Graph exports by format",
		},
		[]string{"format"},
	)

	bm.GraphFilters = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "graph",
			Name:      "filters_total",
			Help:      "Graph filter applications",
		},
		[]string{"filter_type"},
	)
}

func initIntegrationMetrics(bm *BusinessMetrics, namespace string) {
	bm.IntegrationSyncs = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "integrations",
			Name:      "syncs_total",
			Help:      "Integration syncs by type and status",
		},
		[]string{"integration_type", "status"},
	)

	bm.IntegrationErrors = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "integrations",
			Name:      "errors_total",
			Help:      "Integration errors by type and error",
		},
		[]string{"integration_type", "error_type"},
	)

	bm.GitHubPRs = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "integrations",
			Name:      "github_prs_total",
			Help:      "GitHub PRs analyzed",
		},
	)

	bm.JiraIssues = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "integrations",
			Name:      "jira_issues_total",
			Help:      "Jira issues imported",
		},
	)

	bm.FigmaFiles = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "integrations",
			Name:      "figma_files_total",
			Help:      "Figma files synced",
		},
	)
}

func initCollaborationMetrics(bm *BusinessMetrics, namespace string) {
	bm.TeamMembers = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Subsystem: "collaboration",
			Name:      "team_members_total",
			Help:      "Team members by team",
		},
		[]string{"team_id"},
	)

	bm.CommentsCreated = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "collaboration",
			Name:      "comments_total",
			Help:      "Comments created",
		},
		[]string{"user_id"},
	)

	bm.ReactionsAdded = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "collaboration",
			Name:      "reactions_total",
			Help:      "Reactions added by type",
		},
		[]string{"reaction_type", "user_id"},
	)

	bm.MentionsUsed = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "collaboration",
			Name:      "mentions_total",
			Help:      "@mentions used",
		},
	)
}

func initPerformanceMetrics(bm *BusinessMetrics, namespace string) {
	initPageLoadMetrics(bm, namespace)
	initWebVitalsMetrics(bm, namespace)
}

func initPageLoadMetrics(bm *BusinessMetrics, namespace string) {
	bm.PageLoadTimes = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Subsystem: "performance",
			Name:      "page_load_seconds",
			Help:      "Page load times by page",
			Buckets:   []float64{0.5, 1, 2, 3, 5, 7, 10, 15},
		},
		[]string{"page"},
	)
}

func initWebVitalsMetrics(bm *BusinessMetrics, namespace string) {
	bm.WebVitalsLCP = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Subsystem: "performance",
			Name:      "lcp_seconds",
			Help:      "Largest Contentful Paint",
			Buckets:   []float64{0.5, 1, 2, 2.5, 3, 4, 5},
		},
		[]string{"page", "rating"},
	)

	bm.WebVitalsFID = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Subsystem: "performance",
			Name:      "fid_seconds",
			Help:      "First Input Delay",
			Buckets:   []float64{0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 1},
		},
		[]string{"page", "rating"},
	)

	bm.WebVitalsCLS = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Subsystem: "performance",
			Name:      "cls_score",
			Help:      "Cumulative Layout Shift",
			Buckets:   []float64{0.01, 0.05, 0.1, 0.25, 0.5, 1, 2},
		},
		[]string{"page", "rating"},
	)

	bm.WebVitalsTTFB = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Subsystem: "performance",
			Name:      "ttfb_seconds",
			Help:      "Time to First Byte",
			Buckets:   []float64{0.05, 0.1, 0.2, 0.3, 0.5, 1, 2},
		},
		[]string{"page", "rating"},
	)

	bm.WebVitalsINP = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Subsystem: "performance",
			Name:      "inp_seconds",
			Help:      "Interaction to Next Paint",
			Buckets:   []float64{0.05, 0.1, 0.2, 0.3, 0.5, 1, 2},
		},
		[]string{"page", "rating"},
	)
}

func initErrorMetrics(bm *BusinessMetrics, namespace string) {
	bm.JSErrors = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "errors",
			Name:      "js_errors_total",
			Help:      "JavaScript errors by component",
		},
		[]string{"component", "error_type"},
	)

	bm.APIErrors = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "errors",
			Name:      "api_errors_total",
			Help:      "API errors experienced by users",
		},
		[]string{"endpoint", "status_code"},
	)

	bm.UserReportedIssues = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Subsystem: "errors",
			Name:      "user_reported_total",
			Help:      "User-reported issues",
		},
	)
}

// InitBusinessMetrics initializes the global business metrics instance.
//
// Deprecated: Use InitializeBusinessMetrics to set a custom namespace before
// first use. Initialization now happens lazily via GetBusinessMetrics().
func InitBusinessMetrics(namespace string) {
	InitializeBusinessMetrics(namespace)
}

// Helper functions for common metric updates

// RecordUserSession records a new user session
func RecordUserSession(userID string, duration time.Duration) {
	if GetBusinessMetrics() != nil {
		GetBusinessMetrics().UserSessions.WithLabelValues(userID).Inc()
		GetBusinessMetrics().SessionDuration.WithLabelValues(userID).Observe(duration.Seconds())
	}
}

// RecordFeatureUsage records feature usage
func RecordFeatureUsage(feature, action, userID string) {
	if GetBusinessMetrics() != nil {
		GetBusinessMetrics().FeatureUsage.WithLabelValues(feature, action, userID).Inc()
	}
}

// RecordJourneyStep records a journey step completion
func RecordJourneyStep(journeyType, step, userID string) {
	if GetBusinessMetrics() != nil {
		GetBusinessMetrics().JourneySteps.WithLabelValues(journeyType, step, userID).Inc()
	}
}

// RecordSearchQuery records a search query
func RecordSearchQuery(queryType string, resultCount int) {
	if GetBusinessMetrics() == nil {
		return
	}

	bucket := "0"
	switch {
	case resultCount > 0 && resultCount <= resultBucketMaxSmall:
		bucket = "1-10"
	case resultCount > resultBucketMaxSmall && resultCount <= resultBucketMaxMedium:
		bucket = "11-50"
	case resultCount > resultBucketMaxMedium:
		bucket = "51+"
	}

	GetBusinessMetrics().SearchQueries.WithLabelValues(queryType, bucket).Inc()

	if resultCount == 0 {
		GetBusinessMetrics().EmptySearchResults.WithLabelValues(queryType).Inc()
	}
}

// RecordWebVitals records web vitals metrics
func RecordWebVitals(page, metric, rating string, value float64) {
	if GetBusinessMetrics() == nil {
		return
	}

	switch metric {
	case "LCP":
		GetBusinessMetrics().WebVitalsLCP.WithLabelValues(page, rating).Observe(value)
	case "FID":
		GetBusinessMetrics().WebVitalsFID.WithLabelValues(page, rating).Observe(value)
	case "CLS":
		GetBusinessMetrics().WebVitalsCLS.WithLabelValues(page, rating).Observe(value)
	case "TTFB":
		GetBusinessMetrics().WebVitalsTTFB.WithLabelValues(page, rating).Observe(value)
	case "INP":
		GetBusinessMetrics().WebVitalsINP.WithLabelValues(page, rating).Observe(value)
	}
}
