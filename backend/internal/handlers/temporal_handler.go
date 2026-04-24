package handlers

import (
	"context"
	"net/http"
	"strings"
	"time"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/services"
)

// TemporalHandler handles HTTP requests for temporal operations
type TemporalHandler struct {
	temporalService services.TemporalService
}

// NewTemporalHandler creates a new temporal handler
func NewTemporalHandler(temporalService services.TemporalService) *TemporalHandler {
	return &TemporalHandler{
		temporalService: temporalService,
	}
}

// ============================================================================
// BRANCH HANDLERS
// ============================================================================

// CreateBranch handles requests to create a new version branch.
func (handler *TemporalHandler) CreateBranch(c echo.Context) error {
	if handler.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	projectID := c.Param("projectId")
	ctx := c.Request().Context()

	var req struct {
		Name        string                 `json:"name"`
		Slug        string                 `json:"slug"`
		Description string                 `json:"description,omitempty"`
		BranchType  string                 `json:"branch_type"`
		Metadata    map[string]interface{} `json:"metadata,omitempty"`
		CreatedBy   string                 `json:"created_by"`
	}

	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body: " + err.Error()})
	}

	if req.Name == "" || req.BranchType == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "name and branch_type are required"})
	}

	branch := &services.VersionBranch{
		ProjectID:   projectID,
		Name:        req.Name,
		Slug:        req.Slug,
		Description: req.Description,
		BranchType:  req.BranchType,
		Metadata:    req.Metadata,
		CreatedBy:   req.CreatedBy,
		Status:      "active",
		IsDefault:   false,
		IsProtected: false,
	}

	result, err := handler.temporalService.CreateBranch(ctx, branch)
	if err != nil {
		errMsg := "Failed to create branch: " + err.Error()
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": errMsg})
	}

	return c.JSON(http.StatusCreated, result)
}

// GetBranch handles requests to fetch a branch by ID.
func (h *TemporalHandler) GetBranch(c echo.Context) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	branchID := c.Param("branchId")
	ctx := c.Request().Context()

	result, err := h.temporalService.GetBranch(ctx, branchID)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Branch not found: " + err.Error()})
	}

	return c.JSON(http.StatusOK, result)
}

// ListBranches handles requests to list branches for a project.
func (handler *TemporalHandler) ListBranches(c echo.Context) error {
	if handler.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	projectID := c.Param("projectId")
	ctx := c.Request().Context()

	result, err := handler.temporalService.ListBranches(ctx, projectID)
	if err != nil {
		errMsg := "Failed to list branches: " + err.Error()
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": errMsg})
	}

	return c.JSON(http.StatusOK, result)
}

// UpdateBranch handles requests to update an existing branch.
func (h *TemporalHandler) UpdateBranch(c echo.Context) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	branchID := c.Param("branchId")
	ctx := c.Request().Context()

	var req struct {
		Name        string                 `json:"name,omitempty"`
		Description string                 `json:"description,omitempty"`
		Status      string                 `json:"status,omitempty"`
		IsProtected *bool                  `json:"is_protected,omitempty"`
		Metadata    map[string]interface{} `json:"metadata,omitempty"`
	}

	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body: " + err.Error()})
	}

	// Fetch existing branch first
	branch, err := h.temporalService.GetBranch(ctx, branchID)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Branch not found"})
	}

	// Update only provided fields
	if req.Name != "" {
		branch.Name = req.Name
	}
	if req.Description != "" {
		branch.Description = req.Description
	}
	if req.Status != "" {
		branch.Status = req.Status
	}
	if req.IsProtected != nil {
		branch.IsProtected = *req.IsProtected
	}
	if req.Metadata != nil {
		branch.Metadata = req.Metadata
	}

	result, err := h.temporalService.UpdateBranch(ctx, branch)
	if err != nil {
		errMsg := "Failed to update branch: " + err.Error()
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": errMsg})
	}

	return c.JSON(http.StatusOK, result)
}

