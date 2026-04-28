package codeindex

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Test constants
const (
	testSourceAuthFilePath = "src/auth.ts"
)

// Mock Repository Implementation for testing
type MockRepository struct {
	entities      map[uuid.UUID]*CodeEntity
	callChains    map[uuid.UUID]*CallChain
	crossLangRefs map[uuid.UUID][]CrossLangRef
}

func NewMockRepository() *MockRepository {
	return &MockRepository{
		entities:      make(map[uuid.UUID]*CodeEntity),
		callChains:    make(map[uuid.UUID]*CallChain),
		crossLangRefs: make(map[uuid.UUID][]CrossLangRef),
	}
}

func (m *MockRepository) SaveCodeEntity(ctx context.Context, entity *CodeEntity) error {
	_ = ctx
	m.entities[entity.ID] = entity
	return nil
}

func (m *MockRepository) GetCodeEntity(ctx context.Context, id uuid.UUID) (*CodeEntity, error) {
	_ = ctx
	if entity, ok := m.entities[id]; ok {
		return entity, nil
	}
	return nil, nil
}

func (m *MockRepository) ListCodeEntities(ctx context.Context, projectID uuid.UUID, _ *ListOptions) ([]CodeEntity, error) {
	_ = ctx
	var result []CodeEntity
	for _, entity := range m.entities {
		if entity.ProjectID == projectID {
			result = append(result, *entity)
		}
	}
	return result, nil
}

func (m *MockRepository) FindByFilePath(ctx context.Context, projectID uuid.UUID, filePath string) ([]CodeEntity, error) {
	_ = ctx
	var result []CodeEntity
	for _, entity := range m.entities {
		if entity.ProjectID == projectID && entity.FilePath == filePath {
			result = append(result, *entity)
		}
	}
	return result, nil
}

func (m *MockRepository) FindBySymbolName(ctx context.Context, projectID uuid.UUID, name string) ([]CodeEntity, error) {
	_ = ctx
	var result []CodeEntity
	for _, entity := range m.entities {
		if entity.ProjectID == projectID && entity.SymbolName == name {
			result = append(result, *entity)
		}
	}
	return result, nil
}

func (m *MockRepository) FindBySymbolType(ctx context.Context, projectID uuid.UUID, symType SymbolType) ([]CodeEntity, error) {
	_ = ctx
	var result []CodeEntity
	for _, entity := range m.entities {
		if entity.ProjectID == projectID && entity.SymbolType == symType {
			result = append(result, *entity)
		}
	}
	return result, nil
}

func (m *MockRepository) FindByAPIPath(ctx context.Context, projectID uuid.UUID, path string) ([]CodeEntity, error) {
	_ = ctx
	var result []CodeEntity
	for _, entity := range m.entities {
		if entity.ProjectID == projectID && entity.Metadata != nil {
			if apiPath, ok := entity.Metadata["api_path"]; ok && apiPath == path {
				result = append(result, *entity)
			}
		}
	}
	return result, nil
}

func (m *MockRepository) FindByContentHash(ctx context.Context, projectID uuid.UUID, hash string) (*CodeEntity, error) {
	_ = ctx
	for _, entity := range m.entities {
		if entity.ProjectID == projectID && entity.ContentHash == hash {
			return entity, nil
		}
	}
	return nil, nil
}

func (m *MockRepository) SearchByEmbedding(ctx context.Context, _ uuid.UUID, _ []float32, _ int) ([]CodeEntity, error) {
	_ = ctx
	return []CodeEntity{}, nil
}

func (m *MockRepository) DeleteCodeEntity(ctx context.Context, id uuid.UUID) error {
	_ = ctx
	delete(m.entities, id)
	return nil
}

func (m *MockRepository) DeleteByFilePath(ctx context.Context, projectID uuid.UUID, filePath string) error {
	_ = ctx
	for id, entity := range m.entities {
		if entity.ProjectID == projectID && entity.FilePath == filePath {
			delete(m.entities, id)
		}
	}
	return nil
}

func (m *MockRepository) UpdateCanonicalLink(ctx context.Context, entityID uuid.UUID, canonicalID *uuid.UUID) error {
	_ = ctx
	if entity, ok := m.entities[entityID]; ok {
		entity.CanonicalID = canonicalID
		return nil
	}
	return nil
}

func (m *MockRepository) SaveCallChain(ctx context.Context, chain *CallChain) error {
	_ = ctx
	m.callChains[chain.ID] = chain
	return nil
}

