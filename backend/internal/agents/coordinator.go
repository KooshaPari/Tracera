package agents

import (
	"context"
	"fmt"
	"log/slog"
	"sync"
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

const (
	coordinatorBackgroundTasks = 2
	heartbeatCheckInterval     = 30 * time.Second
	taskQueuePollInterval      = 5 * time.Second
)

// AgentStatus represents the status of an agent
type AgentStatus string

const (
	// StatusIdle indicates the agent is idle.
	StatusIdle AgentStatus = "idle"
	// StatusActive indicates the agent is active but not busy.
	StatusActive AgentStatus = "active"
	// StatusBusy indicates the agent is currently executing tasks.
	StatusBusy AgentStatus = "busy"
	// StatusError indicates the agent encountered an error state.
	StatusError AgentStatus = "error"
	// StatusOffline indicates the agent is offline or unreachable.
	StatusOffline AgentStatus = "offline"
)

// AgentCapability represents what an agent can do
type AgentCapability struct {
	Name        string   `json:"name"`
	Version     string   `json:"version"`
	Tags        []string `json:"tags"`
	Description string   `json:"description"`
}

// RegisteredAgent represents an agent registered with the coordinator
type RegisteredAgent struct {
	ID            string                 `json:"id"`
	Name          string                 `json:"name"`
	ProjectID     string                 `json:"project_id"`
	Status        AgentStatus            `json:"status"`
	Capabilities  []AgentCapability      `json:"capabilities"`
	LastHeartbeat time.Time              `json:"last_heartbeat"`
	CurrentTask   *Task                  `json:"current_task,omitempty"`
	Metadata      map[string]interface{} `json:"metadata"`
}

// Coordinator manages agent registration and task distribution
type Coordinator struct {
	db               *gorm.DB
	agents           map[string]*RegisteredAgent
	TaskQueue        *TaskQueue // Exported for handler access
	mu               sync.RWMutex
	heartbeatTimeout time.Duration
	ctx              context.Context
	cancel           context.CancelFunc
	wg               sync.WaitGroup
}

// NewCoordinator creates a new agent coordinator
func NewCoordinator(db *gorm.DB, heartbeatTimeout time.Duration) *Coordinator {
	ctx, cancel := context.WithCancel(context.Background())

	coordinator := &Coordinator{
		db:               db,
		agents:           make(map[string]*RegisteredAgent),
		TaskQueue:        NewTaskQueue(db),
		heartbeatTimeout: heartbeatTimeout,
		ctx:              ctx,
		cancel:           cancel,
	}

	if coordinator.db != nil {
		if err := coordinator.acquireSingletonLock(); err != nil {
			panic(fmt.Errorf("agent coordinator init failed: %w", err))
		}
		if err := coordinator.TaskQueue.LoadTasksFromDB(); err != nil {
			panic(fmt.Errorf("agent task queue init failed: %w", err))
		}
	}

	// Start background tasks
	coordinator.wg.Add(coordinatorBackgroundTasks)
	go coordinator.monitorHeartbeats()
	go coordinator.processTaskQueue()

	return coordinator
}

// RegisterAgent registers a new agent or updates an existing one
func (coordinator *Coordinator) RegisterAgent(agent *RegisteredAgent) error {
	coordinator.mu.Lock()
	defer coordinator.mu.Unlock()

	if agent.ID == "" {
		agent.ID = uuid.New().String()
	}

	agent.LastHeartbeat = time.Now()
	agent.Status = StatusIdle

	// Store in memory
	coordinator.agents[agent.ID] = agent

	// Persist to database when enabled.
	if coordinator.db != nil {
		dbAgent := &models.Agent{
			ID:        agent.ID,
			ProjectID: agent.ProjectID,
			Name:      agent.Name,
			Status:    string(agent.Status),
			Metadata:  nil, // Will be handled by GORM's JSON marshaling
		}

		if err := coordinator.db.Save(dbAgent).Error; err != nil {
			return fmt.Errorf("failed to save agent to database: %w", err)
		}
	}

	slog.Info("Agent registered ( ) - Project", "name", agent.Name, "id", agent.ID, "project", agent.ProjectID)
	return nil
}

// UnregisterAgent removes an agent from the coordinator
func (coordinator *Coordinator) UnregisterAgent(agentID string) error {
	coordinator.mu.Lock()
	defer coordinator.mu.Unlock()

	agent, exists := coordinator.agents[agentID]
	if !exists {
		return fmt.Errorf("agent not found: %s", agentID)
	}

	// Mark as offline in database when enabled.
	if coordinator.db != nil {
		if err := coordinator.db.Model(&models.Agent{}).
			Where("id = ?", agentID).
			Update("status", StatusOffline).
			Error; err != nil {
			return fmt.Errorf("failed to update agent status: %w", err)
		}
	}

	// Return any active tasks to the queue
	if agent.CurrentTask != nil {
		if err := coordinator.TaskQueue.RequeueTask(agent.CurrentTask); err != nil {
			return err
		}
		agent.CurrentTask = nil
	}

	delete(coordinator.agents, agentID)
	slog.Info("Agent unregistered ( )", "name", agent.Name, "id", agentID)
	return nil
}

// Heartbeat updates the agent's last heartbeat time
func (coordinator *Coordinator) Heartbeat(agentID string, status AgentStatus) error {
	coordinator.mu.Lock()
	defer coordinator.mu.Unlock()

	agent, exists := coordinator.agents[agentID]
	if !exists {
		return fmt.Errorf("agent not found: %s", agentID)
	}

	agent.LastHeartbeat = time.Now()
	agent.Status = status

	// Update database when enabled.
	if coordinator.db != nil {
		if err := coordinator.db.Model(&models.Agent{}).Where("id = ?", agentID).Updates(map[string]interface{}{
			"status":     string(status),
			"updated_at": time.Now(),
		}).Error; err != nil {
			return fmt.Errorf("failed to update agent heartbeat: %w", err)
		}
	}

	return nil
}

// GetAgent retrieves agent information
func (c *Coordinator) GetAgent(agentID string) (*RegisteredAgent, error) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	agent, exists := c.agents[agentID]
	if !exists {
		return nil, fmt.Errorf("agent not found: %s", agentID)
	}

	return agent, nil
}

