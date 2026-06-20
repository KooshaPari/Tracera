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
	metricsDaysPerWeek     = 7
	metricsDaysPerTwoWeeks = 14
	metricsVelocityScale   = 100
)

// MetricsService provides business logic for progress metrics and calculations
type MetricsService interface {
	CalculateProjectMetrics(ctx context.Context, projectID uuid.UUID) (*ProjectMetrics, error)
	CalculateVelocity(ctx context.Context, projectID uuid.UUID, periods int) (float64, error)
	GetVelocityHistory(ctx context.Context, projectID uuid.UUID) ([]VelocityDataPoint, error)
	CalculateCycleTime(ctx context.Context, projectID uuid.UUID) (float64, error)
	EstimateCompletion(ctx context.Context, sprintID uuid.UUID) (*time.Time, error)
	RecordVelocity(ctx context.Context, sprintID uuid.UUID) error
}

type metricsService struct {
	db *sql.DB
}

// NewMetricsService creates a new metrics service
func NewMetricsService(db *sql.DB) MetricsService {
	return &metricsService{db: db}
}

func (m *metricsService) CalculateProjectMetrics(ctx context.Context, projectID uuid.UUID) (*ProjectMetrics, error) {
	metrics := newProjectMetrics()

	if err := m.populateGroupedCounts(ctx, projectID, metrics); err != nil {
		return nil, err
	}

	if err := m.populateCompletionCounts(ctx, projectID, metrics); err != nil {
		return nil, err
	}

	if err := m.populateRiskCounts(ctx, projectID, metrics); err != nil {
		return nil, err
	}

	return metrics, nil
}

func newProjectMetrics() *ProjectMetrics {
	return &ProjectMetrics{
		ByStatus:    make(map[string]int),
		ByPriority:  make(map[string]int),
		ByType:      make(map[string]int),
		ByLifecycle: make(map[string]int),
	}
}

func (m *metricsService) populateGroupedCounts(
	ctx context.Context,
	projectID uuid.UUID,
	metrics *ProjectMetrics,
) error {
	statusCounts, err := m.countGrouped(ctx, projectID, "status")
	if err != nil {
		return err
	}
	metrics.ByStatus = statusCounts
	for _, count := range statusCounts {
		metrics.TotalItems += count
	}

	priorityCounts, err := m.countGrouped(ctx, projectID, "priority")
	if err != nil {
		return err
	}
	metrics.ByPriority = priorityCounts

	typeCounts, err := m.countGrouped(ctx, projectID, "type")
	if err != nil {
		return err
	}
	metrics.ByType = typeCounts

	return nil
}

func (m *metricsService) populateCompletionCounts(
	ctx context.Context,
	projectID uuid.UUID,
	metrics *ProjectMetrics,
) error {
	weekAgo := time.Now().AddDate(0, 0, -metricsDaysPerWeek)
	twoWeeksAgo := time.Now().AddDate(0, 0, -metricsDaysPerTwoWeeks)

	var err error
	metrics.CompletedThisWeek, err = m.countWithCondition(ctx, projectID, condCompletedSince, weekAgo)
	if err != nil {
		return err
	}

	metrics.CompletedLastWeek, err = m.countWithCondition(ctx, projectID, condCompletedSince, twoWeeksAgo)
	if err != nil {
		return err
	}

	metrics.Velocity = float64(metrics.CompletedThisWeek) / float64(metricsDaysPerWeek)
	return nil
}

func (m *metricsService) populateRiskCounts(
	ctx context.Context,
	projectID uuid.UUID,
	metrics *ProjectMetrics,
) error {
	var err error
	metrics.BlockedCount, err = m.countWithCondition(ctx, projectID, condBlocked)
	if err != nil {
		return err
	}

	metrics.AtRiskCount, err = m.countWithCondition(ctx, projectID, condAtRisk)
	if err != nil {
		return err
	}

	metrics.OverdueCount, err = m.countWithCondition(ctx, projectID, condOverdue)
	if err != nil {
		return err
	}

	return nil
}

