package codeindex

import (
	"context"

	"github.com/google/uuid"
)

// Repository defines the interface for code entity storage
type Repository interface {
	// SaveCodeEntity saves a code entity
	SaveCodeEntity(ctx context.Context, entity *CodeEntity) error

	// GetCodeEntity retrieves a code entity by ID
	GetCodeEntity(ctx context.Context, id uuid.UUID) (*CodeEntity, error)

	// ListCodeEntities lists code entities for a project
	ListCodeEntities(ctx context.Context, projectID uuid.UUID, opts *ListOptions) ([]CodeEntity, error)

	// FindByFilePath finds code entities by file path
	FindByFilePath(ctx context.Context, projectID uuid.UUID, filePath string) ([]CodeEntity, error)

	// FindBySymbolName finds code entities by symbol name
	FindBySymbolName(ctx context.Context, projectID uuid.UUID, name string) ([]CodeEntity, error)

	// FindBySymbolType finds code entities by symbol type
	FindBySymbolType(ctx context.Context, projectID uuid.UUID, symType SymbolType) ([]CodeEntity, error)

	// FindByAPIPath finds handlers that match an API path
	FindByAPIPath(ctx context.Context, projectID uuid.UUID, path string) ([]CodeEntity, error)

	// FindByContentHash finds entities by content hash (for change detection)
	FindByContentHash(ctx context.Context, projectID uuid.UUID, hash string) (*CodeEntity, error)

	// SearchByEmbedding searches code entities by embedding similarity
	SearchByEmbedding(ctx context.Context, projectID uuid.UUID, embedding []float32, limit int) ([]CodeEntity, error)

	// DeleteCodeEntity deletes a code entity
	DeleteCodeEntity(ctx context.Context, id uuid.UUID) error

	// DeleteByFilePath deletes all entities for a file
	DeleteByFilePath(ctx context.Context, projectID uuid.UUID, filePath string) error

	// UpdateCanonicalLink updates the canonical concept link for an entity
	UpdateCanonicalLink(ctx context.Context, entityID uuid.UUID, canonicalID *uuid.UUID) error

	// SaveCallChain saves a call chain
	SaveCallChain(ctx context.Context, chain *CallChain) error

	// GetCallChain retrieves a call chain by ID
	GetCallChain(ctx context.Context, id uuid.UUID) (*CallChain, error)

	// ListCallChains lists call chains for a project
	ListCallChains(ctx context.Context, projectID uuid.UUID) ([]CallChain, error)

	// SaveCrossLangRef saves a cross-language reference
	SaveCrossLangRef(ctx context.Context, ref *CrossLangRef) error

	// GetCrossLangRefs retrieves cross-language references for an entity
	GetCrossLangRefs(ctx context.Context, entityID uuid.UUID) ([]CrossLangRef, error)
}

// ListOptions specifies options for listing code entities
type ListOptions struct {
	Language     Language   `json:"language,omitempty"`
	SymbolType   SymbolType `json:"symbol_type,omitempty"`
	FilePath     string     `json:"file_path,omitempty"`
	ModulePath   string     `json:"module_path,omitempty"`
	IsExported   *bool      `json:"is_exported,omitempty"`
	HasCanonical *bool      `json:"has_canonical,omitempty"`
	Limit        int        `json:"limit,omitempty"`
	Offset       int        `json:"offset,omitempty"`
}

// IndexStats represents indexing statistics
type IndexStats struct {
	TotalEntities   int                `json:"total_entities"`
	ByLanguage      map[Language]int   `json:"by_language"`
	BySymbolType    map[SymbolType]int `json:"by_symbol_type"`
	WithCanonical   int                `json:"with_canonical"`
	WithEmbedding   int                `json:"with_embedding"`
	TotalCallChains int                `json:"total_call_chains"`
	CrossLangRefs   int                `json:"cross_lang_refs"`
}
