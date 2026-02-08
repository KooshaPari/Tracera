//go:build !integration && !e2e

package agents

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestCapabilityMatchingExactMatch(t *testing.T) {
	agent := &RegisteredAgent{
		Capabilities: []AgentCapability{
			{Name: "read"},
			{Name: "write"},
			{Name: "compute"},
		},
	}

	task := &Task{
		RequiredCapabilities: []string{"read", "write"},
	}

	agentCaps := make(map[string]bool)
	for _, cap := range agent.Capabilities {
		agentCaps[cap.Name] = true
	}

	hasAll := true
	for _, required := range task.RequiredCapabilities {
		if !agentCaps[required] {
			hasAll = false
			break
		}
	}

	assert.True(t, hasAll)
}

func TestCapabilityMatchingPartialMatch(t *testing.T) {
	agent := &RegisteredAgent{
		Capabilities: []AgentCapability{
			{Name: "read"},
			{Name: "write"},
		},
	}

	task := &Task{
		RequiredCapabilities: []string{"read", "write", "delete"},
	}

	agentCaps := make(map[string]bool)
	for _, cap := range agent.Capabilities {
		agentCaps[cap.Name] = true
	}

	hasAll := true
	for _, required := range task.RequiredCapabilities {
		if !agentCaps[required] {
			hasAll = false
			break
		}
	}

	assert.False(t, hasAll)
}

func TestCapabilityMatchingBestAgent(t *testing.T) {
	agents := []*RegisteredAgent{
		{
			ID:     "1",
			Status: StatusIdle,
			Capabilities: []AgentCapability{
				{Name: "read"},
			},
		},
		{
			ID:     "2",
			Status: StatusIdle,
			Capabilities: []AgentCapability{
				{Name: "read"},
				{Name: "write"},
				{Name: "compute"},
			},
		},
		{
			ID:     "3",
			Status: StatusBusy,
			Capabilities: []AgentCapability{
				{Name: "read"},
				{Name: "write"},
			},
		},
	}

	task := &Task{
		RequiredCapabilities: []string{"read", "write"},
	}

	var bestAgent *RegisteredAgent
	for _, agent := range agents {
		if agent.Status != StatusIdle {
			continue
		}

		agentCaps := make(map[string]bool)
		for _, cap := range agent.Capabilities {
			agentCaps[cap.Name] = true
		}

		hasAll := true
		for _, required := range task.RequiredCapabilities {
			if !agentCaps[required] {
				hasAll = false
				break
			}
		}

		if hasAll {
			bestAgent = agent
			break
		}
	}

	require.NotNil(t, bestAgent)
	assert.Equal(t, "2", bestAgent.ID)
}