func (m *metricsService) countGrouped(ctx context.Context, projectID uuid.UUID, field string) (map[string]int, error) {
	query, err := groupedCountQuery(field)
	if err != nil {
		return nil, err
	}

	rows, err := m.db.QueryContext(ctx, query, projectID)
	if err != nil {
		return nil, err
	}
	defer func() {
		if err := rows.Close(); err != nil {
			slog.Warn("failed to close database rows", "error", err)
		}
	}()

	counts := make(map[string]int)
	for rows.Next() {
		var key string
		var count int
		if err := rows.Scan(&key, &count); err != nil {
			return nil, err
		}
		counts[key] = count
	}

	if err := rows.Err(); err != nil {
		return nil, err
	}

	return counts, nil
}

func groupedCountQuery(field string) (string, error) {
	switch field {
	case "status":
		return `
			SELECT status, COUNT(*) as count
			FROM items
			WHERE project_id = $1 AND deleted_at IS NULL
			GROUP BY status
		`, nil
	case "priority":
		return `
			SELECT priority, COUNT(*) as count
			FROM items
			WHERE project_id = $1 AND deleted_at IS NULL
			GROUP BY priority
		`, nil
	case "type":
		return `
			SELECT type, COUNT(*) as count
			FROM items
			WHERE project_id = $1 AND deleted_at IS NULL
			GROUP BY type
		`, nil
	default:
		return "", fmt.Errorf("unsupported group field: %s", field)
	}
}

// conditionKey identifies a predefined SQL WHERE-clause fragment.
type conditionKey int

const (
	condBlocked conditionKey = iota
	condAtRisk
	condOverdue
	condCompletedSince
)

// getConditionQuery returns the parameterised query for a given condition key.
// All fragments are compile-time literals so gosec G201 does not apply.
func getConditionQuery(key conditionKey) string {
	switch key {
	case condBlocked:
		return `SELECT COUNT(*) FROM items WHERE project_id = $1 AND status = 'blocked' AND deleted_at IS NULL`
	case condAtRisk:
		return `SELECT COUNT(*) FROM items WHERE project_id = $1 AND status = 'at_risk' AND deleted_at IS NULL`
	case condOverdue:
		return `SELECT COUNT(*) FROM items WHERE project_id = $1 AND target_date < now() AND status != 'done' AND deleted_at IS NULL`
	case condCompletedSince:
		return `SELECT COUNT(*) FROM items ` +
			`WHERE project_id = $1 AND status = 'done' ` +
			`AND completed_at IS NOT NULL AND completed_at >= $2 AND deleted_at IS NULL`
	default:
		return ""
	}
}

func (m *metricsService) countWithCondition(
	ctx context.Context,
	projectID uuid.UUID,
	key conditionKey,
	args ...interface{},
) (int, error) {
	query := getConditionQuery(key)
	if query == "" {
		return 0, fmt.Errorf("unknown condition key: %d", key)
	}

	queryArgs := append([]interface{}{projectID}, args...)
	var count int
	err := m.db.QueryRowContext(ctx, query, queryArgs...).Scan(&count)
	if err == sql.ErrNoRows {
		return 0, nil
	}
	if err != nil {
		return 0, err
	}

	return count, nil
}

func (m *metricsService) CalculateVelocity(ctx context.Context, projectID uuid.UUID, periods int) (float64, error) {
	query := `
		SELECT AVG(velocity)
		FROM velocity_history
		WHERE project_id = $1
		ORDER BY period_start DESC
		LIMIT $2
	`

	var velocity float64
	err := m.db.QueryRowContext(ctx, query, projectID, periods).Scan(&velocity)
	if err != nil && err != sql.ErrNoRows {
		return 0, err
	}

	return velocity, nil
}

