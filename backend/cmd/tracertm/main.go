package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/config"
	"github.com/kooshapari/tracertm-backend/internal/infrastructure"
	"github.com/kooshapari/tracertm-backend/internal/server"
)

func main() {
	if err := run(); err != nil {
		log.Fatalf("Fatal error: %v", err)
	}
}

func run() error {
	// Preflight checks run automatically via init() in preflight.go

	ctx := context.Background()

	// Load configuration
	cfg := config.LoadConfig()

	// Initialize infrastructure (database, redis, NATS, etc.)
	infra, err := infrastructure.InitializeInfrastructure(ctx, cfg)
	if err != nil {
		return fmt.Errorf("failed to initialize infrastructure: %w", err)
	}
	defer func() {
		if err := infra.Close(ctx); err != nil {
			log.Printf("Error closing infrastructure: %v", err)
		}
	}()

	// Create server
	srv, err := server.NewServer(infra, cfg)
	if err != nil {
		return fmt.Errorf("failed to create server: %w", err)
	}

	// Setup graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)

	go func() {
		<-sigChan
		fmt.Println("\nReceived shutdown signal, gracefully stopping...")

		// Give server 30 seconds to shutdown gracefully
		shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 30*time.Second)
		defer shutdownCancel()

		if err := srv.Shutdown(shutdownCtx); err != nil {
			log.Printf("Error during shutdown: %v", err)
		}
		os.Exit(0)
	}()

	// Start server (blocking)
	address := ":" + cfg.Port
	fmt.Println("Starting TraceRTM backend server...")
	fmt.Printf("Server listening on %s\n", address)
	if err := srv.Start(address); err != nil {
		return fmt.Errorf("server error: %w", err)
	}

	return nil
}
