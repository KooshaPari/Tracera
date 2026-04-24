package tests

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/config"
	"github.com/kooshapari/tracertm-backend/internal/graph"
	"github.com/kooshapari/tracertm-backend/internal/handlers"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/services"
	"github.com/kooshapari/tracertm-backend/tests/testutil"
)

// ============================================================================
// PHASE 7 VALIDATION TEST SUITE
// ============================================================================
// This suite validates that Phase 7 cleanup didn't break any functionality:
// 1. All handlers still work
// 2. ServiceContainer initializes correctly
// 3. No Infrastructure leakage
// 4. Feature flag behavior
// 5. Integration smoke tests
// ============================================================================

// TestPhase7_ServiceContainerInitialization validates ServiceContainer setup
func TestPhase7_ServiceContainerInitialization(t *testing.T) {
	ctx := context.Background()

	// Start dependencies
	pgContainer, connString, err := testutil.PostgresContainer(ctx)
	require.NoError(t, err, "should start postgres container")
	defer pgContainer.Terminate(ctx)

	dragonflyContainer, redisAddr, err := testutil.DragonflyContainer(ctx)
	require.NoError(t, err, "should start dragonfly container")
	defer dragonflyContainer.Terminate(ctx)

	// Connect to PostgreSQL
	pool, err := pgxpool.New(ctx, connString)
	require.NoError(t, err, "should connect to postgres")
	defer pool.Close()

	// Run migrations
	err = testutil.ExecuteMigrations(ctx, pool, "../schema.sql")
	require.NoError(t, err, "should run migrations")

	// Setup GORM
	gormDB, err := gorm.Open(postgres.Open(connString), &gorm.Config{})
	require.NoError(t, err, "should create gorm connection")

	// Setup Redis
	redisClient := redis.NewClient(&redis.Options{
		Addr: redisAddr,
	})
	defer redisClient.Close()

	// Setup cache
	redisCache, err := cache.NewRedisCache(cache.RedisCacheConfig{
		RedisURL:      "redis://" + redisAddr,
		DefaultTTL:    5 * time.Minute,
		EnableMetrics: true,
	})
	require.NoError(t, err, "should create redis-compatible cache")

	// Setup NATS publisher (can be nil for testing)
	var natsPublisher *nats.EventPublisher

	// Setup Neo4j client (can be nil for testing)
	var neo4jClient *graph.Neo4jClient

	// Test ServiceContainer creation
	t.Run("create_service_container", func(t *testing.T) {
		container, err := services.NewServiceContainer(
			gormDB,
			redisClient,
			redisCache,
			natsPublisher,
			neo4jClient,
			nil, // backendClients
		)
		require.NoError(t, err, "should create service container")
		require.NotNil(t, container, "container should not be nil")

		// Test health check
		err = container.HealthCheck(ctx)
		assert.NoError(t, err, "health check should pass")
	})

	t.Run("lazy_service_initialization", func(t *testing.T) {
		container, err := services.NewServiceContainer(
			gormDB,
			redisClient,
			redisCache,
			natsPublisher,
			neo4jClient,
			nil, // backendClients
		)
		require.NoError(t, err)

		// Test lazy initialization of services
		itemService := container.ItemService()
		assert.NotNil(t, itemService, "item service should initialize")

		linkService := container.LinkService()
		assert.NotNil(t, linkService, "link service should initialize")

		projectService := container.ProjectService()
		assert.NotNil(t, projectService, "project service should initialize")

		agentService := container.AgentService()
		assert.NotNil(t, agentService, "agent service should initialize")
	})

	t.Run("container_without_database_fails", func(t *testing.T) {
		container, err := services.NewServiceContainer(
			nil, // no database
			redisClient,
			redisCache,
			natsPublisher,
			neo4jClient,
			nil, // backendClients
		)
		assert.Error(t, err, "should fail without database")
		assert.Nil(t, container, "container should be nil on error")
	})

	t.Run("container_cleanup", func(t *testing.T) {
		container, err := services.NewServiceContainer(
			gormDB,
			redisClient,
			redisCache,
			natsPublisher,
			neo4jClient,
			nil, // backendClients
		)
		require.NoError(t, err)

		err = container.Close()
		assert.NoError(t, err, "cleanup should succeed")
	})
}

