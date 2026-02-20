package server

import (
	"log/slog"
	"os"

	"github.com/jackc/pgx/v5/pgxpool"
	natslib "github.com/nats-io/nats.go"
	"github.com/redis/go-redis/v9"

	"github.com/kooshapari/tracertm-backend/internal/adapters"
	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/clients"
	"github.com/kooshapari/tracertm-backend/internal/config"
	"github.com/kooshapari/tracertm-backend/internal/infrastructure"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/search"
	"github.com/kooshapari/tracertm-backend/internal/services"
	"github.com/kooshapari/tracertm-backend/internal/storage"
)

func initRedisCache(redisClient *redis.Client, cfg *config.Config) cache.Cache {
	if redisClient == nil {
		return nil
	}

	rc, err := cache.NewRedisCache(cache.RedisCacheConfig{
		RedisURL:   cfg.RedisURL,
		DefaultTTL: defaultCacheTTL,
	})
	if err != nil {
		slog.Error("Warning: Failed to initialize Redis cache", "error", err)
		return nil
	}

	return rc
}

func initEventPublisher(natsConn *nats.Client, cfg *config.Config) *nats.EventPublisher {
	if natsConn == nil {
		return nil
	}

	ep, err := nats.NewEventPublisherWithAuth(cfg.NATSUrl, cfg.NATSCreds, cfg.NATSUserJWT, cfg.NATSUserNkeySeed)
	if err != nil {
		slog.Error("Warning: Failed to initialize NATS publisher", "error", err)
		return nil
	}

	return ep
}

func initNATSConn(natsConn *nats.Client) *natslib.Conn {
	if natsConn == nil {
		return nil
	}

	return natsConn.GetConnection()
}

func initAdapterFactory(
	pool *pgxpool.Pool,
	infra *infrastructure.Infrastructure,
	cfg *config.Config,
	natsConn *natslib.Conn,
) *adapters.AdapterFactory {
	realtimeProvider := os.Getenv("REALTIME_PROVIDER")
	if realtimeProvider == "" {
		realtimeProvider = "nats"
	}

	adapterConfig := adapters.AdapterConfig{
		AuthProvider:     os.Getenv("AUTH_PROVIDER"),
		WorkOSClientID:   cfg.WorkOSClientID,
		AuthKitSecret:    os.Getenv("AUTHKIT_JWT_SECRET"),
		DBPool:           pool,
		GormDB:           infra.GormDB,
		RealtimeProvider: realtimeProvider,
		NATSConn:         natsConn,
	}

	adapterFactory, err := adapters.NewAdapterFactory(adapterConfig)
	if err != nil {
		slog.Error("Warning: Failed to initialize adapter factory", "error", err)
		return nil
	}

	return adapterFactory
}

func initSearch(pool *pgxpool.Pool) (*search.Engine, *search.Indexer) {
	searchEngine := search.NewSearchEngine(pool)
	searchIndexer := search.NewIndexer(pool, searchIndexerWorkers, searchIndexerBatchSize)
	searchIndexer.Start()

	return searchEngine, searchIndexer
}

func initS3Storage(cfg *config.Config) *storage.S3Storage {
	if cfg.S3Endpoint == "" || cfg.S3AccessKeyID == "" || cfg.S3SecretAccessKey == "" || cfg.S3Bucket == "" {
		slog.Info("S3-compatible storage not configured " +
			"(set S3_ENDPOINT, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, S3_BUCKET)")
		return nil
	}

	s3Cfg := storage.S3Config{
		Endpoint:        cfg.S3Endpoint,
		AccessKeyID:     cfg.S3AccessKeyID,
		SecretAccessKey: cfg.S3SecretAccessKey,
		Bucket:          cfg.S3Bucket,
		Region:          cfg.S3Region,
	}
	s3Storage, err := storage.NewS3Storage(s3Cfg)
	if err != nil {
		slog.Error("⚠️ Failed to initialize S3 storage", "error", err)
		return nil
	}

	return s3Storage
}

func initPythonBackendClients(cfg *config.Config, redisCache cache.Cache) *services.PythonBackendClients {
	if cfg.PythonBackendURL == "" {
		return nil
	}

	pythonClient := clients.NewPythonServiceClient(cfg.PythonBackendURL, cfg.ServiceToken, redisCache)
	specClient, err := clients.NewSpecAnalyticsClient(cfg.PythonBackendGRPCAddr, cfg.ServiceToken, redisCache)
	if err != nil {
		slog.Error("⚠️ Failed to initialize Python SpecAnalytics gRPC client", "error", err)
	}
	return &services.PythonBackendClients{
		Python:        pythonClient,
		AI:            clients.NewAIClient(pythonClient),
		SpecAnalytics: specClient,
		Execution:     clients.NewExecutionClient(pythonClient),
		Workflow:      clients.NewWorkflowClient(pythonClient),
		Chaos:         clients.NewChaosClient(pythonClient),
	}
}
