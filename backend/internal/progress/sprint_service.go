package progress

import (
	"context"
	"database/sql"
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

const (
	sprintHoursPerDay  = 24
	sprintPercentScale = 100
	sprintLagSevere    = 20
	sprintLagWarning   = 10
)

// SprintRepository defines storage operations for sprints
type SprintRepository interface {
	CreateSprint(ctx context.Context, sprint *Sprint) (*Sprint, error)
	GetSprintByID(ctx context.Context, id uuid.UUID) (*Sprint, error)
	GetSprintsByProject(ctx context.Context, projectID uuid.UUID) ([]Sprint, error)
	GetActiveSprint(ctx context.Context, projectID uuid.UUID) (*Sprint, error)
	UpdateSprint(ctx context.Context, sprint *Sprint) (*Sprint, error)
	DeleteSprint(ctx context.Context, id uuid.UUID) error
	AddItemToSprint(ctx context.Context, sprintID, itemID uuid.UUID) error
	RemoveItemFromSprint(ctx context.Context, sprintID, itemID uuid.UUID) error
	GetSprintItems(ctx context.Context, sprintID uuid.UUID) ([]uuid.UUID, error)
	AddBurndownData(ctx context.Context, sprintID uuid.UUID, data *BurndownDataPoint) error
	GetBurndownData(ctx context.Context, sprintID uuid.UUID) ([]BurndownDataPoint, error)
}

// SprintService provides business logic for sprint management
type SprintService interface {
	CreateSprint(ctx context.Context, projectID uuid.UUID, req *CreateSprintRequest) (*Sprint, error)
	GetSprint(ctx context.Context, id uuid.UUID) (*Sprint, error)
	GetSprints(ctx context.Context, projectID uuid.UUID) ([]Sprint, error)
	GetActiveSprint(ctx context.Context, projectID uuid.UUID) (*Sprint, error)
	UpdateSprint(ctx context.Context, id uuid.UUID, req *UpdateSprintRequest) (*Sprint, error)
	DeleteSprint(ctx context.Context, id uuid.UUID) error
	AddItemToSprint(ctx context.Context, sprintID, itemID uuid.UUID) error
	RemoveItemFromSprint(ctx context.Context, sprintID, itemID uuid.UUID) error
	RecordBurndown(ctx context.Context, sprintID uuid.UUID) error
	UpdateSprintHealth(ctx context.Context, sprintID uuid.UUID) error
	CloseSprint(ctx context.Context, sprintID uuid.UUID) error
}

type sprintService struct {
	repo SprintRepository
	db   *sql.DB
}

// NewSprintService creates a new sprint service
func NewSprintService(repo SprintRepository, db *sql.DB) SprintService {
	return &sprintService{
		repo: repo,
		db:   db,
	}
}

func (s *sprintService) CreateSprint(ctx context.Context, projectID uuid.UUID, req *CreateSprintRequest) (*Sprint, error) {
	durationDays := int(req.EndDate.Sub(req.StartDate).Hours() / sprintHoursPerDay)

	sprint := &Sprint{
		ID:              uuid.New(),
		ProjectID:       projectID,
		Name:            req.Name,
		Slug:            req.Slug,
		Goal:            req.Goal,
		StartDate:       req.StartDate,
		EndDate:         req.EndDate,
		Status:          SprintPlanning,
		Health:          HealthUnknown,
		PlannedCapacity: req.PlannedCapacity,
		ActualCapacity:  req.ActualCapacity,
		PlannedPoints:   0,
		CompletedPoints: 0,
		RemainingPoints: 0,
		CreatedAt:       time.Now(),
		UpdatedAt:       time.Now(),
	}

	// Store duration as metadata
	metadata := map[string]interface{}{
		"duration_days": durationDays,
	}
	if metadataJSON, err := json.Marshal(metadata); err == nil {
		sprint.Metadata = metadataJSON
	}

	return s.repo.CreateSprint(ctx, sprint)
}

func (s *sprintService) GetSprint(ctx context.Context, id uuid.UUID) (*Sprint, error) {
	return s.repo.GetSprintByID(ctx, id)
}

func (s *sprintService) GetSprints(ctx context.Context, projectID uuid.UUID) ([]Sprint, error) {
	return s.repo.GetSprintsByProject(ctx, projectID)
}

func (s *sprintService) GetActiveSprint(ctx context.Context, projectID uuid.UUID) (*Sprint, error) {
	return s.repo.GetActiveSprint(ctx, projectID)
}

// applySprintUpdate applies non-nil fields from the update request to the sprint.
func applySprintUpdate(sp *Sprint, req *UpdateSprintRequest) {
	if req.Name != nil {
		sp.Name = *req.Name
	}
	if req.Slug != nil {
		sp.Slug = *req.Slug
	}
	if req.Goal != nil {
		sp.Goal = req.Goal
	}
	if req.Status != nil {
		sp.Status = *req.Status
	}
	if req.Health != nil {
		sp.Health = *req.Health
	}
	if req.PlannedCapacity != nil {
		sp.PlannedCapacity = req.PlannedCapacity
	}
	if req.ActualCapacity != nil {
		sp.ActualCapacity = req.ActualCapacity
	}
	if req.PlannedPoints != nil {
		sp.PlannedPoints = *req.PlannedPoints
	}
	if req.CompletedPoints != nil {
		sp.CompletedPoints = *req.CompletedPoints
		sp.RemainingPoints = sp.PlannedPoints - sp.CompletedPoints
	}
	sp.UpdatedAt = time.Now()
}

func (s *sprintService) UpdateSprint(ctx context.Context, id uuid.UUID, req *UpdateSprintRequest) (*Sprint, error) {
	sprint, err := s.repo.GetSprintByID(ctx, id)
	if err != nil {
		return nil, err
	}
	applySprintUpdate(sprint, req)
	return s.repo.UpdateSprint(ctx, sprint)
}

func (s *sprintService) DeleteSprint(ctx context.Context, id uuid.UUID) error {
	now := time.Now()
	sprint, err := s.repo.GetSprintByID(ctx, id)
	if err != nil {
		return err
	}

	sprint.DeletedAt = &now
	_, err = s.repo.UpdateSprint(ctx, sprint)
	return err
}

func (s *sprintService) AddItemToSprint(ctx context.Context, sprintID, itemID uuid.UUID) error {
	return s.repo.AddItemToSprint(ctx, sprintID, itemID)
}

func (s *sprintService) RemoveItemFromSprint(ctx context.Context, sprintID, itemID uuid.UUID) error {
	return s.repo.RemoveItemFromSprint(ctx, sprintID, itemID)
}

func (s *sprintService) RecordBurndown(ctx context.Context, sprintID uuid.UUID) error {
	sprint, err := s.repo.GetSprintByID(ctx, sprintID)
	if err != nil {
		return err
	}

	itemIDs, err := s.repo.GetSprintItems(ctx, sprintID)
	if err != nil {
		return err
	}

	// Calculate remaining points
	remainingPoints, err := s.calculateRemainingPoints(ctx, itemIDs)
	if err != nil {
		return err
	}

	// Calculate ideal burndown line
	now := time.Now()
	totalDuration := sprint.EndDate.Sub(sprint.StartDate).Hours() / sprintHoursPerDay
	elapsedDuration := now.Sub(sprint.StartDate).Hours() / sprintHoursPerDay
	progressRatio := elapsedDuration / totalDuration

	idealPoints := int(float64(sprint.PlannedPoints) * (1 - progressRatio))
	if idealPoints < 0 {
		idealPoints = 0
	}

	dataPoint := &BurndownDataPoint{
		RecordedDate:    now,
		RemainingPoints: remainingPoints,
		IdealPoints:     idealPoints,
		CompletedPoints: sprint.CompletedPoints,
	}

	return s.repo.AddBurndownData(ctx, sprintID, dataPoint)
}

func (s *sprintService) UpdateSprintHealth(ctx context.Context, sprintID uuid.UUID) error {
	sprint, err := s.repo.GetSprintByID(ctx, sprintID)
	if err != nil {
		return err
	}

	now := time.Now()
	daysRemaining := int(sprint.EndDate.Sub(now).Hours() / sprintHoursPerDay)

	// Calculate health based on burndown progress
	totalDuration := int(sprint.EndDate.Sub(sprint.StartDate).Hours() / sprintHoursPerDay)
	if totalDuration == 0 {
		totalDuration = 1
	}

	expectedCompletion := (totalDuration - daysRemaining) * sprintPercentScale / totalDuration
	actualCompletion := 0
	if sprint.PlannedPoints > 0 {
		actualCompletion = (sprint.CompletedPoints * sprintPercentScale) / sprint.PlannedPoints
	}

	var health HealthStatus
	switch {
	case actualCompletion < (expectedCompletion - sprintLagSevere):
		health = HealthRed
	case actualCompletion < (expectedCompletion - sprintLagWarning):
		health = HealthYellow
	default:
		health = HealthGreen
	}

	sprint.Health = health
	sprint.UpdatedAt = time.Now()

	_, err = s.repo.UpdateSprint(ctx, sprint)
	return err
}

func (s *sprintService) CloseSprint(ctx context.Context, sprintID uuid.UUID) error {
	sprint, err := s.repo.GetSprintByID(ctx, sprintID)
	if err != nil {
		return err
	}

	now := time.Now()
	sprint.Status = SprintCompleted
	sprint.CompletedAt = &now
	sprint.UpdatedAt = now

	_, err = s.repo.UpdateSprint(ctx, sprint)
	return err
}

func (s *sprintService) calculateRemainingPoints(ctx context.Context, itemIDs []uuid.UUID) (int, error) {
	if len(itemIDs) == 0 {
		return 0, nil
	}

	query := `
		SELECT COALESCE(SUM(points), 0)
		FROM items
		WHERE id = ANY($1) AND status != 'done' AND deleted_at IS NULL
	`

	var remainingPoints int
	err := s.db.QueryRowContext(ctx, query, itemIDs).Scan(&remainingPoints)
	return remainingPoints, err
}
