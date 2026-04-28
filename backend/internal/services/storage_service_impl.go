package services

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"log"
	"net/url"
	"path"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/feature/s3/manager"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/aws/aws-sdk-go-v2/service/s3/types"
)

const minBucketPathParts = 2

// s3ClientForStorage is the subset of S3 operations used by storageServiceImpl.
// Allows *s3.Client in production and mocks in tests.
type s3ClientForStorage interface {
	ListObjectsV2(ctx context.Context, params *s3.ListObjectsV2Input, optFns ...func(*s3.Options)) (*s3.ListObjectsV2Output, error)
	DeleteObject(ctx context.Context, params *s3.DeleteObjectInput, optFns ...func(*s3.Options)) (*s3.DeleteObjectOutput, error)
	HeadObject(ctx context.Context, params *s3.HeadObjectInput, optFns ...func(*s3.Options)) (*s3.HeadObjectOutput, error)
	CopyObject(ctx context.Context, params *s3.CopyObjectInput, optFns ...func(*s3.Options)) (*s3.CopyObjectOutput, error)
	DeleteObjects(ctx context.Context, params *s3.DeleteObjectsInput, optFns ...func(*s3.Options)) (*s3.DeleteObjectsOutput, error)
}

// storageServiceImpl implements StorageService
// Owns the S3 client exclusively and gates all S3/MinIO access
type storageServiceImpl struct {
	client        s3ClientForStorage
	realClient    *s3.Client // for presigning and uploader/downloader; same as client in production
	uploader      *manager.Uploader
	downloader    *manager.Downloader
	defaultBucket string
	region        string
	logger        *log.Logger
	endpoint      string
}

// NewStorageService creates a new StorageService instance
func NewStorageService(client *s3.Client, defaultBucket, region, endpoint string, logger *log.Logger) StorageService {
	return &storageServiceImpl{
		client:        client,
		realClient:    client,
		uploader:      manager.NewUploader(client),
		downloader:    manager.NewDownloader(client),
		defaultBucket: defaultBucket,
		region:        region,
		logger:        logger,
		endpoint:      endpoint,
	}
}

// UploadFile uploads a file to the specified bucket
func (s *storageServiceImpl) UploadFile(ctx context.Context, file []byte, bucket string, key string, contentType string) (string, error) {
	if len(file) == 0 {
		return "", errors.New("file data cannot be empty")
	}
	if key == "" {
		return "", errors.New("key cannot be empty")
	}

	// Use default bucket if not specified
	if bucket == "" {
		bucket = s.defaultBucket
	}

	// Validate bucket name
	if err := s.validateBucketName(bucket); err != nil {
		return "", fmt.Errorf("invalid bucket name: %w", err)
	}

	// Calculate content hash for integrity using SHA-256 (secure)
	hash := sha256.Sum256(file)
	contentHash := hex.EncodeToString(hash[:])

	// Set default content type if not provided
	if contentType == "" {
		contentType = "application/octet-stream"
	}

	// Upload to S3
	if s.uploader == nil {
		return "", errors.New("storage uploader not initialized")
	}
	result, err := s.uploader.Upload(ctx, &s3.PutObjectInput{
		Bucket:      aws.String(bucket),
		Key:         aws.String(key),
		Body:        bytes.NewReader(file),
		ContentType: aws.String(contentType),
		Metadata: map[string]string{
			"content-hash": contentHash,
			"uploaded-at":  time.Now().UTC().Format(time.RFC3339),
		},
	})
	if err != nil {
		s.logger.Printf("Failed to upload file %s to bucket %s: %v", key, bucket, err)
		return "", fmt.Errorf("upload failed: %w", err)
	}

	// Generate public URL
	publicURL := s.generatePublicURL(bucket, key)

	s.logger.Printf("Successfully uploaded file %s to bucket %s, ETag: %s", key, bucket, *result.ETag)
	return publicURL, nil
}

// DownloadFile retrieves a file from storage
func (s *storageServiceImpl) DownloadFile(ctx context.Context, urlOrKey string) ([]byte, error) {
	if urlOrKey == "" {
		return nil, errors.New("url or key cannot be empty")
	}

	bucket, key, err := s.parseURLOrKey(urlOrKey)
	if err != nil {
		return nil, fmt.Errorf("invalid url or key: %w", err)
	}

	// Download file to buffer
	buf := manager.NewWriteAtBuffer([]byte{})
	_, err = s.downloader.Download(ctx, buf, &s3.GetObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	})
	if err != nil {
		s.logger.Printf("Failed to download file %s from bucket %s: %v", key, bucket, err)
		return nil, fmt.Errorf("download failed: %w", err)
	}

	s.logger.Printf("Successfully downloaded file %s from bucket %s, size: %d bytes", key, bucket, len(buf.Bytes()))
	return buf.Bytes(), nil
}

