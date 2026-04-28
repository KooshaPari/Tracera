package docindex

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestRepositoryInterface verifies that MockRepository implements Repository
func TestRepositoryInterface(t *testing.T) {
	_ = t
	var _ Repository = (*MockRepository)(nil)
}

// TestSaveAndRetrieveDocEntity tests saving and retrieving a doc entity
func TestSaveAndRetrieveDocEntity(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	entity := &DocEntity{
		ID:        uuid.New(),
		ProjectID: uuid.New(),
		Type:      DocTypeDocument,
		FilePath:  "test.md",
		Title:     "Test Document",
		Content:   "Test content",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		IndexedAt: time.Now(),
	}

	err := repo.SaveDocEntity(ctx, entity)
	require.NoError(t, err)

	retrieved, err := repo.GetDocEntity(ctx, entity.ID)
	require.NoError(t, err)
	assert.NotNil(t, retrieved)
	assert.Equal(t, entity.ID, retrieved.ID)
	assert.Equal(t, entity.Title, retrieved.Title)
}

// TestSaveMultipleDocEntities tests saving multiple entities
func TestSaveMultipleDocEntities(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	entities := []*DocEntity{
		{
			ID:        uuid.New(),
			ProjectID: uuid.New(),
			Type:      DocTypeDocument,
			Title:     "Doc 1",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
			IndexedAt: time.Now(),
		},
		{
			ID:        uuid.New(),
			ProjectID: uuid.New(),
			Type:      DocTypeSection,
			Title:     "Doc 2",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
			IndexedAt: time.Now(),
		},
	}

	for _, e := range entities {
		err := repo.SaveDocEntity(ctx, e)
		require.NoError(t, err)
	}

	assert.Len(t, repo.savedEntities, 2)
}

// TestDeleteDocEntity tests entity deletion
func TestDeleteDocEntity(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	id := uuid.New()
	err := repo.DeleteDocEntity(ctx, id)
	require.NoError(t, err)

	assert.Len(t, repo.deletedIDs, 1)
	assert.Equal(t, id, repo.deletedIDs[0])
}

// TestListDocEntities tests listing doc entities
func TestListDocEntities(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	projectID := uuid.New()
	opts := &ListOptions{
		Limit:  10,
		Offset: 0,
	}

	entities, err := repo.ListDocEntities(ctx, projectID, opts)
	require.NoError(t, err)
	assert.NotNil(t, entities)
}

// TestSearchByEmbedding tests embedding-based search
func TestSearchByEmbedding(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	projectID := uuid.New()
	embedding := make([]float32, 10)
	for i := range embedding {
		embedding[i] = 0.5
	}

	results, err := repo.SearchByEmbedding(ctx, projectID, embedding, 10)
	require.NoError(t, err)
	assert.NotNil(t, results)
}

// TestGetDocumentSections tests retrieving sections for a document
func TestGetDocumentSections(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	documentID := uuid.New()
	sections, err := repo.GetDocumentSections(ctx, documentID)
	require.NoError(t, err)
	assert.NotNil(t, sections)
}

// TestGetSectionChunks tests retrieving chunks for a section
func TestGetSectionChunks(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	sectionID := uuid.New()
	chunks, err := repo.GetSectionChunks(ctx, sectionID)
	require.NoError(t, err)
	assert.NotNil(t, chunks)
}

// TestSaveTraceLink tests saving a trace link
func TestSaveTraceLink(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	link := &TraceLink{
		ID: uuid.New(),
	}

	err := repo.SaveTraceLink(ctx, link)
	require.NoError(t, err)
	assert.Len(t, repo.savedLinks, 1)
}

// TestGetTraceLinks tests retrieving trace links
func TestGetTraceLinks(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	sourceID := uuid.New()
	links, err := repo.GetTraceLinks(ctx, sourceID)
	require.NoError(t, err)
	assert.NotNil(t, links)
}

// TestDeleteTraceLink tests deleting a trace link
func TestDeleteTraceLink(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	id := uuid.New()
	err := repo.DeleteTraceLink(ctx, id)
	require.NoError(t, err)
	assert.Len(t, repo.deletedLinkIDs, 1)
}

// TestDeleteByDocument tests deleting all entities for a document
func TestDeleteByDocument(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	documentID := uuid.New()
	err := repo.DeleteByDocument(ctx, documentID)
	require.NoError(t, err)
}

