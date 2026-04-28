# Multi-View CLI Examples & Advanced Features

## CLI Commands for Multi-View Navigation

### View Switching

```bash
# Switch to different views
rtm view feature              # Feature/epic/story view
rtm view code                 # Code files/classes/functions
rtm view wireframe            # UI screens/components/buttons
rtm view api                  # API endpoints/services
rtm view test                 # Test suites/cases
rtm view database             # Tables/schemas/queries
rtm view timeline             # Changes over time
rtm view roadmap              # Future plans

# Show current view
rtm view

# List all available views
rtm views
```

### Drill Down & Navigation

```bash
# Show item and its children
rtm show EPIC-001                    # Show epic
rtm show EPIC-001 --depth 3          # Show 3 levels deep
rtm show EPIC-001 --depth all        # Show all levels

# Drill down with view switch
rtm show STORY-101 --view code       # Show in code view
rtm show STORY-101 --view wireframe  # Show in wireframe view
rtm show STORY-101 --view test       # Show in test view

# Show all linked items
rtm links STORY-101                  # All views
rtm links STORY-101 --view code      # Code links only
rtm links STORY-101 --view wireframe # Wireframe links only
```

### Project State Dashboard

```bash
# Show complete project state
rtm state

# View-specific state
rtm state --view feature      # Feature completion
rtm state --view code         # Code metrics
rtm state --view test         # Test coverage
rtm state --view ui           # UI implementation

# Export state
rtm state --format json       # JSON export
rtm state --format csv        # CSV export
rtm state --format html       # HTML report
```

### Search Across Views

```bash
# Search all views
rtm search "login"

# Search specific view
rtm search "login" --view code
rtm search "login" --view wireframe
rtm search "login" --view feature

# Advanced search
rtm search "login" --type function    # Search for functions
rtm search "login" --type component   # Search for UI components
rtm search "login" --type endpoint    # Search for API endpoints
```

### CRUD from CLI

```bash
# Create
rtm create feature --parent EPIC-001
rtm create story --parent FEATURE-042 --title "User can logout"
rtm create wireframe --type screen --title "Logout confirmation"
rtm create code --path "auth/logout.py"
rtm create test --path "tests/test_logout.py"

# Read
rtm show STORY-101
rtm show STORY-101 --format json
rtm show STORY-101 --with-links

# Update
rtm update STORY-101 --status complete
rtm update STORY-101 --owner alice
rtm update STORY-101 --priority 90

# Delete
rtm delete FEATURE-042                # Prompt for confirmation
rtm delete FEATURE-042 --cascade      # Delete with all linked items
rtm delete FEATURE-042 --no-cascade   # Delete only this item
rtm delete FEATURE-042 --force        # No confirmation
```

## Example CLI Sessions

### Session 1: Feature View

```bash
$ rtm view feature

Project: MyApp (Feature View)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▼ EPIC-001: User Authentication (80% complete)
  ├─ ✓ FEATURE-042: Login System (100%)
  │   ├─ ✓ STORY-101: User can login with email
  │   ├─ ✓ STORY-102: User can reset password
  │   └─ ⧗ STORY-103: User can enable 2FA
  └─ ⧗ FEATURE-043: Session Management (60%)
      ├─ ✓ STORY-104: Sessions persist across tabs
      └─ ○ STORY-105: Session timeout handling

▼ EPIC-002: Dashboard (40% complete)
  └─ ⧗ FEATURE-044: Analytics Dashboard (40%)
      ├─ ✓ STORY-106: Display user metrics
      └─ ⧗ STORY-107: Export to CSV

Legend: ✓ Complete  ⧗ In Progress  ○ Not Started

$ rtm show STORY-101

STORY-101: User can login with email
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: Complete
Owner: alice
Effort: 5 points
Created: 2024-01-15
Completed: 2024-01-20

Description:
  As a user, I want to login with my email and password
  so that I can access my account.

Linked Items:
  Wireframes (2):
    - SCREEN-LOGIN: Login screen
    - COMPONENT-LOGIN-FORM: Login form component
  
  Code (3):
    - backend/auth/login.py: Login endpoint
    - frontend/components/LoginForm.tsx: Login form UI
    - frontend/pages/login.tsx: Login page
  
  APIs (1):
    - POST /api/auth/login: Authenticate user
  
  Tests (8):
    - test_login_success: ✓ Passing
    - test_login_invalid_email: ✓ Passing
    - test_login_wrong_password: ✓ Passing
    - test_login_rate_limiting: ✓ Passing
    - test_login_ui_validation: ✓ Passing
    - test_login_ui_submit: ✓ Passing
    - test_login_ui_error_display: ✓ Passing
    - test_login_integration: ✓ Passing
  
  Coverage: 100%

Commands:
  rtm show STORY-101 --view code       # Switch to code view
  rtm show STORY-101 --view wireframe  # Switch to wireframe view
  rtm links STORY-101                  # Show all links
```

