package traceability

import (
	"context"
	"log/slog"
)

func (s *MatrixService) getCachedOrCompute(
	ctx context.Context,
	cacheKey string,
	computeFn func() (*Matrix, error),
) (*Matrix, error) {
	// Try cache first
	var cached Matrix
	err := s.cache.Get(ctx, cacheKey, &cached)
	if err == nil {
		return &cached, nil
	}

	// Compute
	result, err := computeFn()
	if err != nil {
		return nil, err
	}

	// Cache for 10 minutes
	if err := s.cache.Set(ctx, cacheKey, result); err != nil {
		slog.Error("Failed to cache result for key", "error", cacheKey, "error", err)
	}

	return result, nil
}

func (s *MatrixService) getCachedOrComputeCoverage(
	ctx context.Context,
	cacheKey string,
	computeFn func() (*CoverageReport, error),
) (*CoverageReport, error) {
	// Try cache first
	var cached CoverageReport
	err := s.cache.Get(ctx, cacheKey, &cached)
	if err == nil {
		return &cached, nil
	}

	// Compute
	result, err := computeFn()
	if err != nil {
		return nil, err
	}

	// Cache for 10 minutes
	if err := s.cache.Set(ctx, cacheKey, result); err != nil {
		slog.Error("Failed to cache result for key", "error", cacheKey, "error", err)
	}

	return result, nil
}

func (s *MatrixService) getCachedOrComputeGaps(
	ctx context.Context,
	cacheKey string,
	computeFn func() (*GapAnalysis, error),
) (*GapAnalysis, error) {
	// Try cache first
	var cached GapAnalysis
	err := s.cache.Get(ctx, cacheKey, &cached)
	if err == nil {
		return &cached, nil
	}

	// Compute
	result, err := computeFn()
	if err != nil {
		return nil, err
	}

	// Cache for 10 minutes
	if err := s.cache.Set(ctx, cacheKey, result); err != nil {
		slog.Error("Failed to cache result for key", "error", cacheKey, "error", err)
	}

	return result, nil
}

func (s *MatrixService) getCachedOrComputeValidation(
	ctx context.Context,
	cacheKey string,
	computeFn func() (*ValidationReport, error),
) (*ValidationReport, error) {
	// Try cache first
	var cached ValidationReport
	err := s.cache.Get(ctx, cacheKey, &cached)
	if err == nil {
		return &cached, nil
	}

	// Compute
	result, err := computeFn()
	if err != nil {
		return nil, err
	}

	// Cache for 10 minutes
	if err := s.cache.Set(ctx, cacheKey, result); err != nil {
		slog.Error("Failed to cache result for key", "error", cacheKey, "error", err)
	}

	return result, nil
}
