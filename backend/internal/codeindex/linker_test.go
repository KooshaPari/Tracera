package codeindex

import (
	"context"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	linkerConfidenceHigh   = 0.95
	linkerConfidenceMedium = 0.9
	linkerConfidenceLow    = 0.8
	linkerConfidenceAlt    = 0.85
	linkerConfidenceMin    = 0.0
)

func TestNewCodeEntityLinker(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	assert.NotNil(t, linker)
	assert.NotNil(t, linker.entities)
	assert.NotNil(t, linker.canonicalMappings)
	assert.Empty(t, linker.entities)
}

func TestCodeEntityLinker_AddEntity(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	entity := &ParsedEntity{
		ID:   uuid.New(),
		Name: "testFunc",
		Type: SymbolTypeFunction,
	}

	linker.AddEntity(entity)

	assert.Len(t, linker.entities, 1)
	assert.Equal(t, entity, linker.entities[entity.ID])
}

func TestCodeEntityLinker_AddMultipleEntities(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	entities := []*ParsedEntity{
		{ID: uuid.New(), Name: "func1", Type: SymbolTypeFunction},
		{ID: uuid.New(), Name: "func2", Type: SymbolTypeFunction},
		{ID: uuid.New(), Name: "Class1", Type: SymbolTypeClass},
	}

	for _, entity := range entities {
		linker.AddEntity(entity)
	}

	assert.Len(t, linker.entities, 3)
}

func TestCodeEntityLinker_LinkToCanonical(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	entityID := uuid.New()
	canonicalID := uuid.New()

	entity := &ParsedEntity{
		ID:   entityID,
		Name: "loginFunc",
		Type: SymbolTypeFunction,
	}
	linker.AddEntity(entity)

	ctx := context.Background()
	err := linker.LinkToCanonical(ctx, entityID, canonicalID, linkerConfidenceHigh)
	require.NoError(t, err)

	mappings := linker.GetCanonicalForEntity(entityID)
	require.Len(t, mappings, 1)
	assert.Equal(t, canonicalID, mappings[0].CanonicalID)
	assert.InEpsilon(t, linkerConfidenceHigh, mappings[0].Confidence, 1e-9)
	assert.Equal(t, "manual", mappings[0].Source)
}

func TestCodeEntityLinker_LinkToCanonical_NonExistentEntity(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	ctx := context.Background()
	err := linker.LinkToCanonical(ctx, uuid.New(), uuid.New(), linkerConfidenceMedium)
	assert.Error(t, err)
}

func TestCodeEntityLinker_InferCanonicalLinks_NameContains(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	// Add entities
	loginFunc := &ParsedEntity{
		ID:   uuid.New(),
		Name: "loginUser",
		Type: SymbolTypeFunction,
	}
	logoutFunc := &ParsedEntity{
		ID:   uuid.New(),
		Name: "logoutUser",
		Type: SymbolTypeFunction,
	}

	linker.AddEntity(loginFunc)
	linker.AddEntity(logoutFunc)

	// Create pattern
	canonicalID := uuid.New()
	pattern := &EntityPattern{
		Name:     "authentication",
		Priority: 1,
		MatchRules: []MatchRule{
			{
				Type:       "name_contains",
				Pattern:    "login",
				Confidence: linkerConfidenceMedium,
			},
		},
		CanonicalsMap: map[string]uuid.UUID{
			"login": canonicalID,
		},
	}

	ctx := context.Background()
	err := linker.InferCanonicalLinks(ctx, []*EntityPattern{pattern})
	require.NoError(t, err)

	// Check that loginUser got mapped
	mappings := linker.GetCanonicalForEntity(loginFunc.ID)
	assert.NotEmpty(t, mappings)
}

func TestCodeEntityLinker_GetCanonicalForEntity(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	entityID := uuid.New()
	canonicalID1 := uuid.New()
	canonicalID2 := uuid.New()

	entity := &ParsedEntity{
		ID:   entityID,
		Name: "multiFunction",
		Type: SymbolTypeFunction,
	}
	linker.AddEntity(entity)

	ctx := context.Background()
	require.NoError(t, linker.LinkToCanonical(ctx, entityID, canonicalID1, linkerConfidenceMedium))
	require.NoError(t, linker.LinkToCanonical(ctx, entityID, canonicalID2, linkerConfidenceLow))

	mappings := linker.GetCanonicalForEntity(entityID)
	assert.Len(t, mappings, 2)

	// Verify both mappings exist
	foundIDs := make(map[uuid.UUID]bool)
	for _, m := range mappings {
		foundIDs[m.CanonicalID] = true
	}

	assert.True(t, foundIDs[canonicalID1])
	assert.True(t, foundIDs[canonicalID2])
}

