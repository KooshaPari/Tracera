# Intelligent CRUD - Complete Walkthrough Examples

## Example 1: Create Feature with Full Auto-Generation

### Command
```bash
rtm create story \
  --title "User can filter products by price range" \
  --description "As a user, I want to filter products by price range so I can find items within my budget" \
  --auto-generate
```

### System Output
```
Creating STORY-115: User can filter products by price range

Analyzing requirements...
  ✓ Detected: UI component needed (price range slider)
  ✓ Detected: API endpoint needed (filter products)
  ✓ Detected: Database query needed (price range filter)
  ✓ Detected: Frontend state management needed

Auto-generating across all views...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FEATURE VIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Created STORY-115: User can filter products by price range
✓ Linked to FEATURE-045: Product Search & Filtering
✓ Created TASK-210: Implement price range slider
✓ Created TASK-211: Add price filter to API
✓ Created TASK-212: Update product query

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WIREFRAME VIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Created COMPONENT-PRICE-RANGE-SLIDER
  Location: SCREEN-PRODUCT-LIST → SECTION-FILTERS
  Type: Range Slider
  Props:
    - minPrice: number
    - maxPrice: number
    - onChange: (min: number, max: number) => void

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CODE VIEW (Frontend)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Scaffolded frontend/components/PriceRangeSlider.tsx
  - Component with dual-thumb slider
  - State management for min/max values
  - Debounced onChange handler
  - Accessibility attributes

✓ Scaffolded frontend/components/PriceRangeSlider.css
  - Slider styling
  - Responsive design
  - Touch-friendly targets

✓ Updated frontend/pages/ProductList.tsx
  - Added PriceRangeSlider to filters
  - Connected to product query
  - Added price range to URL params

✓ Updated frontend/hooks/useProducts.ts
  - Added priceMin and priceMax parameters
  - Updated query key for caching

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CODE VIEW (Backend)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Updated backend/api/products.py
  - Added price_min and price_max query parameters
  - Added validation (min <= max, both >= 0)

✓ Updated backend/repositories/product_repository.py
  - Added filter_by_price_range method
  - Optimized query with price index

✓ Updated backend/services/product_service.py
  - Added price range filtering logic
  - Added caching for common price ranges

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API VIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Updated GET /api/products
  New parameters:
    - price_min: number (optional, default: 0)
    - price_max: number (optional, default: null)
  
✓ Updated OpenAPI spec
  - Added parameter documentation
  - Added example requests
  - Added response examples

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATABASE VIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Verified products.price column exists
✓ Added index: idx_products_price
  - Improves price range query performance
  - Migration: 2024_01_20_add_price_index.sql

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEST VIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Scaffolded tests/components/PriceRangeSlider.test.tsx
  - Render test
  - User interaction test
  - Debounce test
  - Accessibility test

✓ Scaffolded tests/api/test_product_filter.py
  - Test price range filtering
  - Test edge cases (min > max, negative values)
  - Test performance with large datasets

✓ Scaffolded tests/e2e/test_product_filtering.spec.ts
  - Test complete filtering flow
  - Test URL parameter persistence
  - Test filter combination

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERFORMANCE VIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Added performance requirement
  - Query time: < 100ms for price range filter
  - Current: N/A (not yet measured)
  - Target: < 100ms (p95)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MONITORING VIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Added metrics
  - product_filter_price_range_total (counter)
  - product_filter_price_range_duration (histogram)

✓ Added logging
  - Log price range filter usage
  - Log slow queries (> 100ms)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONFIGURATION VIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Added configuration
  - products.price_filter.cache_ttl: 300 (seconds)
  - products.price_filter.debounce_ms: 300 (milliseconds)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Story created: STORY-115
✓ Tasks created: 3
✓ Components created: 1
✓ Files scaffolded: 8
✓ Files modified: 4
✓ Tests scaffolded: 3
✓ Migrations generated: 1
✓ Metrics added: 2
✓ Config items added: 2

Next steps:
  1. Review scaffolded code: rtm show STORY-115 --view code
  2. Review tests: rtm show STORY-115 --view test
  3. Apply changes: rtm scaffold apply
  4. Run tests: rtm test STORY-115
  5. Run migrations: rtm migrate apply
```

