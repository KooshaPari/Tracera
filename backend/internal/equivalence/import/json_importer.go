package importer

import (
	"encoding/json"
	"fmt"
	"io"

	"github.com/kooshapari/tracertm-backend/internal/equivalence/export"
)

// JSONImporter imports equivalence data from JSON format
type JSONImporter struct {
	validator       *Validator
	conflictChecker *ConflictResolver
}

// NewJSONImporter creates a new JSON importer
func NewJSONImporter(
	validator *Validator,
	conflictChecker *ConflictResolver,
) *JSONImporter {
	return &JSONImporter{
		validator:       validator,
		conflictChecker: conflictChecker,
	}
}

// ParseJSON reads and parses JSON-formatted equivalence data
func (ji *JSONImporter) ParseJSON(r io.Reader) (*export.Data, error) {
	decoder := json.NewDecoder(r)
	decoder.UseNumber() // Preserve number precision

	var data export.Data
	if err := decoder.Decode(&data); err != nil {
		return nil, fmt.Errorf("failed to parse JSON: %w", err)
	}

	return &data, nil
}

// Import validates and prepares JSON data for import
func (ji *JSONImporter) Import(r io.Reader) (*ImportResult, error) {
	// Parse JSON
	data, err := ji.ParseJSON(r)
	if err != nil {
		return nil, err
	}

	// Validate
	validationErrors := ji.validator.ValidateExportData(data)
	if len(validationErrors) > 0 {
		return &ImportResult{
			Valid:       false,
			Errors:      validationErrors,
			Warnings:    []ValidationError{},
			Data:        nil,
			ConflictMap: nil,
		}, fmt.Errorf("validation failed: %d errors", len(validationErrors))
	}

	// Check for conflicts
	conflicts := ji.conflictChecker.DetectConflicts(data)

	// Convert conflicts to warnings if they're not errors
	warnings := []ValidationError{}
	for _, c := range conflicts {
		if c.Severity != "error" {
			warnings = append(warnings, ValidationError{
				Field:   c.Field,
				Message: c.Message,
			})
		}
	}

	return &ImportResult{
		Valid:       true,
		Errors:      validationErrors,
		Warnings:    warnings,
		Data:        data,
		ConflictMap: conflicts,
	}, nil
}

// ImportWithConflictResolution imports data with conflict resolution applied
func (ji *JSONImporter) ImportWithConflictResolution(
	r io.Reader,
	resolution ConflictResolution,
) (*ImportResult, error) {
	// Parse and validate
	result, err := ji.Import(r)
	if err != nil && !result.Valid {
		return result, err
	}

	// Apply conflict resolution
	if len(result.ConflictMap) > 0 {
		// Update resolution strategy for all conflicts
		for i := range result.ConflictMap {
			result.ConflictMap[i].Resolution = resolution
		}

		// Resolve conflicts
		resolved, unresolved, err := ji.conflictChecker.ResolveConflicts(result.ConflictMap, result.Data)
		if err != nil {
			return nil, fmt.Errorf("failed to resolve conflicts: %w", err)
		}

		result.Data = resolved
		result.ResolvedConflicts = unresolved
	}

	return result, nil
}
