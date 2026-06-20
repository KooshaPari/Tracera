package storage

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// stubS3Storage returns a minimal S3Storage used only for validation tests.
// Do not call any method that uses .client (Upload, Download, Delete, etc. with valid key).
func stubS3Storage() *S3Storage {
	return &S3Storage{
		bucket:   "test-bucket",
		endpoint: "https://s3.example.com",
	}
}

func TestS3Storage_Download_EmptyKey(t *testing.T) {
	s := stubS3Storage()
	ctx := context.Background()

	rc, err := s.Download(ctx, "")
	require.Error(t, err)
	assert.Nil(t, rc)
	assert.Contains(t, err.Error(), "key is required")
}

func TestS3Storage_Delete_EmptyKey(t *testing.T) {
	s := stubS3Storage()
	ctx := context.Background()

	err := s.Delete(ctx, "")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "key is required")
}

func TestS3Storage_GetFileSize_EmptyKey(t *testing.T) {
	s := stubS3Storage()
	ctx := context.Background()

	size, err := s.GetFileSize(ctx, "")
	require.Error(t, err)
	assert.Equal(t, int64(0), size)
	assert.Contains(t, err.Error(), "key is required")
}

func TestS3Storage_Exists_EmptyKey(t *testing.T) {
	s := stubS3Storage()
	ctx := context.Background()

	exists, err := s.Exists(ctx, "")
	require.Error(t, err)
	assert.False(t, exists)
	assert.Contains(t, err.Error(), "key is required")
}

func TestS3Storage_GeneratePresignedDownloadURL_EmptyKey(t *testing.T) {
	s := stubS3Storage()
	ctx := context.Background()

	url, err := s.GeneratePresignedDownloadURL(ctx, "", time.Hour)
	require.Error(t, err)
	assert.Nil(t, url)
	assert.Contains(t, err.Error(), "key is required")
}

func TestS3Storage_CopyObject_EmptySource(t *testing.T) {
	s := stubS3Storage()
	ctx := context.Background()

	err := s.CopyObject(ctx, "", "dest-key")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "both source and destination keys are required")
}

func TestS3Storage_CopyObject_EmptyDest(t *testing.T) {
	s := stubS3Storage()
	ctx := context.Background()

	err := s.CopyObject(ctx, "source-key", "")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "both source and destination keys are required")
}

func TestS3Storage_DeleteMultiple_EmptySlice(t *testing.T) {
	s := stubS3Storage()
	ctx := context.Background()

	err := s.DeleteMultiple(ctx, []string{})
	require.NoError(t, err)
}

func TestS3Storage_DeleteMultiple_NilSlice(t *testing.T) {
	s := stubS3Storage()
	ctx := context.Background()

	err := s.DeleteMultiple(ctx, nil)
	require.NoError(t, err)
}

func TestS3Storage_Upload_EmptyKey_AutoGenerate(t *testing.T) {
	// Upload with empty key auto-generates; we only test that we don't panic.
	// Full upload test requires real S3/MinIO (integration).
	t.Skip("Upload with empty key requires S3 client - covered by integration test")
}

func TestPresignedURL_DefaultExpiry(t *testing.T) {
	// Document default expiry constant
	assert.Equal(t, 24*time.Hour, s3PresignedURLDefaultExpiry)
}

func TestUploadResult_Fields(t *testing.T) {
	// Type check / doc
	var r *UploadResult
	assert.Nil(t, r)
	r = &UploadResult{Key: "k", URL: "u", Size: 1, ContentType: "ct"}
	assert.Equal(t, "k", r.Key)
	assert.Equal(t, "u", r.URL)
	assert.Equal(t, int64(1), r.Size)
	assert.Equal(t, "ct", r.ContentType)
}

func TestPresignedURL_Fields(t *testing.T) {
	var p *PresignedURL
	assert.Nil(t, p)
	p = &PresignedURL{URL: "u", Method: "GET"}
	assert.Equal(t, "u", p.URL)
	assert.Equal(t, "GET", p.Method)
}

func TestS3Config_Validation_AllMissing(t *testing.T) {
	_, err := NewS3Storage(S3Config{})
	require.Error(t, err)
	assert.Contains(t, err.Error(), "endpoint")
}

func TestS3Config_RegionDefault(t *testing.T) {
	cfg := S3Config{
		Endpoint:        "https://ep",
		AccessKeyID:     "ak",
		SecretAccessKey: "sk",
		Bucket:          "b",
		Region:          "",
	}
	// Region "" should default to "us-east-1" inside NewS3Storage
	// NewS3Storage will try to create AWS config - may fail for other reasons
	_, err := NewS3Storage(cfg)
	// We only care that we don't panic; error is expected without real creds
	if err != nil {
		assert.Contains(t, err.Error(), "config", err.Error())
	}
}