func (m *MockRepository) GetCallChain(ctx context.Context, id uuid.UUID) (*CallChain, error) {
	_ = ctx
	if chain, ok := m.callChains[id]; ok {
		return chain, nil
	}
	return nil, nil
}

func (m *MockRepository) ListCallChains(ctx context.Context, projectID uuid.UUID) ([]CallChain, error) {
	_ = ctx
	var result []CallChain
	for _, chain := range m.callChains {
		if chain.ProjectID == projectID {
			result = append(result, *chain)
		}
	}
	return result, nil
}

func (m *MockRepository) SaveCrossLangRef(ctx context.Context, ref *CrossLangRef) error {
	_ = ctx
	m.crossLangRefs[uuid.New()] = append(m.crossLangRefs[uuid.New()], *ref)
	return nil
}

func (m *MockRepository) GetCrossLangRefs(ctx context.Context, entityID uuid.UUID) ([]CrossLangRef, error) {
	_ = ctx
	if refs, ok := m.crossLangRefs[entityID]; ok {
		return refs, nil
	}
	return []CrossLangRef{}, nil
}

// Test cases
func TestMockRepository_SaveCodeEntity(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	entity := &CodeEntity{
		ID:         uuid.New(),
		ProjectID:  uuid.New(),
		FilePath:   testSourceAuthFilePath,
		SymbolName: "loginUser",
		SymbolType: SymbolTypeFunction,
		Language:   LanguageTypeScript,
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}

	err := repo.SaveCodeEntity(ctx, entity)
	require.NoError(t, err)

	retrieved, err := repo.GetCodeEntity(ctx, entity.ID)
	require.NoError(t, err)
	assert.NotNil(t, retrieved)
	assert.Equal(t, entity.ID, retrieved.ID)
	assert.Equal(t, entity.SymbolName, retrieved.SymbolName)
}

func TestMockRepository_GetCodeEntity_NotFound(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	retrieved, err := repo.GetCodeEntity(ctx, uuid.New())
	require.NoError(t, err)
	assert.Nil(t, retrieved)
}

func TestMockRepository_ListCodeEntities(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	projectID := uuid.New()

	entities := []*CodeEntity{
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			FilePath:   testSourceAuthFilePath,
			SymbolName: "loginUser",
			SymbolType: SymbolTypeFunction,
			Language:   LanguageTypeScript,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		},
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			FilePath:   "src/user.ts",
			SymbolName: "User",
			SymbolType: SymbolTypeClass,
			Language:   LanguageTypeScript,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		},
	}

	for _, entity := range entities {
		require.NoError(t, repo.SaveCodeEntity(ctx, entity))
	}

	result, err := repo.ListCodeEntities(ctx, projectID, nil)
	require.NoError(t, err)
	assert.Len(t, result, 2)
}

func TestMockRepository_FindByFilePath(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	projectID := uuid.New()
	filePath := testSourceAuthFilePath

	entity := &CodeEntity{
		ID:         uuid.New(),
		ProjectID:  projectID,
		FilePath:   filePath,
		SymbolName: "loginUser",
		SymbolType: SymbolTypeFunction,
		Language:   LanguageTypeScript,
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}

	require.NoError(t, repo.SaveCodeEntity(ctx, entity))

	result, err := repo.FindByFilePath(ctx, projectID, filePath)
	require.NoError(t, err)
	assert.Len(t, result, 1)
	assert.Equal(t, entity.ID, result[0].ID)
}

func TestMockRepository_FindByFilePath_Multiple(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	projectID := uuid.New()
	filePath := testSourceAuthFilePath

	entities := []*CodeEntity{
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			FilePath:   filePath,
			SymbolName: "loginUser",
			SymbolType: SymbolTypeFunction,
			Language:   LanguageTypeScript,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		},
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			FilePath:   filePath,
			SymbolName: "AuthService",
			SymbolType: SymbolTypeClass,
			Language:   LanguageTypeScript,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		},
	}

	for _, entity := range entities {
		require.NoError(t, repo.SaveCodeEntity(ctx, entity))
	}

	result, err := repo.FindByFilePath(ctx, projectID, filePath)
	require.NoError(t, err)
	assert.Len(t, result, 2)
}

