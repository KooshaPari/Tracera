package handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/services"
)

// MockTemporalService implements services.TemporalService for testing
type MockTemporalService struct {
	mock.Mock
}

func (m *MockTemporalService) CreateBranch(ctx context.Context, branch *services.VersionBranch) (*services.VersionBranch, error) {
	args := m.Called(ctx, branch)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*services.VersionBranch)
	return val, args.Error(1)
}

func (m *MockTemporalService) GetBranch(ctx context.Context, branchID string) (*services.VersionBranch, error) {
	args := m.Called(ctx, branchID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*services.VersionBranch)
	return val, args.Error(1)
}

func (m *MockTemporalService) ListBranches(ctx context.Context, projectID string) ([]*services.VersionBranch, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*services.VersionBranch)
	return val, args.Error(1)
}

func (m *MockTemporalService) UpdateBranch(ctx context.Context, branch *services.VersionBranch) (*services.VersionBranch, error) {
	args := m.Called(ctx, branch)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*services.VersionBranch)
	return val, args.Error(1)
}

func (m *MockTemporalService) DeleteBranch(ctx context.Context, branchID string) error {
	args := m.Called(ctx, branchID)
	return args.Error(0)
}

func (m *MockTemporalService) CreateVersion(ctx context.Context, version *services.Version) (*services.Version, error) {
	args := m.Called(ctx, version)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*services.Version)
	return val, args.Error(1)
}

func (m *MockTemporalService) GetVersion(ctx context.Context, versionID string) (*services.Version, error) {
	args := m.Called(ctx, versionID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*services.Version)
	return val, args.Error(1)
}

func (m *MockTemporalService) GetVersionsByBranch(ctx context.Context, branchID string) ([]*services.Version, error) {
	args := m.Called(ctx, branchID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*services.Version)
	return val, args.Error(1)
}

func (m *MockTemporalService) ApproveVersion(ctx context.Context, versionID string, approvedBy string) error {
	args := m.Called(ctx, versionID, approvedBy)
	return args.Error(0)
}

func (m *MockTemporalService) RejectVersion(ctx context.Context, versionID string, reason string) error {
	args := m.Called(ctx, versionID, reason)
	return args.Error(0)
}

func (m *MockTemporalService) GetItemVersion(ctx context.Context, itemID, versionID string) (*services.ItemVersionSnapshot, error) {
	args := m.Called(ctx, itemID, versionID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*services.ItemVersionSnapshot)
	return val, args.Error(1)
}

func (m *MockTemporalService) GetItemVersionHistory(
	ctx context.Context, itemID, branchID string,
) ([]*services.ItemVersionSnapshot, error) {
	args := m.Called(ctx, itemID, branchID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*services.ItemVersionSnapshot)
	return val, args.Error(1)
}

func (m *MockTemporalService) GetItemAtTime(
	ctx context.Context, itemID string, timestamp time.Time,
) (*services.ItemVersionSnapshot, error) {
	args := m.Called(ctx, itemID, timestamp)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*services.ItemVersionSnapshot)
	return val, args.Error(1)
}

func (m *MockTemporalService) RestoreItemVersion(ctx context.Context, itemID, versionID string) error {
	args := m.Called(ctx, itemID, versionID)
	return args.Error(0)
}

func (m *MockTemporalService) CreateAlternative(ctx context.Context, alt *services.ItemAlternative) (*services.ItemAlternative, error) {
	args := m.Called(ctx, alt)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*services.ItemAlternative)
	return val, args.Error(1)
}

func (m *MockTemporalService) GetAlternatives(ctx context.Context, baseItemID string) ([]*services.ItemAlternative, error) {
	args := m.Called(ctx, baseItemID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*services.ItemAlternative)
	return val, args.Error(1)
}

func (m *MockTemporalService) SelectAlternative(ctx context.Context, altID string, selectedBy string, reason string) error {
	args := m.Called(ctx, altID, selectedBy, reason)
	return args.Error(0)
}

func (m *MockTemporalService) CreateMergeRequest(ctx context.Context, mr *services.MergeRequest) (*services.MergeRequest, error) {
	args := m.Called(ctx, mr)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*services.MergeRequest)
	return val, args.Error(1)
}

func (m *MockTemporalService) GetMergeRequest(ctx context.Context, mrID string) (*services.MergeRequest, error) {
	args := m.Called(ctx, mrID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*services.MergeRequest)
	return val, args.Error(1)
}

