package codeindex

import (
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/google/uuid"
)

// WebhookHandler handles GitHub webhooks for incremental code sync
type WebhookHandler struct {
	indexer *Indexer
	repo    Repository
	secret  string
}

// NewWebhookHandler creates a new webhook handler
func NewWebhookHandler(indexer *Indexer, repo Repository, secret string) *WebhookHandler {
	return &WebhookHandler{
		indexer: indexer,
		repo:    repo,
		secret:  secret,
	}
}

// GitHubPushEvent represents a GitHub push webhook payload
type GitHubPushEvent struct {
	Ref        string         `json:"ref"`
	Before     string         `json:"before"`
	After      string         `json:"after"`
	Repository GitHubRepo     `json:"repository"`
	Commits    []GitHubCommit `json:"commits"`
	Pusher     GitHubUser     `json:"pusher"`
}

// GitHubRepo represents a GitHub repository
type GitHubRepo struct {
	ID       int64  `json:"id"`
	Name     string `json:"name"`
	FullName string `json:"full_name"`
	CloneURL string `json:"clone_url"`
}

// GitHubCommit represents a GitHub commit
type GitHubCommit struct {
	ID        string   `json:"id"`
	Message   string   `json:"message"`
	Timestamp string   `json:"timestamp"`
	Added     []string `json:"added"`
	Removed   []string `json:"removed"`
	Modified  []string `json:"modified"`
}

// GitHubUser represents a GitHub user
type GitHubUser struct {
	Name  string `json:"name"`
	Email string `json:"email"`
}

// SyncResult represents the result of an incremental sync
type SyncResult struct {
	ProjectID       uuid.UUID `json:"project_id"`
	CommitSHA       string    `json:"commit_sha"`
	FilesAdded      int       `json:"files_added"`
	FilesModified   int       `json:"files_modified"`
	FilesRemoved    int       `json:"files_removed"`
	EntitiesCreated int       `json:"entities_created"`
	EntitiesUpdated int       `json:"entities_updated"`
	EntitiesDeleted int       `json:"entities_deleted"`
	Duration        int64     `json:"duration"`
	Errors          []string  `json:"errors,omitempty"`
}

// VerifySignature verifies the GitHub webhook signature
func (handler *WebhookHandler) VerifySignature(payload []byte, signature string) bool {
	if handler.secret == "" {
		return true // No secret configured, skip verification
	}

	if !strings.HasPrefix(signature, "sha256=") {
		return false
	}

	expectedMAC := hmac.New(sha256.New, []byte(handler.secret))
	expectedMAC.Write(payload)
	expectedSig := "sha256=" + hex.EncodeToString(expectedMAC.Sum(nil))

	return hmac.Equal([]byte(signature), []byte(expectedSig))
}

// HandlePushEvent handles a GitHub push event for incremental sync
func (handler *WebhookHandler) HandlePushEvent(
	ctx context.Context,
	projectID uuid.UUID,
	payload []byte,
) (*SyncResult, error) {
	var event GitHubPushEvent
	if err := json.Unmarshal(payload, &event); err != nil {
		return nil, fmt.Errorf("failed to parse push event: %w", err)
	}

	start := time.Now()
	result := &SyncResult{
		ProjectID: projectID,
		CommitSHA: event.After,
		Errors:    make([]string, 0),
	}

	addedFiles, modifiedFiles, removedFiles := collectChangedFiles(event)

	result.FilesAdded = len(addedFiles)
	result.FilesModified = len(modifiedFiles)
	result.FilesRemoved = len(removedFiles)

	handler.deleteRemovedFiles(ctx, projectID, removedFiles, result)
	handler.indexChangedFiles(ctx, projectID, addedFiles, modifiedFiles, result)

	result.Duration = time.Since(start).Milliseconds()
	return result, nil
}

func collectChangedFiles(event GitHubPushEvent) (map[string]bool, map[string]bool, map[string]bool) {
	addedFiles := make(map[string]bool)
	modifiedFiles := make(map[string]bool)
	removedFiles := make(map[string]bool)

	for _, commit := range event.Commits {
		addCodeFiles(addedFiles, commit.Added)
		addCodeFiles(modifiedFiles, commit.Modified)
		addCodeFiles(removedFiles, commit.Removed)
	}

	return addedFiles, modifiedFiles, removedFiles
}

func addCodeFiles(files map[string]bool, candidates []string) {
	for _, file := range candidates {
		if isCodeFile(file) {
			files[file] = true
		}
	}
}

func (handler *WebhookHandler) deleteRemovedFiles(
	ctx context.Context,
	projectID uuid.UUID,
	removedFiles map[string]bool,
	result *SyncResult,
) {
	for filePath := range removedFiles {
		if err := handler.repo.DeleteByFilePath(ctx, projectID, filePath); err != nil {
			result.Errors = append(result.Errors, fmt.Sprintf("delete %s: %v", filePath, err))
		} else {
			result.EntitiesDeleted++
		}
	}
}

func (handler *WebhookHandler) indexChangedFiles(
	ctx context.Context,
	projectID uuid.UUID,
	addedFiles map[string]bool,
	modifiedFiles map[string]bool,
	result *SyncResult,
) {
	filesToIndex := buildIndexFileList(addedFiles, modifiedFiles)
	if len(filesToIndex) == 0 {
		return
	}

	indexResult, err := handler.indexer.Index(ctx, &IndexRequest{
		ProjectID:          projectID,
		Directory:          "",
		FilePaths:          filesToIndex,
		Recursive:          false,
		FilePatterns:       nil,
		ExcludePatterns:    nil,
		GenerateEmbeddings: true,
		LinkCanonical:      true,
		ResolveCrossLang:   true,
	})
	if err != nil {
		result.Errors = append(result.Errors, fmt.Sprintf("indexing: %v", err))
		return
	}

	result.EntitiesCreated = indexResult.EntitiesCreated
	result.Errors = append(result.Errors, indexResult.Errors...)
}

func buildIndexFileList(addedFiles map[string]bool, modifiedFiles map[string]bool) []string {
	filesToIndex := make([]string, 0, len(addedFiles)+len(modifiedFiles))
	for f := range addedFiles {
		filesToIndex = append(filesToIndex, f)
	}
	for f := range modifiedFiles {
		if !addedFiles[f] {
			filesToIndex = append(filesToIndex, f)
		}
	}
	return filesToIndex
}

// isCodeFile checks if a file is a code file we should index
func isCodeFile(path string) bool {
	extensions := []string{".ts", ".tsx", ".js", ".jsx", ".go", ".py", ".rs", ".java"}
	for _, ext := range extensions {
		if strings.HasSuffix(path, ext) {
			return true
		}
	}
	return false
}
