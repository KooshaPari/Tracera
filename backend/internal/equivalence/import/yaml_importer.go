package importer

import (
	"fmt"
	"io"

	"gopkg.in/yaml.v3"

	"github.com/kooshapari/tracertm-backend/internal/equivalence/export"
)

// YAMLImporter imports equivalence data from YAML format
type YAMLImporter struct {
	validator       *Validator
	conflictChecker *ConflictResolver
}

// NewYAMLImporter creates a new YAML importer
func NewYAMLImporter(
	validator *Validator,
	conflictChecker *ConflictResolver,
) *YAMLImporter {
	return &YAMLImporter{
		validator:       validator,
		conflictChecker: conflictChecker,
	}
}

// ParseYAML reads and parses YAML-formatted equivalence data
func (yi *YAMLImporter) ParseYAML(r io.Reader) (*export.Data, error) {
	var data export.Data
	if err := yaml.NewDecoder(r).Decode(&data); err != nil {
		return nil, fmt.Errorf("failed to parse YAML: %w", err)
	}

	return &data, nil
}

// Import validates and prepares YAML data for import
func (yi *YAMLImporter) Import(r io.Reader) (*ImportResult, error) {
	// Parse YAML
	data, err := yi.ParseYAML(r)
	if err != nil {
		return nil, err
	}

	// Validate
	validationErrors := yi.validator.ValidateExportData(data)
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
	conflicts := yi.conflictChecker.DetectConflicts(data)

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
func (yi *YAMLImporter) ImportWithConflictResolution(
	r io.Reader,
	resolution ConflictResolution,
) (*ImportResult, error) {
	// Parse and validate
	result, err := yi.Import(r)
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
		resolved, unresolved, err := yi.conflictChecker.ResolveConflicts(result.ConflictMap, result.Data)
		if err != nil {
			return nil, fmt.Errorf("failed to resolve conflicts: %w", err)
		}

		result.Data = resolved
		result.ResolvedConflicts = unresolved
	}

	return result, nil
}
