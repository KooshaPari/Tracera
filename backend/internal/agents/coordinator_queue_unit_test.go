//go:build !integration && !e2e

package agents

import (
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const testHeartbeatTimeout = 2 * time.Minute

// ========== Coordinator unit tests (nil DB) ==========

func TestNewCoordinator_NilDB_DoesNotPanic(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	require.NotNil(t, coord)
	defer coord.Shutdown()
	assert.Nil(t, coord.TaskQueue.db)
}

func TestCoordinator_RegisterAgent_NilDB(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	agent := &RegisteredAgent{
		Name:      "unit-agent",
		ProjectID: "proj-1",
		Status:    StatusIdle,
		Capabilities: []AgentCapability{
			{Name: "analyze", Version: "1.0"},
		},
	}

	err := coord.RegisterAgent(agent)
	require.NoError(t, err)
	assert.NotEmpty(t, agent.ID)
	assert.Equal(t, StatusIdle, agent.Status)
}

func TestCoordinator_RegisterAgent_WithID_PreservesID(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	id := uuid.New().String()
	agent := &RegisteredAgent{ID: id, Name: "a", ProjectID: "p1"}
	err := coord.RegisterAgent(agent)
	require.NoError(t, err)
	assert.Equal(t, id, agent.ID)
}

func TestCoordinator_UnregisterAgent_NilDB(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	agent := &RegisteredAgent{ID: "ag-1", Name: "a", ProjectID: "p1"}
	require.NoError(t, coord.RegisterAgent(agent))

	err := coord.UnregisterAgent("ag-1")
	require.NoError(t, err)

	_, err = coord.GetAgent("ag-1")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "not found")
}

func TestCoordinator_UnregisterAgent_NotFound(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	err := coord.UnregisterAgent("nonexistent")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "not found")
}

func TestCoordinator_UnregisterAgent_RequeuesCurrentTask(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	agent := &RegisteredAgent{
		ID: "ag-1", Name: "a", ProjectID: "p1",
		CurrentTask: &Task{ID: "task-1", ProjectID: "p1", Status: TaskStatusAssigned},
	}
	require.NoError(t, coord.RegisterAgent(agent))

	err := coord.UnregisterAgent("ag-1")
	require.NoError(t, err)
	// Task should have been requeued (RequeueTask called)
	assert.Nil(t, agent.CurrentTask)
}

func TestCoordinator_Heartbeat_NilDB(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	agent := &RegisteredAgent{ID: "ag-1", Name: "a", ProjectID: "p1"}
	require.NoError(t, coord.RegisterAgent(agent))

	err := coord.Heartbeat("ag-1", StatusActive)
	require.NoError(t, err)

	a, err := coord.GetAgent("ag-1")
	require.NoError(t, err)
	assert.Equal(t, StatusActive, a.Status)
}

func TestCoordinator_Heartbeat_AgentNotFound(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	err := coord.Heartbeat("nonexistent", StatusActive)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "not found")
}

func TestCoordinator_GetAgent_NotFound(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	_, err := coord.GetAgent("nonexistent")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "not found")
}

func TestCoordinator_GetAgent_Found(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	agent := &RegisteredAgent{ID: "ag-1", Name: "worker", ProjectID: "p1"}
	require.NoError(t, coord.RegisterAgent(agent))

	a, err := coord.GetAgent("ag-1")
	require.NoError(t, err)
	assert.Equal(t, "ag-1", a.ID)
	assert.Equal(t, "worker", a.Name)
}

func TestCoordinator_ListAgents_EmptyFilter(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	require.NoError(t, coord.RegisterAgent(&RegisteredAgent{ID: "1", Name: "a1", ProjectID: "p1"}))
	require.NoError(t, coord.RegisterAgent(&RegisteredAgent{ID: "2", Name: "a2", ProjectID: "p2"}))

	list := coord.ListAgents("")
	assert.Len(t, list, 2)
}

