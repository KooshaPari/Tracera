package repository

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

func setupCodeEntityRepoTest(t *testing.T) *gorm.DB {
	db, err := gorm.Open(getTestDialector(), &gorm.Config{})
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}

	// Auto migrate
	if err := db.AutoMigrate(&models.CodeEntity{}, &models.CodeEntityRelationship{}); err != nil {
		t.Fatalf("Failed to migrate: %v", err)
	}

	return db
}

func getTestDialector() gorm.Dialector {
	return sqlite.Open(":memory:")
}

const (
	testProjectID          = "project-1"
	testUpdatedDescription = "Updated description"
)

func TestCodeEntityRepository_Create(t *testing.T) {
	db := setupCodeEntityRepoTest(t)
	t.Cleanup(func() { require.NoError(t, db.Migrator().DropTable(&models.CodeEntity{})) })

	repo := NewCodeEntityRepository(db)
	ctx := context.Background()

	entity := &models.CodeEntity{
		ProjectID:     testProjectID,
		EntityType:    "function",
		Name:          "test",
		FullName:      "pkg.test",
		FilePath:      "test.go",
		Language:      "go",
		LineNumber:    1,
		EndLineNumber: 5,
		CodeSnippet:   "func test() {}",
		IndexedAt:     time.Now(),
	}

	err := repo.Create(ctx, entity)
	require.NoError(t, err)
	assert.NotEmpty(t, entity.ID)
}

func TestCodeEntityRepository_GetByID(t *testing.T) {
	db := setupCodeEntityRepoTest(t)
	t.Cleanup(func() { require.NoError(t, db.Migrator().DropTable(&models.CodeEntity{})) })

	repo := NewCodeEntityRepository(db)
	ctx := context.Background()

	entity := &models.CodeEntity{
		ProjectID:   testProjectID,
		EntityType:  "function",
		Name:        "test",
		FullName:    "pkg.test",
		FilePath:    "test.go",
		Language:    "go",
		LineNumber:  1,
		CodeSnippet: "func test() {}",
		IndexedAt:   time.Now(),
	}

	err := repo.Create(ctx, entity)
	require.NoError(t, err)

	fetched, err := repo.GetByID(ctx, entity.ID)
	require.NoError(t, err)
	assert.Equal(t, entity.ID, fetched.ID)
	assert.Equal(t, "test", fetched.Name)
}

func TestCodeEntityRepository_GetByProjectID(t *testing.T) {
	db := setupCodeEntityRepoTest(t)
	t.Cleanup(func() { require.NoError(t, db.Migrator().DropTable(&models.CodeEntity{})) })

	repo := NewCodeEntityRepository(db)
	ctx := context.Background()
	projectID := testProjectID

	// Create multiple entities
	for i := 0; i < 5; i++ {
		entity := &models.CodeEntity{
			ProjectID:   projectID,
			EntityType:  "function",
			Name:        "test",
			FullName:    "pkg.test",
			FilePath:    "test.go",
			Language:    "go",
			LineNumber:  i + 1,
			CodeSnippet: "func test() {}",
			IndexedAt:   time.Now(),
		}
		err := repo.Create(ctx, entity)
		require.NoError(t, err)
	}

	entities, err := repo.GetByProjectID(ctx, projectID, 10, 0)
	require.NoError(t, err)
	assert.Len(t, entities, 5)
}

func TestCodeEntityRepository_List(t *testing.T) {
	db := setupCodeEntityRepoTest(t)
	t.Cleanup(func() { require.NoError(t, db.Migrator().DropTable(&models.CodeEntity{})) })

	repo := NewCodeEntityRepository(db)
	ctx := context.Background()
	projectID := testProjectID

	// Create entities with different types
	entities := []*models.CodeEntity{
		{
			ProjectID:  projectID,
			EntityType: "function",
			Name:       "func1",
			FullName:   "pkg.func1",
			Language:   "go",
			FilePath:   "test.go",
			IndexedAt:  time.Now(),
		},
		{
			ProjectID:  projectID,
			EntityType: "class",
			Name:       "MyClass",
			FullName:   "pkg.MyClass",
			Language:   "go",
			FilePath:   "test.go",
			IndexedAt:  time.Now(),
		},
	}

	for _, e := range entities {
		err := repo.Create(ctx, e)
		require.NoError(t, err)
	}

	filter := CodeEntityFilter{
		ProjectID:  projectID,
		EntityType: "function",
		Limit:      10,
	}

	results, err := repo.List(ctx, filter)
	require.NoError(t, err)
	assert.Len(t, results, 1)
	assert.Equal(t, "function", results[0].EntityType)
}

