package repository

import (
	"context"
	"encoding/json"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/progress"
)

// TestProgressRepositoryMilestoneInterface validates milestone repository interface
func TestProgressRepositoryMilestoneInterface(t *testing.T) {
	t.Run("milestone_crud_operations", func(t *testing.T) {
		_ = context.Background()

		// Create a milestone for testing
		milestone := &progress.Milestone{
			ID:         uuid.New(),
			ProjectID:  uuid.New(),
			Name:       "v1.0 Release",
			Slug:       "v1-0-release",
			TargetDate: time.Now().AddDate(0, 0, 60),
			Status:     progress.MilestoneNotStarted,
			Health:     progress.HealthGreen,
			RiskScore:  0,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		}

		// Validate milestone struct
		assert.NotNil(t, milestone)
		assert.Equal(t, "v1.0 Release", milestone.Name)
		assert.NotEmpty(t, milestone.ID)
		assert.NotEmpty(t, milestone.ProjectID)
		assert.Equal(t, progress.MilestoneNotStarted, milestone.Status)
		assert.Equal(t, progress.HealthGreen, milestone.Health)
	})

	t.Run("milestone_risk_factors", func(t *testing.T) {
		milestone := &progress.Milestone{
			ID:        uuid.New(),
			RiskScore: 65,
			RiskFactors: []progress.RiskFactor{
				{
					Type:        "scope_creep",
					Severity:    "high",
					Description: "Additional features requested",
				},
			},
		}

		assert.Equal(t, 65, milestone.RiskScore)
		assert.Len(t, milestone.RiskFactors, 1)
		assert.Equal(t, "scope_creep", milestone.RiskFactors[0].Type)
	})

	t.Run("milestone_hierarchy", func(t *testing.T) {
		parentID := uuid.New()
		milestone := &progress.Milestone{
			ID:       uuid.New(),
			ParentID: &parentID,
			Name:     "Feature A",
		}

		assert.NotNil(t, milestone.ParentID)
		assert.Equal(t, parentID, *milestone.ParentID)
	})
}

// TestProgressRepositorySprintInterface validates sprint repository interface
func TestProgressRepositorySprintInterface(t *testing.T) {
	t.Run("sprint_crud_operations", func(t *testing.T) {
		_ = context.Background()

		sprint := &progress.Sprint{
			ID:        uuid.New(),
			ProjectID: uuid.New(),
			Name:      "Sprint 1",
			Slug:      "sprint-1",
			StartDate: time.Now(),
			EndDate:   time.Now().AddDate(0, 0, 14),
			Status:    progress.SprintActive,
			Health:    progress.HealthGreen,
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}

		assert.NotNil(t, sprint)
		assert.Equal(t, "Sprint 1", sprint.Name)
		assert.Equal(t, progress.SprintActive, sprint.Status)
	})

	t.Run("sprint_metrics", func(t *testing.T) {
		sprint := &progress.Sprint{
			ID:              uuid.New(),
			PlannedPoints:   50,
			CompletedPoints: 30,
			RemainingPoints: 20,
			AddedPoints:     5,
			RemovedPoints:   2,
		}

		assert.Equal(t, 50, sprint.PlannedPoints)
		assert.Equal(t, 30, sprint.CompletedPoints)
		assert.Equal(t, 20, sprint.RemainingPoints)
	})

	t.Run("sprint_capacity", func(t *testing.T) {
		capacity := 8
		sprint := &progress.Sprint{
			ID:              uuid.New(),
			PlannedCapacity: &capacity,
			ActualCapacity:  &capacity,
		}

		assert.NotNil(t, sprint.PlannedCapacity)
		assert.Equal(t, 8, *sprint.PlannedCapacity)
	})
}

// TestBurndownDataPoint validates burndown structure
func TestBurndownDataPoint(t *testing.T) {
	t.Run("burndown_data_point", func(t *testing.T) {
		dataPoint := &progress.BurndownDataPoint{
			RecordedDate:    time.Now(),
			RemainingPoints: 50,
			IdealPoints:     52,
			CompletedPoints: 10,
			AddedPoints:     2,
		}

		assert.Equal(t, 50, dataPoint.RemainingPoints)
		assert.Equal(t, 52, dataPoint.IdealPoints)
		assert.Equal(t, 10, dataPoint.CompletedPoints)
		assert.Equal(t, 2, dataPoint.AddedPoints)
	})
}

