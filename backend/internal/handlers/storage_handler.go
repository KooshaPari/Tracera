package handlers

import (
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"strconv"
	"time"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/storage"
)

const (
	defaultPresignedURLExpiry = 1 * time.Hour
	uploadURLExpiry           = 15 * time.Minute

	// Content type constants
	contentTypeApplicationOctetStream = "application/octet-stream"
)

// StorageHandler handles storage-related HTTP requests
type StorageHandler struct {
	storageService storage.Provider
}

// NewStorageHandler creates a new storage handler
func NewStorageHandler(s storage.Provider) *StorageHandler {
	return &StorageHandler{
		storageService: s,
	}
}

// UploadRequest represents the upload request
type UploadRequest struct {
	Key         string `form:"key"`
	ContentType string `form:"contentType" json:"content_type"`
	File        []byte // Binary file data from form
}

// UploadResponse represents the upload response
type UploadResponse struct {
	Success      bool   `json:"success"`
	Key          string `json:"key"`
	URL          string `json:"url"`
	Size         int64  `json:"size"`
	ContentType  string `json:"content_type"`
	UploadedAt   string `json:"uploaded_at"`
	ThumbnailKey string `json:"thumbnail_key,omitempty"`
	Error        string `json:"error,omitempty"`
}

// DownloadResponse represents the download response
type DownloadResponse struct {
	Success bool        `json:"success"`
	Size    int64       `json:"size"`
	URL     string      `json:"url"`
	Error   string      `json:"error,omitempty"`
	Data    interface{} `json:"data,omitempty"`
}

// DeleteRequest represents the delete request
type DeleteRequest struct {
	Key string `json:"key"`
}

// DeleteResponse represents the delete response
type DeleteResponse struct {
	Success bool   `json:"success"`
	Key     string `json:"key"`
	Error   string `json:"error,omitempty"`
}

// PresignedURLRequest represents the presigned URL request
type PresignedURLRequest struct {
	Key         string `json:"key"`
	Method      string `json:"method"` // "GET" or "PUT"
	ExpiryHours int    `json:"expiry_hours"`
	ContentType string `json:"content_type"`
}

// PresignedURLResponse represents the presigned URL response
type PresignedURLResponse struct {
	Success   bool   `json:"success"`
	URL       string `json:"url"`
	ExpiresAt string `json:"expires_at"`
	Method    string `json:"method"`
	Error     string `json:"error,omitempty"`
}

// FileInfoResponse represents file information
type FileInfoResponse struct {
	Success bool   `json:"success"`
	Key     string `json:"key"`
	Size    int64  `json:"size"`
	Exists  bool   `json:"exists"`
	Error   string `json:"error,omitempty"`
}

// Upload handles file uploads
// @Summary Upload a file to S3 storage
// @Description Upload a file to S3-compatible storage (Cloudflare R2, AWS S3, etc.)
// @Tags storage
// @Accept multipart/form-data
// @Produce json
// @Param file formData file true "File to upload"
// @Param key formData string false "Custom S3 key (auto-generated if not provided)"
// @Param contentType formData string false "Content-Type header (auto-detected if not provided)"
// @Success 200 {object} UploadResponse
// @Failure 400 {object} UploadResponse
// @Failure 500 {object} UploadResponse
// @Router /storage/upload [post]
func uploadErrorResponse(c echo.Context, status int, msg string) error {
	return c.JSON(status, UploadResponse{
		Success:      false,
		Key:          "",
		URL:          "",
		Size:         0,
		ContentType:  "",
		UploadedAt:   "",
		ThumbnailKey: "",
		Error:        msg,
	})
}

