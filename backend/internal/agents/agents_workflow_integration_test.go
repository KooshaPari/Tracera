//go:build integration

package agents

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.temporal.io/sdk/testsuite"
)

// TestWorkflowIntegration_AgentCoordinatorWorkflow tests the full agent coordinator workflow
func TestWorkflowIntegration_AgentCoordinatorWorkflow(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	// Register activities
	env.RegisterActivity((*AgentCoordinator)(nil).ExecuteTask)
	env.RegisterActivity((*AgentCoordinator)(nil).MonitorProgress)

	// Setup test data
	taskID := uuid.New().String()
	ctx := context.Background()

	// Execute workflow
	env.ExecuteWorkflow(AgentCoordinatorWorkflow, ctx, taskID)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())

	var result string
	err := env.GetWorkflowResult(&result)
	assert.NoError(t, err)
	assert.NotEmpty(t, result)
}

// TestWorkflowIntegration_AgentDistributedCoordination tests distributed agent coordination
func TestWorkflowIntegration_AgentDistributedCoordination(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	// Register distributed coordination activities
	env.RegisterActivity((*DistributedCoordinator)(nil).AssignTask)
	env.RegisterActivity((*DistributedCoordinator)(nil).MonitorAgents)
	env.RegisterActivity((*DistributedCoordinator)(nil).CollectResults)

	ctx := context.Background()
	taskIDs := []string{uuid.New().String(), uuid.New().String(), uuid.New().String()}

	env.ExecuteWorkflow(DistributedCoordinationWorkflow, ctx, taskIDs)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

// TestWorkflowIntegration_AgentProtocolHandshake tests agent protocol handshake workflow
func TestWorkflowIntegration_AgentProtocolHandshake(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.RegisterActivity((*ProtocolHandler)(nil).InitiateHandshake)
	env.RegisterActivity((*ProtocolHandler)(nil).ExchangeCapabilities)
	env.RegisterActivity((*ProtocolHandler)(nil).EstablishConnection)

	agentID := uuid.New().String()
	ctx := context.Background()

	env.ExecuteWorkflow(AgentHandshakeWorkflow, ctx, agentID)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

// TestWorkflowIntegration_AgentQueueProcessing tests queue-based agent task processing
func TestWorkflowIntegration_AgentQueueProcessing(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.RegisterActivity((*QueueProcessor)(nil).DequeueTask)
	env.RegisterActivity((*QueueProcessor)(nil).ProcessTask)
	env.RegisterActivity((*QueueProcessor)(nil).UpdateTaskStatus)

	ctx := context.Background()
	queueName := "agent-tasks"

	env.ExecuteWorkflow(QueueProcessingWorkflow, ctx, queueName)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

// TestWorkflowIntegration_AgentCoordinatorWithRetry tests coordinator with retry logic
func TestWorkflowIntegration_AgentCoordinatorWithRetry(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	// Simulate failure then success
	attemptCount := 0
	env.OnActivity((*AgentCoordinator)(nil).ExecuteTask, nil, nil).Return(
		func(ctx context.Context, taskID string) (string, error) {
			attemptCount++
			if attemptCount < 3 {
				return "", assert.AnError
			}
			return "success", nil
		},
	)

	env.RegisterActivity((*AgentCoordinator)(nil).MonitorProgress)

	taskID := uuid.New().String()
	ctx := context.Background()

	env.ExecuteWorkflow(AgentCoordinatorWorkflow, ctx, taskID)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
	assert.Equal(t, 3, attemptCount)
}

// TestWorkflowIntegration_AgentCoordinatorTimeout tests coordinator timeout handling
func TestWorkflowIntegration_AgentCoordinatorTimeout(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	// Simulate long-running task
	env.OnActivity((*AgentCoordinator)(nil).ExecuteTask, nil, nil).Return(
		func(ctx context.Context, taskID string) (string, error) {
			time.Sleep(30 * time.Second) // Exceeds timeout
			return "completed", nil
		},
	)

	env.SetWorkflowRunTimeout(5 * time.Second)

	taskID := uuid.New().String()
	ctx := context.Background()

	env.ExecuteWorkflow(AgentCoordinatorWorkflow, ctx, taskID)

	require.True(t, env.IsWorkflowCompleted())
	assert.Error(t, env.GetWorkflowError())
}

// TestWorkflowIntegration_MultiAgentParallelExecution tests parallel agent execution
func TestWorkflowIntegration_MultiAgentParallelExecution(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	completedAgents := make(map[string]bool)
	env.OnActivity((*AgentCoordinator)(nil).ExecuteTask, nil, nil).Return(
		func(ctx context.Context, taskID string) (string, error) {
			completedAgents[taskID] = true
			return "completed", nil
		},
	)

	taskIDs := []string{
		uuid.New().String(),
		uuid.New().String(),
		uuid.New().String(),
		uuid.New().String(),
		uuid.New().String(),
	}

	ctx := context.Background()
	env.ExecuteWorkflow(ParallelAgentExecutionWorkflow, ctx, taskIDs)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
	assert.Equal(t, len(taskIDs), len(completedAgents))
}

// TestWorkflowIntegration_AgentStateTransitions tests agent state machine workflow
func TestWorkflowIntegration_AgentStateTransitions(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	stateTransitions := []string{}
	env.OnActivity((*AgentCoordinator)(nil).TransitionState, nil, nil).Return(
		func(ctx context.Context, from, to string) error {
			stateTransitions = append(stateTransitions, from+"->"+to)
			return nil
		},
	)

	agentID := uuid.New().String()
	ctx := context.Background()

	env.ExecuteWorkflow(AgentStateTransitionWorkflow, ctx, agentID)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
	assert.GreaterOrEqual(t, len(stateTransitions), 3)
}

// TestWorkflowIntegration_AgentCheckpointing tests agent checkpoint/resume workflow
func TestWorkflowIntegration_AgentCheckpointing(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.RegisterActivity((*AgentCoordinator)(nil).SaveCheckpoint)
	env.RegisterActivity((*AgentCoordinator)(nil).RestoreCheckpoint)
	env.RegisterActivity((*AgentCoordinator)(nil).ExecuteTask)

	agentID := uuid.New().String()
	checkpointID := uuid.New().String()
	ctx := context.Background()

	env.ExecuteWorkflow(AgentCheckpointWorkflow, ctx, agentID, checkpointID)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

// TestWorkflowIntegration_AgentErrorRecovery tests error recovery workflow
func TestWorkflowIntegration_AgentErrorRecovery(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	failureCount := 0
	env.OnActivity((*AgentCoordinator)(nil).ExecuteTask, nil, nil).Return(
		func(ctx context.Context, taskID string) (string, error) {
			failureCount++
			if failureCount == 1 {
				return "", assert.AnError // First attempt fails
			}
			return "recovered", nil // Second attempt succeeds
		},
	)

	env.RegisterActivity((*AgentCoordinator)(nil).HandleError)
	env.RegisterActivity((*AgentCoordinator)(nil).RecoverFromError)

	taskID := uuid.New().String()
	ctx := context.Background()

	env.ExecuteWorkflow(AgentErrorRecoveryWorkflow, ctx, taskID)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
	assert.Equal(t, 2, failureCount)
}

// TestWorkflowIntegration_AgentResourceAllocation tests resource allocation workflow
func TestWorkflowIntegration_AgentResourceAllocation(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.RegisterActivity((*ResourceAllocator)(nil).CheckAvailability)
	env.RegisterActivity((*ResourceAllocator)(nil).AllocateResources)
	env.RegisterActivity((*ResourceAllocator)(nil).ReleaseResources)

	agentID := uuid.New().String()
	resources := map[string]int{"cpu": 2, "memory": 4096}
	ctx := context.Background()

	env.ExecuteWorkflow(ResourceAllocationWorkflow, ctx, agentID, resources)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

// TestWorkflowIntegration_AgentBatchProcessing tests batch task processing
func TestWorkflowIntegration_AgentBatchProcessing(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	processedCount := 0
	env.OnActivity((*AgentCoordinator)(nil).ProcessBatch, nil, nil).Return(
		func(ctx context.Context, batchID string, tasks []string) (int, error) {
			processedCount = len(tasks)
			return processedCount, nil
		},
	)

	batchID := uuid.New().String()
	tasks := []string{
		uuid.New().String(),
		uuid.New().String(),
		uuid.New().String(),
		uuid.New().String(),
		uuid.New().String(),
	}
	ctx := context.Background()

	env.ExecuteWorkflow(BatchProcessingWorkflow, ctx, batchID, tasks)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
	assert.Equal(t, 5, processedCount)
}
