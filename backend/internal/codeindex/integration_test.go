package codeindex

import (
	"context"
	"strings"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const integrationLinkConfidence = 0.95

// Integration tests combining multiple components

func TestIntegration_AnalyzeAndLink(t *testing.T) {
	analyzer := NewAnalyzer()
	linker := NewCodeEntityLinker(nil)

	// Analyze a file
	tsCode := `export function loginUser(email: string) {
  return authenticate(email);
}

export function authenticate(email: string) {
  return fetch('/api/auth', { email });
}`

	analysis, err := analyzer.AnalyzeFile("auth.ts", tsCode)
	require.NoError(t, err)

	// Create parsed entities from analysis
	entities := make([]*ParsedEntity, 0, len(analysis.Symbols))

	for _, sym := range analysis.Symbols {
		entity := &ParsedEntity{
			ID:        uuid.New(),
			Name:      sym.Name,
			Type:      sym.Type,
			FilePath:  "auth.ts",
			StartLine: sym.StartLine,
			Language:  LanguageTypeScript,
		}
		entities = append(entities, entity)
		linker.AddEntity(entity)
	}

	// Link entities to canonical concepts
	canonicalID := uuid.New()
	ctx := context.Background()

	if len(entities) > 0 {
		err = linker.LinkToCanonical(ctx, entities[0].ID, canonicalID, integrationLinkConfidence)
		require.NoError(t, err)
	}

	// Verify linkage
	stats := linker.GetLinkingStatistics()
	assert.Positive(t, stats.LinkedEntities)
	assert.Equal(t, int(1), stats.TotalMappings)
}

func TestIntegration_RepositoryAndAnalyzer(t *testing.T) {
	repo := NewMockRepository()
	analyzer := NewAnalyzer()

	projectID := uuid.New()
	ctx := context.Background()

	// Analyze multiple files
	files := []struct {
		path string
		code string
		lang Language
	}{
		{
			path: "src/user.ts",
			code: `export function getUser(id: string) {
  return fetch('/users/' + id);
}`,
			lang: LanguageTypeScript,
		},
		{
			path: "src/auth.ts",
			code: `export function authenticate(email: string) {
  return validate(email);
}`,
			lang: LanguageTypeScript,
		},
	}

	// Analyze and save
	for _, file := range files {
		analysis, err := analyzer.AnalyzeFile(file.path, file.code)
		require.NoError(t, err)

		// Convert to entities and save
		for _, sym := range analysis.Symbols {
			entity := &CodeEntity{
				ID:         uuid.New(),
				ProjectID:  projectID,
				FilePath:   file.path,
				SymbolName: sym.Name,
				SymbolType: sym.Type,
				Language:   file.lang,
				CreatedAt:  time.Now(),
				UpdatedAt:  time.Now(),
			}

			err := repo.SaveCodeEntity(ctx, entity)
			require.NoError(t, err)
		}
	}

	// Verify saved entities
	results, err := repo.ListCodeEntities(ctx, projectID, nil)
	require.NoError(t, err)
	assert.NotEmpty(t, results)
}

func TestIntegration_CallChainResolution(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	// Create a chain of entities
	handler := &ParsedEntity{
		ID:   uuid.New(),
		Name: "handleLogin",
		Type: SymbolTypeFunction,
	}

	validator := &ParsedEntity{
		ID:   uuid.New(),
		Name: "validateCredentials",
		Type: SymbolTypeFunction,
	}

	authenticator := &ParsedEntity{
		ID:   uuid.New(),
		Name: "authenticate",
		Type: SymbolTypeFunction,
	}

	// Set up call relationships
	validatorID := validator.ID
	authenticatorID := authenticator.ID

	handler.Calls = []ParsedCall{
		{TargetName: "validateCredentials", TargetID: &validatorID},
	}

	validator.Calls = []ParsedCall{
		{TargetName: "authenticate", TargetID: &authenticatorID},
	}

	// Add all to linker
	linker.AddEntity(handler)
	linker.AddEntity(validator)
	linker.AddEntity(authenticator)

	// Build semantic graph
	graph := linker.BuildSemanticGraph()

	assert.NotNil(t, graph)
	assert.Len(t, graph.Nodes, 3)
}

func TestIntegration_MultiLanguageAnalysis(t *testing.T) {
	analyzer := NewAnalyzer()

	samples := []struct {
		name string
		code string
		lang Language
	}{
		{
			name: "TypeScript function",
			code: `export function tsFunc() { return 42; }`,
			lang: LanguageTypeScript,
		},
		{
			name: "Go function",
			code: `func GoFunc() int { return 42; }`,
			lang: LanguageGo,
		},
		{
			name: "Python function",
			code: `def py_func(): return 42`,
			lang: LanguagePython,
		},
	}

	for _, sample := range samples {
		// Use proper file extensions for language detection
		fileName := sample.name
		switch sample.lang {
		case LanguageTypeScript:
			fileName = "test.ts"
		case LanguageJavaScript:
			fileName = "test.js"
		case LanguageGo:
			fileName = "test.go"
		case LanguagePython:
			fileName = "test.py"
		case LanguageRust:
			fileName = "test.rs"
		case LanguageJava:
			fileName = "Test.java"
		}

		analysis, err := analyzer.AnalyzeFile(fileName, sample.code)
		require.NoError(t, err, "Failed to analyze %s", sample.name)
		if analysis != nil {
			assert.Equal(t, sample.lang, analysis.Language)
		}
	}
}

func TestIntegration_RepositoryCRUD(t *testing.T) {
	repo := NewMockRepository()
	ctx := context.Background()

	projectID := uuid.New()
	entityID := uuid.New()

	// Create
	entity := &CodeEntity{
		ID:         entityID,
		ProjectID:  projectID,
		FilePath:   "test.ts",
		SymbolName: "test",
		SymbolType: SymbolTypeFunction,
		Language:   LanguageTypeScript,
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}

	err := repo.SaveCodeEntity(ctx, entity)
	require.NoError(t, err)

	// Read
	retrieved, err := repo.GetCodeEntity(ctx, entityID)
	require.NoError(t, err)
	assert.NotNil(t, retrieved)

	// Update
	canonicalID := uuid.New()
	err = repo.UpdateCanonicalLink(ctx, entityID, &canonicalID)
	require.NoError(t, err)

	// Verify update
	updated, err := repo.GetCodeEntity(ctx, entityID)
	require.NoError(t, err)
	assert.NotNil(t, updated.CanonicalID)
	assert.Equal(t, canonicalID, *updated.CanonicalID)

	// Delete
	err = repo.DeleteCodeEntity(ctx, entityID)
	require.NoError(t, err)

	// Verify deletion
	deleted, err := repo.GetCodeEntity(ctx, entityID)
	require.NoError(t, err)
	assert.Nil(t, deleted)
}

func TestIntegration_ComplexAnalysis(t *testing.T) {
	analyzer := NewAnalyzer()
	linker := NewCodeEntityLinker(nil)
	repo := NewMockRepository()

	projectID := uuid.New()
	ctx := context.Background()

	// Complex TypeScript code with multiple entities
	code := `// @canonical(AuthFlow)
export interface User {
  id: string;
  email: string;
}

// @trace-implements(login)
export async function loginUser(email: string): Promise<User> {
  const validEmail = validateEmail(email);
  if (!validEmail) {
    throw new Error('Invalid email');
  }

  const user = await fetchUser(email);
  return user;
}

export function validateEmail(email: string): boolean {
  return email.includes('@');
}

async function fetchUser(email: string): Promise<User> {
  const response = await fetch('/api/users', { email });
  return response.json();
}`

	// Analyze
	analysis, err := analyzer.AnalyzeFile("auth.ts", code)
	require.NoError(t, err)
	assert.NotEmpty(t, analysis.Symbols)
	assert.NotEmpty(t, analysis.Annotations)
	assert.NotEmpty(t, analysis.Calls)

	saveEntitiesFromAnalysis(ctx, t, repo, linker, analysis, projectID)
	assertComplexAnalysisResults(ctx, t, repo, linker, projectID)
}

func saveEntitiesFromAnalysis(
	ctx context.Context,
	t *testing.T,
	repo Repository,
	linker *CodeEntityLinker,
	analysis *FileAnalysis,
	projectID uuid.UUID,
) {
	t.Helper()
	for _, sym := range analysis.Symbols {
		entity := &CodeEntity{
			ID:         uuid.New(),
			ProjectID:  projectID,
			FilePath:   "auth.ts",
			SymbolName: sym.Name,
			SymbolType: sym.Type,
			Language:   LanguageTypeScript,
			IsExported: sym.IsExported,
			IsAsync:    sym.IsAsync,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		}

		err := repo.SaveCodeEntity(ctx, entity)
		require.NoError(t, err)

		parsedEntity := &ParsedEntity{
			ID:   entity.ID,
			Name: sym.Name,
			Type: sym.Type,
		}
		linker.AddEntity(parsedEntity)
	}
}

func assertComplexAnalysisResults(
	ctx context.Context,
	t *testing.T,
	repo Repository,
	linker *CodeEntityLinker,
	projectID uuid.UUID,
) {
	t.Helper()
	results, err := repo.ListCodeEntities(ctx, projectID, nil)
	require.NoError(t, err)
	assert.NotEmpty(t, results)

	stats := linker.GetLinkingStatistics()
	assert.Positive(t, stats.TotalEntities)
}

func TestIntegration_EdgeCases_EmptyProject(t *testing.T) {
	repo := NewMockRepository()
	projectID := uuid.New()
	ctx := context.Background()

	// Empty project
	results, err := repo.ListCodeEntities(ctx, projectID, nil)
	require.NoError(t, err)
	assert.Empty(t, results)

	chains, err := repo.ListCallChains(ctx, projectID)
	require.NoError(t, err)
	assert.Empty(t, chains)
}

func TestIntegration_EdgeCases_LargeFile(t *testing.T) {
	analyzer := NewAnalyzer()

	// Generate a large file with many functions
	var largeBuilder strings.Builder
	for i := 0; i < 100; i++ {
		largeBuilder.WriteString(`export function func`)
		largeBuilder.WriteString(string(rune('a' + i%26)))
		largeBuilder.WriteString(`_`)
		largeBuilder.WriteString(string(rune(i / 26)))
		largeBuilder.WriteString(`() { return 42; }`)
		if i < 99 {
			largeBuilder.WriteString("\n")
		}
	}
	largeCode := largeBuilder.String()

	analysis, err := analyzer.AnalyzeFile("large.ts", largeCode)
	require.NoError(t, err)
	assert.NotEmpty(t, analysis.Symbols)
}

func TestIntegration_FilteringAndSearch(t *testing.T) {
	repo := NewMockRepository()
	projectID := uuid.New()
	ctx := context.Background()

	// Create entities with different types
	entities := []*CodeEntity{
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			SymbolName: "getUserFunction",
			SymbolType: SymbolTypeFunction,
			Language:   LanguageTypeScript,
			FilePath:   "user.ts",
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		},
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			SymbolName: "UserClass",
			SymbolType: SymbolTypeClass,
			Language:   LanguageTypeScript,
			FilePath:   "user.ts",
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		},
		{
			ID:         uuid.New(),
			ProjectID:  projectID,
			SymbolName: "getUserInterface",
			SymbolType: SymbolTypeInterface,
			Language:   LanguageTypeScript,
			FilePath:   "user.ts",
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		},
	}

	for _, entity := range entities {
		require.NoError(t, repo.SaveCodeEntity(ctx, entity))
	}

	// Search by symbol type
	functions, err := repo.FindBySymbolType(ctx, projectID, SymbolTypeFunction)
	require.NoError(t, err)
	assert.Len(t, functions, 1)

	classes, err := repo.FindBySymbolType(ctx, projectID, SymbolTypeClass)
	require.NoError(t, err)
	assert.Len(t, classes, 1)

	// Search by file
	byFile, err := repo.FindByFilePath(ctx, projectID, "user.ts")
	require.NoError(t, err)
	assert.Len(t, byFile, 3)
}

func TestIntegration_ContentHashing(t *testing.T) {
	analyzer := NewAnalyzer()
	repo := NewMockRepository()
	projectID := uuid.New()
	ctx := context.Background()

	code1 := `export function test() { return 42; }`
	code2 := `export function test() { return 43; }`

	// Analyze both
	analysis1, err := analyzer.AnalyzeFile("test.ts", code1)
	require.NoError(t, err)

	analysis2, err := analyzer.AnalyzeFile("test.ts", code2)
	require.NoError(t, err)

	// Hashes should be different
	assert.NotEqual(t, analysis1.ContentHash, analysis2.ContentHash)

	// Save with hashes
	entity1 := &CodeEntity{
		ID:          uuid.New(),
		ProjectID:   projectID,
		FilePath:    "test.ts",
		SymbolName:  "test",
		SymbolType:  SymbolTypeFunction,
		Language:    LanguageTypeScript,
		ContentHash: analysis1.ContentHash,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	require.NoError(t, repo.SaveCodeEntity(ctx, entity1))

	// Find by hash
	found, err := repo.FindByContentHash(ctx, projectID, analysis1.ContentHash)
	require.NoError(t, err)
	assert.NotNil(t, found)
}
