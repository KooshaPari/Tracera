package progress

import (
	"context"
	"database/sql"
	"fmt"
	"log/slog"
	"time"

	"github.com/google/uuid"
)

const (
	milestonePercentScale          = 100
	milestonePercentScaleFloat     = 100.0
	milestoneHealthRiskRed         = 70
	milestoneHealthRiskYellow      = 40
	milestoneProgressRatioRed      = 0.5
	milestoneProgressRatioYellow   = 0.8
	milestoneProgressBehindFactor  = 0.8
	milestoneHoursPerDay           = 24
	milestoneRiskScoreOverdue      = 30
	milestoneRiskScoreLowVelocity  = 20
	milestoneRiskScoreBlockedItems = 25
	milestoneRiskScoreMax          = 100
)

// MilestoneRepository defines storage operations for milestones
type MilestoneRepository interface {
	CreateMilestone(ctx context.Context, milestone *Milestone) (*Milestone, error)
	GetMilestoneByID(ctx context.Context, id uuid.UUID) (*Milestone, error)
	GetMilestonesByProject(ctx context.Context, projectID uuid.UUID) ([]Milestone, error)
	UpdateMilestone(ctx context.Context, milestone *Milestone) (*Milestone, error)
	DeleteMilestone(ctx context.Context, id uuid.UUID) error
	GetMilestonesByParent(ctx context.Context, parentID uuid.UUID) ([]Milestone, error)
	AddItemToMilestone(ctx context.Context, milestoneID, itemID uuid.UUID) error
	RemoveItemFromMilestone(ctx context.Context, milestoneID, itemID uuid.UUID) error
	GetMilestoneItems(ctx context.Context, milestoneID uuid.UUID) ([]uuid.UUID, error)
	UpdateMilestoneRisk(ctx context.Context, milestoneID uuid.UUID, riskScore int, riskFactors []RiskFactor) error
}

// MilestoneService provides business logic for milestone management
type MilestoneService interface {
	CreateMilestone(ctx context.Context, projectID uuid.UUID, req *CreateMilestoneRequest) (*Milestone, error)
	GetMilestone(ctx context.Context, id uuid.UUID) (*Milestone, error)
	GetMilestones(ctx context.Context, projectID uuid.UUID) ([]Milestone, error)
	GetMilestoneHierarchy(ctx context.Context, projectID uuid.UUID) ([]Milestone, error)
	UpdateMilestone(ctx context.Context, id uuid.UUID, req *UpdateMilestoneRequest) (*Milestone, error)
	DeleteMilestone(ctx context.Context, id uuid.UUID) error
	AddItemToMilestone(ctx context.Context, milestoneID, itemID uuid.UUID) error
	RemoveItemFromMilestone(ctx context.Context, milestoneID, itemID uuid.UUID) error
	GetMilestoneProgress(ctx context.Context, milestoneID uuid.UUID) (*MilestoneProgress, error)
	UpdateMilestoneHealth(ctx context.Context, milestoneID uuid.UUID) error
	ComputeRiskFactors(ctx context.Context, milestoneID uuid.UUID) ([]RiskFactor, int, error)
}

type milestoneService struct {
	repo MilestoneRepository
	db   *sql.DB
}

// NewMilestoneService creates a new milestone service
func NewMilestoneService(repo MilestoneRepository, db *sql.DB) MilestoneService {
	return &milestoneService{
		repo: repo,
		db:   db,
	}
}

