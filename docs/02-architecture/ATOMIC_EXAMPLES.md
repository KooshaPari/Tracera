# Trace Atomic Requirements: Complete Examples

**Date**: 2025-11-20
**Purpose**: Concrete, end-to-end examples of atomic requirements system
**Audience**: Developers, product managers, AI agents

---

## Table of Contents

1. [Example 1: Authentication Requirement - Complete Lifecycle](#example-1-authentication-requirement)
2. [Example 2: E-Commerce Checkout - Complex Composition](#example-2-e-commerce-checkout)
3. [Example 3: Multi-Tenant SaaS - Product Line Configuration](#example-3-multi-tenant-saas)
4. [Example 4: Future Feature Planning](#example-4-future-feature-planning)
5. [Example 5: Cascading Updates Across 16 Views](#example-5-cascading-updates)
6. [Example 6: A/B Testing Requirements](#example-6-ab-testing)
7. [Example 7: Migration from Non-Atomic](#example-7-migration)

---

## Example 1: Authentication Requirement - Complete Lifecycle

### Scenario

Build a user authentication feature with:
- Initial implementation: Email/password
- Later: Migrate to OAuth 2.0 (Google)
- Enterprise variant: Add SAML support

### Step 1: Create Atoms

```bash
# Create Subject atom: User
$ trace atom create \
  --type subject \
  --value user \
  --label "User" \
  --scope authentication \
  --description "End user of the application"

✓ Created atom: user (UUID: a1b2c3d4-...)

# Create Action atom: login
$ trace atom create \
  --type action \
  --value login \
  --label "Login" \
  --scope authentication \
  --antonym logout \
  --description "Authenticate and establish session"

✓ Created atom: login (UUID: e5f6g7h8-...)

# Create Method atom: email-password
$ trace atom create \
  --type method \
  --value email-password \
  --label "Email and Password" \
  --scope authentication \
  --implementation custom \
  --description "Traditional email/password authentication"

✓ Created atom: email-password (UUID: i9j0k1l2-...)

# Create Interface atom: web-ui
$ trace atom create \
  --type interface \
  --value web-ui \
  --label "Web UI" \
  --scope user_interface \
  --description "Browser-based web interface"

✓ Created atom: web-ui (UUID: m3n4o5p6-...)
```

### Step 2: Create Atomic Requirement

```bash
$ trace req create --interactive

? Requirement ID: FR-001
? Template: [{subject}] can [{action}] with [{method}] via [{interface}]
? Subject atom: user
? Action atom: login
? Method atom: email-password
? Interface atom: web-ui
? Auto-generate derived items? Yes

Creating atomic requirement FR-001...

✓ Created requirement: FR-001
  Rendered: "User can login with Email and Password via Web UI"

Auto-generating items across views...

FEATURE view:
  ✓ Created: User Authentication Story
  ✓ Acceptance criteria:
     - User can enter email and password
     - System validates credentials against database
     - User is redirected to dashboard on success
     - Error message shown for invalid credentials

CODE view:
  ✓ Scaffolded: backend/auth/email_login_handler.py
  ✓ Scaffolded: frontend/components/LoginForm.tsx
  ✓ Scaffolded: backend/services/auth_service.py

TEST view:
  ✓ Scaffolded: tests/auth/test_email_login.py (unit)
  ✓ Scaffolded: tests/e2e/test_login_flow.spec.ts (e2e)

API view:
  ✓ Created: POST /api/auth/login
  ✓ Request schema: {"email": string, "password": string}
  ✓ Response schema: {"token": string, "user": object}

DATABASE view:
  ✓ Created: users table (email, password_hash, created_at)
  ✓ Created: sessions table (user_id, token, expires_at)
  ✓ Generated migration: 001_create_users_and_sessions.sql

INFRASTRUCTURE view:
  ✓ Created: Authentication service config
  ✓ Environment variables: PASSWORD_MIN_LENGTH=8

WIREFRAME view:
  ✓ Created: Login Screen wireframe
  ✓ Components: Email input, Password input, Submit button

DOCUMENT view:
  ✓ Generated: Authentication Guide (docs/auth/login.md)

Generation complete:
  - Items created: 12 (across 7 views)
  - Files scaffolded: 5
  - Migrations generated: 1
  - Trace links created: 12

Next steps:
  1. Review scaffolded files: trace req show FR-001 --derived
  2. Implement business logic in scaffolded files
  3. Run tests: uv run pytest
  4. Apply migration: trace migrate apply
```

### Step 3: View Scaffolded Code

```bash
$ cat backend/auth/email_login_handler.py
```

```python
"""
Email/Password Login Handler

Auto-generated from atomic requirement FR-001
Atoms: user (subject), login (action), email-password (method), web-ui (interface)

Generated: 2025-11-20
Status: SCAFFOLDED - Implement business logic below
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Login request with email and password."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response with session token."""
    token: str
    user: dict


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """Handle user login with email and password.

    Validates credentials and creates session.

    Linked to requirement: FR-001
    Atoms: user, login, email-password, web-ui
    """
    # TODO: Implement authentication logic
    # 1. Look up user by email
    # 2. Verify password hash
    # 3. Create session token
    # 4. Return token and user data

    raise HTTPException(
        status_code=501,
        detail="Authentication logic not yet implemented. See FR-001 for requirements."
    )
```

### Step 4: Implement Business Logic

```python
# Developer implements the scaffolded function
@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    """Handle user login with email and password."""

    # Authenticate user
    user = await auth_service.authenticate_with_email_password(
        request.email,
        request.password
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create session
    session = await auth_service.create_session(user.id)

    return LoginResponse(
        token=session.token,
        user=user.to_dict()
    )
```

### Step 5: Toggle to OAuth (Weeks Later)

```bash
# Product decision: Migrate to OAuth 2.0 (Google)

# First, create OAuth atom
$ trace atom create \
  --type method \
  --value oauth2-google \
  --label "Google OAuth 2.0" \
  --scope authentication \
  --implementation google-oauth \
  --related oauth2

✓ Created atom: oauth2-google (UUID: q7r8s9t0-...)

# Preview impact of toggle
$ trace atom toggle FR-001 --atom method --new oauth2-google --preview

Analyzing impact...

Requirement FR-001 will change:
  Old: "User can login with Email and Password via Web UI"
  New: "User can login with Google OAuth 2.0 via Web UI"

Affected items:
  CODE (3 items):
    - backend/auth/email_login_handler.py → backend/auth/oauth_google_handler.py
    - frontend/components/LoginForm.tsx → frontend/components/GoogleOAuthButton.tsx
    - backend/services/auth_service.py (logic updated)

  TEST (2 items):
    - tests/auth/test_email_login.py → tests/auth/test_oauth_google.py
    - tests/e2e/test_login_flow.spec.ts (updated scenarios)

  API (1 item):
    - POST /api/auth/login → POST /api/auth/oauth/google
    - Request schema: {"authorization_code": string}

  DATABASE (2 items):
    - users table: remove password_hash column
    - oauth_providers table: add new table
    - Migration: 005_migrate_to_oauth.sql

  INFRASTRUCTURE (1 item):
    - Add Google OAuth credentials:
      * GOOGLE_CLIENT_ID
      * GOOGLE_CLIENT_SECRET
      * GOOGLE_REDIRECT_URI

  DOCUMENT (1 item):
    - Update docs/auth/login.md with OAuth flow

Impact summary:
  - Requirements affected: 1 (FR-001)
  - Items affected: 10 (across 6 views)
  - Migrations required: 1
  - Config changes: 3 environment variables
  - Estimated effort: 4 hours
  - Risk level: medium

⚠️  WARNING: This is a BREAKING CHANGE
   - Removes password-based authentication
   - Requires database migration
   - Affects 10 existing items

Apply changes? [y/N/d (dry-run)]: d

# User chooses dry-run first
Executing cascade (DRY RUN)...

✓ (DRY RUN) Updated backend/auth/email_login_handler.py
✓ (DRY RUN) Updated frontend/components/LoginForm.tsx
✓ (DRY RUN) Updated tests/auth/test_email_login.py
✓ (DRY RUN) Generated migration: 005_migrate_to_oauth.sql
✓ (DRY RUN) Updated .env.example with GOOGLE_* variables

Dry run complete. No changes persisted.
Review generated files and run again with 'y' to apply.

# User reviews, then applies
$ trace atom toggle FR-001 --atom method --new oauth2-google

Apply changes? [y/N]: y

Executing cascade...

✓ Updated backend/auth/email_login_handler.py → backend/auth/oauth_google_handler.py
✓ Updated frontend/components/LoginForm.tsx → frontend/components/GoogleOAuthButton.tsx
✓ Updated backend/services/auth_service.py
✓ Updated tests/auth/test_email_login.py → tests/auth/test_oauth_google.py
✓ Updated tests/e2e/test_login_flow.spec.ts
✓ Updated POST /api/auth/login API spec
✓ Generated migration: migrations/005_migrate_to_oauth.sql
✓ Updated .env.example

Cascade complete:
  - Items updated: 10
  - Views affected: 6
  - Migrations generated: 1
  - Config updated: 3 variables

⚠️  ACTION REQUIRED:
  1. Review updated code files
  2. Implement OAuth business logic in oauth_google_handler.py
  3. Run tests: uv run pytest
  4. Apply migration: trace migrate apply 005
  5. Update .env with GOOGLE_* credentials
  6. Deploy to staging for testing

Cascade events published to NATS.
Stakeholders notified via email.
```

### Step 6: Add Implementation Variant (Auth0)

```bash
# Later, add Auth0 as alternative implementation

$ trace variant create \
  --atom oauth2-google \
  --name auth0 \
  --display-name "Auth0" \
  --library authlib \
  --config AUTH0_DOMAIN=your-tenant.auth0.com \
  --config AUTH0_CLIENT_ID=... \
  --config AUTH0_CLIENT_SECRET=... \
  --vendor "Auth0 Inc." \
  --docs "https://auth0.com/docs" \
  --implemented true

✓ Created implementation variant: auth0

# Now FR-001 can toggle between implementations
$ trace req set-variant FR-001 --variant auth0

✓ Set implementation variant for FR-001: auth0

Affected configuration:
  - GOOGLE_CLIENT_ID → AUTH0_CLIENT_ID
  - GOOGLE_CLIENT_SECRET → AUTH0_CLIENT_SECRET
  + AUTH0_DOMAIN

Code changes:
  - Update backend/auth/oauth_google_handler.py to use authlib
  - Update OAuth provider endpoint

Apply configuration changes? [y/N]: y

✓ Configuration updated
✓ Code placeholders updated (implement with Auth0 SDK)
```

---

## Example 2: E-Commerce Checkout - Complex Composition

### Scenario

Build complete checkout flow composed of multiple atomic requirements:
- Cart management
- Payment processing
- Order confirmation
- Email notification

### Step 1: Define Atoms for E-Commerce

```python
# Create atoms programmatically (Python API)
from trace.domain.atoms import Atom, AtomType, AtomScope

# Subject atoms
customer_atom = Atom(
    id=uuid4(),
    type=AtomType.SUBJECT,
    value="customer",
    label="Customer",
    scope=AtomScope.USER_INTERFACE
)

order_atom = Atom(
    id=uuid4(),
    type=AtomType.SUBJECT,
    value="order",
    label="Order",
    scope=AtomScope.DATA_STORAGE
)

# Action atoms
add_to_cart_atom = Atom(
    id=uuid4(),
    type=AtomType.ACTION,
    value="add-to-cart",
    label="Add to Cart",
    scope=AtomScope.USER_INTERFACE
)

checkout_atom = Atom(
    id=uuid4(),
    type=AtomType.ACTION,
    value="checkout",
    label="Checkout",
    scope=AtomScope.PAYMENT
)

complete_order_atom = Atom(
    id=uuid4(),
    type=AtomType.ACTION,
    value="complete-order",
    label="Complete Order",
    scope=AtomScope.PAYMENT
)

# Method atoms
credit_card_atom = Atom(
    id=uuid4(),
    type=AtomType.METHOD,
    value="credit-card",
    label="Credit Card",
    scope=AtomScope.PAYMENT,
    implementations=["stripe", "braintree"],
    default_implementation="stripe"
)

email_notification_atom = Atom(
    id=uuid4(),
    type=AtomType.METHOD,
    value="email-notification",
    label="Email Notification",
    scope=AtomScope.NOTIFICATION,
    implementations=["sendgrid", "ses"],
    default_implementation="sendgrid"
)

# Interface atoms
mobile_app_atom = Atom(
    id=uuid4(),
    type=AtomType.INTERFACE,
    value="mobile-app",
    label="Mobile App",
    scope=AtomScope.USER_INTERFACE
)

# Save all atoms
await atom_service.save_all([
    customer_atom, order_atom,
    add_to_cart_atom, checkout_atom, complete_order_atom,
    credit_card_atom, email_notification_atom,
    mobile_app_atom
])
```

### Step 2: Compose Atomic Requirements (Molecules)

```python
# Molecule 1: Add to Cart
add_to_cart_req = AtomicRequirement(
    id="ECOM-001",
    template="[{subject}] can [{action}] via [{interface}]",
    atoms={
        AtomType.SUBJECT: customer_atom,
        AtomType.ACTION: add_to_cart_atom,
        AtomType.INTERFACE: mobile_app_atom,
    },
    description="Customer can add products to shopping cart from mobile app",
    acceptance_criteria=[
        "Customer can tap 'Add to Cart' button on product detail screen",
        "Product is added to cart with quantity 1",
        "Cart icon badge updates to show item count",
        "Customer sees confirmation toast",
    ]
)

# Molecule 2: Checkout with Payment
checkout_req = AtomicRequirement(
    id="ECOM-002",
    template="[{subject}] can [{action}] with [{method}] via [{interface}]",
    atoms={
        AtomType.SUBJECT: customer_atom,
        AtomType.ACTION: checkout_atom,
        AtomType.METHOD: credit_card_atom,
        AtomType.INTERFACE: mobile_app_atom,
    },
    description="Customer can complete checkout with credit card payment",
    acceptance_criteria=[
        "Customer can enter credit card details (number, exp, CVV)",
        "Payment is processed via Stripe",
        "Order is created upon successful payment",
        "Customer receives order confirmation",
    ],
    implementation_variant="stripe",  # Use Stripe as payment processor
    dependencies=["ECOM-001"]  # Depends on add-to-cart
)

# Molecule 3: Order Confirmation
confirmation_req = AtomicRequirement(
    id="ECOM-003",
    template="[{subject}] receives [{action}] via [{method}]",
    atoms={
        AtomType.SUBJECT: customer_atom,
        AtomType.ACTION: complete_order_atom,  # "complete order" repurposed as "receive confirmation"
        AtomType.METHOD: email_notification_atom,
    },
    description="Customer receives order confirmation via email",
    acceptance_criteria=[
        "Email sent within 1 minute of order completion",
        "Email contains order summary and tracking link",
        "Email sent via SendGrid",
    ],
    implementation_variant="sendgrid",
    dependencies=["ECOM-002"]
)

# Create all molecules
await atomic_req_service.create_with_cascade(add_to_cart_req, user="product-manager@example.com")
await atomic_req_service.create_with_cascade(checkout_req, user="product-manager@example.com")
await atomic_req_service.create_with_cascade(confirmation_req, user="product-manager@example.com")
```

### Step 3: Compose Organism (Epic)

```python
# Organism: Complete checkout flow
checkout_flow_epic = AtomicRequirement(
    id="EPIC-001",
    template="Complete Checkout Flow",
    atoms={},  # Epics typically don't have direct atoms, they compose molecules
    description="End-to-end checkout experience for customers",
    children=["ECOM-001", "ECOM-002", "ECOM-003"],
    composition_rule="AND",  # All children must be implemented
)

await atomic_req_service.create(checkout_flow_epic, user="product-manager@example.com")

# System creates dependency graph:
# EPIC-001
#   ├─ ECOM-001 (Add to Cart)
#   ├─ ECOM-002 (Checkout) [depends on ECOM-001]
#   └─ ECOM-003 (Confirmation) [depends on ECOM-002]
```

### Step 4: Toggle Payment Method (Stripe → Braintree)

```bash
$ trace variant toggle ECOM-002 --from stripe --to braintree

Analyzing impact...

This will toggle payment implementation from Stripe to Braintree.

Affected items:
  CODE (2 items):
    - backend/payment/stripe_handler.py → backend/payment/braintree_handler.py
    - Update backend/services/payment_service.py (SDK calls)

  INFRASTRUCTURE (1 item):
    - docker-compose.yml: no changes (both use HTTP APIs)

  CONFIGURATION (3 changes):
    - STRIPE_SECRET_KEY → BRAINTREE_MERCHANT_ID
    - STRIPE_PUBLISHABLE_KEY → BRAINTREE_PUBLIC_KEY
    + BRAINTREE_PRIVATE_KEY

  TEST (2 items):
    - tests/payment/test_stripe.py → tests/payment/test_braintree.py
    - Update test fixtures with Braintree test cards

Estimated effort: 2 hours
Risk: low (both are payment SDKs, similar APIs)

Apply toggle? [y/N]: y

✓ Toggled payment variant: stripe → braintree
✓ Updated 5 items across 3 views
✓ Configuration updated (see .env.example)

⚠️  TODO:
  1. Install braintree library: uv add braintree
  2. Update .env with Braintree credentials
  3. Test payment flow in sandbox
```

---

## Example 3: Multi-Tenant SaaS - Product Line Configuration

### Scenario

Build SaaS with multiple product tiers:
- **Starter**: Email auth, basic features
- **Professional**: OAuth, advanced analytics
- **Enterprise**: SAML, SSO, audit logs, custom SLAs

### Step 1: Define Base Requirements (Product Line)

```python
# Base authentication requirement (configurable)
auth_base = AtomicRequirement(
    id="SAAS-AUTH-001",
    template="[{subject}] can [{action}] with [{method}] via [{interface}]",
    atoms={
        AtomType.SUBJECT: user_atom,
        AtomType.ACTION: login_atom,
        AtomType.METHOD: email_password_atom,  # Default method
        AtomType.INTERFACE: web_atom,
    },
    flag_key=None,  # Always included (mandatory)
)

# OAuth variant (optional, for Professional+)
auth_oauth = AtomicRequirement(
    id="SAAS-AUTH-002",
    template="[{subject}] can [{action}] with [{method}] via [{interface}]",
    atoms={
        AtomType.SUBJECT: user_atom,
        AtomType.ACTION: login_atom,
        AtomType.METHOD: oauth2_atom,
        AtomType.INTERFACE: web_atom,
    },
    flag_key="ff_oauth_enabled",  # Controlled by feature flag
    implementation_variant="auth0"
)

# SAML variant (optional, for Enterprise only)
auth_saml = AtomicRequirement(
    id="SAAS-AUTH-003",
    template="[{subject}] can [{action}] with [{method}] via [{interface}]",
    atoms={
        AtomType.SUBJECT: user_atom,
        AtomType.ACTION: login_atom,
        AtomType.METHOD: saml_atom,
        AtomType.INTERFACE: web_atom,
    },
    flag_key="ff_saml_enabled",  # Enterprise only
    implementation_status="flagged"  # Not yet implemented
)

# Audit logs (Enterprise only)
audit_logs = AtomicRequirement(
    id="SAAS-AUDIT-001",
    template="[{subject}] actions are logged to [{interface}]",
    atoms={
        AtomType.SUBJECT: user_atom,
        AtomType.ACTION: create_atom,  # Repurposed
        AtomType.INTERFACE: database_atom,
    },
    flag_key="ff_audit_logs_enabled"
)
```

### Step 2: Create Feature Flags for Tiers

```bash
# Starter tier: No flags (only base requirements active)

# Professional tier: Enable OAuth
$ trace flag create \
  --key ff_oauth_enabled \
  --name "OAuth Authentication" \
  --type permission \
  --default false \
  --strategy tenant --tenants "pro-tier-*,enterprise-tier-*"

✓ Created flag: ff_oauth_enabled
  - Enabled for: Professional and Enterprise tiers

# Enterprise tier: Enable SAML + audit logs
$ trace flag create \
  --key ff_saml_enabled \
  --name "SAML SSO" \
  --type permission \
  --default false \
  --strategy tenant --tenants "enterprise-tier-*"

$ trace flag create \
  --key ff_audit_logs_enabled \
  --name "Audit Logging" \
  --type permission \
  --default false \
  --strategy tenant --tenants "enterprise-tier-*"

✓ Created 2 flags for Enterprise tier
```

### Step 3: Derive Product Configurations

```bash
# Derive Starter tier configuration
$ trace product derive --env production --tenant starter-tier-acme --output acme-starter.json

Evaluating feature flags...
  ff_oauth_enabled: false (tenant not in target list)
  ff_saml_enabled: false
  ff_audit_logs_enabled: false

Active requirements: 15
  - SAAS-AUTH-001 (email/password login) ✓
  - SAAS-FEAT-001 to SAAS-FEAT-014 (basic features) ✓
  - SAAS-AUTH-002 (OAuth) ✗ EXCLUDED
  - SAAS-AUTH-003 (SAML) ✗ EXCLUDED
  - SAAS-AUDIT-001 (audit logs) ✗ EXCLUDED

✓ Saved configuration: acme-starter.json

# Derive Professional tier
$ trace product derive --env production --tenant pro-tier-beta --output beta-pro.json

Evaluating feature flags...
  ff_oauth_enabled: true ✓ (tenant matches "pro-tier-*")
  ff_saml_enabled: false
  ff_audit_logs_enabled: false

Active requirements: 23
  - SAAS-AUTH-001 (email/password) ✓
  - SAAS-AUTH-002 (OAuth) ✓ INCLUDED
  - SAAS-FEAT-001 to SAAS-FEAT-021 (basic + advanced features) ✓
  - SAAS-AUTH-003 (SAML) ✗ EXCLUDED
  - SAAS-AUDIT-001 ✗ EXCLUDED

✓ Saved configuration: beta-pro.json

# Derive Enterprise tier
$ trace product derive --env production --tenant enterprise-tier-megacorp --output megacorp-ent.json

Evaluating feature flags...
  ff_oauth_enabled: true ✓
  ff_saml_enabled: true ✓ (tenant matches "enterprise-tier-*")
  ff_audit_logs_enabled: true ✓

⚠️  WARNING: SAAS-AUTH-003 (SAML) is flagged as future implementation
   Status: planned, not yet implemented

Include in configuration anyway? [y/N]: y

Active requirements: 31
  - SAAS-AUTH-001 (email/password) ✓
  - SAAS-AUTH-002 (OAuth) ✓
  - SAAS-AUTH-003 (SAML) ✓ FUTURE (will fail validation)
  - SAAS-AUDIT-001 (audit logs) ✓
  - SAAS-FEAT-001 to SAAS-FEAT-027 ✓

✓ Saved configuration: megacorp-ent.json

⚠️  Validation warnings:
  - SAAS-AUTH-003: Future implementation (SAML not coded yet)
  - Generate roadmap: trace roadmap generate --future-flags
```

### Step 4: Export Environment Configurations

```bash
# Export as .env file for each tier
$ trace product export --config acme-starter.json --output deployments/acme-starter/.env

# Generates:
# TIER=starter
# TENANT=starter-tier-acme
# AUTH_METHODS=email-password
# FEATURES=basic
# PAYMENT_PROVIDER=stripe
# EMAIL_PROVIDER=sendgrid
# AUDIT_LOGS_ENABLED=false

$ trace product export --config megacorp-ent.json --output deployments/megacorp-ent/.env

# Generates:
# TIER=enterprise
# TENANT=enterprise-tier-megacorp
# AUTH_METHODS=email-password,oauth2,saml
# FEATURES=basic,advanced,enterprise
# PAYMENT_PROVIDER=stripe
# EMAIL_PROVIDER=sendgrid
# AUDIT_LOGS_ENABLED=true
# SAML_PROVIDER=onelogin  # Future implementation
# SAML_STATUS=planned     # Flagged as not implemented
```

### Step 5: Generate Roadmap for Future Features

```bash
$ trace roadmap generate --future-flags --output roadmap.md

Generated implementation roadmap:

## Q1 2025
- SAML SSO (SAAS-AUTH-003)
  Blocked by: SAML provider setup
  Blocking: 5 enterprise customer requirements
  Estimated effort: 40 hours
  Priority: high

## Q2 2025
- Advanced Analytics (SAAS-FEAT-028 to SAAS-FEAT-035)
  Blocked by: Data warehouse setup
  Priority: medium

✓ Roadmap saved: roadmap.md
```

---

## Example 3: Cascading Updates Across 16 Views

### Scenario

Toggle SUBJECT atom from [User] to [Agent] and observe cascade across all views.

### Initial State

```
FR-010: [User] can [execute task] via [API]

Derived items:
  FEATURE view: "User can execute task via API"
  CODE view: src/tasks/user_task_executor.py
  TEST view: tests/test_user_task_execution.py
  API view: POST /api/users/:id/tasks
  DATABASE view: user_tasks table
  WIREFRAME view: N/A (no UI)
  INFRASTRUCTURE view: Task execution service
  SEQUENCE view: User → API → Task Executor → DB
  ARCHITECTURE view: User layer → Service layer
  DOCUMENT view: docs/api/user-tasks.md
  DECISION view: ADR-015: User-initiated task execution
  RISK view: RISK-023: User can execute malicious tasks
  DEPENDENCY view: Depends on user authentication
  METRIC view: user_tasks_executed_total counter
  TIMELINE view: Sprint 12 delivery
  RESOURCE view: Task execution workers (10 workers)
```

### Toggle Action

```bash
$ trace atom toggle FR-010 --atom subject --new agent --preview

Analyzing impact across ALL 16 views...

Impact Analysis for FR-010:
  Atom toggle: subject: user → agent

Affected items by view:

1. FEATURE view (1 item):
   - Title: "User can execute task" → "Agent can execute task"
   - Description: Update "user" references to "agent"

2. CODE view (1 item):
   - File: src/tasks/user_task_executor.py → src/tasks/agent_task_executor.py
   - Class: UserTaskExecutor → AgentTaskExecutor
   - Parameters: user_id → agent_id

3. TEST view (1 item):
   - File: tests/test_user_task_execution.py → tests/test_agent_task_execution.py
   - Test data: create_test_user() → create_test_agent()

4. API view (1 item):
   - Endpoint: POST /api/users/:id/tasks → POST /api/agents/:id/tasks
   - Schema: user_id field → agent_id field

5. DATABASE view (1 item):
   - Table: user_tasks → agent_tasks
   - Migration: ALTER TABLE user_tasks RENAME TO agent_tasks;
               ALTER TABLE agent_tasks RENAME COLUMN user_id TO agent_id;

6. WIREFRAME view (0 items):
   - N/A (no UI components for API-only feature)

7. INFRASTRUCTURE view (1 item):
   - Service: user-task-service → agent-task-service
   - Container rename in docker-compose.yml

8. SEQUENCE view (1 item):
   - Diagram update: User actor → Agent actor

9. ARCHITECTURE view (1 item):
   - Component: User Task Layer → Agent Task Layer

10. DOCUMENT view (1 item):
    - File: docs/api/user-tasks.md → docs/api/agent-tasks.md
    - References: Update all "user" → "agent"

11. DECISION view (1 item):
    - ADR-015: Update rationale (agents, not users, execute tasks)

12. RISK view (1 item):
    - RISK-023: "User can execute malicious" → "Agent can execute malicious"
    - Mitigation: Update to reflect agent permissions model

13. DEPENDENCY view (1 item):
    - Dependency: "user authentication" → "agent authentication"

14. METRIC view (1 item):
    - Metric: user_tasks_executed_total → agent_tasks_executed_total

15. TIMELINE view (0 items):
    - No changes (delivery timeline unchanged)

16. RESOURCE view (1 item):
    - Resource: Task workers remain same (10 workers)

Total Impact:
  - Items affected: 14 (across 14 views)
  - Migrations: 1 (rename table and column)
  - Config changes: 0
  - Estimated effort: 6 hours
  - Risk: high (widespread naming changes)

Apply changes? [y/N/d]: d

# Dry run first
Executing (DRY RUN)...

✓ (DRY RUN) Renamed src/tasks/user_task_executor.py → src/tasks/agent_task_executor.py
✓ (DRY RUN) Updated class UserTaskExecutor → AgentTaskExecutor
✓ (DRY RUN) Updated tests/test_user_task_execution.py
✓ (DRY RUN) Updated API endpoint: POST /api/agents/:id/tasks
✓ (DRY RUN) Generated migration: 012_rename_user_tasks_to_agent_tasks.sql
✓ (DRY RUN) Updated 14 items across 14 views

Dry run complete. Review and apply with 'y'.
```

### Actual Application

```bash
$ trace atom toggle FR-010 --atom subject --new agent

Apply changes? [y/N]: y

Executing cascade...

[1/14] Updating FEATURE view...
✓ Updated item FEAT-010: "Agent can execute task via API"

[2/14] Updating CODE view...
✓ Renamed src/tasks/user_task_executor.py → src/tasks/agent_task_executor.py
✓ Updated class and function names

[3/14] Updating TEST view...
✓ Renamed tests/test_user_task_execution.py → tests/test_agent_task_execution.py
✓ Updated test fixtures

[4/14] Updating API view...
✓ Updated endpoint: POST /api/agents/:id/tasks
✓ Regenerated OpenAPI spec

[5/14] Updating DATABASE view...
✓ Generated migration: migrations/012_rename_user_tasks_to_agent_tasks.sql

[6/14] Updating INFRASTRUCTURE view...
✓ Updated docker-compose.yml service name

[7/14] Updating SEQUENCE view...
✓ Updated sequence diagram: User actor → Agent actor

[8/14] Updating ARCHITECTURE view...
✓ Updated architecture diagram layer

[9/14] Updating DOCUMENT view...
✓ Updated docs/api/agent-tasks.md

[10/14] Updating DECISION view...
✓ Updated ADR-015 rationale

[11/14] Updating RISK view...
✓ Updated RISK-023 description

[12/14] Updating DEPENDENCY view...
✓ Updated dependency reference

[13/14] Updating METRIC view...
✓ Renamed metric: agent_tasks_executed_total

[14/14] Updating RESOURCE view...
✓ No changes required

Cascade complete:
  ✓ 14 items updated across 14 views
  ✓ 1 migration generated
  ✓ 0 errors

Events published to NATS:
  - TRACE_ATOMIC_EVENTS.requirement.atom_changed
  - TRACE_EVENTS.CODE.updated (×1)
  - TRACE_EVENTS.TEST.updated (×1)
  - TRACE_EVENTS.API.updated (×1)
  - ... (×14 total)

⚠️  ACTION REQUIRED:
  1. Review updated files: git diff
  2. Run tests: uv run pytest
  3. Apply migration: trace migrate apply 012
  4. Update documentation if needed
  5. Commit changes: git add . && git commit -m "feat: Toggle subject atom user→agent for FR-010"
```

---

## Example 4: Future Feature Planning

### Scenario

Plan a feature that requires technology not yet available/implemented.

### Step 1: Create Future Atoms

```bash
# Want to support WebAuthn (biometric), but not implemented yet
$ trace atom create \
  --type method \
  --value webauthn \
  --label "WebAuthn (Biometric)" \
  --scope authentication \
  --implementation-status future \
  --target-date 2025-04-01

✓ Created atom: webauthn
⚠️  Marked as FUTURE IMPLEMENTATION (no code exists yet)

# Create requirement using future atom
$ trace req create --interactive

? ID: FR-099
? Template: [{subject}] can [{action}] with [{method}] via [{interface}]
? Subject: user
? Action: login
? Method: webauthn  # Future atom
? Interface: web-ui
? Auto-generate? Yes

⚠️  WARNING: Atom 'webauthn' is marked as future implementation
   This requirement will be flagged and excluded from production until implemented.

Continue? [y/N]: y

✓ Created FR-099: "User can login with WebAuthn (Biometric) via Web UI"
✓ Status: FLAGGED (future implementation)
✓ Flag key: ff_webauthn_enabled (auto-created, default: false)

Auto-generating items...

CODE view:
  ✓ Scaffolded: src/auth/webauthn_handler.py (STUB)
  ✓ Added TODO comments: "WebAuthn not yet implemented"

TEST view:
  ✓ Scaffolded: tests/auth/test_webauthn.py (PENDING)
  ✓ Tests marked as pytest.skip

DOCUMENT view:
  ✓ Created: docs/roadmap/webauthn.md
  ✓ Linked to roadmap planning

Generation complete:
  - Items created: 3 (CODE, TEST, DOCUMENT views only)
  - Files scaffolded: 2 (stubs)
  - Future flags: 1 (ff_webauthn_enabled)

This requirement is on the roadmap but not production-ready.
```

### Step 2: Generate Implementation Roadmap

```bash
$ trace roadmap generate --future-flags

Analyzing future implementation flags...

## Implementation Roadmap

### Q2 2025 (Apr-Jun)

**WebAuthn Biometric Authentication** (FR-099)
  - Atom: webauthn (METHOD)
  - Estimated effort: 40 hours
  - Priority: high
  - Blocked by: Browser API support, server library selection
  - Blocking: 3 customer requests

  Implementation tasks:
    1. Research WebAuthn libraries (Python: webauthn, py-webauthn)
    2. Implement registration flow
    3. Implement authentication flow
    4. Add browser compatibility checks
    5. Test on multiple devices/browsers
    6. Update documentation

  Dependencies:
    - py-webauthn library
    - HTTPS endpoints (WebAuthn requires secure context)
    - Session management updates

✓ Roadmap generated: roadmap.md
```

### Step 3: When WebAuthn is Implemented

```bash
# Developer finishes WebAuthn implementation
$ trace variant create \
  --atom webauthn \
  --name py-webauthn \
  --display-name "Python WebAuthn Library" \
  --library py-webauthn \
  --implemented true \
  --config WEBAUTHN_RP_ID=example.com \
  --config WEBAUTHN_RP_NAME="Example App"

✓ Created implementation variant: py-webauthn
✓ Marked as IMPLEMENTED

# Update future flag
$ trace future-flag complete <flag-id>

✓ Updated future implementation flag: planned → implemented

# Update requirement status
$ trace req update FR-099 --status active

Updating FR-099...
  Old status: flagged
  New status: active

Affected items:
  CODE: Remove STUB markers, implement logic
  TEST: Remove pytest.skip, enable tests

Apply updates? [y/N]: y

✓ FR-099 now active and production-ready
✓ Can include in next deployment

# Enable feature flag for rollout
$ trace flag update ff_webauthn_enabled --default true

✓ Feature flag enabled globally
✓ WebAuthn now available in all deployments
```

---

## Example 5: A/B Testing Requirements

### Scenario

Test two variants of payment flow to see which converts better.

### Setup

```bash
# Create two variants of checkout requirement

# Variant A: One-step checkout (current)
$ trace req create \
  --id ECOM-CHECKOUT-A \
  --template "[{subject}] can [{action}] with [{method}] via [{interface}]" \
  --atom subject=customer \
  --atom action=checkout-one-step \
  --atom method=credit-card \
  --atom interface=mobile-app \
  --flag-key ff_checkout_variant_a

# Variant B: Two-step checkout (test)
$ trace req create \
  --id ECOM-CHECKOUT-B \
  --template "[{subject}] can [{action}] with [{method}] via [{interface}]" \
  --atom subject=customer \
  --atom action=checkout-two-step \
  --atom method=credit-card \
  --atom interface=mobile-app \
  --flag-key ff_checkout_variant_b

# Create A/B test flag (gradual rollout)
$ trace flag create \
  --key ff_checkout_variant_b \
  --name "Checkout Variant B (Two-Step)" \
  --type experimental \
  --default false \
  --strategy gradual-rollout --percentage 50 \
  --expires-at 2025-02-01

✓ Created experimental flag with 50% rollout
✓ Flag auto-expires on 2025-02-01

# Configure variants as mutually exclusive
$ trace flag create \
  --key ff_checkout_variant_a \
  --name "Checkout Variant A (One-Step)" \
  --type experimental \
  --default true \  # Default variant
  --strategy custom --expression "not context.flags.ff_checkout_variant_b"

✓ Created flag: variant A active when variant B is not
```

### Deploy A/B Test

```bash
# Derive product for user cohort A (50% get variant A)
$ trace product derive --env production --tenant app-users --user-id user-12345

Evaluating flags...
  ff_checkout_variant_a: true (user hash: 42, < 50)
  ff_checkout_variant_b: false

Active requirements:
  - ECOM-CHECKOUT-A ✓ (one-step checkout)

✓ User user-12345 gets Variant A

# Derive for user cohort B
$ trace product derive --env production --tenant app-users --user-id user-67890

Evaluating flags...
  ff_checkout_variant_b: true (user hash: 73, >= 50)
  ff_checkout_variant_a: false

Active requirements:
  - ECOM-CHECKOUT-B ✓ (two-step checkout)

✓ User user-67890 gets Variant B
```

### Analyze Results

```bash
# After 2 weeks, analyze metrics
$ trace flag analyze ff_checkout_variant_b

A/B Test Results (2 weeks):

Variant A (One-Step Checkout):
  - Users: 5,234
  - Conversions: 892 (17.0%)
  - Avg. time to checkout: 45 seconds
  - Drop-off rate: 12%

Variant B (Two-Step Checkout):
  - Users: 5,189
  - Conversions: 1,048 (20.2%)  # 3.2% higher ✓
  - Avg. time to checkout: 62 seconds
  - Drop-off rate: 8%  # 4% lower ✓

Recommendation: Variant B performs better (3.2% conversion lift)
  - Statistical significance: p < 0.05 ✓
  - Confidence: 95%

Suggested action:
  1. Roll out Variant B to 100%
  2. Deprecate Variant A
  3. Remove ff_checkout_variant_a flag

# Roll out winner
$ trace flag update ff_checkout_variant_b --percentage 100

✓ Variant B rolled out to 100% of users

# Schedule cleanup (remove losing variant)
$ trace req archive ECOM-CHECKOUT-A --reason "Lost A/B test to Variant B"

✓ Archived ECOM-CHECKOUT-A
✓ Associated items marked as deprecated
✓ Flag ff_checkout_variant_a scheduled for removal
```

---

## Example 6: Batch Operations with Template

### Scenario

Generate complete CRUD feature for "Product" entity using atomic template.

```bash
$ trace batch create --template crud --entity Product --atoms-auto

Analyzing entity: Product

Inferring atoms...
  Subject: product (auto-created)
  Actions: create, read, update, delete (from template)
  Methods: rest-api, form-input (from template)
  Interfaces: web-ui, rest-api (from template)

Creating atomic requirements...

✓ Created PRODUCT-CRUD-001: [user] can [create] [product] via [web-ui]
✓ Created PRODUCT-CRUD-002: [user] can [read] [product] via [web-ui]
✓ Created PRODUCT-CRUD-003: [user] can [update] [product] via [web-ui]
✓ Created PRODUCT-CRUD-004: [user] can [delete] [product] via [web-ui]
✓ Created PRODUCT-CRUD-005: [api-client] can [create] [product] via [rest-api]
✓ Created PRODUCT-CRUD-006: [api-client] can [read] [product] via [rest-api]
✓ Created PRODUCT-CRUD-007: [api-client] can [update] [product] via [rest-api]
✓ Created PRODUCT-CRUD-008: [api-client] can [delete] [product] via [rest-api]

Auto-generating items across 16 views...

CODE view (12 files scaffolded):
  ✓ backend/models/product.py (SQLAlchemy model)
  ✓ backend/repositories/product_repository.py (CRUD)
  ✓ backend/services/product_service.py (business logic)
  ✓ backend/api/products.py (FastAPI routes)
  ✓ frontend/components/ProductList.tsx
  ✓ frontend/components/ProductForm.tsx
  ✓ frontend/components/ProductDetail.tsx
  ✓ frontend/api/products.ts (API client)
  ✓ frontend/hooks/useProducts.ts
  ✓ frontend/hooks/useProduct.ts
  ✓ frontend/hooks/useCreateProduct.ts
  ✓ frontend/hooks/useUpdateProduct.ts

TEST view (8 files scaffolded):
  ✓ tests/models/test_product.py
  ✓ tests/repositories/test_product_repository.py
  ✓ tests/services/test_product_service.py
  ✓ tests/api/test_products.py
  ✓ tests/components/ProductList.test.tsx
  ✓ tests/components/ProductForm.test.tsx
  ✓ tests/components/ProductDetail.test.tsx
  ✓ tests/e2e/test_product_crud.spec.ts

API view (8 endpoints created):
  ✓ GET /api/products (list)
  ✓ GET /api/products/:id (get)
  ✓ POST /api/products (create)
  ✓ PUT /api/products/:id (update)
  ✓ DELETE /api/products/:id (delete)
  ✓ PATCH /api/products/:id (partial update)
  ✓ GET /api/products/search (search)
  ✓ GET /api/products/:id/history (audit trail)

DATABASE view (1 migration):
  ✓ Generated migration: 013_create_products_table.sql
    CREATE TABLE products (
      id UUID PRIMARY KEY,
      name TEXT NOT NULL,
      description TEXT,
      price DECIMAL(10,2) NOT NULL,
      created_at TIMESTAMPTZ DEFAULT now(),
      updated_at TIMESTAMPTZ DEFAULT now()
    );

WIREFRAME view (3 screens):
  ✓ Product List Screen
  ✓ Product Form Screen (create/edit)
  ✓ Product Detail Screen

DOCUMENT view (4 docs):
  ✓ docs/api/products.md (API reference)
  ✓ docs/models/product.md (data model)
  ✓ docs/ui/product-screens.md (UI guide)
  ✓ docs/tutorials/managing-products.md

Batch creation complete:
  - Atomic requirements: 8
  - Items generated: 47 (across 8 views)
  - Files scaffolded: 20
  - API endpoints: 8
  - Migrations: 1
  - Documentation: 4 files

Estimated time to implement: 2 days
  (scaffolding done, business logic needs implementation)

Next steps:
  1. Review scaffolded code: ls -R backend/ frontend/
  2. Implement business logic (TODOs in code)
  3. Run tests: uv run pytest
  4. Apply migration: trace migrate apply 013
  5. Test CRUD flow: trace test e2e
```

---

## Example 7: Migrating from Non-Atomic Requirement

### Scenario

Existing requirement written in traditional format needs migration to atomic.

### Before (Traditional Requirement)

```
ID: REQ-042
Title: Admin Dashboard Access Control
Description:
  Administrators must be able to log in to the admin dashboard using
  their company email and password. Upon successful authentication,
  they should have access to user management, analytics, and system
  configuration features. The dashboard should only be accessible via
  the web interface and should enforce IP whitelist restrictions for
  security.

Acceptance Criteria:
  - Admin can log in with email/password
  - Admin sees dashboard after login
  - Dashboard shows: user management, analytics, config
  - Only accessible from whitelisted IPs
  - Session expires after 1 hour of inactivity
```

### Migration Process

```bash
# Use LLM to assist migration
$ trace migrate to-atomic REQ-042 --llm-assist

Analyzing REQ-042 with LLM...

LLM Decomposition Proposal:

Detected atoms:
  Subject: admin (confidence: 0.95)
  Action: login (confidence: 0.98)
  Method: email-password (confidence: 0.92)
  Interface: web-ui (confidence: 0.90)

Additional constraints detected:
  - IP whitelist (security constraint)
  - Session timeout: 1 hour (configuration)
  - Post-login features: user mgmt, analytics, config

Proposed atomic structure:

Primary requirement (login):
  FR-042-A: [admin] can [login] with [email-password] via [web-ui]
  Constraints:
    - IP must be in whitelist
    - Session expires after 1 hour

Derived requirements (features):
  FR-042-B: [admin] can [manage users] via [web-ui]
  FR-042-C: [admin] can [view analytics] via [web-ui]
  FR-042-D: [admin] can [configure system] via [web-ui]

Parent epic:
  EPIC-042: Admin Dashboard Access

Accept decomposition? [y/N/e (edit)]: y

Creating atomic requirements...

✓ Created FR-042-A: "Admin can login with Email and Password via Web UI"
  Constraints: IP whitelist, session timeout (1 hour)

✓ Created FR-042-B: "Admin can manage users via Web UI"
  Depends on: FR-042-A

✓ Created FR-042-C: "Admin can view analytics via Web UI"
  Depends on: FR-042-A

✓ Created FR-042-D: "Admin can configure system via Web UI"
  Depends on: FR-042-A

✓ Created EPIC-042: Admin Dashboard Access
  Children: FR-042-A, FR-042-B, FR-042-C, FR-042-D
  Composition: AND (all required)

Auto-generating items...

[Generates items across all views for each requirement]

Migration complete:
  - Original requirement: REQ-042 (archived)
  - Atomic requirements: 5 (1 epic + 4 molecules)
  - Items generated: 52 (across 10 views)
  - Files scaffolded: 18
  - Dependency graph established

Old REQ-042 linked to new FR-042-* with "migrated_to" relationship.
```

---

## Example 8: CLI Workflow - Day in the Life

### Morning: Create New Feature

```bash
# Product manager starts day
$ trace atom list --recent

Recent atoms (last 7 days):
  - oauth2-google (method) - added yesterday
  - mobile-app (interface) - added 3 days ago
  - export-csv (action) - added 5 days ago

# Create new requirement
$ trace req create \
  --id FEAT-201 \
  --template "[{subject}] can [{action}] with [{method}] via [{interface}]" \
  --atom subject=customer \
  --atom action=export-data \
  --atom method=csv-format \
  --atom interface=web-ui \
  --auto-generate

✓ Created FEAT-201: "Customer can export data with CSV format via Web UI"
✓ Auto-generated 8 items across 5 views
✓ Scaffolded 3 code files

# Assign to developer
$ trace req assign FEAT-201 --to dev@example.com

✓ Assigned FEAT-201 to dev@example.com
✓ Notification sent
```

### Midday: Developer Reviews and Implements

```bash
# Developer checks assigned requirements
$ trace req list --assigned-to me --status scaffolded

Assigned to you:
  1. FEAT-201: Customer can export data (scaffolded, 3 hours ago)

# View generated code
$ trace req show FEAT-201 --code

CODE view items (3):
  1. backend/export/csv_exporter.py
     Status: SCAFFOLDED
     TODOs: 5

  2. frontend/components/ExportButton.tsx
     Status: SCAFFOLDED
     TODOs: 2

  3. backend/services/export_service.py
     Status: SCAFFOLDED
     TODOs: 8

# Open in editor (hooks into $EDITOR)
$ trace code edit FEAT-201

# Developer implements business logic...
# (opens all 3 files in VS Code)

# Run tests
$ uv run pytest tests/export/

tests/export/test_csv_exporter.py::test_export_generates_csv ✓
tests/export/test_csv_exporter.py::test_export_handles_large_datasets ✓
tests/export/test_csv_exporter.py::test_export_validates_permissions ✓

# Update requirement status
$ trace req update FEAT-201 --status implemented

✓ Updated FEAT-201 status: scaffolded → implemented
✓ Notified product manager
```

### Afternoon: Product Manager Toggles Atom

```bash
# Product decision: Also support JSON export
$ trace atom create \
  --type method \
  --value json-format \
  --label "JSON Format" \
  --scope data_export \
  --related csv-format

✓ Created atom: json-format

# Create variation of requirement
$ trace req clone FEAT-201 --new-id FEAT-202 \
  --toggle method=json-format

Cloning FEAT-201 with atom toggle...

✓ Created FEAT-202: "Customer can export data with JSON format via Web UI"
✓ Auto-generated 8 items (cloned from FEAT-201 with JSON variant)
✓ Scaffolded code references FEAT-201 implementation (DRY)

Generation used smart cloning:
  - backend/export/json_exporter.py extends BaseExporter (from csv_exporter)
  - Tests reuse fixtures from CSV tests
  - Frontend reuses ExportButton with format selector

Estimated time to implement: 1 hour (reuses 80% of CSV logic)
```

### Evening: Review Day's Work

```bash
# View all changes today
$ trace log --since today --atomic

Today's changes:
  09:15 - Created FEAT-201 (Customer export CSV)
  09:16 - Auto-generated 8 items across 5 views
  14:32 - Updated FEAT-201: scaffolded → implemented
  16:45 - Created json-format atom
  16:47 - Created FEAT-202 (Customer export JSON) via clone+toggle

  Atoms created: 1
  Requirements created: 2
  Items generated: 16
  Files scaffolded: 6

# Commit changes
$ trace commit -m "feat: Add customer data export (CSV and JSON variants)"

✓ Committed 16 items across 5 views
✓ Version: v0.2.0 (minor bump, new features)
✓ Semantic version auto-detected from commit message
```

---

## Example 9: Implementation Variant Toggle in Production

### Scenario

Switch payment processor from Stripe to Braintree in production (zero downtime).

### Step 1: Register Braintree Variant

```bash
# Braintree implementation is ready
$ trace variant create \
  --atom credit-card \
  --name braintree \
  --display-name "Braintree" \
  --implemented true \
  --library braintree \
  --config BRAINTREE_MERCHANT_ID=... \
  --config BRAINTREE_PUBLIC_KEY=... \
  --config BRAINTREE_PRIVATE_KEY=... \
  --vendor "PayPal (Braintree)" \
  --docs "https://developer.paypal.com/braintree/docs"

✓ Created implementation variant: braintree

Current variants for credit-card atom:
  - stripe (active) ✓
  - braintree (inactive, ready to toggle)
```

### Step 2: Test Braintree in Staging

```bash
# Create feature flag for progressive rollout
$ trace flag create \
  --key ff_payment_braintree \
  --name "Braintree Payment Processor" \
  --type operational \
  --default false \
  --strategy environment --envs staging

✓ Created flag: ff_payment_braintree (enabled in staging only)

# Deploy to staging
$ trace product derive --env staging --tenant test --output staging.env

✓ Braintree enabled in staging (flag evaluated to true)

# Run integration tests against staging
$ ENVIRONMENT=staging uv run pytest tests/integration/test_payment_braintree.py

tests/integration/test_payment_braintree.py::test_charge_card ✓
tests/integration/test_payment_braintree.py::test_refund ✓
tests/integration/test_payment_braintree.py::test_webhook_processing ✓

✓ All Braintree tests pass in staging
```

### Step 3: Progressive Rollout to Production

```bash
# Gradual rollout: 10% of production traffic
$ trace flag update ff_payment_braintree \
  --strategy gradual-rollout --percentage 10 \
  --env production

✓ Updated flag: 10% rollout in production

# Monitor metrics
$ trace flag metrics ff_payment_braintree --live

Live Metrics (refreshing every 5s):

  Time    | Evaluations | True | False | Error Rate | Avg Latency |
  --------|-------------|------|-------|------------|-------------|
  10:00   | 1,234       | 123  | 1,111 | 0.0%       | 45ms        |
  10:05   | 2,456       | 245  | 2,211 | 0.1%       | 47ms        |
  10:10   | 3,678       | 367  | 3,311 | 0.0%       | 44ms        |

  Braintree Performance:
    - Success rate: 99.9% (vs Stripe: 99.8%) ✓
    - Avg charge time: 1.2s (vs Stripe: 1.5s) ✓ 20% faster
    - Errors: 1 (vs Stripe: 3 expected)

  Recommendation: Performance equal or better. Safe to increase rollout.

# Increase to 50%
$ trace flag update ff_payment_braintree --percentage 50

✓ Rollout increased to 50%

# After 24 hours of successful operation, go to 100%
$ trace flag update ff_payment_braintree --percentage 100

✓ Braintree now active for 100% of production traffic

# Deprecate Stripe variant
$ trace variant update credit-card/stripe --status deprecated

✓ Marked Stripe as deprecated
✓ Braintree is now the default implementation
```

---

## Complete API Usage Example

### Python API

```python
from trace.application.services import (
    AtomService,
    AtomicRequirementService,
    ImpactAnalyzer,
    CascadingUpdateEngine,
    IntelligentCRUDEngine,
    ProductDerivationEngine,
)
from trace.domain.atoms import Atom, AtomType, AtomScope
from trace.domain.atomic_requirements import AtomicRequirement, EvalContext

# Initialize services
atom_service = AtomService(atom_repository, event_store)
req_service = AtomicRequirementService(requirement_repository, event_store)
impact_analyzer = ImpactAnalyzer(requirement_repository, item_repository, mapping_repository)
cascade_engine = CascadingUpdateEngine(event_store, item_repository, event_bus)
intelligent_crud = IntelligentCRUDEngine(item_repository, template_library, llm_client)
product_engine = ProductDerivationEngine(requirement_repository, flag_service)

# Create atom
user_atom = Atom(
    id=uuid4(),
    type=AtomType.SUBJECT,
    value="user",
    label="User",
    scope=AtomScope.AUTHENTICATION
)
await atom_service.create(user_atom)

# Create atomic requirement
req = AtomicRequirement(
    id="FR-001",
    template="[{subject}] can [{action}] with [{method}] via [{interface}]",
    atoms={
        AtomType.SUBJECT: user_atom,
        AtomType.ACTION: login_atom,
        AtomType.METHOD: email_password_atom,
        AtomType.INTERFACE: web_atom,
    }
)

# Auto-generate across views
generation_result = await intelligent_crud.create_requirement_with_cascade(
    req, user="api-user@example.com"
)

print(generation_result.summary())
# Generated 12 items across 7 views
# - Files scaffolded: 5
# - Links created: 12

# Toggle atom
atom_change = req.toggle_atom(AtomType.METHOD, oauth_atom)

# Analyze impact
impact = await impact_analyzer.analyze("FR-001", atom_change)
print(impact.summary())
# {
#   "requirements_affected": 1,
#   "items_affected": 10,
#   "views_affected": ["CODE", "TEST", "API", "DATABASE", "INFRASTRUCTURE", "DOCUMENT"],
#   "estimated_effort_hours": 4,
#   "risk_level": "medium"
# }

# Execute cascade
cascade_result = await cascade_engine.execute_cascade(
    requirement_id="FR-001",
    atom_change=atom_change,
    impact=impact,
    user="api-user@example.com",
    dry_run=False
)

print(cascade_result.summary())
# {
#   "items_updated": 10,
#   "views_affected": 6,
#   "migrations": 0,
#   "errors": []
# }

# Derive product configuration
context = EvalContext(env="production", tenant="enterprise-corp")
product = await product_engine.derive_product(all_requirements, context)

print(f"Active requirements: {len(product.requirements)}")
# Active requirements: 87 (out of 120 base requirements)

# Export configuration
product.export_to_env_file("deployments/enterprise-corp/.env")
# Generated .env file with all resolved implementation variants
```

---

## Summary of Examples

### Examples Covered

1. **Authentication Lifecycle**: Create → Auto-generate → Toggle → Variant switch
2. **E-Commerce Checkout**: Complex composition with molecules and organisms
3. **Multi-Tenant SaaS**: Product line configuration with feature flags
4. **Future Planning**: Flag unimplemented features for roadmap
5. **Cascading Updates**: 16-view update from single atom toggle
6. **A/B Testing**: Experimental flags with gradual rollout
7. **Migration**: Convert traditional requirement to atomic format
8. **Batch CRUD**: Generate complete feature with template
9. **Production Toggle**: Zero-downtime implementation variant switch
10. **API Usage**: Complete Python API examples

### Key Takeaways

**Atomic Requirements Enable**:
- ✅ **Extreme Flexibility**: Swap any component independently
- ✅ **Auto-Generation**: Scaffold 80% of boilerplate across 16 views
- ✅ **Impact Visibility**: Always know what changes affect
- ✅ **Product Lines**: Single codebase, multiple configurations
- ✅ **Progressive Delivery**: A/B test, gradual rollout, feature flags
- ✅ **Future Planning**: Reference unimplemented features in roadmap
- ✅ **Zero Downtime**: Toggle implementations without code deployment

**Complexity Trade-Offs**:
- ⚠️ **Setup Overhead**: Requires atom library definition
- ⚠️ **Learning Curve**: New mental model for requirements
- ⚠️ **Cascade Complexity**: Large changes affect many items
- ⚠️ **Validation Needed**: Ensure cascades don't break constraints

**Mitigation**:
- Start with 10-20 core atoms (grow organically)
- Provide interactive wizards (CLI)
- Preview mode for all cascades (dry run)
- Automated validation at every step

---

## Next Steps

1. **Try the Examples**: Follow examples 1-3 to build intuition
2. **Extend Atom Library**: Add atoms for your domain (fintech, healthcare, etc.)
3. **Create Templates**: Build reusable templates for common patterns
4. **Integrate with CI/CD**: Auto-validate on PR, auto-generate on requirement change
5. **Measure Impact**: Track metrics (reuse rate, generation success rate, cascade time)

---

**End of Examples Document**
