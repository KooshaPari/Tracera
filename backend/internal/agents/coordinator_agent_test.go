//go:build !integration && !e2e

package agents

import (
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestRegisterAgent(t *testing.T) {
	agent := &RegisteredAgent{
		Name:      "test-agent",
		ProjectID: uuid.New().String(),
		Status:    StatusIdle,
		Capabilities: []AgentCapability{
			{
				Name:    "test-capability",
				Version: "1.0.0",
				Tags:    []string{"test"},
			},
		},
		Metadata: map[string]interface{}{
			"version": "1.0",
		},
	}

	assert.NotEmpty(t, agent.Name)
	assert.Equal(t, StatusIdle, agent.Status)
	assert.Len(t, agent.Capabilities, 1)
}

func TestAgentStatus(t *testing.T) {
	testCases := []struct {
		name   string
		status AgentStatus
	}{
		{"Idle", StatusIdle},
		{"Active", StatusActive},
		{"Busy", StatusBusy},
		{"Error", StatusError},
		{"Offline", StatusOffline},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			agent := &RegisteredAgent{
				ID:     uuid.New().String(),
				Status: tc.status,
			}

			assert.Equal(t, tc.status, agent.Status)
		})
	}
}

func TestAgentCapabilities(t *testing.T) {
	agent := &RegisteredAgent{
		ID:   uuid.New().String(),
		Name: "test-agent",
		Capabilities: []AgentCapability{
			{Name: "read", Version: "1.0", Tags: []string{"io"}},
			{Name: "write", Version: "1.0", Tags: []string{"io"}},
			{Name: "compute", Version: "2.0", Tags: []string{"processing"}},
		},
	}

	assert.Len(t, agent.Capabilities, 3)

	var found *AgentCapability
	for _, cap := range agent.Capabilities {
		if cap.Name == "compute" {
			found = &cap
			break
		}
	}

	require.NotNil(t, found)
	assert.Equal(t, "2.0", found.Version)
	assert.Contains(t, found.Tags, "processing")
}

func TestAgentHeartbeat(t *testing.T) {
	agent := &RegisteredAgent{
		ID:            uuid.New().String(),
		LastHeartbeat: time.Now().Add(-5 * time.Minute),
	}

	oldHeartbeat := agent.LastHeartbeat
	time.Sleep(agentHeartbeatDelay)
	agent.LastHeartbeat = time.Now()

	assert.True(t, agent.LastHeartbeat.After(oldHeartbeat))
}

func TestAgentMetadata(t *testing.T) {
	agent := &RegisteredAgent{
		ID:   uuid.New().String(),
		Name: "test-agent",
		Metadata: map[string]interface{}{
			"version":     "1.0.0",
			"environment": "test",
			"cpu_cores":   4,
			"memory_gb":   8.5,
		},
	}

	assert.Equal(t, "1.0.0", agent.Metadata["version"])
	assert.Equal(t, "test", agent.Metadata["environment"])
	assert.Equal(t, 4, agent.Metadata["cpu_cores"])
	assert.InEpsilon(t, 8.5, agent.Metadata["memory_gb"], 1e-9)
}
