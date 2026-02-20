//go:build !integration && !e2e

package search

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewQueryBuilder(t *testing.T) {
	qb := NewQueryBuilder()
	require.NotNil(t, qb)
	assert.Empty(t, qb.selectCols)
	assert.Empty(t, qb.fromTable)
	assert.Empty(t, qb.whereClause)
	assert.Empty(t, qb.orderBy)
	assert.Equal(t, 1, qb.argIndex)
	assert.Empty(t, qb.args)
}

func TestQueryBuilder_Select(t *testing.T) {
	qb := NewQueryBuilder().Select("id", "title", "description")
	assert.Len(t, qb.selectCols, 3)
	assert.Equal(t, "id", qb.selectCols[0])
	assert.Equal(t, "title", qb.selectCols[1])
	assert.Equal(t, "description", qb.selectCols[2])

	qb.Select("created_at")
	assert.Len(t, qb.selectCols, 4)
	assert.Equal(t, "created_at", qb.selectCols[3])
}

func TestQueryBuilder_From(t *testing.T) {
	qb := NewQueryBuilder().From("items")
	assert.Equal(t, "items", qb.fromTable)

	qb.From("projects")
	assert.Equal(t, "projects", qb.fromTable)
}

func TestQueryBuilder_Where(t *testing.T) {
	qb := NewQueryBuilder().Where("id = ?", "abc-123")
	require.Len(t, qb.whereClause, 1)
	assert.Contains(t, qb.whereClause[0], "$1")
	require.Len(t, qb.args, 1)
	assert.Equal(t, "abc-123", qb.args[0])

	qb.Where("project_id = ?", "proj-456")
	require.Len(t, qb.whereClause, 2)
	assert.Contains(t, qb.whereClause[1], "$2")
	require.Len(t, qb.args, 2)
	assert.Equal(t, "proj-456", qb.args[1])
}

func TestQueryBuilder_Where_MultiplePlaceholders(t *testing.T) {
	qb := NewQueryBuilder().Where("a = ? AND b = ?", 1, 2)
	require.Len(t, qb.whereClause, 1)
	assert.Contains(t, qb.whereClause[0], "$1")
	assert.Contains(t, qb.whereClause[0], "$2")
	require.Len(t, qb.args, 2)
	assert.Equal(t, 1, qb.args[0])
	assert.Equal(t, 2, qb.args[1])
}

func TestQueryBuilder_OrderBy(t *testing.T) {
	qb := NewQueryBuilder().OrderBy("created_at", "DESC")
	require.Len(t, qb.orderBy, 1)
	assert.Equal(t, "created_at DESC", qb.orderBy[0])

	qb.OrderBy("title", "asc")
	require.Len(t, qb.orderBy, 2)
	assert.Equal(t, "title ASC", qb.orderBy[1])

	qb.OrderBy("score", "invalid")
	assert.Equal(t, "score ASC", qb.orderBy[2])
}

func TestQueryBuilder_Limit(t *testing.T) {
	qb := NewQueryBuilder().Limit(10)
	assert.Equal(t, 10, qb.limitVal)
}

func TestQueryBuilder_Offset(t *testing.T) {
	qb := NewQueryBuilder().Offset(5)
	assert.Equal(t, 5, qb.offsetVal)
}

func TestQueryBuilder_Build_Empty(t *testing.T) {
	qb := NewQueryBuilder()
	query, args := qb.Build()
	assert.Equal(t, "SELECT *", query)
	assert.Empty(t, args)
}

func TestQueryBuilder_Build_FromOnly(t *testing.T) {
	qb := NewQueryBuilder().From("items")
	query, args := qb.Build()
	assert.Equal(t, "SELECT * FROM items", query)
	assert.Empty(t, args)
}

func TestQueryBuilder_Build_Full(t *testing.T) {
	qb := NewQueryBuilder().
		Select("id", "title").
		From("items").
		Where("project_id = ?", "p1").
		Where("deleted_at IS NULL").
		OrderBy("created_at", "DESC").
		Limit(20).
		Offset(0)

	query, args := qb.Build()
	assert.Contains(t, query, "SELECT id, title")
	assert.Contains(t, query, "FROM items")
	assert.Contains(t, query, "WHERE ")
	assert.Contains(t, query, "AND ")
	assert.Contains(t, query, "ORDER BY created_at DESC")
	assert.Contains(t, query, "LIMIT ")
	assert.Contains(t, query, "OFFSET ")
	require.Len(t, args, 3)
	assert.Equal(t, "p1", args[0])
	assert.Equal(t, 20, args[1])
	assert.Equal(t, 0, args[2])
}

func TestQueryBuilder_Build_LimitOnly(t *testing.T) {
	qb := NewQueryBuilder().From("items").Limit(5)
	query, args := qb.Build()
	assert.Contains(t, query, "LIMIT $1")
	// Offset is implicit for pagination when a LIMIT is used.
	assert.Contains(t, query, "OFFSET $2")
	require.Len(t, args, 2)
	assert.Equal(t, 5, args[0])
	assert.Equal(t, 0, args[1])
}

func TestQueryBuilder_Build_OffsetOnly(t *testing.T) {
	qb := NewQueryBuilder().From("items").Offset(10)
	query, args := qb.Build()
	assert.Contains(t, query, "OFFSET $1")
	require.Len(t, args, 1)
	assert.Equal(t, 10, args[0])
}

func TestQueryBuilder_Chained(t *testing.T) {
	qb := NewQueryBuilder().
		Select("id").
		From("items").
		Where("id = ?", "x").
		OrderBy("id", "ASC").
		Limit(1).
		Offset(0)

	query, args := qb.Build()
	assert.NotEmpty(t, query)
	require.Len(t, args, 3)
	assert.Equal(t, "x", args[0])
	assert.Equal(t, 1, args[1])
	assert.Equal(t, 0, args[2])
}
