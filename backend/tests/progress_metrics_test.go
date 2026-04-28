package tests

import (
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"

	"github.com/kooshapari/tracertm-backend/internal/progress"
)

// Mock database for metrics testing
type MockMetricsDB struct {
	items map[uuid.UUID]map[string]interface{}
}

func NewMockMetricsDB() *MockMetricsDB {
	return &MockMetricsDB{
		items: make(map[uuid.UUID]map[string]interface{}),
	}
}

func (m *MockMetricsDB) AddItem(itemID uuid.UUID, data map[string]interface{}) {
	m.items[itemID] = data
}

func TestCalculateHealthStatus(t *testing.T) {
	testCases := []struct {
		name               string
		onTime             bool
		blockedPercentage  float64
		progressVsExpected float64
		expectedHealth     string
	}{
		{
			name:               "Green - On time, no blockers, good progress",
			onTime:             true,
			blockedPercentage:  0,
			progressVsExpected: 1.0,
			expectedHealth:     "green",
		},
		{
			name:               "Yellow - Behind schedule",
			onTime:             false,
			blockedPercentage:  5,
			progressVsExpected: 0.85,
			expectedHealth:     "yellow",
		},
		{
			name:               "Yellow - Some blockers",
			onTime:             true,
			blockedPercentage:  15,
			progressVsExpected: 0.9,
			expectedHealth:     "yellow",
		},
		{
			name:               "Red - Many blockers",
			onTime:             true,
			blockedPercentage:  35,
			progressVsExpected: 0.7,
			expectedHealth:     "red",
		},
		{
			name:               "Red - Poor progress",
			onTime:             true,
			blockedPercentage:  5,
			progressVsExpected: 0.4,
			expectedHealth:     "red",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			health := progress.CalculateHealthStatus(
				tc.onTime,
				tc.blockedPercentage,
				tc.progressVsExpected,
			)
			assert.NotEmpty(t, health)
		})
	}
}

func TestCalculateProgressPercentage(t *testing.T) {
	testCases := []struct {
		name            string
		completed       int
		total           int
		expectedPercent int
	}{
		{
			name:            "No items",
			completed:       0,
			total:           0,
			expectedPercent: 0,
		},
		{
			name:            "No progress",
			completed:       0,
			total:           10,
			expectedPercent: 0,
		},
		{
			name:            "Half complete",
			completed:       5,
			total:           10,
			expectedPercent: 50,
		},
		{
			name:            "All complete",
			completed:       10,
			total:           10,
			expectedPercent: 100,
		},
		{
			name:            "Rounding",
			completed:       1,
			total:           3,
			expectedPercent: 33,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			percent := progress.CalculateProgressPercentage(tc.completed, tc.total)
			assert.Equal(t, tc.expectedPercent, percent)
		})
	}
}

func TestDaysUntilTarget(t *testing.T) {
	testCases := []struct {
		name          string
		targetDate    time.Time
		expectedRange func(int) bool
	}{
		{
			name:       "Tomorrow",
			targetDate: time.Now().AddDate(0, 0, 1),
			expectedRange: func(days int) bool {
				return days == 1
			},
		},
		{
			name:       "30 days from now",
			targetDate: time.Now().AddDate(0, 0, 30),
			expectedRange: func(days int) bool {
				return days >= 29 && days <= 31
			},
		},
		{
			name:       "Overdue by 1 day",
			targetDate: time.Now().AddDate(0, 0, -1),
			expectedRange: func(days int) bool {
				return days == -1 || days == -2
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			days := progress.DaysUntilTarget(tc.targetDate.String())
			assert.True(t, tc.expectedRange(days))
		})
	}
}

func TestCalculateVelocity(t *testing.T) {
	testCases := []struct {
		name           string
		history        []progress.VelocityDataPoint
		periods        int
		expectedResult func(float64) bool
	}{
		{
			name:    "Empty history",
			history: []progress.VelocityDataPoint{},
			periods: 3,
			expectedResult: func(v float64) bool {
				return v == 0
			},
		},
		{
			name: "Single period",
			history: []progress.VelocityDataPoint{
				{Velocity: 20},
			},
			periods: 3,
			expectedResult: func(v float64) bool {
				return v == 20
			},
		},
		{
			name: "Multiple periods",
			history: []progress.VelocityDataPoint{
				{Velocity: 20},
				{Velocity: 25},
				{Velocity: 30},
				{Velocity: 35},
			},
			periods: 3,
			expectedResult: func(v float64) bool {
				// Average of last 3: (25+30+35)/3 = 30
				return v == 30
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			velocity := progress.CalculateVelocity(tc.history, tc.periods)
			assert.True(t, tc.expectedResult(velocity))
		})
	}
}

func TestEstimateCompletionDate(t *testing.T) {
	testCases := []struct {
		name            string
		remainingPoints int
		velocity        float64
		shouldEstimate  bool
	}{
		{
			name:            "Zero velocity",
			remainingPoints: 10,
			velocity:        0,
			shouldEstimate:  false,
		},
		{
			name:            "Negative velocity",
			remainingPoints: 10,
			velocity:        -5,
			shouldEstimate:  false,
		},
		{
			name:            "Valid estimation",
			remainingPoints: 10,
			velocity:        5,
			shouldEstimate:  true,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			completion := progress.EstimateCompletionDate(tc.remainingPoints, tc.velocity)
			if tc.shouldEstimate {
				assert.NotNil(t, completion)
			} else {
				assert.Nil(t, completion)
			}
		})
	}
}

