//go:build !integration && !e2e

package agents

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

const testLockTimeout = 5 * time.Minute

func newTestDB(t *testing.T) *gorm.DB {
	t.Helper()
	// Use a unique in-memory database per test to avoid data pollution between tests
	db, err := gorm.Open(sqlite.Open("file::memory:"), &gorm.Config{})
	require.NoError(t, err)
	require.NoError(t, db.AutoMigrate(
		&AgentLock{},
		&ItemVersion{},
		&ConflictRecord{},
		&AgentTeam{},
		&AgentTeamMembership{},
		&DistributedOperation{},
		&OperationParticipant{},
	))
	return db
}

// ========== LockManager unit tests ==========

func TestNewLockManager(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	require.NotNil(t, lm)
	defer lm.Shutdown()
}

func TestLockManager_AcquireLock_FirstTime(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	ctx := context.Background()

	lock, err := lm.AcquireLock(ctx, "item-1", "task", "agent-1", LockTypePessimistic)
	require.NoError(t, err)
	require.NotNil(t, lock)
	assert.Equal(t, "item-1", lock.ItemID)
	assert.Equal(t, "agent-1", lock.AgentID)
	assert.Equal(t, LockTypePessimistic, lock.LockType)
}

func TestLockManager_AcquireLock_SameAgentRefreshes(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	ctx := context.Background()

	lock1, err := lm.AcquireLock(ctx, "item-1", "task", "agent-1", LockTypePessimistic)
	require.NoError(t, err)
	lock2, err := lm.AcquireLock(ctx, "item-1", "task", "agent-1", LockTypePessimistic)
	require.NoError(t, err)
	assert.Equal(t, lock1.ID, lock2.ID)
}

func TestLockManager_AcquireLock_OtherAgentFails(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	ctx := context.Background()

	_, err := lm.AcquireLock(ctx, "item-1", "task", "agent-1", LockTypePessimistic)
	require.NoError(t, err)
	_, err = lm.AcquireLock(ctx, "item-1", "task", "agent-2", LockTypePessimistic)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "locked by agent")
}

func TestLockManager_ReleaseLock_Success(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	ctx := context.Background()

	lock, err := lm.AcquireLock(ctx, "item-1", "task", "agent-1", LockTypePessimistic)
	require.NoError(t, err)
	err = lm.ReleaseLock(ctx, lock.ID, "agent-1")
	require.NoError(t, err)
	// Second acquire by other agent should succeed
	_, err = lm.AcquireLock(ctx, "item-1", "task", "agent-2", LockTypePessimistic)
	require.NoError(t, err)
}

func TestLockManager_ReleaseLock_WrongAgent(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	ctx := context.Background()

	lock, err := lm.AcquireLock(ctx, "item-1", "task", "agent-1", LockTypePessimistic)
	require.NoError(t, err)
	err = lm.ReleaseLock(ctx, lock.ID, "agent-2")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "owned by")
}

func TestLockManager_ValidateVersion_NewItem(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	ctx := context.Background()

	err := lm.ValidateVersion(ctx, "new-item", 1)
	require.NoError(t, err)
}

func TestLockManager_ValidateVersion_Mismatch(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	ctx := context.Background()

	err := lm.ValidateVersion(ctx, "new-item", 2)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "version")
}

func TestLockManager_RecordVersion(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	ctx := context.Background()

	err := lm.RecordVersion(ctx, "item-1", "agent-1", 1, map[string]interface{}{"x": 1}, "h0", "h1")
	require.NoError(t, err)
}

func TestLockManager_GetActiveLocks(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	ctx := context.Background()

	_, err := lm.AcquireLock(ctx, "item-1", "task", "agent-1", LockTypePessimistic)
	require.NoError(t, err)
	locks, err := lm.GetActiveLocks(ctx, "agent-1", "")
	require.NoError(t, err)
	assert.Len(t, locks, 1)
}

// ========== ConflictDetector unit tests ==========

func TestNewConflictDetector(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	require.NotNil(t, cd)
}

func TestConflictDetector_DetectConflict_NoConflict(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	ctx := context.Background()

	conflict, err := cd.DetectConflict(ctx, "item-1", "agent-1", 1)
	require.NoError(t, err)
	assert.Nil(t, conflict)
}

