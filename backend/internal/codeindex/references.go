package codeindex

import (
	"context"
	"fmt"
	"strings"
	"sync"

	"github.com/google/uuid"
)

// ReferenceResolver handles cross-language and cross-file reference resolution
type ReferenceResolver struct {
	symbolTables   map[string]*SymbolTable  // filePath -> SymbolTable
	symbolCache    map[string]*ParsedEntity // qualifiedName -> entity
	importResolver *ImportResolver
	mu             sync.RWMutex
}

// ImportResolver handles import statement resolution
type ImportResolver struct {
	projectRoot       string
	languageResolvers map[Language]ImportResolverStrategy
	mu                sync.RWMutex
}

// ImportResolverStrategy defines language-specific import resolution
type ImportResolverStrategy interface {
	ResolveImport(ctx context.Context, importPath string, fromFile string) (*ImportResolution, error)
	GetExports(ctx context.Context, modulePath string) ([]string, error)
}

// NewReferenceResolver creates a new reference resolver
func NewReferenceResolver(projectRoot string) *ReferenceResolver {
	return &ReferenceResolver{
		symbolTables: make(map[string]*SymbolTable),
		symbolCache:  make(map[string]*ParsedEntity),
		importResolver: &ImportResolver{
			projectRoot:       projectRoot,
			languageResolvers: make(map[Language]ImportResolverStrategy),
		},
	}
}

// RegisterResolver registers a language-specific import resolver.
func (ir *ImportResolver) RegisterResolver(lang Language, resolver ImportResolverStrategy) {
	ir.mu.Lock()
	defer ir.mu.Unlock()
	ir.languageResolvers[lang] = resolver
}

// ResolveImport resolves an import statement to its actual location
func (ir *ImportResolver) ResolveImport(
	ctx context.Context,
	importRef ImportRef,
	fromFile string,
	lang Language,
) (*ImportResolution, error) {
	ir.mu.RLock()
	resolver, ok := ir.languageResolvers[lang]
	ir.mu.RUnlock()

	if !ok {
		return nil, fmt.Errorf("no resolver registered for language: %s", lang)
	}

	resolution, err := resolver.ResolveImport(ctx, importRef.ModulePath, fromFile)
	if err != nil {
		return nil, err
	}

	return resolution, nil
}

// AddSymbolTable registers a symbol table for a file
func (rr *ReferenceResolver) AddSymbolTable(filePath string, table *SymbolTable) {
	rr.mu.Lock()
	defer rr.mu.Unlock()
	rr.symbolTables[filePath] = table
	for name, entity := range table.Exports {
		if entity.QualifiedName == "" {
			entity.QualifiedName = filePath + ":" + name
		}
		rr.symbolCache[entity.QualifiedName] = entity
	}
}

// ResolveCallTarget resolves a call to its target entity
func (rr *ReferenceResolver) ResolveCallTarget(
	ctx context.Context,
	call ParsedCall,
	_ string,
	_ Language,
) (*ParsedEntity, error) {
	_ = ctx
	rr.mu.RLock()
	defer rr.mu.RUnlock()

	// First check if it's in the local symbol cache
	if entity, ok := rr.symbolCache[call.TargetName]; ok {
		return entity, nil
	}

	// Check if it's a qualified name (e.g., "module.Function")
	if strings.Contains(call.TargetName, ".") {
		if entity, ok := rr.symbolCache[call.TargetName]; ok {
			return entity, nil
		}
	}

	// If module path is provided, search in that module
	if call.ModulePath != "" {
		for name, entity := range rr.symbolCache {
			if strings.HasPrefix(name, call.ModulePath) && strings.HasSuffix(name, call.TargetName) {
				return entity, nil
			}
		}
	}

	// Not found
	return nil, fmt.Errorf("could not resolve call target: %s", call.TargetName)
}

// ResolveReference resolves a symbol reference to its definition
func (rr *ReferenceResolver) ResolveReference(
	ctx context.Context,
	ref ParsedReference,
	fromFile string,
	_ Language,
) (*ParsedEntity, error) {
	_ = ctx
	rr.mu.RLock()
	defer rr.mu.RUnlock()

	if entity := rr.resolveFromLocalTable(fromFile, ref.SymbolName); entity != nil {
		return entity, nil
	}

	if entity := rr.resolveFromCache(ref.SymbolName); entity != nil {
		return entity, nil
	}

	return nil, fmt.Errorf("could not resolve reference: %s", ref.SymbolName)
}

func (rr *ReferenceResolver) resolveFromLocalTable(fromFile string, symbolName string) *ParsedEntity {
	table, ok := rr.symbolTables[fromFile]
	if !ok {
		return nil
	}
	if entity, ok := table.Exports[symbolName]; ok {
		return entity
	}
	return rr.resolveImportedSymbol(table, symbolName)
}

