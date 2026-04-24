package traceability

import (
	"context"
	"testing"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/cache"
)

// setupItemsAndLinks is a helper to insert test items and links, then cleanup
func setupItemsAndLinks(ctx context.Context, t *testing.T, pool *pgxpool.Pool, projectID string, itemsSQL, linksSQL string) func() {
	t.Helper()
	_, err := pool.Exec(ctx, itemsSQL, projectID)
	require.NoError(t, err)

	if linksSQL != "" {
		_, err = pool.Exec(ctx, linksSQL)
		require.NoError(t, err)
	}

	return func() {
		_, err = pool.Exec(ctx, `DELETE FROM links WHERE source_id LIKE $1`, projectID+"%")
		require.NoError(t, err)
		_, err = pool.Exec(ctx, `DELETE FROM items WHERE project_id = $1`, projectID)
		require.NoError(t, err)
	}
}

// Mock cache for testing
type mockCache struct {
	data map[string]interface{}
}

func newMockCache() *mockCache {
	return &mockCache{
		data: make(map[string]interface{}),
	}
}

func (m *mockCache) Get(_ context.Context, _ string, _ interface{}) error {
	// Always return error to force computation
	return ErrCacheMiss
}

func (m *mockCache) Set(_ context.Context, key string, value interface{}) error {
	m.data[key] = value
	return nil
}

func (m *mockCache) Delete(_ context.Context, keys ...string) error {
	for _, key := range keys {
		delete(m.data, key)
	}
	return nil
}

func (m *mockCache) InvalidatePattern(_ context.Context, _ string) error {
	return nil
}

func (m *mockCache) Close() error {
	return nil
}

var _ cache.Cache = (*mockCache)(nil)

// ErrCacheMiss represents a cache miss error
var ErrCacheMiss = assert.AnError

// setupTestDB creates a test database pool
func setupTestDB(t *testing.T) *pgxpool.Pool {
	// This would connect to a test database
	// For now, we'll skip if no test DB is available
	t.Skip("Integration test requires database connection")
	return nil
}

func TestNewMatrixService(t *testing.T) {
	pool := setupTestDB(t)
	if pool != nil {
		defer pool.Close()
	}

	mockCache := newMockCache()
	service := NewMatrixService(pool, mockCache)

	assert.NotNil(t, service)
	assert.Equal(t, pool, service.db)
	assert.Equal(t, mockCache, service.cache)
}

func TestGenerateMatrix(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	pool := setupTestDB(t)
	if pool == nil {
		return
	}
	defer pool.Close()

	// Setup test data
	ctx := context.Background()
	projectID := "test-project-1"

	// Create test items
	_, err := pool.Exec(ctx, `
		INSERT INTO items (id, project_id, title, type, status, metadata, created_at, updated_at)
		VALUES
			('req-1', $1, 'User Authentication', 'requirement', 'active', '{}', NOW(), NOW()),
			('req-2', $1, 'Data Validation', 'requirement', 'active', '{}', NOW(), NOW()),
			('test-1', $1, 'Auth Test Suite', 'test_suite', 'active', '{}', NOW(), NOW()),
			('test-2', $1, 'Validation Tests', 'test_case', 'active', '{}', NOW(), NOW())
		ON CONFLICT (id) DO NOTHING
	`, projectID)
	require.NoError(t, err)

	// Create links
	_, err = pool.Exec(ctx, `
		INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at)
		VALUES
			('link-1', 'req-1', 'test-1', 'TRACES_TO', '{}', NOW(), NOW()),
			('link-2', 'req-2', 'test-2', 'VALIDATES', '{}', NOW(), NOW())
		ON CONFLICT (id) DO NOTHING
	`)
	require.NoError(t, err)

	mockCache := newMockCache()
	service := NewMatrixService(pool, mockCache)

	// Test matrix generation
	matrix, err := service.GenerateMatrix(ctx, projectID)
	require.NoError(t, err)
	require.NotNil(t, matrix)

	assert.Equal(t, projectID, matrix.ProjectID)
	assert.NotZero(t, matrix.GeneratedAt)
	assert.GreaterOrEqual(t, len(matrix.Requirements), 2)
	assert.GreaterOrEqual(t, len(matrix.TestCases), 2)
	assert.GreaterOrEqual(t, len(matrix.Links), 2)
	assert.NotNil(t, matrix.Coverage)
	assert.Greater(t, matrix.Coverage.CoveragePercent, 0.0)

	// Cleanup
	_, err = pool.Exec(ctx, `DELETE FROM links WHERE source_id LIKE 'req-%' OR target_id LIKE 'test-%'`)
	require.NoError(t, err)
	_, err = pool.Exec(ctx, `DELETE FROM items WHERE project_id = $1`, projectID)
	require.NoError(t, err)
}

