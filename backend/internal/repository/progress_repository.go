package repository

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/jackc/pgx/v5/stdlib"

	"github.com/kooshapari/tracertm-backend/internal/progress"
)

// ProgressRepository handles all progress-related data operations
type ProgressRepository struct {
	pool *pgxpool.Pool
	db   *sql.DB
}

const milestoneSelectFields = `
	SELECT id, project_id, parent_id, name, slug, description, objective,
	       start_date, target_date, actual_date, status, health, risk_score,
	       risk_factors, owner_id, tags, metadata, created_at, updated_at, deleted_at
	FROM milestones
`

const sprintSelectFields = `
	SELECT id, project_id, name, slug, goal, start_date, end_date,
	       status, health, planned_capacity, actual_capacity, planned_points,
	       completed_points, remaining_points, added_points, removed_points,
	       metadata, created_at, updated_at, completed_at, deleted_at
	FROM sprints
`

// NewProgressRepository creates a new progress repository
func NewProgressRepository(pool *pgxpool.Pool) *ProgressRepository {
	return &ProgressRepository{
		pool: pool,
		db:   stdlib.OpenDBFromPool(pool),
	}
}

// Milestone Operations

// CreateMilestone creates a new milestone
func (r *ProgressRepository) CreateMilestone(ctx context.Context, milestone *progress.Milestone) (*progress.Milestone, error) {
	riskFactorsJSON, err := json.Marshal(milestone.RiskFactors)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal risk factors: %w", err)
	}

	tagsJSON, err := json.Marshal(milestone.Tags)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal tags: %w", err)
	}

	query := `
		INSERT INTO milestones (
			id, project_id, parent_id, name, slug, description, objective,
			start_date, target_date, actual_date, status, health, risk_score,
			risk_factors, owner_id, tags, metadata, created_at, updated_at
		) VALUES (
			$1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19
		) RETURNING id, created_at, updated_at
	`

	err = r.pool.QueryRow(ctx, query,
		milestone.ID, milestone.ProjectID, milestone.ParentID, milestone.Name, milestone.Slug,
		milestone.Description, milestone.Objective, milestone.StartDate, milestone.TargetDate,
		milestone.ActualDate, milestone.Status, milestone.Health, milestone.RiskScore,
		riskFactorsJSON, milestone.OwnerID, tagsJSON, milestone.Metadata,
		time.Now(), time.Now(),
	).Scan(&milestone.ID, &milestone.CreatedAt, &milestone.UpdatedAt)
	if err != nil {
		return nil, fmt.Errorf("failed to create milestone: %w", err)
	}

	return milestone, nil
}

// GetMilestoneByID retrieves a milestone by ID
func (r *ProgressRepository) GetMilestoneByID(ctx context.Context, id uuid.UUID) (*progress.Milestone, error) {
	query := `
		SELECT id, project_id, parent_id, name, slug, description, objective,
			   start_date, target_date, actual_date, status, health, risk_score,
			   risk_factors, owner_id, tags, metadata, created_at, updated_at, deleted_at
		FROM milestones
		WHERE id = $1 AND deleted_at IS NULL
	`

	var milestone progress.Milestone
	var riskFactorsJSON []byte
	var tagsJSON []byte

	err := r.pool.QueryRow(ctx, query, id).Scan(
		&milestone.ID, &milestone.ProjectID, &milestone.ParentID, &milestone.Name, &milestone.Slug,
		&milestone.Description, &milestone.Objective, &milestone.StartDate, &milestone.TargetDate,
		&milestone.ActualDate, &milestone.Status, &milestone.Health, &milestone.RiskScore,
		&riskFactorsJSON, &milestone.OwnerID, &tagsJSON, &milestone.Metadata,
		&milestone.CreatedAt, &milestone.UpdatedAt, &milestone.DeletedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New("milestone not found")
		}
		return nil, fmt.Errorf("failed to get milestone: %w", err)
	}

	// Unmarshal JSON fields
	if len(riskFactorsJSON) > 0 {
		if err := json.Unmarshal(riskFactorsJSON, &milestone.RiskFactors); err != nil {
			return nil, fmt.Errorf("failed to unmarshal risk factors: %w", err)
		}
	}

	if len(tagsJSON) > 0 {
		if err := json.Unmarshal(tagsJSON, &milestone.Tags); err != nil {
			return nil, fmt.Errorf("failed to unmarshal tags: %w", err)
		}
	}

	return &milestone, nil
}

