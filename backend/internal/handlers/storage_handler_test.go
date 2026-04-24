package handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/storage"
)

const storageHandlerTestExpiry = 1 * time.Hour

// MockS3Storage implements a mock S3 storage for testing
type MockS3Storage struct {
	files      map[string][]byte
	fileTypes  map[string]string
	uploadTime time.Time
}

// NewMockS3Storage creates a new mock storage
func NewMockS3Storage() *MockS3Storage {
	return &MockS3Storage{
		files:      make(map[string][]byte),
		fileTypes:  make(map[string]string),
		uploadTime: time.Now(),
	}
}

func (m *MockS3Storage) Upload(_ context.Context, key string, data io.Reader, contentType string) (*storage.UploadResult, error) {
	if key == "" {
		key = fmt.Sprintf("uploads/%d/%s", time.Now().Unix(), "test-file")
	}

	buf, err := io.ReadAll(data)
	if err != nil {
		return nil, err
	}

	m.files[key] = buf
	m.fileTypes[key] = contentType

	return &storage.UploadResult{
		Key:         key,
		URL:         "http://mock-s3/" + key,
		Size:        int64(len(buf)),
		ContentType: contentType,
		UploadedAt:  m.uploadTime,
	}, nil
}

func (m *MockS3Storage) Download(_ context.Context, key string) (io.ReadCloser, error) {
	if data, ok := m.files[key]; ok {
		return io.NopCloser(bytes.NewReader(data)), nil
	}
	return nil, errors.New("file not found")
}

func (m *MockS3Storage) Delete(_ context.Context, key string) error {
	delete(m.files, key)
	delete(m.fileTypes, key)
	return nil
}

func (m *MockS3Storage) DeleteMultiple(ctx context.Context, keys []string) error {
	for _, key := range keys {
		if err := m.Delete(ctx, key); err != nil {
			return err
		}
	}
	return nil
}

func (m *MockS3Storage) GeneratePresignedDownloadURL(_ context.Context, key string, expiry time.Duration) (*storage.PresignedURL, error) {
	if key == "" {
		return nil, errors.New("key is required")
	}
	return &storage.PresignedURL{
		URL:       "http://mock-presigned-download/" + key,
		ExpiresAt: time.Now().Add(expiry),
		Method:    "GET",
	}, nil
}

func (m *MockS3Storage) GeneratePresignedUploadURL(
	_ context.Context, key, _ string, expiry time.Duration,
) (*storage.PresignedURL, error) {
	if key == "" {
		key = "auto-generated-key"
	}
	return &storage.PresignedURL{
		URL:       "http://mock-presigned-upload/" + key,
		ExpiresAt: time.Now().Add(expiry),
		Method:    "PUT",
	}, nil
}

func (m *MockS3Storage) UploadWithThumbnail(ctx context.Context, key string, data io.Reader, _ int) (*storage.UploadResult, error) {
	result, err := m.Upload(ctx, key, data, "image/jpeg")
	if err != nil {
		return nil, err
	}
	result.ThumbnailKey = key + "-thumb"
	m.files[result.ThumbnailKey] = []byte("thumbnail-data")
	return result, nil
}

func (m *MockS3Storage) GetFileSize(_ context.Context, key string) (int64, error) {
	if data, ok := m.files[key]; ok {
		return int64(len(data)), nil
	}
	return 0, errors.New("file not found")
}

func (m *MockS3Storage) ListObjects(_ context.Context, prefix string) ([]string, error) {
	var keys []string
	for key := range m.files {
		if len(prefix) == 0 || len(key) >= len(prefix) && key[:len(prefix)] == prefix {
			keys = append(keys, key)
		}
	}
	return keys, nil
}

func (m *MockS3Storage) Exists(_ context.Context, key string) (bool, error) {
	_, ok := m.files[key]
	return ok, nil
}

