# Library Decomposition & Microservices Extraction Guide

A comprehensive guide for decomposing monolithic repositories into reusable libraries and microservices.

---

## Table of Contents

1. [When to Decompose](#when-to-decompose)
2. [Library vs Microservice](#library-vs-microservice)
3. [Decomposition Strategies](#decomposition-strategies)
4. [Step-by-Step Process](#step-by-step-process)
5. [Productization](#productization)
6. [Plugin Architecture](#plugin-architecture)
7. [Migration Path](#migration-path)

---

## When to Decompose

### Signs You Need Decomposition

| Signal | Threshold | Action |
|--------|-----------|--------|
| Build times | >5 min | Extract slow modules |
| Test coverage | <60% | Modularize for testing |
| Coupling | >50% cross-module deps | Identify bounded contexts |
| Team velocity | <50% of expected | Reduce coordination overhead |
| Cognitive load | >7 modules in head | Break into focused areas |

### Signs You Should NOT Decompose

| Signal | Threshold | Action |
|--------|-----------|--------|
| Team size | <5 developers | Keep simple |
| Complexity | Simple domain | Monolith is fine |
| Deployment frequency | <1/week | No microservices needed |
| Data relationships | Tightly coupled | Keep together |

---

## Library vs Microservice

### Decision Matrix

| Factor | Library | Microservice |
|--------|---------|--------------|
| Deployment | Same process | Independent |
| Data | Shared DB | Own database |
| Communication | Direct calls | Network/API |
| Transaction | ACID | Eventually consistent |
| Latency | Sub-ms | ms to seconds |
| Scaling | Vertical only | Horizontal |
| Operational cost | Low | High |

### When to Use Each

```
LIBRARY: Internal reuse, same deployment, fast paths, transaction-bound operations
MICROSERVICE: Independent deploy, different teams, different scaling, polyglot
```

---

## Decomposition Strategies

### 1. Domain-Driven Design (DDD) Bounded Contexts

```
Monolith                    -> Extract bounded contexts
+------------------+        +------------------+------------------+
| User Management  |        | User Service     | Auth Service     |
| + Orders         |   ->   +------------------+------------------+
| + Products       |        | Inventory        | Notification     |
| + Billing        |        | Service          | Service          |
+------------------+        +------------------+------------------+
```

### 2. Layer-Based Extraction

```
Extract from top to bottom:
1. Extract UI components -> Shared UI library
2. Extract domain logic -> Domain library
3. Extract data access -> Repository library
4. Extract shared infra -> Infrastructure library
```

### 3. Capability-Based Decomposition

| Capability | Type | Reason |
|------------|------|--------|
| Authentication | Library | Shared security model |
| User Management | Service | Different team ownership |
| File Storage | Library | Simple, low change |
| Email Sending | Library | Easy to test |
| Payment Processing | Service | Compliance isolation |

---

## Step-by-Step Process

### Phase 1: Analysis

```bash
# 1. Analyze dependencies
go mod graph | head -100          # Go
npm ls --all | head -50           # Node.js
cargo tree | head -100            # Rust

# 2. Find circular dependencies
go mod why <module>               # Go

# 3. Calculate coupling metrics
```

### Phase 2: Isolation

```bash
# 1. Move files to new module location
mv internal/auth pkg/auth

# 2. Create new go.mod / package.json
cd pkg/auth && go mod init pkg/auth
cd pkg/auth && npm init

# 3. Update imports
find . -name "*.go" -exec sed -i 's|internal/auth|pkg/auth|g' {}

# 4. Verify build
go build ./...
```

### Phase 3: Library Extraction

```bash
# 1. Create library repo
git subtree split --prefix=pkg/auth -b split/auth
git push git@github.com:org/auth-library split/auth

# 2. Add as dependency
go get github.com/org/auth-library@v0.1.0
npm install @org/auth-library

# 3. Create wrapper
go mod edit -replace github.com/org/auth-library=../auth-library
```

### Phase 4: Testing & Documentation

```
Library Checklist:
[ ] Unit tests cover 80%+
[ ] README with examples
[ ] API documentation
[ ] Version tagging (semver)
[ ] CHANGELOG
[ ] License
[ ] Security policy
[ ] Code of conduct
```

---

## Productization

### From Internal to Public

| Stage | Focus | Quality Bar |
|-------|-------|--------------|
| Internal | Works | Basic tests |
| Partner | Reliable | >90% tests, docs |
| Public | Usable | Full docs, examples |
| Commercial | Scalable | Performance tested |

### Product Readiness Checklist

```
[ ] API versioned (v1, v2)
[ ] Breaking change policy
[ ] Deprecation notices
[ ] Migration guides
[ ] Support channels
[ ] SLA definitions
[ ] Pricing model
[ ] Terms of service
[ ] Privacy policy (if applicable)
```

---

## Plugin Architecture

### When to Use Plugins

| Scenario | Plugin Type |
|----------|-------------|
| User extensibility | Extension plugins |
| Partner integration | Adapter plugins |
| Feature modularity | Feature plugins |
| Runtime loading | Runtime plugins |

### Plugin Patterns

```typescript
// Plugin interface (ISP - Interface Segregation)
interface Plugin {
  readonly name: string;
  readonly version: string;
  initialize(): Promise<void>;
  shutdown(): Promise<void>;
}

// Plugin manifest
interface PluginManifest {
  name: string;
  version: string;
  main: string;
  permissions: string[];
}

// Plugin registry (GRASP - Controller)
class PluginRegistry {
  private plugins = new Map<string, Plugin>();

  async register(plugin: Plugin): Promise<void>;
  async unregister(name: string): Promise<void>;
  get(name: string): Plugin | undefined;
  list(): Plugin[];
}
```

---

## Migration Path

### Strangler Fig Pattern

```
Phase 1: Wrap new around old
+------------------+    +------------------+
| Monolith         | -> | Monolith + API   |
|   /auth         |    |   /auth (proxy)  |
+------------------+    +------------------+

Phase 2: Move functionality
+------------------+    +------------------+
| Monolith         | -> | New Service      |
|   /auth (proxy)  |    |   + /auth proxy  |
+------------------+    +------------------+

Phase 3: Remove proxy
+------------------+    +------------------+
| Monolith         | -> | Monolith (clean)  |
|   /auth (gone)   |    +------------------+
+------------------+
```

---

## Code Quality Checklist

### xDD Principles Applied

| Principle | How Applied |
|-----------|-------------|
| **DRY** | Shared code in libraries |
| **KISS** | Simple module boundaries |
| **YAGNI** | Extract when needed, not before |
| **SOLID** | SRP per module, ISP for interfaces |
| **DIP** | Depend on abstractions |
| **CQRS** | Separate read/write in services |
| **HA** | Ports & adapters for flexibility |

---

## Document Metadata

- **Created**: 2026-03-25
- **Version**: 1.0
- **Source**: DinoForge Inc + AgilePlus best practices
- **See Also**: [xDD Methodologies](../reference/xDD/XDD_METHODOLOGIES.md)
