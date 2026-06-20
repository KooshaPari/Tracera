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

func TestTaskQueuePop(t *testing.T) {
	pq := make(priorityQueue, 0)
	heap.Init(&pq)

	task1 := &Task{ID: "1", Priority: PriorityNormal, CreatedAt: time.Now()}
	task2 := &Task{ID: "2", Priority: PriorityHigh, CreatedAt: time.Now()}

	heap.Push(&pq, task1)
	heap.Push(&pq, task2)

	popped, ok := heap.Pop(&pq).(*Task)
	require.True(t, ok)
	assert.Equal(t, PriorityHigh, popped.Priority)
	assert.Equal(t, 1, pq.Len())
}

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

	expectedOrder := []TaskPriority{PriorityCritical, PriorityHigh, PriorityNormal, PriorityLow}
	for _, expectedPriority := range expectedOrder {
		task, ok := heap.Pop(&pq).(*Task)
		require.True(t, ok)
		assert.Equal(t, expectedPriority, task.Priority)
	}
}

func TestTaskQueueConcurrentOperations(t *testing.T) {
	pq := make(priorityQueue, 0)
	heap.Init(&pq)
	var mu sync.Mutex

	const numGoroutines = 10
	const tasksPerGoroutine = 10
	var wg sync.WaitGroup

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

	task1, ok := heap.Pop(&pq).(*Task)
	require.True(t, ok)
	task2, ok := heap.Pop(&pq).(*Task)
	require.True(t, ok)
	task3, ok := heap.Pop(&pq).(*Task)
	require.True(t, ok)

	assert.Equal(t, "1", task1.ID)
	assert.Equal(t, "2", task2.ID)
	assert.Equal(t, "3", task3.ID)
}
