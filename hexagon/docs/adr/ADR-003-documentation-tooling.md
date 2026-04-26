# ADR-003: Documentation and Tooling Strategy

**Status**: Accepted  
**Date**: 2026-04-04  
**Deciders**: Phenotype Architecture Team  
**Related**: HEXAGON-SPEC-001, HEXAGON-ADR-001, HEXAGON-ADR-002

## Context

The Hexagon project requires comprehensive documentation and tooling to support a multi-language template registry. The documentation must serve multiple audiences (template users, template contributors, architecture decision makers) while maintaining consistency across seven programming languages.

### Problem Statement

1. **Documentation Proliferation**: Multiple repositories led to inconsistent documentation patterns
2. **Audience Confusion**: Mixed documentation for users vs contributors
3. **Maintenance Burden**: Keeping documentation synchronized across languages
4. **Tooling Fragmentation**: Each language template had different tooling approaches
5. **Discovery Challenges**: Difficult to find relevant documentation
6. **Traceability Gaps**: No consistent traceability to requirements

## Decision Drivers

| Driver | Weight | Description |
|--------|--------|-------------|
| Discoverability | High | Easy to find relevant docs |
| Consistency | High | Common structure across languages |
| Maintainability | High | Living documents, easy to update |
| Audience Clarity | High | Clear separation of concerns |
| Automation | Medium | Tooling support for common tasks |
| Extensibility | Medium | Easy to add new languages |

## Decisions

### Decision 1: Documentation Hierarchy

**Decision**: Establish a three-tier documentation hierarchy.

```
Documentation Hierarchy:
├── Registry-Level (Project Root)
│   ├── README.md           # Project overview, quick start
│   ├── SPEC.md             # Comprehensive specification
│   ├── SOTA.md             # State of the art research
│   ├── CHARTER.md          # Project charter
│   ├── ROADMAP.md          # Future plans
│   ├── FAQ.md              # Common questions
│   ├── CONTRIBUTING.md     # Contribution guidelines
│   └── SECURITY.md         # Security policies
│
├── Language-Level (templates/{lang}/)
│   ├── README.md           # Language-specific quick start
│   ├── SPEC.md             # Language-specific specification
│   ├── docs/
│   │   ├── adr/            # Language-specific ADRs
│   │   ├── research/       # SOTA for language
│   │   ├── guides/         # Tutorials, how-tos
│   │   └── reference/      # API docs
│   └── {config files}      # Language-specific configs
│
└── Template-Level (Within each language)
    ├── Getting Started     # First-time user guide
    ├── Architecture        # How hexagonal is implemented
    ├── Examples            # Working code examples
    └── Troubleshooting     # Common issues
```

**Document Purposes**:

| Document | Audience | Content | Update Frequency |
|----------|----------|---------|------------------|
| README.md | New users | Overview, quick start | Per release |
| SPEC.md | Developers | Detailed specification | Per major change |
| SOTA.md | Architects | Research, patterns | Quarterly |
| ADR | Contributors | Decision rationale | Per decision |
| FAQ.md | Users | Common questions | Continuous |
| CONTRIBUTING.md | Contributors | How to contribute | Per process change |

**Rationale**:
- Clear separation of concerns
- Appropriate depth for each audience
- Scalable as languages are added
- Maintainable update cycles

**Consequences**:
- (+) Clear navigation for different needs
- (+) Appropriate information depth
- (+) Scalable structure
- (-) More documents to maintain
- (-) Potential duplication between levels

### Decision 2: nanovms-Style Documentation Format

**Decision**: Adopt nanovms-style documentation format for core project documents.

**Format Characteristics**:

```markdown
# Document Title

## Executive Summary
Brief overview of document purpose and key findings.

## Table of Contents
Navigation for longer documents.

## Main Sections
### Section Header
Content with:
- Tables for comparisons
- Code blocks for examples
- Diagrams (ASCII art when possible)
- Bullet points for clarity

## Decision Records (for ADRs)
### Decision X: Title
**Decision**: Clear statement
**Rationale**: Explanation
**Consequences**: Positive/Negative

## References
Links to external resources.

## Traceability
/// @trace PROJECT-ID-XXX
```

**Document Structure**:

| Element | Purpose | Usage |
|---------|---------|-------|
| Executive Summary | Quick overview | All major docs |
| Table of Contents | Navigation | Docs > 50 lines |
| Code Examples | Concrete illustration | Technical docs |
| Tables | Comparisons | Analysis docs |
| Diagrams | Visual understanding | Architecture docs |
| Traceability | Requirements linking | All docs |

**Rationale**:
- Proven format (nanovms successful example)
- Information density
- Skimmable structure
- Professional presentation

**Consequences**:
- (+) Consistent reading experience
- (+) Easy to navigate
- (+) Information-dense
- (-) Requires discipline to maintain
- (-) More formal than some alternatives

### Decision 3: Traceability Markers

**Decision**: Use standard traceability markers across all documentation.

**Marker Format**:
```markdown
/// @trace HEXAGON-{CATEGORY}-{NUMBER}

Categories:
- SPEC    - Specification documents
- ADR     - Architecture decision records
- SOTA    - State of the art research
- IMPL    - Implementation
- TEST    - Test cases
- DOC     - Documentation
```

**Usage**:
```markdown
# SPEC.md

## Overview
This section defines the core requirements.

/// @trace HEXAGON-SPEC-001

## Domain Layer
Domain entities and business logic.

/// @trace HEXAGON-SPEC-002
/// @trace HEXAGON-ADR-002
```

**Rationale**:
- Link documentation to requirements
- Impact analysis support
- Verification traceability
- Compliance support

**Consequences**:
- (+) Clear requirement linkage
- (+) Audit support
- (+) Impact analysis
- (-) Maintenance overhead
- (-) Requires discipline

### Decision 4: Common Tooling Platform

**Decision**: Implement common tooling at registry level with language-specific plugins.

**Tooling Architecture**:
```
hexagon/
├── scripts/
│   ├── hexagon.sh          # Main CLI entry
│   ├── verify.sh           # Structure verification
│   ├── generate.sh         # Code generation
│   └── release.sh          # Release automation
├── tools/
│   ├── common/             # Shared tooling code
│   ├── go/                 # Go-specific tools
│   ├── rust/               # Rust-specific tools
│   └── ...                 # Other languages
└── Makefile                # Common tasks
```

**Common Commands**:

| Command | Purpose | Scope |
|---------|---------|-------|
| `hexagon verify` | Verify template structure | All languages |
| `hexagon generate` | Generate scaffolding | Language-specific |
| `hexagon test` | Run template tests | Language-specific |
| `hexagon release` | Release template | All languages |
| `hexagon docs` | Generate documentation | All languages |
| `hexagon lint` | Lint templates | Language-specific |

**Language-Specific Integration**:

**Go**:
```bash
hexagon generate entity --name User --language go
# Generates:
# - domain/user.go
# - ports/user_repository.go
# - application/create_user.go
# - infrastructure/postgres_user_repository.go
```

**Rust**:
```bash
hexagon generate entity --name User --language rust
# Generates:
# - src/domain/user.rs
# - src/ports/user_repository.rs
# - src/application/create_user.rs
# - src/infrastructure/postgres_user_repository.rs
```

**Rationale**:
- Consistent interface across languages
- Shared validation logic
- Language-idiomatic generation
- Reduced duplication

**Consequences**:
- (+) Consistent developer experience
- (+) Reduced duplication
- (+) Easier to add languages
- (-) Complex to implement
- (-) Requires maintenance

### Decision 5: Automation Strategy

**Decision**: Automate common maintenance tasks through CI/CD.

**Automated Checks**:

| Check | Trigger | Action |
|-------|---------|--------|
| Structure validation | PR | Verify hexagonal structure |
| Documentation lint | PR | Check markdown, links |
| Traceability check | PR | Verify traceability markers |
| Template testing | PR | Run language-specific tests |
| Release notes | Tag | Generate from CHANGELOG |
| Documentation publish | Merge | Deploy to docs site |

**CI/CD Pipeline**:
```yaml
name: Hexagon CI

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify structure
        run: ./scripts/verify.sh
      - name: Check traceability
        run: ./scripts/check-traceability.sh
      - name: Lint documentation
        run: ./scripts/lint-docs.sh

  test:
    strategy:
      matrix:
        language: [go, rust, zig, elixir, kotlin, mojo, swift]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Test ${{ matrix.language }}
        run: ./scripts/test.sh ${{ matrix.language }}

  docs:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build documentation
        run: ./scripts/build-docs.sh
      - name: Deploy
        run: ./scripts/deploy-docs.sh
```

