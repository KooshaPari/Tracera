//go:build !integration && !e2e

package agents

import (
	"sync"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

const coordinatorHeartbeatDelay = 10 * time.Millisecond

// ===== COORDINATOR STATE MANAGEMENT TESTS =====

// TestCoordinatorStateInitialization tests coordinator state initialization
func TestCoordinatorStateInitialization(t *testing.T) {
	agents := make(map[string]*RegisteredAgent)
	assert.NotNil(t, agents)
	assert.Empty(t, agents)

	var mu sync.RWMutex
	assert.NotNil(t, &mu)
}

// TestAgentRegistrationInMemory tests agent registration in memory
func TestAgentRegistrationInMemory(t *testing.T) {
	agents := make(map[string]*RegisteredAgent)
	var mu sync.RWMutex

	projectID := uuid.New().String()
	agent := &RegisteredAgent{
		ID:            uuid.New().String(),
		Name:          "test-agent",
		ProjectID:     projectID,
		Status:        StatusIdle,
		LastHeartbeat: time.Now(),
		Capabilities: []AgentCapability{
			{Name: "test-cap", Version: "1.0"},
		},
	}

	mu.Lock()
	agents[agent.ID] = agent
	mu.Unlock()

	mu.RLock()
	retrieved := agents[agent.ID]
	mu.RUnlock()

	assert.NotNil(t, retrieved)
	assert.Equal(t, agent.ID, retrieved.ID)
	assert.Equal(t, "test-agent", retrieved.Name)
}

// TestAgentUnregistrationInMemory tests agent unregistration in memory
func TestAgentUnregistrationInMemory(t *testing.T) {
	agents := make(map[string]*RegisteredAgent)
	var mu sync.RWMutex

	agent := &RegisteredAgent{
		ID:   uuid.New().String(),
		Name: "test-agent",
	}

	mu.Lock()
	agents[agent.ID] = agent
	mu.Unlock()

	mu.Lock()
	delete(agents, agent.ID)
	mu.Unlock()

	mu.RLock()
	_, exists := agents[agent.ID]
	mu.RUnlock()

	assert.False(t, exists)
}

// ===== AGENT LIFECYCLE TESTS =====

// TestAgentStatusTransitions tests agent status transitions
func TestAgentStatusTransitions(t *testing.T) {
	agent := &RegisteredAgent{
		ID:     uuid.New().String(),
		Name:   "test-agent",
		Status: StatusIdle,
	}

	assert.Equal(t, StatusIdle, agent.Status)

	agent.Status = StatusActive
	assert.Equal(t, StatusActive, agent.Status)

	agent.Status = StatusBusy
	assert.Equal(t, StatusBusy, agent.Status)

	agent.Status = StatusError
	assert.Equal(t, StatusError, agent.Status)

	agent.Status = StatusOffline
	assert.Equal(t, StatusOffline, agent.Status)
}

// TestAgentHeartbeatUpdates tests agent heartbeat timestamp updates
func TestAgentHeartbeatUpdates(t *testing.T) {
	agent := &RegisteredAgent{
		ID:            uuid.New().String(),
		LastHeartbeat: time.Now().Add(-5 * time.Minute),
	}

	oldTime := agent.LastHeartbeat
	time.Sleep(coordinatorHeartbeatDelay)
	agent.LastHeartbeat = time.Now()

	assert.True(t, agent.LastHeartbeat.After(oldTime))
}

// TestAgentCapabilityManagement tests capability management
func TestAgentCapabilityManagement(t *testing.T) {
	agent := &RegisteredAgent{
		ID: uuid.New().String(),
		Capabilities: []AgentCapability{
			{Name: "read", Version: "1.0", Tags: []string{"io"}},
			{Name: "write", Version: "1.0", Tags: []string{"io"}},
			{Name: "compute", Version: "2.0", Tags: []string{"processing"}},
		},
	}

	assert.Len(t, agent.Capabilities, 3)

	capMap := make(map[string]bool)
	for _, cap := range agent.Capabilities {
		capMap[cap.Name] = true
	}

	assert.True(t, capMap["read"])
	assert.True(t, capMap["write"])
	assert.True(t, capMap["compute"])
	assert.False(t, capMap["delete"])
}

// TestAgentMetadataStorage tests agent metadata storage
func TestAgentMetadataStorage(t *testing.T) {
	agent := &RegisteredAgent{
		ID: uuid.New().String(),
		Metadata: map[string]interface{}{
			"version":      "1.0.0",
			"environment":  "test",
			"cpu_cores":    4,
			"memory_gb":    8.5,
			"is_enabled":   true,
			"capabilities": []string{"read", "write"},
		},
	}

	assert.Equal(t, "1.0.0", agent.Metadata["version"])
	assert.Equal(t, "test", agent.Metadata["environment"])
	assert.Equal(t, 4, agent.Metadata["cpu_cores"])
	assert.Equal(t, 8.5, agent.Metadata["memory_gb"])
	assert.Equal(t, true, agent.Metadata["is_enabled"])
}

// ===== TASK MANAGEMENT TESTS =====

// TestTaskCreation tests task creation and fields
func TestTaskCreation(t *testing.T) {
	taskID := uuid.New().String()
	projectID := uuid.New().String()

	task := &Task{
		ID:         taskID,
		ProjectID:  projectID,
		Type:       "analyze",
		Priority:   PriorityHigh,
		Status:     TaskStatusPending,
		CreatedAt:  time.Now(),
		Timeout:    30 * time.Second,
		MaxRetries: 3,
		Tags:       []string{"important"},
		Metadata: map[string]interface{}{
			"user_id": "user-123",
		},
	}

	assert.Equal(t, taskID, task.ID)
	assert.Equal(t, projectID, task.ProjectID)
	assert.Equal(t, "analyze", task.Type)
	assert.Equal(t, PriorityHigh, task.Priority)
	assert.Equal(t, TaskStatusPending, task.Status)
	assert.Equal(t, 30*time.Second, task.Timeout)
	assert.Equal(t, 3, task.MaxRetries)
}

// TestTaskStatusTransitions tests task status changes
func TestTaskStatusTransitions(t *testing.T) {
	task := &Task{
		ID:     uuid.New().String(),
		Status: TaskStatusPending,
	}

	assert.Equal(t, TaskStatusPending, task.Status)

	task.Status = TaskStatusAssigned
	assert.Equal(t, TaskStatusAssigned, task.Status)

	task.Status = TaskStatusRunning
	assert.Equal(t, TaskStatusRunning, task.Status)

	task.Status = TaskStatusCompleted
	assert.Equal(t, TaskStatusCompleted, task.Status)
	task.CompletedAt = time.Now()
	assert.False(t, task.CompletedAt.IsZero())
}

// TestTaskRetryManagement tests retry count management
func TestTaskRetryManagement(t *testing.T) {
	task := &Task{
		ID:         uuid.New().String(),
		MaxRetries: 3,
		RetryCount: 0,
	}

	assert.Equal(t, 0, task.RetryCount)
	assert.Equal(t, 3, task.MaxRetries)
	assert.True(t, task.RetryCount < task.MaxRetries)

	task.RetryCount = 1
	assert.True(t, task.RetryCount < task.MaxRetries)

	task.RetryCount = 3
	assert.False(t, task.RetryCount < task.MaxRetries)
}

// TestTaskResultHandling tests task result handling
func TestTaskResultHandling(t *testing.T) {
	result := &TaskResult{
		Success: true,
		Data: map[string]interface{}{
			"output": "processed",
			"count":  42,
		},
		Message:  "Task completed successfully",
		Duration: 5 * time.Second,
	}

	assert.True(t, result.Success)
	assert.Equal(t, "processed", result.Data["output"])
	assert.Equal(t, 42, result.Data["count"])
	assert.Equal(t, "Task completed successfully", result.Message)
	assert.Equal(t, 5*time.Second, result.Duration)
}

// ===== CAPABILITY MATCHING TESTS =====

// TestCapabilityMatchingExactMatchComprehensive tests exact capability match
func TestCapabilityMatchingExactMatchComprehensive(t *testing.T) {
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

	capMap := make(map[string]bool)
	for _, cap := range agent.Capabilities {
		capMap[cap.Name] = true
	}

	hasAll := true
	for _, required := range task.RequiredCapabilities {
		if !capMap[required] {
			hasAll = false
			break
		}
	}

	assert.True(t, hasAll)
}

// TestCapabilityMatchingPartialMismatch tests partial capability mismatch
func TestCapabilityMatchingPartialMismatch(t *testing.T) {
	agent := &RegisteredAgent{
		Capabilities: []AgentCapability{
			{Name: "read"},
			{Name: "write"},
		},
	}

	task := &Task{
		RequiredCapabilities: []string{"read", "write", "delete"},
	}

	capMap := make(map[string]bool)
	for _, cap := range agent.Capabilities {
		capMap[cap.Name] = true
	}

	hasAll := true
	for _, required := range task.RequiredCapabilities {
		if !capMap[required] {
			hasAll = false
			break
		}
	}

	assert.False(t, hasAll)
}

// TestCapabilityMatchingNoCapabilities tests agent with no capabilities
func TestCapabilityMatchingNoCapabilities(t *testing.T) {
	agent := &RegisteredAgent{
		Capabilities: []AgentCapability{},
	}

	task := &Task{
		RequiredCapabilities: []string{"read"},
	}

	capMap := make(map[string]bool)
	for _, cap := range agent.Capabilities {
		capMap[cap.Name] = true
	}

	hasAll := true
	for _, required := range task.RequiredCapabilities {
		if !capMap[required] {
			hasAll = false
			break
		}
	}

	assert.False(t, hasAll)
}

// TestCapabilityMatchingNoRequirements tests task with no requirements
func TestCapabilityMatchingNoRequirements(t *testing.T) {
	task := &Task{
		RequiredCapabilities: []string{},
	}

	hasAll := true
	for range task.RequiredCapabilities {
		hasAll = false
		break
	}

	if len(task.RequiredCapabilities) == 0 {
		hasAll = true
	}

	assert.True(t, hasAll)
}

// ===== AGENT ASSIGNMENT TESTS =====

// TestSelectIdleAgent tests selection of idle agent
func TestSelectIdleAgent(t *testing.T) {
	agents := map[string]*RegisteredAgent{
		"1": {
			ID:     "1",
			Status: StatusIdle,
		},
		"2": {
			ID:     "2",
			Status: StatusBusy,
		},
		"3": {
			ID:     "3",
			Status: StatusIdle,
		},
	}

	var idleAgent *RegisteredAgent
	for _, agent := range agents {
		if agent.Status == StatusIdle {
			idleAgent = agent
			break
		}
	}

	assert.NotNil(t, idleAgent)
	assert.Equal(t, StatusIdle, idleAgent.Status)
}

// TestLoadBalancingAcrossAgents tests load distribution across agents
func TestLoadBalancingAcrossAgents(t *testing.T) {
	agents := map[string]*RegisteredAgent{
		"1": {ID: "1", Status: StatusIdle, CurrentTask: nil},
		"2": {ID: "2", Status: StatusIdle, CurrentTask: nil},
		"3": {ID: "3", Status: StatusBusy, CurrentTask: &Task{ID: "task-x"}},
	}

	tasks := []*Task{
		{ID: "task-1"},
		{ID: "task-2"},
		{ID: "task-3"},
	}

	assignments := make(map[string]string)
	for _, task := range tasks {
		for _, agent := range agents {
			if agent.Status == StatusIdle && agent.CurrentTask == nil {
				assignments[agent.ID] = task.ID
				agent.Status = StatusBusy
				agent.CurrentTask = task
				break
			}
		}
	}

	assert.Equal(t, 2, len(assignments))
	assert.Contains(t, assignments, "1")
	assert.Contains(t, assignments, "2")
}

// ===== CONCURRENT OPERATION TESTS =====

// TestConcurrentAgentHeartbeats tests concurrent heartbeat updates
func TestConcurrentAgentHeartbeats(t *testing.T) {
	agents := make(map[string]*RegisteredAgent)
	var mu sync.RWMutex

	for i := 0; i < 10; i++ {
		agents[uuid.New().String()] = &RegisteredAgent{
			Name: "agent-" + uuid.New().String(),
		}
	}

	var wg sync.WaitGroup
	for agentID, agent := range agents {
		wg.Add(1)
		go func(_ string, ag *RegisteredAgent) {
			defer wg.Done()
			for j := 0; j < 100; j++ {
				mu.Lock()
				ag.LastHeartbeat = time.Now()
				ag.Status = StatusActive
				mu.Unlock()
			}
		}(agentID, agent)
	}

	wg.Wait()

	mu.RLock()
	for _, agent := range agents {
		assert.False(t, agent.LastHeartbeat.IsZero())
		assert.Equal(t, StatusActive, agent.Status)
	}
	mu.RUnlock()
}

// TestConcurrentTaskAssignmentMemory tests concurrent task assignments in memory
func TestConcurrentTaskAssignmentMemory(t *testing.T) {
	agents := make(map[string]*RegisteredAgent)
	tasks := make(map[string]*Task)
	var mu sync.RWMutex

	for i := 0; i < 5; i++ {
		agents[uuid.New().String()] = &RegisteredAgent{
			Status: StatusIdle,
		}
	}

	var wg sync.WaitGroup
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			task := &Task{
				ID:       uuid.New().String(),
				Priority: TaskPriority(idx % 4),
			}

			mu.Lock()
			tasks[task.ID] = task

			for _, agent := range agents {
				if agent.Status == StatusIdle && agent.CurrentTask == nil {
					agent.CurrentTask = task
					agent.Status = StatusBusy
					break
				}
			}
			mu.Unlock()
		}(i)
	}

	wg.Wait()

	mu.RLock()
	assert.Len(t, tasks, 20)
	mu.RUnlock()
}

