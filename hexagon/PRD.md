# Product Requirements Document (PRD)
# Hexagon - Unified Hexagonal Architecture Template Registry

**Version:** 1.0  
**Date:** 2026-04-05  
**Status:** Active Development  
**Author:** Hexagon Architecture Team  
**Scope:** Multi-language architecture templates  

---

## 1. Executive Summary

### 1.1 Product Overview

Hexagon is a unified template registry for hexagonal architecture implementations across seven programming languages (Go, Rust, Zig, Elixir, Kotlin, Mojo, Swift). It provides production-ready templates that embody clean architecture principles, enabling developers to build maintainable, testable applications following consistent patterns regardless of their chosen language.

**Mission Statement:**  
*Provide battle-tested, language-idiomatic hexagonal architecture templates that enable teams to build clean, maintainable applications with consistent patterns across any programming language.*

### 1.2 Key Capabilities

| Capability | Description | Status |
|------------|-------------|--------|
| Multi-Language Support | 7 language templates | Active |
| Hexagonal Architecture | Ports and Adapters pattern | Active |
| Domain-Driven Design | DDD scaffolding | Active |
| Testing Strategies | Comprehensive test templates | Active |
| CI/CD Templates | GitHub Actions, etc. | Active |
| Documentation | Full spec documentation | Active |
| Code Generation | Template generation tooling | Active |

### 1.3 Language Templates

| Language | Template Name | Status |
|----------|---------------|--------|
| Go | go-hex | Active |
| Rust | hexcore | Active |
| Zig | zig-hex | Active |
| Elixir | hex-elixir | Active |
| Kotlin | hex-kotlin | Active |
| Mojo | hex-mojo | Active |
| Swift | hex-swift | Active |

### 1.4 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Hexagon Registry                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Common Framework                         │   │
│  │   • Metadata schema   • Tooling interfaces              │   │
│  │   • Documentation     • CI/CD templates                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Language-Specific Templates                  │   │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐│   │
│  │  │ Go  │ │Rust │ │ Zig │ │Ex   │ │ Kt  │ │ Moj │ │Swift││   │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘│   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Generated Projects                       │   │
│  │           Working hexagonal implementations               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Problem Statement

### 2.1 Core Problems Addressed

#### Problem 1: Architecture Inconsistency
Teams working across multiple languages struggle to maintain consistent architectural patterns, leading to cognitive overhead when switching between codebases.

**Evidence:**
- 70% of organizations use 3+ languages
- Architecture patterns vary wildly between teams
- Context switching overhead between projects
- Code review standards inconsistent

#### Problem 2: Boilerplate Overhead
Setting up a new project with proper hexagonal architecture requires significant boilerplate code that varies by language, delaying actual feature development.

**Evidence:**
- 2-3 days to set up clean architecture skeleton
- 40% of initial code is boilerplate
- Teams copy-paste from previous projects (with errors)
- Onboarding time increases without templates

#### Problem 3: Learning Curve
Developers learning hexagonal architecture struggle to find idiomatic examples in their language, often giving up or implementing patterns incorrectly.

**Evidence:**
- Hexagonal architecture books use Java examples
- Blog posts don't cover all languages
- "Translation" of patterns leads to errors
- 60% of attempted implementations diverge from spec

#### Problem 4: Testing Complexity
Hexagonal architecture requires specific testing patterns (mock adapters, contract tests), but teams struggle to implement these consistently.

**Evidence:**
- Testing setup takes 30% of project setup time
- Inconsistent test patterns across projects
- Contract testing rarely implemented
- Integration tests flake due to poor isolation

### 2.2 Target User Pain Points

| User Type | Pain Point | Impact |
|-----------|------------|--------|
| Architect | Inconsistent patterns | Technical debt |
| Tech Lead | Boilerplate overhead | Delayed delivery |
| Developer | Learning curve | Wrong implementation |
| QA | Testing complexity | Coverage gaps |
| New Hire | No reference | Slow onboarding |

---

## 3. Target Users

### 3.1 Primary User Personas

#### Persona 1: Software Architect "Maya"
- **Demographics:** 42 years old, enterprise architect
- **Experience:** 18 years, designs multi-language systems
- **Goals:** Standardize architecture across teams
- **Pain Points:** Inconsistent patterns, hard to enforce
- **Usage Pattern:** Evaluates templates, defines standards

