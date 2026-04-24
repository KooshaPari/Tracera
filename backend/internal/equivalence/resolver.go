package equivalence

import (
	"sort"
	"time"

	"github.com/google/uuid"
)

const (
	conflictHighConfidenceThreshold = 0.75
	conflictHighConfidenceMinCount  = 2
	agreementVarianceNormalization  = 0.25
	agreementPercentScale           = 100
)

// Resolver handles complex resolution logic for detected equivalences
type Resolver struct {
	conflictReconciler *ConflictReconciler
	scorer             *ConfidenceScorer
	validator          *ConfidenceValidator
}

// NewEquivalenceResolver creates a new resolver
func NewEquivalenceResolver() *Resolver {
	return &Resolver{
		conflictReconciler: NewConflictReconciler(),
		scorer:             NewConfidenceScorer(),
		validator:          NewConfidenceValidator(),
	}
}

// ResolutionContext provides context for resolution decisions
type ResolutionContext struct {
	ProjectID       uuid.UUID
	SourceItemID    uuid.UUID
	Candidates      []Suggestion
	ExistingLinks   []Link
	UserPreferences *UserPreferences
}

// UserPreferences captures user resolution preferences
type UserPreferences struct {
	AutoConfirmThreshold float64
	RequireManualReview  bool
	PreferredStrategy    StrategyType
	ExcludeStrategies    []StrategyType
}

// ResolvedEquivalence is the final result of resolution
type ResolvedEquivalence struct {
	ID               uuid.UUID
	SourceItemID     uuid.UUID
	TargetItemID     uuid.UUID
	LinkType         string
	Confidence       float64
	SelectedStrategy StrategyType
	Evidence         []Evidence
	Status           Status
	ResolutionReason string
	RequiresReview   bool
	Timestamp        time.Time
}

// Resolve performs comprehensive equivalence resolution
func (er *Resolver) Resolve(ctx *ResolutionContext) []*ResolvedEquivalence {
	if len(ctx.Candidates) == 0 {
		return nil
	}

	// Group candidates by target
	byTarget := er.groupByTarget(ctx.Candidates)

	var results []*ResolvedEquivalence
	for targetID, suggestions := range byTarget {
		resolved := er.resolveSingleTarget(ctx, targetID, suggestions)
		if resolved != nil {
			results = append(results, resolved)
		}
	}

	// Sort by confidence descending
	sort.Slice(results, func(i, j int) bool {
		return results[i].Confidence > results[j].Confidence
	})

	return results
}

// resolveSingleTarget resolves equivalences for a single target
func (er *Resolver) resolveSingleTarget(
	_ *ResolutionContext,
	targetID uuid.UUID,
	suggestions []Suggestion,
) *ResolvedEquivalence {
	if len(suggestions) == 0 {
		return nil
	}

	// Pick the best suggestion
	best := er.selectBestSuggestion(suggestions)
	if best == nil {
		return nil
	}

	// Validate the confidence score
	evidence := best.Evidence
	score := er.scorer.ComputeConfidence(evidence)
	validation := er.validator.ValidateScore(score)

	if !validation.Valid {
		return nil
	}

	// Build resolved equivalence
	resolved := &ResolvedEquivalence{
		ID:               uuid.New(),
		SourceItemID:     best.SourceItemID,
		TargetItemID:     targetID,
		LinkType:         best.SuggestedType,
		Confidence:       score.Score,
		Evidence:         evidence,
		ResolutionReason: er.buildResolutionReason(suggestions, best),
		Timestamp:        time.Now(),
	}

	// Determine strategy and status
	if len(best.Strategies) > 0 {
		resolved.SelectedStrategy = best.Strategies[0]
	}

	// Auto-confirm if confidence is very high
	switch validation.Status {
	case "auto_confirm":
		resolved.Status = StatusAuto
		resolved.RequiresReview = false
	case "review_suggested":
		resolved.Status = StatusSuggested
		resolved.RequiresReview = true
	case "review_required":
		resolved.Status = StatusSuggested
		resolved.RequiresReview = true
	}

	return resolved
}

