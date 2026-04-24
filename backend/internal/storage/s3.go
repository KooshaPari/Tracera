// Package storage provides S3-compatible storage operations (e.g. AWS S3, Cloudflare R2).
// Package storage provides S3-backed storage helpers.
package storage

import (
	"bytes"
	"context"
	"errors"
	"fmt"
	"io"
	"path/filepath"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/credentials"
	"github.com/aws/aws-sdk-go-v2/feature/s3/manager"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/aws/aws-sdk-go-v2/service/s3/types"
	"github.com/aws/smithy-go"
	"github.com/google/uuid"
)

const (
	s3PresignedURLDefaultExpiry = 24 * time.Hour
)

// Provider defines the interface for storage operations
type Provider interface {
	Upload(ctx context.Context, key string, data io.Reader, contentType string) (*UploadResult, error)
	Download(ctx context.Context, key string) (io.ReadCloser, error)
	Delete(ctx context.Context, key string) error
	DeleteMultiple(ctx context.Context, keys []string) error
	GeneratePresignedDownloadURL(ctx context.Context, key string, expiry time.Duration) (*PresignedURL, error)
	GeneratePresignedUploadURL(ctx context.Context, key string, contentType string, expiry time.Duration) (*PresignedURL, error)
	UploadWithThumbnail(ctx context.Context, key string, data io.Reader, thumbWidth int) (*UploadResult, error)
	GetFileSize(ctx context.Context, key string) (int64, error)
	ListObjects(ctx context.Context, prefix string) ([]string, error)
	Exists(ctx context.Context, key string) (bool, error)
	CopyObject(ctx context.Context, sourceKey, destKey string) error
}

// S3Storage provides S3-compatible storage operations
type S3Storage struct {
	client     *s3.Client
	bucket     string
	endpoint   string
	region     string
	uploader   *manager.Uploader
	downloader *manager.Downloader
}

// S3Config holds S3 configuration
type S3Config struct {
	Endpoint        string // S3 endpoint URL (e.g., https://account.r2.cloudflarestorage.com)
	AccessKeyID     string // AWS Access Key ID
	SecretAccessKey string // AWS Secret Access Key
	Bucket          string // S3 bucket name
	Region          string // AWS region or "auto" for R2
}

// UploadResult contains information about an uploaded file
type UploadResult struct {
	Key          string
	URL          string
	Size         int64
	ContentType  string
	UploadedAt   time.Time
	ThumbnailKey string
}

// PresignedURL contains information about a presigned URL
type PresignedURL struct {
	URL       string
	ExpiresAt time.Time
	Method    string
}

// NewS3Storage initializes a new S3 storage service
func NewS3Storage(cfg S3Config) (*S3Storage, error) {
	if cfg.Endpoint == "" {
		return nil, errors.New("S3 endpoint is required")
	}
	if cfg.AccessKeyID == "" {
		return nil, errors.New("S3 access key ID is required")
	}
	if cfg.SecretAccessKey == "" {
		return nil, errors.New("S3 secret access key is required")
	}
	if cfg.Bucket == "" {
		return nil, errors.New("S3 bucket name is required")
	}

	// Validate region (allow "auto" for Cloudflare R2)
	region := cfg.Region
	if region == "" {
		region = "us-east-1" // Default to us-east-1 for AWS
	}

	// Create AWS SDK config with credentials
	sdkConfig, err := config.LoadDefaultConfig(context.Background(),
		config.WithRegion(region),
		config.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(
			cfg.AccessKeyID,
			cfg.SecretAccessKey,
			"", // session token
		)),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to load AWS SDK config: %w", err)
	}

	// Create S3 client
	client := s3.NewFromConfig(sdkConfig, func(options *s3.Options) {
		options.BaseEndpoint = aws.String(cfg.Endpoint)
	})

	return &S3Storage{
		client:     client,
		bucket:     cfg.Bucket,
		endpoint:   cfg.Endpoint,
		region:     region,
		uploader:   manager.NewUploader(client),
		downloader: manager.NewDownloader(client),
	}, nil
}

// Upload uploads a file to S3
func (s *S3Storage) Upload(ctx context.Context, key string, data io.Reader, contentType string) (*UploadResult, error) {
	if key == "" {
		key = generateKey()
	}

	// Read data into buffer to get size
	buf := new(bytes.Buffer)
	if _, err := io.Copy(buf, data); err != nil {
		return nil, fmt.Errorf("failed to read file data: %w", err)
	}

	// Upload to S3
	_, uploadErr := s.uploader.Upload(ctx, &s3.PutObjectInput{
		Bucket:      aws.String(s.bucket),
		Key:         aws.String(key),
		Body:        bytes.NewReader(buf.Bytes()),
		ContentType: aws.String(contentType),
	})
	if uploadErr != nil {
		return nil, fmt.Errorf("failed to upload file to S3: %w", uploadErr)
	}

	return &UploadResult{
		Key:         key,
		URL:         fmt.Sprintf("%s/%s/%s", s.endpoint, s.bucket, key),
		Size:        int64(buf.Len()),
		ContentType: contentType,
		UploadedAt:  time.Now(),
	}, nil
}

