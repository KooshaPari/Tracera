package services

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"sync"

	"github.com/redis/go-redis/v9"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/clients"
	"github.com/kooshapari/tracertm-backend/internal/graph"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// PythonBackendClients holds HTTP clients for the Python backend (AI, Spec Analytics, Execution, Workflow, Chaos).
// Injected into ServiceContainer so handlers use the container instead of Infrastructure.
type PythonBackendClients struct {
	Python        *clients.PythonServiceClient
	AI            *clients.AIClient
	SpecAnalytics *clients.SpecAnalyticsClient
	Execution     *clients.ExecutionClient
	Workflow      *clients.WorkflowClient
	Chaos         *clients.ChaosClient
}

// ServiceContainer implements ServiceRegistry
// It's the single dependency injection container for the application
// Replace passing Infrastructure everywhere with this container
type ServiceContainer struct {
	// Thread-safety for lazy initialization
	mu sync.RWMutex

	// Low-level dependencies
	db            *gorm.DB
	redis         *redis.Client
	cache         cache.Cache
	natsPublisher *nats.EventPublisher
	neo4jClient   *graph.Neo4jClient

	// Lazy-loaded services
	itemService      ItemService
	linkService      LinkService
	projectService   ProjectService
	agentService     AgentService
	codeIndexService CodeIndexService
	// temporalService is defined in temporal_service.go, not included here
	searchService        SearchService
	graphAnalysisService GraphAnalysisService
	cacheService         CacheService
	eventService         EventService
	notificationService  *NotificationService

	// Python backend HTTP clients (optional; nil when Python backend not configured)
	backendClients *PythonBackendClients

	// Initialization flags for debugging/monitoring
	itemServiceInitialized          bool
	linkServiceInitialized          bool
	projectServiceInitialized       bool
	agentServiceInitialized         bool
	codeIndexServiceInitialized     bool
	searchServiceInitialized        bool
	graphAnalysisServiceInitialized bool
	cacheServiceInitialized         bool
	eventServiceInitialized         bool
	notificationServiceInitialized  bool
}

// NewServiceContainer creates and initializes a service container.
// backendClients is optional; when nil, AIClient/SpecAnalyticsClient/etc. return nil
// and handlers may skip registering Python-backed routes.
func NewServiceContainer(
	db *gorm.DB,
	redis *redis.Client,
	cache cache.Cache,
	natsPublisher *nats.EventPublisher,
	neo4jClient *graph.Neo4jClient,
	backendClients *PythonBackendClients,
) (*ServiceContainer, error) {
	if db == nil {
		return nil, errors.New("database connection required")
	}

	container := &ServiceContainer{
		db:             db,
		redis:          redis,
		cache:          cache,
		natsPublisher:  natsPublisher,
		neo4jClient:    neo4jClient,
		backendClients: backendClients,
	}

	return container, nil
}

// ============================================================================
// PYTHON BACKEND CLIENT ACCESSORS (ServiceContainer as single source of truth)
// ============================================================================

// PythonClient returns the Python backend client, or nil if not set.
func (sc *ServiceContainer) PythonClient() *clients.PythonServiceClient {
	if sc.backendClients == nil {
		return nil
	}
	return sc.backendClients.Python
}

// AIClient returns the AI client, or nil if not set.
func (sc *ServiceContainer) AIClient() *clients.AIClient {
	if sc.backendClients == nil {
		return nil
	}
	return sc.backendClients.AI
}

// SpecAnalyticsClient returns the spec analytics client, or nil if not set.
func (sc *ServiceContainer) SpecAnalyticsClient() *clients.SpecAnalyticsClient {
	if sc.backendClients == nil {
		return nil
	}
	return sc.backendClients.SpecAnalytics
}

// ExecutionClient returns the execution client, or nil if not set.
func (sc *ServiceContainer) ExecutionClient() *clients.ExecutionClient {
	if sc.backendClients == nil {
		return nil
	}
	return sc.backendClients.Execution
}

// WorkflowClient returns the workflow client, or nil if not set.
func (sc *ServiceContainer) WorkflowClient() *clients.WorkflowClient {
	if sc.backendClients == nil {
		return nil
	}
	return sc.backendClients.Workflow
}

// ChaosClient returns the chaos client, or nil if not set.
func (sc *ServiceContainer) ChaosClient() *clients.ChaosClient {
	if sc.backendClients == nil {
		return nil
	}
	return sc.backendClients.Chaos
}

// ============================================================================
// SERVICE ACCESSORS (Lazy initialization)
// ============================================================================