func TestGetCoverageReport(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	pool := setupTestDB(t)
	if pool == nil {
		return
	}
	defer pool.Close()

	ctx := context.Background()
	projectID := "test-project-coverage"

	// Setup test data with varied coverage
	_, err := pool.Exec(ctx, `
		INSERT INTO items (id, project_id, title, type, status, metadata, created_at, updated_at)
		VALUES
			('req-c1', $1, 'Covered Requirement', 'requirement', 'active', '{}', NOW(), NOW()),
			('req-c2', $1, 'Uncovered Requirement', 'requirement', 'active', '{}', NOW(), NOW()),
			('feat-c1', $1, 'Covered Feature', 'feature', 'active', '{}', NOW(), NOW()),
			('test-c1', $1, 'Test for Req', 'test_case', 'active', '{}', NOW(), NOW())
		ON CONFLICT (id) DO NOTHING
	`, projectID)
	require.NoError(t, err)

	// Link only some items
	_, err = pool.Exec(ctx, `
		INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at)
		VALUES
			('link-c1', 'req-c1', 'test-c1', 'TRACES_TO', '{}', NOW(), NOW()),
			('link-c2', 'feat-c1', 'test-c1', 'VALIDATES', '{}', NOW(), NOW())
		ON CONFLICT (id) DO NOTHING
	`)
	require.NoError(t, err)

	mockCache := newMockCache()
	service := NewMatrixService(pool, mockCache)

	// Test coverage report
	report, err := service.GetCoverageReport(ctx, projectID)
	require.NoError(t, err)
	require.NotNil(t, report)

	assert.Equal(t, projectID, report.ProjectID)
	assert.NotNil(t, report.Overall)
	assert.Positive(t, report.Overall.TotalRequirements)
	assert.LessOrEqual(t, report.Overall.TracedRequirements, report.Overall.TotalRequirements)
	assert.NotNil(t, report.ByType)
	assert.NotEmpty(t, report.Recommendations)

	// Cleanup
	_, err = pool.Exec(ctx, `DELETE FROM links WHERE source_id LIKE 'req-c%' OR source_id LIKE 'feat-c%'`)
	require.NoError(t, err)
	_, err = pool.Exec(ctx, `DELETE FROM items WHERE project_id = $1`, projectID)
	require.NoError(t, err)
}

func TestGetGapAnalysis(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	pool := setupTestDB(t)
	if pool == nil {
		return
	}
	defer pool.Close()

	ctx := context.Background()
	projectID := "test-project-gaps"

	// Setup test data with gaps
	_, err := pool.Exec(ctx, `
		INSERT INTO items (id, project_id, title, type, status, metadata, created_at, updated_at)
		VALUES
			('req-g1', $1, 'Requirement Without Test', 'requirement', 'active', '{}', NOW(), NOW()),
			('test-g1', $1, 'Test Without Requirement', 'test_case', 'active', '{}', NOW(), NOW()),
			('orphan-g1', $1, 'Orphaned Item', 'feature', 'active', '{}', NOW(), NOW())
		ON CONFLICT (id) DO NOTHING
	`, projectID)
	require.NoError(t, err)

	mockCache := newMockCache()
	service := NewMatrixService(pool, mockCache)

	// Test gap analysis
	analysis, err := service.GetGapAnalysis(ctx, projectID)
	require.NoError(t, err)
	require.NotNil(t, analysis)

	assert.Equal(t, projectID, analysis.ProjectID)
	assert.GreaterOrEqual(t, len(analysis.MissingForward), 1)  // req-g1
	assert.GreaterOrEqual(t, len(analysis.MissingBackward), 1) // test-g1
	assert.GreaterOrEqual(t, len(analysis.Orphaned), 3)        // All items are orphaned
	assert.NotEmpty(t, analysis.Recommendations)

	// Cleanup
	_, err = pool.Exec(ctx, `DELETE FROM items WHERE project_id = $1`, projectID)
	require.NoError(t, err)
}

