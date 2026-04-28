package cache

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

func TestMetrics_HitRate(t *testing.T) {
	metrics := &Metrics{
		Hits:          70,
		Misses:        30,
		TotalRequests: 100,
	}

	hitRate := metrics.HitRate()
	assert.InEpsilon(t, 0.7, hitRate, 1e-9)
}

func TestMetrics_MissRate(t *testing.T) {
	metrics := &Metrics{
		Hits:          70,
		Misses:        30,
		TotalRequests: 100,
	}

	missRate := metrics.MissRate()
	assert.InDelta(t, 0.3, missRate, 0.0001)
}

func TestMetrics_ErrorRate(t *testing.T) {
	metrics := &Metrics{
		Errors:        5,
		TotalRequests: 100,
	}

	errorRate := metrics.ErrorRate()
	assert.InEpsilon(t, 0.05, errorRate, 1e-9)
}

func TestMetrics_ZeroRequests(t *testing.T) {
	metrics := &Metrics{}

	assert.InDelta(t, 0.0, metrics.HitRate(), 1e-9)
	assert.InEpsilon(t, 1.0, metrics.MissRate(), 1e-9)
	assert.InDelta(t, 0.0, metrics.ErrorRate(), 1e-9)
}

func TestMetricsCache_Get_Hit(t *testing.T) {
	mockCache := new(MockCache)
	mc := NewMetricsCache(mockCache)

	mockCache.On("Get", mock.Anything, "test-key", mock.Anything).Return(nil)

	err := mc.Get(context.Background(), "test-key", &struct{}{})

	require.NoError(t, err)
	assert.Equal(t, int64(1), mc.metrics.Hits)
	assert.Equal(t, int64(0), mc.metrics.Misses)
	assert.Equal(t, int64(1), mc.metrics.TotalRequests)
	mockCache.AssertExpectations(t)
}

func TestMetricsCache_Get_Miss(t *testing.T) {
	mockCache := new(MockCache)
	mc := NewMetricsCache(mockCache)

	mockCache.On("Get", mock.Anything, "test-key", mock.Anything).Return(assert.AnError)

	err := mc.Get(context.Background(), "test-key", &struct{}{})

	require.Error(t, err)
	assert.Equal(t, int64(0), mc.metrics.Hits)
	assert.Equal(t, int64(1), mc.metrics.Misses)
	assert.Equal(t, int64(1), mc.metrics.TotalRequests)
	mockCache.AssertExpectations(t)
}

func TestMetricsCache_Set(t *testing.T) {
	mockCache := new(MockCache)
	mc := NewMetricsCache(mockCache)

	mockCache.On("Set", mock.Anything, "test-key", mock.Anything).Return(nil)

	err := mc.Set(context.Background(), "test-key", "test-value")

	require.NoError(t, err)
	assert.Equal(t, int64(1), mc.metrics.Sets)
	assert.Equal(t, int64(1), mc.metrics.KeyCount)
	mockCache.AssertExpectations(t)
}

func TestMetricsCache_Delete(t *testing.T) {
	mockCache := new(MockCache)
	mc := NewMetricsCache(mockCache)

	// Set initial key count
	mc.metrics.KeyCount = 5

	keys := []string{"key1", "key2"}
	mockCache.On("Delete", mock.Anything, keys).Return(nil)

	err := mc.Delete(context.Background(), keys...)

	require.NoError(t, err)
	assert.Equal(t, int64(2), mc.metrics.Deletes)
	assert.Equal(t, int64(3), mc.metrics.KeyCount) // 5 - 2 = 3
	mockCache.AssertExpectations(t)
}

func TestMetricsCache_ResetMetrics(t *testing.T) {
	mc := NewMetricsCache(new(MockCache))

	// Set some metrics
	mc.metrics.Hits = 100
	mc.metrics.Misses = 50
	mc.metrics.TotalRequests = 150

	// Reset
	mc.ResetMetrics()

	// Verify all zeroed
	assert.Equal(t, int64(0), mc.metrics.Hits)
	assert.Equal(t, int64(0), mc.metrics.Misses)
	assert.Equal(t, int64(0), mc.metrics.TotalRequests)
}

func TestMetricsCollector_Register(t *testing.T) {
	collector := NewMetricsCollector()

	sm := collector.Register("test-service")

	assert.NotNil(t, sm)
	assert.Equal(t, "test-service", sm.ServiceName)
	assert.NotNil(t, sm.Metrics)
}

func TestMetricsCollector_GetServiceMetrics(t *testing.T) {
	collector := NewMetricsCollector()

	collector.Register("service1")
	collector.Register("service2")

	sm := collector.GetServiceMetrics("service1")
	assert.NotNil(t, sm)
	assert.Equal(t, "service1", sm.ServiceName)

	sm2 := collector.GetServiceMetrics("non-existent")
	assert.Nil(t, sm2)
}

func TestMetricsCollector_GetAllMetrics(t *testing.T) {
	collector := NewMetricsCollector()

	sm1 := collector.Register("service1")
	sm1.Metrics.Hits = 100

	sm2 := collector.Register("service2")
	sm2.Metrics.Hits = 200

	allMetrics := collector.GetAllMetrics()

	assert.Len(t, allMetrics, 2)
	assert.Contains(t, allMetrics, "service1")
	assert.Contains(t, allMetrics, "service2")
}

func TestMetricsCollector_AggregatedMetrics(t *testing.T) {
	collector := NewMetricsCollector()

	sm1 := collector.Register("service1")
	sm1.Metrics.Hits = 70
	sm1.Metrics.Misses = 30
	sm1.Metrics.TotalRequests = 100

	sm2 := collector.Register("service2")
	sm2.Metrics.Hits = 80
	sm2.Metrics.Misses = 20
	sm2.Metrics.TotalRequests = 100

	agg := collector.AggregatedMetrics()

	assert.Equal(t, int64(150), agg["total_hits"])
	assert.Equal(t, int64(50), agg["total_misses"])
	assert.Equal(t, int64(200), agg["total_requests"])
	assert.InEpsilon(t, 0.75, agg["overall_hit_rate"], 1e-9) // 150/200 = 0.75
	assert.Equal(t, 2, agg["service_count"])
}

func TestMetrics_ToMap(t *testing.T) {
	metrics := &Metrics{
		Hits:          70,
		Misses:        30,
		TotalRequests: 100,
	}

	m := metrics.ToMap()

	assert.Equal(t, int64(70), m["hits"])
	assert.Equal(t, int64(30), m["misses"])
	assert.Equal(t, int64(100), m["total_requests"])
	assert.InDelta(t, 0.7, m["hit_rate"], 0.0001)
	assert.InDelta(t, 0.3, m["miss_rate"], 0.0001)
}