func TestCoordinator_ListAgents_ByProject(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	require.NoError(t, coord.RegisterAgent(&RegisteredAgent{ID: "1", Name: "a1", ProjectID: "p1"}))
	require.NoError(t, coord.RegisterAgent(&RegisteredAgent{ID: "2", Name: "a2", ProjectID: "p1"}))
	require.NoError(t, coord.RegisterAgent(&RegisteredAgent{ID: "3", Name: "a3", ProjectID: "p2"}))

	list := coord.ListAgents("p1")
	assert.Len(t, list, 2)
	for _, a := range list {
		assert.Equal(t, "p1", a.ProjectID)
	}
}

func TestCoordinator_AssignTask_EnqueuesWhenNoAgent(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	task := &Task{ID: "t1", ProjectID: "p1", Status: TaskStatusPending}
	err := coord.AssignTask(task)
	require.NoError(t, err)
	assert.Equal(t, TaskStatusPending, task.Status)
	assert.Equal(t, 1, coord.TaskQueue.QueueLength())
}

func TestCoordinator_AssignTask_AssignsToIdleAgent(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	agent := &RegisteredAgent{
		ID: "ag-1", Name: "w", ProjectID: "p1", Status: StatusIdle,
		Capabilities: []AgentCapability{{Name: "run"}},
	}
	require.NoError(t, coord.RegisterAgent(agent))

	task := &Task{
		ID: "t1", ProjectID: "p1", RequiredCapabilities: []string{"run"},
	}
	err := coord.AssignTask(task)
	require.NoError(t, err)
	assert.Equal(t, TaskStatusAssigned, task.Status)
	assert.Equal(t, "ag-1", task.AssignedTo)
	assert.Equal(t, StatusBusy, agent.Status)
	assert.NotNil(t, agent.CurrentTask)
}

func TestCoordinator_AssignTask_RequiresCapabilityMatch(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	agent := &RegisteredAgent{
		ID: "ag-1", Name: "w", ProjectID: "p1", Status: StatusIdle,
		Capabilities: []AgentCapability{{Name: "read"}},
	}
	require.NoError(t, coord.RegisterAgent(agent))

	task := &Task{
		ID: "t1", ProjectID: "p1", RequiredCapabilities: []string{"read", "write"},
	}
	err := coord.AssignTask(task)
	require.NoError(t, err)
	// No agent has both read and write -> enqueued
	assert.Equal(t, TaskStatusPending, task.Status)
	assert.Equal(t, 1, coord.TaskQueue.QueueLength())
}

func TestCoordinator_CompleteTask_Success(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	task := &Task{ID: "t1", ProjectID: "p1", Status: TaskStatusAssigned}
	agent := &RegisteredAgent{
		ID: "ag-1", Name: "w", ProjectID: "p1", Status: StatusBusy,
		CurrentTask: task,
	}
	require.NoError(t, coord.RegisterAgent(agent))

	result := &TaskResult{Success: true, Message: "ok"}
	err := coord.CompleteTask("ag-1", "t1", result)
	require.NoError(t, err)
	assert.Equal(t, TaskStatusCompleted, task.Status)
	assert.Nil(t, agent.CurrentTask)
	assert.Equal(t, StatusIdle, agent.Status)
}

func TestCoordinator_CompleteTask_AgentNotFound(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	err := coord.CompleteTask("nonexistent", "t1", &TaskResult{})
	require.Error(t, err)
	assert.Contains(t, err.Error(), "agent not found")
}

func TestCoordinator_CompleteTask_TaskNotAssignedToAgent(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	agent := &RegisteredAgent{ID: "ag-1", Name: "w", ProjectID: "p1"}
	require.NoError(t, coord.RegisterAgent(agent))

	err := coord.CompleteTask("ag-1", "other-task", &TaskResult{})
	require.Error(t, err)
	assert.Contains(t, err.Error(), "not assigned")
}