func TestExtractConflictingAgents(t *testing.T) {
	locks := []AgentLock{
		{ItemID: "i1", AgentID: "agent-2"},
		{ItemID: "i2", AgentID: "agent-3"},
	}
	agents := extractConflictingAgents(locks, "agent-1")
	assert.Len(t, agents, 2)
	assert.Contains(t, agents, "agent-2")
	assert.Contains(t, agents, "agent-3")
}

func TestBuildConcurrentConflict_EmptyAgents(t *testing.T) {
	c := buildConcurrentConflict("item-1", "agent-1", nil)
	assert.Nil(t, c)
	c = buildConcurrentConflict("item-1", "agent-1", []string{})
	assert.Nil(t, c)
}

func TestBuildConcurrentConflict_WithAgents(t *testing.T) {
	c := buildConcurrentConflict("item-1", "agent-1", []string{"agent-2"})
	require.NotNil(t, c)
	assert.Equal(t, "concurrent_modification", c.ConflictType)
	assert.Equal(t, ResolutionFirstWins, c.ResolutionStrategy)
}

// ========== TeamManager unit tests ==========

func TestNewTeamManager(t *testing.T) {
	db := newTestDB(t)
	tm := NewTeamManager(db)
	require.NotNil(t, tm)
}

func TestTeamManager_CreateTeam(t *testing.T) {
	db := newTestDB(t)
	tm := NewTeamManager(db)
	ctx := context.Background()

	team := &AgentTeam{
		ProjectID: "p1",
		Name:      "Dev Team",
		Roles: map[string]TeamRole{
			"member": {Name: "member", Permissions: []string{"read"}, Priority: 1},
		},
	}
	err := tm.CreateTeam(ctx, team)
	require.NoError(t, err)
	assert.NotEmpty(t, team.ID)
}

func TestTeamManager_AddTeamMember(t *testing.T) {
	db := newTestDB(t)
	tm := NewTeamManager(db)
	ctx := context.Background()

	team := &AgentTeam{
		ProjectID: "p1",
		Name:      "Team",
		Roles:     map[string]TeamRole{"member": {Name: "member", Permissions: []string{"read"}, Priority: 1}},
	}
	require.NoError(t, tm.CreateTeam(ctx, team))
	err := tm.AddTeamMember(ctx, team.ID, "agent-1", "member")
	require.NoError(t, err)
}

func TestTeamManager_AddTeamMember_TeamNotFound(t *testing.T) {
	db := newTestDB(t)
	tm := NewTeamManager(db)
	ctx := context.Background()

	err := tm.AddTeamMember(ctx, uuid.New().String(), "agent-1", "member")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "team not found")
}

func TestTeamManager_GetAgentPermissions_NoMemberships(t *testing.T) {
	db := newTestDB(t)
	tm := NewTeamManager(db)
	ctx := context.Background()

	perms, priority, err := tm.GetAgentPermissions(ctx, "no-agent")
	require.NoError(t, err)
	assert.Empty(t, perms)
	assert.Equal(t, 0, priority)
}

func TestTeamManager_HasPermission_NoPerm(t *testing.T) {
	db := newTestDB(t)
	tm := NewTeamManager(db)
	ctx := context.Background()

	ok, err := tm.HasPermission(ctx, "agent-1", "write")
	require.NoError(t, err)
	assert.False(t, ok)
}

// ========== DistributedCoordinator unit tests ==========

func TestNewDistributedCoordinator(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	tm := NewTeamManager(db)
	dc := NewDistributedCoordinator(db, lm, cd, tm)
	require.NotNil(t, dc)
}

func TestDistributedCoordinator_CreateDistributedOperation(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	tm := NewTeamManager(db)
	dc := NewDistributedCoordinator(db, lm, cd, tm)
	ctx := context.Background()

	op := &DistributedOperation{
		ProjectID:   "p1",
		Type:        "batch_update",
		TargetItems: []string{"i1"},
	}
	err := dc.CreateDistributedOperation(ctx, op)
	require.NoError(t, err)
	assert.NotEmpty(t, op.ID)
	assert.Equal(t, string(TaskStatusPending), op.Status)
}

func TestBuildItemIDs(t *testing.T) {
	updates := map[string]map[string]interface{}{
		"id1": {"a": 1},
		"id2": {"b": 2},
	}
	ids := buildItemIDs(updates)
	require.Len(t, ids, 2)
	assert.Contains(t, ids, "id1")
	assert.Contains(t, ids, "id2")
}