// EnsureBucket creates the bucket if it does not exist.
// Returns true when the bucket was created in this call.
func (s *S3Storage) EnsureBucket(ctx context.Context) (bool, error) {
	_, err := s.client.CreateBucket(ctx, &s3.CreateBucketInput{Bucket: aws.String(s.bucket)})
	if err == nil {
		return true, nil
	}

	var alreadyOwned *types.BucketAlreadyOwnedByYou
	var alreadyExists *types.BucketAlreadyExists
	if errors.As(err, &alreadyOwned) || errors.As(err, &alreadyExists) {
		return false, nil
	}

	_, headErr := s.client.HeadBucket(ctx, &s3.HeadBucketInput{Bucket: aws.String(s.bucket)})
	if headErr == nil {
		return false, nil
	}

	return false, fmt.Errorf("create bucket: %w", err)
}

// Download downloads a file from S3
func (s *S3Storage) Download(ctx context.Context, key string) (io.ReadCloser, error) {
	if key == "" {
		return nil, errors.New("key is required")
	}

	// Use GetObject to get a ReadCloser
	result, err := s.client.GetObject(ctx, &s3.GetObjectInput{
		Bucket: aws.String(s.bucket),
		Key:    aws.String(key),
	})
	if err != nil {
		return nil, fmt.Errorf("failed to download file from S3: %w", err)
	}

	return result.Body, nil
}

// Delete deletes a file from S3
func (s *S3Storage) Delete(ctx context.Context, key string) error {
	if key == "" {
		return errors.New("key is required")
	}

	_, err := s.client.DeleteObject(ctx, &s3.DeleteObjectInput{
		Bucket: aws.String(s.bucket),
		Key:    aws.String(key),
	})
	if err != nil {
		return fmt.Errorf("failed to delete file from S3: %w", err)
	}

	return nil
}

// DeleteMultiple deletes multiple files from S3
func (s *S3Storage) DeleteMultiple(ctx context.Context, keys []string) error {
	if len(keys) == 0 {
		return nil
	}

	// Build object identifiers
	objects := make([]types.ObjectIdentifier, len(keys))
	for i, key := range keys {
		objects[i] = types.ObjectIdentifier{Key: aws.String(key)}
	}

	_, err := s.client.DeleteObjects(ctx, &s3.DeleteObjectsInput{
		Bucket: aws.String(s.bucket),
		Delete: &types.Delete{
			Objects: objects,
		},
	})
	if err != nil {
		return fmt.Errorf("failed to delete files from S3: %w", err)
	}

	return nil
}

// GeneratePresignedDownloadURL generates a presigned URL for downloading a file
func (s *S3Storage) GeneratePresignedDownloadURL(ctx context.Context, key string, expiry time.Duration) (*PresignedURL, error) {
	if key == "" {
		return nil, errors.New("key is required")
	}

	if expiry == 0 {
		expiry = s3PresignedURLDefaultExpiry
	}

	presigner := s3.NewPresignClient(s.client)
	presignedRequest, err := presigner.PresignGetObject(ctx, &s3.GetObjectInput{
		Bucket: aws.String(s.bucket),
		Key:    aws.String(key),
	}, func(opts *s3.PresignOptions) {
		opts.Expires = expiry
	})
	if err != nil {
		return nil, fmt.Errorf("failed to generate presigned download URL: %w", err)
	}

	return &PresignedURL{
		URL:       presignedRequest.URL,
		ExpiresAt: time.Now().Add(expiry),
		Method:    "GET",
	}, nil
}

// GeneratePresignedUploadURL generates a presigned URL for uploading a file
func (s *S3Storage) GeneratePresignedUploadURL(
	ctx context.Context, key, contentType string, expiry time.Duration,
) (*PresignedURL, error) {
	if key == "" {
		key = generateKey()
	}

	if expiry == 0 {
		expiry = s3PresignedURLDefaultExpiry
	}

	presigner := s3.NewPresignClient(s.client)
	presignedRequest, err := presigner.PresignPutObject(ctx, &s3.PutObjectInput{
		Bucket:      aws.String(s.bucket),
		Key:         aws.String(key),
		ContentType: aws.String(contentType),
	}, func(opts *s3.PresignOptions) {
		opts.Expires = expiry
	})
	if err != nil {
		return nil, fmt.Errorf("failed to generate presigned upload URL: %w", err)
	}

	return &PresignedURL{
		URL:       presignedRequest.URL,
		ExpiresAt: time.Now().Add(expiry),
		Method:    "PUT",
	}, nil
}

