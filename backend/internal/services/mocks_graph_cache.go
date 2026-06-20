package services

import (
	"context"
	"time"
)

// MockGraphAnalysisService for testing
type MockGraphAnalysisService struct {
	AnalyzeItemDependenciesFunc  func(ctx context.Context, itemID string) (*DependencyAnalysis, error)
	GetItemImpactAnalysisFunc    func(ctx context.Context, itemID string) (*ImpactAnalysis, error)
	VisualizeDependencyGraphFunc func(ctx context.Context, itemID string) (string, error)
}

// AnalyzeItemDependencies implements GraphAnalysisService.AnalyzeItemDependencies for testing.
func (m *MockGraphAnalysisService) AnalyzeItemDependencies(ctx context.Context, itemID string) (*DependencyAnalysis, error) {
	if m.AnalyzeItemDependenciesFunc != nil {
		return m.AnalyzeItemDependenciesFunc(ctx, itemID)
	}
	return nil, nil
}

// GetItemImpactAnalysis implements GraphAnalysisService.GetItemImpactAnalysis for testing.
func (m *MockGraphAnalysisService) GetItemImpactAnalysis(ctx context.Context, itemID string) (*ImpactAnalysis, error) {
	if m.GetItemImpactAnalysisFunc != nil {
		return m.GetItemImpactAnalysisFunc(ctx, itemID)
	}
	return nil, nil
}

// VisualizeDependencyGraph implements GraphAnalysisService.VisualizeDependencyGraph for testing.
func (m *MockGraphAnalysisService) VisualizeDependencyGraph(ctx context.Context, itemID string) (string, error) {
	if m.VisualizeDependencyGraphFunc != nil {
		return m.VisualizeDependencyGraphFunc(ctx, itemID)
	}
	return "", nil
}

// MockCacheService for testing
type MockCacheService struct {
	GetFunc               func(ctx context.Context, key string) (string, error)
	SetFunc               func(ctx context.Context, key string, value string, ttl time.Duration) error
	DeleteFunc            func(ctx context.Context, key string) error
	ExpireFunc            func(ctx context.Context, key string, ttl time.Duration) error
	InvalidatePatternFunc func(ctx context.Context, pattern string) error
	GetMultiFunc          func(ctx context.Context, keys []string) (map[string]string, error)
	SetMultiFunc          func(ctx context.Context, items map[string]string, ttl time.Duration) error
	ExistsFunc            func(ctx context.Context, key string) (bool, error)
}

// Get implements CacheService.Get for testing.
func (m *MockCacheService) Get(ctx context.Context, key string) (string, error) {
	if m.GetFunc != nil {
		return m.GetFunc(ctx, key)
	}
	return "", nil
}

// Set implements CacheService.Set for testing.
func (m *MockCacheService) Set(ctx context.Context, key string, value string, ttl time.Duration) error {
	if m.SetFunc != nil {
		return m.SetFunc(ctx, key, value, ttl)
	}
	return nil
}

// Delete implements CacheService.Delete for testing.
func (m *MockCacheService) Delete(ctx context.Context, key string) error {
	if m.DeleteFunc != nil {
		return m.DeleteFunc(ctx, key)
	}
	return nil
}

// Expire implements CacheService.Expire for testing.
func (m *MockCacheService) Expire(ctx context.Context, key string, ttl time.Duration) error {
	if m.ExpireFunc != nil {
		return m.ExpireFunc(ctx, key, ttl)
	}
	return nil
}

// InvalidatePattern implements CacheService.InvalidatePattern for testing.
func (m *MockCacheService) InvalidatePattern(ctx context.Context, pattern string) error {
	if m.InvalidatePatternFunc != nil {
		return m.InvalidatePatternFunc(ctx, pattern)
	}
	return nil
}

// GetMulti implements CacheService.GetMulti for testing.
func (m *MockCacheService) GetMulti(ctx context.Context, keys []string) (map[string]string, error) {
	if m.GetMultiFunc != nil {
		return m.GetMultiFunc(ctx, keys)
	}
	return nil, nil
}

// SetMulti implements CacheService.SetMulti for testing.
func (m *MockCacheService) SetMulti(ctx context.Context, items map[string]string, ttl time.Duration) error {
	if m.SetMultiFunc != nil {
		return m.SetMultiFunc(ctx, items, ttl)
	}
	return nil
}

// Exists implements CacheService.Exists for testing.
func (m *MockCacheService) Exists(ctx context.Context, key string) (bool, error) {
	if m.ExistsFunc != nil {
		return m.ExistsFunc(ctx, key)
	}
	return false, nil
}
