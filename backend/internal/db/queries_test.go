//go:build integration
// +build integration

package db

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
)

// setupTestQueries creates a PostgreSQL container and returns Queries instance
func setupTestQueries(t *testing.T) (*Queries, *pgxpool.Pool, testcontainers.Container) {
	ctx := context.Background()

	req := testcontainers.ContainerRequest{
		Image:        "postgres:16-alpine",
		ExposedPorts: []string{"5432/tcp"},
		Env: map[string]string{
			"POSTGRES_USER":     "testuser",
			"POSTGRES_PASSWORD": "testpass",
			"POSTGRES_DB":       "testdb",
		},
		WaitingFor: wait.ForLog("database system is ready to accept connections").
			WithOccurrence(2).
			WithStartupTimeout(30 * time.Second),
	}

	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	require.NoError(t, err)

	host, err := container.Host(ctx)
	require.NoError(t, err)

	port, err := container.MappedPort(ctx, "5432")
	require.NoError(t, err)

	connString := "postgres://testuser:testpass@" + host + ":" + port.Port() + "/testdb?sslmode=disable"

	pool, err := pgxpool.New(ctx, connString)
	require.NoError(t, err)

	// Run migrations using pgxpool
	// We need to use the pool's underlying connection for migrations
	conn, err := pool.Acquire(ctx)
	require.NoError(t, err)
	defer conn.Release()

	// Execute migration SQL directly
	migrationSQL := `
		CREATE TABLE IF NOT EXISTS projects (
			id uuid NOT NULL DEFAULT gen_random_uuid(),
			name varchar(255) NOT NULL,
			description text,
			metadata jsonb DEFAULT '{}'::jsonb,
			created_at timestamp NOT NULL DEFAULT now(),
			updated_at timestamp NOT NULL DEFAULT now(),
			deleted_at timestamp,
			PRIMARY KEY (id)
		);
		CREATE TABLE IF NOT EXISTS items (
			id uuid NOT NULL DEFAULT gen_random_uuid(),
			project_id uuid NOT NULL,
			title varchar(255) NOT NULL,
			description text,
			type varchar(50) NOT NULL,
			status varchar(50) NOT NULL,
			priority integer,
			metadata jsonb DEFAULT '{}'::jsonb,
			created_at timestamp NOT NULL DEFAULT now(),
			updated_at timestamp NOT NULL DEFAULT now(),
			deleted_at timestamp,
			PRIMARY KEY (id),
			FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
		);
		CREATE TABLE IF NOT EXISTS links (
			id uuid NOT NULL DEFAULT gen_random_uuid(),
			source_id uuid NOT NULL,
			target_id uuid NOT NULL,
			type varchar(50) NOT NULL,
			metadata jsonb DEFAULT '{}'::jsonb,
			created_at timestamp NOT NULL DEFAULT now(),
			updated_at timestamp NOT NULL DEFAULT now(),
			deleted_at timestamp,
			PRIMARY KEY (id),
			FOREIGN KEY (source_id) REFERENCES items(id) ON DELETE CASCADE,
			FOREIGN KEY (target_id) REFERENCES items(id) ON DELETE CASCADE
		);
		CREATE TABLE IF NOT EXISTS agents (
			id uuid NOT NULL DEFAULT gen_random_uuid(),
			project_id uuid NOT NULL,
			name varchar(255) NOT NULL,
			status varchar(50) NOT NULL,
			metadata jsonb DEFAULT '{}'::jsonb,
			last_activity_at timestamp,
			created_at timestamp NOT NULL DEFAULT now(),
			updated_at timestamp NOT NULL DEFAULT now(),
			deleted_at timestamp,
			PRIMARY KEY (id),
			FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
		);
	`
	_, err = conn.Exec(ctx, migrationSQL)
	require.NoError(t, err)

	queries := New(pool)
	return queries, pool, container
}

func TestCreateProject(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	t.Run("creates project successfully", func(t *testing.T) {
		project, err := queries.CreateProject(ctx, CreateProjectParams{
			Name:        "Test Project",
			Description: pgtype.Text{String: "Test Description", Valid: true},
			Metadata:    []byte(`{"key": "value"}`),
		})
		require.NoError(t, err)
		assert.Equal(t, "Test Project", project.Name)
		assert.Equal(t, "Test Description", project.Description.String)
		assert.NotEqual(t, uuid.Nil, project.ID)
	})

	t.Run("creates project with nil description", func(t *testing.T) {
		project, err := queries.CreateProject(ctx, CreateProjectParams{
			Name:        "Project No Desc",
			Description: pgtype.Text{Valid: false},
			Metadata:    []byte("{}"),
		})
		require.NoError(t, err)
		assert.Equal(t, "Project No Desc", project.Name)
		assert.False(t, project.Description.Valid)
	})
}

