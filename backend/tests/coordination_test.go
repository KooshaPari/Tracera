package tests

import (
	"context"
	"fmt"
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/agents"
)

// TestLockManagerOptimisticLocking tests optimistic locking with version control
func TestLockManagerOptimisticLocking(t *testing.T) {
	db := setupTestDB(t)
	defer db.Migrator().DropTable(&agents.AgentLock{}, &agents.ItemVersion{})

	db.AutoMigrate(&agents.AgentLock{}, &agents.ItemVersion{})

	lm := agents.NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()

	ctx := context.Background()
	itemID := "item-123"
	agent1ID := "agent-1"
	agent2ID := "agent-2"

	// Agent 1 acquires optimistic lock
	lock1, err := lm.AcquireLock(ctx, itemID, "item", agent1ID, agents.LockTypeOptimistic)
	require.NoError(t, err)
	assert.NotNil(t, lock1)
	assert.Equal(t, int64(1), lock1.Version)

	// Agent 2 can also acquire an optimistic lock (version-based, non-blocking)
	lock2, err := lm.AcquireLock(ctx, itemID, "item", agent2ID, agents.LockTypeOptimistic)
	require.NoError(t, err)
	assert.NotNil(t, lock2)

	// Validate version for agent 1 (should succeed)
	err = lm.ValidateVersion(ctx, itemID, 1)
	assert.NoError(t, err)

	// Record version after agent 1's update
	err = lm.RecordVersion(ctx, itemID, agent1ID, 1, map[string]interface{}{"field": "value1"}, "", "hash1")
	require.NoError(t, err)

	// Now validate version for agent 2 (should fail due to version mismatch)
	err = lm.ValidateVersion(ctx, itemID, 1)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "version mismatch")

	// Release locks
	err = lm.ReleaseLock(ctx, lock1.ID, agent1ID)
	assert.NoError(t, err)

	err = lm.ReleaseLock(ctx, lock2.ID, agent2ID)
	assert.NoError(t, err)
}

// TestLockManagerPessimisticLocking tests pessimistic (exclusive) locking
func TestLockManagerPessimisticLocking(t *testing.T) {
	db := setupTestDB(t)
	defer db.Migrator().DropTable(&agents.AgentLock{})

	db.AutoMigrate(&agents.AgentLock{})

	lm := agents.NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()

	ctx := context.Background()
	itemID := "item-456"
	agent1ID := "agent-1"
	agent2ID := "agent-2"

	// Agent 1 acquires pessimistic lock
	lock1, err := lm.AcquireLock(ctx, itemID, "item", agent1ID, agents.LockTypePessimistic)
	require.NoError(t, err)
	assert.NotNil(t, lock1)

	// Agent 2 tries to acquire lock on same item (should fail)
	lock2, err := lm.AcquireLock(ctx, itemID, "item", agent2ID, agents.LockTypePessimistic)
	assert.Error(t, err)
	assert.Nil(t, lock2)
	assert.Contains(t, err.Error(), "is locked by")

	// Agent 1 releases lock
	err = lm.ReleaseLock(ctx, lock1.ID, agent1ID)
	require.NoError(t, err)

	// Now agent 2 can acquire the lock
	lock2, err = lm.AcquireLock(ctx, itemID, "item", agent2ID, agents.LockTypePessimistic)
	assert.NoError(t, err)
	assert.NotNil(t, lock2)

	err = lm.ReleaseLock(ctx, lock2.ID, agent2ID)
	assert.NoError(t, err)
}