// TestRaceConditionDetection tests race condition scenarios
func TestRaceConditionDetection(t *testing.T) {
	var mu sync.RWMutex
	agentMap := make(map[string]*RegisteredAgent)

	var wg sync.WaitGroup

	// Writer goroutine
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(_ int) {
			defer wg.Done()
			for j := 0; j < 50; j++ {
				agent := &RegisteredAgent{
					ID:     uuid.New().String(),
					Status: StatusActive,
				}
				mu.Lock()
				agentMap[agent.ID] = agent
				mu.Unlock()
			}
		}(i)
	}

	// Reader goroutine
	wg.Add(1)
	go func() {
		defer wg.Done()
		for i := 0; i < 250; i++ {
			mu.RLock()
			_ = len(agentMap)
			mu.RUnlock()
		}
	}()

	wg.Wait()
	assert.Greater(t, len(agentMap), 0)
}

// ===== ERROR HANDLING TESTS =====

// TestTaskFailureWithRetry tests task failure handling with retry
func TestTaskFailureWithRetry(t *testing.T) {
	task := &Task{
		ID:           uuid.New().String(),
		Status:       TaskStatusFailed,
		MaxRetries:   3,
		RetryCount:   0,
		ErrorMessage: "Connection timeout",
	}

	assert.Equal(t, TaskStatusFailed, task.Status)
	assert.True(t, task.RetryCount < task.MaxRetries)

	task.RetryCount++
	task.Status = TaskStatusPending
	assert.Equal(t, TaskStatusPending, task.Status)
	assert.Equal(t, 1, task.RetryCount)
}

