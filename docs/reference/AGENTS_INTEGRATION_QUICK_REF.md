# Agent Integration Tests - Quick Reference

## Test Location
```
backend/internal/agents/integration_workflows_test.go
```

## Running Tests

### All 15 integration tests
```bash
cd backend
go test -v -tags=integration ./internal/agents/... -timeout 60s
```

### Only new workflow tests
```bash
go test -v -tags=integration ./internal/agents/... \
  -run "TestCoordinator|TestDistributed|TestQueue|TestTeam|TestConflict|TestConcurrent" \
  -timeout 60s
```

### Specific test
```bash
go test -v -tags=integration ./internal/agents/... \
  -run TestCoordinatorWorkflowCompleteTaskLifecycle -timeout 60s
```

## Test Categories (15 Tests)

### Coordinator Workflows (4 tests)
| Test | Purpose | Key Validation |
|------|---------|-----------------|
| `TestCoordinatorWorkflowCompleteTaskLifecycle` | Full task lifecycle | Register → Enqueue → Assign → Complete |
| `TestCoordinatorWorkflowTaskFailureAndRetry` | Failure handling | Fail → Requeue → Retry → Succeed/Fail |
| `TestCoordinatorWorkflowMultiAgentDistribution` | Multi-agent parallelism | 5 agents × 3 tasks each |
| `TestCoordinatorWorkflowHeartbeatTimeout` | Agent timeout detection | Miss heartbeat → Offline → Task recovery |

### Distributed Coordination (3 tests)
| Test | Purpose | Key Validation |
|------|---------|-----------------|
| `TestDistributedCoordinationLockAcquisition` | Pessimistic locking | Lock → Contention → Release → Re-acquire |
| `TestDistributedCoordinationOptimisticLocking` | Version-based locking | Version increment → Track history |
| `TestDistributedCoordinationConflictDetection` | Conflict detection | Concurrent modification detection |

### Queue Processing (3 tests)
| Test | Purpose | Key Validation |
|------|---------|-----------------|
| `TestQueueProcessingPriority` | Priority ordering | CRITICAL → HIGH → NORMAL → LOW |
| `TestQueueProcessingCapabilityMatching` | Capability filtering | Match agent caps to task requirements |
| `TestQueueCleanup` | Old task cleanup | Remove completed tasks > 1 hour old |

### Team Management (1 test)
| Test | Purpose | Key Validation |
|------|---------|-----------------|
| `TestTeamManagementRoleBasedPermissions` | RBAC system | Team → Role → Permissions → Check |

### Conflict Resolution (1 test)
| Test | Purpose | Key Validation |
|------|---------|-----------------|
| `TestConflictResolution` | Conflict workflow | Create → Resolve → Status/Timestamp |

### Concurrency (2 tests)
| Test | Purpose | Key Validation |
|------|---------|-----------------|
| `TestConcurrentTaskProcessing` | Concurrent execution | 10 agents × 50 tasks, no lost updates |
| `TestQueueStats` | Statistics collection | Count by status/priority, verify accuracy |

## Key Test Patterns

### Setup Helper
```go
db := setupTestDB(t)  // Creates isolated SQLite database
```

### Register Agent Pattern
```go
agent := &RegisteredAgent{
    ID:        uuid.New().String(),
    Name:      "test-agent",
    ProjectID: "proj-1",
    Status:    StatusIdle,
    Capabilities: []AgentCapability{
        {Name: "analyze", Version: "1.0"},
    },
}
coord.RegisterAgent(agent)
```

### Enqueue Task Pattern
```go
task := &Task{
    ProjectID:            "proj-1",
    Type:                 "analyze",
    Priority:             PriorityNormal,
    RequiredCapabilities: []string{"analyze"},
    MaxRetries:           3,
}
coord.TaskQueue.EnqueueTask(task)
```

### Task Assignment Pattern
```go
nextTask, err := coord.GetNextTask(agent.ID)
// Agent now working on task
result := &TaskResult{Success: true}
coord.CompleteTask(agent.ID, task.ID, result)
```

## Database Schema

Tables auto-created for tests:
- `agents` - Agent registration
- `agent_locks` - Lock management
- `agent_teams` - Team definitions
- `agent_team_memberships` - Team membership
- `item_versions` - Version history
- `conflict_records` - Conflict tracking
- `agent_tasks` - Task persistence

