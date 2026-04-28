package export

import (
	"context"
	"fmt"
	"io"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/equivalence"
)

// Service handles exporting equivalence data
type Service struct {
	conceptRepo    CanonicalConceptRepository
	projectionRepo CanonicalProjectionRepository
	linkRepo       EquivalenceLinkRepository
}

// CanonicalConceptRepository defines methods for accessing canonical concepts
type CanonicalConceptRepository interface {
	GetByProjectID(ctx context.Context, projectID uuid.UUID) ([]equivalence.CanonicalConcept, error)
	GetByProjectIDWithFilter(
		ctx context.Context,
		projectID uuid.UUID,
		filter ConceptFilter,
	) ([]equivalence.CanonicalConcept, error)
}

// CanonicalProjectionRepository defines methods for accessing projections
type CanonicalProjectionRepository interface {
	GetByProjectID(ctx context.Context, projectID uuid.UUID) ([]equivalence.CanonicalProjection, error)
	GetByProjectIDWithFilter(
		ctx context.Context,
		projectID uuid.UUID,
		filter ProjectionFilter,
	) ([]equivalence.CanonicalProjection, error)
}

// EquivalenceLinkRepository defines methods for accessing equivalence links
type EquivalenceLinkRepository interface {
	GetByProjectID(ctx context.Context, projectID uuid.UUID) ([]equivalence.Link, error)
	GetByProjectIDWithFilter(ctx context.Context, projectID uuid.UUID, filter LinkFilter) ([]equivalence.Link, error)
}

// ConceptFilter provides filtering options for canonical concepts
type ConceptFilter struct {
	Domain        string
	Category      string
	Tags          []string
	OnlyConfirmed bool
}

// ProjectionFilter provides filtering options for projections
type ProjectionFilter struct {
	Perspective   string
	Status        equivalence.Status
	OnlyConfirmed bool
}

// LinkFilter provides filtering options for equivalence links
type LinkFilter struct {
	LinkType      string
	Status        equivalence.Status
	MinConfidence float64
	OnlyConfirmed bool
}

// Options configures export behavior.
type Options struct {
	Format            Format
	IncludeEmbeddings bool
	IncludeMetadata   bool
	IncludeItemInfo   bool
	ConceptFilter     *ConceptFilter
	ProjectionFilter  *ProjectionFilter
	LinkFilter        *LinkFilter
	Pretty            bool
}

// NewService creates a new export service
func NewService(
	conceptRepo CanonicalConceptRepository,
	projectionRepo CanonicalProjectionRepository,
	linkRepo EquivalenceLinkRepository,
) *Service {
	return &Service{
		conceptRepo:    conceptRepo,
		projectionRepo: projectionRepo,
		linkRepo:       linkRepo,
	}
}

// Export exports equivalence data based on options
func (service *Service) Export(
	ctx context.Context,
	projectID uuid.UUID,
	projectName string,
	writer io.Writer,
	opts Options,
) error {
	// Fetch concepts
	var concepts []equivalence.CanonicalConcept
	var err error

	if opts.ConceptFilter != nil {
		concepts, err = service.conceptRepo.GetByProjectIDWithFilter(ctx, projectID, *opts.ConceptFilter)
	} else {
		concepts, err = service.conceptRepo.GetByProjectID(ctx, projectID)
	}
	if err != nil {
		return fmt.Errorf("failed to fetch concepts: %w", err)
	}

	// Fetch projections
	var projections []equivalence.CanonicalProjection
	if opts.ProjectionFilter != nil {
		projections, err = service.projectionRepo.GetByProjectIDWithFilter(ctx, projectID, *opts.ProjectionFilter)
	} else {
		projections, err = service.projectionRepo.GetByProjectID(ctx, projectID)
	}
	if err != nil {
		return fmt.Errorf("failed to fetch projections: %w", err)
	}

	// Fetch links
	var links []equivalence.Link
	if opts.LinkFilter != nil {
		links, err = service.linkRepo.GetByProjectIDWithFilter(ctx, projectID, *opts.LinkFilter)
	} else {
		links, err = service.linkRepo.GetByProjectID(ctx, projectID)
	}
	if err != nil {
		return fmt.Errorf("failed to fetch links: %w", err)
	}

	// Export based on format
	switch opts.Format {
	case FormatJSON:
		exporter := NewJSONExporter(
			WithEmbeddings(opts.IncludeEmbeddings),
			WithMetadata(opts.IncludeMetadata),
			WithPrettyPrint(opts.Pretty),
		)
		return exporter.Export(writer, concepts, projections, links, projectID, projectName)

	case FormatYAML:
		exporter := NewYAMLExporter(
			WithYAMLEmbeddings(opts.IncludeEmbeddings),
			WithYAMLMetadata(opts.IncludeMetadata),
		)
		return exporter.Export(writer, concepts, projections, links, projectID, projectName)

	default:
		return fmt.Errorf("unsupported export format: %s", opts.Format)
	}
}

// Statistics returns statistics about the project's equivalence data without exporting
func (service *Service) Statistics(
	ctx context.Context,
	projectID uuid.UUID,
) (Statistics, error) {
	// Fetch all data
	concepts, err := service.conceptRepo.GetByProjectID(ctx, projectID)
	if err != nil {
		return Statistics{}, fmt.Errorf("failed to fetch concepts: %w", err)
	}

	projections, err := service.projectionRepo.GetByProjectID(ctx, projectID)
	if err != nil {
		return Statistics{}, fmt.Errorf("failed to fetch projections: %w", err)
	}

	links, err := service.linkRepo.GetByProjectID(ctx, projectID)
	if err != nil {
		return Statistics{}, fmt.Errorf("failed to fetch links: %w", err)
	}

	// Calculate statistics
	return calculateStatistics(concepts, projections, links), nil
}

// calculateStatistics computes statistics about the data
func calculateStatistics(
	concepts []equivalence.CanonicalConcept,
	projections []equivalence.CanonicalProjection,
	links []equivalence.Link,
) Statistics {
	stats := Statistics{
		CanonicalConceptCount: len(concepts),
		ProjectionCount:       len(projections),
		EquivalenceLinkCount:  len(links),
		StrategyBreakdown:     make(map[string]int),
		DomainBreakdown:       make(map[string]int),
	}

	// Count statuses and strategies
	totalConfidence := 0.0
	perspectiveSet := make(map[string]bool)

	for _, link := range links {
		switch link.Status {
		case equivalence.StatusConfirmed:
			stats.ConfirmedCount++
		case equivalence.StatusSuggested:
			stats.SuggestedCount++
		case equivalence.StatusRejected:
			stats.RejectedCount++
		case equivalence.StatusAuto:
			stats.ConfirmedCount++
		}

		stats.StrategyBreakdown[string(link.Provenance)]++
		totalConfidence += link.Confidence
	}

	// Count perspectives
	for _, proj := range projections {
		perspectiveSet[proj.Perspective] = true
	}
	stats.PerspectiveCount = len(perspectiveSet)

	// Calculate average confidence
	if len(links) > 0 {
		stats.AverageConfidence = totalConfidence / float64(len(links))
	}

	// Count domains
	for _, concept := range concepts {
		if concept.Domain != "" {
			stats.DomainBreakdown[concept.Domain]++
		}
	}

	return stats
}
