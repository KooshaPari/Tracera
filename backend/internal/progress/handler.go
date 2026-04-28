// Package progress provides HTTP handlers and types for milestones, sprints, and progress metrics.
package progress

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"strconv"

	"github.com/google/uuid"
	"github.com/gorilla/mux"
)

// Handler handles HTTP requests for progress endpoints
type Handler struct {
	milestoneService MilestoneService
	sprintService    SprintService
	metricsService   MetricsService
	snapshotService  SnapshotService
}

// NewHandler creates a new progress handler
func NewHandler(
	milestoneService MilestoneService,
	sprintService SprintService,
	metricsService MetricsService,
	snapshotService SnapshotService,
) *Handler {
	return &Handler{
		milestoneService: milestoneService,
		sprintService:    sprintService,
		metricsService:   metricsService,
		snapshotService:  snapshotService,
	}
}

// RegisterRoutes registers all progress-related routes
func (h *Handler) RegisterRoutes(router *mux.Router, basePath string) {
	// Milestone routes
	router.HandleFunc(basePath+"/milestones", h.ListMilestones).Methods("GET")
	router.HandleFunc(basePath+"/milestones", h.CreateMilestone).Methods("POST")
	router.HandleFunc(basePath+"/milestones/{id}", h.GetMilestone).Methods("GET")
	router.HandleFunc(basePath+"/milestones/{id}", h.UpdateMilestone).Methods("PUT")
	router.HandleFunc(basePath+"/milestones/{id}", h.DeleteMilestone).Methods("DELETE")
	router.HandleFunc(basePath+"/milestones/{id}/progress", h.GetMilestoneProgress).Methods("GET")
	router.HandleFunc(basePath+"/milestones/{id}/health", h.UpdateMilestoneHealth).Methods("POST")
	router.HandleFunc(basePath+"/milestones/{id}/items/{itemId}", h.AddItemToMilestone).Methods("POST")
	router.HandleFunc(basePath+"/milestones/{id}/items/{itemId}", h.RemoveItemFromMilestone).Methods("DELETE")

	// Sprint routes
	router.HandleFunc(basePath+"/sprints", h.ListSprints).Methods("GET")
	router.HandleFunc(basePath+"/sprints", h.CreateSprint).Methods("POST")
	router.HandleFunc(basePath+"/sprints/{id}", h.GetSprint).Methods("GET")
	router.HandleFunc(basePath+"/sprints/{id}", h.UpdateSprint).Methods("PUT")
	router.HandleFunc(basePath+"/sprints/{id}", h.DeleteSprint).Methods("DELETE")
	router.HandleFunc(basePath+"/sprints/{id}/close", h.CloseSprint).Methods("POST")
	router.HandleFunc(basePath+"/sprints/{id}/burndown", h.RecordBurndown).Methods("POST")
	router.HandleFunc(basePath+"/sprints/{id}/health", h.UpdateSprintHealth).Methods("POST")
	router.HandleFunc(basePath+"/sprints/{id}/items/{itemId}", h.AddItemToSprint).Methods("POST")
	router.HandleFunc(basePath+"/sprints/{id}/items/{itemId}", h.RemoveItemFromSprint).Methods("DELETE")

	// Metrics routes
	router.HandleFunc(basePath+"/metrics", h.GetProjectMetrics).Methods("GET")
	router.HandleFunc(basePath+"/metrics/velocity", h.GetVelocity).Methods("GET")
	router.HandleFunc(basePath+"/metrics/velocity/history", h.GetVelocityHistory).Methods("GET")
	router.HandleFunc(basePath+"/metrics/cycle-time", h.GetCycleTime).Methods("GET")

	// Snapshot routes
	router.HandleFunc(basePath+"/snapshots", h.ListSnapshots).Methods("GET")
	router.HandleFunc(basePath+"/snapshots", h.CreateSnapshot).Methods("POST")
	router.HandleFunc(basePath+"/snapshots/{id}", h.GetSnapshot).Methods("GET")
}

func writeJSON(w http.ResponseWriter, payload interface{}) {
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(payload); err != nil {
		http.Error(w, "failed to encode response", http.StatusInternalServerError)
	}
}

func parseProjectID(r *http.Request) (uuid.UUID, error) {
	projectID := r.URL.Query().Get("project_id")
	if projectID == "" {
		return uuid.Nil, errors.New("project_id is required")
	}

	projID, err := uuid.Parse(projectID)
	if err != nil {
		return uuid.Nil, errors.New("invalid project_id")
	}

	return projID, nil
}

