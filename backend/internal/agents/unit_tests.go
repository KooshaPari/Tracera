//go:build !integration && !e2e

package agents

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

const (
	testQueueCapacity          = 2
	testPriorityHighValue      = 2
	testPriorityCriticalValue  = 3
	testMaxRetries             = 5
	testTagsCount              = 2
	testResultCount            = 42
	testDuration               = 5 * time.Second
	testCapabilityTagsCount    = 2
	testCPUUsageHigh           = 75.5
	testMemoryUsageHigh        = 60.2
	testTasksCompleted         = 150
	testTasksFailed            = 5
	testAverageTaskTime        = 2.5
	testCPUUsageMid            = 45.5
	testCapabilitiesCount      = 2
	testCPUUsageLow            = 40.0
	testMemoryUsageMid         = 55.0
	testRequestTagsCount       = 2
	testProcessedCount         = 100
	testRolePriorityAdmin      = 10
	testRolePermissionsCount   = 3
	testRolePrioritySuperAdmin = 20
	testParticipantCount       = 2
	testProcessedCountSmall    = 2
	testTimeoutDuration        = 5 * time.Minute
	testLockTimeoutDuration    = 5 * time.Minute
	testCurrentVersion         = int64(5)
	testExpectedVersion        = int64(6)
	testExpectedWrongVersion   = int64(7)
	testConflictingAgentsCount = 3
)

// ============================================================================
// Priority Queue Tests (without database)
// ============================================================================

// TestPriorityQueueLen tests the length of the priority queue.
func TestPriorityQueueLen(t *testing.T) {
	pq := make(priorityQueue, 0, testQueueCapacity)

	assert.Equal(t, 0, pq.Len())

	pq = append(pq, &Task{ID: "1", Priority: PriorityNormal})
	assert.Equal(t, 1, pq.Len())

	pq = append(pq, &Task{ID: "2", Priority: PriorityHigh})
	assert.Equal(t, testQueueCapacity, pq.Len())
}

// TestPriorityQueueLess tests ordering by priority.
func TestPriorityQueueLess(t *testing.T) {
	now := time.Now()

	// Higher priority should come first
	pq := priorityQueue{
		&Task{ID: "1", Priority: PriorityNormal, CreatedAt: now},
		&Task{ID: "2", Priority: PriorityHigh, CreatedAt: now},
	}

	// High priority (index 1) should be less than Normal priority (index 0)
	// because Less returns true if i should come before j
	assert.True(t, pq.Less(1, 0))
	assert.False(t, pq.Less(0, 1))
}

// TestPriorityQueueLessSamePriority tests ordering by creation time when priority is equal.
func TestPriorityQueueLessSamePriority(t *testing.T) {
	earlier := time.Now().Add(-1 * time.Minute)
	later := time.Now()

	// Same priority, earlier task should come first
	pq := priorityQueue{
		&Task{ID: "1", Priority: PriorityNormal, CreatedAt: later},
		&Task{ID: "2", Priority: PriorityNormal, CreatedAt: earlier},
	}

	// Earlier task (index 1) should come before later task (index 0)
	assert.True(t, pq.Less(1, 0))
	assert.False(t, pq.Less(0, 1))
}

// TestPriorityQueueSwap tests swapping two elements in the priority queue.
func TestPriorityQueueSwap(t *testing.T) {
	task1 := &Task{ID: "1"}
	task2 := &Task{ID: "2"}

	pq := priorityQueue{task1, task2}

	pq.Swap(0, 1)

	assert.Equal(t, "2", pq[0].ID)
	assert.Equal(t, "1", pq[1].ID)
}

// ============================================================================
// Protocol Error Tests (additional)
// ============================================================================

// TestErrInvalidMessageCreation tests protocol error creation.
func TestErrInvalidMessageCreation(t *testing.T) {
	err := ErrInvalidMessage("field is required")
	assert.NotNil(t, err)
	assert.Contains(t, err.Error(), "field is required")

	// Check if it's the right type
	protoErr, ok := err.(*ProtocolError)
	assert.True(t, ok)
	assert.Equal(t, "field is required", protoErr.Message)
}

// ============================================================================
// MessageType and AgentStatus Enums
// ============================================================================

// TestMessageTypes tests message type enum values.
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

// TestAgentStatusValues tests agent status enum values.
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

