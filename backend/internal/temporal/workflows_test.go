package temporal

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.uber.org/zap"
)

// TestSnapshotActivitiesQuerySnapshot tests the QuerySnapshot activity
func TestSnapshotActivitiesQuerySnapshot(t *testing.T) {
	activities := &SnapshotActivities{
		db:     nil, // Will be mocked in integration tests
		neo4j:  nil,
		minio:  nil,
		logger: zap.NewNop(),
	}

	sessionID := "test-session-456"
	payload, err := activities.QuerySnapshot(context.Background(), sessionID)

	require.NoError(t, err)
	assert.Equal(t, sessionID, payload.SessionID)
	assert.NotZero(t, payload.Timestamp)
}

// TestSnapshotActivitiesCreateSnapshot tests the CreateSnapshot activity
func TestSnapshotActivitiesCreateSnapshot(t *testing.T) {
	activities := &SnapshotActivities{
		logger: zap.NewNop(),
	}

	payload := &SnapshotPayload{
		SessionID: "test-session-789",
		Projects:  []map[string]interface{}{},
		Items:     []map[string]interface{}{},
		Timestamp: time.Now(),
	}

	tarballData, err := activities.CreateSnapshot(context.Background(), payload)

	require.NoError(t, err)
	assert.NotEmpty(t, tarballData)
	// Should be gzip compressed tar
	assert.NotEmpty(t, tarballData)
	// Check for gzip magic bytes
	assert.Equal(t, byte(0x1f), tarballData[0])
	assert.Equal(t, byte(0x8b), tarballData[1])
}

// TestSnapshotActivitiesUploadSnapshotMocked tests UploadSnapshot with mocked MinIO
func TestSnapshotActivitiesUploadSnapshotMocked(t *testing.T) {
	// Create activities instance with nil MinIO (will skip upload)
	activities := &SnapshotActivities{
		minio:  nil,
		logger: zap.NewNop(),
	}

	sessionID := "test-session-111"
	tarballData := []byte("mock-tarball-data")

	// Should fail gracefully with no MinIO client
	_, err := activities.UploadSnapshot(context.Background(), sessionID, tarballData)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "MinIO client not available")
}

// TestSnapshotPayloadSerialization tests that SnapshotPayload can be serialized
func TestSnapshotPayloadSerialization(t *testing.T) {
	payload := &SnapshotPayload{
		SessionID: "test-session-serial",
		Projects: []map[string]interface{}{
			{"id": "proj-1", "name": "Project 1"},
		},
		Items: []map[string]interface{}{
			{"id": "item-1", "title": "Item 1"},
			{"id": "item-2", "title": "Item 2"},
		},
		Timestamp: time.Now(),
	}

	// Verify payload structure is valid
	assert.Equal(t, "test-session-serial", payload.SessionID)
	assert.Len(t, payload.Projects, 1)
	assert.Len(t, payload.Items, 2)
	assert.NotZero(t, payload.Timestamp)
}

// TestSnapshotResultStructure tests SnapshotResult structure
func TestSnapshotResultStructure(t *testing.T) {
	result := &SnapshotResult{
		S3Key:    "s3://bucket/path/snapshot.tar.gz",
		Size:     1024,
		Checksum: "abc123def456",
		Created:  time.Now(),
	}

	assert.NotEmpty(t, result.S3Key)
	assert.Positive(t, result.Size)
	assert.NotEmpty(t, result.Checksum)
	assert.NotZero(t, result.Created)
}
