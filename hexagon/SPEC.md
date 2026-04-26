# Hexagon Specification

## Executive Summary

Hexagon is a unified template registry for hexagonal architecture implementations across seven programming languages (Go, Rust, Zig, Elixir, Kotlin, Mojo, Swift). It provides production-ready templates that embody clean architecture principles, enabling developers to build maintainable, testable applications following consistent patterns regardless of their chosen language.

**Key Capabilities:**
- Multi-language hexagonal architecture templates
- Consistent architectural patterns across languages
- Domain-driven design scaffolding
- Comprehensive testing strategies
- CI/CD integration templates
- Documentation generation
- Code generation tooling

**Target Users:**
- Software architects designing multi-language systems
- Teams adopting hexagonal architecture
- Developers learning clean architecture patterns
- Organizations standardizing on DDD practices

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Architecture Overview](#2-architecture-overview)
3. [Template Structure](#3-template-structure)
4. [Language Specifications](#4-language-specifications)
5. [Domain Layer Specification](#5-domain-layer-specification)
6. [Application Layer Specification](#6-application-layer-specification)
7. [Ports Layer Specification](#7-ports-layer-specification)
8. [Infrastructure Layer Specification](#8-infrastructure-layer-specification)
9. [Testing Specification](#9-testing-specification)
10. [Tooling Specification](#10-tooling-specification)
11. [Documentation Specification](#11-documentation-specification)
12. [CI/CD Specification](#12-cicd-specification)
13. [Security Specification](#13-security-specification)
14. [Performance Specification](#14-performance-specification)
15. [Migration Guide](#15-migration-guide)
16. [Appendices](#16-appendices)

---

## 1. Introduction

### 1.1 Purpose

This specification defines the Hexagon template registry - a comprehensive system for generating, maintaining, and evolving hexagonal architecture implementations across multiple programming languages.

### 1.2 Scope

**In Scope:**
- Template structure and organization
- Architectural patterns and conventions
- Language-specific implementations
- Testing strategies
- Tooling interfaces
- Documentation standards
- CI/CD integration

**Out of Scope:**
- Runtime framework implementation
- Deployment automation
- Production monitoring
- Runtime performance optimization

### 1.3 Definitions

| Term | Definition |
|------|------------|
| Hexagonal Architecture | Ports and Adapters pattern isolating domain logic |
| Template | Scaffolded project structure for a specific language |
| Port | Interface defining application boundaries |
| Adapter | Implementation of a port for specific technology |
| Domain | Core business logic, independent of infrastructure |
| Registry | Centralized repository for all templates |

### 1.4 References

- ADR-001: Multi-Language Template Registry Architecture
- ADR-002: Hexagonal Architecture Pattern Standardization
- ADR-003: Documentation and Tooling Strategy
- SOTA.md: State of the Art Research

---

## 2. Architecture Overview

### 2.1 System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                     Hexagon Registry                             │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Template   │  │  Template   │  │  Template   │            │
│  │    Go       │  │   Rust      │  │    Zig      │            │
│  │  (go-hex)   │  │ (hexcore)   │  │ (zig-hex)   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Template   │  │  Template   │  │  Template   │            │
│  │   Elixir    │  │   Kotlin    │  │    Mojo     │            │
│  │ (hex-elixir)│  │ (hex-kotlin)│  │ (hex-mojo)  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
│  ┌─────────────┐                                                 │
│  │  Template   │                                                 │
│  │   Swift     │                                                 │
│  │ (hex-swift) │                                                 │
│  └─────────────┘                                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Generates
                              ▼
                    ┌─────────────────┐
                    │   User Projects   │
                    │   (Any Language)  │
                    └─────────────────┘
```

### 2.2 High-Level Architecture

The Hexagon registry follows a hierarchical architecture:

**Layer 1: Registry Core**
- Common metadata schema
- Shared tooling interfaces
- Documentation framework
- CI/CD templates

**Layer 2: Language Templates**
- Language-specific scaffolding
- Idiomatic implementations
- Tooling integration
- Testing frameworks

**Layer 3: Generated Projects**
- Working hexagonal implementations
- Domain-specific customizations
- Infrastructure adapters
- Production configurations

### 2.3 Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    Hexagon Registry                             │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────┐      ┌─────────────────┐               │
│  │  Common Tools   │      │  Documentation  │               │
│  │                 │      │                 │               │
│  │ • hexagon CLI   │◄────►│ • SPEC.md       │               │
│  │ • verify.sh     │      │ • SOTA.md       │               │
│  │ • generate.sh   │      │ • ADRs          │               │
│  │ • release.sh    │      │ • Guides        │               │
│  └─────────────────┘      └─────────────────┘               │
│           │                                                    │
│           ▼                                                    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              Language Templates                       │    │
│  │                                                        │    │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │    │
│  │  │ Go  │ │Rust │ │ Zig │ │ Ex  │ │ Kt  │ │ Moj │   │    │
│  │  │     │ │     │ │     │ │     │ │     │ │     │   │    │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘   │    │
│  │                                                        │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### 2.4 Data Flow

```
User Request
    │
    ▼
┌─────────────────────┐
│   hexagon CLI       │
│   (Common entry)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Template Selection │
│  (Language, Type)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Code Generation    │
│  (Language-specific)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Generated Project  │
│  (Ready to use)     │
└─────────────────────┘
```

---

## 3. Template Structure

### 3.1 Directory Structure

All templates MUST follow this structure:

```
templates/{language}/
├── README.md                   # Language-specific quick start
├── SPEC.md                     # Detailed language spec
├── CHANGELOG.md                # Version history
├── LICENSE                     # License file
├── {build files}               # Language-specific (go.mod, Cargo.toml, etc.)
│
├── domain/                     # Domain layer (REQUIRED)
│   ├── entity.go               # Entity definitions
│   ├── value_object.go         # Value objects
│   ├── aggregate.go            # Aggregates
│   └── event.go                # Domain events
│
├── application/                # Application layer (REQUIRED)
│   ├── usecase/                # Use case implementations
│   ├── dto/                    # Data transfer objects
│   └── handler/                # Input handlers
│
├── ports/                      # Ports layer (REQUIRED)
│   ├── input_port.go           # Driving ports
│   └── output_port.go          # Driven ports
│
├── infrastructure/             # Infrastructure layer (REQUIRED)
│   ├── persistence/            # Repository implementations
│   ├── web/                    # Web adapters
│   └── external/               # External service adapters
│
├── docs/                     # Documentation
│   ├── adr/                    # Architecture decisions
│   ├── research/               # Research documents
│   └── guides/                 # User guides
│
└── tests/                      # Tests
    ├── unit/                   # Unit tests
    ├── integration/            # Integration tests
    └── e2e/                    # End-to-end tests
```

### 3.2 File Naming Conventions

**General Rules:**
- Lowercase with underscores for multi-word names
- Test files: `{name}_test.{ext}` or `test_{name}.{ext}` (language-specific)
- Documentation: UPPERCASE.md for root docs, lowercase for subdirs

**Language-Specific:**

| Language | Entity | Repository | Use Case | Test |
|----------|--------|------------|----------|------|
| Go | `user.go` | `user_repository.go` | `create_user.go` | `user_test.go` |
| Rust | `user.rs` | `user_repository.rs` | `create_user.rs` | `user_tests.rs` |
| Zig | `user.zig` | `user_repository.zig` | `create_user.zig` | `user_test.zig` |
| Elixir | `user.ex` | `user_repository.ex` | `create_user.ex` | `user_test.exs` |
| Kotlin | `User.kt` | `UserRepository.kt` | `CreateUser.kt` | `UserTest.kt` |
| Mojo | `user.mojo` | `user_repository.mojo` | `create_user.mojo` | `user_test.mojo` |
| Swift | `User.swift` | `UserRepository.swift` | `CreateUser.swift` | `UserTests.swift` |

### 3.3 Required Files

Every template MUST contain:

1. **README.md**: Quick start guide
2. **SPEC.md**: Detailed specification
3. **domain/**: At least one entity
4. **application/**: At least one use case
5. **ports/**: Input and output port definitions
6. **infrastructure/**: At least one adapter
7. **LICENSE**: Open source license
8. **CHANGELOG.md**: Version history

### 3.4 Optional Files

Templates MAY contain:

1. **Dockerfile**: Container build
2. **docker-compose.yml**: Local development
3. **.github/workflows/**: CI/CD configuration
4. **docs/**: Extended documentation
5. **scripts/**: Utility scripts
6. **Makefile**: Build automation

---

## 4. Language Specifications

### 4.1 Go Template Specification

#### 4.1.1 Module Structure

```go
// go.mod
module github.com/{organization}/{project}

go 1.22

require (
    github.com/google/uuid v1.6.0
    github.com/stretchr/testify v1.9.0
)
```

#### 4.1.2 Domain Layer

```go
// domain/entity.go
package domain

import (
    "github.com/google/uuid"
    "time"
)

type EntityID = uuid.UUID

type Entity interface {
    ID() EntityID
    CreatedAt() time.Time
    UpdatedAt() time.Time
}

// Example entity
type User struct {
    id        EntityID
    email     string
    name      string
    createdAt time.Time
    updatedAt time.Time
}

func NewUser(id EntityID, email, name string) (*User, error) {
    if email == "" {
        return nil, ErrInvalidEmail
    }
    if name == "" {
        return nil, ErrEmptyName
    }
    
    now := time.Now()
    return &User{
        id:        id,
        email:     email,
        name:      name,
        createdAt: now,
        updatedAt: now,
    }, nil
}

func (u *User) ID() EntityID        { return u.id }
func (u *User) Email() string       { return u.email }
func (u *User) Name() string        { return u.name }
func (u *User) CreatedAt() time.Time { return u.createdAt }
func (u *User) UpdatedAt() time.Time { return u.updatedAt }

func (u *User) ChangeEmail(newEmail string) error {
    if newEmail == "" {
        return ErrInvalidEmail
    }
    u.email = newEmail
    u.updatedAt = time.Now()
    return nil
}
```

#### 4.1.3 Value Objects

```go
// domain/value_object.go
package domain

type ValueObject interface {
    Equals(ValueObject) bool
    String() string
}

type Money struct {
    amount   int64  // Store as cents to avoid floating point
    currency string
}

func NewMoney(amount int64, currency string) (*Money, error) {
    if currency == "" {
        return nil, ErrInvalidCurrency
    }
    return &Money{amount: amount, currency: currency}, nil
}

func (m Money) Equals(other ValueObject) bool {
    if o, ok := other.(Money); ok {
        return m.amount == o.amount && m.currency == o.currency
    }
    return false
}

func (m Money) String() string {
    return fmt.Sprintf("%s %.2f", m.currency, float64(m.amount)/100)
}

func (m Money) Add(other Money) (Money, error) {
    if m.currency != other.currency {
        return Money{}, ErrCurrencyMismatch
    }
    return Money{amount: m.amount + other.amount, currency: m.currency}, nil
}
```

#### 4.1.4 Ports

```go
// ports/input_port.go
package ports

import "context"

// Marker interface for input ports
type InputPort interface {
    isInputPort()
}

// CommandPort for state-changing operations
type CommandPort[I, O any] interface {
    InputPort
    Execute(ctx context.Context, input I) (O, error)
}

// QueryPort for read-only operations
type QueryPort[I, O any] interface {
    InputPort
    Execute(ctx context.Context, input I) (O, error)
}
```

```go
// ports/output_port.go
package ports

import "context"

// Marker interface for output ports
type OutputPort interface {
    isOutputPort()
}

// RepositoryPort for persistence
type RepositoryPort[T any] interface {
    OutputPort
    Save(ctx context.Context, entity T) (T, error)
    FindByID(ctx context.Context, id string) (T, error)
    Delete(ctx context.Context, id string) error
    FindAll(ctx context.Context) ([]T, error)
}

// EventPort for event publishing
type EventPort interface {
    OutputPort
    Publish(ctx context.Context, event interface{}) error
}
```

#### 4.1.5 Application Layer

```go
// application/usecase/create_user.go
package usecase

import (
    "context"
    "{module}/domain"
    "{module}/ports"
)

type CreateUserInput struct {
    Email string
    Name  string
}

type CreateUserOutput struct {
    User *domain.User
}

type CreateUser struct {
    userRepo ports.RepositoryPort[*domain.User]
    eventPort ports.EventPort
}

func NewCreateUser(
    userRepo ports.RepositoryPort[*domain.User],
    eventPort ports.EventPort,
) *CreateUser {
    return &CreateUser{
        userRepo: userRepo,
        eventPort: eventPort,
    }
}

func (uc *CreateUser) Execute(ctx context.Context, input CreateUserInput) (CreateUserOutput, error) {
    user, err := domain.NewUser(
        uuid.New(),
        input.Email,
        input.Name,
    )
    if err != nil {
        return CreateUserOutput{}, err
    }

    saved, err := uc.userRepo.Save(ctx, user)
    if err != nil {
        return CreateUserOutput{}, err
    }

    _ = uc.eventPort.Publish(ctx, UserCreatedEvent{UserID: saved.ID()})

    return CreateUserOutput{User: saved}, nil
}

// Verify interface implementation
var _ ports.CommandPort[CreateUserInput, CreateUserOutput] = (*CreateUser)(nil)

func (uc *CreateUser) isInputPort() {}
```

#### 4.1.6 Infrastructure Layer

```go
// infrastructure/persistence/postgres_user_repository.go
package persistence

import (
    "context"
    "database/sql"
    "{module}/domain"
    "{module}/ports"
)

type PostgresUserRepository struct {
    db *sql.DB
}

func NewPostgresUserRepository(db *sql.DB) *PostgresUserRepository {
    return &PostgresUserRepository{db: db}
}

func (r *PostgresUserRepository) Save(ctx context.Context, user *domain.User) (*domain.User, error) {
    query := `
        INSERT INTO users (id, email, name, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (id) DO UPDATE SET
            email = $2,
            name = $3,
            updated_at = $5
        RETURNING id, email, name, created_at, updated_at
    `
    
    var result domain.User
    err := r.db.QueryRowContext(
        ctx, query,
        user.ID(), user.Email(), user.Name(),
        user.CreatedAt(), user.UpdatedAt(),
    ).Scan(&result.ID, &result.Email, &result.Name, &result.CreatedAt, &result.UpdatedAt)
    
    if err != nil {
        return nil, err
    }
    
    return &result, nil
}

func (r *PostgresUserRepository) FindByID(ctx context.Context, id string) (*domain.User, error) {
    query := `SELECT id, email, name, created_at, updated_at FROM users WHERE id = $1`
    
    var result domain.User
    err := r.db.QueryRowContext(ctx, query, id).Scan(
        &result.ID, &result.Email, &result.Name,
        &result.CreatedAt, &result.UpdatedAt,
    )
    
    if err == sql.ErrNoRows {
        return nil, domain.ErrNotFound
    }
    if err != nil {
        return nil, err
    }
    
    return &result, nil
}

func (r *PostgresUserRepository) Delete(ctx context.Context, id string) error {
    _, err := r.db.ExecContext(ctx, `DELETE FROM users WHERE id = $1`, id)
    return err
}

func (r *PostgresUserRepository) FindAll(ctx context.Context) ([]*domain.User, error) {
    rows, err := r.db.QueryContext(ctx, `SELECT id, email, name, created_at, updated_at FROM users`)
    if err != nil {
        return nil, err
    }
    defer rows.Close()
    
    var users []*domain.User
    for rows.Next() {
        var u domain.User
        if err := rows.Scan(&u.ID, &u.Email, &u.Name, &u.CreatedAt, &u.UpdatedAt); err != nil {
            return nil, err
        }
        users = append(users, &u)
    }
    
    return users, rows.Err()
}

func (r *PostgresUserRepository) isOutputPort() {}
```

### 4.2 Rust Template Specification

#### 4.2.1 Module Structure

```toml
# Cargo.toml
[package]
name = "hexcore"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1", features = ["full"] }
uuid = { version = "1", features = ["v4"] }
thiserror = "1"
async-trait = "0.1"
serde = { version = "1", features = ["derive"] }
chrono = { version = "0.4", features = ["serde"] }

[dev-dependencies]
tokio-test = "0.4"
mockall = "0.12"
```

#### 4.2.2 Domain Layer

```rust
// src/domain/mod.rs
pub mod entity;
pub mod value_object;
pub mod error;

// src/domain/entity.rs
use chrono::{DateTime, Utc};
use uuid::Uuid;
use crate::domain::error::DomainError;

pub type EntityId = Uuid;

pub trait Entity {
    fn id(&self) -> EntityId;
    fn created_at(&self) -> DateTime<Utc>;
    fn updated_at(&self) -> DateTime<Utc>;
}

pub struct User {
    id: EntityId,
    email: String,
    name: String,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

impl User {
    pub fn new(id: EntityId, email: String, name: String) -> Result<Self, DomainError> {
        if email.is_empty() {
            return Err(DomainError::InvalidEmail("email is empty".to_string()));
        }
        if name.is_empty() {
            return Err(DomainError::EmptyName);
        }
        
        let now = Utc::now();
        Ok(Self {
            id,
            email,
            name,
            created_at: now,
            updated_at: now,
        })
    }
    
    pub fn email(&self) -> &str { &self.email }
    pub fn name(&self) -> &str { &self.name }
    
    pub fn change_email(&mut self, new_email: String) -> Result<(), DomainError> {
        if new_email.is_empty() {
            return Err(DomainError::InvalidEmail("email is empty".to_string()));
        }
        self.email = new_email;
        self.updated_at = Utc::now();
        Ok(())
    }
}

impl Entity for User {
    fn id(&self) -> EntityId { self.id }
    fn created_at(&self) -> DateTime<Utc> { self.created_at }
    fn updated_at(&self) -> DateTime<Utc> { self.updated_at }
}
```

#### 4.2.3 Value Objects

```rust
// src/domain/value_object.rs
pub trait ValueObject: Clone + PartialEq + std::fmt::Display {}

#[derive(Debug, Clone, PartialEq)]
pub struct Money {
    amount: i64, // cents
    currency: String,
}

impl Money {
    pub fn new(amount: i64, currency: String) -> Result<Self, DomainError> {
        if currency.is_empty() {
            return Err(DomainError::InvalidCurrency);
        }
        Ok(Self { amount, currency })
    }
    
    pub fn add(&self, other: &Self) -> Result<Self, DomainError> {
        if self.currency != other.currency {
            return Err(DomainError::CurrencyMismatch);
        }
        Ok(Self {
            amount: self.amount + other.amount,
            currency: self.currency.clone(),
        })
    }
}

impl ValueObject for Money {}

impl std::fmt::Display for Money {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{} {:.2}", self.currency, self.amount as f64 / 100.0)
    }
}
```

#### 4.2.4 Error Handling

```rust
// src/domain/error.rs
use thiserror::Error;

#[derive(Error, Debug)]
pub enum DomainError {
    #[error("invalid email: {0}")]
    InvalidEmail(String),
    
    #[error("name cannot be empty")]
    EmptyName,
    
    #[error("invalid currency")]
    InvalidCurrency,
    
    #[error("currency mismatch")]
    CurrencyMismatch,
    
    #[error("entity not found")]
    NotFound,
    
    #[error("validation failed: {0}")]
    Validation(String),
}
```

#### 4.2.5 Ports

```rust
// src/ports/mod.rs
pub mod input;
pub mod output;

// src/ports/input.rs
use async_trait::async_trait;
use crate::domain::error::DomainError;

pub trait InputPort: Send + Sync {}

#[async_trait]
pub trait CommandPort<I, O>: InputPort {
    async fn execute(&self, input: I) -> Result<O, DomainError>;
}

#[async_trait]
pub trait QueryPort<I, O>: InputPort {
    async fn execute(&self, input: I) -> Result<O, DomainError>;
}

// src/ports/output.rs
use async_trait::async_trait;
use crate::domain::error::DomainError;

pub trait OutputPort: Send + Sync {}

#[async_trait]
pub trait RepositoryPort<T>: OutputPort {
    async fn save(&self, entity: T) -> Result<T, RepositoryError>;
    async fn find_by_id(&self, id: &str) -> Result<Option<T>, RepositoryError>;
    async fn delete(&self, id: &str) -> Result<(), RepositoryError>;
    async fn find_all(&self) -> Result<Vec<T>, RepositoryError>;
}

#[derive(Debug, thiserror::Error)]
pub enum RepositoryError {
    #[error("not found")]
    NotFound,
    #[error("database error: {0}")]
    Database(String),
}
```

#### 4.2.6 Application Layer

```rust
// src/application/usecases/create_user.rs
use async_trait::async_trait;
use crate::domain::{User, DomainError};
use crate::ports::input::{CommandPort, InputPort};
use crate::ports::output::{RepositoryPort, RepositoryError};

pub struct CreateUserInput {
    pub email: String,
    pub name: String,
}

pub struct CreateUserOutput {
    pub user: User,
}

pub struct CreateUser<R: RepositoryPort<User>> {
    user_repo: R,
}

impl<R: RepositoryPort<User>> CreateUser<R> {
    pub fn new(user_repo: R) -> Self {
        Self { user_repo }
    }
}

impl<R: RepositoryPort<User>> InputPort for CreateUser<R> {}

#[async_trait]
impl<R: RepositoryPort<User>> CommandPort<CreateUserInput, CreateUserOutput> for CreateUser<R> {
    async fn execute(&self, input: CreateUserInput) -> Result<CreateUserOutput, DomainError> {
        let user = User::new(
            uuid::Uuid::new_v4(),
            input.email,
            input.name,
        )?;
        
        let saved = self.user_repo.save(user).await
            .map_err(|e| DomainError::Validation(e.to_string()))?;
        
        Ok(CreateUserOutput { user: saved })
    }
}
```

### 4.3 Zig Template Specification

#### 4.3.1 Project Structure

```zig
// build.zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exe = b.addExecutable(.{
        .name = "zig-hex",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });

    b.installArtifact(exe);
    
    // Tests
    const unit_tests = b.addTest(.{
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });
    
    const run_unit_tests = b.addRunArtifact(unit_tests);
    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&run_unit_tests.step);
}
```

#### 4.3.2 Domain Layer

```zig
// src/domain/entity.zig
const std = @import("std");
const uuid = @import("uuid");
const Time = @import("time.zig").Time;

pub const EntityId = uuid.Uuid;

pub const Entity = struct {
    id: EntityId,
    created_at: Time,
    updated_at: Time,
    
    pub fn init(id: EntityId) Entity {
        const now = Time.now();
        return .{
            .id = id,
            .created_at = now,
            .updated_at = now,
        };
    }
    
    pub fn touch(self: *Entity) void {
        self.updated_at = Time.now();
    }
};

pub const User = struct {
    base: Entity,
    email: []const u8,
    name: []const u8,
    allocator: std.mem.Allocator,
    
    pub fn init(
        allocator: std.mem.Allocator,
        id: EntityId,
        email: []const u8,
        name: []const u8,
    ) !User {
        if (email.len == 0) return error.InvalidEmail;
        if (name.len == 0) return error.EmptyName;
        
        const email_copy = try allocator.dupe(u8, email);
        errdefer allocator.free(email_copy);
        
        const name_copy = try allocator.dupe(u8, name);
        errdefer allocator.free(name_copy);
        
        return .{
            .base = Entity.init(id),
            .email = email_copy,
            .name = name_copy,
            .allocator = allocator,
        };
    }
    
    pub fn deinit(self: *User) void {
        self.allocator.free(self.email);
        self.allocator.free(self.name);
    }
    
    pub fn changeEmail(self: *User, new_email: []const u8) !void {
        if (new_email.len == 0) return error.InvalidEmail;
        
        const new_copy = try self.allocator.dupe(u8, new_email);
        self.allocator.free(self.email);
        self.email = new_copy;
        self.base.touch();
    }
};
```

#### 4.3.3 Value Objects

```zig
// src/domain/value_object.zig
const std = @import("std");

pub const ValueObject = struct {
    equals_fn: *const fn (*const anyopaque, *const anyopaque) bool,
    toString_fn: *const fn (*const anyopaque, []u8) []const u8,
};

pub const Money = struct {
    amount: i64, // cents
    currency: []const u8,
    allocator: std.mem.Allocator,
    
    pub fn init(allocator: std.mem.Allocator, amount: i64, currency: []const u8) !Money {
        if (currency.len == 0) return error.InvalidCurrency;
        
        const currency_copy = try allocator.dupe(u8, currency);
        errdefer allocator.free(currency_copy);
        
        return .{
            .amount = amount,
            .currency = currency_copy,
            .allocator = allocator,
        };
    }
    
    pub fn deinit(self: *Money) void {
        self.allocator.free(self.currency);
    }
    
    pub fn equals(self: Money, other: Money) bool {
        return self.amount == other.amount and 
               std.mem.eql(u8, self.currency, other.currency);
    }
    
    pub fn add(self: Money, other: Money) !Money {
        if (!std.mem.eql(u8, self.currency, other.currency)) {
            return error.CurrencyMismatch;
        }
        return Money.init(self.allocator, self.amount + other.amount, self.currency);
    }
};
```

### 4.4 Elixir Template Specification

#### 4.4.1 Project Structure

```elixir
# mix.exs
defmodule HexElixir.MixProject do
  use Mix.Project

  def project do
    [
      app: :hex_elixir,
      version: "0.1.0",
      elixir: "~> 1.16",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  def application do
    [
      extra_applications: [:logger],
      mod: {HexElixir.Application, []}
    ]
  end

  defp deps do
    [
      {:ecto, "~> 3.11"},
      {:uuid, "~> 1.1"},
      {:ex_machina, "~> 2.7", only: :test}
    ]
  end
end
```

#### 4.4.2 Domain Layer

```elixir
# lib/hex_elixir/domain/user.ex
defmodule HexElixir.Domain.User do
  @moduledoc """
  User domain entity.
  """
  
  @type t :: %__MODULE__{
    id: String.t(),
    email: String.t(),
    name: String.t(),
    created_at: DateTime.t(),
    updated_at: DateTime.t()
  }
  
  defstruct [:id, :email, :name, :created_at, :updated_at]
  
  alias HexElixir.Domain.ValueObject.Email
  
  @spec new(String.t(), String.t(), String.t()) :: {:ok, t()} | {:error, atom()}
  def new(id, email, name) do
    with {:ok, valid_email} <- Email.new(email),
         :ok <- validate_name(name) do
      now = DateTime.utc_now()
      
      {:ok, %__MODULE__{
        id: id,
        email: valid_email.value,
        name: name,
        created_at: now,
        updated_at: now
      }}
    end
  end
  
  @spec change_email(t(), String.t()) :: {:ok, t()} | {:error, atom()}
  def change_email(user, new_email) do
    case Email.new(new_email) do
      {:ok, valid_email} ->
        {:ok, %{user | 
          email: valid_email.value,
          updated_at: DateTime.utc_now()
        }}
        
      {:error, _} = error ->
        error
    end
  end
  
  defp validate_name(name) when is_binary(name) and byte_size(name) > 0, do: :ok
  defp validate_name(_), do: {:error, :empty_name}
end
```

#### 4.4.3 Ports

```elixir
# lib/hex_elixir/ports/user_repository.ex
defmodule HexElixir.Ports.UserRepository do
  @moduledoc """
  User repository port (behaviour).
  """
  
  alias HexElixir.Domain.User
  
  @callback save(user :: User.t()) :: {:ok, User.t()} | {:error, term()}
  @callback find_by_id(id :: String.t()) :: {:ok, User.t()} | {:error, :not_found}
  @callback delete(id :: String.t()) :: :ok | {:error, term()}
  @callback list_all() :: {:ok, [User.t()]} | {:error, term()}
end
```

#### 4.4.4 Application Layer

```elixir
# lib/hex_elixir/application/use_cases/create_user.ex
defmodule HexElixir.Application.UseCases.CreateUser do
  @moduledoc """
  Create user use case.
  """
  
  alias HexElixir.Domain.User
  alias HexElixir.Ports.UserRepository
  
  @type input :: %{
    email: String.t(),
    name: String.t()
  }
  
  @type output :: {:ok, User.t()} | {:error, term()}
  
  @spec execute(module(), input()) :: output()
  def execute(repo, %{email: email, name: name}) do
    id = UUID.uuid4()
    
    with {:ok, user} <- User.new(id, email, name),
         {:ok, saved} <- repo.save(user) do
      {:ok, saved}
    end
  end
end
```

### 4.5 Kotlin Template Specification

#### 4.5.1 Project Structure

```kotlin
// build.gradle.kts
plugins {
    kotlin("jvm") version "1.9.22"
    id("org.jetbrains.kotlinx.kover") version "0.7.5"
}

group = "com.phenotype"
version = "0.1.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("com.github.f4b6a3:uuid-creator:5.3.7")
    
    testImplementation(kotlin("test"))
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
}

tasks.test {
    useJUnitPlatform()
}

kotlin {
    jvmToolchain(17)
}
```

#### 4.5.2 Domain Layer

```kotlin
// src/main/kotlin/domain/User.kt
package domain

import java.time.Instant
import java.util.UUID

class User private constructor(
    val id: UUID,
    val email: String,
    val name: String,
    val createdAt: Instant,
    val updatedAt: Instant
) {
    companion object {
        fun create(id: UUID, email: String, name: String): Result<User> {
            if (email.isBlank()) {
                return Result.failure(DomainError.InvalidEmail("email is blank"))
            }
            if (name.isBlank()) {
                return Result.failure(DomainError.EmptyName)
            }
            
            val now = Instant.now()
            return Result.success(User(id, email, name, now, now))
        }
    }
    
    fun changeEmail(newEmail: String): Result<User> {
        if (newEmail.isBlank()) {
            return Result.failure(DomainError.InvalidEmail("email is blank"))
        }
        
        return Result.success(User(
            id = id,
            email = newEmail,
            name = name,
            createdAt = createdAt,
            updatedAt = Instant.now()
        ))
    }
}

// src/main/kotlin/domain/DomainError.kt
package domain

sealed class DomainError : Exception() {
    data class InvalidEmail(val reason: String) : DomainError()
    object EmptyName : DomainError()
    data class Validation(val message: String) : DomainError()
    object NotFound : DomainError()
}
```

#### 4.5.3 Value Objects

```kotlin
// src/main/kotlin/domain/Money.kt
package domain

import java.math.BigDecimal

data class Money private constructor(
    val amount: BigDecimal,
    val currency: Currency
) {
    companion object {
        fun of(amount: BigDecimal, currency: Currency): Result<Money> {
            return Result.success(Money(amount, currency))
        }
    }
    
    fun add(other: Money): Result<Money> {
        if (currency != other.currency) {
            return Result.failure(DomainError.Validation("currency mismatch"))
        }
        return Result.success(Money(amount + other.amount, currency))
    }
    
    override fun toString(): String = "$currency $amount"
}

enum class Currency {
    USD, EUR, GBP, JPY
}
```

#### 4.5.4 Ports

```kotlin
// src/main/kotlin/ports/InputPort.kt
package ports

interface InputPort

interface CommandPort<I, O> : InputPort {
    suspend fun execute(input: I): Result<O>
}

interface QueryPort<I, O> : InputPort {
    suspend fun execute(input: I): Result<O>
}

// src/main/kotlin/ports/OutputPort.kt
package ports

import domain.User

interface OutputPort

interface UserRepository : OutputPort {
    suspend fun save(user: User): Result<User>
    suspend fun findById(id: String): Result<User>
    suspend fun delete(id: String): Result<Unit>
    suspend fun findAll(): Result<List<User>>
}
```

### 4.6 Mojo Template Specification

#### 4.6.1 Project Structure

```mojo
# src/domain/entity.mojo
from memory import UnsafePointer
from utils import StringSlice

struct EntityID:
    var value: String
    
    fn __init__(inout self, value: String):
        self.value = value

struct Time:
    var timestamp: Int64
    
    fn __init__(inout self):
        self.timestamp = 0  # Placeholder for current time
    
    @staticmethod
    fn now() -> Self:
        return Self()

struct Entity:
    var id: EntityID
    var created_at: Time
    var updated_at: Time
    
    fn __init__(inout self, id: EntityID):
        self.id = id
        self.created_at = Time.now()
        self.updated_at = Time.now()
    
    fn touch(inout self):
        self.updated_at = Time.now()

struct User:
    var entity: Entity
    var email: String
    var name: String
    
    fn __init__(inout self, id: EntityID, email: String, name: String) raises:
        if len(email) == 0:
            raise Error("InvalidEmail")
        if len(name) == 0:
            raise Error("EmptyName")
        
        self.entity = Entity(id)
        self.email = email
        self.name = name
    
    fn change_email(inout self, new_email: String) raises:
        if len(new_email) == 0:
            raise Error("InvalidEmail")
        self.email = new_email
        self.entity.touch()
```

### 4.7 Swift Template Specification

#### 4.7.1 Project Structure

```swift
// Package.swift
// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "HexSwift",
    platforms: [.macOS(.v13), .iOS(.v16)],
    products: [
        .library(name: "HexSwift", targets: ["HexSwift"]),
    ],
    dependencies: [
        .package(url: "https://github.com/vapor/fluent.git", from: "4.8.0"),
    ],
    targets: [
        .target(
            name: "HexSwift",
            dependencies: [
                .product(name: "Fluent", package: "fluent"),
            ]
        ),
        .testTarget(
            name: "HexSwiftTests",
            dependencies: ["HexSwift"]
        ),
    ]
)
```

#### 4.7.2 Domain Layer

```swift
// Sources/HexSwift/Domain/User.swift
import Foundation

public struct User: Entity {
    public let id: UUID
    public let email: String
    public let name: String
    public let createdAt: Date
    public private(set) var updatedAt: Date
    
    public init(id: UUID, email: String, name: String) throws {
        guard !email.isEmpty else {
            throw DomainError.invalidEmail("email is empty")
        }
        guard !name.isEmpty else {
            throw DomainError.emptyName
        }
        
        self.id = id
        self.email = email
        self.name = name
        self.createdAt = Date()
        self.updatedAt = Date()
    }
    
    public mutating func changeEmail(_ newEmail: String) throws {
        guard !newEmail.isEmpty else {
            throw DomainError.invalidEmail("email is empty")
        }
        self.email = newEmail
        self.updatedAt = Date()
    }
}

public protocol Entity: Identifiable {
    var id: UUID { get }
    var createdAt: Date { get }
    var updatedAt: Date { get }
}

public enum DomainError: Error {
    case invalidEmail(String)
    case emptyName
    case notFound
    case validation(String)
}
```

#### 4.7.3 Value Objects

```swift
// Sources/HexSwift/Domain/Money.swift
import Foundation

public struct Money: ValueObject, Equatable {
    public let amount: Decimal
    public let currency: Currency
    
    public init(amount: Decimal, currency: Currency) throws {
        self.amount = amount
        self.currency = currency
    }
    
    public func add(_ other: Money) throws -> Money {
        guard currency == other.currency else {
            throw DomainError.validation("currency mismatch")
        }
        return try Money(amount: amount + other.amount, currency: currency)
    }
    
    public var description: String {
        return "\(currency) \(amount)"
    }
}

public enum Currency: String, CaseIterable {
    case usd = "USD"
    case eur = "EUR"
    case gbp = "GBP"
}

public protocol ValueObject: CustomStringConvertible, Equatable {}
```

#### 4.7.4 Ports

```swift
// Sources/HexSwift/Ports/InputPort.swift
public protocol InputPort {}

public protocol CommandPort<Input, Output>: InputPort {
    associatedtype Input
    associatedtype Output
    
    func execute(_ input: Input) async throws -> Output
}

public protocol QueryPort<Input, Output>: InputPort {
    associatedtype Input
    associatedtype Output
    
    func execute(_ input: Input) async throws -> Output
}

// Sources/HexSwift/Ports/OutputPort.swift
public protocol OutputPort {}

public protocol RepositoryPort<Entity>: OutputPort {
    associatedtype Entity
    
    func save(_ entity: Entity) async throws -> Entity
    func findByID(_ id: String) async throws -> Entity
    func delete(_ id: String) async throws
    func findAll() async throws -> [Entity]
}
```

---

## 5. Domain Layer Specification

### 5.1 Domain Layer Responsibilities

The domain layer contains pure business logic with no external dependencies:

1. **Entity Management**: Define and manage domain entities
2. **Value Objects**: Immutable objects compared by value
3. **Domain Events**: Events representing significant occurrences
4. **Business Rules**: Invariants and validation logic
5. **Domain Services**: Complex operations not fitting entities

### 5.2 Entity Requirements

All entities MUST:

| Requirement | Description | Verification |
|-------------|-------------|--------------|
| Identity | Unique identifier | `ID()` method/property |
| Lifecycle | Creation and modification rules | Constructor validation |
| Equality | Based on identity, not attributes | `Equals()` implementation |
| Immutability | Controlled mutation via methods | No direct field access |
| Validation | Self-validating construction | Panic/Error on invalid |

### 5.3 Value Object Requirements

All value objects MUST:

| Requirement | Description | Example |
|-------------|-------------|---------|
| No identity | No unique identifier | Money, Email, Address |
| Immutability | Cannot change after creation | Copy-on-write pattern |
| Value equality | Equal if attributes equal | `Equals()` by value |
| Side-effect free | Operations return new instances | `Add()` returns new VO |
| Validation | Self-validating | Constructor validation |

### 5.4 Domain Event Specification

```go
// Go example
type DomainEvent interface {
    EventType() string
    OccurredAt() time.Time
    AggregateID() EntityID
}

type UserCreatedEvent struct {
    eventType   string
    occurredAt  time.Time
    aggregateID EntityID
    email       string
}

func NewUserCreatedEvent(userID EntityID, email string) *UserCreatedEvent {
    return &UserCreatedEvent{
        eventType:   "UserCreated",
        occurredAt:  time.Now(),
        aggregateID: userID,
        email:       email,
    }
}

func (e *UserCreatedEvent) EventType() string    { return e.eventType }
func (e *UserCreatedEvent) OccurredAt() time.Time { return e.occurredAt }
func (e *UserCreatedEvent) AggregateID() EntityID  { return e.aggregateID }
```

---

## 6. Application Layer Specification

### 6.1 Application Layer Responsibilities

1. **Use Case Orchestration**: Coordinate domain objects
2. **Transaction Management**: Handle units of work
3. **DTO Mapping**: Convert between domain and external formats
4. **Authorization**: Check permissions
5. **Event Publishing**: Emit domain events

### 6.2 Use Case Structure

All use cases MUST follow this structure:

```go
type {Action}{Entity} struct {
    // Dependencies (ports)
}

type {Action}{Entity}Input struct {
    // Input fields
}

type {Action}{Entity}Output struct {
    // Output fields
}

func (uc *{Action}{Entity}) Execute(ctx context.Context, input {Action}{Entity}Input) ({Action}{Entity}Output, error) {
    // 1. Validate input
    // 2. Retrieve domain objects
    // 3. Execute business logic
    // 4. Persist changes
    // 5. Publish events
    // 6. Return result
}
```

### 6.3 Command vs Query

| Aspect | Command | Query |
|--------|---------|-------|
| Purpose | Change state | Read state |
| Side effects | Yes | No |
| Return | Result or error | Data or error |
| Naming | Imperative (Create, Update, Delete) | Interrogative (Get, Find, List) |

### 6.4 DTO Specification

DTOs MUST:
- Be serializable
- Contain no business logic
- Be language-idiomatic (struct/class/data class)
- Use primitive types or other DTOs

---

## 7. Ports Layer Specification

### 7.1 Port Categories

**Input Ports (Driving):**
- Receive external input
- Triggered by user actions or external systems
- Implemented by application layer

**Output Ports (Driven):**
- Define infrastructure requirements
- Implemented by infrastructure layer
- Triggered by application layer

### 7.2 Port Interface Requirements

All ports MUST:
- Define clear contracts
- Use domain types in signatures
- Be technology-agnostic
- Enable test doubles

### 7.3 Common Port Patterns

**Repository Port:**
```go
type RepositoryPort[T any] interface {
    OutputPort
    Save(ctx context.Context, entity T) (T, error)
    FindByID(ctx context.Context, id string) (T, error)
    Delete(ctx context.Context, id string) error
    FindAll(ctx context.Context) ([]T, error)
}
```

**Event Port:**
```go
type EventPort interface {
    OutputPort
    Publish(ctx context.Context, event DomainEvent) error
}
```

**Cache Port:**
```go
type CachePort[T any] interface {
    OutputPort
    Get(ctx context.Context, key string) (T, error)
    Set(ctx context.Context, key string, value T, ttl time.Duration) error
    Delete(ctx context.Context, key string) error
}
```

---

## 8. Infrastructure Layer Specification

### 8.1 Infrastructure Layer Responsibilities

1. **Technology Implementation**: Concrete implementations of ports
2. **External Integration**: Database, API, messaging
3. **Framework Integration**: Web frameworks, ORMs
4. **Configuration**: Environment-specific settings

### 8.2 Adapter Requirements

All adapters MUST:
- Implement exactly one port interface
- Not leak framework details to domain
- Handle technology-specific errors
- Be replaceable without domain changes

### 8.3 Common Adapter Patterns

**Repository Adapter:**
```go
type PostgresUserRepository struct {
    db *sql.DB
    // No domain logic here
}

func (r *PostgresUserRepository) Save(ctx context.Context, user *domain.User) (*domain.User, error) {
    // PostgreSQL-specific implementation
    // Map domain errors to repository errors
}
```

**Web Adapter:**
```go
type UserHandler struct {
    createUser *application.CreateUser
    // Other use cases
}

func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
    // Parse HTTP request
    // Call use case
    // Format HTTP response
}
```

---

## 9. Testing Specification

### 9.1 Testing Strategy

**Test Pyramid:**
```
         ▲
        /_\        E2E Tests (5%)
       /___\       Slow, comprehensive
      /_____\     
     /_______\    Integration Tests (15%)
    /_________\   Medium speed, external deps
   /___________\
  /_____________\ Unit Tests (80%)
                   Fast, isolated
```

### 9.2 Unit Testing

**Domain Tests:**
```go
func TestUser_ChangeEmail(t *testing.T) {
    // Arrange
    user, _ := domain.NewUser(uuid.New(), "old@example.com", "John")
    
    // Act
    err := user.ChangeEmail("new@example.com")
    
    // Assert
    assert.NoError(t, err)
    assert.Equal(t, "new@example.com", user.Email())
}
```

**Use Case Tests (with mocks):**
```go
func TestCreateUser_Execute(t *testing.T) {
    // Arrange
    mockRepo := new(MockUserRepository)
    mockEvents := new(MockEventPort)
    uc := NewCreateUser(mockRepo, mockEvents)
    
    mockRepo.On("Save", mock.Anything, mock.Anything).Return(&domain.User{}, nil)
    
    // Act
    _, err := uc.Execute(context.Background(), CreateUserInput{...})
    
    // Assert
    assert.NoError(t, err)
    mockRepo.AssertExpectations(t)
}
```

### 9.3 Integration Testing

```go
func TestPostgresUserRepository_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }
    
    // Setup test container
    ctx := context.Background()
    container := SetupPostgresContainer(t)
    defer container.Terminate(ctx)
    
    db := container.GetDB()
    repo := NewPostgresUserRepository(db)
    
    // Test actual database operations
    user, _ := domain.NewUser(uuid.New(), "test@example.com", "Test")
    saved, err := repo.Save(ctx, user)
    
    require.NoError(t, err)
    assert.Equal(t, user.ID(), saved.ID())
}
```

### 9.4 E2E Testing

```go
func TestUserWorkflow_E2E(t *testing.T) {
    // Setup full application
    app := SetupTestApplication(t)
    
    // Execute workflow
    resp := app.Post("/users", CreateUserRequest{Email: "test@example.com", Name: "Test"})
    assert.Equal(t, 201, resp.StatusCode)
    
    // Verify through GET
    created := ParseJSON(resp.Body)
    getResp := app.Get("/users/" + created.ID)
    assert.Equal(t, 200, getResp.StatusCode)
}
```

---

## 10. Tooling Specification

### 10.1 Hexagon CLI

**Command Structure:**
```bash
hexagon [global-options] <command> [command-options] [arguments]

Commands:
  generate    Generate code from templates
  verify      Verify template structure
  test        Run template tests
  lint        Lint template code
  release     Release a new version
  docs        Generate documentation
  init        Initialize new template
```

**Generate Command:**
```bash
hexagon generate entity --name User --language go
hexagon generate usecase --action Create --entity User --language rust
hexagon generate adapter --port Repository --technology Postgres --language go
```

**Verify Command:**
```bash
hexagon verify templates/go/
hexagon verify --language rust
hexagon verify --all
```

### 10.2 Code Generation Templates

**Entity Template (Go):**
```gotemplate
// domain/{{.name | lower}}.go
package domain

import (
    "github.com/google/uuid"
    "time"
)

type {{.name}}ID = uuid.UUID

type {{.name}} struct {
    id        {{.name}}ID
    {{- range .fields }}
    {{.name}} {{.type}}
    {{- end }}
    createdAt time.Time
    updatedAt time.Time
}

func New{{.name}}(id {{.name}}ID{{range .fields}}, {{.name}} {{.type}}{{end}}) (*{{.name}}, error) {
    // Validation
    now := time.Now()
    return &{{.name}}{
        id:        id,
        {{- range .fields }}
        {{.name}}: {{.name}},
        {{- end }}
        createdAt: now,
        updatedAt: now,
    }, nil
}

func (e *{{.name}}) ID() {{.name}}ID { return e.id }
{{- range .fields }}
func (e *{{.name}}) {{.name | title}}() {{.type}} { return e.{{.name}} }
{{- end }}
```

---

## 11. Documentation Specification

### 11.1 Required Documentation

| Document | Location | Audience | Min Length |
|----------|----------|----------|------------|
| README.md | Root | Users | 100 lines |
| SPEC.md | Root | Developers | 500 lines |
| ADRs | docs/adr/ | Architects | 50 lines each |
| SOTA.md | docs/research/ | Architects | 300 lines |

### 11.2 Documentation Standards

1. **UTF-8 encoding** only
2. **No smart quotes** or special characters
3. **Markdown format** with tables
4. **Traceability markers** on all docs
5. **Code examples** for technical content
6. **Diagrams** for architecture

### 11.3 Traceability Format

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

---

## 12. CI/CD Specification

### 12.1 GitHub Actions Workflow

```yaml
name: Hexagon CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify structure
        run: ./scripts/verify.sh
      - name: Check traceability
        run: ./scripts/check-traceability.sh

  test:
    strategy:
      matrix:
        language: [go, rust, zig, elixir, kotlin, mojo, swift]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup ${{ matrix.language }}
        uses: ./.github/actions/setup-${{ matrix.language }}
      - name: Test ${{ matrix.language }}
        run: ./scripts/test.sh ${{ matrix.language }}

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint documentation
        run: ./scripts/lint-docs.sh
```

### 12.2 Release Process

1. Version bump in CHANGELOG.md
2. Tag with semantic version
3. Generate release notes
4. Build artifacts
5. Publish to registries

---

## 13. Security Specification

### 13.1 Security Requirements

1. **Dependency scanning** in CI
2. **Secret detection** in commits
3. **SBOM generation** for releases
4. **Vulnerability disclosure** process

### 13.2 Template Security

- No hardcoded secrets in templates
- Secure defaults in generated code
- Input validation examples
- OWASP Top 10 coverage

---

## 14. Performance Specification

### 14.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Code generation | < 1s | Template instantiation |
| Compilation | Language-specific | Clean build |
| Test execution | < 30s | Unit test suite |
| Memory overhead | < 10% | vs non-hexagonal |

### 14.2 Optimization Guidelines

- Interface dispatch awareness
- Allocation minimization in hot paths
- Lazy initialization patterns
- Caching strategies

---

## 15. Migration Guide

### 15.1 From Separate Repositories

1. Identify templates to merge
2. Create subtree merge plan
3. Execute merges preserving history
4. Update documentation
5. Archive old repositories

### 15.2 Template Updates

1. Update hexagon.yaml metadata
2. Refresh dependencies
3. Run verification
4. Update CHANGELOG
5. Tag release

---

## 16. Appendices

### Appendix A: Language Feature Matrix

| Feature | Go | Rust | Zig | Elixir | Kotlin | Mojo | Swift |
|---------|-----|------|-----|--------|--------|------|-------|
| Generics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Interfaces | ✅ | Traits | Vtable | Behaviours | Interfaces | Structs | Protocols |
| Async | ✅ | ✅ | ❌ | ✅ | ✅ | ⚠️ | ✅ |
| Null safety | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Pattern matching | ⚠️ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ |

### Appendix B: Template Variable Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `project_name` | Project identifier | `my-service` |
| `organization` | GitHub/org | `phenotype` |
| `language` | Target language | `go` |
| `include_tests` | Test scaffolding | `true` |
| `license` | SPDX license | `MIT` |

### Appendix C: Glossary

| Term | Definition |
|------|------------|
| Hexagonal Architecture | Ports and Adapters pattern |
| Domain | Core business logic |
| Port | Interface defining boundary |
| Adapter | Port implementation |
| Entity | Object with identity |
| Value Object | Immutable, value-compared |
| Aggregate | Consistency boundary |

---

## Document Information

**Version:** 1.0  
**Last Updated:** 2026-04-04  
**Author:** Phenotype Architecture Team  
**Status:** Draft  

**Traceability:**
- /// @trace HEXAGON-SPEC-001
- /// @trace HEXAGON-ADR-001
- /// @trace HEXAGON-ADR-002
- /// @trace HEXAGON-ADR-003

---

*This specification is part of the Hexagon project - a unified template registry for hexagonal architecture across multiple programming languages.*

---

## Additional Implementation Patterns

### 17. Transaction Management

#### 17.1 Unit of Work Pattern

The Unit of Work pattern maintains a list of objects affected by a business transaction and coordinates the writing out of changes.

**Go Implementation:**
```go
// ports/output_port.go
type UnitOfWork interface {
    OutputPort
    RegisterNew(entity Entity)
    RegisterDirty(entity Entity)
    RegisterDeleted(entity Entity)
    Commit(ctx context.Context) error
    Rollback() error
}

// infrastructure/persistence/unit_of_work.go
type SQLUnitOfWork struct {
    db       *sql.DB
    tx       *sql.Tx
    new      []Entity
    dirty    []Entity
    deleted  []string
}

func (u *SQLUnitOfWork) Commit(ctx context.Context) error {
    tx, err := u.db.BeginTx(ctx, nil)
    if err != nil {
        return err
    }
    
    // Insert new entities
    for _, entity := range u.new {
        if err := u.insert(tx, entity); err != nil {
            tx.Rollback()
            return err
        }
    }
    
    // Update dirty entities
    for _, entity := range u.dirty {
        if err := u.update(tx, entity); err != nil {
            tx.Rollback()
            return err
        }
    }
    
    // Delete entities
    for _, id := range u.deleted {
        if err := u.delete(tx, id); err != nil {
            tx.Rollback()
            return err
        }
    }
    
    return tx.Commit()
}
```

**Rust Implementation:**
```rust
// src/ports/output.rs
#[async_trait]
pub trait UnitOfWork: OutputPort {
    async fn register_new(&mut self, entity: &dyn Entity);
    async fn register_dirty(&mut self, entity: &dyn Entity);
    async fn register_deleted(&mut self, id: &str);
    async fn commit(&mut self) -> Result<(), RepositoryError>;
    async fn rollback(&mut self) -> Result<(), RepositoryError>;
}
```

### 17.2 Saga Pattern

For distributed transactions, the Saga pattern coordinates multiple local transactions.

```go
// application/saga/order_saga.go
type OrderSaga struct {
    steps []SagaStep
    compensations []SagaStep
}

type SagaStep func(ctx context.Context) error

func (s *OrderSaga) Execute(ctx context.Context) error {
    completed := 0
    
    for i, step := range s.steps {
        if err := step(ctx); err != nil {
            // Compensate completed steps
            for j := completed - 1; j >= 0; j-- {
                s.compensations[j](ctx)
            }
            return err
        }
        completed = i + 1
    }
    
    return nil
}
```

### 18. Caching Strategies

#### 18.1 Cache-Aside Pattern

```go
// infrastructure/cache/redis_cache.go
type RedisCachePort[T any] struct {
    client *redis.Client
    ttl    time.Duration
}

func (c *RedisCachePort[T]) Get(ctx context.Context, key string) (T, error) {
    var result T
    data, err := c.client.Get(ctx, key).Result()
    if err == redis.Nil {
        return result, ErrCacheMiss
    }
    if err != nil {
        return result, err
    }
    
    err = json.Unmarshal([]byte(data), &result)
    return result, err
}

func (c *RedisCachePort[T]) Set(ctx context.Context, key string, value T) error {
    data, err := json.Marshal(value)
    if err != nil {
        return err
    }
    return c.client.Set(ctx, key, data, c.ttl).Err()
}
```

#### 18.2 Cache Invalidation Strategies

| Strategy | Use Case | Implementation |
|----------|----------|----------------|
| TTL | Predictable lifetime | Redis EXPIRE |
| Write-through | Strong consistency | Update cache on write |
| Write-behind | High write throughput | Queue cache updates |
| Event-based | Complex dependencies | Listen to domain events |

### 19. Event Sourcing

#### 19.1 Event Store

```go
// domain/event_store.go
type EventStore interface {
    Append(ctx context.Context, streamID string, events []DomainEvent, expectedVersion int) error
    Read(ctx context.Context, streamID string, fromVersion int) ([]DomainEvent, error)
    GetAllStreams(ctx context.Context) ([]string, error)
}

// infrastructure/event_store/postgres_event_store.go
type PostgresEventStore struct {
    db *sql.DB
}

func (s *PostgresEventStore) Append(ctx context.Context, streamID string, events []DomainEvent, expectedVersion int) error {
    return withTransaction(ctx, s.db, func(tx *sql.Tx) error {
        // Optimistic concurrency check
        var currentVersion int
        err := tx.QueryRowContext(ctx,
            "SELECT version FROM streams WHERE id = $1 FOR UPDATE",
            streamID,
        ).Scan(&currentVersion)
        
        if err == sql.ErrNoRows {
            currentVersion = 0
        } else if err != nil {
            return err
        }
        
        if currentVersion != expectedVersion {
            return ErrConcurrencyConflict
        }
        
        // Append events
        for _, event := range events {
            _, err := tx.ExecContext(ctx,
                `INSERT INTO events (stream_id, type, data, version, occurred_at)
                 VALUES ($1, $2, $3, $4, $5)`,
                streamID, event.EventType(), event.Data(), currentVersion+1, event.OccurredAt(),
            )
            if err != nil {
                return err
            }
            currentVersion++
        }
        
        // Update stream version
        _, err = tx.ExecContext(ctx,
            `INSERT INTO streams (id, version) VALUES ($1, $2)
             ON CONFLICT (id) DO UPDATE SET version = $2`,
            streamID, currentVersion,
        )
        return err
    })
}
```

#### 19.2 Projection Rebuilding

```go
// application/projections/order_projection.go
type OrderProjection struct {
    eventStore EventStore
    readModel  OrderReadModel
}

func (p *OrderProjection) Rebuild(ctx context.Context) error {
    streams, err := p.eventStore.GetAllStreams(ctx)
    if err != nil {
        return err
    }
    
    for _, streamID := range streams {
        events, err := p.eventStore.Read(ctx, streamID, 0)
        if err != nil {
            return err
        }
        
        order := NewOrderAggregate(streamID)
        for _, event := range events {
            order.Apply(event)
        }
        
        if err := p.readModel.Save(ctx, order.ToReadModel()); err != nil {
            return err
        }
    }
    
    return nil
}
```

### 20. API Design Patterns

#### 20.1 RESTful API Conventions

**URL Structure:**
```
GET    /v1/{resources}          # List all
GET    /v1/{resources}/{id}    # Get one
POST   /v1/{resources}          # Create
PUT    /v1/{resources}/{id}    # Full update
PATCH  /v1/{resources}/{id}    # Partial update
DELETE /v1/{resources}/{id}    # Delete
```

**Response Envelope:**
```go
type APIResponse[T any] struct {
    Data       T              `json:"data,omitempty"`
    Error      *APIError      `json:"error,omitempty"`
    Pagination *Pagination    `json:"pagination,omitempty"`
    Meta       map[string]any `json:"meta,omitempty"`
}

type APIError struct {
    Code    string `json:"code"`
    Message string `json:"message"`
    Details string `json:"details,omitempty"`
}

type Pagination struct {
    Page      int `json:"page"`
    PageSize  int `json:"page_size"`
    Total     int `json:"total"`
    TotalPages int `json:"total_pages"`
}
```

#### 20.2 GraphQL Integration

```go
// infrastructure/graphql/resolver.go
type Resolver struct {
    userRepo ports.RepositoryPort[*domain.User]
}

func (r *Resolver) User(ctx context.Context, args struct{ ID string }) (*UserResolver, error) {
    user, err := r.userRepo.FindByID(ctx, args.ID)
    if err != nil {
        return nil, err
    }
    return &UserResolver{user: user}, nil
}

type UserResolver struct {
    user *domain.User
}

func (r *UserResolver) ID() string      { return r.user.ID().String() }
func (r *UserResolver) Email() string   { return r.user.Email() }
func (r *UserResolver) Name() string    { return r.user.Name() }
```

### 21. Observability

#### 21.1 Structured Logging

```go
// infrastructure/logging/structured_logger.go
type StructuredLogger struct {
    logger *slog.Logger
}

func (l *StructuredLogger) LogOperation(ctx context.Context, operation string, fields ...LogField) {
    attrs := []slog.Attr{
        slog.String("operation", operation),
        slog.String("trace_id", trace.GetTraceID(ctx)),
    }
    
    for _, field := range fields {
        attrs = append(attrs, slog.Any(field.Key, field.Value))
    }
    
    l.logger.LogAttrs(ctx, slog.LevelInfo, "operation", attrs...)
}
```

#### 21.2 Metrics

```go
// infrastructure/metrics/prometheus_metrics.go
type PrometheusMetrics struct {
    requestDuration *prometheus.HistogramVec
    requestCount    *prometheus.CounterVec
    errorCount      *prometheus.CounterVec
}

func (m *PrometheusMetrics) RecordRequest(ctx context.Context, method, path string, duration time.Duration, status int) {
    labels := []string{method, path, strconv.Itoa(status)}
    m.requestDuration.WithLabelValues(labels...).Observe(duration.Seconds())
    m.requestCount.WithLabelValues(labels...).Inc()
    
    if status >= 400 {
        m.errorCount.WithLabelValues(labels...).Inc()
    }
}
```

### 22. Configuration Management

#### 22.1 Environment-Based Configuration

```go
// infrastructure/config/config.go
type Config struct {
    Database   DatabaseConfig
    Server     ServerConfig
    Cache      CacheConfig
    Observability ObservabilityConfig
}

type DatabaseConfig struct {
    Host     string `env:"DB_HOST" default:"localhost"`
    Port     int    `env:"DB_PORT" default:"5432"`
    User     string `env:"DB_USER" required:"true"`
    Password string `env:"DB_PASSWORD" required:"true"`
    Database string `env:"DB_NAME" required:"true"`
    SSLMode  string `env:"DB_SSL_MODE" default:"disable"`
}

func Load() (*Config, error) {
    var cfg Config
    if err := envconfig.Process("", &cfg); err != nil {
        return nil, err
    }
    return &cfg, nil
}
```

### 23. Testing Patterns

#### 23.1 Contract Testing

```go
// tests/contract/user_repository_test.go
type RepositoryContractTest struct {
    repo RepositoryPort[*domain.User]
}

func (t *RepositoryContractTest) TestSaveAndFind(t *testing.T) {
    ctx := context.Background()
    user, _ := domain.NewUser(uuid.New(), "test@example.com", "Test")
    
    saved, err := t.repo.Save(ctx, user)
    require.NoError(t, err)
    
    found, err := t.repo.FindByID(ctx, saved.ID().String())
    require.NoError(t, err)
    assert.Equal(t, saved.ID(), found.ID())
}

func (t *RepositoryContractTest) TestNotFound(t *testing.T) {
    ctx := context.Background()
    _, err := t.repo.FindByID(ctx, "non-existent")
    assert.ErrorIs(t, err, domain.ErrNotFound)
}
```

#### 23.2 Property-Based Testing

```go
// tests/property/user_properties_test.go
func TestUserProperties(t *testing.T) {
    parameters := gopter.DefaultTestParameters()
    parameters.MinSuccessfulTests = 100
    
    properties := gopter.NewProperties(parameters)
    
    properties.Property("user ID is unique", prop.ForAll(
        func(id uuid.UUID, email, name string) bool {
            user1, _ := domain.NewUser(id, email, name)
            user2, _ := domain.NewUser(id, email, name)
            return user1.ID() == user2.ID()
        },
        gen.UUID(),
        gen.AlphaString(),
        gen.AlphaString(),
    ))
    
    properties.TestingRun(t)
}
```

### 24. Deployment Patterns

#### 24.1 Container Configuration

```dockerfile
# Dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o server ./cmd/server

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/server .
EXPOSE 8080
CMD ["./server"]
```

#### 24.2 Health Checks

```go
// infrastructure/health/health_check.go
type HealthChecker struct {
    checks map[string]HealthCheck
}

type HealthCheck func(ctx context.Context) error

func (h *HealthChecker) Register(name string, check HealthCheck) {
    h.checks[name] = check
}

func (h *HealthChecker) Check(ctx context.Context) HealthStatus {
    status := HealthStatus{
        Status:    "healthy",
        Checks:    make(map[string]CheckResult),
        Timestamp: time.Now(),
    }
    
    for name, check := range h.checks {
        if err := check(ctx); err != nil {
            status.Status = "unhealthy"
            status.Checks[name] = CheckResult{Status: "unhealthy", Error: err.Error()}
        } else {
            status.Checks[name] = CheckResult{Status: "healthy"}
        }
    }
    
    return status
}
```

### 25. Advanced Domain Patterns

#### 25.1 Specification Pattern

```go
// domain/specification.go
type Specification interface {
    IsSatisfiedBy(entity Entity) bool
    And(other Specification) Specification
    Or(other Specification) Specification
    Not() Specification
}

type UserActiveSpec struct{}

func (s UserActiveSpec) IsSatisfiedBy(entity Entity) bool {
    if user, ok := entity.(*User); ok {
        return user.IsActive()
    }
    return false
}

// Usage
activeUsers := repo.FindBySpec(ctx, UserActiveSpec{})
```

#### 25.2 Policy Pattern

```go
// domain/policy.go
type DiscountPolicy interface {
    CalculateDiscount(order *Order) (Money, error)
}

type PercentageDiscount struct {
    Percentage float64
}

func (p PercentageDiscount) CalculateDiscount(order *Order) (Money, error) {
    total := order.Total()
    discountAmount := float64(total.Amount()) * p.Percentage / 100
    return MoneyFrom(int64(discountAmount), total.Currency())
}

type BulkDiscount struct {
    MinimumQuantity int
    DiscountPercent float64
}

func (b BulkDiscount) CalculateDiscount(order *Order) (Money, error) {
    if order.ItemCount() < b.MinimumQuantity {
        return MoneyZero(order.Total().Currency()), nil
    }
    // Apply discount
}
```

### Appendix D: Migration Examples

#### From Layered to Hexagonal

**Before (Layered):**
```go
// Layered approach with database in business logic
func ProcessOrder(orderID string) error {
    db := getDB()
    row := db.QueryRow("SELECT * FROM orders WHERE id = ?", orderID)
    // Process directly with DB
}
```

**After (Hexagonal):**
```go
// Domain - pure business logic
func (o *Order) Process() error {
    if o.Status != StatusPending {
        return ErrInvalidStatus
    }
    o.Status = StatusProcessing
    return nil
}

// Application - orchestration
type ProcessOrderUseCase struct {
    orderRepo RepositoryPort[*Order]
}

func (uc *ProcessOrderUseCase) Execute(ctx context.Context, orderID string) error {
    order, err := uc.orderRepo.FindByID(ctx, orderID)
    if err != nil {
        return err
    }
    
    if err := order.Process(); err != nil {
        return err
    }
    
    _, err = uc.orderRepo.Save(ctx, order)
    return err
}

// Infrastructure - technology specific
type PostgresOrderRepository struct {
    db *sql.DB
}
```

### Appendix E: Code Generation Templates

#### Entity Generator

```yaml
# generator/entity.yaml
name: entity
parameters:
  - name: entity_name
    type: string
    required: true
  - name: fields
    type: array
    required: true
  - name: language
    type: string
    required: true

templates:
  go: |
    package domain
    
    type {{.entity_name}} struct {
      id EntityID
      {{range .fields}}{{.name}} {{.type}}
      {{end}}
      createdAt time.Time
      updatedAt time.Time
    }
    
    func New{{.entity_name}}(id EntityID{{range .fields}}, {{.name}} {{.type}}{{end}}) (*{{.entity_name}}, error) {
      // Validation
      return &{{.entity_name}}{
        id: id,
        {{range .fields}}{{.name}}: {{.name}},
        {{end}}
        createdAt: time.Now(),
        updatedAt: time.Now(),
      }, nil
    }
  
  rust: |
    pub struct {{.entity_name}} {
      id: EntityId,
      {{range .fields}}{{.name}}: {{.type}},
      {{end}}
      created_at: DateTime<Utc>,
      updated_at: DateTime<Utc>,
    }
```

---

## Document Information

**Version:** 1.0  
**Last Updated:** 2026-04-04  
**Author:** Phenotype Architecture Team  
**Status:** Draft  

**Traceability:**
- /// @trace HEXAGON-SPEC-001
- /// @trace HEXAGON-ADR-001
- /// @trace HEXAGON-ADR-002
- /// @trace HEXAGON-ADR-003

---

*This specification is part of the Hexagon project - a unified template registry for hexagonal architecture across multiple programming languages.*