func (rr *ReferenceResolver) resolveImportedSymbol(table *SymbolTable, symbolName string) *ParsedEntity {
	resolution, ok := table.Imports[symbolName]
	if !ok || resolution.ResolvedID == nil {
		return nil
	}
	return rr.findEntityByID(*resolution.ResolvedID)
}

func (rr *ReferenceResolver) resolveFromCache(symbolName string) *ParsedEntity {
	entity, ok := rr.symbolCache[symbolName]
	if !ok {
		return nil
	}
	return entity
}

func (rr *ReferenceResolver) findEntityByID(id uuid.UUID) *ParsedEntity {
	for _, entity := range rr.symbolCache {
		if entity.ID == id {
			return entity
		}
	}
	return nil
}

// BuildCallChain builds a call chain starting from an entity
func (rr *ReferenceResolver) BuildCallChain(
	ctx context.Context,
	entity *ParsedEntity,
	maxDepth int,
) (*CallChainResolution, error) {
	rr.mu.RLock()
	defer rr.mu.RUnlock()

	chain := &CallChainResolution{
		EntryPoint:   entity,
		Steps:        make([]*ChainStepResolved, 0),
		CircularRefs: make([]string, 0),
	}

	visited := make(map[string]bool)
	err := rr.buildCallChainRecursive(ctx, entity, chain, visited, 0, maxDepth)
	if err != nil {
		return nil, err
	}

	chain.Depth = len(chain.Steps)
	return chain, nil
}

func (rr *ReferenceResolver) buildCallChainRecursive(
	ctx context.Context,
	entity *ParsedEntity,
	chain *CallChainResolution,
	visited map[string]bool,
	currentDepth int,
	maxDepth int,
) error {
	if rr.isMaxDepthReached(currentDepth, maxDepth) {
		return nil
	}

	qualifiedName := entity.QualifiedName
	if rr.markVisited(visited, chain, qualifiedName) {
		return nil
	}

	for _, call := range entity.Calls {
		targetEntity, err := rr.resolveCallTargetEntity(ctx, call, entity)
		if err != nil {
			continue
		}

		rr.appendCallChainStep(chain, call, targetEntity)

		// Recursively build chain
		if err := rr.buildCallChainRecursive(ctx, targetEntity, chain, visited, currentDepth+1, maxDepth); err != nil {
			return err
		}
	}

	return nil
}

func (rr *ReferenceResolver) isMaxDepthReached(currentDepth int, maxDepth int) bool {
	return currentDepth >= maxDepth
}

func (rr *ReferenceResolver) markVisited(
	visited map[string]bool,
	chain *CallChainResolution,
	qualifiedName string,
) bool {
	if visited[qualifiedName] {
		chain.CircularRefs = append(chain.CircularRefs, qualifiedName)
		return true
	}
	visited[qualifiedName] = true
	return false
}

func (rr *ReferenceResolver) resolveCallTargetEntity(
	ctx context.Context,
	call ParsedCall,
	entity *ParsedEntity,
) (*ParsedEntity, error) {
	targetEntity := rr.findTargetByID(call.TargetID)
	if targetEntity != nil {
		return targetEntity, nil
	}

	resolved, err := rr.ResolveCallTarget(ctx, call, entity.FilePath, entity.Language)
	if err != nil {
		return nil, err
	}
	return resolved, nil
}

func (rr *ReferenceResolver) findTargetByID(targetID *uuid.UUID) *ParsedEntity {
	if targetID == nil {
		return nil
	}
	for _, cached := range rr.symbolCache {
		if cached.ID == *targetID {
			return cached
		}
	}
	return nil
}

func (rr *ReferenceResolver) appendCallChainStep(
	chain *CallChainResolution,
	call ParsedCall,
	targetEntity *ParsedEntity,
) {
	step := &ChainStepResolved{
		Entity:    targetEntity,
		FilePath:  targetEntity.FilePath,
		Language:  targetEntity.Language,
		Order:     len(chain.Steps),
		CallType:  "direct",
		Arguments: call.Arguments,
	}
	if call.IsAsync {
		step.CallType = "async"
	}
	chain.Steps = append(chain.Steps, step)
}

// GetEntityByQualifiedName looks up an entity by its fully qualified name
func (rr *ReferenceResolver) GetEntityByQualifiedName(qualifiedName string) *ParsedEntity {
	rr.mu.RLock()
	defer rr.mu.RUnlock()
	return rr.symbolCache[qualifiedName]
}

// GetEntitiesInFile returns all entities defined in a file
func (rr *ReferenceResolver) GetEntitiesInFile(filePath string) []*ParsedEntity {
	rr.mu.RLock()
	defer rr.mu.RUnlock()

	table, ok := rr.symbolTables[filePath]
	if !ok {
		return nil
	}

	entities := make([]*ParsedEntity, 0, len(table.Exports))
	for _, entity := range table.Exports {
		entities = append(entities, entity)
	}
	return entities
}