func TestCodeEntityRepository_Update(t *testing.T) {
	db := setupCodeEntityRepoTest(t)
	t.Cleanup(func() { require.NoError(t, db.Migrator().DropTable(&models.CodeEntity{})) })

	repo := NewCodeEntityRepository(db)
	ctx := context.Background()

	entity := &models.CodeEntity{
		ProjectID:   testProjectID,
		EntityType:  "function",
		Name:        "test",
		FullName:    "pkg.test",
		Description: "Original",
		FilePath:    "test.go",
		Language:    "go",
		IndexedAt:   time.Now(),
	}

	err := repo.Create(ctx, entity)
	require.NoError(t, err)

	entity.Description = testUpdatedDescription
	err = repo.Update(ctx, entity)
	require.NoError(t, err)

	fetched, err := repo.GetByID(ctx, entity.ID)
	require.NoError(t, err)
	assert.Equal(t, testUpdatedDescription, fetched.Description)
}

func TestCodeEntityRepository_Delete(t *testing.T) {
	db := setupCodeEntityRepoTest(t)
	t.Cleanup(func() { require.NoError(t, db.Migrator().DropTable(&models.CodeEntity{})) })

	repo := NewCodeEntityRepository(db)
	ctx := context.Background()

	entity := &models.CodeEntity{
		ProjectID:  testProjectID,
		EntityType: "function",
		Name:       "test",
		FullName:   "pkg.test",
		FilePath:   "test.go",
		Language:   "go",
		IndexedAt:  time.Now(),
	}

	err := repo.Create(ctx, entity)
	require.NoError(t, err)

	err = repo.Delete(ctx, entity.ID)
	require.NoError(t, err)

	// Verify soft delete
	_, err = repo.GetByID(ctx, entity.ID)
	require.Error(t, err)
}

func TestCodeEntityRepository_Search(t *testing.T) {
	db := setupCodeEntityRepoTest(t)
	t.Cleanup(func() { require.NoError(t, db.Migrator().DropTable(&models.CodeEntity{})) })

	repo := NewCodeEntityRepository(db)
	ctx := context.Background()
	projectID := testProjectID

	entities := []*models.CodeEntity{
		{
			ProjectID:   projectID,
			EntityType:  "function",
			Name:        "getUserByID",
			FullName:    "pkg.getUserByID",
			Description: "Get user by their ID",
			FilePath:    "user.go",
			Language:    "go",
			IndexedAt:   time.Now(),
		},
		{
			ProjectID:   projectID,
			EntityType:  "function",
			Name:        "getUser",
			FullName:    "pkg.getUser",
			Description: "Get user by username",
			FilePath:    "user.go",
			Language:    "go",
			IndexedAt:   time.Now(),
		},
	}

	for _, e := range entities {
		err := repo.Create(ctx, e)
		require.NoError(t, err)
	}

	results, err := repo.Search(ctx, projectID, "getUser", 10, 0)
	require.NoError(t, err)
	assert.GreaterOrEqual(t, len(results), 1)
}

func TestCodeEntityRepository_GetByType(t *testing.T) {
	db := setupCodeEntityRepoTest(t)
	t.Cleanup(func() { require.NoError(t, db.Migrator().DropTable(&models.CodeEntity{})) })

	repo := NewCodeEntityRepository(db)
	ctx := context.Background()
	projectID := testProjectID

	entities := []*models.CodeEntity{
		{
			ProjectID:  projectID,
			EntityType: "function",
			Name:       "func1",
			FullName:   "pkg.func1",
			FilePath:   "test.go",
			Language:   "go",
			IndexedAt:  time.Now(),
		},
		{
			ProjectID:  projectID,
			EntityType: "class",
			Name:       "MyClass",
			FullName:   "pkg.MyClass",
			FilePath:   "test.go",
			Language:   "go",
			IndexedAt:  time.Now(),
		},
	}

	for _, e := range entities {
		err := repo.Create(ctx, e)
		require.NoError(t, err)
	}

	results, err := repo.GetByType(ctx, projectID, "function")
	require.NoError(t, err)
	assert.Len(t, results, 1)
	assert.Equal(t, "function", results[0].EntityType)
}

func TestCodeEntityRepository_Count(t *testing.T) {
	db := setupCodeEntityRepoTest(t)
	t.Cleanup(func() { require.NoError(t, db.Migrator().DropTable(&models.CodeEntity{})) })

	repo := NewCodeEntityRepository(db)
	ctx := context.Background()
	projectID := testProjectID

	for i := 0; i < 3; i++ {
		entity := &models.CodeEntity{
			ProjectID:  projectID,
			EntityType: "function",
			Name:       "test",
			FullName:   "pkg.test",
			FilePath:   "test.go",
			Language:   "go",
			IndexedAt:  time.Now(),
		}
		err := repo.Create(ctx, entity)
		require.NoError(t, err)
	}

	count, err := repo.Count(ctx, projectID)
	require.NoError(t, err)
	assert.Equal(t, int64(3), count)
}

