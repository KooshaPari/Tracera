package repository

import (
	"context"
	"errors"
	"time"

	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/pagination"
	"github.com/kooshapari/tracertm-backend/internal/tx"
)

// Repository interfaces define the contract for data access

// ItemRepository defines methods for item data access
type ItemRepository interface {
	Create(ctx context.Context, item *models.Item) error
	GetByID(ctx context.Context, id string) (*models.Item, error)
	GetByProjectID(ctx context.Context, projectID string) ([]*models.Item, error)
	List(ctx context.Context, filter ItemFilter) ([]*models.Item, error)
	Update(ctx context.Context, item *models.Item) error
	Delete(ctx context.Context, id string) error
	Count(ctx context.Context, filter ItemFilter) (int64, error)
}

// LinkRepository defines methods for link data access
type LinkRepository interface {
	Create(ctx context.Context, link *models.Link) error
	GetByID(ctx context.Context, id string) (*models.Link, error)
	GetBySourceID(ctx context.Context, sourceID string) ([]*models.Link, error)
	GetByTargetID(ctx context.Context, targetID string) ([]*models.Link, error)
	List(ctx context.Context, filter LinkFilter) ([]*models.Link, error)
	Update(ctx context.Context, link *models.Link) error
	Delete(ctx context.Context, id string) error
	DeleteByItemID(ctx context.Context, itemID string) error
}

// ProjectRepository defines methods for project data access
type ProjectRepository interface {
	Create(ctx context.Context, project *models.Project) error
	GetByID(ctx context.Context, id string) (*models.Project, error)
	List(ctx context.Context) ([]*models.Project, error)
	Update(ctx context.Context, project *models.Project) error
	Delete(ctx context.Context, id string) error
}

// AgentRepository defines methods for agent data access
type AgentRepository interface {
	Create(ctx context.Context, agent *models.Agent) error
	GetByID(ctx context.Context, id string) (*models.Agent, error)
	GetByProjectID(ctx context.Context, projectID string) ([]*models.Agent, error)
	List(ctx context.Context) ([]*models.Agent, error)
	Update(ctx context.Context, agent *models.Agent) error
	UpdateStatus(ctx context.Context, id, status string) error
	Delete(ctx context.Context, id string) error
}

// ViewRepository defines methods for view data access
type ViewRepository interface {
	Create(ctx context.Context, view *models.View) error
	GetByID(ctx context.Context, id string) (*models.View, error)
	GetByProjectID(ctx context.Context, projectID string) ([]*models.View, error)
	List(ctx context.Context) ([]*models.View, error)
	Update(ctx context.Context, view *models.View) error
	Delete(ctx context.Context, id string) error
	CountItemsByView(ctx context.Context, viewID string) (int64, error)
}

// ItemFilter filters item list/query results.
type ItemFilter struct {
	ProjectID *string
	Type      *string
	Status    *string
	Priority  *models.Priority
	Limit     int
	Offset    int
	// Cursor-based pagination fields
	Cursor    *string // Base64-encoded cursor for pagination
	UseCursor bool    // If true, use cursor instead of offset
}

// LinkFilter filters link list/query results.
type LinkFilter struct {
	ProjectID *string
	SourceID  *string
	TargetID  *string
	Type      *string
	Limit     int
	Offset    int
}

// GORM Implementations

type itemRepository struct {
	db *gorm.DB
}

// NewItemRepository returns a GORM-based ItemRepository.
func NewItemRepository(db *gorm.DB) ItemRepository {
	return &itemRepository{db: db}
}

func (r *itemRepository) Create(ctx context.Context, item *models.Item) error {
	db := tx.GetDB(ctx, r.db)
	return db.WithContext(ctx).Create(item).Error
}

func (r *itemRepository) GetByID(ctx context.Context, id string) (*models.Item, error) {
	db := tx.GetDB(ctx, r.db)
	var item models.Item
	err := db.WithContext(ctx).Where("id = ? AND deleted_at IS NULL", id).First(&item).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("item not found")
		}
		return nil, err
	}
	return &item, nil
}

