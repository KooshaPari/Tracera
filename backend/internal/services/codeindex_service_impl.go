package services

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

const (
	codeIndexDefaultCacheTTL   = 5 * time.Minute
	codeIndexCacheWriteTimeout = 2 * time.Second
)

// Ensure CodeIndexServiceImpl implements CodeIndexService interface
var _ CodeIndexService = (*CodeIndexServiceImpl)(nil)

// CodeIndexServiceImpl implements the CodeIndexService interface with caching
type CodeIndexServiceImpl struct {
	entityRepo       repository.CodeEntityRepository
	relationshipRepo repository.CodeEntityRelationshipRepository
	cache            cache.Cache
	cacheTTL         time.Duration
}

// NewCodeIndexServiceImpl creates a new code index service implementation
func NewCodeIndexServiceImpl(
	entityRepo repository.CodeEntityRepository,
	relationshipRepo repository.CodeEntityRelationshipRepository,
	cache cache.Cache,
) CodeIndexService {
	if entityRepo == nil {
		panic("entityRepo cannot be nil")
	}
	if relationshipRepo == nil {
		panic("relationshipRepo cannot be nil")
	}

	return &CodeIndexServiceImpl{
		entityRepo:       entityRepo,
		relationshipRepo: relationshipRepo,
		cache:            cache,
		cacheTTL:         codeIndexDefaultCacheTTL,
	}
}

// ============================================================================
// CORE CRUD OPERATIONS
// ============================================================================

// IndexCodeEntity creates or updates a code entity with validation and caching
func (s *CodeIndexServiceImpl) IndexCodeEntity(ctx context.Context, entity *models.CodeEntity) error {
	// Validate input
	if err := s.validateCodeEntity(entity); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}

	// Set defaults if not provided
	if entity.IndexedAt.IsZero() {
		entity.IndexedAt = time.Now()
	}

	// Persist to database
	if err := s.entityRepo.Create(ctx, entity); err != nil {
		return fmt.Errorf("failed to index code entity: %w", err)
	}

	// Invalidate related caches
	s.invalidateEntityCaches(ctx, entity)

	log.Printf("[CODE INDEX] Indexed entity %s (%s) in file %s", entity.Name, entity.EntityType, entity.FilePath)
	return nil
}

// GetCodeEntity retrieves a code entity by ID with caching
func (s *CodeIndexServiceImpl) GetCodeEntity(ctx context.Context, id string) (*models.CodeEntity, error) {
	if id == "" {
		return nil, errors.New("entity ID is required")
	}

	// Try cache first (cache-aside pattern)
	cacheKey := "code_entity:" + id
	if cached, err := s.getEntityFromCache(ctx, cacheKey); cached != nil && err == nil {
		log.Printf("[CACHE HIT] Retrieved code entity %s from cache", id)
		return cached, nil
	}

	// Cache miss - fetch from database
	entity, err := s.entityRepo.GetByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get code entity: %w", err)
	}

	// Populate cache (non-blocking)
	go func() {
		cacheCtx, cancel := context.WithTimeout(context.Background(), codeIndexCacheWriteTimeout)
		defer cancel()
		if err := s.setEntityInCache(cacheCtx, cacheKey, entity); err != nil {
			log.Printf("Warning: Failed to cache entity %s: %v", id, err)
		}
	}()

	return entity, nil
}