// DeleteFile removes a file from storage
func (s *storageServiceImpl) DeleteFile(ctx context.Context, urlOrKey string) error {
	if urlOrKey == "" {
		return errors.New("url or key cannot be empty")
	}

	bucket, key, err := s.parseURLOrKey(urlOrKey)
	if err != nil {
		return fmt.Errorf("invalid url or key: %w", err)
	}

	_, err = s.client.DeleteObject(ctx, &s3.DeleteObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	})
	if err != nil {
		s.logger.Printf("Failed to delete file %s from bucket %s: %v", key, bucket, err)
		return fmt.Errorf("delete failed: %w", err)
	}

	s.logger.Printf("Successfully deleted file %s from bucket %s", key, bucket)
	return nil
}

// ListFiles returns all files in a bucket with optional prefix filter
func (s *storageServiceImpl) ListFiles(ctx context.Context, bucket string, prefix string) ([]FileInfo, error) {
	// Use default bucket if not specified
	if bucket == "" {
		bucket = s.defaultBucket
	}

	files := make([]FileInfo, 0) // Initialize as empty slice, not nil
	input := &s3.ListObjectsV2Input{
		Bucket: aws.String(bucket),
		Prefix: aws.String(prefix),
	}
	for {
		page, err := s.client.ListObjectsV2(ctx, input)
		if err != nil {
			s.logger.Printf("Failed to list files in bucket %s with prefix %s: %v", bucket, prefix, err)
			return nil, fmt.Errorf("list failed: %w", err)
		}
		for _, obj := range page.Contents {
			if obj.Key != nil {
				files = append(files, FileInfo{
					Key:          *obj.Key,
					Bucket:       bucket,
					Size:         safeInt64(obj.Size),
					ETag:         safeString(obj.ETag),
					LastModified: safeTime(obj.LastModified),
					URL:          s.generatePublicURL(bucket, *obj.Key),
				})
			}
		}
		if !aws.ToBool(page.IsTruncated) {
			break
		}
		input.ContinuationToken = page.NextContinuationToken
	}

	s.logger.Printf("Listed %d files in bucket %s with prefix '%s'", len(files), bucket, prefix)
	return files, nil
}

// GetFileMetadata retrieves metadata for a file without downloading content
func (s *storageServiceImpl) GetFileMetadata(ctx context.Context, urlOrKey string) (*FileInfo, error) {
	if urlOrKey == "" {
		return nil, errors.New("url or key cannot be empty")
	}

	bucket, key, err := s.parseURLOrKey(urlOrKey)
	if err != nil {
		return nil, fmt.Errorf("invalid url or key: %w", err)
	}

	result, err := s.client.HeadObject(ctx, &s3.HeadObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	})
	if err != nil {
		s.logger.Printf("Failed to get metadata for file %s in bucket %s: %v", key, bucket, err)
		return nil, fmt.Errorf("failed to get metadata: %w", err)
	}

	// Convert S3 metadata to map
	metadata := make(map[string]interface{})
	for k, v := range result.Metadata {
		metadata[k] = v
	}

	fileInfo := &FileInfo{
		Key:          key,
		Bucket:       bucket,
		Size:         safeInt64(result.ContentLength),
		ContentType:  safeString(result.ContentType),
		ETag:         safeString(result.ETag),
		LastModified: safeTime(result.LastModified),
		Metadata:     metadata,
		URL:          s.generatePublicURL(bucket, key),
	}

	s.logger.Printf("Retrieved metadata for file %s in bucket %s", key, bucket)
	return fileInfo, nil
}

