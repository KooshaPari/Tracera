package codeindex

import (
	"context"
	"strings"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/equivalence"
)

const (
	canonicalNameMatchMinConfidence = 0.7
	canonicalEmbeddingSearchLimit   = 5
	canonicalSemanticBaseConfidence = 0.6
	canonicalExactMatchConfidence   = 0.95
	canonicalPartialMatchConfidence = 0.8
	canonicalPrefixSuffixConfidence = 0.75
)

// CanonicalLinker links code entities to canonical concepts
type CanonicalLinker struct {
	codeRepo      Repository
	canonicalRepo CanonicalRepository
	detector      *equivalence.Detector
}

// CanonicalRepository defines the interface for canonical concept storage
type CanonicalRepository interface {
	GetCanonicalConcept(ctx context.Context, id uuid.UUID) (*equivalence.CanonicalConcept, error)
	ListCanonicalConcepts(ctx context.Context, projectID uuid.UUID) ([]equivalence.CanonicalConcept, error)
	SearchByName(ctx context.Context, projectID uuid.UUID, name string) ([]equivalence.CanonicalConcept, error)
	SearchByEmbedding(
		ctx context.Context,
		projectID uuid.UUID,
		embedding []float32,
		limit int,
	) ([]equivalence.CanonicalConcept, error)
	CreateProjection(ctx context.Context, projection *equivalence.CanonicalProjection) error
}

// NewCanonicalLinker creates a new canonical linker
func NewCanonicalLinker(
	codeRepo Repository,
	canonicalRepo CanonicalRepository,
	detector *equivalence.Detector,
) *CanonicalLinker {
	return &CanonicalLinker{
		codeRepo:      codeRepo,
		canonicalRepo: canonicalRepo,
		detector:      detector,
	}
}

// LinkEntityToCanonical attempts to link a code entity to a canonical concept
func (linker *CanonicalLinker) LinkEntityToCanonical(
	ctx context.Context,
	entity *CodeEntity,
) (*LinkResult, error) {
	result := &LinkResult{
		EntityID: entity.ID,
	}

	if linker.applyAnnotationLink(ctx, entity, result) {
		return result, nil
	}

	if err := linker.applyNameLink(ctx, entity, result); err != nil {
		return result, err
	}
	if result.CanonicalID != nil {
		return result, nil
	}

	if linker.applyEmbeddingLink(ctx, entity, result) {
		return result, nil
	}

	return result, nil
}

func (linker *CanonicalLinker) applyAnnotationLink(
	ctx context.Context,
	entity *CodeEntity,
	result *LinkResult,
) bool {
	for _, ann := range entity.Annotations {
		if ann.Name != "canonical" && ann.Name != "trace_implements" {
			continue
		}
		concepts, err := linker.canonicalRepo.SearchByName(ctx, entity.ProjectID, ann.Value)
		if err != nil || len(concepts) == 0 {
			continue
		}
		result.CanonicalID = &concepts[0].ID
		result.Confidence = 1.0
		result.Strategy = "annotation"
		return true
	}
	return false
}

func (linker *CanonicalLinker) applyNameLink(
	ctx context.Context,
	entity *CodeEntity,
	result *LinkResult,
) error {
	concepts, err := linker.canonicalRepo.ListCanonicalConcepts(ctx, entity.ProjectID)
	if err != nil {
		return err
	}
	bestMatch := linker.findBestNameMatch(entity, concepts)
	if bestMatch == nil || bestMatch.Confidence < canonicalNameMatchMinConfidence {
		return nil
	}
	result.CanonicalID = &bestMatch.ConceptID
	result.Confidence = bestMatch.Confidence
	result.Strategy = "naming"
	return nil
}

func (linker *CanonicalLinker) applyEmbeddingLink(
	ctx context.Context,
	entity *CodeEntity,
	result *LinkResult,
) bool {
	if len(entity.Embedding) == 0 {
		return false
	}

	embeddingMatches, err := linker.canonicalRepo.SearchByEmbedding(
		ctx,
		entity.ProjectID,
		entity.Embedding,
		canonicalEmbeddingSearchLimit,
	)
	if err != nil || len(embeddingMatches) == 0 {
		return false
	}

	result.CanonicalID = &embeddingMatches[0].ID
	result.Confidence = canonicalSemanticBaseConfidence
	result.Strategy = "semantic"
	return true
}

// LinkResult represents the result of a canonical linking attempt
type LinkResult struct {
	EntityID    uuid.UUID  `json:"entity_id"`
	CanonicalID *uuid.UUID `json:"canonical_id,omitempty"`
	Confidence  float64    `json:"confidence"`
	Strategy    string     `json:"strategy"`
}

// NameMatch represents a name-based match
type NameMatch struct {
	ConceptID  uuid.UUID
	Confidence float64
}

// findBestNameMatch finds the best canonical concept match by name
func (l *CanonicalLinker) findBestNameMatch(entity *CodeEntity, concepts []equivalence.CanonicalConcept) *NameMatch {
	entityName := normalizeSymbolName(entity.SymbolName)
	var bestMatch *NameMatch

	for _, concept := range concepts {
		match := findConceptNameMatch(entityName, concept)
		if match == nil {
			continue
		}
		if match.Confidence >= canonicalExactMatchConfidence {
			return match
		}
		bestMatch = chooseBetterMatch(bestMatch, match)
	}

	return bestMatch
}

func findConceptNameMatch(entityName string, concept equivalence.CanonicalConcept) *NameMatch {
	conceptName := normalizeSymbolName(concept.Name)

	if entityName == conceptName {
		return &NameMatch{
			ConceptID:  concept.ID,
			Confidence: canonicalExactMatchConfidence,
		}
	}

	if strings.Contains(entityName, conceptName) || strings.Contains(conceptName, entityName) {
		return &NameMatch{
			ConceptID:  concept.ID,
			Confidence: canonicalPartialMatchConfidence,
		}
	}

	if strings.HasPrefix(entityName, conceptName) || strings.HasSuffix(entityName, conceptName) {
		return &NameMatch{
			ConceptID:  concept.ID,
			Confidence: canonicalPrefixSuffixConfidence,
		}
	}

	return nil
}

func chooseBetterMatch(current *NameMatch, candidate *NameMatch) *NameMatch {
	if current == nil {
		return candidate
	}
	if candidate == nil {
		return current
	}
	if candidate.Confidence > current.Confidence {
		return candidate
	}
	return current
}

// normalizeSymbolName normalizes a symbol name for comparison
func normalizeSymbolName(name string) string {
	// Convert to lowercase
	name = strings.ToLower(name)

	// Remove common suffixes
	suffixes := []string{"service", "handler", "controller", "repository", "repo", "manager", "helper", "util", "utils"}
	for _, suffix := range suffixes {
		name = strings.TrimSuffix(name, suffix)
	}

	// Remove common prefixes
	prefixes := []string{"get", "set", "create", "update", "delete", "fetch", "handle"}
	for _, prefix := range prefixes {
		name = strings.TrimPrefix(name, prefix)
	}

	return name
}

// CreateProjection creates a canonical projection for a code entity
func (linker *CanonicalLinker) CreateProjection(
	ctx context.Context,
	entity *CodeEntity,
	canonicalID uuid.UUID,
	confidence float64,
) error {
	projection := &equivalence.CanonicalProjection{
		ID:          uuid.New(),
		CanonicalID: canonicalID,
		ItemID:      entity.ID,
		Perspective: string(entity.Language),
		Confidence:  confidence,
	}

	return linker.canonicalRepo.CreateProjection(ctx, projection)
}