func (m *MockTemporalService) ListMergeRequests(ctx context.Context, projectID string, status string) ([]*services.MergeRequest, error) {
	args := m.Called(ctx, projectID, status)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*services.MergeRequest)
	return val, args.Error(1)
}

func (m *MockTemporalService) ComputeMergeDiff(ctx context.Context, mrID string) (*services.VersionDiff, error) {
	args := m.Called(ctx, mrID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*services.VersionDiff)
	return val, args.Error(1)
}

func (m *MockTemporalService) MergeBranches(ctx context.Context, mrID string, mergedBy string) error {
	args := m.Called(ctx, mrID, mergedBy)
	return args.Error(0)
}

func (m *MockTemporalService) ComparVersions(ctx context.Context, versionAID, versionBID string) (*services.VersionDiff, error) {
	args := m.Called(ctx, versionAID, versionBID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*services.VersionDiff)
	return val, args.Error(1)
}

// Test helpers
func setupEchoContext(t *testing.T, method, path string, body interface{}) (echo.Context, *httptest.ResponseRecorder) {
	e := echo.New()
	var req *http.Request
	var err error

	if body != nil {
		bodyBytes, err := json.Marshal(body)
		require.NoError(t, err)
		req, err = http.NewRequestWithContext(context.Background(), method, path, bytes.NewReader(bodyBytes))
		require.NoError(t, err)
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	} else {
		req, err = http.NewRequestWithContext(context.Background(), method, path, nil)
		require.NoError(t, err)
	}

	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	return c, rec
}

// ============================================================================
// BRANCH TESTS
// ============================================================================