// TestLockExpiration tests automatic lock expiration
func TestLockExpiration(t *testing.T) {
	db := setupTestDB(t)
	defer db.Migrator().DropTable(&agents.AgentLock{})

	db.AutoMigrate(&agents.AgentLock{})

	// Use very short timeout for testing
	lm := agents.NewLockManager(db, 1*time.Second)
	defer lm.Shutdown()

	ctx := context.Background()
	itemID := "item-789"
	agent1ID := "agent-1"
	agent2ID := "agent-2"

	// Agent 1 acquires lock with 1 second timeout
	lock1, err := lm.AcquireLock(ctx, itemID, "item", agent1ID, agents.LockTypePessimistic)
	require.NoError(t, err)
	assert.NotNil(t, lock1)

	// Agent 2 cannot acquire immediately
	_, err = lm.AcquireLock(ctx, itemID, "item", agent2ID, agents.LockTypePessimistic)
	assert.Error(t, err)

	// Wait for lock to expire
	time.Sleep(2 * time.Second)

	// Now agent 2 can acquire the lock
	lock2, err := lm.AcquireLock(ctx, itemID, "item", agent2ID, agents.LockTypePessimistic)
	assert.NoError(t, err)
	assert.NotNil(t, lock2)

	err = lm.ReleaseLock(ctx, lock2.ID, agent2ID)
	assert.NoError(t, err)
}

// TestConflictDetection tests conflict detection between agents
func TestConflictDetection(t *testing.T) {
	db := setupTestDB(t)
	defer db.Migrator().DropTable(&agents.AgentLock{}, &agents.ItemVersion{}, &agents.ConflictRecord{})

	db.AutoMigrate(&agents.AgentLock{}, &agents.ItemVersion{}, &agents.ConflictRecord{})

	lm := agents.NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()

	cd := agents.NewConflictDetector(db, lm)
	ctx := context.Background()

	itemID := "item-conflict"
	agent1ID := "agent-1"
	agent2ID := "agent-2"

	// Agent 1 updates item version 1
	err := lm.RecordVersion(ctx, itemID, agent1ID, 1, map[string]interface{}{"field": "value1"}, "", "hash1")
	require.NoError(t, err)

	// Agent 2 tries to update with outdated version
	conflict, err := cd.DetectConflict(ctx, itemID, agent2ID, 1)
	require.NoError(t, err)
	assert.NotNil(t, conflict)
	assert.Equal(t, "version_mismatch", conflict.ConflictType)
	assert.Contains(t, conflict.ConflictingAgents, agent1ID)

	// Resolve the conflict
	err = cd.ResolveConflict(ctx, conflict.ID, agent2ID, agents.ResolutionLastWriteWins, map[string]interface{}{"resolved": true})
	assert.NoError(t, err)

	// Verify conflict is resolved
	var resolvedConflict agents.ConflictRecord
	err = db.First(&resolvedConflict, "id = ?", conflict.ID).Error
	require.NoError(t, err)
	assert.Equal(t, "resolved", resolvedConflict.ResolutionStatus)
	assert.Equal(t, agent2ID, resolvedConflict.ResolvedBy)
}

// TestConcurrentLockAcquisition tests concurrent lock acquisition by multiple agents
func TestConcurrentLockAcquisition(t *testing.T) {
	db := setupTestDB(t)
	defer db.Migrator().DropTable(&agents.AgentLock{})

	db.AutoMigrate(&agents.AgentLock{})

	lm := agents.NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()

	ctx := context.Background()
	numAgents := 10
	itemID := "item-concurrent"

	var wg sync.WaitGroup
	successCount := 0
	var mu sync.Mutex

	// Simulate 10 agents trying to acquire pessimistic lock concurrently
	for i := 0; i < numAgents; i++ {
		wg.Add(1)
		go func(agentNum int) {
			defer wg.Done()
			agentID := fmt.Sprintf("agent-%d", agentNum)

			lock, err := lm.AcquireLock(ctx, itemID, "item", agentID, agents.LockTypePessimistic)
			if err == nil && lock != nil {
				mu.Lock()
				successCount++
				mu.Unlock()

				// Hold lock briefly
				time.Sleep(10 * time.Millisecond)

				lm.ReleaseLock(ctx, lock.ID, agentID)
			}
		}(i)
	}

	wg.Wait()

	// Only one agent should successfully acquire the pessimistic lock initially
	assert.Equal(t, 1, successCount)
}

