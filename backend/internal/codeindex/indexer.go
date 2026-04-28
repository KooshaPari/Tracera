package codeindex

import (
	"context"
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/embeddings"
)

const modulePathPartsThreshold = 2

// Indexer indexes code files into structured entities
type Indexer struct {
	repo              Repository
	analyzer          *Analyzer
	canonicalLinker   *CanonicalLinker
	crossLangResolver *CrossLangResolver
	embeddings        embeddings.Provider
}

// NewIndexer creates a new code indexer
func NewIndexer(repo Repository, canonicalRepo CanonicalRepository, embeddingProvider embeddings.Provider) *Indexer {
	analyzer := NewAnalyzer()

	return &Indexer{
		repo:              repo,
		analyzer:          analyzer,
		canonicalLinker:   NewCanonicalLinker(repo, canonicalRepo, nil),
		crossLangResolver: NewCrossLangResolver(repo),
		embeddings:        embeddingProvider,
	}
}

// IndexRequest represents a request to index code
type IndexRequest struct {
	ProjectID          uuid.UUID `json:"project_id"`
	Directory          string    `json:"directory"`
	FilePaths          []string  `json:"file_paths,omitempty"`
	Recursive          bool      `json:"recursive"`
	FilePatterns       []string  `json:"file_patterns,omitempty"`
	ExcludePatterns    []string  `json:"exclude_patterns,omitempty"`
	GenerateEmbeddings bool      `json:"generate_embeddings"`
	LinkCanonical      bool      `json:"link_canonical"`
	ResolveCrossLang   bool      `json:"resolve_cross_lang"`
}

// IndexResult represents the result of an indexing operation
type IndexResult struct {
	ProjectID         uuid.UUID `json:"project_id"`
	FilesIndexed      int       `json:"files_indexed"`
	EntitiesCreated   int       `json:"entities_created"`
	CanonicalLinked   int       `json:"canonical_linked"`
	CrossLangResolved int       `json:"cross_lang_resolved"`
	Errors            []string  `json:"errors,omitempty"`
	Duration          int64     `json:"duration"`
}

// Index indexes code based on the request
func (idx *Indexer) Index(ctx context.Context, req *IndexRequest) (*IndexResult, error) {
	start := time.Now()
	result := idx.newIndexResult(req.ProjectID)

	// Collect files to index
	files, err := idx.collectFiles(req)
	if err != nil {
		return nil, fmt.Errorf("failed to collect files: %w", err)
	}

	entities, err := idx.indexFiles(ctx, req, files, result)
	if err != nil {
		result.Duration = time.Since(start).Milliseconds()
		return result, err
	}

	if req.LinkCanonical {
		idx.linkCanonicalEntities(ctx, entities, result)
	}

	if req.ResolveCrossLang {
		idx.resolveCrossLangReferences(ctx, req.ProjectID, entities, result)
	}

	result.Duration = time.Since(start).Milliseconds()
	return result, nil
}

func (idx *Indexer) newIndexResult(projectID uuid.UUID) *IndexResult {
	return &IndexResult{
		ProjectID: projectID,
		Errors:    make([]string, 0),
	}
}

func (idx *Indexer) indexFiles(
	ctx context.Context,
	req *IndexRequest,
	files []string,
	result *IndexResult,
) ([]*CodeEntity, error) {
	var entities []*CodeEntity
	for _, filePath := range files {
		if err := ctx.Err(); err != nil {
			result.Errors = append(result.Errors, "indexing cancelled")
			return entities, err
		}

		fileEntities, err := idx.indexFile(ctx, req.ProjectID, filePath, req.GenerateEmbeddings)
		if err != nil {
			result.Errors = append(result.Errors, fmt.Sprintf("%s: %v", filePath, err))
			continue
		}

		entities = append(entities, fileEntities...)
		result.FilesIndexed++
		result.EntitiesCreated += len(fileEntities)
	}
	return entities, nil
}

func (idx *Indexer) linkCanonicalEntities(ctx context.Context, entities []*CodeEntity, result *IndexResult) {
	for _, entity := range entities {
		linkResult, err := idx.canonicalLinker.LinkEntityToCanonical(ctx, entity)
		if err != nil || linkResult.CanonicalID == nil {
			continue
		}
		entity.CanonicalID = linkResult.CanonicalID
		if err := idx.repo.UpdateCanonicalLink(ctx, entity.ID, linkResult.CanonicalID); err == nil {
			result.CanonicalLinked++
		}
	}
}

func (idx *Indexer) resolveCrossLangReferences(
	ctx context.Context,
	projectID uuid.UUID,
	entities []*CodeEntity,
	result *IndexResult,
) {
	for _, entity := range entities {
		refs, err := idx.crossLangResolver.ResolveAPIReferences(ctx, projectID, entity)
		if err != nil {
			continue
		}
		for _, ref := range refs {
			if err := idx.repo.SaveCrossLangRef(ctx, &ref); err == nil {
				result.CrossLangResolved++
			}
		}
	}
}

// collectFiles collects all files to be indexed
func (idx *Indexer) collectFiles(req *IndexRequest) ([]string, error) {
	files := append([]string{}, req.FilePaths...)
	if req.Directory == "" {
		return files, nil
	}

	patterns := resolveIndexPatterns(req.FilePatterns)
	walkFn := idx.buildWalkFunc(req, patterns, &files)
	if err := filepath.WalkDir(req.Directory, walkFn); err != nil {
		return nil, err
	}

	return files, nil
}

