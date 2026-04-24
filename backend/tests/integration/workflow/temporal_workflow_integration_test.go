//go:build integration

package workflow

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.temporal.io/sdk/testsuite"
	"go.temporal.io/sdk/workflow"
)

// TEST 1-15: Temporal Workflow Integration Tests

func TestTemporalWorkflow_BasicExecution(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.ExecuteWorkflow(SimpleTaskWorkflow, "test-task")

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())

	var result string
	err := env.GetWorkflowResult(&result)
	assert.NoError(t, err)
	assert.Equal(t, "completed", result)
}

func TestTemporalWorkflow_ActivityRetry(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	attemptCount := 0
	env.OnActivity(ProcessTaskActivity, nil, nil).Return(
		func(ctx context.Context, taskID string) (string, error) {
			attemptCount++
			if attemptCount < 3 {
				return "", fmt.Errorf("temporary failure")
			}
			return "success after retries", nil
		},
	)

	env.ExecuteWorkflow(RetryableWorkflow, "task-1")

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
	assert.Equal(t, 3, attemptCount)
}

func TestTemporalWorkflow_ParallelActivities(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	completedTasks := make(map[string]bool)
	env.OnActivity(ProcessTaskActivity, nil, nil).Return(
		func(ctx context.Context, taskID string) (string, error) {
			completedTasks[taskID] = true
			return "completed", nil
		},
	)

	taskIDs := []string{"task-1", "task-2", "task-3", "task-4", "task-5"}
	env.ExecuteWorkflow(ParallelTasksWorkflow, taskIDs)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
	assert.Equal(t, 5, len(completedTasks))
}

func TestTemporalWorkflow_ChildWorkflow(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.RegisterWorkflow(ChildTaskWorkflow)

	env.ExecuteWorkflow(ParentTaskWorkflow, "parent-task")

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())

	var result string
	err := env.GetWorkflowResult(&result)
	assert.NoError(t, err)
	assert.Contains(t, result, "parent completed")
}

