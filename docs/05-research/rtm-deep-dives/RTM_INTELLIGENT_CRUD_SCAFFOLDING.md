# Intelligent CRUD with Auto-Scaffolding & View-Aware Generation

## Core Concept

**When you create/edit/extend an item in ANY view, the system automatically:**
1. Generates related items in other views
2. Creates appropriate links
3. Scaffolds boilerplate code/tests/configs
4. Maintains consistency across all views

## Auto-Generation by View

### 1. Feature View → Auto-Generate Everything

**Scenario**: Create a new user story

```bash
rtm create story --title "User can export data to CSV"
```

**System Auto-Generates**:

```
✓ Created STORY-108: User can export data to CSV

Auto-generating related items...

Wireframe View:
  ✓ Created SCREEN-EXPORT: Export screen
  ✓ Created COMPONENT-EXPORT-BUTTON: Export button
  ✓ Created COMPONENT-FORMAT-SELECTOR: Format selector

Code View:
  ✓ Scaffolded backend/export/csv_exporter.py
  ✓ Scaffolded frontend/components/ExportButton.tsx
  ✓ Scaffolded frontend/components/FormatSelector.tsx

API View:
  ✓ Created POST /api/export/csv endpoint
  ✓ Generated OpenAPI spec

Test View:
  ✓ Scaffolded tests/test_csv_export.py
  ✓ Scaffolded tests/e2e/test_export_flow.spec.ts

Database View:
  ✓ Created export_jobs table (migration pending)

Configuration View:
  ✓ Added export.max_rows config (default: 10000)
  ✓ Added export.timeout config (default: 30s)

Links created: 12
Files scaffolded: 6
Migrations pending: 1

Next steps:
  1. Review scaffolded code
  2. Implement business logic
  3. Run: rtm scaffold apply
```

### 2. Wireframe View → Auto-Generate Implementation

**Scenario**: Create a new UI component

```bash
rtm create component --parent SCREEN-DASHBOARD --title "User Activity Chart"
```

**System Auto-Generates**:

```
✓ Created COMPONENT-ACTIVITY-CHART: User Activity Chart

Auto-generating implementation...

Code View:
  ✓ Scaffolded frontend/components/ActivityChart.tsx
    - Props interface
    - Component skeleton
    - Styling file
  ✓ Scaffolded frontend/hooks/useActivityData.ts
    - Data fetching hook
    - Loading/error states

API View:
  ✓ Created GET /api/analytics/activity endpoint
  ✓ Generated TypeScript types

Test View:
  ✓ Scaffolded tests/components/ActivityChart.test.tsx
    - Render test
    - Data loading test
    - Error handling test

Feature View:
  ✓ Linked to STORY-106: Display user metrics

Configuration View:
  ✓ Added analytics.refresh_interval config

Files scaffolded: 5
Tests scaffolded: 3
```

### 3. API View → Auto-Generate Full Stack

**Scenario**: Create a new API endpoint

```bash
rtm create endpoint --service UserService --path "/api/users/:id/preferences" --method PUT
```

**System Auto-Generates**:

```
✓ Created ENDPOINT-USER-PREFS: PUT /api/users/:id/preferences

Auto-generating full stack...

Code View (Backend):
  ✓ Scaffolded backend/api/users/preferences.py
    - Route handler
    - Request validation
    - Response serialization
  ✓ Scaffolded backend/services/user_preferences.py
    - Business logic
    - Database operations

Code View (Frontend):
  ✓ Scaffolded frontend/api/userPreferences.ts
    - API client function
    - TypeScript types
  ✓ Scaffolded frontend/hooks/useUserPreferences.ts
    - React hook
    - Mutation handling

Database View:
  ✓ Created user_preferences table
  ✓ Generated migration: 2024_01_20_add_user_preferences.sql

Test View:
  ✓ Scaffolded tests/api/test_user_preferences.py
    - Unit tests
    - Integration tests
  ✓ Scaffolded tests/e2e/test_preferences_flow.spec.ts

Security View:
  ✓ Added authentication requirement
  ✓ Added authorization check (user can only edit own preferences)

Monitoring View:
  ✓ Added metrics: user_preferences_update_total
  ✓ Added logging: preferences update events

Files scaffolded: 8
Tests scaffolded: 6
Migrations generated: 1
```

### 4. Database View → Auto-Generate Access Layer

**Scenario**: Create a new database table

