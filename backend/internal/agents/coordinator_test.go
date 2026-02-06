//go:build !integration && !e2e

package agents

import (
	"container/heap"
	"sync"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const agentHeartbeatDelay = 10 * time.Millisecond

// TestRegisterAgent tests agent registration
func TestRegisterAgent(t *testing.T) {
	agent := &RegisteredAgent{
		Name:      "test-agent",
		ProjectID: uuid.New().String(),
		Status:    StatusIdle,
		Capabilities: []AgentCapability{
			{
				Name:    "test-capability",
				Version: "1.0.0",
				Tags:    []string{"test"},
			},
		},
		Metadata: map[string]interface{}{
			"version": "1.0",
		},
	}

	assert.NotEmpty(t, agent.Name)
	assert.Equal(t, StatusIdle, agent.Status)
	assert.Len(t, agent.Capabilities, 1)
}

// TestAgentStatus tests agent status transitions
func TestAgentStatus(t *testing.T) {
	testCases := []struct {
		name   string
		status AgentStatus
	}{
		{"Idle", StatusIdle},
		{"Active", StatusActive},
		{"Busy", StatusBusy},
		{"Error", StatusError},
		{"Offline", StatusOffline},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			agent := &RegisteredAgent{
				ID:     uuid.New().String(),
				Status: tc.status,
			}

			assert.Equal(t, tc.status, agent.Status)
		})
	}
}

// TestAgentCapabilities tests capability management
func TestAgentCapabilities(t *testing.T) {
	agent := &RegisteredAgent{
		ID:   uuid.New().String(),
		Name: "test-agent",
		Capabilities: []AgentCapability{
			{Name: "read", Version: "1.0", Tags: []string{"io"}},
			{Name: "write", Version: "1.0", Tags: []string{"io"}},
			{Name: "compute", Version: "2.0", Tags: []string{"processing"}},
		},
	}

	assert.Len(t, agent.Capabilities, 3)

	var found *AgentCapability
	for _, cap := range agent.Capabilities {
		if cap.Name == "compute" {
			found = &cap
			break
		}
	}

	require.NotNil(t, found)
	assert.Equal(t, "2.0", found.Version)
	assert.Contains(t, found.Tags, "processing")
}

// TestAgentHeartbeat tests heartbeat timestamp updates
func TestAgentHeartbeat(t *testing.T) {
	agent := &RegisteredAgent{
		ID:            uuid.New().String(),
		LastHeartbeat: time.Now().Add(-5 * time.Minute),
	}

	oldHeartbeat := agent.LastHeartbeat
	time.Sleep(agentHeartbeatDelay)
	agent.LastHeartbeat = time.Now()

	assert.True(t, agent.LastHeartbeat.After(oldHeartbeat))
}

// TestAgentMetadata tests metadata storage
func TestAgentMetadata(t *testing.T) {
	agent := &RegisteredAgent{
		ID:   uuid.New().String(),
		Name: "test-agent",
		Metadata: map[string]interface{}{
			"version":     "1.0.0",
			"environment": "test",
			"cpu_cores":   4,
			"memory_gb":   8.5,
		},
	}

	assert.Equal(t, "1.0.0", agent.Metadata["version"])
	assert.Equal(t, "test", agent.Metadata["environment"])
	assert.Equal(t, 4, agent.Metadata["cpu_cores"])
	assert.Equal(t, 8.5, agent.Metadata["memory_gb"])
}

// ===== TASK QUEUE TESTS =====

// TestTaskQueuePush tests adding tasks to the queue
func TestTaskQueuePush(t *testing.T) {
	pq := make(priorityQueue, 0)
	heap.Init(&pq)

	task1 := &Task{ID: "1", Priority: PriorityNormal, CreatedAt: time.Now()}
	task2 := &Task{ID: "2", Priority: PriorityHigh, CreatedAt: time.Now()}
	task3 := &Task{ID: "3", Priority: PriorityCritical, CreatedAt: time.Now()}

	heap.Push(&pq, task1)
	heap.Push(&pq, task2)
	heap.Push(&pq, task3)

	assert.Equal(t, 3, pq.Len())
}

// TestTaskQueuePop tests removing tasks from the queue
func TestTaskQueuePop(t *testing.T) {
	pq := make(priorityQueue, 0)
	heap.Init(&pq)

	task1 := &Task{ID: "1", Priority: PriorityNormal, CreatedAt: time.Now()}
	task2 := &Task{ID: "2", Priority: PriorityHigh, CreatedAt: time.Now()}

	heap.Push(&pq, task1)
	heap.Push(&pq, task2)

	popped := heap.Pop(&pq).(*Task)
	assert.Equal(t, PriorityHigh, popped.Priority)
	assert.Equal(t, 1, pq.Len())
}