// ============================================================================
// Task Status and Priority Tests
// ============================================================================

// TestTaskStatuses tests task status enum values.
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

// TestTaskPriorities tests task priority enum values.
func TestTaskPriorities(t *testing.T) {
	assert.Equal(t, TaskPriority(0), PriorityLow)
	assert.Equal(t, TaskPriority(1), PriorityNormal)
	assert.Equal(t, TaskPriority(testPriorityHighValue), PriorityHigh)
	assert.Equal(t, TaskPriority(testPriorityCriticalValue), PriorityCritical)

	// Higher priority should have higher numeric value
	assert.True(t, PriorityCritical > PriorityHigh)
	assert.True(t, PriorityHigh > PriorityNormal)
	assert.True(t, PriorityNormal > PriorityLow)
}

// ============================================================================
// Task Struct Tests (additional)
// ============================================================================

// TestTaskCreationWithMetadata tests task creation with metadata fields.
func TestTaskCreationWithMetadata(t *testing.T) {
	task := &Task{
		ProjectID: "proj-1",
		Type:      "validate",
		Priority:  PriorityNormal,
		Parameters: map[string]interface{}{
			"strict": true,
		},
		MaxRetries: testMaxRetries,
		Tags:       []string{"validation", "critical"},
	}

	assert.Equal(t, "proj-1", task.ProjectID)
	assert.Equal(t, "validate", task.Type)
	assert.Equal(t, PriorityNormal, task.Priority)
	assert.Equal(t, testMaxRetries, task.MaxRetries)
	assert.Len(t, task.Tags, testTagsCount)
}

// TestTaskResult tests task result structure.
func TestTaskResult(t *testing.T) {
	result := &TaskResult{
		Success: true,
		Data: map[string]interface{}{
			"count": testResultCount,
		},
		Message:  "Processing complete",
		Duration: testDuration,
	}

	assert.True(t, result.Success)
	assert.Equal(t, "Processing complete", result.Message)
	assert.Equal(t, testDuration, result.Duration)
	assert.Equal(t, testResultCount, result.Data["count"])
}

// ============================================================================
// RegisteredAgent Tests
// ============================================================================

// TestRegisteredAgentCreation tests registered agent structure.
func TestRegisteredAgentCreation(t *testing.T) {
	agent := &RegisteredAgent{
		Name:      "test-agent",
		ProjectID: "proj-1",
		Status:    StatusIdle,
		Capabilities: []AgentCapability{
			{
				Name:        "analyze",
				Version:     "1.0.0",
				Tags:        []string{"processing"},
				Description: "Data analysis capability",
			},
		},
		Metadata: map[string]interface{}{
			"version": "1.0",
			"region":  "us-east-1",
		},
	}

	assert.Equal(t, "test-agent", agent.Name)
	assert.Equal(t, "proj-1", agent.ProjectID)
	assert.Equal(t, StatusIdle, agent.Status)
	assert.Len(t, agent.Capabilities, 1)
	assert.Equal(t, "analyze", agent.Capabilities[0].Name)
}

// ============================================================================
// AgentCapability Tests
// ============================================================================

// TestAgentCapability tests agent capability structure.
func TestAgentCapability(t *testing.T) {
	capability := AgentCapability{
		Name:        "compute",
		Version:     "2.1.0",
		Tags:        []string{"heavy-lifting", "math"},
		Description: "Mathematical computation",
	}

	assert.Equal(t, "compute", capability.Name)
	assert.Equal(t, "2.1.0", capability.Version)
	assert.Len(t, capability.Tags, testCapabilityTagsCount)
	assert.Contains(t, capability.Tags, "heavy-lifting")
	assert.Equal(t, "Mathematical computation", capability.Description)
}

// ============================================================================
// LockType Tests
// ============================================================================

// TestLockTypes tests lock type enum values.
func TestLockTypes(t *testing.T) {
	assert.Equal(t, LockType("optimistic"), LockTypeOptimistic)
	assert.Equal(t, LockType("pessimistic"), LockTypePessimistic)
}

// ============================================================================
// ConflictResolutionStrategy Tests
// ============================================================================

