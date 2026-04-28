package equivalence

import (
	"context"
	"errors"
	"fmt"
	"sort"
	"sync"
	"time"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/embeddings"
)

// Engine orchestrates all equivalence detection strategies and returns aggregated results
type Engine struct {
	strategies map[StrategyType]Strategy
	detector   *Detector
	scorer     *ConfidenceScorer
	resolver   *Resolver
	reconciler *ConflictReconciler

	// Configuration
	config EngineConfig

	// Metrics
	metrics *EngineMetrics
	mu      sync.RWMutex
}

// EngineConfig contains engine configuration
type EngineConfig struct {
	// Execution
	ParallelizeStrategies bool
	StrategyTimeout       time.Duration
	MaxResults            int

	// Confidence
	MinConfidenceThreshold float64
	RequireAgreement       bool // Require 2+ strategies
	AutoConfirmThreshold   float64

	// Conflict handling
	ResolveConflicts      bool
	PreferHighestStrategy bool

	// Caching
	EnableCache bool
	CacheTTL    time.Duration
}

const (
	defaultStrategyTimeout = 30 * time.Second
	defaultMaxResults      = 50

	defaultMinConfidenceThreshold = 0.3
	defaultAutoConfirmThreshold   = 0.95

	defaultCacheTTL = 1 * time.Hour

	emaWeightPrevious = 0.9
	emaWeightCurrent  = 0.1

	validationStrategyAgreementThreshold = 2.0
	validationHighConfidenceThreshold    = 0.8
)

// DefaultEngineConfig returns sensible defaults
func DefaultEngineConfig() EngineConfig {
	return EngineConfig{
		ParallelizeStrategies:  true,
		StrategyTimeout:        defaultStrategyTimeout,
		MaxResults:             defaultMaxResults,
		MinConfidenceThreshold: defaultMinConfidenceThreshold,
		RequireAgreement:       false,
		AutoConfirmThreshold:   defaultAutoConfirmThreshold,
		ResolveConflicts:       true,
		PreferHighestStrategy:  true,
		EnableCache:            true,
		CacheTTL:               defaultCacheTTL,
	}
}

// EngineMetrics tracks engine performance
type EngineMetrics struct {
	TotalDetections      int64
	SuccessfulDetections int64
	FailedDetections     int64
	TotalDuration        time.Duration
	StrategyDurations    map[StrategyType]time.Duration
	AverageConfidence    float64
	ConflictsDetected    int64
}

// DetectionOutput is the final result of equivalence detection
type DetectionOutput struct {
	SourceItemID uuid.UUID
	Equivalences []*ResolvedEquivalence
	Conflicts    []ConflictReport
	Metrics      StrategyMetrics
	Timestamp    time.Time
}

// StrategyMetrics contains performance metrics
type StrategyMetrics struct {
	TotalDuration    time.Duration
	StrategiesRun    int
	ResultsGenerated int
	ConflictsFound   int
}

// NewEngine creates a new equivalence detection engine
func NewEngine(embeddingProvider embeddings.Provider) *Engine {
	// Create all strategies
	strategies := map[StrategyType]Strategy{
		StrategyNamingPattern:      NewNamingStrategy(),
		StrategySemanticSimilarity: NewSemanticStrategy(embeddingProvider),
		StrategyAPIContract:        NewAPIContractStrategy(),
		StrategyExplicitAnnotation: NewAnnotationStrategy(),
	}

	// Create detector
	detector := NewDetector()
	for _, strategy := range strategies {
		detector.RegisterStrategy(strategy)
	}

	return &Engine{
		strategies: strategies,
		detector:   detector,
		scorer:     NewConfidenceScorer(),
		resolver:   NewEquivalenceResolver(),
		reconciler: NewConflictReconciler(),
		config:     DefaultEngineConfig(),
		metrics: &EngineMetrics{
			StrategyDurations: make(map[StrategyType]time.Duration),
		},
	}
}

// SetConfig updates engine configuration
func (engine *Engine) SetConfig(config EngineConfig) {
	engine.mu.Lock()
	defer engine.mu.Unlock()
	engine.config = config
}