// TestTaskFailureExceedsRetries tests task failure after max retries
func TestTaskFailureExceedsRetries(t *testing.T) {
	task := &Task{
		ID:         uuid.New().String(),
		MaxRetries: 3,
		RetryCount: 3,
		Status:     TaskStatusFailed,
	}

	shouldRetry := task.RetryCount < task.MaxRetries
	assert.False(t, shouldRetry)

	task.Status = TaskStatusFailed
	assert.Equal(t, TaskStatusFailed, task.Status)
}

// TestAgentOfflineScenario tests agent offline behavior
func TestAgentOfflineScenario(t *testing.T) {
	agent := &RegisteredAgent{
		ID:            uuid.New().String(),
		Status:        StatusActive,
		LastHeartbeat: time.Now(),
		CurrentTask:   &Task{ID: "task-1"},
	}

	timeout := 5 * time.Minute
	agent.LastHeartbeat = time.Now().Add(-10 * time.Minute)

	isTimedOut := time.Since(agent.LastHeartbeat) > timeout
	assert.True(t, isTimedOut)

	// Mark as offline
	agent.Status = StatusOffline
	taskToRequeue := agent.CurrentTask
	agent.CurrentTask = nil

	assert.Equal(t, StatusOffline, agent.Status)
	assert.Nil(t, agent.CurrentTask)
	assert.NotNil(t, taskToRequeue)
}