// TestTeamManagement tests agent team and role management
func TestTeamManagement(t *testing.T) {
	db := setupTestDB(t)
	defer db.Migrator().DropTable(&agents.AgentTeam{}, &agents.AgentTeamMembership{})

	db.AutoMigrate(&agents.AgentTeam{}, &agents.AgentTeamMembership{})

	tm := agents.NewTeamManager(db)
	ctx := context.Background()

	// Create team with roles
	team := &agents.AgentTeam{
		ProjectID:   "project-123",
		Name:        "Dev Team",
		Description: "Development team",
		Roles: map[string]agents.TeamRole{
			"developer": {
				Name:        "developer",
				Permissions: []string{"read", "write"},
				Priority:    5,
			},
			"lead": {
				Name:        "lead",
				Permissions: []string{"read", "write", "delete", "lock"},
				Priority:    10,
			},
		},
		Metadata: make(map[string]interface{}),
	}

	err := tm.CreateTeam(ctx, team)
	require.NoError(t, err)
	assert.NotEmpty(t, team.ID)

	// Add team members
	agent1ID := "agent-1"
	agent2ID := "agent-2"

	err = tm.AddTeamMember(ctx, team.ID, agent1ID, "developer")
	assert.NoError(t, err)

	err = tm.AddTeamMember(ctx, team.ID, agent2ID, "lead")
	assert.NoError(t, err)

	// Check permissions for developer
	perms1, priority1, err := tm.GetAgentPermissions(ctx, agent1ID)
	require.NoError(t, err)
	assert.Contains(t, perms1, "read")
	assert.Contains(t, perms1, "write")
	assert.NotContains(t, perms1, "delete")
	assert.Equal(t, 5, priority1)

	// Check permissions for lead
	perms2, priority2, err := tm.GetAgentPermissions(ctx, agent2ID)
	require.NoError(t, err)
	assert.Contains(t, perms2, "read")
	assert.Contains(t, perms2, "write")
	assert.Contains(t, perms2, "delete")
	assert.Contains(t, perms2, "lock")
	assert.Equal(t, 10, priority2)

	// Verify has permission
	hasWrite, err := tm.HasPermission(ctx, agent1ID, "write")
	assert.NoError(t, err)
	assert.True(t, hasWrite)

	hasDelete, err := tm.HasPermission(ctx, agent1ID, "delete")
	assert.NoError(t, err)
	assert.False(t, hasDelete)
}

// TestDistributedOperation tests coordinated operations across multiple agents
func TestDistributedOperation(t *testing.T) {
	db := setupTestDB(t)
	defer db.Migrator().DropTable(&agents.DistributedOperation{}, &agents.OperationParticipant{}, &agents.AgentLock{}, &agents.ConflictRecord{})

	db.AutoMigrate(&agents.DistributedOperation{}, &agents.OperationParticipant{}, &agents.AgentLock{}, &agents.ConflictRecord{})

	lm := agents.NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()

	cd := agents.NewConflictDetector(db, lm)
	tm := agents.NewTeamManager(db)
	dc := agents.NewDistributedCoordinator(db, lm, cd, tm)

	ctx := context.Background()
	projectID := "project-123"
	coordinatorID := "agent-coordinator"

	// Create distributed operation
	op := &agents.DistributedOperation{
		ProjectID:      projectID,
		Type:           "batch_update",
		ParticipantIDs: []string{"agent-1", "agent-2", "agent-3"},
		CoordinatorID:  coordinatorID,
		TargetItems:    []string{"item-1", "item-2", "item-3"},
		OperationData:  make(map[string]interface{}),
	}

	err := dc.CreateDistributedOperation(ctx, op)
	require.NoError(t, err)
	assert.NotEmpty(t, op.ID)

	// Assign work to agents
	assignments := map[string][]string{
		"agent-1": {"item-1"},
		"agent-2": {"item-2"},
		"agent-3": {"item-3"},
	}

	err = dc.AssignOperationToAgents(ctx, op.ID, assignments)
	require.NoError(t, err)

	// Simulate agents completing their work
	for agentID, items := range assignments {
		err = dc.StartParticipation(ctx, op.ID, agentID)
		assert.NoError(t, err)

		result := map[string]interface{}{
			"items_processed": items,
			"status":          "success",
		}

		err = dc.CompleteParticipation(ctx, op.ID, agentID, result)
		assert.NoError(t, err)
	}

	// Check operation status
	opStatus, participants, err := dc.GetOperationStatus(ctx, op.ID)
	require.NoError(t, err)
	assert.Equal(t, "completed", opStatus.Status)
	assert.Len(t, participants, 3)

	for _, p := range participants {
		assert.Equal(t, "completed", p.Status)
	}
}

