# Interactive Node Expansion in Graph/Diagram Tools - Research Report

**Date:** January 24, 2026
**Scope:** Best practices for interactive node expansion, progressive disclosure, and navigation patterns in graph visualization tools
**Audience:** Product managers, UX designers, and developers designing graph/diagram tools

---

## Executive Summary

This research synthesizes best practices from leading graph and diagram tools (Figma, Miro, Linear, React Flow, Storybook, Whimsical) to provide strategic recommendations for interactive node expansion UI patterns. The research identifies seven distinct progressive disclosure patterns, provides decision frameworks for choosing between inline vs. sidebar expansion, and documents keyboard navigation standards aligned with WAI-ARIA accessibility guidelines.

**Key Findings:**
- Progressive disclosure patterns span from simple collapsed states to full-page detail views
- Side panels are preferred for complex information; inline expansion is better for quick previews
- Keyboard navigation using arrow keys for navigation + Enter/Space for expansion is the accessibility standard
- Visual affordances (chevron icons pointing down=collapsed, up=expanded) are crucial for discoverability
- Breadcrumb trails are essential for deep hierarchies; truncation patterns prevent visual clutter

**Recommendation:** Implement a hybrid approach supporting both inline node pills (quick preview) and side panels (rich details), with keyboard accessibility and smart breadcrumb truncation for deep hierarchies.

---

## 1. Progressive Disclosure Patterns

### Pattern Hierarchy: Collapsed → Preview → Panel → Full Page

Progressive disclosure gradually reveals information based on user actions, reducing cognitive load. For graph tools, the typical progression is:

#### 1.1 Collapsed Node State
**Description:** Minimal node representation (just icon + label)
**Use Case:** When canvas is crowded or initial graph load needs to be fast
**Implementation:**
```
┌─────────────────┐
│  📦 Component   │
└─────────────────┘
```
**Affordance:** Chevron icon or expand button visible (must be discoverable)
**Keyboard:** Arrow keys to focus, Enter to expand
**Example:** Linear's roadmap view initially shows collapsed epics

---

#### 1.2 Inline Preview / Rich Node Pill
**Description:** Expanded node showing metadata (status badges, counts, preview image)
**Use Case:** Quick context without opening side panel
**Implementation:**
```
┌────────────────────────────┐
│ 📦 Component Button         │
│ Status: In Review | 3 links │
│ Owner: @dev                 │
└────────────────────────────┘
```
**Content to Show:**
- Type badge (color-coded)
- Status indicator
- Link counts (incoming/outgoing)
- Owner/assignee
- Small thumbnail (for UI components)

**Best Practice:** Keep node pill ≤ 300px wide; truncate long labels with ellipsis
**Keyboard:** Arrow keys to navigate, Space/Enter to expand detail panel
**Visual Feedback:** Subtle shadow or border highlight on hover/focus

---

#### 1.3 Side Panel / Detail View
**Description:** Rich information panel (396-480px width standard) with tabs and nested content
**Use Case:** Detailed exploration without leaving graph context
**Implementation:** React Flow uses Panel component (top-left to bottom-right positioning options)

**Panel Structure:**
```
┌────────────────────────────┐
│ Header (Type Badge, Close) │
├────────────────────────────┤
│ Quick Stats (Incoming/Out) │
├────────────────────────────┤
│ Tabs: Details|Links|Preview│
│                            │
│ Scrollable Content Area    │
│ (Description, Metadata,    │
│  Hierarchy, Timestamps)    │
│                            │
├────────────────────────────┤
│ Footer Actions             │
│ (Open Full Details, etc)   │
└────────────────────────────┘
```

**Tab Organization (from existing implementation):**
1. **Details Tab** - Description, metadata (owner, priority, version), hierarchy info, timestamps
2. **Links Tab** - Incoming/outgoing links grouped by type with link counts
3. **Preview Tab** - Screenshots, interactive widgets (for UI components)
4. **Code Tab** - Component code snippets

**Width:** 380-480px (sweet spot balances readability with canvas visibility)
**Scroll Behavior:** Use ScrollArea component to prevent vertical expansion
**Navigation:** Keyboard accessibility - Tab through items, arrow keys within lists

---

#### 1.4 Full-Page Detail View
**Description:** Complete item details on dedicated page (full focus)
**Use Case:** Deep editing, extensive documentation, or agent-based transformations
**Implementation:** Navigation to `/items/$itemId` route

