package services

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/nats-io/nats.go"
	"github.com/redis/go-redis/v9"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

const (
	agentStatusIdle = "idle"

	// asyncTimeout is the default timeout for async fire-and-forget operations
	// (cache writes, event publishing) that are intentionally detached from request context.
	asyncTimeout = 2 * time.Second
)

// asyncFireAndForget runs fn in a goroutine with a fresh context detached from the request.
// Used for non-blocking cache writes and event publishing where the caller does not wait
// for completion and failure is logged, not propagated.
func asyncFireAndForget(fn func(ctx context.Context)) {
	go func() {
		ctx, cancel := context.WithTimeout(context.Background(), asyncTimeout)
		defer cancel()
		fn(ctx)
	}()
}

// ItemService handles business logic for items
type ItemService interface {
	// Create operations
	CreateItem(ctx context.Context, item *models.Item) error
	CreateBatch(ctx context.Context, items []*models.Item) error

	// Read operations
	GetItem(ctx context.Context, id string) (*models.Item, error)
	GetWithLinks(ctx context.Context, id string) (*ItemWithLinks, error)
	ListItems(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error)
	Count(ctx context.Context, filter repository.ItemFilter) (int64, error)

	// Update operations
	UpdateItem(ctx context.Context, item *models.Item) error
	UpdateStatus(ctx context.Context, id, status string) error
	UpdateBatch(ctx context.Context, items []*models.Item) error

	// Delete operations
	DeleteItem(ctx context.Context, id string) error
	DeleteBatch(ctx context.Context, ids []string) error

	// Validation and utility
	Validate(ctx context.Context, item *models.Item) error
	ItemExists(ctx context.Context, id string) (bool, error)
	GetItemStats(ctx context.Context, projectID string) (*ItemStats, error)
}

// ItemWithLinks represents an item with its related links
type ItemWithLinks struct {
	Item        *models.Item   `json:"item"`
	SourceLinks []*models.Link `json:"source_links"`
	TargetLinks []*models.Link `json:"target_links"`
}

// LinkService handles business logic for links
type LinkService interface {
	CreateLink(ctx context.Context, link *models.Link) error
	GetLink(ctx context.Context, id string) (*models.Link, error)
	ListLinks(ctx context.Context, filter repository.LinkFilter) ([]*models.Link, error)
	UpdateLink(ctx context.Context, link *models.Link) error
	DeleteLink(ctx context.Context, id string) error
	GetItemDependencies(ctx context.Context, itemID string) (*DependencyGraph, error)
}

// ProjectService handles business logic for projects
type ProjectService interface {
	CreateProject(ctx context.Context, project *models.Project) error
	CreateProjectWithItems(ctx context.Context, project *models.Project, items []*models.Item) error
	GetProject(ctx context.Context, id string) (*models.Project, error)
	ListProjects(ctx context.Context) ([]*models.Project, error)
	UpdateProject(ctx context.Context, project *models.Project) error
	UpdateProjectAndItems(ctx context.Context, project *models.Project, items []*models.Item) error
	DeleteProject(ctx context.Context, id string) error
	DeleteProjectWithItems(ctx context.Context, projectID string) error
	GetProjectStats(ctx context.Context, projectID string) (*ProjectStats, error)
}

// AgentService handles business logic for agents
type AgentService interface {
	CreateAgent(ctx context.Context, agent *models.Agent) error
	GetAgent(ctx context.Context, id string) (*models.Agent, error)
	ListAgents(ctx context.Context) ([]*models.Agent, error)
	UpdateAgent(ctx context.Context, agent *models.Agent) error
	UpdateAgentStatus(ctx context.Context, id, status string) error
	DeleteAgent(ctx context.Context, id string) error
	NotifyAgentEvent(ctx context.Context, event *AgentEvent) error
}

// DTOs and helper structures

// ItemStats holds aggregate item counts by type, status, and priority.
type ItemStats struct {
	TotalItems int64            `json:"total_items"`
	ByType     map[string]int64 `json:"by_type"`
	ByStatus   map[string]int64 `json:"by_status"`
	ByPriority map[string]int64 `json:"by_priority"`
}

// DependencyGraph holds item dependencies and dependents for graph analysis.
type DependencyGraph struct {
	ItemID       string                  `json:"item_id"`
	Dependencies []*models.Link          `json:"dependencies"`
	Dependents   []*models.Link          `json:"dependents"`
	Items        map[string]*models.Item `json:"items"`
}

