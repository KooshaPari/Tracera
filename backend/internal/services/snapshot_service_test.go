package services

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

// MockStorageService implements StorageService for testing
type MockStorageService struct {
	files map[string][]byte
}

func NewMockStorageService() *MockStorageService {
	return &MockStorageService{
		files: make(map[string][]byte),
	}
}

func (m *MockStorageService) UploadFile(_ context.Context, file []byte, bucket string, key string, _ string) (string, error) {
	m.files[key] = file
	return fmt.Sprintf("https://mock.s3.amazonaws.com/%s/%s", bucket, key), nil
}

func (m *MockStorageService) DownloadFile(_ context.Context, urlOrKey string) ([]byte, error) {
	if data, ok := m.files[urlOrKey]; ok {
		return data, nil
	}
	return nil, fmt.Errorf("file not found: %s", urlOrKey)
}

func (m *MockStorageService) DeleteFile(_ context.Context, urlOrKey string) error {
	delete(m.files, urlOrKey)
	return nil
}

func (m *MockStorageService) ListFiles(_ context.Context, bucket string, prefix string) ([]FileInfo, error) {
	var files []FileInfo
	for key := range m.files {
		if len(prefix) == 0 || len(key) >= len(prefix) && key[:len(prefix)] == prefix {
			files = append(files, FileInfo{
				Key:    key,
				Bucket: bucket,
				Size:   int64(len(m.files[key])),
			})
		}
	}
	return files, nil
}

func (m *MockStorageService) GetFileMetadata(_ context.Context, urlOrKey string) (*FileInfo, error) {
	if data, ok := m.files[urlOrKey]; ok {
		return &FileInfo{
			Key:  urlOrKey,
			Size: int64(len(data)),
		}, nil
	}
	return nil, fmt.Errorf("file not found: %s", urlOrKey)
}

func (m *MockStorageService) GeneratePresignedUploadURL(_ context.Context, bucket string, key string, _ string, _ int) (string, error) {
	return fmt.Sprintf("https://mock.s3.amazonaws.com/%s/%s?presigned=true", bucket, key), nil
}

func (m *MockStorageService) GeneratePresignedDownloadURL(_ context.Context, urlOrKey string, _ int) (string, error) {
	return "https://mock.s3.amazonaws.com/" + urlOrKey + "?presigned=true", nil
}

func (m *MockStorageService) CopyFile(_ context.Context, sourceURL string, _ string, destKey string) error {
	if data, ok := m.files[sourceURL]; ok {
		m.files[destKey] = data
		return nil
	}
	return fmt.Errorf("source file not found: %s", sourceURL)
}

func (m *MockStorageService) FileExists(_ context.Context, urlOrKey string) (bool, error) {
	_, ok := m.files[urlOrKey]
	return ok, nil
}

func (m *MockStorageService) DeleteMultiple(_ context.Context, urls []string) error {
	for _, url := range urls {
		delete(m.files, url)
	}
	return nil
}

// Test helper functions

func createTestSandbox(t *testing.T) string {
	// Create temporary sandbox directory
	tempDir, err := os.MkdirTemp("", "sandbox-test-*")
	if err != nil {
		t.Fatalf("Failed to create temp dir: %v", err)
	}

	// Create test files
	testFiles := map[string]string{
		"file1.txt":          "Hello, World!",
		"dir1/file2.txt":     "Test content",
		"dir2/file3.txt":     "More content",
		"dir2/sub/file4.txt": "Nested content",
	}

	for path, content := range testFiles {
		fullPath := filepath.Join(tempDir, path)
		if err := os.MkdirAll(filepath.Dir(fullPath), 0o750); err != nil {
			t.Fatalf("Failed to create directory: %v", err)
		}
		if err := os.WriteFile(fullPath, []byte(content), 0o600); err != nil {
			t.Fatalf("Failed to create test file: %v", err)
		}
	}

	return tempDir
}

// Tests