// ItemService returns the item service (implements ServiceRegistry)
// Thread-safe lazy initialization using double-checked locking pattern
func (sc *ServiceContainer) ItemService() ItemService {
	// Fast path: check if already initialized (read lock)
	sc.mu.RLock()
	if sc.itemService != nil {
		defer sc.mu.RUnlock()
		return sc.itemService
	}
	sc.mu.RUnlock()

	// Slow path: initialize service (write lock)
	sc.mu.Lock()
	defer sc.mu.Unlock()

	// Double-check: another goroutine might have initialized while we waited
	if sc.itemService == nil {
		itemRepo := repository.NewItemRepository(sc.db)
		linkRepo := repository.NewLinkRepository(sc.db)

		// ItemService expects *nats.Conn but we only have EventPublisher
		// For now, pass nil - services handle nil gracefully
		sc.itemService = NewItemService(
			itemRepo,
			linkRepo,
			sc.redis,
			nil, // NATS conn - will be nil for now
		)
		sc.itemServiceInitialized = true
	}
	return sc.itemService
}

// LinkService returns the link service
// Thread-safe lazy initialization using double-checked locking pattern
func (sc *ServiceContainer) LinkService() LinkService {
	sc.mu.RLock()
	if sc.linkService != nil {
		defer sc.mu.RUnlock()
		return sc.linkService
	}
	sc.mu.RUnlock()

	sc.mu.Lock()
	defer sc.mu.Unlock()

	if sc.linkService == nil {
		linkRepo := repository.NewLinkRepository(sc.db)
		itemRepo := repository.NewItemRepository(sc.db)

		sc.linkService = NewLinkService(
			linkRepo,
			itemRepo,
			nil, // NATS conn - will be nil for now
		)
		sc.linkServiceInitialized = true
	}
	return sc.linkService
}

// ProjectService returns the project service
// Thread-safe lazy initialization using double-checked locking pattern
func (sc *ServiceContainer) ProjectService() ProjectService {
	sc.mu.RLock()
	if sc.projectService != nil {
		defer sc.mu.RUnlock()
		return sc.projectService
	}
	sc.mu.RUnlock()

	sc.mu.Lock()
	defer sc.mu.Unlock()

	if sc.projectService == nil {
		projectRepo := repository.NewProjectRepository(sc.db)
		itemRepo := repository.NewItemRepository(sc.db)

		// Note: NATS integration fix pending - EventPublisher doesn't expose conn
		// Currently passing nil to avoid compilation errors
		sc.projectService = NewProjectServiceImpl(
			projectRepo,
			itemRepo,
			sc.cache,
			nil,   // natsConn - needs refactoring
			sc.db, // Pass DB for transaction support
		)
		sc.projectServiceInitialized = true
	}
	return sc.projectService
}

// AgentService returns the agent service
// Thread-safe lazy initialization using double-checked locking pattern
func (sc *ServiceContainer) AgentService() AgentService {
	sc.mu.RLock()
	if sc.agentService != nil {
		defer sc.mu.RUnlock()
		return sc.agentService
	}
	sc.mu.RUnlock()

	sc.mu.Lock()
	defer sc.mu.Unlock()

	if sc.agentService == nil {
		agentRepo := repository.NewAgentRepository(sc.db)
		sc.agentService = NewAgentService(agentRepo, nil) // NATS conn - will be nil for now
		sc.agentServiceInitialized = true
	}
	return sc.agentService
}

// CodeIndexService returns the code index service
// Thread-safe lazy initialization (placeholder)
func (sc *ServiceContainer) CodeIndexService() CodeIndexService {
	sc.mu.RLock()
	if sc.codeIndexService != nil {
		defer sc.mu.RUnlock()
		return sc.codeIndexService
	}
	sc.mu.RUnlock()

	sc.mu.Lock()
	defer sc.mu.Unlock()

	if sc.codeIndexService == nil {
		// Placeholder - implement when needed
		slog.Warn("Warning: CodeIndexService not yet implemented")
		sc.codeIndexServiceInitialized = true
	}
	return sc.codeIndexService
}

// Note: TemporalService is implemented in temporal_service.go
// We don't include it in the container to avoid conflicts

// SearchService returns the search service
// Thread-safe lazy initialization (placeholder)
func (sc *ServiceContainer) SearchService() SearchService {
	sc.mu.RLock()
	if sc.searchService != nil {
		defer sc.mu.RUnlock()
		return sc.searchService
	}
	sc.mu.RUnlock()

	sc.mu.Lock()
	defer sc.mu.Unlock()

	if sc.searchService == nil {
		// Placeholder - implement when needed
		slog.Warn("Warning: SearchService not yet implemented")
		sc.searchServiceInitialized = true
	}
	return sc.searchService
}