#### Persona 2: Tech Lead "Jordan"
- **Demographics:** 35 years old, full-stack lead
- **Experience:** 12 years, polyglot developer
- **Goals:** Bootstrap projects quickly with good architecture
- **Pain Points:** Repetitive setup, boilerplate errors
- **Usage Pattern:** Generates projects, customizes templates

#### Persona 3: Senior Developer "Alex"
- **Demographics:** 30 years old, backend specialist
- **Experience:** 8 years in one language, learning others
- **Goals:** Learn hexagonal architecture idiomatically
- **Pain Points:** Java-centric resources, poor translations
- **Usage Pattern:** Studies templates, applies patterns

#### Persona 4: Junior Developer "Taylor"
- **Demographics:** 25 years old, 2 years experience
- **Experience:** Familiar with one language, eager to learn
- **Goals:** Build production-quality code from start
- **Pain Points:** Don't know best practices
- **Usage Pattern:** Uses templates as learning resource

#### Persona 5: Consultant "Riley"
- **Demographics:** 38 years old, independent consultant
- **Experience:** 15 years across many clients and languages
- **Goals:** Deliver consistent quality across projects
- **Pain Points:** Each client uses different patterns
- **Usage Pattern:** Standardizes on Hexagon templates

### 3.2 User Needs Matrix

| Need | Maya | Jordan | Alex | Taylor | Riley |
|------|------|--------|------|--------|-------|
| Consistency | Critical | High | Medium | Low | Critical |
| Quick Setup | Medium | Critical | Medium | High | High |
| Learning Resource | Low | Medium | Critical | Critical | Medium |
| Best Practices | High | High | Critical | Critical | High |
| Customization | High | High | Medium | Low | High |
| Testing Patterns | High | High | Medium | Medium | High |

---

## 4. Functional Requirements

### 4.1 Template Generation (FR-TEMP-001 to FR-TEMP-020)

#### FR-TEMP-001: CLI Generation Tool
- Language selection
- Project name input
- Template variant selection (API, CLI, etc.)
- Output directory specification

**CLI Example:**
```bash
hexagon generate --lang go --name my-api --type api --output ./my-api
hexagon generate --lang rust --name my-cli --type cli
hexagon generate --lang zig --name embedded --type embedded
```

#### FR-TEMP-002: Template Variants
Multiple project types per language:
- API/REST service
- CLI application
- Event-driven service
- Embedded/system
- Library/package

#### FR-TEMP-003: Configuration Options
- Module naming
- Port definitions
- Adapter selections
- Dependency choices

### 4.2 Language Templates (FR-LANG-001 to FR-LANG-040)

#### FR-LANG-001: Go Template (go-hex)
- Hexagonal structure with idiomatic Go
- Interface-based ports
- Standard project layout
- Go modules support
- Testing with mocks

#### FR-LANG-002: Rust Template (hexcore)
- Trait-based ports
- Async/await support
- Workspace structure
- Cargo integration
- Testing with mockall

#### FR-LANG-003: Zig Template (zig-hex)
- Comptime configuration
- Explicit allocator passing
- Build.zig setup
- C interop support
- Minimal runtime

#### FR-LANG-004: Elixir Template (hex-elixir)
- OTP application structure
- Behaviours for ports
- GenServer adapters
- Mix project setup
- Ecto integration option

#### FR-LANG-005: Kotlin Template (hex-kotlin)
- Interface-based ports
- Coroutines support
- Gradle configuration
- Spring Boot option
- Testing with MockK

#### FR-LANG-006: Mojo Template (hex-mojo)
- Python interop
- Performance-critical paths
- Package structure
- SIMD support options
- ML integration hooks

#### FR-LANG-007: Swift Template (hex-swift)
- Protocol-based ports
- Swift Package Manager
- iOS/macOS/Linux support
- Combine/async support
- XCTest integration

### 4.3 Architecture Components (FR-ARCH-001 to FR-ARCH-020)

#### FR-ARCH-001: Domain Layer
- Entities with business logic
- Value objects
- Domain events
- Domain services
- Repository interfaces (ports)

#### FR-ARCH-002: Application Layer
- Use cases (interactors)
- DTOs
- Input/output ports
- Application services
- Transaction boundaries

#### FR-ARCH-003: Port Definitions
- Driving ports (input)
- Driven ports (output)
- Interface/trait definitions
- Port testing contracts