// AgentEvent represents an agent lifecycle or activity event.
type AgentEvent struct {
	AgentID   string                 `json:"agent_id"`
	EventType string                 `json:"event_type"`
	Data      map[string]interface{} `json:"data"`
	Timestamp time.Time              `json:"timestamp"`
}

// Implementations

// NewItemService returns a new ItemService implementation.
func NewItemService(
	repo repository.ItemRepository,
	linkRepo repository.LinkRepository,
	redisClient *redis.Client,
	natsConn *nats.Conn,
) ItemService {
	return &itemService{
		repo:        repo,
		linkRepo:    linkRepo,
		redisClient: redisClient,
		natsConn:    natsConn,
	}
}

type itemService struct {
	repo        repository.ItemRepository
	linkRepo    repository.LinkRepository
	redisClient *redis.Client
	natsConn    *nats.Conn
}

func (s *itemService) CreateItem(ctx context.Context, item *models.Item) error {
	// Validate item
	if item.Title == "" {
		return errors.New("item title is required")
	}
	if item.ProjectID == "" {
		return errors.New("project ID is required")
	}

	// Set defaults
	if item.Status == "" {
		item.Status = statusTodo
	}
	if item.Priority == 0 {
		item.Priority = models.PriorityMedium
	}

	// Create item
	if err := s.repo.Create(ctx, item); err != nil {
		return fmt.Errorf("failed to create item: %w", err)
	}

	// Invalidate cache
	if s.redisClient != nil {
		cacheKey := "project:" + item.ProjectID + ":items"
		s.redisClient.Del(ctx, cacheKey)
	}

	// Publish event
	if s.natsConn != nil {
		s.publishEvent("item.created", item)
	}

	return nil
}

func (s *itemService) GetItem(ctx context.Context, id string) (*models.Item, error) {
	// Try cache first
	if s.redisClient != nil {
		cacheKey := "item:" + id
		val, err := s.redisClient.Get(ctx, cacheKey).Result()
		if err == nil {
			var item models.Item
			if err := json.Unmarshal([]byte(val), &item); err == nil {
				return &item, nil
			}
		}
	}

	// Get from database
	item, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, err
	}

	// Cache the result
	if s.redisClient != nil {
		cacheKey := "item:" + id
		data, err := json.Marshal(item)
		if err != nil {
			slog.Warn("failed to marshal item for cache", "error", err)
		} else {
			s.redisClient.Set(ctx, cacheKey, data, defaultCacheTTL)
		}
	}

	return item, nil
}

func (s *itemService) ListItems(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error) {
	return s.repo.List(ctx, filter)
}

func (s *itemService) UpdateItem(ctx context.Context, item *models.Item) error {
	// Validate
	if item.ID == "" {
		return errors.New("item ID is required")
	}

	// Update
	if err := s.repo.Update(ctx, item); err != nil {
		return fmt.Errorf("failed to update item: %w", err)
	}

	// Invalidate cache
	if s.redisClient != nil {
		s.redisClient.Del(ctx, "item:"+item.ID)
		s.redisClient.Del(ctx, "project:"+item.ProjectID+":items")
	}

	// Publish event
	if s.natsConn != nil {
		s.publishEvent("item.updated", item)
	}

	return nil
}

func (s *itemService) DeleteItem(ctx context.Context, id string) error {
	// Get item first for cache invalidation
	item, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return err
	}

	// Delete related links
	if err := s.linkRepo.DeleteByItemID(ctx, id); err != nil {
		return fmt.Errorf("failed to delete item links: %w", err)
	}

	// Delete item
	if err := s.repo.Delete(ctx, id); err != nil {
		return fmt.Errorf("failed to delete item: %w", err)
	}

	// Invalidate cache
	if s.redisClient != nil {
		s.redisClient.Del(ctx, "item:"+id)
		s.redisClient.Del(ctx, "project:"+item.ProjectID+":items")
	}

	// Publish event
	if s.natsConn != nil {
		s.publishEvent("item.deleted", map[string]string{"id": id})
	}

	return nil
}