// selectBestSuggestion picks the highest-quality suggestion
func (er *Resolver) selectBestSuggestion(suggestions []Suggestion) *Suggestion {
	if len(suggestions) == 0 {
		return nil
	}

	// Sort by:
	// 1. Confidence (highest first)
	// 2. Number of strategies (more is better - more agreement)
	// 3. Evidence count (more evidence is better)
	sort.Slice(suggestions, func(left, right int) bool {
		// First by confidence
		if suggestions[left].Confidence != suggestions[right].Confidence {
			return suggestions[left].Confidence > suggestions[right].Confidence
		}

		// Then by agreement (more strategies)
		if len(suggestions[left].Strategies) != len(suggestions[right].Strategies) {
			return len(suggestions[left].Strategies) > len(suggestions[right].Strategies)
		}

		// Then by evidence count
		if len(suggestions[left].Evidence) != len(suggestions[right].Evidence) {
			return len(suggestions[left].Evidence) > len(suggestions[right].Evidence)
		}

		// Finally by created time (prefer more recent)
		return suggestions[left].CreatedAt.After(suggestions[right].CreatedAt)
	})

	return &suggestions[0]
}

// groupByTarget groups suggestions by their target item
func (er *Resolver) groupByTarget(suggestions []Suggestion) map[uuid.UUID][]Suggestion {
	byTarget := make(map[uuid.UUID][]Suggestion)
	for _, s := range suggestions {
		byTarget[s.TargetItemID] = append(byTarget[s.TargetItemID], s)
	}
	return byTarget
}

// buildResolutionReason creates a human-readable explanation
func (er *Resolver) buildResolutionReason(
	suggestions []Suggestion,
	selected *Suggestion,
) string {
	if len(suggestions) == 1 {
		return "Single suggestion selected"
	}

	reason := "Selected best match from " + string(rune(len(suggestions))) + " candidates"

	if len(selected.Strategies) > 1 {
		reason += " (confirmed by " + string(rune(len(selected.Strategies))) + " strategies)"
	}

	return reason
}

// ConflictResolver specifically handles conflict detection and resolution
type ConflictResolver struct {
	resolver *Resolver
}

// NewConflictResolver creates a new conflict resolver
func NewConflictResolver() *ConflictResolver {
	return &ConflictResolver{
		resolver: NewEquivalenceResolver(),
	}
}

// DetectConflicts finds conflicting equivalence suggestions
func (cr *ConflictResolver) DetectConflicts(suggestions []Suggestion) []ConflictReport {
	conflicts := make([]ConflictReport, 0, len(suggestions))

	// Group by source item
	bySource := make(map[uuid.UUID][]Suggestion)
	for _, s := range suggestions {
		bySource[s.SourceItemID] = append(bySource[s.SourceItemID], s)
	}

	// Check each source for conflicts
	for sourceID, sourceSuggestions := range bySource {
		sourceConflicts := cr.detectSourceConflicts(sourceID, sourceSuggestions)
		conflicts = append(conflicts, sourceConflicts...)
	}

	return conflicts
}

// detectSourceConflicts detects conflicts for a single source item
func (cr *ConflictResolver) detectSourceConflicts(
	sourceID uuid.UUID,
	suggestions []Suggestion,
) []ConflictReport {
	conflicts := make([]ConflictReport, 0, len(suggestions))

	if len(suggestions) <= 1 {
		return conflicts
	}

	// Find high-confidence suggestions
	highConfidence := make([]Suggestion, 0, len(suggestions))
	for _, s := range suggestions {
		if s.Confidence >= conflictHighConfidenceThreshold {
			highConfidence = append(highConfidence, s)
		}
	}

	// Conflict if 2+ high-confidence suggestions to different targets
	if len(highConfidence) >= conflictHighConfidenceMinCount {
		conflicts = append(conflicts, ConflictReport{
			Type:               "multiple_high_confidence_targets",
			SourceItemID:       sourceID,
			Description:        "Multiple high-confidence equivalences detected for the same source item",
			Suggestions:        highConfidence,
			Severity:           "warning",
			ResolutionRequired: true,
		})
	}

	// Check for circular equivalences (A→B and B→A)
	circularConflicts := cr.detectCircularConflicts(suggestions)
	conflicts = append(conflicts, circularConflicts...)

	return conflicts
}

