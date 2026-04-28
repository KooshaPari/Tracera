//go:build !integration && !e2e

package db

import (
	"context"
	"database/sql"
	"errors"
	"testing"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/pashagolub/pgxmock/v3"
	"github.com/pgvector/pgvector-go"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Helper function to add agent rows to mock
func addAgentRow(rows *pgxmock.Rows, id, projectID byte, name, status string) *pgxmock.Rows {
	return rows.AddRow(
		pgtype.UUID{Bytes: [16]byte{id}, Valid: true},
		pgtype.UUID{Bytes: [16]byte{projectID}, Valid: true},
		name,
		status,
		[]byte("{}"),
		pgtype.Timestamp{Time: time.Now(), Valid: true},
		pgtype.Timestamp{Time: time.Now(), Valid: true},
		pgtype.Timestamp{Time: time.Now(), Valid: true},
		pgtype.Timestamp{Valid: false},
	)
}

func TestScanItem(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		mock, err := pgxmock.NewConn()
		require.NoError(t, err)
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		rows := mock.NewRows([]string{
			"id", "project_id", "title", "description", "type", "status",
			"priority", "metadata", "search_vector", "embedding",
			"created_at", "updated_at", "deleted_at",
		}).AddRow(
			pgtype.UUID{Bytes: [16]byte{1}, Valid: true},
			pgtype.UUID{Bytes: [16]byte{2}, Valid: true},
			"Test Item",
			pgtype.Text{String: "Test Description", Valid: true},
			"task",
			"open",
			pgtype.Int4{Int32: 2, Valid: true},
			[]byte("{}"),
			nil,
			pgvector.Vector{},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Valid: false},
		)

		mock.ExpectQuery(".*").WillReturnRows(rows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM items LIMIT 1")
		item, err := ScanItem(row)
		require.NoError(t, err)
		assert.NotNil(t, item)
		assert.Equal(t, "Test Item", item.Title)

		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("not found", func(t *testing.T) {
		mock, err := pgxmock.NewConn()
		require.NoError(t, err)
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		mock.ExpectQuery(".*").WithArgs(pgxmock.AnyArg()).WillReturnError(sql.ErrNoRows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM items WHERE id = $1", "nonexistent")
		item, err := ScanItem(row)
		require.Error(t, err)
		assert.Nil(t, item)
		assert.Contains(t, err.Error(), "not found")

		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("scan error", func(t *testing.T) {
		mock, err := pgxmock.NewConn()
		require.NoError(t, err)
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		scanErr := errors.New("scan error: column mismatch")
		rows := mock.NewRows([]string{"id"}).AddRow("invalid").RowError(0, scanErr)

		mock.ExpectQuery(".*").WillReturnRows(rows)

		row := mock.QueryRow(context.Background(), "SELECT id FROM items LIMIT 1")
		item, err := ScanItem(row)
		require.Error(t, err)
		assert.Nil(t, item)

		require.NoError(t, mock.ExpectationsWereMet())
	})
}

// TestScanItems tests scanning of multiple items
func TestScanItems(t *testing.T) {
	t.Run("success with multiple items", func(t *testing.T) {
		mock, err := pgxmock.NewConn()
		require.NoError(t, err)
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		rows := mock.NewRows([]string{
			"id", "project_id", "title", "description", "type", "status",
			"priority", "metadata", "search_vector", "embedding",
			"created_at", "updated_at", "deleted_at",
		}).AddRow(
			pgtype.UUID{Bytes: [16]byte{1}, Valid: true},
			pgtype.UUID{Bytes: [16]byte{2}, Valid: true},
			"Item 1",
			pgtype.Text{String: "Desc 1", Valid: true},
			"task",
			"open",
			pgtype.Int4{Int32: 1, Valid: true},
			[]byte("{}"),
			nil,
			pgvector.Vector{},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Valid: false},
		).AddRow(
			pgtype.UUID{Bytes: [16]byte{3}, Valid: true},
			pgtype.UUID{Bytes: [16]byte{2}, Valid: true},
			"Item 2",
			pgtype.Text{String: "Desc 2", Valid: true},
			"bug",
			"closed",
			pgtype.Int4{Int32: 2, Valid: true},
			[]byte("{}"),
			nil,
			pgvector.Vector{},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Valid: false},
		)

		mock.ExpectQuery(".*").WillReturnRows(rows)

		rowsResult, err := mock.Query(context.Background(), "SELECT * FROM items")
		require.NoError(t, err)

		items, err := ScanItems(rowsResult)
		require.NoError(t, err)
		assert.Len(t, items, 2)
		assert.Equal(t, "Item 1", items[0].Title)
		assert.Equal(t, "Item 2", items[1].Title)

		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("empty result", func(t *testing.T) {
		mock, err := pgxmock.NewConn()
		require.NoError(t, err)
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		rows := mock.NewRows([]string{
			"id", "project_id", "title", "description", "type", "status",
			"priority", "metadata", "search_vector", "embedding",
			"created_at", "updated_at", "deleted_at",
		})

		mock.ExpectQuery(".*").WillReturnRows(rows)

		rowsResult, err := mock.Query(context.Background(), "SELECT * FROM items")
		require.NoError(t, err)

		items, err := ScanItems(rowsResult)
		require.NoError(t, err)
		assert.Empty(t, items)

		require.NoError(t, mock.ExpectationsWereMet())
	})
}

func TestScanLink(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		mock, err := pgxmock.NewConn()
		require.NoError(t, err)
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		rows := mock.NewRows([]string{
			"id", "source_id", "target_id", "type", "metadata",
			"created_at", "updated_at", "deleted_at",
		}).AddRow(
			pgtype.UUID{Bytes: [16]byte{1}, Valid: true},
			pgtype.UUID{Bytes: [16]byte{2}, Valid: true},
			pgtype.UUID{Bytes: [16]byte{3}, Valid: true},
			"depends_on",
			[]byte("{}"),
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Valid: false},
		)

		mock.ExpectQuery(".*").WillReturnRows(rows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM links LIMIT 1")
		link, err := ScanLink(row)
		require.NoError(t, err)
		assert.NotNil(t, link)
		assert.Equal(t, "depends_on", link.Type)

		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("not found", func(t *testing.T) {
		mock, err := pgxmock.NewConn()
		require.NoError(t, err)
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		mock.ExpectQuery(".*").WithArgs(pgxmock.AnyArg()).WillReturnError(sql.ErrNoRows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM links WHERE id = $1", "nonexistent")
		link, err := ScanLink(row)
		require.Error(t, err)
		assert.Nil(t, link)
		assert.Contains(t, err.Error(), "not found")

		require.NoError(t, mock.ExpectationsWereMet())
	})
}

func TestScanLinks(t *testing.T) {
	t.Run("success with multiple links", func(t *testing.T) {
		mock, err := pgxmock.NewConn()
		require.NoError(t, err)
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		rows := mock.NewRows([]string{
			"id", "source_id", "target_id", "type", "metadata",
			"created_at", "updated_at", "deleted_at",
		}).AddRow(
			pgtype.UUID{Bytes: [16]byte{1}, Valid: true},
			pgtype.UUID{Bytes: [16]byte{2}, Valid: true},
			pgtype.UUID{Bytes: [16]byte{3}, Valid: true},
			"depends_on",
			[]byte("{}"),
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Valid: false},
		).AddRow(
			pgtype.UUID{Bytes: [16]byte{4}, Valid: true},
			pgtype.UUID{Bytes: [16]byte{5}, Valid: true},
			pgtype.UUID{Bytes: [16]byte{6}, Valid: true},
			"blocks",
			[]byte("{}"),
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Valid: false},
		)

		mock.ExpectQuery(".*").WillReturnRows(rows)

		rowsResult, err := mock.Query(context.Background(), "SELECT * FROM links")
		require.NoError(t, err)

		links, err := ScanLinks(rowsResult)
		require.NoError(t, err)
		assert.Len(t, links, 2)
		assert.Equal(t, "depends_on", links[0].Type)
		assert.Equal(t, "blocks", links[1].Type)

		require.NoError(t, mock.ExpectationsWereMet())
	})
}

func TestScanProject(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		mock, err := pgxmock.NewConn()
		require.NoError(t, err)
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		rows := mock.NewRows([]string{
			"id", "name", "description", "metadata",
			"created_at", "updated_at", "deleted_at",
		}).AddRow(
			pgtype.UUID{Bytes: [16]byte{1}, Valid: true},
			"Test Project",
			pgtype.Text{String: "Test Description", Valid: true},
			[]byte("{}"),
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Valid: false},
		)

		mock.ExpectQuery(".*").WillReturnRows(rows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM projects LIMIT 1")
		project, err := ScanProject(row)
		require.NoError(t, err)
		assert.NotNil(t, project)
		assert.Equal(t, "Test Project", project.Name)

		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("not found", func(t *testing.T) {
		mock, err := pgxmock.NewConn()
		require.NoError(t, err)
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		mock.ExpectQuery(".*").WithArgs(pgxmock.AnyArg()).WillReturnError(sql.ErrNoRows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM projects WHERE id = $1", "nonexistent")
		project, err := ScanProject(row)
		require.Error(t, err)
		assert.Nil(t, project)
		assert.Contains(t, err.Error(), "project not found")

		require.NoError(t, mock.ExpectationsWereMet())
	})
}

func TestScanProjects(t *testing.T) {
	t.Run("success with multiple projects", func(t *testing.T) {
		mock, err := pgxmock.NewConn()
		require.NoError(t, err)
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		rows := mock.NewRows([]string{
			"id", "name", "description", "metadata",
			"created_at", "updated_at", "deleted_at",
		}).AddRow(
			pgtype.UUID{Bytes: [16]byte{1}, Valid: true},
			"Project 1",
			pgtype.Text{String: "Desc 1", Valid: true},
			[]byte("{}"),
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Valid: false},
		).AddRow(
			pgtype.UUID{Bytes: [16]byte{2}, Valid: true},
			"Project 2",
			pgtype.Text{String: "Desc 2", Valid: true},
			[]byte("{}"),
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Valid: false},
		)

		mock.ExpectQuery(".*").WillReturnRows(rows)

		rowsResult, err := mock.Query(context.Background(), "SELECT * FROM projects")
		require.NoError(t, err)

		projects, err := ScanProjects(rowsResult)
		require.NoError(t, err)
		assert.Len(t, projects, 2)
		assert.Equal(t, "Project 1", projects[0].Name)
		assert.Equal(t, "Project 2", projects[1].Name)

		require.NoError(t, mock.ExpectationsWereMet())
	})
}

func TestScanAgent(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		mock, err := pgxmock.NewConn()
		require.NoError(t, err)
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		rows := mock.NewRows([]string{
			"id", "project_id", "name", "status", "metadata",
			"last_activity_at", "created_at", "updated_at", "deleted_at",
		}).AddRow(
			pgtype.UUID{Bytes: [16]byte{1}, Valid: true},
			pgtype.UUID{Bytes: [16]byte{2}, Valid: true},
			"Test Agent",
			"active",
			[]byte("{}"),
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Valid: false},
		)

		mock.ExpectQuery(".*").WillReturnRows(rows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM agents LIMIT 1")
		agent, err := ScanAgent(row)
		require.NoError(t, err)
		assert.NotNil(t, agent)
		assert.Equal(t, "Test Agent", agent.Name)
		assert.Equal(t, "active", agent.Status)

		require.NoError(t, mock.ExpectationsWereMet())
	})

	t.Run("not found", func(t *testing.T) {
		mock, err := pgxmock.NewConn()
		require.NoError(t, err)
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		mock.ExpectQuery(".*").WithArgs(pgxmock.AnyArg()).WillReturnError(sql.ErrNoRows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM agents WHERE id = $1", "nonexistent")
		agent, err := ScanAgent(row)
		require.Error(t, err)
		assert.Nil(t, agent)
		assert.Contains(t, err.Error(), "agent not found")

		require.NoError(t, mock.ExpectationsWereMet())
	})
}

func TestScanAgents(t *testing.T) {
	t.Run("success with multiple agents", func(t *testing.T) {
		mock, err := pgxmock.NewConn()
		require.NoError(t, err)
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		rows := mock.NewRows([]string{
			"id", "project_id", "name", "status", "metadata",
			"last_activity_at", "created_at", "updated_at", "deleted_at",
		})
		rows = addAgentRow(rows, 1, 2, "Agent 1", "active")
		rows = addAgentRow(rows, 3, 2, "Agent 2", "idle")

		mock.ExpectQuery(".*").WillReturnRows(rows)

		rowsResult, err := mock.Query(context.Background(), "SELECT * FROM agents")
		require.NoError(t, err)

		agents, err := ScanAgents(rowsResult)
		require.NoError(t, err)
		assert.Len(t, agents, 2)
		assert.Equal(t, "Agent 1", agents[0].Name)
		assert.Equal(t, "Agent 2", agents[1].Name)

		require.NoError(t, mock.ExpectationsWereMet())
	})
}

// setupGraphScanMock creates a mock connection with graph scan rows.
func setupGraphScanMock(t *testing.T, queryFragment string) (pgxmock.PgxConnIface, pgx.Rows) {
	t.Helper()
	mock, err := pgxmock.NewConn()
	require.NoError(t, err)

	rows := mock.NewRows([]string{"item_id", "link_type", "depth"}).
		AddRow(
			pgtype.UUID{Bytes: [16]byte{1}, Valid: true},
			"depends_on",
			int32(0),
		).AddRow(
		pgtype.UUID{Bytes: [16]byte{2}, Valid: true},
		"blocks",
		int32(1),
	)

	mock.ExpectQuery(".*").WillReturnRows(rows)

	rowsResult, err := mock.Query(context.Background(), queryFragment)
	require.NoError(t, err)
	return mock, rowsResult
}

func TestScanDescendants(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		mock, rowsResult := setupGraphScanMock(t, "WITH RECURSIVE descendants")
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		edges, err := ScanDescendants(rowsResult)
		require.NoError(t, err)
		assert.Len(t, edges, 2)
		assert.Equal(t, "depends_on", edges[0].LinkType)
		assert.Equal(t, int32(0), edges[0].Depth)
		require.NoError(t, mock.ExpectationsWereMet())
	})
}

func TestScanAncestors(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		mock, rowsResult := setupGraphScanMock(t, "WITH RECURSIVE ancestors")
		defer func() {
			if err := mock.Close(context.Background()); err != nil {
				t.Logf("cleanup close error: %v", err)
			}
		}()

		edges, err := ScanAncestors(rowsResult)
		require.NoError(t, err)
		assert.Len(t, edges, 2)
		assert.Equal(t, "depends_on", edges[0].LinkType)
		assert.Equal(t, int32(0), edges[0].Depth)
		require.NoError(t, mock.ExpectationsWereMet())
	})
}
