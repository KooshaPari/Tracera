# Graph Toolbar Visual Guide

## Toolbar Variants

### Full Variant (Desktop)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ [Layout: Flow Chart ▼] | [🔍 Filter] [⬇ Export] | Nodes: 120/150 │ 300  │
│                                                                         │
│ Stats: Edges: 250/300 │ [➕] [➖] [⬜] [⚙] | [⛶] [📋]                   │
└─────────────────────────────────────────────────────────────────────────┘
```

**Components:**
- Left: Layout selector, filter button, export button, stats
- Right: Zoom controls (in, out, fit, actual size), fullscreen, panel toggle

**Expandable Sections:**
- Filter panel (when filter button clicked)
- Export panel (when export button clicked)

---

### Compact Variant (Tablet)

```
┌───────────────────────────────────────────────────────┐
│ [⬇ ➡ 🌐 ○] | [➕] [➖] [⬜] | [📋]                    │
└───────────────────────────────────────────────────────┘
```

**Components:**
- Left: Layout icons (4 most common)
- Center: Zoom controls
- Right: Panel toggle

**Features:**
- Icon-only layout selector
- Essential controls only
- Compact spacing

---

### Minimal Variant (Mobile)

```
┌─────────────────────────┐
│ [➕] [➖] [⬜]            │
└─────────────────────────┘
```

**Components:**
- Zoom controls only
- Minimal footprint
- Single row

---

## Filter Panel (Expanded)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Filters                                          [3 active] [Clear all] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ [🔵 Technical ▼]  |  [Node Types ▼]  |  [Status ▼]                     │
│                                                                         │
│ Active: [🔵 Technical ×] [API ×] [Database ×] [In Progress ×]          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Filter Types:**

1. **Perspective Dropdown**
   ```
   🔵 Product
   🟣 Technical      ✓
   🟢 UI
   🔴 Security
   🟡 Performance
   ```

2. **Node Type Multi-Select**
   ```
   ✓ API
   ✓ Database
   □ Code
   □ Test Case
   □ Feature
   ```

3. **Status Multi-Select**
   ```
   ✓ In Progress
   □ Completed
   □ Pending
   □ Blocked
   ```

---

## Export Panel (Expanded)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Export Graph                                                         [×] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│ │   📷     │  │   📄     │  │   { }    │  │   📊     │                 │
│ │          │  │          │  │          │  │          │                 │
│ │   PNG    │  │   SVG    │  │   JSON   │  │   CSV    │                 │
│ │  Raster  │  │  Vector  │  │   Data   │  │  Table   │                 │
│ └──────────┘  └──────────┘  └──────────┘  └──────────┘                 │
│                                                                         │
│ PNG/SVG: Visual snapshot • JSON: Complete data • CSV: Analysis         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Export Options:**

1. **PNG** - High-quality raster image (2x resolution)
2. **SVG** - Vector format (scalable)
3. **JSON** - Complete graph data with metadata
4. **CSV** - Node and edge lists for spreadsheet

**Loading State:**
```
┌──────────┐
│    ⌛    │  ← Spinner while exporting
│          │
│   PNG    │
│  Raster  │
└──────────┘
```

---

## Layout Selector Dropdown

```
┌─────────────────────────────────────────────┐
│ ⬇ Flow Chart (Top-Bottom)                 │
│   Hierarchical layout from top to bottom   │
├─────────────────────────────────────────────┤
│ ➡ Flow Chart (Left-Right)                 │
│   Hierarchical layout from left to right   │
├─────────────────────────────────────────────┤
│ 🌳 Tree (Hierarchical)                     │
│   Parent-child tree structure              │
├─────────────────────────────────────────────┤
│ ○ Radial (Circular)                        │
│   Circular layout from center              │
├─────────────────────────────────────────────┤
│ 🌐 Organic Network                         │
│   Force-directed natural layout            │
└─────────────────────────────────────────────┘
```

---

## Perspective Selector

```
┌─────────────────────────────────────────────┐
│ 🔵 Product                                 ✓│
│   Customer-facing features and journeys    │
├─────────────────────────────────────────────┤
│ 🟣 Technical                               │
│   APIs, databases, and infrastructure      │
├─────────────────────────────────────────────┤
│ 🟢 UI                                      │
│   User interface components and pages      │
├─────────────────────────────────────────────┤
│ 🔴 Security                                │
│   Security audits and vulnerabilities      │
├─────────────────────────────────────────────┤
│ 🟡 Performance                             │
│   Monitoring and metrics                   │
└─────────────────────────────────────────────┘
```

---

## Toolbar States

### Default State
```
┌─────────────────────────────────────────────────────────┐
│ [Layout ▼] [🔍] [⬇] | Nodes: 150/150 | [➕] [➖] [⬜]   │
└─────────────────────────────────────────────────────────┘
```

### With Active Filters
```
┌─────────────────────────────────────────────────────────┐
│ [Layout ▼] [🔍 3] [⬇] | Nodes: 45/150 | [➕] [➖] [⬜] │
│                                                          │
│ [🔵 Technical ×] [API ×] [Database ×]                   │
└─────────────────────────────────────────────────────────┘
```
*Note: Filter count badge, reduced node count, active filters shown*

### Fullscreen Mode
```
┌─────────────────────────────────────────────────────────┐
│ [Layout ▼] [🔍] [⬇] | Nodes: 150/150 | [➕] [➖] [⬜] [⛶]│
└─────────────────────────────────────────────────────────┘
```
*Note: Fullscreen icon changed to exit fullscreen*

### Large Dataset
```
┌─────────────────────────────────────────────────────────┐
│ [Layout ▼] [🔍] [⬇] | Nodes: 500/5000 (90% culled)     │
│ Edges: 1200/12000 | [➕] [➖] [⬜]                       │
└─────────────────────────────────────────────────────────┘
```
*Note: Shows culling percentage for performance optimization*

---

## Keyboard Shortcuts Overlay

Press `?` to show shortcuts:

```
┌─────────────────────────────────────────────────┐
│           Keyboard Shortcuts                   │
├─────────────────────────────────────────────────┤
│                                                 │
│ Zoom Controls                                   │
│  Cmd/Ctrl + Plus     Zoom in                   │
│  Cmd/Ctrl + Minus    Zoom out                  │
│  Cmd/Ctrl + 0        Fit view                  │
│  Cmd/Ctrl + 1        Actual size               │
│                                                 │
│ View Controls                                   │
│  F                   Toggle fullscreen         │
│  P                   Toggle detail panel       │
│  M                   Toggle mini-map           │
│                                                 │
│ Actions                                         │
│  Cmd/Ctrl + E        Export                    │
│  Cmd/Ctrl + F        Toggle filters            │
│  Cmd/Ctrl + Shift+R  Reset view                │
│                                                 │
│                               [Close]           │
└─────────────────────────────────────────────────┘
```

---

## Color Coding

### Perspective Colors
- 🔵 **Product** - `#3b82f6` (Blue)
- 🟣 **Technical** - `#8b5cf6` (Purple)
- 🟢 **UI** - `#10b981` (Green)
- 🔴 **Security** - `#ef4444` (Red)
- 🟡 **Performance** - `#f59e0b` (Amber)

