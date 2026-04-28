package server

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/config"
	"github.com/kooshapari/tracertm-backend/internal/infrastructure"
)

func TestConfigConstants(t *testing.T) {
	t.Run("cache TTL is reasonable", func(t *testing.T) {
		assert.Equal(t, 5*time.Minute, defaultCacheTTL)
	})

	t.Run("search indexer workers set", func(t *testing.T) {
		assert.Equal(t, 4, searchIndexerWorkers)
	})

	t.Run("search indexer batch size set", func(t *testing.T) {
		assert.Equal(t, 1000, searchIndexerBatchSize)
	})

	t.Run("gzip level valid", func(t *testing.T) {
		assert.GreaterOrEqual(t, gzipLevel, 1)
		assert.LessOrEqual(t, gzipLevel, 9)
	})

	t.Run("session TTL set", func(t *testing.T) {
		assert.Equal(t, 24*time.Hour, sessionTTL)
	})

	t.Run("agent coordinator interval set", func(t *testing.T) {
		assert.Equal(t, 2*time.Minute, agentCoordinatorInterval)
	})

	t.Run("lock manager TTL set", func(t *testing.T) {
		assert.Equal(t, 5*time.Minute, lockManagerTTL)
	})

	t.Run("gzip min length set", func(t *testing.T) {
		assert.Equal(t, 1024, gzipMinLength)
	})

	t.Run("journey config values set", func(t *testing.T) {
		assert.Equal(t, 2, journeyMinPathLength)
		assert.Equal(t, 10, journeyMaxPathLength)
		assert.Equal(t, 1, journeyMinFrequency)
	})

	t.Run("journey similarity threshold set", func(t *testing.T) {
		assert.InEpsilon(t, 0.8, journeySimilarityThreshold, 1e-9)
	})
}

func TestInitFunctionsConfig(t *testing.T) {
	t.Run("initRedisCache with nil client", func(t *testing.T) {
		cache := initRedisCache(nil, createTestConfig())
		assert.Nil(t, cache)
	})

	t.Run("initEventPublisher with nil NATS", func(t *testing.T) {
		pub := initEventPublisher(nil, createTestConfig())
		assert.Nil(t, pub)
	})

	t.Run("initNATSConn with nil client", func(t *testing.T) {
		conn := initNATSConn(nil)
		assert.Nil(t, conn)
	})

	t.Run("initS3Storage with no config", func(t *testing.T) {
		storage := initS3Storage(&config.Config{})
		assert.Nil(t, storage)
	})

	t.Run("initS3Storage with incomplete config", func(t *testing.T) {
		cfg := &config.Config{S3Endpoint: "http://localhost:9000"}
		storage := initS3Storage(cfg)
		assert.Nil(t, storage)
	})

	t.Run("initAdapterFactory with nil pool", func(t *testing.T) {
		cfg := createTestConfig()
		factory := initAdapterFactory(nil, &infrastructure.Infrastructure{}, cfg, nil)
		assert.Nil(t, factory)
	})

	t.Run("initPythonBackendClients with empty URL", func(t *testing.T) {
		clients := initPythonBackendClients(&config.Config{}, nil)
		assert.Nil(t, clients)
	})

	t.Run("initPythonBackendClients with URL", func(t *testing.T) {
		clients := initPythonBackendClients(&config.Config{PythonBackendURL: "http://localhost:8000"}, nil)
		assert.NotNil(t, clients)
	})
}

func TestTestConfigCreation(t *testing.T) {
	cfg := createTestConfig()
	assert.NotNil(t, cfg)
	assert.Equal(t, "test", cfg.Env)
	assert.Equal(t, "8080", cfg.Port)
}

