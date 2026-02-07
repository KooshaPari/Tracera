//go:build integration
// +build integration

package storage

import (
	"bytes"
	"context"
	"io"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	miniocontainer "github.com/testcontainers/testcontainers-go/modules/minio"
	"github.com/testcontainers/testcontainers-go/wait"
)

type MinIOContainerSetup struct {
	Container testcontainers.Container
	Endpoint  string
	Storage   *S3Storage
}

// setupMinIOContainer starts a MinIO testcontainer for integration testing
func setupMinIOContainer(ctx context.Context, t *testing.T) *MinIOContainerSetup {
	t.Helper()

	req := testcontainers.ContainerRequest{
		Image:        "minio/minio:latest",
		ExposedPorts: []string{"9000/tcp"},
		Env: map[string]string{
			"MINIO_ROOT_USER":     "minioadmin",
			"MINIO_ROOT_PASSWORD": "minioadmin",
		},
		WaitingFor: wait.ForLog("API listening on"),
		Cmd:        []string{"minio", "server", "/data"},
	}

	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	require.NoError(t, err, "failed to start MinIO container")

	host, err := container.Host(ctx)
	require.NoError(t, err)

	port, err := container.MappedPort(ctx, "9000/tcp")
	require.NoError(t, err)

	endpoint := "http://" + host + ":" + port.Port()

	// Create S3Storage client
	cfg := S3Config{
		Endpoint:        endpoint,
		AccessKeyID:     "minioadmin",
		SecretAccessKey: "minioadmin",
		Bucket:          "test-bucket",
		Region:          "us-east-1",
	}

	storage, err := NewS3Storage(cfg)
	require.NoError(t, err)

	// Ensure bucket exists
	_, err = storage.EnsureBucket(ctx)
	require.NoError(t, err)

	return &MinIOContainerSetup{
		Container: container,
		Endpoint:  endpoint,
		Storage:   storage,
	}
}

// setupMinIOContainerAlt is an alternative setup using the minio module directly
func setupMinIOContainerAlt(ctx context.Context, t *testing.T) *MinIOContainerSetup {
	t.Helper()

	minioContainer, err := miniocontainer.RunContainer(ctx,
		testcontainers.WithImage("minio/minio:latest"),
		miniocontainer.WithUsername("minioadmin"),
		miniocontainer.WithPassword("minioadmin"),
	)
	require.NoError(t, err, "failed to start MinIO container")

	endpoint, err := minioContainer.GetEndpoint(ctx)
	require.NoError(t, err)

	// Create S3Storage client
	cfg := S3Config{
		Endpoint:        endpoint,
		AccessKeyID:     "minioadmin",
		SecretAccessKey: "minioadmin",
		Bucket:          "test-bucket",
		Region:          "us-east-1",
	}

	storage, err := NewS3Storage(cfg)
	require.NoError(t, err)

	// Ensure bucket exists
	_, err = storage.EnsureBucket(ctx)
	require.NoError(t, err)

	return &MinIOContainerSetup{
		Container: minioContainer.Container,
		Endpoint:  endpoint,
		Storage:   storage,
	}
}

// Cleanup stops the MinIO container
func (m *MinIOContainerSetup) Cleanup(ctx context.Context, t *testing.T) {
	if m.Container != nil {
		err := m.Container.Terminate(ctx)
		require.NoError(t, err)
	}
}

// ============================================================================
// Integration Tests with MinIO Testcontainer
// ============================================================================

func TestS3Storage_Integration_UploadDownload(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	// Test data
	testData := []byte("Hello, MinIO! This is test content.")
	contentType := "text/plain"

	// Upload
	result, err := setup.Storage.Upload(ctx, "test/hello.txt", bytes.NewReader(testData), contentType)
	require.NoError(t, err)
	assert.NotEmpty(t, result.Key)
	assert.Equal(t, int64(len(testData)), result.Size)
	assert.Equal(t, contentType, result.ContentType)

	// Verify file exists
	exists, err := setup.Storage.Exists(ctx, result.Key)
	require.NoError(t, err)
	assert.True(t, exists)

	// Download
	reader, err := setup.Storage.Download(ctx, result.Key)
	require.NoError(t, err)
	defer reader.Close()

	downloaded, err := io.ReadAll(reader)
	require.NoError(t, err)
	assert.Equal(t, testData, downloaded)
}

