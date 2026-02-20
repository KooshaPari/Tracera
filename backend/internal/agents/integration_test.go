//go:build integration && !e2e

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

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// integrationAgentTaskStore mirrors queue's task storage for migration.
type integrationAgentTaskStore struct {
	ID        string `gorm:"primaryKey"`
	ProjectID string `gorm:"index"`
	Status    string `gorm:"index"`
	Priority  int    `gorm:"index"`
	Data      []byte `gorm:"type:jsonb"`
	CreatedAt time.Time
	UpdatedAt time.Time
}

func (integrationAgentTaskStore) TableName() string { return "agent_tasks" }

func integrationDB(t *testing.T) *gorm.DB {
	t.Helper()
	db, err := gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{})
	require.NoError(t, err)
	require.NoError(t, db.AutoMigrate(
		&models.Agent{},
		&AgentLock{},
		&ItemVersion{},
		&ConflictRecord{},
		&AgentTeam{},
		&AgentTeamMembership{},
		&DistributedOperation{},
		&OperationParticipant{},
		&integrationAgentTaskStore{},
	))
	return db
}

// Integration test 1: Coordinator with DB – register and persist
func TestIntegration_Coordinator_RegisterAgent_WithDB(t *testing.T) {
	db := integrationDB(t)
	c := NewCoordinator(db, 2*time.Minute)
	defer c.Shutdown()

	agent := &RegisteredAgent{Name: "int-agent", ProjectID: "p1"}
	err := c.RegisterAgent(agent)
	require.NoError(t, err)
	assert.NotEmpty(t, agent.ID)

	got, err := c.GetAgent(agent.ID)
	require.NoError(t, err)
	assert.Equal(t, agent.Name, got.Name)
}

// Integration test 2: Coordinator – unregister with DB
func TestIntegration_Coordinator_UnregisterAgent_WithDB(t *testing.T) {
	db := integrationDB(t)
	c := NewCoordinator(db, 2*time.Minute)
	defer c.Shutdown()

	agent := &RegisteredAgent{Name: "a", ProjectID: "p1"}
	_ = c.RegisterAgent(agent)
	err := c.UnregisterAgent(agent.ID)
	require.NoError(t, err)
	_, err = c.GetAgent(agent.ID)
	require.Error(t, err)
}

// Integration test 3: TaskQueue – enqueue and load from DB
func TestIntegration_TaskQueue_EnqueueAndLoadFromDB(t *testing.T) {
	db := integrationDB(t)
	tq := NewTaskQueue(db)
	task := &Task{ID: "t1", ProjectID: "p1", Type: "run"}
	err := tq.EnqueueTask(task)
	require.NoError(t, err)

	tq2 := NewTaskQueue(db)
	err = tq2.LoadTasksFromDB()
	require.NoError(t, err)
	got, err := tq2.GetTask("t1")
	require.NoError(t, err)
	assert.Equal(t, "t1", got.ID)
}

// Integration test 4: Coordinator AssignTask with DB and idle agent
func TestIntegration_Coordinator_AssignTask_WithDB(t *testing.T) {
	db := integrationDB(t)
	c := NewCoordinator(db, 2*time.Minute)
	defer c.Shutdown()

	agent := &RegisteredAgent{
		ID: "ag-1", Name: "w", ProjectID: "p1", Status: StatusIdle,
		Capabilities: []AgentCapability{{Name: "run"}},
	}
	_ = c.RegisterAgent(agent)
	task := &Task{ID: "t1", ProjectID: "p1", RequiredCapabilities: []string{"run"}}
	err := c.AssignTask(task)
	require.NoError(t, err)
	assert.Equal(t, TaskStatusAssigned, task.Status)
	assert.Equal(t, "ag-1", task.AssignedTo)
}

// Integration test 5: Coordinator CompleteTask with DB
func TestIntegration_Coordinator_CompleteTask_WithDB(t *testing.T) {
	db := integrationDB(t)
	c := NewCoordinator(db, 2*time.Minute)
	defer c.Shutdown()

	task := &Task{ID: "t1", ProjectID: "p1", Status: TaskStatusAssigned}
	agent := &RegisteredAgent{
		ID: "ag-1", Name: "w", ProjectID: "p1", Status: StatusBusy,
		CurrentTask: task,
	}
	_ = c.RegisterAgent(agent)
	err := c.CompleteTask("ag-1", "t1", &TaskResult{Success: true})
	require.NoError(t, err)
	assert.Equal(t, TaskStatusCompleted, task.Status)
}

