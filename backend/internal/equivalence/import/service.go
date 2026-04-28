package importer

import (
	"context"
	"errors"
	"fmt"
	"io"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/equivalence"
	"github.com/kooshapari/tracertm-backend/internal/equivalence/export"
)

// Service handles importing equivalence data
type Service struct {
	conceptRepo    CanonicalConceptRepository
	projectionRepo CanonicalProjectionRepository
	linkRepo       EquivalenceLinkRepository
}

// CanonicalConceptRepository defines methods for managing canonical concepts
type CanonicalConceptRepository interface {
	Create(ctx context.Context, concept *equivalence.CanonicalConcept) error
	Update(ctx context.Context, concept *equivalence.CanonicalConcept) error
	GetByProjectID(ctx context.Context, projectID uuid.UUID) ([]equivalence.CanonicalConcept, error)
	Delete(ctx context.Context, conceptID uuid.UUID) error
}

// CanonicalProjectionRepository defines methods for managing projections
type CanonicalProjectionRepository interface {
	Create(ctx context.Context, projection *equivalence.CanonicalProjection) error
	Update(ctx context.Context, projection *equivalence.CanonicalProjection) error
	GetByProjectID(ctx context.Context, projectID uuid.UUID) ([]equivalence.CanonicalProjection, error)
	Delete(ctx context.Context, projectionID uuid.UUID) error
}

// EquivalenceLinkRepository defines methods for managing equivalence links
type EquivalenceLinkRepository interface {
	Create(ctx context.Context, link *equivalence.Link) error
	Update(ctx context.Context, link *equivalence.Link) error
	GetByProjectID(ctx context.Context, projectID uuid.UUID) ([]equivalence.Link, error)
	Delete(ctx context.Context, linkID uuid.UUID) error
}

// ImportStrategy defines how to handle imports
type ImportStrategy string

const (
	// StrategyReplace replaces existing data during import.
	StrategyReplace ImportStrategy = "replace"
	// StrategyMerge merges imported data with existing data.
	StrategyMerge ImportStrategy = "merge"
	// StrategySkip skips conflicting records during import.
	StrategySkip ImportStrategy = "skip"
)

// ImportOptions configures import behavior
type ImportOptions struct {
	Strategy             ImportStrategy
	PreserveExisting     bool // Keep existing records not in import
	UpdateConfidences    bool // Update confidence scores
	AllowDowngrade       bool // Allow replacing high confidence with low
	ResolveDuplicates    bool // Handle duplicate UUIDs
	ConflictResolution   ConflictResolution
	ValidateReferential  bool // Check referential integrity
	AutoConfirm          bool // Auto-confirm high confidence links
	HighConfidenceThresh float64
}

// importer defines the behavior for format-specific importers
type importer interface {
	ImportWithConflictResolution(r io.Reader, resolution ConflictResolution) (*ImportResult, error)
}

// NewService creates a new import service
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

// ImportJSON imports equivalence data from JSON format
func (service *Service) ImportJSON(
	ctx context.Context,
	projectID uuid.UUID,
	reader io.Reader,
	opts ImportOptions,
) (*ImportResponse, error) {
	return service.importWith(ctx, projectID, reader, opts, "JSON", func(v *Validator, c *ConflictResolver) importer {
		return NewJSONImporter(v, c)
	})
}

// ImportYAML imports equivalence data from YAML format
func (service *Service) ImportYAML(
	ctx context.Context,
	projectID uuid.UUID,
	reader io.Reader,
	opts ImportOptions,
) (*ImportResponse, error) {
	return service.importWith(ctx, projectID, reader, opts, "YAML", func(v *Validator, c *ConflictResolver) importer {
		return NewYAMLImporter(v, c)
	})
}

type importerFactory func(*Validator, *ConflictResolver) importer

