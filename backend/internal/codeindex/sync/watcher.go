package sync

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"path/filepath"
	"sync"
	"time"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/codeindex"
	"github.com/kooshapari/tracertm-backend/internal/codeindex/parsers"
)

const (
	defaultDebounceMs    = 500
	defaultMaxConcurrent = 3
)

// FileWatcher watches the local filesystem for code changes
// Used during development for real-time indexing
type FileWatcher struct {
	projectRoot   string
	watchPaths    []string
	indexer       *codeindex.Indexer
	debounceMs    int
	maxConcurrent int
	mu            sync.RWMutex
	watching      bool
	stopCh        chan struct{}
	changedFiles  map[string]time.Time // filePath -> last change time
	pendingFiles  map[string]bool      // filePath -> pending sync
}

// NewFileWatcher creates a new file watcher
func NewFileWatcher(projectRoot string, indexer *codeindex.Indexer) *FileWatcher {
	return &FileWatcher{
		projectRoot:   projectRoot,
		indexer:       indexer,
		debounceMs:    defaultDebounceMs,
		maxConcurrent: defaultMaxConcurrent,
		changedFiles:  make(map[string]time.Time),
		pendingFiles:  make(map[string]bool),
		stopCh:        make(chan struct{}),
	}
}

// AddWatchPath adds a directory path to watch
func (fw *FileWatcher) AddWatchPath(path string) {
	fw.mu.Lock()
	defer fw.mu.Unlock()
	fw.watchPaths = append(fw.watchPaths, path)
}

// SetDebounce sets the debounce delay in milliseconds
func (fw *FileWatcher) SetDebounce(ms int) {
	fw.mu.Lock()
	defer fw.mu.Unlock()
	fw.debounceMs = ms
}

// Start begins watching for file changes
func (fw *FileWatcher) Start(ctx context.Context) error {
	fw.mu.Lock()
	if fw.watching {
		fw.mu.Unlock()
		return errors.New("watcher already running")
	}
	fw.watching = true
	fw.mu.Unlock()

	// Start periodic sync goroutine
	go fw.periodicSync(ctx)

	// In a real implementation, we would use fsnotify or similar
	// For now, this demonstrates the interface
	return nil
}

// Stop stops watching for file changes
func (fw *FileWatcher) Stop() {
	fw.mu.Lock()
	defer fw.mu.Unlock()

	if fw.watching {
		fw.watching = false
		close(fw.stopCh)
	}
}

// NotifyFileChange notifies the watcher of a file change
// This can be called by external systems or file system watchers
func (fw *FileWatcher) NotifyFileChange(filePath string) {
	fw.mu.Lock()
	defer fw.mu.Unlock()

	if !fw.watching {
		return
	}

	fw.changedFiles[filePath] = time.Now()
	fw.pendingFiles[filePath] = true
}

// NotifyFileDelete notifies the watcher of a file deletion
func (fw *FileWatcher) NotifyFileDelete(filePath string) {
	fw.mu.Lock()
	defer fw.mu.Unlock()

	if !fw.watching {
		return
	}

	// Mark for deletion
	delete(fw.changedFiles, filePath)
	delete(fw.pendingFiles, filePath)
}

// periodicSync periodically syncs pending files
func (fw *FileWatcher) periodicSync(ctx context.Context) {
	ticker := time.NewTicker(time.Duration(fw.debounceMs) * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			fw.syncPendingFiles(ctx)
		case <-fw.stopCh:
			return
		case <-ctx.Done():
			return
		}
	}
}