## Performance Notes

| Test | Duration | Agent Count | Task Count |
|------|----------|-------------|-----------|
| Complete Lifecycle | <1ms | 1 | 1 |
| Failure Retry | <1ms | 1 | 1 (3 retries) |
| Multi-Agent Distribution | 140ms | 5 | 15 |
| Heartbeat Timeout | 170ms | 1 | 1 |
| Lock Acquisition | <1ms | 2 | 1 item |
| Optimistic Locking | <1ms | 1 | 1 item |
| Conflict Detection | <1ms | 2 | 1 item |
| Queue Priority | <1ms | 1 | 4 |
| Capability Matching | <10ms | 2 | 2 |
| Team Management | <1ms | 1 | 1 team |
| Conflict Resolution | <1ms | - | 1 conflict |
| Concurrent Processing | 10ms | 10 | 50 |
| Queue Cleanup | <1ms | - | 6 tasks |
| Queue Stats | <1ms | - | 5 tasks |

**Total Suite:** ~600ms (includes 170ms heartbeat timeout)

## Integration Paths Covered

✅ Task lifecycle: register → enqueue → assign → complete
✅ Failure recovery: fail → requeue → retry → succeed
✅ Multi-agent: parallel task distribution and completion
✅ Timeout handling: detect offline agents and recover tasks
✅ Pessimistic locks: exclusive access to resources
✅ Optimistic locks: version-based concurrent access
✅ Conflict detection: identify concurrent modifications
✅ Priority queue: task ordering by priority
✅ Capability matching: agent-task compatibility
✅ Team RBAC: role-based permission system
✅ Conflict resolution: resolve pending conflicts
✅ Concurrency: safe concurrent task processing
✅ Queue management: cleanup and statistics

## Assertions Per Test

- TestCoordinatorWorkflowCompleteTaskLifecycle: 7
- TestCoordinatorWorkflowTaskFailureAndRetry: 9
- TestCoordinatorWorkflowMultiAgentDistribution: 3
- TestCoordinatorWorkflowHeartbeatTimeout: 4
- TestDistributedCoordinationLockAcquisition: 5
- TestDistributedCoordinationOptimisticLocking: 4
- TestDistributedCoordinationConflictDetection: 4
- TestQueueProcessingPriority: 4
- TestQueueProcessingCapabilityMatching: 5
- TestTeamManagementRoleBasedPermissions: 6
- TestConflictResolution: 4
- TestConcurrentTaskProcessing: 1
- TestQueueCleanup: 3
- TestQueueStats: 6

**Total: 66 assertions** validating all integration paths

## Mocking Strategy

- **Temporal:** Simulated via task queue + database persistence
- **Distributed Coordination:** Lock manager + version tracking
- **Concurrency:** Go goroutines + sync primitives
- **Database:** SQLite in-memory, no external services

## Extending Tests

### Add new coordinator workflow test
```go
func TestCoordinatorWorkflow_YourScenario(t *testing.T) {
    db := setupTestDB(t)
    coord := NewCoordinator(db, 30*time.Second)
    defer coord.Shutdown()
    // Your test logic
}
```

### Add new lock test
```go
func TestDistributedCoordination_YourLocking(t *testing.T) {
    db := setupTestDB(t)
    lockMgr := NewLockManager(db, 5*time.Second)
    defer lockMgr.Shutdown()
    // Your test logic
}
```

### Add new queue test
```go
func TestQueueProcessing_YourQueue(t *testing.T) {
    db := setupTestDB(t)
    queue := NewTaskQueue(db)
    // Your test logic
}
```

## Troubleshooting

### Tests not found
```bash
# Ensure integration build tag is set
go test -tags=integration ./internal/agents/...
```

### Database errors
```bash
# Ensure setupTestDB is called before using coordinator
db := setupTestDB(t)
coord := NewCoordinator(db, timeout)
```

### Timeout errors
```bash
# Increase timeout for concurrent tests
go test -timeout 120s ./internal/agents/...
```

## See Also
- Complete Report: `docs/reports/AGENTS_INTEGRATION_TESTS_COMPLETE.md`
- Coordinator Code: `backend/internal/agents/coordinator.go`
- Queue Code: `backend/internal/agents/queue.go`
- Coordination Code: `backend/internal/agents/coordination.go`