// GeneratePresignedUploadURL creates a presigned URL for direct uploads
func (s *storageServiceImpl) GeneratePresignedUploadURL(
	ctx context.Context, bucket, key, contentType string, expiryMinutes int,
) (string, error) {
	if key == "" {
		return "", errors.New("key cannot be empty")
	}

	// Use default bucket if not specified
	if bucket == "" {
		bucket = s.defaultBucket
	}

	// Default expiry to 15 minutes
	if expiryMinutes <= 0 {
		expiryMinutes = 15
	}

	// Set default content type
	if contentType == "" {
		contentType = "application/octet-stream"
	}

	presigner := s3.NewPresignClient(s.realClient)
	presignResult, err := presigner.PresignPutObject(ctx, &s3.PutObjectInput{
		Bucket:      aws.String(bucket),
		Key:         aws.String(key),
		ContentType: aws.String(contentType),
	}, func(opts *s3.PresignOptions) {
		opts.Expires = time.Duration(expiryMinutes) * time.Minute
	})
	if err != nil {
		s.logger.Printf("Failed to generate presigned upload URL for %s: %v", key, err)
		return "", fmt.Errorf("presigned URL generation failed: %w", err)
	}

	s.logger.Printf("Generated presigned upload URL for %s, expires in %d minutes", key, expiryMinutes)
	return presignResult.URL, nil
}

// GeneratePresignedDownloadURL creates a presigned URL for direct downloads
func (s *storageServiceImpl) GeneratePresignedDownloadURL(ctx context.Context, urlOrKey string, expiryMinutes int) (string, error) {
	if urlOrKey == "" {
		return "", errors.New("url or key cannot be empty")
	}

	bucket, key, err := s.parseURLOrKey(urlOrKey)
	if err != nil {
		return "", fmt.Errorf("invalid url or key: %w", err)
	}

	// Default expiry to 60 minutes
	if expiryMinutes <= 0 {
		expiryMinutes = 60
	}

	presigner := s3.NewPresignClient(s.realClient)
	presignResult, err := presigner.PresignGetObject(ctx, &s3.GetObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	}, func(opts *s3.PresignOptions) {
		opts.Expires = time.Duration(expiryMinutes) * time.Minute
	})
	if err != nil {
		s.logger.Printf("Failed to generate presigned download URL for %s: %v", key, err)
		return "", fmt.Errorf("presigned URL generation failed: %w", err)
	}

	s.logger.Printf("Generated presigned download URL for %s, expires in %d minutes", key, expiryMinutes)
	return presignResult.URL, nil
}

// CopyFile copies a file within storage
func (s *storageServiceImpl) CopyFile(ctx context.Context, sourceURL string, destBucket string, destKey string) error {
	if sourceURL == "" {
		return errors.New("source url cannot be empty")
	}
	if destKey == "" {
		return errors.New("destination key cannot be empty")
	}

	sourceBucket, sourceKey, err := s.parseURLOrKey(sourceURL)
	if err != nil {
		return fmt.Errorf("invalid source url: %w", err)
	}

	// Use default bucket if destination not specified
	if destBucket == "" {
		destBucket = s.defaultBucket
	}

	copySource := sourceBucket + "/" + sourceKey
	_, err = s.client.CopyObject(ctx, &s3.CopyObjectInput{
		Bucket:     aws.String(destBucket),
		CopySource: aws.String(copySource),
		Key:        aws.String(destKey),
	})
	if err != nil {
		s.logger.Printf("Failed to copy file from %s to %s/%s: %v", copySource, destBucket, destKey, err)
		return fmt.Errorf("copy failed: %w", err)
	}

	s.logger.Printf("Successfully copied file from %s to %s/%s", copySource, destBucket, destKey)
	return nil
}

// FileExists checks if a file exists in storage
func (s *storageServiceImpl) FileExists(ctx context.Context, urlOrKey string) (bool, error) {
	if urlOrKey == "" {
		return false, errors.New("url or key cannot be empty")
	}

	bucket, key, err := s.parseURLOrKey(urlOrKey)
	if err != nil {
		return false, fmt.Errorf("invalid url or key: %w", err)
	}

	_, err = s.client.HeadObject(ctx, &s3.HeadObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	})
	if err != nil {
		// Check if it's a 404 Not Found error
		var noSuchKey *types.NoSuchKey
		var notFound *types.NotFound
		if errors.As(err, &noSuchKey) || errors.As(err, &notFound) {
			return false, nil
		}
		s.logger.Printf("Error checking if file exists %s/%s: %v", bucket, key, err)
		return false, fmt.Errorf("existence check failed: %w", err)
	}

	return true, nil
}