// Integration test 6: LockManager acquire and release across calls
func TestIntegration_LockManager_AcquireRelease(t *testing.T) {
	db := integrationDB(t)
	lm := NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()
	ctx := context.Background()

	lock, err := lm.AcquireLock(ctx, "item-1", "task", "agent-1", LockTypePessimistic)
	require.NoError(t, err)
	err = lm.ReleaseLock(ctx, lock.ID, "agent-1")
	require.NoError(t, err)
	lock2, err := lm.AcquireLock(ctx, "item-1", "task", "agent-2", LockTypePessimistic)
	require.NoError(t, err)
	assert.Equal(t, "agent-2", lock2.AgentID)
}

// Integration test 7: ConflictDetector – resolve conflict
func TestIntegration_ConflictDetector_ResolveConflict(t *testing.T) {
	db := integrationDB(t)
	lm := NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	ctx := context.Background()

	conflict := &ConflictRecord{
		ID:                uuid.New().String(),
		ItemID:            "item-1",
		ConflictingAgents: []string{"agent-2"},
		ConflictType:      "concurrent_modification",
		ResolutionStatus:  resolutionStatusPending,
		ConflictData:      map[string]interface{}{},
		CreatedAt:         time.Now(),
		UpdatedAt:         time.Now(),
	}
	_ = db.Create(conflict).Error

	err := cd.ResolveConflict(ctx, conflict.ID, "agent-1", ResolutionLastWriteWins, map[string]interface{}{"chosen": "agent-1"})
	require.NoError(t, err)
}

// Integration test 8: TeamManager – create team and add member, then get permissions
func TestIntegration_TeamManager_CreateTeam_AddMember_GetPermissions(t *testing.T) {
	db := integrationDB(t)
	tm := NewTeamManager(db)
	ctx := context.Background()

	team := &AgentTeam{
		ProjectID: "p1",
		Name:      "Team",
		Roles:     map[string]TeamRole{"member": {Name: "member", Permissions: []string{"read", "write"}, Priority: 10}},
	}
	err := tm.CreateTeam(ctx, team)
	require.NoError(t, err)
	err = tm.AddTeamMember(ctx, team.ID, "agent-1", "member")
	require.NoError(t, err)

	perms, priority, err := tm.GetAgentPermissions(ctx, "agent-1")
	require.NoError(t, err)
	assert.GreaterOrEqual(t, len(perms), 1)
	assert.Equal(t, 10, priority)

	ok, err := tm.HasPermission(ctx, "agent-1", "read")
	require.NoError(t, err)
	assert.True(t, ok)
}

// Integration test 9: DistributedCoordinator – create and assign operation
func TestIntegration_DistributedCoordinator_CreateAndAssign(t *testing.T) {
	db := integrationDB(t)
	lm := NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	tm := NewTeamManager(db)
	dc := NewDistributedCoordinator(db, lm, cd, tm)
	ctx := context.Background()

	op := &DistributedOperation{ProjectID: "p1", Type: "batch", TargetItems: []string{"i1", "i2"}}
	err := dc.CreateDistributedOperation(ctx, op)
	require.NoError(t, err)
	err = dc.AssignOperationToAgents(ctx, op.ID, map[string][]string{"agent-1": {"i1"}, "agent-2": {"i2"}})
	require.NoError(t, err)

	status, participants, err := dc.GetOperationStatus(ctx, op.ID)
	require.NoError(t, err)
	assert.Equal(t, statusInProgress, status.Status)
	assert.Len(t, participants, 2)
}

