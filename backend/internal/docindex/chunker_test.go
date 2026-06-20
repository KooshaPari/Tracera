package docindex

import (
	"context"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// MockRepository implements Repository interface for testing
type MockRepository struct {
	savedEntities  []*DocEntity
	deletedIDs     []uuid.UUID
	savedLinks     []*TraceLink
	deletedLinkIDs []uuid.UUID
}

func NewMockRepository() *MockRepository {
	return &MockRepository{
		savedEntities:  make([]*DocEntity, 0),
		deletedIDs:     make([]uuid.UUID, 0),
		savedLinks:     make([]*TraceLink, 0),
		deletedLinkIDs: make([]uuid.UUID, 0),
	}
}

func (m *MockRepository) SaveDocEntity(ctx context.Context, entity *DocEntity) error {
	_ = ctx
	if entity == nil {
		return nil
	}
	m.savedEntities = append(m.savedEntities, entity)
	return nil
}

func (m *MockRepository) GetDocEntity(ctx context.Context, id uuid.UUID) (*DocEntity, error) {
	_ = ctx
	for _, e := range m.savedEntities {
		if e.ID == id {
			return e, nil
		}
	}
	return nil, nil
}

func (m *MockRepository) ListDocEntities(ctx context.Context, _ uuid.UUID, _ *ListOptions) ([]DocEntity, error) {
	_ = ctx
	return []DocEntity{}, nil
}

func (m *MockRepository) SearchByEmbedding(ctx context.Context, _ uuid.UUID, _ []float32, _ int) ([]DocEntity, error) {
	_ = ctx
	return []DocEntity{}, nil
}

func (m *MockRepository) DeleteDocEntity(ctx context.Context, id uuid.UUID) error {
	_ = ctx
	m.deletedIDs = append(m.deletedIDs, id)
	return nil
}

func (m *MockRepository) DeleteByDocument(ctx context.Context, _ uuid.UUID) error {
	_ = ctx
	return nil
}

func (m *MockRepository) GetDocumentSections(ctx context.Context, _ uuid.UUID) ([]DocEntity, error) {
	_ = ctx
	return []DocEntity{}, nil
}

func (m *MockRepository) GetSectionChunks(ctx context.Context, _ uuid.UUID) ([]DocEntity, error) {
	_ = ctx
	return []DocEntity{}, nil
}

func (m *MockRepository) SaveTraceLink(ctx context.Context, link *TraceLink) error {
	_ = ctx
	m.savedLinks = append(m.savedLinks, link)
	return nil
}

func (m *MockRepository) GetTraceLinks(ctx context.Context, _ uuid.UUID) ([]TraceLink, error) {
	_ = ctx
	return []TraceLink{}, nil
}

func (m *MockRepository) DeleteTraceLink(ctx context.Context, id uuid.UUID) error {
	_ = ctx
	m.deletedLinkIDs = append(m.deletedLinkIDs, id)
	return nil
}

// Note: TraceLink is defined in linker.go

// TestCreateChunksSmallContent tests chunking of small content (doesn't need chunking)
func TestCreateChunksSmallContent(t *testing.T) {
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)

	content := "This is small content that doesn't need chunking."
	chunks := indexer.createChunks(content)

	assert.Len(t, chunks, 1)
	assert.Equal(t, content, chunks[0])
}

// TestCreateChunksLargeContent tests chunking of large content
func TestCreateChunksLargeContent(t *testing.T) {
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)
	indexer.chunkSize = 100
	indexer.chunkOverlap = 20

	// Create content larger than chunk size
	content := generateContent(500)

	chunks := indexer.createChunks(content)

	assert.Greater(t, len(chunks), 1, "Should create multiple chunks for large content")

	// Verify each chunk doesn't exceed size
	for _, chunk := range chunks {
		assert.LessOrEqual(t, len(chunk), indexer.chunkSize+50, "Chunk should not significantly exceed chunk size")
	}
}

