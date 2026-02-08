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
	// Preflight checks run automatically via init() in preflight.go

	ctx := context.Background()

	// Load configuration
	cfg := config.LoadConfig()

	// Initialize infrastructure (database, redis, NATS, etc.)
	infra, err := infrastructure.InitializeInfrastructure(ctx, cfg)
	if err != nil {
		log.Fatalf("Failed to initialize infrastructure: %v", err)
	}
	defer infra.Close(ctx)

	// Create server
	srv, err := server.NewServer(infra, cfg)
	if err != nil {
		log.Fatalf("Failed to create server: %v", err)
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
	address := fmt.Sprintf(":%s", cfg.Port)
	fmt.Println("Starting TraceRTM backend server...")
	fmt.Printf("Server listening on %s\n", address)
	if err := srv.Start(address); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}
