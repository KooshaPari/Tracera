package codeindex

import (
	"context"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/embeddings"
)

// Service defines the code indexing service interface
type Service interface {
	// Index indexes code files
	Index(ctx context.Context, req *IndexRequest) (*IndexResult, error)

	// GetEntity retrieves a code entity by ID
	GetEntity(ctx context.Context, id uuid.UUID) (*CodeEntity, error)

	// ListEntities lists code entities for a project
	ListEntities(ctx context.Context, projectID uuid.UUID, opts *ListOptions) ([]CodeEntity, error)

	// SearchEntities searches code entities by query
	SearchEntities(ctx context.Context, projectID uuid.UUID, query string, limit int) ([]CodeEntity, error)

	// AnalyzeCallChains analyzes call chains for a project
	AnalyzeCallChains(ctx context.Context, projectID uuid.UUID) ([]CallChain, error)

	// GetCallChain retrieves a specific call chain
	GetCallChain(ctx context.Context, id uuid.UUID) (*CallChain, error)

	// GetCrossLangRefs retrieves cross-language references for an entity
	GetCrossLangRefs(ctx context.Context, entityID uuid.UUID) ([]CrossLangRef, error)

	// HandleWebhook handles a GitHub webhook for incremental sync
	HandleWebhook(ctx context.Context, projectID uuid.UUID, eventType string, payload []byte) (*SyncResult, error)

	// GetStats retrieves indexing statistics for a project
	GetStats(ctx context.Context, projectID uuid.UUID) (*IndexStats, error)

	// DeleteEntity deletes a code entity
	DeleteEntity(ctx context.Context, id uuid.UUID) error

	// ReindexProject re-indexes all code for a project
	ReindexProject(ctx context.Context, req *IndexRequest) (*IndexResult, error)
}

// ServiceImpl implements the Service interface
type ServiceImpl struct {
	repo              Repository
	canonicalRepo     CanonicalRepository
	indexer           *Indexer
	callChainAnalyzer *CallChainAnalyzer
	webhookHandler    *WebhookHandler
	embeddings        embeddings.Provider
}

// NewService creates a new code indexing service
func NewService(
	repo Repository,
	canonicalRepo CanonicalRepository,
	embeddingProvider embeddings.Provider,
	webhookSecret string,
) Service {
	indexer := NewIndexer(repo, canonicalRepo, embeddingProvider)
	callChainAnalyzer := NewCallChainAnalyzer(repo)
	webhookHandler := NewWebhookHandler(indexer, repo, webhookSecret)

	return &ServiceImpl{
		repo:              repo,
		canonicalRepo:     canonicalRepo,
		indexer:           indexer,
		callChainAnalyzer: callChainAnalyzer,
		webhookHandler:    webhookHandler,
		embeddings:        embeddingProvider,
	}
}

// Index indexes code files
func (service *ServiceImpl) Index(ctx context.Context, req *IndexRequest) (*IndexResult, error) {
	return service.indexer.Index(ctx, req)
}

// GetEntity retrieves a code entity by ID
func (service *ServiceImpl) GetEntity(ctx context.Context, id uuid.UUID) (*CodeEntity, error) {
	return service.repo.GetCodeEntity(ctx, id)
}

// ListEntities lists code entities for a project
func (service *ServiceImpl) ListEntities(
	ctx context.Context,
	projectID uuid.UUID,
	opts *ListOptions,
) ([]CodeEntity, error) {
	return service.repo.ListCodeEntities(ctx, projectID, opts)
}

// SearchEntities searches code entities by query using embeddings
func (service *ServiceImpl) SearchEntities(
	ctx context.Context,
	projectID uuid.UUID,
	query string,
	limit int,
) ([]CodeEntity, error) {
	if service.embeddings == nil {
		// Fall back to name search
		return service.repo.FindBySymbolName(ctx, projectID, query)
	}

	// Generate embedding for query
	resp, err := service.embeddings.Embed(ctx, &embeddings.EmbeddingRequest{
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

	return service.repo.SearchByEmbedding(ctx, projectID, resp.Embeddings[0], limit)
}

// AnalyzeCallChains analyzes call chains for a project
func (service *ServiceImpl) AnalyzeCallChains(ctx context.Context, projectID uuid.UUID) ([]CallChain, error) {
	chains, err := service.callChainAnalyzer.AnalyzeAllChains(ctx, projectID)
	if err != nil {
		return nil, err
	}

	// Save chains
	for i := range chains {
		if err := service.repo.SaveCallChain(ctx, &chains[i]); err != nil {
			return nil, err
		}
	}

	return chains, nil
}

// GetCallChain retrieves a specific call chain
func (service *ServiceImpl) GetCallChain(ctx context.Context, id uuid.UUID) (*CallChain, error) {
	return service.repo.GetCallChain(ctx, id)
}

// GetCrossLangRefs retrieves cross-language references for an entity
func (service *ServiceImpl) GetCrossLangRefs(ctx context.Context, entityID uuid.UUID) ([]CrossLangRef, error) {
	return service.repo.GetCrossLangRefs(ctx, entityID)
}

// HandleWebhook handles a GitHub webhook for incremental sync
func (service *ServiceImpl) HandleWebhook(
	ctx context.Context,
	projectID uuid.UUID,
	eventType string,
	payload []byte,
) (*SyncResult, error) {
	if eventType != "push" {
		return nil, nil // Only handle push events
	}
	return service.webhookHandler.HandlePushEvent(ctx, projectID, payload)
}

// GetStats retrieves indexing statistics for a project
func (service *ServiceImpl) GetStats(ctx context.Context, projectID uuid.UUID) (*IndexStats, error) {
	entities, err := service.repo.ListCodeEntities(ctx, projectID, nil)
	if err != nil {
		return nil, err
	}

	stats := &IndexStats{
		TotalEntities: len(entities),
		ByLanguage:    make(map[Language]int),
		BySymbolType:  make(map[SymbolType]int),
	}

	for _, entity := range entities {
		stats.ByLanguage[entity.Language]++
		stats.BySymbolType[entity.SymbolType]++
		if entity.CanonicalID != nil {
			stats.WithCanonical++
		}
		if len(entity.Embedding) > 0 {
			stats.WithEmbedding++
		}
	}

	chains, err := service.repo.ListCallChains(ctx, projectID)
	if err != nil {
		return nil, err
	}
	stats.TotalCallChains = len(chains)

	return stats, nil
}

// DeleteEntity deletes a code entity
func (service *ServiceImpl) DeleteEntity(ctx context.Context, id uuid.UUID) error {
	return service.repo.DeleteCodeEntity(ctx, id)
}

// ReindexProject re-indexes all code for a project
func (service *ServiceImpl) ReindexProject(ctx context.Context, req *IndexRequest) (*IndexResult, error) {
	// Delete all existing entities
	entities, err := service.repo.ListCodeEntities(ctx, req.ProjectID, nil)
	if err != nil {
		return nil, err
	}

	for _, e := range entities {
		if err := service.repo.DeleteCodeEntity(ctx, e.ID); err != nil {
			return nil, err
		}
	}

	// Re-index
	return service.indexer.Index(ctx, req)
}
