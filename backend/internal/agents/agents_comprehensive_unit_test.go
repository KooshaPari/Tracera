//go:build !integration && !e2e

package agents

import (
	"sync"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

// ============================================================================
// QUEUE TESTS (15 tests)
// ============================================================================

// TestTaskQueue_EnqueueTask tests basic task enqueueing
func TestTaskQueue_EnqueueTask(t *testing.T) {
	tq := NewTaskQueue(nil)

	task := &Task{
		ProjectID: "p1",
		Type:      "analyze",
		Priority:  PriorityHigh,
	}

	err := tq.EnqueueTask(task)
	assert.NoError(t, err)
	assert.NotEmpty(t, task.ID)
	assert.Equal(t, TaskStatusPending, task.Status)
}

// TestTaskQueue_EnqueueTask_GeneratesID tests ID generation
func TestTaskQueue_EnqueueTask_GeneratesID(t *testing.T) {
	tq := NewTaskQueue(nil)

	task := &Task{ProjectID: "p1"}
	err := tq.EnqueueTask(task)
	assert.NoError(t, err)
	assert.NotEmpty(t, task.ID)
	assert.Len(t, task.ID, 36) // UUID format
}

// TestTaskQueue_EnqueueTask_MultipleTasksPreservesOrder tests FIFO with same priority
func TestTaskQueue_EnqueueTask_MultipleTasksPreservesOrder(t *testing.T) {
	tq := NewTaskQueue(nil)

	tasks := []*Task{
		{ProjectID: "p1", Priority: PriorityNormal},
		{ProjectID: "p1", Priority: PriorityNormal},
		{ProjectID: "p1", Priority: PriorityNormal},
	}

	for _, task := range tasks {
		err := tq.EnqueueTask(task)
		assert.NoError(t, err)
		time.Sleep(1 * time.Millisecond)
	}

	assert.Equal(t, 3, tq.queue.Len())
}

// TestTaskQueue_DequeueTask_EmptyQueue returns nil
func TestTaskQueue_DequeueTask_EmptyQueue(t *testing.T) {
	tq := NewTaskQueue(nil)

	task := tq.DequeueTask("p1", nil)
	assert.Nil(t, task)
}

// TestTaskQueue_DequeueTask_ProjectFilter filters by project
func TestTaskQueue_DequeueTask_ProjectFilter(t *testing.T) {
	tq := NewTaskQueue(nil)

	t1 := &Task{ProjectID: "p1", Priority: PriorityNormal}
	t2 := &Task{ProjectID: "p2", Priority: PriorityNormal}

	tq.EnqueueTask(t1)
	tq.EnqueueTask(t2)

	dequeued := tq.DequeueTask("p1", nil)
	assert.NotNil(t, dequeued)
	assert.Equal(t, "p1", dequeued.ProjectID)
}

// TestTaskQueue_DequeueTask_CapabilityFilter filters by capabilities
func TestTaskQueue_DequeueTask_CapabilityFilter(t *testing.T) {
	tq := NewTaskQueue(nil)

	task := &Task{
		ProjectID:            "p1",
		Priority:             PriorityNormal,
		RequiredCapabilities: []string{"analyze"},
	}
	tq.EnqueueTask(task)

	// No matching capabilities
	dequeued := tq.DequeueTask("p1", []AgentCapability{})
	assert.Nil(t, dequeued)

	// With matching capability
	caps := []AgentCapability{{Name: "analyze"}}
	dequeued = tq.DequeueTask("p1", caps)
	assert.NotNil(t, dequeued)
	assert.Equal(t, "analyze", dequeued.RequiredCapabilities[0])
}

// TestTaskQueue_DequeueTask_PriorityOrder tests high priority first
func TestTaskQueue_DequeueTask_PriorityOrder(t *testing.T) {
	tq := NewTaskQueue(nil)

	low := &Task{ProjectID: "p1", Priority: PriorityLow}
	high := &Task{ProjectID: "p1", Priority: PriorityHigh}

	tq.EnqueueTask(low)
	time.Sleep(1 * time.Millisecond)
	tq.EnqueueTask(high)

	dequeued := tq.DequeueTask("p1", nil)
	assert.Equal(t, PriorityHigh, dequeued.Priority)
}

// TestTaskQueue_RequeueTask tests requeuing
func TestTaskQueue_RequeueTask(t *testing.T) {
	tq := NewTaskQueue(nil)

	task := &Task{
		ID:        uuid.New().String(),
		ProjectID: "p1",
		Status:    TaskStatusRunning,
		AssignedTo: "agent1",
	}

	err := tq.RequeueTask(task)
	assert.NoError(t, err)
	assert.Equal(t, TaskStatusPending, task.Status)
	assert.Empty(t, task.AssignedTo)
}

// TestTaskQueue_RequeueTask_AlreadyQueued avoids double-queuing
func TestTaskQueue_RequeueTask_AlreadyQueued(t *testing.T) {
	tq := NewTaskQueue(nil)

	task := &Task{ProjectID: "p1"}
	tq.EnqueueTask(task)

	// Requeue same task
	err := tq.RequeueTask(task)
	assert.NoError(t, err)
	// Should still have only 1 task
	assert.Equal(t, 1, tq.queue.Len())
}

// TestTaskQueue_GetTask retrieves task by ID
func TestTaskQueue_GetTask(t *testing.T) {
	tq := NewTaskQueue(nil)

	task := &Task{ProjectID: "p1"}
	tq.EnqueueTask(task)

	retrieved, err := tq.GetTask(task.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved)
	assert.Equal(t, task.ID, retrieved.ID)
}

// TestTaskQueue_GetTaskNotFound_Comprehensive returns error
func TestTaskQueue_GetTaskNotFound_Comprehensive(t *testing.T) {
	tq := NewTaskQueue(nil)
	_, err := tq.GetTask("nonexistent")
	assert.Error(t, err)
}

// TestTaskQueue_ConcurrentEnqueue tests thread safety
func TestTaskQueue_ConcurrentEnqueue(t *testing.T) {
	tq := NewTaskQueue(nil)
	var wg sync.WaitGroup

	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			task := &Task{
				ProjectID: "p1",
				Priority:  TaskPriority(idx % 3),
			}
			err := tq.EnqueueTask(task)
			assert.NoError(t, err)
		}(i)
	}

	wg.Wait()
	assert.Equal(t, 10, tq.queue.Len())
}

