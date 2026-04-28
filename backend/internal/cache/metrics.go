package cache

import (
	"context"
	"sync/atomic"
	"time"
)

const nanosPerMillisecond = 1_000_000

// Metrics tracks cache performance metrics
type Metrics struct {
	Hits          int64
	Misses        int64
	Errors        int64
	Sets          int64
	Deletes       int64
	TotalRequests int64

	// Latency tracking (in nanoseconds)
	GetLatencyTotal    int64
	SetLatencyTotal    int64
	DeleteLatencyTotal int64

	// Size metrics
	KeyCount     int64
	BytesWritten int64
	BytesRead    int64
}

// GetMetrics returns a normalized map view used by tests.
func (m *Metrics) GetMetrics() map[string]interface{} {
	data := m.ToMap()
	data["total_operations"] = data["total_requests"]
	data["total_hits"] = data["hits"]
	data["total_misses"] = data["misses"]
	return data
}

// HitRate returns the cache hit rate (0.0 to 1.0)
func (m *Metrics) HitRate() float64 {
	total := atomic.LoadInt64(&m.TotalRequests)
	if total == 0 {
		return 0
	}
	hits := atomic.LoadInt64(&m.Hits)
	return float64(hits) / float64(total)
}

// MissRate returns the cache miss rate (0.0 to 1.0)
func (m *Metrics) MissRate() float64 {
	return 1.0 - m.HitRate()
}

// ErrorRate returns the cache error rate (0.0 to 1.0)
func (m *Metrics) ErrorRate() float64 {
	total := atomic.LoadInt64(&m.TotalRequests)
	if total == 0 {
		return 0
	}
	errors := atomic.LoadInt64(&m.Errors)
	return float64(errors) / float64(total)
}

// AvgGetLatency returns the average GET latency in milliseconds
func (m *Metrics) AvgGetLatency() float64 {
	requests := atomic.LoadInt64(&m.Hits) + atomic.LoadInt64(&m.Misses)
	if requests == 0 {
		return 0
	}
	totalNanos := atomic.LoadInt64(&m.GetLatencyTotal)
	return float64(totalNanos) / float64(requests) / nanosPerMillisecond // Convert to ms
}

// AvgSetLatency returns the average SET latency in milliseconds
func (m *Metrics) AvgSetLatency() float64 {
	sets := atomic.LoadInt64(&m.Sets)
	if sets == 0 {
		return 0
	}
	totalNanos := atomic.LoadInt64(&m.SetLatencyTotal)
	return float64(totalNanos) / float64(sets) / nanosPerMillisecond // Convert to ms
}

// AvgDeleteLatency returns the average DELETE latency in milliseconds
func (m *Metrics) AvgDeleteLatency() float64 {
	deletes := atomic.LoadInt64(&m.Deletes)
	if deletes == 0 {
		return 0
	}
	totalNanos := atomic.LoadInt64(&m.DeleteLatencyTotal)
	return float64(totalNanos) / float64(deletes) / nanosPerMillisecond // Convert to ms
}

// ToMap converts metrics to a map for JSON serialization
func (metrics *Metrics) ToMap() map[string]interface{} {
	return map[string]interface{}{
		"hits":               atomic.LoadInt64(&metrics.Hits),
		"misses":             atomic.LoadInt64(&metrics.Misses),
		"errors":             atomic.LoadInt64(&metrics.Errors),
		"sets":               atomic.LoadInt64(&metrics.Sets),
		"deletes":            atomic.LoadInt64(&metrics.Deletes),
		"total_requests":     atomic.LoadInt64(&metrics.TotalRequests),
		"hit_rate":           metrics.HitRate(),
		"miss_rate":          metrics.MissRate(),
		"error_rate":         metrics.ErrorRate(),
		"avg_get_latency_ms": metrics.AvgGetLatency(),
		"avg_set_latency_ms": metrics.AvgSetLatency(),
		"avg_del_latency_ms": metrics.AvgDeleteLatency(),
		"key_count":          atomic.LoadInt64(&metrics.KeyCount),
		"bytes_written":      atomic.LoadInt64(&metrics.BytesWritten),
		"bytes_read":         atomic.LoadInt64(&metrics.BytesRead),
	}
}

// Reset resets all metrics
func (metrics *Metrics) Reset() {
	atomic.StoreInt64(&metrics.Hits, 0)
	atomic.StoreInt64(&metrics.Misses, 0)
	atomic.StoreInt64(&metrics.Errors, 0)
	atomic.StoreInt64(&metrics.Sets, 0)
	atomic.StoreInt64(&metrics.Deletes, 0)
	atomic.StoreInt64(&metrics.TotalRequests, 0)
	atomic.StoreInt64(&metrics.GetLatencyTotal, 0)
	atomic.StoreInt64(&metrics.SetLatencyTotal, 0)
	atomic.StoreInt64(&metrics.DeleteLatencyTotal, 0)
	atomic.StoreInt64(&metrics.KeyCount, 0)
	atomic.StoreInt64(&metrics.BytesWritten, 0)
	atomic.StoreInt64(&metrics.BytesRead, 0)
}

// MetricsCache wraps Cache with metrics tracking
type MetricsCache struct {
	cache   Cache
	metrics *Metrics
}

// NewMetricsCache creates a cache with metrics tracking
func NewMetricsCache(cache Cache) *MetricsCache {
	return &MetricsCache{
		cache:   cache,
		metrics: &Metrics{},
	}
}

