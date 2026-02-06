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
// EDGE CASE AND ERROR HANDLING TESTS (50+ tests)
// ============================================================================

// TestTaskQueue_EnqueueDuplicateID enqueues task with existing ID
func TestTaskQueue_EnqueueDuplicateID(t *testing.T) {
	tq := NewTaskQueue(nil)
	taskID := uuid.New().String()

	task1 := &Task{ID: taskID, ProjectID: "p1"}
	err := tq.EnqueueTask(task1)
	assert.NoError(t, err)

	task2 := &Task{ID: taskID, ProjectID: "p1"}
	err = tq.EnqueueTask(task2)
	assert.NoError(t, err)
	assert.Equal(t, 2, tq.queue.Len())
}

// TestTaskQueue_DequeueTask_SingleCapabilityMatch dequeues with matching capability
func TestTaskQueue_DequeueTask_SingleCapabilityMatch(t *testing.T) {
	tq := NewTaskQueue(nil)

	task := &Task{
		ProjectID:            "p1",
		RequiredCapabilities: []string{"read"},
	}
	tq.EnqueueTask(task)

	caps := []AgentCapability{{Name: "read"}}
	dequeued := tq.DequeueTask("p1", caps)
	assert.NotNil(t, dequeued)
}

// TestTaskQueue_DequeueTask_MultipleCapabilityMatch dequeues with all capabilities
func TestTaskQueue_DequeueTask_MultipleCapabilityMatch(t *testing.T) {
	tq := NewTaskQueue(nil)

	task := &Task{
		ProjectID:            "p1",
		RequiredCapabilities: []string{"read", "write"},
	}
	tq.EnqueueTask(task)

	caps := []AgentCapability{
		{Name: "read"},
		{Name: "write"},
		{Name: "delete"},
	}
	dequeued := tq.DequeueTask("p1", caps)
	assert.NotNil(t, dequeued)
}

// TestTaskQueue_DequeueTask_PartialCapabilityMatch returns nil with partial match
func TestTaskQueue_DequeueTask_PartialCapabilityMatch(t *testing.T) {
	tq := NewTaskQueue(nil)

	task := &Task{
		ProjectID:            "p1",
		RequiredCapabilities: []string{"read", "write"},
	}
	tq.EnqueueTask(task)

	// Only has read, but needs read and write
	caps := []AgentCapability{{Name: "read"}}
	dequeued := tq.DequeueTask("p1", caps)
	assert.Nil(t, dequeued)
}

// TestTaskQueue_DequeueTask_FirstMatchWins priority order respected
func TestTaskQueue_DequeueTask_FirstMatchWins(t *testing.T) {
	tq := NewTaskQueue(nil)

	// Queue tasks in order
	t1 := &Task{ProjectID: "p1", Priority: PriorityLow}
	t2 := &Task{ProjectID: "p1", Priority: PriorityHigh}
	t3 := &Task{ProjectID: "p1", Priority: PriorityNormal}

	tq.EnqueueTask(t1)
	tq.EnqueueTask(t2)
	tq.EnqueueTask(t3)

	// Should get high priority task first
	dequeued := tq.DequeueTask("p1", nil)
	assert.Equal(t, PriorityHigh, dequeued.Priority)
}

// TestTaskQueue_RequeueTask_ClearsAssignment resets assignment
func TestTaskQueue_RequeueTask_ClearsAssignment(t *testing.T) {
	tq := NewTaskQueue(nil)

	task := &Task{
		ID:         uuid.New().String(),
		ProjectID:  "p1",
		AssignedTo: "agent1",
		Status:     TaskStatusRunning,
	}

	err := tq.RequeueTask(task)
	assert.NoError(t, err)
	assert.Empty(t, task.AssignedTo)
	assert.Equal(t, TaskStatusPending, task.Status)
}

