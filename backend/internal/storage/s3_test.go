package storage

import (
	"bytes"
	"context"
	"io"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// MockS3Client for testing
// Note: In production, use MinIO for local testing
// For unit tests, we'll test the logic without actual S3 calls

func TestNewS3Storage(t *testing.T) {
	for _, tt := range s3StorageTestCases() {
		t.Run(tt.name, func(t *testing.T) {
			storage, err := NewS3Storage(tt.cfg)

			if tt.wantErr {
				require.Error(t, err)
				assert.Nil(t, storage)
				assert.Contains(t, err.Error(), tt.errMsg)
			} else {
				require.NoError(t, err)
				assert.NotNil(t, storage)
				assert.Equal(t, tt.cfg.Bucket, storage.bucket)
				assert.Equal(t, tt.cfg.Endpoint, storage.endpoint)
			}
		})
	}
}

type s3StorageTestCase struct {
	name    string
	cfg     S3Config
	wantErr bool
	errMsg  string
}

func s3StorageTestCases() []s3StorageTestCase {
	return []s3StorageTestCase{
		{
			name: "valid config",
			cfg: S3Config{
				Endpoint:        "https://account.r2.cloudflarestorage.com",
				AccessKeyID:     "test-key",
				SecretAccessKey: "test-secret",
				Bucket:          "test-bucket",
				Region:          "auto",
			},
			wantErr: false,
		},
		{
			name: "missing endpoint",
			cfg: S3Config{
				AccessKeyID:     "test-key",
				SecretAccessKey: "test-secret",
				Bucket:          "test-bucket",
			},
			wantErr: true,
			errMsg:  "S3 endpoint is required",
		},
		{
			name: "missing access key",
			cfg: S3Config{
				Endpoint:        "https://account.r2.cloudflarestorage.com",
				SecretAccessKey: "test-secret",
				Bucket:          "test-bucket",
			},
			wantErr: true,
			errMsg:  "S3 access key ID is required",
		},
		{
			name: "missing secret key",
			cfg: S3Config{
				Endpoint:    "https://account.r2.cloudflarestorage.com",
				AccessKeyID: "test-key",
				Bucket:      "test-bucket",
			},
			wantErr: true,
			errMsg:  "S3 secret access key is required",
		},
		{
			name: "missing bucket",
			cfg: S3Config{
				Endpoint:        "https://account.r2.cloudflarestorage.com",
				AccessKeyID:     "test-key",
				SecretAccessKey: "test-secret",
			},
			wantErr: true,
			errMsg:  "S3 bucket name is required",
		},
	}
}

func TestGenerateKey(t *testing.T) {
	key1 := generateKey()
	key2 := generateKey()

	// Should generate non-empty keys
	assert.NotEmpty(t, key1)
	assert.NotEmpty(t, key2)

	// Keys should be different (due to UUID)
	assert.NotEqual(t, key1, key2)

	// Should contain date-based path
	assert.Contains(t, key1, "uploads/")
	assert.Contains(t, key1, time.Now().Format("2006/01/02"))
}

func TestAddSuffixBeforeExt(t *testing.T) {
	tests := []struct {
		filename string
		suffix   string
		expected string
	}{
		{
			filename: "image.jpg",
			suffix:   "-thumb",
			expected: "image-thumb.jpg",
		},
		{
			filename: "document.pdf",
			suffix:   "-archived",
			expected: "document-archived.pdf",
		},
		{
			filename: "file.tar.gz",
			suffix:   "-backup",
			expected: "file.tar-backup.gz",
		},
		{
			filename: "noext",
			suffix:   "-copy",
			expected: "noext-copy",
		},
	}

	for _, tt := range tests {
		t.Run(tt.filename, func(t *testing.T) {
			result := addSuffixBeforeExt(tt.filename, tt.suffix)
			assert.Equal(t, tt.expected, result)
		})
	}
}

// Integration tests (requires MinIO or real S3)
// These tests demonstrate the expected behavior

func TestS3StorageUploadDownloadFlow(t *testing.T) {
	// Skip if no S3 endpoint is configured
	t.Skip("Requires MinIO or S3 setup")

	ctx := context.Background()
	cfg := S3Config{
		Endpoint:        "http://localhost:9000",
		AccessKeyID:     "minioadmin",
		SecretAccessKey: "minioadmin",
		Bucket:          "test-bucket",
		Region:          "us-east-1",
	}

	storage, err := NewS3Storage(cfg)
	require.NoError(t, err)
	require.NotNil(t, storage)

	// Test upload
	testData := []byte("test file content")
	result, err := storage.Upload(ctx, "test/test.txt", bytes.NewReader(testData), "text/plain")
	require.NoError(t, err)
	require.NotNil(t, result)
	assert.Equal(t, "test/test.txt", result.Key)
	assert.Equal(t, int64(len(testData)), result.Size)
	assert.Equal(t, "text/plain", result.ContentType)

	// Test download
	downloadReader, err := storage.Download(ctx, result.Key)
	require.NoError(t, err)
	defer func() { require.NoError(t, downloadReader.Close()) }()

	downloadedData, err := io.ReadAll(downloadReader)
	require.NoError(t, err)
	assert.Equal(t, testData, downloadedData)

	// Test file exists
	exists, err := storage.Exists(ctx, result.Key)
	require.NoError(t, err)
	assert.True(t, exists)

	// Test presigned URLs
	downloadURL, err := storage.GeneratePresignedDownloadURL(ctx, result.Key, time.Hour)
	require.NoError(t, err)
	assert.NotEmpty(t, downloadURL.URL)
	assert.Equal(t, "GET", downloadURL.Method)

	uploadURL, err := storage.GeneratePresignedUploadURL(ctx, "presigned/test.txt", "text/plain", time.Hour)
	require.NoError(t, err)
	assert.NotEmpty(t, uploadURL.URL)
	assert.Equal(t, "PUT", uploadURL.Method)

	// Test delete
	err = storage.Delete(ctx, result.Key)
	require.NoError(t, err)

	exists, err = storage.Exists(ctx, result.Key)
	require.NoError(t, err)
	assert.False(t, exists)
}

func TestS3StorageErrors(t *testing.T) {
	// Skip if no S3 endpoint is configured
	t.Skip("Requires MinIO or S3 setup")

	ctx := context.Background()
	cfg := S3Config{
		Endpoint:        "http://localhost:9000",
		AccessKeyID:     "minioadmin",
		SecretAccessKey: "minioadmin",
		Bucket:          "test-bucket",
		Region:          "us-east-1",
	}

	storage, err := NewS3Storage(cfg)
	require.NoError(t, err)

	// Test error cases
	t.Run("upload with empty key", func(t *testing.T) {
		result, err := storage.Upload(ctx, "", bytes.NewReader([]byte("data")), "text/plain")
		require.NoError(t, err) // Should auto-generate key
		assert.NotEmpty(t, result.Key)
	})

	t.Run("download non-existent file", func(t *testing.T) {
		_, err := storage.Download(ctx, "non-existent/file.txt")
		require.Error(t, err)
	})

	t.Run("delete non-existent file", func(t *testing.T) {
		err := storage.Delete(ctx, "non-existent/file.txt")
		// Should not error even for non-existent files
		require.NoError(t, err)
	})

	t.Run("empty key for download", func(t *testing.T) {
		_, err := storage.Download(ctx, "")
		require.Error(t, err)
		assert.Contains(t, err.Error(), "key is required")
	})

	t.Run("empty key for delete", func(t *testing.T) {
		err := storage.Delete(ctx, "")
		require.Error(t, err)
		assert.Contains(t, err.Error(), "key is required")
	})

	t.Run("empty key for get size", func(t *testing.T) {
		_, err := storage.GetFileSize(ctx, "")
		require.Error(t, err)
		assert.Contains(t, err.Error(), "key is required")
	})
}

func TestS3StoragePresignedURLs(t *testing.T) {
	// Skip if no S3 endpoint is configured
	t.Skip("Requires MinIO or S3 setup")

	ctx := context.Background()
	cfg := S3Config{
		Endpoint:        "http://localhost:9000",
		AccessKeyID:     "minioadmin",
		SecretAccessKey: "minioadmin",
		Bucket:          "test-bucket",
		Region:          "us-east-1",
	}

	storage, err := NewS3Storage(cfg)
	require.NoError(t, err)

	t.Run("generate download URL with custom expiry", func(t *testing.T) {
		url, err := storage.GeneratePresignedDownloadURL(ctx, "test/file.txt", 2*time.Hour)
		require.NoError(t, err)
		assert.NotEmpty(t, url.URL)
		assert.Equal(t, "GET", url.Method)
		assert.True(t, url.ExpiresAt.After(time.Now()))
	})

	t.Run("generate download URL with default expiry", func(t *testing.T) {
		url, err := storage.GeneratePresignedDownloadURL(ctx, "test/file.txt", 0)
		require.NoError(t, err)
		assert.NotEmpty(t, url.URL)
		// Should default to 24 hours
		assert.True(t, url.ExpiresAt.After(time.Now().Add(23*time.Hour)))
	})

	t.Run("generate upload URL with auto-generated key", func(t *testing.T) {
		url, err := storage.GeneratePresignedUploadURL(ctx, "", "application/json", time.Hour)
		require.NoError(t, err)
		assert.NotEmpty(t, url.URL)
		assert.Equal(t, "PUT", url.Method)
	})

	t.Run("empty key for presigned URLs", func(t *testing.T) {
		url, err := storage.GeneratePresignedDownloadURL(ctx, "", time.Hour)
		require.Error(t, err)
		assert.Nil(t, url)
	})
}

func TestS3StorageMultipleOperations(t *testing.T) {
	// Skip if no S3 endpoint is configured
	t.Skip("Requires MinIO or S3 setup")

	ctx, storage := setupMinioStorage(t)

	t.Run("delete multiple files", func(t *testing.T) {
		// Upload multiple files
		keys := []string{}
		for i := 0; i < 3; i++ {
			result, err := storage.Upload(ctx, "", bytes.NewReader([]byte("test")), "text/plain")
			require.NoError(t, err)
			keys = append(keys, result.Key)
		}

		// Delete multiple files
		err := storage.DeleteMultiple(ctx, keys)
		require.NoError(t, err)

		// Verify deletion
		for _, key := range keys {
			exists, err := storage.Exists(ctx, key)
			require.NoError(t, err)
			assert.False(t, exists)
		}
	})

	t.Run("copy object", func(t *testing.T) {
		// Upload file
		result, err := storage.Upload(ctx, "copy-test/original.txt", bytes.NewReader([]byte("test content")), "text/plain")
		require.NoError(t, err)

		// Copy file
		err = storage.CopyObject(ctx, result.Key, "copy-test/copied.txt")
		require.NoError(t, err)

		// Verify copy exists
		exists, err := storage.Exists(ctx, "copy-test/copied.txt")
		require.NoError(t, err)
		assert.True(t, exists)

		// Cleanup
		require.NoError(t, storage.Delete(ctx, result.Key))
		require.NoError(t, storage.Delete(ctx, "copy-test/copied.txt"))
	})

	t.Run("list objects", func(t *testing.T) {
		// Upload files with common prefix
		prefix := "list-test/"
		for i := 0; i < 3; i++ {
			_, err := storage.Upload(ctx, prefix+"file"+string(rune('1'+i))+".txt", bytes.NewReader([]byte("test")), "text/plain")
			require.NoError(t, err)
		}

		// List objects
		keys, err := storage.ListObjects(ctx, prefix)
		require.NoError(t, err)
		assert.GreaterOrEqual(t, len(keys), 3)

		// Cleanup
		err = storage.DeleteMultiple(ctx, keys)
		require.NoError(t, err)
	})
}

func setupMinioStorage(t *testing.T) (context.Context, *S3Storage) {
	t.Helper()

	ctx := context.Background()
	cfg := S3Config{
		Endpoint:        "http://localhost:9000",
		AccessKeyID:     "minioadmin",
		SecretAccessKey: "minioadmin",
		Bucket:          "test-bucket",
		Region:          "us-east-1",
	}

	storage, err := NewS3Storage(cfg)
	require.NoError(t, err)

	return ctx, storage
}

func TestS3StorageValidation(t *testing.T) {
	t.Run("copy with missing source", func(t *testing.T) {
		storage := &S3Storage{bucket: "test"}
		err := storage.CopyObject(context.Background(), "", "dest")
		require.Error(t, err)
		assert.Contains(t, err.Error(), "both source and destination keys are required")
	})

	t.Run("copy with missing destination", func(t *testing.T) {
		storage := &S3Storage{bucket: "test"}
		err := storage.CopyObject(context.Background(), "source", "")
		require.Error(t, err)
		assert.Contains(t, err.Error(), "both source and destination keys are required")
	})

	t.Run("delete multiple with empty list", func(t *testing.T) {
		storage := &S3Storage{bucket: "test"}
		err := storage.DeleteMultiple(context.Background(), []string{})
		// Should handle gracefully
		require.NoError(t, err)
	})
}