### Node Type Colors
- **Requirement** - `#9333ea` (Purple)
- **Feature** - `#a855f7` (Light Purple)
- **API** - `#f59e0b` (Amber)
- **Database** - `#8b5cf6` (Purple)
- **Test Case** - `#16a34a` (Green)
- **Bug** - `#ef4444` (Red)

### Status Colors
- **Completed** - `#10b981` (Green)
- **In Progress** - `#f59e0b` (Amber)
- **Pending** - `#64748b` (Slate)
- **Blocked** - `#ef4444` (Red)

---

## Responsive Breakpoints

### Desktop (≥1024px)
- Full variant
- All controls visible
- Stats displayed
- Expandable panels

### Tablet (768px - 1023px)
- Compact variant
- Icon-only layouts
- Essential controls
- Collapsed stats

### Mobile (<768px)
- Minimal variant
- Zoom only
- Stacked layout
- No stats

---

## Tooltips

All controls have descriptive tooltips:

```
[➕]  ← "Zoom in (Cmd +)"
[➖]  ← "Zoom out (Cmd -)"
[⬜]  ← "Fit view (Cmd 0)"
[⚙]  ← "Actual size (1:1)"
[⛶]  ← "Fullscreen (F)"
[📋]  ← "Toggle detail panel (P)"
[🔍]  ← "Filter nodes and edges"
[⬇]  ← "Export graph (Cmd E)"
```

---

## Accessibility

### Focus States
```
[➕]  ← Default
[➕]  ← Hover (opacity 0.9)
[➕]  ← Focus (ring-2 ring-primary)
[➕]  ← Active (scale 0.95)
```

### Keyboard Navigation
- Tab through controls
- Enter/Space to activate
- Escape to close panels
- Arrow keys in dropdowns

### Screen Reader
```
<button aria-label="Zoom in">
  <ZoomIn className="h-4 w-4" aria-hidden="true" />
</button>
```

All icons marked as `aria-hidden`, labels on buttons.
