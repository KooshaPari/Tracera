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

func TestScanItem(t *testing.T) {
	mock, err := pgxmock.NewConn()
	require.NoError(t, err)
	defer func() { require.NoError(t, mock.Close(context.Background())) }()

	t.Run("success", func(t *testing.T) {
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

		mock.ExpectQuery("SELECT").WillReturnRows(rows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM items LIMIT 1")
		item, err := ScanItem(row)
		require.NoError(t, err)
		assert.NotNil(t, item)
		assert.Equal(t, "Test Item", item.Title)
	})

	t.Run("not found", func(t *testing.T) {
		mock.ExpectQuery("SELECT").WithArgs(pgxmock.AnyArg()).WillReturnError(sql.ErrNoRows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM items WHERE id = $1", "nonexistent")
		item, err := ScanItem(row)
		assert.Error(t, err)
		assert.Nil(t, item)
		// Scanner returns "item not found" when sql.ErrNoRows
		if err != nil {
			assert.Contains(t, err.Error(), "not found")
		}
	})

	t.Run("scan error", func(t *testing.T) {
		scanErr := errors.New("scan error: column mismatch")
		rows := mock.NewRows([]string{"id"}).AddRow("invalid").RowError(0, scanErr)

		mock.ExpectQuery("SELECT").WillReturnRows(rows)

		row := mock.QueryRow(context.Background(), "SELECT id FROM items LIMIT 1")
		item, err := ScanItem(row)
		assert.Error(t, err)
		assert.Nil(t, item)
	})
}

// TestScanItems tests scanning of multiple items
//
//nolint:funlen
func TestScanItems(t *testing.T) {
	mock, err := pgxmock.NewConn()
	require.NoError(t, err)
	defer func() { require.NoError(t, mock.Close(context.Background())) }()

	t.Run("success with multiple items", func(t *testing.T) {
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

		mock.ExpectQuery("SELECT").WillReturnRows(rows)

		rowsResult, err := mock.Query(context.Background(), "SELECT * FROM items")
		require.NoError(t, err)

		items, err := ScanItems(rowsResult)
		require.NoError(t, err)
		assert.Equal(t, 2, len(items))
		assert.Equal(t, "Item 1", items[0].Title)
		assert.Equal(t, "Item 2", items[1].Title)
	})

	t.Run("empty result", func(t *testing.T) {
		rows := mock.NewRows([]string{
			"id", "project_id", "title", "description", "type", "status",
			"priority", "metadata", "search_vector", "embedding",
			"created_at", "updated_at", "deleted_at",
		})

		mock.ExpectQuery("SELECT").WillReturnRows(rows)

		rowsResult, err := mock.Query(context.Background(), "SELECT * FROM items")
		require.NoError(t, err)

		items, err := ScanItems(rowsResult)
		require.NoError(t, err)
		assert.Equal(t, 0, len(items))
	})
}

func TestScanLink(t *testing.T) {
	mock, err := pgxmock.NewConn()
	require.NoError(t, err)
	defer func() { require.NoError(t, mock.Close(context.Background())) }()

	t.Run("success", func(t *testing.T) {
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

		mock.ExpectQuery("SELECT").WillReturnRows(rows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM links LIMIT 1")
		link, err := ScanLink(row)
		require.NoError(t, err)
		assert.NotNil(t, link)
		assert.Equal(t, "depends_on", link.Type)
	})

	t.Run("not found", func(t *testing.T) {
		mock.ExpectQuery("SELECT").WithArgs(pgxmock.AnyArg()).WillReturnError(sql.ErrNoRows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM links WHERE id = $1", "nonexistent")
		link, err := ScanLink(row)
		assert.Error(t, err)
		assert.Nil(t, link)
		// Scanner returns "link not found" when sql.ErrNoRows
		if err != nil {
			assert.Contains(t, err.Error(), "not found")
		}
	})
}

func TestScanLinks(t *testing.T) {
	mock, err := pgxmock.NewConn()
	require.NoError(t, err)
	defer func() { require.NoError(t, mock.Close(context.Background())) }()

	t.Run("success with multiple links", func(t *testing.T) {
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

		mock.ExpectQuery("SELECT").WillReturnRows(rows)

		rowsResult, err := mock.Query(context.Background(), "SELECT * FROM links")
		require.NoError(t, err)

		links, err := ScanLinks(rowsResult)
		require.NoError(t, err)
		assert.Equal(t, 2, len(links))
		assert.Equal(t, "depends_on", links[0].Type)
		assert.Equal(t, "blocks", links[1].Type)
	})
}

func TestScanProject(t *testing.T) {
	mock, err := pgxmock.NewConn()
	require.NoError(t, err)
	defer func() { require.NoError(t, mock.Close(context.Background())) }()

	t.Run("success", func(t *testing.T) {
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

		mock.ExpectQuery("SELECT").WillReturnRows(rows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM projects LIMIT 1")
		project, err := ScanProject(row)
		require.NoError(t, err)
		assert.NotNil(t, project)
		assert.Equal(t, "Test Project", project.Name)
	})

	t.Run("not found", func(t *testing.T) {
		mock.ExpectQuery("SELECT").WithArgs(pgxmock.AnyArg()).WillReturnError(sql.ErrNoRows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM projects WHERE id = $1", "nonexistent")
		project, err := ScanProject(row)
		assert.Error(t, err)
		assert.Nil(t, project)
		assert.Contains(t, err.Error(), "project not found")
	})
}

func TestScanProjects(t *testing.T) {
	mock, err := pgxmock.NewConn()
	require.NoError(t, err)
	defer func() { require.NoError(t, mock.Close(context.Background())) }()

	t.Run("success with multiple projects", func(t *testing.T) {
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

		mock.ExpectQuery("SELECT").WillReturnRows(rows)

		rowsResult, err := mock.Query(context.Background(), "SELECT * FROM projects")
		require.NoError(t, err)

		projects, err := ScanProjects(rowsResult)
		require.NoError(t, err)
		assert.Equal(t, 2, len(projects))
		assert.Equal(t, "Project 1", projects[0].Name)
		assert.Equal(t, "Project 2", projects[1].Name)
	})
}

func TestScanAgent(t *testing.T) {
	mock, err := pgxmock.NewConn()
	require.NoError(t, err)
	defer func() { require.NoError(t, mock.Close(context.Background())) }()

	t.Run("success", func(t *testing.T) {
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

		mock.ExpectQuery("SELECT").WillReturnRows(rows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM agents LIMIT 1")
		agent, err := ScanAgent(row)
		require.NoError(t, err)
		assert.NotNil(t, agent)
		assert.Equal(t, "Test Agent", agent.Name)
		assert.Equal(t, "active", agent.Status)
	})

	t.Run("not found", func(t *testing.T) {
		mock.ExpectQuery("SELECT").WithArgs(pgxmock.AnyArg()).WillReturnError(sql.ErrNoRows)

		row := mock.QueryRow(context.Background(), "SELECT * FROM agents WHERE id = $1", "nonexistent")
		agent, err := ScanAgent(row)
		assert.Error(t, err)
		assert.Nil(t, agent)
		assert.Contains(t, err.Error(), "agent not found")
	})
}

func TestScanAgents(t *testing.T) {
	mock, err := pgxmock.NewConn()
	require.NoError(t, err)
	defer func() { require.NoError(t, mock.Close(context.Background())) }()

	t.Run("success with multiple agents", func(t *testing.T) {
		rows := mock.NewRows([]string{
			"id", "project_id", "name", "status", "metadata",
			"last_activity_at", "created_at", "updated_at", "deleted_at",
		}).AddRow(
			pgtype.UUID{Bytes: [16]byte{1}, Valid: true},
			pgtype.UUID{Bytes: [16]byte{2}, Valid: true},
			"Agent 1",
			"active",
			[]byte("{}"),
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Valid: false},
		).AddRow(
			pgtype.UUID{Bytes: [16]byte{3}, Valid: true},
			pgtype.UUID{Bytes: [16]byte{2}, Valid: true},
			"Agent 2",
			"idle",
			[]byte("{}"),
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Time: time.Now(), Valid: true},
			pgtype.Timestamp{Valid: false},
		)

		mock.ExpectQuery("SELECT").WillReturnRows(rows)

		rowsResult, err := mock.Query(context.Background(), "SELECT * FROM agents")
		require.NoError(t, err)

		agents, err := ScanAgents(rowsResult)
		require.NoError(t, err)
		assert.Equal(t, 2, len(agents))
		assert.Equal(t, "Agent 1", agents[0].Name)
		assert.Equal(t, "Agent 2", agents[1].Name)
	})
}

func TestScanDescendants(t *testing.T) {
	runScanEdgeTest(
		t,
		"descendants",
		ScanDescendants,
		func(edge *GetDescendantsRow) string { return edge.LinkType },
		func(edge *GetDescendantsRow) int32 { return edge.Depth },
	)
}

func TestScanAncestors(t *testing.T) {
	runScanEdgeTest(
		t,
		"ancestors",
		ScanAncestors,
		func(edge *GetAncestorsRow) string { return edge.LinkType },
		func(edge *GetAncestorsRow) int32 { return edge.Depth },
	)
}

func runScanEdgeTest[T any](
	t *testing.T,
	querySuffix string,
	scan func(pgx.Rows) ([]*T, error),
	getLinkType func(*T) string,
	getDepth func(*T) int32,
) {
	t.Helper()

	mock, err := pgxmock.NewConn()
	require.NoError(t, err)
	defer func() { require.NoError(t, mock.Close(context.Background())) }()

	t.Run("success", func(t *testing.T) {
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

		mock.ExpectQuery("WITH RECURSIVE").WillReturnRows(rows)

		rowsResult, err := mock.Query(context.Background(), "WITH RECURSIVE "+querySuffix)
		require.NoError(t, err)

		edges, err := scan(rowsResult)
		require.NoError(t, err)
		assert.Equal(t, 2, len(edges))
		assert.Equal(t, "depends_on", getLinkType(edges[0]))
		assert.Equal(t, int32(0), getDepth(edges[0]))
	})
}