// DeleteBranch handles requests to delete a branch.
func (handler *TemporalHandler) DeleteBranch(echoCtx echo.Context) error {
	if handler.temporalService == nil {
		return echoCtx.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	branchID := echoCtx.Param("branchId")
	ctx := echoCtx.Request().Context()

	err := handler.temporalService.DeleteBranch(ctx, branchID)
	if err != nil {
		errorResponse := map[string]string{"error": "Failed to delete branch: " + err.Error()}
		return echoCtx.JSON(http.StatusInternalServerError, errorResponse)
	}

	return echoCtx.NoContent(http.StatusNoContent)
}

// ============================================================================
// VERSION HANDLERS
// ============================================================================

// CreateVersion handles requests to create a new version.
func (h *TemporalHandler) CreateVersion(c echo.Context) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	branchID := c.Param("branchId")
	ctx := c.Request().Context()

	var req struct {
		ProjectID   string `json:"project_id"`
		Tag         string `json:"tag,omitempty"`
		Message     string `json:"message"`
		ChangeCount int    `json:"change_count,omitempty"`
		ItemCount   int    `json:"item_count,omitempty"`
		CreatedBy   string `json:"created_by"`
	}

	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body: " + err.Error()})
	}

	if req.Message == "" || req.ProjectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "message and project_id are required"})
	}

	version := &services.Version{
		BranchID:      branchID,
		ProjectID:     req.ProjectID,
		Message:       req.Message,
		Tag:           req.Tag,
		ChangeCount:   req.ChangeCount,
		ItemCount:     req.ItemCount,
		CreatedBy:     req.CreatedBy,
		Status:        "draft",
		VersionNumber: 1, // Will be incremented by service if needed
	}

	result, err := h.temporalService.CreateVersion(ctx, version)
	if err != nil {
		errMsg := "Failed to create version: " + err.Error()
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": errMsg})
	}

	return c.JSON(http.StatusCreated, result)
}

// GetVersion handles requests to fetch a version by ID.
func (h *TemporalHandler) GetVersion(c echo.Context) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	versionID := c.Param("versionId")
	ctx := c.Request().Context()

	result, err := h.temporalService.GetVersion(ctx, versionID)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Version not found: " + err.Error()})
	}

	return c.JSON(http.StatusOK, result)
}

// ListVersions handles requests to list versions for a branch.
func (handler *TemporalHandler) ListVersions(c echo.Context) error {
	if handler.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	branchID := c.Param("branchId")
	ctx := c.Request().Context()

	result, err := handler.temporalService.GetVersionsByBranch(ctx, branchID)
	if err != nil {
		errorResponse := map[string]string{"error": "Failed to list versions: " + err.Error()}
		return c.JSON(http.StatusInternalServerError, errorResponse)
	}

	return c.JSON(http.StatusOK, result)
}

// ApproveVersion handles requests to approve a version.
func (h *TemporalHandler) ApproveVersion(c echo.Context) error {
	return h.handleActionWithBodyField(
		c,
		"versionId",
		"approved_by",
		"approved_by is required",
		"Failed to approve version: ",
		"approved",
		h.temporalService.ApproveVersion,
	)
}

// RejectVersion handles requests to reject a version.
func (h *TemporalHandler) RejectVersion(c echo.Context) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	versionID := c.Param("versionId")
	ctx := c.Request().Context()

	var req struct {
		Reason string `json:"reason"`
	}

	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body: " + err.Error()})
	}

	err := h.temporalService.RejectVersion(ctx, versionID, req.Reason)
	if err != nil {
		errMsg := "Failed to reject version: " + err.Error()
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": errMsg})
	}

	return c.JSON(http.StatusOK, map[string]string{"status": "rejected"})
}

// ============================================================================
// ITEM VERSION HANDLERS
// ============================================================================

// GetItemVersion handles requests to fetch a specific item version.
func (h *TemporalHandler) GetItemVersion(c echo.Context) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	itemID := c.Param("itemId")
	versionID := c.Param("versionId")
	ctx := c.Request().Context()

	result, err := h.temporalService.GetItemVersion(ctx, itemID, versionID)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Item version not found: " + err.Error()})
	}

	return c.JSON(http.StatusOK, result)
}

// GetItemVersionHistory handles requests to fetch item version history.
func (h *TemporalHandler) GetItemVersionHistory(c echo.Context) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	itemID := c.Param("itemId")
	branchID := c.QueryParam("branch_id")
	ctx := c.Request().Context()

	if branchID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "branch_id query parameter is required"})
	}

	result, err := h.temporalService.GetItemVersionHistory(ctx, itemID, branchID)
	if err != nil {
		errorResponse := map[string]string{"error": "Failed to get item history: " + err.Error()}
		return c.JSON(http.StatusInternalServerError, errorResponse)
	}

	return c.JSON(http.StatusOK, result)
}