func TestS3Storage_Integration_UploadWithAutoKey(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	testData := []byte("auto key test")

	// Upload with empty key - should auto-generate
	result, err := setup.Storage.Upload(ctx, "", bytes.NewReader(testData), "text/plain")
	require.NoError(t, err)
	assert.NotEmpty(t, result.Key)
	assert.Contains(t, result.Key, "uploads/")

	// Verify it was uploaded
	exists, err := setup.Storage.Exists(ctx, result.Key)
	require.NoError(t, err)
	assert.True(t, exists)
}

func TestS3Storage_Integration_Delete(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	// Upload a file
	result, err := setup.Storage.Upload(ctx, "delete-test/file.txt", bytes.NewReader([]byte("delete me")), "text/plain")
	require.NoError(t, err)

	// Verify it exists
	exists, err := setup.Storage.Exists(ctx, result.Key)
	require.NoError(t, err)
	assert.True(t, exists)

	// Delete it
	err = setup.Storage.Delete(ctx, result.Key)
	require.NoError(t, err)

	// Verify it's gone
	exists, err = setup.Storage.Exists(ctx, result.Key)
	require.NoError(t, err)
	assert.False(t, exists)
}

func TestS3Storage_Integration_DeleteMultiple(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	// Upload multiple files
	keys := make([]string, 5)
	for i := 0; i < 5; i++ {
		result, err := setup.Storage.Upload(ctx, "", bytes.NewReader([]byte("test")), "text/plain")
		require.NoError(t, err)
		keys[i] = result.Key
	}

	// Delete all at once
	err := setup.Storage.DeleteMultiple(ctx, keys)
	require.NoError(t, err)

	// Verify all are deleted
	for _, key := range keys {
		exists, err := setup.Storage.Exists(ctx, key)
		require.NoError(t, err)
		assert.False(t, exists, "key should not exist: %s", key)
	}
}

func TestS3Storage_Integration_GetFileSize(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	testData := []byte("size test content")

	// Upload
	result, err := setup.Storage.Upload(ctx, "size-test/file.txt", bytes.NewReader(testData), "text/plain")
	require.NoError(t, err)

	// Get size
	size, err := setup.Storage.GetFileSize(ctx, result.Key)
	require.NoError(t, err)
	assert.Equal(t, int64(len(testData)), size)
}

func TestS3Storage_Integration_GeneratePresignedDownloadURL(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	// Upload a file
	result, err := setup.Storage.Upload(ctx, "presigned/file.txt", bytes.NewReader([]byte("test")), "text/plain")
	require.NoError(t, err)

	// Generate presigned URL with custom expiry
	presigned, err := setup.Storage.GeneratePresignedDownloadURL(ctx, result.Key, 2*time.Hour)
	require.NoError(t, err)
	assert.NotEmpty(t, presigned.URL)
	assert.Equal(t, "GET", presigned.Method)
	assert.True(t, presigned.ExpiresAt.After(time.Now()))

	// Verify expiry is approximately 2 hours from now
	expiryDiff := presigned.ExpiresAt.Sub(time.Now())
	assert.Greater(t, expiryDiff, 119*time.Minute) // Allow 1 minute drift
	assert.Less(t, expiryDiff, 121*time.Minute)
}

func TestS3Storage_Integration_GeneratePresignedDownloadURL_DefaultExpiry(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	// Upload a file
	result, err := setup.Storage.Upload(ctx, "presigned/file.txt", bytes.NewReader([]byte("test")), "text/plain")
	require.NoError(t, err)

	// Generate presigned URL with default expiry (0 = use default)
	presigned, err := setup.Storage.GeneratePresignedDownloadURL(ctx, result.Key, 0)
	require.NoError(t, err)
	assert.NotEmpty(t, presigned.URL)

	// Verify default is 24 hours
	expiryDiff := presigned.ExpiresAt.Sub(time.Now())
	assert.Greater(t, expiryDiff, 23*time.Hour)
	assert.Less(t, expiryDiff, 25*time.Hour)
}

func TestS3Storage_Integration_GeneratePresignedUploadURL(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	// Generate presigned upload URL with custom expiry
	presigned, err := setup.Storage.GeneratePresignedUploadURL(ctx, "presigned/upload.txt", "text/plain", 1*time.Hour)
	require.NoError(t, err)
	assert.NotEmpty(t, presigned.URL)
	assert.Equal(t, "PUT", presigned.Method)
	assert.True(t, presigned.ExpiresAt.After(time.Now()))
}

func TestS3Storage_Integration_GeneratePresignedUploadURL_AutoKey(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	// Generate presigned upload URL with empty key - should auto-generate
	presigned, err := setup.Storage.GeneratePresignedUploadURL(ctx, "", "application/json", 30*time.Minute)
	require.NoError(t, err)
	assert.NotEmpty(t, presigned.URL)
	assert.Equal(t, "PUT", presigned.Method)
}