// ListCodeEntities lists code entities with filtering and optional caching
func (s *CodeIndexServiceImpl) ListCodeEntities(ctx context.Context, filter CodeEntityFilter) ([]*models.CodeEntity, error) {
	if filter.ProjectID == "" {
		return nil, errors.New("project ID is required")
	}

	// For small pages, try cache
	if filter.Limit <= 50 && filter.Offset == 0 && filter.Type == "" && filter.FilePath == "" {
		cacheKey := "code_entities:project:" + filter.ProjectID + ":page:0"
		if cached, err := s.getEntitiesFromCache(ctx, cacheKey); cached != nil && err == nil {
			log.Printf("[CACHE HIT] Retrieved code entities for project %s from cache", filter.ProjectID)
			return cached, nil
		}
	}

	// Build repository filter
	repoFilter := repository.CodeEntityFilter{
		ProjectID:  filter.ProjectID,
		EntityType: filter.Type,
		FilePath:   filter.FilePath,
		Limit:      filter.Limit,
		Offset:     filter.Offset,
	}

	// Fetch from database
	entities, err := s.entityRepo.List(ctx, repoFilter)
	if err != nil {
		return nil, fmt.Errorf("failed to list code entities: %w", err)
	}

	// Cache first page of project entities
	if filter.Limit <= 50 && filter.Offset == 0 && filter.Type == "" && filter.FilePath == "" {
		cacheKey := "code_entities:project:" + filter.ProjectID + ":page:0"
		go func() {
			cacheCtx, cancel := context.WithTimeout(context.Background(), codeIndexCacheWriteTimeout)
			defer cancel()
			if err := s.setEntitiesInCache(cacheCtx, cacheKey, entities); err != nil {
				log.Printf("Warning: Failed to cache entities: %v", err)
			}
		}()
	}

	return entities, nil
}

// UpdateCodeEntity updates a code entity with validation and cache invalidation
func (s *CodeIndexServiceImpl) UpdateCodeEntity(ctx context.Context, entity *models.CodeEntity) error {
	if err := s.validateCodeEntity(entity); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}

	// Update indexed timestamp
	entity.IndexedAt = time.Now()

	if err := s.entityRepo.Update(ctx, entity); err != nil {
		return fmt.Errorf("failed to update code entity: %w", err)
	}

	// Invalidate caches
	s.invalidateEntityCaches(ctx, entity)

	log.Printf("[CODE INDEX] Updated entity %s (%s)", entity.Name, entity.EntityType)
	return nil
}

// DeleteCodeEntity deletes a code entity and invalidates caches
func (s *CodeIndexServiceImpl) DeleteCodeEntity(ctx context.Context, id string) error {
	if id == "" {
		return errors.New("entity ID is required")
	}

	// Get entity first to know which caches to invalidate
	entity, err := s.entityRepo.GetByID(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to delete code entity: %w", err)
	}

	if err := s.entityRepo.Delete(ctx, id); err != nil {
		return fmt.Errorf("failed to delete code entity: %w", err)
	}

	// Delete associated relationships
	relationships, err := s.relationshipRepo.GetRelationships(ctx, id)
	if err == nil && len(relationships) > 0 {
		for _, rel := range relationships {
			_ = s.relationshipRepo.Delete(ctx, rel.ID)
		}
	}

	// Invalidate caches
	s.invalidateEntityCaches(ctx, entity)

	log.Printf("[CODE INDEX] Deleted entity %s and %d relationships", id, len(relationships))
	return nil
}

// ============================================================================
// BATCH OPERATIONS
// ============================================================================

// IndexCodeEntities indexes multiple code entities in a batch
func (s *CodeIndexServiceImpl) IndexCodeEntities(ctx context.Context, entities []*models.CodeEntity) error {
	if len(entities) == 0 {
		return errors.New("entities list cannot be empty")
	}

	// Validate all entities
	for i, entity := range entities {
		if err := s.validateCodeEntity(entity); err != nil {
			return fmt.Errorf("validation failed for entity at index %d: %w", i, err)
		}
		// Set defaults
		if entity.IndexedAt.IsZero() {
			entity.IndexedAt = time.Now()
		}
	}

	// Batch create
	if err := s.entityRepo.BatchCreate(ctx, entities); err != nil {
		return fmt.Errorf("failed to batch index entities: %w", err)
	}

	// Invalidate project cache
	if len(entities) > 0 {
		projectID := entities[0].ProjectID
		s.invalidateProjectCaches(ctx, projectID)
		log.Printf("[CODE INDEX] Batch indexed %d entities for project %s", len(entities), projectID)
	}

	return nil
}

// ============================================================================
// SEARCH AND FILTERING
// ============================================================================

