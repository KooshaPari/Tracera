package docindex

import (
	"context"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/embeddings"
)

const (
	defaultDocChunkSize    = 1500
	defaultDocChunkOverlap = 200
)

// Indexer indexes documentation files into structured entities
type Indexer struct {
	parser       *Parser
	embeddings   embeddings.Provider
	repo         Repository
	chunkSize    int
	chunkOverlap int
}

// NewIndexer creates a new documentation indexer
func NewIndexer(repo Repository, embeddingProvider embeddings.Provider) *Indexer {
	return &Indexer{
		parser:       NewParser(),
		embeddings:   embeddingProvider,
		repo:         repo,
		chunkSize:    defaultDocChunkSize,    // Characters per chunk
		chunkOverlap: defaultDocChunkOverlap, // Overlap between chunks
	}
}

// Index indexes documentation based on the request
func (idx *Indexer) Index(ctx context.Context, req *IndexRequest) (*IndexResult, error) {
	start := time.Now()
	result := &IndexResult{
		ProjectID: req.ProjectID,
		Errors:    make([]string, 0),
	}

	// Set chunk parameters from request
	if req.ChunkSize > 0 {
		idx.chunkSize = req.ChunkSize
	}
	if req.ChunkOverlap > 0 {
		idx.chunkOverlap = req.ChunkOverlap
	}

	// Collect files to index
	files, err := idx.collectFiles(req)
	if err != nil {
		return nil, fmt.Errorf("failed to collect files: %w", err)
	}

	// Process each file
	for _, filePath := range files {
		select {
		case <-ctx.Done():
			result.Errors = append(result.Errors, "indexing cancelled")
			result.DurationMs = time.Since(start).Milliseconds()
			return result, ctx.Err()
		default:
		}

		if err := idx.indexFile(ctx, req.ProjectID, filePath, req.GenerateEmbeddings, result); err != nil {
			result.Errors = append(result.Errors, fmt.Sprintf("%s: %v", filePath, err))
		}
	}

	result.DurationMs = time.Since(start).Milliseconds()
	return result, nil
}

// collectFiles collects all files to be indexed
func (idx *Indexer) collectFiles(req *IndexRequest) ([]string, error) {
	files := append([]string{}, req.FilePaths...)
	if req.Directory == "" {
		return files, nil
	}

	patterns := normalizeFilePatterns(req.FilePatterns)
	walkFn := buildFileWalkFn(req, patterns, &files)
	if err := filepath.WalkDir(req.Directory, walkFn); err != nil {
		return nil, err
	}

	return files, nil
}

func normalizeFilePatterns(patterns []string) []string {
	if len(patterns) == 0 {
		return []string{"*.md", "*.mdx"}
	}
	return patterns
}

func buildFileWalkFn(req *IndexRequest, patterns []string, files *[]string) fs.WalkDirFunc {
	return func(path string, doc fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if doc.IsDir() {
			return handleWalkDir(req, path)
		}
		if isExcludedPath(path, doc.Name(), req.ExcludePatterns) {
			return nil
		}
		if matchesIncludePattern(doc.Name(), patterns) {
			*files = append(*files, path)
		}
		return nil
	}
}

func handleWalkDir(req *IndexRequest, path string) error {
	if !req.Recursive && path != req.Directory {
		return fs.SkipDir
	}
	return nil
}

func isExcludedPath(path string, name string, patterns []string) bool {
	for _, pattern := range patterns {
		matched, err := filepath.Match(pattern, name)
		if err != nil {
			continue // skip invalid patterns
		}
		if matched {
			return true
		}
		if strings.Contains(path, pattern) {
			return true
		}
	}
	return false
}

func matchesIncludePattern(name string, patterns []string) bool {
	for _, pattern := range patterns {
		matched, err := filepath.Match(pattern, name)
		if err != nil {
			continue // skip invalid patterns
		}
		if matched {
			return true
		}
	}
	return false
}

// isSafeFilePath validates that a file path is safe to read
func isSafeFilePath(filePath string) error {
	// Path must be absolute
	if !filepath.IsAbs(filePath) {
		return fmt.Errorf("file path must be absolute: %s", filePath)
	}
	// Clean the path to resolve any .. or symlinks
	cleanedPath := filepath.Clean(filePath)
	// Ensure the path doesn't escape to parent directories
	if strings.Contains(cleanedPath, ".."+string(filepath.Separator)) || strings.HasSuffix(cleanedPath, "..") {
		return fmt.Errorf("file path contains unsafe sequence: %s", filePath)
	}
	return nil
}

// indexFile indexes a single documentation file
func (idx *Indexer) indexFile(
	ctx context.Context, projectID uuid.UUID, filePath string, generateEmbeddings bool, result *IndexResult,
) error {
	// Validate file path is safe
	if err := isSafeFilePath(filePath); err != nil {
		return fmt.Errorf("unsafe file path: %w", err)
	}
	// Read file content
	content, err := os.ReadFile(filepath.Clean(filePath))
	if err != nil {
		return fmt.Errorf("failed to read file: %w", err)
	}

	// Parse the document
	doc, err := idx.parser.Parse(filePath, content)
	if err != nil {
		return fmt.Errorf("failed to parse: %w", err)
	}

	// Extract references
	doc.CodeRefs = idx.parser.ExtractCodeRefs(doc.RawContent)
	doc.APIRefs = ExtractAPIRefs(doc.RawContent)
	doc.InternalLinks = ExtractInternalLinks(doc.RawContent)

	result.CodeRefsFound += len(doc.CodeRefs)
	result.APIRefsFound += len(doc.APIRefs)

	// Create document entity
	docEntity := &DocEntity{
		ID:            uuid.New(),
		ProjectID:     projectID,
		Type:          DocTypeDocument,
		DocumentID:    uuid.Nil, // Will be set to self
		FilePath:      filePath,
		Title:         doc.Title,
		Content:       doc.RawContent,
		RawMarkdown:   doc.RawContent,
		CodeRefs:      doc.CodeRefs,
		APIRefs:       doc.APIRefs,
		InternalLinks: doc.InternalLinks,
		Metadata:      doc.Frontmatter,
		CreatedAt:     time.Now(),
		UpdatedAt:     time.Now(),
		IndexedAt:     time.Now(),
	}
	docEntity.DocumentID = docEntity.ID

	if err := idx.repo.SaveDocEntity(ctx, docEntity); err != nil {
		return fmt.Errorf("failed to save document: %w", err)
	}
	result.DocumentsIndexed++

	// Create section entities
	if err := idx.indexSections(ctx, projectID, docEntity.ID, doc.Sections, generateEmbeddings, result); err != nil {
		return err
	}

	return nil
}
