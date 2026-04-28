# Hierarchical Scoping System

The Pheno SDK's Hierarchical Scoping System provides deeply composable credential management with unlimited nesting levels, allowing organizations to structure their credential access in a way that mirrors their organizational hierarchy.

## Table of Contents

- [Overview](#overview)
- [Scope Types](#scope-types)
- [Hierarchy Structure](#hierarchy-structure)
- [Scope Resolution](#scope-resolution)
- [Creating Hierarchies](#creating-hierarchies)
- [Scope Templates](#scope-templates)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

The hierarchical scoping system allows you to organize credentials in a tree-like structure where:

- **Global** credentials are available to all projects
- **Group/Org/Program/Portfolio** credentials are available to their children
- **Project** credentials are specific to individual projects
- **Environment** credentials are specific to deployment environments
- **User** credentials are specific to individual users

This creates a natural fallback chain where credentials are resolved by walking up the hierarchy tree.

## Scope Types

### Core Scope Types

```python
from pheno.credentials.hierarchy import ScopeType

# Available scope types
ScopeType.GLOBAL        # Available everywhere
ScopeType.GROUP         # Organization-level grouping
ScopeType.ORG           # Organization-specific
ScopeType.PROGRAM       # Program-level
ScopeType.PORTFOLIO     # Portfolio-level
ScopeType.PROJECT       # Project-specific
ScopeType.ENVIRONMENT   # Environment-specific (dev, staging, prod)
ScopeType.USER          # User-specific
```

### Scope Hierarchy

The natural hierarchy order (from most specific to most general):

```
USER
├── ENVIRONMENT
│   └── PROJECT
│       └── PORTFOLIO
│           └── PROGRAM
│               └── ORG
│                   └── GROUP
│                       └── GLOBAL
```

## Hierarchy Structure

### ScopeNode

Each node in the hierarchy is represented by a `ScopeNode`:

```python
from pheno.credentials.hierarchy import ScopeNode, ScopeType

node = ScopeNode(
    name="atoms",
    type=ScopeType.ORG,
    path="atoms",
    parent_id=None,  # Root node
    description="ATOMS organization"
)
```

### ScopeHierarchy

A complete hierarchy is managed by a `ScopeHierarchy`:

```python
from pheno.credentials.hierarchy import ScopeHierarchy

hierarchy = ScopeHierarchy(
    name="enterprise",
    description="Enterprise-wide credential hierarchy",
    nodes={
        global_node.id: global_node,
        org_node.id: org_node,
        # ... more nodes
    },
    root_node_id=global_node.id
)
```

## Scope Resolution

### Resolution Order

When resolving a credential, the system follows this order:

1. **User scope** (most specific)
2. **Environment scope**
3. **Project scope**
4. **Portfolio scope**
5. **Program scope**
6. **Org scope**
7. **Group scope**
8. **Global scope** (least specific)

### Example Resolution

```python
# Given this hierarchy:
# global
# └── atoms (org)
#     └── platform (group)
#         └── ai-ml (program)
#             └── llm-ops (portfolio)
#                 └── krouter (project)
#                     └── production (environment)

# Resolving API_KEY for scope path "atoms/platform/ai-ml/llm-ops/krouter/production"
# Will check in this order:
# 1. production environment scope
# 2. krouter project scope
# 3. llm-ops portfolio scope
# 4. ai-ml program scope
# 5. platform group scope
# 6. atoms org scope
# 7. global scope
```

## Creating Hierarchies

### Using ScopeBuilder

The `ScopeBuilder` provides a fluent API for creating hierarchies:

```python
from pheno.credentials.hierarchy import ScopeBuilder

builder = ScopeBuilder("enterprise")
builder.add_global("global", "Global credentials")
builder.add_org("atoms", "ATOMS organization")
builder.add_group("platform", "Platform team", parent_path="atoms")
builder.add_program("ai-ml", "AI/ML program", parent_path="atoms/platform")
builder.add_portfolio("llm-ops", "LLM Operations portfolio", parent_path="atoms/platform/ai-ml")
builder.add_project("krouter", "KRouter project", parent_path="atoms/platform/ai-ml/llm-ops")
builder.add_environment("production", "Production environment", parent_path="atoms/platform/ai-ml/llm-ops/krouter")

hierarchy = builder.build()
```

### Manual Creation

```python
from pheno.credentials.hierarchy import ScopeHierarchy, ScopeNode, ScopeType

# Create nodes
global_node = ScopeNode("global", ScopeType.GLOBAL, "global")
org_node = ScopeNode("atoms", ScopeType.ORG, "atoms", parent_id=global_node.id)
group_node = ScopeNode("platform", ScopeType.GROUP, "atoms/platform", parent_id=org_node.id)
project_node = ScopeNode("krouter", ScopeType.PROJECT, "atoms/platform/krouter", parent_id=group_node.id)

# Create hierarchy
hierarchy = ScopeHierarchy(
    name="enterprise",
    nodes={
        global_node.id: global_node,
        org_node.id: org_node,
        group_node.id: group_node,
        project_node.id: project_node,
    },
    root_node_id=global_node.id
)
```

## Scope Templates

### Enterprise Template

```python
from pheno.credentials.hierarchy import ScopeTemplate

# Create enterprise hierarchy
enterprise = ScopeTemplate.create_enterprise_hierarchy("atoms")
hierarchy = enterprise.build()

# This creates:
# global
# └── atoms (org)
#     ├── engineering (group)
#     │   ├── platform (program)
#     │   └── data (program)
#     ├── product (group)
#     │   ├── frontend (program)
#     │   └── backend (program)
#     └── operations (group)
#         ├── devops (program)
#         └── security (program)
```

### Development Template

```python
# Create development hierarchy
dev = ScopeTemplate.create_development_hierarchy("atoms")
hierarchy = dev.build()

# This creates:
# global
# └── atoms (org)
#     ├── development (group)
#     │   ├── local (environment)
#     │   ├── testing (environment)
#     │   └── staging (environment)
#     └── production (group)
#         └── production (environment)
```

### Team Template

```python
# Create team hierarchy
team = ScopeTemplate.create_team_hierarchy("atoms", "platform-team")
hierarchy = team.build()

# This creates:
# global
# └── atoms (org)
#     └── platform-team (group)
#         ├── frontend (project)
#         ├── backend (project)
#         └── infrastructure (project)
```

## API Reference

### ScopeBuilder

```python
class ScopeBuilder:
    def __init__(self, name: str):
        """Initialize scope builder."""
    
    def add_global(self, name: str, description: str = None) -> 'ScopeBuilder':
        """Add global scope."""
    
    def add_org(self, name: str, parent_path: str = None, description: str = None) -> 'ScopeBuilder':
        """Add organization scope."""
    
    def add_group(self, name: str, parent_path: str = None, description: str = None) -> 'ScopeBuilder':
        """Add group scope."""
    
    def add_program(self, name: str, parent_path: str = None, description: str = None) -> 'ScopeBuilder':
        """Add program scope."""
    
    def add_portfolio(self, name: str, parent_path: str = None, description: str = None) -> 'ScopeBuilder':
        """Add portfolio scope."""
    
    def add_project(self, name: str, parent_path: str = None, description: str = None) -> 'ScopeBuilder':
        """Add project scope."""
    
    def add_environment(self, name: str, parent_path: str = None, description: str = None) -> 'ScopeBuilder':
        """Add environment scope."""
    
    def add_user(self, name: str, parent_path: str = None, description: str = None) -> 'ScopeBuilder':
        """Add user scope."""
    
    def build(self) -> ScopeHierarchy:
        """Build the hierarchy."""
```

### ScopeHierarchy

```python
class ScopeHierarchy:
    def __init__(self, name: str, nodes: Dict[UUID, ScopeNode]):
        """Initialize hierarchy."""
    
    def add_node(self, node: ScopeNode) -> bool:
        """Add a node to the hierarchy."""
    
    def remove_node(self, node_id: UUID) -> bool:
        """Remove a node from the hierarchy."""
    
    def get_node(self, node_id: UUID) -> Optional[ScopeNode]:
        """Get a node by ID."""
    
    def get_node_by_path(self, path: str) -> Optional[ScopeNode]:
        """Get a node by path."""
    
    def get_children(self, node_id: UUID) -> List[ScopeNode]:
        """Get child nodes."""
    
    def get_ancestors(self, node_id: UUID) -> List[ScopeNode]:
        """Get ancestor nodes."""
    
    def get_descendants(self, node_id: UUID) -> List[ScopeNode]:
        """Get descendant nodes."""
    
    def get_path(self, node_id: UUID) -> str:
        """Get full path for a node."""
    
    def validate(self) -> bool:
        """Validate hierarchy structure."""
    
    def get_stats(self) -> Dict[str, Any]:
        """Get hierarchy statistics."""
```

### ScopeNode

```python
class ScopeNode:
    def __init__(self, name: str, type: ScopeType, path: str, 
                 parent_id: Optional[UUID] = None, **kwargs):
        """Initialize scope node."""
    
    def get_full_path(self) -> str:
        """Get full hierarchical path."""
    
    def is_ancestor_of(self, other: 'ScopeNode') -> bool:
        """Check if this node is an ancestor of another."""
    
    def is_descendant_of(self, other: 'ScopeNode') -> bool:
        """Check if this node is a descendant of another."""
    
    def get_ancestors(self, hierarchy: 'ScopeHierarchy') -> List['ScopeNode']:
        """Get all ancestor nodes."""
    
    def get_descendants(self, hierarchy: 'ScopeHierarchy') -> List['ScopeNode']:
        """Get all descendant nodes."""
```

## Best Practices

### 1. Design Your Hierarchy

Before creating a hierarchy, design it on paper:

```
global
└── your-org (org)
    ├── engineering (group)
    │   ├── platform (program)
    │   │   ├── frontend (portfolio)
    │   │   │   ├── web-app (project)
    │   │   │   └── mobile-app (project)
    │   │   └── backend (portfolio)
    │   │       ├── api (project)
    │   │       └── workers (project)
    │   └── data (program)
    │       └── analytics (portfolio)
    │           └── dashboards (project)
    └── product (group)
        └── user-experience (program)
            └── design-system (project)
```

### 2. Use Meaningful Names

```python
# Good
builder.add_org("atoms", "ATOMS organization")
builder.add_group("platform-engineering", "Platform Engineering team")
builder.add_project("krouter", "KRouter API Gateway")

# Bad
builder.add_org("org1", "Organization 1")
builder.add_group("team1", "Team 1")
builder.add_project("proj1", "Project 1")
```

### 3. Keep Hierarchies Shallow

While the system supports unlimited nesting, keep hierarchies shallow for better performance:

```python
# Good (3-4 levels deep)
global -> org -> group -> project

# Avoid (too deep)
global -> org -> group -> program -> portfolio -> project -> environment -> user
```

### 4. Use Environment Scopes

Use environment scopes for deployment-specific credentials:

```python
# Production credentials
builder.add_environment("production", "Production environment", parent_path="atoms/platform/krouter")

# Staging credentials
builder.add_environment("staging", "Staging environment", parent_path="atoms/platform/krouter")

# Development credentials
builder.add_environment("development", "Development environment", parent_path="atoms/platform/krouter")
```

### 5. Document Your Hierarchy

```python
# Add descriptions to nodes
builder.add_org("atoms", "ATOMS organization - Main development organization")
builder.add_group("platform", "Platform team - Core platform services", parent_path="atoms")
builder.add_project("krouter", "KRouter - API Gateway and routing service", parent_path="atoms/platform")
```

## Examples

### Complete Enterprise Setup

```python
from pheno.credentials import CredentialBroker
from pheno.credentials.hierarchy import ScopeBuilder

# Initialize broker
broker = CredentialBroker()

# Create enterprise hierarchy
builder = ScopeBuilder("enterprise")
builder.add_global("global", "Global credentials available to all projects")
builder.add_org("atoms", "ATOMS organization")
builder.add_group("engineering", "Engineering team", parent_path="atoms")
builder.add_program("platform", "Platform services program", parent_path="atoms/engineering")
builder.add_portfolio("api-gateway", "API Gateway portfolio", parent_path="atoms/engineering/platform")
builder.add_project("krouter", "KRouter API Gateway", parent_path="atoms/engineering/platform/api-gateway")
builder.add_environment("production", "Production environment", parent_path="atoms/engineering/platform/api-gateway/krouter")
builder.add_environment("staging", "Staging environment", parent_path="atoms/engineering/platform/api-gateway/krouter")
builder.add_environment("development", "Development environment", parent_path="atoms/engineering/platform/api-gateway/krouter")

hierarchy = builder.build()
broker.create_hierarchy("enterprise", hierarchy)

# Store credentials at different scopes
broker.create_scope_credential("GLOBAL_API_KEY", "global-key", "global", "secret", "enterprise")
broker.create_scope_credential("ORG_API_KEY", "org-key", "atoms", "secret", "enterprise")
broker.create_scope_credential("GROUP_API_KEY", "group-key", "atoms/engineering", "secret", "enterprise")
broker.create_scope_credential("PROGRAM_API_KEY", "program-key", "atoms/engineering/platform", "secret", "enterprise")
broker.create_scope_credential("PORTFOLIO_API_KEY", "portfolio-key", "atoms/engineering/platform/api-gateway", "secret", "enterprise")
broker.create_scope_credential("PROJECT_API_KEY", "project-key", "atoms/engineering/platform/api-gateway/krouter", "secret", "enterprise")
broker.create_scope_credential("PROD_API_KEY", "prod-key", "atoms/engineering/platform/api-gateway/krouter/production", "secret", "enterprise")

# Resolve credentials
# This will return "prod-key" (most specific)
prod_key = broker.resolve_credential_hierarchical("PROD_API_KEY", "atoms/engineering/platform/api-gateway/krouter/production", "enterprise")

# This will return "project-key" (falls back to project level)
project_key = broker.resolve_credential_hierarchical("PROJECT_API_KEY", "atoms/engineering/platform/api-gateway/krouter/staging", "enterprise")

# This will return "global-key" (falls back to global level)
global_key = broker.resolve_credential_hierarchical("GLOBAL_API_KEY", "atoms/engineering/platform/api-gateway/krouter/development", "enterprise")
```

### CLI Usage

```bash
# Create hierarchy
pheno-cli hierarchy create enterprise --description "Enterprise hierarchy"

# Show hierarchy tree
pheno-cli hierarchy show enterprise

# Create scope credentials
pheno-cli scope create GLOBAL_API_KEY "global-key" global --type secret --hierarchy enterprise
pheno-cli scope create PROJECT_API_KEY "project-key" atoms/engineering/platform/api-gateway/krouter --type secret --hierarchy enterprise

# List credentials for a scope
pheno-cli scope list atoms/engineering/platform/api-gateway/krouter --hierarchy enterprise

# Resolve credential
pheno-cli scope resolve PROJECT_API_KEY atoms/engineering/platform/api-gateway/krouter --hierarchy enterprise

# Show scope statistics
pheno-cli scope stats --hierarchy enterprise
```

### Integration with Existing Projects

```python
# In your application
from pheno.credentials import CredentialBroker

broker = CredentialBroker()

# Resolve credentials for current project
project_path = "atoms/engineering/platform/api-gateway/krouter"
api_key = broker.resolve_credential_hierarchical("API_KEY", project_path, "enterprise")
database_url = broker.resolve_credential_hierarchical("DATABASE_URL", project_path, "enterprise")

# Use in your application
import httpx
response = httpx.get("https://api.example.com/data", headers={"Authorization": f"Bearer {api_key}"})
```

This hierarchical scoping system provides the flexibility and power needed for complex organizational structures while maintaining simplicity for basic use cases.