// GetMilestonesByProject retrieves all milestones for a project
func (r *ProgressRepository) GetMilestonesByProject(ctx context.Context, projectID uuid.UUID) ([]progress.Milestone, error) {
	return r.listMilestonesByCondition(ctx, "project_id = $1 AND deleted_at IS NULL", projectID)
}

// GetMilestonesByParent retrieves all milestones with a specific parent
func (r *ProgressRepository) GetMilestonesByParent(ctx context.Context, parentID uuid.UUID) ([]progress.Milestone, error) {
	return r.listMilestonesByCondition(ctx, "parent_id = $1 AND deleted_at IS NULL", parentID)
}

// UpdateMilestone updates an existing milestone
func (r *ProgressRepository) UpdateMilestone(ctx context.Context, milestone *progress.Milestone) (*progress.Milestone, error) {
	riskFactorsJSON, err := json.Marshal(milestone.RiskFactors)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal risk factors: %w", err)
	}

	tagsJSON, err := json.Marshal(milestone.Tags)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal tags: %w", err)
	}

	query := `
		UPDATE milestones
		SET name = $2, slug = $3, description = $4, objective = $5,
			start_date = $6, target_date = $7, actual_date = $8,
			status = $9, health = $10, risk_score = $11, risk_factors = $12,
			owner_id = $13, tags = $14, metadata = $15, updated_at = $16
		WHERE id = $1 AND deleted_at IS NULL
		RETURNING id, created_at, updated_at
	`

	err = r.pool.QueryRow(ctx, query,
		milestone.ID, milestone.Name, milestone.Slug, milestone.Description, milestone.Objective,
		milestone.StartDate, milestone.TargetDate, milestone.ActualDate,
		milestone.Status, milestone.Health, milestone.RiskScore, riskFactorsJSON,
		milestone.OwnerID, tagsJSON, milestone.Metadata, time.Now(),
	).Scan(&milestone.ID, &milestone.CreatedAt, &milestone.UpdatedAt)
	if err != nil {
		return nil, fmt.Errorf("failed to update milestone: %w", err)
	}

	return milestone, nil
}

// DeleteMilestone soft-deletes a milestone
func (r *ProgressRepository) DeleteMilestone(ctx context.Context, id uuid.UUID) error {
	query := `
		UPDATE milestones
		SET deleted_at = $2, updated_at = $2
		WHERE id = $1 AND deleted_at IS NULL
	`

	result, err := r.pool.Exec(ctx, query, id, time.Now())
	if err != nil {
		return fmt.Errorf("failed to delete milestone: %w", err)
	}

	if result.RowsAffected() == 0 {
		return errors.New("milestone not found")
	}

	return nil
}

// AddItemToMilestone adds an item to a milestone
func (r *ProgressRepository) AddItemToMilestone(ctx context.Context, milestoneID, itemID uuid.UUID) error {
	query := `
		INSERT INTO milestone_items (milestone_id, item_id, created_at)
		VALUES ($1, $2, $3)
		ON CONFLICT (milestone_id, item_id) DO NOTHING
	`

	_, err := r.pool.Exec(ctx, query, milestoneID, itemID, time.Now())
	if err != nil {
		return fmt.Errorf("failed to add item to milestone: %w", err)
	}

	return nil
}

// RemoveItemFromMilestone removes an item from a milestone
func (r *ProgressRepository) RemoveItemFromMilestone(ctx context.Context, milestoneID, itemID uuid.UUID) error {
	query := `
		DELETE FROM milestone_items
		WHERE milestone_id = $1 AND item_id = $2
	`

	result, err := r.pool.Exec(ctx, query, milestoneID, itemID)
	if err != nil {
		return fmt.Errorf("failed to remove item from milestone: %w", err)
	}

	if result.RowsAffected() == 0 {
		return errors.New("item not found in milestone")
	}

	return nil
}

