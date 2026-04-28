# Example Project: Complex System

**Project Type:** Complex (200+ features, 8 views)  
**Complexity:** High  
**Estimated Time:** 20-30 hours

---

## Overview

This example demonstrates using TraceRTM for a complex enterprise system with 200+ features across all 8 views. Shows advanced traceability, progress tracking, and multi-view management.

---

## Project Setup

```bash
# Initialize project
rtm config init --database-url postgresql://user:pass@localhost/complex-system
rtm project init "Enterprise System" --description "Large-scale enterprise application"
rtm db migrate
```

---

## Project Structure

### Views Used (All 8)

1. **FEATURE** - 200+ features organized in epics
2. **CODE** - 150+ code files
3. **WIREFRAME** - 80+ wireframes
4. **API** - 100+ API endpoints
5. **TEST** - 200+ test suites
6. **DATABASE** - 50+ database schemas
7. **ROADMAP** - 20+ roadmap items
8. **PROGRESS** - Progress tracking items

---

## Creating Features (200+)

### Main Epics (10)

```bash
# Create main epics
EPIC1=$(rtm item create "User Management System" --view FEATURE --type epic | grep "ID:" | awk '{print $2}')
EPIC2=$(rtm item create "Product Catalog" --view FEATURE --type epic | grep "ID:" | awk '{print $2}')
EPIC3=$(rtm item create "Order Processing" --view FEATURE --type epic | grep "ID:" | awk '{print $2}')
EPIC4=$(rtm item create "Payment Gateway" --view FEATURE --type epic | grep "ID:" | awk '{print $2}')
EPIC5=$(rtm item create "Inventory Management" --view FEATURE --type epic | grep "ID:" | awk '{print $2}')
EPIC6=$(rtm item create "Shipping & Logistics" --view FEATURE --type epic | grep "ID:" | awk '{print $2}')
EPIC7=$(rtm item create "Analytics & Reporting" --view FEATURE --type epic | grep "ID:" | awk '{print $2}')
EPIC8=$(rtm item create "Admin Dashboard" --view FEATURE --type epic | grep "ID:" | awk '{print $2}')
EPIC9=$(rtm item create "Mobile App" --view FEATURE --type epic | grep "ID:" | awk '{print $2}')
EPIC10=$(rtm item create "Integration Layer" --view FEATURE --type epic | grep "ID:" | awk '{print $2}')
```

### Features per Epic (20 each = 200 total)

Each epic contains 20 features, organized hierarchically.

---

## Creating Code Files (150+)

```bash
# Organize by module
rtm item create "src/auth/register.py" --view CODE --type file
rtm item create "src/auth/login.py" --view CODE --type file
rtm item create "src/products/catalog.py" --view CODE --type file
rtm item create "src/orders/processor.py" --view CODE --type file
# ... (146 more files)
```

---

## Creating Wireframes (80+)

```bash
# UI wireframes
rtm item create "wireframes/login-page.png" --view WIREFRAME --type wireframe
rtm item create "wireframes/product-list.png" --view WIREFRAME --type wireframe
# ... (78 more wireframes)
```

---

## Creating API Endpoints (100+)

```bash
# REST API endpoints
rtm item create "POST /api/v1/auth/register" --view API --type endpoint
rtm item create "GET /api/v1/products" --view API --type endpoint
# ... (98 more endpoints)
```

---

## Creating Tests (200+)

```bash
# Test suites
rtm item create "tests/unit/test_auth.py" --view TEST --type test_suite
rtm item create "tests/integration/test_orders.py" --view TEST --type test_suite
# ... (198 more test suites)
```

---

## Creating Database Schemas (50+)

```bash
# Database tables
rtm item create "schema/users.sql" --view DATABASE --type schema
rtm item create "schema/products.sql" --view DATABASE --type schema
# ... (48 more schemas)
```

---

## Creating Roadmap Items (20+)

```bash
# Roadmap milestones
rtm item create "Q1 2025: MVP Launch" --view ROADMAP --type milestone
rtm item create "Q2 2025: Mobile App" --view ROADMAP --type milestone
# ... (18 more milestones)
```

---

## Advanced Traceability

### Creating Comprehensive Links

```bash
# Feature → Code → Test → API traceability
for feature in $(rtm item list --view FEATURE --type feature | grep "ID:" | awk '{print $2}'); do
  # Find related code
  CODE_ID=$(rtm query --related-to $feature --link-type implements | grep "ID:" | head -1 | awk '{print $2}')
  
  # Find related tests
  TEST_ID=$(rtm query --related-to $CODE_ID --link-type tested_by | grep "ID:" | head -1 | awk '{print $2}')
  
  # Find related API
  API_ID=$(rtm query --related-to $feature --link-type implements | grep "ID:" | head -1 | awk '{print $2}')
  
  # Create links
  rtm link create --source $feature --target $CODE_ID --type implements
  rtm link create --source $CODE_ID --target $TEST_ID --type tested_by
  rtm link create --source $feature --target $API_ID --type implements
done
```

---

## Progress Tracking

```bash
# Show progress by view
for view in FEATURE CODE TEST API DATABASE WIREFRAME ROADMAP PROGRESS; do
  rtm progress show --view $view
done

# Find all blocked items
rtm progress blocked

# Find stalled items
rtm progress stalled --days 30

# Generate comprehensive report
rtm progress report --days 90 --json > progress-report.json
```

---

## Advanced Queries

```bash
# Query across all views
rtm query --all-projects --status todo

# Find items by relationship
rtm query --related-to <epic-id> --link-type implements

# Cross-view search
rtm search "authentication" --view FEATURE
rtm search "authentication" --view CODE
rtm search "authentication" --view TEST
rtm search "authentication" --view API
```

---

## Saved Queries

```bash
# Save frequently-used queries
rtm saved-queries save "all-todos" --filter status=todo
rtm saved-queries save "blocked-items" --filter status=blocked
rtm saved-queries save "high-priority" --priority high

# Run saved queries
rtm saved-queries run "all-todos"
```

---

## History & Rollback

```bash
# Track changes
rtm history <item-id>

# Query state at specific date
rtm history <item-id> --at "2025-01-15"

# Rollback if needed
rtm history rollback <item-id> --version 5
```

---

## Exporting the Project

```bash
# Export to multiple formats
rtm export --format json --output complex-system.json
rtm export --format yaml --output complex-system.yaml
rtm export --format markdown --output complex-system.md
rtm export --format csv --output complex-system.csv

# Backup entire project
rtm backup backup --output complex-system-backup.json.gz --compress
```

---

## Summary

This complex project demonstrates:
- ✅ All 8 views in use
- ✅ 200+ features with hierarchical organization
- ✅ Comprehensive cross-view traceability
- ✅ Advanced progress tracking
- ✅ Multi-view queries and search
- ✅ History tracking and rollback
- ✅ Saved queries for efficiency
- ✅ Full project export/backup

**Total Items:** 600+ (200 features + 400 other items)  
**Views Used:** 8 (all views)  
**Complexity:** High

---

**Last Updated**: 2025-01-27  
**Version**: 1.0
