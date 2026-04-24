// Package services provides business logic and API types for agents, items, cache, and other domains.
package services

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/nats-io/nats.go"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// Ensure AgentServiceImpl implements AgentService interface
var _ AgentService = (*AgentServiceImpl)(nil)

const (
	defaultAgentCacheTTL = 5 * time.Minute
	cacheWriteTimeout    = 2 * time.Second
	maxAgentNameLength   = 255
)

// AgentServiceImpl implements the AgentService interface with caching and event publishing
type AgentServiceImpl struct {
	agentRepo repository.AgentRepository
	cache     cache.Cache
	natsConn  *nats.Conn
	cacheTTL  time.Duration
}

// NewAgentServiceImpl creates a new agent service implementation
func NewAgentServiceImpl(
	agentRepo repository.AgentRepository,
	cache cache.Cache,
	natsConn *nats.Conn,
) AgentService {
	if agentRepo == nil {
		panic("agentRepo cannot be nil")
	}

	return &AgentServiceImpl{
		agentRepo: agentRepo,
		cache:     cache,
		natsConn:  natsConn,
		cacheTTL:  defaultAgentCacheTTL,
	}
}

// ============================================================================
// CORE CRUD OPERATIONS
// ============================================================================

// CreateAgent creates a new agent with validation, caching, and event publishing
func (s *AgentServiceImpl) CreateAgent(ctx context.Context, agent *models.Agent) error {
	// Validate input
	if err := s.validateAgent(agent); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}

	// Set defaults if not provided
	if agent.Status == "" {
		agent.Status = "active"
	}

	// Persist to database using GORM
	if err := s.agentRepo.Create(ctx, agent); err != nil {
		return fmt.Errorf("failed to create agent: %w", err)
	}

	// Invalidate related caches
	s.invalidateProjectCaches(ctx, agent.ProjectID)

	// Publish event
	s.publishAgentEvent(ctx, &AgentEvent{
		AgentID:   agent.ID,
		EventType: "agent.created",
		Data: map[string]interface{}{
			"agent_id":   agent.ID,
			"project_id": agent.ProjectID,
			"name":       agent.Name,
			"status":     agent.Status,
		},
		Timestamp: time.Now(),
	})

	return nil
}

// GetAgent retrieves an agent by ID with caching
func (s *AgentServiceImpl) GetAgent(ctx context.Context, id string) (*models.Agent, error) {
	if id == "" {
		return nil, errors.New("agent ID is required")
	}

	// Try cache first (cache-aside pattern)
	cacheKey := "agent:" + id
	if cached, err := s.getFromCache(ctx, cacheKey); cached != nil && err == nil {
		slog.Info("[CACHE HIT] Retrieved agent from cache", "id", id)
		return cached, nil
	}

	// Cache miss - fetch from database using GORM
	agent, err := s.agentRepo.GetByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get agent: %w", err)
	}

	// Populate cache (non-blocking)
	asyncFireAndForget(func(ctx context.Context) {
		if err := s.setInCache(ctx, cacheKey, agent); err != nil {
			slog.Error("Warning: Failed to cache agent", "error", id, "error", err)
		}
	})

	return agent, nil
}

// ListAgents lists all agents with optional caching
func (s *AgentServiceImpl) ListAgents(ctx context.Context) ([]*models.Agent, error) {
	// Try cache first for full list
	cacheKey := "agents:all"
	if cached, err := s.getAgentsFromCache(ctx, cacheKey); cached != nil && err == nil {
		slog.Info("[CACHE HIT] Retrieved agents list from cache")
		return cached, nil
	}

	// Fetch from database using GORM
	agents, err := s.agentRepo.List(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to list agents: %w", err)
	}

	// Cache the result (non-blocking)
	asyncFireAndForget(func(ctx context.Context) {
		if err := s.setAgentsInCache(ctx, cacheKey, agents); err != nil {
			slog.Error("Warning: Failed to cache agents list", "error", err)
		}
	})

	return agents, nil
}

// ============================================================================
// UPDATE OPERATIONS
// ============================================================================

// UpdateAgent updates an existing agent with validation and cache invalidation
func (s *AgentServiceImpl) UpdateAgent(ctx context.Context, agent *models.Agent) error {
	if err := s.validateAgent(agent); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}

	// Update using GORM
	if err := s.agentRepo.Update(ctx, agent); err != nil {
		return fmt.Errorf("failed to update agent: %w", err)
	}

	// Invalidate caches
	agentCacheKey := "agent:" + agent.ID
	if s.cache != nil {
		if err := s.cache.Delete(ctx, agentCacheKey); err != nil {
			slog.Warn("failed to invalidate agent cache", "key", agentCacheKey, "error", err)
		}
	}

	s.invalidateProjectCaches(ctx, agent.ProjectID)

	// Publish event
	s.publishAgentEvent(ctx, &AgentEvent{
		AgentID:   agent.ID,
		EventType: "agent.updated",
		Data: map[string]interface{}{
			"agent_id":   agent.ID,
			"project_id": agent.ProjectID,
			"name":       agent.Name,
			"status":     agent.Status,
		},
		Timestamp: time.Now(),
	})

	return nil
}

