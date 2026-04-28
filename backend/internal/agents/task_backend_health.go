package agents

import (
	"context"
	"errors"
	"fmt"
	"time"

	"gorm.io/gorm"
)

// VerifyTaskBackendPersistence verifies that task data can be persisted.
func VerifyTaskBackendPersistence(ctx context.Context, db *gorm.DB) error {
	if db == nil {
		return errors.New("gorm db is nil")
	}

	projectID := "health-check-system"
	taskID := "health-check-" + time.Now().Format("20060102150405")
	taskData := fmt.Sprintf(
		`{"id":"%s","project_id":"%s","type":"health","priority":1,"status":"pending",`+
			`"parameters":{},"timeout":0,"retry_count":0,"max_retries":0}`,
		taskID,
		projectID,
	)

	// Use a raw insert to verify basic table existence and connectivity
	err := db.WithContext(ctx).Exec(
		"INSERT INTO agent_tasks (id, project_id, status, priority, data, created_at, updated_at) "+
			"VALUES (?, ?, ?, ?, ?, ?, ?)",
		taskID,
		projectID,
		"pending",
		1,
		taskData,
		time.Now(),
		time.Now(),
	).Error
	if err != nil {
		return fmt.Errorf("persistence verification failed: %w", err)
	}

	// Cleanup
	db.WithContext(ctx).Exec("DELETE FROM agent_tasks WHERE id = ?", taskID)

	return nil
}
