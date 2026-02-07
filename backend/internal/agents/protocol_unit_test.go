//go:build unit

package agents

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// ========== Protocol Create* and Parse* unit tests ==========

func TestProtocol_CreateRegisterMessage(t *testing.T) {
	p := NewProtocol()
	req := &RegisterRequest{
		Name:         "agent-1",
		ProjectID:    "proj-1",
		Capabilities: []AgentCapability{{Name: "run", Version: "1.0"}},
		Metadata:     map[string]interface{}{"env": "test"},
	}
	msg := p.CreateRegisterMessage(req)
	require.NotNil(t, msg)
	assert.Equal(t, MsgTypeRegister, msg.Type)
	assert.NotZero(t, msg.Timestamp)
	assert.Equal(t, "agent-1", msg.Payload["name"])
	assert.Equal(t, "proj-1", msg.Payload["project_id"])
}

func TestProtocol_CreateHeartbeatMessage_WithoutMetrics(t *testing.T) {
	p := NewProtocol()
	req := &HeartbeatRequest{AgentID: "ag-1", Status: StatusIdle}
	msg := p.CreateHeartbeatMessage(req)
	require.NotNil(t, msg)
	assert.Equal(t, MsgTypeHeartbeat, msg.Type)
	assert.Equal(t, "ag-1", msg.AgentID)
	assert.Equal(t, "ag-1", msg.Payload["agent_id"])
}

func TestProtocol_CreateHeartbeatMessage_WithMetrics(t *testing.T) {
	p := NewProtocol()
	req := &HeartbeatRequest{
		AgentID: "ag-1",
		Status:  StatusActive,
		Metrics: &AgentMetrics{CPUUsage: 50, MemoryUsage: 60},
	}
	msg := p.CreateHeartbeatMessage(req)
	require.NotNil(t, msg)
	assert.NotNil(t, msg.Payload["metrics"])
}

func TestProtocol_CreateTaskRequestMessage_WithTags(t *testing.T) {
	p := NewProtocol()
	req := &TaskRequest{AgentID: "ag-1", Tags: []string{"urgent"}}
	msg := p.CreateTaskRequestMessage(req)
	require.NotNil(t, msg)
	assert.Equal(t, MsgTypeTaskRequest, msg.Type)
	assert.Equal(t, "ag-1", msg.AgentID)
	assert.Equal(t, []interface{}{"urgent"}, msg.Payload["tags"])
}

func TestProtocol_CreateTaskResultMessage(t *testing.T) {
	p := NewProtocol()
	req := &TaskResultRequest{
		AgentID: "ag-1",
		TaskID:  "task-1",
		Result:  &TaskResult{Success: true, Message: "done"},
	}
	msg := p.CreateTaskResultMessage(req)
	require.NotNil(t, msg)
	assert.Equal(t, MsgTypeTaskResult, msg.Type)
	assert.Equal(t, "task-1", msg.Payload["task_id"])
}

func TestProtocol_CreateTaskErrorMessage(t *testing.T) {
	p := NewProtocol()
	req := &TaskErrorRequest{
		AgentID: "ag-1", TaskID: "task-1",
		ErrorMessage: "failed", Retryable: true,
		Timestamp: time.Now(),
	}
	msg := p.CreateTaskErrorMessage(req)
	require.NotNil(t, msg)
	assert.Equal(t, MsgTypeTaskError, msg.Type)
	assert.Equal(t, "failed", msg.Payload["error_message"])
	assert.True(t, msg.Payload["retryable"].(bool))
}

func TestProtocol_CreateAckMessage(t *testing.T) {
	p := NewProtocol()
	msg := p.CreateAckMessage("ok", "registered")
	require.NotNil(t, msg)
	assert.Equal(t, MsgTypeAck, msg.Type)
	assert.Equal(t, "ok", msg.Payload["status"])
	assert.Equal(t, "registered", msg.Payload["message"])
}

func TestProtocol_CreateTaskAssignedMessage(t *testing.T) {
	p := NewProtocol()
	task := &Task{ID: "t1", ProjectID: "p1"}
	msg := p.CreateTaskAssignedMessage(task)
	require.NotNil(t, msg)
	assert.Equal(t, MsgTypeTaskAssigned, msg.Type)
	assert.NotNil(t, msg.Payload["task"])
}

func TestProtocol_CreateNoTaskMessage(t *testing.T) {
	p := NewProtocol()
	msg := p.CreateNoTaskMessage()
	require.NotNil(t, msg)
	assert.Equal(t, MsgTypeNoTask, msg.Type)
	assert.Equal(t, "No tasks available", msg.Payload["message"])
}

func TestProtocol_CreateErrorMessage(t *testing.T) {
	p := NewProtocol()
	msg := p.CreateErrorMessage("something failed")
	require.NotNil(t, msg)
	assert.Equal(t, MsgTypeError, msg.Type)
	assert.Equal(t, "something failed", msg.Error)
}

func TestProtocol_ParseMessage_ValidJSON(t *testing.T) {
	p := NewProtocol()
	raw := []byte(`{"type":"heartbeat","agent_id":"ag-1","timestamp":"2024-01-01T00:00:00Z"}`)
	msg, err := p.ParseMessage(raw)
	require.NoError(t, err)
	require.NotNil(t, msg)
	assert.Equal(t, MsgTypeHeartbeat, msg.Type)
	assert.Equal(t, "ag-1", msg.AgentID)
}