// UploadWithThumbnail uploads an image and generates a thumbnail reference
// Note: For production thumbnail generation, consider using a dedicated image processing service
// or cloud provider's image transformation APIs (e.g., Cloudflare Image Resizing)
func (s *S3Storage) UploadWithThumbnail(ctx context.Context, key string, data io.Reader, _ int) (*UploadResult, error) {
	if key == "" {
		key = generateKey()
	}

	// Read image data
	imageData, err := io.ReadAll(data)
	if err != nil {
		return nil, fmt.Errorf("failed to read image data: %w", err)
	}

	// Upload original image
	originalResult, err := s.Upload(ctx, key, bytes.NewReader(imageData), "image/jpeg")
	if err != nil {
		return nil, fmt.Errorf("failed to upload original image: %w", err)
	}

	// Create thumbnail key reference
	// In production, use Cloudflare Image Resizing or similar service for actual thumbnail generation
	thumbKey := addSuffixBeforeExt(key, "-thumb")

	// For now, just return the thumbnail key reference
	// The actual thumbnail can be generated by:
	// 1. Using Cloudflare Image Resizing (if using R2)
	// 2. Using AWS Lambda@Edge
	// 3. Using a dedicated image processing service
	originalResult.ThumbnailKey = thumbKey

	return originalResult, nil
}

// GetFileSize returns the size of a file in S3
func (s *S3Storage) GetFileSize(ctx context.Context, key string) (int64, error) {
	if key == "" {
		return 0, errors.New("key is required")
	}

	result, err := s.client.HeadObject(ctx, &s3.HeadObjectInput{
		Bucket: aws.String(s.bucket),
		Key:    aws.String(key),
	})
	if err != nil {
		return 0, fmt.Errorf("failed to get file size: %w", err)
	}

	if result.ContentLength == nil {
		return 0, nil
	}
	return *result.ContentLength, nil
}

// ListObjects lists objects in the bucket with optional prefix
func (s *S3Storage) ListObjects(ctx context.Context, prefix string) ([]string, error) {
	result, err := s.client.ListObjectsV2(ctx, &s3.ListObjectsV2Input{
		Bucket: aws.String(s.bucket),
		Prefix: aws.String(prefix),
	})
	if err != nil {
		return nil, fmt.Errorf("failed to list objects: %w", err)
	}

	keys := make([]string, 0, len(result.Contents))
	for _, obj := range result.Contents {
		if obj.Key != nil {
			keys = append(keys, *obj.Key)
		}
	}

	return keys, nil
}

// Exists checks if a file exists in S3
func (s *S3Storage) Exists(ctx context.Context, key string) (bool, error) {
	if key == "" {
		return false, errors.New("key is required")
	}

	_, err := s.client.HeadObject(ctx, &s3.HeadObjectInput{
		Bucket: aws.String(s.bucket),
		Key:    aws.String(key),
	})
	if err != nil {
		var ae smithy.APIError
		if ae != nil && ae.ErrorCode() == "NotFound" {
			return false, nil
		}
		return false, fmt.Errorf("failed to check if file exists: %w", err)
	}

	return true, nil
}

// CopyObject copies an object within the same bucket
func (s *S3Storage) CopyObject(ctx context.Context, sourceKey, destKey string) error {
	if sourceKey == "" || destKey == "" {
		return errors.New("both source and destination keys are required")
	}

	_, err := s.client.CopyObject(ctx, &s3.CopyObjectInput{
		Bucket:     aws.String(s.bucket),
		CopySource: aws.String(s.bucket + "/" + sourceKey),
		Key:        aws.String(destKey),
	})
	if err != nil {
		return fmt.Errorf("failed to copy object: %w", err)
	}

	return nil
}

// Helper functions

func generateKey() string {
	return "uploads/" + time.Now().Format("2006/01/02") + "/" + uuid.New().String()
}

func addSuffixBeforeExt(filename, suffix string) string {
	// Handle edge case: filename is only dots (with no extension text)
	if strings.TrimRight(filename, ".") == "" {
		return suffix
	}

	ext := filepath.Ext(filename)
	name := filename[:len(filename)-len(ext)]

	// Handle edge case: filename consists of all dots with extension text
	// e.g., "...txt" should become "....v1txt"
	// filepath.Ext("...txt") returns ".txt", so name=".." and ext=".txt"
	// Strip leading dash from suffix for this edge case
	// We want: ".." + ".." + "v1" + "txt" = "....v1txt"
	if strings.TrimRight(name, ".") == "" && ext != "" {
		// Strip leading dashes from suffix
		suffixText := strings.TrimLeft(suffix, "-")
		// Add dots equal to the number of dashes stripped + original dots
		dashesStripped := len(suffix) - len(suffixText)
		dotsToAdd := strings.Repeat(".", dashesStripped+1)
		return name + dotsToAdd + suffixText + ext[1:]
	}

	return name + suffix + ext
}