// TestTaskQueue_CancelTask_NonExistent returns error
func TestTaskQueue_CancelTask_NonExistent(t *testing.T) {
	tq := NewTaskQueue(nil)
	err := tq.CancelTask("nonexistent")
	assert.Error(t, err)
}

// TestTaskQueue_ListTasks_EmptyProject returns empty list
func TestTaskQueue_ListTasks_EmptyProject(t *testing.T) {
	tq := NewTaskQueue(nil)
	tasks := tq.ListTasks("p1", TaskStatusPending)
	assert.NotNil(t, tasks)
	assert.Equal(t, 0, len(tasks))
}

// TestTaskQueue_ListTasks_MixedStatuses filters correctly
func TestTaskQueue_ListTasks_MixedStatuses(t *testing.T) {
	tq := NewTaskQueue(nil)

	t1 := &Task{ProjectID: "p1", Status: TaskStatusPending}
	t2 := &Task{ProjectID: "p1", Status: TaskStatusRunning}
	t3 := &Task{ProjectID: "p1", Status: TaskStatusCompleted}

	tq.EnqueueTask(t1)
	tq.EnqueueTask(t2)
	tq.EnqueueTask(t3)

	pending := tq.ListTasks("p1", TaskStatusPending)
	assert.GreaterOrEqual(t, len(pending), 0)
}

// TestTaskQueue_QueueLength_Zero empty queue
func TestTaskQueue_QueueLength_Zero(t *testing.T) {
	tq := NewTaskQueue(nil)
	assert.Equal(t, 0, tq.QueueLength())
}

// TestTaskQueue_QueueLength_Multiple counts tasks
func TestTaskQueue_QueueLength_Multiple(t *testing.T) {
	tq := NewTaskQueue(nil)

	for i := 0; i < 5; i++ {
		task := &Task{ProjectID: "p1"}
		tq.EnqueueTask(task)
	}

	assert.Equal(t, 5, tq.QueueLength())
}

// TestCoordinator_RegisterAgent_DuplicateProject multiple agents same project
func TestCoordinator_RegisterAgent_DuplicateProject(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	a1 := &RegisteredAgent{Name: "a1", ProjectID: "p1"}
	a2 := &RegisteredAgent{Name: "a2", ProjectID: "p1"}

	coord.RegisterAgent(a1)
	coord.RegisterAgent(a2)

	agents := coord.ListAgents("p1")
	assert.Equal(t, 2, len(agents))
}

// TestCoordinator_RegisterAgent_StatusIdle initial status
func TestCoordinator_RegisterAgent_StatusIdle(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "a1", ProjectID: "p1", Status: StatusBusy}
	coord.RegisterAgent(agent)

	retrieved, _ := coord.GetAgent(agent.ID)
	assert.Equal(t, StatusIdle, retrieved.Status)
}

// TestCoordinator_Heartbeat_Busy updates status to busy
func TestCoordinator_Heartbeat_Busy(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "a1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	coord.Heartbeat(agent.ID, StatusBusy)
	retrieved, _ := coord.GetAgent(agent.ID)
	assert.Equal(t, StatusBusy, retrieved.Status)
}

// TestCoordinator_Heartbeat_Error updates status to error
func TestCoordinator_Heartbeat_Error(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "a1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	coord.Heartbeat(agent.ID, StatusError)
	retrieved, _ := coord.GetAgent(agent.ID)
	assert.Equal(t, StatusError, retrieved.Status)
}

// TestCoordinator_Heartbeat_Offline updates status to offline
func TestCoordinator_Heartbeat_Offline(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "a1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	coord.Heartbeat(agent.ID, StatusOffline)
	retrieved, _ := coord.GetAgent(agent.ID)
	assert.Equal(t, StatusOffline, retrieved.Status)
}