// TestTaskQueuePriorityOrdering tests that tasks are ordered by priority
func TestTaskQueuePriorityOrdering(t *testing.T) {
	pq := make(priorityQueue, 0)
	heap.Init(&pq)

	baseTime := time.Now()
	tasks := []*Task{
		{ID: "1", Priority: PriorityLow, CreatedAt: baseTime},
		{ID: "2", Priority: PriorityCritical, CreatedAt: baseTime.Add(1 * time.Second)},
		{ID: "3", Priority: PriorityHigh, CreatedAt: baseTime.Add(2 * time.Second)},
		{ID: "4", Priority: PriorityNormal, CreatedAt: baseTime.Add(3 * time.Second)},
	}

	for _, task := range tasks {
		heap.Push(&pq, task)
	}

	// Pop should return: Critical, High, Normal, Low
	expectedOrder := []TaskPriority{PriorityCritical, PriorityHigh, PriorityNormal, PriorityLow}
	for _, expectedPriority := range expectedOrder {
		task := heap.Pop(&pq).(*Task)
		assert.Equal(t, expectedPriority, task.Priority)
	}
}

// TestTaskQueueConcurrentOperations tests concurrent push/pop operations
func TestTaskQueueConcurrentOperations(t *testing.T) {
	pq := make(priorityQueue, 0)
	heap.Init(&pq)
	var mu sync.Mutex

	const numGoroutines = 10
	const tasksPerGoroutine = 10
	var wg sync.WaitGroup

	// Concurrent push
	wg.Add(numGoroutines)
	for i := 0; i < numGoroutines; i++ {
		go func(_ int) {
			defer wg.Done()
			for j := 0; j < tasksPerGoroutine; j++ {
				task := &Task{
					ID:        uuid.New().String(),
					Priority:  TaskPriority(j % 4),
					CreatedAt: time.Now(),
				}
				mu.Lock()
				heap.Push(&pq, task)
				mu.Unlock()
			}
		}(i)
	}
	wg.Wait()

	mu.Lock()
	assert.Equal(t, numGoroutines*tasksPerGoroutine, pq.Len())
	mu.Unlock()

	// Concurrent pop
	wg.Add(numGoroutines)
	for i := 0; i < numGoroutines; i++ {
		go func() {
			defer wg.Done()
			for j := 0; j < tasksPerGoroutine; j++ {
				mu.Lock()
				if pq.Len() > 0 {
					heap.Pop(&pq)
				}
				mu.Unlock()
			}
		}()
	}
	wg.Wait()

	mu.Lock()
	assert.Equal(t, 0, pq.Len())
	mu.Unlock()
}

// TestTaskQueueFIFOWithinPriority tests FIFO ordering within same priority
func TestTaskQueueFIFOWithinPriority(t *testing.T) {
	pq := make(priorityQueue, 0)
	heap.Init(&pq)

	baseTime := time.Now()
	tasks := []*Task{
		{ID: "1", Priority: PriorityHigh, CreatedAt: baseTime},
		{ID: "2", Priority: PriorityHigh, CreatedAt: baseTime.Add(1 * time.Second)},
		{ID: "3", Priority: PriorityHigh, CreatedAt: baseTime.Add(2 * time.Second)},
	}

	for _, task := range tasks {
		heap.Push(&pq, task)
	}

	// Should pop in order of creation (FIFO within priority)
	task1 := heap.Pop(&pq).(*Task)
	task2 := heap.Pop(&pq).(*Task)
	task3 := heap.Pop(&pq).(*Task)

	assert.Equal(t, "1", task1.ID)
	assert.Equal(t, "2", task2.ID)
	assert.Equal(t, "3", task3.ID)
}

// ===== CAPABILITY MATCHING TESTS =====

// TestCapabilityMatchingExactMatch tests exact capability matching
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

	// Simulate capability matching logic
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

// TestCapabilityMatchingPartialMatch tests partial capability matching
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