// DeleteMultiple removes multiple files in a single operation
func (s *storageServiceImpl) DeleteMultiple(ctx context.Context, urls []string) error {
	if len(urls) == 0 {
		return nil
	}

	// Group files by bucket
	bucketFiles := make(map[string][]string)
	for _, urlOrKey := range urls {
		bucket, key, err := s.parseURLOrKey(urlOrKey)
		if err != nil {
			s.logger.Printf("Skipping invalid URL during batch delete: %s", urlOrKey)
			continue
		}
		bucketFiles[bucket] = append(bucketFiles[bucket], key)
	}

	// Delete files per bucket
	var deleteErrors []error
	for bucket, keys := range bucketFiles {
		// Build object identifiers
		objects := make([]types.ObjectIdentifier, len(keys))
		for i, key := range keys {
			objects[i] = types.ObjectIdentifier{Key: aws.String(key)}
		}

		_, err := s.client.DeleteObjects(ctx, &s3.DeleteObjectsInput{
			Bucket: aws.String(bucket),
			Delete: &types.Delete{
				Objects: objects,
				Quiet:   aws.Bool(false),
			},
		})
		if err != nil {
			s.logger.Printf("Failed to delete batch of files from bucket %s: %v", bucket, err)
			deleteErrors = append(deleteErrors, fmt.Errorf("bucket %s: %w", bucket, err))
		} else {
			s.logger.Printf("Successfully deleted %d files from bucket %s", len(keys), bucket)
		}
	}

	if len(deleteErrors) > 0 {
		return fmt.Errorf("batch delete encountered errors: %v", deleteErrors)
	}

	return nil
}

// ============================================================================
// Helper Methods
// ============================================================================

// parseURLOrKey extracts bucket and key from a URL or returns key as-is
func (s *storageServiceImpl) parseURLOrKey(urlOrKey string) (bucket, key string, err error) {
	// Try parsing as URL first
	if strings.HasPrefix(urlOrKey, "http://") || strings.HasPrefix(urlOrKey, "https://") {
		parsedURL, parseErr := url.Parse(urlOrKey)
		if parseErr != nil {
			return "", "", fmt.Errorf("invalid URL: %w", parseErr)
		}

		// Extract bucket from host or path
		// Format: https://bucket.s3.region.amazonaws.com/key or https://endpoint/bucket/key
		pathParts := strings.Split(strings.TrimPrefix(parsedURL.Path, "/"), "/")

		// Check if bucket is in subdomain (AWS S3 style)
		switch {
		case strings.Contains(parsedURL.Host, "s3"):
			hostParts := strings.Split(parsedURL.Host, ".")
			if len(hostParts) > 0 {
				bucket = hostParts[0]
			}
			key = strings.TrimPrefix(parsedURL.Path, "/")
		case len(pathParts) >= minBucketPathParts:
			// MinIO/custom endpoint style: endpoint/bucket/key
			bucket = pathParts[0]
			key = path.Join(pathParts[1:]...)
		default:
			// Use default bucket
			bucket = s.defaultBucket
			key = strings.TrimPrefix(parsedURL.Path, "/")
		}
	} else {
		// Treat as key only, use default bucket
		bucket = s.defaultBucket
		key = urlOrKey
	}

	if bucket == "" {
		return "", "", errors.New("could not determine bucket")
	}
	if key == "" {
		return "", "", errors.New("could not determine key")
	}

	return bucket, key, nil
}

// generatePublicURL creates a public URL for a file
func (s *storageServiceImpl) generatePublicURL(bucket, key string) string {
	if s.endpoint != "" {
		// Custom endpoint (MinIO/R2)
		return strings.TrimSuffix(s.endpoint, "/") + "/" + bucket + "/" + key
	}
	// AWS S3 format
	return "https://" + bucket + ".s3." + s.region + ".amazonaws.com/" + key
}

// validateBucketName validates S3 bucket naming rules
func (s *storageServiceImpl) validateBucketName(bucket string) error {
	if bucket == "" {
		return errors.New("bucket name cannot be empty")
	}
	if len(bucket) < 3 || len(bucket) > 63 {
		return errors.New("bucket name must be between 3 and 63 characters")
	}
	// Basic validation - more comprehensive rules exist for production
	if strings.Contains(bucket, "..") || strings.HasPrefix(bucket, "-") || strings.HasSuffix(bucket, "-") {
		return errors.New("invalid bucket name format")
	}
	return nil
}

// ============================================================================
// Safe Helpers for Nullable Pointers
// ============================================================================

func safeString(s *string) string {
	if s == nil {
		return ""
	}
	return *s
}

func safeInt64(i *int64) int64 {
	if i == nil {
		return 0
	}
	return *i
}

func safeTime(t *time.Time) time.Time {
	if t == nil {
		return time.Time{}
	}
	return *t
}