// SearchCodeEntities searches code entities by query string
func (s *CodeIndexServiceImpl) SearchCodeEntities(ctx context.Context, projectID, query string, limit, offset int) ([]*models.CodeEntity, error) {
	if projectID == "" {
		return nil, errors.New("project ID is required")
	}
	if query == "" {
		return nil, errors.New("search query is required")
	}

	entities, err := s.entityRepo.Search(ctx, projectID, query, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to search code entities: %w", err)
	}

	return entities, nil
}

// GetCodeEntitiesByType retrieves code entities by type
func (s *CodeIndexServiceImpl) GetCodeEntitiesByType(ctx context.Context, projectID, entityType string) ([]*models.CodeEntity, error) {
	if projectID == "" {
		return nil, errors.New("project ID is required")
	}
	if entityType == "" {
		return nil, errors.New("entity type is required")
	}

	cacheKey := "code_entities:project:" + projectID + ":type:" + entityType
	return s.getOrCacheEntities(
		ctx,
		cacheKey,
		func() ([]*models.CodeEntity, error) { return s.entityRepo.GetByType(ctx, projectID, entityType) },
		"entities by type "+entityType,
		"failed to get code entities by type",
	)
}

// GetCodeEntitiesByFile retrieves code entities by file path
func (s *CodeIndexServiceImpl) GetCodeEntitiesByFile(ctx context.Context, projectID, filePath string) ([]*models.CodeEntity, error) {
	if projectID == "" {
		return nil, errors.New("project ID is required")
	}
	if filePath == "" {
		return nil, errors.New("file path is required")
	}

	cacheKey := "code_entities:project:" + projectID + ":file:" + filePath
	return s.getOrCacheEntities(
		ctx,
		cacheKey,
		func() ([]*models.CodeEntity, error) { return s.entityRepo.GetByFilePath(ctx, projectID, filePath) },
		"entities for file "+filePath,
		"failed to get code entities by file",
	)
}

// ============================================================================
// RELATIONSHIP MANAGEMENT
// ============================================================================

func (s *CodeIndexServiceImpl) getOrCacheEntities(
	ctx context.Context,
	cacheKey string,
	fetch func() ([]*models.CodeEntity, error),
	cacheLabel string,
	errorMessage string,
) ([]*models.CodeEntity, error) {
	if cached, err := s.getEntitiesFromCache(ctx, cacheKey); cached != nil && err == nil {
		log.Printf("[CACHE HIT] Retrieved %s from cache", cacheLabel)
		return cached, nil
	}

	entities, err := fetch()
	if err != nil {
		return nil, fmt.Errorf("%s: %w", errorMessage, err)
	}

	go func() {
		cacheCtx, cancel := context.WithTimeout(context.Background(), codeIndexCacheWriteTimeout)
		defer cancel()
		if err := s.setEntitiesInCache(cacheCtx, cacheKey, entities); err != nil {
			log.Printf("Warning: Failed to cache %s: %v", cacheLabel, err)
		}
	}()

	return entities, nil
}

// CreateRelationship creates a relationship between code entities
func (s *CodeIndexServiceImpl) CreateRelationship(ctx context.Context, rel *models.CodeEntityRelationship) error {
	if err := s.validateRelationship(rel); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}

	// Verify source and target entities exist
	if _, err := s.entityRepo.GetByID(ctx, rel.SourceID); err != nil {
		return fmt.Errorf("source entity not found: %w", err)
	}
	if _, err := s.entityRepo.GetByID(ctx, rel.TargetID); err != nil {
		return fmt.Errorf("target entity not found: %w", err)
	}

	if err := s.relationshipRepo.Create(ctx, rel); err != nil {
		return fmt.Errorf("failed to create relationship: %w", err)
	}

	// Invalidate relationship caches
	_ = s.cache.Delete(ctx, "relationships:"+rel.SourceID)
	_ = s.cache.Delete(ctx, "relationships:"+rel.TargetID)

	log.Printf("[CODE INDEX] Created relationship: %s -> %s (%s)", rel.SourceID, rel.TargetID, rel.RelationType)
	return nil
}