func resolveIndexPatterns(patterns []string) []string {
	if len(patterns) == 0 {
		return []string{"*.ts", "*.tsx", "*.js", "*.jsx", "*.go", "*.py"}
	}
	return patterns
}

func (idx *Indexer) buildWalkFunc(
	req *IndexRequest,
	patterns []string,
	files *[]string,
) fs.WalkDirFunc {
	return func(path string, entry fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if entry.IsDir() {
			return handleIndexDir(req, path, entry.Name())
		}
		if matchesAnyPattern(req.ExcludePatterns, entry.Name()) {
			return nil
		}
		if matchesAnyPattern(patterns, entry.Name()) {
			*files = append(*files, path)
		}
		return nil
	}
}

func handleIndexDir(req *IndexRequest, path, name string) error {
	if name == "node_modules" || name == ".git" || name == "vendor" || name == "__pycache__" {
		return fs.SkipDir
	}
	if !req.Recursive && path != req.Directory {
		return fs.SkipDir
	}
	return nil
}

func matchesAnyPattern(patterns []string, name string) bool {
	for _, pattern := range patterns {
		matched, err := filepath.Match(pattern, name)
		if err != nil {
			continue
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

// indexFile indexes a single code file
func (idx *Indexer) indexFile(
	ctx context.Context,
	projectID uuid.UUID,
	filePath string,
	generateEmbeddings bool,
) ([]*CodeEntity, error) {
	analysis, err := idx.prepareFileForIndexing(ctx, projectID, filePath)
	if err != nil {
		return nil, err
	}
	return idx.indexSymbols(ctx, projectID, filePath, analysis, generateEmbeddings)
}

func (idx *Indexer) prepareFileForIndexing(
	ctx context.Context,
	projectID uuid.UUID,
	filePath string,
) (*FileAnalysis, error) {
	content, err := readFileSafely(filePath)
	if err != nil {
		return nil, err
	}

	analysis, err := idx.analyzeFile(filePath, content)
	if err != nil {
		return nil, err
	}

	if err := idx.repo.DeleteByFilePath(ctx, projectID, filePath); err != nil {
		return nil, err
	}

	return analysis, nil
}

func readFileSafely(filePath string) ([]byte, error) {
	if err := isSafeFilePath(filePath); err != nil {
		return nil, fmt.Errorf("unsafe file path: %w", err)
	}
	content, err := os.ReadFile(filepath.Clean(filePath))
	if err != nil {
		return nil, fmt.Errorf("failed to read file: %w", err)
	}
	return content, nil
}

func (idx *Indexer) analyzeFile(filePath string, content []byte) (*FileAnalysis, error) {
	analysis, err := idx.analyzer.AnalyzeFile(filePath, string(content))
	if err != nil {
		return nil, err
	}
	if analysis == nil {
		return nil, errors.New("analysis result is empty")
	}
	return analysis, nil
}

func (idx *Indexer) indexSymbols(
	ctx context.Context,
	projectID uuid.UUID,
	filePath string,
	analysis *FileAnalysis,
	generateEmbeddings bool,
) ([]*CodeEntity, error) {
	entities := make([]*CodeEntity, 0, len(analysis.Symbols))
	for _, sym := range analysis.Symbols {
		entity := idx.buildEntity(projectID, filePath, analysis, sym)
		idx.maybeAttachEmbedding(ctx, entity, sym, generateEmbeddings)
		if err := idx.repo.SaveCodeEntity(ctx, entity); err != nil {
			return nil, err
		}
		entities = append(entities, entity)
	}
	return entities, nil
}

func (idx *Indexer) buildEntity(
	projectID uuid.UUID,
	filePath string,
	analysis *FileAnalysis,
	sym SymbolInfo,
) *CodeEntity {
	entity := &CodeEntity{
		ID:          uuid.New(),
		ProjectID:   projectID,
		FilePath:    filePath,
		SymbolName:  sym.Name,
		SymbolType:  sym.Type,
		Language:    analysis.Language,
		Signature:   sym.Signature,
		DocComment:  sym.DocComment,
		StartLine:   sym.StartLine,
		EndLine:     sym.EndLine,
		IsExported:  sym.IsExported,
		IsAsync:     sym.IsAsync,
		ContentHash: analysis.ContentHash,
		Imports:     analysis.Imports,
		Calls:       analysis.Calls,
		Annotations: analysis.Annotations,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
		IndexedAt:   time.Now(),
	}
	entity.ModulePath = extractModulePath(filePath)
	return entity
}

func (idx *Indexer) maybeAttachEmbedding(
	ctx context.Context,
	entity *CodeEntity,
	sym SymbolInfo,
	generateEmbeddings bool,
) {
	if !generateEmbeddings || idx.embeddings == nil {
		return
	}
	embeddingText := sym.Name + " " + sym.DocComment
	embedding, err := idx.generateEmbedding(ctx, embeddingText)
	if err != nil {
		return
	}
	entity.Embedding = embedding
	entity.EmbeddingModel = idx.embeddings.GetDefaultModel()
}

func extractModulePath(filePath string) string {
	// Extract relative module path
	parts := strings.Split(filePath, string(filepath.Separator))
	if len(parts) > modulePathPartsThreshold {
		return strings.Join(parts[len(parts)-3:len(parts)-1], "/")
	}
	return ""
}

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