// GetMilestoneItems retrieves all item IDs for a milestone
func (r *ProgressRepository) GetMilestoneItems(ctx context.Context, milestoneID uuid.UUID) ([]uuid.UUID, error) {
	query := `
		SELECT item_id FROM milestone_items WHERE milestone_id = $1
	`

	rows, err := r.pool.Query(ctx, query, milestoneID)
	if err != nil {
		return nil, fmt.Errorf("failed to query milestone items: %w", err)
	}
	defer rows.Close()

	var itemIDs []uuid.UUID
	for rows.Next() {
		var itemID uuid.UUID
		if err := rows.Scan(&itemID); err != nil {
			return nil, fmt.Errorf("failed to scan item id: %w", err)
		}
		itemIDs = append(itemIDs, itemID)
	}

	return itemIDs, rows.Err()
}

// UpdateMilestoneRisk updates risk factors and risk score
func (r *ProgressRepository) UpdateMilestoneRisk(
	ctx context.Context, milestoneID uuid.UUID, riskScore int, riskFactors []progress.RiskFactor,
) error {
	riskFactorsJSON, err := json.Marshal(riskFactors)
	if err != nil {
		return fmt.Errorf("failed to marshal risk factors: %w", err)
	}

	query := `
		UPDATE milestones
		SET risk_score = $2, risk_factors = $3, updated_at = $4
		WHERE id = $1 AND deleted_at IS NULL
	`

	result, err := r.pool.Exec(ctx, query, milestoneID, riskScore, riskFactorsJSON, time.Now())
	if err != nil {
		return fmt.Errorf("failed to update milestone risk: %w", err)
	}

	if result.RowsAffected() == 0 {
		return errors.New("milestone not found")
	}

	return nil
}

// Sprint Operations

// CreateSprint creates a new sprint
func (r *ProgressRepository) CreateSprint(ctx context.Context, sprint *progress.Sprint) (*progress.Sprint, error) {
	query := `
		INSERT INTO sprints (
			id, project_id, name, slug, goal, start_date, end_date,
			status, health, planned_capacity, actual_capacity, planned_points,
			completed_points, remaining_points, added_points, removed_points,
			metadata, created_at, updated_at
		) VALUES (
			$1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19
		) RETURNING id, created_at, updated_at
	`

	err := r.pool.QueryRow(ctx, query,
		sprint.ID, sprint.ProjectID, sprint.Name, sprint.Slug, sprint.Goal,
		sprint.StartDate, sprint.EndDate, sprint.Status, sprint.Health,
		sprint.PlannedCapacity, sprint.ActualCapacity, sprint.PlannedPoints,
		sprint.CompletedPoints, sprint.RemainingPoints, sprint.AddedPoints,
		sprint.RemovedPoints, sprint.Metadata,
		time.Now(), time.Now(),
	).Scan(&sprint.ID, &sprint.CreatedAt, &sprint.UpdatedAt)
	if err != nil {
		return nil, fmt.Errorf("failed to create sprint: %w", err)
	}

	return sprint, nil
}

// GetSprintByID retrieves a sprint by ID
func (r *ProgressRepository) GetSprintByID(ctx context.Context, id uuid.UUID) (*progress.Sprint, error) {
	return r.getSprintByCondition(ctx, "id = $1 AND deleted_at IS NULL", "sprint not found", id)
}

// GetActiveSprint retrieves the active sprint for a project
func (r *ProgressRepository) GetActiveSprint(ctx context.Context, projectID uuid.UUID) (*progress.Sprint, error) {
	return r.getSprintByCondition(
		ctx,
		"project_id = $1 AND status = 'active' AND deleted_at IS NULL ORDER BY start_date DESC LIMIT 1",
		"no active sprint found",
		projectID,
	)
}

