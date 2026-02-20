// Package repository provides data access for items, links, projects, code entities, and related aggregates.
package repository

import (
	"context"
	"errors"
	"time"

	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

const codeEntityBatchSize = 100

// CodeEntityRepository defines methods for code entity data access
type CodeEntityRepository interface {
	Create(ctx context.Context, entity *models.CodeEntity) error
	GetByID(ctx context.Context, id string) (*models.CodeEntity, error)
	GetByProjectID(ctx context.Context, projectID string, limit, offset int) ([]*models.CodeEntity, error)
	List(ctx context.Context, filter CodeEntityFilter) ([]*models.CodeEntity, error)
	Update(ctx context.Context, entity *models.CodeEntity) error
	Delete(ctx context.Context, id string) error
	DeleteByProjectID(ctx context.Context, projectID string) error
	Search(ctx context.Context, projectID string, query string, limit, offset int) ([]*models.CodeEntity, error)
	GetByType(ctx context.Context, projectID string, entityType string) ([]*models.CodeEntity, error)
	GetByFilePath(ctx context.Context, projectID, filePath string) ([]*models.CodeEntity, error)
	Count(ctx context.Context, projectID string) (int64, error)
	GetStats(ctx context.Context, projectID string) (*models.CodeIndexStats, error)
	BatchCreate(ctx context.Context, entities []*models.CodeEntity) error
	BatchDelete(ctx context.Context, ids []string) error
}

// CodeEntityRelationshipRepository defines methods for code entity relationship data access
type CodeEntityRelationshipRepository interface {
	Create(ctx context.Context, rel *models.CodeEntityRelationship) error
	GetByID(ctx context.Context, id string) (*models.CodeEntityRelationship, error)
	GetBySourceID(ctx context.Context, sourceID string) ([]*models.CodeEntityRelationship, error)
	GetByTargetID(ctx context.Context, targetID string) ([]*models.CodeEntityRelationship, error)
	List(ctx context.Context, filter CodeEntityRelationshipFilter) ([]*models.CodeEntityRelationship, error)
	Update(ctx context.Context, rel *models.CodeEntityRelationship) error
	Delete(ctx context.Context, id string) error
	DeleteByProjectID(ctx context.Context, projectID string) error
	GetRelationships(ctx context.Context, entityID string) ([]*models.CodeEntityRelationship, error)
	BatchCreate(ctx context.Context, relationships []*models.CodeEntityRelationship) error
}

// CodeEntityFilter filters code entity list/query results.
type CodeEntityFilter struct {
	ProjectID  string
	EntityType string
	Language   string
	FilePath   string
	Limit      int
	Offset     int
}

// CodeEntityRelationshipFilter filters code entity relationship list/query results.
type CodeEntityRelationshipFilter struct {
	ProjectID    string
	RelationType string
	Limit        int
	Offset       int
}

// GORM Implementation for CodeEntityRepository

type codeEntityRepository struct {
	db *gorm.DB
}

// NewCodeEntityRepository returns a GORM-based CodeEntityRepository.
func NewCodeEntityRepository(db *gorm.DB) CodeEntityRepository {
	return &codeEntityRepository{db: db}
}

func (r *codeEntityRepository) Create(ctx context.Context, entity *models.CodeEntity) error {
	return r.db.WithContext(ctx).Create(entity).Error
}

func (r *codeEntityRepository) GetByID(ctx context.Context, id string) (*models.CodeEntity, error) {
	var entity models.CodeEntity
	err := r.db.WithContext(ctx).Where("id = ? AND deleted_at IS NULL", id).First(&entity).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("code entity not found")
		}
		return nil, err
	}
	return &entity, nil
}

func (r *codeEntityRepository) GetByProjectID(ctx context.Context, projectID string, limit, offset int) ([]*models.CodeEntity, error) {
	var entities []*models.CodeEntity
	query := r.db.WithContext(ctx).Where("project_id = ? AND deleted_at IS NULL", projectID)

	if limit > 0 {
		query = query.Limit(limit)
	}
	if offset > 0 {
		query = query.Offset(offset)
	}

	err := query.Order("created_at DESC").Find(&entities).Error
	return entities, err
}

func (r *codeEntityRepository) List(ctx context.Context, filter CodeEntityFilter) ([]*models.CodeEntity, error) {
	var entities []*models.CodeEntity
	query := r.db.WithContext(ctx).Where("project_id = ? AND deleted_at IS NULL", filter.ProjectID)

	if filter.EntityType != "" {
		query = query.Where("symbol_type = ?", filter.EntityType)
	}
	if filter.Language != "" {
		query = query.Where("language = ?", filter.Language)
	}
	if filter.FilePath != "" {
		query = query.Where("file_path = ?", filter.FilePath)
	}

	if filter.Limit > 0 {
		query = query.Limit(filter.Limit)
	}
	if filter.Offset > 0 {
		query = query.Offset(filter.Offset)
	}

	err := query.Order("file_path, start_line").Find(&entities).Error
	return entities, err
}

func (r *codeEntityRepository) Update(ctx context.Context, entity *models.CodeEntity) error {
	entity.UpdatedAt = time.Now()
	return r.db.WithContext(ctx).Save(entity).Error
}