// ===== PRIORITY AND ORDERING TESTS =====

// TestTaskPriorityOrdering tests task priority levels
func TestTaskPriorityOrdering(t *testing.T) {
	tasks := []struct {
		name     string
		priority TaskPriority
	}{
		{"Critical", PriorityCritical},
		{"High", PriorityHigh},
		{"Normal", PriorityNormal},
		{"Low", PriorityLow},
	}

	for _, tt := range tasks {
		t.Run(tt.name, func(t *testing.T) {
			task := &Task{
				ID:       uuid.New().String(),
				Priority: tt.priority,
			}

			assert.Equal(t, tt.priority, task.Priority)
		})
	}
}

// TestPriorityComparison tests priority comparison
func TestPriorityComparison(t *testing.T) {
	assert.Greater(t, int(PriorityCritical), int(PriorityHigh))
	assert.Greater(t, int(PriorityHigh), int(PriorityNormal))
	assert.Greater(t, int(PriorityNormal), int(PriorityLow))
}

// ===== PROTOCOL TESTS =====

// TestMessageTypeConstants tests message type constants
func TestMessageTypeConstants(t *testing.T) {
	types := []MessageType{
		MsgTypeRegister,
		MsgTypeHeartbeat,
		MsgTypeTaskRequest,
		MsgTypeTaskResult,
		MsgTypeTaskError,
		MsgTypeUnregister,
		MsgTypeAck,
		MsgTypeTaskAssigned,
		MsgTypeNoTask,
		MsgTypeError,
		MsgTypeShutdown,
	}

	for _, mt := range types {
		assert.NotEmpty(t, mt)
	}
}