```bash
rtm create table --name notifications --columns "user_id:uuid, message:text, read:boolean, created_at:timestamp"
```

**System Auto-Generates**:

```
✓ Created TABLE-NOTIFICATIONS: notifications

Auto-generating access layer...

Code View:
  ✓ Scaffolded backend/models/notification.py
    - SQLAlchemy model
    - Pydantic schema
  ✓ Scaffolded backend/repositories/notification_repository.py
    - CRUD operations
    - Query methods
  ✓ Scaffolded backend/services/notification_service.py
    - Business logic

Database View:
  ✓ Generated migration: 2024_01_20_create_notifications.sql
  ✓ Added indexes: user_id, created_at

API View:
  ✓ Scaffolded GET /api/notifications endpoint
  ✓ Scaffolded POST /api/notifications endpoint
  ✓ Scaffolded PATCH /api/notifications/:id/read endpoint

Test View:
  ✓ Scaffolded tests/models/test_notification.py
  ✓ Scaffolded tests/repositories/test_notification_repository.py

Monitoring View:
  ✓ Added metrics: notifications_created_total
  ✓ Added metrics: notifications_read_total

Files scaffolded: 6
Migrations generated: 1
```

### 5. Test View → Auto-Generate Test Infrastructure

**Scenario**: Create a new test suite

```bash
rtm create test-suite --name "Payment Flow Tests" --type e2e
```

**System Auto-Generates**:

```
✓ Created TEST-SUITE-PAYMENT: Payment Flow Tests

Auto-generating test infrastructure...

Test View:
  ✓ Scaffolded tests/e2e/payment_flow.spec.ts
    - Setup/teardown
    - Test fixtures
    - Helper functions

Code View:
  ✓ Scaffolded tests/fixtures/payment_fixtures.ts
    - Mock payment data
    - Test users
  ✓ Scaffolded tests/helpers/payment_helpers.ts
    - Payment creation helper
    - Verification helper

Configuration View:
  ✓ Added test.payment.mock_api_key config
  ✓ Added test.payment.timeout config

Infrastructure View:
  ✓ Added test database: test_payments
  ✓ Added test environment config

Feature View:
  ✓ Linked to FEATURE-043: Payment Processing

Files scaffolded: 4
Fixtures created: 3
```

## Intelligent Scaffolding Templates

### Template System

```python
class ScaffoldTemplate:
    """Base class for scaffolding templates"""
    
    def __init__(self, context: dict):
        self.context = context
    
    def generate(self) -> str:
        """Generate code from template"""
        pass
    
    def get_dependencies(self) -> List[str]:
        """Get required dependencies"""
        pass
    
    def get_related_items(self) -> List[ViewItem]:
        """Get items to create in other views"""
        pass

class ReactComponentTemplate(ScaffoldTemplate):
    """Template for React components"""
    
    def generate(self) -> str:
        component_name = self.context['name']
        props = self.context.get('props', [])
        
        return f"""
import React from 'react';

interface {component_name}Props {{
{self._generate_props_interface(props)}
}}

export const {component_name}: React.FC<{component_name}Props> = ({{
  {', '.join(p['name'] for p in props)}
}}) => {{
  return (
    <div className="{self._to_kebab_case(component_name)}">
      {{/* TODO: Implement component */}}
    </div>
  );
}};
"""
    
    def get_dependencies(self) -> List[str]:
        return ['react', '@types/react']
    
    def get_related_items(self) -> List[ViewItem]:
        component_name = self.context['name']
        
        return [
            # Test file
            TestItem(
                path=f"tests/components/{component_name}.test.tsx",
                type='unit'
            ),
            # Style file
            CodeItem(
                path=f"frontend/components/{component_name}.css",
                type='stylesheet'
            ),
            # Storybook story
            CodeItem(
                path=f"frontend/components/{component_name}.stories.tsx",
                type='story'
            )
        ]

class APIEndpointTemplate(ScaffoldTemplate):
    """Template for API endpoints"""
    
    def generate(self) -> str:
        method = self.context['method']
        path = self.context['path']
        handler_name = self._path_to_handler_name(path)
        
        return f"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class {handler_name}Request(BaseModel):
    # TODO: Add request fields
    pass

class {handler_name}Response(BaseModel):
    # TODO: Add response fields
    pass

@router.{method.lower()}("{path}")
async def {handler_name}(
    request: {handler_name}Request,
    # TODO: Add dependencies (auth, db, etc.)
) -> {handler_name}Response:
    # TODO: Implement endpoint logic
    raise HTTPException(status_code=501, detail="Not implemented")
"""
    
    def get_related_items(self) -> List[ViewItem]:
        path = self.context['path']
        
        return [
            # Test file
            TestItem(
                path=f"tests/api/test_{self._path_to_test_name(path)}.py",
                type='integration'
            ),
            # OpenAPI spec
            APIItem(
                path=path,
                method=self.context['method'],
                spec_generated=True
            ),
            # Frontend client
            CodeItem(
                path=f"frontend/api/{self._path_to_client_name(path)}.ts",
                language='typescript'
            )
        ]
```

