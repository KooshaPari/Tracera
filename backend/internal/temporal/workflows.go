package temporal

import (
	"fmt"
	"time"

	"go.temporal.io/sdk/workflow"
)

// SnapshotRequest represents a request to create a snapshot
type SnapshotRequest struct {
	SessionID string `json:"session_id"`
}

// SnapshotWorkflow defines the snapshot creation workflow
// Orchestrates: QuerySnapshot → CreateSnapshot → UploadSnapshot
// With appropriate retry policies and error handling
func SnapshotWorkflow(ctx workflow.Context, req SnapshotRequest) (string, error) {
	// Note: RetryPolicy is configured per-activity below

	// Initialize activities
	activities := &SnapshotActivities{}

	// Phase 1: Query snapshot state (2 retries, 5s backoff)
	var payload *SnapshotPayload
	err := workflow.ExecuteActivity(
		workflow.WithActivityOptions(ctx, workflow.ActivityOptions{
			ScheduleToCloseTimeout: time.Minute * 2,
		}),
		activities.QuerySnapshot,
		req.SessionID,
	).Get(ctx, &payload)
	if err != nil {
		return "", fmt.Errorf("QuerySnapshot failed: %w", err)
	}

	// Phase 2: Create snapshot tarball (1 retry, 10s backoff)
	var tarballData []byte
	err = workflow.ExecuteActivity(
		workflow.WithActivityOptions(ctx, workflow.ActivityOptions{
			ScheduleToCloseTimeout: time.Minute * 3,
		}),
		activities.CreateSnapshot,
		payload,
	).Get(ctx, &tarballData)
	if err != nil {
		return "", fmt.Errorf("CreateSnapshot failed: %w", err)
	}

	// Phase 3: Upload snapshot to MinIO (3 retries, 2s exponential backoff)
	var s3Key string
	err = workflow.ExecuteActivity(
		workflow.WithActivityOptions(ctx, workflow.ActivityOptions{
			ScheduleToCloseTimeout: time.Minute * 2,
		}),
		activities.UploadSnapshot,
		req.SessionID,
		tarballData,
	).Get(ctx, &s3Key)
	if err != nil {
		return "", fmt.Errorf("UploadSnapshot failed: %w", err)
	}

	return s3Key, nil
}

// ScheduledSnapshotWorkflow wraps the snapshot workflow for scheduled execution
// Called every hour or on-demand
func ScheduledSnapshotWorkflow(ctx workflow.Context, sessionID string) error {
	req := SnapshotRequest{SessionID: sessionID}
	var s3Key string
	err := workflow.ExecuteChildWorkflow(ctx, SnapshotWorkflow, req).Get(ctx, &s3Key)
	if err != nil {
		return fmt.Errorf("ScheduledSnapshotWorkflow failed: %w", err)
	}

	return nil
}
