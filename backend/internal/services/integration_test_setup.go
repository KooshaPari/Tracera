//go:build integration
// +build integration

package services

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// IntegrationTestContainer holds PostgreSQL container and connection information
// Follows domain-driven architecture: named by purpose (Integration Testing) not phase
type IntegrationTestContainer struct {
	Container testcontainers.Container
	Pool      *pgxpool.Pool
	DB        *gorm.DB
	DSN       string
}

// SetupIntegrationPostgresContainer creates a PostgreSQL container for service integration tests
// Domain-driven naming: reflects purpose (integration testing) not implementation phase
func SetupIntegrationPostgresContainer(ctx context.Context, t testing.TB) *IntegrationTestContainer {
	req := testcontainers.ContainerRequest{
		Image:        "postgres:15-alpine",
		ExposedPorts: []string{"5432/tcp"},
		Env: map[string]string{
			"POSTGRES_USER":     "tracertm",
			"POSTGRES_PASSWORD": "tracertm_password",
			"POSTGRES_DB":       "tracertm_test",
		},
		WaitingFor: wait.ForLog("database system is ready to accept connections").
			WithOccurrence(2).
			WithStartupTimeout(30 * time.Second),
	}

	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	if err != nil {
		t.Fatalf("Failed to create PostgreSQL container: %v", err)
	}

	// Get mapped port
	port, err := container.MappedPort(ctx, "5432")
	if err != nil {
		container.Terminate(ctx)
		t.Fatalf("Failed to get mapped port: %v", err)
	}

	host, err := container.Host(ctx)
	if err != nil {
		container.Terminate(ctx)
		t.Fatalf("Failed to get container host: %v", err)
	}

	// Construct DSN
	dsn := fmt.Sprintf("host=%s port=%s user=tracertm password=tracertm_password dbname=tracertm_test sslmode=disable",
		host, port.Port())

	// Create pgxpool connection
	dbPool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		container.Terminate(ctx)
		t.Fatalf("Failed to create pgxpool connection: %v", err)
	}

	// Create GORM connection for migration and testing
	gormDB, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		container.Terminate(ctx)
		_ = dbPool.Close()
		t.Fatalf("Failed to create GORM connection: %v", err)
	}

	return &IntegrationTestContainer{
		Container: container,
		Pool:      dbPool,
		DB:        gormDB,
		DSN:       dsn,
	}
}

// Close cleanly closes the container and connections
func (pc *IntegrationTestContainer) Close(ctx context.Context) error {
	if pc.Pool != nil {
		pc.Pool.Close()
	}

	if pc.Container != nil {
		return pc.Container.Terminate(ctx)
	}

	return nil
}

// InitializeSchema initializes the database schema using raw SQL
func (pc *IntegrationTestContainer) InitializeSchema(ctx context.Context, t testing.TB) error {
	schema := `
	-- Projects table
	CREATE TABLE IF NOT EXISTS projects (
		id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
		name VARCHAR(255) NOT NULL,
		description TEXT,
		metadata JSONB,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		deleted_at TIMESTAMP
	);

	-- Items table
	CREATE TABLE IF NOT EXISTS items (
		id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
		project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
		title VARCHAR(255) NOT NULL,
		description TEXT,
		type VARCHAR(50),
		status VARCHAR(50),
		priority INTEGER,
		metadata JSONB,
		search_vector TSVECTOR,
		embedding vector(1536),
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		deleted_at TIMESTAMP
	);

	-- Links table
	CREATE TABLE IF NOT EXISTS links (
		id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
		source_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
		target_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
		type VARCHAR(50),
		metadata JSONB,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		deleted_at TIMESTAMP
	);

	-- Agents table
	CREATE TABLE IF NOT EXISTS agents (
		id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
		project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
		name VARCHAR(255) NOT NULL,
		status VARCHAR(50),
		metadata JSONB,
		last_activity_at TIMESTAMP,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		deleted_at TIMESTAMP
	);

	-- Indexes
	CREATE INDEX IF NOT EXISTS idx_items_project_id ON items(project_id);
	CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
	CREATE INDEX IF NOT EXISTS idx_links_source_id ON links(source_id);
	CREATE INDEX IF NOT EXISTS idx_links_target_id ON links(target_id);
	CREATE INDEX IF NOT EXISTS idx_agents_project_id ON agents(project_id);
	`

	if err := pc.DB.Exec(schema).Error; err != nil {
		return fmt.Errorf("failed to initialize schema: %w", err)
	}

	return nil
}

// ItemRepository returns a configured repository for testing ItemService
func (pc *IntegrationTestContainer) ItemRepository() repository.ItemRepository {
	return repository.NewItemRepository(pc.DB)
}

// LinkRepository returns a configured repository for testing LinkService
func (pc *IntegrationTestContainer) LinkRepository() repository.LinkRepository {
	return repository.NewLinkRepository(pc.DB)
}

// ProjectRepository returns a configured repository for testing ProjectService
func (pc *IntegrationTestContainer) ProjectRepository() repository.ProjectRepository {
	return repository.NewProjectRepository(pc.DB)
}

// AgentRepository returns a configured repository for testing AgentService
func (pc *IntegrationTestContainer) AgentRepository() repository.AgentRepository {
	return repository.NewAgentRepository(pc.DB)
}

// IntegrationTestHelper provides common test utilities for all domain service integration tests
// Follows domain-driven architecture: named by purpose (integration testing) not implementation phase
// Used by repository layer tests, service layer tests, and cross-domain tests
type IntegrationTestHelper struct {
	Ctx         context.Context
	Container   *IntegrationTestContainer
	ItemRepo    repository.ItemRepository
	LinkRepo    repository.LinkRepository
	ProjectRepo repository.ProjectRepository
	AgentRepo   repository.AgentRepository
}

// NewIntegrationTestHelper creates and sets up a test environment with isolated PostgreSQL container
// Domain-driven naming: reflects purpose (integration test helper) not implementation phase
// Automatically initializes database schema and all repositories
func NewIntegrationTestHelper(ctx context.Context, t testing.TB) *IntegrationTestHelper {
	container := SetupIntegrationPostgresContainer(ctx, t)
	if err := container.InitializeSchema(ctx, t); err != nil {
		container.Close(ctx)
		t.Fatalf("Failed to initialize schema: %v", err)
	}

	return &IntegrationTestHelper{
		Ctx:         ctx,
		Container:   container,
		ItemRepo:    container.ItemRepository(),
		LinkRepo:    container.LinkRepository(),
		ProjectRepo: container.ProjectRepository(),
		AgentRepo:   container.AgentRepository(),
	}
}

// Cleanup cleans up the test environment and closes all connections
func (h *IntegrationTestHelper) Cleanup() error {
	return h.Container.Close(h.Ctx)
}