**Content Expansion:**
- Full description with rich markdown
- Complete edit history and version timeline
- Related items in grid/list view
- Advanced settings and configuration
- API/code samples with syntax highlighting
- Audit logs and permissions

**Entry Points:**
- "Open Details" button in side panel footer
- Click on item title in detail panel
- Keyboard: Ctrl+Click or Cmd+Click on node

---

### 1.5 Progressive Disclosure Decision Tree

```
Start: User clicks node
  │
  ├─ Single click → Show inline node pill (expanded)
  │   └─ Contains: status, counts, preview
  │   └─ Keyboard accessible: Space/Enter to expand panel
  │
  ├─ Double-click or "Expand" button → Open side panel
  │   └─ Shows: Full Details + Links + Preview + Code tabs
  │   └─ Contains: Scrollable content, navigation buttons
  │   └─ Keyboard: Esc to close, Tab through content
  │
  ├─ "Open Details" / "Go to Full Page" → Navigate to detail page
  │   └─ Full-screen focused editing/exploration
  │   └─ URL changes (deep linkable state)
  │
  └─ Hover → Show minimal tooltip
      └─ Label + type badge
      └─ Don't block access to other nodes
```

---

## 2. Block Pill / Control Panel Design Patterns

### 2.1 What Leading Tools Show on Node Click

#### Figma: Property Inspector Pattern
**On Node Select:**
- Name/layer in hierarchy
- Frame type (component, auto-layout, etc.)
- Dimensions and position
- Fill, stroke, effects
- Constraints and responsive behavior
- Instance details (if component instance)

**Pattern Insight:** Right-side panel with tabs (Design|Inspect|Code|Assets)
**Why It Works:** Designers work in context; need to adjust properties without leaving canvas

#### Miro: Minimalist Approach
**On Node Click:**
- Shape displays selection handles
- Top toolbar shows formatting options
- Limited inline editing
- **Limitation:** No expand/collapse for nested content (community-requested feature)

**Pattern Insight:** Miro relies on linking between frames for "drill-down" rather than true node expansion
**Decision:** Miro chose simplicity over hierarchical navigation

#### Linear: Tree-Based Expansion
**On Epic/Issue Click:**
- Expand/collapse to show child issues
- Inline status indicators
- Quick actions (assign, change priority)
- Side panel with full details

**Pattern Insight:** Uses chevron icons to signal expandable state
**Keyboard Support:** Arrow keys to navigate hierarchy, Enter to select/expand

#### React Flow: Flexible Architecture
**On Node Select:**
- Configurable node content (React components)
- NodeToolbar component for quick actions
- Panel component for positioning info UI
- Custom handles for connections

**Pattern Insight:** Framework allows any UI pattern; developers decide (flexibility as power)
**Best Practice:** Show toolbar on hover, detail panel on select

---

### 2.2 Recommended Node Pill Design for Trace Tool

For this traceability/graph tool, recommend this on-node expansion sequence:

**Step 1: Hover State (Non-intrusive)**
```
┌─────────────────────────┐
│ 📦 Component Button     │  ← Tooltip on hover
│                         │
│ Quick affordance: small │
│ chevron icon or +       │
└─────────────────────────┘
```

**Step 2: Click = Rich Node Pill + Inline Metadata**
```
┌─────────────────────────────────────────┐
│ 📦 Component Button     [Close X]       │
│ Status: 🟢 In Progress  | Review        │
│ ──────────────────────────────────────  │
│ Incoming: 3  Outgoing: 5                │
│ Owner: @developer                       │
│ Version: 2.1.0                          │
│                                         │
│ Links & Related:                        │
│ ├─ ✓ Depends on (2)                     │
│ ├─ ⚡ Uses (3)                          │
│ └─ 📌 Related to (1)                    │
│                                         │
│ [→ Open Details]                        │
└─────────────────────────────────────────┘
```

**Step 3: Expand Button or Double-Click = Full Side Panel**
- Opens right-side panel with tabs
- Preserves graph context
- Scrollable content area
- Close with Esc or X button

---

## 3. In-Graph vs Sidebar Panels: Decision Framework

### 3.1 When to Use Each Approach