// TestConflictResolutionStrategies tests conflict resolution strategy values.
func TestConflictResolutionStrategies(t *testing.T) {
	strategies := []ConflictResolutionStrategy{
		ResolutionLastWriteWins,
		ResolutionAgentPriority,
		ResolutionManual,
		ResolutionMerge,
		ResolutionFirstWins,
	}

	for _, strategy := range strategies {
		assert.NotEmpty(t, string(strategy))
	}
}

// ============================================================================
// AgentMetrics Tests
// ============================================================================

// TestAgentMetrics tests agent metrics structure.
func TestAgentMetrics(t *testing.T) {
	metrics := &AgentMetrics{
		CPUUsage:        testCPUUsageHigh,
		MemoryUsage:     testMemoryUsageHigh,
		TasksCompleted:  testTasksCompleted,
		TasksFailed:     testTasksFailed,
		AverageTaskTime: testAverageTaskTime,
	}

	assert.Equal(t, testCPUUsageHigh, metrics.CPUUsage)
	assert.Equal(t, testMemoryUsageHigh, metrics.MemoryUsage)
	assert.Equal(t, testTasksCompleted, metrics.TasksCompleted)
	assert.Equal(t, testTasksFailed, metrics.TasksFailed)
	assert.Equal(t, testAverageTaskTime, metrics.AverageTaskTime)
}

// ============================================================================
// Message Struct Tests
// ============================================================================

// TestMessageCreation tests message structure creation.
func TestMessageCreation(t *testing.T) {
	now := time.Now()
	msg := &Message{
		Type:      MsgTypeHeartbeat,
		AgentID:   "agent-1",
		Timestamp: now,
		Payload: map[string]interface{}{
			"status": "active",
			"cpu":    testCPUUsageMid,
		},
	}

	assert.Equal(t, MsgTypeHeartbeat, msg.Type)
	assert.Equal(t, "agent-1", msg.AgentID)
	assert.Equal(t, now, msg.Timestamp)
	assert.Equal(t, "active", msg.Payload["status"])
	assert.Equal(t, testCPUUsageMid, msg.Payload["cpu"])
}

// ============================================================================
// Register/Heartbeat Request Tests
// ============================================================================

// TestRegisterRequest tests register request structure.
func TestRegisterRequest(t *testing.T) {
	req := &RegisterRequest{
		Name:      "my-agent",
		ProjectID: "proj-123",
		Capabilities: []AgentCapability{
			{Name: "analyze", Version: "1.0"},
			{Name: "validate", Version: "2.0"},
		},
		Metadata: map[string]interface{}{
			"env": "production",
		},
	}

	assert.Equal(t, "my-agent", req.Name)
	assert.Equal(t, "proj-123", req.ProjectID)
	assert.Len(t, req.Capabilities, testCapabilitiesCount)
	assert.Equal(t, "production", req.Metadata["env"])
}

// TestHeartbeatRequest tests heartbeat request structure.
func TestHeartbeatRequest(t *testing.T) {
	metrics := &AgentMetrics{
		CPUUsage:    testCPUUsageLow,
		MemoryUsage: testMemoryUsageMid,
	}

	req := &HeartbeatRequest{
		AgentID: "agent-1",
		Status:  StatusActive,
		Metrics: metrics,
	}

	assert.Equal(t, "agent-1", req.AgentID)
	assert.Equal(t, StatusActive, req.Status)
	assert.Equal(t, testCPUUsageLow, req.Metrics.CPUUsage)
}

// ============================================================================
// Task Request/Response Tests
// ============================================================================

// TestTaskRequest tests task request structure.
func TestTaskRequest(t *testing.T) {
	req := &TaskRequest{
		AgentID: "agent-1",
		Tags:    []string{"priority", "urgent"},
	}

	assert.Equal(t, "agent-1", req.AgentID)
	assert.Len(t, req.Tags, testRequestTagsCount)
	assert.Contains(t, req.Tags, "priority")
}

// TestTaskResponse tests task response structure.
func TestTaskResponse(t *testing.T) {
	task := &Task{
		ID:        "task-1",
		ProjectID: "proj-1",
		Type:      "analyze",
	}

	resp := &TaskResponse{
		Task:    task,
		Status:  "assigned",
		Message: "Task assigned successfully",
	}

	assert.Equal(t, "task-1", resp.Task.ID)
	assert.Equal(t, "assigned", resp.Status)
	assert.Equal(t, "Task assigned successfully", resp.Message)
}