func (s *milestoneService) CreateMilestone(ctx context.Context, projectID uuid.UUID, req *CreateMilestoneRequest) (*Milestone, error) {
	milestone := &Milestone{
		ID:          uuid.New(),
		ProjectID:   projectID,
		Name:        req.Name,
		Slug:        req.Slug,
		Description: req.Description,
		Objective:   req.Objective,
		StartDate:   req.StartDate,
		TargetDate:  req.TargetDate,
		ParentID:    req.ParentID,
		OwnerID:     req.OwnerID,
		Status:      MilestoneNotStarted,
		Health:      HealthUnknown,
		RiskScore:   0,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	return s.repo.CreateMilestone(ctx, milestone)
}

func (s *milestoneService) GetMilestone(ctx context.Context, id uuid.UUID) (*Milestone, error) {
	return s.repo.GetMilestoneByID(ctx, id)
}

func (s *milestoneService) GetMilestones(ctx context.Context, projectID uuid.UUID) ([]Milestone, error) {
	return s.repo.GetMilestonesByProject(ctx, projectID)
}

func (s *milestoneService) GetMilestoneHierarchy(ctx context.Context, projectID uuid.UUID) ([]Milestone, error) {
	milestones, err := s.repo.GetMilestonesByProject(ctx, projectID)
	if err != nil {
		return nil, err
	}

	// Filter only root milestones (parent_id is null)
	var roots []Milestone
	for _, m := range milestones {
		if m.ParentID == nil {
			roots = append(roots, m)
		}
	}

	return roots, nil
}

// applyMilestoneIdentityFields applies name, slug, description, objective, and dates.
func applyMilestoneIdentityFields(milestone *Milestone, req *UpdateMilestoneRequest) {
	if req.Name != nil {
		milestone.Name = *req.Name
	}
	if req.Slug != nil {
		milestone.Slug = *req.Slug
	}
	if req.Description != nil {
		milestone.Description = req.Description
	}
	if req.Objective != nil {
		milestone.Objective = req.Objective
	}
	if req.StartDate != nil {
		milestone.StartDate = req.StartDate
	}
	if req.TargetDate != nil {
		milestone.TargetDate = *req.TargetDate
	}
}

// applyMilestoneUpdate applies non-nil fields from the update request to the milestone.
func applyMilestoneUpdate(milestone *Milestone, req *UpdateMilestoneRequest) {
	applyMilestoneIdentityFields(milestone, req)
	if req.Status != nil {
		milestone.Status = *req.Status
	}
	if req.Health != nil {
		milestone.Health = *req.Health
	}
	if req.RiskScore != nil {
		milestone.RiskScore = *req.RiskScore
	}
	if req.OwnerID != nil {
		milestone.OwnerID = req.OwnerID
	}
	milestone.UpdatedAt = time.Now()
}

func (s *milestoneService) UpdateMilestone(ctx context.Context, id uuid.UUID, req *UpdateMilestoneRequest) (*Milestone, error) {
	milestone, err := s.repo.GetMilestoneByID(ctx, id)
	if err != nil {
		return nil, err
	}
	applyMilestoneUpdate(milestone, req)
	return s.repo.UpdateMilestone(ctx, milestone)
}

func (s *milestoneService) DeleteMilestone(ctx context.Context, id uuid.UUID) error {
	now := time.Now()
	milestone, err := s.repo.GetMilestoneByID(ctx, id)
	if err != nil {
		return err
	}

	milestone.DeletedAt = &now
	_, err = s.repo.UpdateMilestone(ctx, milestone)
	return err
}

func (s *milestoneService) AddItemToMilestone(ctx context.Context, milestoneID, itemID uuid.UUID) error {
	return s.repo.AddItemToMilestone(ctx, milestoneID, itemID)
}

func (s *milestoneService) RemoveItemFromMilestone(ctx context.Context, milestoneID, itemID uuid.UUID) error {
	return s.repo.RemoveItemFromMilestone(ctx, milestoneID, itemID)
}

func (s *milestoneService) GetMilestoneProgress(ctx context.Context, milestoneID uuid.UUID) (*MilestoneProgress, error) {
	itemIDs, err := s.repo.GetMilestoneItems(ctx, milestoneID)
	if err != nil {
		return nil, err
	}

	if len(itemIDs) == 0 {
		return &MilestoneProgress{
			TotalItems:     0,
			CompletedItems: 0,
			Percentage:     0,
		}, nil
	}

	// Query items to get their statuses
	query := `
		SELECT status, COUNT(*) as count
		FROM items
		WHERE id = ANY($1) AND deleted_at IS NULL
		GROUP BY status
	`

	rows, err := s.db.QueryContext(ctx, query, itemIDs)
	if err != nil {
		return nil, err
	}
	defer func() {
		if err := rows.Close(); err != nil {
			slog.Warn("failed to close database rows", "error", err)
		}
	}()

	progress := &MilestoneProgress{
		TotalItems: len(itemIDs),
	}

	if err := scanMilestoneStatusCounts(rows, progress); err != nil {
		return nil, err
	}

	if progress.TotalItems > 0 {
		progress.Percentage = (progress.CompletedItems * milestonePercentScale) / progress.TotalItems
	}

	return progress, rows.Err()
}

func scanMilestoneStatusCounts(rows *sql.Rows, progress *MilestoneProgress) error {
	for rows.Next() {
		var status string
		var count int
		if err := rows.Scan(&status, &count); err != nil {
			return err
		}

		switch status {
		case "done":
			progress.CompletedItems += count
		case "in_progress":
			progress.InProgressItems += count
		case "blocked":
			progress.BlockedItems += count
		default:
			progress.NotStartedItems += count
		}
	}
	return nil
}

// computeHealthStatus derives the health status from risk score, overdue state, and progress.
func computeHealthStatus(riskScore int, isOverdue bool, progressRatio float64, blockedItems int) HealthStatus {
	switch {
	case riskScore > milestoneHealthRiskRed || (isOverdue && progressRatio < milestoneProgressRatioRed):
		return HealthRed
	case riskScore > milestoneHealthRiskYellow || (isOverdue && progressRatio < milestoneProgressRatioYellow) || blockedItems > 0:
		return HealthYellow
	default:
		return HealthGreen
	}
}

func (s *milestoneService) UpdateMilestoneHealth(ctx context.Context, milestoneID uuid.UUID) error {
	milestone, err := s.repo.GetMilestoneByID(ctx, milestoneID)
	if err != nil {
		return err
	}

	progress, err := s.GetMilestoneProgress(ctx, milestoneID)
	if err != nil {
		return err
	}

	riskFactors, riskScore, err := s.ComputeRiskFactors(ctx, milestoneID)
	if err != nil {
		return err
	}

	isOverdue := milestone.TargetDate.Before(time.Now())
	progressRatio := float64(progress.Percentage) / milestonePercentScaleFloat

	milestone.Health = computeHealthStatus(riskScore, isOverdue, progressRatio, progress.BlockedItems)
	milestone.RiskScore = riskScore
	milestone.RiskFactors = riskFactors
	milestone.UpdatedAt = time.Now()

	_, err = s.repo.UpdateMilestone(ctx, milestone)
	return err
}

func (s *milestoneService) ComputeRiskFactors(ctx context.Context, milestoneID uuid.UUID) ([]RiskFactor, int, error) {
	milestone, err := s.repo.GetMilestoneByID(ctx, milestoneID)
	if err != nil {
		return nil, 0, err
	}

	var riskFactors []RiskFactor
	riskScore := 0

	// Check if overdue
	now := time.Now()
	if milestone.TargetDate.Before(now) && milestone.Status != MilestoneCompleted {
		daysOverdue := int(now.Sub(milestone.TargetDate).Hours() / milestoneHoursPerDay)
		factor := RiskFactor{
			Type:        "overdue",
			Severity:    "high",
			Description: fmt.Sprintf("Milestone is %d days overdue", daysOverdue),
		}
		riskFactors = append(riskFactors, factor)
		riskScore += milestoneRiskScoreOverdue
	}

	// Check progress
	progress, err := s.GetMilestoneProgress(ctx, milestoneID)
	if err != nil {
		return nil, 0, err
	}

	if progress.TotalItems > 0 {
		expectedProgress := s.calculateExpectedProgress(milestone)
		actualProgress := float64(progress.Percentage) / milestonePercentScaleFloat

		if actualProgress < expectedProgress*milestoneProgressBehindFactor {
			factor := RiskFactor{
				Type:     "low_velocity",
				Severity: "medium",
				Description: fmt.Sprintf(
					"Progress is behind schedule (%.0f%% actual vs %.0f%% expected)",
					actualProgress*milestonePercentScaleFloat,
					expectedProgress*milestonePercentScaleFloat,
				),
			}
			riskFactors = append(riskFactors, factor)
			riskScore += milestoneRiskScoreLowVelocity
		}
	}

	// Check blocked items
	if progress.BlockedItems > 0 {
		factor := RiskFactor{
			Type:        "blocked_dependency",
			Severity:    "high",
			Description: fmt.Sprintf("%d items are blocked", progress.BlockedItems),
		}
		riskFactors = append(riskFactors, factor)
		riskScore += milestoneRiskScoreBlockedItems
	}

	// Cap risk score at 100
	if riskScore > milestoneRiskScoreMax {
		riskScore = milestoneRiskScoreMax
	}

	return riskFactors, riskScore, nil
}

func (s *milestoneService) calculateExpectedProgress(milestone *Milestone) float64 {
	if milestone.StartDate == nil {
		return 0.0
	}

	now := time.Now()
	startTime := milestone.StartDate.Unix()
	targetTime := milestone.TargetDate.Unix()
	nowTime := now.Unix()

	if nowTime >= targetTime {
		return 1.0
	}
	if nowTime <= startTime {
		return 0.0
	}

	totalDuration := float64(targetTime - startTime)
	elapsedDuration := float64(nowTime - startTime)
	return elapsedDuration / totalDuration
}