// TestCoordinatedUpdate tests coordinated batch updates with lock acquisition
func TestCoordinatedUpdate(t *testing.T) {
	db := setupTestDB(t)
	defer db.Migrator().DropTable(&agents.DistributedOperation{}, &agents.AgentLock{}, &agents.ConflictRecord{}, &agents.ItemVersion{})

	db.AutoMigrate(&agents.DistributedOperation{}, &agents.AgentLock{}, &agents.ConflictRecord{}, &agents.ItemVersion{})

	lm := agents.NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()

	cd := agents.NewConflictDetector(db, lm)
	tm := agents.NewTeamManager(db)
	dc := agents.NewDistributedCoordinator(db, lm, cd, tm)

	ctx := context.Background()
	projectID := "project-456"
	coordinatorID := "agent-coordinator"

	updates := map[string]map[string]interface{}{
		"item-1": {"field": "value1"},
		"item-2": {"field": "value2"},
		"item-3": {"field": "value3"},
	}

	// Start coordinated update
	op, err := dc.CoordinatedUpdate(ctx, projectID, updates, coordinatorID)
	require.NoError(t, err)
	assert.NotNil(t, op)
	assert.Equal(t, "in_progress", op.Status)

	// Verify locks were acquired
	locks, err := lm.GetActiveLocks(ctx, coordinatorID, "")
	require.NoError(t, err)
	assert.Len(t, locks, 3)

	// Complete the update
	err = dc.CompleteCoordinatedUpdate(ctx, op.ID, coordinatorID)
	require.NoError(t, err)

	// Verify locks were released
	locks, err = lm.GetActiveLocks(ctx, coordinatorID, "")
	require.NoError(t, err)
	assert.Len(t, locks, 0)
}

// TestConcurrentConflictDetection tests conflict detection under concurrent load
func TestConcurrentConflictDetection(t *testing.T) {
	db := setupTestDB(t)
	defer db.Migrator().DropTable(&agents.AgentLock{}, &agents.ItemVersion{}, &agents.ConflictRecord{})

	db.AutoMigrate(&agents.AgentLock{}, &agents.ItemVersion{}, &agents.ConflictRecord{})

	lm := agents.NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()

	cd := agents.NewConflictDetector(db, lm)
	ctx := context.Background()

	itemID := "item-hotspot"
	numAgents := 20

	// Record initial version
	err := lm.RecordVersion(ctx, itemID, "initial-agent", 1, map[string]interface{}{"field": "initial"}, "", "hash0")
	require.NoError(t, err)

	var wg sync.WaitGroup
	conflictCount := 0
	var mu sync.Mutex

	// Simulate 20 agents trying to modify the same item concurrently
	for i := 0; i < numAgents; i++ {
		wg.Add(1)
		go func(agentNum int) {
			defer wg.Done()
			agentID := fmt.Sprintf("agent-%d", agentNum)

			// All agents expect version 2 (conflict with each other)
			conflict, err := cd.DetectConflict(ctx, itemID, agentID, 2)
			if err == nil && conflict != nil {
				mu.Lock()
				conflictCount++
				mu.Unlock()
			}
		}(i)
	}

	wg.Wait()

	// Should detect conflicts
	assert.Greater(t, conflictCount, 0)

	// Get all pending conflicts
	conflicts, err := cd.GetPendingConflicts(ctx, itemID, "")
	require.NoError(t, err)
	assert.Greater(t, len(conflicts), 0)
}