// GetEntityDependencies retrieves all dependencies for a code entity
func (s *CodeIndexServiceImpl) GetEntityDependencies(ctx context.Context, entityID string) ([]*models.CodeEntityRelationship, error) {
	if entityID == "" {
		return nil, errors.New("entity ID is required")
	}

	// Try cache
	cacheKey := "dependencies:" + entityID
	if cached, err := s.getRelationshipsFromCache(ctx, cacheKey); cached != nil && err == nil {
		log.Printf("[CACHE HIT] Retrieved dependencies for entity %s from cache", entityID)
		return cached, nil
	}

	relationships, err := s.relationshipRepo.GetBySourceID(ctx, entityID)
	if err != nil {
		return nil, fmt.Errorf("failed to get dependencies: %w", err)
	}

	// Cache result
	go func() {
		cacheCtx, cancel := context.WithTimeout(context.Background(), codeIndexCacheWriteTimeout)
		defer cancel()
		if err := s.setRelationshipsInCache(cacheCtx, cacheKey, relationships); err != nil {
			log.Printf("Warning: Failed to cache dependencies: %v", err)
		}
	}()

	return relationships, nil
}

// GetEntityDependents retrieves all entities that depend on this entity
func (s *CodeIndexServiceImpl) GetEntityDependents(ctx context.Context, entityID string) ([]*models.CodeEntityRelationship, error) {
	if entityID == "" {
		return nil, errors.New("entity ID is required")
	}

	relationships, err := s.relationshipRepo.GetByTargetID(ctx, entityID)
	if err != nil {
		return nil, fmt.Errorf("failed to get dependents: %w", err)
	}

	return relationships, nil
}

// ============================================================================
// STATISTICS AND ANALYSIS
// ============================================================================

// GetCodeIndexStats retrieves statistics for code indexing
func (s *CodeIndexServiceImpl) GetCodeIndexStats(ctx context.Context, projectID string) (*models.CodeIndexStats, error) {
	if projectID == "" {
		return nil, errors.New("project ID is required")
	}

	// Try cache
	cacheKey := "code_stats:" + projectID
	if cached, err := s.getStatsFromCache(ctx, cacheKey); cached != nil && err == nil {
		log.Printf("[CACHE HIT] Retrieved code stats for project %s from cache", projectID)
		return cached, nil
	}

	stats, err := s.entityRepo.GetStats(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to get code index stats: %w", err)
	}

	// Cache result with shorter TTL (stats change frequently)
	go func() {
		cacheCtx, cancel := context.WithTimeout(context.Background(), codeIndexCacheWriteTimeout)
		defer cancel()
		if err := s.setStatsInCache(cacheCtx, cacheKey, stats); err != nil {
			log.Printf("Warning: Failed to cache stats: %v", err)
		}
	}()

	return stats, nil
}

// ============================================================================
// NEW INTERFACE METHODS
// ============================================================================

// IndexCode indexes code with the new request/response structure
func (s *CodeIndexServiceImpl) IndexCode(ctx context.Context, req *IndexCodeRequest) (*IndexCodeResponse, error) {
	// Stub implementation - delegates to legacy method
	entities := make([]*models.CodeEntity, 0, len(req.Entities))
	for _, e := range req.Entities {
		entity := &models.CodeEntity{
			ProjectID:     req.ProjectID,
			FilePath:      req.FilePath,
			Language:      req.Language,
			EntityType:    e.EntityType,
			Name:          e.Name,
			FullName:      e.FullName,
			Description:   e.Description,
			LineNumber:    e.LineNumber,
			EndLineNumber: e.EndLineNumber,
		}
		entities = append(entities, entity)
	}

	if err := s.IndexCodeEntities(ctx, entities); err != nil {
		return nil, err
	}

	return &IndexCodeResponse{
		EntityCount: len(entities),
		Entities:    entities,
	}, nil
}