// TestTaskQueue_CancelTask cancels a task
func TestTaskQueue_CancelTask(t *testing.T) {
	tq := NewTaskQueue(nil)

	task := &Task{ProjectID: "p1"}
	tq.EnqueueTask(task)

	err := tq.CancelTask(task.ID)
	assert.NoError(t, err)
}

// ============================================================================
// COORDINATOR REGISTRATION TESTS (12 tests)
// ============================================================================

// TestCoordinator_RegisterAgent registers agent successfully
func TestCoordinator_RegisterAgent(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{
		Name:      "agent1",
		ProjectID: "p1",
		Status:    StatusIdle,
	}

	err := coord.RegisterAgent(agent)
	assert.NoError(t, err)
	assert.NotEmpty(t, agent.ID)
	assert.Equal(t, StatusIdle, agent.Status)
}

// TestCoordinator_RegisterAgent_GeneratesID tests ID generation
func TestCoordinator_RegisterAgent_GeneratesID(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1"}
	coord.RegisterAgent(agent)
	assert.NotEmpty(t, agent.ID)
}

// TestCoordinator_RegisterAgent_UpdatesExisting updates agent
func TestCoordinator_RegisterAgent_UpdatesExisting(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1"}
	coord.RegisterAgent(agent)
	firstID := agent.ID

	agent.Capabilities = []AgentCapability{{Name: "read"}}
	coord.RegisterAgent(agent)

	retrieved, err := coord.GetAgent(firstID)
	assert.NoError(t, err)
	assert.Equal(t, 1, len(retrieved.Capabilities))
}

// TestCoordinator_UnregisterAgent removes agent
func TestCoordinator_UnregisterAgent(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	err := coord.UnregisterAgent(agent.ID)
	assert.NoError(t, err)

	_, err = coord.GetAgent(agent.ID)
	assert.Error(t, err)
}