### Session 2: Wireframe View with Drill-Down

```bash
$ rtm view wireframe

Project: MyApp (Wireframe View)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▼ SCREEN-LOGIN: Login Screen (100% implemented)
  ├─ SECTION-HEADER: Header
  │   └─ COMPONENT-LOGO: App logo
  ├─ SECTION-MAIN: Main content
  │   └─ COMPONENT-LOGIN-FORM: Login form
  │       ├─ INPUT-EMAIL: Email input
  │       ├─ INPUT-PASSWORD: Password input
  │       ├─ BUTTON-SUBMIT: Login button
  │       └─ LINK-FORGOT: Forgot password link
  └─ SECTION-FOOTER: Footer
      └─ LINK-SIGNUP: Sign up link

▼ SCREEN-DASHBOARD: Dashboard (60% implemented)
  ├─ SECTION-NAV: Navigation
  └─ SECTION-CONTENT: Main content

$ rtm show COMPONENT-LOGIN-FORM

COMPONENT-LOGIN-FORM: Login form
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type: Form Component
Screen: SCREEN-LOGIN
Status: Implemented
Implementation: 100%

Children (4):
  ├─ INPUT-EMAIL: Email input
  ├─ INPUT-PASSWORD: Password input
  ├─ BUTTON-SUBMIT: Login button
  └─ LINK-FORGOT: Forgot password link

Implements Features:
  - STORY-101: User can login with email

Implemented By:
  - frontend/components/LoginForm.tsx (React component)
  - frontend/styles/LoginForm.css (Styles)

Uses APIs:
  - POST /api/auth/login

Tested By:
  - test_login_ui_validation.spec.ts (✓ Passing)
  - test_login_ui_submit.spec.ts (✓ Passing)
  - test_login_ui_error_display.spec.ts (✓ Passing)

Commands:
  rtm show COMPONENT-LOGIN-FORM --view code  # See implementation
  rtm show INPUT-EMAIL                       # Drill down to email input

$ rtm show INPUT-EMAIL

INPUT-EMAIL: Email input
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type: Input Field
Component: COMPONENT-LOGIN-FORM
Status: Implemented

Properties:
  - Type: email
  - Required: true
  - Validation: Email format
  - Placeholder: "Enter your email"
  - Autocomplete: email

Implemented In:
  - frontend/components/LoginForm.tsx (lines 45-52)

Tested By:
  - test_login_ui_validation.spec.ts::test_email_validation

Commands:
  rtm show INPUT-EMAIL --view code  # See code implementation
```

### Session 3: Code View with Cross-Linking

```bash
$ rtm view code

Project: MyApp (Code View)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▼ backend/
  ├─ ▼ auth/
  │   ├─ login.py (234 lines, 100% coverage)
  │   ├─ session.py (156 lines, 95% coverage)
  │   └─ middleware.py (89 lines, 100% coverage)
  └─ ▼ api/
      └─ routes.py (445 lines, 88% coverage)

▼ frontend/
  ├─ ▼ components/
  │   ├─ LoginForm.tsx (123 lines, 100% coverage)
  │   └─ Dashboard.tsx (267 lines, 75% coverage)
  └─ ▼ pages/
      ├─ login.tsx (78 lines, 100% coverage)
      └─ dashboard.tsx (145 lines, 80% coverage)

$ rtm show backend/auth/login.py

backend/auth/login.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Language: Python
Lines: 234
Coverage: 100%
Last Modified: 2024-01-20

Classes (2):
  ├─ LoginHandler (lines 15-145)
  │   ├─ validate_credentials() (lines 25-45)
  │   ├─ create_session() (lines 47-78)
  │   └─ handle_login() (lines 80-145)
  └─ LoginError (lines 147-160)

Functions (3):
  ├─ hash_password() (lines 162-175)
  ├─ verify_password() (lines 177-190)
  └─ rate_limit_check() (lines 192-220)

Implements Features:
  - STORY-101: User can login with email
  - STORY-102: User can reset password

Calls APIs:
  - POST /api/auth/login (defined here)

Tested By:
  - tests/test_login.py (8 tests, all passing)

Dependencies:
  - bcrypt (password hashing)
  - redis (rate limiting)
  - jwt (session tokens)

Commands:
  rtm show LoginHandler                    # Drill down to class
  rtm show backend/auth/login.py --view feature  # See features
  rtm show backend/auth/login.py --view test     # See tests
```

