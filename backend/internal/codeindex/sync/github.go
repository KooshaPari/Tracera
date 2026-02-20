// Package sync provides sync functionality.
package sync

import (
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/codeindex"
)

const (
	githubSignatureParts     = 2
	githubMaxConcurrentFetch = 5
)

// GitHubSyncer handles incremental synchronization with GitHub repositories
type GitHubSyncer struct {
	owner          string
	repo           string
	token          string
	webhookSecret  string
	projectID      uuid.UUID
	lastSyncTime   time.Time
	changedFiles   map[string]string // filePath -> changeType (modified, added, deleted)
	mu             sync.RWMutex
	syncInProgress bool
}

// GitHubWebhookPayload represents a GitHub webhook push payload
type GitHubWebhookPayload struct {
	Ref        string           `json:"ref"`
	Repository GitHubRepository `json:"repository"`
	Pusher     GitHubPusher     `json:"pusher"`
	Commits    []GitHubCommit   `json:"commits"`
	HeadCommit GitHubCommit     `json:"head_commit"`
	Deleted    bool             `json:"deleted"`
	Created    bool             `json:"created"`
	Forced     bool             `json:"forced"`
}

// GitHubRepository represents repository information in webhook
type GitHubRepository struct {
	ID          int         `json:"id"`
	Name        string      `json:"name"`
	FullName    string      `json:"full_name"`
	Owner       GitHubOwner `json:"owner"`
	CloneURL    string      `json:"clone_url"`
	SSHURL      string      `json:"ssh_url"`
	Description string      `json:"description"`
}

// GitHubOwner represents the repository owner
type GitHubOwner struct {
	Name  string `json:"name"`
	Email string `json:"email"`
}

// GitHubPusher represents who triggered the push
type GitHubPusher struct {
	Name  string `json:"name"`
	Email string `json:"email"`
}

// GitHubCommit represents a commit in the webhook
type GitHubCommit struct {
	ID        string       `json:"id"`
	Message   string       `json:"message"`
	Timestamp string       `json:"timestamp"`
	Author    GitHubAuthor `json:"author"`
	Added     []string     `json:"added"`
	Removed   []string     `json:"removed"`
	Modified  []string     `json:"modified"`
}

// GitHubAuthor represents commit author information
type GitHubAuthor struct {
	Name     string `json:"name"`
	Email    string `json:"email"`
	Username string `json:"username"`
}

// Result contains the result of a sync operation
type Result struct {
	ProjectID       uuid.UUID     `json:"project_id"`
	StartTime       time.Time     `json:"start_time"`
	EndTime         time.Time     `json:"end_time"`
	Duration        time.Duration `json:"duration"`
	FilesProcessed  int           `json:"files_processed"`
	FilesAdded      int           `json:"files_added"`
	FilesModified   int           `json:"files_modified"`
	FilesDeleted    int           `json:"files_deleted"`
	EntitiesAdded   int           `json:"entities_added"`
	EntitiesUpdated int           `json:"entities_updated"`
	Errors          []string      `json:"errors"`
	Success         bool          `json:"success"`
}

// NewGitHubSyncer creates a new GitHub syncer
func NewGitHubSyncer(projectID uuid.UUID, owner, repo, token, webhookSecret string) *GitHubSyncer {
	return &GitHubSyncer{
		projectID:     projectID,
		owner:         owner,
		repo:          repo,
		token:         token,
		webhookSecret: webhookSecret,
		changedFiles:  make(map[string]string),
		lastSyncTime:  time.Now(),
	}
}

// ValidateWebhookSignature validates the GitHub webhook signature
func (gs *GitHubSyncer) ValidateWebhookSignature(payload []byte, signature string) bool {
	if gs.webhookSecret == "" {
		return true // No validation if secret not set
	}

	// GitHub sends as "sha256=<hash>"
	parts := strings.Split(signature, "=")
	if len(parts) != githubSignatureParts {
		return false
	}

	expectedSignature := parts[1]

	// Compute HMAC-SHA256
	h := hmac.New(sha256.New, []byte(gs.webhookSecret))
	h.Write(payload)
	computedSignature := hex.EncodeToString(h.Sum(nil))

	return hmac.Equal([]byte(expectedSignature), []byte(computedSignature))
}