// Get retrieves a value from cache with metrics tracking
func (mc *MetricsCache) Get(ctx context.Context, key string, dest interface{}) error {
	start := time.Now()
	atomic.AddInt64(&mc.metrics.TotalRequests, 1)

	err := mc.cache.Get(ctx, key, dest)
	duration := time.Since(start).Nanoseconds()
	atomic.AddInt64(&mc.metrics.GetLatencyTotal, duration)

	if err == nil {
		atomic.AddInt64(&mc.metrics.Hits, 1)
	} else {
		atomic.AddInt64(&mc.metrics.Misses, 1)
	}

	return err
}

// Set stores a value in cache with metrics tracking
func (mc *MetricsCache) Set(ctx context.Context, key string, value interface{}) error {
	start := time.Now()
	atomic.AddInt64(&mc.metrics.Sets, 1)
	atomic.AddInt64(&mc.metrics.KeyCount, 1)

	err := mc.cache.Set(ctx, key, value)
	duration := time.Since(start).Nanoseconds()
	atomic.AddInt64(&mc.metrics.SetLatencyTotal, duration)

	if err != nil {
		atomic.AddInt64(&mc.metrics.Errors, 1)
	}

	return err
}

// Delete removes values from cache with metrics tracking
func (mc *MetricsCache) Delete(ctx context.Context, keys ...string) error {
	start := time.Now()
	atomic.AddInt64(&mc.metrics.Deletes, int64(len(keys)))
	atomic.AddInt64(&mc.metrics.KeyCount, -int64(len(keys)))

	err := mc.cache.Delete(ctx, keys...)
	duration := time.Since(start).Nanoseconds()
	atomic.AddInt64(&mc.metrics.DeleteLatencyTotal, duration)

	if err != nil {
		atomic.AddInt64(&mc.metrics.Errors, 1)
	}

	return err
}

// InvalidatePattern invalidates all keys matching a pattern with metrics tracking
func (mc *MetricsCache) InvalidatePattern(ctx context.Context, pattern string) error {
	start := time.Now()

	err := mc.cache.InvalidatePattern(ctx, pattern)
	duration := time.Since(start).Nanoseconds()
	atomic.AddInt64(&mc.metrics.DeleteLatencyTotal, duration)

	if err != nil {
		atomic.AddInt64(&mc.metrics.Errors, 1)
	}

	return err
}

// Close closes the underlying cache
func (mc *MetricsCache) Close() error {
	return mc.cache.Close()
}

// GetMetrics returns the current metrics
func (mc *MetricsCache) GetMetrics() *Metrics {
	return mc.metrics
}

// ResetMetrics resets all metrics
func (mc *MetricsCache) ResetMetrics() {
	mc.metrics.Reset()
}

// ServiceMetrics tracks metrics for a specific service
type ServiceMetrics struct {
	ServiceName string
	Metrics     *Metrics
}

// NewServiceMetrics creates metrics for a service
func NewServiceMetrics(serviceName string) *ServiceMetrics {
	return &ServiceMetrics{
		ServiceName: serviceName,
		Metrics:     &Metrics{},
	}
}

// ToMap converts service metrics to a map
func (sm *ServiceMetrics) ToMap() map[string]interface{} {
	return map[string]interface{}{
		"service": sm.ServiceName,
		"metrics": sm.Metrics.ToMap(),
	}
}

// MetricsCollector aggregates metrics from multiple services
type MetricsCollector struct {
	services map[string]*ServiceMetrics
}

// NewMetricsCollector creates a new metrics collector
func NewMetricsCollector() *MetricsCollector {
	return &MetricsCollector{
		services: make(map[string]*ServiceMetrics),
	}
}

// Register registers a service for metrics collection
func (mc *MetricsCollector) Register(serviceName string) *ServiceMetrics {
	sm := NewServiceMetrics(serviceName)
	mc.services[serviceName] = sm
	return sm
}

// GetServiceMetrics returns metrics for a specific service
func (mc *MetricsCollector) GetServiceMetrics(serviceName string) *ServiceMetrics {
	return mc.services[serviceName]
}

// GetAllMetrics returns metrics for all services
func (mc *MetricsCollector) GetAllMetrics() map[string]interface{} {
	result := make(map[string]interface{})
	for name, sm := range mc.services {
		result[name] = sm.Metrics.ToMap()
	}
	return result
}

// AggregatedMetrics returns aggregated metrics across all services
func (mc *MetricsCollector) AggregatedMetrics() map[string]interface{} {
	var totalHits, totalMisses, totalErrors, totalRequests int64
	var totalGetLatency, totalSetLatency, totalDeleteLatency int64

	for _, sm := range mc.services {
		totalHits += atomic.LoadInt64(&sm.Metrics.Hits)
		totalMisses += atomic.LoadInt64(&sm.Metrics.Misses)
		totalErrors += atomic.LoadInt64(&sm.Metrics.Errors)
		totalRequests += atomic.LoadInt64(&sm.Metrics.TotalRequests)
		totalGetLatency += atomic.LoadInt64(&sm.Metrics.GetLatencyTotal)
		totalSetLatency += atomic.LoadInt64(&sm.Metrics.SetLatencyTotal)
		totalDeleteLatency += atomic.LoadInt64(&sm.Metrics.DeleteLatencyTotal)
	}

	hitRate := 0.0
	if totalRequests > 0 {
		hitRate = float64(totalHits) / float64(totalRequests)
	}

	avgGetLatency := 0.0
	if totalRequests > 0 {
		avgGetLatency = float64(totalGetLatency) / float64(totalRequests) / nanosPerMillisecond
	}

	return map[string]interface{}{
		"total_hits":         totalHits,
		"total_misses":       totalMisses,
		"total_errors":       totalErrors,
		"total_requests":     totalRequests,
		"overall_hit_rate":   hitRate,
		"avg_get_latency_ms": avgGetLatency,
		"service_count":      len(mc.services),
	}
}