func (service *Service) importWith(
	ctx context.Context,
	projectID uuid.UUID,
	reader io.Reader,
	opts ImportOptions,
	format string,
	factory importerFactory,
) (*ImportResponse, error) {
	validator := NewValidator()
	conflictResolver := NewConflictResolver(opts.ConflictResolution)

	// Load existing data for conflict detection
	existing, err := service.linkRepo.GetByProjectID(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to load existing data: %w", err)
	}

	concepts, err := service.conceptRepo.GetByProjectID(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to load existing concepts: %w", err)
	}

	conflictResolver.LoadExisting(concepts, existing)

	importer := factory(validator, conflictResolver)
	result, err := importer.ImportWithConflictResolution(reader, opts.ConflictResolution)
	if err != nil {
		return nil, fmt.Errorf("failed to import %s: %w", format, err)
	}

	if !result.Valid && len(result.Errors) > 0 {
		errs := make([]string, len(result.Errors))
		for i, e := range result.Errors {
			errs[i] = e.Field + ": " + e.Message
		}
		return &ImportResponse{
			Status:              "error",
			ConceptsImported:    0,
			ProjectionsImported: 0,
			LinksImported:       0,
			ConflictsResolved:   0,
			ConflictsUnresolved: 0,
			Errors:              errs,
			Warnings:            nil,
			Summary:             "",
		}, errors.New("validation failed")
	}

	return service.applyImport(ctx, projectID, result.Data, opts)
}

// applyImport applies the validated import to the database
func (service *Service) applyImport(
	ctx context.Context,
	projectID uuid.UUID,
	data *export.Data,
	_ ImportOptions,
) (*ImportResponse, error) {
	response := newImportResponse()

	service.importConcepts(ctx, projectID, data.CanonicalConcepts, response)
	service.importProjections(ctx, projectID, data.Projections, response)
	service.importLinks(ctx, projectID, data.EquivalenceLinks, response)
	setImportSummary(response)

	return response, nil
}

func newImportResponse() *ImportResponse {
	return &ImportResponse{
		Status:              "success",
		ConceptsImported:    0,
		ProjectionsImported: 0,
		LinksImported:       0,
		ConflictsResolved:   0,
		ConflictsUnresolved: 0,
		Errors:              []string{},
		Warnings:            []string{},
		Summary:             "",
	}
}

func (service *Service) importConcepts(
	ctx context.Context,
	projectID uuid.UUID,
	concepts []export.CanonicalConcept,
	response *ImportResponse,
) {
	for _, concept := range concepts {
		if concept.ProjectID != projectID {
			appendProjectMismatchWarning(response, "concept", concept.ID)
			continue
		}

		domainConcept := toDomainConcept(concept)
		if err := service.conceptRepo.Create(ctx, domainConcept); err != nil {
			response.Errors = append(
				response.Errors,
				fmt.Sprintf("failed to import concept %s: %v", concept.ID, err),
			)
			continue
		}
		response.ConceptsImported++
	}
}

func (service *Service) importProjections(
	ctx context.Context,
	projectID uuid.UUID,
	projections []export.CanonicalProjection,
	response *ImportResponse,
) {
	for _, projection := range projections {
		if projection.ProjectID != projectID {
			appendProjectMismatchWarning(response, "projection", projection.ID)
			continue
		}

		domainProjection := toDomainProjection(projection)
		if err := service.projectionRepo.Create(ctx, domainProjection); err != nil {
			response.Errors = append(
				response.Errors,
				fmt.Sprintf("failed to import projection %s: %v", projection.ID, err),
			)
			continue
		}
		response.ProjectionsImported++
	}
}

func (service *Service) importLinks(
	ctx context.Context,
	projectID uuid.UUID,
	links []export.EquivalenceLink,
	response *ImportResponse,
) {
	for _, link := range links {
		if link.ProjectID != projectID {
			appendProjectMismatchWarning(response, "link", link.ID)
			continue
		}

		domainLink := toDomainLink(link)
		if err := service.linkRepo.Create(ctx, domainLink); err != nil {
			response.Errors = append(
				response.Errors,
				fmt.Sprintf("failed to import link %s: %v", link.ID, err),
			)
			continue
		}
		response.LinksImported++
	}
}

func appendProjectMismatchWarning(response *ImportResponse, entity string, id uuid.UUID) {
	response.Warnings = append(response.Warnings, entity+" "+id.String()+" is from different project, skipping")
}

func setImportSummary(response *ImportResponse) {
	if len(response.Errors) > 0 {
		response.Status = "partial"
		response.Summary = fmt.Sprintf(
			"Imported %d concepts, %d projections, %d links with %d errors",
			response.ConceptsImported,
			response.ProjectionsImported,
			response.LinksImported,
			len(response.Errors),
		)
		return
	}

	response.Summary = fmt.Sprintf(
		"Successfully imported %d concepts, %d projections, %d links",
		response.ConceptsImported,
		response.ProjectionsImported,
		response.LinksImported,
	)
}