func TestCodeEntityLinker_GetEntitiesForCanonical(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	canonicalID := uuid.New()

	// Add multiple entities
	entities := []*ParsedEntity{
		{ID: uuid.New(), Name: "loginUser", Type: SymbolTypeFunction},
		{ID: uuid.New(), Name: "validateCredentials", Type: SymbolTypeFunction},
		{ID: uuid.New(), Name: "unrelatedFunc", Type: SymbolTypeFunction},
	}

	for _, entity := range entities {
		linker.AddEntity(entity)
	}

	ctx := context.Background()
	// Link first two to canonical
	require.NoError(t, linker.LinkToCanonical(ctx, entities[0].ID, canonicalID, linkerConfidenceHigh))
	require.NoError(t, linker.LinkToCanonical(ctx, entities[1].ID, canonicalID, linkerConfidenceMedium))
	// Don't link third one

	result := linker.GetEntitiesForCanonical(canonicalID)
	assert.Len(t, result, 2)

	names := make(map[string]bool)
	for _, entity := range result {
		names[entity.Name] = true
	}

	assert.True(t, names["loginUser"])
	assert.True(t, names["validateCredentials"])
	assert.False(t, names["unrelatedFunc"])
}

func TestCodeEntityLinker_LinkCallChainToCanonical(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	canonicalID := uuid.New()

	// Create entities for chain
	entry := &ParsedEntity{
		ID:   uuid.New(),
		Name: "handleLogin",
		Type: SymbolTypeFunction,
	}
	step1 := &ParsedEntity{
		ID:   uuid.New(),
		Name: "validateUser",
		Type: SymbolTypeFunction,
	}
	step2 := &ParsedEntity{
		ID:   uuid.New(),
		Name: "createSession",
		Type: SymbolTypeFunction,
	}

	linker.AddEntity(entry)
	linker.AddEntity(step1)
	linker.AddEntity(step2)

	// Create call chain
	chain := &CallChainResolution{
		EntryPoint: entry,
		Steps: []*ChainStepResolved{
			{Entity: step1, Order: 1},
			{Entity: step2, Order: 2},
		},
		Depth:         2,
		CrossLanguage: false,
	}

	ctx := context.Background()
	err := linker.LinkCallChainToCanonical(ctx, chain, canonicalID)
	require.NoError(t, err)

	// All entities in chain should be mapped
	entryMappings := linker.GetCanonicalForEntity(entry.ID)
	assert.NotEmpty(t, entryMappings)

	step1Mappings := linker.GetCanonicalForEntity(step1.ID)
	assert.NotEmpty(t, step1Mappings)

	step2Mappings := linker.GetCanonicalForEntity(step2.ID)
	assert.NotEmpty(t, step2Mappings)

	// Entry point should have higher confidence
	assert.Greater(t, entryMappings[0].Confidence, step2Mappings[0].Confidence)
}

func TestCodeEntityLinker_FindRelatedEntities_Calls(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	caller := &ParsedEntity{
		ID:   uuid.New(),
		Name: "processUser",
		Type: SymbolTypeFunction,
	}

	callee := &ParsedEntity{
		ID:   uuid.New(),
		Name: "validateUser",
		Type: SymbolTypeFunction,
	}

	calleeID := callee.ID
	caller.Calls = []ParsedCall{
		{
			TargetName: "validateUser",
			TargetID:   &calleeID,
		},
	}

	linker.AddEntity(caller)
	linker.AddEntity(callee)

	ctx := context.Background()
	related := linker.FindRelatedEntities(ctx, caller.ID)

	assert.NotEmpty(t, related)
	found := false
	for _, rel := range related {
		if rel.Entity.ID == callee.ID && rel.Relationship == "calls" {
			found = true
			break
		}
	}
	assert.True(t, found, "Should find called entity")
}