// detectCircularConflicts detects circular equivalence relationships
func (cr *ConflictResolver) detectCircularConflicts(_ []Suggestion) []ConflictReport {
	conflicts := make([]ConflictReport, 0)

	// This would require access to existing links to detect
	// A→B already exists and we're suggesting B→A
	// For now, structure is in place for future implementation

	return conflicts
}

// ConflictReport describes a detected conflict
type ConflictReport struct {
	Type               string
	SourceItemID       uuid.UUID
	Description        string
	Suggestions        []Suggestion
	Severity           string // info, warning, error
	ResolutionRequired bool
	RecommendedAction  string
	Details            map[string]interface{}
}

// StrategyAgreement represents agreement among strategies
type StrategyAgreement struct {
	Agreement             int // 0-1, how many strategies agree (percentage)
	AgreeingStrategies    []StrategyType
	DisagreeingStrategies []StrategyType
	HighestScore          float64
	LowestScore           float64
	Variance              float64 // Statistical variance
}

// AnalyzeAgreement computes strategy agreement metrics
func (er *Resolver) AnalyzeAgreement(evidence []Evidence) *StrategyAgreement {
	if len(evidence) == 0 {
		return &StrategyAgreement{}
	}

	agreementMap, scores := collectAgreementInputs(evidence)
	mean := meanScore(scores)
	variance := varianceScore(scores, mean)
	highest, lowest := minMaxScore(scores)
	agreement := clampAgreement(1.0 - (variance / agreementVarianceNormalization))

	result := &StrategyAgreement{
		Agreement:          int(agreement * agreementPercentScale),
		AgreeingStrategies: make([]StrategyType, 0),
		HighestScore:       highest,
		LowestScore:        lowest,
		Variance:           variance,
	}

	populateAgreementBuckets(result, agreementMap)

	return result
}

func collectAgreementInputs(evidence []Evidence) (map[StrategyType]float64, []float64) {
	agreementMap := make(map[StrategyType]float64, len(evidence))
	scores := make([]float64, 0, len(evidence))

	for _, ev := range evidence {
		agreementMap[ev.Strategy] = ev.Confidence
		scores = append(scores, ev.Confidence)
	}

	return agreementMap, scores
}

func meanScore(scores []float64) float64 {
	if len(scores) == 0 {
		return 0
	}
	sum := 0.0
	for _, score := range scores {
		sum += score
	}
	return sum / float64(len(scores))
}

func varianceScore(scores []float64, mean float64) float64 {
	if len(scores) == 0 {
		return 0
	}
	variance := 0.0
	for _, score := range scores {
		variance += (score - mean) * (score - mean)
	}
	return variance / float64(len(scores))
}

func minMaxScore(scores []float64) (float64, float64) {
	if len(scores) == 0 {
		return 0, 0
	}
	highest := scores[0]
	lowest := scores[0]
	for _, score := range scores {
		if score > highest {
			highest = score
		}
		if score < lowest {
			lowest = score
		}
	}
	return highest, lowest
}

func clampAgreement(value float64) float64 {
	if value < 0 {
		return 0
	}
	if value > 1 {
		return 1
	}
	return value
}

func populateAgreementBuckets(result *StrategyAgreement, agreementMap map[StrategyType]float64) {
	for strategy, score := range agreementMap {
		if score >= conflictHighConfidenceThreshold {
			result.AgreeingStrategies = append(result.AgreeingStrategies, strategy)
		} else {
			result.DisagreeingStrategies = append(result.DisagreeingStrategies, strategy)
		}
	}
}