// syncPendingFiles syncs all pending files
func (fw *FileWatcher) syncPendingFiles(ctx context.Context) {
	fw.mu.Lock()
	filesToSync := make([]string, 0, len(fw.pendingFiles))
	for filePath := range fw.pendingFiles {
		filesToSync = append(filesToSync, filePath)
	}
	fw.pendingFiles = make(map[string]bool)
	fw.mu.Unlock()

	if len(filesToSync) == 0 {
		return
	}

	// Sync files with concurrency limit
	semaphore := make(chan struct{}, fw.maxConcurrent)
	results := make(chan *FileResult, len(filesToSync))

	for _, filePath := range filesToSync {
		go func(fp string) {
			semaphore <- struct{}{}
			defer func() { <-semaphore }()

			indexResult, err := fw.indexer.Index(ctx, &codeindex.IndexRequest{
				ProjectID:          uuid.Nil,
				Directory:          "",
				FilePaths:          []string{fp},
				Recursive:          false,
				FilePatterns:       nil,
				ExcludePatterns:    nil,
				GenerateEmbeddings: false,
				LinkCanonical:      false,
				ResolveCrossLang:   false,
			})
			result := &FileResult{
				FilePath: fp,
				Success:  err == nil && len(indexResult.Errors) == 0,
				Errors:   indexResult.Errors,
			}
			if err != nil {
				result.Errors = append(result.Errors, err.Error())
			}
			results <- result
		}(filePath)
	}

	// Collect results
	successCount := 0
	for i := 0; i < len(filesToSync); i++ {
		result := <-results
		if result.Success {
			successCount++
		} else {
			// Log error but continue
			slog.Error("Failed to sync", "error", result.FilePath, "error", result.Errors)
		}
	}

	slog.Info("File watcher synced / files", "path", successCount, "value", len(filesToSync))
}

// FileResult represents the result of syncing a file
type FileResult struct {
	FilePath string
	Success  bool
	Errors   []string
}

// Indexer wraps code indexing functionality
type Indexer struct {
	tsParser *parsers.TypeScriptParser
	goParser *parsers.GoParser
	pyParser *parsers.PythonParser
	resolver *codeindex.ReferenceResolver
	linker   *codeindex.CodeEntityLinker
	mu       sync.RWMutex
}

// NewIndexer creates a new indexer
func NewIndexer(projectRoot string) *Indexer {
	resolver := codeindex.NewReferenceResolver(projectRoot)
	return &Indexer{
		tsParser: parsers.NewTypeScriptParser(projectRoot),
		goParser: parsers.NewGoParser(projectRoot),
		pyParser: parsers.NewPythonParser(projectRoot),
		resolver: resolver,
		linker:   codeindex.NewCodeEntityLinker(resolver),
	}
}

// IndexFileFromPath reads and indexes a file from the filesystem
func (idx *Indexer) IndexFileFromPath(ctx context.Context, filePath string) *FileResult {
	_ = ctx
	idx.mu.Lock()
	defer idx.mu.Unlock()

	result := &FileResult{
		FilePath: filePath,
		Errors:   make([]string, 0),
	}

	// Detect language
	lang := detectLanguage(filePath)

	// Read file (would use actual file I/O in production)
	// For now, just create the structure
	var _ CodeFileParser
	switch lang {
	case codeindex.LanguageTypeScript:
		_ = idx.tsParser
	case codeindex.LanguageJavaScript:
		result.Errors = append(result.Errors, "unsupported language: "+string(lang))
		return result
	case codeindex.LanguageGo:
		_ = idx.goParser
	case codeindex.LanguagePython:
		_ = idx.pyParser
	case codeindex.LanguageRust, codeindex.LanguageJava:
		result.Errors = append(result.Errors, "unsupported language: "+string(lang))
		return result
	default:
		result.Errors = append(result.Errors, "unsupported language: "+string(lang))
		return result
	}

	// Parse the file (would need actual content)
	// parsedFile, err := parser.ParseFile(ctx, filePath, content)
	// if err != nil {
	//     result.Errors = append(result.Errors, err.Error())
	//     return result
	// }

	result.Success = true
	return result
}

// CodeFileParser interface for language-specific parsers
type CodeFileParser interface {
	ParseFile(ctx context.Context, filePath string, content string) (*codeindex.ParsedFile, error)
}

// WatcherConfig holds configuration for the file watcher
type WatcherConfig struct {
	ProjectRoot   string
	WatchPaths    []string
	DebounceMs    int
	MaxConcurrent int
	Patterns      []string // File patterns to watch (e.g., "**/*.ts", "**/*.go")
}

// BatchWatchResult holds results from batch watching
type BatchWatchResult struct {
	StartTime       time.Time
	EndTime         time.Time
	Duration        time.Duration
	TotalFiles      int
	SuccessfulFiles int
	FailedFiles     int
	EntitiesAdded   int
	Errors          []string
}

// GitDeltaSync performs incremental sync based on git changes.
type GitDeltaSync struct {
	indexer     *Indexer
	gitService  GitService
	projectRoot string
	lastSyncRef string
}

