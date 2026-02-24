// @title TraceRTM API
// @version 1.0
// @description TraceRTM Backend API - Requirements Traceability Management System with AI-powered agents
// @openapi:version 3.0.3
// @description
// @description TraceRTM is a comprehensive requirements traceability management system that helps teams
// @description track relationships between requirements, features, and tasks throughout the development lifecycle.
// @description
// @description ## Features
// @description - Project and Item Management
// @description - Link Management for traceability
// @description - AI Agent Coordination
// @description - Graph-based relationship analysis
// @description - Full-text search with pgvector
// @description - Real-time updates via WebSocket and NATS
// @description
// @description ## Authentication
// @description Currently supports WorkOS AuthKit. Set Authorization header with Bearer token.

// @contact.name TraceRTM Support
// @contact.url https://github.com/kooshapari/tracertm-backend
// @contact.email support@tracertm.example.com

// @license.name MIT
// @license.url https://opensource.org/licenses/MIT

// @host localhost:8080
// @BasePath /api/v1

// @schemes http https

// @securityDefinitions.apikey ApiKeyAuth
// @in header
// @name Authorization
// @description Enter your bearer token in the format: Bearer {token}

// @tag.name health
// @tag.description Health check endpoints

// @tag.name projects
// @tag.description Project management endpoints

// @tag.name items
// @tag.description Item (requirements/features/tasks) management endpoints

// @tag.name links
// @tag.description Link (relationship) management endpoints

// @tag.name agents
// @tag.description AI agent management and coordination endpoints

// @tag.name graph
// @tag.description Graph analysis and traversal endpoints

// @tag.name search
// @tag.description Search and indexing endpoints

// @tag.name auth
// @tag.description Authentication and authorization endpoints

// @tag.name equivalences
// @tag.description Equivalence detection and link management endpoints

// @tag.name canonical-concepts
// @tag.description Canonical concept and projection management endpoints

// @tag.name distributed-operations
// @tag.description Distributed operations across multiple agents

// @tag.name journeys
// @tag.description User flow and journey detection endpoints

// Package main is the TraceRTM backend entrypoint.
// Package main starts the TraceRTM backend service.
package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/joho/godotenv"

	// _ "github.com/kooshapari/tracertm-backend/docs" // Import generated docs
	"github.com/kooshapari/tracertm-backend/internal/config"
	"github.com/kooshapari/tracertm-backend/internal/database"
	grpcserver "github.com/kooshapari/tracertm-backend/internal/grpc"
	"github.com/kooshapari/tracertm-backend/internal/infrastructure"
	"github.com/kooshapari/tracertm-backend/internal/preflight"
	sentrylib "github.com/kooshapari/tracertm-backend/internal/sentry"
	"github.com/kooshapari/tracertm-backend/internal/server"
)

func main() {
	loadEnvFiles()
	cfg := config.LoadConfig()

	initSentry(cfg)
	defer sentrylib.Close()

	// Initialize context
	ctx := context.Background()

	if err := runPreflight(ctx, cfg); err != nil {
		log.Printf("Preflight checks failed: %v", err)
		return
	}

	infra, err := initInfrastructure(ctx, cfg)
	if err != nil {
		log.Printf("Failed to initialize infrastructure: %v", err)
		return
	}
	defer func() {
		if cerr := infra.Close(ctx); cerr != nil {
			log.Printf("Failed to close infrastructure: %v", cerr)
		}
	}()

	// Run migrations (non-fatal - server can start even if migrations fail)
	if err := database.RunMigrations(infra.DB); err != nil {
		log.Printf("⚠️  Migration warning (continuing startup): %v", err)
	}

	// Run health checks with retry and progressive backoff (deps may not be ready yet)
	waitForInfrastructure(ctx, infra)

	// Initialize HTTP server with infrastructure and services
	srv, err := newServer(infra, cfg)
	if err != nil {
		log.Printf("Server initialization failed: %v", err)
		return
	}
	grpcPort := parseGRPCPort(cfg.GRPCPort)

	// Use repositories from infrastructure (no need to create duplicates)
	grpcSrv, err := grpcserver.NewServer(
		grpcPort,
		infra.ItemRepository,
		infra.LinkRepository,
		infra.GraphAnalysis,
	)
	if err != nil {
		log.Printf("Failed to create gRPC server: %v", err)
		return
	}

	startServices(infra, srv, grpcSrv, cfg.Port)
	waitForShutdown()
	if err := shutdownServices(infra, srv, grpcSrv); err != nil {
		log.Printf("HTTP server forced to shutdown: %v", err)
	}
	log.Println("Servers exited")
}