func TestCodeEntityLinker_FindRelatedEntities_CalledBy(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	caller := &ParsedEntity{
		ID:   uuid.New(),
		Name: "processUser",
		Type: SymbolTypeFunction,
	}

	callee := &ParsedEntity{
		ID:   uuid.New(),
		Name: "validateUser",
		Type: SymbolTypeFunction,
	}

	calleeID := callee.ID
	caller.Calls = []ParsedCall{
		{
			TargetName: "validateUser",
			TargetID:   &calleeID,
		},
	}

	linker.AddEntity(caller)
	linker.AddEntity(callee)

	// Find related from callee perspective
	related := linker.FindRelatedEntities(context.Background(), callee.ID)

	assert.NotEmpty(t, related)
	found := false
	for _, rel := range related {
		if rel.Entity.ID == caller.ID && rel.Relationship == "called_by" {
			found = true
			break
		}
	}
	assert.True(t, found, "Should find calling entity")
}

func TestCodeEntityLinker_FindRelatedEntities_SharedCanonical(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	canonicalID := uuid.New()

	func1 := &ParsedEntity{
		ID:   uuid.New(),
		Name: "loginUser",
		Type: SymbolTypeFunction,
	}

	func2 := &ParsedEntity{
		ID:   uuid.New(),
		Name: "authenticateUser",
		Type: SymbolTypeFunction,
	}

	linker.AddEntity(func1)
	linker.AddEntity(func2)

	ctx := context.Background()
	// Link both to same canonical
	require.NoError(t, linker.LinkToCanonical(ctx, func1.ID, canonicalID, linkerConfidenceMedium))
	require.NoError(t, linker.LinkToCanonical(ctx, func2.ID, canonicalID, linkerConfidenceMedium))

	related := linker.FindRelatedEntities(ctx, func1.ID)

	found := false
	for _, rel := range related {
		if rel.Entity.ID == func2.ID && rel.Relationship == "shares_canonical" {
			found = true
			break
		}
	}
	assert.True(t, found, "Should find entity sharing canonical concept")
}

func TestCodeEntityLinker_BuildSemanticGraph(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	canonicalID := uuid.New()

	entity1 := &ParsedEntity{
		ID:   uuid.New(),
		Name: "func1",
		Type: SymbolTypeFunction,
	}

	entity2 := &ParsedEntity{
		ID:   uuid.New(),
		Name: "func2",
		Type: SymbolTypeFunction,
	}

	// Create call relationship
	entity2ID := entity2.ID
	entity1.Calls = []ParsedCall{
		{TargetName: "func2", TargetID: &entity2ID},
	}

	linker.AddEntity(entity1)
	linker.AddEntity(entity2)

	ctx := context.Background()
	require.NoError(t, linker.LinkToCanonical(ctx, entity1.ID, canonicalID, linkerConfidenceMedium))
	require.NoError(t, linker.LinkToCanonical(ctx, entity2.ID, canonicalID, linkerConfidenceMedium))

	graph := linker.BuildSemanticGraph()

	assert.NotNil(t, graph)
	assert.NotEmpty(t, graph.Nodes)
	assert.NotEmpty(t, graph.Concepts)

	// Should have nodes for both entities
	assert.Len(t, graph.Nodes, 2)

	// Should have concept node
	assert.NotEmpty(t, graph.Concepts)
	conceptNode := graph.Concepts[canonicalID]
	assert.NotNil(t, conceptNode)
	assert.NotEmpty(t, conceptNode.Entities)
}

func TestCodeEntityLinker_GetLinkingStatistics(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	canonicalID := uuid.New()

	// Add entities
	linked := &ParsedEntity{
		ID:   uuid.New(),
		Name: "linkedFunc",
		Type: SymbolTypeFunction,
	}

	unlinked := &ParsedEntity{
		ID:   uuid.New(),
		Name: "unlinkedFunc",
		Type: SymbolTypeFunction,
	}

	linker.AddEntity(linked)
	linker.AddEntity(unlinked)

	ctx := context.Background()
	require.NoError(t, linker.LinkToCanonical(ctx, linked.ID, canonicalID, linkerConfidenceHigh))
	require.NoError(t, linker.LinkToCanonical(ctx, linked.ID, uuid.New(), linkerConfidenceAlt))

	stats := linker.GetLinkingStatistics()

	// Stats counts based on canonicalMappings only
	// TotalEntities counts all entities added
	assert.Equal(t, 2, stats.TotalEntities)
	// LinkedEntities counts entries in canonicalMappings with mappings
	assert.Positive(t, stats.LinkedEntities)
	// TotalMappings counts all canonical links
	assert.Equal(t, 2, stats.TotalMappings)
	assert.Greater(t, stats.AverageConfidence, linkerConfidenceMin)
	assert.Less(t, stats.AverageConfidence, 1.0)
}