// HandleWebhook processes an incoming GitHub webhook
func (gs *GitHubSyncer) HandleWebhook(ctx context.Context, payload []byte) (*Result, error) {
	_ = ctx
	var webhookPayload GitHubWebhookPayload
	if err := json.Unmarshal(payload, &webhookPayload); err != nil {
		return nil, fmt.Errorf("failed to unmarshal webhook payload: %w", err)
	}

	result := &Result{
		ProjectID: gs.projectID,
		StartTime: time.Now(),
	}

	gs.mu.Lock()
	if gs.syncInProgress {
		gs.mu.Unlock()
		return result, errors.New("sync already in progress")
	}
	gs.syncInProgress = true
	gs.mu.Unlock()

	defer func() {
		gs.mu.Lock()
		gs.syncInProgress = false
		gs.mu.Unlock()
	}()

	// Extract branch from ref (e.g., "refs/heads/main" -> "main")
	_ = strings.TrimPrefix(webhookPayload.Ref, "refs/heads/")

	// Collect changed files
	changedFiles := make(map[string]string)
	for _, commit := range webhookPayload.Commits {
		for _, file := range commit.Added {
			changedFiles[file] = "added"
		}
		for _, file := range commit.Modified {
			changedFiles[file] = "modified"
		}
		for _, file := range commit.Removed {
			changedFiles[file] = "deleted"
		}
	}

	// Update our tracking
	gs.mu.Lock()
	gs.changedFiles = changedFiles
	gs.lastSyncTime = time.Now()
	gs.mu.Unlock()

	result.FilesProcessed = len(changedFiles)
	result.FilesAdded = len(webhookPayload.HeadCommit.Added)
	result.FilesModified = len(webhookPayload.HeadCommit.Modified)
	result.FilesDeleted = len(webhookPayload.HeadCommit.Removed)
	result.Success = true
	result.EndTime = time.Now()
	result.Duration = result.EndTime.Sub(result.StartTime)

	return result, nil
}

// GetChangedFiles returns the files that were changed in the last sync
func (gs *GitHubSyncer) GetChangedFiles() map[string]string {
	gs.mu.RLock()
	defer gs.mu.RUnlock()

	// Make a copy
	files := make(map[string]string)
	for k, v := range gs.changedFiles {
		files[k] = v
	}
	return files
}

// GetLastSyncTime returns the last sync time
func (gs *GitHubSyncer) GetLastSyncTime() time.Time {
	gs.mu.RLock()
	defer gs.mu.RUnlock()
	return gs.lastSyncTime
}

// ClearChangedFiles clears the changed files tracking
func (gs *GitHubSyncer) ClearChangedFiles() {
	gs.mu.Lock()
	defer gs.mu.Unlock()
	gs.changedFiles = make(map[string]string)
}

// DeltaSync performs an incremental sync of changed files
type DeltaSync struct {
	syncer      *GitHubSyncer
	fileFetcher FileFetcher
	codeIndexer CodeIndexer
	mu          sync.RWMutex
}

// FileFetcher interface for fetching file contents from GitHub
type FileFetcher interface {
	FetchFile(ctx context.Context, owner, repo, branch, path string) ([]byte, error)
}

// CodeIndexer interface for indexing code entities
type CodeIndexer interface {
	IndexFile(
		ctx context.Context,
		filePath string,
		content string,
		language codeindex.Language,
	) (*codeindex.IndexingResult, error)
}

// NewDeltaSync creates a new delta syncer
func NewDeltaSync(syncer *GitHubSyncer, fetcher FileFetcher, indexer CodeIndexer) *DeltaSync {
	return &DeltaSync{
		syncer:      syncer,
		fileFetcher: fetcher,
		codeIndexer: indexer,
	}
}

// SyncChangedFiles syncs only the files that were changed
func (ds *DeltaSync) SyncChangedFiles(ctx context.Context, branch string) (*Result, error) {
	ds.mu.Lock()
	defer ds.mu.Unlock()

	result := &Result{
		ProjectID: ds.syncer.projectID,
		StartTime: time.Now(),
	}

	changedFiles := ds.syncer.GetChangedFiles()
	if len(changedFiles) == 0 {
		ds.finishResult(result, nil)
		return result, nil
	}

	result.FilesProcessed = len(changedFiles)

	// Determine which files are code files
	codeFiles := filterCodeFiles(changedFiles)

	// Skip if no code files changed
	if len(codeFiles) == 0 {
		ds.finishResult(result, nil)
		return result, nil
	}

	// Process each file
	errors := ds.processCodeFiles(ctx, branch, codeFiles, result)
	ds.finishResult(result, errors)

	return result, nil
}

func filterCodeFiles(changedFiles map[string]string) map[string]string {
	codeFiles := make(map[string]string)
	for filePath, changeType := range changedFiles {
		if isCodeFile(filePath) {
			codeFiles[filePath] = changeType
		}
	}
	return codeFiles
}

func (ds *DeltaSync) processCodeFiles(
	ctx context.Context,
	branch string,
	codeFiles map[string]string,
	result *Result,
) []string {
	errors := make([]string, 0)
	for filePath, changeType := range codeFiles {
		if changeType == "deleted" {
			result.FilesDeleted++
			continue
		}

		content, err := ds.fileFetcher.FetchFile(ctx, ds.syncer.owner, ds.syncer.repo, branch, filePath)
		if err != nil {
			errors = append(errors, fmt.Sprintf("failed to fetch %s: %v", filePath, err))
			continue
		}

		lang := detectLanguage(filePath)
		indexResult, err := ds.codeIndexer.IndexFile(ctx, filePath, string(content), lang)
		if err != nil {
			errors = append(errors, fmt.Sprintf("failed to index %s: %v", filePath, err))
			continue
		}

		if !indexResult.Success {
			errors = append(errors, "indexing failed for "+filePath+": "+strings.Join(indexResult.Errors, "; "))
			continue
		}

		result.EntitiesAdded += indexResult.EntitiesCount
		switch changeType {
		case "added":
			result.FilesAdded++
		case "modified":
			result.FilesModified++
		}
	}
	return errors
}