// UpdateAgentStatus updates only the status field of an agent
func (s *AgentServiceImpl) UpdateAgentStatus(ctx context.Context, id, status string) error {
	if id == "" {
		return errors.New("agent ID is required")
	}
	if status == "" {
		return errors.New("status is required")
	}

	// Validate status
	validStatuses := map[string]bool{
		"active":  true,
		"idle":    true,
		"error":   true,
		"offline": true,
		"paused":  true,
	}
	if !validStatuses[status] {
		return fmt.Errorf("invalid status: %s", status)
	}

	// Get existing agent to check old status and project ID
	agent, err := s.agentRepo.GetByID(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to get agent: %w", err)
	}

	oldStatus := agent.Status

	// Update status using repository method
	if err := s.agentRepo.UpdateStatus(ctx, id, status); err != nil {
		return fmt.Errorf("failed to update agent status: %w", err)
	}

	// Invalidate caches
	agentCacheKey := "agent:" + id
	if s.cache != nil {
		if err := s.cache.Delete(ctx, agentCacheKey); err != nil {
			slog.Warn("failed to invalidate agent cache", "key", agentCacheKey, "error", err)
		}
	}

	s.invalidateProjectCaches(ctx, agent.ProjectID)

	// Publish status change event
	s.publishAgentEvent(ctx, &AgentEvent{
		AgentID:   id,
		EventType: "agent.status_changed",
		Data: map[string]interface{}{
			"agent_id":   id,
			"old_status": oldStatus,
			"new_status": status,
		},
		Timestamp: time.Now(),
	})

	return nil
}

// ============================================================================
// DELETE OPERATIONS
// ============================================================================

// DeleteAgent deletes an agent with cache invalidation
func (s *AgentServiceImpl) DeleteAgent(ctx context.Context, id string) error {
	if id == "" {
		return errors.New("agent ID is required")
	}

	// Get agent first to know which project cache to invalidate
	agent, err := s.agentRepo.GetByID(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to get agent for deletion: %w", err)
	}

	// Delete agent using GORM
	if err := s.agentRepo.Delete(ctx, id); err != nil {
		return fmt.Errorf("failed to delete agent: %w", err)
	}

	// Invalidate caches
	agentCacheKey := "agent:" + id
	if s.cache != nil {
		if err := s.cache.Delete(ctx, agentCacheKey); err != nil {
			slog.Warn("failed to invalidate agent cache", "key", agentCacheKey, "error", err)
		}
	}

	s.invalidateProjectCaches(ctx, agent.ProjectID)

	// Publish event
	s.publishAgentEvent(ctx, &AgentEvent{
		AgentID:   id,
		EventType: "agent.deleted",
		Data: map[string]interface{}{
			"agent_id":   id,
			"project_id": agent.ProjectID,
		},
		Timestamp: time.Now(),
	})

	return nil
}

// ============================================================================
// EVENT NOTIFICATION
// ============================================================================

// NotifyAgentEvent publishes an agent event
// This allows external systems to notify about agent events
func (s *AgentServiceImpl) NotifyAgentEvent(ctx context.Context, event *AgentEvent) error {
	if event == nil {
		return errors.New("event cannot be nil")
	}

	if event.AgentID == "" {
		return errors.New("agent_id is required in event")
	}

	if event.EventType == "" {
		return errors.New("event_type is required in event")
	}

	// Set timestamp if not provided
	if event.Timestamp.IsZero() {
		event.Timestamp = time.Now()
	}

	// Publish the event
	s.publishAgentEvent(ctx, event)

	// For certain events, invalidate cache
	if event.EventType == "agent.activity" || event.EventType == "agent.health_check" {
		agentCacheKey := "agent:" + event.AgentID
		if s.cache != nil {
			if err := s.cache.Delete(ctx, agentCacheKey); err != nil {
				slog.Warn("failed to invalidate agent cache on event", "key", agentCacheKey, "error", err)
			}
		}
	}

	return nil
}

// ============================================================================
// VALIDATION AND UTILITY METHODS
// ============================================================================

// validateAgent validates agent business rules
func (s *AgentServiceImpl) validateAgent(agent *models.Agent) error {
	if agent.ID == "" {
		return errors.New("agent ID is required")
	}
	if agent.ProjectID == "" {
		return errors.New("project ID is required")
	}
	if agent.Name == "" {
		return errors.New("agent name is required")
	}
	if len(agent.Name) > maxAgentNameLength {
		return fmt.Errorf("agent name must be less than %d characters", maxAgentNameLength)
	}

	// Validate status if provided
	if agent.Status != "" {
		validStatuses := map[string]bool{
			"active":  true,
			"idle":    true,
			"error":   true,
			"offline": true,
			"paused":  true,
		}
		if !validStatuses[agent.Status] {
			return fmt.Errorf("invalid status: %s", agent.Status)
		}
	}

	return nil
}

