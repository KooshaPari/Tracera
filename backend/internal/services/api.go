package services

import (
	"context"
	"encoding/json"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

const defaultListLimit = 50

// ============================================================================
// Service API Interfaces
// ============================================================================
//
// These interfaces define the service-layer API for TracerTM backend.
// Handlers MUST depend on these service interfaces, NOT directly on repositories.
//
// Design Principles:
// - Context as first parameter for all methods
// - Clear error returns
// - Services may call other services via their interfaces
// - Services own business logic validation
// - Services manage caching and event publishing

// ============================================================================
// Core Service Interfaces (CRUD + Validation)
// ============================================================================

// NOTE: ItemService, LinkService, ProjectService, and AgentService interfaces
// are already defined in services.go to maintain backward compatibility.
// See services.go for the complete interface definitions.
//
// This file extends the API with additional service interfaces and types
// needed for the service-oriented architecture migration.

// ============================================================================
// ViewService - Manages custom views/perspectives
// ============================================================================

// ViewService defines business operations for views
// Views are user-defined perspectives on data (Kanban, Timeline, Matrix, etc.)
type ViewService interface {
	// CreateView creates a new view with validation
	CreateView(ctx context.Context, view *models.View) error

	// GetView retrieves a view by ID
	GetView(ctx context.Context, id string) (*models.View, error)

	// GetViewsByProject retrieves all views for a project
	GetViewsByProject(ctx context.Context, projectID string) ([]*models.View, error)

	// ListViews lists all views
	ListViews(ctx context.Context) ([]*models.View, error)

	// UpdateView updates a view
	UpdateView(ctx context.Context, view *models.View) error

	// DeleteView deletes a view
	DeleteView(ctx context.Context, id string) error

	// GetViewStats returns statistics for a view
	GetViewStats(ctx context.Context, viewID string) (*models.ViewStats, error)

	// ValidateView validates view business rules
	ValidateView(view *models.View) error
}

// ============================================================================
// CacheService - Manages caching operations
// ============================================================================

// CacheService defines caching operations for all services
// This service owns the Redis client exclusively and gates all cache access
type CacheService interface {
	// Generic cache operations
	Get(ctx context.Context, key string) (string, error)
	Set(ctx context.Context, key string, value string, ttl time.Duration) error
	Delete(ctx context.Context, key string) error
	InvalidatePattern(ctx context.Context, pattern string) error
	GetMulti(ctx context.Context, keys []string) (map[string]string, error)
	SetMulti(ctx context.Context, items map[string]string, ttl time.Duration) error
	Exists(ctx context.Context, key string) (bool, error)
	Expire(ctx context.Context, key string, ttl time.Duration) error

	// Entity-specific operations with namespacing
	GetItem(ctx context.Context, itemID string) (*models.Item, error)
	SetItem(ctx context.Context, item *models.Item) error
	InvalidateItem(ctx context.Context, itemID string) error

	GetProject(ctx context.Context, projectID string) (*models.Project, error)
	SetProject(ctx context.Context, project *models.Project) error
	InvalidateProject(ctx context.Context, projectID string) error

	GetLink(ctx context.Context, linkID string) (*models.Link, error)
	SetLink(ctx context.Context, link *models.Link) error
	InvalidateLink(ctx context.Context, linkID string) error

	GetAgent(ctx context.Context, agentID string) (*models.Agent, error)
	SetAgent(ctx context.Context, agent *models.Agent) error
	InvalidateAgent(ctx context.Context, agentID string) error

	// List cache by key (for project item lists)
	GetItems(ctx context.Context, key string) ([]*models.Item, error)
	SetItems(ctx context.Context, key string, items []*models.Item, ttl time.Duration) error

	// Item stats cache
	GetStats(ctx context.Context, key string) (*ItemStats, error)
	SetStats(ctx context.Context, key string, stats *ItemStats, ttl time.Duration) error

	// Batch operations for performance
	GetItemsBatch(ctx context.Context, itemIDs []string) (map[string]*models.Item, error)
	SetItemsBatch(ctx context.Context, items []*models.Item) error
	InvalidateProjectItems(ctx context.Context, projectID string) error

	// Monitoring and health
	HealthCheck(ctx context.Context) error
}

// ============================================================================
// EventService - Manages event publishing and subscription
// ============================================================================

// EventService defines event publishing and subscription
// Events enable loose coupling between services
type EventService interface {
	// PublishItemEvent publishes an item event
	PublishItemEvent(ctx context.Context, event *ItemEvent) error

	// PublishLinkEvent publishes a link event
	PublishLinkEvent(ctx context.Context, event *LinkEvent) error

	// PublishProjectEvent publishes a project event
	PublishProjectEvent(ctx context.Context, event *ProjectEvent) error

	// PublishAgentEvent publishes an agent event
	PublishAgentEvent(ctx context.Context, event *AgentEventType) error

	// SubscribeToItemEvents subscribes to item events
	SubscribeToItemEvents(ctx context.Context, handler ItemEventHandler) error

	// SubscribeToLinkEvents subscribes to link events
	SubscribeToLinkEvents(ctx context.Context, handler LinkEventHandler) error

	// SubscribeToProjectEvents subscribes to project events
	SubscribeToProjectEvents(ctx context.Context, handler ProjectEventHandler) error

	// SubscribeToAgentEvents subscribes to agent events
	SubscribeToAgentEvents(ctx context.Context, handler AgentEventHandler) error
}

// ============================================================================
// Event Types
// ============================================================================

// ItemEvent represents an item domain event
type ItemEvent struct {
	EventType string                 `json:"event_type"` // created, updated, deleted
	ItemID    string                 `json:"item_id"`
	ProjectID string                 `json:"project_id"`
	Timestamp time.Time              `json:"timestamp"`
	Data      map[string]interface{} `json:"data"`
}

// LinkEvent represents a link domain event
type LinkEvent struct {
	EventType string                 `json:"event_type"` // created, updated, deleted
	LinkID    string                 `json:"link_id"`
	SourceID  string                 `json:"source_id"`
	TargetID  string                 `json:"target_id"`
	Timestamp time.Time              `json:"timestamp"`
	Data      map[string]interface{} `json:"data"`
}

// ProjectEvent represents a project domain event
type ProjectEvent struct {
	EventType string                 `json:"event_type"` // created, updated, deleted
	ProjectID string                 `json:"project_id"`
	Timestamp time.Time              `json:"timestamp"`
	Data      map[string]interface{} `json:"data"`
}

// AgentEventType represents an agent domain event
type AgentEventType struct {
	EventType string                 `json:"event_type"` // created, updated, deleted, status_changed
	AgentID   string                 `json:"agent_id"`
	ProjectID string                 `json:"project_id"`
	Timestamp time.Time              `json:"timestamp"`
	Data      map[string]interface{} `json:"data"`
}

// ============================================================================
// Event Handlers
// ============================================================================

// ItemEventHandler handles item events
type ItemEventHandler func(ctx context.Context, event *ItemEvent) error

// LinkEventHandler handles link events
type LinkEventHandler func(ctx context.Context, event *LinkEvent) error

// ProjectEventHandler handles project events
type ProjectEventHandler func(ctx context.Context, event *ProjectEvent) error

// AgentEventHandler handles agent events
type AgentEventHandler func(ctx context.Context, event *AgentEventType) error

// ============================================================================
// Supporting Types
// ============================================================================

// ProjectStats contains aggregated statistics for a project
type ProjectStats struct {
	ProjectID     string           `json:"project_id"`
	TotalItems    int64            `json:"total_items"`
	TotalLinks    int64            `json:"total_links"`
	ItemsByType   map[string]int64 `json:"items_by_type"`
	ItemsByStatus map[string]int64 `json:"items_by_status"`
	UpdatedAt     time.Time        `json:"updated_at"`
}

// AgentMetrics contains performance metrics for an agent
type AgentMetrics struct {
	AgentID       string        `json:"agent_id"`
	Status        string        `json:"status"`
	Uptime        time.Duration `json:"uptime"`
	TasksExecuted int64         `json:"tasks_executed"`
	LastActive    time.Time     `json:"last_active"`
}

// ============================================================================
// Cross-Service APIs
// ============================================================================

// CodeIndexService handles code entity indexing
type CodeIndexService interface {
	// Index operations
	IndexCode(ctx context.Context, req *IndexCodeRequest) (*IndexCodeResponse, error)
	BatchIndexCode(ctx context.Context, req *BatchIndexRequest) (*BatchIndexResponse, error)
	Reindex(ctx context.Context, projectID string) error

	// Entity operations
	GetEntity(ctx context.Context, entityID string) (*CodeEntityWithRelations, error)
	ListEntities(ctx context.Context, projectID string, limit, offset int) ([]*models.CodeEntity, error)
	UpdateEntity(ctx context.Context, entityID string, description string, metadata json.RawMessage) (*models.CodeEntity, error)
	DeleteEntity(ctx context.Context, entityID string) error

	// Search operations
	SearchEntities(ctx context.Context, projectID, query string, limit, offset int) ([]*models.CodeEntity, error)
	GetStats(ctx context.Context, projectID string) (*models.CodeIndexStats, error)

	// Legacy methods (deprecated - use new methods above)
	IndexCodeEntity(ctx context.Context, entity *models.CodeEntity) error
	IndexCodeEntities(ctx context.Context, entities []*models.CodeEntity) error
	GetCodeEntity(ctx context.Context, id string) (*models.CodeEntity, error)
	ListCodeEntities(ctx context.Context, filter CodeEntityFilter) ([]*models.CodeEntity, error)
	UpdateCodeEntity(ctx context.Context, entity *models.CodeEntity) error
	DeleteCodeEntity(ctx context.Context, id string) error
	GetCodeEntitiesByType(ctx context.Context, projectID, entityType string) ([]*models.CodeEntity, error)
	GetCodeEntitiesByFile(ctx context.Context, projectID, filePath string) ([]*models.CodeEntity, error)
	CreateRelationship(ctx context.Context, rel *models.CodeEntityRelationship) error
	GetEntityDependencies(ctx context.Context, entityID string) ([]*models.CodeEntityRelationship, error)
	GetEntityDependents(ctx context.Context, entityID string) ([]*models.CodeEntityRelationship, error)
	GetCodeIndexStats(ctx context.Context, projectID string) (*models.CodeIndexStats, error)
}

// CodeEntityFilter defines filtering for code entities
type CodeEntityFilter struct {
	ProjectID string
	FilePath  string
	Type      string
	Limit     int
	Offset    int
}

// Code Index DTOs

// IndexCodeRequest is the request body for indexing code entities and relationships.
type IndexCodeRequest struct {
	ProjectID     string                  `json:"project_id"`
	FilePath      string                  `json:"file_path"`
	Language      string                  `json:"language"`
	Entities      []CodeEntityInput       `json:"entities"`
	Relationships []CodeRelationshipInput `json:"relationships"`
}

// CodeEntityInput is a single code entity payload for index requests.
type CodeEntityInput struct {
	EntityType    string          `json:"entity_type"`
	Name          string          `json:"name"`
	FullName      string          `json:"full_name"`
	Description   string          `json:"description"`
	LineNumber    int             `json:"line_number"`
	EndLineNumber int             `json:"end_line_number"`
	ColumnNumber  int             `json:"column_number"`
	CodeSnippet   string          `json:"code_snippet"`
	Signature     string          `json:"signature"`
	ReturnType    string          `json:"return_type"`
	Parameters    json.RawMessage `json:"parameters"`
	Metadata      json.RawMessage `json:"metadata"`
}

// CodeRelationshipInput is a single relationship payload for index requests.
type CodeRelationshipInput struct {
	SourceEntityName string          `json:"source_entity_name"`
	TargetEntityName string          `json:"target_entity_name"`
	RelationType     string          `json:"relation_type"`
	Metadata         json.RawMessage `json:"metadata"`
}

// IndexCodeResponse is the response after indexing code.
type IndexCodeResponse struct {
	EntityCount int                  `json:"entity_count"`
	Entities    []*models.CodeEntity `json:"entities"`
}

// BatchIndexRequest is the request for batch code indexing.
type BatchIndexRequest struct {
	ProjectID string             `json:"project_id"`
	Batches   []IndexCodeRequest `json:"batches"`
}

// BatchIndexResponse is the response after batch code indexing.
type BatchIndexResponse struct {
	EntityCount       int `json:"entity_count"`
	RelationshipCount int `json:"relationship_count"`
	BatchCount        int `json:"batch_count"`
}

// CodeEntityWithRelations is a code entity plus its relationships for API responses.
type CodeEntityWithRelations struct {
	Entity        *models.CodeEntity               `json:"entity"`
	Relationships []*models.CodeEntityRelationship `json:"relationships"`
	RelationCount int                              `json:"relation_count"`
}

// SearchService is defined in search_service.go

// SearchFilters defines search filtering options
type SearchFilters struct {
	ProjectID string
	Status    string
	Type      string
	Limit     int
	Offset    int
}

// GraphAnalysisService provides graph analysis operations
type GraphAnalysisService interface {
	AnalyzeItemDependencies(ctx context.Context, itemID string) (*DependencyAnalysis, error)
	GetItemImpactAnalysis(ctx context.Context, itemID string) (*ImpactAnalysis, error)
	VisualizeDependencyGraph(ctx context.Context, itemID string) (string, error) // Returns DOT format
}

// DependencyAnalysis contains dependency analysis results
type DependencyAnalysis struct {
	ItemID           string `json:"item_id"`
	DirectDependents int    `json:"direct_dependents"`
	TransitiveDeps   int    `json:"transitive_deps"`
	Complexity       string `json:"complexity"` // low, medium, high
}

// ImpactAnalysis contains impact analysis results
type ImpactAnalysis struct {
	ItemID         string   `json:"item_id"`
	DirectImpact   []string `json:"direct_impact"`
	IndirectImpact []string `json:"indirect_impact"`
	RiskLevel      string   `json:"risk_level"` // low, medium, high
}

// VersionInfo contains temporal version information
type VersionInfo struct {
	Version   int       `json:"version"`
	Timestamp time.Time `json:"timestamp"`
	ChangedBy string    `json:"changed_by"`
}

// ============================================================================
// StorageService - Manages S3/MinIO file storage operations
// ============================================================================

// FileInfo represents metadata for a stored file
type FileInfo struct {
	Key          string                 `json:"key"`
	Bucket       string                 `json:"bucket"`
	Size         int64                  `json:"size"`
	ContentType  string                 `json:"content_type"`
	ETag         string                 `json:"etag"`
	LastModified time.Time              `json:"last_modified"`
	Metadata     map[string]interface{} `json:"metadata"`
	URL          string                 `json:"url"`
}

// StorageService defines operations for S3/MinIO file storage
// This service owns the S3 client exclusively and provides controlled access
type StorageService interface {
	// UploadFile uploads a file to the specified bucket
	// Returns the public URL and metadata
	UploadFile(ctx context.Context, file []byte, bucket string, key string, contentType string) (string, error)

	// DownloadFile retrieves a file from storage by URL or key
	// URL can be a full S3 URL or just the key
	DownloadFile(ctx context.Context, url string) ([]byte, error)

	// DeleteFile removes a file from storage
	// URL can be a full S3 URL or just the key
	DeleteFile(ctx context.Context, url string) error

	// ListFiles returns all files in a bucket with optional prefix filter
	ListFiles(ctx context.Context, bucket string, prefix string) ([]FileInfo, error)

	// GetFileMetadata retrieves metadata for a file without downloading content
	GetFileMetadata(ctx context.Context, url string) (*FileInfo, error)

	// GeneratePresignedUploadURL creates a presigned URL for direct uploads
	GeneratePresignedUploadURL(ctx context.Context, bucket string, key string, contentType string, expiryMinutes int) (string, error)

	// GeneratePresignedDownloadURL creates a presigned URL for direct downloads
	GeneratePresignedDownloadURL(ctx context.Context, url string, expiryMinutes int) (string, error)

	// CopyFile copies a file within storage
	CopyFile(ctx context.Context, sourceURL string, destBucket string, destKey string) error

	// FileExists checks if a file exists in storage
	FileExists(ctx context.Context, url string) (bool, error)

	// DeleteMultiple removes multiple files in a single operation
	DeleteMultiple(ctx context.Context, urls []string) error
}

// ============================================================================
// Service Registry Interface
// ============================================================================

// ServiceRegistry is the main service container interface
// Provides access to all domain services
type ServiceRegistry interface {
	ItemService() ItemService
	LinkService() LinkService
	ProjectService() ProjectService
	AgentService() AgentService
	ViewService() ViewService
	CacheService() CacheService
	EventService() EventService
	CodeIndexService() CodeIndexService
	SearchService() SearchService
	GraphAnalysisService() GraphAnalysisService
	StorageService() StorageService
}

// ============================================================================
// Utility Functions
// ============================================================================

// NewItemFilter creates a new ItemFilter with default values
func NewItemFilter() repository.ItemFilter {
	return repository.ItemFilter{
		Limit:  defaultListLimit,
		Offset: 0,
	}
}

// NewLinkFilter creates a new LinkFilter with default values
func NewLinkFilter() repository.LinkFilter {
	return repository.LinkFilter{
		Limit:  defaultListLimit,
		Offset: 0,
	}
}
