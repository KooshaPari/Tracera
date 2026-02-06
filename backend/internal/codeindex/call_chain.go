package codeindex

import (
	"context"
	"time"

	"github.com/google/uuid"
)

const (
	defaultCallChainMaxDepth = 10
	minChainSteps            = 2
)

// CallChainAnalyzer analyzes call chains for journey derivation
type CallChainAnalyzer struct {
	repo     Repository
	maxDepth int
}

// NewCallChainAnalyzer creates a new call chain analyzer
func NewCallChainAnalyzer(repo Repository) *CallChainAnalyzer {
	return &CallChainAnalyzer{
		repo:     repo,
		maxDepth: defaultCallChainMaxDepth, // Default max depth
	}
}

// SetMaxDepth sets the maximum depth for call chain analysis
func (analyzer *CallChainAnalyzer) SetMaxDepth(depth int) {
	analyzer.maxDepth = depth
}

// AnalyzeCallChain traces the call chain starting from an entity
func (analyzer *CallChainAnalyzer) AnalyzeCallChain(
	ctx context.Context,
	projectID uuid.UUID,
	entryPointID uuid.UUID,
) (*CallChain, error) {
	// Get the entry point entity
	entryPoint, err := analyzer.repo.GetCodeEntity(ctx, entryPointID)
	if err != nil {
		return nil, err
	}

	chain := &CallChain{
		ID:         uuid.New(),
		ProjectID:  projectID,
		EntryPoint: entryPointID,
		Type:       analyzer.determineChainType(entryPoint),
		Steps:      make([]ChainStep, 0),
		CreatedAt:  time.Now(),
	}

	// Track visited entities to avoid cycles
	visited := make(map[uuid.UUID]bool)

	// Build the chain
	analyzer.buildChain(ctx, projectID, entryPoint, chain, visited, 0)

	chain.Depth = len(chain.Steps)
	chain.CrossLang = analyzer.hasCrossLanguageCalls(chain)

	return chain, nil
}

// determineChainType determines the type of call chain based on entry point
func (analyzer *CallChainAnalyzer) determineChainType(entity *CodeEntity) string {
	switch entity.SymbolType {
	case SymbolTypeHandler, SymbolTypeRoute:
		return "api_chain"
	case SymbolTypeComponent:
		return "user_flow"
	case SymbolTypeFunction,
		SymbolTypeMethod,
		SymbolTypeClass,
		SymbolTypeInterface,
		SymbolTypeStruct,
		SymbolTypeType,
		SymbolTypeVariable,
		SymbolTypeConstant,
		SymbolTypeEnum,
		SymbolTypeModule,
		SymbolTypePackage,
		SymbolTypeProperty,
		SymbolTypeParameter,
		SymbolTypeHook:
		return "data_path"
	default:
		return "data_path"
	}
}

// buildChain recursively builds the call chain
func (analyzer *CallChainAnalyzer) buildChain(
	ctx context.Context,
	projectID uuid.UUID,
	entity *CodeEntity,
	chain *CallChain,
	visited map[uuid.UUID]bool,
	depth int,
) {
	if analyzer.shouldStopChain(depth, entity, visited) {
		return
	}

	analyzer.appendChainStep(entity, chain)
	analyzer.followEntityCalls(ctx, projectID, entity, chain, visited, depth)
}

func (analyzer *CallChainAnalyzer) shouldStopChain(
	depth int,
	entity *CodeEntity,
	visited map[uuid.UUID]bool,
) bool {
	if depth >= analyzer.maxDepth {
		return true
	}
	if visited[entity.ID] {
		return true
	}
	visited[entity.ID] = true
	return false
}

func (analyzer *CallChainAnalyzer) appendChainStep(entity *CodeEntity, chain *CallChain) {
	step := ChainStep{
		EntityID:   entity.ID,
		SymbolName: entity.SymbolName,
		FilePath:   entity.FilePath,
		Language:   entity.Language,
		Order:      len(chain.Steps),
		CallType:   "direct",
	}

	if entity.IsAsync {
		step.CallType = "async"
	}

	chain.Steps = append(chain.Steps, step)
}