// FindReferencesToEntity finds all references to a specific entity
func (rr *ReferenceResolver) FindReferencesToEntity(entityID uuid.UUID) []*CrossFileReference {
	rr.mu.RLock()
	defer rr.mu.RUnlock()

	refs := make([]*CrossFileReference, 0)

	for _, entity := range rr.symbolCache {
		rr.appendSymbolRefMatches(&refs, entity, entityID)
		rr.appendCallRefMatches(&refs, entity, entityID)
	}

	return refs
}

func (rr *ReferenceResolver) appendSymbolRefMatches(
	refs *[]*CrossFileReference,
	entity *ParsedEntity,
	entityID uuid.UUID,
) {
	for _, ref := range entity.References {
		if ref.SymbolID == nil || *ref.SymbolID != entityID {
			continue
		}
		*refs = append(*refs, &CrossFileReference{
			SourceFile:    entity.FilePath,
			SourceEntity:  &entity.ID,
			SourceLine:    ref.Line,
			TargetEntity:  ref.SymbolID,
			TargetName:    ref.SymbolName,
			ReferenceType: "reference",
		})
	}
}

func (rr *ReferenceResolver) appendCallRefMatches(
	refs *[]*CrossFileReference,
	entity *ParsedEntity,
	entityID uuid.UUID,
) {
	for _, call := range entity.Calls {
		if call.TargetID == nil || *call.TargetID != entityID {
			continue
		}
		*refs = append(*refs, &CrossFileReference{
			SourceFile:    entity.FilePath,
			SourceEntity:  &entity.ID,
			SourceLine:    call.Line,
			TargetEntity:  call.TargetID,
			TargetName:    call.TargetName,
			ReferenceType: "call",
		})
	}
}

// BuildImportGraph builds a directed graph of module imports
func (rr *ReferenceResolver) BuildImportGraph() map[string][]string {
	rr.mu.RLock()
	defer rr.mu.RUnlock()

	graph := make(map[string][]string)

	for filePath, table := range rr.symbolTables {
		imports := make([]string, 0, len(table.Imports))
		for _, importRes := range table.Imports {
			imports = append(imports, importRes.ResolvedPath)
		}
		graph[filePath] = imports
	}

	return graph
}

// DetectCircularImports detects circular import dependencies
func (rr *ReferenceResolver) DetectCircularImports() [][]string {
	graph := rr.BuildImportGraph()
	circular := make([][]string, 0)
	visited := make(map[string]bool)
	recursionStack := make(map[string]bool)

	for node := range graph {
		if !visited[node] {
			rr.walkImportGraph(graph, node, visited, recursionStack, nil, &circular)
		}
	}

	return circular
}

func (rr *ReferenceResolver) walkImportGraph(
	graph map[string][]string,
	node string,
	visited map[string]bool,
	recursionStack map[string]bool,
	path []string,
	circular *[][]string,
) {
	visited[node] = true
	recursionStack[node] = true
	path = append(path, node)

	for _, neighbor := range graph[node] {
		if !visited[neighbor] {
			rr.walkImportGraph(graph, neighbor, visited, recursionStack, path, circular)
			continue
		}
		if recursionStack[neighbor] {
			cycle := buildImportCycle(path, neighbor)
			if len(cycle) > 0 {
				*circular = append(*circular, cycle)
			}
		}
	}

	recursionStack[node] = false
}

func buildImportCycle(path []string, target string) []string {
	for index, entry := range path {
		if entry == target {
			cycle := make([]string, 0, len(path)-index+1)
			cycle = append(cycle, path[index:]...)
			cycle = append(cycle, target)
			return cycle
		}
	}
	return nil
}

// GetDependenciesOf returns all modules that depend on a given module
func (rr *ReferenceResolver) GetDependenciesOf(filePath string) map[string]int {
	rr.mu.RLock()
	defer rr.mu.RUnlock()

	table, ok := rr.symbolTables[filePath]
	if !ok {
		return nil
	}

	deps := make(map[string]int)
	for _, importRes := range table.Imports {
		deps[importRes.ResolvedPath]++
	}
	return deps
}

// GetDependentsOf returns all modules that depend on a given module
func (rr *ReferenceResolver) GetDependentsOf(filePath string) []string {
	rr.mu.RLock()
	defer rr.mu.RUnlock()

	dependents := make([]string, 0)
	for path, table := range rr.symbolTables {
		if path == filePath {
			continue
		}
		for _, importRes := range table.Imports {
			if importRes.ResolvedPath == filePath {
				dependents = append(dependents, path)
				break
			}
		}
	}
	return dependents
}