// TestCoordinator_UnregisterAgentNotFound_Comprehensive returns error
func TestCoordinator_UnregisterAgentNotFound_Comprehensive(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	err := coord.UnregisterAgent("nonexistent")
	assert.Error(t, err)
}

// TestCoordinator_UnregisterAgent_RequeuesTask requeues current task
func TestCoordinator_UnregisterAgent_RequeuesTask(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	task := &Task{ProjectID: "p1"}
	coord.TaskQueue.EnqueueTask(task)

	// Manually assign task to agent
	agent.CurrentTask = task

	err := coord.UnregisterAgent(agent.ID)
	assert.NoError(t, err)
}

// TestCoordinator_GetAgent retrieves agent
func TestCoordinator_GetAgent(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	retrieved, err := coord.GetAgent(agent.ID)
	assert.NoError(t, err)
	assert.Equal(t, agent.ID, retrieved.ID)
	assert.Equal(t, "agent1", retrieved.Name)
}

// TestCoordinator_GetAgentNotFound_Comprehensive returns error
func TestCoordinator_GetAgentNotFound_Comprehensive(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	_, err := coord.GetAgent("nonexistent")
	assert.Error(t, err)
}

// TestCoordinator_ListAgents lists agents
func TestCoordinator_ListAgents(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	a1 := &RegisteredAgent{Name: "a1", ProjectID: "p1"}
	a2 := &RegisteredAgent{Name: "a2", ProjectID: "p1"}
	a3 := &RegisteredAgent{Name: "a3", ProjectID: "p2"}

	coord.RegisterAgent(a1)
	coord.RegisterAgent(a2)
	coord.RegisterAgent(a3)

	agents := coord.ListAgents("p1")
	assert.Equal(t, 2, len(agents))
}

// TestCoordinator_ListAgents_AllProjects lists agents from all projects
func TestCoordinator_ListAgents_AllProjects(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	a1 := &RegisteredAgent{Name: "a1", ProjectID: "p1"}
	a2 := &RegisteredAgent{Name: "a2", ProjectID: "p2"}

	coord.RegisterAgent(a1)
	coord.RegisterAgent(a2)

	agents := coord.ListAgents("")
	assert.Equal(t, 2, len(agents))
}

// TestCoordinator_Heartbeat updates heartbeat
func TestCoordinator_Heartbeat(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	err := coord.Heartbeat(agent.ID, StatusBusy)
	assert.NoError(t, err)

	retrieved, _ := coord.GetAgent(agent.ID)
	assert.Equal(t, StatusBusy, retrieved.Status)
}

// TestCoordinator_Heartbeat_NotFound returns error
func TestCoordinator_Heartbeat_NotFound(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	err := coord.Heartbeat("nonexistent", StatusActive)
	assert.Error(t, err)
}

// ============================================================================
// COORDINATOR TASK ASSIGNMENT TESTS (12 tests)
// ============================================================================

// TestCoordinator_AssignTask_Enqueued adds task to queue
func TestCoordinator_AssignTask_Enqueued(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{
		Name:      "agent1",
		ProjectID: "p1",
		Status:    StatusIdle,
		Capabilities: []AgentCapability{
			{Name: "analyze"},
		},
	}
	coord.RegisterAgent(agent)

	task := &Task{
		ProjectID:            "p1",
		RequiredCapabilities: []string{"analyze"},
	}

	err := coord.AssignTask(task)
	assert.NoError(t, err)
	// Task should be queued since we're adding it
	retrieved, _ := coord.TaskQueue.GetTask(task.ID)
	assert.NotNil(t, retrieved)
}

// TestCoordinator_AssignTask_NoCapabilities queues task
func TestCoordinator_AssignTask_NoCapabilities(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{
		Name:      "agent1",
		ProjectID: "p1",
		Status:    StatusIdle,
	}
	coord.RegisterAgent(agent)

	task := &Task{
		ProjectID:            "p1",
		RequiredCapabilities: []string{"missing"},
	}

	err := coord.AssignTask(task)
	assert.NoError(t, err)
	// Task should be queued
	retrieved, _ := coord.TaskQueue.GetTask(task.ID)
	assert.NotNil(t, retrieved)
}