func (ds *DeltaSync) finishResult(result *Result, errors []string) {
	result.Errors = errors
	result.Success = len(errors) == 0
	result.EndTime = time.Now()
	result.Duration = result.EndTime.Sub(result.StartTime)
}

// FullSync performs a complete sync of the repository
func (ds *DeltaSync) FullSync(ctx context.Context, filePaths []string, branch string) (*Result, error) {
	ds.mu.Lock()
	defer ds.mu.Unlock()

	result := &Result{
		ProjectID: ds.syncer.projectID,
		StartTime: time.Now(),
	}

	result.FilesProcessed = len(filePaths)
	errors := make([]string, 0)

	// Process each file in parallel (with semaphore)
	semaphore := make(chan struct{}, githubMaxConcurrentFetch) // Max concurrent fetches
	results := make(chan *fileIndexResult, len(filePaths))

	for _, filePath := range filePaths {
		go func(fp string) {
			semaphore <- struct{}{}        // Acquire
			defer func() { <-semaphore }() // Release

			// Fetch file
			content, err := ds.fileFetcher.FetchFile(ctx, ds.syncer.owner, ds.syncer.repo, branch, fp)
			if err != nil {
				results <- &fileIndexResult{path: fp, err: err}
				return
			}

			// Index file
			lang := detectLanguage(fp)
			indexResult, err := ds.codeIndexer.IndexFile(ctx, fp, string(content), lang)
			if err != nil {
				results <- &fileIndexResult{path: fp, err: err}
				return
			}

			results <- &fileIndexResult{
				path:     fp,
				success:  indexResult.Success,
				entities: indexResult.EntitiesCount,
			}
		}(filePath)
	}

	// Collect results
	for i := 0; i < len(filePaths); i++ {
		res := <-results
		switch {
		case res.err != nil:
			errors = append(errors, fmt.Sprintf("failed to process %s: %v", res.path, res.err))
		case !res.success:
			errors = append(errors, "indexing failed for "+res.path)
		default:
			result.EntitiesAdded += res.entities
		}
	}

	result.Errors = errors
	result.Success = len(errors) == 0
	result.EndTime = time.Now()
	result.Duration = result.EndTime.Sub(result.StartTime)

	return result, nil
}

// fileIndexResult represents a single file indexing result
type fileIndexResult struct {
	path     string
	success  bool
	entities int
	err      error
}

// isCodeFile checks if a file is a code file we care about
func isCodeFile(filePath string) bool {
	codeExtensions := map[string]bool{
		".ts":   true,
		".tsx":  true,
		".js":   true,
		".jsx":  true,
		".go":   true,
		".py":   true,
		".java": true,
		".rs":   true,
		".cpp":  true,
		".c":    true,
		".h":    true,
		".cs":   true,
		".rb":   true,
		".php":  true,
	}

	for ext := range codeExtensions {
		if strings.HasSuffix(filePath, ext) {
			return true
		}
	}
	return false
}

// detectLanguage detects the language from a file path
func detectLanguage(filePath string) codeindex.Language {
	switch {
	case strings.HasSuffix(filePath, ".ts"), strings.HasSuffix(filePath, ".tsx"):
		return codeindex.LanguageTypeScript
	case strings.HasSuffix(filePath, ".js"), strings.HasSuffix(filePath, ".jsx"):
		return codeindex.LanguageJavaScript
	case strings.HasSuffix(filePath, ".go"):
		return codeindex.LanguageGo
	case strings.HasSuffix(filePath, ".py"):
		return codeindex.LanguagePython
	case strings.HasSuffix(filePath, ".java"):
		return codeindex.LanguageJava
	case strings.HasSuffix(filePath, ".rs"):
		return codeindex.LanguageRust
	default:
		return codeindex.LanguageTypeScript
	}
}

// WebhookHandler creates an HTTP handler for GitHub webhooks
func (gs *GitHubSyncer) WebhookHandler(syncer *DeltaSync) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// Read request body
		body, err := io.ReadAll(r.Body)
		if err != nil {
			http.Error(w, "failed to read body", http.StatusBadRequest)
			return
		}

		// Validate signature
		signature := r.Header.Get("X-Hub-Signature-256")
		if !gs.ValidateWebhookSignature(body, signature) {
			http.Error(w, "invalid signature", http.StatusUnauthorized)
			return
		}

		// Handle webhook
		ctx := r.Context()
		result, err := gs.HandleWebhook(ctx, body)
		if err != nil {
			http.Error(w, fmt.Sprintf("failed to process webhook: %v", err), http.StatusInternalServerError)
			return
		}

		// Perform incremental sync
		if syncer != nil {
			syncResult, err := syncer.SyncChangedFiles(ctx, "main") // Branch could be extracted from payload
			if err != nil {
				http.Error(w, fmt.Sprintf("failed to sync: %v", err), http.StatusInternalServerError)
				return
			}
			result = syncResult
		}

		// Return result
		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(result); err != nil {
			slog.Warn("failed to encode webhook response", "error", err)
		}
	}
}