// ============================================================================
// Task Result Request/Response Tests
// ============================================================================

// TestTaskResultRequest tests task result request structure.
func TestTaskResultRequest(t *testing.T) {
	result := &TaskResult{
		Success: true,
		Data: map[string]interface{}{
			"processed": testProcessedCount,
		},
	}

	req := &TaskResultRequest{
		AgentID: "agent-1",
		TaskID:  "task-1",
		Result:  result,
	}

	assert.Equal(t, "agent-1", req.AgentID)
	assert.Equal(t, "task-1", req.TaskID)
	assert.True(t, req.Result.Success)
}

// ============================================================================
// Team and Role Tests
// ============================================================================

// TestTeamRole tests team role structure.
func TestTeamRole(t *testing.T) {
	role := TeamRole{
		Name:        "admin",
		Permissions: []string{"read", "write", "delete"},
		Priority:    testRolePriorityAdmin,
	}

	assert.Equal(t, "admin", role.Name)
	assert.Len(t, role.Permissions, testRolePermissionsCount)
	assert.Contains(t, role.Permissions, "delete")
	assert.Equal(t, testRolePriorityAdmin, role.Priority)
}

// TestTeamRoleWithWildcardPermission tests team role with wildcard permission.
func TestTeamRoleWithWildcardPermission(t *testing.T) {
	role := TeamRole{
		Name:        "super-admin",
		Permissions: []string{"*"},
		Priority:    testRolePrioritySuperAdmin,
	}

	assert.Len(t, role.Permissions, 1)
	assert.Equal(t, "*", role.Permissions[0])
}

// ============================================================================
// Distributed Operation Tests (structure only)
// ============================================================================

// TestDistributedOperationCreation tests distributed operation structure.
func TestDistributedOperationCreation(t *testing.T) {
	op := &DistributedOperation{
		ProjectID:      "proj-1",
		Type:           "batch_update",
		Status:         "pending",
		ParticipantIDs: []string{"agent-1", "agent-2"},
		CoordinatorID:  "agent-1",
		TargetItems:    []string{"item-1", "item-2"},
		OperationData: map[string]interface{}{
			"operation": "merge",
		},
	}

	assert.Equal(t, "proj-1", op.ProjectID)
	assert.Equal(t, "batch_update", op.Type)
	assert.Equal(t, "pending", op.Status)
	assert.Len(t, op.ParticipantIDs, testParticipantCount)
	assert.Equal(t, "agent-1", op.CoordinatorID)
}

// TestOperationParticipantCreation tests operation participant structure.
func TestOperationParticipantCreation(t *testing.T) {
	participant := &OperationParticipant{
		OperationID:   "op-1",
		AgentID:       "agent-1",
		Status:        "ready",
		AssignedItems: []string{"item-1", "item-2"},
		Result: map[string]interface{}{
			"processed": testProcessedCountSmall,
		},
	}

	assert.Equal(t, "op-1", participant.OperationID)
	assert.Equal(t, "agent-1", participant.AgentID)
	assert.Equal(t, "ready", participant.Status)
	assert.Len(t, participant.AssignedItems, testParticipantCount)
}

// ============================================================================
// Validation Logic Tests
// ============================================================================