func TestS3Storage_Integration_CopyObject(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	testData := []byte("copy source content")

	// Upload original
	result, err := setup.Storage.Upload(ctx, "copy-test/original.txt", bytes.NewReader(testData), "text/plain")
	require.NoError(t, err)

	// Copy object
	destKey := "copy-test/copied.txt"
	err = setup.Storage.CopyObject(ctx, result.Key, destKey)
	require.NoError(t, err)

	// Verify copy exists
	exists, err := setup.Storage.Exists(ctx, destKey)
	require.NoError(t, err)
	assert.True(t, exists)

	// Verify content is the same
	reader, err := setup.Storage.Download(ctx, destKey)
	require.NoError(t, err)
	defer reader.Close()

	copied, err := io.ReadAll(reader)
	require.NoError(t, err)
	assert.Equal(t, testData, copied)
}

func TestS3Storage_Integration_ListObjects(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	prefix := "list-test/"

	// Upload multiple files with common prefix
	uploadedKeys := make([]string, 5)
	for i := 0; i < 5; i++ {
		result, err := setup.Storage.Upload(ctx, prefix+"file_"+string(rune(i+48))+".txt", bytes.NewReader([]byte("test")), "text/plain")
		require.NoError(t, err)
		uploadedKeys[i] = result.Key
	}

	// List objects with prefix
	keys, err := setup.Storage.ListObjects(ctx, prefix)
	require.NoError(t, err)
	assert.GreaterOrEqual(t, len(keys), 5)

	// Verify all uploaded keys are in the list
	for _, uploaded := range uploadedKeys {
		found := false
		for _, listed := range keys {
			if listed == uploaded {
				found = true
				break
			}
		}
		assert.True(t, found, "uploaded key not found in list: %s", uploaded)
	}

	// Cleanup
	err = setup.Storage.DeleteMultiple(ctx, uploadedKeys)
	require.NoError(t, err)
}

func TestS3Storage_Integration_UploadWithThumbnail(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	imageData := []byte("fake image data")

	// Upload with thumbnail
	result, err := setup.Storage.UploadWithThumbnail(ctx, "images/photo.jpg", bytes.NewReader(imageData), 100)
	require.NoError(t, err)
	assert.NotEmpty(t, result.Key)
	assert.NotEmpty(t, result.ThumbnailKey)
	assert.Equal(t, int64(len(imageData)), result.Size)

	// Verify original was uploaded
	exists, err := setup.Storage.Exists(ctx, result.Key)
	require.NoError(t, err)
	assert.True(t, exists)

	// Verify thumbnail key has "-thumb" suffix
	assert.Contains(t, result.ThumbnailKey, "-thumb")
}

func TestS3Storage_Integration_EnsureBucket_AlreadyExists(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	// Call EnsureBucket again - bucket already exists
	created, err := setup.Storage.EnsureBucket(ctx)
	require.NoError(t, err)
	assert.False(t, created, "bucket already exists, should return false")
}

func TestS3Storage_Integration_HealthCheck(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	// Health check should succeed
	err := setup.Storage.HealthCheck(ctx)
	require.NoError(t, err)
}

func TestS3Storage_Integration_DownloadNonExistent(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	// Download non-existent file
	_, err := setup.Storage.Download(ctx, "nonexistent/file.txt")
	assert.Error(t, err)
}

func TestS3Storage_Integration_ConcurrentUploads(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	const numGoroutines = 10
	resultsChan := make(chan *UploadResult, numGoroutines)
	errsChan := make(chan error, numGoroutines)

	// Spawn concurrent uploads
	for i := 0; i < numGoroutines; i++ {
		go func(index int) {
			data := []byte("concurrent upload " + string(rune(index+48)))
			result, err := setup.Storage.Upload(ctx, "", bytes.NewReader(data), "text/plain")
			if err != nil {
				errsChan <- err
				return
			}
			resultsChan <- result
		}(i)
	}

	// Collect results
	uploadedKeys := make([]string, 0, numGoroutines)
	for i := 0; i < numGoroutines; i++ {
		select {
		case err := <-errsChan:
			t.Fatalf("upload error: %v", err)
		case result := <-resultsChan:
			uploadedKeys = append(uploadedKeys, result.Key)
		}
	}

	// Verify all were uploaded
	assert.Equal(t, numGoroutines, len(uploadedKeys))

	// Verify all exist
	for _, key := range uploadedKeys {
		exists, err := setup.Storage.Exists(ctx, key)
		require.NoError(t, err)
		assert.True(t, exists, "key should exist: %s", key)
	}

	// Cleanup
	err := setup.Storage.DeleteMultiple(ctx, uploadedKeys)
	require.NoError(t, err)
}

