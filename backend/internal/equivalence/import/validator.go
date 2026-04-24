package importer

import (
	"fmt"
	"strings"
	"time"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/equivalence/export"
)

const (
	defaultMaxConceptName = 255
	defaultMaxProjections = 100000
	defaultMaxLinks       = 100000
)

// ValidationError represents a validation error with context
type ValidationError struct {
	Field   string
	Message string
	Index   int // For array items
}

// Validator validates imported equivalence data
type Validator struct {
	allowFutureDates bool
	maxConceptName   int
	maxProjections   int
	maxLinks         int
}

// NewValidator creates a new validator
func NewValidator() *Validator {
	return &Validator{
		allowFutureDates: false,
		maxConceptName:   defaultMaxConceptName,
		maxProjections:   defaultMaxProjections,
		maxLinks:         defaultMaxLinks,
	}
}

func (validator *Validator) validateHeader(data *export.Data) []ValidationError {
	errors := make(
		[]ValidationError,
		0,
		len(data.CanonicalConcepts)+len(data.Projections)+len(data.EquivalenceLinks),
	)

	if data.Version == "" {
		errors = append(errors, ValidationError{
			Field:   "version",
			Message: "version is required",
		})
	} else if !validator.isCompatibleVersion(data.Version) {
		errors = append(errors, ValidationError{
			Field:   "version",
			Message: "version " + data.Version + " is not supported",
		})
	}

	if data.ProjectID == uuid.Nil {
		errors = append(errors, ValidationError{
			Field:   "project_id",
			Message: "project_id is required",
		})
	}

	if data.ExportedAt.IsZero() {
		errors = append(errors, ValidationError{
			Field:   "exported_at",
			Message: "exported_at is required",
		})
	} else if !validator.allowFutureDates && data.ExportedAt.After(time.Now().Add(1*time.Minute)) {
		errors = append(errors, ValidationError{
			Field:   "exported_at",
			Message: "exported_at cannot be in the future",
		})
	}

	return errors
}

func (validator *Validator) validateConcepts(concepts []export.CanonicalConcept) []ValidationError {
	errors := make([]ValidationError, 0, len(concepts))
	for index, concept := range concepts {
		if errs := validator.validateConcept(concept, index); len(errs) > 0 {
			errors = append(errors, errs...)
		}
	}
	return errors
}

func (validator *Validator) validateProjections(projections []export.CanonicalProjection) []ValidationError {
	errors := make([]ValidationError, 0, len(projections))
	for index, projection := range projections {
		if errs := validator.validateProjection(projection, index); len(errs) > 0 {
			errors = append(errors, errs...)
		}
	}
	return errors
}

func (validator *Validator) validateLinks(links []export.EquivalenceLink) []ValidationError {
	errors := make([]ValidationError, 0, len(links))
	for index, link := range links {
		if errs := validator.validateLink(link, index); len(errs) > 0 {
			errors = append(errors, errs...)
		}
	}
	return errors
}

// ValidateExportData validates the structure and content of export data
func (validator *Validator) ValidateExportData(data *export.Data) []ValidationError {
	// Validate basic structure
	if data == nil {
		return []ValidationError{
			{Field: "root", Message: "export data is nil"},
		}
	}

	errors := make(
		[]ValidationError,
		0,
		len(data.CanonicalConcepts)+len(data.Projections)+len(data.EquivalenceLinks)+4,
	)
	errors = append(errors, validator.validateHeader(data)...)
	errors = append(errors, validator.validateConcepts(data.CanonicalConcepts)...)
	errors = append(errors, validator.validateProjections(data.Projections)...)
	errors = append(errors, validator.validateLinks(data.EquivalenceLinks)...)
	errors = append(errors, validator.validateReferentialIntegrity(data)...)
	return errors
}

