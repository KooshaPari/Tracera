# ADR-001: Multi-Language Template Registry Architecture

**Status**: Accepted  
**Date**: 2026-04-04  
**Deciders**: Phenotype Architecture Team  
**Related**: HEXAGON-SPEC-001, HEXAGON-PLAN-001

## Context

The Phenotype ecosystem requires consistent hexagonal architecture implementations across multiple programming languages. Individual language-specific template repositories (hexagon-go, hexagon-rust, hexagon-zig, template-lang-elixir, template-lang-kotlin, template-lang-mojo, template-lang-swift) created fragmentation and maintenance overhead.

### Problem Statement

1. **Fragmentation**: 7 separate repositories with different structures, conventions, and maintenance practices
2. **Inconsistency**: No unified approach to hexagonal architecture across languages
3. **Duplication**: Common patterns (CI/CD, documentation, tooling) repeated across repositories
4. **Discovery**: Developers couldn't easily find templates for their preferred language
5. **Evolution**: Changes to core patterns required updates across all repositories

## Decision Drivers

| Driver | Weight | Description |
|--------|--------|-------------|
| Consistency | High | Unified hexagonal architecture patterns across languages |
| Maintainability | High | Single source of truth for templates |
| Discoverability | High | Centralized registry for all language templates |
| Language Idioms | High | Respect language-specific best practices |
| Tooling Integration | Medium | Common CLI and automation |
| Documentation | Medium | Unified documentation approach |
| Migration Path | Medium | Preserve existing template investments |

## Decisions

### Decision 1: Unified Registry Structure

**Decision**: Consolidate all language templates into a single `hexagon` repository with language-specific subdirectories.

**Structure**:
```
hexagon/
├── templates/
│   ├── go/           # Merged from hexagon-go
│   ├── rust/         # Merged from hexagon-rust
│   ├── zig/          # Merged from hexagon-zig
│   ├── elixir/       # Merged from template-lang-elixir
│   ├── kotlin/       # Merged from template-lang-kotlin
│   ├── mojo/         # Merged from template-lang-mojo
│   └── swift/        # Merged from template-lang-swift
├── docs/
├── scripts/
└── README.md
```

**Rationale**:
- Single repository for discovery and contribution
- Shared tooling and automation
- Cross-language pattern comparison
- Atomic updates across templates

**Consequences**:
- (+) Unified versioning and release management
- (+) Easier cross-language pattern sharing
- (+) Reduced maintenance overhead
- (-) Larger repository size
- (-) More complex CI/CD pipelines

### Decision 2: Language-Specific Template Autonomy

**Decision**: Each language template maintains autonomy in implementation while following common structural conventions.

**Common Conventions**:
```
templates/{language}/
├── domain/              # Business logic (required)
├── application/         # Use cases (required)
├── ports/              # Interfaces (required)
├── infrastructure/     # Adapters (required)
├── docs/               # Language-specific docs
├── tests/              # Test structure
├── README.md           # Language-specific guide
├── SPEC.md             # Detailed specification
└── {config files}      # Language-specific (Cargo.toml, go.mod, etc.)
```

**Language-Specific Flexibility**:
- Go: Interface-based ports, context propagation
- Rust: Trait-based ports, generic repositories
- Zig: Vtable-based interfaces, explicit allocators
- Elixir: Behaviour-based ports, OTP supervision
- Kotlin: Interface-based with coroutines
- Mojo: Struct-based with Python interop
- Swift: Protocol-oriented with async/await

**Rationale**:
- Respects language idioms and conventions
- Enables optimal use of language features
- Maintains developer familiarity
- Allows language-specific tooling

**Consequences**:
- (+) Language-idiomatic implementations
- (+) Developer adoption ease
- (+) Optimal performance characteristics
- (-) Reduced code sharing between languages
- (-) Language-specific learning curves

### Decision 3: Git Subtree Merge Strategy

**Decision**: Use Git subtree merges to preserve commit history from source repositories.

**Process**:
```bash
# Add remote for source repository
git remote add source-template-lang-elixir https://github.com/KooshaPari/template-lang-elixir.git

# Fetch and merge with subtree
git fetch source-template-lang-elixir
git merge -s ours --no-commit source-template-lang-elixir/main
git read-tree --prefix=templates/elixir/ -u source-template-lang-elixir/main

# Commit with reference
# Merged template-lang-elixir into templates/elixir/
```

**Rationale**:
- Preserves full commit history from source repositories
- Maintains authorship attribution
- Enables future updates from source if needed
- Standard Git operations work normally

**Consequences**:
- (+) Complete history preservation
- (+) Normal Git workflow compatibility
- (-) Larger repository history
- (-) Slightly more complex initial setup

