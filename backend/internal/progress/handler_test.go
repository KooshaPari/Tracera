//go:build !integration

package progress

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/gorilla/mux"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// --- Mock implementations ---

type mockMilestoneService struct {
	milestones []Milestone
	milestone  *Milestone
	progress   *MilestoneProgress
	err        error
}

func (m *mockMilestoneService) CreateMilestone(_ context.Context, _ uuid.UUID, _ *CreateMilestoneRequest) (*Milestone, error) {
	return m.milestone, m.err
}

func (m *mockMilestoneService) GetMilestone(_ context.Context, _ uuid.UUID) (*Milestone, error) {
	return m.milestone, m.err
}

func (m *mockMilestoneService) GetMilestones(_ context.Context, _ uuid.UUID) ([]Milestone, error) {
	return m.milestones, m.err
}

func (m *mockMilestoneService) GetMilestoneHierarchy(_ context.Context, _ uuid.UUID) ([]Milestone, error) {
	return m.milestones, m.err
}

func (m *mockMilestoneService) UpdateMilestone(_ context.Context, _ uuid.UUID, _ *UpdateMilestoneRequest) (*Milestone, error) {
	return m.milestone, m.err
}
func (m *mockMilestoneService) DeleteMilestone(_ context.Context, _ uuid.UUID) error { return m.err }
func (m *mockMilestoneService) AddItemToMilestone(_ context.Context, _, _ uuid.UUID) error {
	return m.err
}

func (m *mockMilestoneService) RemoveItemFromMilestone(_ context.Context, _, _ uuid.UUID) error {
	return m.err
}

func (m *mockMilestoneService) GetMilestoneProgress(_ context.Context, _ uuid.UUID) (*MilestoneProgress, error) {
	return m.progress, m.err
}

func (m *mockMilestoneService) UpdateMilestoneHealth(_ context.Context, _ uuid.UUID) error {
	return m.err
}

func (m *mockMilestoneService) ComputeRiskFactors(_ context.Context, _ uuid.UUID) ([]RiskFactor, int, error) {
	return nil, 0, m.err
}

type mockSprintService struct {
	sprints []Sprint
	sprint  *Sprint
	err     error
}

func (m *mockSprintService) CreateSprint(_ context.Context, _ uuid.UUID, _ *CreateSprintRequest) (*Sprint, error) {
	return m.sprint, m.err
}

func (m *mockSprintService) GetSprint(_ context.Context, _ uuid.UUID) (*Sprint, error) {
	return m.sprint, m.err
}

func (m *mockSprintService) GetSprints(_ context.Context, _ uuid.UUID) ([]Sprint, error) {
	return m.sprints, m.err
}

func (m *mockSprintService) GetActiveSprint(_ context.Context, _ uuid.UUID) (*Sprint, error) {
	return m.sprint, m.err
}

func (m *mockSprintService) UpdateSprint(_ context.Context, _ uuid.UUID, _ *UpdateSprintRequest) (*Sprint, error) {
	return m.sprint, m.err
}
func (m *mockSprintService) DeleteSprint(_ context.Context, _ uuid.UUID) error { return m.err }
func (m *mockSprintService) AddItemToSprint(_ context.Context, _, _ uuid.UUID) error {
	return m.err
}

func (m *mockSprintService) RemoveItemFromSprint(_ context.Context, _, _ uuid.UUID) error {
	return m.err
}
func (m *mockSprintService) RecordBurndown(_ context.Context, _ uuid.UUID) error     { return m.err }
func (m *mockSprintService) UpdateSprintHealth(_ context.Context, _ uuid.UUID) error { return m.err }
func (m *mockSprintService) CloseSprint(_ context.Context, _ uuid.UUID) error        { return m.err }

type mockMetricsService struct {
	metrics  *ProjectMetrics
	velocity float64
	history  []VelocityDataPoint
	cycle    float64
	err      error
}

func (m *mockMetricsService) CalculateProjectMetrics(_ context.Context, _ uuid.UUID) (*ProjectMetrics, error) {
	return m.metrics, m.err
}

func (m *mockMetricsService) CalculateVelocity(_ context.Context, _ uuid.UUID, _ int) (float64, error) {
	return m.velocity, m.err
}

func (m *mockMetricsService) GetVelocityHistory(_ context.Context, _ uuid.UUID) ([]VelocityDataPoint, error) {
	return m.history, m.err
}