**Rationale**:
- Consistent quality enforcement
- Reduced manual work
- Early issue detection
- Documentation freshness

**Consequences**:
- (+) Consistent quality
- (+) Early issue detection
- (+) Reduced manual work
- (-) CI complexity
- (-) Maintenance of automation

### Decision 6: Documentation Standards

**Decision**: Establish documentation quality standards with automated enforcement.

**Required Elements**:

| Element | Required In | Rationale |
|---------|-------------|-----------|
| Table of Contents | Docs > 100 lines | Navigation |
| Code examples | Technical docs | Clarity |
| Traceability markers | All docs | Requirement linkage |
| Diagrams | Architecture docs | Understanding |
| References | Research docs | Credibility |

**Style Guidelines**:

1. **Line Length**: Max 100 characters for code, 80 for text
2. **Headings**: Sentence case, no trailing punctuation
3. **Lists**: Use dashes for bullets, numbers for sequences
4. **Code**: Syntax highlighted, runnable examples preferred
5. **Tables**: Header separators, consistent alignment

**Linting Rules**:
```yaml
# .markdownlint.yml
line-length:
  line_length: 100
  code_blocks: false
  tables: false

no-trailing-punctuation:
  punctuation: ".,;:!"

no-inline-html:
  allowed_elements:
    - details
    - summary

heading-increment: true
first-line-heading: true
```

**Rationale**:
- Consistent reading experience
- Professional presentation
- Maintainability
- Automated enforcement

**Consequences**:
- (+) Consistent quality
- (+) Automated enforcement
- (+) Professional presentation
- (-) Learning curve
- (-) Occasional false positives

## Alternatives Considered

### Alternative 1: Per-Language Documentation Tooling

**Approach**: Each language uses its own documentation tools

**Rejection**: Fragmented experience, harder to maintain, no cross-language consistency.

### Alternative 2: Wiki-Based Documentation

**Approach**: Use GitHub Wiki or similar

**Rejection**: Harder to version with code, limited review process, less discoverable.

### Alternative 3: External Documentation Site Only

**Approach**: Documentation only on external site (GitBook, ReadTheDocs)

**Rejection**: Harder to keep synchronized, requires separate workflow, less integrated.

## Consequences Summary

### Positive

1. **Unified Experience**: Same structure across all languages
2. **Quality Enforcement**: Automated checks ensure standards
3. **Maintainability**: Living documents with clear update cycles
4. **Discoverability**: Clear hierarchy and navigation
5. **Tooling Support**: Common interface for all languages
6. **Traceability**: Clear requirement linkage

### Negative

1. **Complexity**: More structure than simple projects
2. **Overhead**: Traceability markers require discipline
3. **CI Time**: Multiple checks increase build time
4. **Learning Curve**: Standards must be learned

### Mitigations

| Concern | Mitigation |
|---------|------------|
| Complexity | Templates and examples |
| Overhead | Automated checks, IDE snippets |
| CI time | Parallel jobs, selective checks |
| Learning curve | Documentation guide, mentoring |

## Implementation Checklist

### Documentation Structure
- [x] Registry-level documents created
- [x] Language-level structure defined
- [x] Template-level guides outlined
- [ ] Full documentation for all languages
- [ ] Cross-language comparison guide

### Tooling
- [ ] Common CLI implemented
- [ ] Verification scripts created
- [ ] Generation scripts implemented
- [ ] Release automation configured
- [ ] Documentation generation working

### Automation
- [x] CI pipeline configured
- [ ] Automated checks implemented
- [ ] Documentation deployment working
- [ ] Release automation complete

## References

- [nanos Documentation](https://github.com/nanovms/nanos/tree/master/doc)
- [Documentation as Code](https://www.writethedocs.org/guide/docs-as-code/)
- [Arc42 Documentation Template](https://arc42.org/)

## Traceability

/// @trace HEXAGON-ADR-003
/// @trace HEXAGON-SPEC-003