| Aspect | Inline/In-Graph | Side Panel | Full Page |
|--------|-----------------|------------|-----------|
| **Info Density** | Low (3-5 items) | Medium-High (10-50 items) | Very High (50+) |
| **Editing** | Quick/simple only | Complex editing | Advanced/rare operations |
| **Canvas Visibility** | Preserved | Partially obstructed | Lost |
| **Keyboard Efficiency** | High (arrow keys) | Medium | Low (requires navigation) |
| **Mobile Friendly** | Poor | Good (overlaid) | Good (full screen) |
| **Discovery** | Good (always visible) | Moderate (panel may be hidden) | Poor (requires page nav) |
| **Multi-node Comparison** | Excellent | Good | Poor |
| **Drill-down Deep Navigation** | Limited (3 levels max) | Good (5-7 levels) | Excellent (unlimited) |
| **Accessibility (SR)** | Challenging | Easier (landmark regions) | Easiest (dedicated page) |

### 3.2 Hybrid Approach: Recommended for This Tool

**Tier 1: Node Pill (Click)**
- Status, counts, owner
- Quick preview without disrupting canvas
- ~250-300px wide, positioned near node

**Tier 2: Side Panel (Double-click or expand button)**
- Full details, links, preview, code
- Right-aligned, 380-480px wide
- 60% of viewport height
- Scrollable content

**Tier 3: Full Page (Navigate button)**
- Deep editing, full history, advanced features
- Route change to `/items/$itemId`
- Back button returns to graph

**Implementation Logic:**
```javascript
// User interaction flow
onClick(node) → expand node pill (show inline)
onClick(expandButton) → open side panel
onClick("Open Details") → navigate to full page
onEscape → collapse everything
onArrowKey → navigate between nodes
```

---

## 4. Drill-Down Navigation for Deep Hierarchies

### 4.1 Challenge: Deep Component Hierarchies

Traceability trees can be deep:
```
Project
  └─ Page
    └─ Layout Section
      └─ Component Group
        └─ Component
          └─ Subcomponent
            └─ Element
```

**Problem:** Showing full path requires too much space; clicking through 6 levels is tedious

### 4.2 Solutions Used in Leading Tools

#### Miro's Linking Approach
- Create separate frames for each level
- Link from parent frame to child frame
- Click to "drill down" to new frame
- Back button in frame to return

**Pros:** Clean, easy to understand
**Cons:** No true hierarchy visualization; requires manual setup

#### Figma's Component Nesting
- Components can contain other components
- Navigate through hierarchy via component tree panel
- Double-click to enter component
- Breadcrumb shows current path

**Pros:** Deep nesting supported; file structure mirrors components
**Cons:** Can be confusing with many levels

#### Linear's Flat Filtering + Inline Tree
- Flat list of issues with chevron expand/collapse
- Shows parent/child relationships inline
- Can expand multiple levels at once
- Filter to show only relevant branches

**Pros:** Keeps everything visible; fast horizontal scrolling
**Cons:** Visual clutter with many items

---

### 4.3 Recommended Pattern for Trace Tool: Focus + Context + Breadcrumbs

**Hybrid Model:**

1. **Initial View:** Show 1-2 levels of hierarchy expanded
2. **Click to Focus:** Clicking a node makes it context; shows its children (1 level down)
3. **Breadcrumb Trail:** Always visible path from root to current focus
4. **Lazy Loading:** Load children on expand (not upfront)

**Visual Implementation:**
```
Breadcrumbs: Dashboard > Projects > Mobile App > Screens > [Home Screen]

Node Tree View:
┌─────────────────────────────────────┐
│ Dashboard                           │
│ ├─ Projects (3)                     │
│ │  ├─ Web App (2)                   │
│ │  └─ Mobile App ✓ [focused]        │
│ │     ├─ Navigation (2)             │
│ │     ├─ Screens (5) ← expanded     │
│ │     │  ├─ Home Screen ✓ [current] │
│ │     │  ├─ Details Screen          │
│ │     │  └─ Settings Screen         │
│ │     └─ Components (12)            │
│ └─ Design System (1)                │
└─────────────────────────────────────┘
```

**Interaction Pattern:**
- Single click on "Mobile App" → Focus on that node (breadcrumb updates)
- Children auto-expand to show next level
- Chevrons indicate nodes with children
- Keyboard: Arrow keys to traverse; Right arrow to expand; Left arrow to collapse