func (m *mockMetricsService) CalculateCycleTime(_ context.Context, _ uuid.UUID) (float64, error) {
	return m.cycle, m.err
}

func (m *mockMetricsService) EstimateCompletion(_ context.Context, _ uuid.UUID) (*time.Time, error) {
	return nil, m.err
}
func (m *mockMetricsService) RecordVelocity(_ context.Context, _ uuid.UUID) error { return m.err }

type mockSnapshotService struct {
	snapshot  *Snapshot
	snapshots []Snapshot
	err       error
}

func (m *mockSnapshotService) CreateSnapshot(_ context.Context, _ uuid.UUID, _ *ProjectMetrics) (*Snapshot, error) {
	return m.snapshot, m.err
}

func (m *mockSnapshotService) GetSnapshot(_ context.Context, _ uuid.UUID) (*Snapshot, error) {
	return m.snapshot, m.err
}

func (m *mockSnapshotService) GetSnapshots(_ context.Context, _ uuid.UUID, _ int) ([]Snapshot, error) {
	return m.snapshots, m.err
}

func (m *mockSnapshotService) GetSnapshotTrend(_ context.Context, _ uuid.UUID, _ int) ([]Snapshot, error) {
	return m.snapshots, m.err
}

func (m *mockSnapshotService) RecordDailySnapshot(_ context.Context, _ uuid.UUID) (*Snapshot, error) {
	return m.snapshot, m.err
}

// --- Tests ---

func TestNewHandler(t *testing.T) {
	h := NewHandler(&mockMilestoneService{}, &mockSprintService{}, &mockMetricsService{}, &mockSnapshotService{})
	require.NotNil(t, h)
}

