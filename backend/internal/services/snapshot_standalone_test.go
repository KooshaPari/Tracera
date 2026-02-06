//nolint:gosec //G304,G306 - test file uses standard file permissions for test data
package services

import (
	"context"
	"os"
	"path/filepath"
	"testing"
)

// This is a standalone integration test for the snapshot service
// It tests the core functionality without depending on the full service layer

func TestSnapshotService_Standalone(t *testing.T) {
	// Skip if running in CI or if MinIO is not available
	if testing.Short() {
		t.Skip("Skipping snapshot service integration test in short mode")
	}

	storage := NewMockStorageService()
	service := NewSnapshotService(storage, "test-bucket", nil)
	if service == nil {
		t.Fatal("Expected non-nil service")
	}

	sandboxRoot := createTempDir(t, "sandbox-test-*")
	testFile := filepath.Join(sandboxRoot, "test.txt")
	writeFile(t, testFile, "Hello, World!")

	ctx := context.Background()
	sessionID := testSnapshotSessionID
	turnNumber := 1

	s3Key, metadata := createSnapshot(ctx, t, service, sessionID, sandboxRoot, turnNumber)
	assertSnapshotMetadata(t, s3Key, metadata)

	restoreDir := createTempDir(t, "restore-test-*")
	restoreSnapshot(ctx, t, service, sessionID, s3Key, restoreDir)
	verifyRestoredFile(t, restoreDir, "test.txt", "Hello, World!")

	retrievedMeta := getSnapshotMetadata(ctx, t, service, s3Key)
	assertSessionID(t, sessionID, retrievedMeta.SessionID)

	assertSnapshotsList(ctx, t, service, sessionID, 1)
	deleteSnapshot(ctx, t, service, s3Key)
	assertSnapshotDeleted(ctx, t, storage, s3Key)
}

func createTempDir(t *testing.T, pattern string) string {
	t.Helper()
	dir, err := os.MkdirTemp("", pattern)
	if err != nil {
		t.Fatalf("Failed to create temp dir: %v", err)
	}
	t.Cleanup(func() { _ = os.RemoveAll(dir) })
	return dir
}

func writeFile(t *testing.T, path string, content string) {
	t.Helper()
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatalf("Failed to write file: %v", err)
	}
}

func createSnapshot(ctx context.Context, t *testing.T, service SnapshotService, sessionID, sandboxRoot string, turnNumber int) (string, *SnapshotMetadata) {
	t.Helper()
	s3Key, metadata, err := service.CreateSnapshot(ctx, sessionID, sandboxRoot, turnNumber)
	if err != nil {
		t.Fatalf("CreateSnapshot failed: %v", err)
	}
	return s3Key, metadata
}

func assertSnapshotMetadata(t *testing.T, s3Key string, metadata *SnapshotMetadata) {
	t.Helper()
	if s3Key == "" {
		t.Error("Expected non-empty S3 key")
	}
	if metadata == nil {
		t.Fatal("Expected non-nil metadata")
	}
	if metadata.FileCount != 1 {
		t.Errorf("Expected file count 1, got %d", metadata.FileCount)
	}
	t.Logf("Snapshot created successfully: %s", s3Key)
	t.Logf("Metadata: Size=%d, Files=%d, Compression=%.2f",
		metadata.Size, metadata.FileCount, metadata.CompressionRatio)
}

func restoreSnapshot(ctx context.Context, t *testing.T, service SnapshotService, sessionID, s3Key, restoreDir string) {
	t.Helper()
	if err := service.RestoreSnapshot(ctx, sessionID, s3Key, restoreDir); err != nil {
		t.Fatalf("RestoreSnapshot failed: %v", err)
	}
}

func verifyRestoredFile(t *testing.T, restoreDir, filename, expected string) {
	t.Helper()
	restoredFile := filepath.Join(restoreDir, filename)
	content, err := os.ReadFile(restoredFile)
	if err != nil {
		t.Fatalf("Failed to read restored file: %v", err)
	}
	if string(content) != expected {
		t.Errorf("Expected content %q, got %q", expected, string(content))
	}
	t.Log("Snapshot restored successfully")
}

func getSnapshotMetadata(ctx context.Context, t *testing.T, service SnapshotService, s3Key string) *SnapshotMetadata {
	t.Helper()
	retrievedMeta, err := service.GetSnapshotMetadata(ctx, s3Key)
	if err != nil {
		t.Fatalf("GetSnapshotMetadata failed: %v", err)
	}
	return retrievedMeta
}

func assertSessionID(t *testing.T, expected, actual string) {
	t.Helper()
	if actual != expected {
		t.Errorf("Expected session ID %s, got %s", expected, actual)
	}
}

func assertSnapshotsList(ctx context.Context, t *testing.T, service SnapshotService, sessionID string, expectedCount int) {
	t.Helper()
	snapshots, err := service.ListSnapshots(ctx, sessionID)
	if err != nil {
		t.Fatalf("ListSnapshots failed: %v", err)
	}
	if len(snapshots) != expectedCount {
		t.Errorf("Expected %d snapshot, got %d", expectedCount, len(snapshots))
	}
}

func deleteSnapshot(ctx context.Context, t *testing.T, service SnapshotService, s3Key string) {
	t.Helper()
	if err := service.DeleteSnapshot(ctx, s3Key); err != nil {
		t.Fatalf("DeleteSnapshot failed: %v", err)
	}
}

func assertSnapshotDeleted(ctx context.Context, t *testing.T, storage *MockStorageService, s3Key string) {
	t.Helper()
	exists, err := storage.FileExists(ctx, s3Key)
	if err != nil {
		t.Fatalf("FileExists failed: %v", err)
	}
	if exists {
		t.Error("Expected snapshot to be deleted")
	}
	t.Log("All snapshot service tests passed!")
}
