// Package server provides HTTP and gRPC server setup and routing.
package server

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"
	natslib "github.com/nats-io/nats.go"
	"github.com/redis/go-redis/v9"

	"github.com/kooshapari/tracertm-backend/internal/adapters"
	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/config"
	"github.com/kooshapari/tracertm-backend/internal/graph"
	"github.com/kooshapari/tracertm-backend/internal/infrastructure"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/search"
	"github.com/kooshapari/tracertm-backend/internal/services"
	"github.com/kooshapari/tracertm-backend/internal/storage"
	"github.com/kooshapari/tracertm-backend/internal/websocket"
)

const (
	defaultCacheTTL            = 5 * time.Minute
	searchIndexerWorkers       = 4
	searchIndexerBatchSize     = 1000
	gzipLevel                  = 5
	gzipMinLength              = 1024
	sessionTTL                 = 24 * time.Hour
	agentCoordinatorInterval   = 2 * time.Minute
	lockManagerTTL             = 5 * time.Minute
	journeyMinPathLength       = 2
	journeyMaxPathLength       = 10
	journeyMinFrequency        = 1
	journeyMinScore            = 0.1
	journeySimilarityThreshold = 0.8
)

// Server is the main HTTP server (Echo, DB, Redis, NATS, search, services).
type Server struct {
	echo             *echo.Echo
	pool             *pgxpool.Pool
	cfg              *config.Config
	infra            *infrastructure.Infrastructure
	redisClient      *redis.Client
	natsConn         *natslib.Conn
	redisCache       cache.Cache
	eventPublisher   *nats.EventPublisher
	adapterFactory   *adapters.AdapterFactory
	searchEngine     *search.Engine
	searchIndexer    *search.Indexer
	wsHub            *websocket.Hub
	s3Storage        *storage.S3Storage
	serviceContainer *services.ServiceContainer
	graphConsumer    *graph.EventConsumer
}

// NewServer creates a new server with infrastructure and required ServiceContainer.
func NewServer(infra *infrastructure.Infrastructure, cfg *config.Config) (*Server, error) {
	pool := infra.DB
	redisClient := infra.Redis
	e := echo.New()

	redisCache := initRedisCache(redisClient, cfg)
	eventPublisher := initEventPublisher(infra.NATS, cfg)
	natsConn := initNATSConn(infra.NATS)
	adapterFactory := initAdapterFactory(pool, infra, cfg, natsConn)
	searchEngine, searchIndexer := initSearch(pool)
	wsHub := websocket.NewHub()
	s3Storage := initS3Storage(cfg)
	backendClients := initPythonBackendClients(cfg, redisCache)

	if infra.GormDB == nil {
		return nil, errors.New("failed to initialize server: GormDB is nil")
	}
	serviceContainer, err := services.NewServiceContainer(
		infra.GormDB,
		redisClient,
		redisCache,
		eventPublisher,
		infra.Neo4j,
		backendClients,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize ServiceContainer: %w", err)
	}
	slog.Info("✓ ServiceContainer initialized")

	server := &Server{
		echo:             e,
		pool:             pool,
		cfg:              cfg,
		infra:            infra,
		redisClient:      redisClient,
		natsConn:         natsConn,
		redisCache:       redisCache,
		eventPublisher:   eventPublisher,
		adapterFactory:   adapterFactory,
		searchEngine:     searchEngine,
		searchIndexer:    searchIndexer,
		wsHub:            wsHub,
		s3Storage:        s3Storage,
		serviceContainer: serviceContainer,
	}

	// Setup middleware
	server.setupMiddleware()

	// Setup routes
	server.setupRoutes()

	return server, nil
}

// Start starts the HTTP server on the given address.
func (s *Server) Start(addr string) error {
	return s.echo.Start(addr)
}

// wrapMuxHandler converts a net/http handler to an Echo handler
func (s *Server) wrapMuxHandler(h func(http.ResponseWriter, *http.Request)) echo.HandlerFunc {
	return func(c echo.Context) error {
		h(c.Response(), c.Request())
		return nil
	}
}

// Shutdown gracefully shuts down the server (indexer, NATS, Redis, Echo).
func (s *Server) Shutdown(ctx context.Context) error {
	// Stop search indexer
	if s.searchIndexer != nil {
		s.searchIndexer.Stop()
	}

	// Close NATS connection
	if s.natsConn != nil {
		s.natsConn.Close()
	}

	// Close Redis connection
	if s.redisClient != nil {
		if err := s.redisClient.Close(); err != nil {
			slog.Error("Warning: Failed to close Redis", "error", err)
		}
	}

	// Shutdown Echo server
	return s.echo.Shutdown(ctx)
}

func (s *Server) setupEventConsumer() {
	if s.infra.NATS == nil || s.infra.Neo4j == nil {
		slog.Warn("⚠️  NATS or Neo4j not available, skipping Graph Event Consumer")
		return
	}

	// Create EventBus for Graph Consumer
	bus, err := nats.NewEventBus(nats.DefaultConfig())
	if err != nil {
		slog.Error("⚠️ Failed to create EventBus for Graph Consumer", "error", err)
		return
	}

	// Create Graph Event Consumer
	s.graphConsumer = graph.NewEventConsumer(bus, s.infra.Neo4j.GetDriver())

	// Start Consumer in background
	go func() {
		ctx := context.Background()
		if err := s.graphConsumer.Start(ctx); err != nil {
			slog.Error("⚠️ Graph Event Consumer failed", "error", err)
		}
	}()
}