// TestListOptionsFiltering tests ListOptions functionality
func TestListOptionsFiltering(t *testing.T) {
	opts := &ListOptions{
		Type:          DocTypeSection,
		FilePath:      "/docs/guide.md",
		Limit:         20,
		Offset:        10,
		IncludeChunks: true,
	}

	assert.Equal(t, DocTypeSection, opts.Type)
	assert.Equal(t, "/docs/guide.md", opts.FilePath)
	assert.Equal(t, 20, opts.Limit)
	assert.Equal(t, 10, opts.Offset)
	assert.True(t, opts.IncludeChunks)
}

// TestSearchOptionsConfiguration tests SearchOptions
func TestSearchOptionsConfiguration(t *testing.T) {
	opts := &SearchOptions{
		Query:    "authentication",
		Types:    []DocEntityType{DocTypeSection, DocTypeChunk},
		Limit:    50,
		MinScore: 0.7,
	}

	assert.Equal(t, "authentication", opts.Query)
	assert.Len(t, opts.Types, 2)
	assert.Equal(t, 50, opts.Limit)
	assert.InEpsilon(t, 0.7, opts.MinScore, 1e-9)
}

// TestSearchResult tests Result structure
func TestSearchResult(t *testing.T) {
	entity := DocEntity{
		ID:    uuid.New(),
		Title: "Test",
	}

	result := Result{
		Entity: entity,
		Score:  0.95,
	}

	assert.Equal(t, entity.ID, result.Entity.ID)
	assert.InEpsilon(t, 0.95, result.Score, 1e-9)
}

// TestDocEntityHierarchy tests parent-child entity relationships
func TestDocEntityHierarchy(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	projectID := uuid.New()
	parentID := uuid.New()
	childID := uuid.New()

	parent := &DocEntity{
		ID:        parentID,
		ProjectID: projectID,
		Type:      DocTypeSection,
		Title:     "Parent Section",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		IndexedAt: time.Now(),
	}

	child := &DocEntity{
		ID:        childID,
		ProjectID: projectID,
		ParentID:  &parentID,
		Type:      DocTypeChunk,
		Title:     "Child Chunk",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		IndexedAt: time.Now(),
	}

	err := repo.SaveDocEntity(ctx, parent)
	require.NoError(t, err)
	err = repo.SaveDocEntity(ctx, child)
	require.NoError(t, err)

	// Retrieve and verify hierarchy
	retrievedParent, err := repo.GetDocEntity(ctx, parentID)
	require.NoError(t, err)
	assert.Nil(t, retrievedParent.ParentID)

	retrievedChild, err := repo.GetDocEntity(ctx, childID)
	require.NoError(t, err)
	assert.NotNil(t, retrievedChild.ParentID)
	assert.Equal(t, parentID, *retrievedChild.ParentID)
}

// TestDocEntityReferences tests reference fields in entities
func TestDocEntityReferences(t *testing.T) {
	entity := &DocEntity{
		ID:        uuid.New(),
		ProjectID: uuid.New(),
		Type:      DocTypeDocument,
		CodeRefs: []CodeRef{
			{Type: "function", Name: "myFunction"},
			{Type: "file", Name: "main.go"},
		},
		APIRefs: []APIRef{
			{Method: "GET", Path: "/api/users"},
		},
		InternalLinks: []InternalLink{
			{TargetPath: "guide.md", Text: "Guide"},
		},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		IndexedAt: time.Now(),
	}

	assert.Len(t, entity.CodeRefs, 2)
	assert.Len(t, entity.APIRefs, 1)
	assert.Len(t, entity.InternalLinks, 1)

	assert.Equal(t, "function", entity.CodeRefs[0].Type)
	assert.Equal(t, "GET", entity.APIRefs[0].Method)
	assert.Equal(t, "guide.md", entity.InternalLinks[0].TargetPath)
}

// TestDocEntityEmbeddings tests embedding storage in entities
func TestDocEntityEmbeddings(t *testing.T) {
	entity := &DocEntity{
		ID:             uuid.New(),
		ProjectID:      uuid.New(),
		Type:           DocTypeSection,
		Embedding:      make([]float32, 768),
		EmbeddingModel: "OpenAI-3-Small",
		CreatedAt:      time.Now(),
		UpdatedAt:      time.Now(),
		IndexedAt:      time.Now(),
	}

	// Fill embedding with test values
	for i := range entity.Embedding {
		entity.Embedding[i] = 0.5
	}

	assert.Len(t, entity.Embedding, 768)
	assert.Equal(t, "OpenAI-3-Small", entity.EmbeddingModel)
}

