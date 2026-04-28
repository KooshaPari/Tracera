//go:build !integration && !e2e

package agents

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestMessageTypes(t *testing.T) {
	tests := []struct {
		name    string
		msgType MessageType
		value   string
	}{
		{"Register", MsgTypeRegister, "register"},
		{"Heartbeat", MsgTypeHeartbeat, "heartbeat"},
		{"TaskRequest", MsgTypeTaskRequest, "task_request"},
		{"TaskResult", MsgTypeTaskResult, "task_result"},
		{"TaskError", MsgTypeTaskError, "task_error"},
		{"Unregister", MsgTypeUnregister, "unregister"},
		{"Ack", MsgTypeAck, "ack"},
		{"TaskAssigned", MsgTypeTaskAssigned, "task_assigned"},
		{"NoTask", MsgTypeNoTask, "no_task"},
		{"Error", MsgTypeError, "error"},
		{"Shutdown", MsgTypeShutdown, "shutdown"},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			assert.Equal(t, MessageType(tc.value), tc.msgType)
		})
	}
}

func TestAgentStatusValues(t *testing.T) {
	tests := []struct {
		name   string
		status AgentStatus
		value  string
	}{
		{"Idle", StatusIdle, "idle"},
		{"Active", StatusActive, "active"},
		{"Busy", StatusBusy, "busy"},
		{"Error", StatusError, "error"},
		{"Offline", StatusOffline, "offline"},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			assert.Equal(t, AgentStatus(tc.value), tc.status)
		})
	}
}

func TestTaskStatuses(t *testing.T) {
	tests := []struct {
		name   string
		status TaskStatus
		value  string
	}{
		{"Pending", TaskStatusPending, "pending"},
		{"Assigned", TaskStatusAssigned, "assigned"},
		{"Running", TaskStatusRunning, "running"},
		{"Completed", TaskStatusCompleted, "completed"},
		{"Failed", TaskStatusFailed, "failed"},
		{"Canceled", TaskStatusCanceled, "canceled"},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			assert.Equal(t, TaskStatus(tc.value), tc.status)
		})
	}
}

func TestTaskPriorities(t *testing.T) {
	assert.Equal(t, PriorityLow, TaskPriority(0))
	assert.Equal(t, PriorityNormal, TaskPriority(1))
	assert.Equal(t, PriorityHigh, TaskPriority(2))
	assert.Equal(t, PriorityCritical, TaskPriority(3))

	assert.Greater(t, PriorityCritical, PriorityHigh)
	assert.Greater(t, PriorityHigh, PriorityNormal)
	assert.Greater(t, PriorityNormal, PriorityLow)
}