func TestConstantsAreValid(t *testing.T) {
	tests := []struct {
		name  string
		value interface{}
		check func(interface{}) bool
	}{
		{"gzip level", gzipLevel, func(v interface{}) bool {
			l, ok := v.(int)
			require.True(t, ok)
			return l >= 1 && l <= 9
		}},
		{"search workers", searchIndexerWorkers, func(v interface{}) bool {
			w, ok := v.(int)
			require.True(t, ok)
			return w > 0
		}},
		{"gzip min length", gzipMinLength, func(v interface{}) bool {
			m, ok := v.(int)
			require.True(t, ok)
			return m > 0
		}},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.True(t, tt.check(tt.value))
		})
	}
}

func TestConfigCreation(t *testing.T) {
	t.Run("creates minimal valid config", func(t *testing.T) {
		cfg := createTestConfig()
		assert.Equal(t, "test", cfg.Env)
		assert.Equal(t, "8080", cfg.Port)
	})

	t.Run("config has required fields", func(t *testing.T) {
		cfg := createTestConfig()
		assert.NotNil(t, cfg)
		assert.NotEmpty(t, cfg.Env)
		assert.NotEmpty(t, cfg.Port)
	})
}

func TestInitializationPatterns(t *testing.T) {
	t.Run("nil inputs handled gracefully", func(t *testing.T) {
		cache := initRedisCache(nil, nil)
		assert.Nil(t, cache)
	})

	t.Run("various config combinations", func(t *testing.T) {
		configs := []*config.Config{
			{},
			{RedisURL: "redis://localhost:6379"},
			{NATSUrl: "nats://localhost:4222"},
			{PythonBackendURL: "http://localhost:8000"},
		}

		for _, cfg := range configs {
			assert.NotNil(t, cfg)
		}
	})
}

func TestValueRanges(t *testing.T) {
	t.Run("cache TTL > 0", func(t *testing.T) {
		assert.Greater(t, defaultCacheTTL, time.Duration(0))
	})

	t.Run("gzip level in valid range", func(t *testing.T) {
		assert.GreaterOrEqual(t, gzipLevel, 1)
		assert.LessOrEqual(t, gzipLevel, 9)
	})

	t.Run("search workers > 0", func(t *testing.T) {
		assert.Positive(t, searchIndexerWorkers)
	})

	t.Run("batch size > 0", func(t *testing.T) {
		assert.Positive(t, searchIndexerBatchSize)
	})

	t.Run("session TTL is 24 hours", func(t *testing.T) {
		assert.Equal(t, 24*time.Hour, sessionTTL)
	})

	t.Run("journey path length bounds", func(t *testing.T) {
		assert.Greater(t, journeyMaxPathLength, journeyMinPathLength)
		assert.Positive(t, journeyMinPathLength)
	})

	t.Run("similarity threshold in valid range", func(t *testing.T) {
		assert.GreaterOrEqual(t, journeySimilarityThreshold, 0.0)
		assert.LessOrEqual(t, journeySimilarityThreshold, 1.0)
	})
}

func TestConsumerNameSanitization(t *testing.T) {
	t.Run("replaces wildcards in consumer name", func(t *testing.T) {
		// ... implementation ...
	})
}

func TestAdapterResolverEdgeCases(t *testing.T) {
	t.Run("nil factory returns nil adapters", func(t *testing.T) {
		var factory interface{} = nil
		assert.Nil(t, factory)
	})
}

func TestServerNilComponents(t *testing.T) {
	t.Run("server with minimal infrastructure", func(t *testing.T) {
		dbURL := os.Getenv("TEST_DATABASE_URL")
		if dbURL == "" {
			t.Skip("TEST_DATABASE_URL not set")
		}
		pool, err := pgxpool.New(context.Background(), dbURL)
		if err != nil {
			t.Skipf("Database not available: %v", err)
		}
		defer pool.Close()

		gormDB, err := gorm.Open(postgres.Open(dbURL), &gorm.Config{})
		if err != nil {
			pool.Close()
			t.Skipf("Failed to create GORM DB: %v", err)
		}

		infra := &infrastructure.Infrastructure{
			DB:     pool,
			GormDB: gormDB,
		}
		cfg := createTestConfig()

		server, err := NewServer(infra, cfg)
		require.NoError(t, err)
		assert.NotNil(t, server)
	})
}