#### FR-ARCH-004: Adapter Implementations
- Primary adapters (driving)
- Secondary adapters (driven)
- Configuration adapters
- Testing adapters (mocks)

### 4.4 Testing Templates (FR-TEST-001 to FR-TEST-015)

#### FR-TEST-001: Unit Tests
- Domain logic tests
- Use case tests with mocked ports
- Test organization patterns

#### FR-TEST-002: Integration Tests
- Adapter integration tests
- Repository tests with test containers
- End-to-end workflow tests

#### FR-TEST-003: Contract Tests
- Port contract verification
- Consumer-driven contracts
- Breaking change detection

### 4.5 Documentation (FR-DOC-001 to FR-DOC-015)

#### FR-DOC-001: Generated Documentation
- README with architecture overview
- ADRs for template decisions
- API documentation placeholders
- Testing guide

#### FR-DOC-002: Code Comments
- Architecture pattern documentation
- Example usage in comments
- Port/adapter documentation

---

## 5. Non-Functional Requirements

### 5.1 Quality Requirements (NFR-QUAL-001 to NFR-QUAL-010)

#### NFR-QUAL-001: Code Quality
- All templates pass linters
- No compiler warnings
- Idiomatic code for each language
- Consistent formatting

#### NFR-QUAL-002: Testing Standards
- >80% test coverage
- All critical paths tested
- Integration tests included
- Example contract tests

#### NFR-QUAL-003: Documentation
- Every public API documented
- Architecture decision records
- Usage examples
- Migration guides

### 5.2 Performance (NFR-PERF-001 to NFR-PERF-010)

| Metric | Target |
|--------|--------|
| Generation time | <5 seconds |
| Template build time | Language-appropriate |
| Test execution | <30 seconds |
| Binary size | Minimal overhead |

### 5.3 Usability (NFR-USE-001 to NFR-USE-010)

- Clear error messages
- Sensible defaults
- Interactive prompts
- Verbose/quiet modes
- Color output

---

## 6. User Stories

### 6.1 Architect Stories

#### US-ARCH-001: Pattern Standardization
**As an** architect  
**I want** consistent hexagonal templates across all languages  
**So that** teams follow the same patterns

**Acceptance Criteria:**
- [ ] All templates follow ports/adapters
- [ ] Similar structure across languages
- [ ] Same terminology used
- [ ] Cross-language comparison guide

#### US-ARCH-002: DDD Scaffolding
**As an** architect  
**I want** DDD patterns built into templates  
**So that** domain-driven design is encouraged

**Acceptance Criteria:**
- [ ] Entity scaffolding
- [ ] Value object examples
- [ ] Domain event structure
- [ ] Repository pattern ready

### 6.2 Developer Stories

#### US-DEV-001: Quick Bootstrap
**As a** developer  
**I want** to generate a project in one command  
**So that** I can start coding immediately

**Acceptance Criteria:**
- [ ] Single command generation
- [ ] Working code out of the box
- [ ] Build passes immediately
- [ ] Tests pass initially

#### US-DEV-002: Learning Resource
**As a** developer learning hexagonal  
**I want** idiomatic examples in my language  
**So that** I learn correctly

**Acceptance Criteria:**
- [ ] Idiomatic code (not Java translation)
- [ ] Comments explain patterns
- [ ] Links to concepts
- [ ] Progressive complexity

---

## 7. Features

### 7.1 Core Features

#### F-CORE-001: hexagon CLI
**Description:** Command-line tool for template generation

**Commands:**
```bash
hexagon generate --help
hexagon generate --lang go --name project --type api
hexagon list-templates
hexagon validate ./my-project
hexagon update-templates
```

---

#### F-CORE-002: Template Registry
**Description:** Centralized template storage

**Structure:**
```
templates/
├── go-hex/
│   ├── api/
│   ├── cli/
│   └── service/
├── hexcore/
│   ├── api/
│   ├── cli/
│   └── library/
└── ...
```

---

### 7.2 Language-Specific Features

#### F-LANG-001: Go Template Features
- Standard Go project layout
- Interface-based ports
- Wire dependency injection (optional)
- Testify/mock for testing
- GORM/sqlx adapter examples

#### F-LANG-002: Rust Template Features
- Workspace organization
- Trait-based ports with async-trait
- Axum/Actix adapter examples
- sqlx database adapters
- Mockall for mocking

---

## 8. Metrics and Success Criteria