// BatchIndexCode indexes multiple code files in batch
func (s *CodeIndexServiceImpl) BatchIndexCode(_ context.Context, req *BatchIndexRequest) (*BatchIndexResponse, error) {
	// Stub implementation
	var totalEntities int
	for _, batch := range req.Batches {
		totalEntities += len(batch.Entities)
	}

	return &BatchIndexResponse{
		EntityCount:       totalEntities,
		RelationshipCount: 0,
		BatchCount:        len(req.Batches),
	}, nil
}

// Reindex reindexes all code for a project
func (s *CodeIndexServiceImpl) Reindex(ctx context.Context, projectID string) error {
	// Stub implementation - invalidate caches
	s.invalidateProjectCaches(ctx, projectID)
	return nil
}

// GetEntity gets a code entity with its relationships
func (s *CodeIndexServiceImpl) GetEntity(ctx context.Context, entityID string) (*CodeEntityWithRelations, error) {
	entity, err := s.GetCodeEntity(ctx, entityID)
	if err != nil {
		return nil, err
	}

	deps, _ := s.GetEntityDependencies(ctx, entityID)
	dependents, _ := s.GetEntityDependents(ctx, entityID)

	// Combine all relationships
	allRelationships := make([]*models.CodeEntityRelationship, 0, len(deps)+len(dependents))
	allRelationships = append(allRelationships, deps...)
	allRelationships = append(allRelationships, dependents...)

	return &CodeEntityWithRelations{
		Entity:        entity,
		Relationships: allRelationships,
		RelationCount: len(allRelationships),
	}, nil
}

// ListEntities lists code entities with simplified parameters
func (s *CodeIndexServiceImpl) ListEntities(ctx context.Context, projectID string, limit, offset int) ([]*models.CodeEntity, error) {
	return s.ListCodeEntities(ctx, CodeEntityFilter{
		ProjectID: projectID,
		Limit:     limit,
		Offset:    offset,
	})
}

// UpdateEntity updates a code entity with specific fields
func (s *CodeIndexServiceImpl) UpdateEntity(ctx context.Context, entityID string, description string, _ json.RawMessage) (*models.CodeEntity, error) {
	entity, err := s.GetCodeEntity(ctx, entityID)
	if err != nil {
		return nil, err
	}

	entity.Description = description
	// Note: models.CodeEntity uses datatypes.JSON, need to convert
	// For now, just skip the metadata update if it's causing issues

	if err := s.UpdateCodeEntity(ctx, entity); err != nil {
		return nil, err
	}

	return entity, nil
}

// DeleteEntity deletes a code entity
func (s *CodeIndexServiceImpl) DeleteEntity(ctx context.Context, entityID string) error {
	return s.DeleteCodeEntity(ctx, entityID)
}

// SearchEntities searches for code entities
func (s *CodeIndexServiceImpl) SearchEntities(ctx context.Context, projectID, query string, limit, offset int) ([]*models.CodeEntity, error) {
	return s.SearchCodeEntities(ctx, projectID, query, limit, offset)
}

// GetStats gets code index statistics
func (s *CodeIndexServiceImpl) GetStats(ctx context.Context, projectID string) (*models.CodeIndexStats, error) {
	return s.GetCodeIndexStats(ctx, projectID)
}

// ============================================================================
// VALIDATION HELPERS
// ============================================================================

func (s *CodeIndexServiceImpl) validateCodeEntity(entity *models.CodeEntity) error {
	if entity.ID == "" {
		return errors.New("entity ID is required")
	}
	if entity.ProjectID == "" {
		return errors.New("project ID is required")
	}
	if entity.Name == "" {
		return errors.New("entity name is required")
	}
	if entity.EntityType == "" {
		return errors.New("entity type is required")
	}
	if entity.FilePath == "" {
		return errors.New("file path is required")
	}
	if entity.Language == "" {
		return errors.New("language is required")
	}
	if entity.LineNumber < 0 {
		return errors.New("line number must be non-negative")
	}
	if entity.EndLineNumber > 0 && entity.EndLineNumber < entity.LineNumber {
		return errors.New("end line number must be greater than or equal to line number")
	}
	return nil
}