func (r *ProgressRepository) listMilestones(
	ctx context.Context,
	query string,
	queryErrMsg string,
	args ...interface{},
) ([]progress.Milestone, error) {
	rows, err := r.pool.Query(ctx, query, args...)
	if err != nil {
		return nil, fmt.Errorf("%s: %w", queryErrMsg, err)
	}
	defer rows.Close()

	var milestones []progress.Milestone
	for rows.Next() {
		var milestone progress.Milestone
		var riskFactorsJSON []byte
		var tagsJSON []byte

		err := rows.Scan(
			&milestone.ID, &milestone.ProjectID, &milestone.ParentID, &milestone.Name, &milestone.Slug,
			&milestone.Description, &milestone.Objective, &milestone.StartDate, &milestone.TargetDate,
			&milestone.ActualDate, &milestone.Status, &milestone.Health, &milestone.RiskScore,
			&riskFactorsJSON, &milestone.OwnerID, &tagsJSON, &milestone.Metadata,
			&milestone.CreatedAt, &milestone.UpdatedAt, &milestone.DeletedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan milestone: %w", err)
		}

		if len(riskFactorsJSON) > 0 {
			if err := json.Unmarshal(riskFactorsJSON, &milestone.RiskFactors); err != nil {
				return nil, fmt.Errorf("failed to unmarshal risk factors: %w", err)
			}
		}

		if len(tagsJSON) > 0 {
			if err := json.Unmarshal(tagsJSON, &milestone.Tags); err != nil {
				return nil, fmt.Errorf("failed to unmarshal tags: %w", err)
			}
		}

		milestones = append(milestones, milestone)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating milestones: %w", err)
	}

	return milestones, nil
}

func (r *ProgressRepository) listMilestonesByCondition(
	ctx context.Context,
	condition string,
	args ...interface{},
) ([]progress.Milestone, error) {
	query := fmt.Sprintf("%s WHERE %s ORDER BY target_date ASC", milestoneSelectFields, condition)
	return r.listMilestones(ctx, query, "failed to query milestones", args...)
}

func (r *ProgressRepository) getSprint(
	ctx context.Context,
	query string,
	notFoundMsg string,
	args ...interface{},
) (*progress.Sprint, error) {
	var sprint progress.Sprint
	err := r.pool.QueryRow(ctx, query, args...).Scan(
		&sprint.ID, &sprint.ProjectID, &sprint.Name, &sprint.Slug, &sprint.Goal,
		&sprint.StartDate, &sprint.EndDate, &sprint.Status, &sprint.Health,
		&sprint.PlannedCapacity, &sprint.ActualCapacity, &sprint.PlannedPoints,
		&sprint.CompletedPoints, &sprint.RemainingPoints, &sprint.AddedPoints,
		&sprint.RemovedPoints, &sprint.Metadata,
		&sprint.CreatedAt, &sprint.UpdatedAt, &sprint.CompletedAt, &sprint.DeletedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New(notFoundMsg)
		}
		return nil, fmt.Errorf("failed to get sprint: %w", err)
	}

	return &sprint, nil
}

func (r *ProgressRepository) getSprintByCondition(
	ctx context.Context,
	condition string,
	notFoundMessage string,
	args ...interface{},
) (*progress.Sprint, error) {
	query := fmt.Sprintf("%s WHERE %s", sprintSelectFields, condition)
	return r.getSprint(ctx, query, notFoundMessage, args...)
}

// GetSprintsByProject retrieves all sprints for a project
func (r *ProgressRepository) GetSprintsByProject(ctx context.Context, projectID uuid.UUID) ([]progress.Sprint, error) {
	query := `
		SELECT id, project_id, name, slug, goal, start_date, end_date,
			   status, health, planned_capacity, actual_capacity, planned_points,
			   completed_points, remaining_points, added_points, removed_points,
			   metadata, created_at, updated_at, completed_at, deleted_at
		FROM sprints
		WHERE project_id = $1 AND deleted_at IS NULL
		ORDER BY start_date DESC
	`

	rows, err := r.pool.Query(ctx, query, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to query sprints: %w", err)
	}
	defer rows.Close()

	var sprints []progress.Sprint
	for rows.Next() {
		var sprint progress.Sprint
		err := rows.Scan(
			&sprint.ID, &sprint.ProjectID, &sprint.Name, &sprint.Slug, &sprint.Goal,
			&sprint.StartDate, &sprint.EndDate, &sprint.Status, &sprint.Health,
			&sprint.PlannedCapacity, &sprint.ActualCapacity, &sprint.PlannedPoints,
			&sprint.CompletedPoints, &sprint.RemainingPoints, &sprint.AddedPoints,
			&sprint.RemovedPoints, &sprint.Metadata,
			&sprint.CreatedAt, &sprint.UpdatedAt, &sprint.CompletedAt, &sprint.DeletedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan sprint: %w", err)
		}
		sprints = append(sprints, sprint)
	}

	return sprints, rows.Err()
}

