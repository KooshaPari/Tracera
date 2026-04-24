package services

import (
	"context"
	"errors"
	"sync"
	"testing"
	"time"

	"github.com/DATA-DOG/go-sqlmock"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/graph"
	"github.com/kooshapari/tracertm-backend/internal/nats"
)

const serviceContainerHealthTimeout = 5 * time.Second

func setupTestContainer(t *testing.T) (*ServiceContainer, sqlmock.Sqlmock) {
	// Create mock database (without ping monitoring to avoid GORM init pings)
	db, mock, err := sqlmock.New()
	require.NoError(t, err)

	// Create GORM DB with the mock
	gormDB, err := gorm.Open(postgres.New(postgres.Config{
		Conn: db,
	}), &gorm.Config{})
	require.NoError(t, err)

	// Create container
	container, err := NewServiceContainer(gormDB, nil, nil, nil, nil, nil)
	require.NoError(t, err)

	return container, mock
}

func TestNewServiceContainer(t *testing.T) {
	tests := []struct {
		name    string
		db      *gorm.DB
		wantErr bool
		errMsg  string
	}{
		{
			name:    "nil database",
			db:      nil,
			wantErr: true,
			errMsg:  "database connection required",
		},
		{
			name:    "valid database",
			db:      &gorm.DB{},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			container, err := NewServiceContainer(tt.db, nil, nil, nil, nil, nil)

			if tt.wantErr {
				require.Error(t, err)
				assert.Contains(t, err.Error(), tt.errMsg)
				assert.Nil(t, container)
			} else {
				require.NoError(t, err)
				assert.NotNil(t, container)
			}
		})
	}
}

func TestServiceContainer_ItemService(t *testing.T) {
	container, _ := setupTestContainer(t)

	// First call should initialize the service
	svc1 := container.ItemService()
	assert.NotNil(t, svc1)

	// Second call should return the same instance (lazy singleton)
	svc2 := container.ItemService()
	assert.NotNil(t, svc2)
	assert.Same(t, svc1, svc2, "ItemService should return the same instance")
}

func TestServiceContainer_LinkService(t *testing.T) {
	container, _ := setupTestContainer(t)

	// First call should initialize the service
	svc1 := container.LinkService()
	assert.NotNil(t, svc1)

	// Second call should return the same instance
	svc2 := container.LinkService()
	assert.NotNil(t, svc2)
	assert.Same(t, svc1, svc2, "LinkService should return the same instance")
}

func TestServiceContainer_ProjectService(t *testing.T) {
	container, _ := setupTestContainer(t)

	svc := container.ProjectService()
	assert.NotNil(t, svc)

	// Verify lazy loading
	svc2 := container.ProjectService()
	assert.Same(t, svc, svc2)
}

func TestServiceContainer_AgentService(t *testing.T) {
	container, _ := setupTestContainer(t)

	svc := container.AgentService()
	assert.NotNil(t, svc)

	// Verify lazy loading
	svc2 := container.AgentService()
	assert.Same(t, svc, svc2)
}

func TestServiceContainer_UnimplementedServices(t *testing.T) {
	container, _ := setupTestContainer(t)

	// These services should return nil (not yet implemented)
	t.Run("CodeIndexService", func(t *testing.T) {
		svc := container.CodeIndexService()
		assert.Nil(t, svc)
	})

	// Note: TemporalService is implemented separately in temporal_service.go

	t.Run("SearchService", func(t *testing.T) {
		svc := container.SearchService()
		assert.Nil(t, svc)
	})

	t.Run("GraphAnalysisService", func(t *testing.T) {
		svc := container.GraphAnalysisService()
		assert.Nil(t, svc)
	})

	t.Run("CacheService", func(t *testing.T) {
		svc := container.CacheService()
		assert.Nil(t, svc)
	})

	t.Run("EventService", func(t *testing.T) {
		svc := container.EventService()
		assert.Nil(t, svc)
	})
}

func TestServiceContainer_WithTx(t *testing.T) {
	container, mock := setupTestContainer(t)

	t.Run("successful transaction", func(t *testing.T) {
		// Expect begin, commit
		mock.ExpectBegin()
		mock.ExpectCommit()

		err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
			assert.NotNil(t, txCtx)
			assert.NotNil(t, txCtx.tx)
			return nil
		})

		require.NoError(t, err)
		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("transaction with error", func(t *testing.T) {
		// Expect begin, rollback
		mock.ExpectBegin()
		mock.ExpectRollback()

		testErr := assert.AnError
		err := container.WithTx(context.Background(), func(_ *TransactionContext) error {
			return testErr
		})

		require.Error(t, err)
		assert.Equal(t, testErr, err)
		require.NoError(t, mock.ExpectationsWereMet())
	})
}