// DetectEquivalences runs all strategies and returns comprehensive results
func (engine *Engine) DetectEquivalences(ctx context.Context, req *StrategyDetectionRequest) (*DetectionOutput, error) {
	startTime := time.Now()

	// Validate request
	if req.SourceItem == nil || req.SourceItem.ID == uuid.Nil {
		return nil, errors.New("invalid source item")
	}

	output := &DetectionOutput{
		SourceItemID: req.SourceItem.ID,
		Equivalences: make([]*ResolvedEquivalence, 0),
		Conflicts:    make([]ConflictReport, 0),
		Timestamp:    startTime,
	}

	// Run detection strategies
	var suggestions []Suggestion
	var detectionErr error

	if engine.config.ParallelizeStrategies {
		suggestions, detectionErr = engine.detectParallel(ctx, req)
	} else {
		suggestions, detectionErr = engine.detectSequential(ctx, req)
	}

	if detectionErr != nil {
		return output, detectionErr
	}

	// Filter by minimum confidence
	suggestions = engine.filterByConfidence(suggestions)

	if len(suggestions) == 0 {
		output.Metrics.TotalDuration = time.Since(startTime)
		return output, nil
	}

	// Detect conflicts
	conflicts := engine.detectConflicts(suggestions)
	output.Conflicts = conflicts

	// Resolve to final equivalences
	resolutionCtx := &ResolutionContext{
		ProjectID:    req.ProjectID,
		SourceItemID: req.SourceItem.ID,
		Candidates:   suggestions,
	}

	equivalences := engine.resolver.Resolve(resolutionCtx)

	// Limit results
	if engine.config.MaxResults > 0 && len(equivalences) > engine.config.MaxResults {
		equivalences = equivalences[:engine.config.MaxResults]
	}

	output.Equivalences = equivalences

	// Record metrics
	engine.recordMetrics(output, time.Since(startTime))

	return output, nil
}

// detectSequential runs strategies one at a time
func (engine *Engine) detectSequential(ctx context.Context, req *StrategyDetectionRequest) ([]Suggestion, error) {
	return engine.detector.Detect(ctx, req)
}

// detectParallel runs multiple strategies in parallel
func (engine *Engine) detectParallel(ctx context.Context, req *StrategyDetectionRequest) ([]Suggestion, error) {
	strategies := engine.strategyNamesForRequest(req)
	resultsChan := make(chan []Link, len(strategies))
	errChan := make(chan error, len(strategies))

	// Create a cancellation context with timeout
	ctx, cancel := context.WithTimeout(ctx, engine.config.StrategyTimeout)
	defer cancel()

	var wg sync.WaitGroup
	engine.runStrategiesAsync(ctx, req, strategies, resultsChan, errChan, &wg)
	go engine.waitAndClose(&wg, resultsChan, errChan)

	allLinks := collectLinks(resultsChan)

	// Aggregate results
	suggestions := engine.detector.aggregator.Aggregate(req.SourceItem, allLinks, req.MinConfidence)

	return suggestions, nil
}

func (engine *Engine) strategyNamesForRequest(req *StrategyDetectionRequest) []StrategyType {
	strategies := req.Strategies
	if len(strategies) == 0 {
		return engine.detector.ListStrategies()
	}
	return strategies
}

func (engine *Engine) runStrategiesAsync(
	ctx context.Context,
	req *StrategyDetectionRequest,
	strategyNames []StrategyType,
	resultsChan chan<- []Link,
	errChan chan<- error,
	wg *sync.WaitGroup,
) {
	for _, strategyName := range strategyNames {
		strategy, ok := engine.detector.GetStrategy(strategyName)
		if !ok {
			continue
		}
		wg.Add(1)
		go engine.runSingleStrategy(ctx, req, strategy, resultsChan, errChan, wg)
	}
}

func (engine *Engine) runSingleStrategy(
	ctx context.Context,
	req *StrategyDetectionRequest,
	strategy Strategy,
	resultsChan chan<- []Link,
	errChan chan<- error,
	wg *sync.WaitGroup,
) {
	defer wg.Done()

	startTime := time.Now()
	result, err := strategy.Detect(ctx, req)
	duration := time.Since(startTime)

	engine.recordStrategyDuration(strategy.Name(), duration)

	if err != nil {
		errChan <- err
		return
	}
	if result != nil && len(result.Links) > 0 {
		resultsChan <- result.Links
	}
}