// RestoreItemVersion handles requests to restore a prior item version.
func (h *TemporalHandler) RestoreItemVersion(c echo.Context) error {
	return h.handleActionWithBodyField(
		c,
		"itemId",
		"version_id",
		"version_id is required",
		"Failed to restore item version: ",
		"restored",
		h.temporalService.RestoreItemVersion,
	)
}

// ============================================================================
// ALTERNATIVE HANDLERS
// ============================================================================

// ListAlternatives handles requests to list alternatives for an item.
func (h *TemporalHandler) ListAlternatives(c echo.Context) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	itemID := c.Param("itemId")
	ctx := c.Request().Context()

	result, err := h.temporalService.GetAlternatives(ctx, itemID)
	if err != nil {
		errMsg := "Failed to list alternatives: " + err.Error()
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": errMsg})
	}

	return c.JSON(http.StatusOK, result)
}

// CreateAlternative handles requests to create an alternative.
func (h *TemporalHandler) CreateAlternative(c echo.Context) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	itemID := c.Param("itemId")
	ctx := c.Request().Context()

	var req struct {
		AlternativeItemID string                 `json:"alternative_item_id"`
		Relationship      string                 `json:"relationship"`
		Description       string                 `json:"description,omitempty"`
		Metrics           map[string]interface{} `json:"metrics,omitempty"`
		ProjectID         string                 `json:"project_id"`
	}

	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body: " + err.Error()})
	}

	if req.AlternativeItemID == "" || req.Relationship == "" || req.ProjectID == "" {
		errorResponse := map[string]string{"error": "alternative_item_id, relationship, and project_id are required"}
		return c.JSON(http.StatusBadRequest, errorResponse)
	}

	alt := &services.ItemAlternative{
		ProjectID:         req.ProjectID,
		BaseItemID:        itemID,
		AlternativeItemID: req.AlternativeItemID,
		Relationship:      req.Relationship,
		Description:       req.Description,
		Metrics:           req.Metrics,
		IsChosen:          false,
	}

	result, err := h.temporalService.CreateAlternative(ctx, alt)
	if err != nil {
		errMsg := "Failed to create alternative: " + err.Error()
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": errMsg})
	}

	return c.JSON(http.StatusCreated, result)
}

// SelectAlternative handles requests to select an alternative.
func (h *TemporalHandler) SelectAlternative(c echo.Context) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	altID := c.Param("altId")
	ctx := c.Request().Context()

	var req struct {
		SelectedBy string `json:"selected_by"`
		Reason     string `json:"reason,omitempty"`
	}

	if err := c.Bind(&req); err != nil {
		errorResponse := map[string]string{"error": "Invalid request body: " + err.Error()}
		return c.JSON(http.StatusBadRequest, errorResponse)
	}

	if req.SelectedBy == "" {
		errorResponse := map[string]string{"error": "selected_by is required"}
		return c.JSON(http.StatusBadRequest, errorResponse)
	}

	err := h.temporalService.SelectAlternative(ctx, altID, req.SelectedBy, req.Reason)
	if err != nil {
		errMsg := "Failed to select alternative: " + err.Error()
		errorResponse := map[string]string{"error": errMsg}
		return c.JSON(http.StatusInternalServerError, errorResponse)
	}

	return c.JSON(http.StatusOK, map[string]string{"status": "selected"})
}

// ============================================================================
// MERGE REQUEST HANDLERS
// ============================================================================