func TestCoordinator_FailTask_RequeuesWhenRetriesLeft(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	task := &Task{
		ID: "t1", ProjectID: "p1", Status: TaskStatusAssigned,
		RetryCount: 0, MaxRetries: 2,
	}
	agent := &RegisteredAgent{
		ID: "ag-1", Name: "w", ProjectID: "p1", Status: StatusBusy,
		CurrentTask: task,
	}
	require.NoError(t, coord.RegisterAgent(agent))

	err := coord.FailTask("ag-1", "t1", "err")
	require.NoError(t, err)
	assert.Nil(t, agent.CurrentTask)
	assert.Equal(t, StatusIdle, agent.Status)
	assert.Equal(t, TaskStatusPending, task.Status)
	assert.Equal(t, 1, task.RetryCount)
}

func TestCoordinator_FailTask_NoRetries_PermanentFail(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	task := &Task{
		ID: "t1", ProjectID: "p1", Status: TaskStatusAssigned,
		RetryCount: 2, MaxRetries: 2,
	}
	agent := &RegisteredAgent{
		ID: "ag-1", Name: "w", ProjectID: "p1", Status: StatusBusy,
		CurrentTask: task,
	}
	require.NoError(t, coord.RegisterAgent(agent))

	err := coord.FailTask("ag-1", "t1", "err")
	require.NoError(t, err)
	assert.Equal(t, TaskStatusFailed, task.Status)
	assert.Nil(t, agent.CurrentTask)
}

func TestCoordinator_FailTask_AgentNotFound(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	err := coord.FailTask("nonexistent", "t1", "err")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "not found")
}

func TestCoordinator_GetNextTask_ReturnsCurrentIfHasTask(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	task := &Task{ID: "t1", ProjectID: "p1"}
	agent := &RegisteredAgent{
		ID: "ag-1", Name: "w", ProjectID: "p1", Status: StatusBusy,
		CurrentTask: task,
	}
	require.NoError(t, coord.RegisterAgent(agent))

	next, err := coord.GetNextTask("ag-1")
	require.NoError(t, err)
	require.NotNil(t, next)
	assert.Equal(t, "t1", next.ID)
}

func TestCoordinator_GetNextTask_AgentNotFound(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	next, err := coord.GetNextTask("nonexistent")
	require.Error(t, err)
	assert.Nil(t, next)
	assert.Contains(t, err.Error(), "not found")
}

func TestCoordinator_GetNextTask_DequeuesAndAssigns(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	agent := &RegisteredAgent{
		ID: "ag-1", Name: "w", ProjectID: "p1", Status: StatusIdle,
		Capabilities: []AgentCapability{{Name: "run"}},
	}
	require.NoError(t, coord.RegisterAgent(agent))

	task := &Task{
		ID: "t1", ProjectID: "p1", RequiredCapabilities: []string{"run"},
	}
	require.NoError(t, coord.TaskQueue.EnqueueTask(task))

	next, err := coord.GetNextTask("ag-1")
	require.NoError(t, err)
	require.NotNil(t, next)
	assert.Equal(t, "t1", next.ID)
	assert.Equal(t, "ag-1", next.AssignedTo)
	a, err := coord.GetAgent("ag-1")
	require.NoError(t, err)
	assert.Equal(t, StatusBusy, a.Status)
}

func TestCoordinator_GetNextTask_NoTaskReturnsNil(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	agent := &RegisteredAgent{
		ID: "ag-1", Name: "w", ProjectID: "p1", Status: StatusIdle,
		Capabilities: []AgentCapability{{Name: "run"}},
	}
	require.NoError(t, coord.RegisterAgent(agent))

	next, err := coord.GetNextTask("ag-1")
	require.NoError(t, err)
	assert.Nil(t, next)
}

func TestCoordinator_HasRequiredCapabilities_EmptyRequired(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	agent := &RegisteredAgent{Capabilities: []AgentCapability{{Name: "x"}}}
	task := &Task{RequiredCapabilities: nil}
	assert.True(t, coord.hasRequiredCapabilities(agent, task))
}

func TestCoordinator_HasRequiredCapabilities_AllMatch(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	agent := &RegisteredAgent{
		Capabilities: []AgentCapability{{Name: "a"}, {Name: "b"}},
	}
	task := &Task{RequiredCapabilities: []string{"a", "b"}}
	assert.True(t, coord.hasRequiredCapabilities(agent, task))
}

