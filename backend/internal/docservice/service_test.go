//go:build !integration

package docservice

import (
	"context"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewService(t *testing.T) {
	t.Run("creates service with nil pool", func(t *testing.T) {
		svc := NewService(nil)
		require.NotNil(t, svc)
		assert.Nil(t, svc.pool)
	})
}

func TestGetDocumentation(t *testing.T) {
	svc := NewService(nil)
	ctx := context.Background()

	result, err := svc.GetDocumentation(ctx, uuid.New())
	require.NoError(t, err)
	assert.Nil(t, result)
}

func TestIndexDocumentation(t *testing.T) {
	svc := NewService(nil)
	ctx := context.Background()

	result, err := svc.IndexDocumentation(ctx, "some payload")
	require.NoError(t, err)
	assert.Nil(t, result)
}

func TestListDocumentation(t *testing.T) {
	svc := NewService(nil)
	ctx := context.Background()

	tests := []struct {
		name   string
		projID uuid.UUID
		limit  int
		offset int
	}{
		{"zero pagination", uuid.New(), 0, 0},
		{"standard pagination", uuid.New(), 10, 0},
		{"offset pagination", uuid.New(), 10, 20},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, count, err := svc.ListDocumentation(ctx, tt.projID, tt.limit, tt.offset)
			require.NoError(t, err)
			assert.Nil(t, result)
			assert.Equal(t, 0, count)
		})
	}
}

func TestUpdateDocumentation(t *testing.T) {
	svc := NewService(nil)
	ctx := context.Background()

	result, err := svc.UpdateDocumentation(ctx, uuid.New(), "updated payload")
	require.NoError(t, err)
	assert.Nil(t, result)
}

func TestDeleteDocumentation(t *testing.T) {
	svc := NewService(nil)
	ctx := context.Background()

	err := svc.DeleteDocumentation(ctx, uuid.New())
	require.NoError(t, err)
}

func TestSearchDocumentation(t *testing.T) {
	svc := NewService(nil)
	ctx := context.Background()

	tests := []struct {
		name   string
		query  string
		limit  int
		offset int
	}{
		{"empty query", "", 10, 0},
		{"keyword query", "architecture", 10, 0},
		{"paginated query", "test", 5, 10},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, count, err := svc.SearchDocumentation(ctx, uuid.New(), tt.query, tt.limit, tt.offset)
			require.NoError(t, err)
			assert.Nil(t, result)
			assert.Equal(t, 0, count)
		})
	}
}

func TestNewDocumentationRepository(t *testing.T) {
	result := NewDocumentationRepository(nil)
	assert.Nil(t, result)
}

func TestIndexDocumentationRequest(t *testing.T) {
	req := IndexDocumentationRequest{
		ProjectID: "proj-123",
		Title:     "Test Doc",
		Format:    "markdown",
		Content:   "# Hello",
	}
	assert.Equal(t, "proj-123", req.ProjectID)
	assert.Equal(t, "Test Doc", req.Title)
	assert.Equal(t, "markdown", req.Format)
	assert.Equal(t, "# Hello", req.Content)
}

func TestParsedDocument(t *testing.T) {
	id := uuid.New()
	doc := ParsedDocument{
		ID:      id,
		Title:   "Test",
		Content: "Content here",
	}
	assert.Equal(t, id, doc.ID)
	assert.Equal(t, "Test", doc.Title)
	assert.Equal(t, "Content here", doc.Content)
}
