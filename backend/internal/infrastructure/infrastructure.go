// Package infrastructure wires infrastructure dependencies.
package infrastructure

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/redis/go-redis/v9"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/agents"
	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/cliproxy"
	"github.com/kooshapari/tracertm-backend/internal/config"
	"github.com/kooshapari/tracertm-backend/internal/graph"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/kooshapari/tracertm-backend/internal/tracing"
)

const infrastructureCacheDefaultTTL = 5 * time.Minute

// Infrastructure holds low-level infrastructure clients
// High-level services have been moved to services.ServiceContainer (Phase 7)
type Infrastructure struct {
	// Low-level infrastructure (connections, caches, message queues)
	DB     *pgxpool.Pool
	GormDB *gorm.DB // GORM DB instance for ORM operations
	Redis  *redis.Client
	NATS   *nats.Client
	Neo4j  *graph.Neo4jClient
	Cache  cache.Cache

	// CLIProxy service for OAuth-based AI provider routing
	CLIProxy *cliproxy.Service

	// Tracing provider for distributed tracing
	TracerProvider *tracing.TracerProvider

	TemporalService interface{} // TemporalService interface (see services/temporal_service.go)

	// Legacy graph service - kept temporarily for gRPC server
	// Note: gRPC server migration to ServiceContainer deferred
	GraphAnalysis *graph.AnalysisService

	// Repository interfaces - kept for gRPC service
	// Note: Moving to ServiceContainer under consideration
	ItemRepository    repository.ItemRepository
	LinkRepository    repository.LinkRepository
	ProjectRepository repository.ProjectRepository
	AgentRepository   repository.AgentRepository
}

// initDataLayer initializes Postgres, GORM, Redis, NATS, and Neo4j.
func initDataLayer(ctx context.Context, infra *Infrastructure, cfg *config.Config) error {
	pool, err := initPostgres(ctx, cfg.DatabaseURL)
	if err != nil {
		return err
	}
	infra.DB = pool

	gormDB, err := initGorm(cfg.DatabaseURL)
	if err != nil {
		return err
	}
	infra.GormDB = gormDB

	if err := migrateAuthProfiles(gormDB); err != nil {
		return err
	}
	if err := migrateNotifications(gormDB); err != nil {
		return err
	}
	initRepositories(infra, gormDB)

	redisClient, err := initRedis(ctx, cfg.RedisURL)
	if err != nil {
		return err
	}
	infra.Redis = redisClient

	natsClient, err := initNATS(cfg)
	if err != nil {
		return err
	}
	infra.NATS = natsClient

	neo4jClient, err := initNeo4j(ctx, cfg)
	if err != nil {
		return err
	}
	infra.Neo4j = neo4jClient
	return nil
}

// InitializeInfrastructure initializes all infrastructure services
func InitializeInfrastructure(ctx context.Context, cfg *config.Config) (*Infrastructure, error) {
	infra := &Infrastructure{}

	if err := initDataLayer(ctx, infra, cfg); err != nil {
		return nil, err
	}

	//nolint:contextcheck // initCache creates own context
	redisCache, err := initCache(cfg.RedisURL)
	if err != nil {
		return nil, err
	}
	infra.Cache = redisCache

	tracerProvider, err := initTracing(ctx, cfg)
	if err != nil {
		return nil, err
	}
	infra.TracerProvider = tracerProvider

	if infra.Cache == nil {
		return nil, errors.New("cache is required for Graph Analysis Service but is not initialized")
	}
	infra.GraphAnalysis = graph.NewAnalysisService(infra.Neo4j.GetDriver(), infra.Cache)
	infra.CLIProxy = initCLIProxy()

	slog.Info("Infrastructure ready (Postgres, Redis, NATS, Neo4j)")
	return infra, nil
}

func initCLIProxy() *cliproxy.Service {
	cliproxyCfg, err := cliproxy.LoadConfig("configs/cliproxy.yaml")
	if err != nil {
		slog.Info("CLIProxy config file not found, trying environment variables", "path", err)
		cliproxyCfg = cliproxy.LoadConfigFromEnv()
	}

	if len(cliproxyCfg.Providers) > 0 {
		if err := cliproxyCfg.Validate(); err != nil {
			slog.Warn("⚠️ CLIProxy configuration invalid (skipping)", "id", err)
		} else {
			cliproxyService, err := cliproxy.NewService(cliproxyCfg)
			if err != nil {
				slog.Error("⚠️ Failed to initialize CLIProxy service (skipping)", "error", err)
			} else {
				slog.Info("🔐 CLIProxy service configured with provider(s)", "name", len(cliproxyCfg.Providers))
				return cliproxyService
			}
		}
	} else {
		slog.Info("ℹ️  CLIProxy not configured (no OAuth providers found)")
	}
	return nil
}