func (r *itemRepository) GetByProjectID(ctx context.Context, projectID string) ([]*models.Item, error) {
	db := tx.GetDB(ctx, r.db)
	var items []*models.Item
	err := db.WithContext(ctx).Where("project_id = ? AND deleted_at IS NULL", projectID).Find(&items).Error
	return items, err
}

// applyItemFilters adds WHERE clauses for non-nil filter fields.
func applyItemFilters(query *gorm.DB, filter ItemFilter) *gorm.DB {
	if filter.ProjectID != nil {
		query = query.Where("project_id = ?", *filter.ProjectID)
	}
	if filter.Type != nil {
		query = query.Where("type = ?", *filter.Type)
	}
	if filter.Status != nil {
		query = query.Where("status = ?", *filter.Status)
	}
	if filter.Priority != nil {
		query = query.Where("priority = ?", *filter.Priority)
	}
	return query
}

// applyPagination adds cursor or offset pagination to the query.
func applyPagination(query *gorm.DB, filter ItemFilter) *gorm.DB {
	if filter.UseCursor && filter.Cursor != nil && *filter.Cursor != "" {
		cursor, err := pagination.DecodeCursor(*filter.Cursor)
		if err == nil && cursor != nil {
			query = query.Where(
				"(created_at < ?) OR (created_at = ? AND id > ?)",
				cursor.Timestamp, cursor.Timestamp, cursor.ID,
			)
		}
	} else if filter.Offset > 0 {
		query = query.Offset(filter.Offset)
	}
	if filter.Limit > 0 {
		query = query.Limit(filter.Limit)
	}
	return query
}

func (r *itemRepository) List(ctx context.Context, filter ItemFilter) ([]*models.Item, error) {
	db := tx.GetDB(ctx, r.db)
	var items []*models.Item
	query := db.WithContext(ctx).Where("deleted_at IS NULL")
	query = applyItemFilters(query, filter)
	query = applyPagination(query, filter)
	err := query.Order("created_at DESC, id ASC").Find(&items).Error
	return items, err
}

func (r *itemRepository) Update(ctx context.Context, item *models.Item) error {
	db := tx.GetDB(ctx, r.db)
	item.UpdatedAt = time.Now()
	return db.WithContext(ctx).Save(item).Error
}

func (r *itemRepository) Delete(ctx context.Context, id string) error {
	db := tx.GetDB(ctx, r.db)
	now := time.Now()
	return db.WithContext(ctx).Model(&models.Item{}).Where("id = ?", id).Update("deleted_at", now).Error
}

func (r *itemRepository) Count(ctx context.Context, filter ItemFilter) (int64, error) {
	db := tx.GetDB(ctx, r.db)
	var count int64
	query := db.WithContext(ctx).Model(&models.Item{}).Where("deleted_at IS NULL")

	if filter.ProjectID != nil {
		query = query.Where("project_id = ?", *filter.ProjectID)
	}
	if filter.Type != nil {
		query = query.Where("type = ?", *filter.Type)
	}
	if filter.Status != nil {
		query = query.Where("status = ?", *filter.Status)
	}

	err := query.Count(&count).Error
	return count, err
}

// Link Repository Implementation

type linkRepository struct {
	db *gorm.DB
}

// NewLinkRepository returns a GORM-based LinkRepository.
func NewLinkRepository(db *gorm.DB) LinkRepository {
	return &linkRepository{db: db}
}

func (r *linkRepository) Create(ctx context.Context, link *models.Link) error {
	db := tx.GetDB(ctx, r.db)
	return db.WithContext(ctx).Create(link).Error
}

func (r *linkRepository) GetByID(ctx context.Context, id string) (*models.Link, error) {
	db := tx.GetDB(ctx, r.db)
	var link models.Link
	err := db.WithContext(ctx).Where("id = ?", id).First(&link).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("link not found")
		}
		return nil, err
	}
	return &link, nil
}