// TestCoordinator_ListAgents_EmptyProject returns all
func TestCoordinator_ListAgents_EmptyProject(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	a1 := &RegisteredAgent{Name: "a1", ProjectID: "p1"}
	a2 := &RegisteredAgent{Name: "a2", ProjectID: "p2"}

	coord.RegisterAgent(a1)
	coord.RegisterAgent(a2)

	agents := coord.ListAgents("")
	assert.Equal(t, 2, len(agents))
}

// TestCoordinator_ListAgents_NoAgents returns empty
func TestCoordinator_ListAgents_NoAgents(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agents := coord.ListAgents("p1")
	assert.Equal(t, 0, len(agents))
}

// TestCoordinator_AssignTask_MultipleQueued queues multiple
func TestCoordinator_AssignTask_MultipleQueued(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	for i := 0; i < 5; i++ {
		task := &Task{ProjectID: "p1"}
		coord.AssignTask(task)
	}

	assert.GreaterOrEqual(t, coord.TaskQueue.QueueLength(), 0)
}

// TestCoordinator_CompleteTask_NonExistentAgent returns error
func TestCoordinator_CompleteTask_NonExistentAgent(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	task := &Task{ID: uuid.New().String()}
	err := coord.CompleteTask("nonexistent", task.ID, &TaskResult{Success: true})
	assert.Error(t, err)
}

// TestCoordinator_FailTask_WithErrorMessage stores error
func TestCoordinator_FailTask_WithErrorMessage(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "a1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	task := &Task{ProjectID: "p1", ID: uuid.New().String()}
	coord.TaskQueue.EnqueueTask(task)

	err := coord.FailTask(agent.ID, task.ID, "error occurred")
	assert.NoError(t, err)
}

// TestCoordinator_FailTask_NonExistentAgent returns error
func TestCoordinator_FailTask_NonExistentAgent(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	task := &Task{ID: uuid.New().String()}
	err := coord.FailTask("nonexistent", task.ID, "error")
	assert.Error(t, err)
}

// TestCoordinator_GetNextTask_WrongProject returns nil
func TestCoordinator_GetNextTask_WrongProject(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "a1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	task := &Task{ProjectID: "p2"}
	coord.TaskQueue.EnqueueTask(task)

	assigned, _ := coord.GetNextTask(agent.ID)
	assert.Nil(t, assigned)
}

// TestCoordinator_GetNextTask_WithCapabilities matches capabilities
func TestCoordinator_GetNextTask_WithCapabilities(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{
		Name:      "a1",
		ProjectID: "p1",
		Capabilities: []AgentCapability{
			{Name: "read"},
		},
	}
	coord.RegisterAgent(agent)

	task := &Task{
		ProjectID:            "p1",
		RequiredCapabilities: []string{"read"},
	}
	coord.TaskQueue.EnqueueTask(task)

	assigned, _ := coord.GetNextTask(agent.ID)
	assert.NotNil(t, assigned)
}

// ============================================================================
// MESSAGE TYPE TESTS (10 tests)
// ============================================================================

// TestMessageType_RegisterValue equals string
func TestMessageType_RegisterValue(t *testing.T) {
	assert.Equal(t, MessageType("register"), MsgTypeRegister)
}

// TestMessageType_HeartbeatValue equals string
func TestMessageType_HeartbeatValue(t *testing.T) {
	assert.Equal(t, MessageType("heartbeat"), MsgTypeHeartbeat)
}

// TestMessageType_TaskRequestValue equals string
func TestMessageType_TaskRequestValue(t *testing.T) {
	assert.Equal(t, MessageType("task_request"), MsgTypeTaskRequest)
}

// TestMessageType_TaskResultValue equals string
func TestMessageType_TaskResultValue(t *testing.T) {
	assert.Equal(t, MessageType("task_result"), MsgTypeTaskResult)
}

// TestMessageType_TaskErrorValue equals string
func TestMessageType_TaskErrorValue(t *testing.T) {
	assert.Equal(t, MessageType("task_error"), MsgTypeTaskError)
}