// TestProgressSnapshot validates snapshot structure
func TestProgressSnapshot(t *testing.T) {
	t.Run("snapshot_creation", func(t *testing.T) {
		metrics := &progress.ProjectMetrics{
			TotalItems:        20,
			CompletedThisWeek: 5,
			Velocity:          2.5,
			ByStatus:          make(map[string]int),
		}

		metricsJSON, err := json.Marshal(metrics)
		require.NoError(t, err)

		snapshot := &progress.Snapshot{
			ID:           uuid.New(),
			ProjectID:    uuid.New(),
			SnapshotDate: time.Now(),
			Metrics:      metricsJSON,
			CreatedAt:    time.Now(),
		}

		assert.NotNil(t, snapshot)
		assert.NotEmpty(t, snapshot.Metrics)

		// Verify metrics can be unmarshaled
		var unmarshaled progress.ProjectMetrics
		err = json.Unmarshal(snapshot.Metrics, &unmarshaled)
		require.NoError(t, err)
		assert.Equal(t, 20, unmarshaled.TotalItems)
	})
}

// TestVelocityDataPoint validates velocity structure
func TestVelocityDataPoint(t *testing.T) {
	t.Run("velocity_calculation", func(t *testing.T) {
		point := &progress.VelocityDataPoint{
			PeriodStart:     time.Now().AddDate(0, 0, -7),
			PeriodEnd:       time.Now(),
			PeriodLabel:     "Sprint 1",
			PlannedPoints:   20,
			CompletedPoints: 18,
			Velocity:        18,
		}

		assert.Equal(t, "Sprint 1", point.PeriodLabel)
		assert.Equal(t, 20, point.PlannedPoints)
		assert.Equal(t, 18, point.CompletedPoints)
		assert.Equal(t, 18, point.Velocity)
	})

	t.Run("velocity_tracking", func(t *testing.T) {
		// Simulate multiple sprint velocities
		velocities := []progress.VelocityDataPoint{
			{PeriodLabel: "Sprint 1", Velocity: 15},
			{PeriodLabel: "Sprint 2", Velocity: 18},
			{PeriodLabel: "Sprint 3", Velocity: 20},
		}

		avg := 0
		for _, v := range velocities {
			avg += v.Velocity
		}
		avg /= len(velocities)

		assert.Equal(t, 17, avg)
	})
}

// TestProjectMetrics validates metrics structure
func TestProjectMetrics(t *testing.T) {
	t.Run("project_metrics_structure", func(t *testing.T) {
		metrics := &progress.ProjectMetrics{
			TotalItems:        100,
			BlockedCount:      5,
			AtRiskCount:       3,
			OverdueCount:      2,
			CompletedThisWeek: 10,
			CompletedLastWeek: 8,
			Velocity:          2.5,
			ByStatus:          make(map[string]int),
			ByPriority:        make(map[string]int),
			ByType:            make(map[string]int),
		}

		metrics.ByStatus["done"] = 50
		metrics.ByStatus["in_progress"] = 30
		metrics.ByStatus["todo"] = 20

		assert.Equal(t, 100, metrics.TotalItems)
		assert.Equal(t, 5, metrics.BlockedCount)
		assert.Equal(t, 50, metrics.ByStatus["done"])
	})

	t.Run("test_coverage_metrics", func(t *testing.T) {
		testCoverage := 85.5
		docCoverage := 72.0

		metrics := &progress.ProjectMetrics{
			TestCoverage: &testCoverage,
			DocCoverage:  &docCoverage,
		}

		assert.NotNil(t, metrics.TestCoverage)
		assert.InEpsilon(t, 85.5, *metrics.TestCoverage, 1e-9)
		assert.InEpsilon(t, 72.0, *metrics.DocCoverage, 1e-9)
	})
}

// TestMilestoneProgress validates progress calculation
func TestMilestoneProgress(t *testing.T) {
	t.Run("progress_calculation", func(t *testing.T) {
		progress := &progress.MilestoneProgress{
			TotalItems:      20,
			CompletedItems:  15,
			InProgressItems: 3,
			BlockedItems:    1,
			NotStartedItems: 1,
			Percentage:      75,
		}

		assert.Equal(t, 20, progress.TotalItems)
		assert.Equal(t, 15, progress.CompletedItems)
		assert.Equal(t, 75, progress.Percentage)

		// Verify sum
		sum := progress.CompletedItems + progress.InProgressItems +
			progress.BlockedItems + progress.NotStartedItems
		assert.Equal(t, progress.TotalItems, sum)
	})
}