func TestNewSnapshotService(t *testing.T) {
	storage := NewMockStorageService()
	logger := log.New(os.Stdout, "[TEST] ", log.LstdFlags)

	service := NewSnapshotService(storage, "test-bucket", logger)
	if service == nil {
		t.Fatal("Expected non-nil service")
	}
}

func TestCreateSnapshot(t *testing.T) {
	storage := NewMockStorageService()
	logger := log.New(os.Stdout, "[TEST] ", log.LstdFlags)
	service := NewSnapshotService(storage, "test-bucket", logger)

	// Create test sandbox
	sandboxRoot := createTestSandbox(t)
	defer func() { require.NoError(t, os.RemoveAll(sandboxRoot)) }()

	ctx := context.Background()
	sessionID := testSnapshotSessionID
	turnNumber := 1

	// Create snapshot
	s3Key, metadata, err := service.CreateSnapshot(ctx, sessionID, sandboxRoot, turnNumber)
	if err != nil {
		t.Fatalf("CreateSnapshot failed: %v", err)
	}

	// Verify S3 key format
	expectedKey := fmt.Sprintf("sandboxes/%s/snapshots/snapshot-%d.tar.gz", sessionID, turnNumber)
	if s3Key != expectedKey {
		t.Errorf("Expected S3 key %s, got %s", expectedKey, s3Key)
	}

	// Verify metadata
	if metadata.SessionID != sessionID {
		t.Errorf("Expected session ID %s, got %s", sessionID, metadata.SessionID)
	}
	if metadata.TurnNumber != turnNumber {
		t.Errorf("Expected turn number %d, got %d", turnNumber, metadata.TurnNumber)
	}
	if metadata.FileCount != 4 {
		t.Errorf("Expected file count 4, got %d", metadata.FileCount)
	}
	if metadata.Size == 0 {
		t.Error("Expected non-zero size")
	}
	if metadata.CompressionRatio == 0 {
		t.Error("Expected non-zero compression ratio")
	}

	// Verify snapshot was uploaded
	exists, err := storage.FileExists(ctx, s3Key)
	if err != nil {
		t.Fatalf("FileExists failed: %v", err)
	}
	if !exists {
		t.Error("Expected snapshot to exist in storage")
	}

	// Verify metadata was uploaded
	metadataKey := fmt.Sprintf("sandboxes/%s/snapshots/snapshot-%d-metadata.json", sessionID, turnNumber)
	exists, err = storage.FileExists(ctx, metadataKey)
	if err != nil {
		t.Fatalf("FileExists failed for metadata: %v", err)
	}
	if !exists {
		t.Error("Expected metadata to exist in storage")
	}
}

func TestCreateSnapshot_InvalidInputs(t *testing.T) {
	storage := NewMockStorageService()
	logger := log.New(os.Stdout, "[TEST] ", log.LstdFlags)
	service := NewSnapshotService(storage, "test-bucket", logger)
	ctx := context.Background()

	tests := []struct {
		name        string
		sessionID   string
		sandboxRoot string
		turnNumber  int
		expectError bool
	}{
		{
			name:        "Empty session ID",
			sessionID:   "",
			sandboxRoot: "/tmp/test",
			turnNumber:  1,
			expectError: true,
		},
		{
			name:        "Empty sandbox root",
			sessionID:   "test-session",
			sandboxRoot: "",
			turnNumber:  1,
			expectError: true,
		},
		{
			name:        "Non-existent directory",
			sessionID:   "test-session",
			sandboxRoot: "/non/existent/path",
			turnNumber:  1,
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			_, _, err := service.CreateSnapshot(ctx, tt.sessionID, tt.sandboxRoot, tt.turnNumber)
			if tt.expectError && err == nil {
				t.Error("Expected error, got nil")
			}
			if !tt.expectError && err != nil {
				t.Errorf("Expected no error, got %v", err)
			}
		})
	}
}