// GetAgentsByProject retrieves all agents for a specific project
func (s *AgentServiceImpl) GetAgentsByProject(ctx context.Context, projectID string) ([]*models.Agent, error) {
	if projectID == "" {
		return nil, errors.New("project ID is required")
	}

	// Try cache first
	cacheKey := "agents:project:" + projectID
	if cached, err := s.getAgentsFromCache(ctx, cacheKey); cached != nil && err == nil {
		slog.Info("[CACHE HIT] Retrieved project agents from cache")
		return cached, nil
	}

	// Fetch from database
	agents, err := s.agentRepo.GetByProjectID(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to get agents by project: %w", err)
	}

	// Cache the result (non-blocking)
	asyncFireAndForget(func(ctx context.Context) {
		if err := s.setAgentsInCache(ctx, cacheKey, agents); err != nil {
			slog.Error("Warning: Failed to cache project agents", "error", err)
		}
	})

	return agents, nil
}

// GetAgentHealth calculates health metrics for an agent
func (s *AgentServiceImpl) GetAgentHealth(ctx context.Context, agentID string) (*AgentHealth, error) {
	agent, err := s.GetAgent(ctx, agentID)
	if err != nil {
		return nil, err
	}

	// Parse metadata for health metrics
	var metadata map[string]interface{}
	if agent.Metadata != nil {
		if err := json.Unmarshal(agent.Metadata, &metadata); err != nil {
			slog.Error("Warning: Failed to parse agent metadata", "error", err)
			metadata = make(map[string]interface{})
		}
	}

	health := &AgentHealth{
		AgentID:   agentID,
		Status:    agent.Status,
		Healthy:   agent.Status == "active",
		LastCheck: time.Now(),
		Metrics:   metadata,
	}

	return health, nil
}

// ============================================================================
// PRIVATE HELPER METHODS
// ============================================================================

// Cache helper functions

func (s *AgentServiceImpl) getFromCache(ctx context.Context, key string) (*models.Agent, error) {
	if s.cache == nil {
		return nil, errors.New("cache not available")
	}

	var agent models.Agent
	if err := s.cache.Get(ctx, key, &agent); err != nil {
		return nil, err
	}

	return &agent, nil
}

func (s *AgentServiceImpl) setInCache(ctx context.Context, key string, agent *models.Agent) error {
	if s.cache == nil {
		return nil
	}

	return s.cache.Set(ctx, key, agent)
}

func (s *AgentServiceImpl) getAgentsFromCache(ctx context.Context, key string) ([]*models.Agent, error) {
	if s.cache == nil {
		return nil, errors.New("cache not available")
	}

	var agents []*models.Agent
	if err := s.cache.Get(ctx, key, &agents); err != nil {
		return nil, err
	}

	return agents, nil
}

func (s *AgentServiceImpl) setAgentsInCache(ctx context.Context, key string, agents []*models.Agent) error {
	if s.cache == nil {
		return nil
	}

	return s.cache.Set(ctx, key, agents)
}

func (s *AgentServiceImpl) invalidateProjectCaches(ctx context.Context, projectID string) {
	if s.cache == nil {
		return
	}

	// Invalidate project-specific agent cache
	projectAgentsKey := "agents:project:" + projectID
	if err := s.cache.Delete(ctx, projectAgentsKey); err != nil {
		slog.Warn("failed to invalidate project agents cache", "error", err)
	}

	// Invalidate full agents list cache
	allAgentsKey := "agents:all"
	if err := s.cache.Delete(ctx, allAgentsKey); err != nil {
		slog.Warn("failed to invalidate all agents cache", "error", err)
	}
}

func (s *AgentServiceImpl) publishAgentEvent(_ context.Context, event *AgentEvent) {
	if s.natsConn == nil {
		return
	}

	payload, err := json.Marshal(event)
	if err != nil {
		slog.Error("Warning: Failed to marshal agent event", "error", err)
		return
	}

	subject := "agents." + event.EventType
	if err := s.natsConn.Publish(subject, payload); err != nil {
		slog.Error("Warning: Failed to publish agent event", "error", event.EventType, "error", err)
	} else {
		slog.Info("[EVENT PUBLISHED] for agent", "detail", event.EventType, "id", event.AgentID)
	}
}

// AgentHealth represents the health status of an agent
type AgentHealth struct {
	AgentID   string                 `json:"agent_id"`
	Status    string                 `json:"status"`
	Healthy   bool                   `json:"healthy"`
	LastCheck time.Time              `json:"last_check"`
	Metrics   map[string]interface{} `json:"metrics,omitempty"`
}