const (
	defaultGRPCPort       = 9091
	healthInitialDelay    = 2 * time.Second
	healthMaxDelay        = 30 * time.Second
	preflightPollAttempts = 6
	preflightPollInterval = 2 * time.Second
	shutdownTimeout       = 10 * time.Second
)

func loadEnvFiles() {
	if err := godotenv.Load("../.env"); err != nil {
		log.Println("No root .env file found")
	}
	if err := godotenv.Overload(".env"); err != nil {
		log.Println("No backend .env file found")
	}
}

func initSentry(cfg *config.Config) {
	if err := sentrylib.Initialize(sentrylib.Config{
		DSN:              cfg.SentryDSN,
		Environment:      cfg.SentryEnvironment,
		Release:          cfg.SentryRelease,
		TracesSampleRate: cfg.SentryTracesSampleRate,
		Debug:            cfg.SentryDebug,
	}); err != nil {
		log.Printf("Failed to initialize Sentry: %v", err)
	}
}

func runPreflight(ctx context.Context, cfg *config.Config) error {
	if err := preflight.RunWithPoll(
		ctx,
		preflight.BuildBackendChecks(cfg),
		preflight.DefaultPollCheckNames(),
		preflightPollAttempts,
		preflightPollInterval,
	); err != nil {
		return err
	}
	return nil
}

func initInfrastructure(ctx context.Context, cfg *config.Config) (*infrastructure.Infrastructure, error) {
	infra, err := infrastructure.InitializeInfrastructure(ctx, cfg)
	if err != nil {
		return nil, err
	}
	return infra, nil
}

func waitForInfrastructure(ctx context.Context, infra *infrastructure.Infrastructure) {
	healthDelay := healthInitialDelay
	for {
		err := infra.HealthCheck(ctx)
		if err == nil {
			log.Println("Infrastructure health check passed")
			return
		}
		log.Printf("Infrastructure health check failed (retrying in %v): %v", healthDelay, err)
		time.Sleep(healthDelay)
		if healthDelay < healthMaxDelay {
			healthDelay *= 2
			if healthDelay > healthMaxDelay {
				healthDelay = healthMaxDelay
			}
		}
	}
}

func newServer(infra *infrastructure.Infrastructure, cfg *config.Config) (*server.Server, error) {
	srv, err := server.NewServer(infra, cfg)
	if err != nil {
		return nil, err
	}
	return srv, nil
}

func parseGRPCPort(port string) int {
	grpcPort := defaultGRPCPort
	if port == "" {
		return grpcPort
	}
	if _, err := fmt.Sscanf(port, "%d", &grpcPort); err != nil {
		log.Printf("Invalid GRPC port %q, using default %d: %v", port, grpcPort, err)
		return defaultGRPCPort
	}
	return grpcPort
}

func startServices(infra *infrastructure.Infrastructure, srv *server.Server, grpcSrv *grpcserver.Server, port string) {
	if infra.CLIProxy != nil {
		go func() {
			if err := infra.CLIProxy.Run(context.Background()); err != nil {
				log.Printf("CLIProxy service error: %v", err)
			}
		}()
	}

	addr := ":" + port
	go func() {
		log.Printf("🚀 TraceRTM HTTP API starting on %s", addr)
		if err := srv.Start(addr); err != nil {
			log.Printf("HTTP server error (exiting): %v", err)
			os.Exit(1)
		}
	}()

	go func() {
		if err := grpcSrv.Start(); err != nil {
			log.Printf("gRPC server error (exiting): %v", err)
			os.Exit(1)
		}
	}()
}

func waitForShutdown() {
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)
	sig := <-quit
	log.Printf("Received shutdown signal: %s", sig.String())
	log.Println("Shutting down servers...")
}

func shutdownServices(infra *infrastructure.Infrastructure, srv *server.Server, grpcSrv *grpcserver.Server) error {
	if infra.CLIProxy != nil {
		if err := infra.CLIProxy.Shutdown(context.Background()); err != nil {
			log.Printf("CLIProxy shutdown error: %v", err)
		}
	}

	grpcSrv.Stop()

	ctx, cancel := context.WithTimeout(context.Background(), shutdownTimeout)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		return err
	}
	return nil
}