## Example 2: Extend Existing Feature

### Command
```bash
rtm extend STORY-101 --with "Add 'Remember me' checkbox and social login buttons"
```

### System Output
```
Extending STORY-101: User can login

Analyzing current implementation...
  ✓ Found SCREEN-LOGIN
  ✓ Found COMPONENT-LOGIN-FORM
  ✓ Found backend/auth/login.py
  ✓ Found POST /api/auth/login
  ✓ Found 8 existing tests

Planning extensions...
  Extension 1: Remember me checkbox
  Extension 2: Social login buttons (Google, GitHub)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXTENSION 1: Remember Me Checkbox
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Wireframe View:
  ✓ Added CHECKBOX-REMEMBER-ME to COMPONENT-LOGIN-FORM
    Position: Below password input
    Label: "Remember me for 30 days"

Code View (Frontend):
  ✓ Modified frontend/components/LoginForm.tsx
    + Added rememberMe state (boolean)
    + Added checkbox input
    + Updated form submission to include rememberMe

Code View (Backend):
  ✓ Modified backend/auth/login.py
    + Added remember_me parameter (optional, default: false)
    + Extended session duration when remember_me=true
  
  ✓ Modified backend/models/session.py
    + Added extended_session field (boolean)
    + Updated session expiry logic

API View:
  ✓ Updated POST /api/auth/login
    + Added remember_me: boolean parameter
    + Updated response to include session_expires_at

Database View:
  ✓ Modified sessions table
    + Added extended_session column (boolean)
    + Migration: 2024_01_20_add_extended_session.sql

Test View:
  ✓ Added tests/test_login.py::test_login_with_remember_me
  ✓ Added tests/test_login.py::test_extended_session_duration
  ✓ Updated tests/e2e/test_login_flow.spec.ts
    + Added remember me checkbox interaction

Configuration View:
  ✓ Added auth.extended_session_duration: 2592000 (30 days in seconds)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXTENSION 2: Social Login Buttons
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Wireframe View:
  ✓ Added SECTION-SOCIAL-LOGIN to SCREEN-LOGIN
    Position: Below login form
    Components:
      - BUTTON-GOOGLE-LOGIN
      - BUTTON-GITHUB-LOGIN

Code View (Frontend):
  ✓ Scaffolded frontend/components/SocialLoginButtons.tsx
    - Google OAuth button
    - GitHub OAuth button
    - Loading states
    - Error handling
  
  ✓ Updated frontend/pages/login.tsx
    + Added SocialLoginButtons component
    + Added OAuth callback handling

Code View (Backend):
  ✓ Scaffolded backend/auth/oauth.py
    - Google OAuth flow
    - GitHub OAuth flow
    - User creation/linking logic
  
  ✓ Scaffolded backend/api/auth/oauth.py
    - OAuth callback endpoints
    - Token exchange logic

API View:
  ✓ Created GET /api/auth/oauth/google
  ✓ Created GET /api/auth/oauth/google/callback
  ✓ Created GET /api/auth/oauth/github
  ✓ Created GET /api/auth/oauth/github/callback

Database View:
  ✓ Created oauth_accounts table
    Columns:
      - id (uuid, primary key)
      - user_id (uuid, foreign key)
      - provider (varchar: google, github)
      - provider_user_id (varchar)
      - access_token (encrypted)
      - refresh_token (encrypted)
      - created_at (timestamp)
    Migration: 2024_01_20_create_oauth_accounts.sql

Security View:
  ✓ Added OAuth security requirements
    - PKCE flow for OAuth
    - State parameter validation
    - Token encryption at rest

Test View:
  ✓ Scaffolded tests/auth/test_oauth.py
    - Test Google OAuth flow
    - Test GitHub OAuth flow
    - Test user linking
    - Test error cases
  
  ✓ Scaffolded tests/e2e/test_social_login.spec.ts
    - Test Google login flow
    - Test GitHub login flow

Configuration View:
  ✓ Added oauth.google.client_id (secret)
  ✓ Added oauth.google.client_secret (secret)
  ✓ Added oauth.github.client_id (secret)
  ✓ Added oauth.github.client_secret (secret)
  ✓ Added oauth.callback_url

Dependency View:
  ✓ Added dependencies
    - google-auth-oauthlib (Python)
    - PyGithub (Python)
    - react-google-login (npm)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Extensions applied: 2
✓ Files modified: 5
✓ Files scaffolded: 6
✓ Tests added: 7
✓ Migrations generated: 2
✓ API endpoints added: 4
✓ Config items added: 5
✓ Dependencies added: 3

Changes ready for review:
  rtm diff show STORY-101
  rtm extend apply
```