## Smart Extension System

### Extend Feature → Auto-Extend Everything

**Scenario**: Extend existing feature with new capability

```bash
rtm extend STORY-101 --with "Add remember me checkbox"
```

**System Auto-Extends**:

```
Extending STORY-101: User can login
  with: Add remember me checkbox

Analyzing existing implementation...
  ✓ Found: SCREEN-LOGIN
  ✓ Found: COMPONENT-LOGIN-FORM
  ✓ Found: backend/auth/login.py
  ✓ Found: POST /api/auth/login

Auto-extending...

Wireframe View:
  ✓ Added CHECKBOX-REMEMBER-ME to COMPONENT-LOGIN-FORM
  ✓ Updated component layout

Code View (Frontend):
  ✓ Modified frontend/components/LoginForm.tsx
    - Added rememberMe state
    - Added checkbox input
    - Updated form submission
  ✓ Modified frontend/api/auth.ts
    - Added rememberMe parameter

Code View (Backend):
  ✓ Modified backend/auth/login.py
    - Added remember_me parameter
    - Extended session duration logic
  ✓ Modified backend/models/session.py
    - Added extended_session field

API View:
  ✓ Updated POST /api/auth/login
    - Added remember_me: boolean parameter
    - Updated OpenAPI spec

Database View:
  ✓ Modified sessions table
    - Added extended_session column
  ✓ Generated migration: 2024_01_20_add_remember_me.sql

Test View:
  ✓ Extended tests/test_login.py
    - Added test_login_with_remember_me
    - Added test_extended_session_duration
  ✓ Extended tests/e2e/test_login_flow.spec.ts
    - Added remember me checkbox test

Configuration View:
  ✓ Added auth.extended_session_duration config (default: 30 days)

Files modified: 6
Tests added: 3
Migrations generated: 1

Changes ready for review:
  rtm diff show
  rtm extend apply
```

## Collapse/Expand with Intelligence

### Collapse Feature → Clean Up Everything

**Scenario**: Collapse (delete) a feature

```bash
rtm collapse STORY-107 --cascade
```

**System Analyzes Impact**:

```
Analyzing STORY-107: Export to CSV

Finding all linked items...

Wireframe View:
  - COMPONENT-EXPORT-BUTTON (used only by this story)
  - COMPONENT-FORMAT-SELECTOR (used only by this story)

Code View:
  - backend/export/csv_exporter.py (used only by this story)
  - frontend/components/ExportButton.tsx (used only by this story)
  - frontend/components/FormatSelector.tsx (used only by this story)

API View:
  - POST /api/export/csv (used only by this story)

Database View:
  - export_jobs table (used only by this story)

Test View:
  - tests/test_csv_export.py (tests only this story)
  - tests/e2e/test_export_flow.spec.ts (tests only this story)

Configuration View:
  - export.max_rows (used only by this story)
  - export.timeout (used only by this story)

Monitoring View:
  - export_requests_total metric (tracks only this story)

Impact Summary:
  Files to delete: 5
  Tests to delete: 2
  Database migrations to generate: 1 (drop table)
  Config items to remove: 2
  Metrics to remove: 1

⚠️  WARNING: This will permanently delete code and data structures.

Options:
  1. Delete everything (full cleanup)
  2. Mark as deprecated (soft delete)
  3. Archive for later (move to archive/)
  4. Cancel

Choice: 1

Collapsing STORY-107...

✓ Deleted 5 code files
✓ Deleted 2 test files
✓ Generated migration: 2024_01_20_drop_export_jobs.sql
✓ Removed 2 config items
✓ Removed 1 metric
✓ Updated 3 related features (removed dependencies)

Collapse complete. Run migrations:
  rtm migrate apply
```