func (s *itemService) GetItemStats(ctx context.Context, projectID string) (*ItemStats, error) {
	// Try cache
	if s.redisClient != nil {
		cacheKey := "project:" + projectID + ":stats"
		val, err := s.redisClient.Get(ctx, cacheKey).Result()
		if err == nil {
			var stats ItemStats
			if err := json.Unmarshal([]byte(val), &stats); err == nil {
				return &stats, nil
			}
		}
	}

	// Calculate stats
	projectIDPtr := &projectID
	items, err := s.repo.List(ctx, repository.ItemFilter{ProjectID: projectIDPtr})
	if err != nil {
		return nil, err
	}

	stats := &ItemStats{
		TotalItems: int64(len(items)),
		ByType:     make(map[string]int64),
		ByStatus:   make(map[string]int64),
		ByPriority: make(map[string]int64),
	}

	for _, item := range items {
		stats.ByType[item.Type]++
		stats.ByStatus[item.Status]++
		stats.ByPriority[models.PriorityLabel(item.Priority)]++
	}

	// Cache the result
	if s.redisClient != nil {
		cacheKey := "project:" + projectID + ":stats"
		data, err := json.Marshal(stats)
		if err != nil {
			slog.Warn("failed to marshal stats for cache", "error", err)
		} else {
			s.redisClient.Set(ctx, cacheKey, data, defaultCacheTTL)
		}
	}

	return stats, nil
}

// CreateBatch - stub implementation (delegate to ItemServiceImpl)
func (s *itemService) CreateBatch(ctx context.Context, items []*models.Item) error {
	for _, item := range items {
		if err := s.CreateItem(ctx, item); err != nil {
			return err
		}
	}
	return nil
}

// GetWithLinks - stub implementation
func (s *itemService) GetWithLinks(ctx context.Context, id string) (*ItemWithLinks, error) {
	item, err := s.GetItem(ctx, id)
	if err != nil {
		return nil, err
	}
	sourceLinks, err := s.linkRepo.GetBySourceID(ctx, id)
	if err != nil {
		slog.Warn("failed to get source links", "item_id", id, "error", err)
	}
	targetLinks, err := s.linkRepo.GetByTargetID(ctx, id)
	if err != nil {
		slog.Warn("failed to get target links", "item_id", id, "error", err)
	}
	return &ItemWithLinks{
		Item:        item,
		SourceLinks: sourceLinks,
		TargetLinks: targetLinks,
	}, nil
}

// Count - stub implementation
func (s *itemService) Count(ctx context.Context, filter repository.ItemFilter) (int64, error) {
	return s.repo.Count(ctx, filter)
}

// UpdateStatus - stub implementation
func (s *itemService) UpdateStatus(ctx context.Context, id, status string) error {
	item, err := s.GetItem(ctx, id)
	if err != nil {
		return err
	}
	item.Status = status
	return s.UpdateItem(ctx, item)
}

// UpdateBatch - stub implementation
func (s *itemService) UpdateBatch(ctx context.Context, items []*models.Item) error {
	for _, item := range items {
		if err := s.UpdateItem(ctx, item); err != nil {
			return err
		}
	}
	return nil
}

// DeleteBatch - stub implementation
func (s *itemService) DeleteBatch(ctx context.Context, ids []string) error {
	for _, id := range ids {
		if err := s.DeleteItem(ctx, id); err != nil {
			return err
		}
	}
	return nil
}

// Validate - stub implementation
func (s *itemService) Validate(_ context.Context, item *models.Item) error {
	if item.Title == "" {
		return errors.New("item title is required")
	}
	if item.ProjectID == "" {
		return errors.New("project ID is required")
	}
	return nil
}

// ItemExists - stub implementation
func (s *itemService) ItemExists(ctx context.Context, id string) (bool, error) {
	_, err := s.repo.GetByID(ctx, id)
	if err != nil {
		if err.Error() == "item not found" {
			return false, nil
		}
		return false, err
	}
	return true, nil
}

func (s *itemService) publishEvent(eventType string, data interface{}) {
	if s.natsConn == nil {
		return
	}

	payload, err := json.Marshal(map[string]interface{}{
		"type":      eventType,
		"data":      data,
		"timestamp": time.Now(),
	})
	if err != nil {
		return
	}

	if err := s.natsConn.Publish(eventType, payload); err != nil {
		slog.Warn("failed to publish NATS event", "type", eventType, "error", err)
	}
}

// Link Service Implementation

type linkService struct {
	repo     repository.LinkRepository
	itemRepo repository.ItemRepository
	natsConn *nats.Conn
}

