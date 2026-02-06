//go:build !integration && !e2e

package agents

import (
	"encoding/json"
	"sync"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

// ============================================================================
// LOCK TYPE TESTS (8 tests)
// ============================================================================

// TestLockType_Optimistic tests optimistic lock type
func TestLockType_Optimistic(t *testing.T) {
	lockType := LockTypeOptimistic
	assert.Equal(t, LockTypeOptimistic, lockType)
	assert.NotEmpty(t, string(lockType))
}

// TestLockType_Pessimistic tests pessimistic lock type
func TestLockType_Pessimistic(t *testing.T) {
	lockType := LockTypePessimistic
	assert.Equal(t, LockTypePessimistic, lockType)
	assert.NotEmpty(t, string(lockType))
}

// TestConflictResolutionStrategy_LastWriteWins tests strategy
func TestConflictResolutionStrategy_LastWriteWins(t *testing.T) {
	strategy := ResolutionLastWriteWins
	assert.Equal(t, ResolutionLastWriteWins, strategy)
}

// TestConflictResolutionStrategy_AgentPriority tests strategy
func TestConflictResolutionStrategy_AgentPriority(t *testing.T) {
	strategy := ResolutionAgentPriority
	assert.Equal(t, ResolutionAgentPriority, strategy)
}

// TestConflictResolutionStrategy_Manual tests strategy
func TestConflictResolutionStrategy_Manual(t *testing.T) {
	strategy := ResolutionManual
	assert.Equal(t, ResolutionManual, strategy)
}

// TestConflictResolutionStrategy_Merge tests strategy
func TestConflictResolutionStrategy_Merge(t *testing.T) {
	strategy := ResolutionMerge
	assert.Equal(t, ResolutionMerge, strategy)
}

// TestConflictResolutionStrategy_FirstWins tests strategy
func TestConflictResolutionStrategy_FirstWins(t *testing.T) {
	strategy := ResolutionFirstWins
	assert.Equal(t, ResolutionFirstWins, strategy)
}

// TestResolutionStatus_Values tests status constants
func TestResolutionStatus_Values(t *testing.T) {
	statuses := []string{
		resolutionStatusPending,
		resolutionStatusResolved,
		resolutionStatusFailed,
	}

	for _, status := range statuses {
		assert.NotEmpty(t, status)
	}
}

// ============================================================================
// AGENT LOCK TESTS (10 tests)
// ============================================================================

// TestAgentLock_Creation creates agent lock
func TestAgentLock_Creation(t *testing.T) {
	lock := &AgentLock{
		ID:       uuid.New().String(),
		ItemID:   "item1",
		ItemType: "task",
		AgentID:  "agent1",
		LockType: LockTypePessimistic,
		Version:  1,
		ExpireAt: time.Now().Add(5 * time.Minute),
	}

	assert.NotEmpty(t, lock.ID)
	assert.Equal(t, "item1", lock.ItemID)
	assert.Equal(t, "agent1", lock.AgentID)
	assert.Equal(t, int64(1), lock.Version)
}

// TestAgentLock_WithMetadata tests lock with metadata
func TestAgentLock_WithMetadata(t *testing.T) {
	metadata := JSONMap{
		"reason":      "processing",
		"region":      "us-east-1",
		"priority":    3,
		"retryCount":  0,
	}

	lock := &AgentLock{
		ID:       uuid.New().String(),
		ItemID:   "item1",
		AgentID:  "agent1",
		Metadata: metadata,
	}

	assert.Equal(t, "processing", lock.Metadata["reason"])
	assert.Equal(t, "us-east-1", lock.Metadata["region"])
}

// TestAgentLock_Expiration tests lock expiration time
func TestAgentLock_Expiration(t *testing.T) {
	now := time.Now()
	expireAt := now.Add(10 * time.Second)

	lock := &AgentLock{
		ID:       uuid.New().String(),
		ItemID:   "item1",
		AgentID:  "agent1",
		ExpireAt: expireAt,
	}

	assert.True(t, lock.ExpireAt.After(now))
}

// TestAgentLock_IsExpired checks if lock is expired
func TestAgentLock_IsExpired(t *testing.T) {
	lock := &AgentLock{
		ID:       uuid.New().String(),
		ItemID:   "item1",
		AgentID:  "agent1",
		ExpireAt: time.Now().Add(-1 * time.Second), // Already expired
	}

	assert.True(t, lock.ExpireAt.Before(time.Now()))
}

// TestAgentLock_IsNotExpired checks if lock is not expired
func TestAgentLock_IsNotExpired(t *testing.T) {
	lock := &AgentLock{
		ID:       uuid.New().String(),
		ItemID:   "item1",
		AgentID:  "agent1",
		ExpireAt: time.Now().Add(5 * time.Minute),
	}

	assert.True(t, lock.ExpireAt.After(time.Now()))
}

// TestAgentLock_VersionIncrement increments version
func TestAgentLock_VersionIncrement(t *testing.T) {
	lock := &AgentLock{
		ID:      uuid.New().String(),
		ItemID:  "item1",
		AgentID: "agent1",
		Version: 1,
	}

	lock.Version++
	assert.Equal(t, int64(2), lock.Version)
}

// TestAgentLock_MultipleAgents different agents can have locks
func TestAgentLock_MultipleAgents(t *testing.T) {
	locks := []*AgentLock{
		{
			ID:      uuid.New().String(),
			ItemID:  "item1",
			AgentID: "agent1",
		},
		{
			ID:      uuid.New().String(),
			ItemID:  "item2",
			AgentID: "agent2",
		},
	}

	assert.Equal(t, 2, len(locks))
	assert.Equal(t, "agent1", locks[0].AgentID)
	assert.Equal(t, "agent2", locks[1].AgentID)
}

// TestAgentLock_CreatedAt timestamp
func TestAgentLock_CreatedAt(t *testing.T) {
	now := time.Now()
	lock := &AgentLock{
		ID:        uuid.New().String(),
		ItemID:    "item1",
		AgentID:   "agent1",
		CreatedAt: now,
	}

	assert.Equal(t, now.Truncate(time.Second), lock.CreatedAt.Truncate(time.Second))
}

// ============================================================================
// AGENT TEAM TESTS (9 tests)
// ============================================================================

// TestAgentTeam_Creation creates agent team
func TestAgentTeam_Creation(t *testing.T) {
	team := &AgentTeam{
		ID:        uuid.New().String(),
		ProjectID: "p1",
		Name:      "Team A",
	}

	assert.NotEmpty(t, team.ID)
	assert.Equal(t, "Team A", team.Name)
	assert.Equal(t, "p1", team.ProjectID)
}

// TestAgentTeam_WithDescription includes description
func TestAgentTeam_WithDescription(t *testing.T) {
	team := &AgentTeam{
		ID:          uuid.New().String(),
		ProjectID:   "p1",
		Name:        "Team A",
		Description: "Processing agents",
	}

	assert.Equal(t, "Processing agents", team.Description)
}

// TestAgentTeam_WithRoles includes roles
func TestAgentTeam_WithRoles(t *testing.T) {
	roles := make(map[string]TeamRole)
	roles["leader"] = TeamRole{
		Name:        "leader",
		Permissions: []string{"assign", "monitor"},
	}

	team := &AgentTeam{
		ID:        uuid.New().String(),
		ProjectID: "p1",
		Name:      "Team A",
		Roles:     roles,
	}

	assert.Equal(t, 1, len(team.Roles))
	assert.Equal(t, "leader", team.Roles["leader"].Name)
}

// TestAgentTeam_WithMetadata includes metadata
func TestAgentTeam_WithMetadata(t *testing.T) {
	metadata := JSONMap{
		"region":    "us-east-1",
		"tier":      "premium",
		"maxAgents": 10,
	}

	team := &AgentTeam{
		ID:        uuid.New().String(),
		ProjectID: "p1",
		Name:      "Team A",
		Metadata:  metadata,
	}

	assert.Equal(t, "us-east-1", team.Metadata["region"])
	assert.Equal(t, 10, team.Metadata["maxAgents"])
}

// TestAgentTeam_Timestamps sets creation and update times
func TestAgentTeam_Timestamps(t *testing.T) {
	now := time.Now()
	team := &AgentTeam{
		ID:        uuid.New().String(),
		ProjectID: "p1",
		Name:      "Team A",
		CreatedAt: now,
		UpdatedAt: now,
	}

	assert.Equal(t, now.Truncate(time.Second), team.CreatedAt.Truncate(time.Second))
}

// TestAgentTeam_MultipleTeams creates multiple teams
func TestAgentTeam_MultipleTeams(t *testing.T) {
	teams := []*AgentTeam{
		{ID: uuid.New().String(), ProjectID: "p1", Name: "Team 1"},
		{ID: uuid.New().String(), ProjectID: "p1", Name: "Team 2"},
		{ID: uuid.New().String(), ProjectID: "p2", Name: "Team 3"},
	}

	assert.Equal(t, 3, len(teams))
	count := 0
	for _, team := range teams {
		if team.ProjectID == "p1" {
			count++
		}
	}
	assert.Equal(t, 2, count)
}

// TestAgentTeam_EmptyRoles initializes with empty roles
func TestAgentTeam_EmptyRoles(t *testing.T) {
	team := &AgentTeam{
		ID:        uuid.New().String(),
		ProjectID: "p1",
		Name:      "Team A",
		Roles:     make(map[string]TeamRole),
	}

	assert.Equal(t, 0, len(team.Roles))
}

// TestAgentTeam_Role represents team role
func TestAgentTeam_Role(t *testing.T) {
	role := TeamRole{
		Name:        "reviewer",
		Permissions: []string{"review", "approve"},
	}

	assert.Equal(t, "reviewer", role.Name)
	assert.Equal(t, 2, len(role.Permissions))
}

// ============================================================================
// JSON MAP TESTS (8 tests)
// ============================================================================

// TestJSONMap_Creation creates JSON map
func TestJSONMap_Creation(t *testing.T) {
	m := JSONMap{
		"key1": "value1",
		"key2": 42,
		"key3": true,
	}

	assert.Equal(t, "value1", m["key1"])
	assert.Equal(t, 42, m["key2"])
	assert.Equal(t, true, m["key3"])
}

// TestJSONMap_Empty creates empty map
func TestJSONMap_Empty(t *testing.T) {
	m := make(JSONMap)
	assert.Equal(t, 0, len(m))
}

// TestJSONMap_Nested creates nested structures
func TestJSONMap_Nested(t *testing.T) {
	nested := JSONMap{
		"parent": JSONMap{
			"child": "value",
		},
	}

	parent := nested["parent"].(JSONMap)
	assert.Equal(t, "value", parent["child"])
}

// TestJSONMap_Value converts to driver value
func TestJSONMap_Value(t *testing.T) {
	m := JSONMap{
		"key": "value",
	}

	val, err := m.Value()
	assert.NoError(t, err)
	assert.NotNil(t, val)

	// Should be JSON bytes
	data, ok := val.([]byte)
	assert.True(t, ok)
	assert.NotEmpty(t, data)
}

// TestJSONMap_Scan parses from value
func TestJSONMap_Scan(t *testing.T) {
	m := &JSONMap{}
	jsonData := []byte(`{"key":"value"}`)

	err := m.Scan(jsonData)
	assert.NoError(t, err)
	assert.Equal(t, "value", (*m)["key"])
}

// TestJSONMap_ScanNil handles nil value
func TestJSONMap_ScanNil(t *testing.T) {
	m := &JSONMap{}
	err := m.Scan(nil)
	assert.NoError(t, err)
	assert.Equal(t, 0, len(*m))
}

// TestJSONMap_RoundTrip encodes and decodes
func TestJSONMap_RoundTrip(t *testing.T) {
	original := JSONMap{
		"string": "hello",
		"number": 123,
		"bool":   true,
	}

	// Encode
	val, _ := original.Value()
	data, _ := val.([]byte)

	// Decode
	restored := &JSONMap{}
	restored.Scan(data)

	assert.Equal(t, "hello", (*restored)["string"])
	assert.Equal(t, float64(123), (*restored)["number"]) // JSON numbers are floats
	assert.Equal(t, true, (*restored)["bool"])
}

// TestJSONMap_JSONMarshaling tests JSON marshaling
func TestJSONMap_JSONMarshaling(t *testing.T) {
	m := JSONMap{
		"test": "data",
	}

	data, err := json.Marshal(m)
	assert.NoError(t, err)
	assert.Contains(t, string(data), "test")
}

// ============================================================================
// DISTRIBUTED OPERATION TESTS (10 tests)
// ============================================================================

// TestDistributedOperation_Creation creates distributed operation
func TestDistributedOperation_Creation(t *testing.T) {
	op := &DistributedOperation{
		ID:        uuid.New().String(),
		ProjectID: "p1",
		Type:      "batch_update",
		Status:    "pending",
	}

	assert.NotEmpty(t, op.ID)
	assert.Equal(t, "p1", op.ProjectID)
	assert.Equal(t, "batch_update", op.Type)
}

// TestDistributedOperation_WithParticipants sets participants
func TestDistributedOperation_WithParticipants(t *testing.T) {
	op := &DistributedOperation{
		ID:             uuid.New().String(),
		ProjectID:      "p1",
		Type:           "batch_update",
		ParticipantIDs: []string{"agent1", "agent2", "agent3"},
	}

	assert.Equal(t, 3, len(op.ParticipantIDs))
	assert.Equal(t, "agent1", op.ParticipantIDs[0])
}

// TestDistributedOperation_WithCoordinator sets coordinator
func TestDistributedOperation_WithCoordinator(t *testing.T) {
	op := &DistributedOperation{
		ID:            uuid.New().String(),
		ProjectID:     "p1",
		Type:          "batch_update",
		CoordinatorID: "coord1",
	}

	assert.Equal(t, "coord1", op.CoordinatorID)
}

// TestDistributedOperation_WithTargetItems sets items
func TestDistributedOperation_WithTargetItems(t *testing.T) {
	op := &DistributedOperation{
		ID:          uuid.New().String(),
		ProjectID:   "p1",
		Type:        "batch_update",
		TargetItems: []string{"item1", "item2", "item3"},
	}

	assert.Equal(t, 3, len(op.TargetItems))
}

// TestDistributedOperation_WithOperationData sets data
func TestDistributedOperation_WithOperationData(t *testing.T) {
	data := JSONMap{
		"version": 2,
		"action":  "update",
	}

	op := &DistributedOperation{
		ID:            uuid.New().String(),
		ProjectID:     "p1",
		Type:          "batch_update",
		OperationData: data,
	}

	assert.Equal(t, 2, op.OperationData["version"])
}

// TestDistributedOperation_StartedAt sets start time
func TestDistributedOperation_StartedAt(t *testing.T) {
	now := time.Now()
	op := &DistributedOperation{
		ID:        uuid.New().String(),
		ProjectID: "p1",
		Type:      "batch_update",
		StartedAt: &now,
	}

	assert.NotNil(t, op.StartedAt)
	assert.True(t, op.StartedAt.Before(time.Now().Add(1 * time.Second)))
}

// TestDistributedOperation_CompletedAt sets end time
func TestDistributedOperation_CompletedAt(t *testing.T) {
	now := time.Now()
	op := &DistributedOperation{
		ID:          uuid.New().String(),
		ProjectID:   "p1",
		Type:        "batch_update",
		CompletedAt: &now,
	}

	assert.NotNil(t, op.CompletedAt)
}

// TestDistributedOperation_StatusProgression tests status changes
func TestDistributedOperation_StatusProgression(t *testing.T) {
	op := &DistributedOperation{
		ID:        uuid.New().String(),
		ProjectID: "p1",
		Type:      "batch_update",
	}

	statuses := []string{"pending", "in_progress", "completed"}
	for _, status := range statuses {
		op.Status = status
		assert.Equal(t, status, op.Status)
	}
}

// TestDistributedOperation_Timestamps sets creation and update
func TestDistributedOperation_Timestamps(t *testing.T) {
	now := time.Now()
	op := &DistributedOperation{
		ID:        uuid.New().String(),
		ProjectID: "p1",
		Type:      "batch_update",
		CreatedAt: now,
		UpdatedAt: now,
	}

	assert.Equal(t, now.Truncate(time.Second), op.CreatedAt.Truncate(time.Second))
}

// ============================================================================
// OPERATION PARTICIPANT TESTS (10 tests)
// ============================================================================

// TestOperationParticipant_Creation creates participant
func TestOperationParticipant_Creation(t *testing.T) {
	p := &OperationParticipant{
		ID:          uuid.New().String(),
		OperationID: uuid.New().String(),
		AgentID:     "agent1",
		Status:      "ready",
	}

	assert.NotEmpty(t, p.ID)
	assert.Equal(t, "agent1", p.AgentID)
	assert.Equal(t, "ready", p.Status)
}

// TestOperationParticipant_WithAssignedItems sets items
func TestOperationParticipant_WithAssignedItems(t *testing.T) {
	p := &OperationParticipant{
		ID:            uuid.New().String(),
		OperationID:   uuid.New().String(),
		AgentID:       "agent1",
		Status:        "working",
		AssignedItems: []string{"item1", "item2"},
	}

	assert.Equal(t, 2, len(p.AssignedItems))
}

// TestOperationParticipant_WithResult sets result
func TestOperationParticipant_WithResult(t *testing.T) {
	result := map[string]interface{}{
		"processed": 10,
		"success":   true,
	}

	p := &OperationParticipant{
		ID:            uuid.New().String(),
		OperationID:   uuid.New().String(),
		AgentID:       "agent1",
		Status:        "completed",
		Result:        result,
	}

	assert.Equal(t, 10, p.Result["processed"])
	assert.Equal(t, true, p.Result["success"])
}

// TestOperationParticipant_WithError sets error
func TestOperationParticipant_WithError(t *testing.T) {
	p := &OperationParticipant{
		ID:          uuid.New().String(),
		OperationID: uuid.New().String(),
		AgentID:     "agent1",
		Status:      "failed",
		Error:       "connection timeout",
	}

	assert.Equal(t, "connection timeout", p.Error)
}

// TestOperationParticipant_StatusValues tests statuses
func TestOperationParticipant_StatusValues(t *testing.T) {
	statuses := []string{"ready", "working", "completed", "failed"}

	for _, status := range statuses {
		p := &OperationParticipant{
			ID:          uuid.New().String(),
			OperationID: uuid.New().String(),
			AgentID:     "agent1",
			Status:      status,
		}
		assert.Equal(t, status, p.Status)
	}
}

// TestOperationParticipant_StartedAt sets start time
func TestOperationParticipant_StartedAt(t *testing.T) {
	now := time.Now()
	p := &OperationParticipant{
		ID:          uuid.New().String(),
		OperationID: uuid.New().String(),
		AgentID:     "agent1",
		StartedAt:   &now,
	}

	assert.NotNil(t, p.StartedAt)
}

// TestOperationParticipant_CompletedAt sets end time
func TestOperationParticipant_CompletedAt(t *testing.T) {
	now := time.Now()
	p := &OperationParticipant{
		ID:          uuid.New().String(),
		OperationID: uuid.New().String(),
		AgentID:     "agent1",
		CompletedAt: &now,
	}

	assert.NotNil(t, p.CompletedAt)
}

// TestOperationParticipant_Timestamps sets creation and update
func TestOperationParticipant_Timestamps(t *testing.T) {
	now := time.Now()
	p := &OperationParticipant{
		ID:          uuid.New().String(),
		OperationID: uuid.New().String(),
		AgentID:     "agent1",
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	assert.Equal(t, now.Truncate(time.Second), p.CreatedAt.Truncate(time.Second))
}

// TestOperationParticipant_MultipleParticipants multiple agents
func TestOperationParticipant_MultipleParticipants(t *testing.T) {
	opID := uuid.New().String()
	participants := []*OperationParticipant{
		{ID: uuid.New().String(), OperationID: opID, AgentID: "agent1"},
		{ID: uuid.New().String(), OperationID: opID, AgentID: "agent2"},
		{ID: uuid.New().String(), OperationID: opID, AgentID: "agent3"},
	}

	assert.Equal(t, 3, len(participants))
	for _, p := range participants {
		assert.Equal(t, opID, p.OperationID)
	}
}

// ============================================================================
// COORDINATION CONSTANTS TESTS (3 tests)
// ============================================================================

// TestDistributedOperationStatus_Constants tests status constants
func TestDistributedOperationStatus_Constants(t *testing.T) {
	statuses := []string{
		statusInProgress,
		statusReady,
		statusWorking,
		statusResolved,
	}

	for _, status := range statuses {
		assert.NotEmpty(t, status)
	}
}

// TestDefaultLockCleanupInterval verifies cleanup interval
func TestDefaultLockCleanupInterval(t *testing.T) {
	assert.Equal(t, 30*time.Second, defaultLockCleanupInterval)
}

// TestLockCleanupConcurrency tests concurrent lock operations
func TestLockCleanupConcurrency(t *testing.T) {
	locks := make(map[string]*AgentLock)
	mu := &sync.RWMutex{}

	var wg sync.WaitGroup
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			lock := &AgentLock{
				ID:      uuid.New().String(),
				ItemID:  "item" + string(rune(idx)),
				AgentID: "agent" + string(rune(idx)),
			}
			mu.Lock()
			locks[lock.ID] = lock
			mu.Unlock()
		}(i)
	}

	wg.Wait()
	mu.RLock()
	defer mu.RUnlock()
	assert.Equal(t, 20, len(locks))
}