func TestGetItemTraceability(t *testing.T) {
	withMatrixService(t, func(ctx context.Context, pool *pgxpool.Pool, service *MatrixService) {
		projectID := "test-project-item-trace"
		itemID := "req-it1"

		cleanup := setupItemsAndLinks(ctx, t, pool, projectID, `
			INSERT INTO items (id, project_id, title, type, status, metadata, created_at, updated_at)
			VALUES
				('req-it1', $1, 'Main Requirement', 'requirement', 'active', '{}', NOW(), NOW()),
				('test-it1', $1, 'Test 1', 'test_case', 'active', '{}', NOW(), NOW()),
				('test-it2', $1, 'Test 2', 'test_case', 'active', '{}', NOW(), NOW())
			ON CONFLICT (id) DO NOTHING
		`, `
			INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at)
			VALUES
				('link-it1', 'req-it1', 'test-it1', 'TRACES_TO', '{}', NOW(), NOW()),
				('link-it2', 'req-it1', 'test-it2', 'VALIDATES', '{}', NOW(), NOW())
			ON CONFLICT (id) DO NOTHING
		`)
		defer cleanup()

		traceability, err := service.GetItemTraceability(ctx, itemID)
		require.NoError(t, err)
		require.NotNil(t, traceability)

		assert.Equal(t, itemID, traceability.ItemID)
		assert.GreaterOrEqual(t, len(traceability.DownstreamLinks), 2)
		assert.NotEmpty(t, traceability.CoverageStatus)
	})
}

func TestValidateCompleteness(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	pool := setupTestDB(t)
	if pool == nil {
		return
	}
	defer pool.Close()

	ctx := context.Background()
	projectID := "test-project-validation"

	// Setup test data with validation issues
	_, err := pool.Exec(ctx, `
		INSERT INTO items (id, project_id, title, type, status, metadata, created_at, updated_at)
		VALUES
			('req-v1', $1, 'Valid Requirement', 'requirement', 'active', '{}', NOW(), NOW()),
			('req-v2', $1, 'Invalid Requirement', 'requirement', 'active', '{}', NOW(), NOW()),
			('test-v1', $1, 'Valid Test', 'test_case', 'active', '{}', NOW(), NOW())
		ON CONFLICT (id) DO NOTHING
	`, projectID)
	require.NoError(t, err)

	// Link only one requirement
	_, err = pool.Exec(ctx, `
		INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at)
		VALUES
			('link-v1', 'req-v1', 'test-v1', 'TRACES_TO', '{}', NOW(), NOW())
		ON CONFLICT (id) DO NOTHING
	`)
	require.NoError(t, err)

	mockCache := newMockCache()
	service := NewMatrixService(pool, mockCache)

	// Test validation
	report, err := service.ValidateCompleteness(ctx, projectID)
	require.NoError(t, err)
	require.NotNil(t, report)

	assert.Equal(t, projectID, report.ProjectID)
	assert.False(t, report.IsComplete)
	assert.Positive(t, report.Failed)
	assert.NotEmpty(t, report.Issues)
	assert.Less(t, report.Score, 100.0)

	// Cleanup
	_, err = pool.Exec(ctx, `DELETE FROM links WHERE source_id LIKE 'req-v%'`)
	require.NoError(t, err)
	_, err = pool.Exec(ctx, `DELETE FROM items WHERE project_id = $1`, projectID)
	require.NoError(t, err)
}

func TestGetChangeImpact(t *testing.T) {
	withMatrixService(t, func(ctx context.Context, pool *pgxpool.Pool, service *MatrixService) {
		projectID := "test-project-impact"
		itemID := "req-imp1"

		cleanup := setupItemsAndLinks(ctx, t, pool, projectID, `
			INSERT INTO items (id, project_id, title, type, status, metadata, created_at, updated_at)
			VALUES
				('req-imp1', $1, 'Main Requirement', 'requirement', 'active', '{}', NOW(), NOW()),
				('feat-imp1', $1, 'Direct Feature', 'feature', 'active', '{}', NOW(), NOW()),
				('test-imp1', $1, 'Direct Test', 'test_case', 'active', '{}', NOW(), NOW()),
				('test-imp2', $1, 'Indirect Test', 'test_case', 'active', '{}', NOW(), NOW())
			ON CONFLICT (id) DO NOTHING
		`, `
			INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at)
			VALUES
				('link-imp1', 'req-imp1', 'feat-imp1', 'IMPLEMENTS', '{}', NOW(), NOW()),
				('link-imp2', 'req-imp1', 'test-imp1', 'TRACES_TO', '{}', NOW(), NOW()),
				('link-imp3', 'feat-imp1', 'test-imp2', 'VALIDATES', '{}', NOW(), NOW())
			ON CONFLICT (id) DO NOTHING
		`)
		defer cleanup()

		impact, err := service.GetChangeImpact(ctx, itemID)
		require.NoError(t, err)
		require.NotNil(t, impact)

		assert.Equal(t, itemID, impact.ItemID)
		assert.GreaterOrEqual(t, len(impact.DirectImpact), 2)
		assert.NotEmpty(t, impact.TestsToRun)
	})
}