// TestMessageStructure tests message structure
func TestMessageStructure(t *testing.T) {
	msg := &Message{
		Type:      MsgTypeRegister,
		AgentID:   uuid.New().String(),
		Timestamp: time.Now(),
		Payload: map[string]interface{}{
			"name": "test-agent",
		},
	}

	assert.Equal(t, MsgTypeRegister, msg.Type)
	assert.NotEmpty(t, msg.AgentID)
	assert.NotZero(t, msg.Timestamp)
	assert.NotEmpty(t, msg.Payload)
}

// ===== STATE CONSISTENCY TESTS =====

// TestAgentStateConsistency tests agent state remains consistent
func TestAgentStateConsistency(t *testing.T) {
	agent := &RegisteredAgent{
		ID:        uuid.New().String(),
		Name:      "test",
		ProjectID: uuid.New().String(),
		Status:    StatusIdle,
	}

	id1 := agent.ID
	status1 := agent.Status

	// Modify status
	agent.Status = StatusBusy
	status2 := agent.Status

	// ID should not change
	assert.Equal(t, id1, agent.ID)
	assert.NotEqual(t, status1, status2)
	assert.Equal(t, StatusBusy, status2)
}

// TestMultipleAgentFiltering tests filtering agents by project
func TestMultipleAgentFiltering(t *testing.T) {
	project1 := uuid.New().String()
	project2 := uuid.New().String()

	agents := map[string]*RegisteredAgent{
		"a1": {ID: "a1", ProjectID: project1},
		"a2": {ID: "a2", ProjectID: project1},
		"a3": {ID: "a3", ProjectID: project2},
	}

	filtered := make([]*RegisteredAgent, 0)
	for _, agent := range agents {
		if agent.ProjectID == project1 {
			filtered = append(filtered, agent)
		}
	}

	assert.Len(t, filtered, 2)
	for _, agent := range filtered {
		assert.Equal(t, project1, agent.ProjectID)
	}
}