func (h *Handler) createWithProjectID(
	w http.ResponseWriter,
	r *http.Request,
	decode func() error,
	create func(context.Context, uuid.UUID) (interface{}, error),
) {
	if err := decode(); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	projID, err := parseProjectID(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	result, err := create(r.Context(), projID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	writeJSON(w, result)
}

// Milestone Handlers

// ListMilestones returns all milestones for a project (query: project_id).
func (h *Handler) ListMilestones(w http.ResponseWriter, r *http.Request) {
	projectID := r.URL.Query().Get("project_id")
	if projectID == "" {
		http.Error(w, "project_id is required", http.StatusBadRequest)
		return
	}

	projID, err := uuid.Parse(projectID)
	if err != nil {
		http.Error(w, "invalid project_id", http.StatusBadRequest)
		return
	}

	milestones, err := h.milestoneService.GetMilestones(r.Context(), projID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	writeJSON(w, milestones)
}

// CreateMilestone creates a new milestone (query: project_id, body: CreateMilestoneRequest).
func (h *Handler) CreateMilestone(w http.ResponseWriter, r *http.Request) {
	var req CreateMilestoneRequest
	h.createWithProjectID(
		w,
		r,
		func() error { return json.NewDecoder(r.Body).Decode(&req) },
		func(ctx context.Context, projID uuid.UUID) (interface{}, error) {
			return h.milestoneService.CreateMilestone(ctx, projID, &req)
		},
	)
}

// GetMilestone returns a single milestone by ID.
func (h *Handler) GetMilestone(w http.ResponseWriter, r *http.Request) {
	idStr := mux.Vars(r)["id"]
	id, err := uuid.Parse(idStr)
	if err != nil {
		http.Error(w, "invalid id", http.StatusBadRequest)
		return
	}

	milestone, err := h.milestoneService.GetMilestone(r.Context(), id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	writeJSON(w, milestone)
}

// UpdateMilestone updates an existing milestone by ID.
func (h *Handler) UpdateMilestone(w http.ResponseWriter, r *http.Request) {
	idStr := mux.Vars(r)["id"]
	id, err := uuid.Parse(idStr)
	if err != nil {
		http.Error(w, "invalid id", http.StatusBadRequest)
		return
	}

	var req UpdateMilestoneRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	milestone, err := h.milestoneService.UpdateMilestone(r.Context(), id, &req)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	writeJSON(w, milestone)
}

// DeleteMilestone deletes a milestone by ID.
func (h *Handler) DeleteMilestone(w http.ResponseWriter, r *http.Request) {
	idStr := mux.Vars(r)["id"]
	id, err := uuid.Parse(idStr)
	if err != nil {
		http.Error(w, "invalid id", http.StatusBadRequest)
		return
	}

	err = h.milestoneService.DeleteMilestone(r.Context(), id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// GetMilestoneProgress returns progress metrics for a milestone.
func (h *Handler) GetMilestoneProgress(w http.ResponseWriter, r *http.Request) {
	idStr := mux.Vars(r)["id"]
	id, err := uuid.Parse(idStr)
	if err != nil {
		http.Error(w, "invalid id", http.StatusBadRequest)
		return
	}

	progress, err := h.milestoneService.GetMilestoneProgress(r.Context(), id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	writeJSON(w, progress)
}

// UpdateMilestoneHealth updates the health status of a milestone.
func (h *Handler) UpdateMilestoneHealth(w http.ResponseWriter, r *http.Request) {
	idStr := mux.Vars(r)["id"]
	id, err := uuid.Parse(idStr)
	if err != nil {
		http.Error(w, "invalid id", http.StatusBadRequest)
		return
	}

	err = h.milestoneService.UpdateMilestoneHealth(r.Context(), id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// AddItemToMilestone links an item to a milestone.
func (h *Handler) AddItemToMilestone(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	milestoneID, err := uuid.Parse(vars["id"])
	if err != nil {
		http.Error(w, "invalid milestone id", http.StatusBadRequest)
		return
	}

	itemID, err := uuid.Parse(vars["itemId"])
	if err != nil {
		http.Error(w, "invalid item id", http.StatusBadRequest)
		return
	}

	err = h.milestoneService.AddItemToMilestone(r.Context(), milestoneID, itemID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

// RemoveItemFromMilestone unlinks an item from a milestone.
func (h *Handler) RemoveItemFromMilestone(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	milestoneID, err := uuid.Parse(vars["id"])
	if err != nil {
		http.Error(w, "invalid milestone id", http.StatusBadRequest)
		return
	}

	itemID, err := uuid.Parse(vars["itemId"])
	if err != nil {
		http.Error(w, "invalid item id", http.StatusBadRequest)
		return
	}

	err = h.milestoneService.RemoveItemFromMilestone(r.Context(), milestoneID, itemID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// Sprint Handlers

// ListSprints returns all sprints for a project (query: project_id).
func (h *Handler) ListSprints(w http.ResponseWriter, r *http.Request) {
	projectID := r.URL.Query().Get("project_id")
	if projectID == "" {
		http.Error(w, "project_id is required", http.StatusBadRequest)
		return
	}

	projID, err := uuid.Parse(projectID)
	if err != nil {
		http.Error(w, "invalid project_id", http.StatusBadRequest)
		return
	}

	sprints, err := h.sprintService.GetSprints(r.Context(), projID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	writeJSON(w, sprints)
}

// CreateSprint creates a new sprint (query: project_id, body: CreateSprintRequest).
func (h *Handler) CreateSprint(w http.ResponseWriter, r *http.Request) {
	var req CreateSprintRequest
	h.createWithProjectID(
		w,
		r,
		func() error { return json.NewDecoder(r.Body).Decode(&req) },
		func(ctx context.Context, projID uuid.UUID) (interface{}, error) {
			return h.sprintService.CreateSprint(ctx, projID, &req)
		},
	)
}

// GetSprint returns a single sprint by ID.
func (h *Handler) GetSprint(w http.ResponseWriter, r *http.Request) {
	idStr := mux.Vars(r)["id"]
	id, err := uuid.Parse(idStr)
	if err != nil {
		http.Error(w, "invalid id", http.StatusBadRequest)
		return
	}

	sprint, err := h.sprintService.GetSprint(r.Context(), id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	writeJSON(w, sprint)
}

// UpdateSprint updates an existing sprint by ID.
func (h *Handler) UpdateSprint(w http.ResponseWriter, r *http.Request) {
	idStr := mux.Vars(r)["id"]
	id, err := uuid.Parse(idStr)
	if err != nil {
		http.Error(w, "invalid id", http.StatusBadRequest)
		return
	}

	var req UpdateSprintRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sprint, err := h.sprintService.UpdateSprint(r.Context(), id, &req)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	writeJSON(w, sprint)
}

// DeleteSprint deletes a sprint by ID.
func (h *Handler) DeleteSprint(w http.ResponseWriter, r *http.Request) {
	idStr := mux.Vars(r)["id"]
	id, err := uuid.Parse(idStr)
	if err != nil {
		http.Error(w, "invalid id", http.StatusBadRequest)
		return
	}

	err = h.sprintService.DeleteSprint(r.Context(), id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// CloseSprint marks a sprint as closed.
func (h *Handler) CloseSprint(w http.ResponseWriter, r *http.Request) {
	idStr := mux.Vars(r)["id"]
	id, err := uuid.Parse(idStr)
	if err != nil {
		http.Error(w, "invalid id", http.StatusBadRequest)
		return
	}

	err = h.sprintService.CloseSprint(r.Context(), id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// RecordBurndown records a burndown data point for a sprint.
func (h *Handler) RecordBurndown(w http.ResponseWriter, r *http.Request) {
	idStr := mux.Vars(r)["id"]
	id, err := uuid.Parse(idStr)
	if err != nil {
		http.Error(w, "invalid id", http.StatusBadRequest)
		return
	}

	err = h.sprintService.RecordBurndown(r.Context(), id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// UpdateSprintHealth updates the health status of a sprint.
func (h *Handler) UpdateSprintHealth(w http.ResponseWriter, r *http.Request) {
	idStr := mux.Vars(r)["id"]
	id, err := uuid.Parse(idStr)
	if err != nil {
		http.Error(w, "invalid id", http.StatusBadRequest)
		return
	}

	err = h.sprintService.UpdateSprintHealth(r.Context(), id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// AddItemToSprint links an item to a sprint.
func (h *Handler) AddItemToSprint(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	sprintID, err := uuid.Parse(vars["id"])
	if err != nil {
		http.Error(w, "invalid sprint id", http.StatusBadRequest)
		return
	}

	itemID, err := uuid.Parse(vars["itemId"])
	if err != nil {
		http.Error(w, "invalid item id", http.StatusBadRequest)
		return
	}

	err = h.sprintService.AddItemToSprint(r.Context(), sprintID, itemID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

// RemoveItemFromSprint unlinks an item from a sprint.
func (h *Handler) RemoveItemFromSprint(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	sprintID, err := uuid.Parse(vars["id"])
	if err != nil {
		http.Error(w, "invalid sprint id", http.StatusBadRequest)
		return
	}

	itemID, err := uuid.Parse(vars["itemId"])
	if err != nil {
		http.Error(w, "invalid item id", http.StatusBadRequest)
		return
	}

	err = h.sprintService.RemoveItemFromSprint(r.Context(), sprintID, itemID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// Metrics Handlers

// GetProjectMetrics returns aggregated project metrics (query: project_id).
func (h *Handler) GetProjectMetrics(w http.ResponseWriter, r *http.Request) {
	projectID := r.URL.Query().Get("project_id")
	if projectID == "" {
		http.Error(w, "project_id is required", http.StatusBadRequest)
		return
	}

	projID, err := uuid.Parse(projectID)
	if err != nil {
		http.Error(w, "invalid project_id", http.StatusBadRequest)
		return
	}

	metrics, err := h.metricsService.CalculateProjectMetrics(r.Context(), projID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	writeJSON(w, metrics)
}

// GetVelocity returns velocity for a project (query: project_id, optional periods).
func (h *Handler) GetVelocity(w http.ResponseWriter, r *http.Request) {
	projectID := r.URL.Query().Get("project_id")
	if projectID == "" {
		http.Error(w, "project_id is required", http.StatusBadRequest)
		return
	}

	projID, err := uuid.Parse(projectID)
	if err != nil {
		http.Error(w, "invalid project_id", http.StatusBadRequest)
		return
	}

	periods := 3
	if p := r.URL.Query().Get("periods"); p != "" {
		if parsedP, err := strconv.Atoi(p); err == nil {
			periods = parsedP
		}
	}

	velocity, err := h.metricsService.CalculateVelocity(r.Context(), projID, periods)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	writeJSON(w, map[string]float64{"velocity": velocity})
}

// GetVelocityHistory returns historical velocity data for a project.
func (h *Handler) GetVelocityHistory(w http.ResponseWriter, r *http.Request) {
	projectID := r.URL.Query().Get("project_id")
	if projectID == "" {
		http.Error(w, "project_id is required", http.StatusBadRequest)
		return
	}

	projID, err := uuid.Parse(projectID)
	if err != nil {
		http.Error(w, "invalid project_id", http.StatusBadRequest)
		return
	}

	history, err := h.metricsService.GetVelocityHistory(r.Context(), projID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	writeJSON(w, history)
}

// GetCycleTime returns average cycle time for a project.
func (h *Handler) GetCycleTime(w http.ResponseWriter, r *http.Request) {
	projectID := r.URL.Query().Get("project_id")
	if projectID == "" {
		http.Error(w, "project_id is required", http.StatusBadRequest)
		return
	}

	projID, err := uuid.Parse(projectID)
	if err != nil {
		http.Error(w, "invalid project_id", http.StatusBadRequest)
		return
	}

	cycleTime, err := h.metricsService.CalculateCycleTime(r.Context(), projID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	writeJSON(w, map[string]float64{"cycle_time_days": cycleTime})
}

// Snapshot Handlers

// ListSnapshots returns progress snapshots for a project (query: project_id, optional limit).
func (h *Handler) ListSnapshots(w http.ResponseWriter, r *http.Request) {
	projectID := r.URL.Query().Get("project_id")
	if projectID == "" {
		http.Error(w, "project_id is required", http.StatusBadRequest)
		return
	}

	projID, err := uuid.Parse(projectID)
	if err != nil {
		http.Error(w, "invalid project_id", http.StatusBadRequest)
		return
	}

	limit := 30
	if l := r.URL.Query().Get("limit"); l != "" {
		if parsedL, err := strconv.Atoi(l); err == nil {
			limit = parsedL
		}
	}

	snapshots, err := h.snapshotService.GetSnapshots(r.Context(), projID, limit)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	writeJSON(w, snapshots)
}

// CreateSnapshot creates a new progress snapshot for a project (query: project_id).
func (h *Handler) CreateSnapshot(w http.ResponseWriter, r *http.Request) {
	projectID := r.URL.Query().Get("project_id")
	if projectID == "" {
		http.Error(w, "project_id is required", http.StatusBadRequest)
		return
	}

	projID, err := uuid.Parse(projectID)
	if err != nil {
		http.Error(w, "invalid project_id", http.StatusBadRequest)
		return
	}

	snapshot, err := h.snapshotService.RecordDailySnapshot(r.Context(), projID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	writeJSON(w, snapshot)
}

// GetSnapshot returns a single progress snapshot by ID.
func (h *Handler) GetSnapshot(w http.ResponseWriter, r *http.Request) {
	idStr := mux.Vars(r)["id"]
	id, err := uuid.Parse(idStr)
	if err != nil {
		http.Error(w, "invalid id", http.StatusBadRequest)
		return
	}

	snapshot, err := h.snapshotService.GetSnapshot(r.Context(), id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	writeJSON(w, snapshot)
}