// UpdateSprint updates an existing sprint
func (r *ProgressRepository) UpdateSprint(ctx context.Context, sprint *progress.Sprint) (*progress.Sprint, error) {
	query := `
		UPDATE sprints
		SET name = $2, slug = $3, goal = $4, start_date = $5, end_date = $6,
			status = $7, health = $8, planned_capacity = $9, actual_capacity = $10,
			planned_points = $11, completed_points = $12, remaining_points = $13,
			added_points = $14, removed_points = $15, metadata = $16,
			completed_at = $17, updated_at = $18
		WHERE id = $1 AND deleted_at IS NULL
		RETURNING id, created_at, updated_at
	`

	err := r.pool.QueryRow(ctx, query,
		sprint.ID, sprint.Name, sprint.Slug, sprint.Goal, sprint.StartDate, sprint.EndDate,
		sprint.Status, sprint.Health, sprint.PlannedCapacity, sprint.ActualCapacity,
		sprint.PlannedPoints, sprint.CompletedPoints, sprint.RemainingPoints,
		sprint.AddedPoints, sprint.RemovedPoints, sprint.Metadata,
		sprint.CompletedAt, time.Now(),
	).Scan(&sprint.ID, &sprint.CreatedAt, &sprint.UpdatedAt)
	if err != nil {
		return nil, fmt.Errorf("failed to update sprint: %w", err)
	}

	return sprint, nil
}

// DeleteSprint soft-deletes a sprint
func (r *ProgressRepository) DeleteSprint(ctx context.Context, id uuid.UUID) error {
	query := `
		UPDATE sprints
		SET deleted_at = $2, updated_at = $2
		WHERE id = $1 AND deleted_at IS NULL
	`

	result, err := r.pool.Exec(ctx, query, id, time.Now())
	if err != nil {
		return fmt.Errorf("failed to delete sprint: %w", err)
	}

	if result.RowsAffected() == 0 {
		return errors.New("sprint not found")
	}

	return nil
}

// AddItemToSprint adds an item to a sprint
func (r *ProgressRepository) AddItemToSprint(ctx context.Context, sprintID, itemID uuid.UUID) error {
	query := `
		INSERT INTO sprint_items (sprint_id, item_id, created_at)
		VALUES ($1, $2, $3)
		ON CONFLICT (sprint_id, item_id) DO NOTHING
	`

	_, err := r.pool.Exec(ctx, query, sprintID, itemID, time.Now())
	if err != nil {
		return fmt.Errorf("failed to add item to sprint: %w", err)
	}

	return nil
}

// RemoveItemFromSprint removes an item from a sprint
func (r *ProgressRepository) RemoveItemFromSprint(ctx context.Context, sprintID, itemID uuid.UUID) error {
	query := `
		DELETE FROM sprint_items
		WHERE sprint_id = $1 AND item_id = $2
	`

	result, err := r.pool.Exec(ctx, query, sprintID, itemID)
	if err != nil {
		return fmt.Errorf("failed to remove item from sprint: %w", err)
	}

	if result.RowsAffected() == 0 {
		return errors.New("item not found in sprint")
	}

	return nil
}

// GetSprintItems retrieves all item IDs for a sprint
func (r *ProgressRepository) GetSprintItems(ctx context.Context, sprintID uuid.UUID) ([]uuid.UUID, error) {
	query := `
		SELECT item_id
		FROM sprint_items
		WHERE sprint_id = $1
		ORDER BY created_at ASC
	`

	rows, err := r.pool.Query(ctx, query, sprintID)
	if err != nil {
		return nil, fmt.Errorf("failed to query sprint items: %w", err)
	}
	defer rows.Close()

	var itemIDs []uuid.UUID
	for rows.Next() {
		var itemID uuid.UUID
		if err := rows.Scan(&itemID); err != nil {
			return nil, fmt.Errorf("failed to scan item ID: %w", err)
		}
		itemIDs = append(itemIDs, itemID)
	}

	return itemIDs, rows.Err()
}