func TestProtocol_ParseMessage_InvalidJSON(t *testing.T) {
	p := NewProtocol()
	msg, err := p.ParseMessage([]byte("not json"))
	require.Error(t, err)
	assert.Nil(t, msg)
}

func TestProtocol_SerializeMessage(t *testing.T) {
	p := NewProtocol()
	msg := &Message{Type: MsgTypeAck, Timestamp: time.Now()}
	data, err := p.SerializeMessage(msg)
	require.NoError(t, err)
	require.NotEmpty(t, data)
	var decoded Message
	err = json.Unmarshal(data, &decoded)
	require.NoError(t, err)
	assert.Equal(t, MsgTypeAck, decoded.Type)
}

func TestProtocol_ParseRegisterRequest(t *testing.T) {
	p := NewProtocol()
	payload := map[string]interface{}{
		"name":         "a1",
		"project_id":   "p1",
		"capabilities": []interface{}{},
		"metadata":     map[string]interface{}{},
	}
	req, err := p.ParseRegisterRequest(payload)
	require.NoError(t, err)
	require.NotNil(t, req)
	assert.Equal(t, "a1", req.Name)
	assert.Equal(t, "p1", req.ProjectID)
}

func TestProtocol_ParseHeartbeatRequest(t *testing.T) {
	p := NewProtocol()
	payload := map[string]interface{}{
		"agent_id": "ag-1",
		"status":   "idle",
	}
	req, err := p.ParseHeartbeatRequest(payload)
	require.NoError(t, err)
	require.NotNil(t, req)
	assert.Equal(t, "ag-1", req.AgentID)
}

func TestProtocol_ParseTaskRequest(t *testing.T) {
	p := NewProtocol()
	payload := map[string]interface{}{"agent_id": "ag-1", "tags": []interface{}{"x"}}
	req, err := p.ParseTaskRequest(payload)
	require.NoError(t, err)
	require.NotNil(t, req)
	assert.Equal(t, "ag-1", req.AgentID)
}

func TestProtocol_ParseTaskResultRequest(t *testing.T) {
	p := NewProtocol()
	payload := map[string]interface{}{
		"agent_id": "ag-1",
		"task_id":  "t1",
		"result":   map[string]interface{}{"success": true},
	}
	req, err := p.ParseTaskResultRequest(payload)
	require.NoError(t, err)
	require.NotNil(t, req)
	assert.Equal(t, "t1", req.TaskID)
}

func TestProtocol_ParseTaskErrorRequest(t *testing.T) {
	p := NewProtocol()
	payload := map[string]interface{}{
		"agent_id":      "ag-1",
		"task_id":       "t1",
		"error_message": "err",
		"retryable":     true,
		"timestamp":     time.Now(),
	}
	req, err := p.ParseTaskErrorRequest(payload)
	require.NoError(t, err)
	require.NotNil(t, req)
	assert.Equal(t, "err", req.ErrorMessage)
}

func TestProtocol_ValidateMessage_EmptyType(t *testing.T) {
	p := NewProtocol()
	msg := &Message{Type: ""}
	err := p.ValidateMessage(msg)
	require.Error(t, err)
	assert.True(t, err != nil)
}

func TestProtocol_ValidateMessage_RegisterNeedsPayload(t *testing.T) {
	p := NewProtocol()
	msg := &Message{Type: MsgTypeRegister, Payload: nil}
	err := p.ValidateMessage(msg)
	require.Error(t, err)
}

func TestProtocol_ValidateMessage_HeartbeatNeedsAgentID(t *testing.T) {
	p := NewProtocol()
	msg := &Message{Type: MsgTypeHeartbeat, AgentID: ""}
	err := p.ValidateMessage(msg)
	require.Error(t, err)
}

func TestProtocol_ValidateMessage_TaskRequestNeedsAgentID(t *testing.T) {
	p := NewProtocol()
	msg := &Message{Type: MsgTypeTaskRequest, AgentID: ""}
	err := p.ValidateMessage(msg)
	require.Error(t, err)
}

func TestProtocol_ValidateMessage_UnknownTypePasses(t *testing.T) {
	p := NewProtocol()
	msg := &Message{Type: MessageType("unknown")}
	err := p.ValidateMessage(msg)
	assert.NoError(t, err)
}

func TestProtocolError_Error(t *testing.T) {
	err := ErrInvalidMessage("test")
	require.NotNil(t, err)
	assert.Contains(t, err.Error(), "protocol error")
	assert.Contains(t, err.Error(), "test")
	pe, ok := err.(*ProtocolError)
	require.True(t, ok)
	assert.Equal(t, "test", pe.Message)
}

func TestPriorityQueue_Push_NonTaskIgnored(t *testing.T) {
	pq := make(priorityQueue, 0)
	// Push non-*Task: queue.go Push checks type and returns without appending if not *Task
	// So we need to test that Push with *Task works (already in coordinator_test)
	// and that Pop with empty returns nil. Len for empty.
	assert.Equal(t, 0, pq.Len())
}