func initPostgres(ctx context.Context, databaseURL string) (*pgxpool.Pool, error) {
	pool, err := pgxpool.New(ctx, databaseURL)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize database: %w", err)
	}
	return pool, nil
}

func initGorm(databaseURL string) (*gorm.DB, error) {
	gormDB, err := gorm.Open(postgres.Open(databaseURL), &gorm.Config{})
	if err != nil {
		return nil, fmt.Errorf("failed to initialize GORM: %w", err)
	}
	return gormDB, nil
}

func migrateAuthProfiles(gormDB *gorm.DB) error {
	// One-time migration: old schema had workos_id NOT NULL; GORM model uses workos_user_id only.
	// Try RENAME; if workos_user_id already exists (both columns), DROP workos_id instead.
	// To run manually: psql $DATABASE_URL -f migrations/20260131_profiles_workos_id.sql
	_ = gormDB.Exec(`DO $$ BEGIN
		IF EXISTS (SELECT 1 FROM information_schema.columns
			WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'workos_id') THEN
			BEGIN
				ALTER TABLE public.profiles RENAME COLUMN workos_id TO workos_user_id;
			EXCEPTION
				WHEN duplicate_column THEN
					ALTER TABLE public.profiles DROP COLUMN workos_id;
				WHEN undefined_column THEN
					NULL;
			END;
		END IF;
	END $$`).Error

	// Migrate auth profile table (WorkOS profiles); schema owned by GORM, not Alembic.
	// GORM may try to DROP constraint uni_profiles_email (without IF EXISTS).
	// Ensure it exists in both schemas so DROP succeeds regardless of search_path.
	// Only ADD if missing to avoid PostgreSQL "relation already exists" (which GORM logs even when EXCEPTION swallows it).
	for _, schema := range []string{"public", "tracertm"} {
		_ = gormDB.Exec(fmt.Sprintf(`DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint c
    JOIN pg_class t ON t.oid = c.conrelid
    JOIN pg_namespace n ON n.oid = t.relnamespace
    WHERE n.nspname = '%s' AND t.relname = 'profiles' AND c.conname = 'uni_profiles_email'
  ) THEN
    ALTER TABLE %s.profiles ADD CONSTRAINT uni_profiles_email UNIQUE (email);
  END IF;
EXCEPTION
  WHEN undefined_table THEN NULL;
END $$`, schema, schema)).Error
	}
	if err := gormDB.AutoMigrate(&models.Profile{}); err != nil {
		return fmt.Errorf("failed to auto-migrate profiles: %w", err)
	}
	for _, schema := range []string{"public", "tracertm"} {
		_ = gormDB.Exec("ALTER TABLE " + schema + ".profiles DROP CONSTRAINT IF EXISTS uni_profiles_email").Error
	}
	return nil
}

func migrateNotifications(gormDB *gorm.DB) error {
	// Migrate notifications table (for SSE notifications)
	// Import services package to access Notification model
	type Notification struct {
		ID        string `gorm:"primaryKey"`
		UserID    string `gorm:"index"`
		Type      string
		Title     string
		Message   string
		Link      *string
		ReadAt    *time.Time
		CreatedAt time.Time  `gorm:"index"`
		ExpiresAt *time.Time `gorm:"index"`
	}
	if err := gormDB.AutoMigrate(&Notification{}); err != nil {
		return fmt.Errorf("failed to auto-migrate notifications: %w", err)
	}
	return nil
}

func initRepositories(infra *Infrastructure, gormDB *gorm.DB) {
	infra.ItemRepository = repository.NewItemRepository(gormDB)
	infra.LinkRepository = repository.NewLinkRepository(gormDB)
	infra.ProjectRepository = repository.NewProjectRepository(gormDB)
	infra.AgentRepository = repository.NewAgentRepository(gormDB)
}

func initRedis(ctx context.Context, redisURL string) (*redis.Client, error) {
	redisOpts, err := redis.ParseURL(redisURL)
	if err != nil {
		return nil, fmt.Errorf("failed to parse redis url: %w", err)
	}
	redisClient := redis.NewClient(redisOpts)
	if err := redisClient.Ping(ctx).Err(); err != nil {
		return nil, fmt.Errorf("failed to connect to redis: %w", err)
	}
	return redisClient, nil
}