func (engine *Engine) recordStrategyDuration(strategyName StrategyType, duration time.Duration) {
	engine.mu.Lock()
	engine.metrics.StrategyDurations[strategyName] = duration
	engine.mu.Unlock()
}

func (engine *Engine) waitAndClose(wg *sync.WaitGroup, resultsChan chan []Link, errChan chan error) {
	wg.Wait()
	close(resultsChan)
	close(errChan)
}

func collectLinks(resultsChan <-chan []Link) []Link {
	var allLinks []Link
	for links := range resultsChan {
		allLinks = append(allLinks, links...)
	}
	return allLinks
}

// filterByConfidence removes suggestions below threshold
func (engine *Engine) filterByConfidence(suggestions []Suggestion) []Suggestion {
	filtered := make([]Suggestion, 0, len(suggestions))
	for _, s := range suggestions {
		if s.Confidence >= engine.config.MinConfidenceThreshold {
			filtered = append(filtered, s)
		}
	}
	return filtered
}

// detectConflicts identifies conflicting equivalences
func (engine *Engine) detectConflicts(suggestions []Suggestion) []ConflictReport {
	if !engine.config.ResolveConflicts || len(suggestions) < 2 {
		return nil
	}

	resolver := NewConflictResolver()
	return resolver.DetectConflicts(suggestions)
}

// recordMetrics updates engine metrics
func (engine *Engine) recordMetrics(output *DetectionOutput, duration time.Duration) {
	engine.mu.Lock()
	defer engine.mu.Unlock()

	engine.metrics.TotalDetections++
	engine.metrics.TotalDuration += duration

	if len(output.Equivalences) > 0 {
		engine.metrics.SuccessfulDetections++
	}

	if len(output.Conflicts) > 0 {
		engine.metrics.ConflictsDetected++
	}

	// Update average confidence
	if len(output.Equivalences) > 0 {
		totalConf := 0.0
		for _, eq := range output.Equivalences {
			totalConf += eq.Confidence
		}
		avgConf := totalConf / float64(len(output.Equivalences))

		// Exponential moving average
		if engine.metrics.AverageConfidence == 0 {
			engine.metrics.AverageConfidence = avgConf
		} else {
			previous := engine.metrics.AverageConfidence
			engine.metrics.AverageConfidence = emaWeightPrevious*previous + emaWeightCurrent*avgConf
		}
	}

	output.Metrics = StrategyMetrics{
		TotalDuration:    duration,
		StrategiesRun:    len(engine.strategies),
		ResultsGenerated: len(output.Equivalences),
		ConflictsFound:   len(output.Conflicts),
	}
}

// GetMetrics returns current engine metrics (copy of fields only; mutex is not copied)
func (engine *Engine) GetMetrics() *EngineMetrics {
	engine.mu.RLock()
	defer engine.mu.RUnlock()

	metrics := engine.metrics
	return &EngineMetrics{
		TotalDetections:      metrics.TotalDetections,
		SuccessfulDetections: metrics.SuccessfulDetections,
		FailedDetections:     metrics.FailedDetections,
		TotalDuration:        metrics.TotalDuration,
		StrategyDurations:    metrics.StrategyDurations,
		AverageConfidence:    metrics.AverageConfidence,
		ConflictsDetected:    metrics.ConflictsDetected,
	}
}

// RegisterStrategy adds a custom strategy to the engine
func (engine *Engine) RegisterStrategy(strategy Strategy) error {
	if strategy == nil {
		return errors.New("strategy cannot be nil")
	}

	engine.mu.Lock()
	defer engine.mu.Unlock()

	engine.strategies[strategy.Name()] = strategy
	engine.detector.RegisterStrategy(strategy)

	return nil
}

// GetStrategy returns a registered strategy
func (engine *Engine) GetStrategy(name StrategyType) (Strategy, bool) {
	engine.mu.RLock()
	defer engine.mu.RUnlock()

	strategy, ok := engine.strategies[name]
	return strategy, ok
}

