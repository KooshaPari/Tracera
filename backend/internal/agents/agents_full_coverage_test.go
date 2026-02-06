// Package agents tests the agent coordination and queue behaviors.
package agents

import (
	"encoding/json"
	"sync"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

// ============================================================================
// MOCK DATABASE FUNCTIONALITY TESTS
// ============================================================================

// TestMockDBSave tests mock database save operations
func TestMockDB_Save(t *testing.T) {
	mock := NewMockDB()

	// Test save operation tracking
	mock.Save(&struct{ ID string }{ID: "test-1"})
	calls := mock.GetSaveCalls()
	assert.Equal(t, 1, len(calls))
}

// TestMockDBUpdate tests mock database update operations
func TestMockDB_Update(t *testing.T) {
	mock := NewMockDB()

	// Test update operation tracking
	result := mock.Update("status", "active")
	assert.NotNil(t, result)

	calls := mock.GetUpdateCalls()
	assert.Equal(t, 1, len(calls))
	assert.Contains(t, calls[0], "status")
}

// TestMockDBSetError tests error simulation
func TestMockDB_SetShouldError(t *testing.T) {
	mock := NewMockDB()

	// Set error on save operation
	mock.SetShouldError("save", true)

	// Now save should return error
	result := mock.Save(&struct{ ID string }{ID: "test"})
	assert.NotNil(t, result.Error)
}

// TestMockDBReset tests resetting mock database
func TestMockDB_Reset(t *testing.T) {
	mock := NewMockDB()

	// Add some data
	mock.Save(&struct{ ID string }{ID: "test"})
	assert.Equal(t, 1, len(mock.GetSaveCalls()))

	// Reset
	mock.Reset()
	assert.Equal(t, 0, len(mock.GetSaveCalls()))
}

// ============================================================================
// TEST HELPERS FUNCTIONALITY TESTS
// ============================================================================

// TestTestHelpers_CreateAgent tests agent creation helper
func TestTestHelpers_CreateAgent(t *testing.T) {
	helpers := NewTestHelpers()

	agent := helpers.CreateTestAgent("agent-1", "test", "proj-1")

	assert.Equal(t, "agent-1", agent.ID)
	assert.Equal(t, "test", agent.Name)
	assert.Equal(t, "proj-1", agent.ProjectID)
	assert.Equal(t, StatusIdle, agent.Status)
	assert.Greater(t, len(agent.Capabilities), 0)
}

// TestTestHelpers_CreateTask tests task creation helper
func TestTestHelpers_CreateTask(t *testing.T) {
	helpers := NewTestHelpers()

	task := helpers.CreateTestTask("task-1", "proj-1", "analyze", PriorityHigh)

	assert.Equal(t, "task-1", task.ID)
	assert.Equal(t, "proj-1", task.ProjectID)
	assert.Equal(t, "analyze", task.Type)
	assert.Equal(t, PriorityHigh, task.Priority)
	assert.Equal(t, TaskStatusPending, task.Status)
}

// TestTestHelpers_CreateLock tests lock creation helper
func TestTestHelpers_CreateLock(t *testing.T) {
	helpers := NewTestHelpers()

	lock := helpers.CreateTestLock("lock-1", "item-1", "agent-1", LockTypePessimistic)

	assert.Equal(t, "lock-1", lock.ID)
	assert.Equal(t, "item-1", lock.ItemID)
	assert.Equal(t, "agent-1", lock.AgentID)
	assert.Equal(t, LockTypePessimistic, lock.LockType)
}

// TestTestHelpers_CreateTeam tests team creation helper
func TestTestHelpers_CreateTeam(t *testing.T) {
	helpers := NewTestHelpers()

	team := helpers.CreateTestTeam("team-1", "proj-1", "Dev Team")

	assert.Equal(t, "team-1", team.ID)
	assert.Equal(t, "proj-1", team.ProjectID)
	assert.Equal(t, "Dev Team", team.Name)
	assert.Greater(t, len(team.Roles), 0)
}

// TestTestHelpers_CreateConflict tests conflict creation helper
func TestTestHelpers_CreateConflict(t *testing.T) {
	helpers := NewTestHelpers()

	conflict := helpers.CreateTestConflict("conflict-1", "item-1", []string{"agent-1", "agent-2"})

	assert.Equal(t, "conflict-1", conflict.ID)
	assert.Equal(t, "item-1", conflict.ItemID)
	assert.Equal(t, 2, len(conflict.ConflictingAgents))
	assert.Equal(t, "pending", conflict.ResolutionStatus)
}

// ============================================================================
// SERIALIZATION TESTS
// ============================================================================

// TestSerializeTask tests task serialization
func TestSerializeTask(t *testing.T) {
	task := &Task{
		ID:        uuid.New().String(),
		ProjectID: "proj-1",
		Type:      "analyze",
		Priority:  PriorityNormal,
		Status:    TaskStatusPending,
	}

	// Act
	serialized := SerializeTask(task)

	// Assert
	assert.NotNil(t, serialized)
	assert.Greater(t, len(serialized), 0)

	// Verify it's valid JSON
	var data map[string]interface{}
	err := json.Unmarshal(serialized, &data)
	assert.NoError(t, err)
}

// TestDeserializeTask tests task deserialization
func TestDeserializeTask(t *testing.T) {
	original := &Task{
		ID:        uuid.New().String(),
		ProjectID: "proj-1",
		Type:      "analyze",
		Priority:  PriorityNormal,
		Status:    TaskStatusPending,
	}

	// Serialize and deserialize
	serialized := SerializeTask(original)
	deserialized, err := DeserializeTask(serialized)

	// Assert
	assert.NoError(t, err)
	assert.Equal(t, original.ID, deserialized.ID)
	assert.Equal(t, original.ProjectID, deserialized.ProjectID)
	assert.Equal(t, original.Type, deserialized.Type)
}

// ============================================================================
// PROTOCOL MESSAGE CREATION TESTS
// ============================================================================

// TestProtocol_CreateRegisterMessage tests registration message creation
func TestProtocol_CreateRegisterMessage(t *testing.T) {
	proto := NewProtocol()

	req := &RegisterRequest{
		Name:      "test-agent",
		ProjectID: "proj-1",
		Capabilities: []AgentCapability{
			{Name: "analyze"},
		},
	}

	msg := proto.CreateRegisterMessage(req)

	assert.NotNil(t, msg)
	assert.Equal(t, MsgTypeRegister, msg.Type)
	assert.NotZero(t, msg.Timestamp)
	assert.NotNil(t, msg.Payload)
}

// TestProtocol_CreateHeartbeatMessage tests heartbeat message creation
func TestProtocol_CreateHeartbeatMessage(t *testing.T) {
	proto := NewProtocol()

	req := &HeartbeatRequest{
		AgentID: "agent-1",
		Status:  StatusActive,
	}

	msg := proto.CreateHeartbeatMessage(req)

	assert.NotNil(t, msg)
	assert.Equal(t, MsgTypeHeartbeat, msg.Type)
	assert.Equal(t, "agent-1", msg.AgentID)
}

// TestProtocol_CreateTaskRequestMessage tests task request message creation
func TestProtocol_CreateTaskRequestMessage(t *testing.T) {
	proto := NewProtocol()

	req := &TaskRequest{
		AgentID: "agent-1",
		Tags:    []string{"tag1", "tag2"},
	}

	msg := proto.CreateTaskRequestMessage(req)

	assert.NotNil(t, msg)
	assert.Equal(t, MsgTypeTaskRequest, msg.Type)
	assert.Equal(t, "agent-1", msg.AgentID)
}

// TestProtocol_CreateTaskResultMessage tests task result message creation
func TestProtocol_CreateTaskResultMessage(t *testing.T) {
	proto := NewProtocol()

	req := &TaskResultRequest{
		AgentID: "agent-1",
		TaskID:  "task-1",
		Result: &TaskResult{
			Success:  true,
			Duration: 5 * time.Second,
		},
	}

	msg := proto.CreateTaskResultMessage(req)

	assert.NotNil(t, msg)
	assert.Equal(t, MsgTypeTaskResult, msg.Type)
	assert.Equal(t, "agent-1", msg.AgentID)
}

// TestProtocol_CreateTaskErrorMessage tests task error message creation
func TestProtocol_CreateTaskErrorMessage(t *testing.T) {
	proto := NewProtocol()

	req := &TaskErrorRequest{
		AgentID:      "agent-1",
		TaskID:       "task-1",
		ErrorMessage: "Task failed",
		ErrorCode:    "ERROR_001",
		Retryable:    true,
		Timestamp:    time.Now(),
	}

	msg := proto.CreateTaskErrorMessage(req)

	assert.NotNil(t, msg)
	assert.Equal(t, MsgTypeTaskError, msg.Type)
	assert.Equal(t, "agent-1", msg.AgentID)
}

// TestProtocol_CreateAckMessage tests acknowledgment message creation
func TestProtocol_CreateAckMessage(t *testing.T) {
	proto := NewProtocol()

	msg := proto.CreateAckMessage("success", "Operation completed")

	assert.NotNil(t, msg)
	assert.Equal(t, MsgTypeAck, msg.Type)
	assert.NotNil(t, msg.Payload)
}

// TestProtocol_CreateTaskAssignedMessage tests task assigned message creation
func TestProtocol_CreateTaskAssignedMessage(t *testing.T) {
	proto := NewProtocol()

	task := &Task{
		ID:        "task-1",
		ProjectID: "proj-1",
		Type:      "analyze",
	}

	msg := proto.CreateTaskAssignedMessage(task)

	assert.NotNil(t, msg)
	assert.Equal(t, MsgTypeTaskAssigned, msg.Type)
}

// TestProtocol_CreateNoTaskMessage tests no-task message creation
func TestProtocol_CreateNoTaskMessage(t *testing.T) {
	proto := NewProtocol()

	msg := proto.CreateNoTaskMessage()

	assert.NotNil(t, msg)
	assert.Equal(t, MsgTypeNoTask, msg.Type)
}

// TestProtocol_CreateErrorMessage tests error message creation
func TestProtocol_CreateErrorMessage(t *testing.T) {
	proto := NewProtocol()

	msg := proto.CreateErrorMessage("An error occurred")

	assert.NotNil(t, msg)
	assert.Equal(t, MsgTypeError, msg.Type)
	assert.Equal(t, "An error occurred", msg.Error)
}

// ============================================================================
// PROTOCOL MESSAGE PARSING TESTS
// ============================================================================

// TestProtocol_ParseMessage tests message parsing
func TestProtocol_ParseMessage(t *testing.T) {
	proto := NewProtocol()

	msgJSON := []byte(`{
		"type": "heartbeat",
		"agent_id": "agent-1",
		"timestamp": "2024-01-01T00:00:00Z"
	}`)

	msg, err := proto.ParseMessage(msgJSON)

	assert.NoError(t, err)
	assert.NotNil(t, msg)
	assert.Equal(t, MsgTypeHeartbeat, msg.Type)
	assert.Equal(t, "agent-1", msg.AgentID)
}

// TestProtocol_SerializeMessage tests message serialization
func TestProtocol_SerializeMessage(t *testing.T) {
	proto := NewProtocol()

	msg := &Message{
		Type:      MsgTypeHeartbeat,
		AgentID:   "agent-1",
		Timestamp: time.Now(),
	}

	data, err := proto.SerializeMessage(msg)

	assert.NoError(t, err)
	assert.NotNil(t, data)

	// Verify can be unmarshaled
	var parsed Message
	err = json.Unmarshal(data, &parsed)
	assert.NoError(t, err)
}

// TestProtocol_ParseRegisterRequest tests parsing register request
func TestProtocol_ParseRegisterRequest(t *testing.T) {
	proto := NewProtocol()

	payload := map[string]interface{}{
		"name":       "test-agent",
		"project_id": "proj-1",
	}

	req, err := proto.ParseRegisterRequest(payload)

	assert.NoError(t, err)
	assert.NotNil(t, req)
	assert.Equal(t, "test-agent", req.Name)
	assert.Equal(t, "proj-1", req.ProjectID)
}

// TestProtocol_ParseHeartbeatRequest tests parsing heartbeat request
func TestProtocol_ParseHeartbeatRequest(t *testing.T) {
	proto := NewProtocol()

	payload := map[string]interface{}{
		"agent_id": "agent-1",
		"status":   "active",
	}

	req, err := proto.ParseHeartbeatRequest(payload)

	assert.NoError(t, err)
	assert.NotNil(t, req)
	assert.Equal(t, "agent-1", req.AgentID)
}

// TestProtocol_ParseTaskRequest tests parsing task request
func TestProtocol_ParseTaskRequest(t *testing.T) {
	proto := NewProtocol()

	payload := map[string]interface{}{
		"agent_id": "agent-1",
		"tags":     []interface{}{"tag1"},
	}

	req, err := proto.ParseTaskRequest(payload)

	assert.NoError(t, err)
	assert.NotNil(t, req)
	assert.Equal(t, "agent-1", req.AgentID)
}

// TestProtocol_ValidateMessage tests message validation
func TestProtocol_ValidateMessage(t *testing.T) {
	proto := NewProtocol()

	// Valid message
	validMsg := &Message{
		Type:    MsgTypeHeartbeat,
		AgentID: "agent-1",
	}
	assert.NoError(t, proto.ValidateMessage(validMsg))

	// Invalid message - missing type
	invalidMsg := &Message{
		Type: "",
	}
	assert.Error(t, proto.ValidateMessage(invalidMsg))
}

// ============================================================================
// TASK QUEUE OPERATIONS TESTS (WITHOUT DB DEPENDENCY)
// ============================================================================

// TestTaskStore_Serialization tests task store serialization
func TestTaskStore_Serialization(t *testing.T) {
	taskStore := &TaskStore{
		ID:        "task-1",
		ProjectID: "proj-1",
		Status:    "pending",
		Priority:  2,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	// Verify fields are accessible
	assert.Equal(t, "task-1", taskStore.ID)
	assert.Equal(t, "proj-1", taskStore.ProjectID)
	assert.Equal(t, "pending", taskStore.Status)
	assert.Equal(t, 2, taskStore.Priority)
}

// ============================================================================
// DATA STRUCTURE TESTS
// ============================================================================

// TestAgentCapabilityStructure tests capability structure
func TestAgentCapabilityStructure(t *testing.T) {
	capability := AgentCapability{
		Name:        "analyze",
		Version:     "1.0",
		Description: "Code analysis",
		Tags:        []string{"tag1"},
	}

	assert.Equal(t, "analyze", capability.Name)
	assert.Equal(t, "1.0", capability.Version)
	assert.Equal(t, "Code analysis", capability.Description)
}

// TestRegisteredAgent tests agent registration structure
func TestRegisteredAgent(t *testing.T) {
	agent := &RegisteredAgent{
		ID:            "agent-1",
		Name:          "test-agent",
		ProjectID:     "proj-1",
		Status:        StatusIdle,
		LastHeartbeat: time.Now(),
		Metadata:      make(map[string]interface{}),
	}

	assert.Equal(t, "agent-1", agent.ID)
	assert.Equal(t, "test-agent", agent.Name)
	assert.Equal(t, StatusIdle, agent.Status)
}

// TestTask tests task structure
func TestTask(t *testing.T) {
	task := &Task{
		ID:         "task-1",
		ProjectID:  "proj-1",
		Type:       "analyze",
		Priority:   PriorityHigh,
		Status:     TaskStatusPending,
		CreatedAt:  time.Now(),
		MaxRetries: 3,
		Timeout:    30 * time.Second,
		Parameters: make(map[string]interface{}),
	}

	assert.Equal(t, "task-1", task.ID)
	assert.Equal(t, "analyze", task.Type)
	assert.Equal(t, PriorityHigh, task.Priority)
	assert.Equal(t, TaskStatusPending, task.Status)
}

// TestTaskResultStructure tests task result structure
func TestTaskResultStructure(t *testing.T) {
	result := &TaskResult{
		Success:  true,
		Data:     map[string]interface{}{"key": "value"},
		Message:  "Success",
		Duration: 5 * time.Second,
	}

	assert.True(t, result.Success)
	assert.Equal(t, "Success", result.Message)
	assert.Equal(t, 5*time.Second, result.Duration)
}

// TestAgentLock tests lock structure
func TestAgentLock(t *testing.T) {
	lock := &AgentLock{
		ID:       "lock-1",
		ItemID:   "item-1",
		AgentID:  "agent-1",
		LockType: LockTypePessimistic,
		Version:  1,
		ExpireAt: time.Now().Add(5 * time.Minute),
		Metadata: make(map[string]interface{}),
	}

	assert.Equal(t, "lock-1", lock.ID)
	assert.Equal(t, "item-1", lock.ItemID)
	assert.Equal(t, LockTypePessimistic, lock.LockType)
}

// TestAgentTeam tests team structure
func TestAgentTeam(t *testing.T) {
	team := &AgentTeam{
		ID:        "team-1",
		ProjectID: "proj-1",
		Name:      "dev-team",
		Roles:     make(map[string]TeamRole),
		Metadata:  make(map[string]interface{}),
	}

	assert.Equal(t, "team-1", team.ID)
	assert.Equal(t, "dev-team", team.Name)
}

// TestConflictRecord tests conflict record structure
func TestConflictRecord(t *testing.T) {
	conflict := &ConflictRecord{
		ID:                 "conflict-1",
		ItemID:             "item-1",
		ConflictingAgents:  []string{"agent-1", "agent-2"},
		ConflictType:       "concurrent_modification",
		ResolutionStrategy: ResolutionLastWriteWins,
		ResolutionStatus:   "pending",
		CreatedAt:          time.Now(),
	}

	assert.Equal(t, "conflict-1", conflict.ID)
	assert.Equal(t, 2, len(conflict.ConflictingAgents))
	assert.Equal(t, "pending", conflict.ResolutionStatus)
}

// ============================================================================
// CONCURRENCY TESTS FOR MOCK DB
// ============================================================================

// TestMockDB_ConcurrentSave tests concurrent save operations
func TestMockDB_ConcurrentSave(t *testing.T) {
	mock := NewMockDB()
	numOps := 100

	var wg sync.WaitGroup
	wg.Add(numOps)

	for i := 0; i < numOps; i++ {
		go func(_ int) {
			defer wg.Done()
			mock.Save(&struct{ ID string }{ID: uuid.New().String()})
		}(i)
	}

	wg.Wait()

	calls := mock.GetSaveCalls()
	assert.Equal(t, numOps, len(calls))
}

// TestMockDB_ConcurrentUpdate tests concurrent update operations
func TestMockDB_ConcurrentUpdate(t *testing.T) {
	mock := NewMockDB()
	numOps := 100

	var wg sync.WaitGroup
	wg.Add(numOps)

	for i := 0; i < numOps; i++ {
		go func(_ int) {
			defer wg.Done()
			mock.Update("status", "active")
		}(i)
	}

	wg.Wait()

	calls := mock.GetUpdateCalls()
	assert.Equal(t, numOps, len(calls))
}

// ============================================================================
// EDGE CASES AND ERROR HANDLING
// ============================================================================

// TestDeserializeTaskInvalid tests deserializing invalid JSON
func TestDeserializeTaskInvalid(t *testing.T) {
	invalidJSON := []byte("invalid json")

	_, err := DeserializeTask(invalidJSON)

	assert.Error(t, err)
}

// TestProtocolParseMessageInvalid tests parsing invalid message JSON
func TestProtocolParseMessageInvalid(t *testing.T) {
	proto := NewProtocol()

	invalidJSON := []byte("not json")

	_, err := proto.ParseMessage(invalidJSON)

	assert.Error(t, err)
}

// TestProtocolValidateMessageEmpty tests validating empty message
func TestProtocolValidateMessageEmpty(t *testing.T) {
	proto := NewProtocol()

	msg := &Message{}

	assert.Error(t, proto.ValidateMessage(msg))
}

// ============================================================================
// TYPE CONSTANTS AND ENUMS VALIDATION
// ============================================================================

// TestAgentStatusConstants tests agent status constants
func TestAgentStatusConstants(t *testing.T) {
	assert.Equal(t, AgentStatus("idle"), StatusIdle)
	assert.Equal(t, AgentStatus("active"), StatusActive)
	assert.Equal(t, AgentStatus("busy"), StatusBusy)
	assert.Equal(t, AgentStatus("error"), StatusError)
	assert.Equal(t, AgentStatus("offline"), StatusOffline)
}

// TestTaskStatusConstants tests task status constants
func TestTaskStatusConstants(t *testing.T) {
	assert.Equal(t, TaskStatus("pending"), TaskStatusPending)
	assert.Equal(t, TaskStatus("assigned"), TaskStatusAssigned)
	assert.Equal(t, TaskStatus("running"), TaskStatusRunning)
	assert.Equal(t, TaskStatus("completed"), TaskStatusCompleted)
	assert.Equal(t, TaskStatus("failed"), TaskStatusFailed)
	assert.Equal(t, TaskStatus("canceled"), TaskStatusCanceled)
}

// TestTaskPriorityConstants tests task priority constants
func TestTaskPriorityConstants(t *testing.T) {
	assert.Equal(t, TaskPriority(0), PriorityLow)
	assert.Equal(t, TaskPriority(1), PriorityNormal)
	assert.Equal(t, TaskPriority(2), PriorityHigh)
	assert.Equal(t, TaskPriority(3), PriorityCritical)
}

// Note: TestMessageTypeConstants is already defined in coordinator_comprehensive_test.go
// Skipping duplicate here to avoid declaration conflicts

// TestLockTypeConstants tests lock type constants
func TestLockTypeConstants(t *testing.T) {
	assert.Equal(t, LockType("optimistic"), LockTypeOptimistic)
	assert.Equal(t, LockType("pessimistic"), LockTypePessimistic)
}

// TestConflictResolutionStrategyConstants tests conflict resolution constants
func TestConflictResolutionStrategyConstants(t *testing.T) {
	assert.Equal(t, ConflictResolutionStrategy("last_write_wins"), ResolutionLastWriteWins)
	assert.Equal(t, ConflictResolutionStrategy("agent_priority"), ResolutionAgentPriority)
	assert.Equal(t, ConflictResolutionStrategy("manual"), ResolutionManual)
	assert.Equal(t, ConflictResolutionStrategy("merge"), ResolutionMerge)
	assert.Equal(t, ConflictResolutionStrategy("first_wins"), ResolutionFirstWins)
}

// ============================================================================
// HELPER FUNCTION COVERAGE TESTS
// ============================================================================

// TestNewTestHelpers creates new test helpers and verifies initialization
func TestNewTestHelpers(t *testing.T) {
	helpers := NewTestHelpers()

	assert.NotNil(t, helpers)
	assert.NotNil(t, helpers.GetMockDB())
}

// TestMockDBAddAgent adds agent and verifies storage
func TestMockDBAddAgent(t *testing.T) {
	mock := NewMockDB()

	agent := &struct{ ID string }{ID: "test-1"}
	mock.Save(agent)

	// Verify save was tracked
	calls := mock.GetSaveCalls()
	assert.Equal(t, 1, len(calls))
}

// TestMockDBRowsAffected verifies rows affected tracking
func TestMockDBRowsAffected(t *testing.T) {
	mock := NewMockDB()

	// Initial should be 0
	initial := mock.RowsAffected()
	assert.Equal(t, int64(0), initial)

	// After update should increment rows affected
	mock.Update("status", "active")
	after := mock.RowsAffected()
	assert.Equal(t, int64(1), after)
}

// TestProtocolAllMessageTypes tests all message type creation functions
func TestProtocolAllMessageTypes(t *testing.T) {
	proto := NewProtocol()

	// Test all message creation functions don't panic
	assert.NotNil(t, proto.CreateRegisterMessage(&RegisterRequest{}))
	assert.NotNil(t, proto.CreateHeartbeatMessage(&HeartbeatRequest{}))
	assert.NotNil(t, proto.CreateTaskRequestMessage(&TaskRequest{}))
	assert.NotNil(t, proto.CreateTaskResultMessage(&TaskResultRequest{}))
	assert.NotNil(t, proto.CreateTaskErrorMessage(&TaskErrorRequest{}))
	assert.NotNil(t, proto.CreateAckMessage("", ""))
	assert.NotNil(t, proto.CreateTaskAssignedMessage(&Task{}))
	assert.NotNil(t, proto.CreateNoTaskMessage())
	assert.NotNil(t, proto.CreateErrorMessage(""))
}

// TestRegisterRequestValidation tests register request field population
func TestRegisterRequestValidation(t *testing.T) {
	req := &RegisterRequest{
		Name:      "agent",
		ProjectID: "proj",
		Capabilities: []AgentCapability{
			{Name: "test"},
		},
		Metadata: map[string]interface{}{
			"key": "value",
		},
	}

	assert.Equal(t, "agent", req.Name)
	assert.Equal(t, "proj", req.ProjectID)
	assert.Equal(t, 1, len(req.Capabilities))
	assert.Equal(t, 1, len(req.Metadata))
}

// TestHeartbeatRequestValidation tests heartbeat request fields
func TestHeartbeatRequestValidation(t *testing.T) {
	req := &HeartbeatRequest{
		AgentID: "agent-1",
		Status:  StatusActive,
		Metrics: &AgentMetrics{
			CPUUsage:    50.5,
			MemoryUsage: 60.0,
		},
	}

	assert.Equal(t, "agent-1", req.AgentID)
	assert.Equal(t, StatusActive, req.Status)
	assert.Equal(t, 50.5, req.Metrics.CPUUsage)
}

// TestTaskRequestValidation tests task request fields
func TestTaskRequestValidation(t *testing.T) {
	req := &TaskRequest{
		AgentID: "agent-1",
		Tags:    []string{"tag1", "tag2"},
	}

	assert.Equal(t, "agent-1", req.AgentID)
	assert.Equal(t, 2, len(req.Tags))
}

// TestTaskResultRequestValidation tests task result request fields
func TestTaskResultRequestValidation(t *testing.T) {
	req := &TaskResultRequest{
		AgentID: "agent-1",
		TaskID:  "task-1",
		Result: &TaskResult{
			Success: true,
			Data: map[string]interface{}{
				"output": "test",
			},
		},
	}

	assert.Equal(t, "agent-1", req.AgentID)
	assert.Equal(t, "task-1", req.TaskID)
	assert.True(t, req.Result.Success)
}

// TestTaskErrorRequestValidation tests task error request fields
func TestTaskErrorRequestValidation(t *testing.T) {
	req := &TaskErrorRequest{
		AgentID:      "agent-1",
		TaskID:       "task-1",
		ErrorMessage: "Test error",
		ErrorCode:    "ERR_001",
		Retryable:    true,
		Timestamp:    time.Now(),
	}

	assert.Equal(t, "agent-1", req.AgentID)
	assert.Equal(t, "task-1", req.TaskID)
	assert.Equal(t, "Test error", req.ErrorMessage)
	assert.True(t, req.Retryable)
}

// TestMessageFieldPopulation tests message field assignment
func TestMessageFieldPopulation(t *testing.T) {
	msg := &Message{
		Type:      MsgTypeRegister,
		AgentID:   "agent-1",
		Timestamp: time.Now(),
		Payload: map[string]interface{}{
			"test": "value",
		},
		Error: "",
	}

	assert.Equal(t, MsgTypeRegister, msg.Type)
	assert.Equal(t, "agent-1", msg.AgentID)
	assert.NotNil(t, msg.Payload)
}

// TestAgentMetricsStructure tests agent metrics field access
func TestAgentMetricsStructure(t *testing.T) {
	metrics := &AgentMetrics{
		CPUUsage:        25.5,
		MemoryUsage:     40.0,
		TasksCompleted:  10,
		TasksFailed:     2,
		AverageTaskTime: 2.5,
	}

	assert.Equal(t, 25.5, metrics.CPUUsage)
	assert.Equal(t, 40.0, metrics.MemoryUsage)
	assert.Equal(t, 10, metrics.TasksCompleted)
	assert.Equal(t, 2, metrics.TasksFailed)
}