// CreateMergeRequest handles requests to create a merge request.
func (h *TemporalHandler) CreateMergeRequest(c echo.Context) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	projectID := c.Param("projectId")
	ctx := c.Request().Context()

	var req struct {
		SourceBranchID string   `json:"source_branch_id"`
		TargetBranchID string   `json:"target_branch_id"`
		Title          string   `json:"title"`
		Description    string   `json:"description,omitempty"`
		Reviewers      []string `json:"reviewers,omitempty"`
		CreatedBy      string   `json:"created_by"`
	}

	if err := c.Bind(&req); err != nil {
		errorResponse := map[string]string{"error": "Invalid request body: " + err.Error()}
		return c.JSON(http.StatusBadRequest, errorResponse)
	}

	if req.SourceBranchID == "" || req.TargetBranchID == "" || req.Title == "" {
		errMsg := "source_branch_id, target_branch_id, and title are required"
		errorResponse := map[string]string{"error": errMsg}
		return c.JSON(http.StatusBadRequest, errorResponse)
	}

	mr := &services.MergeRequest{
		ID:              "",
		ProjectID:       projectID,
		SourceBranchID:  req.SourceBranchID,
		TargetBranchID:  req.TargetBranchID,
		SourceVersionID: "",
		BaseVersionID:   "",
		Status:          "open",
		Title:           req.Title,
		Description:     req.Description,
		Diff:            nil,
		Conflicts:       nil,
		Reviewers:       req.Reviewers,
		ApprovedBy:      nil,
		CreatedBy:       req.CreatedBy,
		CreatedAt:       time.Time{},
		MergedAt:        nil,
		MergedBy:        "",
		ClosedAt:        nil,
		UpdatedAt:       time.Time{},
	}

	result, err := h.temporalService.CreateMergeRequest(ctx, mr)
	if err != nil {
		errorResponse := map[string]string{"error": "Failed to create merge request: " + err.Error()}
		return c.JSON(http.StatusInternalServerError, errorResponse)
	}

	return c.JSON(http.StatusCreated, result)
}

// GetMergeRequest handles requests to fetch a merge request by ID.
func (h *TemporalHandler) GetMergeRequest(c echo.Context) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	mrID := c.Param("mrId")
	ctx := c.Request().Context()

	result, err := h.temporalService.GetMergeRequest(ctx, mrID)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Merge request not found: " + err.Error()})
	}

	return c.JSON(http.StatusOK, result)
}

// ListMergeRequests handles requests to list merge requests for a branch.
func (handler *TemporalHandler) ListMergeRequests(c echo.Context) error {
	if handler.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	projectID := c.Param("projectId")
	status := c.QueryParam("status")
	ctx := c.Request().Context()

	result, err := handler.temporalService.ListMergeRequests(ctx, projectID, status)
	if err != nil {
		errMsg := "Failed to list merge requests: " + err.Error()
		errorResponse := map[string]string{"error": errMsg}
		return c.JSON(http.StatusInternalServerError, errorResponse)
	}

	return c.JSON(http.StatusOK, result)
}

// GetMergeDiff handles requests to fetch a merge diff.
func (h *TemporalHandler) GetMergeDiff(c echo.Context) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	mrID := c.Param("mrId")
	ctx := c.Request().Context()

	result, err := h.temporalService.ComputeMergeDiff(ctx, mrID)
	if err != nil {
		errMsg := "Failed to compute diff: " + err.Error()
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": errMsg})
	}

	return c.JSON(http.StatusOK, result)
}

// MergeBranches handles requests to merge branches.
func (h *TemporalHandler) MergeBranches(c echo.Context) error {
	return h.handleActionWithBodyField(
		c,
		"mrId",
		"merged_by",
		"merged_by is required",
		"Failed to merge branches: ",
		"merged",
		h.temporalService.MergeBranches,
	)
}

func (h *TemporalHandler) handleActionWithBodyField(
	c echo.Context,
	idParam string,
	fieldKey string,
	requiredMsg string,
	failureMsg string,
	successStatus string,
	action func(ctx context.Context, id string, value string) error,
) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	id := c.Param(idParam)
	ctx := c.Request().Context()

	var req map[string]string
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body: " + err.Error()})
	}

	value := strings.TrimSpace(req[fieldKey])
	if value == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": requiredMsg})
	}

	if err := action(ctx, id, value); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": failureMsg + err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]string{"status": successStatus})
}

// ============================================================================
// VERSION COMPARISON HANDLERS
// ============================================================================

// CompareVersions handles requests to compare versions.
func (h *TemporalHandler) CompareVersions(c echo.Context) error {
	if h.temporalService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "Temporal service not available"})
	}

	versionAID := c.Param("versionAId")
	versionBID := c.Param("versionBId")
	ctx := c.Request().Context()

	result, err := h.temporalService.ComparVersions(ctx, versionAID, versionBID)
	if err != nil {
		errorResponse := map[string]string{"error": "Failed to compare versions: " + err.Error()}
		return c.JSON(http.StatusInternalServerError, errorResponse)
	}

	return c.JSON(http.StatusOK, result)
}