func TestRestoreSnapshot(t *testing.T) {
	storage := NewMockStorageService()
	logger := log.New(os.Stdout, "[TEST] ", log.LstdFlags)
	service := NewSnapshotService(storage, "test-bucket", logger)

	// Create test sandbox
	sandboxRoot := createTestSandbox(t)
	defer func() { require.NoError(t, os.RemoveAll(sandboxRoot)) }()

	ctx := context.Background()
	sessionID := testSnapshotSessionID
	turnNumber := 1

	// Create snapshot
	s3Key, _, err := service.CreateSnapshot(ctx, sessionID, sandboxRoot, turnNumber)
	if err != nil {
		t.Fatalf("CreateSnapshot failed: %v", err)
	}

	// Create target directory for restoration
	restoreDir, err := os.MkdirTemp("", "restore-test-*")
	if err != nil {
		t.Fatalf("Failed to create restore dir: %v", err)
	}
	defer func() { require.NoError(t, os.RemoveAll(restoreDir)) }()

	// Restore snapshot
	err = service.RestoreSnapshot(ctx, sessionID, s3Key, restoreDir)
	if err != nil {
		t.Fatalf("RestoreSnapshot failed: %v", err)
	}

	// Verify restored files
	expectedFiles := []string{
		"file1.txt",
		"dir1/file2.txt",
		"dir2/file3.txt",
		"dir2/sub/file4.txt",
	}

	for _, file := range expectedFiles {
		fullPath := filepath.Join(restoreDir, file)
		if _, err := os.Stat(fullPath); os.IsNotExist(err) {
			t.Errorf("Expected file %s to exist after restore", file)
		}
	}

	// Verify file content
	content, err := os.ReadFile(filepath.Clean(filepath.Join(restoreDir, "file1.txt")))
	if err != nil {
		t.Fatalf("Failed to read restored file: %v", err)
	}
	expectedContent := "Hello, World!"
	if string(content) != expectedContent {
		t.Errorf("Expected content %q, got %q", expectedContent, string(content))
	}
}

func TestRestoreSnapshot_InvalidInputs(t *testing.T) {
	storage := NewMockStorageService()
	logger := log.New(os.Stdout, "[TEST] ", log.LstdFlags)
	service := NewSnapshotService(storage, "test-bucket", logger)
	ctx := context.Background()

	tests := []struct {
		name        string
		sessionID   string
		s3Key       string
		targetDir   string
		expectError bool
	}{
		{
			name:        "Empty session ID",
			sessionID:   "",
			s3Key:       "test-key",
			targetDir:   "/tmp/test",
			expectError: true,
		},
		{
			name:        "Empty S3 key",
			sessionID:   "test-session",
			s3Key:       "",
			targetDir:   "/tmp/test",
			expectError: true,
		},
		{
			name:        "Empty target dir",
			sessionID:   "test-session",
			s3Key:       "test-key",
			targetDir:   "",
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := service.RestoreSnapshot(ctx, tt.sessionID, tt.s3Key, tt.targetDir)
			if tt.expectError && err == nil {
				t.Error("Expected error, got nil")
			}
			if !tt.expectError && err != nil {
				t.Errorf("Expected no error, got %v", err)
			}
		})
	}
}

func TestGetSnapshotMetadata(t *testing.T) {
	storage := NewMockStorageService()
	logger := log.New(os.Stdout, "[TEST] ", log.LstdFlags)
	service := NewSnapshotService(storage, "test-bucket", logger)

	// Create test sandbox
	sandboxRoot := createTestSandbox(t)
	defer func() { require.NoError(t, os.RemoveAll(sandboxRoot)) }()

	ctx := context.Background()
	sessionID := testSnapshotSessionID
	turnNumber := 1

	// Create snapshot
	s3Key, originalMeta, err := service.CreateSnapshot(ctx, sessionID, sandboxRoot, turnNumber)
	if err != nil {
		t.Fatalf("CreateSnapshot failed: %v", err)
	}

	// Retrieve metadata
	metadata, err := service.GetSnapshotMetadata(ctx, s3Key)
	if err != nil {
		t.Fatalf("GetSnapshotMetadata failed: %v", err)
	}

	// Verify metadata
	if metadata.SessionID != originalMeta.SessionID {
		t.Errorf("Expected session ID %s, got %s", originalMeta.SessionID, metadata.SessionID)
	}
	if metadata.TurnNumber != originalMeta.TurnNumber {
		t.Errorf("Expected turn number %d, got %d", originalMeta.TurnNumber, metadata.TurnNumber)
	}
	if metadata.FileCount != originalMeta.FileCount {
		t.Errorf("Expected file count %d, got %d", originalMeta.FileCount, metadata.FileCount)
	}
}