---

## 5. Breadcrumb Trail Implementation

### 5.1 Breadcrumb Structure

**Always show breadcrumbs in graph view (top of panel or above graph):**
```
Home / Project: Mobile App / Screen: Home / Button: Login
```

**Clickable:** Each breadcrumb item links back to that level

**Format Options:**

**Option A: Full Path (preferred for ≤ 4 levels)**
```
Dashboard > Projects > Mobile App > Screens > Home Screen
```

**Option B: Truncated Path (for 5+ levels)**
```
Dashboard > ... > Mobile App > Screens > Home Screen
```

**Option C: Parent + Current (minimal)**
```
Mobile App > Home Screen
```

### 5.2 Deep Hierarchy Truncation Best Practices

**Problem:** Long breadcrumbs don't fit in header
**Solutions:**

1. **Middle Truncation with Dropdown**
```
Dashboard > [▼ 3 more] > Home Screen

Click [▼ 3 more] to show:
  - Projects
  - Mobile App
  - Screens
```

2. **Responsive Truncation**
   - Desktop: Show full path
   - Tablet: Show parent + current + 1 level back
   - Mobile: Show [Home] / Current Level only

3. **Overflow Menu**
   - Store full path in accessible state
   - Show "..." menu with popover listing all ancestors

### 5.3 Breadcrumb Interaction

**Keyboard:**
- Tab to navigate breadcrumb items
- Enter to navigate to that level
- Right arrow to see next level
- Left arrow to go back

**Mouse:**
- Click to navigate
- Hover to show preview of that level (optional tooltip)

**Important:** Breadcrumbs are supplementary navigation; don't replace primary graph view

---

## 6. Edit Affordances: Quick Edit vs. Agent-Required Operations

### 6.1 Classification of Editable Properties

**Category A: Quick Inline Edit (No Agent)**
- Status updates (✓ Ready → In Progress)
- Simple text fields (name, short description)
- Badge/tag assignment
- Priority changes

**Example UI:**
```
Status: [In Progress ▼]  ← Click to select
Owner: @developer [X]    ← Click to clear
Priority: [High ▼]       ← Dropdown
```

**Category B: Modal Edit (Simple Form)**
- Description (rich text)
- Link creation
- Metadata updates

**Example UI:**
```
[Edit Description] → Modal Form → Save/Cancel
```

**Category C: Agent-Required (Agent Badge + Notice)**
- Generate test cases
- Analyze dependencies
- Suggest optimizations
- Generate documentation

**Visual Treatment:**
```
┌─────────────────────────────────────┐
│ ⚙️ AI Analysis Available            │
│                                     │
│ Suggestions that require agent:     │
│ • Optimize component structure      │
│ • Generate storybook stories        │
│ • Analyze dependency graph          │
│                                     │
│ [Ask Claude] [Learn More]           │
└─────────────────────────────────────┘
```

### 6.2 Visual Indicators for Edit Capability

**Instant Edit Affordance:**
```
Name: [Button Component ▼]  ← Appears editable (bold/underline or edit icon)
```

**Agent-Required Affordance:**
```
🤖 Generate Test Cases    ← Sparkle icon + "Agent" badge
```

**Implementation:**
- Instant edit: Icon appears on hover (pencil icon, or field becomes underlined)
- Agent actions: Sparkle icon + tooltip "This requires AI assistance"
- Disabled edit: Grayed out with lock icon + "requires permission"

---

## 7. Keyboard Navigation Patterns (WAI-ARIA)

### 7.1 Standard Navigation Model

Following WAI-ARIA best practices for complex widgets:

**Tab and Arrow Key Model:**
- **Tab/Shift+Tab:** Move between major UI regions (graph, panel, breadcrumbs)
- **Arrow Keys (Up/Down/Left/Right):** Navigate within widgets
- **Enter/Space:** Activate/select focused element
- **Escape:** Close panels or deselect

### 7.2 Specific Keyboard Shortcuts for Graph Navigation

#### In Graph Canvas:

```
Arrow Up/Down/Left/Right    Navigate between nodes
                           (move focus to adjacent node)

Enter/Space                Select/expand focused node
                           (show inline pill)

Ctrl+Enter / Cmd+Enter     Open side panel for focused node

Escape                     Deselect current node
                           Close any open panels

Home                       Go to root node (focus on first)

End                        Go to last visible node

*                          Expand all sibling nodes
                           (disclosure triangle pattern)

Ctrl+Shift+Collapse/Expand Collapse all nodes
                           (toggle all at once)
```