// validateConcept validates a single canonical concept
func (validator *Validator) validateConcept(concept export.CanonicalConcept, index int) []ValidationError {
	var errors []ValidationError

	if concept.ID == uuid.Nil {
		errors = append(errors, ValidationError{
			Field:   "id",
			Message: "concept id is required",
			Index:   index,
		})
	}

	if strings.TrimSpace(concept.Name) == "" {
		errors = append(errors, ValidationError{
			Field:   "name",
			Message: "concept name is required",
			Index:   index,
		})
	} else if len(concept.Name) > validator.maxConceptName {
		errors = append(errors, ValidationError{
			Field:   "name",
			Message: fmt.Sprintf("concept name exceeds max length of %d", validator.maxConceptName),
			Index:   index,
		})
	}

	if strings.TrimSpace(concept.Slug) == "" {
		errors = append(errors, ValidationError{
			Field:   "slug",
			Message: "concept slug is required",
			Index:   index,
		})
	}

	if concept.Confidence < 0 || concept.Confidence > 1.0 {
		errors = append(errors, ValidationError{
			Field:   "confidence",
			Message: "confidence must be between 0 and 1",
			Index:   index,
		})
	}

	if strings.TrimSpace(concept.Source) == "" {
		errors = append(errors, ValidationError{
			Field:   "source",
			Message: "concept source is required",
			Index:   index,
		})
	}

	if concept.CreatedAt.IsZero() {
		errors = append(errors, ValidationError{
			Field:   "created_at",
			Message: "concept created_at is required",
			Index:   index,
		})
	}

	return errors
}

// validateProjection validates a single projection
func (validator *Validator) validateProjection(proj export.CanonicalProjection, index int) []ValidationError {
	var errors []ValidationError

	if proj.ID == uuid.Nil {
		errors = append(errors, ValidationError{
			Field:   "id",
			Message: "projection id is required",
			Index:   index,
		})
	}

	if proj.CanonicalID == uuid.Nil {
		errors = append(errors, ValidationError{
			Field:   "canonical_id",
			Message: "projection canonical_id is required",
			Index:   index,
		})
	}

	if proj.ItemID == uuid.Nil {
		errors = append(errors, ValidationError{
			Field:   "item_id",
			Message: "projection item_id is required",
			Index:   index,
		})
	}

	if strings.TrimSpace(proj.Perspective) == "" {
		errors = append(errors, ValidationError{
			Field:   "perspective",
			Message: "projection perspective is required",
			Index:   index,
		})
	}

	if proj.Confidence < 0 || proj.Confidence > 1.0 {
		errors = append(errors, ValidationError{
			Field:   "confidence",
			Message: "projection confidence must be between 0 and 1",
			Index:   index,
		})
	}

	if strings.TrimSpace(proj.Provenance) == "" {
		errors = append(errors, ValidationError{
			Field:   "provenance",
			Message: "projection provenance is required",
			Index:   index,
		})
	}

	if proj.CreatedAt.IsZero() {
		errors = append(errors, ValidationError{
			Field:   "created_at",
			Message: "projection created_at is required",
			Index:   index,
		})
	}

	return errors
}

// validateLink validates a single equivalence link
func (validator *Validator) validateLink(link export.EquivalenceLink, index int) []ValidationError {
	errors := validateLinkBaseFields(link, index)
	return append(errors, validateLinkEvidence(link, index)...)
}

func validateLinkBaseFields(link export.EquivalenceLink, index int) []ValidationError {
	var errors []ValidationError

	if link.ID == uuid.Nil {
		errors = appendValidationError(errors, "id", "link id is required", index)
	}

	if link.SourceItemID == uuid.Nil {
		errors = appendValidationError(errors, "source_item_id", "link source_item_id is required", index)
	}

	if link.TargetItemID == uuid.Nil {
		errors = appendValidationError(errors, "target_item_id", "link target_item_id is required", index)
	}

	if strings.TrimSpace(link.LinkType) == "" {
		errors = appendValidationError(errors, "link_type", "link link_type is required", index)
	}

	if link.Confidence < 0 || link.Confidence > 1.0 {
		errors = appendValidationError(errors, "confidence", "link confidence must be between 0 and 1", index)
	}

	if strings.TrimSpace(link.Provenance) == "" {
		errors = appendValidationError(errors, "provenance", "link provenance is required", index)
	}

	if link.CreatedAt.IsZero() {
		errors = appendValidationError(errors, "created_at", "link created_at is required", index)
	}

	return errors
}