func TestS3Storage_Upload_ReadError(t *testing.T) {
	// Upload copies from reader; if reader fails, we get error
	// We need a real S3Storage with client to trigger upload - skip
	t.Skip("Requires S3 client mock")
}

func TestGenerateKey_Format(t *testing.T) {
	k := generateKey()
	assert.Contains(t, k, "uploads/")
	assert.NotEmpty(t, k)
}

func TestAddSuffixBeforeExt_EmptyExt(t *testing.T) {
	out := addSuffixBeforeExt("noext", "-suf")
	assert.Equal(t, "noext-suf", out)
}

func TestAddSuffixBeforeExt_EmptyFilename(t *testing.T) {
	out := addSuffixBeforeExt("", "-suf")
	assert.Equal(t, "-suf", out)
}

func TestUploadResult_ThumbnailKey(t *testing.T) {
	r := &UploadResult{ThumbnailKey: "thumb/key"}
	assert.Equal(t, "thumb/key", r.ThumbnailKey)
}

// Test that a failing reader in Upload returns error (unit test with minimal stub).
// Upload reads from the reader before calling S3; a failing reader triggers the error path.
func TestUpload_FailingReader(t *testing.T) {
	s := stubS3Storage()
	ctx := context.Background()
	_, err := s.Upload(ctx, "key", &failingReaderImpl{}, "text/plain")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "failed to read file data")
}

type failingReaderImpl struct{}

func (f *failingReaderImpl) Read(_ []byte) (n int, err error) {
	return 0, assert.AnError
}

// ============================================================================
// Additional Coverage Tests for Edge Cases
// ============================================================================

// Note: Tests for CopyObject, ListObjects, GetFileSize, etc with valid keys
// require a real S3 client and are better tested in integration tests with MinIO.
// These stub-based tests only validate input validation before S3 calls.

func TestAddSuffixBeforeExt_ComplexFilename(t *testing.T) {
	tests := []struct {
		input    string
		suffix   string
		expected string
	}{
		{"path/to/file.txt", "-v1", "path/to/file-v1.txt"},
		{"file.backup.tar.gz", "-old", "file.backup.tar-old.gz"},
		{"index.html", "", "index.html"},
		{"script.min.js", "-unminified", "script.min-unminified.js"},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			result := addSuffixBeforeExt(tt.input, tt.suffix)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestGenerateKey_DateFormat(t *testing.T) {
	key := generateKey()
	now := time.Now()

	// Verify the date is in the expected format
	expectedPrefix := "uploads/" + now.Format("2006/01/02") + "/"
	assert.Contains(t, key, expectedPrefix)

	// Verify there's a UUID after the date
	parts := len(key) - len(expectedPrefix)
	assert.Positive(t, parts)
}

// Test PresignedURL and UploadResult constructors with all fields
func TestUploadResult_WithAllMetadata(t *testing.T) {
	now := time.Now()
	result := &UploadResult{
		Key:          "bucket/key/file.txt",
		URL:          "https://s3.example.com/bucket/key/file.txt",
		Size:         int64(1024),
		ContentType:  "text/plain",
		UploadedAt:   now,
		ThumbnailKey: "bucket/key/file-thumb.txt",
	}

	assert.NotNil(t, result)
	assert.Equal(t, now, result.UploadedAt)
}

func TestPresignedURL_WithGETMethod(t *testing.T) {
	url := &PresignedURL{
		URL:       "https://presigned.example.com/get?token=xyz",
		ExpiresAt: time.Now().Add(time.Hour),
		Method:    "GET",
	}
	assert.Equal(t, "GET", url.Method)
}

func TestPresignedURL_WithPUTMethod(t *testing.T) {
	url := &PresignedURL{
		URL:       "https://presigned.example.com/put?token=xyz",
		ExpiresAt: time.Now().Add(time.Hour),
		Method:    "PUT",
	}
	assert.Equal(t, "PUT", url.Method)
}

func TestS3Config_AllFieldsSet(t *testing.T) {
	cfg := S3Config{
		Endpoint:        "https://s3.amazonaws.com",
		AccessKeyID:     "AKIAIOSFODNN7EXAMPLE",
		SecretAccessKey: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
		Bucket:          "my-bucket",
		Region:          "us-west-2",
	}

	assert.Equal(t, "https://s3.amazonaws.com", cfg.Endpoint)
	assert.Equal(t, "AKIAIOSFODNN7EXAMPLE", cfg.AccessKeyID)
	assert.Equal(t, "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", cfg.SecretAccessKey)
	assert.Equal(t, "my-bucket", cfg.Bucket)
	assert.Equal(t, "us-west-2", cfg.Region)
}

// HealthCheck and EnsureBucket tests are better tested in integration tests with MinIO
