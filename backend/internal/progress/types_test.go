//go:build !integration

package progress

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestMilestoneStatusConstants(t *testing.T) {
	tests := []struct {
		status MilestoneStatus
		want   string
	}{
		{MilestoneNotStarted, "not_started"},
		{MilestoneInProgress, "in_progress"},
		{MilestoneAtRisk, "at_risk"},
		{MilestoneBlocked, "blocked"},
		{MilestoneCompleted, "completed"},
		{MilestoneCancelled, "cancelled"},
	}
	for _, tt := range tests {
		t.Run(tt.want, func(t *testing.T) {
			assert.Equal(t, MilestoneStatus(tt.want), tt.status)
		})
	}
}

func TestHealthStatusConstants(t *testing.T) {
	assert.Equal(t, HealthStatus("green"), HealthGreen)
	assert.Equal(t, HealthStatus("yellow"), HealthYellow)
	assert.Equal(t, HealthStatus("red"), HealthRed)
	assert.Equal(t, HealthStatus("unknown"), HealthUnknown)
}

func TestSprintStatusConstants(t *testing.T) {
	assert.Equal(t, SprintStatus("planning"), SprintPlanning)
	assert.Equal(t, SprintStatus("active"), SprintActive)
	assert.Equal(t, SprintStatus("completed"), SprintCompleted)
	assert.Equal(t, SprintStatus("cancelled"), SprintCancelled)
}

func TestRiskFactorSlice_ScanNil(t *testing.T) {
	var rf RiskFactorSlice
	err := rf.Scan(nil)
	require.NoError(t, err)
	assert.Empty(t, rf)
}

func TestRiskFactorSlice_ScanValid(t *testing.T) {
	data := []RiskFactor{
		{Type: "overdue", Severity: "high", Description: "test"},
	}
	jsonBytes, err := json.Marshal(data)
	require.NoError(t, err)

	var rf RiskFactorSlice
	err = rf.Scan(jsonBytes)
	require.NoError(t, err)
	require.Len(t, rf, 1)
	assert.Equal(t, "overdue", rf[0].Type)
	assert.Equal(t, "high", rf[0].Severity)
}

func TestRiskFactorSlice_ScanInvalidJSON(t *testing.T) {
	var rf RiskFactorSlice
	err := rf.Scan([]byte("invalid json"))
	require.Error(t, err)
}

func TestRiskFactorSlice_Value(t *testing.T) {
	rf := RiskFactorSlice{
		{Type: "blocked_dependency", Severity: "medium", Description: "dep blocked"},
	}
	val, err := rf.Value()
	require.NoError(t, err)
	require.NotNil(t, val)

	// Should be valid JSON
	var decoded []RiskFactor
	err = json.Unmarshal(val.([]byte), &decoded)
	require.NoError(t, err)
	assert.Len(t, decoded, 1)
	assert.Equal(t, "blocked_dependency", decoded[0].Type)
}

func TestRiskFactorSlice_ValueEmpty(t *testing.T) {
	rf := RiskFactorSlice{}
	val, err := rf.Value()
	require.NoError(t, err)
	require.NotNil(t, val)
	assert.Equal(t, []byte("[]"), val.([]byte))
}

func TestStringSlice_ScanNil(t *testing.T) {
	var ss StringSlice
	err := ss.Scan(nil)
	require.NoError(t, err)
	assert.Empty(t, ss)
}

func TestStringSlice_ScanValid(t *testing.T) {
	data := []string{"tag1", "tag2", "tag3"}
	jsonBytes, err := json.Marshal(data)
	require.NoError(t, err)

	var ss StringSlice
	err = ss.Scan(jsonBytes)
	require.NoError(t, err)
	assert.Len(t, ss, 3)
	assert.Equal(t, "tag1", ss[0])
}

func TestStringSlice_ScanInvalidJSON(t *testing.T) {
	var ss StringSlice
	err := ss.Scan([]byte("{not array}"))
	require.Error(t, err)
}

func TestStringSlice_Value(t *testing.T) {
	ss := StringSlice{"a", "b"}
	val, err := ss.Value()
	require.NoError(t, err)
	require.NotNil(t, val)

	var decoded []string
	err = json.Unmarshal(val.([]byte), &decoded)
	require.NoError(t, err)
	assert.Equal(t, []string{"a", "b"}, decoded)
}

func TestStringSlice_ValueEmpty(t *testing.T) {
	ss := StringSlice{}
	val, err := ss.Value()
	require.NoError(t, err)
	assert.Equal(t, []byte("[]"), val.([]byte))
}

func TestMilestoneStruct(t *testing.T) {
	id := uuid.New()
	projID := uuid.New()
	now := time.Now()
	desc := "test desc"

	m := Milestone{
		ID:          id,
		ProjectID:   projID,
		Name:        "Milestone 1",
		Slug:        "milestone-1",
		Description: &desc,
		TargetDate:  now,
		Status:      MilestoneNotStarted,
		Health:      HealthUnknown,
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	assert.Equal(t, id, m.ID)
	assert.Equal(t, projID, m.ProjectID)
	assert.Equal(t, "Milestone 1", m.Name)
	assert.Equal(t, &desc, m.Description)
	assert.Equal(t, MilestoneNotStarted, m.Status)
	assert.Equal(t, HealthUnknown, m.Health)
	assert.Nil(t, m.ParentID)
	assert.Nil(t, m.DeletedAt)
}

func TestSprintStruct(t *testing.T) {
	now := time.Now()
	goal := "Ship feature X"

	s := Sprint{
		ID:        uuid.New(),
		ProjectID: uuid.New(),
		Name:      "Sprint 1",
		Slug:      "sprint-1",
		Goal:      &goal,
		StartDate: now,
		EndDate:   now.AddDate(0, 0, 14),
		Status:    SprintPlanning,
		Health:    HealthGreen,
	}

	assert.Equal(t, "Sprint 1", s.Name)
	assert.Equal(t, &goal, s.Goal)
	assert.Equal(t, SprintPlanning, s.Status)
	assert.Nil(t, s.CompletedAt)
}

func TestMilestoneProgress(t *testing.T) {
	p := MilestoneProgress{
		TotalItems:      10,
		CompletedItems:  5,
		InProgressItems: 3,
		BlockedItems:    1,
		NotStartedItems: 1,
		Percentage:      50,
	}

	assert.Equal(t, 10, p.TotalItems)
	assert.Equal(t, 5, p.CompletedItems)
	assert.Equal(t, 50, p.Percentage)
}

func TestRiskFactor_WithOptionalFields(t *testing.T) {
	itemID := uuid.New()
	mitigation := "Fix the dependency"

	rf := RiskFactor{
		Type:                 "blocked_dependency",
		Severity:             "high",
		Description:          "Item X is blocked",
		ItemID:               &itemID,
		MitigationSuggestion: &mitigation,
	}

	assert.Equal(t, &itemID, rf.ItemID)
	assert.Equal(t, &mitigation, rf.MitigationSuggestion)
}

func TestProjectMetrics(t *testing.T) {
	testCov := 85.5
	pm := ProjectMetrics{
		TotalItems:   100,
		ByStatus:     map[string]int{"done": 50, "in_progress": 30},
		ByPriority:   map[string]int{"high": 20},
		ByType:       map[string]int{"feature": 60},
		ByLifecycle:  map[string]int{},
		TestCoverage: &testCov,
	}

	assert.Equal(t, 100, pm.TotalItems)
	assert.Equal(t, 50, pm.ByStatus["done"])
	assert.Equal(t, &testCov, pm.TestCoverage)
	assert.Nil(t, pm.DocCoverage)
}
