package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.uber.org/zap"

	"github.com/org/microservice/internal/application/handlers"
	"github.com/org/microservice/internal/config"
	"github.com/org/microservice/internal/infrastructure/adapters/nats"
	"github.com/org/microservice/internal/infrastructure/adapters/postgres"
	"github.com/org/microservice/internal/infrastructure/logging"
	"github.com/org/microservice/internal/infrastructure/metrics"
	"github.com/org/microservice/internal/infrastructure/tracing"
)

func main() {
	// Initialize structured logging
	logger := logging.New()
	defer logger.Sync()

	// Load configuration
	cfg := config.Load()
	logger.Info("Starting microservice", zap.String("service", cfg.ServiceName))

	// Initialize tracing (OpenTelemetry)
	shutdown, err := tracing.InitTracer(cfg.ServiceName, cfg.OtelEndpoint)
	if err != nil {
		logger.Warn("Failed to initialize tracer", zap.Error(err))
	} else {
		defer shutdown()
	}

	// Initialize metrics (Prometheus)
	metrics.Init(cfg.ServiceName)

	// Initialize PostgreSQL adapter (Wrap-Over pattern)
	db, err := postgres.NewPostgresAdapter(cfg.DatabaseURL)
	if err != nil {
		logger.Fatal("Failed to connect to database", zap.Error(err))
	}
	defer db.Close()

	// Initialize NATS adapter (Event-driven messaging)
	nc, err := nats.NewNatsAdapter(cfg.NatsURL)
	if err != nil {
		logger.Fatal("Failed to connect to NATS", zap.Error(err))
	}
	defer nc.Close()

	// Create application handlers (CQRS)
	commandHandler := handlers.NewCommandHandler(db)
	queryHandler := handlers.NewQueryHandler(db)
	httpHandler := handlers.NewHTTPHandler(commandHandler, queryHandler)

	// Start HTTP server
	mux := http.NewServeMux()
	mux.HandleFunc("/health", httpHandler.Health)
	mux.HandleFunc("/ready", httpHandler.Ready)
	mux.Handle("/metrics", promhttp.Handler())

	srv := &http.Server{
		Addr:    fmt.Sprintf(":%d", cfg.HTTPPort),
		Handler: mux,
	}

	// Graceful shutdown
	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal("HTTP server failed", zap.Error(err))
		}
	}()

	logger.Info("HTTP server started", zap.Int("port", cfg.HTTPPort))

	// Wait for shutdown signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Fatal("Server forced to shutdown", zap.Error(err))
	}

	logger.Info("Server exited")
}