func TestTemporalWorkflow_SignalHandling(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.RegisterDelayedCallback(func() {
		env.SignalWorkflow("update-signal", "signal-data")
	}, time.Second)

	env.ExecuteWorkflow(SignalHandlingWorkflow)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

func TestTemporalWorkflow_QueryHandling(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.ExecuteWorkflow(QueryableWorkflow, "test-data")

	// Query workflow state
	value, err := env.QueryWorkflow("getState")
	assert.NoError(t, err)
	assert.NotNil(t, value)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

func TestTemporalWorkflow_Timer(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.ExecuteWorkflow(TimerWorkflow, 5*time.Second)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())

	var duration time.Duration
	err := env.GetWorkflowResult(&duration)
	assert.NoError(t, err)
	assert.Equal(t, 5*time.Second, duration)
}

func TestTemporalWorkflow_CancellationHandling(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.RegisterDelayedCallback(func() {
		env.CancelWorkflow()
	}, 2*time.Second)

	env.ExecuteWorkflow(CancellableWorkflow)

	require.True(t, env.IsWorkflowCompleted())
	assert.Error(t, env.GetWorkflowError())
	assert.Contains(t, env.GetWorkflowError().Error(), "canceled")
}

func TestTemporalWorkflow_ContinueAsNew(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	iterationCount := 0
	env.OnWorkflow(ContinueAsNewWorkflow, nil, nil).Return(
		func(ctx workflow.Context, iteration int) (string, error) {
			iterationCount++
			if iteration < 3 {
				return "", workflow.NewContinueAsNewError(ctx, ContinueAsNewWorkflow, iteration+1)
			}
			return "completed after continuations", nil
		},
	)

	env.ExecuteWorkflow(ContinueAsNewWorkflow, 0)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

func TestTemporalWorkflow_SideEffect(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.ExecuteWorkflow(SideEffectWorkflow)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())

	var result string
	err := env.GetWorkflowResult(&result)
	assert.NoError(t, err)
	assert.NotEmpty(t, result)
}

func TestTemporalWorkflow_SearchAttributes(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.ExecuteWorkflow(SearchAttributesWorkflow, map[string]interface{}{
		"CustomKeyword": "test-value",
		"CustomInt":     42,
	})

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

func TestTemporalWorkflow_LocalActivity(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.OnActivity(LocalProcessActivity, nil, nil).Return("local-result", nil)

	env.ExecuteWorkflow(LocalActivityWorkflow, "test-input")

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())

	var result string
	err := env.GetWorkflowResult(&result)
	assert.NoError(t, err)
	assert.Equal(t, "local-result", result)
}

func TestTemporalWorkflow_Selector(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.RegisterDelayedCallback(func() {
		env.SignalWorkflow("signal-a", "data-a")
	}, 1*time.Second)

	env.RegisterDelayedCallback(func() {
		env.SignalWorkflow("signal-b", "data-b")
	}, 2*time.Second)

	env.ExecuteWorkflow(SelectorWorkflow)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

func TestTemporalWorkflow_ActivityHeartbeat(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	heartbeatCount := 0
	env.OnActivity(HeartbeatingActivity, nil, nil).Return(
		func(ctx context.Context, duration time.Duration) (string, error) {
			// Simulate heartbeats
			for i := 0; i < 5; i++ {
				heartbeatCount++
				time.Sleep(duration / 5)
			}
			return "completed", nil
		},
	)

	env.ExecuteWorkflow(HeartbeatWorkflow, 5*time.Second)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
	assert.Equal(t, 5, heartbeatCount)
}

func TestTemporalWorkflow_ErrorPropagation(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.OnActivity(FailingActivity, nil, nil).Return("", fmt.Errorf("activity failed"))

	env.ExecuteWorkflow(ErrorHandlingWorkflow)

	require.True(t, env.IsWorkflowCompleted())
	assert.Error(t, env.GetWorkflowError())
	assert.Contains(t, env.GetWorkflowError().Error(), "activity failed")
}

// TEST 16-30: Workflow Coordination Tests

func TestWorkflowCoordination_DatabaseTransaction(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.RegisterActivity(BeginTransactionActivity)
	env.RegisterActivity(ExecuteDatabaseOperationActivity)
	env.RegisterActivity(CommitTransactionActivity)

	env.ExecuteWorkflow(DatabaseTransactionWorkflow, "create-items")

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

func TestWorkflowCoordination_RollbackOnFailure(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.OnActivity(BeginTransactionActivity, nil, nil).Return("tx-123", nil)
	env.OnActivity(ExecuteDatabaseOperationActivity, nil, nil).Return("", fmt.Errorf("operation failed"))
	env.RegisterActivity(RollbackTransactionActivity)

	env.ExecuteWorkflow(DatabaseTransactionWorkflow, "failing-operation")

	require.True(t, env.IsWorkflowCompleted())
	// Should complete despite error (rollback handled)
}

func TestWorkflowCoordination_SagaPattern(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.RegisterActivity(ReserveInventoryActivity)
	env.RegisterActivity(ProcessPaymentActivity)
	env.RegisterActivity(ShipOrderActivity)
	env.RegisterActivity(CompensateInventoryActivity)
	env.RegisterActivity(RefundPaymentActivity)

	env.ExecuteWorkflow(SagaWorkflow, "order-123")

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

func TestWorkflowCoordination_SagaCompensation(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.OnActivity(ReserveInventoryActivity, nil, nil).Return("reserved", nil)
	env.OnActivity(ProcessPaymentActivity, nil, nil).Return("paid", nil)
	env.OnActivity(ShipOrderActivity, nil, nil).Return("", fmt.Errorf("shipping failed"))
	env.RegisterActivity(CompensateInventoryActivity)
	env.RegisterActivity(RefundPaymentActivity)

	env.ExecuteWorkflow(SagaWorkflow, "order-456")

	require.True(t, env.IsWorkflowCompleted())
	// Compensating actions should have been triggered
}

func TestWorkflowCoordination_DistributedLock(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.RegisterActivity(AcquireLockActivity)
	env.RegisterActivity(PerformCriticalOperationActivity)
	env.RegisterActivity(ReleaseLockActivity)

	env.ExecuteWorkflow(DistributedLockWorkflow, "resource-123")

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

func TestWorkflowCoordination_MultiStepProcess(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.RegisterActivity(Step1Activity)
	env.RegisterActivity(Step2Activity)
	env.RegisterActivity(Step3Activity)
	env.RegisterActivity(FinalizeActivity)

	env.ExecuteWorkflow(MultiStepProcessWorkflow, "process-data")

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())

	var result string
	err := env.GetWorkflowResult(&result)
	assert.NoError(t, err)
	assert.Equal(t, "finalized", result)
}

func TestWorkflowCoordination_ConditionalBranching(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.OnActivity(EvaluateConditionActivity, nil, nil).Return(true, nil)
	env.RegisterActivity(BranchAActivity)
	env.RegisterActivity(BranchBActivity)

	env.ExecuteWorkflow(ConditionalWorkflow, "test-condition")

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

func TestWorkflowCoordination_LoopProcessing(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	processedItems := 0
	env.OnActivity(ProcessItemActivity, nil, nil).Return(
		func(ctx context.Context, item interface{}) (string, error) {
			processedItems++
			return "processed", nil
		},
	)

	items := []interface{}{1, 2, 3, 4, 5}
	env.ExecuteWorkflow(LoopProcessingWorkflow, items)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
	assert.Equal(t, 5, processedItems)
}

func TestWorkflowCoordination_FanOutFanIn(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	completedTasks := make(map[int]bool)
	env.OnActivity(ParallelTaskActivity, nil, nil).Return(
		func(ctx context.Context, taskNum int) (string, error) {
			completedTasks[taskNum] = true
			return fmt.Sprintf("result-%d", taskNum), nil
		},
	)

	env.RegisterActivity(AggregateResultsActivity)

	env.ExecuteWorkflow(FanOutFanInWorkflow, 10)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
	assert.Equal(t, 10, len(completedTasks))
}

func TestWorkflowCoordination_DataPipeline(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.RegisterActivity(ExtractDataActivity)
	env.RegisterActivity(TransformDataActivity)
	env.RegisterActivity(LoadDataActivity)

	env.ExecuteWorkflow(ETLWorkflow, "source-data")

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())

	var result string
	err := env.GetWorkflowResult(&result)
	assert.NoError(t, err)
	assert.Equal(t, "loaded", result)
}

func TestWorkflowCoordination_ScheduledTask(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.RegisterActivity(ScheduledTaskActivity)

	env.ExecuteWorkflow(ScheduledTaskWorkflow, 5*time.Minute)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

func TestWorkflowCoordination_RateLimiting(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	executionTimes := []time.Time{}
	env.OnActivity(RateLimitedActivity, nil, nil).Return(
		func(ctx context.Context) (string, error) {
			executionTimes = append(executionTimes, time.Now())
			return "executed", nil
		},
	)

	env.ExecuteWorkflow(RateLimitedWorkflow, 5, 1*time.Second) // 5 tasks, 1 per second

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
	assert.Equal(t, 5, len(executionTimes))
}

func TestWorkflowCoordination_DynamicWorkflow(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	env.OnActivity(DetermineTasksActivity, nil, nil).Return(
		[]string{"task-1", "task-2", "task-3"}, nil,
	)
	env.RegisterActivity(DynamicTaskActivity)

	env.ExecuteWorkflow(DynamicWorkflow)

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
}

func TestWorkflowCoordination_StateManagement(t *testing.T) {
	testSuite := &testsuite.WorkflowTestSuite{}
	env := testSuite.NewTestWorkflowEnvironment()

	states := []string{}
	env.OnActivity(TransitionStateActivity, nil, nil).Return(
		func(ctx context.Context, fromState, toState string) (string, error) {
			states = append(states, toState)
			return toState, nil
		},
	)

	env.ExecuteWorkflow(StateMachineWorkflow, "initial")

	require.True(t, env.IsWorkflowCompleted())
	require.NoError(t, env.GetWorkflowError())
	assert.GreaterOrEqual(t, len(states), 3)
}