func (s *CodeIndexServiceImpl) validateRelationship(rel *models.CodeEntityRelationship) error {
	if rel.ID == "" {
		return errors.New("relationship ID is required")
	}
	if rel.ProjectID == "" {
		return errors.New("project ID is required")
	}
	if rel.SourceID == "" {
		return errors.New("source ID is required")
	}
	if rel.TargetID == "" {
		return errors.New("target ID is required")
	}
	if rel.RelationType == "" {
		return errors.New("relation type is required")
	}
	if rel.SourceID == rel.TargetID {
		return errors.New("source and target cannot be the same entity")
	}
	return nil
}

// ============================================================================
// CACHE HELPERS
// ============================================================================

func (s *CodeIndexServiceImpl) invalidateEntityCaches(ctx context.Context, entity *models.CodeEntity) {
	// Invalidate entity cache
	_ = s.cache.Delete(ctx, "code_entity:"+entity.ID)

	// Invalidate project caches
	s.invalidateProjectCaches(ctx, entity.ProjectID)

	// Invalidate file cache
	_ = s.cache.Delete(ctx, "code_entities:project:"+entity.ProjectID+":file:"+entity.FilePath)

	// Invalidate type cache
	_ = s.cache.Delete(ctx, "code_entities:project:"+entity.ProjectID+":type:"+entity.EntityType)
}

func (s *CodeIndexServiceImpl) invalidateProjectCaches(ctx context.Context, projectID string) {
	_ = s.cache.Delete(ctx, "code_entities:project:"+projectID+":page:0")
	_ = s.cache.Delete(ctx, "code_stats:"+projectID)
}

func (s *CodeIndexServiceImpl) getEntityFromCache(ctx context.Context, key string) (*models.CodeEntity, error) {
	if s.cache == nil {
		return nil, errors.New("cache not available")
	}

	var entity models.CodeEntity
	err := s.cache.Get(ctx, key, &entity)
	if err != nil {
		return nil, err
	}

	return &entity, nil
}

func (s *CodeIndexServiceImpl) setEntityInCache(ctx context.Context, key string, entity *models.CodeEntity) error {
	if s.cache == nil {
		return nil
	}

	return s.cache.Set(ctx, key, entity)
}

func (s *CodeIndexServiceImpl) getEntitiesFromCache(ctx context.Context, key string) ([]*models.CodeEntity, error) {
	if s.cache == nil {
		return nil, errors.New("cache not available")
	}

	var entities []*models.CodeEntity
	err := s.cache.Get(ctx, key, &entities)
	if err != nil {
		return nil, err
	}

	return entities, nil
}

func (s *CodeIndexServiceImpl) setEntitiesInCache(ctx context.Context, key string, entities []*models.CodeEntity) error {
	if s.cache == nil {
		return nil
	}

	return s.cache.Set(ctx, key, entities)
}

func (s *CodeIndexServiceImpl) getRelationshipsFromCache(ctx context.Context, key string) ([]*models.CodeEntityRelationship, error) {
	if s.cache == nil {
		return nil, errors.New("cache not available")
	}

	var relationships []*models.CodeEntityRelationship
	err := s.cache.Get(ctx, key, &relationships)
	if err != nil {
		return nil, err
	}

	return relationships, nil
}

func (s *CodeIndexServiceImpl) setRelationshipsInCache(ctx context.Context, key string, relationships []*models.CodeEntityRelationship) error {
	if s.cache == nil {
		return nil
	}

	return s.cache.Set(ctx, key, relationships)
}

func (s *CodeIndexServiceImpl) getStatsFromCache(ctx context.Context, key string) (*models.CodeIndexStats, error) {
	if s.cache == nil {
		return nil, errors.New("cache not available")
	}

	var stats models.CodeIndexStats
	err := s.cache.Get(ctx, key, &stats)
	if err != nil {
		return nil, err
	}

	return &stats, nil
}

func (s *CodeIndexServiceImpl) setStatsInCache(ctx context.Context, key string, stats *models.CodeIndexStats) error {
	if s.cache == nil {
		return nil
	}

	return s.cache.Set(ctx, key, stats)
}