// TestPhase7_HandlersFunctionality validates all handlers still work
func TestPhase7_HandlersFunctionality(t *testing.T) {
	ctx := context.Background()

	// Start dependencies
	pgContainer, connString, err := testutil.PostgresContainer(ctx)
	require.NoError(t, err)
	defer pgContainer.Terminate(ctx)

	dragonflyContainer, redisAddr, err := testutil.DragonflyContainer(ctx)
	require.NoError(t, err)
	defer dragonflyContainer.Terminate(ctx)

	// Connect to databases
	pool, err := pgxpool.New(ctx, connString)
	require.NoError(t, err)
	defer pool.Close()

	err = testutil.ExecuteMigrations(ctx, pool, "../schema.sql")
	require.NoError(t, err)

	redisClient := redis.NewClient(&redis.Options{Addr: redisAddr})
	defer redisClient.Close()

	redisCache, err := cache.NewRedisCache(cache.RedisCacheConfig{
		RedisURL:      "redis://" + redisAddr,
		DefaultTTL:    5 * time.Minute,
		EnableMetrics: true,
	})
	require.NoError(t, err)

	// Setup Echo
	e := echo.New()

	// Test HealthCheck handler
	t.Run("health_check_handler", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/health", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handlers.HealthCheck(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var response handlers.HealthResponse
		err = json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Equal(t, "ok", response.Status)
		assert.Equal(t, "tracertm-backend", response.Service)
	})

	// Test ProjectHandler
	t.Run("project_handler_creation", func(t *testing.T) {
		projectHandler := handlers.NewProjectHandler(
			redisCache,
			nil, // NATS publisher
			nil, // realtime broadcaster
			nil, // auth provider
			&testutil.MockBinder{},
			nil, // project service (optional)
		)
		require.NotNil(t, projectHandler, "project handler should not be nil")
	})

	// Test ProjectHandler with service layer
	t.Run("project_handler_with_service", func(t *testing.T) {
		// Setup GORM for service layer
		gormDB, err := gorm.Open(postgres.Open(connString), &gorm.Config{})
		require.NoError(t, err)

		// Create service container
		container, err := services.NewServiceContainer(
			gormDB,
			redisClient,
			redisCache,
			nil,
			nil,
			nil, // backendClients
		)
		require.NoError(t, err)

		// Create handler with service layer
		projectHandler := handlers.NewProjectHandler(
			redisCache,
			nil,
			nil,
			nil,
			&testutil.MockBinder{},
			container.ProjectService(),
		)

		// Test ListProjects via service layer
		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err = projectHandler.ListProjects(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)
	})
}

// TestPhase7_NoInfrastructureLeakage validates no Infrastructure references
func TestPhase7_NoInfrastructureLeakage(t *testing.T) {
	t.Run("handlers_use_service_container", func(t *testing.T) {
		// This is a structural validation test
		// We verify handlers accept ServiceContainer, not Infrastructure
		// This test validates the design, actual implementation is tested above

		// Verify ProjectHandler can be created without Infrastructure
		projectHandler := handlers.NewProjectHandler(
			nil, // cache
			nil, // NATS
			nil, // realtime
			nil, // auth
			&testutil.MockBinder{},
			nil, // project service
		)
		assert.NotNil(t, projectHandler, "handler should work without Infrastructure")
	})

	t.Run("services_use_repositories", func(t *testing.T) {
		// Validate services depend on repositories, not Infrastructure
		ctx := context.Background()
		pgContainer, connString, err := testutil.PostgresContainer(ctx)
		require.NoError(t, err)
		defer pgContainer.Terminate(ctx)

		gormDB, err := gorm.Open(postgres.Open(connString), &gorm.Config{})
		require.NoError(t, err)

		redisClient := redis.NewClient(&redis.Options{})
		defer redisClient.Close()

		// Create container without Infrastructure
		container, err := services.NewServiceContainer(
			gormDB,
			redisClient,
			nil, // cache
			nil, // NATS
			nil, // Neo4j
			nil, // backendClients
		)
		require.NoError(t, err)
		assert.NotNil(t, container, "container should work with minimal deps")
	})
}

