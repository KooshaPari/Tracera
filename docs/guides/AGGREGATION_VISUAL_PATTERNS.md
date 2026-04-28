# Visual Patterns & Design Reference
## Graph Node Aggregation UI/UX Patterns

---

## Aggregate Node Visual Design

### Aggregate Node States

```
STATE 1: COLLAPSED (Default)
┌─────────────────────────────┐
│ ▸ Component (42)             │
├─────────────────────────────┤
│ ↓ 8 incoming  ↑ 12 outgoing│
│ ⟳ 15 internal               │
└─────────────────────────────┘

STATE 2: EXPANDED
┌─────────────────────────────┐
│ ▾ Component (42)             │
├─────────────────────────────┤
│ ↓ 8 incoming  ↑ 12 outgoing│
│ ⟳ 15 internal               │
├─────────────────────────────┤
│ 42 items:                   │
│ • Button.tsx                │
│ • Alert.tsx                 │
│ • Modal.tsx                 │
│ • Dropdown.tsx              │
│ ... +38 more                │
└─────────────────────────────┘

STATE 3: SELECTED
┌═════════════════════════════┐
│ ▾ Component (42)             │  ← Ring highlight
├─────────────────────────────┤
│ ↓ 8 incoming  ↑ 12 outgoing│
│ ⟳ 15 internal               │
├─────────────────────────────┤
│ 42 items: ...               │
└═════════════════════════════┘
```

### Visual Encoding

**Color Scheme:**
```
Type-Based Aggregates:
- UI Components: #ec4899 (Pink)
- APIs: #f59e0b (Amber)
- Databases: #8b5cf6 (Purple)
- Tests: #22c55e (Green)

Shared Dependency:
- Status: #3b82f6 (Blue) - distinct from types

Community Detection:
- Status: #06b6d4 (Cyan) - distinct overlay
```

**Border Style:**
```
├─ Individual Node: solid border
│
├─ Type Aggregate: dashed border (collapsed)
│                  solid border (expanded)
│
└─ Shared Dep: solid with colored accent bar (left)
```

**Icons & Badges:**
```
Component
├─ Type Icon: [specific icon per type]
├─ Count Badge: "42" (orange, top-right)
├─ Expand Icon: "▸" (collapsed) / "▾" (expanded)
└─ Connection Icons:
   ├─ ↓ (incoming arrows)
   ├─ ↑ (outgoing arrows)
   └─ ⟳ (circular for internal)
```

---

## Edge Bundle Visualization

### Single vs Bundled Edges

```
UNBUNDLED (few connections):
Node A ─────→ Node B
Node A ─────→ Node C
Node A ─────→ Node D


BUNDLED (many connections):
Node A ════╰───→ Aggregate B
              ↘─→ Item 1
              ↘─→ Item 2
              ↘─→ Item 3
            +10 more

Visual: Thicker line with count badge "13"
```

### Edge Bundling Rules

```
Bundle when:
1. Multiple edges from same source aggregate to multiple targets
2. Edge count between pair of aggregates > 3
3. All edges have similar type/directionality

Don't bundle:
1. Single edge between nodes
2. Edges from individual (non-aggregate) nodes
3. Edges with different link types
```

### Edge Bundle Styling

```
Single Edge:
stroke: #64748b (gray)
strokeWidth: 1.5px
strokeDasharray: none
opacity: 1.0
marker: arrow

Bundled Edge:
stroke: #64748b (gray)
strokeWidth: 2 + log(count) px   // Scales with bundle size
strokeDasharray: none
opacity: 0.7
marker: arrow + badge with count

Badge Format:
┌───┐
│13 │  ← white text on dark background
└───┘
Positioned at edge midpoint
```

---

## Aggregate Node Details Panel

### Connected Items Display

```
┌──────────────────────────────────┐
│ Component (42 items)             │
├──────────────────────────────────┤
│                                  │
│ Overview                         │
│ ├─ Type: UI Component           │
│ ├─ Items: 42                    │
│ ├─ External Incoming: 8         │
│ ├─ External Outgoing: 12        │
│ └─ Internal Links: 15           │
│                                  │
│ Incoming Dependencies (8)        │
│ ├─ ErrorHandler (5 sources)     │
│ ├─ ThemeProvider (3 sources)    │
│ └─ ...                          │
│                                  │
│ Outgoing Dependencies (12)       │
│ ├─ API Service (8 targets)      │
│ ├─ LocalStorage (4 targets)     │
│ └─ ...                          │
│                                  │
│ Items in Group:                  │
│ ├─ Button.tsx                   │
│ ├─ Alert.tsx                    │
│ ├─ Modal.tsx                    │
│ ├─ Dropdown.tsx                 │
│ ├─ Select.tsx                   │
│ ├─ Input.tsx                    │
│ ├─ Card.tsx                     │
│ ├─ Badge.tsx                    │
│ ├─ Tooltip.tsx                  │
│ ├─ Dialog.tsx                   │
│ └─ +32 more                     │
│                                  │
└──────────────────────────────────┘
```