func TestCoordinator_HasRequiredCapabilities_Missing(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	defer coord.Shutdown()

	agent := &RegisteredAgent{
		Capabilities: []AgentCapability{{Name: "a"}},
	}
	task := &Task{RequiredCapabilities: []string{"a", "b"}}
	assert.False(t, coord.hasRequiredCapabilities(agent, task))
}

func TestCoordinator_Shutdown_StopsBackgroundTasks(t *testing.T) {
	coord := NewCoordinator(nil, testHeartbeatTimeout)
	coord.Shutdown()
	// Shutdown should not block; no panic
}

// ========== TaskQueue unit tests (nil DB) ==========

func TestNewTaskQueue_NilDB(t *testing.T) {
	tq := NewTaskQueue(nil)
	require.NotNil(t, tq)
	assert.Equal(t, 0, tq.QueueLength())
}

func TestTaskQueue_EnqueueTask_AssignsIDIfEmpty(t *testing.T) {
	tq := NewTaskQueue(nil)
	task := &Task{ProjectID: "p1", Type: "run"}
	err := tq.EnqueueTask(task)
	require.NoError(t, err)
	assert.NotEmpty(t, task.ID)
	assert.Equal(t, TaskStatusPending, task.Status)
	assert.Equal(t, 1, tq.QueueLength())
}

func TestTaskQueue_EnqueueTask_PreservesID(t *testing.T) {
	tq := NewTaskQueue(nil)
	task := &Task{ID: "custom-id", ProjectID: "p1"}
	err := tq.EnqueueTask(task)
	require.NoError(t, err)
	assert.Equal(t, "custom-id", task.ID)
}

func TestTaskQueue_DequeueTask_EmptyReturnsNil(t *testing.T) {
	tq := NewTaskQueue(nil)
	task := tq.DequeueTask("p1", nil)
	assert.Nil(t, task)
}

func TestTaskQueue_DequeueTask_ProjectMismatch(t *testing.T) {
	tq := NewTaskQueue(nil)
	require.NoError(t, tq.EnqueueTask(&Task{ID: "t1", ProjectID: "p1"}))
	task := tq.DequeueTask("p2", []AgentCapability{{Name: "x"}})
	assert.Nil(t, task)
}

func TestTaskQueue_DequeueTask_CapabilityMismatch(t *testing.T) {
	tq := NewTaskQueue(nil)
	task := &Task{ID: "t1", ProjectID: "p1", RequiredCapabilities: []string{"write"}}
	require.NoError(t, tq.EnqueueTask(task))
	out := tq.DequeueTask("p1", []AgentCapability{{Name: "read"}})
	assert.Nil(t, out)
}

func TestTaskQueue_DequeueTask_ReturnsAndRemoves(t *testing.T) {
	tq := NewTaskQueue(nil)
	require.NoError(t, tq.EnqueueTask(&Task{ID: "t1", ProjectID: "p1"}))
	task := tq.DequeueTask("p1", nil)
	require.NotNil(t, task)
	assert.Equal(t, "t1", task.ID)
	assert.Equal(t, 0, tq.QueueLength())
}

func TestTaskQueue_RequeueTask_IdempotentIfAlreadyQueued(t *testing.T) {
	tq := NewTaskQueue(nil)
	task := &Task{ID: "t1", ProjectID: "p1"}
	require.NoError(t, tq.EnqueueTask(task))
	err := tq.RequeueTask(task)
	require.NoError(t, err)
	assert.Equal(t, 1, tq.QueueLength())
}

func TestTaskQueue_RequeueTask_ResetsAssignment(t *testing.T) {
	tq := NewTaskQueue(nil)
	task := &Task{ID: "t1", ProjectID: "p1", AssignedTo: "ag-1"}
	err := tq.RequeueTask(task)
	require.NoError(t, err)
	assert.Empty(t, task.AssignedTo)
	assert.Equal(t, TaskStatusPending, task.Status)
}