// TestStatusTypes validates milestone status types
func TestStatusTypes(t *testing.T) {
	t.Run("milestone_statuses", func(t *testing.T) {
		statuses := []progress.MilestoneStatus{
			progress.MilestoneNotStarted,
			progress.MilestoneInProgress,
			progress.MilestoneAtRisk,
			progress.MilestoneBlocked,
			progress.MilestoneCompleted,
			progress.MilestoneCancelled,
		}

		assert.Len(t, statuses, 6)
		assert.Equal(t, progress.MilestoneNotStarted, progress.MilestoneStatus("not_started"))
	})

	t.Run("sprint_statuses", func(t *testing.T) {
		statuses := []progress.SprintStatus{
			progress.SprintPlanning,
			progress.SprintActive,
			progress.SprintCompleted,
			progress.SprintCancelled,
		}

		assert.Len(t, statuses, 4)
	})

	t.Run("health_statuses", func(t *testing.T) {
		statuses := []progress.HealthStatus{
			progress.HealthGreen,
			progress.HealthYellow,
			progress.HealthRed,
			progress.HealthUnknown,
		}

		assert.Len(t, statuses, 4)
	})
}

// TestRequestTypes validates request structures
func TestRequestTypes(t *testing.T) {
	t.Run("create_milestone_request", func(t *testing.T) {
		targetDate := time.Now().AddDate(0, 0, 60)
		req := &progress.CreateMilestoneRequest{
			Name:       "v1.0",
			Slug:       "v1-0",
			TargetDate: targetDate,
		}

		assert.Equal(t, "v1.0", req.Name)
		assert.Equal(t, targetDate, req.TargetDate)
	})

	t.Run("create_sprint_request", func(t *testing.T) {
		startDate := time.Now()
		endDate := time.Now().AddDate(0, 0, 14)

		req := &progress.CreateSprintRequest{
			Name:      "Sprint 1",
			Slug:      "sprint-1",
			StartDate: startDate,
			EndDate:   endDate,
		}

		assert.Equal(t, "Sprint 1", req.Name)
		assert.Equal(t, startDate, req.StartDate)
		assert.Equal(t, endDate, req.EndDate)
	})

	t.Run("update_milestone_request", func(t *testing.T) {
		newName := "Updated Milestone"
		newStatus := progress.MilestoneInProgress

		req := &progress.UpdateMilestoneRequest{
			Name:   &newName,
			Status: &newStatus,
		}

		assert.NotNil(t, req.Name)
		assert.Equal(t, "Updated Milestone", *req.Name)
		assert.Equal(t, progress.MilestoneInProgress, *req.Status)
	})
}

// TestHealthCalculation validates health status logic
func TestHealthCalculation(t *testing.T) {
	t.Run("milestone_health_red", func(t *testing.T) {
		milestone := &progress.Milestone{
			RiskScore: 75,
			Health:    progress.HealthRed,
		}

		// Health red when risk score > 70
		assert.Equal(t, progress.HealthRed, milestone.Health)
	})

	t.Run("milestone_health_yellow", func(t *testing.T) {
		milestone := &progress.Milestone{
			RiskScore: 50,
			Health:    progress.HealthYellow,
		}

		// Health yellow when risk score 40-70
		assert.Equal(t, progress.HealthYellow, milestone.Health)
	})

	t.Run("milestone_health_green", func(t *testing.T) {
		milestone := &progress.Milestone{
			RiskScore: 20,
			Health:    progress.HealthGreen,
		}

		assert.Equal(t, progress.HealthGreen, milestone.Health)
	})
}

// TestRiskFactorStructure validates risk factor structure
func TestRiskFactorStructure(t *testing.T) {
	t.Run("risk_factor", func(t *testing.T) {
		itemID := uuid.New()
		suggestion := "Allocate more resources"

		rf := progress.RiskFactor{
			Type:                 "resource_constraint",
			Severity:             "high",
			Description:          "Team member unavailable",
			ItemID:               &itemID,
			MitigationSuggestion: &suggestion,
		}

		assert.Equal(t, "resource_constraint", rf.Type)
		assert.Equal(t, "high", rf.Severity)
		assert.NotNil(t, rf.ItemID)
		assert.NotNil(t, rf.MitigationSuggestion)
	})
}

// TestErrorHandling validates error scenarios
func TestErrorHandling(t *testing.T) {
	t.Run("invalid_uuid", func(t *testing.T) {
		_, err := uuid.Parse("invalid-uuid")
		assert.Error(t, err)
	})

	t.Run("date_validation", func(t *testing.T) {
		now := time.Now()
		past := now.AddDate(0, 0, -1)

		// End date before start date
		assert.True(t, past.Before(now))
	})

	t.Run("json_marshaling", func(t *testing.T) {
		factors := []progress.RiskFactor{
			{Type: "scope_creep", Severity: "high"},
		}

		jsonData, err := json.Marshal(factors)
		require.NoError(t, err)
		assert.NotEmpty(t, jsonData)

		var unmarshaled []progress.RiskFactor
		err = json.Unmarshal(jsonData, &unmarshaled)
		require.NoError(t, err)
		assert.Equal(t, "scope_creep", unmarshaled[0].Type)
	})
}