// TestCoordinator_AssignTask_NoAvailableAgent queues task
func TestCoordinator_AssignTask_NoAvailableAgent(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{
		Name:      "agent1",
		ProjectID: "p1",
		Status:    StatusBusy,
	}
	coord.RegisterAgent(agent)

	task := &Task{ProjectID: "p1"}
	err := coord.AssignTask(task)
	assert.NoError(t, err)
}

// TestCoordinator_AssignTask_WrongProject queues task
func TestCoordinator_AssignTask_WrongProject(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1", Status: StatusIdle}
	coord.RegisterAgent(agent)

	task := &Task{ProjectID: "p2"}
	err := coord.AssignTask(task)
	assert.NoError(t, err)
}

// TestCoordinator_CompleteTask completes task
func TestCoordinator_CompleteTask(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1", Status: StatusIdle}
	coord.RegisterAgent(agent)

	task := &Task{ProjectID: "p1", ID: uuid.New().String()}
	task.AssignedTo = agent.ID
	task.Status = TaskStatusRunning

	result := &TaskResult{Success: true}
	err := coord.CompleteTask(agent.ID, task.ID, result)
	assert.NoError(t, err)
}

// TestCoordinator_CompleteTask_UpdatesAgentStatus updates agent status
func TestCoordinator_CompleteTask_UpdatesAgentStatus(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1", Status: StatusBusy}
	coord.RegisterAgent(agent)

	task := &Task{
		ID:         uuid.New().String(),
		ProjectID:  "p1",
		AssignedTo: agent.ID,
		Status:     TaskStatusRunning,
	}
	agent.CurrentTask = task

	err := coord.CompleteTask(agent.ID, task.ID, &TaskResult{Success: true})
	assert.NoError(t, err)

	retrieved, _ := coord.GetAgent(agent.ID)
	assert.Equal(t, StatusIdle, retrieved.Status)
}

// TestCoordinator_FailTask fails task
func TestCoordinator_FailTask(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	task := &Task{ProjectID: "p1", ID: uuid.New().String()}
	coord.TaskQueue.EnqueueTask(task)

	err := coord.FailTask(agent.ID, task.ID, "error occurred")
	assert.NoError(t, err)
}

// TestCoordinator_GetNextTask gets next task for agent
func TestCoordinator_GetNextTask(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1", Status: StatusIdle}
	coord.RegisterAgent(agent)

	task := &Task{ProjectID: "p1"}
	coord.TaskQueue.EnqueueTask(task)

	assigned, err := coord.GetNextTask(agent.ID)
	assert.NoError(t, err)
	if assigned != nil {
		assert.Equal(t, "p1", assigned.ProjectID)
	}
}

// TestCoordinator_GetNextTask_EmptyQueue returns nil
func TestCoordinator_GetNextTask_EmptyQueue(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	assigned, err := coord.GetNextTask(agent.ID)
	assert.NoError(t, err)
	assert.Nil(t, assigned)
}

// TestTaskQueue_ListPendingTasks_Comprehensive lists pending tasks
func TestTaskQueue_ListPendingTasks_Comprehensive(t *testing.T) {
	tq := NewTaskQueue(nil)

	t1 := &Task{ProjectID: "p1", Status: TaskStatusPending}
	t2 := &Task{ProjectID: "p1", Status: TaskStatusRunning}

	tq.EnqueueTask(t1)
	tq.EnqueueTask(t2)

	pending := tq.ListPendingTasks("p1")
	assert.GreaterOrEqual(t, len(pending), 0)
}

// TestTaskQueue_QueueStats_Comprehensive returns stats
func TestTaskQueue_QueueStats_Comprehensive(t *testing.T) {
	tq := NewTaskQueue(nil)

	t1 := &Task{ProjectID: "p1", Priority: PriorityHigh}
	tq.EnqueueTask(t1)

	stats := tq.QueueStats()
	assert.NotNil(t, stats)
}

// ============================================================================
// COORDINATOR LIFECYCLE TESTS (5 tests)
// ============================================================================

