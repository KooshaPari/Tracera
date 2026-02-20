package agents

import (
	"container/heap"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// TaskStatus represents the status of a task
type TaskStatus string

const (
	// TaskStatusPending indicates the task is queued.
	TaskStatusPending TaskStatus = "pending"
	// TaskStatusAssigned indicates the task is assigned to an agent.
	TaskStatusAssigned TaskStatus = "assigned"
	// TaskStatusRunning indicates the task is in progress.
	TaskStatusRunning TaskStatus = "running"
	// TaskStatusCompleted indicates the task completed successfully.
	TaskStatusCompleted TaskStatus = "completed"
	// TaskStatusFailed indicates the task execution failed.
	TaskStatusFailed TaskStatus = "failed"
	// TaskStatusCanceled indicates the task was canceled.
	TaskStatusCanceled TaskStatus = "canceled"
)

// TaskPriority represents the priority of a task
type TaskPriority int

const (
	// PriorityLow is the lowest task priority.
	PriorityLow TaskPriority = 0
	// PriorityNormal is the default task priority.
	PriorityNormal TaskPriority = 1
	// PriorityHigh indicates a high-priority task.
	PriorityHigh TaskPriority = 2
	// PriorityCritical indicates a critical-priority task.
	PriorityCritical TaskPriority = 3
)

// Task represents a task to be executed by an agent
type Task struct {
	ID                   string                 `json:"id"`
	ProjectID            string                 `json:"project_id"`
	Type                 string                 `json:"type"` // e.g., "analyze", "generate", "validate"
	Priority             TaskPriority           `json:"priority"`
	Status               TaskStatus             `json:"status"`
	RequiredCapabilities []string               `json:"required_capabilities,omitempty"`
	Parameters           map[string]interface{} `json:"parameters"`
	Result               *TaskResult            `json:"result,omitempty"`
	AssignedTo           string                 `json:"assigned_to,omitempty"`
	CreatedAt            time.Time              `json:"created_at"`
	AssignedAt           time.Time              `json:"assigned_at,omitempty"`
	CompletedAt          time.Time              `json:"completed_at,omitempty"`
	Timeout              time.Duration          `json:"timeout"` // Task timeout
	RetryCount           int                    `json:"retry_count"`
	MaxRetries           int                    `json:"max_retries"`
	ErrorMessage         string                 `json:"error_message,omitempty"`
	Tags                 []string               `json:"tags,omitempty"`
	Metadata             map[string]interface{} `json:"metadata,omitempty"`
}

// TaskResult represents the result of a completed task
type TaskResult struct {
	Success  bool                   `json:"success"`
	Data     map[string]interface{} `json:"data,omitempty"`
	Message  string                 `json:"message,omitempty"`
	Duration time.Duration          `json:"duration"` // Task execution time
}

// TaskQueue manages a priority queue of tasks
type TaskQueue struct {
	db          *gorm.DB
	queue       *priorityQueue
	mu          sync.RWMutex
	taskIndex   map[string]*Task // For quick task lookup
	queuedTasks map[string]bool  // Track queued tasks
}

// priorityQueue implements heap.Interface for Task
type priorityQueue []*Task

func (pq priorityQueue) Len() int { return len(pq) }

func (pq priorityQueue) Less(leftIndex, rightIndex int) bool {
	// Higher priority tasks come first
	if pq[leftIndex].Priority != pq[rightIndex].Priority {
		return pq[leftIndex].Priority > pq[rightIndex].Priority
	}
	// If same priority, older tasks come first (FIFO)
	return pq[leftIndex].CreatedAt.Before(pq[rightIndex].CreatedAt)
}

func (pq priorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *priorityQueue) Push(x interface{}) {
	task, ok := x.(*Task)
	if !ok {
		return
	}
	*pq = append(*pq, task)
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	task := old[n-1]
	old[n-1] = nil // avoid memory leak
	*pq = old[0 : n-1]
	return task
}

// NewTaskQueue creates a new task queue
func NewTaskQueue(db *gorm.DB) *TaskQueue {
	pq := make(priorityQueue, 0)
	heap.Init(&pq)

	return &TaskQueue{
		db:          db,
		queue:       &pq,
		taskIndex:   make(map[string]*Task),
		queuedTasks: make(map[string]bool),
	}
}

// EnqueueTask adds a task to the queue
func (tq *TaskQueue) EnqueueTask(task *Task) error {
	tq.mu.Lock()
	defer tq.mu.Unlock()

	if task.ID == "" {
		task.ID = uuid.New().String()
	}

	task.Status = TaskStatusPending
	task.CreatedAt = time.Now()

	// Add to priority queue
	heap.Push(tq.queue, task)
	tq.taskIndex[task.ID] = task
	tq.queuedTasks[task.ID] = true

	// Persist to database
	if err := tq.saveTask(task); err != nil {
		return fmt.Errorf("failed to save task to database: %w", err)
	}

	return nil
}

// DequeueTask removes and returns the highest priority task from the queue
func (tq *TaskQueue) DequeueTask(projectID string, capabilities []AgentCapability) *Task {
	tq.mu.Lock()
	defer tq.mu.Unlock()

	if tq.queue.Len() == 0 {
		return nil
	}

	// Build capability map
	capMap := make(map[string]bool)
	for _, cap := range capabilities {
		capMap[cap.Name] = true
	}

	// Find first task that matches criteria
	for index := 0; index < tq.queue.Len(); index++ {
		task := (*tq.queue)[index]

		if tq.taskMatches(task, projectID, capMap) {
			// Remove task from queue
			heap.Remove(tq.queue, index)
			delete(tq.queuedTasks, task.ID)
			return task
		}
	}

	return nil
}

func (tq *TaskQueue) taskMatches(task *Task, projectID string, agentCaps map[string]bool) bool {
	// Check project match
	if task.ProjectID != projectID {
		return false
	}

	// Check capabilities
	for _, required := range task.RequiredCapabilities {
		if !agentCaps[required] {
			return false
		}
	}

	return true
}

// RequeueTask puts a task back in the queue (used for retries)
func (tq *TaskQueue) RequeueTask(task *Task) error {
	tq.mu.Lock()
	defer tq.mu.Unlock()

	if tq.queuedTasks[task.ID] {
		return nil // Already in queue
	}

	task.Status = TaskStatusPending
	task.AssignedTo = ""
	task.AssignedAt = time.Time{}

	heap.Push(tq.queue, task)
	tq.queuedTasks[task.ID] = true

	// Update in database. If the agent task queue is enabled, persistence is required.
	if err := tq.saveTask(task); err != nil {
		return fmt.Errorf("failed to persist requeued task %s: %w", task.ID, err)
	}

	return nil
}

// GetTask retrieves a task by ID
func (tq *TaskQueue) GetTask(taskID string) (*Task, error) {
	tq.mu.RLock()
	defer tq.mu.RUnlock()

	task, exists := tq.taskIndex[taskID]
	if !exists {
		return nil, fmt.Errorf("task not found: %s", taskID)
	}

	return task, nil
}

// UpdateTaskStatus updates the status of a task
func (tq *TaskQueue) UpdateTaskStatus(task *Task) error {
	tq.mu.Lock()
	defer tq.mu.Unlock()

	// Update in index
	tq.taskIndex[task.ID] = task

	// Remove from queued tasks if status is not pending
	if task.Status != TaskStatusPending {
		if tq.queuedTasks[task.ID] {
			// Remove from priority queue heap
			for i := 0; i < tq.queue.Len(); i++ {
				if (*tq.queue)[i].ID == task.ID {
					heap.Remove(tq.queue, i)
					break
				}
			}
			delete(tq.queuedTasks, task.ID)
		}
	}

	// Persist to database
	return tq.saveTask(task)
}

// CancelTask cancels a task
func (tq *TaskQueue) CancelTask(taskID string) error {
	tq.mu.Lock()
	defer tq.mu.Unlock()

	task, exists := tq.taskIndex[taskID]
	if !exists {
		return fmt.Errorf("task not found: %s", taskID)
	}

	// Remove from queue if it's there
	if tq.queuedTasks[taskID] {
		for i := 0; i < tq.queue.Len(); i++ {
			if (*tq.queue)[i].ID == taskID {
				heap.Remove(tq.queue, i)
				break
			}
		}
		delete(tq.queuedTasks, taskID)
	}

	task.Status = TaskStatusCanceled
	task.CompletedAt = time.Now()

	return tq.saveTask(task)
}

// ListTasks returns all tasks with optional filtering
func (tq *TaskQueue) ListTasks(projectID string, status TaskStatus) []*Task {
	tq.mu.RLock()
	defer tq.mu.RUnlock()

	var tasks []*Task
	for _, task := range tq.taskIndex {
		if projectID != "" && task.ProjectID != projectID {
			continue
		}
		if status != "" && task.Status != status {
			continue
		}
		tasks = append(tasks, task)
	}

	return tasks
}

// QueueLength returns the number of tasks in the queue
func (tq *TaskQueue) QueueLength() int {
	tq.mu.RLock()
	defer tq.mu.RUnlock()
	return tq.queue.Len()
}

// QueueStats returns statistics about the queue
func (tq *TaskQueue) QueueStats() map[string]interface{} {
	tq.mu.RLock()
	defer tq.mu.RUnlock()

	stats := map[string]interface{}{
		"total_tasks": len(tq.taskIndex),
		"queued":      tq.queue.Len(),
		"by_status":   make(map[string]int),
		"by_priority": make(map[string]int),
	}

	statusCounts := make(map[TaskStatus]int)
	priorityCounts := make(map[TaskPriority]int)

	for _, task := range tq.taskIndex {
		statusCounts[task.Status]++
		priorityCounts[task.Priority]++
	}

	byStatus, ok := stats["by_status"].(map[string]int)
	if !ok {
		return stats
	}

	byPriority, ok := stats["by_priority"].(map[string]int)
	if !ok {
		return stats
	}

	for status, count := range statusCounts {
		byStatus[string(status)] = count
	}

	for priority, count := range priorityCounts {
		priorityName := "unknown"
		switch priority {
		case PriorityLow:
			priorityName = "low"
		case PriorityNormal:
			priorityName = "normal"
		case PriorityHigh:
			priorityName = "high"
		case PriorityCritical:
			priorityName = "critical"
		}
		byPriority[priorityName] = count
	}

	return stats
}

// ListPendingTasks returns all pending tasks for a project
func (tq *TaskQueue) ListPendingTasks(projectID string) []*Task {
	tq.mu.RLock()
	defer tq.mu.RUnlock()

	var tasks []*Task
	for _, task := range tq.taskIndex {
		if task.Status == TaskStatusPending && task.ProjectID == projectID {
			tasks = append(tasks, task)
		}
	}

	return tasks
}

// CleanupOldTasks removes completed/failed tasks older than the specified duration
func (tq *TaskQueue) CleanupOldTasks(olderThan time.Duration) int {
	tq.mu.Lock()
	defer tq.mu.Unlock()

	cutoff := time.Now().Add(-olderThan)
	cleaned := 0

	for taskID, task := range tq.taskIndex {
		isTerminal := task.Status == TaskStatusCompleted ||
			task.Status == TaskStatusFailed ||
			task.Status == TaskStatusCanceled
		if isTerminal && task.CompletedAt.Before(cutoff) {
			delete(tq.taskIndex, taskID)
			cleaned++
		}
	}

	return cleaned
}

// saveTask persists a task to the database
func (tq *TaskQueue) saveTask(task *Task) error {
	if tq.db == nil {
		// Test-only / in-memory mode. Production modes must provide a DB.
		return nil
	}

	// Convert task to JSON for storage
	taskData, err := json.Marshal(task)
	if err != nil {
		return fmt.Errorf("failed to marshal task: %w", err)
	}

	// For now, we'll store tasks as metadata in a simple key-value table
	// In a production system, you'd want a proper tasks table
	type TaskStore struct {
		ID        string `gorm:"primaryKey"`
		ProjectID string `gorm:"index"`
		Status    string `gorm:"index"`
		Priority  int    `gorm:"index"`
		Data      []byte `gorm:"type:jsonb"`
		CreatedAt time.Time
		UpdatedAt time.Time
	}

	taskStore := TaskStore{
		ID:        task.ID,
		ProjectID: task.ProjectID,
		Status:    string(task.Status),
		Priority:  int(task.Priority),
		Data:      taskData,
		CreatedAt: task.CreatedAt,
		UpdatedAt: time.Now(),
	}

	// Use GORM to save or update
	result := tq.db.Table("agent_tasks").Save(&taskStore)
	if result.Error != nil {
		return fmt.Errorf("failed to save task to database: %w", result.Error)
	}

	return nil
}

// LoadTasksFromDB loads pending and assigned tasks from the database
func (tq *TaskQueue) LoadTasksFromDB() error {
	tq.mu.Lock()
	defer tq.mu.Unlock()

	if tq.db == nil {
		return nil
	}

	taskStores, err := tq.getNonTerminalTasksFromDB()
	if err != nil {
		return err
	}

	for _, ts := range taskStores {
		task, err := tq.loadAndNormalizeTask(ts)
		if err != nil {
			return err
		}

		tq.taskIndex[task.ID] = task

		if task.Status == TaskStatusPending {
			heap.Push(tq.queue, task)
			tq.queuedTasks[task.ID] = true
		}
	}

	return nil
}

type taskStore struct {
	ID        string
	ProjectID string
	Status    string
	Priority  int
	Data      []byte
	CreatedAt time.Time
	UpdatedAt time.Time
}

func (tq *TaskQueue) getNonTerminalTasksFromDB() ([]taskStore, error) {
	var taskStores []taskStore
	nonTerminalStatuses := []string{string(TaskStatusPending), string(TaskStatusAssigned), string(TaskStatusRunning)}
	if err := tq.db.Table("agent_tasks").
		Where("status IN ?", nonTerminalStatuses).
		Find(&taskStores).Error; err != nil {
		return nil, fmt.Errorf("failed to load tasks from database: %w", err)
	}
	return taskStores, nil
}

func (tq *TaskQueue) loadAndNormalizeTask(ts taskStore) (*Task, error) {
	var task Task
	if err := json.Unmarshal(ts.Data, &task); err != nil {
		return nil, fmt.Errorf("failed to unmarshal agent task %s from database: %w", ts.ID, err)
	}

	// After a process restart, we do not assume an in-memory agent still holds a claim.
	// Converge all non-terminal tasks to pending so they are claimable again.
	if task.Status != TaskStatusPending {
		task.Status = TaskStatusPending
		task.AssignedTo = ""
		task.AssignedAt = time.Time{}

		if err := tq.saveTask(&task); err != nil {
			return nil, fmt.Errorf("failed to normalize agent task %s to pending: %w", task.ID, err)
		}
	}
	return &task, nil
}