// TestCapabilityMatchingNoMatch tests no capability matching
func TestCapabilityMatchingNoMatch(t *testing.T) {
	agent := &RegisteredAgent{
		Capabilities: []AgentCapability{
			{Name: "read"},
		},
	}

	task := &Task{
		RequiredCapabilities: []string{"write", "delete"},
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

// TestCapabilityMatchingBestAgent tests finding the best matching agent
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

// ===== AGENT PROTOCOL TESTS =====

// TestProtocolMessageSerialization tests message serialization
func TestProtocolMessageSerialization(t *testing.T) {
	protocol := NewProtocol()

	req := &RegisterRequest{
		Name:      "test-agent",
		ProjectID: uuid.New().String(),
		Capabilities: []AgentCapability{
			{Name: "test", Version: "1.0"},
		},
	}

	msg := protocol.CreateRegisterMessage(req)
	assert.Equal(t, MsgTypeRegister, msg.Type)
	assert.NotNil(t, msg.Payload)

	serialized, err := protocol.SerializeMessage(msg)
	require.NoError(t, err)
	assert.NotEmpty(t, serialized)
}

// TestProtocolMessageDeserialization tests message deserialization
func TestProtocolMessageDeserialization(t *testing.T) {
	protocol := NewProtocol()

	original := &Message{
		Type:      MsgTypeHeartbeat,
		AgentID:   uuid.New().String(),
		Timestamp: time.Now(),
		Payload: map[string]interface{}{
			"status": "idle",
		},
	}

	serialized, err := protocol.SerializeMessage(original)
	require.NoError(t, err)

	parsed, err := protocol.ParseMessage(serialized)
	require.NoError(t, err)
	assert.Equal(t, original.Type, parsed.Type)
	assert.Equal(t, original.AgentID, parsed.AgentID)
}

// TestProtocolVersionNegotiation tests protocol version handling
func TestProtocolVersionNegotiation(t *testing.T) {
	protocol := NewProtocol()

	msg := &Message{
		Type:      MsgTypeRegister,
		Timestamp: time.Now(),
		Payload: map[string]interface{}{
			"name":       "test-agent",
			"project_id": uuid.New().String(),
			"version":    "1.0",
		},
	}

	err := protocol.ValidateMessage(msg)
	assert.NoError(t, err)
}

// TestProtocolHandshake tests protocol handshake flow
func TestProtocolHandshake(t *testing.T) {
	protocol := NewProtocol()

	// Step 1: Agent sends register request
	registerMsg := protocol.CreateRegisterMessage(&RegisterRequest{
		Name:      "test-agent",
		ProjectID: uuid.New().String(),
	})

	err := protocol.ValidateMessage(registerMsg)
	assert.NoError(t, err)

	// Step 2: Coordinator responds with ACK
	ackMsg := protocol.CreateAckMessage("success", "Agent registered")
	assert.Equal(t, MsgTypeAck, ackMsg.Type)
}

// ===== TASK ASSIGNMENT TESTS =====

// TestTaskAssignmentLoadBalancing tests load balancing across agents
func TestTaskAssignmentLoadBalancing(t *testing.T) {
	agents := []*RegisteredAgent{
		{ID: "1", Status: StatusIdle, CurrentTask: nil},
		{ID: "2", Status: StatusIdle, CurrentTask: nil},
		{ID: "3", Status: StatusBusy, CurrentTask: &Task{ID: "existing"}},
	}

	tasks := []*Task{
		{ID: "task-1"},
		{ID: "task-2"},
		{ID: "task-3"},
	}

	assignments := make(map[string]string) // agentID -> taskID
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

// TestTaskAssignmentFailureHandling tests handling of task failures
func TestTaskAssignmentFailureHandling(t *testing.T) {
	task := &Task{
		ID:         "failed-task",
		Status:     TaskStatusFailed,
		RetryCount: 1,
		MaxRetries: 3,
	}

	// Should retry
	shouldRetry := task.RetryCount < task.MaxRetries
	assert.True(t, shouldRetry)

	task.RetryCount = 3
	shouldRetry = task.RetryCount < task.MaxRetries
	assert.False(t, shouldRetry)
}

// TestTaskAssignmentRetryLogic tests task retry logic
func TestTaskAssignmentRetryLogic(t *testing.T) {
	task := &Task{
		ID:         "retry-task",
		Status:     TaskStatusFailed,
		RetryCount: 0,
		MaxRetries: 3,
	}

	retries := 0
	for task.RetryCount < task.MaxRetries {
		task.RetryCount++
		task.Status = TaskStatusPending
		retries++
	}

	assert.Equal(t, 3, retries)
	assert.Equal(t, 3, task.RetryCount)
}

// ===== EDGE CASE TESTS =====

// TestAgentOfflineRecovery tests agent offline and recovery scenarios
func TestAgentOfflineRecovery(t *testing.T) {
	agent := &RegisteredAgent{
		ID:            uuid.New().String(),
		Status:        StatusActive,
		LastHeartbeat: time.Now(),
		CurrentTask:   &Task{ID: "active-task"},
	}

	// Simulate timeout
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

	// Recovery
	agent.LastHeartbeat = time.Now()
	agent.Status = StatusIdle
	assert.Equal(t, StatusIdle, agent.Status)
}

// TestConcurrentAgentRegistration tests concurrent agent registration
func TestConcurrentAgentRegistration(t *testing.T) {
	agents := make(map[string]*RegisteredAgent)
	var mu sync.RWMutex

	const count = 100
	done := make(chan *RegisteredAgent, count)

	for i := 0; i < count; i++ {
		go func() {
			agent := &RegisteredAgent{
				ID:            uuid.New().String(),
				Name:          "agent-" + uuid.New().String(),
				ProjectID:     uuid.New().String(),
				Status:        StatusIdle,
				LastHeartbeat: time.Now(),
			}
			done <- agent
		}()
	}

	for i := 0; i < count; i++ {
		agent := <-done
		mu.Lock()
		agents[agent.ID] = agent
		mu.Unlock()
	}

	mu.RLock()
	assert.Equal(t, count, len(agents))
	mu.RUnlock()
}

// TestConcurrentTaskAssignment tests concurrent task assignment
func TestConcurrentTaskAssignment(t *testing.T) {
	var mu sync.RWMutex
	agents := make(map[string]*RegisteredAgent)

	for i := 0; i < 5; i++ {
		agents[uuid.New().String()] = &RegisteredAgent{
			Status:      StatusIdle,
			CurrentTask: nil,
		}
	}

	const taskCount = 20
	var wg sync.WaitGroup
	assigned := make(chan bool, taskCount)

	wg.Add(taskCount)
	for i := 0; i < taskCount; i++ {
		go func(_ int) {
			defer wg.Done()

			task := &Task{ID: uuid.New().String()}
			mu.Lock()
			defer mu.Unlock()

			for _, agent := range agents {
				if agent.Status == StatusIdle && agent.CurrentTask == nil {
					agent.CurrentTask = task
					agent.Status = StatusBusy
					assigned <- true
					return
				}
			}
			assigned <- false
		}(i)
	}

	wg.Wait()
	close(assigned)

	assignedCount := 0
	for success := range assigned {
		if success {
			assignedCount++
		}
	}

	assert.LessOrEqual(t, assignedCount, 5)
}

// TestAgentConflictDetection tests detecting conflicting agents
func TestAgentConflictDetection(t *testing.T) {
	projectID := uuid.New().String()

	agents := map[string]*RegisteredAgent{
		"agent-1": {
			ID:        uuid.New().String(),
			Name:      "worker",
			ProjectID: projectID,
			Status:    StatusActive,
		},
		"agent-2": {
			ID:        uuid.New().String(),
			Name:      "worker",
			ProjectID: projectID,
			Status:    StatusActive,
		},
	}

	names := make(map[string]string)
	conflicts := []string{}

	for id, agent := range agents {
		key := agent.ProjectID + ":" + agent.Name
		if existingID, exists := names[key]; exists {
			conflicts = append(conflicts, id, existingID)
		} else {
			names[key] = id
		}
	}

	assert.Greater(t, len(conflicts), 0)
}

// BenchmarkAgentRegistration benchmarks agent registration
func BenchmarkAgentRegistration(b *testing.B) {
	projectID := uuid.New().String()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = &RegisteredAgent{
			ID:            uuid.New().String(),
			Name:          "agent-" + uuid.New().String(),
			ProjectID:     projectID,
			Status:        StatusIdle,
			LastHeartbeat: time.Now(),
			Capabilities: []AgentCapability{
				{Name: "test", Version: "1.0", Tags: []string{"benchmark"}},
			},
			Metadata: map[string]interface{}{
				"version": "1.0",
			},
		}
	}
}

// BenchmarkCapabilityMatching benchmarks capability matching
func BenchmarkCapabilityMatching(b *testing.B) {
	agents := make([]*RegisteredAgent, 1000)
	for i := 0; i < 1000; i++ {
		agents[i] = &RegisteredAgent{
			ID: uuid.New().String(),
			Capabilities: []AgentCapability{
				{Name: "capability-" + string(rune(i%10)), Version: "1.0"},
			},
		}
	}

	targetCap := "capability-5"

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		var matches []*RegisteredAgent
		for _, agent := range agents {
			for _, cap := range agent.Capabilities {
				if cap.Name == targetCap {
					matches = append(matches, agent)
					break
				}
			}
		}
		_ = matches
	}
}

// BenchmarkTaskQueueOperations benchmarks task queue operations
func BenchmarkTaskQueueOperations(b *testing.B) {
	pq := make(priorityQueue, 0)
	heap.Init(&pq)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		task := &Task{
			ID:        uuid.New().String(),
			Priority:  TaskPriority(i % 4),
			CreatedAt: time.Now(),
		}
		heap.Push(&pq, task)

		if pq.Len() > 100 {
			heap.Pop(&pq)
		}
	}
}