#### In Side Panel:

```
Tab/Shift+Tab              Navigate between interactive elements
                           (buttons, links, form fields)

Arrow Up/Down              Scroll or navigate within lists
                           (Links list, related items)

Enter                      Activate link (navigate to node)
                           or Expand link group

Escape                     Close side panel
                           Return focus to graph

Ctrl+A                     Select all items in current list
                           (within Links tab)
```

#### In Breadcrumb:

```
Tab                        Move to next breadcrumb item

Shift+Tab                  Move to previous breadcrumb item

Enter                      Navigate to that level

Right Arrow                Jump to next level (if available)

Left Arrow                 Go to parent level
```

### 7.3 Implementation Checklist

**Accessibility Requirements:**
- [ ] All focusable elements have visible focus indicator
- [ ] Focus order follows visual layout (left-to-right, top-to-bottom)
- [ ] No keyboard trap (can always escape with Esc or Tab)
- [ ] Aria labels and roles correctly applied
  - `role="tree"` on node hierarchy
  - `aria-expanded="true|false"` on expandable nodes
  - `aria-current="page"` on current breadcrumb
  - `aria-label` on icon-only buttons
- [ ] Screen reader announces state changes
  - "Node expanded" / "Node collapsed"
  - "Panel opened" / "Panel closed"
  - "Current location: Dashboard > Project > Item"

---

## 8. Visual Affordances and State Indicators

### 8.1 Chevron/Icon Affordances for Expansion

**Standard Pattern (from Accordion research):**

| State | Icon | Rotation | Meaning |
|-------|------|----------|---------|
| Collapsed | ▼ | 0° | Content hidden, click to reveal |
| Expanded | ▲ | 180° | Content visible, click to hide |

**Alternative Icons:**
- Plus (+) for collapsed, Minus (−) for expanded
- Caret (‣) rotated 90° left (collapsed) / down (expanded)
- Disclosure triangle (▶/▼) standard in macOS

**Best Practice:** Use chevron + smooth rotation animation
**Why:** Most recognizable; rotation animation provides visual feedback

**Implementation:**
```tsx
<ChevronDown
  className={`transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}
/>
```

### 8.2 Node State Indicators

**Visual Encoding for Node States:**

| State | Visual | Indication |
|-------|--------|-----------|
| Collapsed | Icon only | Node can be expanded |
| Expanded | Icon + label + metadata | Currently showing preview |
| Selected | Border highlight + shadow | Currently focused |
| Expandable | Chevron visible | Has children to reveal |
| Has errors | Red border or badge | Attention needed |
| Agent processing | Spinner/pulse animation | AI working on this node |

### 8.3 Hover States

**Node Hover (in graph canvas):**
```
Collapsed:    Light background + chevron appears
Expanded:     Border highlight + shadow
```

**Panel Elements Hover:**
```
Button:       Background color change
Link:         Underline appears + color change
Badge:        Slight scale increase (1.05x)
```

---

## 9. Implementation Recommendations for Trace Tool

### 9.1 Current Implementation Strengths (from code review)

The existing `NodeDetailPanel.tsx` and related components implement:

✅ **Rich Detail Panel** with tabs (Details, Links, Preview, Code)
✅ **Link Grouping** by type with counts
✅ **Hierarchy Navigation** (Go to parent button)
✅ **Type-Based Coloring** for visual categorization
✅ **Metadata Display** (Owner, Priority, Version, Timestamps)

### 9.2 Recommended Enhancements

#### Priority 1: Keyboard Navigation
- [ ] Add keyboard navigation to graph (arrow keys between nodes)
- [ ] Arrow key expand/collapse for node tree
- [ ] Escape to close side panel
- [ ] Ctrl+Enter to open side panel
- [ ] Implementation: Add useKeyboardNavigation hook

**Code Structure:**
```tsx
// In UnifiedGraphView.tsx or FlowGraphViewInner.tsx
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'ArrowUp') navigateToNode(getPreviousNode())
  if (e.key === 'ArrowDown') navigateToNode(getNextNode())
  if (e.key === 'Enter') selectNode(focusedNode)
  if (e.key === 'Escape') deselectNode()
  // etc.
}
```

#### Priority 2: Breadcrumb Navigation
- [ ] Add breadcrumb trail component to graph header
- [ ] Show path: Home > Project > Item type > Item
- [ ] Truncate for deep hierarchies (5+ levels)
- [ ] Clickable breadcrumbs for navigation
- [ ] Implementation: Add BreadcrumbTrail component

**Component Structure:**
```tsx
interface BreadcrumbTrail {
  path: Array<{ id: string; label: string; type: string }>
  onNavigate: (itemId: string) => void
  truncateAt?: number // default 4
}
```

#### Priority 3: Enhanced Node Pills
- [ ] Expand node to show type badge + status + counts
- [ ] Add subtle chevron icon to indicate expandability
- [ ] Show quick actions on hover (expand, navigate, etc.)
- [ ] Animation when transitioning between states

#### Priority 4: Edit Affordances
- [ ] Add distinction between instant-edit (status dropdown) and modal-edit (description)
- [ ] Add visual indicator for agent-required operations (sparkle badge)
- [ ] Implement inline status selector in side panel
- [ ] Add "Ask Claude" button for agent-based tasks

**Example:**
```tsx
// In NodeDetailPanel Details tab
<div>
  <label>Status</label>
  <StatusSelector
    value={node.status}
    onChange={handleStatusChange}
    options={['To Do', 'In Progress', 'Review', 'Done']}
  />
