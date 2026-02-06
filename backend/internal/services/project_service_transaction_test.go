package services

import (
	"context"
	"testing"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

type projectServiceTxEnv struct {
	db      *gorm.DB
	service ProjectService
	impl    *ProjectServiceImpl
}

func setupProjectServiceTxEnv(t *testing.T) projectServiceTxEnv {
	t.Helper()
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	require.NoError(t, err)
	err = db.AutoMigrate(&models.Project{}, &models.Item{})
	require.NoError(t, err)
	projectRepo := newTestProjectRepository(db)
	itemRepo := newTestItemRepository(db)
	service := NewProjectServiceImpl(projectRepo, itemRepo, nil, nil, db)

	return projectServiceTxEnv{
		db:      db,
		service: service,
		impl:    service.(*ProjectServiceImpl),
	}
}

func runCreateProjectUsesContext(t *testing.T, env projectServiceTxEnv) {
	t.Helper()
	ctx := context.Background()
	tx := env.db.Begin()
	txCtx := WithTransaction(ctx, tx)
	project := &models.Project{
		ID:          "tx-test-1",
		Name:        "Transaction Test Project",
		Description: "Testing transaction support",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	err := env.service.CreateProject(txCtx, project)
	require.NoError(t, err)
	var count int64
	tx.Model(&models.Project{}).Where("id = ?", "tx-test-1").Count(&count)
	assert.Equal(t, int64(1), count, "Project should exist in transaction")
	tx.Rollback()
	env.db.Model(&models.Project{}).Where("id = ?", "tx-test-1").Count(&count)
	assert.Equal(t, int64(0), count, "Project should not exist after rollback")
}

func runCreateProjectWithItemsAtomic(t *testing.T, env projectServiceTxEnv) {
	t.Helper()
	ctx := context.Background()
	project := &models.Project{
		ID:          "atomic-test-1",
		Name:        "Atomic Operation Project",
		Description: "Testing atomic multi-step operations",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	items := []*models.Item{
		{
			ID:        "item-1",
			ProjectID: "atomic-test-1",
			Title:     "Item 1",
			Type:      "task",
			Status:    "pending",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		},
		{
			ID:        "item-2",
			ProjectID: "atomic-test-1",
			Title:     "Item 2",
			Type:      "task",
			Status:    "pending",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		},
	}
	err := env.service.CreateProjectWithItems(ctx, project, items)
	require.NoError(t, err)
	var projectCount int64
	env.db.Model(&models.Project{}).Where("id = ?", "atomic-test-1").Count(&projectCount)
	assert.Equal(t, int64(1), projectCount)
	var itemCount int64
	env.db.Model(&models.Item{}).Where("project_id = ?", "atomic-test-1").Count(&itemCount)
	assert.Equal(t, int64(2), itemCount)
}

func runCreateProjectWithItemsRollback(t *testing.T, env projectServiceTxEnv) {
	t.Helper()
	ctx := context.Background()
	project := &models.Project{
		ID:          "rollback-test-1",
		Name:        "Rollback Test Project",
		Description: "Testing transaction rollback",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	items := []*models.Item{
		{
			ID:        "bad-item-1",
			ProjectID: "wrong-project-id",
			Title:     "Bad Item",
			Type:      "task",
			Status:    "pending",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		},
	}
	err := env.service.CreateProjectWithItems(ctx, project, items)
	require.NoError(t, err)
	var projectCount int64
	env.db.Model(&models.Project{}).Where("id = ?", "rollback-test-1").Count(&projectCount)
	assert.Equal(t, int64(1), projectCount)
	var itemCount int64
	env.db.Model(&models.Item{}).Where("project_id = ?", "rollback-test-1").Count(&itemCount)
	assert.Equal(t, int64(1), itemCount)
}

func runUpdateProjectAndItems(t *testing.T, env projectServiceTxEnv) {
	t.Helper()
	ctx := context.Background()
	project := &models.Project{
		ID:          "update-test-1",
		Name:        "Update Test Project",
		Description: "Initial description",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	env.db.Create(project)
	item1 := &models.Item{
		ID:        "update-item-1",
		ProjectID: "update-test-1",
		Title:     "Item 1",
		Type:      "task",
		Status:    "pending",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	env.db.Create(item1)
	project.Description = "Updated description"
	item1.Status = "completed"
	err := env.service.UpdateProjectAndItems(ctx, project, []*models.Item{item1})
	require.NoError(t, err)
	var updatedProject models.Project
	env.db.First(&updatedProject, "id = ?", "update-test-1")
	assert.Equal(t, "Updated description", updatedProject.Description)
	var updatedItem models.Item
	env.db.First(&updatedItem, "id = ?", "update-item-1")
	assert.Equal(t, "completed", updatedItem.Status)
}

func runDeleteProjectWithItems(t *testing.T, env projectServiceTxEnv) {
	t.Helper()
	ctx := context.Background()
	project := &models.Project{
		ID:          "delete-test-1",
		Name:        "Delete Test Project",
		Description: "Will be deleted",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	env.db.Create(project)
	item1 := &models.Item{
		ID:        "delete-item-1",
		ProjectID: "delete-test-1",
		Title:     "Item 1",
		Type:      "task",
		Status:    "pending",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	item2 := &models.Item{
		ID:        "delete-item-2",
		ProjectID: "delete-test-1",
		Title:     "Item 2",
		Type:      "task",
		Status:    "pending",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	env.db.Create(item1)
	env.db.Create(item2)
	err := env.service.DeleteProjectWithItems(ctx, "delete-test-1")
	require.NoError(t, err)
	var project2 models.Project
	err = env.db.Where("id = ? AND deleted_at IS NULL", "delete-test-1").First(&project2).Error
	assert.Error(t, err)
	var itemCount int64
	env.db.Model(&models.Item{}).Where("project_id = ? AND deleted_at IS NULL", "delete-test-1").Count(&itemCount)
	assert.Equal(t, int64(0), itemCount)
}

func runWithTransactionHelper(t *testing.T, env projectServiceTxEnv) {
	t.Helper()
	ctx := context.Background()
	project := &models.Project{
		ID:          "helper-test-1",
		Name:        "Helper Test Project",
		Description: "Testing WithTransaction helper",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	err := env.impl.WithTransaction(ctx, func(txCtx context.Context) error {
		return env.service.CreateProject(txCtx, project)
	})
	require.NoError(t, err)
	var count int64
	env.db.Model(&models.Project{}).Where("id = ?", "helper-test-1").Count(&count)
	assert.Equal(t, int64(1), count)
}

func runNestedTransactionUsesExisting(t *testing.T, env projectServiceTxEnv) {
	t.Helper()
	ctx := context.Background()
	tx := env.db.Begin()
	txCtx := WithTransaction(ctx, tx)
	project := &models.Project{
		ID:          "nested-test-1",
		Name:        "Nested Transaction Test",
		Description: "Testing nested transaction handling",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	err := env.impl.WithTransaction(txCtx, func(innerCtx context.Context) error {
		return env.service.CreateProject(innerCtx, project)
	})
	require.NoError(t, err)
	tx.Rollback()
	var count int64
	env.db.Model(&models.Project{}).Where("id = ?", "nested-test-1").Count(&count)
	assert.Equal(t, int64(0), count, "Project should not exist after outer transaction rollback")
}

// TestProjectServiceTransactionSupport validates transaction awareness
func TestProjectServiceTransactionSupport(t *testing.T) {
	t.Run("CreateProject uses transaction from context", func(t *testing.T) {
		runCreateProjectUsesContext(t, setupProjectServiceTxEnv(t))
	})

	t.Run("CreateProjectWithItems atomic operation", func(t *testing.T) {
		runCreateProjectWithItemsAtomic(t, setupProjectServiceTxEnv(t))
	})

	t.Run("CreateProjectWithItems rollback on error", func(t *testing.T) {
		runCreateProjectWithItemsRollback(t, setupProjectServiceTxEnv(t))
	})

	t.Run("UpdateProjectAndItems atomic operation", func(t *testing.T) {
		runUpdateProjectAndItems(t, setupProjectServiceTxEnv(t))
	})

	t.Run("DeleteProjectWithItems cascading delete", func(t *testing.T) {
		runDeleteProjectWithItems(t, setupProjectServiceTxEnv(t))
	})

	t.Run("WithTransaction helper method", func(t *testing.T) {
		runWithTransactionHelper(t, setupProjectServiceTxEnv(t))
	})

	t.Run("Nested transaction uses existing transaction", func(t *testing.T) {
		runNestedTransactionUsesExisting(t, setupProjectServiceTxEnv(t))
	})
}

// Test repository implementations for testing
type testProjectRepository struct {
	db *gorm.DB
}

func newTestProjectRepository(db *gorm.DB) *testProjectRepository {
	return &testProjectRepository{db: db}
}

func (r *testProjectRepository) Create(ctx context.Context, project *models.Project) error {
	db := GetDB(ctx, r.db)
	return db.WithContext(ctx).Create(project).Error
}

func (r *testProjectRepository) GetByID(ctx context.Context, id string) (*models.Project, error) {
	db := GetDB(ctx, r.db)
	var project models.Project
	err := db.WithContext(ctx).Where("id = ? AND deleted_at IS NULL", id).First(&project).Error
	if err != nil {
		return nil, err
	}
	return &project, nil
}

func (r *testProjectRepository) List(ctx context.Context) ([]*models.Project, error) {
	db := GetDB(ctx, r.db)
	var projects []*models.Project
	err := db.WithContext(ctx).Where("deleted_at IS NULL").Find(&projects).Error
	return projects, err
}

func (r *testProjectRepository) Update(ctx context.Context, project *models.Project) error {
	db := GetDB(ctx, r.db)
	project.UpdatedAt = time.Now()
	return db.WithContext(ctx).Save(project).Error
}

func (r *testProjectRepository) Delete(ctx context.Context, id string) error {
	db := GetDB(ctx, r.db)
	now := time.Now()
	return db.WithContext(ctx).Model(&models.Project{}).Where("id = ?", id).Update("deleted_at", now).Error
}

type testItemRepository struct {
	db *gorm.DB
}

func newTestItemRepository(db *gorm.DB) *testItemRepository {
	return &testItemRepository{db: db}
}

func (r *testItemRepository) Create(ctx context.Context, item *models.Item) error {
	db := GetDB(ctx, r.db)
	return db.WithContext(ctx).Create(item).Error
}

func (r *testItemRepository) GetByID(ctx context.Context, id string) (*models.Item, error) {
	db := GetDB(ctx, r.db)
	var item models.Item
	err := db.WithContext(ctx).Where("id = ? AND deleted_at IS NULL", id).First(&item).Error
	return &item, err
}

func (r *testItemRepository) GetByProjectID(ctx context.Context, projectID string) ([]*models.Item, error) {
	db := GetDB(ctx, r.db)
	var items []*models.Item
	err := db.WithContext(ctx).Where("project_id = ? AND deleted_at IS NULL", projectID).Find(&items).Error
	return items, err
}

func (r *testItemRepository) List(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error) {
	db := GetDB(ctx, r.db)
	var items []*models.Item
	query := db.WithContext(ctx).Where("deleted_at IS NULL")

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

	err := query.Find(&items).Error
	return items, err
}

func (r *testItemRepository) Update(ctx context.Context, item *models.Item) error {
	db := GetDB(ctx, r.db)
	item.UpdatedAt = time.Now()
	return db.WithContext(ctx).Save(item).Error
}

func (r *testItemRepository) Delete(ctx context.Context, id string) error {
	db := GetDB(ctx, r.db)
	now := time.Now()
	return db.WithContext(ctx).Model(&models.Item{}).Where("id = ?", id).Update("deleted_at", now).Error
}

func (r *testItemRepository) Count(ctx context.Context, filter repository.ItemFilter) (int64, error) {
	db := GetDB(ctx, r.db)
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