## Example 3: Collapse Feature with Cleanup

### Command
```bash
rtm collapse STORY-107 --cascade --analyze
```

### System Output
```
Analyzing STORY-107: Export to CSV

Finding all linked items across 16 views...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPACT ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Feature View:
  ✗ STORY-107 (will be deleted)
  ⚠  FEATURE-044 (parent, will lose 1 story)

Wireframe View:
  ✗ COMPONENT-EXPORT-BUTTON (used only by STORY-107)
  ✗ COMPONENT-FORMAT-SELECTOR (used only by STORY-107)
  ✓ SCREEN-DASHBOARD (used by other features, will keep)

Code View:
  ✗ backend/export/csv_exporter.py (used only by STORY-107)
  ✗ frontend/components/ExportButton.tsx (used only by STORY-107)
  ✗ frontend/components/FormatSelector.tsx (used only by STORY-107)
  ⚠  frontend/pages/Dashboard.tsx (imports ExportButton, needs update)

API View:
  ✗ POST /api/export/csv (used only by STORY-107)
  ⚠  API Gateway routes (needs update)

Database View:
  ✗ export_jobs table (used only by STORY-107)
  ⚠  Will need migration to drop table

Test View:
  ✗ tests/test_csv_export.py (tests only STORY-107)
  ✗ tests/e2e/test_export_flow.spec.ts (tests only STORY-107)

Configuration View:
  ✗ export.max_rows (used only by STORY-107)
  ✗ export.timeout (used only by STORY-107)

Monitoring View:
  ✗ export_requests_total metric (tracks only STORY-107)
  ✗ export_duration histogram (tracks only STORY-107)
  ⚠  Grafana dashboard "Exports" (needs update)

Performance View:
  ✗ Export performance requirement (for STORY-107 only)

Security View:
  ✗ Export rate limiting rule (for STORY-107 only)

Dependency View:
  ✗ csv-writer (npm package, used only by STORY-107)
  ⚠  pandas (Python package, also used by other features)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPACT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Items to delete: 15
Items to update: 4
Migrations to generate: 1
Dependencies to remove: 1

Estimated effort saved: 8 story points
Code lines to delete: ~450 lines

⚠️  WARNING: This is a destructive operation!

Options:
  1. Delete everything (full cleanup)
  2. Mark as deprecated (soft delete, keep code)
  3. Archive (move to archive/ directory)
  4. Show detailed diff
  5. Cancel

Your choice: 1

Proceeding with full cleanup...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLEANUP PROGRESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Deleted backend/export/csv_exporter.py
✓ Deleted frontend/components/ExportButton.tsx
✓ Deleted frontend/components/FormatSelector.tsx
✓ Deleted tests/test_csv_export.py
✓ Deleted tests/e2e/test_export_flow.spec.ts

✓ Updated frontend/pages/Dashboard.tsx
  - Removed ExportButton import
  - Removed ExportButton from render

✓ Updated backend/api/routes.py
  - Removed /api/export/csv route

✓ Generated migration: 2024_01_20_drop_export_jobs.sql
  - DROP TABLE export_jobs

✓ Removed config: export.max_rows
✓ Removed config: export.timeout

✓ Removed metrics: export_requests_total, export_duration
✓ Updated Grafana dashboard: Removed export panel

✓ Removed dependency: csv-writer (npm)

✓ Deleted STORY-107 from database
✓ Updated FEATURE-044 (removed link to STORY-107)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLEANUP COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Files deleted: 5
✓ Files updated: 2
✓ Migrations generated: 1
✓ Config items removed: 2
✓ Metrics removed: 2
✓ Dependencies removed: 1
✓ Lines of code removed: 453

Next steps:
  1. Review changes: git diff
  2. Run tests: rtm test --all
  3. Apply migration: rtm migrate apply
  4. Commit changes: git commit -m "Remove CSV export feature"
```

