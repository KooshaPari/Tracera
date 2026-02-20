// Package importer handles equivalence import conflict detection and resolution.
package importer

import (
	"fmt"
	"time"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/equivalence"
	"github.com/kooshapari/tracertm-backend/internal/equivalence/export"
)

// ConflictType represents the type of conflict detected
type ConflictType string

const (
	// ConflictConceptExists indicates a canonical concept already exists.
	ConflictConceptExists ConflictType = "concept_exists"
	// ConflictProjectionExists indicates a projection already exists.
	ConflictProjectionExists ConflictType = "projection_exists"
	// ConflictLinkExists indicates a link already exists.
	ConflictLinkExists ConflictType = "link_exists"
	// ConflictConflictingData indicates fields differ between existing and imported data.
	ConflictConflictingData ConflictType = "conflicting_data"
	// ConflictParentNotFound indicates a referenced parent concept is missing.
	ConflictParentNotFound ConflictType = "parent_not_found"
)

// Conflict severity levels
const (
	conflictSeverityError   = "error"
	conflictSeverityWarning = "warning"
	conflictSeverityInfo    = "info"
)

// ConflictResolution represents how to resolve a conflict
type ConflictResolution string

const (
	// ResolutionSkip leaves existing data untouched.
	ResolutionSkip ConflictResolution = "skip"
	// ResolutionReplace overwrites existing data with imported data.
	ResolutionReplace ConflictResolution = "replace"
	// ResolutionMerge merges imported data into existing data.
	ResolutionMerge ConflictResolution = "merge"
)

// Conflict represents a detected conflict during import
type Conflict struct {
	Type        ConflictType
	Severity    string // "error", "warning", "info" - use conflictSeverity* constants
	ItemID      uuid.UUID
	ItemType    string // "concept", "projection", "link"
	Field       string
	Message     string
	ExistingVal interface{}
	ImportedVal interface{}
	Resolution  ConflictResolution
}

// ConflictResolver detects and resolves conflicts during import
type ConflictResolver struct {
	existingConcepts  map[uuid.UUID]*equivalence.CanonicalConcept
	existingLinkIDs   map[uuid.UUID]bool
	defaultResolution ConflictResolution
}

// NewConflictResolver creates a new conflict resolver
func NewConflictResolver(defaultResolution ConflictResolution) *ConflictResolver {
	return &ConflictResolver{
		existingConcepts:  make(map[uuid.UUID]*equivalence.CanonicalConcept),
		existingLinkIDs:   make(map[uuid.UUID]bool),
		defaultResolution: defaultResolution,
	}
}

// LoadExisting loads existing data into the resolver
func (cr *ConflictResolver) LoadExisting(
	concepts []equivalence.CanonicalConcept,
	links []equivalence.Link,
) {
	for i, c := range concepts {
		cr.existingConcepts[c.ID] = &concepts[i]
	}

	for _, l := range links {
		cr.existingLinkIDs[l.ID] = true
	}
}

// DetectConflicts identifies conflicts between imported and existing data
func (cr *ConflictResolver) DetectConflicts(
	importedData *export.Data,
) []Conflict {
	var conflicts []Conflict

	// Check concepts
	for _, concept := range importedData.CanonicalConcepts {
		if existing, exists := cr.existingConcepts[concept.ID]; exists {
			conflict := cr.detectConceptConflict(concept, *existing)
			if conflict != nil {
				conflicts = append(conflicts, *conflict)
			}
		}
	}

	// Check links
	for _, link := range importedData.EquivalenceLinks {
		if cr.existingLinkIDs[link.ID] {
			conflict := &Conflict{
				Type:        ConflictLinkExists,
				Severity:    "warning",
				ItemID:      link.ID,
				ItemType:    "link",
				Message:     "equivalence link already exists",
				ExistingVal: "exists",
				ImportedVal: link.LinkType,
				Resolution:  cr.defaultResolution,
			}
			conflicts = append(conflicts, *conflict)
		}
	}

	return conflicts
}