// Upload handles file upload requests
func (h *StorageHandler) Upload(c echo.Context) error {
	ctx := c.Request().Context()

	// Parse multipart form
	form, err := c.MultipartForm()
	if err != nil {
		return uploadErrorResponse(c, http.StatusBadRequest, fmt.Sprintf("failed to parse form: %v", err))
	}

	// Get file
	files := form.File["file"]
	if len(files) == 0 {
		return uploadErrorResponse(c, http.StatusBadRequest, "no file provided")
	}

	fileHeader := files[0]

	// Open file
	file, err := fileHeader.Open()
	if err != nil {
		return uploadErrorResponse(c, http.StatusInternalServerError, fmt.Sprintf("failed to open file: %v", err))
	}
	defer func() {
		if err := file.Close(); err != nil {
			slog.Error("failed to close upload file", "error", err)
		}
	}()

	// Get optional parameters
	key := c.FormValue("key")
	contentType := c.FormValue("contentType")
	if contentType == "" {
		contentType = fileHeader.Header.Get("Content-Type")
		if contentType == "" {
			contentType = contentTypeApplicationOctetStream
		}
	}

	// Upload file using S3Storage (Upload accepts io.Reader)
	metadata, err := h.storageService.Upload(ctx, key, file, contentType)
	if err != nil {
		return uploadErrorResponse(c, http.StatusInternalServerError, fmt.Sprintf("failed to upload file: %v", err))
	}

	return c.JSON(http.StatusOK, UploadResponse{
		Success:      true,
		Key:          metadata.Key,
		URL:          metadata.URL,
		Size:         metadata.Size,
		ContentType:  metadata.ContentType,
		UploadedAt:   metadata.UploadedAt.Format(time.RFC3339),
		ThumbnailKey: "",
		Error:        "",
	})
}

// UploadWithThumbnail handles image uploads with thumbnail generation
// @Summary Upload an image with thumbnail generation
// @Description Upload an image and automatically generate a thumbnail
// @Tags storage
// @Accept multipart/form-data
// @Produce json
// @Param file formData file true "Image file to upload"
// @Param key formData string false "Custom S3 key (auto-generated if not provided)"
// @Param thumbWidth formData integer false "Thumbnail width in pixels (default: 200)"
// @Success 200 {object} UploadResponse
// @Failure 400 {object} UploadResponse
// @Failure 500 {object} UploadResponse
// @Router /storage/upload-with-thumbnail [post]
func (h *StorageHandler) UploadWithThumbnail(c echo.Context) error {
	ctx := c.Request().Context()

	// Parse multipart form
	form, err := c.MultipartForm()
	if err != nil {
		return c.JSON(http.StatusBadRequest, UploadResponse{
			Success:      false,
			Key:          "",
			URL:          "",
			Size:         0,
			ContentType:  "",
			UploadedAt:   "",
			ThumbnailKey: "",
			Error:        fmt.Sprintf("failed to parse form: %v", err),
		})
	}

	// Get file
	files := form.File["file"]
	if len(files) == 0 {
		return c.JSON(http.StatusBadRequest, UploadResponse{
			Success:      false,
			Key:          "",
			URL:          "",
			Size:         0,
			ContentType:  "",
			UploadedAt:   "",
			ThumbnailKey: "",
			Error:        "no file provided",
		})
	}

	fileHeader := files[0]

	// Open file
	file, err := fileHeader.Open()
	if err != nil {
		return c.JSON(http.StatusInternalServerError, UploadResponse{
			Success:      false,
			Key:          "",
			URL:          "",
			Size:         0,
			ContentType:  "",
			UploadedAt:   "",
			ThumbnailKey: "",
			Error:        fmt.Sprintf("failed to open file: %v", err),
		})
	}
	defer func() {
		if err := file.Close(); err != nil {
			slog.Error("failed to close upload file", "error", err)
		}
	}()

	// Get optional parameters
	key := c.FormValue("key")
	// Note: thumbWidth parameter ignored as StorageService doesn't support thumbnail generation
	// Thumbnail generation should be handled by a dedicated image processing service

	// Upload image using S3Storage (UploadWithThumbnail for images; thumbWidth 0 = default 200)
	metadata, err := h.storageService.UploadWithThumbnail(ctx, key, file, 0)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, UploadResponse{
			Success:      false,
			Key:          "",
			URL:          "",
			Size:         0,
			ContentType:  "",
			UploadedAt:   "",
			ThumbnailKey: "",
			Error:        fmt.Sprintf("failed to upload image: %v", err),
		})
	}

	return c.JSON(http.StatusOK, UploadResponse{
		Success:      true,
		Key:          metadata.Key,
		URL:          metadata.URL,
		Size:         metadata.Size,
		ContentType:  metadata.ContentType,
		UploadedAt:   metadata.UploadedAt.Format(time.RFC3339),
		ThumbnailKey: "",
		Error:        "",
	})
}