func TestListMilestones_MissingProjectID(t *testing.T) {
	h := NewHandler(&mockMilestoneService{}, &mockSprintService{}, &mockMetricsService{}, &mockSnapshotService{})

	req := httptest.NewRequest(http.MethodGet, "/milestones", nil)
	rec := httptest.NewRecorder()

	h.ListMilestones(rec, req)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestListMilestones_InvalidProjectID(t *testing.T) {
	h := NewHandler(&mockMilestoneService{}, &mockSprintService{}, &mockMetricsService{}, &mockSnapshotService{})

	req := httptest.NewRequest(http.MethodGet, "/milestones?project_id=not-a-uuid", nil)
	rec := httptest.NewRecorder()

	h.ListMilestones(rec, req)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestListMilestones_Success(t *testing.T) {
	ms := &mockMilestoneService{
		milestones: []Milestone{{ID: uuid.New(), Name: "M1"}},
	}
	h := NewHandler(ms, &mockSprintService{}, &mockMetricsService{}, &mockSnapshotService{})

	projID := uuid.New()
	req := httptest.NewRequest(http.MethodGet, "/milestones?project_id="+projID.String(), nil)
	rec := httptest.NewRecorder()

	h.ListMilestones(rec, req)
	assert.Equal(t, http.StatusOK, rec.Code)
	assert.Equal(t, "application/json", rec.Header().Get("Content-Type"))
}

func TestListMilestones_ServiceError(t *testing.T) {
	ms := &mockMilestoneService{err: errors.New("db error")}
	h := NewHandler(ms, &mockSprintService{}, &mockMetricsService{}, &mockSnapshotService{})

	projID := uuid.New()
	req := httptest.NewRequest(http.MethodGet, "/milestones?project_id="+projID.String(), nil)
	rec := httptest.NewRecorder()

	h.ListMilestones(rec, req)
	assert.Equal(t, http.StatusInternalServerError, rec.Code)
}

func TestGetMilestone_InvalidID(t *testing.T) {
	h := NewHandler(&mockMilestoneService{}, &mockSprintService{}, &mockMetricsService{}, &mockSnapshotService{})

	req := httptest.NewRequest(http.MethodGet, "/milestones/not-a-uuid", nil)
	req = mux.SetURLVars(req, map[string]string{"id": "not-a-uuid"})
	rec := httptest.NewRecorder()

	h.GetMilestone(rec, req)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestGetMilestone_NotFound(t *testing.T) {
	ms := &mockMilestoneService{err: errors.New("not found")}
	handler := NewHandler(ms, &mockSprintService{}, &mockMetricsService{}, &mockSnapshotService{})

	id := uuid.New()
	req := httptest.NewRequest(http.MethodGet, "/milestones/"+id.String(), nil)
	req = mux.SetURLVars(req, map[string]string{"id": id.String()})
	rec := httptest.NewRecorder()

	handler.GetMilestone(rec, req)
	assert.Equal(t, http.StatusNotFound, rec.Code)
}

func TestDeleteMilestone_Success(t *testing.T) {
	handler := NewHandler(&mockMilestoneService{}, &mockSprintService{}, &mockMetricsService{}, &mockSnapshotService{})

	id := uuid.New()
	req := httptest.NewRequest(http.MethodDelete, "/milestones/"+id.String(), nil)
	req = mux.SetURLVars(req, map[string]string{"id": id.String()})
	rec := httptest.NewRecorder()

	handler.DeleteMilestone(rec, req)
	assert.Equal(t, http.StatusNoContent, rec.Code)
}

func TestListSprints_MissingProjectID(t *testing.T) {
	h := NewHandler(&mockMilestoneService{}, &mockSprintService{}, &mockMetricsService{}, &mockSnapshotService{})

	req := httptest.NewRequest(http.MethodGet, "/sprints", nil)
	rec := httptest.NewRecorder()

	h.ListSprints(rec, req)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestGetProjectMetrics_MissingProjectID(t *testing.T) {
	h := NewHandler(&mockMilestoneService{}, &mockSprintService{}, &mockMetricsService{}, &mockSnapshotService{})

	req := httptest.NewRequest(http.MethodGet, "/metrics", nil)
	rec := httptest.NewRecorder()

	h.GetProjectMetrics(rec, req)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestGetProjectMetrics_Success(t *testing.T) {
	ms := &mockMetricsService{
		metrics: &ProjectMetrics{
			TotalItems: 42, ByStatus: map[string]int{},
			ByPriority: map[string]int{}, ByType: map[string]int{}, ByLifecycle: map[string]int{},
		},
	}
	h := NewHandler(&mockMilestoneService{}, &mockSprintService{}, ms, &mockSnapshotService{})

	projID := uuid.New()
	req := httptest.NewRequest(http.MethodGet, "/metrics?project_id="+projID.String(), nil)
	rec := httptest.NewRecorder()

	h.GetProjectMetrics(rec, req)
	assert.Equal(t, http.StatusOK, rec.Code)
}

func TestGetVelocity_WithPeriods(t *testing.T) {
	ms := &mockMetricsService{velocity: 12.5}
	h := NewHandler(&mockMilestoneService{}, &mockSprintService{}, ms, &mockSnapshotService{})

	projID := uuid.New()
	req := httptest.NewRequest(http.MethodGet, "/metrics/velocity?project_id="+projID.String()+"&periods=5", nil)
	rec := httptest.NewRecorder()

	h.GetVelocity(rec, req)
	assert.Equal(t, http.StatusOK, rec.Code)
}

func TestParseProjectID(t *testing.T) {
	tests := []struct {
		name    string
		query   string
		wantErr bool
	}{
		{"valid uuid", "project_id=" + uuid.New().String(), false},
		{"missing project_id", "", true},
		{"invalid uuid", "project_id=not-a-uuid", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest(http.MethodGet, "/?"+tt.query, nil)
			_, err := parseProjectID(req)
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

func TestRegisterRoutes(t *testing.T) {
	router := mux.NewRouter()
	h := NewHandler(&mockMilestoneService{}, &mockSprintService{}, &mockMetricsService{}, &mockSnapshotService{})

	assert.NotPanics(t, func() {
		h.RegisterRoutes(router, "/api/v1/projects/{projectId}/progress")
	})
}

func TestWriteJSON(t *testing.T) {
	rec := httptest.NewRecorder()
	writeJSON(rec, map[string]string{"key": "value"})
	assert.Equal(t, "application/json", rec.Header().Get("Content-Type"))

	var decoded map[string]string
	err := json.NewDecoder(rec.Body).Decode(&decoded)
	require.NoError(t, err)
	assert.Equal(t, "value", decoded["key"])
}

func TestCreateMilestone_InvalidBody(t *testing.T) {
	h := NewHandler(&mockMilestoneService{}, &mockSprintService{}, &mockMetricsService{}, &mockSnapshotService{})

	projID := uuid.New()
	req := httptest.NewRequest(http.MethodPost, "/milestones?project_id="+projID.String(), bytes.NewBufferString("invalid json"))
	rec := httptest.NewRecorder()

	h.CreateMilestone(rec, req)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}