### Expand Feature → Generate Sub-Tasks

**Scenario**: Expand a high-level feature into detailed tasks

```bash
rtm expand FEATURE-044 --depth 3
```

**System Auto-Generates**:

```
Expanding FEATURE-044: Analytics Dashboard

Using AI to decompose feature...

Generated structure:

FEATURE-044: Analytics Dashboard
  ├─ STORY-109: Display user metrics
  │   ├─ TASK-201: Create metrics API endpoint
  │   ├─ TASK-202: Build metrics chart component
  │   └─ TASK-203: Add real-time updates
  ├─ STORY-110: Export analytics data
  │   ├─ TASK-204: Implement CSV export
  │   ├─ TASK-205: Implement PDF export
  │   └─ TASK-206: Add export scheduling
  └─ STORY-111: Custom dashboard layouts
      ├─ TASK-207: Drag-and-drop widget system
      ├─ TASK-208: Save layout preferences
      └─ TASK-209: Share dashboard templates

For each task, auto-generating...

TASK-201: Create metrics API endpoint
  ✓ Scaffolded backend/api/analytics/metrics.py
  ✓ Scaffolded tests/api/test_metrics.py
  ✓ Created API spec

TASK-202: Build metrics chart component
  ✓ Scaffolded frontend/components/MetricsChart.tsx
  ✓ Scaffolded tests/components/MetricsChart.test.tsx
  ✓ Created wireframe: COMPONENT-METRICS-CHART

... (continues for all tasks)

Expansion complete:
  Stories created: 3
  Tasks created: 9
  Files scaffolded: 27
  Tests scaffolded: 18

Next steps:
  1. Review generated structure: rtm show FEATURE-044 --depth 3
  2. Adjust priorities: rtm prioritize
  3. Assign tasks: rtm assign
```

## Edit with Propagation

### Edit Feature → Propagate Changes

**Scenario**: Edit a feature's core details

```bash
rtm edit STORY-101 --title "User can login with email or username"
```

**System Propagates Changes**:

```
Editing STORY-101...

Analyzing impact of title change...

Affected items:
  - 3 code files (function names, comments)
  - 8 tests (test names, descriptions)
  - 2 API endpoints (descriptions)
  - 1 wireframe (screen title)
  - 4 documentation files

Auto-updating...

Code View:
  ✓ Updated backend/auth/login.py
    - Function: login_with_email → login_with_email_or_username
    - Docstring updated
  ✓ Updated frontend/components/LoginForm.tsx
    - Component comments updated
    - Placeholder text updated

Test View:
  ✓ Updated tests/test_login.py
    - test_login_with_email → test_login_with_email_or_username
    - Test descriptions updated

API View:
  ✓ Updated POST /api/auth/login
    - Description updated
    - OpenAPI spec regenerated

Wireframe View:
  ✓ Updated SCREEN-LOGIN
    - Title updated
    - Label text updated

Documentation:
  ✓ Updated docs/authentication.md
  ✓ Updated README.md

Files modified: 9
Tests updated: 8

Changes ready for review:
  rtm diff show
  rtm edit apply
```

## AI-Powered Smart Generation

### Context-Aware Scaffolding