func (m *metricsService) GetVelocityHistory(ctx context.Context, projectID uuid.UUID) ([]VelocityDataPoint, error) {
	query := `
		SELECT period_start, period_end, period_label, planned_points, completed_points, velocity
		FROM velocity_history
		WHERE project_id = $1
		ORDER BY period_start DESC
		LIMIT 52
	`

	rows, err := m.db.QueryContext(ctx, query, projectID)
	if err != nil {
		return nil, err
	}
	defer func() {
		if err := rows.Close(); err != nil {
			slog.Warn("failed to close database rows", "error", err)
		}
	}()

	var history []VelocityDataPoint
	for rows.Next() {
		var dataPoint VelocityDataPoint
		if err := rows.Scan(
			&dataPoint.PeriodStart,
			&dataPoint.PeriodEnd,
			&dataPoint.PeriodLabel,
			&dataPoint.PlannedPoints,
			&dataPoint.CompletedPoints,
			&dataPoint.Velocity,
		); err != nil {
			return nil, err
		}
		history = append(history, dataPoint)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	// Reverse to get chronological order
	for i := 0; i < len(history)/2; i++ {
		j := len(history) - 1 - i
		history[i], history[j] = history[j], history[i]
	}

	return history, nil
}

func (m *metricsService) CalculateCycleTime(ctx context.Context, projectID uuid.UUID) (float64, error) {
	query := `
		SELECT AVG(EXTRACT(DAY FROM (completed_at - created_at)))
		FROM items
		WHERE project_id = $1 AND status = 'done' AND completed_at IS NOT NULL AND deleted_at IS NULL
		AND completed_at >= now() - interval '90 days'
	`

	var cycleTime float64
	err := m.db.QueryRowContext(ctx, query, projectID).Scan(&cycleTime)
	if err != nil && err != sql.ErrNoRows {
		return 0, err
	}

	return cycleTime, nil
}

func (m *metricsService) EstimateCompletion(ctx context.Context, sprintID uuid.UUID) (*time.Time, error) {
	// Get sprint
	var sprint Sprint
	query := `
		SELECT id, planned_points, completed_points, remaining_points, start_date, end_date, status
		FROM sprints
		WHERE id = $1 AND deleted_at IS NULL
	`

	err := m.db.QueryRowContext(ctx, query, sprintID).Scan(
		&sprint.ID,
		&sprint.PlannedPoints,
		&sprint.CompletedPoints,
		&sprint.RemainingPoints,
		&sprint.StartDate,
		&sprint.EndDate,
		&sprint.Status,
	)
	if err != nil {
		return nil, err
	}

	// Calculate velocity from burndown data
	burndownQuery := `
		SELECT AVG(completed_points - LAG(completed_points, 1, 0) OVER (ORDER BY recorded_date))
		FROM burndown_data
		WHERE sprint_id = $1
	`

	var dailyVelocity float64
	err = m.db.QueryRowContext(ctx, burndownQuery, sprintID).Scan(&dailyVelocity)
	if err != nil && err != sql.ErrNoRows {
		return nil, err
	}

	if dailyVelocity <= 0 {
		return nil, nil // Cannot estimate
	}

	// Estimate days remaining
	daysRemaining := float64(sprint.RemainingPoints) / dailyVelocity
	estimatedCompletion := time.Now().AddDate(0, 0, int(daysRemaining))

	return &estimatedCompletion, nil
}

func (m *metricsService) RecordVelocity(ctx context.Context, sprintID uuid.UUID) error {
	// Get sprint
	var sprint Sprint
	var projectID uuid.UUID

	query := `
		SELECT id, project_id, name, start_date, end_date, planned_points, completed_points
		FROM sprints
		WHERE id = $1 AND deleted_at IS NULL
	`

	err := m.db.QueryRowContext(ctx, query, sprintID).Scan(
		&sprint.ID,
		&projectID,
		&sprint.Name,
		&sprint.StartDate,
		&sprint.EndDate,
		&sprint.PlannedPoints,
		&sprint.CompletedPoints,
	)
	if err != nil {
		return err
	}

	velocity := 0
	if sprint.PlannedPoints > 0 {
		velocity = (sprint.CompletedPoints * metricsVelocityScale) / sprint.PlannedPoints
	}

	dataPoint := VelocityDataPoint{
		PeriodStart:     sprint.StartDate,
		PeriodEnd:       sprint.EndDate,
		PeriodLabel:     sprint.Name,
		PlannedPoints:   sprint.PlannedPoints,
		CompletedPoints: sprint.CompletedPoints,
		Velocity:        velocity,
	}

	insertQuery := `
		INSERT INTO velocity_history (project_id, period_start, period_end, period_label, planned_points, completed_points, velocity)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
	`

	_, err = m.db.ExecContext(ctx, insertQuery,
		projectID,
		dataPoint.PeriodStart,
		dataPoint.PeriodEnd,
		dataPoint.PeriodLabel,
		dataPoint.PlannedPoints,
		dataPoint.CompletedPoints,
		dataPoint.Velocity,
	)

	return err
}

func closeRows(rows *sql.Rows) {
	if rows == nil {
		return
	}
	if err := rows.Close(); err != nil {
		slog.Warn("failed to close database rows", "error", err)
	}
}