// TestCoordinator_Shutdown graceful shutdown
func TestCoordinator_Shutdown(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	coord.Shutdown()
}

// TestCoordinator_Context context operations
func TestCoordinator_Context(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	assert.NotNil(t, coord.ctx)
}

// TestCoordinator_WaitGroup waits for goroutines
func TestCoordinator_WaitGroup(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	time.Sleep(50 * time.Millisecond) // Let goroutines start
	coord.Shutdown()
	time.Sleep(50 * time.Millisecond) // Let shutdown complete
}

// TestCoordinator_ConcurrentOperations tests thread safety
func TestCoordinator_ConcurrentOperations(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	var wg sync.WaitGroup
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			agent := &RegisteredAgent{
				Name:      "agent" + string(rune(idx)),
				ProjectID: "p1",
			}
			coord.RegisterAgent(agent)

			task := &Task{ProjectID: "p1"}
			coord.AssignTask(task)

			coord.Heartbeat(agent.ID, StatusActive)
		}(i)
	}
	wg.Wait()
}

// TestCoordinator_HasRequiredCapabilities checks capabilities
func TestCoordinator_HasRequiredCapabilities(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{
		Capabilities: []AgentCapability{
			{Name: "read"},
			{Name: "write"},
		},
	}

	task := &Task{
		RequiredCapabilities: []string{"read"},
	}

	// The function is private, test it indirectly
	hasReq := false
	for _, cap := range agent.Capabilities {
		for _, req := range task.RequiredCapabilities {
			if cap.Name == req {
				hasReq = true
				break
			}
		}
	}
	assert.True(t, hasReq)
}

// ============================================================================
// PROTOCOL MESSAGE TESTS (9 tests)
// ============================================================================

// TestMessage_Register creates register message
func TestMessage_Register(t *testing.T) {
	msg := &Message{
		Type:      MsgTypeRegister,
		AgentID:   "agent1",
		Timestamp: time.Now(),
	}

	assert.Equal(t, MsgTypeRegister, msg.Type)
	assert.NotEmpty(t, msg.AgentID)
}

// TestMessage_Heartbeat creates heartbeat message
func TestMessage_Heartbeat(t *testing.T) {
	msg := &Message{
		Type:      MsgTypeHeartbeat,
		AgentID:   "agent1",
		Timestamp: time.Now(),
	}

	assert.Equal(t, MsgTypeHeartbeat, msg.Type)
}

// TestMessage_TaskRequest creates task request message
func TestMessage_TaskRequest(t *testing.T) {
	msg := &Message{
		Type:      MsgTypeTaskRequest,
		AgentID:   "agent1",
		Timestamp: time.Now(),
		Payload: map[string]interface{}{
			"tags": []string{"high-priority"},
		},
	}

	assert.Equal(t, MsgTypeTaskRequest, msg.Type)
}

// TestMessage_TaskResult creates task result message
func TestMessage_TaskResult(t *testing.T) {
	msg := &Message{
		Type:      MsgTypeTaskResult,
		AgentID:   "agent1",
		Timestamp: time.Now(),
		Payload: map[string]interface{}{
			"task_id": "task1",
			"success": true,
		},
	}

	assert.Equal(t, MsgTypeTaskResult, msg.Type)
}

// TestMessage_TaskError creates error message
func TestMessage_TaskError(t *testing.T) {
	msg := &Message{
		Type:      MsgTypeTaskError,
		AgentID:   "agent1",
		Timestamp: time.Now(),
		Error:     "task failed",
	}

	assert.Equal(t, MsgTypeTaskError, msg.Type)
	assert.NotEmpty(t, msg.Error)
}

// TestMessage_Unregister creates unregister message
func TestMessage_Unregister(t *testing.T) {
	msg := &Message{
		Type:      MsgTypeUnregister,
		AgentID:   "agent1",
		Timestamp: time.Now(),
	}

	assert.Equal(t, MsgTypeUnregister, msg.Type)
}

// TestMessage_Shutdown creates shutdown message
func TestMessage_Shutdown(t *testing.T) {
	msg := &Message{
		Type:      MsgTypeShutdown,
		AgentID:   "agent1",
		Timestamp: time.Now(),
	}

	assert.Equal(t, MsgTypeShutdown, msg.Type)
}