func TestCreateBranch_Success(t *testing.T) {
	mockSvc := new(MockTemporalService)
	handler := NewTemporalHandler(mockSvc)

	branch := &services.VersionBranch{
		ID:         "branch-1",
		ProjectID:  "proj-1",
		Name:       "main",
		Slug:       "main",
		BranchType: "main",
		Status:     "active",
		CreatedBy:  "user-1",
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}

	mockSvc.On("CreateBranch", mock.Anything, mock.MatchedBy(func(b *services.VersionBranch) bool {
		return b.Name == "main" && b.ProjectID == "proj-1"
	})).Return(branch, nil)

	c, rec := setupEchoContext(t, http.MethodPost, "/projects/proj-1/branches", map[string]interface{}{
		"name":        "main",
		"slug":        "main",
		"branch_type": "main",
		"created_by":  "user-1",
	})
	c.SetParamNames("projectId")
	c.SetParamValues("proj-1")

	err := handler.CreateBranch(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	var result services.VersionBranch
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	require.NoError(t, err)
	assert.Equal(t, "main", result.Name)
	assert.Equal(t, "proj-1", result.ProjectID)
}

func TestGetBranch_Success(t *testing.T) {
	mockSvc := new(MockTemporalService)
	handler := NewTemporalHandler(mockSvc)

	branch := &services.VersionBranch{
		ID:        "branch-1",
		ProjectID: "proj-1",
		Name:      "main",
		Status:    "active",
	}

	mockSvc.On("GetBranch", mock.Anything, "branch-1").Return(branch, nil)

	c, rec := setupEchoContext(t, http.MethodGet, "/branches/branch-1", nil)
	c.SetParamNames("branchId")
	c.SetParamValues("branch-1")

	err := handler.GetBranch(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result services.VersionBranch
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	require.NoError(t, err)
	assert.Equal(t, "main", result.Name)
}

func TestListBranches_Success(t *testing.T) {
	mockSvc := new(MockTemporalService)
	handler := NewTemporalHandler(mockSvc)

	branches := []*services.VersionBranch{
		{ID: "branch-1", Name: "main"},
		{ID: "branch-2", Name: "develop"},
	}

	mockSvc.On("ListBranches", mock.Anything, "proj-1").Return(branches, nil)

	c, rec := setupEchoContext(t, http.MethodGet, "/projects/proj-1/branches", nil)
	c.SetParamNames("projectId")
	c.SetParamValues("proj-1")

	err := handler.ListBranches(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result []*services.VersionBranch
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	require.NoError(t, err)
	assert.Len(t, result, 2)
}

func TestDeleteBranch_Success(t *testing.T) {
	mockSvc := new(MockTemporalService)
	handler := NewTemporalHandler(mockSvc)

	mockSvc.On("DeleteBranch", mock.Anything, "branch-1").Return(nil)

	c, rec := setupEchoContext(t, http.MethodDelete, "/branches/branch-1", nil)
	c.SetParamNames("branchId")
	c.SetParamValues("branch-1")

	err := handler.DeleteBranch(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusNoContent, rec.Code)
}

// ============================================================================
// VERSION TESTS
// ============================================================================

func TestCreateVersion_Success(t *testing.T) {
	mockSvc := new(MockTemporalService)
	handler := NewTemporalHandler(mockSvc)

	version := &services.Version{
		ID:        "ver-1",
		BranchID:  "branch-1",
		ProjectID: "proj-1",
		Message:   "Initial version",
		Status:    "draft",
	}

	mockSvc.On("CreateVersion", mock.Anything, mock.MatchedBy(func(v *services.Version) bool {
		return v.Message == "Initial version" && v.BranchID == "branch-1"
	})).Return(version, nil)

	c, rec := setupEchoContext(t, http.MethodPost, "/branches/branch-1/versions", map[string]interface{}{
		"project_id": "proj-1",
		"message":    "Initial version",
		"created_by": "user-1",
	})
	c.SetParamNames("branchId")
	c.SetParamValues("branch-1")

	err := handler.CreateVersion(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	var result services.Version
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	require.NoError(t, err)
	assert.Equal(t, "Initial version", result.Message)
}

func TestApproveVersion_Success(t *testing.T) {
	mockSvc := new(MockTemporalService)
	handler := NewTemporalHandler(mockSvc)

	mockSvc.On("ApproveVersion", mock.Anything, "ver-1", "reviewer-1").Return(nil)

	c, rec := setupEchoContext(t, http.MethodPost, "/versions/ver-1/approve", map[string]interface{}{
		"approved_by": "reviewer-1",
	})
	c.SetParamNames("versionId")
	c.SetParamValues("ver-1")

	err := handler.ApproveVersion(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)
}

func TestMergeBranches_Success(t *testing.T) {
	mockSvc := new(MockTemporalService)
	handler := NewTemporalHandler(mockSvc)

	mockSvc.On("MergeBranches", mock.Anything, "mr-1", "user-1").Return(nil)

	c, rec := setupEchoContext(t, http.MethodPost, "/merge-requests/mr-1/merge", map[string]interface{}{
		"merged_by": "user-1",
	})
	c.SetParamNames("mrId")
	c.SetParamValues("mr-1")

	err := handler.MergeBranches(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result map[string]string
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	require.NoError(t, err)
	assert.Equal(t, "merged", result["status"])
}

func TestListMergeRequests_Success(t *testing.T) {
	mockSvc := new(MockTemporalService)
	handler := NewTemporalHandler(mockSvc)

	mrs := []*services.MergeRequest{
		{ID: "mr-1", Title: "Feature 1", Status: "open"},
		{ID: "mr-2", Title: "Feature 2", Status: "merged"},
	}

	mockSvc.On("ListMergeRequests", mock.Anything, "proj-1", "").Return(mrs, nil)

	c, rec := setupEchoContext(t, http.MethodGet, "/projects/proj-1/merge-requests", nil)
	c.SetParamNames("projectId")
	c.SetParamValues("proj-1")

	err := handler.ListMergeRequests(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result []*services.MergeRequest
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	require.NoError(t, err)
	assert.Len(t, result, 2)
}

func TestCompareVersions_Success(t *testing.T) {
	mockSvc := new(MockTemporalService)
	handler := NewTemporalHandler(mockSvc)

	diff := &services.VersionDiff{
		VersionAID:     "ver-1",
		VersionBID:     "ver-2",
		VersionANumber: 1,
		VersionBNumber: 2,
		Stats: services.DiffStats{
			TotalChanges:  2,
			AddedCount:    1,
			RemovedCount:  0,
			ModifiedCount: 1,
		},
	}

	mockSvc.On("ComparVersions", mock.Anything, "ver-1", "ver-2").Return(diff, nil)

	c, rec := setupEchoContext(t, http.MethodGet, "/versions/ver-1/compare/ver-2", nil)
	c.SetParamNames("versionAId", "versionBId")
	c.SetParamValues("ver-1", "ver-2")

	err := handler.CompareVersions(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result services.VersionDiff
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	require.NoError(t, err)
	assert.Equal(t, 2, result.Stats.TotalChanges)
}
