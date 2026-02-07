package temporal

import (
	"archive/tar"
	"bytes"
	"compress/gzip"
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	"github.com/minio/minio-go/v7"
	"go.uber.org/zap"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

// SnapshotPayload represents the state to be snapshotted
type SnapshotPayload struct {
	SessionID string                   `json:"session_id"`
	Projects  []map[string]interface{} `json:"projects"`
	Items     []map[string]interface{} `json:"items"`
	Timestamp time.Time                `json:"timestamp"`
}

// SnapshotResult represents the result of a snapshot operation
type SnapshotResult struct {
	S3Key    string    `json:"s3_key"`
	Size     int64     `json:"size"`
	Checksum string    `json:"checksum"`
	Created  time.Time `json:"created"`
}

// SnapshotActivities contains the activities for snapshot workflow
type SnapshotActivities struct {
	db     *sql.DB
	neo4j  neo4j.Driver
	minio  *minio.Client
	logger *zap.Logger
}

// NewSnapshotActivities creates a new snapshot activities instance
func NewSnapshotActivities(db *sql.DB, neo4jDriver neo4j.Driver, minioClient *minio.Client, logger *zap.Logger) *SnapshotActivities {
	return &SnapshotActivities{
		db:     db,
		neo4j:  neo4jDriver,
		minio:  minioClient,
		logger: logger,
	}
}

// QuerySnapshot queries project and item state from databases
// Activity with retry policy: 2 retries, 5s backoff
func (a *SnapshotActivities) QuerySnapshot(ctx context.Context, sessionID string) (*SnapshotPayload, error) {
	// Note: activity.GetLogger() requires proper activity context from Temporal runtime
	// In tests/standalone, we skip logging or use regular logger

	// Initialize payload
	payload := &SnapshotPayload{
		SessionID: sessionID,
		Projects:  []map[string]interface{}{},
		Items:     []map[string]interface{}{},
		Timestamp: time.Now(),
	}

	// Query Neo4j for project state
	if a.neo4j != nil {
		session := a.neo4j.NewSession(neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
		defer session.Close()

		result, err := session.Run(
			"MATCH (p:Project) WHERE p.session_id = $sessionID RETURN p",
			map[string]interface{}{"sessionID": sessionID})
		if err != nil {
			if a.logger != nil {
				a.logger.Error("Failed to query Neo4j for projects", zap.Error(err), zap.String("session_id", sessionID))
			}
			// Don't fail on this error, just log it
		} else {
			for result.Next() {
				record := result.Record()
				if p, ok := record.Get("p"); ok {
					payload.Projects = append(payload.Projects, map[string]interface{}{
						"data": p,
					})
				}
			}
			if err = result.Err(); err != nil {
				if a.logger != nil {
					a.logger.Error("Error iterating Neo4j results", zap.Error(err))
				}
			}
		}
	}

	// Query PostgreSQL for items
	if a.db != nil {
		rows, err := a.db.QueryContext(ctx,
			"SELECT id, title, description, type, status, priority FROM items WHERE session_id = $1 ORDER BY created_at",
			sessionID)
		if err != nil {
			if a.logger != nil {
				a.logger.Error("Failed to query PostgreSQL for items", zap.Error(err), zap.String("session_id", sessionID))
			}
			// Don't fail on this error, just log it
		} else {
			defer rows.Close()
			for rows.Next() {
				var id, title, description, itemType, status, priority string
				if err := rows.Scan(&id, &title, &description, &itemType, &status, &priority); err != nil {
					if a.logger != nil {
						a.logger.Error("Failed to scan item row", zap.Error(err))
					}
					continue
				}
				payload.Items = append(payload.Items, map[string]interface{}{
					"id":          id,
					"title":       title,
					"description": description,
					"type":        itemType,
					"status":      status,
					"priority":    priority,
				})
			}
		}
	}

	if a.logger != nil {
		a.logger.Info("Snapshot state queried successfully",
			zap.String("session_id", sessionID),
			zap.Int("projects_count", len(payload.Projects)),
			zap.Int("items_count", len(payload.Items)))
	}

	return payload, nil
}

// CreateSnapshot creates a compressed tarball of the snapshot payload
// Activity with retry policy: 1 retry, 10s backoff
func (a *SnapshotActivities) CreateSnapshot(ctx context.Context, payload *SnapshotPayload) ([]byte, error) {
	// Logging would use activity.GetLogger(ctx) in Temporal runtime
	_ = ctx // Activity context available during workflow execution

	// Create in-memory tar archive
	var tarBuf bytes.Buffer
	tw := tar.NewWriter(&tarBuf)
	defer tw.Close()

	// Marshal payload to JSON
	data, err := json.Marshal(payload)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal snapshot payload: %w", err)
	}

	// Create tar entry for snapshot data
	header := &tar.Header{
		Name: fmt.Sprintf("snapshot-%s.json", payload.SessionID),
		Size: int64(len(data)),
		Mode: 0o644,
	}
	if err := tw.WriteHeader(header); err != nil {
		return nil, fmt.Errorf("failed to write tar header: %w", err)
	}

	if _, err := tw.Write(data); err != nil {
		return nil, fmt.Errorf("failed to write tar data: %w", err)
	}

	// Add metadata file
	metadata := map[string]interface{}{
		"session_id": payload.SessionID,
		"created_at": payload.Timestamp,
		"projects":   len(payload.Projects),
		"items":      len(payload.Items),
	}
	metadataData, _ := json.MarshalIndent(metadata, "", "  ")

	header = &tar.Header{
		Name: "metadata.json",
		Size: int64(len(metadataData)),
		Mode: 0o644,
	}
	if err := tw.WriteHeader(header); err != nil {
		return nil, fmt.Errorf("failed to write metadata header: %w", err)
	}
	if _, err := tw.Write(metadataData); err != nil {
		return nil, fmt.Errorf("failed to write metadata: %w", err)
	}

	tw.Close() // Ensure tar is finalized

	// Compress with gzip
	var compressedBuf bytes.Buffer
	gw := gzip.NewWriter(&compressedBuf)
	if _, err := gw.Write(tarBuf.Bytes()); err != nil {
		return nil, fmt.Errorf("failed to compress snapshot: %w", err)
	}
	if err := gw.Close(); err != nil {
		return nil, fmt.Errorf("failed to close gzip writer: %w", err)
	}

	compressedData := compressedBuf.Bytes()
	if a.logger != nil {
		a.logger.Info("Snapshot created successfully",
			zap.String("session_id", payload.SessionID),
			zap.Int("size_bytes", len(compressedData)))
	}

	return compressedData, nil
}

// UploadSnapshot uploads the snapshot to MinIO
// Activity with retry policy: 3 retries, 2s exponential backoff
func (a *SnapshotActivities) UploadSnapshot(ctx context.Context, sessionID string, data []byte) (string, error) {
	// Activity context available during workflow execution
	_ = ctx

	if a.minio == nil {
		return "", fmt.Errorf("MinIO client not available")
	}

	// Create object key
	timestamp := time.Now().Format("20060102-150405")
	objectKey := fmt.Sprintf("snapshots/%s/%s.tar.gz", sessionID, timestamp)

	// Upload to MinIO
	info, err := a.minio.PutObject(ctx, "tracertm", objectKey, bytes.NewReader(data), int64(len(data)), minio.PutObjectOptions{
		ContentType: "application/gzip",
	})
	if err != nil {
		return "", fmt.Errorf("failed to upload snapshot to MinIO: %w", err)
	}

	// Return S3-style key
	s3Key := fmt.Sprintf("s3://tracertm/%s", objectKey)

	if a.logger != nil {
		a.logger.Info("Snapshot uploaded successfully",
			zap.String("session_id", sessionID),
			zap.String("object_key", objectKey),
			zap.String("etag", info.ETag),
			zap.Int64("size", info.Size))
	}

	return s3Key, nil
}
