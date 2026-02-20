# Atomic Trace Architecture: Complete System Design

**Date**: 2025-11-20
**Version**: 2.0 (Atomic Integration)
**Status**: Comprehensive Design

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [The Atomic Vision](#the-atomic-vision)
3. [Complete Data Model](#complete-data-model)
4. [Integration with 16-View System](#integration-with-16-view-system)
5. [Cascading Update Mechanism](#cascading-update-mechanism)
6. [Toggle/Flag System](#toggle-flag-system)
7. [Graph Query Patterns](#graph-query-patterns)
8. [Intelligent CRUD](#intelligent-crud)
9. [Event Sourcing Integration](#event-sourcing-integration)
10. [Performance Optimization](#performance-optimization)
11. [API Design](#api-design)
12. [Implementation Examples](#implementation-examples)

---

## Executive Summary

The **Atomic Trace Architecture** extends the trace multi-view PM system with **hyper-granular atomic decomposition**, enabling unprecedented flexibility and composability:

**Core Innovation**:
```
FR-001: [User] can [login] with [email/password] via [main website]
         ↓       ↓            ↓                       ↓
      Subject Action      Method                Interface

Each bracket [] is a swappable, first-class entity with:
- Representation in all 16 views
- Cascading updates when changed
- Implementation variant toggles (auth0 vs authkit)
- Future implementation flags
```

**Key Capabilities**:
1. **Atomic Decomposition**: Requirements broken into swappable atoms
2. **Multi-View Consistency**: Changes cascade across all 16 views
3. **Runtime Configuration**: Feature flags activate/deactivate atoms
4. **Intelligent Scaffolding**: Auto-generate Code, Test, API views from requirements
5. **Event-Sourced History**: Complete audit trail with time-travel
6. **Graph Traceability**: Impact analysis via recursive queries

**Technology Integration**:
- **Existing**: 16 views, Git-style versioning, NATS coordination, OpenSpec workflow
- **New**: Atomic entities, feature flags (Unleash), NLP validation (IntentGuard), cascading updates

---

## The Atomic Vision

### Conceptual Model

**Traditional Requirement** (monolithic):
```
FR-001: User can login with email and password via the main website
```

**Atomic Requirement** (decomposed):
```
FR-001: [{atom:subject:user}] can [{atom:action:login}]
        with [{atom:method:email-password}]
        via [{atom:interface:main-website}]

Atoms:
  - subject:user (swappable: user → agent → system → api-client)
  - action:login (swappable: login → logout → register → verify)
  - method:email-password (swappable: email-pass → oauth2 → saml → sso → biometric)
  - interface:main-website (swappable: web → mobile-app → cli → api → desktop)

Implementation Variants:
  - auth_provider: auth0 | authkit | custom (toggle if implemented, flag if not)
  - session_storage: redis | postgresql | memory (toggle)
  - mfa_enabled: true | false (feature flag)
```

**Benefits of Atomic Approach**:
1. **Composability**: Swap atoms to create variations (100s of configs from 10s of atoms)
2. **Reusability**: Atoms shared across requirements (auth atoms used in login, register, verify)
3. **Impact Analysis**: Change atom → instantly see all affected requirements
4. **Progressive Enhancement**: Start minimal, add atoms incrementally
5. **A/B Testing**: Toggle atoms to test variants (oauth2 vs saml)

### Atomic Hierarchy

```
Level 0: ATOM (capability primitive)
  ├─ Subject Atoms: user, agent, system, api-client, admin
  ├─ Action Atoms: create, read, update, delete, login, logout, verify, approve
  ├─ Method Atoms: email-password, oauth2, saml, api-key, jwt, session-cookie
  └─ Interface Atoms: web-ui, mobile-app, rest-api, cli, graphql-api, grpc

Level 1: MOLECULE (feature composition, 2-5 atoms)
  ├─ User Authentication: [user] + [login] + [email-password] + [web-ui]
  ├─ API Access: [api-client] + [read] + [api-key] + [rest-api]
  └─ Admin Panel: [admin] + [approve] + [session-cookie] + [web-ui]

Level 2: ORGANISM (epic composition, 3-10 molecules)
  ├─ User Management: Authentication + Profile + Permissions
  ├─ Payment Processing: Cart + Checkout + Receipt + Refund
  └─ Analytics Dashboard: Data Collection + Visualization + Export

Level 3: TEMPLATE (bounded context, reusable pattern)
  ├─ SaaS Multi-Tenant: User Mgmt + Billing + Analytics + Admin
  ├─ E-Commerce Platform: Catalog + Cart + Payment + Shipping
  └─ Content Management: Authoring + Publishing + Media + SEO

Level 4: PRODUCT (concrete configuration, template + flags)
  ├─ B2B SaaS: SaaS Multi-Tenant + [sso] + [api-access] + [audit-logs]
  ├─ B2C E-Commerce: E-Commerce + [oauth2] + [payment-stripe]
  └─ Enterprise CMS: CMS + [saml] + [ldap] + [on-prem-deployment]
```

**Atom Count Estimate**:
- Subject atoms: ~20 (user, agent, system, admin, guest, ...)
- Action atoms: ~50 (CRUD + domain-specific: approve, cancel, ship, ...)
- Method atoms: ~30 (auth methods, protocols, formats, ...)
- Interface atoms: ~15 (web, mobile, API types, ...)

**Total**: ~115 atoms → 1000s of possible molecule combinations

---

## Complete Data Model

### Core Entities

#### 1. Atom Entity

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Dict
from uuid import UUID, uuid4

class AtomType(Enum):
    """Four fundamental atom types."""
    SUBJECT = "subject"      # Who/what performs (user, agent, system)
    ACTION = "action"        # What is done (login, create, approve)
    METHOD = "method"        # How it's done (oauth2, api-key, email)
    INTERFACE = "interface"  # Where/through what (web, mobile, api)

class AtomScope(Enum):
    """Scope/domain of atom."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_STORAGE = "data_storage"
    API_ACCESS = "api_access"
    USER_INTERFACE = "user_interface"
    NOTIFICATION = "notification"
    PAYMENT = "payment"
    ANALYTICS = "analytics"
    CONTENT = "content"
    SEARCH = "search"
    # ... extensible

@dataclass
class Atom:
    """Smallest decomposable capability unit.

    Represents a single, swappable concept like [User], [login], [oauth2], [web-ui].
    Atoms are reusable across multiple requirements.

    Example:
        >>> auth_atom = Atom(
        ...     id=uuid4(),
        ...     type=AtomType.METHOD,
        ...     value="oauth2",
        ...     label="OAuth 2.0 Authentication",
        ...     scope=AtomScope.AUTHENTICATION
        ... )
    """

    id: UUID
    type: AtomType
    value: str  # Unique identifier (slug): "oauth2", "user", "web-ui"
    label: str  # Human-readable: "OAuth 2.0 Authentication"
    description: str  # Detailed explanation
    scope: AtomScope  # Domain classification

    # Semantic relationships
    synonyms: List[str] = field(default_factory=list)  # ["oauth", "oauth2.0"]
    antonyms: List[str] = field(default_factory=list)  # "login" ↔ "logout"
    related: List[UUID] = field(default_factory=list)  # Related atoms

    # Composition rules
    compatible_with: Dict[AtomType, List[UUID]] = field(default_factory=dict)
    conflicts_with: List[UUID] = field(default_factory=list)
    requires: List[UUID] = field(default_factory=list)  # Prerequisite atoms

    # Implementation status
    implementations: List[str] = field(default_factory=list)  # ["auth0", "authkit"]
    default_implementation: Optional[str] = None

    # Metadata
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "type": self.type.value,
            "value": self.value,
            "label": self.label,
            "description": self.description,
            "scope": self.scope.value,
            "synonyms": self.synonyms,
            "antonyms": self.antonyms,
            "related": [str(r) for r in self.related],
            "compatible_with": {
                k.value: [str(v) for v in vals]
                for k, vals in self.compatible_with.items()
            },
            "conflicts_with": [str(c) for c in self.conflicts_with],
            "implementations": self.implementations,
            "default_implementation": self.default_implementation,
            "tags": self.tags,
        }

#### 2. Atomic Requirement Entity

```python
@dataclass
class AtomicRequirement:
    """Requirement composed of atomic parameters.

    Represents a parameterized requirement where each component is swappable.

    Example:
        >>> req = AtomicRequirement(
        ...     id="FR-001",
        ...     template="[{subject}] can [{action}] with [{method}] via [{interface}]",
        ...     atoms={
        ...         AtomType.SUBJECT: user_atom,
        ...         AtomType.ACTION: login_atom,
        ...         AtomType.METHOD: oauth2_atom,
        ...         AtomType.INTERFACE: web_atom,
        ...     }
        ... )
        >>> req.render()
        "User can login with OAuth 2.0 Authentication via Web UI"
    """

    id: str  # FR-001, STORY-042, REQ-1.2.3
    template: str  # "[{subject}] can [{action}] with [{method}] via [{interface}]"
    atoms: Dict[AtomType, Atom]  # Atomic parameters

    # Requirement metadata
    title: str = ""  # Auto-generated from template or custom
    description: str = ""  # Detailed description
    acceptance_criteria: List[str] = field(default_factory=list)
    priority: int = 50  # 1-100
    status: str = "draft"  # draft, active, implemented, verified, archived

    # Implementation tracking
    implementation_variant: Optional[str] = None  # "auth0" | "authkit" | None
    is_implemented: bool = False
    implementation_status: str = "planned"  # planned, flagged, active, deprecated
    flag_key: Optional[str] = None  # Feature flag for conditional activation

    # Composition
    parent_id: Optional[str] = None
    composition_rule: str = "AND"  # AND, OR, XOR for children

    # Traceability (maps to 16 views)
    derived_items: Dict[str, List[UUID]] = field(default_factory=dict)  # view_type → item_ids

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    version: int = 1

    def render(self) -> str:
        """Render requirement as natural language.

        Returns:
            Human-readable requirement text

        Example:
            >>> req.render()
            "User can login with OAuth 2.0 Authentication via Web UI"
        """
        if self.title:
            return self.title  # Use custom title if provided

        # Generate from template
        params = {atom_type.value: atom.label for atom_type, atom in self.atoms.items()}
        return self.template.format(**params)

    def toggle_atom(self, atom_type: AtomType, new_atom: Atom) -> 'AtomChange':
        """Toggle one atom to create variation.

        Args:
            atom_type: Which atom to swap (SUBJECT, ACTION, METHOD, INTERFACE)
            new_atom: Replacement atom

        Returns:
            AtomChange object describing the modification

        Example:
            >>> # Change from email/password to OAuth
            >>> change = req.toggle_atom(AtomType.METHOD, oauth2_atom)
            >>> change.old_value
            "email-password"
            >>> change.new_value
            "oauth2"
        """
        old_atom = self.atoms.get(atom_type)
        self.atoms[atom_type] = new_atom
        self.updated_at = datetime.utcnow()
        self.version += 1

        return AtomChange(
            requirement_id=self.id,
            atom_type=atom_type,
            old_atom=old_atom,
            new_atom=new_atom,
            timestamp=self.updated_at
        )

    def set_implementation_variant(self, variant: str):
        """Set active implementation variant.

        Args:
            variant: Implementation identifier (e.g., "auth0", "authkit")

        Raises:
            ValueError: If variant not in atom's implementations list

        Example:
            >>> req.set_implementation_variant("auth0")
            >>> req.implementation_variant
            "auth0"
        """
        # Validate variant exists for this requirement's atoms
        for atom in self.atoms.values():
            if variant in atom.implementations:
                self.implementation_variant = variant
                self.implementation_status = "active"
                self.updated_at = datetime.utcnow()
                return

        # If no atom has this implementation, mark as flagged for future
        self.implementation_variant = variant
        self.implementation_status = "flagged"
        self.updated_at = datetime.utcnow()

    def is_active(self, flags: 'FeatureFlagService', context: 'EvalContext') -> bool:
        """Check if requirement is active for deployment context."""
        if not self.flag_key:
            return True  # Always active
        return flags.is_enabled(self.flag_key, context)

@dataclass
class AtomChange:
    """Represents a single atom swap operation."""
    requirement_id: str
    atom_type: AtomType
    old_atom: Optional[Atom]
    new_atom: Atom
    timestamp: datetime

    @property
    def old_value(self) -> Optional[str]:
        return self.old_atom.value if self.old_atom else None

    @property
    def new_value(self) -> str:
        return self.new_atom.value

#### 3. View Integration Entity

```python
@dataclass
class AtomViewMapping:
    """Maps atom changes to view-specific updates.

    Defines how changing an atom affects items in each of the 16 views.
    """

    atom_id: UUID
    atom_type: AtomType
    view_type: str  # One of 16 ViewTypes

    # Mapping rules
    affects_title: bool = False  # Does atom change affect item title?
    affects_description: bool = False
    affects_code: bool = False
    affects_tests: bool = False
    affects_config: bool = False

    # Transformation rules
    title_template: Optional[str] = None  # Template for generating title
    description_template: Optional[str] = None
    code_template: Optional[str] = None  # Path to code template

    # Examples for SUBJECT atom in CODE view:
    # affects_code = True
    # code_template = "templates/code/subject_{atom.value}_handler.py"

    # Examples for METHOD atom in TEST view:
    # affects_tests = True
    # test_template = "templates/test/{method}_integration_test.py"

@dataclass
class DerivedItem:
    """Item derived from atomic requirement in specific view.

    Links back to source requirement and specific atoms that generated it.
    """

    item_id: UUID  # References UniversalItem.id
    source_requirement_id: str  # FR-001, STORY-042
    source_atoms: List[UUID]  # Atoms that generated this item
    view_type: str  # Which of 16 views
    generation_rule: str  # How this item was derived

    # Synchronization
    auto_update: bool = True  # Should this auto-update when atoms change?
    last_synced: datetime = field(default_factory=datetime.utcnow)

#### 4. Feature Flag Entity

```python
@dataclass
class FeatureFlag:
    """Feature flag for runtime requirement activation.

    Controls whether optional requirements are active in a deployment.
    Maps to SPLE variation points.
    """

    key: str  # ff_oauth2_google, ff_saml_enterprise
    name: str  # Human-readable
    description: str
    default_value: bool = False

    # Targeting rules (Unleash-style)
    strategies: List['FlagStrategy'] = field(default_factory=list)

    # Lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # Temporary flags should expire
    owner: str = ""  # Team/person responsible

    # Associated requirements
    controls_requirements: List[str] = field(default_factory=list)  # Requirement IDs

    def evaluate(self, context: 'EvalContext') -> bool:
        """Evaluate flag for given context."""
        # If no strategies, use default
        if not self.strategies:
            return self.default_value

        # Evaluate each strategy (OR logic)
        for strategy in self.strategies:
            if strategy.evaluate(context):
                return True

        return False

@dataclass
class FlagStrategy:
    """Targeting strategy for feature flag."""

    name: str  # "environment", "tenant", "gradual_rollout", "custom"
    parameters: dict[str, Any] = field(default_factory=dict)

    def evaluate(self, context: 'EvalContext') -> bool:
        """Evaluate strategy against context."""
        if self.name == "environment":
            return context.env in self.parameters.get("envs", [])

        elif self.name == "tenant":
            return context.tenant in self.parameters.get("tenants", [])

        elif self.name == "gradual_rollout":
            percentage = self.parameters.get("percentage", 0)
            user_hash = hash(context.user_id or context.tenant) % 100
            return user_hash < percentage

        elif self.name == "custom":
            # Evaluate custom expression
            expr = self.parameters.get("expression", "False")
            return eval(expr, {"context": context})

        return False

@dataclass
class EvalContext:
    """Evaluation context for feature flags."""
    env: str  # production, staging, development
    tenant: str  # Customer/org identifier
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    custom_attrs: dict[str, Any] = field(default_factory=dict)

#### 5. Implementation Variant Entity

```python
@dataclass
class ImplementationVariant:
    """Concrete implementation of an atom.

    Represents specific technology choice for an atom.
    E.g., METHOD:oauth2 can be implemented via auth0, authkit, or custom.
    """

    id: UUID
    atom_id: UUID  # Which atom this implements
    name: str  # "auth0", "authkit", "stripe", "postgresql"
    display_name: str  # "Auth0", "WorkOS AuthKit"

    # Implementation details
    is_implemented: bool = False  # Is code written?
    library: Optional[str] = None  # NPM/PyPI package
    config_required: dict[str, Any] = field(default_factory=dict)  # Required env vars

    # Toggle control
    is_active: bool = False  # Currently active toggle
    can_toggle: bool = True  # Can user toggle this?

    # Metadata
    vendor: Optional[str] = None  # "Auth0 Inc.", "Stripe Inc."
    cost: Optional[str] = None  # "$0/month", "$99/month"
    docs_url: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "atom_id": str(self.atom_id),
            "name": self.name,
            "display_name": self.display_name,
            "is_implemented": self.is_implemented,
            "is_active": self.is_active,
            "library": self.library,
            "config_required": self.config_required,
        }

---

## Integration with 16-View System

### Atom → View Mapping

Each atom change cascades to relevant views. Here's the complete mapping:

#### Subject Atom Changes

**Affects These Views**:
```python
SUBJECT_ATOM_MAPPING = {
    "FEATURE": {
        "affects": ["title", "description", "acceptance_criteria"],
        "example": "[User] can login → [Agent] can login",
        "impact": "Update user stories to reference Agent instead of User"
    },
    "CODE": {
        "affects": ["class_names", "function_parameters", "type_definitions"],
        "example": "class UserHandler → class AgentHandler",
        "impact": "Rename classes, update function signatures"
    },
    "TEST": {
        "affects": ["test_names", "test_data", "assertions"],
        "example": "test_user_login() → test_agent_login()",
        "impact": "Update test names and test data fixtures"
    },
    "API": {
        "affects": ["endpoint_paths", "request_schemas", "documentation"],
        "example": "/api/users → /api/agents",
        "impact": "Update endpoint paths and OpenAPI schemas"
    },
    "DATABASE": {
        "affects": ["table_names", "column_names"],
        "example": "users table → agents table",
        "impact": "Generate migration to rename table/columns"
    },
    "WIREFRAME": {
        "affects": ["screen_labels", "component_names"],
        "example": "User Profile Screen → Agent Profile Screen",
        "impact": "Update UI labels and component names"
    },
    "DOCUMENT": {
        "affects": ["content", "examples"],
        "example": "User Guide → Agent Guide",
        "impact": "Update documentation with new terminology"
    },
    # Other views: ARCHITECTURE, INFRASTRUCTURE, etc.
}
```

#### Action Atom Changes

**Affects These Views**:
```python
ACTION_ATOM_MAPPING = {
    "FEATURE": {
        "affects": ["title", "acceptance_criteria"],
        "example": "User can [login] → User can [logout]",
        "impact": "Complete requirement rewrite"
    },
    "CODE": {
        "affects": ["function_names", "business_logic"],
        "example": "def login() → def logout()",
        "impact": "Implement opposite operation"
    },
    "TEST": {
        "affects": ["test_scenarios", "assertions"],
        "example": "assert user.is_authenticated → assert not user.is_authenticated",
        "impact": "Invert test assertions"
    },
    "API": {
        "affects": ["http_methods", "endpoint_names"],
        "example": "POST /api/auth/login → POST /api/auth/logout",
        "impact": "Create opposite API endpoint"
    },
    "SEQUENCE": {
        "affects": ["flow_diagrams", "interaction_steps"],
        "example": "Login Flow → Logout Flow",
        "impact": "Reverse or create new sequence diagram"
    },
}
```

#### Method Atom Changes

**Affects These Views**:
```python
METHOD_ATOM_MAPPING = {
    "FEATURE": {
        "affects": ["description", "constraints"],
        "example": "with [email/password] → with [OAuth 2.0]",
        "impact": "Update requirement details"
    },
    "CODE": {
        "affects": ["implementation_logic", "dependencies"],
        "example": "validate_email_password() → validate_oauth_token()",
        "impact": "Replace authentication logic, update dependencies"
    },
    "API": {
        "affects": ["request_schema", "security_schemes"],
        "example": "email+password fields → authorization_code field",
        "impact": "Update request schema and OpenAPI security definitions"
    },
    "INFRASTRUCTURE": {
        "affects": ["services", "configuration"],
        "example": "No external service → Auth0 service integration",
        "impact": "Add Auth0 to infrastructure, environment variables"
    },
    "CONFIGURATION": {
        "affects": ["environment_variables", "secrets"],
        "example": "No oauth config → AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET",
        "impact": "Add configuration for OAuth provider"
    },
}
```

#### Interface Atom Changes

**Affects These Views**:
```python
INTERFACE_ATOM_MAPPING = {
    "FEATURE": {
        "affects": ["context", "user_stories"],
        "example": "via [main website] → via [mobile app]",
        "impact": "Update context and acceptance criteria"
    },
    "WIREFRAME": {
        "affects": ["screen_types", "components"],
        "example": "Web form → Mobile screen",
        "impact": "Create mobile wireframes instead of web"
    },
    "CODE": {
        "affects": ["framework", "platform"],
        "example": "React components → React Native components",
        "impact": "Different component library and platform APIs"
    },
    "API": {
        "affects": ["api_design", "constraints"],
        "example": "GraphQL (web) → REST (mobile)",
        "impact": "May need different API style for mobile"
    },
    "INFRASTRUCTURE": {
        "affects": ["deployment_targets", "build_configs"],
        "example": "Web hosting → App store distribution",
        "impact": "Different deployment pipeline and configs"
    },
}
```

### Complete View Matrix

**16 Views × 4 Atom Types = 64 Integration Points**

| View Type | Subject Atom | Action Atom | Method Atom | Interface Atom |
|-----------|-------------|-------------|-------------|----------------|
| FEATURE | ✅ Title, Description | ✅ User story rewrite | ✅ Details, Constraints | ✅ Context |
| CODE | ✅ Classes, Functions | ✅ Business logic | ✅ Implementation | ✅ Framework |
| WIREFRAME | ✅ Labels | ✅ User flows | ✅ Controls | ✅ Screen type |
| API | ✅ Endpoints | ✅ HTTP methods | ✅ Request schema | ✅ API style |
| TEST | ✅ Test data | ✅ Test scenarios | ✅ Assertions | ✅ Test type |
| DATABASE | ✅ Tables | ✅ Operations | ✅ Data types | ✅ Schema |
| INFRASTRUCTURE | ✅ Services | ✅ Processes | ✅ Integration | ✅ Platform |
| SEQUENCE | ✅ Actors | ✅ Interactions | ✅ Protocols | ✅ Diagram type |
| ARCHITECTURE | ✅ Components | ✅ Behaviors | ✅ Patterns | ✅ Layers |
| DOCUMENT | ✅ Terminology | ✅ Procedures | ✅ Examples | ✅ Format |
| DECISION | ✅ Stakeholders | ✅ Decision type | ✅ Criteria | ✅ Context |
| RISK | ✅ Risk owners | ✅ Risk events | ✅ Mitigations | ✅ Impact area |
| DEPENDENCY | ✅ Dependency owner | ✅ Dependency type | ✅ Integration | ✅ Interface |
| METRIC | ✅ Measured entity | ✅ Metric type | ✅ Calculation | ✅ Dashboard |
| TIMELINE | ✅ Assignee | ✅ Milestone type | ✅ Delivery method | ✅ Phase |
| RESOURCE | ✅ Resource type | ✅ Allocation | ✅ Provisioning | ✅ Environment |

---

## Cascading Update Mechanism

### Algorithm Overview

When an atom changes in a requirement:

```
1. Detect Change
   └─ User toggles [email/password] → [OAuth 2.0] in FR-001

2. Find Affected Requirements
   └─ All requirements using the changed atom or its variations

3. Compute Impact Across 16 Views
   └─ For each affected requirement, for each view:
       - Check AtomViewMapping rules
       - Determine what needs updating (title, code, tests, etc.)

4. Generate Update Events
   └─ Create RequirementAtomChanged events
   └─ Create ItemUpdateRequired events for each affected item

5. Cascade Updates (Dependency Order)
   └─ Topological sort of dependency graph
   └─ Apply updates in order (dependencies first)

6. Validate Consistency
   └─ Run validation on all updated items
   └─ Check constraints still satisfied

7. Publish Notifications
   └─ Notify stakeholders of cascading changes
   └─ Update traceability links
```

### Implementation

```python
@dataclass
class ImpactAnalysisResult:
    """Result of impact analysis for atom change."""

    changed_requirement: str
    changed_atom: AtomChange

    # Affected entities
    affected_requirements: List[str] = field(default_factory=list)
    affected_items: Dict[str, List[UUID]] = field(default_factory=dict)  # view → item_ids

    # Update plan
    required_updates: List['ItemUpdate'] = field(default_factory=list)
    required_migrations: List[str] = field(default_factory=list)  # Database migrations
    required_config_changes: List[str] = field(default_factory=list)

    # Estimates
    estimated_effort: int = 0  # Person-hours
    estimated_risk: str = "low"  # low, medium, high

    def summary(self) -> dict:
        return {
            "requirements_affected": len(self.affected_requirements),
            "items_affected": sum(len(items) for items in self.affected_items.values()),
            "views_affected": list(self.affected_items.keys()),
            "migrations_required": len(self.required_migrations),
            "estimated_effort_hours": self.estimated_effort,
            "risk_level": self.estimated_risk,
        }

class AtomicImpactAnalyzer:
    """Analyzes impact of atom changes across all views."""

    def __init__(
        self,
        requirement_repository: 'RequirementRepository',
        item_repository: 'ItemRepository',
        mapping_repository: 'AtomViewMappingRepository',
    ):
        self.req_repo = requirement_repository
        self.item_repo = item_repository
        self.mapping_repo = mapping_repository

    async def analyze(
        self,
        requirement_id: str,
        atom_change: AtomChange
    ) -> ImpactAnalysisResult:
        """Analyze impact of changing an atom.

        Args:
            requirement_id: ID of requirement being modified
            atom_change: Details of atom swap

        Returns:
            Complete impact analysis with update plan
        """
        result = ImpactAnalysisResult(
            changed_requirement=requirement_id,
            changed_atom=atom_change
        )

        # 1. Find all requirements using this atom or its variations
        affected_reqs = await self._find_affected_requirements(atom_change)
        result.affected_requirements = affected_reqs

        # 2. For each affected requirement, compute view impact
        for req_id in affected_reqs:
            req = await self.req_repo.find_by_id(req_id)

            # Get derived items for this requirement
            derived = await self.item_repo.find_derived_items(req_id)

            # For each view with derived items
            for view_type, item_ids in derived.items():
                result.affected_items.setdefault(view_type, []).extend(item_ids)

                # Get mapping rules for this atom type + view
                mapping = await self.mapping_repo.find_mapping(
                    atom_type=atom_change.atom_type,
                    view_type=view_type
                )

                # Generate update plan for each item
                for item_id in item_ids:
                    item = await self.item_repo.find_by_id(item_id)
                    updates = self._compute_required_updates(
                        item, atom_change, mapping
                    )

                    if updates:
                        result.required_updates.append(ItemUpdate(
                            item_id=item_id,
                            view_type=view_type,
                            changes=updates,
                            reason=f"Atom changed: {atom_change.atom_type.value}",
                            source_requirement=req_id
                        ))

        # 3. Identify database migrations needed
        if "DATABASE" in result.affected_items:
            migrations = await self._generate_migrations(result.affected_items["DATABASE"], atom_change)
            result.required_migrations = migrations

        # 4. Identify config changes needed
        if "INFRASTRUCTURE" in result.affected_items or "CONFIGURATION" in result.affected_items:
            configs = await self._generate_config_changes(atom_change)
            result.required_config_changes = configs

        # 5. Estimate effort and risk
        result.estimated_effort = self._estimate_effort(result)
        result.estimated_risk = self._assess_risk(result)

        return result

    async def _find_affected_requirements(self, atom_change: AtomChange) -> List[str]:
        """Find all requirements using this atom or compatible variants."""
        # Direct usage
        direct = await self.req_repo.find_by_atom(atom_change.new_atom.id)

        # Compatible atoms (e.g., "oauth" and "oauth2" are compatible)
        compatible_atom_ids = atom_change.new_atom.related + [
            self._find_atom_by_value(syn) for syn in atom_change.new_atom.synonyms
        ]
        compatible = []
        for atom_id in compatible_atom_ids:
            compatible.extend(await self.req_repo.find_by_atom(atom_id))

        return list(set(direct + compatible))

    def _compute_required_updates(
        self,
        item: 'UniversalItem',
        atom_change: AtomChange,
        mapping: AtomViewMapping
    ) -> dict[str, Any]:
        """Compute what fields need updating in this item."""
        updates = {}

        if mapping.affects_title:
            # Regenerate title with new atom
            updates["title"] = self._generate_title(item, atom_change, mapping)

        if mapping.affects_description:
            updates["description"] = self._generate_description(item, atom_change, mapping)

        if mapping.affects_code:
            updates["metadata.code_changes"] = self._generate_code_changes(item, atom_change, mapping)

        if mapping.affects_tests:
            updates["metadata.test_changes"] = self._generate_test_changes(item, atom_change, mapping)

        return updates

    async def _generate_migrations(
        self,
        affected_db_items: List[UUID],
        atom_change: AtomChange
    ) -> List[str]:
        """Generate SQL migrations for database changes."""
        migrations = []

        for item_id in affected_db_items:
            item = await self.item_repo.find_by_id(item_id)

            # Example: SUBJECT atom change (user → agent)
            if atom_change.atom_type == AtomType.SUBJECT:
                old_table = f"{atom_change.old_value}s"  # "users"
                new_table = f"{atom_change.new_value}s"  # "agents"

                migration = f"""
-- Rename table due to SUBJECT atom change: {atom_change.old_value} → {atom_change.new_value}
ALTER TABLE {old_table} RENAME TO {new_table};

-- Update foreign key references
-- (generated based on item.metadata.foreign_keys)
"""
                migrations.append(migration)

        return migrations

    def _estimate_effort(self, result: ImpactAnalysisResult) -> int:
        """Estimate person-hours for cascading updates."""
        # Simple heuristic (can be refined with ML)
        base_effort = 1  # 1 hour for the change itself

        # +15 minutes per affected requirement
        base_effort += len(result.affected_requirements) * 0.25

        # +5 minutes per affected item
        total_items = sum(len(items) for items in result.affected_items.values())
        base_effort += total_items * 0.08

        # +2 hours per database migration
        base_effort += len(result.required_migrations) * 2

        return int(base_effort)

    def _assess_risk(self, result: ImpactAnalysisResult) -> str:
        """Assess risk level of cascading changes."""
        total_items = sum(len(items) for items in result.affected_items.values())

        if total_items > 100:
            return "high"  # Widespread impact
        elif total_items > 20:
            return "medium"
        elif len(result.required_migrations) > 0:
            return "medium"  # Database changes always risky
        else:
            return "low"

### Cascading Update Execution

```python
class CascadingUpdateEngine:
    """Executes cascading updates across all 16 views."""

    def __init__(
        self,
        event_store: 'EventStore',
        item_repository: 'ItemRepository',
        event_bus: 'EventBus',
    ):
        self.events = event_store
        self.items = item_repository
        self.bus = event_bus

    async def execute_cascade(
        self,
        requirement_id: str,
        atom_change: AtomChange,
        impact: ImpactAnalysisResult,
        user: str,
        dry_run: bool = False
    ) -> 'CascadeResult':
        """Execute all cascading updates.

        Args:
            requirement_id: Source requirement ID
            atom_change: Atom swap that triggered cascade
            impact: Pre-computed impact analysis
            user: User executing the change
            dry_run: If True, don't persist changes (preview only)

        Returns:
            Results of cascade execution
        """
        result = CascadeResult(requirement_id=requirement_id)

        # 1. Update source requirement
        source_event = RequirementAtomChanged(
            aggregate_id=requirement_id,
            event_type="AtomChanged",
            timestamp=datetime.utcnow(),
            data={
                "atom_type": atom_change.atom_type.value,
                "old_value": atom_change.old_value,
                "new_value": atom_change.new_value,
            },
            user=user
        )

        if not dry_run:
            self.events.append([source_event])

        # 2. Apply updates to all affected items (dependency order)
        dependency_graph = await self._build_update_dependency_graph(impact)
        update_order = self._topological_sort(dependency_graph)

        for item_id in update_order:
            # Find update plan for this item
            update_plan = next(
                (u for u in impact.required_updates if u.item_id == item_id),
                None
            )

            if not update_plan:
                continue

            # Apply update
            try:
                updated_item = await self._apply_item_update(
                    item_id, update_plan, dry_run
                )
                result.items_updated.append(updated_item)

                # Emit event
                if not dry_run:
                    await self.bus.publish(
                        f"TRACE_EVENTS.{update_plan.view_type}.updated",
                        {
                            "item_id": str(item_id),
                            "reason": update_plan.reason,
                            "caused_by": requirement_id,
                        }
                    )

            except Exception as e:
                result.errors.append(f"Failed to update {item_id}: {e}")

        # 3. Generate migrations (if DATABASE view affected)
        if impact.required_migrations and not dry_run:
            for migration_sql in impact.required_migrations:
                migration_file = await self._write_migration_file(migration_sql)
                result.migrations_generated.append(migration_file)

        # 4. Update configuration (if needed)
        if impact.required_config_changes and not dry_run:
            for config_change in impact.required_config_changes:
                await self._apply_config_change(config_change)
                result.config_updated.append(config_change)

        # 5. Update traceability links
        if not dry_run:
            await self._update_trace_links(requirement_id, result.items_updated)

        return result

    async def _apply_item_update(
        self,
        item_id: UUID,
        update_plan: 'ItemUpdate',
        dry_run: bool
    ) -> 'UniversalItem':
        """Apply updates to a single item."""
        item = await self.items.find_by_id(item_id)

        # Apply each change
        for field_path, new_value in update_plan.changes.items():
            if "." in field_path:
                # Nested field (e.g., "metadata.code_changes")
                parts = field_path.split(".")
                obj = item
                for part in parts[:-1]:
                    obj = getattr(obj, part)
                setattr(obj, parts[-1], new_value)
            else:
                # Top-level field
                setattr(item, field_path, new_value)

        # Update timestamp
        item.updated_at = datetime.utcnow()

        # Persist
        if not dry_run:
            await self.items.update(item)

        return item

@dataclass
class CascadeResult:
    """Result of cascading update execution."""
    requirement_id: str
    items_updated: List['UniversalItem'] = field(default_factory=list)
    migrations_generated: List[str] = field(default_factory=list)
    config_updated: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> dict:
        return {
            "items_updated": len(self.items_updated),
            "views_affected": len(set(item.view_type for item in self.items_updated)),
            "migrations": len(self.migrations_generated),
            "config_changes": len(self.config_updated),
            "errors": self.errors,
        }

### Example: Complete Cascade Flow

**Scenario**: Change METHOD atom from [email/password] to [OAuth 2.0]

**Step 1: User Action**
```python
# User toggles method atom
req = await requirement_service.find("FR-001")
oauth_atom = await atom_library.find_by_value("oauth2")

atom_change = req.toggle_atom(AtomType.METHOD, oauth_atom)
# AtomChange(
#     requirement_id="FR-001",
#     atom_type=AtomType.METHOD,
#     old_value="email-password",
#     new_value="oauth2"
# )
```

**Step 2: Impact Analysis**
```python
impact = await impact_analyzer.analyze("FR-001", atom_change)

# ImpactAnalysisResult(
#     changed_requirement="FR-001",
#     affected_requirements=["FR-001", "FR-002"],  # FR-002 also uses login
#     affected_items={
#         "CODE": [code_item_1, code_item_2, code_item_3],
#         "TEST": [test_item_1, test_item_2],
#         "API": [api_item_1],
#         "DATABASE": [],  # No DB schema change for this
#         "INFRASTRUCTURE": [infra_item_1],  # Need Auth0 integration
#         "CONFIGURATION": [config_item_1],  # Add AUTH0_CLIENT_ID
#     },
#     required_updates=[
#         ItemUpdate(
#             item_id=code_item_1,
#             view_type="CODE",
#             changes={
#                 "title": "OAuth 2.0 Login Handler",
#                 "description": "Handles user login via OAuth 2.0",
#                 "metadata.function_name": "handle_oauth_login",
#             }
#         ),
#         # ... more updates
#     ],
#     estimated_effort=3,  # 3 hours
#     estimated_risk="medium"
# )
```

**Step 3: User Preview & Confirmation**
```bash
# CLI shows preview
$ trace atom toggle FR-001 --atom method --new oauth2 --preview

Impact Analysis:
  Requirements affected: 2
  Items affected: 7 (across 5 views)
  Migrations required: 0
  Config changes: 2

  Estimated effort: 3 hours
  Risk level: medium

Affected Items:
  CODE (3 items):
    - src/auth/login_handler.py → src/auth/oauth_handler.py
    - frontend/components/LoginForm.tsx → frontend/components/OAuthButton.tsx
    - backend/services/auth_service.py (updated logic)

  TEST (2 items):
    - tests/test_email_login.py → tests/test_oauth_login.py
    - tests/e2e/login_flow.spec.ts (updated)

  API (1 item):
    - POST /api/auth/login (request schema changed)

  INFRASTRUCTURE (1 item):
    - Add Auth0 service to docker-compose.yml

  CONFIGURATION (1 item):
    - Add AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET to .env

Apply changes? [y/N]: y
```

**Step 4: Execute Cascade**
```python
cascade_result = await cascade_engine.execute_cascade(
    requirement_id="FR-001",
    atom_change=atom_change,
    impact=impact,
    user="john@example.com",
    dry_run=False  # Actually apply changes
)

# CascadeResult(
#     requirement_id="FR-001",
#     items_updated=[code_item_1, code_item_2, ...],
#     migrations_generated=[],
#     config_updated=["AUTH0_CLIENT_ID", "AUTH0_CLIENT_SECRET"],
#     errors=[]
# )
```

**Step 5: Publish Events**
```python
# All events published to NATS for async processing
await event_bus.publish("TRACE_EVENTS.requirement.atom_changed", {
    "requirement_id": "FR-001",
    "atom_type": "method",
    "old_value": "email-password",
    "new_value": "oauth2",
    "impact_summary": impact.summary(),
    "timestamp": datetime.utcnow().isoformat()
})
```

---

## Toggle/Flag System

### Feature Flag Integration

**Purpose**: Enable/disable optional requirements at runtime without code changes.

#### Flag Types

```python
class FlagType(Enum):
    """Types of feature flags in trace system."""

    # Release flags (temporary, remove after launch)
    RELEASE = "release"

    # Operational flags (permanent, control system behavior)
    OPERATIONAL = "operational"

    # Experimental flags (A/B testing, remove after experiment)
    EXPERIMENTAL = "experimental"

    # Permission flags (entitlements, per-tenant)
    PERMISSION = "permission"

    # Implementation variant flags (choose implementation)
    IMPLEMENTATION = "implementation"

@dataclass
class RequirementFlag:
    """Feature flag controlling requirement activation."""

    key: str  # ff_oauth2_enabled
    name: str  # "Enable OAuth 2.0 Authentication"
    description: str
    flag_type: FlagType

    # Default value
    default_enabled: bool = False

    # Targeting
    strategies: List[FlagStrategy] = field(default_factory=list)

    # Associated requirements
    controls: List[str] = field(default_factory=list)  # Requirement IDs

    # Lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    owner: str = ""

    # Metrics
    evaluation_count: int = 0
    last_evaluated: Optional[datetime] = None

### Implementation Variant System

**Purpose**: Track multiple implementations for same atom (e.g., auth0 vs authkit for OAuth).

```python
@dataclass
class ImplementationRegistry:
    """Registry of implementation variants for atoms.

    Tracks which implementations exist, which are active, and provides
    toggle mechanisms.
    """

    atom_id: UUID
    variants: List[ImplementationVariant] = field(default_factory=list)
    active_variant: Optional[str] = None

    def add_variant(self, variant: ImplementationVariant):
        """Register new implementation variant."""
        self.variants.append(variant)

        # If first implementation, make it active
        if not self.active_variant:
            self.active_variant = variant.name
            variant.is_active = True

    def toggle_to(self, variant_name: str) -> 'ToggleResult':
        """Switch active implementation variant.

        Args:
            variant_name: Name of variant to activate

        Returns:
            Result with affected requirements and config changes

        Example:
            >>> registry.toggle_to("authkit")
            >>> # Deactivates auth0, activates authkit
            >>> # Returns list of requirements needing config updates
        """
        # Find variant
        new_variant = next((v for v in self.variants if v.name == variant_name), None)
        if not new_variant:
            raise ValueError(f"Variant '{variant_name}' not found")

        if not new_variant.is_implemented:
            raise ValueError(f"Variant '{variant_name}' not yet implemented")

        # Deactivate old
        old_variant = next((v for v in self.variants if v.is_active), None)
        if old_variant:
            old_variant.is_active = False

        # Activate new
        new_variant.is_active = True
        self.active_variant = variant_name

        # Find affected requirements
        affected_reqs = self._find_requirements_using_atom(self.atom_id)

        # Compute config changes needed
        config_changes = self._diff_configs(old_variant, new_variant)

        return ToggleResult(
            old_variant=old_variant.name if old_variant else None,
            new_variant=variant_name,
            affected_requirements=affected_reqs,
            config_changes=config_changes
        )

@dataclass
class ToggleResult:
    """Result of toggling implementation variant."""
    old_variant: Optional[str]
    new_variant: str
    affected_requirements: List[str]
    config_changes: Dict[str, Any]  # env var → new value

    def summary(self) -> str:
        return f"""
Toggled from {self.old_variant} to {self.new_variant}
  - {len(self.affected_requirements)} requirements affected
  - {len(self.config_changes)} config changes required

Config changes:
{chr(10).join(f"  {k} = {v}" for k, v in self.config_changes.items())}
"""

### Future Implementation Flags

**Purpose**: Mark atoms for future implementation (not yet coded).

```python
@dataclass
class FutureImplementationFlag:
    """Flag indicating atom is planned but not yet implemented.

    Allows requirements to reference atoms that don't have code yet.
    Useful for roadmap planning and dependency visualization.
    """

    atom_id: UUID
    planned_implementation: str  # Description of planned approach
    target_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    priority: int = 50  # 1-100

    # Blockers
    blocked_by: List[str] = field(default_factory=list)  # Other atom/requirement IDs
    blocking: List[str] = field(default_factory=list)  # What this blocks

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "planned"  # planned, in_progress, implemented, cancelled

class FutureImplementationTracker:
    """Track and visualize future implementation flags."""

    def __init__(self, flag_repository):
        self.flags = flag_repository

    async def mark_as_future(
        self,
        atom: Atom,
        implementation_name: str,
        rationale: str
    ) -> FutureImplementationFlag:
        """Mark implementation variant as future work.

        Example:
            >>> # OAuth atom exists, but authkit variant not yet implemented
            >>> flag = tracker.mark_as_future(
            ...     atom=oauth_atom,
            ...     implementation_name="authkit",
            ...     rationale="Waiting for authkit API access"
            ... )
        """
        flag = FutureImplementationFlag(
            atom_id=atom.id,
            planned_implementation=implementation_name,
            status="planned"
        )

        # Create implementation variant placeholder
        variant = ImplementationVariant(
            id=uuid4(),
            atom_id=atom.id,
            name=implementation_name,
            display_name=implementation_name.title(),
            is_implemented=False,  # KEY: not yet implemented
            can_toggle=False  # Can't toggle to unimplemented variant
        )

        atom.implementations.append(implementation_name)

        await self.flags.save(flag)
        return flag

    async def generate_roadmap(self) -> 'ImplementationRoadmap':
        """Generate prioritized roadmap of future implementations.

        Returns:
            Roadmap with dependency-ordered implementation tasks
        """
        all_flags = await self.flags.find_all(status="planned")

        # Build dependency graph
        graph = self._build_implementation_dependency_graph(all_flags)

        # Topological sort
        ordered = topological_sort(graph)

        # Group by quarter
        roadmap = ImplementationRoadmap()
        for flag in ordered:
            quarter = self._compute_quarter(flag.target_date or datetime.utcnow())
            roadmap.add_to_quarter(quarter, flag)

        return roadmap

### Flag-Based Product Derivation

```python
class ProductDerivationEngine:
    """Derive concrete product requirements from base + flags."""

    def __init__(
        self,
        requirement_repository,
        flag_service: 'FeatureFlagService'
    ):
        self.reqs = requirement_repository
        self.flags = flag_service

    async def derive_product(
        self,
        base_requirements: List[AtomicRequirement],
        context: EvalContext
    ) -> 'ProductConfiguration':
        """Derive active requirements for deployment context.

        Args:
            base_requirements: All possible requirements (catalog)
            context: Deployment context (env, tenant, etc.)

        Returns:
            Filtered list of requirements active for this context

        Example:
            >>> # Production context for Enterprise tenant
            >>> context = EvalContext(env="production", tenant="acme-corp")
            >>> product = await engine.derive_product(all_requirements, context)
            >>> # Returns only requirements with flags enabled for enterprise
        """
        active_reqs = []

        for req in base_requirements:
            # Check if requirement is active for this context
            if req.is_active(self.flags, context):
                active_reqs.append(req)

        # Validate configuration
        validation = await self._validate_configuration(active_reqs)
        if not validation.is_valid:
            raise ConfigurationError(validation.errors)

        # Resolve implementation variants
        resolved = await self._resolve_variants(active_reqs, context)

        return ProductConfiguration(
            context=context,
            requirements=resolved,
            derived_at=datetime.utcnow()
        )

    async def _validate_configuration(
        self,
        requirements: List[AtomicRequirement]
    ) -> 'ValidationResult':
        """Validate requirement configuration is consistent."""
        errors = []

        # Check for circular dependencies
        dep_graph = build_dependency_graph(requirements)
        cycles = detect_cycles(dep_graph)
        if cycles:
            errors.append(f"Circular dependencies detected: {cycles}")

        # Check for conflicting requirements
        for i, req1 in enumerate(requirements):
            for req2 in requirements[i+1:]:
                if self._are_conflicting(req1, req2):
                    errors.append(f"Conflict: {req1.id} conflicts with {req2.id}")

        # Check implementation variants are compatible
        variants = [req.implementation_variant for req in requirements if req.implementation_variant]
        if not self._are_variants_compatible(variants):
            errors.append(f"Incompatible implementation variants: {variants}")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    async def _resolve_variants(
        self,
        requirements: List[AtomicRequirement],
        context: EvalContext
    ) -> List[AtomicRequirement]:
        """Resolve implementation variants for each requirement.

        Chooses concrete implementation based on context and toggles.
        """
        resolved = []

        for req in requirements:
            if not req.implementation_variant:
                # No variant specified, use defaults from atoms
                variant = self._choose_default_variant(req)
                req.set_implementation_variant(variant)

            # Verify variant is implemented
            if req.implementation_status == "flagged":
                # Future implementation - skip or use fallback
                if context.env != "production":
                    # In dev/staging, use mock implementation
                    req.implementation_variant = "mock"
                else:
                    raise ConfigurationError(
                        f"{req.id} uses unimplemented variant: {req.implementation_variant}"
                    )

            resolved.append(req)

        return resolved

@dataclass
class ProductConfiguration:
    """Concrete product derived from base requirements + flags."""
    context: EvalContext
    requirements: List[AtomicRequirement]
    derived_at: datetime

    def export_to_env_file(self, path: str):
        """Export configuration as .env file."""
        lines = [f"# Generated for {self.context.tenant} ({self.context.env})"]
        lines.append(f"# Derived at: {self.derived_at.isoformat()}")
        lines.append("")

        # Collect all config from implementation variants
        configs = {}
        for req in self.requirements:
            if req.implementation_variant:
                # Get variant details
                for atom in req.atoms.values():
                    variant = next(
                        (v for v in atom.implementations if v == req.implementation_variant),
                        None
                    )
                    if variant:
                        configs.update(variant.config_required)

        for key, value in configs.items():
            lines.append(f"{key}={value}")

        with open(path, "w") as f:
            f.write("\n".join(lines))

---

## Graph Query Patterns

### PostgreSQL Recursive CTEs

**Pattern 1: Find All Atoms Used in a Requirement Tree**
```sql
-- Get all atoms used in FR-001 and its children
WITH RECURSIVE requirement_tree AS (
    -- Base: start requirement
    SELECT id, atoms, 1 AS depth
    FROM atomic_requirements
    WHERE id = 'FR-001'

    UNION ALL

    -- Recursive: children
    SELECT ar.id, ar.atoms, rt.depth + 1
    FROM atomic_requirements ar
    JOIN requirement_tree rt ON ar.parent_id = rt.id
    WHERE rt.depth < 10
)
SELECT DISTINCT
    jsonb_array_elements_text(jsonb_path_query_array(atoms, '$[*].id')) AS atom_id
FROM requirement_tree;
```

**Pattern 2: Impact Analysis - Requirements Affected by Atom Change**
```sql
-- Find all requirements using atom_id='uuid-oauth2'
SELECT ar.id, ar.template
FROM atomic_requirements ar
WHERE ar.atoms @> jsonb_build_object('method', jsonb_build_object('id', 'uuid-oauth2'));
```

**Pattern 3: Feature Flag Evaluation**
```sql
-- Get active requirements for production + tenant=acme
WITH flag_evaluations AS (
    SELECT
        key,
        evaluate_flag_strategies(
            strategies,
            jsonb_build_object('env', 'production', 'tenant', 'acme')
        ) AS is_enabled
    FROM feature_flags
)
SELECT ar.*
FROM atomic_requirements ar
LEFT JOIN flag_evaluations fe ON ar.flag_key = fe.key
WHERE ar.flag_key IS NULL  -- Always active
   OR fe.is_enabled = TRUE;  -- Flag enabled for context
```

**Pattern 4: Implementation Variant Resolution**
```sql
-- Get effective implementation variants for product config
SELECT
    ar.id,
    ar.implementation_variant,
    iv.name AS variant_name,
    iv.config_required
FROM atomic_requirements ar
JOIN implementation_variants iv ON (
    iv.atom_id = ANY(SELECT jsonb_array_elements_text(ar.atoms))
    AND iv.name = ar.implementation_variant
)
WHERE iv.is_active = TRUE;
```

### Graph Algorithms

#### Transitive Atom Closure

```python
def find_all_related_atoms(atom: Atom, depth: int = 3) -> Set[UUID]:
    """Find all atoms related to this atom (transitively).

    Args:
        atom: Starting atom
        depth: Maximum traversal depth

    Returns:
        Set of related atom IDs

    Example:
        >>> oauth_atom = atom_library.find("oauth2")
        >>> related = find_all_related_atoms(oauth_atom, depth=2)
        >>> # Returns: {auth0, authkit, saml, openid} (auth-related atoms)
    """
    visited = set()
    queue = [(atom.id, 0)]

    while queue:
        current_id, current_depth = queue.pop(0)

        if current_id in visited or current_depth >= depth:
            continue

        visited.add(current_id)

        # Load atom
        current_atom = atom_library.find_by_id(current_id)

        # Add related atoms to queue
        for related_id in current_atom.related:
            if related_id not in visited:
                queue.append((related_id, current_depth + 1))

        # Add compatible atoms
        for atom_type, compatible_ids in current_atom.compatible_with.items():
            for comp_id in compatible_ids:
                if comp_id not in visited:
                    queue.append((comp_id, current_depth + 1))

    visited.remove(atom.id)  # Don't include self
    return visited

#### Requirement Compatibility Check

```python
def check_requirement_compatibility(
    req1: AtomicRequirement,
    req2: AtomicRequirement
) -> 'CompatibilityResult':
    """Check if two requirements are compatible (can coexist).

    Args:
        req1: First requirement
        req2: Second requirement

    Returns:
        Compatibility result with conflicts and suggestions

    Example:
        >>> oauth_req = atomic_requirement("FR-001", method="oauth2")
        >>> saml_req = atomic_requirement("FR-002", method="saml")
        >>> result = check_compatibility(oauth_req, saml_req)
        >>> result.compatible
        True  # Both can coexist
    """
    conflicts = []

    # Check for conflicting atoms
    for atom_type in [AtomType.SUBJECT, AtomType.ACTION, AtomType.METHOD, AtomType.INTERFACE]:
        atom1 = req1.atoms.get(atom_type)
        atom2 = req2.atoms.get(atom_type)

        if not atom1 or not atom2:
            continue

        # Check if atoms conflict
        if atom2.id in atom1.conflicts_with or atom1.id in atom2.conflicts_with:
            conflicts.append(f"{atom_type.value}: {atom1.value} conflicts with {atom2.value}")

    # Check implementation variants
    if req1.implementation_variant and req2.implementation_variant:
        if not are_variants_compatible(req1.implementation_variant, req2.implementation_variant):
            conflicts.append(
                f"Implementation variants incompatible: "
                f"{req1.implementation_variant} vs {req2.implementation_variant}"
            )

    return CompatibilityResult(
        compatible=len(conflicts) == 0,
        conflicts=conflicts,
        suggestions=generate_resolution_suggestions(conflicts) if conflicts else []
    )

---

## Intelligent CRUD

### Auto-Generation Engine

```python
class IntelligentCRUDEngine:
    """Auto-generate items across all 16 views from atomic requirements.

    When user creates/updates an atomic requirement, this engine:
    1. Analyzes the requirement's atoms
    2. Determines which views need derived items
    3. Generates items using templates
    4. Creates traceability links
    5. Scaffolds code/tests/config as needed
    """

    def __init__(
        self,
        item_repository,
        template_library,
        llm_client
    ):
        self.items = item_repository
        self.templates = template_library
        self.llm = llm_client

    async def create_requirement_with_cascade(
        self,
        req: AtomicRequirement,
        user: str
    ) -> 'CascadeGenerationResult':
        """Create requirement and auto-generate derived items.

        Args:
            req: Atomic requirement to create
            user: User creating the requirement

        Returns:
            Result with all generated items across views

        Example:
            >>> req = AtomicRequirement(
            ...     id="FR-001",
            ...     template="[{subject}] can [{action}] with [{method}] via [{interface}]",
            ...     atoms={
            ...         AtomType.SUBJECT: user_atom,
            ...         AtomType.ACTION: login_atom,
            ...         AtomType.METHOD: email_password_atom,
            ...         AtomType.INTERFACE: web_atom,
            ...     }
            ... )
            >>> result = await engine.create_requirement_with_cascade(req, "john@example.com")
            >>> len(result.generated_items)
            12  # Items across CODE, TEST, API, DATABASE, etc.
        """
        result = CascadeGenerationResult(requirement_id=req.id)

        # 1. Persist requirement first
        await self.requirements.save(req)

        # 2. Analyze which views need derived items
        affected_views = self._determine_affected_views(req)

        # 3. For each affected view, generate items
        for view_type in affected_views:
            try:
                items = await self._generate_items_for_view(req, view_type, user)
                result.generated_items[view_type] = items

                # Create traceability links
                for item in items:
                    derived = DerivedItem(
                        item_id=item.id,
                        source_requirement_id=req.id,
                        source_atoms=[atom.id for atom in req.atoms.values()],
                        view_type=view_type,
                        generation_rule=f"auto_from_requirement",
                        auto_update=True
                    )
                    await self.items.save_derived_item(derived)

                    result.links_created += 1

            except Exception as e:
                result.errors.append(f"Failed to generate {view_type}: {e}")

        # 4. Scaffold code files (for CODE, TEST views)
        if "CODE" in result.generated_items:
            scaffolded = await self._scaffold_code_files(req, result.generated_items["CODE"])
            result.files_scaffolded.extend(scaffolded)

        if "TEST" in result.generated_items:
            scaffolded = await self._scaffold_test_files(req, result.generated_items["TEST"])
            result.files_scaffolded.extend(scaffolded)

        return result

    def _determine_affected_views(self, req: AtomicRequirement) -> List[str]:
        """Determine which views need derived items for this requirement.

        Uses atom types and requirement content to infer relevant views.
        """
        views = ["FEATURE"]  # Always create in FEATURE view

        # If has interface atom, needs WIREFRAME
        if AtomType.INTERFACE in req.atoms:
            interface = req.atoms[AtomType.INTERFACE]
            if interface.value in ["web-ui", "mobile-app"]:
                views.append("WIREFRAME")

        # If has action atom, needs CODE
        if AtomType.ACTION in req.atoms:
            views.append("CODE")
            views.append("TEST")  # Code always needs tests

        # If action involves API, needs API view
        if AtomType.INTERFACE in req.atoms:
            interface = req.atoms[AtomType.INTERFACE]
            if "api" in interface.value:
                views.append("API")

        # If method involves data persistence, needs DATABASE
        if AtomType.METHOD in req.atoms:
            method = req.atoms[AtomType.METHOD]
            if method.scope in [AtomScope.DATA_STORAGE, AtomScope.AUTHENTICATION]:
                views.append("DATABASE")

        # Always add DOCUMENT for traceability
        views.append("DOCUMENT")

        return views

    async def _generate_items_for_view(
        self,
        req: AtomicRequirement,
        view_type: str,
        user: str
    ) -> List['UniversalItem']:
        """Generate items for specific view based on requirement atoms.

        Uses templates and LLM assistance to create contextually appropriate items.
        """
        items = []

        if view_type == "CODE":
            # Generate code items
            for atom_type, atom in req.atoms.items():
                if atom_type in [AtomType.ACTION, AtomType.METHOD]:
                    # Create handler/service code item
                    code_item = await self._generate_code_item(req, atom, user)
                    items.append(code_item)

        elif view_type == "TEST":
            # Generate test items
            # One test item per code item
            code_items = req.derived_items.get("CODE", [])
            for code_item_id in code_items:
                test_item = await self._generate_test_item(req, code_item_id, user)
                items.append(test_item)

        elif view_type == "API":
            # Generate API endpoint items
            if AtomType.ACTION in req.atoms:
                action = req.atoms[AtomType.ACTION]
                api_item = await self._generate_api_item(req, action, user)
                items.append(api_item)

        elif view_type == "DATABASE":
            # Generate database schema items
            if AtomType.SUBJECT in req.atoms:
                subject = req.atoms[AtomType.SUBJECT]
                db_item = await self._generate_database_item(req, subject, user)
                items.append(db_item)

        elif view_type == "WIREFRAME":
            # Generate UI wireframe items
            if AtomType.INTERFACE in req.atoms:
                interface = req.atoms[AtomType.INTERFACE]
                wireframe_item = await self._generate_wireframe_item(req, interface, user)
                items.append(wireframe_item)

        # ... other views

        return items

    async def _generate_code_item(
        self,
        req: AtomicRequirement,
        atom: Atom,
        user: str
    ) -> 'UniversalItem':
        """Generate code item using templates + LLM."""

        # Find template for this atom type
        template = self.templates.get_code_template(atom.type, atom.scope)

        # Use LLM to fill in details
        llm_context = {
            "requirement": req.render(),
            "atom": atom.to_dict(),
            "template": template,
            "existing_code": await self._get_existing_code_context(req)
        }

        code_details = await self.llm.generate_code_details(llm_context)

        # Create UniversalItem in CODE view
        return UniversalItem(
            id=uuid4(),
            title=code_details["title"],
            view_type=ViewType.CODE,
            description=code_details["description"],
            status="scaffolded",
            created_by=user,
            metadata={
                "file_path": code_details["file_path"],
                "function_name": code_details["function_name"],
                "scaffolded": True,
                "template_used": template.name,
            }
        )

@dataclass
class CascadeGenerationResult:
    """Result of auto-generating items from requirement."""
    requirement_id: str
    generated_items: Dict[str, List['UniversalItem']] = field(default_factory=dict)  # view → items
    files_scaffolded: List[str] = field(default_factory=list)  # File paths
    links_created: int = 0
    errors: List[str] = field(default_factory=list)

    def summary(self) -> str:
        total_items = sum(len(items) for items in self.generated_items.values())
        views_affected = len(self.generated_items)

        return f"""
Generated {total_items} items across {views_affected} views
  - Files scaffolded: {len(self.files_scaffolded)}
  - Links created: {self.links_created}
  - Errors: {len(self.errors)}

Items by view:
{chr(10).join(f"  {view}: {len(items)} items" for view, items in self.generated_items.items())}
"""

---

## Event Sourcing Integration

### Atomic Requirement Events

```python
class AtomicRequirementEvent(Enum):
    """Event types for atomic requirements."""

    # Creation
    REQUIREMENT_CREATED = "requirement.created"

    # Atom changes
    ATOM_TOGGLED = "atom.toggled"
    ATOMS_BATCH_UPDATED = "atoms.batch_updated"

    # Implementation variants
    VARIANT_SET = "variant.set"
    VARIANT_TOGGLED = "variant.toggled"
    VARIANT_IMPLEMENTED = "variant.implemented"

    # Lifecycle
    REQUIREMENT_ACTIVATED = "requirement.activated"
    REQUIREMENT_DEACTIVATED = "requirement.deactivated"
    REQUIREMENT_ARCHIVED = "requirement.archived"

    # Cascade
    CASCADE_STARTED = "cascade.started"
    CASCADE_COMPLETED = "cascade.completed"
    CASCADE_FAILED = "cascade.failed"

@dataclass
class AtomToggledEvent:
    """Event emitted when atom is toggled in a requirement."""

    event_type: str = "atom.toggled"
    aggregate_id: str = ""  # Requirement ID
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user: str = ""

    # Event data
    atom_type: str = ""  # "subject", "action", "method", "interface"
    old_atom_id: Optional[str] = None
    new_atom_id: str = ""
    old_value: Optional[str] = None
    new_value: str = ""

    # Impact
    affected_requirements: List[str] = field(default_factory=list)
    affected_views: List[str] = field(default_factory=list)
    estimated_impact: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "timestamp": self.timestamp.isoformat(),
            "user": self.user,
            "atom_type": self.atom_type,
            "old_atom_id": self.old_atom_id,
            "new_atom_id": self.new_atom_id,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "affected_requirements": self.affected_requirements,
            "affected_views": self.affected_views,
            "estimated_impact": self.estimated_impact,
        }

### Event Handlers

```python
class AtomChangeHandler:
    """Handle atom toggle events with cascading updates."""

    async def handle(self, event: AtomToggledEvent):
        """Process atom toggle event.

        1. Analyze impact
        2. Generate update events for affected items
        3. Execute cascade (async)
        4. Validate results
        5. Notify stakeholders
        """
        # 1. Load requirement
        req = await self.requirements.find_by_id(event.aggregate_id)

        # 2. Reconstruct atom change
        atom_change = AtomChange(
            requirement_id=event.aggregate_id,
            atom_type=AtomType(event.atom_type),
            old_atom=await self.atoms.find_by_id(event.old_atom_id) if event.old_atom_id else None,
            new_atom=await self.atoms.find_by_id(event.new_atom_id),
            timestamp=event.timestamp
        )

        # 3. Analyze impact
        impact = await self.impact_analyzer.analyze(event.aggregate_id, atom_change)

        # 4. Execute cascade
        cascade_result = await self.cascade_engine.execute_cascade(
            requirement_id=event.aggregate_id,
            atom_change=atom_change,
            impact=impact,
            user=event.user,
            dry_run=False
        )

        # 5. Publish completion event
        await self.event_bus.publish("cascade.completed", {
            "requirement_id": event.aggregate_id,
            "items_updated": len(cascade_result.items_updated),
            "views_affected": len(set(item.view_type for item in cascade_result.items_updated)),
            "errors": cascade_result.errors
        })

        # 6. Notify stakeholders (if significant impact)
        if impact.estimated_risk in ["medium", "high"]:
            await self._notify_stakeholders(event, impact, cascade_result)

### NATS Stream Configuration for Atomic Events

```python
# NATS JetStream configuration for atomic requirement events
ATOMIC_REQUIREMENT_STREAM_CONFIG = {
    "name": "TRACE_ATOMIC_EVENTS",
    "subjects": [
        "TRACE_ATOMIC_EVENTS.requirement.>",  # All requirement events
        "TRACE_ATOMIC_EVENTS.atom.>",          # All atom events
        "TRACE_ATOMIC_EVENTS.cascade.>",       # All cascade events
    ],
    "retention": "limits",
    "max_age": timedelta(days=365),  # Keep events for 1 year
    "storage": "file",
    "replicas": 3,  # High availability
    "max_msgs": 100_000_000,  # 100M events
    "max_bytes": 50 * 1024 * 1024 * 1024,  # 50GB
    "discard": "old",
    "duplicate_window": timedelta(minutes=2),
}

# Consumer configuration
ATOMIC_CASCADE_CONSUMER = {
    "stream": "TRACE_ATOMIC_EVENTS",
    "durable_name": "atomic-cascade-processor",
    "filter_subject": "TRACE_ATOMIC_EVENTS.atom.toggled",
    "deliver_policy": "all",  # Process all events
    "ack_policy": "explicit",
    "ack_wait": 30,  # 30 seconds to process + ack
    "max_deliver": 3,  # Retry up to 3 times
}
```

---

## Performance Optimization

### Caching Strategy

```python
class AtomicRequirementCache:
    """Multi-layer caching for atomic requirements."""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.local_cache = LRUCache(maxsize=1000)

    async def get_requirement(self, req_id: str) -> Optional[AtomicRequirement]:
        """Get requirement with L1 (local) → L2 (Redis) → L3 (DB) cascade."""

        # L1: Local cache (fastest, <1ms)
        if req := self.local_cache.get(req_id):
            return req

        # L2: Redis cache (fast, <10ms)
        if cached := await self.redis.get(f"req:{req_id}"):
            req = AtomicRequirement.from_dict(json.loads(cached))
            self.local_cache[req_id] = req  # Populate L1
            return req

        # L3: Database (slow, ~50ms)
        req = await self.db.find_requirement(req_id)
        if req:
            # Populate L2 and L1
            await self.redis.setex(
                f"req:{req_id}",
                3600,  # 1 hour TTL
                json.dumps(req.to_dict())
            )
            self.local_cache[req_id] = req

        return req

    async def invalidate(self, req_id: str):
        """Invalidate caches when requirement changes."""
        self.local_cache.pop(req_id, None)
        await self.redis.delete(f"req:{req_id}")

### Materialized Views

```sql
-- Materialized view for fast requirement lookups by atom
CREATE MATERIALIZED VIEW requirements_by_atom AS
SELECT
    ar.id AS requirement_id,
    ar.title,
    ar.status,
    jsonb_array_elements(ar.atoms) AS atom,
    jsonb_extract_path_text(jsonb_array_elements(ar.atoms), 'type') AS atom_type,
    jsonb_extract_path_text(jsonb_array_elements(ar.atoms), 'value') AS atom_value
FROM atomic_requirements ar;

CREATE INDEX idx_req_by_atom_value ON requirements_by_atom(atom_value);

-- Refresh periodically (or on trigger)
REFRESH MATERIALIZED VIEW CONCURRENTLY requirements_by_atom;

-- Query: Find all requirements using oauth2 method atom
SELECT DISTINCT requirement_id, title
FROM requirements_by_atom
WHERE atom_type = 'method' AND atom_value = 'oauth2';
```

### Batch Processing

```python
async def batch_toggle_atoms(
    toggles: List[Tuple[str, AtomType, Atom]],  # (req_id, atom_type, new_atom)
    user: str
) -> 'BatchToggleResult':
    """Toggle multiple atoms in one operation (optimized).

    Instead of N cascades, compute combined impact and execute once.
    """
    result = BatchToggleResult()

    # 1. Compute combined impact
    combined_impact = ImpactAnalysisResult()

    for req_id, atom_type, new_atom in toggles:
        req = await requirements.find(req_id)
        old_atom = req.atoms.get(atom_type)

        atom_change = AtomChange(req_id, atom_type, old_atom, new_atom, datetime.utcnow())
        impact = await impact_analyzer.analyze(req_id, atom_change)

        # Merge impacts
        combined_impact.merge(impact)

    # 2. Deduplicate affected items (item may be affected by multiple toggles)
    combined_impact.deduplicate_items()

    # 3. Execute single cascade for all changes
    cascade_result = await cascade_engine.execute_batch_cascade(
        toggles=toggles,
        combined_impact=combined_impact,
        user=user
    )

    return BatchToggleResult(
        toggles_applied=len(toggles),
        items_updated=len(cascade_result.items_updated),
        errors=cascade_result.errors
    )
```

---

## API Design

### REST API Endpoints

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI(title="Trace Atomic Requirements API")

# ===== Atom Management =====

@app.get("/api/v1/atoms")
async def list_atoms(
    type: Optional[str] = None,
    scope: Optional[str] = None,
    limit: int = 100
):
    """List all atoms, optionally filtered by type or scope."""
    atoms = await atom_repository.find_all(
        type=AtomType(type) if type else None,
        scope=AtomScope(scope) if scope else None,
        limit=limit
    )
    return {"atoms": [a.to_dict() for a in atoms]}

@app.post("/api/v1/atoms")
async def create_atom(request: 'CreateAtomRequest'):
    """Create new atom."""
    atom = Atom(
        id=uuid4(),
        type=request.type,
        value=request.value,
        label=request.label,
        description=request.description,
        scope=request.scope
    )

    await atom_repository.save(atom)
    return {"atom": atom.to_dict()}

@app.get("/api/v1/atoms/{atom_id}/related")
async def get_related_atoms(atom_id: str, depth: int = 2):
    """Get all atoms related to this atom (transitively)."""
    atom = await atom_repository.find_by_id(UUID(atom_id))
    if not atom:
        raise HTTPException(404, "Atom not found")

    related_ids = find_all_related_atoms(atom, depth)
    related = await atom_repository.find_by_ids(list(related_ids))

    return {"related_atoms": [a.to_dict() for a in related]}

# ===== Atomic Requirement Management =====

@app.post("/api/v1/requirements")
async def create_requirement(request: 'CreateAtomicRequirementRequest'):
    """Create atomic requirement with auto-generation."""

    # Build AtomicRequirement
    req = AtomicRequirement(
        id=request.id or f"REQ-{uuid4().hex[:8]}",
        template=request.template,
        atoms={
            AtomType(k): await atom_repository.find_by_id(UUID(v))
            for k, v in request.atoms.items()
        },
        description=request.description,
        acceptance_criteria=request.acceptance_criteria,
    )

    # Auto-generate derived items
    result = await intelligent_crud.create_requirement_with_cascade(
        req, user=request.user
    )

    return {
        "requirement": req.to_dict(),
        "generation_result": result.summary()
    }

@app.put("/api/v1/requirements/{req_id}/atoms/{atom_type}")
async def toggle_atom(
    req_id: str,
    atom_type: str,
    request: 'ToggleAtomRequest'
):
    """Toggle an atom in a requirement (with impact preview).

    If preview=True, returns impact analysis without applying.
    If preview=False, applies changes and returns cascade result.
    """
    req = await requirement_repository.find_by_id(req_id)
    if not req:
        raise HTTPException(404, "Requirement not found")

    new_atom = await atom_repository.find_by_id(UUID(request.new_atom_id))
    if not new_atom:
        raise HTTPException(404, "Atom not found")

    # Create atom change
    atom_change = req.toggle_atom(AtomType(atom_type), new_atom)

    # Analyze impact
    impact = await impact_analyzer.analyze(req_id, atom_change)

    if request.preview:
        # Return impact analysis only (dry run)
        return {
            "preview": True,
            "impact": impact.summary(),
            "affected_items": {
                view: [str(item_id) for item_id in items]
                for view, items in impact.affected_items.items()
            },
            "estimated_effort_hours": impact.estimated_effort,
            "risk_level": impact.estimated_risk,
        }
    else:
        # Execute cascade
        cascade_result = await cascade_engine.execute_cascade(
            requirement_id=req_id,
            atom_change=atom_change,
            impact=impact,
            user=request.user,
            dry_run=False
        )

        return {
            "applied": True,
            "cascade_result": cascade_result.summary(),
            "errors": cascade_result.errors,
        }

@app.post("/api/v1/requirements/{req_id}/variants")
async def set_implementation_variant(
    req_id: str,
    request: 'SetVariantRequest'
):
    """Set active implementation variant for requirement."""
    req = await requirement_repository.find_by_id(req_id)
    if not req:
        raise HTTPException(404, "Requirement not found")

    # Set variant
    try:
        req.set_implementation_variant(request.variant_name)
    except ValueError as e:
        raise HTTPException(400, str(e))

    # Persist
    await requirement_repository.update(req)

    return {
        "requirement_id": req_id,
        "implementation_variant": req.implementation_variant,
        "implementation_status": req.implementation_status
    }

# ===== Product Derivation =====

@app.post("/api/v1/products/derive")
async def derive_product(request: 'DeriveProductRequest'):
    """Derive concrete product configuration from base + flags.

    Takes a deployment context (env, tenant) and evaluates all feature flags
    to produce the active set of requirements for that context.
    """
    context = EvalContext(
        env=request.env,
        tenant=request.tenant,
        user_id=request.user_id,
        custom_attrs=request.custom_attrs
    )

    # Get base requirements
    base_reqs = await requirement_repository.find_all()

    # Derive product
    product = await product_derivation_engine.derive_product(base_reqs, context)

    return {
        "context": {
            "env": context.env,
            "tenant": context.tenant,
        },
        "requirements": [r.to_dict() for r in product.requirements],
        "derived_at": product.derived_at.isoformat(),
        "total_requirements": len(product.requirements),
    }

# ===== Impact Analysis =====

@app.post("/api/v1/impact/analyze")
async def analyze_impact(request: 'AnalyzeImpactRequest'):
    """Analyze impact of proposed atom change."""

    # Build atom change
    atom_change = AtomChange(
        requirement_id=request.requirement_id,
        atom_type=AtomType(request.atom_type),
        old_atom=await atom_repository.find_by_id(UUID(request.old_atom_id)) if request.old_atom_id else None,
        new_atom=await atom_repository.find_by_id(UUID(request.new_atom_id)),
        timestamp=datetime.utcnow()
    )

    # Analyze
    impact = await impact_analyzer.analyze(request.requirement_id, atom_change)

    return {
        "impact": impact.summary(),
        "affected_requirements": impact.affected_requirements,
        "affected_items_by_view": {
            view: [str(item_id) for item_id in items]
            for view, items in impact.affected_items.items()
        },
        "required_migrations": impact.required_migrations,
        "required_config_changes": impact.required_config_changes,
        "estimated_effort_hours": impact.estimated_effort,
        "risk_level": impact.estimated_risk,
    }
```

### Request/Response Models

```python
class CreateAtomRequest(BaseModel):
    type: str  # "subject", "action", "method", "interface"
    value: str
    label: str
    description: str
    scope: str

class CreateAtomicRequirementRequest(BaseModel):
    id: Optional[str] = None
    template: str
    atoms: dict[str, str]  # atom_type → atom_id
    description: str = ""
    acceptance_criteria: List[str] = []
    user: str

class ToggleAtomRequest(BaseModel):
    new_atom_id: str
    preview: bool = False
    user: str

class SetVariantRequest(BaseModel):
    variant_name: str

class DeriveProductRequest(BaseModel):
    env: str
    tenant: str
    user_id: Optional[str] = None
    custom_attrs: dict[str, Any] = {}

class AnalyzeImpactRequest(BaseModel):
    requirement_id: str
    atom_type: str
    old_atom_id: Optional[str] = None
    new_atom_id: str
```

---

## Implementation Examples

### Example 1: Login Requirement with OAuth Toggle

**Initial State**:
```python
# Create atoms
user_atom = Atom(
    id=uuid4(),
    type=AtomType.SUBJECT,
    value="user",
    label="User",
    scope=AtomScope.AUTHENTICATION
)

login_atom = Atom(
    id=uuid4(),
    type=AtomType.ACTION,
    value="login",
    label="Login",
    scope=AtomScope.AUTHENTICATION,
    antonyms=["logout"]
)

email_password_atom = Atom(
    id=uuid4(),
    type=AtomType.METHOD,
    value="email-password",
    label="Email/Password",
    scope=AtomScope.AUTHENTICATION,
    implementations=["custom"],  # Only custom implementation exists
    default_implementation="custom"
)

web_atom = Atom(
    id=uuid4(),
    type=AtomType.INTERFACE,
    value="web-ui",
    label="Web UI",
    scope=AtomScope.USER_INTERFACE
)

# Create atomic requirement
fr_001 = AtomicRequirement(
    id="FR-001",
    template="[{subject}] can [{action}] with [{method}] via [{interface}]",
    atoms={
        AtomType.SUBJECT: user_atom,
        AtomType.ACTION: login_atom,
        AtomType.METHOD: email_password_atom,
        AtomType.INTERFACE: web_atom,
    },
    acceptance_criteria=[
        "User can submit email and password",
        "System validates credentials",
        "User is redirected to dashboard on success",
    ]
)

# Auto-generate across views
result = await intelligent_crud.create_requirement_with_cascade(fr_001, user="john@example.com")

# Generated items:
# - FEATURE view: "User can login with Email/Password via Web UI"
# - CODE view: src/auth/email_password_handler.py
# - TEST view: tests/auth/test_email_login.py
# - API view: POST /api/auth/login (with email+password schema)
# - DATABASE view: sessions table
# - WIREFRAME view: Login form with email/password fields
```

**Toggle to OAuth**:
```python
# Create OAuth atom
oauth_atom = Atom(
    id=uuid4(),
    type=AtomType.METHOD,
    value="oauth2",
    label="OAuth 2.0",
    scope=AtomScope.AUTHENTICATION,
    implementations=["auth0", "authkit"],  # Two implementations available
    default_implementation="auth0"
)

# Register implementations
auth0_variant = ImplementationVariant(
    id=uuid4(),
    atom_id=oauth_atom.id,
    name="auth0",
    display_name="Auth0",
    is_implemented=True,
    library="authlib",
    config_required={
        "AUTH0_DOMAIN": "your-tenant.auth0.com",
        "AUTH0_CLIENT_ID": "...",
        "AUTH0_CLIENT_SECRET": "...",
    },
    vendor="Auth0 Inc.",
    docs_url="https://auth0.com/docs"
)

# Toggle atom
atom_change = fr_001.toggle_atom(AtomType.METHOD, oauth_atom)

# Analyze impact
impact = await impact_analyzer.analyze("FR-001", atom_change)
# Impact shows: 3 code files, 2 tests, 1 API, 1 infra, 1 config affected

# Execute cascade
cascade_result = await cascade_engine.execute_cascade(
    requirement_id="FR-001",
    atom_change=atom_change,
    impact=impact,
    user="john@example.com"
)

# Result:
# - src/auth/email_password_handler.py → src/auth/oauth_handler.py
# - frontend/LoginForm.tsx → frontend/OAuthButton.tsx
# - POST /api/auth/login schema updated (authorization_code instead of email+password)
# - docker-compose.yml adds Auth0 mock service
# - .env adds AUTH0_* variables
```

### Example 2: Multi-Variant Support

**Scenario**: Support both Auth0 AND AuthKit (user can choose)

```python
# Instead of single requirement, create configurable requirement
oauth_req = AtomicRequirement(
    id="AUTH-001",
    template="[{subject}] can [{action}] with [{method}] via [{interface}]",
    atoms={
        AtomType.SUBJECT: user_atom,
        AtomType.ACTION: login_atom,
        AtomType.METHOD: oauth_atom,
        AtomType.INTERFACE: web_atom,
    },
    # KEY: This requirement has multiple valid implementations
    implementation_variant="auth0",  # Default
    flag_key="ff_oauth_provider"  # Feature flag controls which variant
)

# Create feature flag with strategies
oauth_provider_flag = FeatureFlag(
    key="ff_oauth_provider",
    name="OAuth Provider Selection",
    strategies=[
        FlagStrategy(
            name="tenant",
            parameters={"tenants": {"acme-corp": "authkit", "beta-users": "auth0"}}
        )
    ]
)

# Derive for different tenants
acme_context = EvalContext(env="production", tenant="acme-corp")
acme_product = await product_engine.derive_product([oauth_req], acme_context)
# → Uses authkit implementation

beta_context = EvalContext(env="production", tenant="beta-users")
beta_product = await product_engine.derive_product([oauth_req], beta_context)
# → Uses auth0 implementation
```

### Example 3: Future Implementation Flag

**Scenario**: Want to reference SAML but not implemented yet

```python
# Create SAML atom (exists conceptually)
saml_atom = Atom(
    id=uuid4(),
    type=AtomType.METHOD,
    value="saml",
    label="SAML 2.0 SSO",
    scope=AtomScope.AUTHENTICATION,
    implementations=[],  # EMPTY: no implementations yet
)

# Mark as future implementation
future_flag = await future_tracker.mark_as_future(
    atom=saml_atom,
    implementation_name="onelogin-saml",
    rationale="Enterprise customers requested SAML support"
)

# Create requirement referencing future atom
saml_req = AtomicRequirement(
    id="FR-050",
    template="[{subject}] can [{action}] with [{method}] via [{interface}]",
    atoms={
        AtomType.SUBJECT: user_atom,
        AtomType.ACTION: login_atom,
        AtomType.METHOD: saml_atom,  # Future atom
        AtomType.INTERFACE: web_atom,
    },
    implementation_status="flagged",  # Marked as future work
    flag_key="ff_saml_enabled"
)

# Attempt to derive for production (fails gracefully)
try:
    prod_config = await product_engine.derive_product([saml_req], prod_context)
except ConfigurationError as e:
    # "FR-050 uses unimplemented variant: saml"
    # Requirement excluded from production deployment
    pass

# Roadmap shows this as future work
roadmap = await future_tracker.generate_roadmap()
# Shows: Q2 2025: Implement onelogin-saml for FR-050
```

---

## Integration Summary

### Atomic Requirements + 16-View System

**Complete Flow**:
```
1. User creates AtomicRequirement with atoms
   ↓
2. IntelligentCRUDEngine analyzes atoms
   ↓
3. Generates UniversalItems in relevant views (CODE, TEST, API, etc.)
   ↓
4. Creates DerivedItem links (traceability)
   ↓
5. Scaffolds code files using templates
   ↓
6. Publishes events via NATS
   ↓
7. User toggles atom (e.g., email → oauth)
   ↓
8. ImpactAnalyzer computes affected items across all views
   ↓
9. CascadingUpdateEngine updates all items
   ↓
10. Events published; stakeholders notified
```

**Data Model Integration**:
```
AtomicRequirement (new)
  ↓ derives
UniversalItem (existing, in 16 views)
  ↓ links via
DerivedItem (new traceability layer)
  ↓ synchronized by
CascadingUpdateEngine (new)
  ↓ events via
NATS JetStream (existing)
  ↓ versioned by
Git-style commits (existing)
```

### Technology Stack

**Atomic Layer**:
- Python 3.12 (domain models)
- PostgreSQL JSONB (atom storage)
- Unleash (feature flags)
- sentence-transformers (NLP for duplicates)
- Claude API (LLM validation)

**Integration Layer**:
- Existing 16-view system (UniversalItem)
- Existing NATS event bus
- Existing git-style versioning
- Existing OpenSpec workflow

**Performance Targets**:
| Operation | Target | Strategy |
|-----------|--------|----------|
| Atom lookup | <5ms | L1 cache (LRU) |
| Requirement creation | <200ms | Async generation |
| Impact analysis | <500ms | Materialized views |
| Cascade execution | <5s | Async via NATS |
| Product derivation | <100ms | Flag evaluation cache |

---

## Conclusion

The **Atomic Trace Architecture** provides unprecedented flexibility for requirements management:

**Key Innovations**:
1. **Hyper-Granular Decomposition**: Break requirements into swappable atoms
2. **Cascading Updates**: Change one atom → updates ripple across all views automatically
3. **Runtime Configuration**: Feature flags enable/disable requirements without code changes
4. **Implementation Variants**: Multiple implementations per atom with runtime toggle
5. **Future Flags**: Reference unimplemented features in roadmap

**Integration with Existing System**:
- Extends 16-view system (no breaking changes)
- Uses existing NATS event bus
- Leverages git-style versioning
- Compatible with OpenSpec workflow

**Next Steps**:
1. Review this architecture with team
2. Create ATOMIC_IMPLEMENTATION_ROADMAP.md (phased rollout)
3. Build prototype (atoms + basic cascade, ~2 weeks)
4. Validate with 5-10 real requirements
5. Iterate based on feedback

**Estimated Effort**: 12 weeks (Phase 1-5) for full atomic system

---

**End of Architecture Document**