func TestGetProject(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	t.Run("gets existing project", func(t *testing.T) {
		created, err := queries.CreateProject(ctx, CreateProjectParams{
			Name:     "Get Test Project",
			Metadata: []byte("{}"),
		})
		require.NoError(t, err)

		retrieved, err := queries.GetProject(ctx, created.ID)
		require.NoError(t, err)
		assert.Equal(t, created.ID, retrieved.ID)
		assert.Equal(t, "Get Test Project", retrieved.Name)
	})

	t.Run("returns error for non-existent project", func(t *testing.T) {
		nonExistentID := uuid.New()
		var nonExistentUUID pgtype.UUID
		err := nonExistentUUID.Scan(nonExistentID.String())
		require.NoError(t, err)

		_, err = queries.GetProject(ctx, nonExistentUUID)
		assert.Error(t, err)
	})

	t.Run("does not return soft-deleted project", func(t *testing.T) {
		created, err := queries.CreateProject(ctx, CreateProjectParams{
			Name:     "To Delete",
			Metadata: []byte("{}"),
		})
		require.NoError(t, err)

		err = queries.DeleteProject(ctx, created.ID)
		require.NoError(t, err)

		_, err = queries.GetProject(ctx, created.ID)
		assert.Error(t, err)
	})
}

func TestDeleteProject(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	t.Run("soft deletes project", func(t *testing.T) {
		created, err := queries.CreateProject(ctx, CreateProjectParams{
			Name:     "Delete Test",
			Metadata: []byte("{}"),
		})
		require.NoError(t, err)

		err = queries.DeleteProject(ctx, created.ID)
		require.NoError(t, err)

		// Should not be retrievable
		_, err = queries.GetProject(ctx, created.ID)
		assert.Error(t, err)
	})
}

func TestCreateItem(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Create a project first
	project, err := queries.CreateProject(ctx, CreateProjectParams{
		Name:     "Item Test Project",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)
	projectUUID := project.ID

	t.Run("creates item successfully", func(t *testing.T) {
		item, err := queries.CreateItem(ctx, CreateItemParams{
			ProjectID:   projectUUID,
			Title:       "Test Item",
			Description: pgtype.Text{String: "Item Description", Valid: true},
			Type:        "task",
			Status:      "open",
			Priority:    pgtype.Int4{Int32: 1, Valid: true},
			Metadata:    []byte(`{"key": "value"}`),
		})
		require.NoError(t, err)
		assert.Equal(t, "Test Item", item.Title)
		assert.Equal(t, "task", item.Type)
		assert.Equal(t, "open", item.Status)
		assert.Equal(t, projectUUID, item.ProjectID)
	})

	t.Run("creates item with minimal fields", func(t *testing.T) {
		item, err := queries.CreateItem(ctx, CreateItemParams{
			ProjectID:   projectUUID,
			Title:       "Minimal Item",
			Description: pgtype.Text{Valid: false},
			Type:        "task",
			Status:      "open",
			Priority:    pgtype.Int4{Valid: false},
			Metadata:    []byte("{}"),
		})
		require.NoError(t, err)
		assert.Equal(t, "Minimal Item", item.Title)
		assert.False(t, item.Description.Valid)
		assert.False(t, item.Priority.Valid)
	})
}

func TestGetItem(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Create project and item
	project, err := queries.CreateProject(ctx, CreateProjectParams{
		Name:     "Get Item Project",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)
	projectUUID := project.ID

	created, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Get Test Item",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	t.Run("gets existing item", func(t *testing.T) {
		retrieved, err := queries.GetItem(ctx, created.ID)
		require.NoError(t, err)
		assert.Equal(t, created.ID, retrieved.ID)
		assert.Equal(t, "Get Test Item", retrieved.Title)
	})

	t.Run("returns error for non-existent item", func(t *testing.T) {
		nonExistentID := uuid.New()
		var nonExistentUUID pgtype.UUID
		err := nonExistentUUID.Scan(nonExistentID.String())
		require.NoError(t, err)

		_, err = queries.GetItem(ctx, nonExistentUUID)
		assert.Error(t, err)
	})
}