### 8.1 Adoption Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| GitHub stars | 5,000+ | GitHub |
| Generated projects | 10,000+ | CLI telemetry |
| Contributing projects | 50+ | Usage survey |
| Language coverage | 7 | Template count |

### 8.2 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test coverage | >80% | CI |
| Linter compliance | 100% | CI |
| Documentation | Complete | Review |
| Idiomatic score | >4/5 | User survey |

### 8.3 Usability Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Generation success | >95% | Telemetry |
| First build success | >90% | Telemetry |
| User satisfaction | >4/5 | Survey |

---

## 9. Release Criteria

### 9.1 Pre-Release Checklist

- [ ] All 7 language templates complete
- [ ] CLI tool functional
- [ ] Documentation complete
- [ ] CI/CD templates included
- [ ] Examples working

### 9.2 Per-Template Checklist

- [ ] Generates successfully
- [ ] Builds without errors
- [ ] Tests pass
- [ ] Documentation complete
- [ ] Example usage provided

### 9.3 Quality Gates

| Gate | Criteria | Owner |
|------|----------|-------|
| CI | All checks pass | Automated |
| Review | Language expert review | Domain Owner |
| Docs | Documentation complete | Docs Lead |
| Final | Approval | Product Owner |

---

## 10. Appendix

### 10.1 Hexagonal Architecture Reference

```
┌─────────────────────────────────────────┐
│           Application Core              │
│  ┌─────────────────────────────────┐   │
│  │         Domain Layer            │   │
│  │     Entities, Value Objects     │   │
│  │     Domain Events, Services     │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │      Application Layer          │   │
│  │     Use Cases, DTOs           │   │
│  │     Application Services      │   │
│  └─────────────────────────────────┘   │
│           ▲                    ▲       │
│     ┌─────┘                    └─────┐  │
│     │                                │  │
│  ┌──┴──┐                        ┌──┴──┐│
│  │Driving│                        │Driven││
│  │Adapter│                        │Adapter││
│  │(CLI,  │                        │(DB,  ││
│  │HTTP) │                        │Ext)  ││
│  └──────┘                        └──────┘│
└─────────────────────────────────────────┘
```

### 10.2 Glossary

| Term | Definition |
|------|------------|
| Port | Interface defining application boundary |
| Adapter | Implementation of a port |
| Driving | Input/primary adapter (CLI, HTTP) |
| Driven | Output/secondary adapter (DB, external) |
| Domain | Core business logic |
| Use Case | Application layer operation |
| DTO | Data Transfer Object |

### 10.4 Dependency Rule

```
┌────────────────────────────────────────────────────────────────────┐
│                    Dependency Direction                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Adapters ──▶ Ports ──▶ Core Domain ──▶ Ports ──▶ Adapters        │
│                                                                     │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐                     │
│  │  Input  │─────▶│         │      │         │                     │
│  │ Adapter │      │  Port   │─────▶│  Core   │                     │
│  └─────────┘      │Interface│      │ Domain  │                     │
│                   └─────────┘      └────┬────┘                     │
│                                         │                          │
│                   ┌─────────┐      ┌────┴────┐                     │
│  ┌─────────┐      │         │◀─────│         │                     │
│  │ Output  │◀─────│  Port   │      │         │                     │
│  │ Adapter │      │Interface│      └─────────┘                     │
│  └─────────┘      └─────────┘                                      │
│                                                                     │
│  Rule: Dependencies point INWARD to the domain core                │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### 10.5 Language-Specific Port Examples

#### Rust Port Definition
```rust
// rust/src/ports/repository.rs
#[async_trait]
pub trait Repository<T> {
    async fn find_by_id(&self, id: Uuid) -> Result<T, Error>;
    async fn save(&self, entity: T) -> Result<(), Error>;
    async fn delete(&self, id: Uuid) -> Result<(), Error>;
}
```

#### Go Port Definition
```go
// go/pkg/ports/repository.go
type Repository[T any] interface {
    FindByID(ctx context.Context, id uuid.UUID) (T, error)
    Save(ctx context.Context, entity T) error
    Delete(ctx context.Context, id uuid.UUID) error
}
```

#### TypeScript Port Definition
```typescript
// ts/src/ports/repository.ts
export interface Repository<T> {
    findById(id: string): Promise<T>;
    save(entity: T): Promise<void>;
    delete(id: string): Promise<void>;
}
```

### 10.6 Adapter Implementation Examples

#### Rust Postgres Adapter
```rust
pub struct PostgresRepository<T> {
    pool: PgPool,
    _phantom: PhantomData<T>,
}