func TestMockRepository_FindBySymbolName(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	projectID := uuid.New()

	entity := &CodeEntity{
		ID:         uuid.New(),
		ProjectID:  projectID,
		FilePath:   testSourceAuthFilePath,
		SymbolName: "loginUser",
		SymbolType: SymbolTypeFunction,
		Language:   LanguageTypeScript,
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}

	require.NoError(t, repo.SaveCodeEntity(ctx, entity))

	result, err := repo.FindBySymbolName(ctx, projectID, "loginUser")
	require.NoError(t, err)
	assert.Len(t, result, 1)
	assert.Equal(t, "loginUser", result[0].SymbolName)
}

func TestMockRepository_FindBySymbolType(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	projectID := uuid.New()

	entities := []*CodeEntity{
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			FilePath:   testSourceAuthFilePath,
			SymbolName: "loginUser",
			SymbolType: SymbolTypeFunction,
			Language:   LanguageTypeScript,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		},
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			FilePath:   testSourceAuthFilePath,
			SymbolName: "logoutUser",
			SymbolType: SymbolTypeFunction,
			Language:   LanguageTypeScript,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		},
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			FilePath:   "src/user.ts",
			SymbolName: "User",
			SymbolType: SymbolTypeClass,
			Language:   LanguageTypeScript,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		},
	}

	for _, entity := range entities {
		require.NoError(t, repo.SaveCodeEntity(ctx, entity))
	}

	// Find all functions
	result, err := repo.FindBySymbolType(ctx, projectID, SymbolTypeFunction)
	require.NoError(t, err)
	assert.Len(t, result, 2)

	// Find all classes
	result, err = repo.FindBySymbolType(ctx, projectID, SymbolTypeClass)
	require.NoError(t, err)
	assert.Len(t, result, 1)
}

func TestMockRepository_FindByAPIPath(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	projectID := uuid.New()

	entity := &CodeEntity{
		ID:         uuid.New(),
		ProjectID:  projectID,
		FilePath:   "src/handlers/user.ts",
		SymbolName: "getUserHandler",
		SymbolType: SymbolTypeHandler,
		Language:   LanguageTypeScript,
		Metadata: map[string]any{
			"api_path": "/api/users/:id",
		},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	require.NoError(t, repo.SaveCodeEntity(ctx, entity))

	result, err := repo.FindByAPIPath(ctx, projectID, "/api/users/:id")
	require.NoError(t, err)
	assert.Len(t, result, 1)
}

func TestMockRepository_FindByContentHash(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	projectID := uuid.New()
	hash := "abc123def456"

	entity := &CodeEntity{
		ID:          uuid.New(),
		ProjectID:   projectID,
		FilePath:    testSourceAuthFilePath,
		SymbolName:  "loginUser",
		SymbolType:  SymbolTypeFunction,
		Language:    LanguageTypeScript,
		ContentHash: hash,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	require.NoError(t, repo.SaveCodeEntity(ctx, entity))

	result, err := repo.FindByContentHash(ctx, projectID, hash)
	require.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, entity.ID, result.ID)
}

func TestMockRepository_DeleteCodeEntity(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	entity := &CodeEntity{
		ID:         uuid.New(),
		ProjectID:  uuid.New(),
		FilePath:   testSourceAuthFilePath,
		SymbolName: "loginUser",
		SymbolType: SymbolTypeFunction,
		Language:   LanguageTypeScript,
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}

	require.NoError(t, repo.SaveCodeEntity(ctx, entity))

	// Verify it exists
	retrieved, err := repo.GetCodeEntity(ctx, entity.ID)
	require.NoError(t, err)
	assert.NotNil(t, retrieved)

	// Delete it
	err = repo.DeleteCodeEntity(ctx, entity.ID)
	require.NoError(t, err)

	// Verify it's gone
	retrieved, err = repo.GetCodeEntity(ctx, entity.ID)
	require.NoError(t, err)
	assert.Nil(t, retrieved)
}

func TestMockRepository_DeleteByFilePath(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	projectID := uuid.New()
	filePath := testSourceAuthFilePath

	entities := []*CodeEntity{
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			FilePath:   filePath,
			SymbolName: "loginUser",
			SymbolType: SymbolTypeFunction,
			Language:   LanguageTypeScript,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		},
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			FilePath:   filePath,
			SymbolName: "logoutUser",
			SymbolType: SymbolTypeFunction,
			Language:   LanguageTypeScript,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		},
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			FilePath:   "src/other.ts",
			SymbolName: "otherFunc",
			SymbolType: SymbolTypeFunction,
			Language:   LanguageTypeScript,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		},
	}

	for _, entity := range entities {
		require.NoError(t, repo.SaveCodeEntity(ctx, entity))
	}

	// Delete by file path
	err := repo.DeleteByFilePath(ctx, projectID, filePath)
	require.NoError(t, err)

	// Verify entities in file are deleted
	result, err := repo.FindByFilePath(ctx, projectID, filePath)
	require.NoError(t, err)
	assert.Empty(t, result)

	// Verify other file is untouched
	result, err = repo.FindByFilePath(ctx, projectID, "src/other.ts")
	require.NoError(t, err)
	assert.Len(t, result, 1)
}