---

## Interaction Patterns

### Expand Aggregate Node

```
User Action: Click on aggregate node
│
├─ Highlight with selection ring
├─ Detail panel opens (right side)
├─ User clicks expand icon "▾"
│
└─ Animation (200ms):
   ├─ Border changes solid
   ├─ Background gradient expands
   ├─ Child list slides in
   ├─ Connection counts update display
   └─ Layout recalculates (if needed)
```

### Collapse Aggregate Node

```
User Action: Click expand icon again (now "▸")
│
├─ Animation reverses (200ms)
├─ Child list slides out
├─ Border becomes dashed
└─ Back to compact view
```

### Focus/Search with Aggregates

```
User enters search: "Button"
│
├─ Find all items matching search
├─ If any in aggregates:
│  ├─ Auto-expand those aggregates
│  ├─ Highlight matching items
│  └─ Show breadcrumb: Component > Button.tsx
│
└─ If none in current aggregates:
   └─ Show: "2 matches found in 1 hidden aggregate"
      └─ [Reveal] button to expand
```

---

## Layout Considerations

### Aggregate Node Sizing

```
Collapsed State:
├─ Width: 200px (fixed)
├─ Height: 100px (fixed)
└─ Padding: 12px

Expanded State:
├─ Width: 200px (same)
├─ Height: 140 + (min(childCount, 10) * 28)px
│         = 140 + 280px = 420px max
└─ Padding: 16px
```

### Layout Algorithm Adjustments

When calculating positions with aggregates:

```
Hierarchical Layout:
├─ Aggregates on same level as individual nodes
├─ Larger height accounts for expanded state
└─ Adjust vertical spacing: 50px instead of 30px

Force-Directed Layout:
├─ Treat aggregates as heavier nodes (repel more)
├─ Use nodeMetadata.weight = childCount
└─ Dampen forces to stabilize large node groups

Radial Layout:
├─ Use depth from root
├─ Adjust radius calculation for larger nodes
└─ May need 20% more radius for readability
```

---

## Color Palette Reference

### Type Colors (Existing)

```typescript
const ENHANCED_TYPE_COLORS = {
  // Requirements & Features
  requirement: "#9333ea",      // Purple
  feature: "#a855f7",           // Light Purple
  epic: "#7c3aed",              // Deep Purple
  user_story: "#8b5cf6",        // Violet
  story: "#8b5cf6",

  // Technical
  api: "#f59e0b",               // Amber
  database: "#8b5cf6",          // Purple
  code: "#3b82f6",              // Blue
  architecture: "#6366f1",      // Indigo
  infrastructure: "#06b6d4",    // Cyan
  configuration: "#64748b",     // Slate
  dependency: "#84cc16",        // Lime

  // UI
  wireframe: "#ec4899",         // Pink
  ui_component: "#f472b6",      // Light Pink
  page: "#db2777",              // Rose
  component: "#f472b6",

  // Testing
  test: "#22c55e",              // Green
  test_case: "#16a34a",         // Dark Green
  test_suite: "#15803d",        // Very Dark Green

  // Security & Performance
  security: "#ef4444",          // Red
  vulnerability: "#dc2626",     // Dark Red
  audit: "#b91c1c",
  performance: "#10b981",       // Emerald
  monitoring: "#14b8a6",        // Teal
  metric: "#0d9488",

  // Tasks
  task: "#64748b",              // Slate
  bug: "#ef4444",               // Red
  journey: "#f97316",           // Orange
  domain: "#a855f7",            // Purple
};
```

### Overlay Colors for Aggregates

```typescript
// Semi-transparent overlays for aggregate backgrounds
const aggregateOverlays = {
  "type-based": (baseColor: string) => `${baseColor}08`,   // 3% opacity
  "shared-dependency": "#3b82f6"08",                        // Blue 3%
  "community": "#06b6d408",                                  // Cyan 3%
};

// Borders at full opacity
const aggregateBorders = {
  collapsed: "2px dashed",
  expanded: "2px solid",
};

// Highlight when selected
const selectedRing = "2px solid white with 2px offset";
```

---

## Responsive Behavior

### Mobile / Small Screen Adjustments

```
Aggregate Node (Mobile):
├─ Max Width: 160px (reduced)
├─ Min Width: 140px
├─ Padding: 8px (reduced)
├─ Font Size: 11px (reduced)
│
Expanded List:
├─ Show max 5 items (reduced from 10)
├─ "+N more" instead of showing all
│
Node Details Panel:
├─ Modal overlay instead of side panel
├─ Full width, bottom-aligned
└─ Swipe down to close
```

