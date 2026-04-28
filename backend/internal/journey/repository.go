package journey

import (
	"context"
	"errors"
	"strconv"
	"time"

	"gorm.io/gorm"
)

// Repository defines methods for journey data access
type Repository interface {
	Create(ctx context.Context, j *DerivedJourney) error
	GetByID(ctx context.Context, id string) (*DerivedJourney, error)
	GetByProjectID(ctx context.Context, projectID string) ([]*DerivedJourney, error)
	GetByType(ctx context.Context, projectID string, jType Type) ([]*DerivedJourney, error)
	Update(ctx context.Context, j *DerivedJourney) error
	Delete(ctx context.Context, id string) error
	List(ctx context.Context, filter Filter) ([]*DerivedJourney, error)
	Count(ctx context.Context, projectID string) (int64, error)
	AddStep(ctx context.Context, journeyID string, step *Step) error
	RemoveStep(ctx context.Context, journeyID string, itemID string) error
	GetSteps(ctx context.Context, journeyID string) ([]*Step, error)
}

// Filter for querying journeys
type Filter struct {
	ProjectID *string
	Type      *Type
	MinScore  float64
	Limit     int
	Offset    int
	SortBy    string // "created_at", "score", "name"
}

// journeyRepository implements Repository
type journeyRepository struct {
	db *gorm.DB
}

// NewJourneyRepository creates a new journey repository
func NewJourneyRepository(db *gorm.DB) Repository {
	return &journeyRepository{db: db}
}

// Create inserts a new journey
func (r *journeyRepository) Create(ctx context.Context, journey *DerivedJourney) error {
	if journey.ID == "" {
		journey.ID = generateJourneyID()
	}
	journey.CreatedAt = time.Now()
	journey.UpdatedAt = time.Now()

	return r.db.WithContext(ctx).Create(journey).Error
}

// GetByID retrieves a journey by ID
func (r *journeyRepository) GetByID(ctx context.Context, id string) (*DerivedJourney, error) {
	var journey DerivedJourney
	err := r.db.WithContext(ctx).
		Where("id = ? AND deleted_at IS NULL", id).
		First(&journey).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, &NotFoundError{Resource: "journey"}
		}
		return nil, err
	}
	return &journey, nil
}

// GetByProjectID retrieves all journeys for a project
func (r *journeyRepository) GetByProjectID(ctx context.Context, projectID string) ([]*DerivedJourney, error) {
	var journeys []*DerivedJourney
	err := r.db.WithContext(ctx).
		Where("project_id = ? AND deleted_at IS NULL", projectID).
		Order("created_at DESC").
		Find(&journeys).Error

	return journeys, err
}

// GetByType retrieves journeys of a specific type
func (r *journeyRepository) GetByType(ctx context.Context, projectID string, jType Type) ([]*DerivedJourney, error) {
	var journeys []*DerivedJourney
	err := r.db.WithContext(ctx).
		Where("project_id = ? AND type = ? AND deleted_at IS NULL", projectID, jType).
		Order("created_at DESC").
		Find(&journeys).Error

	return journeys, err
}

// Update modifies an existing journey
func (r *journeyRepository) Update(ctx context.Context, j *DerivedJourney) error {
	j.UpdatedAt = time.Now()
	return r.db.WithContext(ctx).
		Model(&DerivedJourney{}).
		Where("id = ? AND deleted_at IS NULL", j.ID).
		Updates(j).Error
}

// Delete soft-deletes a journey
func (r *journeyRepository) Delete(ctx context.Context, id string) error {
	now := time.Now()
	return r.db.WithContext(ctx).
		Model(&DerivedJourney{}).
		Where("id = ? AND deleted_at IS NULL", id).
		Update("deleted_at", now).Error
}

// List retrieves journeys with filtering and pagination
func (r *journeyRepository) List(ctx context.Context, filter Filter) ([]*DerivedJourney, error) {
	var journeys []*DerivedJourney

	query := r.db.WithContext(ctx).Where("deleted_at IS NULL")

	if filter.ProjectID != nil {
		query = query.Where("project_id = ?", *filter.ProjectID)
	}
	if filter.Type != nil {
		query = query.Where("type = ?", *filter.Type)
	}
	if filter.MinScore > 0 {
		query = query.Where("score >= ?", filter.MinScore)
	}

	sortBy := "created_at"
	if filter.SortBy != "" && isValidSortField(filter.SortBy) {
		sortBy = filter.SortBy
	}

	query = query.Order(sortBy + " DESC")

	if filter.Limit > 0 {
		query = query.Limit(filter.Limit)
	}
	if filter.Offset > 0 {
		query = query.Offset(filter.Offset)
	}

	err := query.Find(&journeys).Error
	return journeys, err
}

// Count returns the total number of journeys for a project
func (r *journeyRepository) Count(ctx context.Context, projectID string) (int64, error) {
	var count int64
	err := r.db.WithContext(ctx).
		Model(&DerivedJourney{}).
		Where("project_id = ? AND deleted_at IS NULL", projectID).
		Count(&count).Error

	return count, err
}

// AddStep adds a step to a journey
func (r *journeyRepository) AddStep(ctx context.Context, journeyID string, step *Step) error {
	j, err := r.GetByID(ctx, journeyID)
	if err != nil {
		return err
	}

	j.NodeIDs = append(j.NodeIDs, step.ItemID)
	return r.Update(ctx, j)
}

// RemoveStep removes a step from a journey
func (r *journeyRepository) RemoveStep(ctx context.Context, journeyID string, itemID string) error {
	journey, err := r.GetByID(ctx, journeyID)
	if err != nil {
		return err
	}

	newNodeIDs := make([]string, 0, len(journey.NodeIDs))
	for _, id := range journey.NodeIDs {
		if id != itemID {
			newNodeIDs = append(newNodeIDs, id)
		}
	}
	journey.NodeIDs = newNodeIDs

	return r.Update(ctx, journey)
}

// GetSteps returns the steps for a journey
func (r *journeyRepository) GetSteps(ctx context.Context, journeyID string) ([]*Step, error) {
	j, err := r.GetByID(ctx, journeyID)
	if err != nil {
		return nil, err
	}

	steps := make([]*Step, len(j.NodeIDs))
	for i, nodeID := range j.NodeIDs {
		steps[i] = &Step{
			ItemID: nodeID,
			Order:  i,
		}
	}

	return steps, nil
}

// Helper functions

func isValidSortField(field string) bool {
	switch field {
	case "created_at", "score", "name", "type", "updated_at":
		return true
	default:
		return false
	}
}

// NotFoundError represents a not found error
type NotFoundError struct {
	Resource string
}

func (e *NotFoundError) Error() string {
	return e.Resource + " not found"
}

// generateJourneyID generates a unique ID for journeys
func generateJourneyID() string {
	return "j_" + strconv.FormatInt(time.Now().UnixNano(), 10)
}

// TableName specifies the GORM table name
func (j *DerivedJourney) TableName() string {
	return "journeys"
}