```python
class AIScaffoldEngine:
    """AI-powered scaffolding with context awareness"""

    def __init__(self):
        self.llm = LLMClient()  # GPT-4, Claude, etc.
        self.context_analyzer = ContextAnalyzer()

    def scaffold_from_description(self, description: str, view: ViewType) -> ScaffoldResult:
        """Generate scaffolding from natural language description"""

        # Analyze project context
        context = self.context_analyzer.analyze_project()

        # Extract intent
        intent = self.llm.extract_intent(description)

        # Generate scaffolding plan
        plan = self.llm.generate_scaffold_plan(
            intent=intent,
            view=view,
            context=context,
            examples=self.get_similar_examples(intent)
        )

        # Generate code/configs/tests
        result = ScaffoldResult()

        for item in plan.items:
            if item.type == 'code':
                code = self.llm.generate_code(
                    description=item.description,
                    language=item.language,
                    framework=context.framework,
                    style=context.code_style
                )
                result.add_file(item.path, code)

            elif item.type == 'test':
                test = self.llm.generate_test(
                    description=item.description,
                    test_framework=context.test_framework,
                    code_to_test=result.get_file(item.tests_file)
                )
                result.add_file(item.path, test)

            elif item.type == 'config':
                config = self.llm.generate_config(
                    description=item.description,
                    format=item.format
                )
                result.add_file(item.path, config)

        return result

    def get_similar_examples(self, intent: Intent) -> List[Example]:
        """Find similar implementations in codebase"""

        # Search for similar features
        similar_features = self.storage.search_features(
            query=intent.description,
            limit=5
        )

        examples = []
        for feature in similar_features:
            # Get implementation
            code_files = self.storage.get_linked_items(feature.id, ViewType.CODE_VIEW)
            test_files = self.storage.get_linked_items(feature.id, ViewType.TEST_VIEW)

            examples.append(Example(
                feature=feature,
                code=code_files,
                tests=test_files
            ))

        return examples

class ContextAnalyzer:
    """Analyze project context for smart scaffolding"""

    def analyze_project(self) -> ProjectContext:
        """Analyze entire project to understand patterns"""

        context = ProjectContext()

        # Detect framework
        context.framework = self.detect_framework()

        # Detect code style
        context.code_style = self.detect_code_style()

        # Detect test framework
        context.test_framework = self.detect_test_framework()

        # Detect patterns
        context.patterns = self.detect_patterns()

        # Detect naming conventions
        context.naming = self.detect_naming_conventions()

        return context

    def detect_framework(self) -> Framework:
        """Detect which framework is being used"""

        # Check package.json
        if self.file_exists('package.json'):
            pkg = self.read_json('package.json')
            if 'react' in pkg.get('dependencies', {}):
                return Framework.REACT
            elif 'vue' in pkg.get('dependencies', {}):
                return Framework.VUE

        # Check requirements.txt
        if self.file_exists('requirements.txt'):
            reqs = self.read_file('requirements.txt')
            if 'fastapi' in reqs:
                return Framework.FASTAPI
            elif 'django' in reqs:
                return Framework.DJANGO

        return Framework.UNKNOWN

    def detect_patterns(self) -> List[Pattern]:
        """Detect common patterns in codebase"""

        patterns = []

        # Check for repository pattern
        if self.has_directory('repositories/'):
            patterns.append(Pattern.REPOSITORY)

        # Check for service layer
        if self.has_directory('services/'):
            patterns.append(Pattern.SERVICE_LAYER)

        # Check for dependency injection
        if self.uses_dependency_injection():
            patterns.append(Pattern.DEPENDENCY_INJECTION)

        return patterns
```

### Natural Language Scaffolding

```bash
# Create from natural language
rtm create "Add a button to export user data as CSV with progress indicator"

# System interprets and generates:
# - Wireframe: Export button component
# - Code: ExportButton.tsx with progress state
# - API: POST /api/export/users endpoint
# - Backend: CSV generation service
# - Tests: Button tests, export tests
# - Config: Export settings
```

## Batch Operations with Smart Defaults

### Batch Create with Templates

```bash
# Create multiple related items at once
rtm batch create --template crud --entity User

# System generates complete CRUD:
# - API endpoints: GET, POST, PUT, DELETE /api/users
# - Backend: UserService, UserRepository, User model
# - Frontend: UserList, UserForm, UserDetail components
# - Tests: Full test coverage
# - Database: users table with migration
```

### Template Library