// ===== EDGE CASES TESTS =====

// TestEmptyAgentName tests agent with empty name
func TestEmptyAgentName(t *testing.T) {
	agent := &RegisteredAgent{
		ID:        uuid.New().String(),
		Name:      "",
		ProjectID: uuid.New().String(),
	}

	assert.Empty(t, agent.Name)
	assert.NotEmpty(t, agent.ID)
}

// TestLongAgentName tests agent with long name
func TestLongAgentName(t *testing.T) {
	longName := string(make([]byte, 1000))
	agent := &RegisteredAgent{
		ID:   uuid.New().String(),
		Name: longName,
	}

	assert.Len(t, agent.Name, 1000)
}

// TestManyCapabilities tests agent with many capabilities
func TestManyCapabilities(t *testing.T) {
	caps := make([]AgentCapability, 100)
	for i := 0; i < 100; i++ {
		caps[i] = AgentCapability{
			Name: "capability-" + uuid.New().String(),
		}
	}

	agent := &RegisteredAgent{
		ID:           uuid.New().String(),
		Capabilities: caps,
	}

	assert.Len(t, agent.Capabilities, 100)
}

// TestTaskWithLargeMetadata tests task with large metadata
func TestTaskWithLargeMetadata(t *testing.T) {
	metadata := make(map[string]interface{})
	for i := 0; i < 100; i++ {
		metadata["key-"+uuid.New().String()] = "value-" + uuid.New().String()
	}

	task := &Task{
		ID:       uuid.New().String(),
		Metadata: metadata,
	}

	assert.Greater(t, len(task.Metadata), 0)
}

// ===== BENCHMARK TESTS =====

// BenchmarkAgentCreation benchmarks agent object creation
func BenchmarkAgentCreation(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = &RegisteredAgent{
			ID:        uuid.New().String(),
			Name:      "agent-" + uuid.New().String(),
			ProjectID: uuid.New().String(),
			Status:    StatusIdle,
		}
	}
}

// BenchmarkTaskCreation benchmarks task object creation
func BenchmarkTaskCreation(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = &Task{
			ID:        uuid.New().String(),
			ProjectID: uuid.New().String(),
			Type:      "test",
			Priority:  TaskPriority(i % 4),
		}
	}
}

// BenchmarkCapabilityMatchingComprehensive benchmarks capability matching comprehensively
func BenchmarkCapabilityMatchingComprehensive(b *testing.B) {
	agent := &RegisteredAgent{
		Capabilities: []AgentCapability{
			{Name: "read"},
			{Name: "write"},
			{Name: "compute"},
			{Name: "delete"},
			{Name: "analyze"},
		},
	}

	requiredCaps := []string{"read", "write", "compute"}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		capMap := make(map[string]bool)
		for _, cap := range agent.Capabilities {
			capMap[cap.Name] = true
		}

		hasAll := true
		for _, required := range requiredCaps {
			if !capMap[required] {
				hasAll = false
				break
			}
		}
		_ = hasAll
	}
}

// BenchmarkConcurrentMapOperations benchmarks concurrent map operations
func BenchmarkConcurrentMapOperations(b *testing.B) {
	agents := make(map[string]*RegisteredAgent)
	var mu sync.RWMutex

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		i := 0
		for pb.Next() {
			if i%2 == 0 {
				agent := &RegisteredAgent{
					ID: uuid.New().String(),
				}
				mu.Lock()
				agents[agent.ID] = agent
				mu.Unlock()
			} else {
				mu.RLock()
				_ = len(agents)
				mu.RUnlock()
			}
			i++
		}
	})
}
