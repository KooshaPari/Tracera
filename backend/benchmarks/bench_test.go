// Package benchmarks contains performance regression benchmarks for the TraceRTM backend.
// Run with: go test ./benchmarks/... -bench=. -benchmem
package benchmarks

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/equivalence"
)

// BenchmarkNamingStrategyDetect measures naming-similarity detection across candidate pool sizes.
func BenchmarkNamingStrategyDetect(b *testing.B) {
	strategy := equivalence.NewNamingStrategy()
	projectID := uuid.New()

	source := &equivalence.StrategyItemInfo{
		ID:          uuid.New(),
		ProjectID:   projectID,
		Title:       "UserAuthenticationService",
		Description: "Handles user login, logout, and session management.",
		Type:        "service",
		Perspective: "backend",
	}

	sizes := []int{10, 50, 100, 500}
	for _, n := range sizes {
		candidates := make([]*equivalence.StrategyItemInfo, n)
		for i := range candidates {
			candidates[i] = &equivalence.StrategyItemInfo{
				ID:          uuid.New(),
				ProjectID:   projectID,
				Title:       fmt.Sprintf("Candidate%dService", i),
				Description: "A candidate service item.",
				Type:        "service",
				Perspective: "frontend",
			}
		}
		// Insert a strong match roughly in the middle.
		candidates[n/2] = &equivalence.StrategyItemInfo{
			ID:          uuid.New(),
			ProjectID:   projectID,
			Title:       "UserAuthService",
			Description: "Manages user authentication flow.",
			Type:        "service",
			Perspective: "frontend",
		}

		req := &equivalence.StrategyDetectionRequest{
			ProjectID:     projectID,
			SourceItem:    source,
			CandidatePool: candidates,
			MinConfidence: 0.3,
			MaxResults:    50,
		}

		b.Run(fmt.Sprintf("candidates=%d", n), func(b *testing.B) {
			b.ReportAllocs()
			b.ResetTimer()
			for i := 0; i < b.N; i++ {
				_, err := strategy.Detect(context.Background(), req)
				if err != nil {
					b.Fatal(err)
				}
			}
		})
	}
}

// BenchmarkConfidenceScorerCompute measures confidence aggregation under varying evidence counts.
func BenchmarkConfidenceScorerCompute(b *testing.B) {
	scorer := equivalence.NewConfidenceScorer()

	strategyTypes := []equivalence.StrategyType{
		equivalence.StrategyNamingPattern,
		equivalence.StrategyStructural,
		equivalence.StrategySemanticSimilarity,
		equivalence.StrategyAPIContract,
		equivalence.StrategyExplicitAnnotation,
	}

	evidenceCounts := []int{1, 3, 5, 10}
	for _, count := range evidenceCounts {
		evidence := make([]equivalence.Evidence, count)
		for i := range evidence {
			st := strategyTypes[i%len(strategyTypes)]
			evidence[i] = equivalence.Evidence{
				Strategy:    st,
				Confidence:  0.6 + float64(i)*0.03,
				Description: fmt.Sprintf("Matched via %s strategy (signal %d)", st, i),
				DetectedAt:  time.Now(),
			}
		}

		b.Run(fmt.Sprintf("evidence=%d", count), func(b *testing.B) {
			b.ReportAllocs()
			b.ResetTimer()
			for i := 0; i < b.N; i++ {
				scorer.ComputeConfidence(evidence)
			}
		})
	}
}

// BenchmarkConflictReconcilerResolve measures conflict resolution across suggestion sets.
func BenchmarkConflictReconcilerResolve(b *testing.B) {
	reconciler := equivalence.NewConflictReconciler()
	targetID := uuid.New()
	itemID := uuid.New()
	projectID := uuid.New()

	sizes := []int{2, 5, 10}
	for _, n := range sizes {
		suggestions := make([]equivalence.Suggestion, n)
		for i := range suggestions {
			suggestions[i] = equivalence.Suggestion{
				ID:           uuid.New(),
				ProjectID:    projectID,
				SourceItemID: itemID,
				TargetItemID: targetID,
				Confidence:   0.5 + float64(i)*0.04,
				Strategies:   []equivalence.StrategyType{equivalence.StrategyNamingPattern},
				Evidence: []equivalence.Evidence{
					{
						Strategy:    equivalence.StrategyNamingPattern,
						Confidence:  0.7,
						Description: "naming similarity",
						DetectedAt:  time.Now(),
					},
				},
				CreatedAt: time.Now(),
			}
		}

		b.Run(fmt.Sprintf("suggestions=%d", n), func(b *testing.B) {
			b.ReportAllocs()
			b.ResetTimer()
			for i := 0; i < b.N; i++ {
				reconciler.ResolveMultipleMatches(suggestions)
			}
		})
	}
}
