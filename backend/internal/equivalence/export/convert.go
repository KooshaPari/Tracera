// Package export provides serializers for equivalence export formats.
package export

import "github.com/kooshapari/tracertm-backend/internal/equivalence"

func convertConcepts(
	concepts []equivalence.CanonicalConcept,
	includeEmbeddings bool,
) []CanonicalConcept {
	result := make([]CanonicalConcept, 0, len(concepts))

	for _, concept := range concepts {
		export := CanonicalConcept{
			ID:                concept.ID,
			ProjectID:         concept.ProjectID,
			Name:              concept.Name,
			Slug:              concept.Slug,
			Description:       concept.Description,
			Domain:            concept.Domain,
			Category:          concept.Category,
			Tags:              concept.Tags,
			ParentConceptID:   concept.ParentConceptID,
			RelatedConceptIDs: concept.RelatedConceptIDs,
			ProjectionCount:   concept.ProjectionCount,
			Confidence:        concept.Confidence,
			Source:            string(concept.Source),
			CreatedBy:         concept.CreatedBy,
			CreatedAt:         concept.CreatedAt,
			UpdatedAt:         concept.UpdatedAt,
			Version:           concept.Version,
		}

		if includeEmbeddings && len(concept.Embedding) > 0 {
			export.Embedding = concept.Embedding
			export.EmbeddingModel = concept.EmbeddingModel
		}

		result = append(result, export)
	}

	return result
}

func convertProjections(
	projections []equivalence.CanonicalProjection,
	includeMetadata bool,
) []CanonicalProjection {
	result := make([]CanonicalProjection, 0, len(projections))

	for _, projection := range projections {
		export := CanonicalProjection{
			ID:          projection.ID,
			ProjectID:   projection.ProjectID,
			CanonicalID: projection.CanonicalID,
			ItemID:      projection.ItemID,
			Perspective: projection.Perspective,
			Role:        projection.Role,
			Confidence:  projection.Confidence,
			Provenance:  string(projection.Provenance),
			Status:      string(projection.Status),
			ConfirmedBy: projection.ConfirmedBy,
			ConfirmedAt: projection.ConfirmedAt,
			CreatedAt:   projection.CreatedAt,
			UpdatedAt:   projection.UpdatedAt,
		}

		if includeMetadata && len(projection.Metadata) > 0 {
			export.Metadata = projection.Metadata
		}

		result = append(result, export)
	}

	return result
}
