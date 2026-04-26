# ADR-005: Layer Contract Architecture for Template Composition

**Status:** Accepted  
**Date:** 2026-04-04  
**Author:** Phenotype Architecture Team  
**Stakeholders:** Template Program, DevEx, Platform Engineering

---

## Context

The Phenotype ecosystem requires a consistent approach to project scaffolding across multiple programming languages (Go, Python, TypeScript, Rust, Zig, Swift, Kotlin, Mojo, Elixir) and domains (APIs, CLIs, libraries, microservices). 

**Problems Identified:**

1. **Duplication across templates**: Each language template reimplements git initialization, CI/CD configuration, documentation structure, and security policies
2. **Drift over time**: Updates to shared concerns (e.g., security policy changes) require touching N templates
3. **Inconsistent quality**: Some templates have thorough CI, others don't; some have proper documentation, others don't
4. **Composability gap**: No formal mechanism to compose templates (e.g., commons + go + hexagonal)
5. **Version hell**: No clear contract between template layers leads to breaking changes in downstream templates

**Research Findings:**

Analysis of existing solutions (see SOTA.md) reveals:
- Yeoman: Good composition via `composeWith()`, but JavaScript-only
- Cookiecutter: Simple but no composition
- copier: Has updates but no formal contract
- Terraform modules: Excellent versioning and contract model
- Helm charts: Good dependency management

**Key Insight:**
Infrastructure-as-code tools (Terraform, Helm, Ansible) have solved similar problems with:
1. Explicit contract definitions (variables/outputs)
2. Semantic versioning
3. Dependency graphs
4. Reconciliation/apply mechanisms

These patterns can be adapted for project templates.

---

## Decision

We will implement a **Layer Contract Architecture** with the following properties:

### 1. Layer Hierarchy

Templates are organized into layers with strict dependency direction:

```
Application Layer      <- Project-specific (hexagonal-go-service)
       ↑
Domain Layer          <- Domain patterns (hexagonal-go, hexagonal-python)
       ↑
Language Layer        <- Language conventions (go-kit, py-kit)
       ↑
Commons Layer         <- Cross-cutting (template-commons) ← This layer
       ↑
Infrastructure Layer  <- Platform (docker, k8s manifests)
```

**Rule:** Dependencies only flow upward. A domain layer may depend on commons, but commons never depends on domain.

### 2. Contract Manifest

Each layer declares its contract in `template.manifest.json`:

```json
{
  "layer_type": "commons|language|domain|application",
  "layer_name": "template-commons",
  "version": "1.2.3",
  "depends_on": [
    {"name": "infrastructure-base", "version": "^0.5.0"}
  ],
  "owned_paths": [
    "contracts/**",
    "docs/**",
    "scripts/**",
    ".github/workflows/ci.yml"
  ],
  "protected_paths": [
    "README.md",
    "SECURITY.md",
    "AGENTS.md",
    "CLAUDE.md"
  ],
  "required_files": [
    {"path": "LICENSE", "template": "templates/LICENSE.mit"}
  ],
  "variables": {
    "PROJECT_NAME": {"required": true, "description": "Project name"},
    "AUTHOR": {"required": false, "default": "Phenotype Team"}
  }
}
```

### 3. Ownership Model

**Owned Paths:**
- Layer has exclusive write access
- Can create, update, delete these paths during scaffolding
- Updates reconcile with user modifications via three-way merge

**Protected Paths:**
- Layer ensures these exist but doesn't overwrite user modifications
- Creates if missing, warns if present but different
- Used for governance files (SECURITY.md, LICENSE)

### 4. Reconciliation Modes

```yaml
# reconcile.rules.yaml
modes:
  smart:
    create_missing: true
    update_template_owned_if_unchanged: true
    create_conflict_sidecar: true
    sidecar_suffix: .template.new
  overwrite:
    create_missing: true
    replace_template_owned: true
  skip:
    report_only: true
```

**Smart Mode (Default):**
1. Files unchanged since original scaffold: Update automatically
2. Files modified by user: Create `.template.new` sidecar for manual merge
3. New files in template: Create in project