func TestCodeEntityLinker_GetLinkingStatistics_BySource(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	entityID := uuid.New()
	entity := &ParsedEntity{
		ID:   entityID,
		Name: "testFunc",
		Type: SymbolTypeFunction,
	}
	linker.AddEntity(entity)

	ctx := context.Background()
	require.NoError(t, linker.LinkToCanonical(ctx, entityID, uuid.New(), linkerConfidenceMedium)) // manual link

	stats := linker.GetLinkingStatistics()

	assert.Positive(t, stats.MappingsBySource["manual"])
}

func TestCodeEntityLinker_MatchesPattern_NameContains(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	entity := &ParsedEntity{
		Name: "loginUser",
		Type: SymbolTypeFunction,
	}

	pattern := &EntityPattern{
		MatchRules: []MatchRule{
			{Type: "name_contains", Pattern: "login"},
		},
	}

	matches := linker.matchesPattern(entity, pattern)
	assert.True(t, matches)

	pattern2 := &EntityPattern{
		MatchRules: []MatchRule{
			{Type: "name_contains", Pattern: "logout"},
		},
	}

	matches2 := linker.matchesPattern(entity, pattern2)
	assert.False(t, matches2)
}

func TestCodeEntityLinker_MatchesPattern_Annotation(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	entity := &ParsedEntity{
		Name:        "authenticateUser",
		Type:        SymbolTypeFunction,
		Annotations: []Annotation{{Name: "canonical", Value: "AuthService"}},
	}

	pattern := &EntityPattern{
		MatchRules: []MatchRule{
			{Type: "annotation", Pattern: "canonical"},
		},
	}

	matches := linker.matchesPattern(entity, pattern)
	assert.True(t, matches)
}

func TestCodeEntityLinker_MatchesPattern_Negation(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	entity := &ParsedEntity{
		Name: "internalHelper",
		Type: SymbolTypeFunction,
	}

	pattern := &EntityPattern{
		MatchRules: []MatchRule{
			{Type: "name_contains", Pattern: "public", Negate: true},
		},
	}

	matches := linker.matchesPattern(entity, pattern)
	assert.True(t, matches, "Should match when negated condition is true")
}

func TestCodeEntityLinker_MatchesPattern_Calls(t *testing.T) {
	linker := NewCodeEntityLinker(nil)

	entity := &ParsedEntity{
		Name: "processData",
		Type: SymbolTypeFunction,
		Calls: []ParsedCall{
			{TargetName: "validateData"},
			{TargetName: "transformData"},
		},
	}

	pattern := &EntityPattern{
		MatchRules: []MatchRule{
			{Type: "calls", Pattern: "validateData"},
		},
	}

	matches := linker.matchesPattern(entity, pattern)
	assert.True(t, matches)
}

func TestCodeEntityLinker_ThreadSafety(t *testing.T) {
	_ = t
	linker := NewCodeEntityLinker(nil)

	// Add initial entity
	entity := &ParsedEntity{
		ID:   uuid.New(),
		Name: "testFunc",
		Type: SymbolTypeFunction,
	}
	linker.AddEntity(entity)

	// Concurrent operations should not panic
	done := make(chan bool, 2)

	go func() {
		canonicalID := uuid.New()
		ctx := context.Background()
		assert.NoError(t, linker.LinkToCanonical(ctx, entity.ID, canonicalID, linkerConfidenceMedium))
		done <- true
	}()

	go func() {
		_ = linker.GetCanonicalForEntity(entity.ID)
		done <- true
	}()

	// Wait for goroutines
	<-done
	<-done
}