func TestServiceContainer_HealthCheck(t *testing.T) {
	t.Run("nil database", func(t *testing.T) {
		container := &ServiceContainer{
			db: nil,
		}

		err := container.HealthCheck(context.Background())
		require.Error(t, err)
		assert.Contains(t, err.Error(), "database connection is nil")
	})

	// Note: Testing "cannot get underlying database" is difficult with GORM
	// as it requires a specific internal state that causes DB() to fail
	// The nil database test above covers the main error path

	t.Run("redis ping failure", func(t *testing.T) {
		// Create mock database
		db, _, err := sqlmock.New()
		require.NoError(t, err)

		gormDB, err := gorm.Open(postgres.New(postgres.Config{
			Conn: db,
		}), &gorm.Config{})
		require.NoError(t, err)

		// Create a mock Redis client with invalid address
		redisClient := redis.NewClient(&redis.Options{
			Addr: "invalid:6379", // Invalid address to simulate failure
		})

		container, err := NewServiceContainer(gormDB, redisClient, nil, nil, nil, nil)
		require.NoError(t, err)

		// Health check should fail due to Redis
		err = container.HealthCheck(context.Background())
		require.Error(t, err)
		// Error will be about ping failure (either redis or database mock ping)
		require.Error(t, err, "health check should fail")
	})
}

func TestServiceContainer_Close(t *testing.T) {
	container, _ := setupTestContainer(t)

	err := container.Close()
	require.NoError(t, err)
}

func TestServiceContainer_WithAllDependencies(t *testing.T) {
	// Create mock database
	db, _, err := sqlmock.New()
	require.NoError(t, err)

	gormDB, err := gorm.Open(postgres.New(postgres.Config{
		Conn: db,
	}), &gorm.Config{})
	require.NoError(t, err)

	// Create container with all dependencies
	container, err := NewServiceContainer(
		gormDB,
		nil,                    // redis
		&cache.RedisCache{},    // cache
		&nats.EventPublisher{}, // nats publisher
		&graph.Neo4jClient{},   // neo4j
		nil,                    // backendClients
	)

	require.NoError(t, err)
	assert.NotNil(t, container)
	assert.NotNil(t, container.db)
	assert.NotNil(t, container.cache)
	assert.NotNil(t, container.natsPublisher)
	assert.NotNil(t, container.neo4jClient)
}

func TestServiceContainer_LazyLoadingMultipleServices(t *testing.T) {
	container, _ := setupTestContainer(t)

	// Load multiple services
	itemSvc := container.ItemService()
	linkSvc := container.LinkService()
	projectSvc := container.ProjectService()
	agentSvc := container.AgentService()

	// Verify all services are initialized
	assert.NotNil(t, itemSvc)
	assert.NotNil(t, linkSvc)
	assert.NotNil(t, projectSvc)
	assert.NotNil(t, agentSvc)

	// Verify they're cached (same instances)
	assert.Same(t, itemSvc, container.ItemService())
	assert.Same(t, linkSvc, container.LinkService())
	assert.Same(t, projectSvc, container.ProjectService())
	assert.Same(t, agentSvc, container.AgentService())
}

func TestTransactionContext(t *testing.T) {
	container, mock := setupTestContainer(t)

	mock.ExpectBegin()
	mock.ExpectCommit()

	var capturedTx *gorm.DB
	err := container.WithTx(context.Background(), func(txCtx *TransactionContext) error {
		capturedTx = txCtx.tx
		assert.NotNil(t, txCtx.tx)
		return nil
	})

	require.NoError(t, err)
	assert.NotNil(t, capturedTx)
	require.NoError(t, mock.ExpectationsWereMet())
}

// ============================================================================
// ADDITIONAL COMPREHENSIVE TESTS
// ============================================================================

func TestNewServiceContainer_Comprehensive(t *testing.T) {
	t.Run("with nil infrastructure components", func(t *testing.T) {
		db, _, err := sqlmock.New()
		require.NoError(t, err)

		gormDB, err := gorm.Open(postgres.New(postgres.Config{
			Conn: db,
		}), &gorm.Config{})
		require.NoError(t, err)

		// Create container with all nil dependencies except DB
		container, err := NewServiceContainer(gormDB, nil, nil, nil, nil, nil)
		require.NoError(t, err)
		assert.NotNil(t, container)
		assert.NotNil(t, container.db)
		assert.Nil(t, container.redis)
		assert.Nil(t, container.cache)
		assert.Nil(t, container.natsPublisher)
		assert.Nil(t, container.neo4jClient)
	})

	t.Run("with all dependencies", func(t *testing.T) {
		db, _, err := sqlmock.New()
		require.NoError(t, err)

		gormDB, err := gorm.Open(postgres.New(postgres.Config{
			Conn: db,
		}), &gorm.Config{})
		require.NoError(t, err)

		redisClient := redis.NewClient(&redis.Options{Addr: "localhost:6379"})
		cacheInstance := &cache.RedisCache{}
		natsPublisher := &nats.EventPublisher{}
		neo4jClient := &graph.Neo4jClient{}

		container, err := NewServiceContainer(
			gormDB,
			redisClient,
			cacheInstance,
			natsPublisher,
			neo4jClient,
			nil, // backendClients
		)

		require.NoError(t, err)
		assert.NotNil(t, container)
		assert.Equal(t, gormDB, container.db)
		assert.Equal(t, redisClient, container.redis)
		assert.Equal(t, cacheInstance, container.cache)
		assert.Equal(t, natsPublisher, container.natsPublisher)
		assert.Equal(t, neo4jClient, container.neo4jClient)
	})
}