func withMatrixService(
	t *testing.T,
	run func(ctx context.Context, pool *pgxpool.Pool, service *MatrixService),
) {
	t.Helper()

	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	pool := setupTestDB(t)
	if pool == nil {
		return
	}
	defer pool.Close()

	ctx := context.Background()
	service := NewMatrixService(pool, newMockCache())
	run(ctx, pool, service)
}

func TestDetermineCoverageStatus(t *testing.T) {
	service := &MatrixService{}

	tests := []struct {
		name       string
		upstream   []Link
		downstream []Link
		expected   string
	}{
		{
			name:       "No links",
			upstream:   []Link{},
			downstream: []Link{},
			expected:   "none",
		},
		{
			name: "Partial coverage",
			upstream: []Link{
				{SourceID: "a", TargetID: "b"},
			},
			downstream: []Link{},
			expected:   "partial",
		},
		{
			name: "Full coverage",
			upstream: []Link{
				{SourceID: "a", TargetID: "b"},
			},
			downstream: []Link{
				{SourceID: "c", TargetID: "d"},
			},
			expected: "full",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := service.determineCoverageStatus(tt.upstream, tt.downstream)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestGenerateCoverageRecommendations(t *testing.T) {
	service := &MatrixService{}

	tests := []struct {
		name          string
		coverage      float64
		untracedCount int
		wantContains  string
	}{
		{
			name:          "Critical coverage",
			coverage:      40.0,
			untracedCount: 10,
			wantContains:  "critically low",
		},
		{
			name:          "Below target",
			coverage:      70.0,
			untracedCount: 5,
			wantContains:  "below target",
		},
		{
			name:          "Good coverage",
			coverage:      95.0,
			untracedCount: 0,
			wantContains:  "good",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			report := &CoverageReport{
				Overall: &CoverageMetrics{
					CoveragePercent: tt.coverage,
				},
				ByType: make(map[string]*CoverageMetrics),
			}

			untraced := make([]string, tt.untracedCount)
			for i := 0; i < tt.untracedCount; i++ {
				untraced[i] = "item-" + string(rune(i))
			}

			recommendations := service.generateCoverageRecommendations(report, untraced)
			assert.NotEmpty(t, recommendations)

			found := false
			for _, rec := range recommendations {
				if contains(rec, tt.wantContains) {
					found = true
					break
				}
			}
			assert.True(t, found, "Expected to find '%s' in recommendations", tt.wantContains)
		})
	}
}

func TestGenerateGapRecommendations(t *testing.T) {
	service := &MatrixService{}

	tests := []struct {
		name         string
		forwardGaps  int
		backwardGaps int
		orphaned     int
		wantContains string
	}{
		{
			name:         "Requirements without tests",
			forwardGaps:  5,
			backwardGaps: 0,
			orphaned:     0,
			wantContains: "requirements lack test coverage",
		},
		{
			name:         "Tests without requirements",
			forwardGaps:  0,
			backwardGaps: 3,
			orphaned:     0,
			wantContains: "tests are not linked",
		},
		{
			name:         "Orphaned items",
			forwardGaps:  0,
			backwardGaps: 0,
			orphaned:     7,
			wantContains: "orphaned",
		},
		{
			name:         "No gaps",
			forwardGaps:  0,
			backwardGaps: 0,
			orphaned:     0,
			wantContains: "No traceability gaps",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			analysis := &GapAnalysis{
				MissingForward:  make([]Gap, tt.forwardGaps),
				MissingBackward: make([]Gap, tt.backwardGaps),
				Orphaned:        make([]string, tt.orphaned),
			}

			recommendations := service.generateGapRecommendations(analysis)
			assert.NotEmpty(t, recommendations)

			found := false
			for _, rec := range recommendations {
				if contains(rec, tt.wantContains) {
					found = true
					break
				}
			}
			assert.True(t, found, "Expected to find '%s' in recommendations", tt.wantContains)
		})
	}
}

// Helper function
func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > 0 && (s[:len(substr)] == substr || contains(s[1:], substr)))
}
