package server

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/config"
	"github.com/kooshapari/tracertm-backend/internal/infrastructure"
)

const (
	serverShutdownDelay           = 10 * time.Millisecond
	serverStartDelay              = 100 * time.Millisecond
	serverShutdownTimeout         = 2 * time.Second
	serverStartTimeout            = 3 * time.Second
	serverGracefulShutdownTimeout = 5 * time.Second
	serverImmediateTimeout        = 1 * time.Nanosecond
)

func createTestInfrastructure(t *testing.T) *infrastructure.Infrastructure {
	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	ctx := context.Background()
	pool, err := pgxpool.New(ctx, dbURL)
	if err != nil {
		t.Skipf("Failed to create database pool: %v", err)
	}

	gormDB, err := gorm.Open(postgres.Open(dbURL), &gorm.Config{})
	if err != nil {
		pool.Close()
		t.Skipf("Failed to create GORM DB: %v", err)
	}

	return &infrastructure.Infrastructure{
		DB:     pool,
		GormDB: gormDB,
	}
}

func createTestConfig() *config.Config {
	return &config.Config{
		DatabaseURL: os.Getenv("TEST_DATABASE_URL"),
		RedisURL:    "redis://localhost:6379",
		NATSUrl:     "nats://localhost:4222",
		Port:        "8080",
		Env:         "test",
	}
}