func TestDeleteItem(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Create project and item
	project, err := queries.CreateProject(ctx, CreateProjectParams{
		Name:     "Delete Item Project",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)
	projectUUID := project.ID

	item, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "To Delete",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	t.Run("soft deletes item", func(t *testing.T) {
		err = queries.DeleteItem(ctx, item.ID)
		require.NoError(t, err)

		// Should not be retrievable
		_, err = queries.GetItem(ctx, item.ID)
		assert.Error(t, err)
	})
}

func TestListItemsByProject(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Create project
	project, err := queries.CreateProject(ctx, CreateProjectParams{
		Name:     "List Items Project",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)
	projectUUID := project.ID

	// Create multiple items
	for i := 0; i < 5; i++ {
		_, err = queries.CreateItem(ctx, CreateItemParams{
			ProjectID: projectUUID,
			Title:     "Item " + string(rune('A'+i)),
			Type:      "task",
			Status:    "open",
			Metadata:  []byte("{}"),
		})
		require.NoError(t, err)
	}

	t.Run("lists all items for project", func(t *testing.T) {
		items, err := queries.ListItemsByProject(ctx, ListItemsByProjectParams{
			ProjectID: projectUUID,
			Limit:     10,
			Offset:    0,
		})
		require.NoError(t, err)
		assert.Len(t, items, 5)
	})

	t.Run("respects limit and offset", func(t *testing.T) {
		items, err := queries.ListItemsByProject(ctx, ListItemsByProjectParams{
			ProjectID: projectUUID,
			Limit:     2,
			Offset:    0,
		})
		require.NoError(t, err)
		assert.Len(t, items, 2)

		items, err = queries.ListItemsByProject(ctx, ListItemsByProjectParams{
			ProjectID: projectUUID,
			Limit:     2,
			Offset:    2,
		})
		require.NoError(t, err)
		assert.Len(t, items, 2)
	})
}

func TestCreateLink(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Create project and items
	project, err := queries.CreateProject(ctx, CreateProjectParams{
		Name:     "Link Test Project",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)
	projectUUID := project.ID

	source, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Source Item",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	target, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Target Item",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	t.Run("creates link successfully", func(t *testing.T) {
		link, err := queries.CreateLink(ctx, CreateLinkParams{
			SourceID: source.ID,
			TargetID: target.ID,
			Type:     "depends_on",
			Metadata: []byte(`{"key": "value"}`),
		})
		require.NoError(t, err)
		assert.Equal(t, source.ID, link.SourceID)
		assert.Equal(t, target.ID, link.TargetID)
		assert.Equal(t, "depends_on", link.Type)
	})
}

func TestGetLink(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Create project and items
	project, err := queries.CreateProject(ctx, CreateProjectParams{
		Name:     "Get Link Project",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)
	projectUUID := project.ID

	source, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Source",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	target, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Target",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	created, err := queries.CreateLink(ctx, CreateLinkParams{
		SourceID: source.ID,
		TargetID: target.ID,
		Type:     "depends_on",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)

	t.Run("gets existing link", func(t *testing.T) {
		retrieved, err := queries.GetLink(ctx, created.ID)
		require.NoError(t, err)
		assert.Equal(t, created.ID, retrieved.ID)
		assert.Equal(t, source.ID, retrieved.SourceID)
		assert.Equal(t, target.ID, retrieved.TargetID)
	})
}

func TestGetAncestors(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Create project and items in a chain: A -> B -> C
	project, err := queries.CreateProject(ctx, CreateProjectParams{
		Name:     "Ancestors Project",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)
	projectUUID := project.ID

	itemA, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Item A",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	itemB, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Item B",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	itemC, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Item C",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	// Create links: A -> B -> C
	_, err = queries.CreateLink(ctx, CreateLinkParams{
		SourceID: itemA.ID,
		TargetID: itemB.ID,
		Type:     "depends_on",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)

	_, err = queries.CreateLink(ctx, CreateLinkParams{
		SourceID: itemB.ID,
		TargetID: itemC.ID,
		Type:     "depends_on",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)

	t.Run("gets ancestors recursively", func(t *testing.T) {
		ancestors, err := queries.GetAncestors(ctx, itemC.ID)
		require.NoError(t, err)
		assert.Len(t, ancestors, 2) // B and A

		// Check depths
		depths := make(map[pgtype.UUID]int32)
		for _, anc := range ancestors {
			depths[anc.ItemID] = anc.Depth
		}

		assert.Equal(t, int32(0), depths[itemB.ID]) // Direct parent
		assert.Equal(t, int32(1), depths[itemA.ID]) // Grandparent
	})
}

func TestGetDescendants(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Create project and items in a chain: A -> B -> C
	project, err := queries.CreateProject(ctx, CreateProjectParams{
		Name:     "Descendants Project",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)
	projectUUID := project.ID

	itemA, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Item A",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	itemB, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Item B",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	itemC, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Item C",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	// Create links: A -> B -> C
	_, err = queries.CreateLink(ctx, CreateLinkParams{
		SourceID: itemA.ID,
		TargetID: itemB.ID,
		Type:     "depends_on",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)

	_, err = queries.CreateLink(ctx, CreateLinkParams{
		SourceID: itemB.ID,
		TargetID: itemC.ID,
		Type:     "depends_on",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)

	t.Run("gets descendants recursively", func(t *testing.T) {
		descendants, err := queries.GetDescendants(ctx, itemA.ID)
		require.NoError(t, err)
		assert.Len(t, descendants, 2) // B and C

		// Check depths
		depths := make(map[pgtype.UUID]int32)
		for _, desc := range descendants {
			depths[desc.ItemID] = desc.Depth
		}

		assert.Equal(t, int32(0), depths[itemB.ID]) // Direct child
		assert.Equal(t, int32(1), depths[itemC.ID]) // Grandchild
	})
}

func TestCreateAgent(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Create project
	project, err := queries.CreateProject(ctx, CreateProjectParams{
		Name:     "Agent Test Project",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)
	projectUUID := project.ID

	t.Run("creates agent successfully", func(t *testing.T) {
		agent, err := queries.CreateAgent(ctx, CreateAgentParams{
			ProjectID: projectUUID,
			Name:      "Test Agent",
			Status:    "active",
			Metadata:  []byte(`{"key": "value"}`),
		})
		require.NoError(t, err)
		assert.Equal(t, "Test Agent", agent.Name)
		assert.Equal(t, "active", agent.Status)
		assert.Equal(t, projectUUID, agent.ProjectID)
	})
}

func TestGetAgent(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Create project and agent
	project, err := queries.CreateProject(ctx, CreateProjectParams{
		Name:     "Get Agent Project",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)
	projectUUID := project.ID

	created, err := queries.CreateAgent(ctx, CreateAgentParams{
		ProjectID: projectUUID,
		Name:      "Get Test Agent",
		Status:    "active",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	t.Run("gets existing agent", func(t *testing.T) {
		retrieved, err := queries.GetAgent(ctx, created.ID)
		require.NoError(t, err)
		assert.Equal(t, created.ID, retrieved.ID)
		assert.Equal(t, "Get Test Agent", retrieved.Name)
	})
}

func TestListAgentsByProject(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Create project
	project, err := queries.CreateProject(ctx, CreateProjectParams{
		Name:     "List Agents Project",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)
	projectUUID := project.ID

	// Create multiple agents
	for i := 0; i < 3; i++ {
		_, err = queries.CreateAgent(ctx, CreateAgentParams{
			ProjectID: projectUUID,
			Name:      "Agent " + string(rune('A'+i)),
			Status:    "active",
			Metadata:  []byte("{}"),
		})
		require.NoError(t, err)
	}

	t.Run("lists all agents for project", func(t *testing.T) {
		agents, err := queries.ListAgentsByProject(ctx, projectUUID)
		require.NoError(t, err)
		assert.Len(t, agents, 3)
	})
}

func TestUpdateItem(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Create project and item
	project, err := queries.CreateProject(ctx, CreateProjectParams{
		Name:     "Update Item Project",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)
	projectUUID := project.ID

	created, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Original Title",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	t.Run("updates item successfully", func(t *testing.T) {
		updated, err := queries.UpdateItem(ctx, UpdateItemParams{
			ID:          created.ID,
			Title:       "Updated Title",
			Description: pgtype.Text{String: "Updated Description", Valid: true},
			Type:        "bug",
			Status:      "in_progress",
			Priority:    pgtype.Int4{Int32: 2, Valid: true},
			Metadata:    []byte(`{"updated": true}`),
		})
		require.NoError(t, err)
		assert.Equal(t, "Updated Title", updated.Title)
		assert.Equal(t, "Updated Description", updated.Description.String)
		assert.Equal(t, "bug", updated.Type)
		assert.Equal(t, "in_progress", updated.Status)
		assert.True(t, updated.Priority.Valid)
		assert.Equal(t, int32(2), updated.Priority.Int32)
	})

	t.Run("returns error for non-existent item", func(t *testing.T) {
		nonExistentID := uuid.New()
		var nonExistentUUID pgtype.UUID
		err := nonExistentUUID.Scan(nonExistentID.String())
		require.NoError(t, err)

		_, err = queries.UpdateItem(ctx, UpdateItemParams{
			ID:       nonExistentUUID,
			Title:    "Should Fail",
			Type:     "task",
			Status:   "open",
			Metadata: []byte("{}"),
		})
		assert.Error(t, err)
	})

	t.Run("does not update soft-deleted item", func(t *testing.T) {
		// Create and delete an item
		item, err := queries.CreateItem(ctx, CreateItemParams{
			ProjectID: projectUUID,
			Title:     "To Delete",
			Type:      "task",
			Status:    "open",
			Metadata:  []byte("{}"),
		})
		require.NoError(t, err)

		err = queries.DeleteItem(ctx, item.ID)
		require.NoError(t, err)

		// Try to update deleted item
		_, err = queries.UpdateItem(ctx, UpdateItemParams{
			ID:       item.ID,
			Title:    "Should Fail",
			Type:     "task",
			Status:   "open",
			Metadata: []byte("{}"),
		})
		assert.Error(t, err)
	})
}

func TestGetLinkBySourceAndTarget(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Create project and items
	project, err := queries.CreateProject(ctx, CreateProjectParams{
		Name:     "Link Source Target Project",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)
	projectUUID := project.ID

	source, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Source",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	target, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Target",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	created, err := queries.CreateLink(ctx, CreateLinkParams{
		SourceID: source.ID,
		TargetID: target.ID,
		Type:     "depends_on",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)

	t.Run("gets link by source and target", func(t *testing.T) {
		retrieved, err := queries.GetLinkBySourceAndTarget(ctx, GetLinkBySourceAndTargetParams{
			SourceID: source.ID,
			TargetID: target.ID,
		})
		require.NoError(t, err)
		assert.Equal(t, created.ID, retrieved.ID)
		assert.Equal(t, source.ID, retrieved.SourceID)
		assert.Equal(t, target.ID, retrieved.TargetID)
	})

	t.Run("returns error when link doesn't exist", func(t *testing.T) {
		otherItem, err := queries.CreateItem(ctx, CreateItemParams{
			ProjectID: projectUUID,
			Title:     "Other",
			Type:      "task",
			Status:    "open",
			Metadata:  []byte("{}"),
		})
		require.NoError(t, err)

		_, err = queries.GetLinkBySourceAndTarget(ctx, GetLinkBySourceAndTargetParams{
			SourceID: source.ID,
			TargetID: otherItem.ID,
		})
		assert.Error(t, err)
	})
}

func TestGetImpactAnalysis(t *testing.T) {
	queries, pool, container := setupTestQueries(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Create project and items in a chain: A -> B -> C -> D
	project, err := queries.CreateProject(ctx, CreateProjectParams{
		Name:     "Impact Analysis Project",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)
	projectUUID := project.ID

	itemA, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Item A",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	itemB, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Item B",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	itemC, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Item C",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	itemD, err := queries.CreateItem(ctx, CreateItemParams{
		ProjectID: projectUUID,
		Title:     "Item D",
		Type:      "task",
		Status:    "open",
		Metadata:  []byte("{}"),
	})
	require.NoError(t, err)

	// Create links: A -> B -> C -> D
	_, err = queries.CreateLink(ctx, CreateLinkParams{
		SourceID: itemA.ID,
		TargetID: itemB.ID,
		Type:     "depends_on",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)

	_, err = queries.CreateLink(ctx, CreateLinkParams{
		SourceID: itemB.ID,
		TargetID: itemC.ID,
		Type:     "depends_on",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)

	_, err = queries.CreateLink(ctx, CreateLinkParams{
		SourceID: itemC.ID,
		TargetID: itemD.ID,
		Type:     "depends_on",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)

	t.Run("gets impact analysis recursively", func(t *testing.T) {
		impact, err := queries.GetImpactAnalysis(ctx, itemA.ID)
		require.NoError(t, err)
		assert.Len(t, impact, 3) // B, C, D

		// Check depths
		depths := make(map[pgtype.UUID]int32)
		for _, imp := range impact {
			depths[imp.ItemID] = imp.Depth
		}

		assert.Equal(t, int32(0), depths[itemB.ID]) // Direct impact
		assert.Equal(t, int32(1), depths[itemC.ID]) // Indirect
		assert.Equal(t, int32(2), depths[itemD.ID]) // Further indirect
	})
}
