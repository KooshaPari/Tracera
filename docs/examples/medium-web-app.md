# Example Project: Medium Web App

**Project Type:** Medium (50 features, 4 views)  
**Complexity:** Medium  
**Estimated Time:** 4-6 hours

---

## Overview

This example demonstrates using TraceRTM for a medium-sized web application with 50 features across 4 views (FEATURE, CODE, TEST, API). Shows multi-view traceability.

---

## Project Setup

```bash
# Initialize project
rtm config init --database-url sqlite:///web-app.db
rtm project init "Web Application" --description "E-commerce web application"
rtm db migrate
```

---

## Creating Features (FEATURE View)

### Step 1: Create Main Epic

```bash
EPIC_ID=$(rtm item create "E-Commerce Platform" \
  --view FEATURE --type epic | grep "ID:" | awk '{print $2}')
```

### Step 2: Create Feature Categories

```bash
# User Management Epic
USER_EPIC=$(rtm item create "User Management" \
  --view FEATURE --type epic --parent $EPIC_ID | grep "ID:" | awk '{print $2}')

# Product Management Epic
PRODUCT_EPIC=$(rtm item create "Product Management" \
  --view FEATURE --type epic --parent $EPIC_ID | grep "ID:" | awk '{print $2}')

# Order Management Epic
ORDER_EPIC=$(rtm item create "Order Management" \
  --view FEATURE --type epic --parent $EPIC_ID | grep "ID:" | awk '{print $2}')

# Payment Epic
PAYMENT_EPIC=$(rtm item create "Payment Processing" \
  --view FEATURE --type epic --parent $EPIC_ID | grep "ID:" | awk '{print $2}')
```

### Step 3: Create Features (50 total)

```bash
# User Management Features (15)
rtm item create "User Registration" --view FEATURE --type feature --parent $USER_EPIC
rtm item create "User Login" --view FEATURE --type feature --parent $USER_EPIC
rtm item create "Password Reset" --view FEATURE --type feature --parent $USER_EPIC
# ... (12 more user features)

# Product Management Features (15)
rtm item create "Product Listing" --view FEATURE --type feature --parent $PRODUCT_EPIC
rtm item create "Product Search" --view FEATURE --type feature --parent $PRODUCT_EPIC
# ... (13 more product features)

# Order Management Features (10)
rtm item create "Create Order" --view FEATURE --type feature --parent $ORDER_EPIC
rtm item create "Order History" --view FEATURE --type feature --parent $ORDER_EPIC
# ... (8 more order features)

# Payment Features (10)
rtm item create "Process Payment" --view FEATURE --type feature --parent $PAYMENT_EPIC
rtm item create "Payment Gateway Integration" --view FEATURE --type feature --parent $PAYMENT_EPIC
# ... (8 more payment features)
```

---

## Creating Code Files (CODE View)

```bash
# User Management Code
rtm item create "src/auth/register.py" --view CODE --type file
rtm item create "src/auth/login.py" --view CODE --type file
rtm item create "src/auth/password_reset.py" --view CODE --type file

# Product Management Code
rtm item create "src/products/list.py" --view CODE --type file
rtm item create "src/products/search.py" --view CODE --type file

# Order Management Code
rtm item create "src/orders/create.py" --view CODE --type file
rtm item create "src/orders/history.py" --view CODE --type file

# Payment Code
rtm item create "src/payment/process.py" --view CODE --type file
rtm item create "src/payment/gateway.py" --view CODE --type file
```

---

## Creating Tests (TEST View)

```bash
# User Management Tests
rtm item create "tests/test_register.py" --view TEST --type test_suite
rtm item create "tests/test_login.py" --view TEST --type test_suite

# Product Management Tests
rtm item create "tests/test_product_list.py" --view TEST --type test_suite
rtm item create "tests/test_product_search.py" --view TEST --type test_suite

# Order Management Tests
rtm item create "tests/test_order_create.py" --view TEST --type test_suite

# Payment Tests
rtm item create "tests/test_payment.py" --view TEST --type test_suite
```

---

## Creating API Endpoints (API View)

```bash
# User API
rtm item create "POST /api/auth/register" --view API --type endpoint
rtm item create "POST /api/auth/login" --view API --type endpoint

# Product API
rtm item create "GET /api/products" --view API --type endpoint
rtm item create "GET /api/products/search" --view API --type endpoint

# Order API
rtm item create "POST /api/orders" --view API --type endpoint
rtm item create "GET /api/orders" --view API --type endpoint

# Payment API
rtm item create "POST /api/payment/process" --view API --type endpoint
```

---

## Creating Links (Traceability)

```bash
# Link features to code
rtm link create --source <register-feature-id> --target <register.py-id> --type implements
rtm link create --source <login-feature-id> --target <login.py-id> --type implements

# Link code to tests
rtm link create --source <register.py-id> --target <test_register.py-id> --type tested_by
rtm link create --source <login.py-id> --target <test_login.py-id> --type tested_by

# Link features to API
rtm link create --source <register-feature-id> --target <POST-/api/auth/register-id> --type implements
rtm link create --source <login-feature-id> --target <POST-/api/auth/login-id> --type implements
```

---

## Multi-View Navigation

```bash
# Switch to FEATURE view
rtm view switch FEATURE
rtm item list

# Switch to CODE view
rtm view switch CODE
rtm item list

# Switch to TEST view
rtm view switch TEST
rtm item list

# Switch to API view
rtm view switch API
rtm item list
```

---

## Querying Across Views

```bash
# Find all items related to a feature
rtm query --related-to <register-feature-id>

# Find all tests for code files
rtm query --related-to <register.py-id> --link-type tested_by

# Cross-view search
rtm search "register" --view FEATURE
rtm search "register" --view CODE
rtm search "register" --view TEST
```

---

## Progress Tracking

```bash
# Show progress by view
rtm progress show --view FEATURE
rtm progress show --view CODE
rtm progress show --view TEST
rtm progress show --view API

# Find blocked items
rtm progress blocked

# Generate report
rtm progress report --days 30
```

---

## Exporting the Project

```bash
# Export to JSON
rtm export --format json --output web-app.json

# Export to YAML
rtm export --format yaml --output web-app.yaml

# Export to Markdown
rtm export --format markdown --output web-app.md
```

---

## Summary

This medium project demonstrates:
- ✅ Multi-view organization (FEATURE, CODE, TEST, API)
- ✅ Cross-view linking and traceability
- ✅ Hierarchical feature organization
- ✅ Progress tracking across views
- ✅ Querying and searching across views
- ✅ Data export in multiple formats

**Total Items:** ~70 (50 features + 20 code/test/api items)  
**Views Used:** 4 (FEATURE, CODE, TEST, API)  
**Complexity:** Medium

---

**Last Updated**: 2025-01-27  
**Version**: 1.0
