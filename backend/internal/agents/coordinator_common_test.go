//go:build !integration && !e2e

package agents

import (
	"time"
)

const agentHeartbeatDelay = 10 * time.Millisecond

func createTestItem(id, title, itemType string) *RegisteredAgent {
	return &RegisteredAgent{
		ID:        id,
		Name:      title,
		ProjectID: "test-project",
		Status:    StatusIdle,
	}
}