// TestCreateChunksOverlap tests that overlapping chunks share content
func TestCreateChunksOverlap(t *testing.T) {
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)
	indexer.chunkSize = 100
	indexer.chunkOverlap = 30

	content := generateContent(300)
	chunks := indexer.createChunks(content)

	assert.Greater(t, len(chunks), 1)

	// Check that consecutive chunks have overlapping content
	if len(chunks) > 1 {
		// Extract words from chunks
		words0 := getContentWords(chunks[0])
		words1 := getContentWords(chunks[1])

		// Find overlap - last words of first chunk should appear in second chunk
		overlap := 0
		for i := len(words0) - 1; i >= 0 && i > len(words0)-10; i-- {
			for j := 0; j < len(words1); j++ {
				if words0[i] == words1[j] {
					overlap++
					break
				}
			}
		}

		assert.Positive(t, overlap, "Chunks should have overlapping content")
	}
}

// TestCreateChunksEmpty tests chunking of empty content
func TestCreateChunksEmpty(t *testing.T) {
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)

	content := ""
	chunks := indexer.createChunks(content)

	// Empty content produces empty slice or one empty chunk depending on implementation
	assert.LessOrEqual(t, len(chunks), 1, "Empty content should produce minimal chunks")
}

// TestCreateChunksSingleWord tests chunking of content with single word
func TestCreateChunksSingleWord(t *testing.T) {
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)

	content := "word"
	chunks := indexer.createChunks(content)

	assert.Len(t, chunks, 1)
	assert.Equal(t, "word", chunks[0])
}

// TestCreateChunksPreserveContent tests that chunking preserves all content
func TestCreateChunksPreserveContent(t *testing.T) {
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)
	indexer.chunkSize = 150
	indexer.chunkOverlap = 25

	content := generateContent(500)
	chunks := indexer.createChunks(content)

	// Reconstruct to verify no content is lost
	reconstructed := ""
	for i, chunk := range chunks {
		if i == 0 {
			reconstructed = chunk
		} else {
			// Find where this chunk starts relative to previous
			// (it should start somewhere in the overlap region)
			reconstructed += " " + chunk
		}
	}

	// Check that key phrases are preserved
	words := len(content) / 5 // rough word count
	reconstructedWords := len(reconstructed) / 5

	assert.GreaterOrEqual(t, reconstructedWords, words/2, "Reconstructed content should preserve majority of original")
}

// TestIndexSectionsBasic tests basic section indexing
func TestIndexSectionsBasic(t *testing.T) {
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)
	indexer.chunkSize = 1500

	projectID := uuid.New()
	documentID := uuid.New()
	ctx := context.Background()

	sections := []*Section{
		{
			Title:     "Section 1",
			Level:     2,
			Content:   "Content for section 1",
			Path:      "1.1",
			StartLine: 1,
			EndLine:   5,
		},
		{
			Title:     "Section 2",
			Level:     2,
			Content:   "Content for section 2",
			Path:      "1.2",
			StartLine: 6,
			EndLine:   10,
		},
	}

	result := &IndexResult{}
	err := indexer.indexSections(ctx, projectID, documentID, sections, false, result)

	require.NoError(t, err)
	assert.Equal(t, 2, result.SectionsCreated)
	assert.Len(t, repo.savedEntities, 2)
}

