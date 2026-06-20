//go:build integration

package agents

import (
	"context"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// setupTestDB creates an in-memory SQLite database for testing
func setupTestDB(t *testing.T) *gorm.DB {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	require.NoError(t, err, "failed to create test database")

	// AutoMigrate the necessary models
	err = db.AutoMigrate(
		&models.Agent{},
		&AgentLock{},
		&AgentTeam{},
		&AgentTeamMembership{},
		&ItemVersion{},
		&ConflictRecord{},
	)
	require.NoError(t, err, "failed to auto migrate models")

	// Create the agent_tasks table for task storage
	type TaskStore struct {
		ID        string `gorm:"primaryKey"`
		ProjectID string `gorm:"index"`
		Status    string `gorm:"index"`
		Priority  int    `gorm:"index"`
		Data      []byte `gorm:"type:jsonb"`
		CreatedAt time.Time
		UpdatedAt time.Time
	}
	err = db.Table("agent_tasks").AutoMigrate(&TaskStore{})
	require.NoError(t, err, "failed to auto migrate agent_tasks table")

	return db
}

// TestCoordinatorWorkflowCompleteTaskLifecycle tests the complete lifecycle of a task
// from creation through assignment, execution, and completion
func TestCoordinatorWorkflowCompleteTaskLifecycle(t *testing.T) {
	db := setupTestDB(t)
	coord := NewCoordinator(db, 30*time.Second)
	defer coord.Shutdown()

	// Register an agent
	agent := &RegisteredAgent{
		ID:        uuid.New().String(),
		Name:      "test-agent-1",
		ProjectID: "proj-1",
		Status:    StatusIdle,
		Capabilities: []AgentCapability{
			{Name: "analyze", Version: "1.0"},
		},
		Metadata: map[string]interface{}{},
	}
	err := coord.RegisterAgent(agent)
	require.NoError(t, err)

	// Enqueue a task
	task := &Task{
		ProjectID:            "proj-1",
		Type:                 "analyze",
		Priority:             PriorityNormal,
		RequiredCapabilities: []string{"analyze"},
		Parameters: map[string]interface{}{
			"data": "test-data",
		},
		Timeout:    10 * time.Second,
		MaxRetries: 3,
	}
	err = coord.TaskQueue.EnqueueTask(task)
	require.NoError(t, err)

	// Verify task is in queue
	assert.Equal(t, 1, coord.TaskQueue.QueueLength())

	// Agent requests next task
	nextTask, err := coord.GetNextTask(agent.ID)
	require.NoError(t, err)
	require.NotNil(t, nextTask)

	// Verify task is assigned
	assert.Equal(t, task.ID, nextTask.ID)
	assert.Equal(t, TaskStatusAssigned, nextTask.Status)
	assert.Equal(t, agent.ID, nextTask.AssignedTo)

	// Complete the task
	result := &TaskResult{
		Success: true,
		Data: map[string]interface{}{
			"result": "success",
		},
		Message:  "Task completed successfully",
		Duration: 1 * time.Second,
	}
	err = coord.CompleteTask(agent.ID, task.ID, result)
	require.NoError(t, err)

	// Verify agent is back to idle
	updatedAgent, err := coord.GetAgent(agent.ID)
	require.NoError(t, err)
	assert.Equal(t, StatusIdle, updatedAgent.Status)
	assert.Nil(t, updatedAgent.CurrentTask)
}

// TestCoordinatorWorkflowTaskFailureAndRetry tests task failure handling with retries
func TestCoordinatorWorkflowTaskFailureAndRetry(t *testing.T) {
	db := setupTestDB(t)
	coord := NewCoordinator(db, 30*time.Second)
	defer coord.Shutdown()

	// Register agent
	agent := &RegisteredAgent{
		ID:        uuid.New().String(),
		Name:      "retry-agent",
		ProjectID: "proj-2",
		Status:    StatusIdle,
		Capabilities: []AgentCapability{
			{Name: "process", Version: "1.0"},
		},
		Metadata: map[string]interface{}{},
	}
	err := coord.RegisterAgent(agent)
	require.NoError(t, err)

	// Create task with retries
	task := &Task{
		ProjectID:            "proj-2",
		Type:                 "process",
		Priority:             PriorityHigh,
		RequiredCapabilities: []string{"process"},
		Parameters:           map[string]interface{}{"data": "fail"},
		MaxRetries:           2,
	}
	err = coord.TaskQueue.EnqueueTask(task)
	require.NoError(t, err)

	taskID := task.ID

	// First attempt: get and fail task
	nextTask, err := coord.GetNextTask(agent.ID)
	require.NoError(t, err)
	assert.Equal(t, taskID, nextTask.ID)
	assert.Equal(t, 0, nextTask.RetryCount)

	// Fail the task
	err = coord.FailTask(agent.ID, taskID, "temporary failure")
	require.NoError(t, err)

	// Verify task was requeued
	requedTask, err := coord.TaskQueue.GetTask(taskID)
	require.NoError(t, err)
	assert.Equal(t, TaskStatusPending, requedTask.Status)
	assert.Equal(t, 1, requedTask.RetryCount)

	// Second attempt: get, fail again
	nextTask2, err := coord.GetNextTask(agent.ID)
	require.NoError(t, err)
	assert.Equal(t, taskID, nextTask2.ID)
	assert.Equal(t, 1, nextTask2.RetryCount)

	// Fail again
	err = coord.FailTask(agent.ID, taskID, "still failing")
	require.NoError(t, err)

	// Task should be requeued again
	requedTask2, err := coord.TaskQueue.GetTask(taskID)
	require.NoError(t, err)
	assert.Equal(t, TaskStatusPending, requedTask2.Status)
	assert.Equal(t, 2, requedTask2.RetryCount)

	// Third attempt
	nextTask3, err := coord.GetNextTask(agent.ID)
	require.NoError(t, err)
	assert.Equal(t, 2, nextTask3.RetryCount)

	// Fail once more - should NOT be requeued
	err = coord.FailTask(agent.ID, taskID, "final failure")
	require.NoError(t, err)

	// Verify task is now failed permanently
	finalTask, err := coord.TaskQueue.GetTask(taskID)
	require.NoError(t, err)
	assert.Equal(t, TaskStatusFailed, finalTask.Status)
	assert.Equal(t, 2, finalTask.RetryCount)
}

// TestCoordinatorWorkflowMultiAgentDistribution tests task distribution across multiple agents
func TestCoordinatorWorkflowMultiAgentDistribution(t *testing.T) {
	db := setupTestDB(t)
	coord := NewCoordinator(db, 30*time.Second)
	defer coord.Shutdown()

	projectID := uuid.New().String()
	const numAgents = 5
	const tasksPerAgent = 3

	// Register multiple agents
	agentIDs := make([]string, numAgents)
	for i := 0; i < numAgents; i++ {
		agent := &RegisteredAgent{
			ID:        uuid.New().String(),
			Name:      "agent-" + string(rune(i)),
			ProjectID: projectID,
			Status:    StatusIdle,
			Capabilities: []AgentCapability{
				{Name: "worker", Version: "1.0"},
			},
			Metadata: map[string]interface{}{},
		}
		agentIDs[i] = agent.ID
		err := coord.RegisterAgent(agent)
		require.NoError(t, err)
	}

	// Enqueue tasks
	taskIDs := make([]string, 0)
	for i := 0; i < numAgents*tasksPerAgent; i++ {
		task := &Task{
			ProjectID:            projectID,
			Type:                 "work",
			Priority:             TaskPriority(i % 4),
			RequiredCapabilities: []string{"worker"},
			Parameters: map[string]interface{}{
				"task_num": i,
			},
		}
		err := coord.TaskQueue.EnqueueTask(task)
		require.NoError(t, err)
		taskIDs = append(taskIDs, task.ID)
	}

	// Distribute tasks to agents
	assignedTasks := make(map[string][]string)
	assignmentMutex := sync.Mutex{}

	var wg sync.WaitGroup
	for _, agentID := range agentIDs {
		wg.Add(1)
		go func(aid string) {
			defer wg.Done()
			for i := 0; i < tasksPerAgent; i++ {
				task, err := coord.GetNextTask(aid)
				if err != nil || task == nil {
					break
				}
				assignmentMutex.Lock()
				assignedTasks[aid] = append(assignedTasks[aid], task.ID)
				assignmentMutex.Unlock()

				// Complete task
				result := &TaskResult{Success: true}
				_ = coord.CompleteTask(aid, task.ID, result)
			}
		}(agentID)
	}

	wg.Wait()

	// Verify distribution
	totalAssigned := 0
	for agentID, tasks := range assignedTasks {
		assert.NotEmpty(t, tasks, "agent %s should have tasks", agentID)
		totalAssigned += len(tasks)
	}
	assert.Equal(t, numAgents*tasksPerAgent, totalAssigned)
}

// TestCoordinatorWorkflowHeartbeatTimeout tests agent timeout detection
func TestCoordinatorWorkflowHeartbeatTimeout(t *testing.T) {
	db := setupTestDB(t)
	heartbeatTimeout := 100 * time.Millisecond
	coord := NewCoordinator(db, heartbeatTimeout)
	defer coord.Shutdown()

	// Register agent
	agent := &RegisteredAgent{
		ID:        uuid.New().String(),
		Name:      "timeout-agent",
		ProjectID: "proj-3",
		Status:    StatusIdle,
		Capabilities: []AgentCapability{
			{Name: "work", Version: "1.0"},
		},
		Metadata: map[string]interface{}{},
	}
	err := coord.RegisterAgent(agent)
	require.NoError(t, err)

	// Enqueue a task and assign to agent
	task := &Task{
		ProjectID:            "proj-3",
		Type:                 "work",
		RequiredCapabilities: []string{"work"},
		MaxRetries:           1,
	}
	err = coord.TaskQueue.EnqueueTask(task)
	require.NoError(t, err)

	nextTask, err := coord.GetNextTask(agent.ID)
	require.NoError(t, err)
	require.NotNil(t, nextTask)

	// Verify agent is busy with task
	busyAgent, err := coord.GetAgent(agent.ID)
	require.NoError(t, err)
	assert.Equal(t, StatusBusy, busyAgent.Status)
	assert.NotNil(t, busyAgent.CurrentTask)

	// Simulate heartbeat timeout by waiting beyond timeout
	time.Sleep(heartbeatTimeout + 50*time.Millisecond)

	// Force heartbeat check
	coord.checkHeartbeats()

	// Verify agent is marked offline
	offlineAgent, err := coord.GetAgent(agent.ID)
	require.NoError(t, err)
	assert.Equal(t, StatusOffline, offlineAgent.Status)
	assert.Nil(t, offlineAgent.CurrentTask)

	// Verify task was requeued
	requedTask, err := coord.TaskQueue.GetTask(task.ID)
	require.NoError(t, err)
	assert.Equal(t, TaskStatusPending, requedTask.Status)
}

// TestDistributedCoordinationLockAcquisition tests optimistic and pessimistic locking
func TestDistributedCoordinationLockAcquisition(t *testing.T) {
	db := setupTestDB(t)
	lockMgr := NewLockManager(db, 5*time.Second)
	defer lockMgr.Shutdown()

	ctx := context.Background()
	itemID := uuid.New().String()
	agent1 := uuid.New().String()
	agent2 := uuid.New().String()

	// Agent 1 acquires pessimistic lock
	lock1, err := lockMgr.AcquireLock(ctx, itemID, "item", agent1, LockTypePessimistic)
	require.NoError(t, err)
	require.NotNil(t, lock1)
	assert.Equal(t, agent1, lock1.AgentID)

	// Agent 2 attempts to acquire same item - should fail
	lock2, err := lockMgr.AcquireLock(ctx, itemID, "item", agent2, LockTypePessimistic)
	assert.Error(t, err)
	assert.Nil(t, lock2)

	// Agent 1 releases lock
	err = lockMgr.ReleaseLock(ctx, lock1.ID, agent1)
	require.NoError(t, err)

	// Now agent 2 should be able to acquire
	lock2, err = lockMgr.AcquireLock(ctx, itemID, "item", agent2, LockTypePessimistic)
	require.NoError(t, err)
	assert.NotNil(t, lock2)
	assert.Equal(t, agent2, lock2.AgentID)
}

// TestDistributedCoordinationOptimisticLocking tests version-based locking
func TestDistributedCoordinationOptimisticLocking(t *testing.T) {
	db := setupTestDB(t)
	lockMgr := NewLockManager(db, 5*time.Second)
	defer lockMgr.Shutdown()

	ctx := context.Background()
	itemID := uuid.New().String()
	agent1 := uuid.New().String()

	// Acquire optimistic lock (should get version 1)
	lock1, err := lockMgr.AcquireLock(ctx, itemID, "item", agent1, LockTypeOptimistic)
	require.NoError(t, err)
	assert.Equal(t, int64(1), lock1.Version)

	// Record version 1
	err = lockMgr.RecordVersion(ctx, itemID, agent1, 1, map[string]interface{}{}, "hash0", "hash1")
	require.NoError(t, err)

	// Release lock
	err = lockMgr.ReleaseLock(ctx, lock1.ID, agent1)
	require.NoError(t, err)

	// Next lock should have version 2
	lock2, err := lockMgr.AcquireLock(ctx, itemID, "item", agent1, LockTypeOptimistic)
	require.NoError(t, err)
	assert.Equal(t, int64(2), lock2.Version)
}

// TestDistributedCoordinationConflictDetection tests conflict detection between agents
func TestDistributedCoordinationConflictDetection(t *testing.T) {
	db := setupTestDB(t)
	lockMgr := NewLockManager(db, 5*time.Second)
	defer lockMgr.Shutdown()

	conflictDetector := NewConflictDetector(db, lockMgr)

	ctx := context.Background()
	itemID := uuid.New().String()
	agent1 := uuid.New().String()
	agent2 := uuid.New().String()

	// Agent 1 acquires lock
	lock1, err := lockMgr.AcquireLock(ctx, itemID, "item", agent1, LockTypePessimistic)
	require.NoError(t, err)

	// Agent 2 tries to modify - should detect conflict
	conflict, err := conflictDetector.DetectConflict(ctx, itemID, agent2, 1)
	require.NoError(t, err)
	require.NotNil(t, conflict)
	assert.Equal(t, "concurrent_modification", conflict.ConflictType)
	assert.Contains(t, conflict.ConflictingAgents, agent1)

	// Release lock
	_ = lockMgr.ReleaseLock(ctx, lock1.ID, agent1)

	// Now no conflict should be detected
	conflict2, err := conflictDetector.DetectConflict(ctx, itemID, agent2, 1)
	require.NoError(t, err)
	assert.Nil(t, conflict2)
}

// TestQueueProcessingPriority tests task priority ordering
func TestQueueProcessingPriority(t *testing.T) {
	db := setupTestDB(t)
	queue := NewTaskQueue(db)

	projectID := uuid.New().String()
	cap := []AgentCapability{{Name: "work", Version: "1.0"}}

	// Create tasks with different priorities
	priorities := []TaskPriority{PriorityLow, PriorityCritical, PriorityNormal, PriorityHigh}
	for _, p := range priorities {
		task := &Task{
			ProjectID:            projectID,
			Type:                 "work",
			Priority:             p,
			RequiredCapabilities: []string{"work"},
		}
		err := queue.EnqueueTask(task)
		require.NoError(t, err)
	}

	// Dequeue tasks - should come in priority order
	task1 := queue.DequeueTask(projectID, cap)
	require.NotNil(t, task1)
	assert.Equal(t, PriorityCritical, task1.Priority)

	task2 := queue.DequeueTask(projectID, cap)
	require.NotNil(t, task2)
	assert.Equal(t, PriorityHigh, task2.Priority)

	task3 := queue.DequeueTask(projectID, cap)
	require.NotNil(t, task3)
	assert.Equal(t, PriorityNormal, task3.Priority)

	task4 := queue.DequeueTask(projectID, cap)
	require.NotNil(t, task4)
	assert.Equal(t, PriorityLow, task4.Priority)
}

// TestQueueProcessingCapabilityMatching tests task capability filtering
func TestQueueProcessingCapabilityMatching(t *testing.T) {
	db := setupTestDB(t)
	queue := NewTaskQueue(db)

	projectID := uuid.New().String()

	// Task requiring specific capability
	task1 := &Task{
		ProjectID:            projectID,
		Type:                 "analyze",
		RequiredCapabilities: []string{"analyzer", "fast"},
	}
	err := queue.EnqueueTask(task1)
	require.NoError(t, err)

	// Task with no requirements
	task2 := &Task{
		ProjectID: projectID,
		Type:      "basic",
	}
	err = queue.EnqueueTask(task2)
	require.NoError(t, err)

	// Agent with limited capabilities - only has "analyzer"
	limitedCaps := []AgentCapability{
		{Name: "analyzer", Version: "1.0"},
	}

	// Should get task2 first (no required capabilities)
	dequeued := queue.DequeueTask(projectID, limitedCaps)
	require.NotNil(t, dequeued)
	assert.Equal(t, task2.ID, dequeued.ID)

	// task1 is still in queue but requires both "analyzer" and "fast"
	// Agent only has "analyzer", so should not get task1
	dequeued2 := queue.DequeueTask(projectID, limitedCaps)
	assert.Nil(t, dequeued2, "agent without 'fast' capability should not get task requiring both")

	// Now try with full capabilities
	fullCaps := []AgentCapability{
		{Name: "analyzer", Version: "1.0"},
		{Name: "fast", Version: "1.0"},
	}
	dequeued3 := queue.DequeueTask(projectID, fullCaps)
	require.NotNil(t, dequeued3)
	assert.Equal(t, task1.ID, dequeued3.ID)
}

// TestTeamManagementRoleBasedPermissions tests team roles and permissions
func TestTeamManagementRoleBasedPermissions(t *testing.T) {
	db := setupTestDB(t)
	teamMgr := NewTeamManager(db)

	ctx := context.Background()

	// Create team with roles
	team := &AgentTeam{
		ProjectID:   uuid.New().String(),
		Name:        "engineering",
		Description: "Engineering team",
		Roles: map[string]TeamRole{
			"admin": {
				Name:        "admin",
				Permissions: []string{"read", "write", "delete", "lock"},
				Priority:    100,
			},
			"engineer": {
				Name:        "engineer",
				Permissions: []string{"read", "write"},
				Priority:    50,
			},
			"viewer": {
				Name:        "viewer",
				Permissions: []string{"read"},
				Priority:    10,
			},
		},
		Metadata: map[string]interface{}{},
	}
	err := teamMgr.CreateTeam(ctx, team)
	require.NoError(t, err)

	agentID := uuid.New().String()

	// Add agent as engineer
	err = teamMgr.AddTeamMember(ctx, team.ID, agentID, "engineer")
	require.NoError(t, err)

	// Check permissions
	perms, priority, err := teamMgr.GetAgentPermissions(ctx, agentID)
	require.NoError(t, err)
	assert.Equal(t, 50, priority)
	assert.Contains(t, perms, "read")
	assert.Contains(t, perms, "write")
	assert.NotContains(t, perms, "delete")

	// Check specific permission
	hasRead, err := teamMgr.HasPermission(ctx, agentID, "read")
	require.NoError(t, err)
	assert.True(t, hasRead)

	hasDelete, err := teamMgr.HasPermission(ctx, agentID, "delete")
	require.NoError(t, err)
	assert.False(t, hasDelete)
}

// TestConflictResolution tests conflict resolution strategies
func TestConflictResolution(t *testing.T) {
	db := setupTestDB(t)
	lockMgr := NewLockManager(db, 5*time.Second)
	defer lockMgr.Shutdown()

	ctx := context.Background()
	conflictID := uuid.New().String()

	// Create a conflict record with empty agent array
	conflict := &ConflictRecord{
		ID:                 conflictID,
		ItemID:             uuid.New().String(),
		ConflictingAgents:  []string{},
		ConflictType:       "concurrent_modification",
		ResolutionStrategy: ResolutionLastWriteWins,
		ResolutionStatus:   resolutionStatusPending,
		ConflictData: JSONMap{
			"test": "data",
		},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	// Save conflict
	err := db.Create(conflict).Error
	require.NoError(t, err)

	// Resolve conflict
	detector := NewConflictDetector(db, lockMgr)
	resolver := uuid.New().String()
	resolution := map[string]interface{}{
		"chosen_version": "agent1_v2",
	}

	err = detector.ResolveConflict(ctx, conflictID, resolver, ResolutionLastWriteWins, resolution)
	require.NoError(t, err)

	// Verify conflict is resolved
	var resolved ConflictRecord
	err = db.First(&resolved, "id = ?", conflictID).Error
	require.NoError(t, err)
	assert.Equal(t, resolutionStatusResolved, resolved.ResolutionStatus)
	assert.Equal(t, resolver, resolved.ResolvedBy)
	assert.NotNil(t, resolved.ResolvedAt)
}

// TestConcurrentTaskProcessing tests concurrent task processing with race conditions
func TestConcurrentTaskProcessing(t *testing.T) {
	db := setupTestDB(t)
	coord := NewCoordinator(db, 30*time.Second)
	defer coord.Shutdown()

	projectID := uuid.New().String()
	const numAgents = 10
	const numTasks = 50

	// Register agents
	for i := 0; i < numAgents; i++ {
		agent := &RegisteredAgent{
			ID:        uuid.New().String(),
			Name:      "concurrent-agent-" + string(rune(i)),
			ProjectID: projectID,
			Status:    StatusIdle,
			Capabilities: []AgentCapability{
				{Name: "concurrent", Version: "1.0"},
			},
			Metadata: map[string]interface{}{},
		}
		err := coord.RegisterAgent(agent)
		require.NoError(t, err)
	}

	// Enqueue tasks
	for i := 0; i < numTasks; i++ {
		task := &Task{
			ProjectID:            projectID,
			Type:                 "concurrent-work",
			RequiredCapabilities: []string{"concurrent"},
			Parameters: map[string]interface{}{
				"iteration": i,
			},
		}
		err := coord.TaskQueue.EnqueueTask(task)
		require.NoError(t, err)
	}

	// Track completion
	var completed int32
	agents := coord.ListAgents(projectID)

	var wg sync.WaitGroup
	for _, agent := range agents {
		wg.Add(1)
		go func(a *RegisteredAgent) {
			defer wg.Done()
			for {
				task, err := coord.GetNextTask(a.ID)
				if err != nil || task == nil {
					break
				}

				// Simulate work
				time.Sleep(1 * time.Millisecond)

				result := &TaskResult{Success: true}
				err = coord.CompleteTask(a.ID, task.ID, result)
				if err == nil {
					atomic.AddInt32(&completed, 1)
				}
			}
		}(agent)
	}

	wg.Wait()

	// Verify all tasks completed
	assert.Equal(t, int32(numTasks), completed)
}

// TestQueueCleanup tests task cleanup of old completed tasks
func TestQueueCleanup(t *testing.T) {
	db := setupTestDB(t)
	queue := NewTaskQueue(db)

	projectID := uuid.New().String()

	// Create completed tasks
	for i := 0; i < 5; i++ {
		task := &Task{
			ProjectID: projectID,
			Type:      "cleanup-test",
			Status:    TaskStatusCompleted,
			CreatedAt: time.Now().Add(-2 * time.Hour),
		}
		err := queue.EnqueueTask(task)
		require.NoError(t, err)
		// Manually mark as completed
		task.Status = TaskStatusCompleted
		task.CompletedAt = time.Now().Add(-2 * time.Hour)
		_ = queue.UpdateTaskStatus(task)
	}

	// Create recent completed task
	recentTask := &Task{
		ProjectID: projectID,
		Type:      "cleanup-test",
		Status:    TaskStatusCompleted,
		CreatedAt: time.Now(),
	}
	err := queue.EnqueueTask(recentTask)
	require.NoError(t, err)
	recentTask.Status = TaskStatusCompleted
	recentTask.CompletedAt = time.Now()
	_ = queue.UpdateTaskStatus(recentTask)

	// Initial count
	allTasks := queue.ListTasks(projectID, "")
	assert.Equal(t, 6, len(allTasks))

	// Cleanup tasks older than 1 hour
	cleaned := queue.CleanupOldTasks(1 * time.Hour)
	assert.Equal(t, 5, cleaned)

	// Verify only recent task remains
	remainingTasks := queue.ListTasks(projectID, "")
	assert.Equal(t, 1, len(remainingTasks))
}

// TestQueueStats tests queue statistics collection
func TestQueueStats(t *testing.T) {
	db := setupTestDB(t)
	queue := NewTaskQueue(db)

	projectID := uuid.New().String()

	// Create various tasks - all start as pending when enqueued
	taskConfigs := []struct {
		priority TaskPriority
	}{
		{PriorityCritical},
		{PriorityCritical},
		{PriorityHigh},
		{PriorityNormal},
		{PriorityLow},
	}

	for _, cfg := range taskConfigs {
		task := &Task{
			ProjectID: projectID,
			Type:      "stats-test",
			Priority:  cfg.priority,
		}
		err := queue.EnqueueTask(task)
		require.NoError(t, err)
	}

	stats := queue.QueueStats()

	assert.Equal(t, 5, stats["total_tasks"])
	// All 5 tasks are in the queue (pending status)
	assert.Equal(t, 5, stats["queued"])

	byStatus := stats["by_status"].(map[string]int)
	assert.Equal(t, 5, byStatus["pending"])

	byPriority := stats["by_priority"].(map[string]int)
	assert.Equal(t, 2, byPriority["critical"])
	assert.Equal(t, 1, byPriority["high"])
	assert.Equal(t, 1, byPriority["normal"])
	assert.Equal(t, 1, byPriority["low"])
}