// GraphAnalysisService returns the graph analysis service
// Thread-safe lazy initialization (placeholder)
func (sc *ServiceContainer) GraphAnalysisService() GraphAnalysisService {
	sc.mu.RLock()
	if sc.graphAnalysisService != nil {
		defer sc.mu.RUnlock()
		return sc.graphAnalysisService
	}
	sc.mu.RUnlock()

	sc.mu.Lock()
	defer sc.mu.Unlock()

	if sc.graphAnalysisService == nil {
		// Placeholder - implement when needed
		slog.Warn("Warning: GraphAnalysisService not yet implemented")
		sc.graphAnalysisServiceInitialized = true
	}
	return sc.graphAnalysisService
}

// CacheService returns the cache service
// Thread-safe lazy initialization (placeholder)
func (sc *ServiceContainer) CacheService() CacheService {
	sc.mu.RLock()
	if sc.cacheService != nil {
		defer sc.mu.RUnlock()
		return sc.cacheService
	}
	sc.mu.RUnlock()

	sc.mu.Lock()
	defer sc.mu.Unlock()

	if sc.cacheService == nil {
		// Placeholder - implement when needed
		slog.Warn("Warning: CacheService not yet implemented")
		sc.cacheServiceInitialized = true
	}
	return sc.cacheService
}

// EventService returns the event service
// Thread-safe lazy initialization (placeholder)
func (sc *ServiceContainer) EventService() EventService {
	sc.mu.RLock()
	if sc.eventService != nil {
		defer sc.mu.RUnlock()
		return sc.eventService
	}
	sc.mu.RUnlock()

	sc.mu.Lock()
	defer sc.mu.Unlock()

	if sc.eventService == nil {
		// Placeholder - implement when needed
		slog.Warn("Warning: EventService not yet implemented")
		sc.eventServiceInitialized = true
	}
	return sc.eventService
}

// NotificationService returns the notification service
// Thread-safe lazy initialization
func (sc *ServiceContainer) NotificationService() *NotificationService {
	sc.mu.RLock()
	if sc.notificationService != nil {
		defer sc.mu.RUnlock()
		return sc.notificationService
	}
	sc.mu.RUnlock()

	sc.mu.Lock()
	defer sc.mu.Unlock()

	if sc.notificationService == nil {
		sc.notificationService = NewNotificationService(sc.db, newNotificationEventBus(sc.natsPublisher))
		sc.notificationServiceInitialized = true
	}
	return sc.notificationService
}

// ============================================================================
// TRANSACTION SUPPORT
// ============================================================================

// WithTx executes a function within a database transaction
// Use this for operations that span multiple services
func (sc *ServiceContainer) WithTx(
	ctx context.Context,
	fn func(*TransactionContext) error,
) error {
	// Validate function is not nil
	if fn == nil {
		panic("transaction function cannot be nil")
	}

	// Begin transaction
	tx := sc.db.Begin()
	if err := tx.Error; err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}

	// Create transaction context (context + raw tx for callbacks)
	txCtx := NewTransactionContext(ctx, tx)

	// Execute function
	if err := fn(txCtx); err != nil {
		// Rollback on error
		if rollbackErr := tx.Rollback().Error; rollbackErr != nil {
			slog.Error("Warning: Failed to rollback transaction", "error", rollbackErr)
		}
		return err
	}

	// Commit transaction
	if err := tx.Commit().Error; err != nil {
		return fmt.Errorf("failed to commit transaction: %w", err)
	}

	return nil
}

// ============================================================================
// HEALTH CHECK
// ============================================================================

// HealthCheck verifies that all critical services are operational
func (sc *ServiceContainer) HealthCheck(ctx context.Context) error {
	// Check database
	if sc.db == nil {
		return errors.New("database connection is nil")
	}

	sqlDB, err := sc.db.DB()
	if err != nil {
		return fmt.Errorf("failed to get database: %w", err)
	}

	if err := sqlDB.PingContext(ctx); err != nil {
		return fmt.Errorf("database ping failed: %w", err)
	}

	// Check Redis if available
	if sc.redis != nil {
		if err := sc.redis.Ping(ctx).Err(); err != nil {
			return fmt.Errorf("redis ping failed: %w", err)
		}
	}

	return nil
}

// ============================================================================
// CLEANUP
// ============================================================================

// Close releases all resources held by the service container
func (sc *ServiceContainer) Close() error {
	if sc.notificationService != nil {
		if err := sc.notificationService.Close(); err != nil {
			return err
		}
	}
	// The underlying infrastructure (DB, Redis, NATS, etc.) is closed separately.
	return nil
}