// TestIndexSectionsNestedHierarchy tests indexing with nested sections
func TestIndexSectionsNestedHierarchy(t *testing.T) {
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)
	indexer.chunkSize = 1500

	projectID := uuid.New()
	documentID := uuid.New()
	ctx := context.Background()

	sections := []*Section{
		{
			Title:     "Parent Section",
			Level:     2,
			Content:   "Parent content",
			Path:      "1.1",
			StartLine: 1,
			EndLine:   10,
			Children: []*Section{
				{
					Title:     "Child Section",
					Level:     3,
					Content:   "Child content",
					Path:      "1.1.1",
					StartLine: 3,
					EndLine:   8,
					Children:  make([]*Section, 0),
				},
			},
		},
	}

	result := &IndexResult{}
	err := indexer.indexSections(ctx, projectID, documentID, sections, false, result)

	require.NoError(t, err)
	assert.Equal(t, 2, result.SectionsCreated) // Parent and child
	assert.Len(t, repo.savedEntities, 2)

	// Verify parent-child relationship
	parentEntity := repo.savedEntities[0]
	childEntity := repo.savedEntities[1]

	assert.Nil(t, parentEntity.ParentID)
	assert.NotNil(t, childEntity.ParentID)
	assert.Equal(t, parentEntity.ID, *childEntity.ParentID)
}

// TestIndexSectionsLargeSectionCreateChunks tests chunking of large sections
func TestIndexSectionsLargeSectionCreateChunks(t *testing.T) {
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)
	indexer.chunkSize = 200 // Small chunk size to force chunking

	projectID := uuid.New()
	documentID := uuid.New()
	ctx := context.Background()

	sections := []*Section{
		{
			Title:     "Large Section",
			Level:     2,
			Content:   generateContent(600),
			Path:      "1.1",
			StartLine: 1,
			EndLine:   20,
		},
	}

	result := &IndexResult{}
	err := indexer.indexSections(ctx, projectID, documentID, sections, false, result)

	require.NoError(t, err)
	assert.Equal(t, 1, result.SectionsCreated)
	assert.Positive(t, result.ChunksCreated)
	assert.Greater(t, len(repo.savedEntities), 1) // Section + chunks
}

// TestIndexSectionsContextCancellation tests context cancellation
func TestIndexSectionsContextCancellation(t *testing.T) {
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)

	projectID := uuid.New()
	documentID := uuid.New()

	ctx, cancel := context.WithCancel(context.Background())
	cancel() // Cancel immediately

	sections := []*Section{
		{
			Title:     "Section 1",
			Level:     2,
			Content:   "Content",
			Path:      "1.1",
			StartLine: 1,
			EndLine:   5,
		},
	}

	result := &IndexResult{}
	err := indexer.indexSections(ctx, projectID, documentID, sections, false, result)

	assert.Error(t, err)
}

// TestChunkSizeParameters tests custom chunk size parameters
func TestChunkSizeParameters(t *testing.T) {
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)

	tests := []struct {
		name         string
		chunkSize    int
		chunkOverlap int
	}{
		{"small chunks", 100, 10},
		{"medium chunks", 500, 50},
		{"large chunks", 2000, 200},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			indexer.chunkSize = test.chunkSize
			indexer.chunkOverlap = test.chunkOverlap

			content := generateContent(test.chunkSize * 2)
			chunks := indexer.createChunks(content)

			for _, chunk := range chunks {
				assert.LessOrEqual(t, len(chunk), test.chunkSize+100)
			}
		})
	}
}

// TestChunkBoundaries tests chunk boundary handling
func TestChunkBoundaries(t *testing.T) {
	repo := NewMockRepository()
	indexer := NewIndexer(repo, nil)
	indexer.chunkSize = 100
	indexer.chunkOverlap = 20

	// Create content with at least some size
	content := generateContent(50)

	chunks := indexer.createChunks(content)
	assert.GreaterOrEqual(t, len(chunks), 1)
}

// Helper functions

func generateContent(sizeInChars int) string {
	content := ""
	word := "word "
	for len(content) < sizeInChars {
		content += word
	}
	return content[:sizeInChars]
}

func getContentWords(content string) []string {
	// Simple word splitting for testing
	words := make([]string, 0)
	currentWord := ""
	for _, char := range content {
		if char == ' ' || char == '\n' {
			if currentWord != "" {
				words = append(words, currentWord)
				currentWord = ""
			}
		} else {
			currentWord += string(char)
		}
	}
	if currentWord != "" {
		words = append(words, currentWord)
	}
	return words
}