### 5. Version Semantics

**MAJOR (X.0.0):**
- Removing `owned_paths` entries
- Removing `required_files` entries
- Changing variable substitution syntax
- Breaking reconcile behavior changes

**MINOR (0.X.0):**
- Adding new `owned_paths`
- Adding new `variables`
- Adding new `required_files`
- New hook types

**PATCH (0.0.X):**
- Template content fixes
- Documentation updates
- Hook script corrections

### 6. Composition Verification

Before scaffolding, verify:

```python
def verify_composition(layers: List[Layer]) -> CompositionResult:
    """
    1. Check version constraints satisfied
    2. Check no owned_paths conflicts (same path owned by multiple layers)
    3. Check all required_files can be satisfied
    4. Check all required variables provided
    5. Check dependency graph is DAG (no cycles)
    """
```

---

## Consequences

### Positive

1. **DRY at Scale**: Bug fixes in commons propagate to all templates
2. **Quality Baseline**: All projects get consistent CI, docs, security
3. **Composability**: Clear rules for combining layers
4. **Reproducibility**: Version pinning ensures consistent output
5. **Evolution Path**: Smart reconciliation enables template updates
6. **Auditability**: Manifests document what each layer provides

### Negative

1. **Learning Curve**: Authors must understand layer contract semantics
2. **Manifest Ceremony**: Additional files to maintain
3. **Tooling Required**: Need tools to verify composition, reconcile updates
4. **Complexity**: More sophisticated than simple template copying

### Neutral

1. **Git Submodules**: Layer distribution via submodules (chosen for auditability)
2. **YAML/JSON**: Human-readable but strict format requirements

---

## Alternatives Considered

### Alternative 1: Git Subtree Merge

**Approach:** Use git subtree to merge commons into each template repo.

**Rejected:**
- Subtree requires complex git operations
- Hard to track which version of commons is in use
- No formal contract verification
- Difficult to handle conflicts

### Alternative 2: npm-style Peer Dependencies

**Approach:** Declare commons as peer dependency, resolve at scaffold time.

**Rejected:**
- Dependency resolution complexity
- Still need contract definition
- Doesn't solve reconciliation problem
- Package manager lock-in

### Alternative 3: Central Template Registry

**Approach:** Single repository with all templates, versioning via directories.

**Rejected:**
- Monorepo scaling issues
- Tight coupling of unrelated templates
- Harder to fork/customize individual templates
- No independent release cycles

### Alternative 4: Pure Copier Integration

**Approach:** Use copier's existing update mechanism.

**Rejected:**
- Python execution requirement
- Limited to copier's Jinja2/YAML model
- No formal contract concept
- Harder to integrate with CI pipelines

---

## Implementation

### Phase 1: Foundation (Current)

- [x] Define layer contract schema
- [x] Create template.manifest.json format
- [x] Create reconcile.rules.yaml format
- [x] Document in SPEC.md

### Phase 2: Tooling (Next)

- [ ] `template-cli verify` - Composition verification
- [ ] `template-cli scaffold` - Execute scaffolding
- [ ] `template-cli update` - Smart reconciliation
- [ ] `template-cli check` - Validate against rules

### Phase 3: Migration (Future)

- [ ] Convert existing templates to layer model
- [ ] Establish commons as dependency
- [ ] Set up update workflows

---

## References

1. [SOTA.md](./SOTA.md) - Research on template systems
2. [SPEC.md](../SPEC.md) - Full specification
3. Terraform Module Registry documentation
4. Helm Chart dependencies documentation
5. Software Product Lines: Practices and Patterns (Clements & Northrop)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-04 | Accepted layer contract architecture | Uniquely addresses composability + versioning + reconciliation |
| 2026-04-04 | YAML/JSON for manifests | Human-readable, tool-parseable, widely supported |
| 2026-04-04 | Three-way merge for reconciliation | Balances automation with user control |
| 2026-04-04 | owned_paths + protected_paths distinction | Clear semantics for different file types |

---

*End of ADR-005*
