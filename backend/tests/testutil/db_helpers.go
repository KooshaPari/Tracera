package testutil

import (
	"context"
	"fmt"
	"os"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
)

// TruncateAllTables removes all data from test tables while preserving schema.
// This is useful for cleaning up between test runs without recreating the database.
// Tables are truncated in reverse dependency order to handle foreign keys.
//
// Example:
//
//	err := TruncateAllTables(ctx, pool)
//	if err != nil {
//	    t.Fatalf("failed to truncate tables: %v", err)
//	}
func TruncateAllTables(ctx context.Context, pool *pgxpool.Pool) error {
	tables := []string{
		"link_embeddings",
		"item_embeddings",
		"links",
		"items",
		"project_members",
		"projects",
		"user_profiles",
	}

	tx, err := pool.Begin(ctx)
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback(ctx)

	for _, table := range tables {
		_, err := tx.Exec(ctx, "TRUNCATE TABLE "+table+" RESTART IDENTITY CASCADE")
		if err != nil {
			return fmt.Errorf("failed to truncate table %s: %w", table, err)
		}
	}

	if err := tx.Commit(ctx); err != nil {
		return fmt.Errorf("failed to commit transaction: %w", err)
	}

	return nil
}

// ExecuteMigrations runs SQL schema migrations from the specified file.
// This is typically called once per test suite to set up the database schema.
//
// Example:
//
//	err := ExecuteMigrations(ctx, pool, "../../src/schema.sql")
//	if err != nil {
//	    t.Fatalf("failed to run migrations: %v", err)
//	}
func ExecuteMigrations(ctx context.Context, pool *pgxpool.Pool, schemaPath string) error {
	sqlContent, err := os.ReadFile(schemaPath)
	if err != nil {
		return fmt.Errorf("failed to read schema file: %w", err)
	}

	_, err = pool.Exec(ctx, string(sqlContent))
	if err != nil {
		return fmt.Errorf("failed to execute migrations: %w", err)
	}

	return nil
}

// CreateTestProject creates a test project with the given name and returns its ID.
// The project is created with default test values and a random UUID.
//
// Example:
//
//	projectID, err := CreateTestProject(ctx, pool, "Test Project")
//	if err != nil {
//	    t.Fatalf("failed to create test project: %v", err)
//	}
func CreateTestProject(ctx context.Context, pool *pgxpool.Pool, name string) (uuid.UUID, error) {
	projectID := uuid.New()
	ownerID := uuid.New()

	// Create user profile first
	_, err := pool.Exec(ctx, `
		INSERT INTO user_profiles (id, email, display_name, avatar_url, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6)
	`, ownerID, "test@example.com", "Test User", "https://example.com/avatar.jpg", time.Now(), time.Now())
	if err != nil {
		return uuid.Nil, fmt.Errorf("failed to create test user: %w", err)
	}

	// Create project
	_, err = pool.Exec(ctx, `
		INSERT INTO projects (id, name, description, owner_id, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6)
	`, projectID, name, "Test project description", ownerID, time.Now(), time.Now())
	if err != nil {
		return uuid.Nil, fmt.Errorf("failed to create project: %w", err)
	}

	// Add owner as project member
	_, err = pool.Exec(ctx, `
		INSERT INTO project_members (project_id, user_id, role, joined_at)
		VALUES ($1, $2, $3, $4)
	`, projectID, ownerID, "owner", time.Now())
	if err != nil {
		return uuid.Nil, fmt.Errorf("failed to add project member: %w", err)
	}

	return projectID, nil
}

// CreateTestItem creates a test item in the specified project and returns its ID.
// The item is created with default test values and a random UUID.
//
// Example:
//
//	itemID, err := CreateTestItem(ctx, pool, projectID, "Test Item Title")
//	if err != nil {
//	    t.Fatalf("failed to create test item: %v", err)
//	}
func CreateTestItem(ctx context.Context, pool *pgxpool.Pool, projectID uuid.UUID, title string) (uuid.UUID, error) {
	itemID := uuid.New()

	_, err := pool.Exec(ctx, `
		INSERT INTO items (id, project_id, title, description, status, type, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
	`, itemID, projectID, title, "Test item description", "open", "task", time.Now(), time.Now())
	if err != nil {
		return uuid.Nil, fmt.Errorf("failed to create item: %w", err)
	}

	return itemID, nil
}