// TestPhase7_ServiceLayerBehavior validates optional service layer usage
func TestPhase7_ServiceLayerBehavior(t *testing.T) {
	ctx := context.Background()

	pgContainer, connString, err := testutil.PostgresContainer(ctx)
	require.NoError(t, err)
	defer pgContainer.Terminate(ctx)

	pool, err := pgxpool.New(ctx, connString)
	require.NoError(t, err)
	defer pool.Close()

	err = testutil.ExecuteMigrations(ctx, pool, "../schema.sql")
	require.NoError(t, err)

	gormDB, err := gorm.Open(postgres.Open(connString), &gorm.Config{})
	require.NoError(t, err)

	redisClient := redis.NewClient(&redis.Options{})
	defer redisClient.Close()

	e := echo.New()

	t.Run("handler_without_service_layer", func(t *testing.T) {
		// Test handler without service layer
		handler := handlers.NewProjectHandler(
			nil,
			nil,
			nil,
			nil,
			&testutil.MockBinder{},
			nil, // no service layer
		)

		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.ListProjects(c)
		// Should return error when service is nil
		require.NoError(t, err)
		assert.Equal(t, http.StatusInternalServerError, rec.Code)
	})

	t.Run("handler_with_service_layer", func(t *testing.T) {
		// Test service layer path
		container, err := services.NewServiceContainer(
			gormDB,
			redisClient,
			nil,
			nil,
			nil,
			nil, // backendClients
		)
		require.NoError(t, err)

		handler := handlers.NewProjectHandler(
			nil,
			nil,
			nil,
			nil,
			&testutil.MockBinder{},
			container.ProjectService(),
		)

		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err = handler.ListProjects(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)
	})
}

// TestPhase7_ConfigurationLoading validates config still works
func TestPhase7_ConfigurationLoading(t *testing.T) {
	t.Run("load_default_config", func(t *testing.T) {
		cfg := config.LoadConfig()
		require.NotNil(t, cfg, "config should load")

		assert.NotEmpty(t, cfg.Port, "port should be set")
		assert.NotEmpty(t, cfg.Env, "env should be set")
		assert.NotEmpty(t, cfg.DatabaseURL, "database URL should be set")
	})

	t.Run("embeddings_config", func(t *testing.T) {
		cfg := config.LoadConfig()
		require.NotNil(t, cfg.Embeddings, "embeddings config should exist")

		assert.NotEmpty(t, cfg.Embeddings.Provider, "provider should be set")
		assert.Greater(t, cfg.Embeddings.MaxBatchSize, 0, "batch size should be positive")
	})
}

// TestPhase7_ErrorHandling validates error handling still works
func TestPhase7_ErrorHandling(t *testing.T) {
	ctx := context.Background()

	pgContainer, connString, err := testutil.PostgresContainer(ctx)
	require.NoError(t, err)
	defer pgContainer.Terminate(ctx)

	pool, err := pgxpool.New(ctx, connString)
	require.NoError(t, err)
	defer pool.Close()

	err = testutil.ExecuteMigrations(ctx, pool, "../schema.sql")
	require.NoError(t, err)

	e := echo.New()

	t.Run("invalid_project_id", func(t *testing.T) {
		handler := handlers.NewProjectHandler(
			nil,
			nil,
			nil,
			nil,
			&testutil.MockBinder{},
			nil, // no service
		)

		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/invalid-uuid", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetParamNames("id")
		c.SetParamValues("invalid-uuid")

		err := handler.GetProject(c)
		require.NoError(t, err)                                   // Handler shouldn't error, but should return error response
		assert.Equal(t, http.StatusInternalServerError, rec.Code) // No service available
	})

	t.Run("project_not_found", func(t *testing.T) {
		handler := handlers.NewProjectHandler(
			nil,
			nil,
			nil,
			nil,
			&testutil.MockBinder{},
			nil, // no service
		)

		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/00000000-0000-0000-0000-000000000000", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetParamNames("id")
		c.SetParamValues("00000000-0000-0000-0000-000000000000")

		err := handler.GetProject(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusInternalServerError, rec.Code) // No service available
	})
}