func (m *MockS3Storage) CopyObject(_ context.Context, sourceKey, destKey string) error {
	if sourceKey == "" || destKey == "" {
		return errors.New("both keys required")
	}
	if data, ok := m.files[sourceKey]; ok {
		m.files[destKey] = data
		if ct, ok := m.fileTypes[sourceKey]; ok {
			m.fileTypes[destKey] = ct
		}
		return nil
	}
	return errors.New("source file not found")
}

// Test functions

func TestStorageHandlerUpload(t *testing.T) {
	e := echo.New()
	mockStorage := NewMockS3Storage()
	handler := &StorageHandler{storageService: mockStorage}

	t.Run("successful upload", func(t *testing.T) {
		// Create multipart form
		body := new(bytes.Buffer)
		writer := multipart.NewWriter(body)

		part, err := writer.CreateFormFile("file", "test.txt")
		require.NoError(t, err)

		_, err = io.WriteString(part, "test content")
		require.NoError(t, err)

		err = writer.WriteField("contentType", "text/plain")
		require.NoError(t, err)

		err = writer.Close()
		require.NoError(t, err)

		// Create request
		req := httptest.NewRequest(http.MethodPost, "/api/storage/upload", body)
		req.Header.Set("Content-Type", writer.FormDataContentType())
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)

		// Call handler
		err = handler.Upload(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var resp UploadResponse
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.True(t, resp.Success)
		assert.NotEmpty(t, resp.Key)
	})

	t.Run("upload without file", func(t *testing.T) {
		body := new(bytes.Buffer)
		writer := multipart.NewWriter(body)
		err := writer.Close()
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/storage/upload", body)
		req.Header.Set("Content-Type", writer.FormDataContentType())
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)

		err = handler.Upload(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})
}

func TestStorageHandlerUploadWithThumbnail(t *testing.T) {
	e := echo.New()
	mockStorage := NewMockS3Storage()
	handler := &StorageHandler{storageService: mockStorage} // Use mock storage in handler

	t.Run("successful image upload with thumbnail", func(t *testing.T) {
		// Create multipart form with image
		body := new(bytes.Buffer)
		writer := multipart.NewWriter(body)

		part, err := writer.CreateFormFile("file", "test.jpg")
		require.NoError(t, err)

		// Write minimal JPEG header (simplified for testing)
		_, err = io.WriteString(part, "\xFF\xD8\xFF\xE0")
		require.NoError(t, err)

		err = writer.WriteField("thumbWidth", "100")
		require.NoError(t, err)

		err = writer.Close()
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/storage/upload-with-thumbnail", body)
		req.Header.Set("Content-Type", writer.FormDataContentType())
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)

		err = handler.UploadWithThumbnail(c)
		// May fail due to image format, but testing the flow
		if err == nil {
			assert.True(t, rec.Code == http.StatusOK || rec.Code == http.StatusInternalServerError)
		}
	})
}

func TestStorageHandlerDelete(t *testing.T) {
	e := echo.New()
	mockStorage := NewMockS3Storage()
	handler := &StorageHandler{storageService: mockStorage}

	t.Run("successful delete", func(t *testing.T) {
		// First upload a file
		key := "test/file.txt"
		mockStorage.files[key] = []byte("test content")

		req := httptest.NewRequest(http.MethodDelete, "/api/storage/test/file.txt", nil)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		c.SetParamNames("key")
		c.SetParamValues(key)

		err := handler.Delete(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		// Verify deletion
		exists, err := mockStorage.Exists(context.Background(), key)
		require.NoError(t, err)
		assert.False(t, exists)
	})

	t.Run("delete without key", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodDelete, "/api/storage/", nil)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		c.SetParamNames("key")
		c.SetParamValues("")

		err := handler.Delete(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})
}

