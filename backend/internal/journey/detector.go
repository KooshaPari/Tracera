package journey

import (
	"context"
	"fmt"
	"sync"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// Detector orchestrates journey detection across multiple dimensions
type Detector interface {
	DetectJourneys(ctx context.Context, projectID string) (*DetectionResult, error)
	DetectUserFlows(ctx context.Context, projectID string) ([]*DerivedJourney, error)
	DetectDataPaths(ctx context.Context, projectID string) ([]*DerivedJourney, error)
	DetectCallChains(ctx context.Context, projectID string) ([]*DerivedJourney, error)
	GetJourneyStats(ctx context.Context, projectID string) (*Stats, error)
}

// detector implements Detector
type detector struct {
	itemRepo     repository.ItemRepository
	linkRepo     repository.LinkRepository
	config       *DetectionConfig
	userFlowDet  UserFlowDetector
	dataFlowDet  DataFlowDetector
	callChainDet CallChainDetector
	scorer       Scorer
	mu           sync.RWMutex
	cache        map[string]*DetectionResult
	cacheTimeout time.Duration
}

const (
	detectionResultBuffer = 1
	detectionErrorBuffer  = 3
	topIntermediateLimit  = 5
	minIntermediateNodes  = 2
)

// NewJourneyDetector creates a new journey detector
func NewJourneyDetector(
	itemRepo repository.ItemRepository,
	linkRepo repository.LinkRepository,
	config *DetectionConfig,
) Detector {
	if config == nil {
		config = &DetectionConfig{
			MinPathLength:       defaultMinPathLength,
			MaxPathLength:       defaultMaxPathLength,
			MinFrequency:        defaultMinFrequency,
			MinScore:            defaultMinScore,
			AllowCycles:         false,
			GroupSimilar:        true,
			SimilarityThreshold: defaultSimilarityThreshold,
		}
	}

	return &detector{
		itemRepo:     itemRepo,
		linkRepo:     linkRepo,
		config:       config,
		userFlowDet:  NewUserFlowDetector(itemRepo, linkRepo, config),
		dataFlowDet:  NewDataFlowDetector(itemRepo, linkRepo, config),
		callChainDet: NewCallChainDetector(itemRepo, linkRepo, config),
		scorer:       NewScorer(),
		cache:        make(map[string]*DetectionResult),
		cacheTimeout: defaultCacheTimeout,
	}
}

// DetectJourneys orchestrates detection across all journey types
func (d *detector) DetectJourneys(ctx context.Context, projectID string) (*DetectionResult, error) {
	if cached, ok := d.getCachedDetection(projectID); ok {
		return cached, nil
	}

	startTime := time.Now()
	result := newDetectionResult()
	journeys, errs := d.runDetectors(ctx, projectID)
	result.Journeys = append(result.Journeys, journeys...)
	result.Errors = append(result.Errors, errs...)

	// Score and rank journeys
	if err := d.scoreAndRankJourneys(result.Journeys); err != nil {
		result.Errors = append(result.Errors, fmt.Sprintf("scoring failed: %v", err))
	}

	// Count total paths analyzed
	result.TotalPaths = len(result.Journeys)
	result.ValidPaths = countValidPaths(result.Journeys, d.config.MinScore)

	result.DetectionTimeMs = time.Since(startTime).Milliseconds()

	// Cache result
	d.mu.Lock()
	d.cache[projectID] = result
	d.mu.Unlock()

	return result, nil
}

func newDetectionResult() *DetectionResult {
	return &DetectionResult{
		Journeys: make([]*DerivedJourney, 0),
		Errors:   make([]string, 0),
	}
}

func (d *detector) getCachedDetection(projectID string) (*DetectionResult, bool) {
	d.mu.RLock()
	defer d.mu.RUnlock()
	if cached, ok := d.cache[projectID]; ok {
		return cached, true
	}
	return nil, false
}

func (d *detector) runDetectors(ctx context.Context, projectID string) ([]*DerivedJourney, []string) {
	userFlowsCh := make(chan []*DerivedJourney, detectionResultBuffer)
	dataPathsCh := make(chan []*DerivedJourney, detectionResultBuffer)
	callChainsCh := make(chan []*DerivedJourney, detectionResultBuffer)
	errCh := make(chan error, detectionErrorBuffer)

	var wg sync.WaitGroup

	wg.Add(1)
	go d.launchDetector(&wg, errCh, userFlowsCh, "user flow", func() ([]*DerivedJourney, error) {
		return d.userFlowDet.DetectUserFlows(ctx, projectID)
	})

	wg.Add(1)
	go d.launchDetector(&wg, errCh, dataPathsCh, "data path", func() ([]*DerivedJourney, error) {
		return d.dataFlowDet.DetectDataPaths(ctx, projectID)
	})

	wg.Add(1)
	go d.launchDetector(&wg, errCh, callChainsCh, "call chain", func() ([]*DerivedJourney, error) {
		return d.callChainDet.DetectCallChains(ctx, projectID)
	})

	wg.Wait()
	close(errCh)

	errors := collectDetectionErrors(errCh)
	journeys := collectDetectionJourneys(userFlowsCh, dataPathsCh, callChainsCh)

	return journeys, errors
}

func (d *detector) launchDetector(
	wg *sync.WaitGroup,
	errCh chan<- error,
	resultCh chan<- []*DerivedJourney,
	name string,
	detect func() ([]*DerivedJourney, error),
) {
	defer wg.Done()
	journeys, err := detect()
	if err != nil {
		errCh <- fmt.Errorf("%s detection failed: %w", name, err)
		resultCh <- nil
		return
	}
	resultCh <- journeys
}

func collectDetectionErrors(errCh <-chan error) []string {
	errors := make([]string, 0)
	for err := range errCh {
		errors = append(errors, err.Error())
	}
	return errors
}

func collectDetectionJourneys(channels ...<-chan []*DerivedJourney) []*DerivedJourney {
	journeys := make([]*DerivedJourney, 0)
	for _, ch := range channels {
		if items := <-ch; items != nil {
			journeys = append(journeys, items...)
		}
	}
	return journeys
}

func countValidPaths(journeys []*DerivedJourney, minScore float64) int {
	count := 0
	for _, j := range journeys {
		if j.Score >= minScore {
			count++
		}
	}
	return count
}

// DetectUserFlows delegates to user flow detector
func (d *detector) DetectUserFlows(ctx context.Context, projectID string) ([]*DerivedJourney, error) {
	return d.userFlowDet.DetectUserFlows(ctx, projectID)
}

// DetectDataPaths delegates to data flow detector
func (d *detector) DetectDataPaths(ctx context.Context, projectID string) ([]*DerivedJourney, error) {
	return d.dataFlowDet.DetectDataPaths(ctx, projectID)
}

// DetectCallChains delegates to call chain detector
func (d *detector) DetectCallChains(ctx context.Context, projectID string) ([]*DerivedJourney, error) {
	return d.callChainDet.DetectCallChains(ctx, projectID)
}

// GetJourneyStats analyzes overall journey statistics
func (d *detector) GetJourneyStats(ctx context.Context, projectID string) (*Stats, error) {
	result, err := d.DetectJourneys(ctx, projectID)
	if err != nil {
		return nil, err
	}

	stats := initJourneyStats(result.Journeys)
	updateStatsByType(stats, result.Journeys)
	updateAverageStats(stats, result.Journeys)

	startCounts, endCounts := countJourneyEndpoints(result.Journeys)
	stats.MostCommonStart = mostCommonNode(startCounts)
	stats.MostCommonEnd = mostCommonNode(endCounts)
	stats.CommonIntermediates = topIntermediateNodes(result.Journeys, topIntermediateLimit)

	return stats, nil
}

func initJourneyStats(journeys []*DerivedJourney) *Stats {
	return &Stats{
		TotalJourneys: len(journeys),
		ByType:        make(map[Type]int),
	}
}

func updateStatsByType(stats *Stats, journeys []*DerivedJourney) {
	for _, j := range journeys {
		stats.ByType[j.Type]++
	}
}

func updateAverageStats(stats *Stats, journeys []*DerivedJourney) {
	var totalLength, totalScore float64
	for _, j := range journeys {
		totalLength += float64(len(j.NodeIDs))
		totalScore += j.Score
	}

	if len(journeys) > 0 {
		stats.AveragePathLength = totalLength / float64(len(journeys))
		stats.AverageScore = totalScore / float64(len(journeys))
	}
}

func countJourneyEndpoints(journeys []*DerivedJourney) (map[string]int, map[string]int) {
	startNodeCounts := make(map[string]int)
	endNodeCounts := make(map[string]int)
	for _, j := range journeys {
		if len(j.NodeIDs) > 0 {
			startNodeCounts[j.NodeIDs[0]]++
			endNodeCounts[j.NodeIDs[len(j.NodeIDs)-1]]++
		}
	}
	return startNodeCounts, endNodeCounts
}

func mostCommonNode(counts map[string]int) string {
	var maxCount int
	var mostCommon string
	for nodeID, count := range counts {
		if count > maxCount {
			maxCount = count
			mostCommon = nodeID
		}
	}
	return mostCommon
}

// countIntermediateNodes counts how often each node appears as an intermediate node in journeys.
func countIntermediateNodes(journeys []*DerivedJourney) map[string]int {
	counts := make(map[string]int)
	for _, j := range journeys {
		if len(j.NodeIDs) > minIntermediateNodes {
			for i := 1; i < len(j.NodeIDs)-1; i++ {
				counts[j.NodeIDs[i]]++
			}
		}
	}
	return counts
}

func topIntermediateNodes(journeys []*DerivedJourney, limit int) []string {
	intermediateCount := countIntermediateNodes(journeys)

	type nodeCount struct {
		id    string
		count int
	}
	intermediate := make([]nodeCount, 0, len(intermediateCount))
	for id, count := range intermediateCount {
		intermediate = append(intermediate, nodeCount{id, count})
	}
	for i := 0; i < len(intermediate) && i < limit; i++ {
		for j := i + 1; j < len(intermediate); j++ {
			if intermediate[j].count > intermediate[i].count {
				intermediate[i], intermediate[j] = intermediate[j], intermediate[i]
			}
		}
	}

	common := make([]string, 0, limit)
	for i := 0; i < len(intermediate) && i < limit; i++ {
		common = append(common, intermediate[i].id)
	}
	return common
}

// scoreAndRankJourneys applies scoring and ranking to journeys
func (d *detector) scoreAndRankJourneys(journeys []*DerivedJourney) error {
	for _, journey := range journeys {
		metrics := d.scorer.ScoreJourney(journey)
		journey.Score = metrics.TotalScore
	}

	// Sort by score (descending)
	for i := 0; i < len(journeys); i++ {
		for j := i + 1; j < len(journeys); j++ {
			if journeys[j].Score > journeys[i].Score {
				journeys[i], journeys[j] = journeys[j], journeys[i]
			}
		}
	}

	return nil
}

// InvalidateCache clears the detection cache
func (d *detector) InvalidateCache() {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.cache = make(map[string]*DetectionResult)
}

// InvalidateCacheFor clears cache for a specific project
func (d *detector) InvalidateCacheFor(projectID string) {
	d.mu.Lock()
	defer d.mu.Unlock()
	delete(d.cache, projectID)
}

// GetConfig returns the current detection configuration
func (d *detector) GetConfig() *DetectionConfig {
	d.mu.RLock()
	defer d.mu.RUnlock()
	return d.config
}

// SetConfig updates the detection configuration
func (d *detector) SetConfig(config *DetectionConfig) {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.config = config
	d.InvalidateCache()
}