// Integration test 10: DistributedCoordinator – StartParticipation and CompleteParticipation
func TestIntegration_DistributedCoordinator_StartAndCompleteParticipation(t *testing.T) {
	db := integrationDB(t)
	lm := NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	tm := NewTeamManager(db)
	dc := NewDistributedCoordinator(db, lm, cd, tm)
	ctx := context.Background()

	op := &DistributedOperation{ProjectID: "p1", Type: "batch", TargetItems: []string{"i1"}}
	_ = dc.CreateDistributedOperation(ctx, op)
	_ = dc.AssignOperationToAgents(ctx, op.ID, map[string][]string{"agent-1": {"i1"}})

	_ = dc.StartParticipation(ctx, op.ID, "agent-1")
	err := dc.CompleteParticipation(ctx, op.ID, "agent-1", map[string]interface{}{"result": "ok"})
	require.NoError(t, err)

	status, _, _ := dc.GetOperationStatus(ctx, op.ID)
	assert.Equal(t, string(TaskStatusCompleted), status.Status)
}

// Integration test 11: TaskQueue – requeue and update status with DB
func TestIntegration_TaskQueue_Requeue_UpdateStatus_WithDB(t *testing.T) {
	db := integrationDB(t)
	tq := NewTaskQueue(db)
	task := &Task{ID: "t1", ProjectID: "p1"}
	_ = tq.EnqueueTask(task)
	task.Status = TaskStatusAssigned
	task.AssignedTo = "ag-1"
	err := tq.UpdateTaskStatus(task)
	require.NoError(t, err)
	err = tq.RequeueTask(task)
	require.NoError(t, err)
	assert.Equal(t, TaskStatusPending, task.Status)
}

// Integration test 12: Coordinator Heartbeat with DB
func TestIntegration_Coordinator_Heartbeat_WithDB(t *testing.T) {
	db := integrationDB(t)
	c := NewCoordinator(db, 2*time.Minute)
	defer c.Shutdown()

	agent := &RegisteredAgent{Name: "a", ProjectID: "p1"}
	_ = c.RegisterAgent(agent)
	err := c.Heartbeat(agent.ID, StatusBusy)
	require.NoError(t, err)
	a, _ := c.GetAgent(agent.ID)
	assert.Equal(t, StatusBusy, a.Status)
}

// Integration test 13: LockManager RecordVersion and ValidateVersion
func TestIntegration_LockManager_RecordAndValidateVersion(t *testing.T) {
	db := integrationDB(t)
	lm := NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()
	ctx := context.Background()

	_ = lm.RecordVersion(ctx, "item-1", "agent-1", 1, map[string]interface{}{"x": 1}, "h0", "h1")
	err := lm.ValidateVersion(ctx, "item-1", 2)
	require.NoError(t, err)
}

// Integration test 14: ConflictDetector GetPendingConflicts
func TestIntegration_ConflictDetector_GetPendingConflicts(t *testing.T) {
	db := integrationDB(t)
	lm := NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	ctx := context.Background()

	conflict := &ConflictRecord{
		ID:                uuid.New().String(),
		ItemID:            "item-1",
		ConflictingAgents: []string{"agent-2"},
		ResolutionStatus:  resolutionStatusPending,
		ConflictData:      map[string]interface{}{},
		CreatedAt:         time.Now(),
		UpdatedAt:         time.Now(),
	}
	_ = db.Create(conflict).Error

	list, err := cd.GetPendingConflicts(ctx, "item-1", "")
	require.NoError(t, err)
	assert.GreaterOrEqual(t, len(list), 1)
}

// Integration test 15: DistributedCoordinator GetOperationResults
func TestIntegration_DistributedCoordinator_GetOperationResults(t *testing.T) {
	db := integrationDB(t)
	lm := NewLockManager(db, 5*time.Minute)
	defer lm.Shutdown()
	cd := NewConflictDetector(db, lm)
	tm := NewTeamManager(db)
	dc := NewDistributedCoordinator(db, lm, cd, tm)
	ctx := context.Background()

	op := &DistributedOperation{ProjectID: "p1", Type: "batch", TargetItems: []string{"i1"}}
	_ = dc.CreateDistributedOperation(ctx, op)
	_ = dc.AssignOperationToAgents(ctx, op.ID, map[string][]string{"agent-1": {"i1"}})
	_ = dc.CompleteParticipation(ctx, op.ID, "agent-1", map[string]interface{}{"done": true})

	// Mark operation completed for GetOperationResults to return full results
	_ = dc.CompleteOperation(ctx, op.ID)

	results, err := dc.GetOperationResults(ctx, op.ID)
	require.NoError(t, err)
	assert.NotNil(t, results)
	assert.Equal(t, op.ID, results["operation_id"])
}
