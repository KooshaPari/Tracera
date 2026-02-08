// Package main runs database migrations for tracertm-backend.
package main

import (
	"bytes"
	"context"
	"log"
	"os"
	"os/exec"
)

func main() {
	// Get database URL from environment
	dbURL := os.Getenv("DB_TRANS_POOL_URL")
	if dbURL == "" {
		dbURL = os.Getenv("DB_DIRECT_URL")
	}
	if dbURL == "" {
		log.Fatal("DB_TRANS_POOL_URL or DB_DIRECT_URL not set")
	}

	// Read schema.sql
	schemaSQL, err := os.ReadFile("schema.sql")
	if err != nil {
		log.Printf("Failed to read schema.sql: %v", err)
		return
	}

	if _, err := exec.LookPath("psql"); err != nil {
		log.Fatalf("psql not found in PATH: %v", err)
	}

	ctx := context.Background()
	cmd := exec.CommandContext(ctx, "psql")
	cmd.Env = append(os.Environ(), "DATABASE_URL="+dbURL)
	cmd.Stdin = bytes.NewReader(schemaSQL)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	if err := cmd.Run(); err != nil {
		log.Printf("Failed to execute schema: %v", err)
		return
	}

	log.Println("✅ Schema applied successfully")
}