// Download downloads a file from storage
// @Summary Download a file from S3 storage
// @Description Download a file from S3-compatible storage
// @Tags storage
// @Produce octet-stream
// @Param key query string true "S3 key of the file to download"
// @Success 200 "File content"
// @Failure 400 {object} DownloadResponse
// @Failure 404 {object} DownloadResponse
// @Failure 500 {object} DownloadResponse
// @Router /storage/download [get]
func (h *StorageHandler) Download(c echo.Context) error {
	ctx := c.Request().Context()
	key := c.QueryParam("key")

	if key == "" {
		return c.JSON(http.StatusBadRequest, DownloadResponse{
			Success: false,
			Size:    0,
			URL:     "",
			Error:   "key is required",
			Data:    nil,
		})
	}

	// Check if file exists
	exists, err := h.storageService.Exists(ctx, key)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, DownloadResponse{
			Success: false,
			Size:    0,
			URL:     "",
			Error:   fmt.Sprintf("failed to check file: %v", err),
			Data:    nil,
		})
	}

	if !exists {
		return c.JSON(http.StatusNotFound, DownloadResponse{
			Success: false,
			Size:    0,
			URL:     "",
			Error:   "file not found",
			Data:    nil,
		})
	}

	// Download file (returns io.ReadCloser)
	rc, err := h.storageService.Download(ctx, key)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, DownloadResponse{
			Success: false,
			Size:    0,
			URL:     "",
			Error:   fmt.Sprintf("failed to download file: %v", err),
			Data:    nil,
		})
	}
	defer func() {
		if err := rc.Close(); err != nil {
			slog.Error("failed to close download reader", "error", err)
		}
	}()

	data, err := io.ReadAll(rc)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, DownloadResponse{
			Success: false,
			Size:    0,
			URL:     "",
			Error:   fmt.Sprintf("failed to read file: %v", err),
			Data:    nil,
		})
	}

	contentType := contentTypeApplicationOctetStream
	c.Response().Header().Set("Content-Length", strconv.Itoa(len(data)))
	c.Response().Header().Set("Content-Disposition", "attachment; filename="+key)
	c.Response().Header().Set("Content-Type", contentType)

	return c.Blob(http.StatusOK, contentType, data)
}

// Delete deletes a file from storage
// @Summary Delete a file from S3 storage
// @Description Delete a file from S3-compatible storage
// @Tags storage
// @Accept json
// @Produce json
// @Param key path string true "S3 key of the file to delete"
// @Success 200 {object} DeleteResponse
// @Failure 400 {object} DeleteResponse
// @Failure 500 {object} DeleteResponse
// @Router /storage/:key [delete]
func (h *StorageHandler) Delete(echoCtx echo.Context) error {
	ctx := echoCtx.Request().Context()
	key := echoCtx.Param("key")

	if key == "" {
		return echoCtx.JSON(http.StatusBadRequest, DeleteResponse{
			Success: false,
			Key:     "",
			Error:   "key is required",
		})
	}

	err := h.storageService.Delete(ctx, key)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, DeleteResponse{
			Success: false,
			Key:     key,
			Error:   fmt.Sprintf("failed to delete file: %v", err),
		})
	}

	return echoCtx.JSON(http.StatusOK, DeleteResponse{
		Success: true,
		Key:     key,
		Error:   "",
	})
}