func TestLazyServiceInitialization_Comprehensive(t *testing.T) {
	container, _ := setupTestContainer(t)

	t.Run("services are nil before initialization", func(t *testing.T) {
		assert.Nil(t, container.itemService)
		assert.Nil(t, container.linkService)
		assert.Nil(t, container.projectService)
		assert.Nil(t, container.agentService)
	})

	t.Run("first access initializes service", func(t *testing.T) {
		svc := container.ItemService()
		assert.NotNil(t, svc)
		assert.NotNil(t, container.itemService)
	})

	t.Run("subsequent access returns cached instance", func(t *testing.T) {
		svc1 := container.LinkService()
		svc2 := container.LinkService()
		assert.Same(t, svc1, svc2)
	})

	t.Run("different services are independent", func(t *testing.T) {
		itemSvc := container.ItemService()
		linkSvc := container.LinkService()
		projectSvc := container.ProjectService()

		assert.NotNil(t, itemSvc)
		assert.NotNil(t, linkSvc)
		assert.NotNil(t, projectSvc)

		// Verify they're different services
		assert.NotEqual(t, itemSvc, linkSvc)
		assert.NotEqual(t, itemSvc, projectSvc)
		assert.NotEqual(t, linkSvc, projectSvc)
	})
}

func TestServiceCaching_Comprehensive(t *testing.T) {
	t.Run("all services are cached correctly", func(t *testing.T) {
		container, _ := setupTestContainer(t)

		// Initialize all implemented services
		itemSvc1 := container.ItemService()
		linkSvc1 := container.LinkService()
		projectSvc1 := container.ProjectService()
		agentSvc1 := container.AgentService()

		// Access again
		itemSvc2 := container.ItemService()
		linkSvc2 := container.LinkService()
		projectSvc2 := container.ProjectService()
		agentSvc2 := container.AgentService()

		// Verify caching
		assert.Same(t, itemSvc1, itemSvc2)
		assert.Same(t, linkSvc1, linkSvc2)
		assert.Same(t, projectSvc1, projectSvc2)
		assert.Same(t, agentSvc1, agentSvc2)
	})

	t.Run("multiple containers have independent caches", func(t *testing.T) {
		container1, _ := setupTestContainer(t)
		container2, _ := setupTestContainer(t)

		svc1 := container1.ItemService()
		svc2 := container2.ItemService()

		assert.NotSame(t, svc1, svc2)
	})
}

func TestHealthCheckAllHealthy(t *testing.T) {
	t.Run("all required fields present", func(t *testing.T) {
		container, _ := setupTestContainer(t)

		// Test that health check runs without panicking
		// With basic sqlmock setup, Redis is nil so it's skipped
		// Database ping succeeds with sqlmock
		err := container.HealthCheck(context.Background())
		require.NoError(t, err) // Should pass with nil Redis
	})

	t.Run("health check with timeout context", func(t *testing.T) {
		container, _ := setupTestContainer(t)

		ctx, cancel := context.WithTimeout(context.Background(), serviceContainerHealthTimeout)
		defer cancel()

		// Health check should respect context and complete quickly
		err := container.HealthCheck(ctx)
		require.NoError(t, err) // Should pass with nil Redis
	})
}

func TestHealthCheckSomeUnhealthy(t *testing.T) {
	t.Run("nil database connection", func(t *testing.T) {
		container := &ServiceContainer{db: nil}

		err := container.HealthCheck(context.Background())
		require.Error(t, err)
		assert.Contains(t, err.Error(), "database connection is nil")
	})

	// Note: Testing "cannot get underlying database" is difficult with GORM
	// as it requires a specific internal state that causes DB() to fail
	// The nil database test above covers the main error path

	t.Run("redis ping failure", func(t *testing.T) {
		db, _, err := sqlmock.New()
		require.NoError(t, err)

		gormDB, err := gorm.Open(postgres.New(postgres.Config{
			Conn: db,
		}), &gorm.Config{})
		require.NoError(t, err)

		// Create Redis client with invalid address
		redisClient := redis.NewClient(&redis.Options{
			Addr: "invalid:6379",
		})

		container, err := NewServiceContainer(gormDB, redisClient, nil, nil, nil, nil)
		require.NoError(t, err)

		// Health check should fail (either on DB ping or Redis ping)
		err = container.HealthCheck(context.Background())
		require.Error(t, err)
	})
}