// TestDocEntityMetadata tests metadata storage in entities
func TestDocEntityMetadata(t *testing.T) {
	metadata := map[string]any{
		"version":    "1.0",
		"author":     "Test User",
		"tags":       []string{"documentation", "guide"},
		"deprecated": false,
	}

	entity := &DocEntity{
		ID:        uuid.New(),
		ProjectID: uuid.New(),
		Type:      DocTypeDocument,
		Metadata:  metadata,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		IndexedAt: time.Now(),
	}

	assert.Equal(t, "1.0", entity.Metadata["version"])
	assert.Equal(t, "Test User", entity.Metadata["author"])
	deprecated, ok := entity.Metadata["deprecated"].(bool)
	assert.True(t, ok)
	assert.False(t, deprecated)
}

// TestDocEntityTypes tests different entity types
func TestDocEntityTypes(t *testing.T) {
	types := []struct {
		name    string
		typeVal DocEntityType
	}{
		{"document", DocTypeDocument},
		{"section", DocTypeSection},
		{"chunk", DocTypeChunk},
	}

	for _, test := range types {
		entity := &DocEntity{
			ID:        uuid.New(),
			ProjectID: uuid.New(),
			Type:      test.typeVal,
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
			IndexedAt: time.Now(),
		}

		assert.Equal(t, test.typeVal, entity.Type)
	}
}

// TestDocEntityLineNumbers tests line number tracking
func TestDocEntityLineNumbers(t *testing.T) {
	entity := &DocEntity{
		ID:        uuid.New(),
		ProjectID: uuid.New(),
		Type:      DocTypeSection,
		StartLine: 10,
		EndLine:   50,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		IndexedAt: time.Now(),
	}

	assert.Equal(t, 10, entity.StartLine)
	assert.Equal(t, 50, entity.EndLine)
	assert.Equal(t, 40, entity.EndLine-entity.StartLine)
}

// TestDocEntityFilePath tests file path handling
func TestDocEntityFilePath(t *testing.T) {
	paths := []string{
		"docs/guide.md",
		"src/components/Button.tsx",
		"/absolute/path/file.md",
		"relative/path/file.md",
	}

	for _, path := range paths {
		entity := &DocEntity{
			ID:        uuid.New(),
			ProjectID: uuid.New(),
			Type:      DocTypeDocument,
			FilePath:  path,
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
			IndexedAt: time.Now(),
		}

		assert.Equal(t, path, entity.FilePath)
	}
}

// TestDocEntitySectionPath tests section path numbering
func TestDocEntitySectionPath(t *testing.T) {
	paths := []struct {
		path     string
		expected string
	}{
		{"1", "1"},
		{"1.1", "1.1"},
		{"1.2.3", "1.2.3"},
		{"2.1.1.1", "2.1.1.1"},
	}

	for _, test := range paths {
		entity := &DocEntity{
			ID:          uuid.New(),
			ProjectID:   uuid.New(),
			Type:        DocTypeSection,
			SectionPath: test.path,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
			IndexedAt:   time.Now(),
		}

		assert.Equal(t, test.expected, entity.SectionPath)
	}
}

// TestNilDocEntity tests handling of nil entities
func TestNilDocEntity(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	// Saving nil should handle gracefully (based on implementation)
	err := repo.SaveDocEntity(ctx, nil)
	require.NoError(t, err)
}

// TestDocEntityTags tests tag management
func TestDocEntityTags(t *testing.T) {
	entity := &DocEntity{
		ID:        uuid.New(),
		ProjectID: uuid.New(),
		Type:      DocTypeDocument,
		Tags:      []string{"guide", "tutorial", "getting-started"},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		IndexedAt: time.Now(),
	}

	assert.Len(t, entity.Tags, 3)
	assert.Contains(t, entity.Tags, "guide")
	assert.Contains(t, entity.Tags, "tutorial")
	assert.Contains(t, entity.Tags, "getting-started")
}

// TestDocEntityHeadingLevel tests heading level tracking
func TestDocEntityHeadingLevel(t *testing.T) {
	for level := 1; level <= 6; level++ {
		entity := &DocEntity{
			ID:           uuid.New(),
			ProjectID:    uuid.New(),
			Type:         DocTypeSection,
			HeadingLevel: level,
			CreatedAt:    time.Now(),
			UpdatedAt:    time.Now(),
			IndexedAt:    time.Now(),
		}

		assert.Equal(t, level, entity.HeadingLevel)
	}
}