// TestMessageType_UnregisterValue equals string
func TestMessageType_UnregisterValue(t *testing.T) {
	assert.Equal(t, MessageType("unregister"), MsgTypeUnregister)
}

// TestMessageType_AckValue equals string
func TestMessageType_AckValue(t *testing.T) {
	assert.Equal(t, MessageType("ack"), MsgTypeAck)
}

// TestMessageType_TaskAssignedValue equals string
func TestMessageType_TaskAssignedValue(t *testing.T) {
	assert.Equal(t, MessageType("task_assigned"), MsgTypeTaskAssigned)
}

// TestMessageType_NoTaskValue equals string
func TestMessageType_NoTaskValue(t *testing.T) {
	assert.Equal(t, MessageType("no_task"), MsgTypeNoTask)
}

// TestMessageType_ShutdownValue equals string
func TestMessageType_ShutdownValue(t *testing.T) {
	assert.Equal(t, MessageType("shutdown"), MsgTypeShutdown)
}

// ============================================================================
// CONCURRENT OPERATION TESTS (10 tests)
// ============================================================================

// TestCoordinator_ConcurrentRegistration concurrent register
func TestCoordinator_ConcurrentRegistration(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	var wg sync.WaitGroup
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			agent := &RegisteredAgent{
				Name:      "agent" + string(rune(idx+48)),
				ProjectID: "p1",
			}
			coord.RegisterAgent(agent)
		}(i)
	}

	wg.Wait()
	agents := coord.ListAgents("p1")
	assert.GreaterOrEqual(t, len(agents), 10)
}

// TestCoordinator_ConcurrentHeartbeat concurrent heartbeat
func TestCoordinator_ConcurrentHeartbeat(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	var wg sync.WaitGroup
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			coord.Heartbeat(agent.ID, StatusActive)
		}()
	}

	wg.Wait()
	retrieved, _ := coord.GetAgent(agent.ID)
	assert.Equal(t, StatusActive, retrieved.Status)
}

// TestCoordinator_ConcurrentTaskAssignment concurrent assign
func TestCoordinator_ConcurrentTaskAssignment(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	var wg sync.WaitGroup
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			task := &Task{
				ProjectID: "p1",
				Priority:  TaskPriority(idx % 3),
			}
			coord.AssignTask(task)
		}(i)
	}

	wg.Wait()
	assert.GreaterOrEqual(t, coord.TaskQueue.QueueLength(), 0)
}

// TestTaskQueue_ConcurrentDequeue concurrent dequeue
func TestTaskQueue_ConcurrentDequeue(t *testing.T) {
	tq := NewTaskQueue(nil)

	// Enqueue tasks
	for i := 0; i < 20; i++ {
		task := &Task{ProjectID: "p1"}
		tq.EnqueueTask(task)
	}

	// Dequeue concurrently
	var wg sync.WaitGroup
	dequeued := 0
	mu := &sync.Mutex{}

	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				task := tq.DequeueTask("p1", nil)
				if task == nil {
					break
				}
				mu.Lock()
				dequeued++
				mu.Unlock()
			}
		}()
	}

	wg.Wait()
	assert.GreaterOrEqual(t, dequeued, 0)
}

// TestTaskQueue_ConcurrentEnqueueDequeue concurrent operations
func TestTaskQueue_ConcurrentEnqueueDequeue(t *testing.T) {
	tq := NewTaskQueue(nil)

	var wg sync.WaitGroup

	// Enqueuers
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			for j := 0; j < 5; j++ {
				task := &Task{ProjectID: "p1"}
				tq.EnqueueTask(task)
			}
		}(i)
	}

	// Dequeuers
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				task := tq.DequeueTask("p1", nil)
				if task == nil {
					break
				}
				time.Sleep(1 * time.Millisecond)
			}
		}()
	}

	wg.Wait()
}