func TestContainerClose_Comprehensive(t *testing.T) {
	t.Run("close empty container", func(t *testing.T) {
		container := &ServiceContainer{}
		err := container.Close()
		require.NoError(t, err)
	})

	t.Run("close container with services", func(t *testing.T) {
		container, _ := setupTestContainer(t)

		// Initialize some services
		_ = container.ItemService()
		_ = container.LinkService()

		err := container.Close()
		require.NoError(t, err)
	})

	t.Run("close is idempotent", func(t *testing.T) {
		container, _ := setupTestContainer(t)

		err1 := container.Close()
		err2 := container.Close()
		err3 := container.Close()

		require.NoError(t, err1)
		require.NoError(t, err2)
		require.NoError(t, err3)
	})
}

func TestTransactionManagement(t *testing.T) {
	t.Run("nested error handling", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		mock.ExpectRollback()

		err := container.WithTx(context.Background(), func(_ *TransactionContext) error {
			return errors.New("business logic error")
		})

		require.Error(t, err)
		assert.Contains(t, err.Error(), "business logic error")
		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("commit failure", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin()
		mock.ExpectCommit().WillReturnError(errors.New("commit failed"))

		err := container.WithTx(context.Background(), func(_ *TransactionContext) error {
			return nil
		})

		require.Error(t, err)
		assert.Contains(t, err.Error(), "failed to commit transaction")
	})

	t.Run("begin transaction failure", func(t *testing.T) {
		container, mock := setupTestContainer(t)

		mock.ExpectBegin().WillReturnError(errors.New("begin failed"))

		err := container.WithTx(context.Background(), func(_ *TransactionContext) error {
			t.Fatal("should not reach here")
			return nil
		})

		require.Error(t, err)
		assert.Contains(t, err.Error(), "failed to begin transaction")
	})
}

func TestConcurrentServiceAccess(t *testing.T) {
	t.Run("concurrent access to same service", func(t *testing.T) {
		container, _ := setupTestContainer(t)

		done := make(chan ItemService, 10)

		// Launch multiple goroutines accessing the same service
		for i := 0; i < 10; i++ {
			go func() {
				svc := container.ItemService()
				done <- svc
			}()
		}

		// Collect all services
		services := make([]ItemService, 10)
		for i := 0; i < 10; i++ {
			services[i] = <-done
		}

		// Verify all services are the same instance (cached)
		for i := 1; i < 10; i++ {
			assert.Same(t, services[0], services[i])
		}
	})

	t.Run("concurrent access to different services", func(t *testing.T) {
		container, _ := setupTestContainer(t)

		var wg sync.WaitGroup
		wg.Add(4)

		go func() {
			defer wg.Done()
			_ = container.ItemService()
		}()

		go func() {
			defer wg.Done()
			_ = container.LinkService()
		}()

		go func() {
			defer wg.Done()
			_ = container.ProjectService()
		}()

		go func() {
			defer wg.Done()
			_ = container.AgentService()
		}()

		wg.Wait()

		// Verify all services were initialized
		assert.NotNil(t, container.itemService)
		assert.NotNil(t, container.linkService)
		assert.NotNil(t, container.projectService)
		assert.NotNil(t, container.agentService)
	})
}

func TestServiceContainerEdgeCases(t *testing.T) {
	t.Run("service initialization with nil dependencies", func(t *testing.T) {
		db, _, err := sqlmock.New()
		require.NoError(t, err)

		gormDB, err := gorm.Open(postgres.New(postgres.Config{
			Conn: db,
		}), &gorm.Config{})
		require.NoError(t, err)

		// Container with all nil except DB
		container, err := NewServiceContainer(gormDB, nil, nil, nil, nil, nil)
		require.NoError(t, err)

		// Services should still initialize (they handle nil gracefully)
		itemSvc := container.ItemService()
		assert.NotNil(t, itemSvc)

		linkSvc := container.LinkService()
		assert.NotNil(t, linkSvc)
	})

	t.Run("unimplemented services return nil", func(t *testing.T) {
		container, _ := setupTestContainer(t)

		assert.Nil(t, container.CodeIndexService())
		assert.Nil(t, container.SearchService())
		assert.Nil(t, container.GraphAnalysisService())
		assert.Nil(t, container.CacheService())
		assert.Nil(t, container.EventService())
	})
}