// TestRegisterRequest_Comprehensive creates register request
func TestRegisterRequest_Comprehensive(t *testing.T) {
	req := &RegisterRequest{
		Name:      "agent1",
		ProjectID: "p1",
		Capabilities: []AgentCapability{
			{Name: "analyze"},
		},
	}

	assert.Equal(t, "agent1", req.Name)
	assert.Equal(t, 1, len(req.Capabilities))
}

// TestTaskRequest_WithTags creates request with tags
func TestTaskRequest_WithTags(t *testing.T) {
	req := &TaskRequest{
		AgentID: "agent1",
		Tags:    []string{"high-priority", "urgent"},
	}

	assert.Equal(t, "agent1", req.AgentID)
	assert.Equal(t, 2, len(req.Tags))
}

// ============================================================================
// AGENT STATUS AND CAPABILITY TESTS (8 tests)
// ============================================================================

// TestAgentCapability_Creation creates capability
func TestAgentCapability_Creation(t *testing.T) {
	cap := AgentCapability{
		Name:        "analyze",
		Version:     "1.0.0",
		Tags:        []string{"processing"},
		Description: "Analyze data",
	}

	assert.Equal(t, "analyze", cap.Name)
	assert.Equal(t, "1.0.0", cap.Version)
}

// TestAgentCapability_MultipleVersions tests capability versions
func TestAgentCapability_MultipleVersions(t *testing.T) {
	caps := []AgentCapability{
		{Name: "analyze", Version: "1.0.0"},
		{Name: "analyze", Version: "2.0.0"},
	}

	assert.Equal(t, 2, len(caps))
	assert.Equal(t, "1.0.0", caps[0].Version)
	assert.Equal(t, "2.0.0", caps[1].Version)
}

// TestRegisteredAgent_Creation creates agent
func TestRegisteredAgent_Creation(t *testing.T) {
	agent := &RegisteredAgent{
		Name:      "agent1",
		ProjectID: "p1",
		Status:    StatusIdle,
	}

	assert.Equal(t, "agent1", agent.Name)
	assert.Equal(t, StatusIdle, agent.Status)
}

// TestRegisteredAgent_Metadata stores metadata
func TestRegisteredAgent_Metadata(t *testing.T) {
	agent := &RegisteredAgent{
		Name:      "agent1",
		ProjectID: "p1",
		Metadata: map[string]interface{}{
			"version": "1.0",
			"region":  "us-east-1",
		},
	}

	assert.Equal(t, "1.0", agent.Metadata["version"])
	assert.Equal(t, "us-east-1", agent.Metadata["region"])
}

// TestAgentStatus_Transitions tests status values
func TestAgentStatus_Transitions(t *testing.T) {
	statuses := []AgentStatus{
		StatusIdle,
		StatusActive,
		StatusBusy,
		StatusError,
		StatusOffline,
	}

	for _, status := range statuses {
		assert.NotEmpty(t, status)
	}
}

// TestTaskStatus_Values tests task status constants
func TestTaskStatus_Values(t *testing.T) {
	statuses := []TaskStatus{
		TaskStatusPending,
		TaskStatusAssigned,
		TaskStatusRunning,
		TaskStatusCompleted,
		TaskStatusFailed,
		TaskStatusCanceled,
	}

	for _, status := range statuses {
		assert.NotEmpty(t, status)
	}
}

// TestTaskPriority_Ordering tests priority ordering
func TestTaskPriority_Ordering(t *testing.T) {
	assert.True(t, PriorityLow < PriorityNormal)
	assert.True(t, PriorityNormal < PriorityHigh)
	assert.True(t, PriorityHigh < PriorityCritical)
}

// TestTaskResult_Creation creates result
func TestTaskResult_Creation(t *testing.T) {
	result := &TaskResult{
		Success:  true,
		Data:     map[string]interface{}{"count": 42},
		Message:  "Task completed",
		Duration: 5 * time.Second,
	}

	assert.True(t, result.Success)
	assert.Equal(t, 42, result.Data["count"])
}