// ListAgents returns all registered agents
func (c *Coordinator) ListAgents(projectID string) []*RegisteredAgent {
	c.mu.RLock()
	defer c.mu.RUnlock()

	var agents []*RegisteredAgent
	for _, agent := range c.agents {
		if projectID == "" || agent.ProjectID == projectID {
			agents = append(agents, agent)
		}
	}

	return agents
}

// AssignTask assigns a task to an available agent
func (coordinator *Coordinator) AssignTask(task *Task) error {
	coordinator.mu.Lock()
	defer coordinator.mu.Unlock()

	// Find an available agent with matching capabilities
	selectedAgent := coordinator.findAgentForTask(task)

	if selectedAgent == nil {
		// No available agent, add to queue
		return coordinator.TaskQueue.EnqueueTask(task)
	}

	return coordinator.assignTaskToAgent(task, selectedAgent)
}

// findAgentForTask finds an available agent with matching capabilities for a task.
// Callers MUST hold the coordinator lock.
func (coordinator *Coordinator) findAgentForTask(task *Task) *RegisteredAgent {
	for _, agent := range coordinator.agents {
		if agent.Status == StatusIdle && agent.ProjectID == task.ProjectID {
			// Check if agent has required capabilities
			if coordinator.hasRequiredCapabilities(agent, task) {
				return agent
			}
		}
	}
	return nil
}

// assignTaskToAgent assigns a task to a specific agent and persists the change.
// Callers MUST hold the coordinator lock.
func (coordinator *Coordinator) assignTaskToAgent(task *Task, agent *RegisteredAgent) error {
	// Assign task to agent
	agent.CurrentTask = task
	agent.Status = StatusBusy
	task.AssignedTo = agent.ID
	task.Status = TaskStatusAssigned
	task.AssignedAt = time.Now()

	if coordinator.TaskQueue != nil && coordinator.db != nil {
		if err := coordinator.TaskQueue.UpdateTaskStatus(task); err != nil {
			return fmt.Errorf("failed to persist assigned task %s: %w", task.ID, err)
		}
	}

	// Update database
	if coordinator.db != nil {
		if err := coordinator.db.Model(&models.Agent{}).
			Where("id = ?", agent.ID).
			Update("status", StatusBusy).
			Error; err != nil {
			return fmt.Errorf("failed to update agent status: %w", err)
		}
	}

	slog.Info("Task assigned to agent", "id", task.ID, "id", agent.ID)
	return nil
}