// CreateTestLink creates a test link between two items and returns its ID.
// The link is created with default test values and a random UUID.
//
// Example:
//
//	linkID, err := CreateTestLink(ctx, pool, sourceItemID, targetItemID)
//	if err != nil {
//	    t.Fatalf("failed to create test link: %v", err)
//	}
func CreateTestLink(ctx context.Context, pool *pgxpool.Pool, sourceID, targetID uuid.UUID) (uuid.UUID, error) {
	linkID := uuid.New()

	_, err := pool.Exec(ctx, `
		INSERT INTO links (id, source_id, target_id, link_type, created_at)
		VALUES ($1, $2, $3, $4, $5)
	`, linkID, sourceID, targetID, "relates_to", time.Now())
	if err != nil {
		return uuid.Nil, fmt.Errorf("failed to create link: %w", err)
	}

	return linkID, nil
}

// CreateTestItemWithEmbedding creates a test item and its embedding vector.
// This is useful for testing vector search and similarity functionality.
//
// Example:
//
//	itemID, err := CreateTestItemWithEmbedding(ctx, pool, projectID, "Test Item", embedding)
//	if err != nil {
//	    t.Fatalf("failed to create test item with embedding: %v", err)
//	}
func CreateTestItemWithEmbedding(ctx context.Context, pool *pgxpool.Pool, projectID uuid.UUID, title string, embedding []float32) (uuid.UUID, error) {
	itemID, err := CreateTestItem(ctx, pool, projectID, title)
	if err != nil {
		return uuid.Nil, err
	}

	_, err = pool.Exec(ctx, `
		INSERT INTO item_embeddings (item_id, embedding, created_at)
		VALUES ($1, $2, $3)
	`, itemID, embedding, time.Now())
	if err != nil {
		return uuid.Nil, fmt.Errorf("failed to create item embedding: %w", err)
	}

	return itemID, nil
}

// GetProjectByID retrieves a project by its ID for test verification.
//
// Example:
//
//	project, err := GetProjectByID(ctx, pool, projectID)
//	if err != nil {
//	    t.Fatalf("failed to get project: %v", err)
//	}
func GetProjectByID(ctx context.Context, pool *pgxpool.Pool, projectID uuid.UUID) (map[string]interface{}, error) {
	var name, description string
	var ownerID uuid.UUID
	var createdAt, updatedAt time.Time

	err := pool.QueryRow(ctx, `
		SELECT name, description, owner_id, created_at, updated_at
		FROM projects WHERE id = $1
	`, projectID).Scan(&name, &description, &ownerID, &createdAt, &updatedAt)
	if err != nil {
		return nil, fmt.Errorf("failed to get project: %w", err)
	}

	return map[string]interface{}{
		"id":          projectID,
		"name":        name,
		"description": description,
		"owner_id":    ownerID,
		"created_at":  createdAt,
		"updated_at":  updatedAt,
	}, nil
}

// GetItemByID retrieves an item by its ID for test verification.
//
// Example:
//
//	item, err := GetItemByID(ctx, pool, itemID)
//	if err != nil {
//	    t.Fatalf("failed to get item: %v", err)
//	}
func GetItemByID(ctx context.Context, pool *pgxpool.Pool, itemID uuid.UUID) (map[string]interface{}, error) {
	var projectID uuid.UUID
	var title, description, status, itemType string
	var createdAt, updatedAt time.Time

	err := pool.QueryRow(ctx, `
		SELECT project_id, title, description, status, type, created_at, updated_at
		FROM items WHERE id = $1
	`, itemID).Scan(&projectID, &title, &description, &status, &itemType, &createdAt, &updatedAt)
	if err != nil {
		return nil, fmt.Errorf("failed to get item: %w", err)
	}

	return map[string]interface{}{
		"id":          itemID,
		"project_id":  projectID,
		"title":       title,
		"description": description,
		"status":      status,
		"type":        itemType,
		"created_at":  createdAt,
		"updated_at":  updatedAt,
	}, nil
}