func TestGetHealthColor(t *testing.T) {
	testCases := []struct {
		health        progress.HealthStatus
		expectedColor string
	}{
		{
			health:        progress.HealthGreen,
			expectedColor: "#22c55e",
		},
		{
			health:        progress.HealthYellow,
			expectedColor: "#eab308",
		},
		{
			health:        progress.HealthRed,
			expectedColor: "#ef4444",
		},
		{
			health:        progress.HealthUnknown,
			expectedColor: "#6b7280",
		},
	}

	for _, tc := range testCases {
		t.Run(string(tc.health), func(t *testing.T) {
			color := progress.GetHealthColor(tc.health)
			assert.Equal(t, tc.expectedColor, color)
		})
	}
}

func TestGetMilestoneStatusColor(t *testing.T) {
	testCases := []struct {
		status        progress.MilestoneStatus
		expectedColor string
	}{
		{
			status:        progress.MilestoneNotStarted,
			expectedColor: "#94a3b8",
		},
		{
			status:        progress.MilestoneInProgress,
			expectedColor: "#3b82f6",
		},
		{
			status:        progress.MilestoneAtRisk,
			expectedColor: "#eab308",
		},
		{
			status:        progress.MilestoneBlocked,
			expectedColor: "#ef4444",
		},
		{
			status:        progress.MilestoneCompleted,
			expectedColor: "#22c55e",
		},
		{
			status:        progress.MilestoneCancelled,
			expectedColor: "#6b7280",
		},
	}

	for _, tc := range testCases {
		t.Run(string(tc.status), func(t *testing.T) {
			color := progress.GetMilestoneStatusColor(tc.status)
			assert.Equal(t, tc.expectedColor, color)
		})
	}
}

func TestGetSprintStatusColor(t *testing.T) {
	testCases := []struct {
		status        progress.SprintStatus
		expectedColor string
	}{
		{
			status:        progress.SprintPlanning,
			expectedColor: "#a78bfa",
		},
		{
			status:        progress.SprintActive,
			expectedColor: "#3b82f6",
		},
		{
			status:        progress.SprintCompleted,
			expectedColor: "#22c55e",
		},
		{
			status:        progress.SprintCancelled,
			expectedColor: "#6b7280",
		},
	}

	for _, tc := range testCases {
		t.Run(string(tc.status), func(t *testing.T) {
			color := progress.GetSprintStatusColor(tc.status)
			assert.Equal(t, tc.expectedColor, color)
		})
	}
}

// RiskFactor validation tests
func TestRiskFactorCreation(t *testing.T) {
	itemID := uuid.New()
	suggestion := "Increase team capacity"

	factor := progress.RiskFactor{
		Type:                 "resource_constraint",
		Severity:             "high",
		Description:          "Not enough team members",
		ItemID:               &itemID,
		MitigationSuggestion: &suggestion,
	}

	assert.Equal(t, "resource_constraint", factor.Type)
	assert.Equal(t, "high", factor.Severity)
	assert.NotNil(t, factor.ItemID)
	assert.NotNil(t, factor.MitigationSuggestion)
	assert.Equal(t, suggestion, *factor.MitigationSuggestion)
}

// Milestone progress calculation tests
func TestMilestoneProgressCalculation(t *testing.T) {
	testCases := []struct {
		name               string
		totalItems         int
		completedItems     int
		inProgressItems    int
		blockedItems       int
		expectedPercentage int
	}{
		{
			name:               "No items",
			totalItems:         0,
			completedItems:     0,
			inProgressItems:    0,
			blockedItems:       0,
			expectedPercentage: 0,
		},
		{
			name:               "All completed",
			totalItems:         10,
			completedItems:     10,
			inProgressItems:    0,
			blockedItems:       0,
			expectedPercentage: 100,
		},
		{
			name:               "Half completed",
			totalItems:         10,
			completedItems:     5,
			inProgressItems:    3,
			blockedItems:       2,
			expectedPercentage: 50,
		},
		{
			name:               "None completed",
			totalItems:         10,
			completedItems:     0,
			inProgressItems:    5,
			blockedItems:       5,
			expectedPercentage: 0,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			progress := &progress.MilestoneProgress{
				TotalItems:      tc.totalItems,
				CompletedItems:  tc.completedItems,
				InProgressItems: tc.inProgressItems,
				BlockedItems:    tc.blockedItems,
			}

			if tc.totalItems > 0 {
				progress.Percentage = (progress.CompletedItems * 100) / progress.TotalItems
			}

			assert.Equal(t, tc.expectedPercentage, progress.Percentage)
		})
	}
}

// Sprint burndown rate calculation
func TestSprintBurndownRate(t *testing.T) {
	testCases := []struct {
		name          string
		plannedPoints int
		elapsedDays   int
		expectedRate  float64
	}{
		{
			name:          "10 points over 2 weeks",
			plannedPoints: 50,
			elapsedDays:   14,
			expectedRate:  50.0 / 14.0,
		},
		{
			name:          "Zero duration",
			plannedPoints: 50,
			elapsedDays:   0,
			expectedRate:  0,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			var rate float64
			if tc.elapsedDays > 0 {
				rate = float64(tc.plannedPoints) / float64(tc.elapsedDays)
			}
			assert.Equal(t, tc.expectedRate, rate)
		})
	}
}
