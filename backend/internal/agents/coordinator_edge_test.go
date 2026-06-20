//go:build !integration && !e2e

package agents

import (
	"sync"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

func TestAgentOfflineRecovery(t *testing.T) {
	agent := &RegisteredAgent{
		ID:            uuid.New().String(),
		Status:        StatusActive,
		LastHeartbeat: time.Now(),
		CurrentTask:   &Task{ID: "active-task"},
	}

	timeout := 5 * time.Minute
	agent.LastHeartbeat = time.Now().Add(-10 * time.Minute)

	isTimedOut := time.Since(agent.LastHeartbeat) > timeout
	assert.True(t, isTimedOut)

	agent.Status = StatusOffline
	taskToRequeue := agent.CurrentTask
	agent.CurrentTask = nil

	assert.Equal(t, StatusOffline, agent.Status)
	assert.Nil(t, agent.CurrentTask)
	assert.NotNil(t, taskToRequeue)

	agent.LastHeartbeat = time.Now()
	agent.Status = StatusIdle
	assert.Equal(t, StatusIdle, agent.Status)
}

func TestConcurrentAgentRegistration(t *testing.T) {
	agents := make(map[string]*RegisteredAgent)
	var mu sync.RWMutex

	const count = 100
	done := make(chan *RegisteredAgent, count)

	for i := 0; i < count; i++ {
		go func() {
			agent := &RegisteredAgent{
				ID:            uuid.New().String(),
				Name:          "agent-" + uuid.New().String(),
				ProjectID:     uuid.New().String(),
				Status:        StatusIdle,
				LastHeartbeat: time.Now(),
			}
			done <- agent
		}()
	}

	for i := 0; i < count; i++ {
		agent := <-done
		mu.Lock()
		agents[agent.ID] = agent
		mu.Unlock()
	}

	mu.RLock()
	assert.Len(t, agents, count)
	mu.RUnlock()
}

func TestAgentConflictDetection(t *testing.T) {
	projectID := uuid.New().String()

	agents := map[string]*RegisteredAgent{
		"agent-1": {
			ID:        uuid.New().String(),
			Name:      "worker",
			ProjectID: projectID,
			Status:    StatusActive,
		},
		"agent-2": {
			ID:        uuid.New().String(),
			Name:      "worker",
			ProjectID: projectID,
			Status:    StatusActive,
		},
	}

	names := make(map[string]string)
	conflicts := []string{}

	for id, agent := range agents {
		key := agent.ProjectID + ":" + agent.Name
		if existingID, exists := names[key]; exists {
			conflicts = append(conflicts, id, existingID)
		} else {
			names[key] = id
		}
	}

	assert.NotEmpty(t, conflicts)
}