// ListStrategies returns all registered strategy names
func (engine *Engine) ListStrategies() []StrategyType {
	engine.mu.RLock()
	defer engine.mu.RUnlock()

	names := make([]StrategyType, 0, len(engine.strategies))
	for name := range engine.strategies {
		names = append(names, name)
	}

	sort.Slice(names, func(i, j int) bool {
		return string(names[i]) < string(names[j])
	})

	return names
}

// ValidateDetection checks the quality of detection results
func (engine *Engine) ValidateDetection(output *DetectionOutput) *ValidationReport {
	report := &ValidationReport{
		Timestamp: time.Now(),
		Quality:   make(map[string]float64),
	}

	if len(output.Equivalences) == 0 {
		report.Valid = true
		report.Message = "No equivalences detected"
		return report
	}

	stats := computeConfidenceStats(output.Equivalences)
	report.Quality["average_confidence"] = stats.average
	report.Quality["min_confidence"] = stats.minimum
	report.Quality["max_confidence"] = stats.maximum

	if len(output.Conflicts) > 0 {
		report.Issues = append(report.Issues, fmt.Sprintf("%d conflicts detected", len(output.Conflicts)))
	}

	avgEvidenceCount := computeAverageEvidenceCount(output.Equivalences)
	report.Quality["avg_evidence_count"] = avgEvidenceCount
	report.Valid, report.Message = selectAgreementOutcome(avgEvidenceCount, stats.average)

	return report
}

type confidenceStats struct {
	average float64
	minimum float64
	maximum float64
}

func computeConfidenceStats(equivalences []*ResolvedEquivalence) confidenceStats {
	totalConf := 0.0
	minConf := equivalences[0].Confidence
	maxConf := equivalences[0].Confidence

	for _, eq := range equivalences {
		totalConf += eq.Confidence
		if eq.Confidence < minConf {
			minConf = eq.Confidence
		}
		if eq.Confidence > maxConf {
			maxConf = eq.Confidence
		}
	}

	averageConf := totalConf / float64(len(equivalences))
	return confidenceStats{
		average: averageConf,
		minimum: minConf,
		maximum: maxConf,
	}
}

func computeAverageEvidenceCount(equivalences []*ResolvedEquivalence) float64 {
	totalEvidence := 0.0
	for _, eq := range equivalences {
		totalEvidence += float64(len(eq.Evidence))
	}
	return totalEvidence / float64(len(equivalences))
}

func selectAgreementOutcome(avgEvidenceCount float64, avgConfidence float64) (bool, string) {
	switch {
	case avgEvidenceCount >= validationStrategyAgreementThreshold:
		return true, "Good agreement across multiple strategies"
	case avgConfidence >= validationHighConfidenceThreshold:
		return true, "Single strategy with high confidence"
	default:
		return false, "Low confidence and weak agreement"
	}
}

// ValidationReport provides assessment of detection quality
type ValidationReport struct {
	Valid     bool
	Message   string
	Quality   map[string]float64
	Issues    []string
	Timestamp time.Time
}

// ExecuteWithTimeout runs detection with a maximum time limit
func (engine *Engine) ExecuteWithTimeout(
	ctx context.Context,
	req *StrategyDetectionRequest,
	timeout time.Duration,
) (*DetectionOutput, error) {
	ctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	return engine.DetectEquivalences(ctx, req)
}

// BatchDetect runs detection for multiple items
func (engine *Engine) BatchDetect(
	ctx context.Context,
	requests []*StrategyDetectionRequest,
) ([]*DetectionOutput, error) {
	results := make([]*DetectionOutput, len(requests))
	errors := make([]error, len(requests))

	var wg sync.WaitGroup
	for index, request := range requests {
		wg.Add(1)
		go func(idx int, r *StrategyDetectionRequest) {
			defer wg.Done()
			output, err := engine.DetectEquivalences(ctx, r)
			results[idx] = output
			errors[idx] = err
		}(index, request)
	}

	wg.Wait()

	// Check for errors
	for _, err := range errors {
		if err != nil {
			return results, err
		}
	}

	return results, nil
}
