package docindex

import (
	"context"
	"strings"
	"time"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/embeddings"
)

// indexSections recursively indexes sections and creates chunks
func (idx *Indexer) indexSections(
	ctx context.Context,
	projectID uuid.UUID,
	documentID uuid.UUID,
	sections []*Section,
	generateEmbeddings bool,
	result *IndexResult,
) error {
	return idx.indexSectionsRecursive(ctx, projectID, documentID, nil, sections, "", generateEmbeddings, result)
}

func (idx *Indexer) indexSectionsRecursive(
	ctx context.Context,
	projectID uuid.UUID,
	documentID uuid.UUID,
	parentID *uuid.UUID,
	sections []*Section,
	filePath string,
	generateEmbeddings bool,
	result *IndexResult,
) error {
	for _, section := range sections {
		if err := idx.checkContext(ctx); err != nil {
			return err
		}
		if err := idx.indexSection(ctx, projectID, documentID, parentID, section, filePath, generateEmbeddings, result); err != nil {
			return err
		}
	}

	return nil
}

func (idx *Indexer) indexSection(
	ctx context.Context,
	projectID uuid.UUID,
	documentID uuid.UUID,
	parentID *uuid.UUID,
	section *Section,
	filePath string,
	generateEmbeddings bool,
	result *IndexResult,
) error {
	sectionID := uuid.New()
	sectionEntity := idx.buildSectionEntity(sectionID, projectID, documentID, parentID, section, filePath)
	idx.embedSectionIfNeeded(ctx, sectionEntity, section, generateEmbeddings)

	if err := idx.repo.SaveDocEntity(ctx, sectionEntity); err != nil {
		return err
	}
	result.SectionsCreated++

	if err := idx.indexSectionChunks(ctx, projectID, documentID, sectionID, section, filePath, generateEmbeddings, result); err != nil {
		return err
	}

	if len(section.Children) == 0 {
		return nil
	}
	return idx.indexSectionsRecursive(ctx, projectID, documentID, &sectionID, section.Children, filePath, generateEmbeddings, result)
}

func (idx *Indexer) buildSectionEntity(
	sectionID uuid.UUID,
	projectID uuid.UUID,
	documentID uuid.UUID,
	parentID *uuid.UUID,
	section *Section,
	filePath string,
) *DocEntity {
	now := time.Now()
	return &DocEntity{
		ID:            sectionID,
		ProjectID:     projectID,
		Type:          DocTypeSection,
		ParentID:      parentID,
		DocumentID:    documentID,
		FilePath:      filePath,
		SectionPath:   section.Path,
		Title:         section.Title,
		Content:       section.Content,
		RawMarkdown:   section.RawMarkdown,
		HeadingLevel:  section.Level,
		StartLine:     section.StartLine,
		EndLine:       section.EndLine,
		CodeRefs:      idx.parser.ExtractCodeRefs(section.Content),
		APIRefs:       ExtractAPIRefs(section.Content),
		InternalLinks: ExtractInternalLinks(section.Content),
		CreatedAt:     now,
		UpdatedAt:     now,
		IndexedAt:     now,
	}
}

func (idx *Indexer) embedSectionIfNeeded(
	ctx context.Context,
	sectionEntity *DocEntity,
	section *Section,
	generateEmbeddings bool,
) {
	if !generateEmbeddings || idx.embeddings == nil || len(section.Content) <= 50 {
		return
	}
	embedding, err := idx.generateEmbedding(ctx, section.Title+" "+section.Content)
	if err != nil {
		return
	}
	sectionEntity.Embedding = embedding
	sectionEntity.EmbeddingModel = idx.embeddings.GetDefaultModel()
}