---

## Animation Timings

```
Expand/Collapse:
├─ Duration: 200ms
├─ Easing: ease-out (cubic-bezier(0, 0, 0.2, 1))
└─ Properties: opacity, max-height, padding

Selection Ring:
├─ Duration: 150ms
├─ Easing: ease-in-out
└─ Properties: ring-width, glow

Border Transition:
├─ Duration: 200ms
├─ Easing: ease-in-out
└─ Properties: border-style, border-width
```

---

## Icon Reference

### Aggregate Node Icons

```
By Aggregation Type:
├─ Type-Based: GitBranch (  ⎇ )
├─ Shared Dependency: Share2 (  ⤔ )
└─ Community Detection: Circle-Dot (  ⊙ )

Connection Icons:
├─ Incoming: ArrowDownLeft (  ↙ )
├─ Outgoing: ArrowUpRight (  ↗ )
└─ Internal: GitBranch (  ⎇ )

Expand/Collapse:
├─ Expanded: ChevronDown rotated (  ▾ )
└─ Collapsed: ChevronDown normal (  ▸ )
```

---

## Accessibility Considerations

### ARIA Labels

```html
<div
  role="button"
  aria-label="Aggregate: Components (42 items)"
  aria-expanded="false"
  tabindex="0"
>
  Component (42)
</div>
```

### Keyboard Navigation

```
Tab:        Navigate between nodes
Enter:      Select/deselect node
Space:      Expand/collapse aggregate
Arrow Keys: Navigate in list (when expanded)
Escape:     Close detail panel
```

### Color Contrast

```
Aggregate Text: #1a1a2e (dark) on #f0f0f0 (light)
Ratio: 7.2:1 (AAA compliant)

Badge Text: White on colored background
Minimum ratio: 4.5:1 (all type colors meet this)
```

---

## Real-World Example: 300-Item Traceability Graph

### Before Aggregation

```
300 nodes displayed
├─ Dense hairball
├─ Hard to identify patterns
├─ Slow rendering (1000+ edges)
├─ Users overwhelmed
└─ Search takes 20+ clicks
```

### After Type-Based Aggregation

```
85 nodes displayed (28% of original)
├─ 12 aggregates
│  ├─ Components (42)
│  ├─ APIs (18)
│  ├─ Tests (56)
│  ├─ Requirements (28)
│  ├─ Databases (8)
│  ├─ Configurations (12)
│  ├─ Features (15)
│  ├─ Pages (12)
│  ├─ Bugs (35)
│  ├─ Tasks (24)
│  ├─ Security Items (8)
│  └─ Performance (1)
│
├─ 73 individual nodes
│  ├─ High-level requirements
│  ├─ Epics
│  ├─ Architectures
│  └─ Special/high-importance items
│
├─ 450 edges (55% reduction)
├─ Fast rendering (<200ms)
├─ Clear structure visible
└─ Search can expand aggregates
```

### After Adding Shared Dependency Clusters

```
65 nodes displayed (22% of original)
├─ 8 type aggregates
├─ 4 shared-dependency aggregates
│  ├─ "Depend on ErrorHandler" (12 items)
│  ├─ "Depend on Auth Service" (8 items)
│  ├─ "Depend on Logger" (15 items)
│  └─ "Test CommonUtils" (22 items)
│
├─ 53 individual nodes
├─ 280 edges
├─ Architectural patterns visible
└─ User can explore by dependency
```

---

## Troubleshooting Visual Issues

### Overlapping Nodes

**Problem:** Aggregates overlap individual nodes
**Solution:** Adjust layout algorithm to give aggregates more space

```typescript
nodeWidth = isAggregate ? 220 : 200;
nodeHeight = isAggregate ? (isExpanded ? 400 : 100) : 80;
spacing = isAggregate ? 80 : 50; // More space around aggregates
```

### Too Many Child Items in List

**Problem:** Expanded aggregate shows too many items
**Solution:** Implement scrollable list with pagination

```typescript
// Show first 10, then +N more
const visibleItems = childNodeIds.slice(0, 10);
const remainingCount = childNodeIds.length - 10;
```

### Edges Not Connecting to Aggregates

**Problem:** Edges stop at individual nodes instead of aggregate
**Solution:** Ensure edges point to aggregate ID in rendered graph

```typescript
// After aggregation, remap edges
const aggregateMap = new Map(); // childId -> aggregateId
const remappedEdges = edges.map(edge => ({
  ...edge,
  source: aggregateMap.get(edge.source) || edge.source,
  target: aggregateMap.get(edge.target) || edge.target,
}));
```

---

**Visual Reference Version:** 1.0
**Last Updated:** January 24, 2026
