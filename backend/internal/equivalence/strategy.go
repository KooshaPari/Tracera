package equivalence

import (
	"context"

	"github.com/google/uuid"
)

// StrategyItemInfo contains the minimal information needed for equivalence detection (internal use)
type StrategyItemInfo struct {
	ID          uuid.UUID        `json:"id"`
	ProjectID   uuid.UUID        `json:"project_id"`
	Title       string           `json:"title"`
	Description string           `json:"description"`
	Type        string           `json:"type"`
	Perspective string           `json:"perspective"`
	CanonicalID *uuid.UUID       `json:"canonical_id,omitempty"`
	CodeRef     *StrategyCodeRef `json:"code_ref,omitempty"`
	DocRef      *StrategyDocRef  `json:"doc_ref,omitempty"`
	Metadata    map[string]any   `json:"metadata,omitempty"`
	Embedding   []float32        `json:"embedding,omitempty"`
}

// StrategyCodeRef contains code location information for strategy detection
type StrategyCodeRef struct {
	FilePath    string `json:"file_path"`
	StartLine   int    `json:"start_line"`
	EndLine     int    `json:"end_line"`
	SymbolName  string `json:"symbol_name"`
	SymbolType  string `json:"symbol_type"` // function, class, variable, etc.
	Language    string `json:"language"`
	PackageName string `json:"package_name,omitempty"`
}

// StrategyDocRef contains documentation location information for strategy detection
type StrategyDocRef struct {
	DocumentID  uuid.UUID `json:"document_id"`
	SectionPath string    `json:"section_path"`
	HeadingText string    `json:"heading_text"`
	ChunkIndex  int       `json:"chunk_index"`
}

// StrategyDetectionRequest contains parameters for equivalence detection (internal use)
type StrategyDetectionRequest struct {
	ProjectID     uuid.UUID           `json:"project_id"`
	SourceItem    *StrategyItemInfo   `json:"source_item"`
	CandidatePool []*StrategyItemInfo `json:"candidate_pool,omitempty"` // If empty, searches all items
	Strategies    []StrategyType      `json:"strategies,omitempty"`     // If empty, uses all strategies
	MinConfidence float64             `json:"min_confidence"`           // Minimum confidence threshold
	MaxResults    int                 `json:"max_results"`              // Maximum results per strategy
}

// DetectionResult contains the result of a single strategy's detection
type DetectionResult struct {
	Strategy     StrategyType `json:"strategy"`
	Links        []Link       `json:"links"`
	DurationMs   int64        `json:"duration_ms"`
	ItemsScanned int          `json:"items_scanned"`
	Error        string       `json:"error,omitempty"`
}

// Strategy defines the interface for equivalence detection strategies
type Strategy interface {
	// Name returns the strategy type identifier
	Name() StrategyType

	// Detect finds equivalences between the source item and candidates
	Detect(ctx context.Context, req *StrategyDetectionRequest) (*DetectionResult, error)

	// DefaultConfidence returns the base confidence score for this strategy
	DefaultConfidence() float64

	// RequiresEmbeddings returns true if this strategy needs embedding vectors
	RequiresEmbeddings() bool
}

// Detector orchestrates multiple strategies for equivalence detection
type Detector struct {
	strategies map[StrategyType]Strategy
	aggregator *ConfidenceAggregator
}

// NewDetector creates a new equivalence detector with the given strategies
func NewDetector(strategies ...Strategy) *Detector {
	detector := &Detector{
		strategies: make(map[StrategyType]Strategy),
		aggregator: NewConfidenceAggregator(),
	}
	for _, s := range strategies {
		detector.strategies[s.Name()] = s
	}
	return detector
}

// RegisterStrategy adds a strategy to the detector
func (detector *Detector) RegisterStrategy(s Strategy) {
	detector.strategies[s.Name()] = s
}

// Detect runs all requested strategies and aggregates results
func (detector *Detector) Detect(ctx context.Context, req *StrategyDetectionRequest) ([]Suggestion, error) {
	strategies := req.Strategies
	if len(strategies) == 0 {
		// Use all registered strategies
		strategies = make([]StrategyType, 0, len(detector.strategies))
		for name := range detector.strategies {
			strategies = append(strategies, name)
		}
	}

	// Collect results from all strategies
	var allLinks []Link
	for _, strategyName := range strategies {
		strategy, ok := detector.strategies[strategyName]
		if !ok {
			continue
		}

		result, err := strategy.Detect(ctx, req)
		if err != nil {
			// Log error but continue with other strategies
			continue
		}

		allLinks = append(allLinks, result.Links...)
	}

	// Aggregate and deduplicate results
	suggestions := detector.aggregator.Aggregate(req.SourceItem, allLinks, req.MinConfidence)

	// Sort by confidence and limit results
	if req.MaxResults > 0 && len(suggestions) > req.MaxResults {
		suggestions = suggestions[:req.MaxResults]
	}

	return suggestions, nil
}

// GetStrategy returns a specific strategy by name
func (detector *Detector) GetStrategy(name StrategyType) (Strategy, bool) {
	s, ok := detector.strategies[name]
	return s, ok
}

// ListStrategies returns all registered strategy names
func (detector *Detector) ListStrategies() []StrategyType {
	names := make([]StrategyType, 0, len(detector.strategies))
	for name := range detector.strategies {
		names = append(names, name)
	}
	return names
}
