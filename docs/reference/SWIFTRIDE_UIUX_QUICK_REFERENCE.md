# SwiftRide UI/UX Quick Reference

**Project ID:** `cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e`

---

## Summary

| Category | Count | Description |
|----------|-------|-------------|
| **Wireframes** | 108 | Screen designs for Driver, Rider, Admin apps |
| **Components** | 120 | Reusable React components |
| **User Flows** | 80 | End-to-end user journeys |
| **Interactions** | 90 | UI interaction patterns |
| **Design Tokens** | 72 | Colors, typography, spacing |
| **Accessibility** | 80 | WCAG compliance requirements |
| **UX Patterns** | 60 | Industry-standard patterns |
| **TOTAL** | **610** | **Complete UI/UX system** |

---

## Quick Queries

### Get all items of a type
```sql
SELECT title, description, metadata
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'wireframe'  -- or component, user_flow, etc.
  AND tags && ARRAY['swiftride', 'ui-ux']
ORDER BY created_at;
```

### Get items by app/category
```sql
-- Driver wireframes
SELECT title FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'wireframe'
  AND metadata->>'app' = 'driver';

-- Map components
SELECT title FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'component'
  AND metadata->>'category' = 'map';

-- Rider flows
SELECT title FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'user_flow'
  AND metadata->>'user_type' = 'rider';
```

### Get related items
```sql
-- Components in a wireframe
SELECT c.title, c.metadata->>'category'
FROM items w
JOIN links l ON w.id = l.source_id AND l.link_type = 'contains'
JOIN items c ON l.target_id = c.id
WHERE w.title = 'Driver App: Driver Dashboard Home';

-- Features implemented by a component
SELECT f.title
FROM items c
JOIN links l ON c.id = l.source_id AND l.link_type = 'implements'
JOIN items f ON l.target_id = f.id
WHERE c.title = 'MapView';

-- Design tokens used by a component
SELECT t.title, t.metadata->>'value'
FROM items c
JOIN links l ON c.id = l.source_id AND l.link_type = 'uses'
JOIN items t ON l.target_id = t.id
WHERE c.title = 'RideRequestCard';
```

---

## Item Types

### Wireframes
**Location:** Driver (35) | Rider (35) | Admin (30) + 8 existing
**Metadata:**
- `app`: driver, rider, admin
- `category`: screen
- `platform`: mobile, web

### Components
**Categories:** Map (15) | Ride (20) | Payment (12) | Rating (10) | Navigation (8) | Profile (10) | Analytics (10) | Messaging (10) | UI (15) | Safety (10)
**Metadata:**
- `category`: map, payment, ride, etc.
- `complexity`: low, medium, high

### User Flows
**Types:** Rider (30) | Driver (30) | Admin (20)
**Metadata:**
- `user_type`: rider, driver, admin
- `steps`: 6-7
- `complexity`: low, medium, high

### Interactions
**Categories:** Touch/Gesture (20) | Button/Click (15) | Form/Input (15) | Animation (15) | Navigation (15) | Real-time (10)
**Metadata:**
- `gesture`: tap, swipe, pinch, etc.
- `type`: toggle, action, input, etc.

### Design Tokens
**Categories:** Color (20) | Typography (17) | Spacing (12) | Radius (6) | Shadow (6) | Animation (11)
**Metadata:**
- `category`: color, typography, spacing, etc.
- `type`: primary, size, padding, etc.
- `value`: #0066FF, 16px, etc.

### Accessibility
**Levels:** WCAG A (25) | WCAG AA (25) | Platform (15) | UX (15)
**Metadata:**
- `level`: A, AA, AAA, platform, ux
- `guideline`: 1.1.1, 2.4.3, etc.

### UX Patterns
**Categories:** Navigation (10) | Input (10) | Feedback (10) | Content (10) | Onboarding (5) | Transaction (5) | Social (5) | Settings (5)
**Metadata:**
- `category`: navigation, input, feedback, etc.
- `usage`: high, medium, low

---

## Link Types

| Type | Source → Target | Count |
|------|----------------|-------|
| **contains** | Wireframe → Component | 500 |
| **complies_with** | UI → Accessibility | 410 |
| **uses** | Component → Design Token | 360 |
| **requires** | Component → Interaction | 240 |
| **implements** | UI → Feature | 227 |
| **enables** | Flow → User Story | 120 |
| **follows** | Component → Pattern | 8 |

---

## Key Wireframes

### Driver App
- Driver Dashboard Home
- Ride Request Notification
- Active Ride Navigation
- Earnings Dashboard
- Driver Safety Center

### Rider App
- Rider Home Screen
- Price Estimate Screen
- Active Ride Tracking
- Rider Safety Toolkit
- Trip History

### Admin Portal
- Admin Analytics Dashboard
- Admin Trip Monitoring
- Admin Financial Dashboard
- Admin Support Ticket System
- Admin Compliance Dashboard

---

## Key Components

**Essential:**
- MapView
- RideRequestCard
- PaymentMethodSelector
- RatingStars
- EmergencyButton

**Navigation:**
- NavigationBar
- TabBar
- SideMenu

**Forms:**
- LocationPicker
- DateTimePicker
- CreditCardForm

---

## Key User Flows

**Rider:**
1. Request Immediate Ride (7 steps)
2. Track Active Ride (6 steps)
3. Complete Payment and Rate (6 steps)

**Driver:**
1. Accept and Complete Ride (6 steps)
2. View Daily Earnings (6 steps)
3. Complete Onboarding (7 steps)

**Admin:**
1. Review Driver Application (6 steps)
2. Monitor Active Trips (6 steps)
3. Process Payouts (6 steps)

---

## Design System

### Colors
- **Primary:** #0066FF (Brand Blue)
- **Success:** #00B894 (Green)
- **Error:** #FF3B30 (Red)
- **Warning:** #FF9500 (Orange)

### Typography
- **Family:** SF Pro Text
- **Sizes:** 12px - 48px
- **Weights:** 400 (Regular) - 700 (Bold)

### Spacing
- **Scale:** 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px

### Accessibility
- **Contrast:** 4.5:1 (normal), 3:1 (large)
- **Touch Targets:** 44x44dp minimum
- **Focus Indicators:** Always visible

---

## Generation Scripts

```bash
# Generate items
python3 scripts/generate_swiftride_uiux_items.py
psql "postgresql://tracertm:tracertm_password@localhost:5432/tracertm" \
  < tmp/swiftride_uiux_items.sql

# Generate links
python3 scripts/link_swiftride_uiux_items.py
psql "postgresql://tracertm:tracertm_password@localhost:5432/tracertm" \
  < tmp/swiftride_uiux_links.sql
```

---

## Files

- **Report:** `/docs/reports/SWIFTRIDE_UIUX_GENERATION_REPORT.md`
- **Quick Ref:** `/docs/reference/SWIFTRIDE_UIUX_QUICK_REFERENCE.md`
- **Scripts:** `/scripts/generate_swiftride_uiux_items.py`, `/scripts/link_swiftride_uiux_items.py`
- **SQL:** `/tmp/swiftride_uiux_items.sql`, `/tmp/swiftride_uiux_links.sql`

---

**Last Updated:** 2026-01-31