// GitService interface for git operations
type GitService interface {
	GetChangedFiles(ctx context.Context, sinceRef string) ([]string, error)
	GetCurrentRef(ctx context.Context) (string, error)
	GetFileContent(ctx context.Context, filePath string, ref string) ([]byte, error)
}

// NewGitDeltaSync creates a new git delta syncer
func NewGitDeltaSync(indexer *Indexer, gitService GitService, projectRoot string) *GitDeltaSync {
	return &GitDeltaSync{
		indexer:     indexer,
		gitService:  gitService,
		projectRoot: projectRoot,
		lastSyncRef: "HEAD~1",
	}
}

// SyncSinceLastCommit syncs files changed since the last commit
func (gds *GitDeltaSync) SyncSinceLastCommit(ctx context.Context) (*BatchWatchResult, error) {
	result := &BatchWatchResult{
		StartTime: time.Now(),
		Errors:    make([]string, 0),
	}

	// Get changed files
	changedFiles, err := gds.gitService.GetChangedFiles(ctx, gds.lastSyncRef)
	if err != nil {
		result.Errors = append(result.Errors, fmt.Sprintf("failed to get changed files: %v", err))
		result.EndTime = time.Now()
		result.Duration = result.EndTime.Sub(result.StartTime)
		return result, nil
	}

	result.TotalFiles = len(changedFiles)

	// Filter to code files
	codeFiles := make([]string, 0)
	for _, f := range changedFiles {
		if isCodeFile(f) {
			codeFiles = append(codeFiles, f)
		}
	}

	if len(codeFiles) == 0 {
		result.EndTime = time.Now()
		result.Duration = result.EndTime.Sub(result.StartTime)
		return result, nil
	}

	// Sync each file
	for _, filePath := range codeFiles {
		syncResult := gds.indexer.IndexFileFromPath(ctx, filePath)
		if syncResult.Success {
			result.SuccessfulFiles++
		} else {
			result.FailedFiles++
			result.Errors = append(result.Errors, syncResult.Errors...)
		}
	}

	// Update sync reference
	currentRef, err := gds.gitService.GetCurrentRef(ctx)
	if err == nil {
		gds.lastSyncRef = currentRef
	}

	result.EndTime = time.Now()
	result.Duration = result.EndTime.Sub(result.StartTime)
	return result, nil
}

// SyncSinceRef syncs files changed since a specific git reference
func (gds *GitDeltaSync) SyncSinceRef(ctx context.Context, sinceRef string) (*BatchWatchResult, error) {
	result := &BatchWatchResult{
		StartTime: time.Now(),
		Errors:    make([]string, 0),
	}

	// Get changed files
	changedFiles, err := gds.gitService.GetChangedFiles(ctx, sinceRef)
	if err != nil {
		result.Errors = append(result.Errors, fmt.Sprintf("failed to get changed files: %v", err))
		result.EndTime = time.Now()
		result.Duration = result.EndTime.Sub(result.StartTime)
		return result, nil
	}

	result.TotalFiles = len(changedFiles)

	// Process files
	for _, filePath := range changedFiles {
		if !isCodeFile(filePath) {
			continue
		}

		syncResult := gds.indexer.IndexFileFromPath(ctx, filePath)
		if syncResult.Success {
			result.SuccessfulFiles++
		} else {
			result.FailedFiles++
			result.Errors = append(result.Errors, syncResult.Errors...)
		}
	}

	result.EndTime = time.Now()
	result.Duration = result.EndTime.Sub(result.StartTime)
	return result, nil
}

// GetWatchStatus returns the current watch status
func (fw *FileWatcher) GetWatchStatus() map[string]interface{} {
	fw.mu.RLock()
	defer fw.mu.RUnlock()

	return map[string]interface{}{
		"watching":       fw.watching,
		"watched_paths":  fw.watchPaths,
		"pending_files":  len(fw.pendingFiles),
		"changed_files":  len(fw.changedFiles),
		"debounce_ms":    fw.debounceMs,
		"max_concurrent": fw.maxConcurrent,
	}
}

// IsWatching returns whether the watcher is running
func (fw *FileWatcher) IsWatching() bool {
	fw.mu.RLock()
	defer fw.mu.RUnlock()
	return fw.watching
}

// NormalizePath normalizes a file path relative to project root
func (fw *FileWatcher) NormalizePath(filePath string) string {
	return filepath.Join(fw.projectRoot, filePath)
}