func (idx *Indexer) indexSectionChunks(
	ctx context.Context,
	projectID uuid.UUID,
	documentID uuid.UUID,
	sectionID uuid.UUID,
	section *Section,
	filePath string,
	generateEmbeddings bool,
	result *IndexResult,
) error {
	if len(section.Content) <= idx.chunkSize {
		return nil
	}
	chunks := idx.createChunks(section.Content)
	for i, chunk := range chunks {
		chunkEntity := idx.buildChunkEntity(projectID, documentID, sectionID, section, filePath, chunk, i)
		idx.embedChunkIfNeeded(ctx, chunkEntity, chunk, generateEmbeddings)
		if err := idx.repo.SaveDocEntity(ctx, chunkEntity); err != nil {
			return err
		}
		result.ChunksCreated++
	}
	return nil
}

func (idx *Indexer) buildChunkEntity(
	projectID uuid.UUID,
	documentID uuid.UUID,
	sectionID uuid.UUID,
	section *Section,
	filePath string,
	chunk string,
	index int,
) *DocEntity {
	now := time.Now()
	return &DocEntity{
		ID:          uuid.New(),
		ProjectID:   projectID,
		Type:        DocTypeChunk,
		ParentID:    &sectionID,
		DocumentID:  documentID,
		FilePath:    filePath,
		SectionPath: section.Path,
		Title:       section.Title,
		Content:     chunk,
		ChunkIndex:  index,
		CodeRefs:    idx.parser.ExtractCodeRefs(chunk),
		CreatedAt:   now,
		UpdatedAt:   now,
		IndexedAt:   now,
	}
}

func (idx *Indexer) embedChunkIfNeeded(
	ctx context.Context,
	chunkEntity *DocEntity,
	chunk string,
	generateEmbeddings bool,
) {
	if !generateEmbeddings || idx.embeddings == nil {
		return
	}
	embedding, err := idx.generateEmbedding(ctx, chunk)
	if err != nil {
		return
	}
	chunkEntity.Embedding = embedding
	chunkEntity.EmbeddingModel = idx.embeddings.GetDefaultModel()
}

func (idx *Indexer) checkContext(ctx context.Context) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	default:
		return nil
	}
}

// createChunks splits content into overlapping chunks
func (idx *Indexer) createChunks(content string) []string {
	if len(content) <= idx.chunkSize {
		return []string{content}
	}

	var chunks []string
	words := strings.Fields(content)

	var currentChunk strings.Builder
	var overlapBuffer []string

	for _, word := range words {
		// Check if adding this word exceeds chunk size
		if currentChunk.Len()+len(word)+1 > idx.chunkSize && currentChunk.Len() > 0 {
			chunks = append(chunks, strings.TrimSpace(currentChunk.String()))

			// Start new chunk with overlap
			currentChunk.Reset()
			for _, w := range overlapBuffer {
				currentChunk.WriteString(w)
				currentChunk.WriteString(" ")
			}
		}

		currentChunk.WriteString(word)
		currentChunk.WriteString(" ")

		// Maintain overlap buffer
		overlapBuffer = append(overlapBuffer, word)
		overlapLen := 0
		for _, w := range overlapBuffer {
			overlapLen += len(w) + 1
		}
		for overlapLen > idx.chunkOverlap && len(overlapBuffer) > 0 {
			overlapLen -= len(overlapBuffer[0]) + 1
			overlapBuffer = overlapBuffer[1:]
		}
	}

	// Add final chunk
	if currentChunk.Len() > 0 {
		chunks = append(chunks, strings.TrimSpace(currentChunk.String()))
	}

	return chunks
}

// generateEmbedding generates an embedding for text
func (idx *Indexer) generateEmbedding(ctx context.Context, text string) ([]float32, error) {
	if idx.embeddings == nil {
		return nil, nil
	}

	resp, err := idx.embeddings.Embed(ctx, &embeddings.EmbeddingRequest{
		Texts:     []string{text},
		Model:     "",
		InputType: "document",
	})
	if err != nil {
		return nil, err
	}

	if len(resp.Embeddings) > 0 {
		return resp.Embeddings[0], nil
	}

	return nil, nil
}