// TestScalabilitySimulation tests system under load with many agents
func TestScalabilitySimulation(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping scalability test in short mode")
	}

	db := setupTestDB(t)
	defer db.Migrator().DropTable(&agents.AgentLock{}, &agents.ItemVersion{}, &agents.ConflictRecord{})

	db.AutoMigrate(&agents.AgentLock{}, &agents.ItemVersion{}, &agents.ConflictRecord{})

	lm := agents.NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()

	cd := agents.NewConflictDetector(db, lm)
	ctx := context.Background()

	numAgents := 100
	numItems := 50
	operationsPerAgent := 10

	var wg sync.WaitGroup
	successfulOps := 0
	failedOps := 0
	var mu sync.Mutex

	startTime := time.Now()

	// Simulate 100 agents performing operations
	for i := 0; i < numAgents; i++ {
		wg.Add(1)
		go func(agentNum int) {
			defer wg.Done()
			agentID := fmt.Sprintf("agent-%d", agentNum)

			for op := 0; op < operationsPerAgent; op++ {
				// Randomly pick an item
				itemID := fmt.Sprintf("item-%d", agentNum%numItems)

				// Try to acquire lock
				lock, err := lm.AcquireLock(ctx, itemID, "item", agentID, agents.LockTypeOptimistic)
				if err != nil {
					mu.Lock()
					failedOps++
					mu.Unlock()
					continue
				}

				// Simulate some work
				time.Sleep(1 * time.Millisecond)

				// Release lock
				err = lm.ReleaseLock(ctx, lock.ID, agentID)
				if err == nil {
					mu.Lock()
					successfulOps++
					mu.Unlock()
				} else {
					mu.Lock()
					failedOps++
					mu.Unlock()
				}
			}
		}(i)
	}

	wg.Wait()
	duration := time.Since(startTime)

	totalOps := successfulOps + failedOps
	successRate := float64(successfulOps) / float64(totalOps) * 100
	opsPerSecond := float64(totalOps) / duration.Seconds()

	t.Logf("Scalability Test Results:")
	t.Logf("  Agents: %d", numAgents)
	t.Logf("  Operations per agent: %d", operationsPerAgent)
	t.Logf("  Total operations: %d", totalOps)
	t.Logf("  Successful: %d (%.2f%%)", successfulOps, successRate)
	t.Logf("  Failed: %d", failedOps)
	t.Logf("  Duration: %v", duration)
	t.Logf("  Throughput: %.2f ops/sec", opsPerSecond)

	// Assert reasonable performance
	assert.Greater(t, successRate, 80.0, "Success rate should be > 80%")
	assert.Greater(t, opsPerSecond, 100.0, "Throughput should be > 100 ops/sec")
}

// BenchmarkLockAcquisition benchmarks lock acquisition performance
func BenchmarkLockAcquisition(b *testing.B) {
	db := setupTestDB(&testing.T{})
	defer db.Migrator().DropTable(&agents.AgentLock{})

	db.AutoMigrate(&agents.AgentLock{})

	lm := agents.NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()

	ctx := context.Background()
	agentID := "bench-agent"

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		itemID := fmt.Sprintf("item-%d", i)
		lock, err := lm.AcquireLock(ctx, itemID, "item", agentID, agents.LockTypeOptimistic)
		if err == nil {
			lm.ReleaseLock(ctx, lock.ID, agentID)
		}
	}
}

// BenchmarkConflictDetection benchmarks conflict detection performance
func BenchmarkConflictDetection(b *testing.B) {
	db := setupTestDB(&testing.T{})
	defer db.Migrator().DropTable(&agents.AgentLock{}, &agents.ItemVersion{}, &agents.ConflictRecord{})

	db.AutoMigrate(&agents.AgentLock{}, &agents.ItemVersion{}, &agents.ConflictRecord{})

	lm := agents.NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()

	cd := agents.NewConflictDetector(db, lm)
	ctx := context.Background()

	// Pre-populate with some versions
	for i := 0; i < 100; i++ {
		itemID := fmt.Sprintf("item-%d", i)
		lm.RecordVersion(ctx, itemID, "agent-0", 1, map[string]interface{}{"field": "value"}, "", "hash")
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		itemID := fmt.Sprintf("item-%d", i%100)
		agentID := fmt.Sprintf("agent-%d", i)
		cd.DetectConflict(ctx, itemID, agentID, 2)
	}
}