```python
class TemplateLibrary:
    """Library of common scaffolding templates"""

    TEMPLATES = {
        'crud': CRUDTemplate,
        'auth': AuthTemplate,
        'dashboard': DashboardTemplate,
        'form': FormTemplate,
        'list': ListTemplate,
        'detail': DetailTemplate,
        'search': SearchTemplate,
        'export': ExportTemplate,
        'import': ImportTemplate,
        'notification': NotificationTemplate,
    }

    def apply_template(self, template_name: str, context: dict) -> ScaffoldResult:
        """Apply a template with given context"""

        template_class = self.TEMPLATES.get(template_name)
        if not template_class:
            raise ValueError(f"Unknown template: {template_name}")

        template = template_class(context)
        return template.generate_all()

class CRUDTemplate:
    """Complete CRUD scaffolding template"""

    def __init__(self, context: dict):
        self.entity = context['entity']
        self.fields = context.get('fields', self.infer_fields())

    def generate_all(self) -> ScaffoldResult:
        result = ScaffoldResult()

        # Backend
        result.add_files(self.generate_backend())

        # Frontend
        result.add_files(self.generate_frontend())

        # API
        result.add_items(self.generate_api())

        # Database
        result.add_items(self.generate_database())

        # Tests
        result.add_files(self.generate_tests())

        return result

    def generate_backend(self) -> Dict[str, str]:
        """Generate backend files"""

        entity_lower = self.entity.lower()
        entity_snake = self.to_snake_case(self.entity)

        return {
            f'backend/models/{entity_snake}.py': self.generate_model(),
            f'backend/repositories/{entity_snake}_repository.py': self.generate_repository(),
            f'backend/services/{entity_snake}_service.py': self.generate_service(),
            f'backend/api/{entity_snake}.py': self.generate_api_routes(),
        }

    def generate_frontend(self) -> Dict[str, str]:
        """Generate frontend files"""

        return {
            f'frontend/components/{self.entity}List.tsx': self.generate_list_component(),
            f'frontend/components/{self.entity}Form.tsx': self.generate_form_component(),
            f'frontend/components/{self.entity}Detail.tsx': self.generate_detail_component(),
            f'frontend/api/{self.entity.lower()}.ts': self.generate_api_client(),
        }
```

## Smart Refactoring

### Refactor with Auto-Update

```bash
# Rename a feature
rtm refactor rename STORY-101 "User authentication with OAuth"

# System updates:
# - All code references
# - All test names
# - All documentation
# - All comments
# - All API descriptions
# - All wireframe labels
```

### Extract Feature

```bash
# Extract part of a feature into separate feature
rtm refactor extract STORY-101 --lines "45-89" --new-feature "OAuth provider selection"

# System:
# 1. Creates new STORY-112: OAuth provider selection
# 2. Extracts code lines 45-89 to new file
# 3. Creates link: STORY-101 depends_on STORY-112
# 4. Updates tests
# 5. Updates documentation
```

## Validation & Consistency Checks

### Auto-Validation on CRUD

```python
class CRUDValidator:
    """Validate CRUD operations for consistency"""

    def validate_create(self, item: ViewItem, view: ViewType) -> ValidationResult:
        """Validate item creation"""

        result = ValidationResult()

        # Check naming conventions
        if not self.follows_naming_convention(item, view):
            result.add_warning(f"Item name doesn't follow convention: {item.title}")

        # Check for duplicates
        duplicates = self.find_duplicates(item)
        if duplicates:
            result.add_warning(f"Potential duplicates found: {duplicates}")

        # Check required links
        required_links = self.get_required_links(view)
        for link_type in required_links:
            if not item.has_link(link_type):
                result.add_error(f"Missing required link: {link_type}")

        # Check consistency with related items
        if not self.check_consistency(item):
            result.add_error("Item inconsistent with related items")

        return result

    def validate_edit(self, old_item: ViewItem, new_item: ViewItem) -> ValidationResult:
        """Validate item edit"""

        result = ValidationResult()

        # Check breaking changes
        if self.is_breaking_change(old_item, new_item):
            result.add_warning("This is a breaking change")
            result.affected_items = self.find_affected_items(old_item)

        # Check link consistency
        if not self.links_still_valid(new_item):
            result.add_error("Edit would break existing links")

        return result
```

## CLI Commands Summary

```bash
# Create with auto-generation
rtm create story --title "..." --auto-generate
rtm create component --parent SCREEN-X --auto-generate
rtm create endpoint --path "/api/..." --auto-generate

# Extend existing
rtm extend STORY-101 --with "Add feature X"
rtm extend COMPONENT-Y --add-prop "propName:type"

# Collapse/delete
rtm collapse STORY-107 --cascade
rtm collapse STORY-107 --soft-delete
rtm collapse STORY-107 --archive

# Expand
rtm expand FEATURE-044 --depth 3
rtm expand FEATURE-044 --ai-decompose

# Edit with propagation
rtm edit STORY-101 --title "..." --propagate
rtm edit STORY-101 --rename-all

# Batch operations
rtm batch create --template crud --entity User
rtm batch create --template dashboard --widgets "chart,table,stats"

# Refactoring
rtm refactor rename STORY-101 "New name"
rtm refactor extract STORY-101 --lines "45-89"
rtm refactor merge STORY-101 STORY-102

# AI-powered
rtm create "Natural language description of what you want"
rtm scaffold --from-description "Detailed description"

# Validation
rtm validate STORY-101
rtm validate --all --view feature
```