// RecordBurndown records burndown data for a sprint
func (r *ProgressRepository) RecordBurndown(ctx context.Context, sprintID uuid.UUID, data *progress.BurndownDataPoint) error {
	query := `
		INSERT INTO burndown_data (
			id, sprint_id, recorded_date, remaining_points, ideal_points,
			completed_points, added_points, created_at
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
	`

	if err := r.exec(ctx, query,
		uuid.New(), sprintID, data.RecordedDate, data.RemainingPoints,
		data.IdealPoints, data.CompletedPoints, data.AddedPoints, time.Now(),
	); err != nil {
		return fmt.Errorf("failed to record burndown: %w", err)
	}

	return nil
}

func (r *ProgressRepository) exec(ctx context.Context, query string, args ...interface{}) error {
	if r.db != nil {
		_, err := r.db.ExecContext(ctx, query, args...)
		return err
	}
	_, err := r.pool.Exec(ctx, query, args...)
	return err
}

// GetBurndownData retrieves burndown data for a sprint
func (r *ProgressRepository) GetBurndownData(ctx context.Context, sprintID uuid.UUID) ([]progress.BurndownDataPoint, error) {
	query := `
		SELECT recorded_date, remaining_points, ideal_points, completed_points, added_points
		FROM burndown_data
		WHERE sprint_id = $1
		ORDER BY recorded_date ASC
	`

	rows, err := r.pool.Query(ctx, query, sprintID)
	if err != nil {
		return nil, fmt.Errorf("failed to query burndown data: %w", err)
	}
	defer rows.Close()

	var dataPoints []progress.BurndownDataPoint
	for rows.Next() {
		var point progress.BurndownDataPoint
		err := rows.Scan(
			&point.RecordedDate, &point.RemainingPoints, &point.IdealPoints,
			&point.CompletedPoints, &point.AddedPoints,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan burndown data: %w", err)
		}
		dataPoints = append(dataPoints, point)
	}

	return dataPoints, rows.Err()
}

// AddBurndownData adds burndown data for a sprint (alias for RecordBurndown to match interface)
func (r *ProgressRepository) AddBurndownData(ctx context.Context, sprintID uuid.UUID, data *progress.BurndownDataPoint) error {
	return r.RecordBurndown(ctx, sprintID, data)
}

// Snapshot Operations

// CreateSnapshot creates a new progress snapshot
func (r *ProgressRepository) CreateSnapshot(ctx context.Context, snapshot *progress.Snapshot) (*progress.Snapshot, error) {
	query := `
		INSERT INTO progress_snapshots (
			id, project_id, snapshot_date, metrics, created_at
		) VALUES ($1, $2, $3, $4, $5)
		RETURNING id, created_at
	`

	err := r.pool.QueryRow(ctx, query,
		snapshot.ID, snapshot.ProjectID, snapshot.SnapshotDate,
		snapshot.Metrics, time.Now(),
	).Scan(&snapshot.ID, &snapshot.CreatedAt)
	if err != nil {
		return nil, fmt.Errorf("failed to create snapshot: %w", err)
	}

	return snapshot, nil
}

// GetSnapshotByID retrieves a snapshot by ID
func (r *ProgressRepository) GetSnapshotByID(ctx context.Context, id uuid.UUID) (*progress.Snapshot, error) {
	query := `
		SELECT id, project_id, snapshot_date, metrics, created_at
		FROM progress_snapshots
		WHERE id = $1
	`

	var snapshot progress.Snapshot
	err := r.pool.QueryRow(ctx, query, id).Scan(
		&snapshot.ID, &snapshot.ProjectID, &snapshot.SnapshotDate,
		&snapshot.Metrics, &snapshot.CreatedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New("snapshot not found")
		}
		return nil, fmt.Errorf("failed to get snapshot: %w", err)
	}

	return &snapshot, nil
}