</div>

// Agent action
<div className="bg-blue-50 p-3 rounded border border-blue-200">
  <span className="text-sm font-medium">🤖 AI Suggestions</span>
  <Button>Ask Claude to analyze dependencies</Button>
</div>
```

#### Priority 5: Deep Hierarchy Support
- [ ] Implement lazy loading of child nodes
- [ ] Add tree view with expand/collapse for hierarchical data
- [ ] Support multiple levels of drill-down (5-7 levels)
- [ ] Implement efficient rendering with virtualisation

---

## 10. Design Patterns Comparison Matrix

### 10.1 Tool Comparison: Expansion Approaches

| Tool | Expansion Method | Pills | Side Panel | Full Page | Deep Hierarchy |
|------|------------------|-------|-----------|-----------|----------------|
| **Figma** | Properties Inspector | N/A | ✓ Right side | N/A | Via component tree |
| **Miro** | Linking (not true expand) | ✓ Shape selection | Limited | ✓ Frame navigation | Frame-based drill-down |
| **Linear** | Chevron expand/collapse | ✓ Inline | ✓ Optional | ✓ Issue detail page | Tree with chevrons |
| **React Flow** | Custom implementation | ✓ Flexible | ✓ Panel component | ✓ Custom | Developer choice |
| **Storybook** | Story select + Controls | ✓ Story list | ✓ Canvas | ✓ Story page | Via sidebar tree |
| **Whimsical** | Manual connections | ✓ Shape-based | ✓ Inspector | Limited | Via linked shapes |
| **Trace Tool (Current)** | Sidebar panel on click | ✓ Basic | ✓ Rich tabs | ✓ Implemented | Limited (needs work) |

### 10.2 Feature Gap Analysis for Trace Tool

| Feature | Current | Needed |
|---------|---------|--------|
| Keyboard Navigation | Minimal | Full arrow key + enter |
| Breadcrumbs | None | Yes, with truncation |
| Expanded Node Pills | Basic | Enhanced with quick stats |
| Panel Tabs | 4 tabs (Details, Links, Preview, Code) | ✓ Complete |
| Deep Hierarchy | Limited | Tree view + lazy loading |
| Edit In-Place | None | Status dropdown only |
| Agent Actions | None | "Ask Claude" section |
| Visual Affordances | Partial | Chevrons, focus states |

---

## 11. Specific UI/UX Recommendations

### 11.1 Recommended Node Pill Evolution

**Current (Minimal):**
```
┌──────────────────┐
│ Component Button │
└──────────────────┘
```

**Recommended (Rich):**
```
┌─────────────────────────────────┐
│ 📦 Component Button      [►]   │
│ 🟢 In Progress | 📍3 links    │
│ Owner: @team                    │
└─────────────────────────────────┘
```

**Features:**
- Type icon + label
- Status badge (colored)
- Link counts (compact)
- Owner attribution
- Chevron indicator (► = collapsed, ▼ = expanded)

### 11.2 Recommended Side Panel Layout

**Current layout** (from code) is good; recommend:

1. Add animation when opening (0.2s slide-in from right)
2. Add focus trap (Tab cycles within panel)
3. Add close affordance (visible X button + Escape key)
4. Add breadcrumb/hierarchy path inside panel header
5. Sticky header (Details tab header stays visible while scrolling)

**Enhanced Header:**
```
┌──────────────────────────────────┐
│ Breadcrumb: Project > Item Type > │
│ 📦 Button Component [X]          │
├──────────────────────────────────┤
│ 🟢 In Progress | 📖 Review       │
│ Incoming: 3 → | ← Outgoing: 5   │
├──────────────────────────────────┤
│ [Details|Links|Preview|Code] tab │
│                                  │
│ (scrollable content)             │
│                                  │
├──────────────────────────────────┤
│ [→ Open Full Details]            │
└──────────────────────────────────┘
```

### 11.3 Recommended Breadcrumb Implementation

**Location:** Above graph, inside header bar

**Format:** Home > Project: [name] > Type: [type] > Item: [name]

**Responsive Behavior:**
```
Desktop (> 1200px):     Full path visible
Tablet (768-1200px):    Truncate middle: Home > ... > Item
Mobile (< 768px):       Current item only
```

**Interaction:**
- Click any breadcrumb to focus that level
- Shows dropdown for truncated items
- Always includes "Home" to escape hierarchy

---

## 12. Accessibility Considerations

### 12.1 WCAG 2.1 Compliance Checklist

**Keyboard Navigation (WCAG 2.1 Level AA):**
- [ ] All functionality accessible via keyboard
- [ ] No keyboard trap (can always Escape)
- [ ] Focus visible (3px highlight minimum)
- [ ] Focus order logical

**Screen Reader Support:**
- [ ] Proper ARIA roles (`role="tree"`, `role="treeitem"`)
- [ ] Expanded state announced (`aria-expanded="true|false"`)
- [ ] Current location clear (`aria-current="page"`)
- [ ] Labels descriptive (`aria-label` for icon buttons)
- [ ] Live regions for dynamic updates (`aria-live="polite"`)

**Visual Design:**
- [ ] Chevron icons have sufficient contrast (4.5:1 minimum)
- [ ] Focus indicator clear against background
- [ ] Color not only indicator (status + icon badge)
- [ ] Text readable (14px minimum)

### 12.2 Screen Reader Announcements

**When Node Expands:**
```
"Item expanded. Showing 3 incoming links, 5 outgoing links."
```

**When Panel Opens:**
```
"Details panel opened. Press Tab to navigate, Escape to close."
```

**When Navigating Breadcrumb:**
```
"Location: Project Mobile App, Screen Home, Button Login"
```

---

## 13. Recommended Implementation Roadmap

### Phase 1: Keyboard Navigation (Week 1-2)
- Implement arrow key navigation in graph
- Add Enter to select/expand nodes
- Add Escape to close panels
- Add keyboard indicator visual feedback

### Phase 2: Breadcrumbs (Week 2-3)
- Add breadcrumb component
- Implement truncation logic
- Add breadcrumb click navigation
- Test accessibility

### Phase 3: Enhanced Node Pills (Week 3)
- Add expanded inline view
- Add status indicators
- Add quick action buttons
- Animate transitions

### Phase 4: Edit Affordances (Week 4)
- Implement inline status selector
- Add modal for complex edits
- Add agent action indicators
- Implement "Ask Claude" pattern

### Phase 5: Deep Hierarchy Support (Week 4-5)
- Implement lazy loading
- Add tree view component
- Support 5-7 levels
- Add performance optimization

---

## Sources & References

### Primary Research Sources

1. **WAI-ARIA Keyboard Navigation Patterns**
   - [W3C - Keyboard Interface Practices](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/)
   - [DEQUE University - Keyboard Navigation Patterns](https://dequeuniversity.com/tips/aria-keyboard-patterns)
   - [MDN - Keyboard-navigable Widgets](https://developer.mozilla.org/en-US/docs/Web/Accessibility/Guides/Keyboard-navigable_JavaScript_widgets)

2. **Tree View & Expansion Patterns**
   - [PatternFly - Tree View Design Guidelines](https://www.patternfly.org/components/tree-view/design-guidelines/)
   - [Carbon Design System - Tree View](https://carbondesignsystem.com/components/tree-view/usage/)
   - [Primer Design System - Tree View](https://primer.style/components/tree-view/)
   - [Ant Design - Tree Component](https://ant.design/components/tree/)

3. **Accordion & Chevron Affordances**
   - [Carbon Design System - Accordion](https://carbondesignsystem.com/components/accordion/usage/)
   - [Smashing Magazine - Designing the Perfect Accordion](https://www.smashingmagazine.com/2017/06/designing-perfect-accordion-checklist/)
   - [UXMovement - Accordion Icon Placement](https://uxmovement.com/navigation/where-to-place-your-accordion-menu-icons/)

4. **Progressive Disclosure**
   - [UXPin - What is Progressive Disclosure](https://www.uxpin.com/studio/blog/what-is-progressive-disclosure/)
   - [Interaction Design Foundation - Progressive Disclosure](https://www.interaction-design.org/literature/topics/progressive-disclosure)
   - [Primer Design - Progressive Disclosure Patterns](https://primer.style/design/ui-patterns/progressive-disclosure/)

5. **Inline Edit vs Modal Dialogs**
   - [PatternFly - Inline Edit Guidelines](https://www.patternfly.org/components/inline-edit/design-guidelines/)
   - [UXDWorld - Best Practices for Inline Editing](https://uxdworld.com/inline-editing-in-tables-design/)
   - [LogRocket - Modal UX Design Patterns](https://blog.logrocket.com/ux-design/modal-ux-design-patterns-examples-best-practices/)

6. **Breadcrumb Navigation**
   - [NN/G - Breadcrumbs Design Guidelines](https://www.nngroup.com/articles/breadcrumbs/)
   - [Smashing Magazine - Breadcrumbs in Web Design](https://www.smashingmagazine.com/2009/03/breadcrumbs-in-web-design-examples-and-best-practices/)
   - [Smashing Magazine - Designing Effective Breadcrumbs](https://www.smashingmagazine.com/2022/04/breadcrumbs-ux-design/)

7. **React Flow Documentation**
   - [React Flow - Interaction Patterns](https://reactflow.dev/examples/interaction/interaction-props)
   - [React Flow - Adding Interactivity](https://reactflow.dev/learn/concepts/adding-interactivity)
   - [React Flow - Panel Component](https://reactflow.dev/api-reference/components/panel)

8. **Tool-Specific Research**
   - [Miro Help - Mind Map](https://help.miro.com/hc/en-us/articles/360017730753-Mind-map)
   - [Miro Help - Structuring Board Content](https://help.miro.com/hc/en-us/articles/360017730973-Structuring-board-content)
   - [Whimsical - Flowchart Maker](https://whimsical.com/flowcharts)

9. **Graph Visualization Patterns**
   - [Cambridge Intelligence - Graph Visualization Fundamentals](https://cambridge-intelligence.com/graph-viz-basics-pt1-why-graphs/)
   - [Tom Sawyer - Node Graph Visualization](https://blog.tomsawyer.com/node-graph-visualization)
   - [Cytoscape.js - Graph Library](https://js.cytoscape.org/)

---

## Conclusion

Interactive node expansion in graph tools requires a carefully orchestrated progression from simple visual cues (collapsed nodes) through rich inline previews (pills) to detailed explorations (side panels) and finally full-featured detail views. The most effective implementations combine:

1. **Progressive Disclosure** - Reveal information gradually based on user action
2. **Keyboard Accessibility** - Full support for arrow keys, Enter, and Escape
3. **Clear Visual Affordances** - Chevrons, badges, and focus states guide user action
4. **Contextual Navigation** - Breadcrumbs enable users to understand and navigate deep hierarchies
5. **Edit-in-Place for Common Tasks** - Quick status updates without modal friction
6. **Clear Separation** - Agent-required operations marked distinctly from instant edits

For the Trace tool, a phased implementation starting with keyboard navigation and breadcrumbs (high-impact, moderate effort) followed by enhanced node pills and edit affordances will substantially improve UX. Deep hierarchy support should follow once the foundation is solid.

---

**Report Prepared:** January 24, 2026
**Last Updated:** January 24, 2026
**Status:** Ready for Implementation Planning