func TestListSnapshots(t *testing.T) {
	storage := NewMockStorageService()
	logger := log.New(os.Stdout, "[TEST] ", log.LstdFlags)
	service := NewSnapshotService(storage, "test-bucket", logger)

	// Create test sandbox
	sandboxRoot := createTestSandbox(t)
	defer func() { require.NoError(t, os.RemoveAll(sandboxRoot)) }()

	ctx := context.Background()
	sessionID := testSnapshotSessionID

	// Create multiple snapshots
	for i := 1; i <= 3; i++ {
		_, _, err := service.CreateSnapshot(ctx, sessionID, sandboxRoot, i)
		if err != nil {
			t.Fatalf("CreateSnapshot %d failed: %v", i, err)
		}
	}

	// List snapshots
	snapshots, err := service.ListSnapshots(ctx, sessionID)
	if err != nil {
		t.Fatalf("ListSnapshots failed: %v", err)
	}

	if len(snapshots) != 3 {
		t.Errorf("Expected 3 snapshots, got %d", len(snapshots))
	}

	// Verify snapshot turn numbers
	turnNumbers := make(map[int]bool)
	for _, snapshot := range snapshots {
		turnNumbers[snapshot.TurnNumber] = true
	}
	for i := 1; i <= 3; i++ {
		if !turnNumbers[i] {
			t.Errorf("Expected turn number %d in snapshots", i)
		}
	}
}

func TestDeleteSnapshot(t *testing.T) {
	storage := NewMockStorageService()
	logger := log.New(os.Stdout, "[TEST] ", log.LstdFlags)
	service := NewSnapshotService(storage, "test-bucket", logger)

	// Create test sandbox
	sandboxRoot := createTestSandbox(t)
	defer func() { require.NoError(t, os.RemoveAll(sandboxRoot)) }()

	ctx := context.Background()
	sessionID := testSnapshotSessionID
	turnNumber := 1

	// Create snapshot
	s3Key, _, err := service.CreateSnapshot(ctx, sessionID, sandboxRoot, turnNumber)
	if err != nil {
		t.Fatalf("CreateSnapshot failed: %v", err)
	}

	// Verify snapshot exists
	exists, err := storage.FileExists(ctx, s3Key)
	if err != nil {
		t.Fatalf("FileExists failed: %v", err)
	}
	if !exists {
		t.Fatal("Expected snapshot to exist before deletion")
	}

	// Delete snapshot
	err = service.DeleteSnapshot(ctx, s3Key)
	if err != nil {
		t.Fatalf("DeleteSnapshot failed: %v", err)
	}

	// Verify snapshot was deleted
	exists, err = storage.FileExists(ctx, s3Key)
	if err != nil {
		t.Fatalf("FileExists failed: %v", err)
	}
	if exists {
		t.Error("Expected snapshot to be deleted")
	}
}