func toDomainConcept(concept export.CanonicalConcept) *equivalence.CanonicalConcept {
	return &equivalence.CanonicalConcept{
		ID:                concept.ID,
		ProjectID:         concept.ProjectID,
		Name:              concept.Name,
		Slug:              concept.Slug,
		Description:       concept.Description,
		Domain:            concept.Domain,
		Category:          concept.Category,
		Tags:              concept.Tags,
		Embedding:         concept.Embedding,
		EmbeddingModel:    concept.EmbeddingModel,
		ParentConceptID:   concept.ParentConceptID,
		RelatedConceptIDs: concept.RelatedConceptIDs,
		ProjectionCount:   concept.ProjectionCount,
		Confidence:        concept.Confidence,
		Source:            equivalence.StrategyType(concept.Source),
		CreatedBy:         concept.CreatedBy,
		CreatedAt:         concept.CreatedAt,
		UpdatedAt:         concept.UpdatedAt,
		Version:           concept.Version,
	}
}

func toDomainProjection(projection export.CanonicalProjection) *equivalence.CanonicalProjection {
	return &equivalence.CanonicalProjection{
		ID:          projection.ID,
		ProjectID:   projection.ProjectID,
		CanonicalID: projection.CanonicalID,
		ItemID:      projection.ItemID,
		Perspective: projection.Perspective,
		Role:        projection.Role,
		Confidence:  projection.Confidence,
		Provenance:  equivalence.StrategyType(projection.Provenance),
		Status:      equivalence.Status(projection.Status),
		ConfirmedBy: projection.ConfirmedBy,
		ConfirmedAt: projection.ConfirmedAt,
		Metadata:    projection.Metadata,
		CreatedAt:   projection.CreatedAt,
		UpdatedAt:   projection.UpdatedAt,
	}
}

func toDomainLink(link export.EquivalenceLink) *equivalence.Link {
	return &equivalence.Link{
		ID:           link.ID,
		ProjectID:    link.ProjectID,
		SourceItemID: link.SourceItemID,
		TargetItemID: link.TargetItemID,
		CanonicalID:  link.CanonicalID,
		LinkType:     link.LinkType,
		Confidence:   link.Confidence,
		Provenance:   equivalence.StrategyType(link.Provenance),
		Status:       equivalence.Status(link.Status),
		Evidence:     toDomainEvidence(link.Evidence),
		ConfirmedBy:  link.ConfirmedBy,
		ConfirmedAt:  link.ConfirmedAt,
		CreatedAt:    link.CreatedAt,
		UpdatedAt:    link.UpdatedAt,
	}
}

func toDomainEvidence(evidence []export.Evidence) []equivalence.Evidence {
	if len(evidence) == 0 {
		return nil
	}

	domainEvidence := make([]equivalence.Evidence, len(evidence))
	for i, ev := range evidence {
		domainEvidence[i] = equivalence.Evidence{
			Strategy:    equivalence.StrategyType(ev.Strategy),
			Confidence:  ev.Confidence,
			Description: ev.Description,
			Details:     ev.Details,
			DetectedAt:  ev.DetectedAt,
		}
	}

	return domainEvidence
}

// ValidateImportFile validates an import file without applying it
func (service *Service) ValidateImportFile(
	ctx context.Context,
	projectID uuid.UUID,
	reader io.Reader,
	format string,
) (*ImportResult, error) {
	validator := NewValidator()
	conflictResolver := NewConflictResolver(ResolutionSkip)

	// Load existing data
	existing, err := service.linkRepo.GetByProjectID(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to load existing data: %w", err)
	}

	concepts, err := service.conceptRepo.GetByProjectID(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to load existing concepts: %w", err)
	}

	conflictResolver.LoadExisting(concepts, existing)

	// Parse and validate
	switch format {
	case "json":
		importer := NewJSONImporter(validator, conflictResolver)
		return importer.Import(reader)
	case "yaml":
		importer := NewYAMLImporter(validator, conflictResolver)
		return importer.Import(reader)
	default:
		return nil, fmt.Errorf("unsupported format: %s", format)
	}
}
