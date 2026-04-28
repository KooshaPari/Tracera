package equivalence

import (
	"context"
	"regexp"
	"strings"
	"time"

	"github.com/google/uuid"
)

const (
	namingMinSimilarity     = 0.7
	namingDefaultConfidence = 0.7
)

// NamingStrategy detects equivalences based on naming patterns
// Handles: CamelCase/snake_case matching, plural/singular, common prefixes/suffixes
type NamingStrategy struct {
	minSimilarity float64
}

// NewNamingStrategy creates a new naming pattern strategy
func NewNamingStrategy() *NamingStrategy {
	return &NamingStrategy{
		minSimilarity: namingMinSimilarity,
	}
}

// Name returns the strategy identifier.
func (strategy *NamingStrategy) Name() StrategyType {
	return StrategyNamingPattern
}

// DefaultConfidence returns the base confidence for naming matches.
func (strategy *NamingStrategy) DefaultConfidence() float64 {
	return namingDefaultConfidence
}

// RequiresEmbeddings reports whether this strategy needs embeddings.
func (strategy *NamingStrategy) RequiresEmbeddings() bool {
	return false
}

// Detect finds candidate links based on naming similarity.
func (strategy *NamingStrategy) Detect(ctx context.Context, req *StrategyDetectionRequest) (*DetectionResult, error) {
	start := time.Now()
	result := newDetectionResult(strategy.Name())

	sourceNorm := strategy.normalizeForComparison(req.SourceItem.Title)
	if sourceNorm == "" {
		finalizeDetectionResult(result, start)
		return result, nil
	}

	for _, candidate := range req.CandidatePool {
		if err := checkContext(ctx, result); err != nil {
			return result, err
		}

		if candidate.ID == req.SourceItem.ID {
			continue
		}
		result.ItemsScanned++

		candidateNorm := strategy.normalizeForComparison(candidate.Title)
		if candidateNorm == "" {
			continue
		}

		similarity := strategy.calculateSimilarity(sourceNorm, candidateNorm)
		if similarity >= strategy.minSimilarity {
			result.Links = append(
				result.Links,
				strategy.buildLink(req, sourceNorm, candidateNorm, candidate, similarity),
			)
		}
	}

	finalizeDetectionResult(result, start)
	return result, nil
}

func newDetectionResult(strategy StrategyType) *DetectionResult {
	return &DetectionResult{
		Strategy: strategy,
		Links:    make([]Link, 0),
	}
}

func finalizeDetectionResult(result *DetectionResult, start time.Time) {
	result.DurationMs = time.Since(start).Milliseconds()
}

func checkContext(ctx context.Context, result *DetectionResult) error {
	select {
	case <-ctx.Done():
		result.Error = ctx.Err().Error()
		return ctx.Err()
	default:
		return nil
	}
}

func (strategy *NamingStrategy) buildLink(
	req *StrategyDetectionRequest,
	sourceNorm string,
	candidateNorm string,
	candidate *StrategyItemInfo,
	similarity float64,
) Link {
	confidence := strategy.DefaultConfidence() * similarity
	now := time.Now()

	return Link{
		ID:           uuid.New(),
		ProjectID:    req.ProjectID,
		SourceItemID: req.SourceItem.ID,
		TargetItemID: candidate.ID,
		LinkType:     "same_as",
		Confidence:   confidence,
		Provenance:   strategy.Name(),
		Status:       StatusSuggested,
		Evidence: []Evidence{{
			Strategy:    strategy.Name(),
			Confidence:  confidence,
			Description: "Naming pattern match detected",
			Details: map[string]any{
				"source_normalized": sourceNorm,
				"target_normalized": candidateNorm,
				"similarity":        similarity,
			},
			DetectedAt: now,
		}},
		CreatedAt: now,
		UpdatedAt: now,
	}
}

// normalizeForComparison converts a name to a normalized form for comparison
func (strategy *NamingStrategy) normalizeForComparison(name string) string {
	// Convert camelCase and PascalCase to space-separated
	re := regexp.MustCompile(`([a-z])([A-Z])`)
	name = re.ReplaceAllString(name, "${1} ${2}")

	// Convert snake_case, kebab-case to space-separated
	name = strings.ReplaceAll(name, "_", " ")
	name = strings.ReplaceAll(name, "-", " ")

	// Lowercase and trim
	name = strings.ToLower(strings.TrimSpace(name))

	// Remove common suffixes that don't affect meaning
	suffixes := []string{" service", " handler", " controller", " component", " view", " model", " entity"}
	for _, suffix := range suffixes {
		name = strings.TrimSuffix(name, suffix)
	}

	// Singularize common plurals
	switch {
	case strings.HasSuffix(name, "ies"):
		name = strings.TrimSuffix(name, "ies") + "y"
	case strings.HasSuffix(name, "es") && !strings.HasSuffix(name, "ss"):
		name = strings.TrimSuffix(name, "es")
	case strings.HasSuffix(name, "s") && !strings.HasSuffix(name, "ss"):
		name = strings.TrimSuffix(name, "s")
	}

	return strings.TrimSpace(name)
}

// calculateSimilarity computes similarity between two normalized names
func (strategy *NamingStrategy) calculateSimilarity(left, right string) float64 {
	if left == right {
		return 1.0
	}

	// Token-based similarity (Jaccard)
	tokensA := strings.Fields(left)
	tokensB := strings.Fields(right)

	if len(tokensA) == 0 || len(tokensB) == 0 {
		return 0.0
	}

	setA := make(map[string]bool)
	for _, t := range tokensA {
		setA[t] = true
	}

	intersection := 0
	for _, t := range tokensB {
		if setA[t] {
			intersection++
		}
	}

	union := len(setA)
	for _, t := range tokensB {
		if !setA[t] {
			union++
		}
	}

	return float64(intersection) / float64(union)
}