// NewLinkService returns a new LinkService implementation.
func NewLinkService(
	repo repository.LinkRepository,
	itemRepo repository.ItemRepository,
	natsConn *nats.Conn,
) LinkService {
	return &linkService{
		repo:     repo,
		itemRepo: itemRepo,
		natsConn: natsConn,
	}
}

func (s *linkService) CreateLink(ctx context.Context, link *models.Link) error {
	// Validate
	if link.SourceID == "" || link.TargetID == "" {
		return errors.New("source and target IDs are required")
	}
	if link.Type == "" {
		return errors.New("link type is required")
	}

	// Verify items exist
	if _, err := s.itemRepo.GetByID(ctx, link.SourceID); err != nil {
		return fmt.Errorf("source item not found: %w", err)
	}
	if _, err := s.itemRepo.GetByID(ctx, link.TargetID); err != nil {
		return fmt.Errorf("target item not found: %w", err)
	}

	// Create link
	if err := s.repo.Create(ctx, link); err != nil {
		return fmt.Errorf("failed to create link: %w", err)
	}

	// Publish event
	if s.natsConn != nil {
		s.publishEvent("link.created", link)
	}

	return nil
}

func (s *linkService) GetLink(ctx context.Context, id string) (*models.Link, error) {
	return s.repo.GetByID(ctx, id)
}

func (s *linkService) ListLinks(ctx context.Context, filter repository.LinkFilter) ([]*models.Link, error) {
	return s.repo.List(ctx, filter)
}

func (s *linkService) UpdateLink(ctx context.Context, link *models.Link) error {
	if err := s.repo.Update(ctx, link); err != nil {
		return fmt.Errorf("failed to update link: %w", err)
	}

	if s.natsConn != nil {
		s.publishEvent("link.updated", link)
	}

	return nil
}

func (s *linkService) DeleteLink(ctx context.Context, id string) error {
	if err := s.repo.Delete(ctx, id); err != nil {
		return fmt.Errorf("failed to delete link: %w", err)
	}

	if s.natsConn != nil {
		s.publishEvent("link.deleted", map[string]string{"id": id})
	}

	return nil
}

func (s *linkService) GetItemDependencies(ctx context.Context, itemID string) (*DependencyGraph, error) {
	// Get all links where item is source or target
	dependencies, err := s.repo.GetBySourceID(ctx, itemID)
	if err != nil {
		return nil, err
	}

	dependents, err := s.repo.GetByTargetID(ctx, itemID)
	if err != nil {
		return nil, err
	}

	// Collect all related item IDs
	itemIDs := make(map[string]bool)
	for _, link := range dependencies {
		itemIDs[link.TargetID] = true
	}
	for _, link := range dependents {
		itemIDs[link.SourceID] = true
	}

	// Fetch all related items
	items := make(map[string]*models.Item)
	for id := range itemIDs {
		item, err := s.itemRepo.GetByID(ctx, id)
		if err == nil {
			items[id] = item
		}
	}

	return &DependencyGraph{
		ItemID:       itemID,
		Dependencies: dependencies,
		Dependents:   dependents,
		Items:        items,
	}, nil
}

func (s *linkService) publishEvent(eventType string, data interface{}) {
	if s.natsConn == nil {
		return
	}

	payload, err := json.Marshal(map[string]interface{}{
		"type":      eventType,
		"data":      data,
		"timestamp": time.Now(),
	})
	if err != nil {
		return
	}

	if err := s.natsConn.Publish(eventType, payload); err != nil {
		slog.Warn("failed to publish NATS event", "type", eventType, "error", err)
	}
}

// Project Service Implementation

type projectService struct {
	repo repository.ProjectRepository
}

// NewProjectService returns a new ProjectService implementation.
func NewProjectService(repo repository.ProjectRepository) ProjectService {
	return &projectService{repo: repo}
}

func (s *projectService) CreateProject(ctx context.Context, project *models.Project) error {
	if project.Name == "" {
		return errors.New("project name is required")
	}

	return s.repo.Create(ctx, project)
}

func (s *projectService) CreateProjectWithItems(ctx context.Context, project *models.Project, _ []*models.Item) error {
	if err := s.CreateProject(ctx, project); err != nil {
		return err
	}
	return nil
}

func (s *projectService) UpdateProjectAndItems(ctx context.Context, project *models.Project, _ []*models.Item) error {
	return s.UpdateProject(ctx, project)
}