func TestCodeEntityRepository_BatchCreate(t *testing.T) {
	db := setupCodeEntityRepoTest(t)
	t.Cleanup(func() { require.NoError(t, db.Migrator().DropTable(&models.CodeEntity{})) })

	repo := NewCodeEntityRepository(db)
	ctx := context.Background()
	projectID := testProjectID

	entities := []*models.CodeEntity{
		{
			ProjectID:  projectID,
			EntityType: "function",
			Name:       "func1",
			FullName:   "pkg.func1",
			FilePath:   "test.go",
			Language:   "go",
			IndexedAt:  time.Now(),
		},
		{
			ProjectID:  projectID,
			EntityType: "function",
			Name:       "func2",
			FullName:   "pkg.func2",
			FilePath:   "test.go",
			Language:   "go",
			IndexedAt:  time.Now(),
		},
	}

	err := repo.BatchCreate(ctx, entities)
	require.NoError(t, err)

	count, err := repo.Count(ctx, projectID)
	require.NoError(t, err)
	assert.Equal(t, int64(2), count)
}

func TestCodeEntityRelationshipRepository_Create(t *testing.T) {
	db := setupCodeEntityRepoTest(t)
	t.Cleanup(func() { require.NoError(t, db.Migrator().DropTable(&models.CodeEntityRelationship{})) })

	repo := NewCodeEntityRelationshipRepository(db)
	ctx := context.Background()

	rel := &models.CodeEntityRelationship{
		ProjectID:    testProjectID,
		SourceID:     "entity-1",
		TargetID:     "entity-2",
		RelationType: "calls",
	}

	err := repo.Create(ctx, rel)
	require.NoError(t, err)
	assert.NotEmpty(t, rel.ID)
}

func TestCodeEntityRelationshipRepository_GetBySourceID(t *testing.T) {
	db := setupCodeEntityRepoTest(t)
	t.Cleanup(func() { require.NoError(t, db.Migrator().DropTable(&models.CodeEntityRelationship{})) })

	repo := NewCodeEntityRelationshipRepository(db)
	ctx := context.Background()

	rels := []*models.CodeEntityRelationship{
		{
			ProjectID:    testProjectID,
			SourceID:     "entity-1",
			TargetID:     "entity-2",
			RelationType: "calls",
		},
		{
			ProjectID:    testProjectID,
			SourceID:     "entity-1",
			TargetID:     "entity-3",
			RelationType: "uses",
		},
	}

	for _, r := range rels {
		err := repo.Create(ctx, r)
		require.NoError(t, err)
	}

	results, err := repo.GetBySourceID(ctx, "entity-1")
	require.NoError(t, err)
	assert.Len(t, results, 2)
}

func TestCodeEntityRelationshipRepository_GetRelationships(t *testing.T) {
	db := setupCodeEntityRepoTest(t)
	t.Cleanup(func() { require.NoError(t, db.Migrator().DropTable(&models.CodeEntityRelationship{})) })

	repo := NewCodeEntityRelationshipRepository(db)
	ctx := context.Background()
	entityID := "entity-1"

	rels := []*models.CodeEntityRelationship{
		{
			ProjectID:    testProjectID,
			SourceID:     entityID,
			TargetID:     "entity-2",
			RelationType: "calls",
		},
		{
			ProjectID:    testProjectID,
			SourceID:     "entity-2",
			TargetID:     entityID,
			RelationType: "uses",
		},
	}

	for _, r := range rels {
		err := repo.Create(ctx, r)
		require.NoError(t, err)
	}

	results, err := repo.GetRelationships(ctx, entityID)
	require.NoError(t, err)
	assert.Len(t, results, 2)
}

func TestCodeEntityRelationshipRepository_Delete(t *testing.T) {
	db := setupCodeEntityRepoTest(t)
	t.Cleanup(func() { require.NoError(t, db.Migrator().DropTable(&models.CodeEntityRelationship{})) })

	repo := NewCodeEntityRelationshipRepository(db)
	ctx := context.Background()

	rel := &models.CodeEntityRelationship{
		ProjectID:    testProjectID,
		SourceID:     "entity-1",
		TargetID:     "entity-2",
		RelationType: "calls",
	}

	err := repo.Create(ctx, rel)
	require.NoError(t, err)

	err = repo.Delete(ctx, rel.ID)
	require.NoError(t, err)

	_, err = repo.GetByID(ctx, rel.ID)
	require.Error(t, err)
}
