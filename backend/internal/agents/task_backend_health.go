package agents

import (
	"context"
	"errors"
	"fmt"
	"time"

	"gorm.io/gorm"
)

// VerifyAgentTaskBackend validates that the agent task backend's persistence contract is operational.
// This is a strict check meant for post-migration health checks, not for preflight that runs before migrations.
func VerifyAgentTaskBackend(ctx context.Context, db *gorm.DB) error {
	if db == nil {
		return errors.New("gorm db is nil")
	}

	type tableCheckRow struct {
		One int `gorm:"column:one"`
	}

	var row tableCheckRow
	if err := db.WithContext(ctx).Raw("SELECT 1 AS one FROM agent_tasks LIMIT 1").Scan(&row).Error; err != nil {
		return fmt.Errorf("agent_tasks table check failed: %w", err)
	}

	taskID := fmt.Sprintf("health-%d", time.Now().UnixNano())
	projectID := "health"
	taskData := fmt.Sprintf(
		`{"id":"%s","project_id":"%s","type":"health","priority":1,"status":"pending","parameters":{},"timeout":0,"retry_count":0,"max_retries":0}`,
		taskID,
		projectID,
	)

	// Commit + explicit cleanup so this remains safe under repeated health checks.
	if err := db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		if err := tx.Exec(
			"INSERT INTO agent_tasks (id, project_id, status, priority, data) VALUES (?, ?, ?, ?, ?)",
			taskID,
			projectID,
			string(TaskStatusPending),
			int(PriorityNormal),
			[]byte(taskData),
		).Error; err != nil {
			return fmt.Errorf("enqueue failed: %w", err)
		}

		if err := tx.Exec("UPDATE agent_tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", string(TaskStatusAssigned), taskID).Error; err != nil {
			return fmt.Errorf("transition to assigned failed: %w", err)
		}

		if err := tx.Exec("UPDATE agent_tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", string(TaskStatusCompleted), taskID).Error; err != nil {
			return fmt.Errorf("transition to completed failed: %w", err)
		}

		if err := tx.Exec("DELETE FROM agent_tasks WHERE id = ?", taskID).Error; err != nil {
			return fmt.Errorf("cleanup failed: %w", err)
		}

		return nil
	}); err != nil {
		return err
	}

	return nil
}