func TestCleanupOldSnapshots(t *testing.T) {
	storage := NewMockStorageService()
	logger := log.New(os.Stdout, "[TEST] ", log.LstdFlags)
	service := NewSnapshotService(storage, "test-bucket", logger)

	// Create test sandbox
	sandboxRoot := createTestSandbox(t)
	defer func() { require.NoError(t, os.RemoveAll(sandboxRoot)) }()

	ctx := context.Background()
	sessionID := testSnapshotSessionID

	// Create snapshots with different ages
	for i := 1; i <= 3; i++ {
		_, _, err := service.CreateSnapshot(ctx, sessionID, sandboxRoot, i)
		if err != nil {
			t.Fatalf("CreateSnapshot %d failed: %v", i, err)
		}

		// Manually update metadata to simulate old snapshots
		if i <= 2 {
			metadataKey := fmt.Sprintf("sandboxes/%s/snapshots/snapshot-%d-metadata.json", sessionID, i)
			data, err := storage.DownloadFile(ctx, metadataKey)
			require.NoError(t, err)
			var meta SnapshotMetadata
			require.NoError(t, json.Unmarshal(data, &meta))

			// Make snapshot older than retention period
			meta.CreatedAt = time.Now().AddDate(0, 0, -10)

			newData, err := json.Marshal(meta)
			require.NoError(t, err)
			_, err = storage.UploadFile(ctx, newData, "test-bucket", metadataKey, "application/json")
			if err != nil {
				t.Fatalf("UploadFile %d failed: %v", i, err)
			}
		}
	}

	// Cleanup snapshots older than 7 days
	err := service.CleanupOldSnapshots(ctx, sessionID, 7)
	if err != nil {
		t.Fatalf("CleanupOldSnapshots failed: %v", err)
	}

	// List remaining snapshots
	snapshots, err := service.ListSnapshots(ctx, sessionID)
	if err != nil {
		t.Fatalf("ListSnapshots failed: %v", err)
	}

	// Only snapshot 3 should remain
	if len(snapshots) != 1 {
		t.Errorf("Expected 1 snapshot remaining, got %d", len(snapshots))
	}
	if len(snapshots) > 0 && snapshots[0].TurnNumber != 3 {
		t.Errorf("Expected remaining snapshot to be turn 3, got turn %d", snapshots[0].TurnNumber)
	}
}

func TestCreateAndRestoreSnapshot_Integration(t *testing.T) {
	storage := NewMockStorageService()
	logger := log.New(os.Stdout, "[TEST] ", log.LstdFlags)
	service := NewSnapshotService(storage, "test-bucket", logger)

	// Create test sandbox with specific content
	sandboxRoot := createTestSandbox(t)
	defer func() { require.NoError(t, os.RemoveAll(sandboxRoot)) }()

	ctx := context.Background()
	sessionID := "integration-test-session"
	turnNumber := 1

	// Create snapshot
	s3Key, metadata, err := service.CreateSnapshot(ctx, sessionID, sandboxRoot, turnNumber)
	if err != nil {
		t.Fatalf("CreateSnapshot failed: %v", err)
	}

	t.Logf("Created snapshot: %s (size: %d bytes, files: %d, compression: %.2f)",
		s3Key, metadata.Size, metadata.FileCount, metadata.CompressionRatio)

	// Create restore directory
	restoreDir, err := os.MkdirTemp("", "integration-restore-*")
	if err != nil {
		t.Fatalf("Failed to create restore dir: %v", err)
	}
	defer func() { require.NoError(t, os.RemoveAll(restoreDir)) }()

	// Restore snapshot
	err = service.RestoreSnapshot(ctx, sessionID, s3Key, restoreDir)
	if err != nil {
		t.Fatalf("RestoreSnapshot failed: %v", err)
	}

	// Verify all files were restored correctly
	err = filepath.Walk(sandboxRoot, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() {
			return nil
		}

		relPath, err := filepath.Rel(sandboxRoot, path)
		require.NoError(t, err)
		restoredPath := filepath.Join(restoreDir, relPath)

		// Check file exists
		if _, err := os.Stat(restoredPath); os.IsNotExist(err) {
			t.Errorf("File %s not found in restored directory", relPath)
			return nil
		}

		// Compare content
		originalContent, err := os.ReadFile(filepath.Clean(path))
		require.NoError(t, err)
		restoredContent, err := os.ReadFile(filepath.Clean(restoredPath))
		require.NoError(t, err)

		if string(originalContent) != string(restoredContent) {
			t.Errorf("Content mismatch for %s", relPath)
		}

		return nil
	})
	if err != nil {
		t.Fatalf("Failed to verify restored files: %v", err)
	}
}
