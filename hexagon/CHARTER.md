# hexagon Charter

## Mission Statement

hexagon provides production-ready hexagonal architecture templates across multiple programming languages, enabling software teams to build maintainable, testable applications following clean architecture principles. It bridges the gap between architectural theory and practical implementation.

Our mission is to democratize clean architecture by providing idiomatic, language-specific templates that teams can adopt immediately—eliminating the boilerplate burden while preserving architectural integrity across Go, Rust, TypeScript, Python, and more.

---

## Tenets (unless you know better ones)

These tenets guide Hexagon's template design, implementation patterns, and ecosystem evolution:

### 1. Language Idioms First

Templates must feel native to their target language. We do not impose foreign patterns that fight against language design. Each template respects and leverages language-specific features, conventions, and ecosystems.

- **Rationale**: Unidiomatic code is unmaintainable
- **Implication**: Go uses interfaces and context; Rust uses traits; Elixir uses behaviours
- **Trade-off**: Architectural purity for language harmony

### 2. Architectural Consistency

While respecting language idioms, we maintain consistent hexagonal architecture patterns across all languages. The four-layer structure (Domain, Application, Ports, Infrastructure) is present in every template.

- **Rationale**: Teams work across multiple languages
- **Implication**: Common vocabulary, predictable structure
- **Trade-off**: Language-specific optimization for cross-language consistency

### 3. Production-Ready Defaults

Templates are not starting points—they are production-ready foundations. Every template includes comprehensive error handling, testing infrastructure, CI/CD configuration, and documentation.

- **Rationale**: Templates should be deployable, not theoretical
- **Implication**: Complete implementations, not TODOs
- **Trade-off**: Template complexity for immediate usability

### 4. Evolvability Over Perfection

Templates are living artifacts that evolve with languages and practices. We prefer iterative improvement over seeking perfect initial solutions.

- **Rationale**: Languages and practices evolve
- **Implication**: Versioned releases, migration guides
- **Trade-off**: Stability for currency

### 5. Developer Experience

The measure of success is developer productivity. Templates must be discoverable, well-documented, and easy to customize.

- **Rationale**: Unused templates have no value
- **Implication**: Documentation, examples, tooling
- **Trade-off**: Template maintenance for adoption

### 6. Testability as Foundation

Every template includes comprehensive testing patterns. Testability is not an add-on; it's a design constraint.

- **Rationale**: Untested architecture is technical debt
- **Implication**: Test doubles, in-memory adapters, contract tests
- **Trade-off**: Template complexity for quality

---

## Scope & Boundaries

### In Scope

1. **Multi-Language Templates**
   - Go templates (interfaces, context propagation)
   - Rust templates (traits, zero-cost abstractions)
   - TypeScript templates (dependency injection, async/await)
   - Python templates (protocols, typing)
   - Elixir templates (behaviours, OTP)

2. **Common Tooling**
   - Code generation CLI
   - Project scaffolding
   - Linting configuration
   - Testing utilities

3. **Documentation**
   - Architecture guides
   - Language-specific patterns
   - Migration guides
   - Best practices

4. **CI/CD Integration**
   - GitHub Actions templates
   - GitLab CI templates
   - Pre-commit hooks
   - Quality gates

### Out of Scope

1. **Runtime Frameworks**
   - Application frameworks
   - Web frameworks
   - Templates integrate with frameworks

2. **Deployment Automation**
   - Kubernetes manifests
   - Terraform modules
   - May provide examples

3. **Production Monitoring**
   - Observability agents
   - APM integration
   - Templates include hooks

4. **Non-Hexagonal Patterns**
   - MVC templates
   - Layered architecture
   - Focus on ports and adapters

---

## Target Users

### Primary Users

1. **Software Architects**
   - Introducing hexagonal architecture
   - Need reference implementations
   - Require language-specific guidance

2. **Technical Leads**
   - Starting new projects
   - Need production-ready foundations
   - Require team onboarding materials

3. **Development Teams**
   - Adopting clean architecture
   - Need working examples
   - Require testing patterns

### Secondary Users

1. **Educators**
   - Teaching clean architecture
   - Need clear examples
   - Require comprehensive documentation

2. **Consultants**
   - Implementing architecture for clients
   - Need rapid scaffolding
   - Require customization guides

### User Personas

#### Persona: Alex (Software Architect)
- **Role**: Standardizing architecture across teams
- **Challenge**: 5 teams, 3 languages, inconsistent patterns
- **Goals**: Consistent hexagonal architecture
- **Pain Points**: Each team reinvents, no shared vocabulary
- **Success Criteria**: All teams use hexagon templates

#### Persona: Sarah (Tech Lead)
- **Role**: Starting new Go microservice
- **Challenge**: Need to ship in 2 weeks
- **Goals**: Production-ready foundation
- **Pain Points**: Starting from scratch, missing patterns
- **Success Criteria**: Service deployed, team productive

#### Persona: Jordan (Developer)
- **Role**: Learning hexagonal architecture
- **Challenge**: Theory understood, practice unclear
- **Goals**: Working implementation reference
- **Pain Points**: Abstract examples, no real code
- **Success Criteria**: Can explain and implement ports/adapters

---

## Success Criteria

### Quality Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Test Coverage | >90% | Per template |
| Documentation | 100% | Completeness audit |
| CI Pass | 100% | Template CI |
| Lint Clean | 100% | Language linters |

### Adoption Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Projects Generated | 10k+ | CLI telemetry |
| Languages | 5+ | Template count |
| Active Users | 1000+ | Downloads |
| Satisfaction | >4.5/5 | Survey |

### Impact Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Time to First PR | <1 week | Telemetry |
| Architecture Consistency | 90%+ | User survey |
| Test Coverage in Projects | >80% | Telemetry |

---

## Governance Model

### Project Structure

```
Maintainers (3-5)
    ├── Go Lead
    │       ├── Templates
    │       └── Tooling
    ├── Rust Lead
    │       ├── Templates
    │       └── Tooling
    ├── TypeScript Lead
    │       ├── Templates
    │       └── Tooling
    ├── Python Lead
    │       ├── Templates
    │       └── Tooling
    └── Tooling Lead
            ├── CLI
            ├── CI Templates
            └── Documentation
```

### Decision Authority

| Decision Type | Authority | Process |
|--------------|-----------|---------|
| Charter Changes | Maintainers | Consensus |
| New Language | Maintainers | RFC |
| Template Changes | Language Lead | PR Review |
| Tooling Changes | Tooling Lead | Review |

---

## Charter Compliance Checklist

### Template Quality

| Check | Method | Requirement |
|-------|--------|-------------|
| Tests | CI | >90% coverage |
| Documentation | Review | Complete |
| Idiomatic | Native review | Language-native |
| Production-Ready | Audit | No TODOs |

### Tooling Quality

| Check | Method | Requirement |
|-------|--------|-------------|
| CLI Tests | CI | >90% coverage |
| Generation | Test | Valid output |
| Docs | Review | Complete |

---

## Amendment History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-05 | Maintainers | Initial charter creation |

---

## Related Documents

- `SPEC.md` - Template specifications
- `docs/adr/` - Architecture Decision Records
- `docs/language/` - Language-specific guides

---

*This charter is a living document. Changes require maintainer consensus.*