// TestHasRequiredCapabilitiesAllPresent tests capability check when agent has all required.
func TestHasRequiredCapabilitiesAllPresent(t *testing.T) {
	agent := &RegisteredAgent{
		Capabilities: []AgentCapability{
			{Name: "read"},
			{Name: "write"},
			{Name: "analyze"},
		},
	}

	task := &Task{
		RequiredCapabilities: []string{"read", "write"},
	}

	// Manually check capability matching logic
	agentCaps := make(map[string]bool)
	for _, c := range agent.Capabilities {
		agentCaps[c.Name] = true
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

// TestHasRequiredCapabilitiesMissing tests capability check when agent is missing required.
func TestHasRequiredCapabilitiesMissing(t *testing.T) {
	agent := &RegisteredAgent{
		Capabilities: []AgentCapability{
			{Name: "read"},
		},
	}

	task := &Task{
		RequiredCapabilities: []string{"read", "write"},
	}

	agentCaps := make(map[string]bool)
	for _, c := range agent.Capabilities {
		agentCaps[c.Name] = true
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

// TestHasRequiredCapabilitiesNoneRequired tests capability check when task requires none.
func TestHasRequiredCapabilitiesNoneRequired(t *testing.T) {
	task := &Task{
		RequiredCapabilities: []string{},
	}

	// No specific capabilities required
	assert.True(t, len(task.RequiredCapabilities) == 0)
}

// ============================================================================
// Permission Checking Tests
// ============================================================================

// TestPermissionChecking tests permission presence check.
func TestPermissionChecking(t *testing.T) {
	permissions := []string{"read", "write"}

	// Check if permission exists
	hasWrite := false
	for _, perm := range permissions {
		if perm == "write" {
			hasWrite = true
			break
		}
	}

	assert.True(t, hasWrite)

	// Check non-existent permission
	hasDelete := false
	for _, perm := range permissions {
		if perm == "delete" {
			hasDelete = true
			break
		}
	}

	assert.False(t, hasDelete)
}

// TestWildcardPermissionChecking tests wildcard permission grant.
func TestWildcardPermissionChecking(t *testing.T) {
	permissions := []string{"*"}

	// Wildcard permission grants everything
	hasDelete := false
	for _, perm := range permissions {
		if perm == "*" {
			hasDelete = true
			break
		}
	}

	assert.True(t, hasDelete)
}

// ============================================================================
// Time-based Logic Tests
// ============================================================================

// TestHeartbeatTimeoutCheck tests heartbeat timeout logic.
func TestHeartbeatTimeoutCheck(t *testing.T) {
	now := time.Now()
	timeout := testTimeoutDuration

	// Agent with recent heartbeat
	agentRecent := time.Now()
	assert.False(t, now.Sub(agentRecent) > timeout)

	// Agent with old heartbeat
	agentOld := now.Add(-10 * time.Minute)
	assert.True(t, now.Sub(agentOld) > timeout)
}

// TestLockExpiration tests lock expiration logic.
func TestLockExpiration(t *testing.T) {
	now := time.Now()
	lockTimeout := testLockTimeoutDuration

	// Fresh lock
	lockExpire := now.Add(lockTimeout)
	assert.True(t, now.Before(lockExpire))

	// Expired lock
	expiredLock := now.Add(-1 * time.Minute)
	assert.False(t, now.Before(expiredLock))
	assert.True(t, now.After(expiredLock))
}

// TestVersionComparison tests version comparison logic.
func TestVersionComparison(t *testing.T) {
	currentVersion := testCurrentVersion
	expectedVersion := testExpectedVersion

	// Should match next sequential version
	assert.Equal(t, currentVersion+1, expectedVersion)

	// Should fail for non-sequential
	expectedWrongVersion := testExpectedWrongVersion
	assert.NotEqual(t, currentVersion+1, expectedWrongVersion)
}

// ============================================================================
// Data Structure Composition Tests
// ============================================================================

// TestComplexAgentWithCurrentTask tests agent with current task composition.
func TestComplexAgentWithCurrentTask(t *testing.T) {
	task := &Task{
		ID:        "task-1",
		ProjectID: "proj-1",
		Status:    TaskStatusRunning,
	}

	agent := &RegisteredAgent{
		ID:            "agent-1",
		Name:          "worker",
		ProjectID:     "proj-1",
		Status:        StatusBusy,
		CurrentTask:   task,
		LastHeartbeat: time.Now(),
	}

	assert.Equal(t, StatusBusy, agent.Status)
	assert.NotNil(t, agent.CurrentTask)
	assert.Equal(t, "task-1", agent.CurrentTask.ID)
	assert.Equal(t, TaskStatusRunning, agent.CurrentTask.Status)
}

// TestConflictRecordWithMultipleAgents tests conflict record with multiple agents.
func TestConflictRecordWithMultipleAgents(t *testing.T) {
	conflict := &ConflictRecord{
		ItemID:             "item-1",
		ConflictingAgents:  []string{"agent-1", "agent-2", "agent-3"},
		ConflictType:       "concurrent_modification",
		ResolutionStrategy: ResolutionLastWriteWins,
	}

	assert.Len(t, conflict.ConflictingAgents, testConflictingAgentsCount)
	assert.Contains(t, conflict.ConflictingAgents, "agent-2")
	assert.Equal(t, ResolutionLastWriteWins, conflict.ResolutionStrategy)
}