func TestTaskQueue_GetTask_NotFound(t *testing.T) {
	tq := NewTaskQueue(nil)
	_, err := tq.GetTask("nonexistent")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "not found")
}

func TestTaskQueue_GetTask_Found(t *testing.T) {
	tq := NewTaskQueue(nil)
	task := &Task{ID: "t1", ProjectID: "p1"}
	require.NoError(t, tq.EnqueueTask(task))
	got, err := tq.GetTask("t1")
	require.NoError(t, err)
	assert.Equal(t, "t1", got.ID)
}

func TestTaskQueue_UpdateTaskStatus_RemovesFromQueuedWhenNotPending(t *testing.T) {
	tq := NewTaskQueue(nil)
	task := &Task{ID: "t1", ProjectID: "p1"}
	require.NoError(t, tq.EnqueueTask(task))
	task.Status = TaskStatusAssigned
	err := tq.UpdateTaskStatus(task)
	require.NoError(t, err)
	assert.Equal(t, 0, tq.QueueLength())
}

func TestTaskQueue_CancelTask_NotFound(t *testing.T) {
	tq := NewTaskQueue(nil)
	err := tq.CancelTask("nonexistent")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "not found")
}

func TestTaskQueue_CancelTask_Success(t *testing.T) {
	tq := NewTaskQueue(nil)
	task := &Task{ID: "t1", ProjectID: "p1"}
	require.NoError(t, tq.EnqueueTask(task))
	err := tq.CancelTask("t1")
	require.NoError(t, err)
	got, err := tq.GetTask("t1")
	require.NoError(t, err)
	assert.Equal(t, TaskStatusCanceled, got.Status)
}

func TestTaskQueue_ListTasks_FilterByProject(t *testing.T) {
	tq := NewTaskQueue(nil)
	require.NoError(t, tq.EnqueueTask(&Task{ID: "t1", ProjectID: "p1"}))
	require.NoError(t, tq.EnqueueTask(&Task{ID: "t2", ProjectID: "p2"}))
	list := tq.ListTasks("p1", "")
	require.Len(t, list, 1)
	assert.Equal(t, "p1", list[0].ProjectID)
}

func TestTaskQueue_ListTasks_FilterByStatus(t *testing.T) {
	tq := NewTaskQueue(nil)
	task := &Task{ID: "t1", ProjectID: "p1"}
	require.NoError(t, tq.EnqueueTask(task))
	task.Status = TaskStatusAssigned
	require.NoError(t, tq.UpdateTaskStatus(task))
	list := tq.ListTasks("", TaskStatusAssigned)
	require.Len(t, list, 1)
	assert.Equal(t, TaskStatusAssigned, list[0].Status)
}

func TestTaskQueue_QueueStats(t *testing.T) {
	tq := NewTaskQueue(nil)
	require.NoError(t, tq.EnqueueTask(&Task{ID: "t1", ProjectID: "p1", Priority: PriorityHigh}))
	stats := tq.QueueStats()
	assert.NotNil(t, stats)
	assert.Equal(t, 1, stats["total_tasks"])
	assert.Equal(t, 1, stats["queued"])
}

func TestTaskQueue_ListPendingTasks(t *testing.T) {
	tq := NewTaskQueue(nil)
	require.NoError(t, tq.EnqueueTask(&Task{ID: "t1", ProjectID: "p1"}))
	list := tq.ListPendingTasks("p1")
	require.Len(t, list, 1)
	assert.Equal(t, TaskStatusPending, list[0].Status)
}

func TestTaskQueue_CleanupOldTasks(t *testing.T) {
	tq := NewTaskQueue(nil)
	task := &Task{
		ID: "t1", ProjectID: "p1",
		Status:      TaskStatusCompleted,
		CompletedAt: time.Now().Add(-2 * time.Hour),
	}
	tq.mu.Lock()
	tq.taskIndex[task.ID] = task
	tq.mu.Unlock()

	n := tq.CleanupOldTasks(1 * time.Hour)
	assert.Equal(t, 1, n)
	_, err := tq.GetTask("t1")
	require.Error(t, err)
}