#[async_trait]
impl Repository<Entity> for PostgresRepository<Entity> {
    async fn find_by_id(&self, id: Uuid) -> Result<Entity, Error> {
        sqlx::query_as::<_, Entity>("SELECT * FROM entities WHERE id = $1")
            .bind(id)
            .fetch_one(&self.pool)
            .await
    }
    // ...
}
```

#### Go Postgres Adapter
```go
type PostgresRepository struct {
    db *sql.DB
}

func (r *PostgresRepository) FindByID(ctx context.Context, id uuid.UUID) (Entity, error) {
    row := r.db.QueryRowContext(ctx, 
        "SELECT * FROM entities WHERE id = $1", id)
    // ...
}
```

### 10.7 Testing Strategy

#### Unit Tests (Domain)
- Test domain logic in isolation
- Mock ports using traits/interfaces
- No external dependencies
- Fast execution

#### Integration Tests (Adapters)
- Test real adapter implementations
- Use test containers for databases
- Verify port contract compliance
- Slower but comprehensive

#### Contract Tests
- Verify adapter implements port correctly
- Breaking change detection
- Consumer-driven contracts

### 10.8 CI/CD Templates

Each template includes:
- GitHub Actions workflow
- Lint checking
- Test execution
- Build verification
- Security scanning
- Documentation generation

### 10.9 Migration Path

#### From Monolith to Hexagonal
1. Identify domain boundaries
2. Extract domain logic
3. Define ports
4. Migrate adapters incrementally
5. Add tests at each step

#### Testing During Migration
- Keep existing tests running
- Add new hexagonal tests
- Gradual replacement
- No big bang rewrites

### 10.10 Quality Standards

| Language | Formatter | Linter | Test Framework |
|----------|-----------|--------|----------------|
| Rust | rustfmt | clippy | built-in |
| Go | gofmt | golangci-lint | built-in |
| TypeScript | prettier | eslint | jest/vitest |
| Python | black | ruff/mypy | pytest |
| Elixir | mix format | credo | built-in |
| Kotlin | ktlint | detekt | junit |
| Swift | swiftformat | swiftlint | xctest |

### 10.12 Design Patterns

#### Repository Pattern
```rust
// Port definition
trait Repository<T> {
    async fn find_by_id(&self, id: Uuid) -> Result<T>;
    async fn save(&self, entity: T) -> Result<()>;
    async fn delete(&self, id: Uuid) -> Result<()>;
}

// In-memory adapter (testing)
struct InMemoryRepository<T> {
    data: Arc<RwLock<HashMap<Uuid, T>>>,
}

// PostgreSQL adapter (production)
struct PostgresRepository<T> {
    pool: PgPool,
}
```

#### Unit of Work Pattern
```rust
trait UnitOfWork {
    async fn begin(&mut self) -> Result<()>;
    async fn commit(&mut self) -> Result<()>;
    async fn rollback(&mut self) -> Result<()>;
}
```

#### CQRS (Command Query Responsibility Segregation)
- Separate read and write models
- Commands modify state
- Queries return data
- Different optimization strategies

### 10.13 Documentation Standards

#### Required Documentation
- README.md with quick start
- ARCHITECTURE.md with diagrams
- API.md with interface definitions
- TESTING.md with test strategy
- DEPLOYMENT.md with ops guide

#### Code Documentation
- Every public function documented
- Examples in doc comments
- Architecture Decision Records
- Changelog maintenance

### 10.14 Version Management

#### Semantic Versioning
- MAJOR: Breaking API changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

#### Changelog Format
```markdown
## [1.2.0] - 2026-04-05
### Added
- New feature X
### Changed
- Improved Y
### Fixed
- Bug in Z
```

### 10.15 Template Customization

#### User Configuration
```yaml
# .hexagon/config.yaml
language: rust
template: api
database: postgres
ci: github-actions
docker: true
tests: true
```

#### Hooks
- Pre-generation hooks
- Post-generation hooks
- Custom file templates
- Conditional rendering

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-05 | Hexagon Team | Initial release |

**Review Schedule:** Bi-weekly during development, monthly post-release  
**Next Review:** 2026-04-19  
**Approvals Required:** Architecture Lead, Product Owner