func (r *codeEntityRepository) Delete(ctx context.Context, id string) error {
	now := time.Now()
	return r.db.WithContext(ctx).Model(&models.CodeEntity{}).Where("id = ?", id).Update("deleted_at", now).Error
}

func (r *codeEntityRepository) DeleteByProjectID(ctx context.Context, projectID string) error {
	now := time.Now()
	return r.db.WithContext(ctx).Model(&models.CodeEntity{}).
		Where("project_id = ?", projectID).
		Update("deleted_at", now).Error
}

func (r *codeEntityRepository) Search(
	ctx context.Context, projectID, query string, limit, offset int,
) ([]*models.CodeEntity, error) {
	var entities []*models.CodeEntity
	// Use LIKE for case-insensitive search (works in both PostgreSQL and SQLite)
	// Note: GORM will use ILIKE automatically for PostgreSQL when using LIKE
	dbQuery := r.db.WithContext(ctx).Where("project_id = ? AND deleted_at IS NULL", projectID).
		Where("symbol_name LIKE ? OR qualified_name LIKE ? OR docstring LIKE ?",
			"%"+query+"%", "%"+query+"%", "%"+query+"%")

	if limit > 0 {
		dbQuery = dbQuery.Limit(limit)
	}
	if offset > 0 {
		dbQuery = dbQuery.Offset(offset)
	}

	err := dbQuery.Order("created_at DESC").Find(&entities).Error
	return entities, err
}

func (r *codeEntityRepository) GetByType(ctx context.Context, projectID string, entityType string) ([]*models.CodeEntity, error) {
	var entities []*models.CodeEntity
	err := r.db.WithContext(ctx).
		Where("project_id = ? AND symbol_type = ? AND deleted_at IS NULL", projectID, entityType).
		Order("file_path, start_line").
		Find(&entities).Error
	return entities, err
}

func (r *codeEntityRepository) GetByFilePath(ctx context.Context, projectID, filePath string) ([]*models.CodeEntity, error) {
	var entities []*models.CodeEntity
	err := r.db.WithContext(ctx).
		Where("project_id = ? AND file_path = ? AND deleted_at IS NULL", projectID, filePath).
		Order("start_line").
		Find(&entities).Error
	return entities, err
}

func (r *codeEntityRepository) Count(ctx context.Context, projectID string) (int64, error) {
	var count int64
	err := r.db.WithContext(ctx).Model(&models.CodeEntity{}).
		Where("project_id = ? AND deleted_at IS NULL", projectID).
		Count(&count).Error
	return count, err
}

// GetStats returns statistics about code entities in a project.
func (r *codeEntityRepository) GetStats(ctx context.Context, projectID string) (*models.CodeIndexStats, error) {
	stats := &models.CodeIndexStats{
		ProjectID:          projectID,
		EntitiesByType:     make(map[string]int64),
		EntitiesByLanguage: make(map[string]int64),
	}

	if err := r.countEntities(ctx, projectID, &stats.TotalEntities); err != nil {
		return nil, err
	}
	if err := r.fillEntitiesByType(ctx, projectID, stats.EntitiesByType); err != nil {
		return nil, err
	}
	if err := r.fillEntitiesByLanguage(ctx, projectID, stats.EntitiesByLanguage); err != nil {
		return nil, err
	}

	lastIndexed, err := r.fetchLastIndexed(ctx, projectID)
	if err != nil {
		return nil, err
	}
	stats.LastIndexedAt = lastIndexed

	if err := r.countRelationships(ctx, projectID, &stats.TotalRelations); err != nil {
		return nil, err
	}

	stats.UpdatedAt = time.Now()
	return stats, nil
}

type codeEntityTypeCount struct {
	EntityType string
	Count      int64
}

type codeEntityLangCount struct {
	Language string
	Count    int64
}

func (r *codeEntityRepository) countEntities(ctx context.Context, projectID string, dest *int64) error {
	return r.db.WithContext(ctx).Model(&models.CodeEntity{}).
		Where("project_id = ? AND deleted_at IS NULL", projectID).
		Count(dest).Error
}

func (r *codeEntityRepository) fillEntitiesByType(ctx context.Context, projectID string, dest map[string]int64) error {
	var results []codeEntityTypeCount
	if err := r.db.WithContext(ctx).Model(&models.CodeEntity{}).
		Where("project_id = ? AND deleted_at IS NULL", projectID).
		Group("symbol_type").
		Select("symbol_type, COUNT(*) as count").
		Scan(&results).Error; err != nil {
		return err
	}
	for _, tr := range results {
		dest[tr.EntityType] = tr.Count
	}
	return nil
}

func (r *codeEntityRepository) fillEntitiesByLanguage(ctx context.Context, projectID string, dest map[string]int64) error {
	var results []codeEntityLangCount
	if err := r.db.WithContext(ctx).Model(&models.CodeEntity{}).
		Where("project_id = ? AND deleted_at IS NULL", projectID).
		Group("language").
		Select("language, COUNT(*) as count").
		Scan(&results).Error; err != nil {
		return err
	}
	for _, lr := range results {
		dest[lr.Language] = lr.Count
	}
	return nil
}