// detectConceptConflict checks for conflicts in a concept
func (cr *ConflictResolver) detectConceptConflict(
	imported export.CanonicalConcept,
	existing equivalence.CanonicalConcept,
) *Conflict {
	// Check name conflict
	if imported.Name != existing.Name {
		return &Conflict{
			Type:     ConflictConflictingData,
			Severity: "warning",
			ItemID:   imported.ID,
			ItemType: "concept",
			Field:    "name",
			Message: fmt.Sprintf(
				"concept name differs: imported '%s' vs existing '%s'",
				imported.Name,
				existing.Name,
			),
			ExistingVal: existing.Name,
			ImportedVal: imported.Name,
			Resolution:  cr.defaultResolution,
		}
	}

	// Check confidence conflict
	if imported.Confidence != existing.Confidence {
		return &Conflict{
			Type:     ConflictConflictingData,
			Severity: "info",
			ItemID:   imported.ID,
			ItemType: "concept",
			Field:    "confidence",
			Message: fmt.Sprintf(
				"concept confidence differs: imported %.2f vs existing %.2f",
				imported.Confidence,
				existing.Confidence,
			),
			ExistingVal: existing.Confidence,
			ImportedVal: imported.Confidence,
			Resolution:  cr.defaultResolution,
		}
	}

	return nil
}

// ResolveConflicts applies resolutions to conflicts
func (cr *ConflictResolver) ResolveConflicts(
	conflicts []Conflict,
	importedData *export.Data,
) (*export.Data, []Conflict, error) {
	unresolved := []Conflict{}
	resolved := &export.Data{
		Version:           importedData.Version,
		ExportedAt:        importedData.ExportedAt,
		ProjectID:         importedData.ProjectID,
		ProjectName:       importedData.ProjectName,
		Metadata:          importedData.Metadata,
		CanonicalConcepts: importedData.CanonicalConcepts,
		Projections:       importedData.Projections,
		EquivalenceLinks:  importedData.EquivalenceLinks,
		Statistics:        importedData.Statistics,
	}

	for _, conflict := range conflicts {
		switch conflict.Resolution {
		case ResolutionSkip:
			// Remove the conflicting item
			resolved = cr.removeConflictingItem(resolved, conflict)
			unresolved = append(unresolved, conflict)

		case ResolutionReplace:
			// Replace existing with imported (imported overwrites)
			unresolved = append(unresolved, conflict)

		case ResolutionMerge:
			// Merge the data
			if err := cr.mergeItem(resolved, conflict); err != nil {
				return nil, nil, fmt.Errorf("failed to merge conflict: %w", err)
			}
			unresolved = append(unresolved, conflict)
		}
	}

	return resolved, unresolved, nil
}

// removeConflictingItem removes a conflicting item from resolved data
func (cr *ConflictResolver) removeConflictingItem(data *export.Data, conflict Conflict) *export.Data {
	switch conflict.ItemType {
	case "concept":
		data.CanonicalConcepts = removeConceptByID(data.CanonicalConcepts, conflict.ItemID)

	case "projection":
		data.Projections = removeProjectionByID(data.Projections, conflict.ItemID)

	case "link":
		data.EquivalenceLinks = removeLinkByID(data.EquivalenceLinks, conflict.ItemID)
	}

	return data
}

func removeConceptByID(
	concepts []export.CanonicalConcept,
	conceptID uuid.UUID,
) []export.CanonicalConcept {
	filtered := make([]export.CanonicalConcept, 0, len(concepts))
	for _, concept := range concepts {
		if concept.ID != conceptID {
			filtered = append(filtered, concept)
		}
	}
	return filtered
}

func removeProjectionByID(
	projections []export.CanonicalProjection,
	projectionID uuid.UUID,
) []export.CanonicalProjection {
	filtered := make([]export.CanonicalProjection, 0, len(projections))
	for _, projection := range projections {
		if projection.ID != projectionID {
			filtered = append(filtered, projection)
		}
	}
	return filtered
}