func initNATS(cfg *config.Config) (*nats.Client, error) {
	natsClient, err := nats.NewNATSClientWithAuth(
		cfg.NATSUrl,
		cfg.NATSCreds,
		cfg.NATSUserJWT,
		cfg.NATSUserNkeySeed,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize nats: %w", err)
	}
	return natsClient, nil
}

func initNeo4j(ctx context.Context, cfg *config.Config) (*graph.Neo4jClient, error) {
	if cfg.Neo4jURI == "" || cfg.Neo4jUser == "" || cfg.Neo4jPassword == "" {
		return nil, errors.New("Neo4j configuration is required but missing. Set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD in .env")
	}
	neo4jClient, err := graph.InitializeNeo4j(ctx, cfg.Neo4jURI, cfg.Neo4jUser, cfg.Neo4jPassword)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize Neo4j (required service): %w. Ensure Neo4j is running: brew services start neo4j", err)
	}
	return neo4jClient, nil
}

func initCache(redisURL string) (cache.Cache, error) {
	rc, err := cache.NewRedisCache(cache.RedisCacheConfig{
		RedisURL:   redisURL,
		DefaultTTL: infrastructureCacheDefaultTTL,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to initialize redis cache: %w", err)
	}
	return rc, nil
}

func initTracing(ctx context.Context, cfg *config.Config) (*tracing.TracerProvider, error) {
	if !cfg.TracingEnabled {
		slog.Info("ℹ️  Distributed tracing is disabled")
		return nil, nil
	}
	tracerProvider, err := tracing.InitTracer(ctx, cfg.CollectorEndpoint, cfg.TracingEnvironment)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize tracing (required service): %w", err)
	}
	slog.Info("✅ Distributed tracing initialized")
	return tracerProvider, nil
}

// checkDataStoreHealth verifies Postgres, GORM, and Redis health.
func (i *Infrastructure) checkDataStoreHealth(ctx context.Context) error {
	if err := i.DB.Ping(ctx); err != nil {
		return fmt.Errorf("postgresql health check failed: %w", err)
	}
	if i.GormDB == nil {
		return errors.New("gorm health check failed: gorm db not initialized")
	}
	if err := agents.VerifyTaskBackendPersistence(ctx, i.GormDB); err != nil {
		return fmt.Errorf("agent task backend health check failed: %w", err)
	}
	if i.Redis == nil {
		return errors.New("redis health check failed: redis client not initialized")
	}
	return i.Redis.Ping(ctx).Err()
}

// checkMessagingHealth verifies NATS, Neo4j, and Cache health.
func (i *Infrastructure) checkMessagingHealth(ctx context.Context) error {
	if i.Cache == nil {
		return errors.New("cache health check failed: cache not initialized")
	}
	if i.NATS == nil {
		return errors.New("nats health check failed: nats client not initialized")
	}
	if err := i.NATS.HealthCheck(ctx); err != nil {
		return fmt.Errorf("nats health check failed: %w", err)
	}
	if i.Neo4j == nil {
		return errors.New("neo4j health check failed: neo4j client not initialized")
	}
	return graph.VerifyNeo4jSetup(ctx, i.Neo4j)
}

// HealthCheck verifies all services are healthy
func (i *Infrastructure) HealthCheck(ctx context.Context) error {
	if err := i.checkDataStoreHealth(ctx); err != nil {
		return err
	}
	return i.checkMessagingHealth(ctx)
}

// Close closes all infrastructure connections
func (i *Infrastructure) Close(ctx context.Context) error {
	// Shutdown tracer provider first to flush any pending spans
	if i.TracerProvider != nil {
		if err := i.TracerProvider.Shutdown(ctx); err != nil {
			slog.Error("error shutting down tracer provider", "error", err)
		}
	}

	if i.DB != nil {
		i.DB.Close()
	}
	if i.Redis != nil {
		if err := i.Redis.Close(); err != nil {
			slog.Error("error closing Redis", "error", err)
		}
	}
	if i.NATS != nil {
		if err := i.NATS.Close(); err != nil {
			slog.Error("error closing NATS", "error", err)
		}
	}
	if i.Neo4j != nil {
		if err := i.Neo4j.Close(ctx); err != nil {
			slog.Error("error closing Neo4j", "error", err)
		}
	}
	return nil
}