### Decision 4: Common Metadata Schema

**Decision**: Define a common metadata schema for all templates to enable tooling integration.

**Schema** (hexagon.yaml):
```yaml
version: "1.0"
template:
  id: "go-hexagonal"
  language: "go"
  version: "1.2.0"
  description: "Hexagonal architecture template for Go"
  
architecture:
  pattern: "hexagonal"
  layers:
    - domain
    - application
    - ports
    - infrastructure
  
features:
  - entity-generation
  - repository-scaffold
  - use-case-template
  - adapter-stubs
  
dependencies:
  required:
    - go >= 1.21
  optional:
    - docker
    - make
  
tooling:
  cli: "hexagon-go"
  commands:
    generate: "go generate ./..."
    test: "go test ./..."
    build: "go build ./..."
```

**Rationale**:
- Enables automated tooling across languages
- Supports template discovery and comparison
- Facilitates IDE integrations
- Standardizes template capabilities

**Consequences**:
- (+) Tooling ecosystem enablement
- (+) Template marketplace potential
- (-) Maintenance of schema versioning
- (-) Required updates for new features

### Decision 5: Shared Documentation Pattern

**Decision**: Use common documentation structure with language-specific sections.

**Required Documents**:
| Document | Purpose | Level |
|----------|---------|-------|
| README.md | Quick start, overview | Language-specific |
| SPEC.md | Detailed specification | Language-specific |
| docs/adr/ | Architecture decisions | Language-specific |
| docs/research/SOTA.md | State of the art | Language-specific |

**Common Elements**:
- Traceability markers (/// @trace HEXAGON-XXX)
- Architecture diagrams
- Getting started guides
- API reference

**Rationale**:
- Consistent developer experience
- Easier cross-language comparison
- Shared documentation tooling
- Unified branding

**Consequences**:
- (+) Familiar structure across languages
- (+) Easier documentation maintenance
- (-) Must balance common vs specific content

## Alternatives Considered

### Alternative 1: Separate Repositories with Shared Library

**Approach**: Keep separate repos, extract shared code to hexagon-lib

**Rejection**: Doesn't solve discovery problem; shared code minimal due to language differences; complexity without benefit.

### Alternative 2: Monorepo with Strict Standardization

**Approach**: Force identical structure across all languages

**Rejection**: Violates language idioms; reduces developer adoption; fights against language ecosystems.

### Alternative 3: Git Submodules

**Approach**: Use submodules to reference external template repos

**Rejection**: Submodules are error-prone; requires separate repo management; complicates contributions.

## Consequences Summary

### Positive

1. **Unified Discovery**: Single repository for all hexagonal templates
2. **Consistent Quality**: Shared standards and review processes
3. **Cross-Language Learning**: Easy comparison between language implementations
4. **Reduced Maintenance**: Common tooling and automation
5. **Ecosystem Growth**: Easier addition of new language templates
6. **Documentation Quality**: Shared documentation infrastructure

### Negative

1. **Repository Size**: Larger clone size with all templates
2. **CI Complexity**: Multi-language CI pipelines
3. **Release Coordination**: Versioning across languages
4. **Permission Management**: More complex access control

### Mitigations

| Concern | Mitigation |
|---------|------------|
| Repository size | Sparse checkout support, shallow clones |
| CI complexity | Parallel jobs, language-specific workflows |
| Release coordination | Semantic versioning per template |
| Permission management | CODEOWNERS per template directory |

## Implementation Notes

### Migration Timeline

| Phase | Templates | Timeline |
|-------|-----------|----------|
| 1 | go, rust, zig | Completed |
| 2 | elixir, kotlin, mojo, swift | Completed |
| 3 | docs consolidation | Current |
| 4 | automation setup | Planned |

### Verification

```bash
# Verify template structure
for lang in go rust zig elixir kotlin mojo swift; do
    echo "Checking $lang..."
    test -d templates/$lang/domain || echo "Missing domain in $lang"
    test -d templates/$lang/application || echo "Missing application in $lang"
    test -d templates/$lang/ports || echo "Missing ports in $lang"
    test -d templates/$lang/infrastructure || echo "Missing infrastructure in $lang"
done
```

## References

- [Hexagon Consolidation Plan](../PLAN.md)
- [Git Subtree Documentation](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging#_subtree_merge)
- [Phenotype Repository Strategy](https://github.com/KooshaPari/PhenoSpecs/blob/main/adr/ADR-001-monorepo-strategy.md)

## Traceability

/// @trace HEXAGON-ADR-001
/// @trace HEXAGON-SPEC-001
