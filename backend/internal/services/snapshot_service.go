package services

import (
	"archive/tar"
	"compress/gzip"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"log/slog"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

const (
	snapshotMaxRetries = 3
	snapshotDirPerm    = 0o750
	snapshotFilePerm   = 0o600
)

// SnapshotMetadata contains metadata about a sandbox snapshot
type SnapshotMetadata struct {
	SessionID        string    `json:"session_id"`
	TurnNumber       int       `json:"turn_number"`
	S3Key            string    `json:"s3_key"`
	Size             int64     `json:"size"`
	FileCount        int       `json:"file_count"`
	CompressionRatio float64   `json:"compression_ratio"`
	CreatedAt        time.Time `json:"created_at"`
	Checksum         string    `json:"checksum"`
}

// SnapshotService provides sandbox snapshot management for agent execution
type SnapshotService interface {
	// CreateSnapshot creates a tarball of the sandbox, uploads to S3, and returns the S3 key
	CreateSnapshot(ctx context.Context, sessionID string, sandboxRoot string, turnNumber int) (string, *SnapshotMetadata, error)

	// RestoreSnapshot downloads a snapshot from S3 and extracts it to the target directory
	RestoreSnapshot(ctx context.Context, sessionID string, s3Key string, targetDir string) error

	// GetSnapshotMetadata retrieves metadata for a snapshot
	GetSnapshotMetadata(ctx context.Context, s3Key string) (*SnapshotMetadata, error)

	// ListSnapshots lists all snapshots for a session
	ListSnapshots(ctx context.Context, sessionID string) ([]*SnapshotMetadata, error)

	// DeleteSnapshot removes a snapshot from S3
	DeleteSnapshot(ctx context.Context, s3Key string) error

	// CleanupOldSnapshots removes snapshots older than the retention period
	CleanupOldSnapshots(ctx context.Context, sessionID string, retentionDays int) error
}

// snapshotServiceImpl implements SnapshotService
type snapshotServiceImpl struct {
	storage StorageService
	logger  *log.Logger
	bucket  string
}

// NewSnapshotService creates a new SnapshotService instance
func NewSnapshotService(storage StorageService, bucket string, logger *log.Logger) SnapshotService {
	if storage == nil {
		panic("storage service cannot be nil")
	}
	if logger == nil {
		logger = log.New(os.Stdout, "[SnapshotService] ", log.LstdFlags)
	}
	if bucket == "" {
		bucket = "tracertm" // default bucket
	}

	return &snapshotServiceImpl{
		storage: storage,
		logger:  logger,
		bucket:  bucket,
	}
}

// CreateSnapshot creates a tarball of the sandbox and uploads to S3
func (s *snapshotServiceImpl) CreateSnapshot(
	ctx context.Context,
	sessionID string,
	sandboxRoot string,
	turnNumber int,
) (string, *SnapshotMetadata, error) {
	if sessionID == "" {
		return "", nil, errors.New("session ID is required")
	}
	if sandboxRoot == "" {
		return "", nil, errors.New("sandbox root is required")
	}

	s.logger.Printf("Creating snapshot for session %s, turn %d from %s", sessionID, turnNumber, sandboxRoot)

	// Validate sandbox directory exists
	if _, err := os.Stat(sandboxRoot); os.IsNotExist(err) {
		return "", nil, fmt.Errorf("sandbox directory does not exist: %s", sandboxRoot)
	}

	// Create temporary tarball file
	tempDir := os.TempDir()
	tarballPath := filepath.Join(tempDir, sessionID+"-"+strconv.FormatInt(time.Now().Unix(), 10)+".tar.gz")
	defer func() {
		if err := os.Remove(tarballPath); err != nil {
			slog.Warn("failed to remove temp tarball", "path", tarballPath, "error", err)
		}
	}() // Cleanup temp file

	s.logger.Printf("Creating tarball at %s", tarballPath)

	// Create tarball
	originalSize, compressedSize, fileCount, err := s.createTarball(sandboxRoot, tarballPath)
	if err != nil {
		return "", nil, fmt.Errorf("failed to create tarball: %w", err)
	}

	s.logger.Printf("Tarball created: %d files, original size: %d bytes, compressed: %d bytes",
		fileCount, originalSize, compressedSize)

	// Calculate compression ratio
	compressionRatio := 0.0
	if originalSize > 0 {
		compressionRatio = float64(compressedSize) / float64(originalSize)
	}

	// Generate S3 key
	s3Key := "sandboxes/" + sessionID + "/snapshots/snapshot-" + strconv.Itoa(turnNumber) + ".tar.gz"

	// Upload to S3 with retry logic
	if err := s.uploadWithRetry(ctx, tarballPath, s3Key, snapshotMaxRetries); err != nil {
		return "", nil, fmt.Errorf("failed to upload snapshot: %w", err)
	}

	s.logger.Printf("Snapshot uploaded successfully to %s", s3Key)

	// Create and upload metadata
	metadata := &SnapshotMetadata{
		SessionID:        sessionID,
		TurnNumber:       turnNumber,
		S3Key:            s3Key,
		Size:             compressedSize,
		FileCount:        fileCount,
		CompressionRatio: compressionRatio,
		CreatedAt:        time.Now(),
		Checksum:         "", // Note: Checksum calculation not yet implemented
	}

	// Upload metadata
	metadataKey := "sandboxes/" + sessionID + "/snapshots/snapshot-" + strconv.Itoa(turnNumber) + "-metadata.json"
	if err := s.uploadMetadata(ctx, metadata, metadataKey); err != nil {
		s.logger.Printf("Warning: Failed to upload metadata: %v", err)
		// Don't fail the snapshot creation if metadata upload fails
	}

	return s3Key, metadata, nil
}

// RestoreSnapshot downloads and extracts a snapshot
func (s *snapshotServiceImpl) RestoreSnapshot(
	ctx context.Context,
	sessionID string,
	s3Key string,
	targetDir string,
) error {
	if sessionID == "" {
		return errors.New("session ID is required")
	}
	if s3Key == "" {
		return errors.New("S3 key is required")
	}
	if targetDir == "" {
		return errors.New("target directory is required")
	}

	s.logger.Printf("Restoring snapshot from %s to %s", s3Key, targetDir)

	// Ensure target directory exists
	if err := os.MkdirAll(targetDir, snapshotDirPerm); err != nil {
		return fmt.Errorf("failed to create target directory: %w", err)
	}

	// Create temporary file for download
	tempDir := os.TempDir()
	tarballPath := filepath.Join(tempDir, sessionID+"-restore-"+strconv.FormatInt(time.Now().Unix(), 10)+".tar.gz")
	defer func() {
		if err := os.Remove(tarballPath); err != nil {
			slog.Warn("failed to remove temp tarball", "path", tarballPath, "error", err)
		}
	}() // Cleanup temp file

	// Download from S3 with retry logic
	if err := s.downloadWithRetry(ctx, s3Key, tarballPath, snapshotMaxRetries); err != nil {
		return fmt.Errorf("failed to download snapshot: %w", err)
	}

	s.logger.Printf("Snapshot downloaded to %s", tarballPath)

	// Extract tarball
	if err := s.extractTarball(tarballPath, targetDir); err != nil {
		return fmt.Errorf("failed to extract tarball: %w", err)
	}

	s.logger.Printf("Snapshot extracted successfully to %s", targetDir)

	return nil
}

// GetSnapshotMetadata retrieves metadata for a snapshot
func (s *snapshotServiceImpl) GetSnapshotMetadata(ctx context.Context, s3Key string) (*SnapshotMetadata, error) {
	if s3Key == "" {
		return nil, errors.New("S3 key is required")
	}

	// Derive metadata key from snapshot key
	metadataKey := s3Key[:len(s3Key)-len(".tar.gz")] + "-metadata.json"

	// Download metadata
	data, err := s.storage.DownloadFile(ctx, metadataKey)
	if err != nil {
		return nil, fmt.Errorf("failed to download metadata: %w", err)
	}

	// Parse metadata
	var metadata SnapshotMetadata
	if err := json.Unmarshal(data, &metadata); err != nil {
		return nil, fmt.Errorf("failed to parse metadata: %w", err)
	}

	return &metadata, nil
}

// ListSnapshots lists all snapshots for a session
func (s *snapshotServiceImpl) ListSnapshots(ctx context.Context, sessionID string) ([]*SnapshotMetadata, error) {
	if sessionID == "" {
		return nil, errors.New("session ID is required")
	}

	prefix := "sandboxes/" + sessionID + "/snapshots/"
	files, err := s.storage.ListFiles(ctx, s.bucket, prefix)
	if err != nil {
		return nil, fmt.Errorf("failed to list snapshots: %w", err)
	}

	// Filter for metadata files and load them
	var snapshots []*SnapshotMetadata
	for _, file := range files {
		if filepath.Ext(file.Key) == ".json" {
			data, err := s.storage.DownloadFile(ctx, file.Key)
			if err != nil {
				s.logger.Printf("Warning: Failed to download metadata %s: %v", file.Key, err)
				continue
			}

			var metadata SnapshotMetadata
			if err := json.Unmarshal(data, &metadata); err != nil {
				s.logger.Printf("Warning: Failed to parse metadata %s: %v", file.Key, err)
				continue
			}

			snapshots = append(snapshots, &metadata)
		}
	}

	return snapshots, nil
}

// DeleteSnapshot removes a snapshot from S3
func (s *snapshotServiceImpl) DeleteSnapshot(ctx context.Context, s3Key string) error {
	if s3Key == "" {
		return errors.New("S3 key is required")
	}

	s.logger.Printf("Deleting snapshot %s", s3Key)

	// Delete snapshot tarball
	if err := s.storage.DeleteFile(ctx, s3Key); err != nil {
		return fmt.Errorf("failed to delete snapshot: %w", err)
	}

	// Delete metadata (best effort)
	metadataKey := s3Key[:len(s3Key)-len(".tar.gz")] + "-metadata.json"
	if err := s.storage.DeleteFile(ctx, metadataKey); err != nil {
		s.logger.Printf("Warning: Failed to delete metadata %s: %v", metadataKey, err)
		// Don't fail if metadata deletion fails
	}

	s.logger.Printf("Snapshot deleted successfully")

	return nil
}

// CleanupOldSnapshots removes snapshots older than retention period
func (s *snapshotServiceImpl) CleanupOldSnapshots(ctx context.Context, sessionID string, retentionDays int) error {
	if sessionID == "" {
		return errors.New("session ID is required")
	}
	if retentionDays < 0 {
		retentionDays = 7 // default to 7 days
	}

	s.logger.Printf("Cleaning up snapshots older than %d days for session %s", retentionDays, sessionID)

	snapshots, err := s.ListSnapshots(ctx, sessionID)
	if err != nil {
		return fmt.Errorf("failed to list snapshots: %w", err)
	}

	cutoffTime := time.Now().AddDate(0, 0, -retentionDays)
	deletedCount := 0

	for _, snapshot := range snapshots {
		if snapshot.CreatedAt.Before(cutoffTime) {
			if err := s.DeleteSnapshot(ctx, snapshot.S3Key); err != nil {
				s.logger.Printf("Warning: Failed to delete old snapshot %s: %v", snapshot.S3Key, err)
				continue
			}
			deletedCount++
		}
	}

	s.logger.Printf("Cleaned up %d old snapshots", deletedCount)

	return nil
}

// ============================================================================
// HELPER METHODS
// ============================================================================

// createTarball creates a gzipped tarball from a directory
func (s *snapshotServiceImpl) createTarball(sourceDir, targetPath string) (originalSize, compressedSize int64, fileCount int, err error) {
	// Validate and clean paths
	sourceDir = filepath.Clean(sourceDir)
	targetPath = filepath.Clean(targetPath)

	// Create target file
	file, err := os.Create(targetPath)
	if err != nil {
		return 0, 0, 0, fmt.Errorf("failed to create tarball file: %w", err)
	}
	defer func() {
		if cerr := file.Close(); cerr != nil {
			slog.Warn("failed to close tarball file", "error", cerr)
		}
	}()

	// Create gzip writer
	gzWriter := gzip.NewWriter(file)
	defer func() {
		if cerr := gzWriter.Close(); cerr != nil {
			slog.Warn("failed to close gzip writer", "error", cerr)
		}
	}()

	// Create tar writer
	tarWriter := tar.NewWriter(gzWriter)
	defer func() {
		if cerr := tarWriter.Close(); cerr != nil {
			slog.Warn("failed to close tar writer", "error", cerr)
		}
	}()

	// Walk directory and add files
	stats := tarballStats{}
	err = filepath.Walk(sourceDir, func(path string, info os.FileInfo, walkErr error) error {
		return addPathToTar(tarWriter, sourceDir, path, info, walkErr, &stats)
	})
	if err != nil {
		return 0, 0, 0, err
	}

	// Get compressed size
	compressedSize, err = getFileSize(targetPath)
	if err != nil {
		return 0, 0, 0, err
	}

	return stats.originalSize, compressedSize, stats.fileCount, nil
}

type tarballStats struct {
	originalSize int64
	fileCount    int
}

func addPathToTar(tarWriter *tar.Writer, sourceDir, path string, info os.FileInfo, walkErr error, stats *tarballStats) error {
	if walkErr != nil {
		return walkErr
	}

	// Skip the source directory itself
	if path == sourceDir {
		return nil
	}

	// Get relative path
	relPath, err := filepath.Rel(sourceDir, path)
	if err != nil {
		return fmt.Errorf("failed to get relative path: %w", err)
	}

	// Create tar header
	header, err := tar.FileInfoHeader(info, info.Name())
	if err != nil {
		return fmt.Errorf("failed to create tar header: %w", err)
	}
	header.Name = relPath

	// Write header
	if err := tarWriter.WriteHeader(header); err != nil {
		return fmt.Errorf("failed to write tar header: %w", err)
	}

	// Write file content (skip directories)
	if info.IsDir() {
		return nil
	}

	// Clean path before opening
	cleanPath := filepath.Clean(path)
	fileData, err := os.Open(cleanPath)
	if err != nil {
		return fmt.Errorf("failed to open file: %w", err)
	}
	defer func() {
		if cerr := fileData.Close(); cerr != nil {
			slog.Warn("failed to close file data", "error", cerr)
		}
	}()

	n, err := io.Copy(tarWriter, fileData)
	if err != nil {
		return fmt.Errorf("failed to write file to tar: %w", err)
	}

	stats.originalSize += n
	stats.fileCount++

	return nil
}

func getFileSize(path string) (int64, error) {
	fileInfo, err := os.Stat(path)
	if err != nil {
		return 0, fmt.Errorf("failed to stat tarball: %w", err)
	}
	return fileInfo.Size(), nil
}

// extractTarball extracts a gzipped tarball to a directory
func (s *snapshotServiceImpl) extractTarball(tarballPath, targetDir string) error {
	// Clean and validate paths
	tarballPath = filepath.Clean(tarballPath)
	targetDir = filepath.Clean(targetDir)

	tarReader, closeFn, err := openTarReader(tarballPath)
	if err != nil {
		return err
	}
	defer closeFn()

	const maxTotalSize = 10 * 1024 * 1024 * 1024 // 10 GB limit
	return extractTarEntries(tarReader, targetDir, maxTotalSize)
}

// isWithinDirectory checks if childPath is within parentPath (prevents path traversal)
func isWithinDirectory(childPath, parentPath string) bool {
	// Clean paths
	child := filepath.Clean(childPath)
	parent := filepath.Clean(parentPath)

	// Get relative path
	rel, err := filepath.Rel(parent, child)
	if err != nil {
		return false
	}

	// Check if relative path tries to escape
	if filepath.IsAbs(rel) {
		return false
	}
	if rel == ".." || strings.HasPrefix(rel, ".."+string(filepath.Separator)) {
		return false
	}
	return true
}

func openTarReader(tarballPath string) (*tar.Reader, func(), error) {
	file, err := os.Open(filepath.Clean(tarballPath))
	if err != nil {
		return nil, nil, fmt.Errorf("failed to open tarball: %w", err)
	}

	gzReader, err := gzip.NewReader(file)
	if err != nil {
		if cerr := file.Close(); cerr != nil {
			slog.Warn("failed to close file after gzip reader error", "error", cerr)
		}
		return nil, nil, fmt.Errorf("failed to create gzip reader: %w", err)
	}

	closeFn := func() {
		if cerr := gzReader.Close(); cerr != nil {
			slog.Warn("failed to close gzip reader", "error", cerr)
		}
		if cerr := file.Close(); cerr != nil {
			slog.Warn("failed to close tarball file", "error", cerr)
		}
	}

	return tar.NewReader(gzReader), closeFn, nil
}

func extractTarEntries(tarReader *tar.Reader, targetDir string, maxTotalSize int64) error {
	var totalExtracted int64

	for {
		header, err := tarReader.Next()
		if err == io.EOF {
			return nil
		}
		if err != nil {
			return fmt.Errorf("failed to read tar header: %w", err)
		}

		if err := extractTarEntry(tarReader, header, targetDir, maxTotalSize, &totalExtracted); err != nil {
			return err
		}
	}
}

func extractTarEntry(tarReader *tar.Reader, header *tar.Header, targetDir string, maxTotalSize int64, totalExtracted *int64) error {
	targetPath, err := safeExtractPath(targetDir, header.Name)
	if err != nil {
		return err
	}

	switch header.Typeflag {
	case tar.TypeDir:
		mode, err := safeFileMode(header.Mode, snapshotDirPerm)
		if err != nil {
			return err
		}
		if err := os.MkdirAll(targetPath, mode); err != nil {
			return fmt.Errorf("failed to create directory: %w", err)
		}
		return nil
	case tar.TypeReg:
		return extractTarFile(tarReader, header, targetPath, maxTotalSize, totalExtracted)
	default:
		return nil
	}
}

// validateTarEntrySize validates the header size and tracks cumulative extraction size.
func validateTarEntrySize(header *tar.Header, maxTotalSize int64, totalExtracted *int64) error {
	if header.Size < 0 {
		return fmt.Errorf("invalid file size in tarball: %d", header.Size)
	}
	if header.Size > int64(^uint32(0)) {
		return fmt.Errorf("file size too large: %d bytes", header.Size)
	}
	*totalExtracted += header.Size
	if *totalExtracted > maxTotalSize {
		return fmt.Errorf("extraction aborted: total size (%d bytes) exceeds limit (%d bytes)", *totalExtracted, maxTotalSize)
	}
	return nil
}

func extractTarFile(tarReader *tar.Reader, header *tar.Header, targetPath string, maxTotalSize int64, totalExtracted *int64) error {
	if err := validateTarEntrySize(header, maxTotalSize, totalExtracted); err != nil {
		return err
	}

	if err := os.MkdirAll(filepath.Dir(targetPath), snapshotDirPerm); err != nil {
		return fmt.Errorf("failed to create parent directory: %w", err)
	}

	mode, err := safeFileMode(header.Mode, snapshotFilePerm)
	if err != nil {
		return err
	}
	outFile, err := os.OpenFile(filepath.Clean(targetPath), os.O_CREATE|os.O_WRONLY|os.O_TRUNC, mode)
	if err != nil {
		return fmt.Errorf("failed to create file: %w", err)
	}

	count, err := io.CopyN(outFile, tarReader, header.Size)
	if cerr := outFile.Close(); cerr != nil {
		return fmt.Errorf("failed to close extracted file: %w", cerr)
	}
	if err != nil && !errors.Is(err, io.EOF) {
		return fmt.Errorf("failed to write file content: %w", err)
	}
	if count != header.Size {
		return fmt.Errorf("incomplete file write: expected %d bytes, wrote %d bytes", header.Size, count)
	}

	return nil
}

func safeExtractPath(targetDir, entryName string) (string, error) {
	cleanName := filepath.Clean(entryName)
	if filepath.IsAbs(cleanName) {
		return "", fmt.Errorf("invalid file path in tarball (absolute path): %s", entryName)
	}
	if cleanName == ".." || strings.HasPrefix(cleanName, ".."+string(filepath.Separator)) {
		return "", fmt.Errorf("invalid file path in tarball (path traversal attempt): %s", entryName)
	}

	targetPath := filepath.Clean(targetDir + string(filepath.Separator) + cleanName)
	if !isWithinDirectory(targetPath, targetDir) {
		return "", fmt.Errorf("invalid file path in tarball (path traversal attempt): %s", entryName)
	}
	return targetPath, nil
}

func safeFileMode(mode int64, mask os.FileMode) (os.FileMode, error) {
	if mode < 0 || mode > int64(^uint32(0)) {
		return 0, fmt.Errorf("invalid file mode in tarball: %d", mode)
	}
	return os.FileMode(uint32(mode)) & mask, nil
}

// uploadWithRetry uploads a file to S3 with retry logic
func (s *snapshotServiceImpl) uploadWithRetry(ctx context.Context, localPath, s3Key string, maxRetries int) error {
	var lastErr error

	// Clean path before reading
	localPath = filepath.Clean(localPath)

	for attempt := 1; attempt <= maxRetries; attempt++ {
		// Read file
		data, err := os.ReadFile(localPath)
		if err != nil {
			return fmt.Errorf("failed to read file: %w", err)
		}

		// Upload
		_, err = s.storage.UploadFile(ctx, data, s.bucket, s3Key, "application/gzip")
		if err == nil {
			return nil
		}

		lastErr = err
		s.logger.Printf("Upload attempt %d/%d failed: %v", attempt, maxRetries, err)

		if attempt < maxRetries {
			// Exponential backoff
			backoff := time.Duration(attempt) * time.Second
			s.logger.Printf("Retrying in %v...", backoff)
			time.Sleep(backoff)
		}
	}

	return fmt.Errorf("upload failed after %d attempts: %w", maxRetries, lastErr)
}

// downloadWithRetry downloads a file from S3 with retry logic
func (s *snapshotServiceImpl) downloadWithRetry(ctx context.Context, s3Key, localPath string, maxRetries int) error {
	var lastErr error

	// Clean path before writing
	localPath = filepath.Clean(localPath)

	for attempt := 1; attempt <= maxRetries; attempt++ {
		// Download
		data, err := s.storage.DownloadFile(ctx, s3Key)
		if err == nil {
			// Write to file with secure permissions
			if err := os.WriteFile(localPath, data, snapshotFilePerm); err != nil {
				return fmt.Errorf("failed to write file: %w", err)
			}
			return nil
		}

		lastErr = err
		s.logger.Printf("Download attempt %d/%d failed: %v", attempt, maxRetries, err)

		if attempt < maxRetries {
			// Exponential backoff
			backoff := time.Duration(attempt) * time.Second
			s.logger.Printf("Retrying in %v...", backoff)
			time.Sleep(backoff)
		}
	}

	return fmt.Errorf("download failed after %d attempts: %w", maxRetries, lastErr)
}

// uploadMetadata uploads snapshot metadata to S3
func (s *snapshotServiceImpl) uploadMetadata(ctx context.Context, metadata *SnapshotMetadata, s3Key string) error {
	data, err := json.MarshalIndent(metadata, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal metadata: %w", err)
	}

	_, err = s.storage.UploadFile(ctx, data, s.bucket, s3Key, "application/json")
	if err != nil {
		return fmt.Errorf("failed to upload metadata: %w", err)
	}

	return nil
}