func TestLockIDsFromLocks(t *testing.T) {
	locks := []*AgentLock{
		{ID: "l1"},
		{ID: "l2"},
	}
	ids := lockIDsFromLocks(locks)
	assert.Equal(t, []string{"l1", "l2"}, ids)
}

func TestDistributedCoordinator_GetOperationStatus(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	tm := NewTeamManager(db)
	dc := NewDistributedCoordinator(db, lm, cd, tm)
	ctx := context.Background()

	op := &DistributedOperation{ProjectID: "p1", Type: "batch", TargetItems: []string{}}
	require.NoError(t, dc.CreateDistributedOperation(ctx, op))

	got, participants, err := dc.GetOperationStatus(ctx, op.ID)
	require.NoError(t, err)
	require.NotNil(t, got)
	assert.Equal(t, op.ID, got.ID)
	assert.NotNil(t, participants)
}

func TestDistributedCoordinator_GetOperationStatus_NotFound(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	tm := NewTeamManager(db)
	dc := NewDistributedCoordinator(db, lm, cd, tm)
	ctx := context.Background()

	_, _, err := dc.GetOperationStatus(ctx, uuid.New().String())
	require.Error(t, err)
	assert.Contains(t, err.Error(), "not found")
}

func TestDistributedCoordinator_AssignOperationToAgents(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	tm := NewTeamManager(db)
	dc := NewDistributedCoordinator(db, lm, cd, tm)
	ctx := context.Background()

	op := &DistributedOperation{ProjectID: "p1", Type: "batch", TargetItems: []string{"i1"}}
	require.NoError(t, dc.CreateDistributedOperation(ctx, op))

	err := dc.AssignOperationToAgents(ctx, op.ID, map[string][]string{"agent-1": {"i1"}})
	require.NoError(t, err)
}

func TestDistributedCoordinator_AssignOperationToAgents_NotPending(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	tm := NewTeamManager(db)
	dc := NewDistributedCoordinator(db, lm, cd, tm)
	ctx := context.Background()

	op := &DistributedOperation{
		ID:          uuid.New().String(),
		ProjectID:   "p1",
		Type:        "batch",
		TargetItems: []string{},
		Status:      statusInProgress,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	_ = dc.db.Create(op).Error

	err := dc.AssignOperationToAgents(ctx, op.ID, map[string][]string{"agent-1": {}})
	require.Error(t, err)
	assert.Contains(t, err.Error(), "not in pending")
}

func TestDistributedCoordinator_StartParticipation(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	tm := NewTeamManager(db)
	dc := NewDistributedCoordinator(db, lm, cd, tm)
	ctx := context.Background()

	op := &DistributedOperation{ProjectID: "p1", Type: "batch", TargetItems: []string{}}
	require.NoError(t, dc.CreateDistributedOperation(ctx, op))
	require.NoError(t, dc.AssignOperationToAgents(ctx, op.ID, map[string][]string{"agent-1": {}}))

	err := dc.StartParticipation(ctx, op.ID, "agent-1")
	require.NoError(t, err)
}

func TestDistributedCoordinator_GetDistributedOperation(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	tm := NewTeamManager(db)
	dc := NewDistributedCoordinator(db, lm, cd, tm)
	ctx := context.Background()

	op := &DistributedOperation{ProjectID: "p1", Type: "batch", TargetItems: []string{}}
	require.NoError(t, dc.CreateDistributedOperation(ctx, op))

	got, err := dc.GetDistributedOperation(ctx, op.ID)
	require.NoError(t, err)
	require.NotNil(t, got)
	assert.Equal(t, op.ID, got.ID)
}

func TestDistributedCoordinator_ListOperations(t *testing.T) {
	db := newTestDB(t)
	lm := NewLockManager(db, testLockTimeout)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	tm := NewTeamManager(db)
	dc := NewDistributedCoordinator(db, lm, cd, tm)
	ctx := context.Background()

	op := &DistributedOperation{ProjectID: "p1", Type: "batch", TargetItems: []string{}}
	require.NoError(t, dc.CreateDistributedOperation(ctx, op))

	list, err := dc.ListOperations(ctx, "p1", "")
	require.NoError(t, err)
	assert.GreaterOrEqual(t, len(list), 1)
}