func (r *linkRepository) GetBySourceID(ctx context.Context, sourceID string) ([]*models.Link, error) {
	db := tx.GetDB(ctx, r.db)
	var links []*models.Link
	err := db.WithContext(ctx).Where("source_id = ?", sourceID).Find(&links).Error
	return links, err
}

func (r *linkRepository) GetByTargetID(ctx context.Context, targetID string) ([]*models.Link, error) {
	db := tx.GetDB(ctx, r.db)
	var links []*models.Link
	err := db.WithContext(ctx).Where("target_id = ?", targetID).Find(&links).Error
	return links, err
}

func (r *linkRepository) List(ctx context.Context, filter LinkFilter) ([]*models.Link, error) {
	db := tx.GetDB(ctx, r.db)
	var links []*models.Link
	query := db.WithContext(ctx)

	if filter.ProjectID != nil {
		// Restrict to links whose source and target items belong to the project
		sub := db.WithContext(ctx).Model(&models.Item{}).Select("id").Where("project_id = ? AND deleted_at IS NULL", *filter.ProjectID)
		query = query.Where("source_id IN (?) AND target_id IN (?)", sub, sub)
	}
	if filter.SourceID != nil {
		query = query.Where("source_id = ?", *filter.SourceID)
	}
	if filter.TargetID != nil {
		query = query.Where("target_id = ?", *filter.TargetID)
	}
	if filter.Type != nil {
		query = query.Where("type = ?", *filter.Type)
	}

	if filter.Limit > 0 {
		query = query.Limit(filter.Limit)
	}
	if filter.Offset > 0 {
		query = query.Offset(filter.Offset)
	}

	err := query.Order("created_at DESC").Find(&links).Error
	return links, err
}

func (r *linkRepository) Update(ctx context.Context, link *models.Link) error {
	db := tx.GetDB(ctx, r.db)
	link.UpdatedAt = time.Now()
	return db.WithContext(ctx).Save(link).Error
}

func (r *linkRepository) Delete(ctx context.Context, id string) error {
	db := tx.GetDB(ctx, r.db)
	return db.WithContext(ctx).Delete(&models.Link{}, "id = ?", id).Error
}

func (r *linkRepository) DeleteByItemID(ctx context.Context, itemID string) error {
	db := tx.GetDB(ctx, r.db)
	return db.WithContext(ctx).Where("source_id = ? OR target_id = ?", itemID, itemID).Delete(&models.Link{}).Error
}

// Project Repository Implementation

type projectRepository struct {
	db *gorm.DB
}

// NewProjectRepository returns a GORM-based ProjectRepository.
func NewProjectRepository(db *gorm.DB) ProjectRepository {
	return &projectRepository{db: db}
}

func (r *projectRepository) Create(ctx context.Context, project *models.Project) error {
	db := tx.GetDB(ctx, r.db)
	return db.WithContext(ctx).Create(project).Error
}

func (r *projectRepository) GetByID(ctx context.Context, id string) (*models.Project, error) {
	db := tx.GetDB(ctx, r.db)
	var project models.Project
	err := db.WithContext(ctx).Where("id = ? AND deleted_at IS NULL", id).First(&project).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("project not found")
		}
		return nil, err
	}
	return &project, nil
}

func (r *projectRepository) List(ctx context.Context) ([]*models.Project, error) {
	db := tx.GetDB(ctx, r.db)
	var projects []*models.Project
	err := db.WithContext(ctx).Where("deleted_at IS NULL").Order("created_at DESC").Find(&projects).Error
	return projects, err
}

func (r *projectRepository) Update(ctx context.Context, project *models.Project) error {
	db := tx.GetDB(ctx, r.db)
	project.UpdatedAt = time.Now()
	return db.WithContext(ctx).Save(project).Error
}

func (r *projectRepository) Delete(ctx context.Context, id string) error {
	db := tx.GetDB(ctx, r.db)
	now := time.Now()
	return db.WithContext(ctx).Model(&models.Project{}).Where("id = ?", id).Update("deleted_at", now).Error
}