func (analyzer *CallChainAnalyzer) followEntityCalls(
	ctx context.Context,
	projectID uuid.UUID,
	entity *CodeEntity,
	chain *CallChain,
	visited map[uuid.UUID]bool,
	depth int,
) {
	for _, call := range entity.Calls {
		target := analyzer.resolveCallTarget(ctx, projectID, entity, call)
		if target == nil {
			continue
		}
		analyzer.buildChain(ctx, projectID, target, chain, visited, depth+1)
	}
}

func (analyzer *CallChainAnalyzer) resolveCallTarget(
	ctx context.Context,
	projectID uuid.UUID,
	entity *CodeEntity,
	call CallRef,
) *CodeEntity {
	if call.TargetID == nil {
		resolved, err := analyzer.resolveCall(ctx, projectID, entity, &call)
		if err != nil {
			return nil
		}
		return resolved
	}

	target, err := analyzer.repo.GetCodeEntity(ctx, *call.TargetID)
	if err != nil {
		return nil
	}
	return target
}

// resolveCall attempts to resolve an unresolved call reference
func (analyzer *CallChainAnalyzer) resolveCall(
	ctx context.Context,
	projectID uuid.UUID,
	caller *CodeEntity,
	call *CallRef,
) (*CodeEntity, error) {
	// Try to find by name in the same module first
	entities, err := analyzer.repo.FindBySymbolName(ctx, projectID, call.TargetName)
	if err != nil {
		return nil, err
	}

	if len(entities) == 0 {
		return nil, nil
	}

	// Prefer entities in the same file/module
	for _, e := range entities {
		if e.FilePath == caller.FilePath {
			return &e, nil
		}
	}

	// Prefer entities in the same language
	for _, e := range entities {
		if e.Language == caller.Language {
			return &e, nil
		}
	}

	// Return the first match
	return &entities[0], nil
}

// hasCrossLanguageCalls checks if the chain crosses language boundaries
func (analyzer *CallChainAnalyzer) hasCrossLanguageCalls(chain *CallChain) bool {
	if len(chain.Steps) < minChainSteps {
		return false
	}

	firstLang := chain.Steps[0].Language
	for _, step := range chain.Steps[1:] {
		if step.Language != firstLang {
			return true
		}
	}

	return false
}

// FindEntryPoints finds potential entry points for journey analysis
func (analyzer *CallChainAnalyzer) FindEntryPoints(ctx context.Context, projectID uuid.UUID) ([]CodeEntity, error) {
	// Entry points are typically:
	// - HTTP handlers
	// - React components
	// - Main functions
	// - Event handlers

	entryPointTypes := []SymbolType{
		SymbolTypeHandler,
		SymbolTypeRoute,
		SymbolTypeComponent,
	}

	var entryPoints []CodeEntity

	for _, symType := range entryPointTypes {
		entities, err := analyzer.repo.FindBySymbolType(ctx, projectID, symType)
		if err != nil {
			continue
		}
		entryPoints = append(entryPoints, entities...)
	}

	return entryPoints, nil
}

// AnalyzeAllChains analyzes call chains for all entry points
func (analyzer *CallChainAnalyzer) AnalyzeAllChains(ctx context.Context, projectID uuid.UUID) ([]CallChain, error) {
	entryPoints, err := analyzer.FindEntryPoints(ctx, projectID)
	if err != nil {
		return nil, err
	}

	var chains []CallChain

	for _, ep := range entryPoints {
		chain, err := analyzer.AnalyzeCallChain(ctx, projectID, ep.ID)
		if err != nil {
			continue
		}
		if len(chain.Steps) >= minChainSteps { // Only include non-trivial chains
			chains = append(chains, *chain)
		}
	}

	return chains, nil
}