func (r *codeEntityRepository) fetchLastIndexed(ctx context.Context, projectID string) (time.Time, error) {
	var lastIndexed time.Time
	if err := r.db.WithContext(ctx).Model(&models.CodeEntity{}).
		Where("project_id = ? AND deleted_at IS NULL", projectID).
		Order("indexed_at DESC").
		Select("indexed_at").
		Scan(&lastIndexed).Error; err != nil {
		if !errors.Is(err, gorm.ErrRecordNotFound) {
			return time.Time{}, err
		}
	}
	return lastIndexed, nil
}

func (r *codeEntityRepository) countRelationships(ctx context.Context, projectID string, dest *int64) error {
	return r.db.WithContext(ctx).Model(&models.CodeEntityRelationship{}).
		Where("project_id = ?", projectID).
		Count(dest).Error
}

func (r *codeEntityRepository) BatchCreate(ctx context.Context, entities []*models.CodeEntity) error {
	if len(entities) == 0 {
		return nil
	}
	return r.db.WithContext(ctx).CreateInBatches(entities, codeEntityBatchSize).Error
}

func (r *codeEntityRepository) BatchDelete(ctx context.Context, ids []string) error {
	if len(ids) == 0 {
		return nil
	}
	now := time.Now()
	return r.db.WithContext(ctx).Model(&models.CodeEntity{}).
		Where("id IN ?", ids).
		Update("deleted_at", now).Error
}

// GORM Implementation for CodeEntityRelationshipRepository

type codeEntityRelationshipRepository struct {
	db *gorm.DB
}

// NewCodeEntityRelationshipRepository returns a GORM-based CodeEntityRelationshipRepository.
func NewCodeEntityRelationshipRepository(db *gorm.DB) CodeEntityRelationshipRepository {
	return &codeEntityRelationshipRepository{db: db}
}

func (r *codeEntityRelationshipRepository) Create(ctx context.Context, rel *models.CodeEntityRelationship) error {
	return r.db.WithContext(ctx).Create(rel).Error
}

func (r *codeEntityRelationshipRepository) GetByID(ctx context.Context, id string) (*models.CodeEntityRelationship, error) {
	var rel models.CodeEntityRelationship
	err := r.db.WithContext(ctx).Where("id = ?", id).First(&rel).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("code entity relationship not found")
		}
		return nil, err
	}
	return &rel, nil
}

func (r *codeEntityRelationshipRepository) GetBySourceID(ctx context.Context, sourceID string) ([]*models.CodeEntityRelationship, error) {
	var rels []*models.CodeEntityRelationship
	err := r.db.WithContext(ctx).Where("source_id = ?", sourceID).Find(&rels).Error
	return rels, err
}

func (r *codeEntityRelationshipRepository) GetByTargetID(ctx context.Context, targetID string) ([]*models.CodeEntityRelationship, error) {
	var rels []*models.CodeEntityRelationship
	err := r.db.WithContext(ctx).Where("target_id = ?", targetID).Find(&rels).Error
	return rels, err
}

func (r *codeEntityRelationshipRepository) List(
	ctx context.Context, filter CodeEntityRelationshipFilter,
) ([]*models.CodeEntityRelationship, error) {
	var rels []*models.CodeEntityRelationship
	query := r.db.WithContext(ctx).Where("project_id = ?", filter.ProjectID)

	if filter.RelationType != "" {
		query = query.Where("relation_type = ?", filter.RelationType)
	}

	if filter.Limit > 0 {
		query = query.Limit(filter.Limit)
	}
	if filter.Offset > 0 {
		query = query.Offset(filter.Offset)
	}

	err := query.Order("created_at DESC").Find(&rels).Error
	return rels, err
}

func (r *codeEntityRelationshipRepository) Update(ctx context.Context, rel *models.CodeEntityRelationship) error {
	rel.UpdatedAt = time.Now()
	return r.db.WithContext(ctx).Save(rel).Error
}

func (r *codeEntityRelationshipRepository) Delete(ctx context.Context, id string) error {
	return r.db.WithContext(ctx).Delete(&models.CodeEntityRelationship{}, "id = ?", id).Error
}

func (r *codeEntityRelationshipRepository) DeleteByProjectID(ctx context.Context, projectID string) error {
	return r.db.WithContext(ctx).Where("project_id = ?", projectID).Delete(&models.CodeEntityRelationship{}).Error
}

func (r *codeEntityRelationshipRepository) GetRelationships(
	ctx context.Context, entityID string,
) ([]*models.CodeEntityRelationship, error) {
	var rels []*models.CodeEntityRelationship
	err := r.db.WithContext(ctx).
		Where("source_id = ? OR target_id = ?", entityID, entityID).
		Find(&rels).Error
	return rels, err
}

func (r *codeEntityRelationshipRepository) BatchCreate(ctx context.Context, relationships []*models.CodeEntityRelationship) error {
	if len(relationships) == 0 {
		return nil
	}
	return r.db.WithContext(ctx).CreateInBatches(relationships, codeEntityBatchSize).Error
}