// GetSnapshot retrieves a snapshot by ID (alias for GetSnapshotByID to match interface)
func (r *ProgressRepository) GetSnapshot(ctx context.Context, id uuid.UUID) (*progress.Snapshot, error) {
	return r.GetSnapshotByID(ctx, id)
}

// GetSnapshotsByProject retrieves snapshots for a project
func (r *ProgressRepository) GetSnapshotsByProject(ctx context.Context, projectID uuid.UUID, limit int) ([]progress.Snapshot, error) {
	query := `
		SELECT id, project_id, snapshot_date, metrics, created_at
		FROM progress_snapshots
		WHERE project_id = $1
		ORDER BY snapshot_date DESC
		LIMIT $2
	`

	rows, err := r.pool.Query(ctx, query, projectID, limit)
	if err != nil {
		return nil, fmt.Errorf("failed to query snapshots: %w", err)
	}
	defer rows.Close()

	var snapshots []progress.Snapshot
	for rows.Next() {
		var snapshot progress.Snapshot
		err := rows.Scan(
			&snapshot.ID, &snapshot.ProjectID, &snapshot.SnapshotDate,
			&snapshot.Metrics, &snapshot.CreatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan snapshot: %w", err)
		}
		snapshots = append(snapshots, snapshot)
	}

	return snapshots, rows.Err()
}

// GetSnapshotsByDateRange retrieves snapshots for a project within a date range
func (r *ProgressRepository) GetSnapshotsByDateRange(
	ctx context.Context, projectID uuid.UUID, startDate, endDate time.Time,
) ([]progress.Snapshot, error) {
	query := `
		SELECT id, project_id, snapshot_date, metrics, created_at
		FROM progress_snapshots
		WHERE project_id = $1 AND snapshot_date >= $2 AND snapshot_date <= $3
		ORDER BY snapshot_date ASC
	`

	rows, err := r.pool.Query(ctx, query, projectID, startDate, endDate)
	if err != nil {
		return nil, fmt.Errorf("failed to query snapshots: %w", err)
	}
	defer rows.Close()

	var snapshots []progress.Snapshot
	for rows.Next() {
		var snapshot progress.Snapshot
		err := rows.Scan(
			&snapshot.ID, &snapshot.ProjectID, &snapshot.SnapshotDate,
			&snapshot.Metrics, &snapshot.CreatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan snapshot: %w", err)
		}
		snapshots = append(snapshots, snapshot)
	}

	return snapshots, rows.Err()
}

// VelocityHistory Operations

// RecordVelocity records velocity history for a sprint
func (r *ProgressRepository) RecordVelocity(ctx context.Context, projectID uuid.UUID, point *progress.VelocityDataPoint) error {
	query := `
		INSERT INTO velocity_history (
			id, project_id, period_start, period_end, period_label,
			planned_points, completed_points, velocity, created_at
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
	`

	_, err := r.pool.Exec(ctx, query,
		uuid.New(), projectID, point.PeriodStart, point.PeriodEnd, point.PeriodLabel,
		point.PlannedPoints, point.CompletedPoints, point.Velocity, time.Now(),
	)
	if err != nil {
		return fmt.Errorf("failed to record velocity: %w", err)
	}

	return nil
}

// GetVelocityHistory retrieves velocity history for a project
func (r *ProgressRepository) GetVelocityHistory(ctx context.Context, projectID uuid.UUID) ([]progress.VelocityDataPoint, error) {
	query := `
		SELECT period_start, period_end, period_label, planned_points,
			   completed_points, velocity
		FROM velocity_history
		WHERE project_id = $1
		ORDER BY period_start DESC
		LIMIT 52
	`

	rows, err := r.pool.Query(ctx, query, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to query velocity history: %w", err)
	}
	defer rows.Close()

	var history []progress.VelocityDataPoint
	for rows.Next() {
		var point progress.VelocityDataPoint
		err := rows.Scan(
			&point.PeriodStart, &point.PeriodEnd, &point.PeriodLabel,
			&point.PlannedPoints, &point.CompletedPoints, &point.Velocity,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan velocity data: %w", err)
		}
		history = append(history, point)
	}

	return history, rows.Err()
}