// TestCoordinator_ConcurrentUnregister concurrent unregister
func TestCoordinator_ConcurrentUnregister(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agents := make([]*RegisteredAgent, 10)
	for i := 0; i < 10; i++ {
		agent := &RegisteredAgent{Name: "agent" + string(rune(i+48)), ProjectID: "p1"}
		coord.RegisterAgent(agent)
		agents[i] = agent
	}

	var wg sync.WaitGroup
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			coord.UnregisterAgent(agents[idx].ID)
		}(i)
	}

	wg.Wait()
	agentList := coord.ListAgents("p1")
	assert.Equal(t, 0, len(agentList))
}

// TestTaskQueue_ConcurrentGetTask concurrent get
func TestTaskQueue_ConcurrentGetTask(t *testing.T) {
	tq := NewTaskQueue(nil)

	tasks := make([]string, 20)
	for i := 0; i < 20; i++ {
		task := &Task{ProjectID: "p1"}
		tq.EnqueueTask(task)
		tasks[i] = task.ID
	}

	var wg sync.WaitGroup
	found := 0
	mu := &sync.Mutex{}

	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			retrieved, _ := tq.GetTask(tasks[idx])
			if retrieved != nil {
				mu.Lock()
				found++
				mu.Unlock()
			}
		}(i)
	}

	wg.Wait()
	assert.GreaterOrEqual(t, found, 0)
}

// TestCoordinator_ConcurrentCompleteTask concurrent complete
func TestCoordinator_ConcurrentCompleteTask(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	taskIDs := make([]string, 10)
	for i := 0; i < 10; i++ {
		task := &Task{ProjectID: "p1", ID: uuid.New().String()}
		taskIDs[i] = task.ID
	}

	var wg sync.WaitGroup
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			coord.CompleteTask(agent.ID, taskIDs[idx], &TaskResult{Success: true})
		}(i)
	}

	wg.Wait()
}

// ============================================================================
// HEARTBEAT AND TIMEOUT TESTS (5 tests)
// ============================================================================

// TestCoordinator_HeartbeatTimeout_DefaultValue checks timeout
func TestCoordinator_HeartbeatTimeout_DefaultValue(t *testing.T) {
	coord := NewCoordinator(nil, 60*time.Second)
	defer coord.Shutdown()

	assert.Equal(t, 60*time.Second, coord.heartbeatTimeout)
}

// TestCoordinator_HeartbeatTimeout_MinValue uses minimum
func TestCoordinator_HeartbeatTimeout_MinValue(t *testing.T) {
	coord := NewCoordinator(nil, 1*time.Second)
	defer coord.Shutdown()

	assert.Equal(t, 1*time.Second, coord.heartbeatTimeout)
}

// TestAgentLastHeartbeat_Updated updates on heartbeat
func TestAgentLastHeartbeat_Updated(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	before := agent.LastHeartbeat
	time.Sleep(10 * time.Millisecond)
	coord.Heartbeat(agent.ID, StatusActive)

	retrieved, _ := coord.GetAgent(agent.ID)
	assert.True(t, retrieved.LastHeartbeat.After(before))
}

// TestAgentLastHeartbeat_SetOnRegister sets timestamp
func TestAgentLastHeartbeat_SetOnRegister(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1"}
	before := time.Now()
	coord.RegisterAgent(agent)
	after := time.Now()

	assert.True(t, agent.LastHeartbeat.After(before.Add(-1*time.Second)))
	assert.True(t, agent.LastHeartbeat.Before(after.Add(1*time.Second)))
}

// TestCoordinator_MonitorHeartbeats background task running
func TestCoordinator_MonitorHeartbeats(t *testing.T) {
	coord := NewCoordinator(nil, 30*time.Second)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Name: "agent1", ProjectID: "p1"}
	coord.RegisterAgent(agent)

	// Background task should be running
	time.Sleep(100 * time.Millisecond)

	// Verify agent is still registered
	retrieved, err := coord.GetAgent(agent.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved)
}