func removeLinkByID(
	links []export.EquivalenceLink,
	linkID uuid.UUID,
) []export.EquivalenceLink {
	filtered := make([]export.EquivalenceLink, 0, len(links))
	for _, link := range links {
		if link.ID != linkID {
			filtered = append(filtered, link)
		}
	}
	return filtered
}

// mergeItem applies merge strategy to a conflicting item
func (cr *ConflictResolver) mergeItem(data *export.Data, conflict Conflict) error {
	switch conflict.ItemType {
	case "concept":
		cr.mergeConcept(data, conflict)
	case "projection":
		cr.mergeProjection(data, conflict)
	case "link":
		cr.mergeLink(data, conflict)
	}
	return nil
}

// mergeConcept merges a concept conflict
func (cr *ConflictResolver) mergeConcept(data *export.Data, conflict Conflict) {
	index, ok := findConceptIndex(data.CanonicalConcepts, conflict.ItemID)
	if !ok {
		return
	}
	if conflict.Field == "confidence" && conflict.ImportedVal != conflict.ExistingVal {
		if updated, ok := higherConfidence(conflict.ImportedVal, conflict.ExistingVal); ok {
			data.CanonicalConcepts[index].Confidence = updated
		}
	}
	data.CanonicalConcepts[index].UpdatedAt = time.Now()
}

// mergeProjection merges a projection conflict
func (cr *ConflictResolver) mergeProjection(data *export.Data, conflict Conflict) {
	index, ok := findProjectionIndex(data.Projections, conflict.ItemID)
	if !ok {
		return
	}
	data.Projections[index].UpdatedAt = time.Now()
}

// mergeLink merges a link conflict
func (cr *ConflictResolver) mergeLink(data *export.Data, conflict Conflict) {
	index, ok := findLinkIndex(data.EquivalenceLinks, conflict.ItemID)
	if !ok {
		return
	}
	if conflict.Field == "confidence" {
		if updated, ok := higherConfidence(conflict.ImportedVal, conflict.ExistingVal); ok {
			data.EquivalenceLinks[index].Confidence = updated
		}
	}
	data.EquivalenceLinks[index].UpdatedAt = time.Now()
}

func higherConfidence(importedVal any, existingVal any) (float64, bool) {
	importedConf, ok := importedVal.(float64)
	if !ok {
		return 0, false
	}
	existingConf, ok := existingVal.(float64)
	if !ok {
		return 0, false
	}
	if importedConf <= existingConf {
		return 0, false
	}
	return importedConf, true
}

func findConceptIndex(concepts []export.CanonicalConcept, id uuid.UUID) (int, bool) {
	for i, concept := range concepts {
		if concept.ID == id {
			return i, true
		}
	}
	return 0, false
}

func findProjectionIndex(projections []export.CanonicalProjection, id uuid.UUID) (int, bool) {
	for i, projection := range projections {
		if projection.ID == id {
			return i, true
		}
	}
	return 0, false
}

func findLinkIndex(links []export.EquivalenceLink, id uuid.UUID) (int, bool) {
	for i, link := range links {
		if link.ID == id {
			return i, true
		}
	}
	return 0, false
}

// SummarizeConflicts returns a human-readable summary of conflicts
func SummarizeConflicts(conflicts []Conflict) string {
	if len(conflicts) == 0 {
		return "No conflicts detected"
	}

	errorCount := 0
	warningCount := 0
	infoCount := 0

	for _, c := range conflicts {
		switch c.Severity {
		case conflictSeverityError:
			errorCount++
		case conflictSeverityWarning:
			warningCount++
		case conflictSeverityInfo:
			infoCount++
		}
	}

	return fmt.Sprintf("Conflicts: %d errors, %d warnings, %d info", errorCount, warningCount, infoCount)
}