// GetPresignedURL generates a presigned URL
// @Summary Generate presigned download URL
// @Description Generate a presigned URL for downloading a file without authentication
// @Tags storage
// @Accept json
// @Produce json
// @Param key path string true "S3 key of the file"
// @Param expiryHours query integer false "URL expiry in hours (default: 24)"
// @Success 200 {object} PresignedURLResponse
// @Failure 400 {object} PresignedURLResponse
// @Failure 500 {object} PresignedURLResponse
// @Router /storage/presigned/:key [get]
func (h *StorageHandler) GetPresignedURL(c echo.Context) error {
	ctx := c.Request().Context()
	key := c.Param("key")

	if key == "" {
		return c.JSON(http.StatusBadRequest, PresignedURLResponse{
			Success:   false,
			URL:       "",
			ExpiresAt: "",
			Method:    "",
			Error:     "key is required",
		})
	}

	expiry := defaultPresignedURLExpiry
	presigned, err := h.storageService.GeneratePresignedDownloadURL(ctx, key, expiry)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, PresignedURLResponse{
			Success:   false,
			URL:       "",
			ExpiresAt: "",
			Method:    "",
			Error:     fmt.Sprintf("failed to generate presigned URL: %v", err),
		})
	}

	return c.JSON(http.StatusOK, PresignedURLResponse{
		Success:   true,
		URL:       presigned.URL,
		ExpiresAt: presigned.ExpiresAt.Format(time.RFC3339),
		Method:    presigned.Method,
		Error:     "",
	})
}

// GenerateUploadPresignedURL generates a presigned URL for uploading
// @Summary Generate presigned upload URL
// @Description Generate a presigned URL for uploading a file without authentication
// @Tags storage
// @Accept json
// @Produce json
// @Param request body PresignedURLRequest true "Request body"
// @Success 200 {object} PresignedURLResponse
// @Failure 400 {object} PresignedURLResponse
// @Failure 500 {object} PresignedURLResponse
// @Router /storage/presigned-upload [post]
func (h *StorageHandler) GenerateUploadPresignedURL(c echo.Context) error {
	ctx := c.Request().Context()

	var req PresignedURLRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, PresignedURLResponse{
			Success:   false,
			URL:       "",
			ExpiresAt: "",
			Method:    "",
			Error:     fmt.Sprintf("invalid request: %v", err),
		})
	}

	expiry := uploadURLExpiry
	if req.ExpiryHours > 0 {
		expiry = time.Duration(req.ExpiryHours) * time.Hour
	}
	contentType := req.ContentType
	if contentType == "" {
		contentType = contentTypeApplicationOctetStream
	}

	presigned, err := h.storageService.GeneratePresignedUploadURL(ctx, req.Key, contentType, expiry)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, PresignedURLResponse{
			Success:   false,
			URL:       "",
			ExpiresAt: "",
			Method:    "",
			Error:     fmt.Sprintf("failed to generate presigned URL: %v", err),
		})
	}

	return c.JSON(http.StatusOK, PresignedURLResponse{
		Success:   true,
		URL:       presigned.URL,
		ExpiresAt: presigned.ExpiresAt.Format(time.RFC3339),
		Method:    presigned.Method,
		Error:     "",
	})
}

// GetFileInfo gets file information
// @Summary Get file information
// @Description Get metadata about a file in storage
// @Tags storage
// @Produce json
// @Param key query string true "S3 key of the file"
// @Success 200 {object} FileInfoResponse
// @Failure 400 {object} FileInfoResponse
// @Failure 500 {object} FileInfoResponse
// @Router /storage/info [get]
func (h *StorageHandler) GetFileInfo(c echo.Context) error {
	ctx := c.Request().Context()
	key := c.QueryParam("key")

	if key == "" {
		return c.JSON(http.StatusBadRequest, FileInfoResponse{
			Success: false,
			Key:     "",
			Size:    0,
			Exists:  false,
			Error:   "key is required",
		})
	}

	exists, err := h.storageService.Exists(ctx, key)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, FileInfoResponse{
			Success: false,
			Key:     "",
			Size:    0,
			Exists:  false,
			Error:   fmt.Sprintf("failed to check file: %v", err),
		})
	}

	var size int64
	if exists {
		size, err = h.storageService.GetFileSize(ctx, key)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, FileInfoResponse{
				Success: false,
				Key:     "",
				Size:    0,
				Exists:  false,
				Error:   fmt.Sprintf("failed to get file size: %v", err),
			})
		}
	}

	return c.JSON(http.StatusOK, FileInfoResponse{
		Success: true,
		Key:     key,
		Size:    size,
		Exists:  exists,
		Error:   "",
	})
}
