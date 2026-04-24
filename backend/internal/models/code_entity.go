// Package models defines database models.
package models

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/datatypes"
	"gorm.io/gorm"
)

// CodeEntity represents an indexed code entity (class, function, module, etc.)
type CodeEntity struct {
	ID            string         `gorm:"primaryKey" json:"id"`
	ProjectID     string         `json:"project_id"`
	EntityType    string         `gorm:"column:symbol_type" json:"entity_type"` // class, function, method, module, interface, etc.
	Name          string         `gorm:"column:symbol_name" json:"name"`
	FullName      string         `gorm:"column:qualified_name" json:"full_name"` // Fully qualified name
	Description   string         `gorm:"column:docstring" json:"description"`
	FilePath      string         `gorm:"column:file_path" json:"file_path"`
	LineNumber    int            `gorm:"column:start_line" json:"line_number"`
	EndLineNumber int            `gorm:"column:end_line" json:"end_line_number"`
	ColumnNumber  int            `gorm:"column:start_column" json:"column_number"`
	CodeSnippet   string         `gorm:"-" json:"code_snippet"` // Not in database schema
	Language      string         `json:"language"`              // go, python, typescript, etc.
	Signature     string         `json:"signature"`             // Function/method signature
	ReturnType    string         `gorm:"-" json:"return_type"`  // Not in database schema
	Parameters    datatypes.JSON `gorm:"-" json:"parameters"`   // Not in database schema (JSON array of parameters)
	Metadata      datatypes.JSON `json:"metadata"`
	IndexedAt     time.Time      `json:"indexed_at"`
	CreatedAt     time.Time      `json:"created_at"`
	UpdatedAt     time.Time      `json:"updated_at"`
	DeletedAt     *time.Time     `json:"deleted_at,omitempty"`
}

// CodeEntityRelationship represents relationships between code entities
type CodeEntityRelationship struct {
	ID           string         `gorm:"primaryKey" json:"id"`
	ProjectID    string         `json:"project_id"`
	SourceID     string         `json:"source_id"`     // CodeEntity ID
	TargetID     string         `json:"target_id"`     // CodeEntity ID
	RelationType string         `json:"relation_type"` // calls, inherits, implements, uses, etc.
	Metadata     datatypes.JSON `json:"metadata"`
	CreatedAt    time.Time      `json:"created_at"`
	UpdatedAt    time.Time      `json:"updated_at"`
}

// CodeIndexStats represents statistics about code indexing
type CodeIndexStats struct {
	ProjectID          string           `json:"project_id"`
	TotalEntities      int64            `json:"total_entities"`
	EntitiesByType     map[string]int64 `json:"entities_by_type"`
	EntitiesByLanguage map[string]int64 `json:"entities_by_language"`
	LastIndexedAt      time.Time        `json:"last_indexed_at"`
	TotalRelations     int64            `json:"total_relations"`
	UpdatedAt          time.Time        `json:"updated_at"`
}

// BeforeCreate hook to generate UUID (signature must be BeforeCreate(*gorm.DB) error for GORM)
func (ce *CodeEntity) BeforeCreate(_ *gorm.DB) error {
	if ce.ID == "" {
		ce.ID = uuid.New().String()
	}
	if ce.IndexedAt.IsZero() {
		ce.IndexedAt = time.Now()
	}
	return nil
}

// BeforeCreate generates a UUID for CodeEntityRelationship.ID if not set.
func (cer *CodeEntityRelationship) BeforeCreate(_ *gorm.DB) error {
	if cer.ID == "" {
		cer.ID = uuid.New().String()
	}
	return nil
}
