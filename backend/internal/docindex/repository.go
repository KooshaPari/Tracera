package docindex

import (
	"context"

	"github.com/google/uuid"
)

// Repository defines the interface for doc entity storage
type Repository interface {
	// SaveDocEntity saves a documentation entity
	SaveDocEntity(ctx context.Context, entity *DocEntity) error

	// GetDocEntity retrieves a documentation entity by ID
	GetDocEntity(ctx context.Context, id uuid.UUID) (*DocEntity, error)

	// ListDocEntities lists documentation entities for a project
	ListDocEntities(ctx context.Context, projectID uuid.UUID, opts *ListOptions) ([]DocEntity, error)

	// SearchByEmbedding searches doc entities by embedding similarity
	SearchByEmbedding(ctx context.Context, projectID uuid.UUID, embedding []float32, limit int) ([]DocEntity, error)

	// DeleteDocEntity deletes a documentation entity
	DeleteDocEntity(ctx context.Context, id uuid.UUID) error

	// DeleteByDocument deletes all entities for a document
	DeleteByDocument(ctx context.Context, documentID uuid.UUID) error

	// GetDocumentSections retrieves all sections for a document
	GetDocumentSections(ctx context.Context, documentID uuid.UUID) ([]DocEntity, error)

	// GetSectionChunks retrieves all chunks for a section
	GetSectionChunks(ctx context.Context, sectionID uuid.UUID) ([]DocEntity, error)

	// SaveTraceLink saves a traceability link
	SaveTraceLink(ctx context.Context, link *TraceLink) error

	// GetTraceLinks retrieves trace links for a source entity
	GetTraceLinks(ctx context.Context, sourceID uuid.UUID) ([]TraceLink, error)

	// DeleteTraceLink deletes a trace link
	DeleteTraceLink(ctx context.Context, id uuid.UUID) error
}

// ListOptions specifies options for listing doc entities
type ListOptions struct {
	Type          DocEntityType `json:"type,omitempty"`
	FilePath      string        `json:"file_path,omitempty"`
	DocumentID    *uuid.UUID    `json:"document_id,omitempty"`
	Limit         int           `json:"limit,omitempty"`
	Offset        int           `json:"offset,omitempty"`
	IncludeChunks bool          `json:"include_chunks,omitempty"`
}

// SearchOptions specifies options for searching doc entities
type SearchOptions struct {
	Query     string          `json:"query,omitempty"`
	Types     []DocEntityType `json:"types,omitempty"`
	FilePaths []string        `json:"file_paths,omitempty"`
	Limit     int             `json:"limit,omitempty"`
	MinScore  float64         `json:"min_score,omitempty"`
}

// Result represents a search result with score
type Result struct {
	Entity DocEntity `json:"entity"`
	Score  float64   `json:"score"`
}