// CompleteTask marks a task as completed
func (coordinator *Coordinator) CompleteTask(agentID string, taskID string, result *TaskResult) error {
	coordinator.mu.Lock()
	defer coordinator.mu.Unlock()

	agent, exists := coordinator.agents[agentID]
	if !exists {
		return fmt.Errorf("agent not found: %s", agentID)
	}

	if agent.CurrentTask == nil || agent.CurrentTask.ID != taskID {
		return fmt.Errorf("task %s not assigned to agent %s", taskID, agentID)
	}

	// Update task status
	agent.CurrentTask.Status = TaskStatusCompleted
	agent.CurrentTask.CompletedAt = time.Now()
	agent.CurrentTask.Result = result

	// Save task result
	if err := coordinator.TaskQueue.UpdateTaskStatus(agent.CurrentTask); err != nil {
		return fmt.Errorf("failed to update task status: %w", err)
	}

	// Clear agent's current task
	agent.CurrentTask = nil
	agent.Status = StatusIdle

	// Update agent status
	if coordinator.db != nil {
		if err := coordinator.db.Model(&models.Agent{}).
			Where("id = ?", agentID).
			Update("status", StatusIdle).
			Error; err != nil {
			return fmt.Errorf("failed to update agent status: %w", err)
		}
	}

	slog.Info("Task completed by agent", "id", taskID, "id", agentID)
	return nil
}

// FailTask marks a task as failed
func (coordinator *Coordinator) FailTask(agentID string, taskID string, errorMsg string) error {
	coordinator.mu.Lock()
	defer coordinator.mu.Unlock()

	agent, exists := coordinator.agents[agentID]
	if !exists {
		return fmt.Errorf("agent not found: %s", agentID)
	}

	if agent.CurrentTask == nil || agent.CurrentTask.ID != taskID {
		return fmt.Errorf("task %s not assigned to agent %s", taskID, agentID)
	}

	// Update task status
	agent.CurrentTask.Status = TaskStatusFailed
	agent.CurrentTask.CompletedAt = time.Now()
	agent.CurrentTask.ErrorMessage = errorMsg

	// Requeue task if retries are available
	if agent.CurrentTask.RetryCount < agent.CurrentTask.MaxRetries {
		agent.CurrentTask.Status = TaskStatusPending
		agent.CurrentTask.RetryCount++
		if err := coordinator.TaskQueue.RequeueTask(agent.CurrentTask); err != nil {
			return err
		}
		slog.Warn("Task failed, requeued",
			"task_id", taskID,
			"retry", agent.CurrentTask.RetryCount,
			"max_retries", agent.CurrentTask.MaxRetries,
		)
	} else {
		// Save failed task
		if err := coordinator.TaskQueue.UpdateTaskStatus(agent.CurrentTask); err != nil {
			return fmt.Errorf("failed to update task status: %w", err)
		}
		slog.Error("Task failed permanently after retries", "id", taskID, "error", agent.CurrentTask.RetryCount)
	}

	// Clear agent's current task
	agent.CurrentTask = nil
	agent.Status = StatusIdle

	// Update agent status
	if coordinator.db != nil {
		if err := coordinator.db.Model(&models.Agent{}).
			Where("id = ?", agentID).
			Update("status", StatusIdle).
			Error; err != nil {
			return fmt.Errorf("failed to update agent status: %w", err)
		}
	}

	return nil
}

// GetNextTask gets the next available task for an agent
func (coordinator *Coordinator) GetNextTask(agentID string) (*Task, error) {
	coordinator.mu.Lock()
	defer coordinator.mu.Unlock()

	agent, exists := coordinator.agents[agentID]
	if !exists {
		return nil, fmt.Errorf("agent not found: %s", agentID)
	}

	if agent.CurrentTask != nil {
		return agent.CurrentTask, nil
	}

	// Get task from queue
	task := coordinator.TaskQueue.DequeueTask(agent.ProjectID, agent.Capabilities)
	if task == nil {
		return nil, nil // No tasks available
	}

	// Assign task to agent
	agent.CurrentTask = task
	agent.Status = StatusBusy
	task.AssignedTo = agentID
	task.Status = TaskStatusAssigned
	task.AssignedAt = time.Now()

	if coordinator.TaskQueue != nil && coordinator.db != nil {
		if err := coordinator.TaskQueue.UpdateTaskStatus(task); err != nil {
			return nil, fmt.Errorf("failed to persist claimed task %s: %w", task.ID, err)
		}
	}

	// Update database
	if coordinator.db != nil {
		if err := coordinator.db.Model(&models.Agent{}).
			Where("id = ?", agentID).
			Update("status", StatusBusy).
			Error; err != nil {
			return nil, fmt.Errorf("failed to update agent status: %w", err)
		}
	}

	slog.Info("Task assigned to agent", "id", task.ID, "id", agentID)
	return task, nil
}

// hasRequiredCapabilities checks if an agent has the required capabilities for a task
func (c *Coordinator) hasRequiredCapabilities(agent *RegisteredAgent, task *Task) bool {
	if len(task.RequiredCapabilities) == 0 {
		return true // No specific capabilities required
	}

	agentCaps := make(map[string]bool)
	for _, cap := range agent.Capabilities {
		agentCaps[cap.Name] = true
	}

	for _, required := range task.RequiredCapabilities {
		if !agentCaps[required] {
			return false
		}
	}

	return true
}