func TestS3Storage_Integration_ConcurrentDownloads(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	testData := []byte("shared test data")

	// Upload one file
	result, err := setup.Storage.Upload(ctx, "concurrent/shared.txt", bytes.NewReader(testData), "text/plain")
	require.NoError(t, err)

	const numGoroutines = 10
	resultsChan := make(chan []byte, numGoroutines)
	errsChan := make(chan error, numGoroutines)

	// Spawn concurrent downloads
	for i := 0; i < numGoroutines; i++ {
		go func() {
			reader, err := setup.Storage.Download(ctx, result.Key)
			if err != nil {
				errsChan <- err
				return
			}
			defer reader.Close()

			data, err := io.ReadAll(reader)
			if err != nil {
				errsChan <- err
				return
			}
			resultsChan <- data
		}()
	}

	// Collect results
	for i := 0; i < numGoroutines; i++ {
		select {
		case err := <-errsChan:
			t.Fatalf("download error: %v", err)
		case data := <-resultsChan:
			assert.Equal(t, testData, data)
		}
	}
}

func TestS3Storage_Integration_LargeFile(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	// Create large data (5 MB)
	largeData := make([]byte, 5*1024*1024)
	for i := range largeData {
		largeData[i] = byte(i % 256)
	}

	// Upload large file
	result, err := setup.Storage.Upload(ctx, "large/file.bin", bytes.NewReader(largeData), "application/octet-stream")
	require.NoError(t, err)
	assert.Equal(t, int64(len(largeData)), result.Size)

	// Download and verify
	reader, err := setup.Storage.Download(ctx, result.Key)
	require.NoError(t, err)
	defer reader.Close()

	downloaded, err := io.ReadAll(reader)
	require.NoError(t, err)
	assert.Equal(t, largeData, downloaded)

	// Cleanup
	err = setup.Storage.Delete(ctx, result.Key)
	require.NoError(t, err)
}

func TestS3Storage_Integration_MultipleContentTypes(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	testCases := []struct {
		name        string
		contentType string
		data        []byte
	}{
		{"text", "text/plain", []byte("plain text")},
		{"json", "application/json", []byte(`{"key": "value"}`)},
		{"html", "text/html", []byte("<html></html>")},
		{"binary", "application/octet-stream", []byte{0x00, 0x01, 0x02}},
	}

	uploadedKeys := make([]string, 0, len(testCases))

	for _, tc := range testCases {
		result, err := setup.Storage.Upload(ctx, "types/"+tc.name, bytes.NewReader(tc.data), tc.contentType)
		require.NoError(t, err)
		assert.Equal(t, tc.contentType, result.ContentType)
		uploadedKeys = append(uploadedKeys, result.Key)
	}

	// Cleanup
	err := setup.Storage.DeleteMultiple(ctx, uploadedKeys)
	require.NoError(t, err)
}

func TestS3Storage_Integration_UploadAndModify(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	ctx := context.Background()
	setup := setupMinIOContainer(ctx, t)
	defer setup.Cleanup(ctx, t)

	// Upload initial version
	initial := []byte("version 1")
	result1, err := setup.Storage.Upload(ctx, "modify-test/file.txt", bytes.NewReader(initial), "text/plain")
	require.NoError(t, err)

	// Verify initial content
	reader, err := setup.Storage.Download(ctx, result1.Key)
	require.NoError(t, err)
	data1, err := io.ReadAll(reader)
	reader.Close()
	require.NoError(t, err)
	assert.Equal(t, initial, data1)

	// Upload new version (overwrite same key)
	updated := []byte("version 2 - updated")
	result2, err := setup.Storage.Upload(ctx, result1.Key, bytes.NewReader(updated), "text/plain")
	require.NoError(t, err)
	assert.Equal(t, result1.Key, result2.Key)

	// Verify updated content
	reader, err = setup.Storage.Download(ctx, result2.Key)
	require.NoError(t, err)
	data2, err := io.ReadAll(reader)
	reader.Close()
	require.NoError(t, err)
	assert.Equal(t, updated, data2)

	// Cleanup
	err = setup.Storage.Delete(ctx, result2.Key)
	require.NoError(t, err)
}