func (s *projectService) DeleteProjectWithItems(ctx context.Context, projectID string) error {
	return s.DeleteProject(ctx, projectID)
}

func (s *projectService) GetProject(ctx context.Context, id string) (*models.Project, error) {
	return s.repo.GetByID(ctx, id)
}

func (s *projectService) ListProjects(ctx context.Context) ([]*models.Project, error) {
	return s.repo.List(ctx)
}

func (s *projectService) UpdateProject(ctx context.Context, project *models.Project) error {
	if project.ID == "" {
		return errors.New("project ID is required")
	}

	return s.repo.Update(ctx, project)
}

func (s *projectService) DeleteProject(ctx context.Context, id string) error {
	return s.repo.Delete(ctx, id)
}

func (s *projectService) GetProjectStats(_ context.Context, projectID string) (*ProjectStats, error) {
	// Stub implementation - returns empty stats
	// Full implementation is in ProjectServiceImpl
	return &ProjectStats{
		ProjectID:     projectID,
		TotalItems:    0,
		TotalLinks:    0,
		ItemsByType:   make(map[string]int64),
		ItemsByStatus: make(map[string]int64),
		UpdatedAt:     time.Now(),
	}, nil
}

// Agent Service Implementation

type agentService struct {
	repo     repository.AgentRepository
	natsConn *nats.Conn
}

// NewAgentService returns a new AgentService implementation.
func NewAgentService(repo repository.AgentRepository, natsConn *nats.Conn) AgentService {
	return &agentService{
		repo:     repo,
		natsConn: natsConn,
	}
}

func (s *agentService) CreateAgent(ctx context.Context, agent *models.Agent) error {
	if agent.Name == "" {
		return errors.New("agent name is required")
	}
	if agent.ProjectID == "" {
		return errors.New("project ID is required")
	}

	if agent.Status == "" {
		agent.Status = agentStatusIdle
	}

	if err := s.repo.Create(ctx, agent); err != nil {
		return fmt.Errorf("failed to create agent: %w", err)
	}

	if s.natsConn != nil {
		s.publishEvent("agent.created", agent)
	}

	return nil
}

func (s *agentService) GetAgent(ctx context.Context, id string) (*models.Agent, error) {
	return s.repo.GetByID(ctx, id)
}

func (s *agentService) ListAgents(ctx context.Context) ([]*models.Agent, error) {
	return s.repo.List(ctx)
}

func (s *agentService) UpdateAgent(ctx context.Context, agent *models.Agent) error {
	if err := s.repo.Update(ctx, agent); err != nil {
		return fmt.Errorf("failed to update agent: %w", err)
	}

	if s.natsConn != nil {
		s.publishEvent("agent.updated", agent)
	}

	return nil
}

func (s *agentService) UpdateAgentStatus(ctx context.Context, id, status string) error {
	if err := s.repo.UpdateStatus(ctx, id, status); err != nil {
		return fmt.Errorf("failed to update agent status: %w", err)
	}

	if s.natsConn != nil {
		s.publishEvent("agent.status_changed", map[string]string{
			"id":     id,
			"status": status,
		})
	}

	return nil
}

func (s *agentService) DeleteAgent(ctx context.Context, id string) error {
	if err := s.repo.Delete(ctx, id); err != nil {
		return fmt.Errorf("failed to delete agent: %w", err)
	}

	if s.natsConn != nil {
		s.publishEvent("agent.deleted", map[string]string{"id": id})
	}

	return nil
}

func (s *agentService) NotifyAgentEvent(_ context.Context, event *AgentEvent) error {
	if s.natsConn == nil {
		return errors.New("NATS connection not available")
	}

	event.Timestamp = time.Now()
	payload, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	subject := "agent." + event.AgentID + "." + event.EventType
	if err := s.natsConn.Publish(subject, payload); err != nil {
		return fmt.Errorf("failed to publish event: %w", err)
	}

	return nil
}

func (s *agentService) publishEvent(eventType string, data interface{}) {
	if s.natsConn == nil {
		return
	}

	payload, err := json.Marshal(map[string]interface{}{
		"type":      eventType,
		"data":      data,
		"timestamp": time.Now(),
	})
	if err != nil {
		return
	}

	if err := s.natsConn.Publish(eventType, payload); err != nil {
		slog.Warn("failed to publish NATS event", "type", eventType, "error", err)
	}
}