// Agent Repository Implementation

type agentRepository struct {
	db *gorm.DB
}

// NewAgentRepository returns a GORM-based AgentRepository.
func NewAgentRepository(db *gorm.DB) AgentRepository {
	return &agentRepository{db: db}
}

func (r *agentRepository) Create(ctx context.Context, agent *models.Agent) error {
	return r.db.WithContext(ctx).Create(agent).Error
}

func (r *agentRepository) GetByID(ctx context.Context, id string) (*models.Agent, error) {
	var agent models.Agent
	err := r.db.WithContext(ctx).Where("id = ?", id).First(&agent).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("agent not found")
		}
		return nil, err
	}
	return &agent, nil
}

func (r *agentRepository) GetByProjectID(ctx context.Context, projectID string) ([]*models.Agent, error) {
	var agents []*models.Agent
	err := r.db.WithContext(ctx).Where("project_id = ?", projectID).Find(&agents).Error
	return agents, err
}

func (r *agentRepository) List(ctx context.Context) ([]*models.Agent, error) {
	var agents []*models.Agent
	err := r.db.WithContext(ctx).Order("created_at DESC").Find(&agents).Error
	return agents, err
}

func (r *agentRepository) Update(ctx context.Context, agent *models.Agent) error {
	agent.UpdatedAt = time.Now()
	return r.db.WithContext(ctx).Save(agent).Error
}

func (r *agentRepository) UpdateStatus(ctx context.Context, id, status string) error {
	return r.db.WithContext(ctx).Model(&models.Agent{}).Where("id = ?", id).Updates(map[string]interface{}{
		"status":     status,
		"updated_at": time.Now(),
	}).Error
}

func (r *agentRepository) Delete(ctx context.Context, id string) error {
	return r.db.WithContext(ctx).Delete(&models.Agent{}, "id = ?", id).Error
}

// View Repository Implementation

type viewRepository struct {
	db *gorm.DB
}

// NewViewRepository returns a GORM-based ViewRepository.
func NewViewRepository(db *gorm.DB) ViewRepository {
	return &viewRepository{db: db}
}

func (r *viewRepository) Create(ctx context.Context, view *models.View) error {
	db := tx.GetDB(ctx, r.db)
	return db.WithContext(ctx).Create(view).Error
}

func (r *viewRepository) GetByID(ctx context.Context, id string) (*models.View, error) {
	db := tx.GetDB(ctx, r.db)
	var view models.View
	err := db.WithContext(ctx).Where("id = ?", id).First(&view).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("view not found")
		}
		return nil, err
	}
	return &view, nil
}

func (r *viewRepository) GetByProjectID(ctx context.Context, projectID string) ([]*models.View, error) {
	db := tx.GetDB(ctx, r.db)
	var views []*models.View
	err := db.WithContext(ctx).Where("project_id = ?", projectID).Order("created_at DESC").Find(&views).Error
	return views, err
}

func (r *viewRepository) List(ctx context.Context) ([]*models.View, error) {
	db := tx.GetDB(ctx, r.db)
	var views []*models.View
	err := db.WithContext(ctx).Order("created_at DESC").Find(&views).Error
	return views, err
}

func (r *viewRepository) Update(ctx context.Context, view *models.View) error {
	db := tx.GetDB(ctx, r.db)
	view.UpdatedAt = time.Now()
	return db.WithContext(ctx).Save(view).Error
}

func (r *viewRepository) Delete(ctx context.Context, id string) error {
	db := tx.GetDB(ctx, r.db)
	return db.WithContext(ctx).Delete(&models.View{}, "id = ?", id).Error
}

func (r *viewRepository) CountItemsByView(_ context.Context, _ string) (int64, error) {
	var count int64
	// This is a placeholder - actual implementation would depend on how items are associated with views
	// For now, we'll return 0 as views don't have direct item associations in the current schema
	return count, nil
}