func validateLinkEvidence(link export.EquivalenceLink, index int) []ValidationError {
	var errors []ValidationError

	for evidenceIndex, ev := range link.Evidence {
		if strings.TrimSpace(ev.Strategy) == "" {
			errors = appendValidationError(
				errors,
				fmt.Sprintf("evidence[%d].strategy", evidenceIndex),
				"evidence strategy is required",
				index,
			)
		}
		if ev.Confidence < 0 || ev.Confidence > 1.0 {
			errors = appendValidationError(
				errors,
				fmt.Sprintf("evidence[%d].confidence", evidenceIndex),
				"evidence confidence must be between 0 and 1",
				index,
			)
		}
	}

	return errors
}

func appendValidationError(
	errors []ValidationError,
	field string,
	message string,
	index int,
) []ValidationError {
	return append(errors, ValidationError{
		Field:   field,
		Message: message,
		Index:   index,
	})
}

func buildConceptMap(concepts []export.CanonicalConcept) map[uuid.UUID]struct{} {
	conceptMap := make(map[uuid.UUID]struct{}, len(concepts))
	for _, concept := range concepts {
		conceptMap[concept.ID] = struct{}{}
	}
	return conceptMap
}

func validateProjectionConceptRefs(
	projections []export.CanonicalProjection,
	conceptMap map[uuid.UUID]struct{},
) []ValidationError {
	var errors []ValidationError
	for index, projection := range projections {
		if _, ok := conceptMap[projection.CanonicalID]; !ok {
			errors = appendValidationError(
				errors,
				"canonical_id",
				"projection references non-existent concept "+projection.CanonicalID.String(),
				index,
			)
		}
	}
	return errors
}

func validateLinkConceptRefs(
	links []export.EquivalenceLink,
	conceptMap map[uuid.UUID]struct{},
) []ValidationError {
	var errors []ValidationError
	for index, link := range links {
		if link.CanonicalID == nil || *link.CanonicalID == uuid.Nil {
			continue
		}
		if _, ok := conceptMap[*link.CanonicalID]; !ok {
			errors = appendValidationError(
				errors,
				"canonical_id",
				"link references non-existent concept "+link.CanonicalID.String(),
				index,
			)
		}
	}
	return errors
}

func validateConceptHierarchy(
	concepts []export.CanonicalConcept,
	conceptMap map[uuid.UUID]struct{},
) []ValidationError {
	var errors []ValidationError
	for index, concept := range concepts {
		errors = validateParentConceptRef(errors, concept, conceptMap, index)
		errors = validateRelatedConceptRefs(errors, concept, conceptMap, index)
	}
	return errors
}

func validateParentConceptRef(
	errors []ValidationError,
	concept export.CanonicalConcept,
	conceptMap map[uuid.UUID]struct{},
	index int,
) []ValidationError {
	if concept.ParentConceptID == nil || *concept.ParentConceptID == uuid.Nil {
		return errors
	}
	if _, ok := conceptMap[*concept.ParentConceptID]; ok {
		return errors
	}
	return appendValidationError(
		errors,
		"parent_concept_id",
		"concept references non-existent parent "+concept.ParentConceptID.String(),
		index,
	)
}

func validateRelatedConceptRefs(
	errors []ValidationError,
	concept export.CanonicalConcept,
	conceptMap map[uuid.UUID]struct{},
	index int,
) []ValidationError {
	for _, relatedID := range concept.RelatedConceptIDs {
		if _, ok := conceptMap[relatedID]; ok {
			continue
		}
		errors = appendValidationError(
			errors,
			"related_concept_ids",
			"concept references non-existent related concept "+relatedID.String(),
			index,
		)
	}
	return errors
}

// validateReferentialIntegrity checks that references are consistent
func (validator *Validator) validateReferentialIntegrity(data *export.Data) []ValidationError {
	conceptMap := buildConceptMap(data.CanonicalConcepts)

	errors := make([]ValidationError, 0, len(data.Projections)+len(data.EquivalenceLinks)+len(data.CanonicalConcepts))
	errors = append(errors, validateProjectionConceptRefs(data.Projections, conceptMap)...)
	errors = append(errors, validateLinkConceptRefs(data.EquivalenceLinks, conceptMap)...)
	errors = append(errors, validateConceptHierarchy(data.CanonicalConcepts, conceptMap)...)
	return errors
}

// isCompatibleVersion checks if a version is compatible
func (validator *Validator) isCompatibleVersion(version string) bool {
	// For now, support 1.x versions
	return strings.HasPrefix(version, "1.")
}