// monitorHeartbeats monitors agent heartbeats and marks inactive agents as offline
func (coordinator *Coordinator) monitorHeartbeats() {
	defer coordinator.wg.Done()

	ticker := time.NewTicker(heartbeatCheckInterval)
	defer ticker.Stop()

	for {
		select {
		case <-coordinator.ctx.Done():
			return
		case <-ticker.C:
			coordinator.checkHeartbeats()
		}
	}
}

// checkHeartbeats checks for agents that haven't sent heartbeats
func (coordinator *Coordinator) checkHeartbeats() {
	coordinator.mu.Lock()
	defer coordinator.mu.Unlock()

	now := time.Now()
	for agentID, agent := range coordinator.agents {
		coordinator.checkAgentHeartbeat(agentID, agent, now)
	}
}

// checkAgentHeartbeat checks if a single agent has timed out and handles it.
// Callers MUST hold the coordinator lock.
func (coordinator *Coordinator) checkAgentHeartbeat(agentID string, agent *RegisteredAgent, now time.Time) {
	if now.Sub(agent.LastHeartbeat) <= coordinator.heartbeatTimeout {
		return
	}

	slog.Info("Agent ( ) heartbeat timeout, marking as offline", "name", agent.Name, "id", agentID)
	agent.Status = StatusOffline

	// Return task to queue if agent was working on one
	if agent.CurrentTask != nil {
		if err := coordinator.TaskQueue.RequeueTask(agent.CurrentTask); err != nil {
			// We log instead of panic to keep the background worker running
			slog.Error("Failed to requeue task after agent timeout", "error", agent.CurrentTask.ID, "id", agentID, "duration", err)
		}
		agent.CurrentTask = nil
	}

	// Update database
	if coordinator.db != nil {
		err := coordinator.db.Model(&models.Agent{}).
			Where("id = ?", agentID).
			Update("status", StatusOffline).Error
		if err != nil {
			slog.Error("Failed to update agent status in DB after timeout", "error", agentID, "status", err)
		}
	}
}

// processTaskQueue processes the task queue and assigns tasks to available agents
func (coordinator *Coordinator) processTaskQueue() {
	defer coordinator.wg.Done()

	ticker := time.NewTicker(taskQueuePollInterval)
	defer ticker.Stop()

	for {
		select {
		case <-coordinator.ctx.Done():
			return
		case <-ticker.C:
			coordinator.distributeTasks()
		}
	}
}

// distributeTasks distributes tasks from the queue to available agents
func (coordinator *Coordinator) distributeTasks() {
	coordinator.mu.Lock()
	defer coordinator.mu.Unlock()

	// Find idle agents
	for _, agent := range coordinator.agents {
		if agent.Status == StatusIdle && agent.CurrentTask == nil {
			coordinator.tryAssignTaskToAgent(agent)
		}
	}
}

// tryAssignTaskToAgent attempts to find and assign a task to a specific idle agent.
// Callers MUST hold the coordinator lock.
func (coordinator *Coordinator) tryAssignTaskToAgent(agent *RegisteredAgent) {
	// Try to get a task for this agent
	task := coordinator.TaskQueue.DequeueTask(agent.ProjectID, agent.Capabilities)
	if task == nil {
		return
	}

	// Assign task to agent
	agent.CurrentTask = task
	agent.Status = StatusBusy
	task.AssignedTo = agent.ID
	task.Status = TaskStatusAssigned
	task.AssignedAt = time.Now()

	// Update database
	if coordinator.db != nil {
		err := coordinator.db.Model(&models.Agent{}).
			Where("id = ?", agent.ID).
			Update("status", StatusBusy).Error
		if err != nil {
			slog.Error("Failed to update agent status in DB", "error", agent.ID, "status", err)
		}
		if coordinator.TaskQueue != nil {
			if err := coordinator.TaskQueue.UpdateTaskStatus(task); err != nil {
				// We don't panic here to avoid crashing the background worker
				slog.Error("Failed to persist auto-assigned task", "error", task.ID, "error", err)
			}
		}
	}
	slog.Info("Task auto-assigned to agent", "id", task.ID, "id", agent.ID)
}

// Shutdown gracefully shuts down the coordinator
func (c *Coordinator) Shutdown() {
	slog.Info("Shutting down agent coordinator...")
	c.cancel()
	c.wg.Wait()
	if c.db != nil {
		if err := c.releaseSingletonLock(); err != nil {
			slog.Error("Error releasing agent coordinator singleton lock", "error", err)
		}
	}
	slog.Info("Agent coordinator shut down")
}