func TestMockRepository_UpdateCanonicalLink(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	entity := &CodeEntity{
		ID:         uuid.New(),
		ProjectID:  uuid.New(),
		FilePath:   testSourceAuthFilePath,
		SymbolName: "loginUser",
		SymbolType: SymbolTypeFunction,
		Language:   LanguageTypeScript,
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}

	require.NoError(t, repo.SaveCodeEntity(ctx, entity))

	// Update canonical link
	canonicalID := uuid.New()
	err := repo.UpdateCanonicalLink(ctx, entity.ID, &canonicalID)
	require.NoError(t, err)

	retrieved, err := repo.GetCodeEntity(ctx, entity.ID)
	require.NoError(t, err)
	assert.NotNil(t, retrieved.CanonicalID)
	assert.Equal(t, canonicalID, *retrieved.CanonicalID)
}

func TestMockRepository_SaveCallChain(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	chain := &CallChain{
		ID:         uuid.New(),
		ProjectID:  uuid.New(),
		Name:       "Login Flow",
		Type:       "user_flow",
		EntryPoint: uuid.New(),
		Steps: []ChainStep{
			{
				EntityID:   uuid.New(),
				SymbolName: "handleLogin",
				FilePath:   "src/handlers.ts",
				Language:   LanguageTypeScript,
				Order:      1,
			},
		},
		Depth:     1,
		CreatedAt: time.Now(),
	}

	err := repo.SaveCallChain(ctx, chain)
	require.NoError(t, err)

	retrieved, err := repo.GetCallChain(ctx, chain.ID)
	require.NoError(t, err)
	assert.NotNil(t, retrieved)
	assert.Equal(t, chain.ID, retrieved.ID)
	assert.Equal(t, "Login Flow", retrieved.Name)
}

func TestMockRepository_ListCallChains(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	projectID := uuid.New()

	chains := []*CallChain{
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			Name:       "Login Flow",
			Type:       "user_flow",
			EntryPoint: uuid.New(),
			CreatedAt:  time.Now(),
		},
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			Name:       "Data Processing",
			Type:       "data_path",
			EntryPoint: uuid.New(),
			CreatedAt:  time.Now(),
		},
	}

	for _, chain := range chains {
		require.NoError(t, repo.SaveCallChain(ctx, chain))
	}

	result, err := repo.ListCallChains(ctx, projectID)
	require.NoError(t, err)
	assert.Len(t, result, 2)
}

func TestRepository_ListOptions(t *testing.T) {
	opts := &ListOptions{
		Language:   LanguageTypeScript,
		SymbolType: SymbolTypeFunction,
		FilePath:   testSourceAuthFilePath,
		ModulePath: "internal/auth",
		Limit:      100,
		Offset:     0,
	}

	assert.Equal(t, LanguageTypeScript, opts.Language)
	assert.Equal(t, SymbolTypeFunction, opts.SymbolType)
	assert.Equal(t, 100, opts.Limit)
}

func TestRepository_IndexStats(t *testing.T) {
	stats := &IndexStats{
		TotalEntities: 100,
		ByLanguage: map[Language]int{
			LanguageTypeScript: 60,
			LanguageGo:         40,
		},
		BySymbolType: map[SymbolType]int{
			SymbolTypeFunction:  50,
			SymbolTypeClass:     30,
			SymbolTypeInterface: 20,
		},
		WithCanonical:   80,
		WithEmbedding:   60,
		TotalCallChains: 10,
		CrossLangRefs:   5,
	}

	assert.Equal(t, 100, stats.TotalEntities)
	assert.Equal(t, 60, stats.ByLanguage[LanguageTypeScript])
	assert.Equal(t, 50, stats.BySymbolType[SymbolTypeFunction])
	assert.Equal(t, 80, stats.WithCanonical)
	assert.Equal(t, 10, stats.TotalCallChains)
}
