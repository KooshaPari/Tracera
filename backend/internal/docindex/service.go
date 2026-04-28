package docindex

import (
	"context"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/embeddings"
)

// Service defines the documentation indexing service interface
type Service interface {
	// Index indexes documentation files
	Index(ctx context.Context, req *IndexRequest) (*IndexResult, error)

	// GetDocument retrieves a document with its sections
	GetDocument(ctx context.Context, id uuid.UUID) (*DocEntity, error)

	// ListDocuments lists documents for a project
	ListDocuments(ctx context.Context, projectID uuid.UUID, opts *ListOptions) ([]DocEntity, error)

	// SearchDocuments searches documents by query
	SearchDocuments(ctx context.Context, projectID uuid.UUID, query string, limit int) ([]Result, error)

	// LinkDocToCode creates traceability links for a document
	LinkDocToCode(ctx context.Context, projectID uuid.UUID, docEntityID uuid.UUID) ([]TraceLink, error)

	// GetTraceLinks retrieves trace links for an entity
	GetTraceLinks(ctx context.Context, entityID uuid.UUID) ([]TraceLink, error)

	// DeleteDocument deletes a document and all its entities
	DeleteDocument(ctx context.Context, id uuid.UUID) error

	// ReindexProject re-indexes all documentation for a project
	ReindexProject(ctx context.Context, req *IndexRequest) (*IndexResult, error)
}

// ServiceImpl implements the Service interface
type ServiceImpl struct {
	repo       Repository
	codeRepo   CodeEntityRepository
	indexer    *Indexer
	linker     *Linker
	embeddings embeddings.Provider
}

// NewService creates a new documentation indexing service
func NewService(repo Repository, codeRepo CodeEntityRepository, embeddingProvider embeddings.Provider) Service {
	indexer := NewIndexer(repo, embeddingProvider)
	linker := NewLinker(repo, codeRepo)

	return &ServiceImpl{
		repo:       repo,
		codeRepo:   codeRepo,
		indexer:    indexer,
		linker:     linker,
		embeddings: embeddingProvider,
	}
}

// Index indexes documentation files
func (s *ServiceImpl) Index(ctx context.Context, req *IndexRequest) (*IndexResult, error) {
	return s.indexer.Index(ctx, req)
}

// GetDocument retrieves a document with its sections
func (s *ServiceImpl) GetDocument(ctx context.Context, id uuid.UUID) (*DocEntity, error) {
	return s.repo.GetDocEntity(ctx, id)
}

// ListDocuments lists documents for a project
func (s *ServiceImpl) ListDocuments(ctx context.Context, projectID uuid.UUID, opts *ListOptions) ([]DocEntity, error) {
	if opts == nil {
		opts = &ListOptions{
			Type:          DocTypeDocument,
			FilePath:      "",
			DocumentID:    nil,
			Limit:         0,
			Offset:        0,
			IncludeChunks: false,
		}
	} else if opts.Type == "" {
		opts.Type = DocTypeDocument
	}
	return s.repo.ListDocEntities(ctx, projectID, opts)
}

// SearchDocuments searches documents by query using embeddings
func (s *ServiceImpl) SearchDocuments(ctx context.Context, projectID uuid.UUID, query string, limit int) ([]Result, error) {
	if s.embeddings == nil {
		return nil, nil
	}

	// Generate embedding for query
	resp, err := s.embeddings.Embed(ctx, &embeddings.EmbeddingRequest{
		Texts:     []string{query},
		Model:     "",
		InputType: "query",
	})
	if err != nil {
		return nil, err
	}

	if len(resp.Embeddings) == 0 {
		return nil, nil
	}

	// Search by embedding
	entities, err := s.repo.SearchByEmbedding(ctx, projectID, resp.Embeddings[0], limit)
	if err != nil {
		return nil, err
	}

	// Convert to search results (scores would come from the repository)
	results := make([]Result, len(entities))
	for i, entity := range entities {
		results[i] = Result{
			Entity: entity,
			Score:  1.0, // Score would be computed by repository
		}
	}

	return results, nil
}

// LinkDocToCode creates traceability links for a document
func (s *ServiceImpl) LinkDocToCode(ctx context.Context, projectID uuid.UUID, docEntityID uuid.UUID) ([]TraceLink, error) {
	links, err := s.linker.LinkDocToCode(ctx, projectID, docEntityID)
	if err != nil {
		return nil, err
	}

	// Save links
	for i := range links {
		if err := s.repo.SaveTraceLink(ctx, &links[i]); err != nil {
			return nil, err
		}
	}

	return links, nil
}

// GetTraceLinks retrieves trace links for an entity
func (s *ServiceImpl) GetTraceLinks(ctx context.Context, entityID uuid.UUID) ([]TraceLink, error) {
	return s.repo.GetTraceLinks(ctx, entityID)
}

// DeleteDocument deletes a document and all its entities
func (s *ServiceImpl) DeleteDocument(ctx context.Context, id uuid.UUID) error {
	return s.repo.DeleteByDocument(ctx, id)
}

// ReindexProject re-indexes all documentation for a project
func (s *ServiceImpl) ReindexProject(ctx context.Context, req *IndexRequest) (*IndexResult, error) {
	// First, list and delete existing documents
	docs, err := s.repo.ListDocEntities(ctx, req.ProjectID, &ListOptions{
		Type:          DocTypeDocument,
		FilePath:      "",
		DocumentID:    nil,
		Limit:         0,
		Offset:        0,
		IncludeChunks: false,
	})
	if err != nil {
		return nil, err
	}

	for _, doc := range docs {
		if err := s.repo.DeleteByDocument(ctx, doc.ID); err != nil {
			return nil, err
		}
	}

	// Re-index
	return s.indexer.Index(ctx, req)
}