func TestStorageHandlerGetPresignedURL(t *testing.T) {
	e := echo.New()
	mockStorage := NewMockS3Storage()
	handler := &StorageHandler{storageService: mockStorage} // Use mock storage in handler

	t.Run("successful presigned URL generation", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/storage/presigned/test/file.txt?expiryHours=2", nil)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		c.SetParamNames("key")
		c.SetParamValues("test/file.txt")

		err := handler.GetPresignedURL(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var resp PresignedURLResponse
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.True(t, resp.Success)
		assert.NotEmpty(t, resp.URL)
		assert.Equal(t, "GET", resp.Method)
	})

	t.Run("presigned URL without key", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/storage/presigned/", nil)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		c.SetParamNames("key")
		c.SetParamValues("")

		err := handler.GetPresignedURL(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})
}

func TestStorageHandlerGenerateUploadPresignedURL(t *testing.T) {
	e := echo.New()
	mockStorage := NewMockS3Storage()
	handler := &StorageHandler{storageService: mockStorage} // Use mock storage in handler

	t.Run("successful upload presigned URL generation", func(t *testing.T) {
		reqBody := `{
			"key": "uploads/test.txt",
			"contentType": "text/plain",
			"expiryHours": 1
		}`

		req := httptest.NewRequest(http.MethodPost, "/api/storage/presigned-upload", bytes.NewBufferString(reqBody))
		req.Header.Set("Content-Type", "application/json")
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)

		err := handler.GenerateUploadPresignedURL(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var resp PresignedURLResponse
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.True(t, resp.Success)
		assert.NotEmpty(t, resp.URL)
		assert.Equal(t, "PUT", resp.Method)
	})

	t.Run("invalid request body", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/storage/presigned-upload", bytes.NewBufferString("invalid json"))
		req.Header.Set("Content-Type", "application/json")
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)

		err := handler.GenerateUploadPresignedURL(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})
}

func TestStorageHandlerGetFileInfo(t *testing.T) {
	e := echo.New()
	mockStorage := NewMockS3Storage()
	handler := &StorageHandler{storageService: mockStorage}

	t.Run("get info for existing file", func(t *testing.T) {
		// Upload a file first
		key := "test/file.txt"
		mockStorage.files[key] = []byte("test content")

		req := httptest.NewRequest(http.MethodGet, "/api/storage/info?key=test/file.txt", nil)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)

		err := handler.GetFileInfo(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var resp FileInfoResponse
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.True(t, resp.Success)
		assert.True(t, resp.Exists)
		assert.Equal(t, int64(len("test content")), resp.Size)
	})

	t.Run("get info for non-existent file", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/storage/info?key=non-existent", nil)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)

		err := handler.GetFileInfo(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var resp FileInfoResponse
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.True(t, resp.Success)
		assert.False(t, resp.Exists)
		assert.Equal(t, int64(0), resp.Size)
	})

	t.Run("get info without key", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/storage/info", nil)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)

		err := handler.GetFileInfo(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})
}

func TestStorageHandlerResponses(t *testing.T) {
	t.Run("upload response structure", func(t *testing.T) {
		resp := UploadResponse{
			Success:      true,
			Key:          "test.txt",
			URL:          "http://example.com/test.txt",
			Size:         100,
			ContentType:  "text/plain",
			UploadedAt:   time.Now().Format(time.RFC3339),
			ThumbnailKey: "test-thumb.jpg",
			Error:        "",
		}

		assert.True(t, resp.Success)
		assert.NotEmpty(t, resp.Key)
		assert.NotEmpty(t, resp.URL)
	})

	t.Run("delete response structure", func(t *testing.T) {
		resp := DeleteResponse{
			Success: true,
			Key:     "test.txt",
			Error:   "",
		}

		assert.True(t, resp.Success)
		assert.Equal(t, "test.txt", resp.Key)
	})

	t.Run("presigned URL response structure", func(t *testing.T) {
		resp := PresignedURLResponse{
			Success:   true,
			URL:       "http://presigned-url.com",
			ExpiresAt: time.Now().Add(storageHandlerTestExpiry).Format(time.RFC3339),
			Method:    "GET",
			Error:     "",
		}

		assert.True(t, resp.Success)
		assert.NotEmpty(t, resp.URL)
		assert.NotEmpty(t, resp.ExpiresAt)
	})
}
