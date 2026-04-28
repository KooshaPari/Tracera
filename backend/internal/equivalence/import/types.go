package importer

import (
	"github.com/kooshapari/tracertm-backend/internal/equivalence/export"
)

// ImportResult contains the result of an import operation
type ImportResult struct {
	// Valid indicates if the import passed validation
	Valid bool

	// Errors contains validation errors
	Errors []ValidationError

	// Warnings contains non-fatal warnings
	Warnings []ValidationError

	// Data is the parsed and validated import data
	Data *export.Data

	// ConflictMap contains detected conflicts
	ConflictMap []Conflict

	// ResolvedConflicts contains conflicts that were resolved
	ResolvedConflicts []Conflict

	// Summary provides a human-readable summary
	Summary string
}

// ImportResponse is returned when import is complete
type ImportResponse struct {
	// Status indicates the result
	Status string

	// ConceptsImported is the number of concepts imported
	ConceptsImported int

	// ProjectionsImported is the number of projections imported
	ProjectionsImported int

	// LinksImported is the number of links imported
	LinksImported int

	// ConflictsResolved is the number of conflicts resolved
	ConflictsResolved int

	// ConflictsUnresolved is the number of unresolved conflicts
	ConflictsUnresolved int

	// Errors contains any errors that occurred
	Errors []string

	// Warnings contains warnings
	Warnings []string

	// Summary provides a summary of the import
	Summary string
}
