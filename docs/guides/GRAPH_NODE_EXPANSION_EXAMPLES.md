# Interactive Node Expansion - Visual Examples & Patterns

**Reference to:** GRAPH_NODE_EXPANSION_RESEARCH.md and GRAPH_NODE_EXPANSION_IMPLEMENTATION.md

This document provides concrete visual examples of each pattern, comparison scenarios, and decision trees.

---

## 1. Progressive Disclosure Sequence

### 1.1 Full User Journey: Click → Expand → Navigate

```
STEP 1: User sees collapsed graph (initial state)
┌────────────────────────────────────────────────────────┐
│ 📊 Traceability Graph                                   │
├────────────────────────────────────────────────────────┤
│                                                         │
│    ┌─────────┐      ┌─────────┐      ┌─────────┐     │
│    │ 📦 Form │  →   │ 🎨 Theme│  →   │ 📄 Page │     │
│    │ Login   │      │ System  │      │ Home    │     │
│    └─────────┘      └─────────┘      └─────────┘     │
│         ▼                  ▼                 ▼         │
│    ┌─────────┐      ┌─────────┐      ┌─────────┐     │
│    │ 🔘 Input│  →   │ 🎨 Color│  →   │ 🖼️  Image│     │
│    │ Field   │      │ Primary │      │ Hero    │     │
│    └─────────┘      └─────────┘      └─────────┘     │
│                                                         │
└────────────────────────────────────────────────────────┘

STEP 2: User clicks on "Form: Login"
┌────────────────────────────────────────────────────────┐
│ 📊 Traceability Graph                                   │
├────────────────────────────────────────────────────────┤
│                                                         │
│    ┌──────────────────┐      ┌─────────┐              │
│    │ ┌──────────────┐ │      │ 🎨 Theme│              │
│    │ │ 📦 Form      │ │  →   │ System  │              │
│    │ │ Login       │ │      └─────────┘              │
│    │ │ Status: ✓   │ │                               │
│    │ │ ← 2 | 3 →   │ │                               │
│    │ │ Owner: @dev │ │                               │
│    │ └──────────────┘ │                               │
│    └──────────────────┘  ← Rich pill on click          │
│                                                         │
│    [Double-click or click expand button to open panel]│
│                                                         │
└────────────────────────────────────────────────────────┘

STEP 3: User clicks expand or double-clicks node
                                    Side Panel Opens
                                    ↓
┌────────────────────────────────────┐ ┌──────────────────┐
│ Graph Canvas                        │ │ Details Panel    │
│                                    │ │                  │
│ ┌──────────────────┐               │ │ Home > Form >    │
│ │ ┌──────────────┐ │               │ │ Login            │
│ │ │ 📦 Form      │ │               │ ├──────────────────┤
│ │ │ Login        │ │ ← Selected    │ │ 📦 Form: Login   │
│ │ │ Status: ✓    │ │               │ │ Status: ✓        │
│ │ └──────────────┘ │               │ │ ← 2 in | 3 out → │
│ │  [Chevron ▼]     │               │ │                  │
│ └──────────────────┘               │ ├──────────────────┤
│                                    │ │ [Details|Links|  │
│ ┌──────────────────┐               │ │  Preview|Code]   │
│ │ 🎨 Theme System  │               │ │                  │
│ └──────────────────┘               │ │ Description:     │
│                                    │ │ Login form for...│
│                                    │ │                  │
│ ┌──────────────────┐               │ │ Owner: @dev      │
│ │ 📄 Page: Home    │               │ │ Priority: High   │
│ └──────────────────┘               │ │                  │
│                                    │ │ Hierarchy:       │
│                                    │ │ [→ Go to parent] │
│                                    │ │                  │
│                                    │ │ [→ Open Details] │
│                                    │ └──────────────────┘
└────────────────────────────────────┘

STEP 4: User clicks "Open Details" or navigates via breadcrumb
                                    Full Page Navigation
                                    ↓
┌────────────────────────────────────────────────────────┐
│ Item Details Page: Form / Login                        │
├────────────────────────────────────────────────────────┤
│                                                         │
│ Home > Projects > Product > Design > Form > [Login]    │
│                                                         │
│ ┌────────────────────────────────────────────────────┐ │
│ │ 📦 Form: Login                                     │ │
│ │ Type: Component | Status: In Progress              │ │
│ │ Owner: @dev | Priority: High                       │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Description (full):                                    │
│ Login form component with email and password fields.   │
│ Supports both form and floating label layouts...       │
│                                                         │
│ Properties:                                            │
│ • Created: 2025-01-15 14:30 UTC                        │
│ • Updated: 2025-01-24 09:15 UTC                        │
│ • Version: 2.1.0                                       │
│ • View: component                                      │
│                                                         │
│ Dependencies (full list):                              │
│ ├─ Input Field (reusable)                              │
│ ├─ Button (primary action)                             │
│ ├─ Label (form label)                                  │
│ └─ Error Message (validation)                          │
│                                                         │
│ Linked From:                                           │
│ ├─ Page: Home Screen                                   │
│ └─ Page: Signup Screen                                 │
│                                                         │
│ Tests:                                                 │
│ ├─ Login with valid credentials                        │
│ ├─ Show error on invalid credentials                   │
│ └─ Remember me checkbox behavior                       │
│                                                         │
│ [Edit] [Preview] [Share] [More...]                     │
│                                                         │
└────────────────────────────────────────────────────────┘
```

---

## 2. Breadcrumb Truncation Examples

### 2.1 Scenario: Deep Component Hierarchy (8 levels)

**Desktop (full width available):**
```
Home > Projects > Design System > Components > Forms > Inputs > Text Field > [Variants]
```

**Tablet (medium width):**
```
Home > ... > Form > Inputs > [Text Field > Variants]
(Click "..." to show: Projects, Design System, Components)
```

**Mobile (narrow width):**
```
Home / [Text Field] > Variants
(Breadcrumbs collapsed to icon + current item)
```

### 2.2 Truncation Menu (on "..." click)

```
┌──────────────────────────────┐
│ Hidden items                 │
├──────────────────────────────┤
│ 📁 Projects                  │
│ 📁 Design System             │
│ 📁 Components                │
│ 📁 Forms                     │
│ 📁 Inputs                    │
└──────────────────────────────┘
  Click to navigate to any level
```

### 2.3 Breadcrumb with Dropdown Sub-Navigation

```
Home > Projects ▼ > Design System > [Current Item]
         ↓
    ┌──────────────────┐
    │ Web App          │
    │ Mobile App       │
    │ Design System ✓  │
    │ Documentation    │
    └──────────────────┘
```

---

## 3. Node Pill States Comparison

### 3.1 Collapsed → Expanded → Panel Transition

```
COLLAPSED STATE (default):
┌─────────────────────┐
│  📦 Component       │
│     (16px padding)  │
└─────────────────────┘
  Affordance: Chevron visible on hover

HOVER STATE (mini-affordance):
┌─────────────────────┐
│ ▶ 📦 Component      │  ← Chevron appears
│     (hint to expand)│
└─────────────────────┘

EXPANDED STATE (inline pill):
┌──────────────────────────────┐
│ ▼ 📦 Component Button        │  ← Chevron rotated
│                              │
│ Status: 🟢 In Review         │
│ ← 3 incoming | 5 outgoing →  │
│ Owner: @developer            │
│ Version: 2.1.0               │
│                              │
│ [✕ Collapse] [→ Open Panel]  │
└──────────────────────────────┘
  ~250-300px wide
  Shows key metadata inline

PANEL STATE (full detail):
Side panel opens with:
- Full Details tab
- Links tab (grouped by type)
- Preview tab (if UI component)
- Code tab (if code linked)
- Scrollable content
- Footer with actions

FULL PAGE STATE (focus):
Complete detail page with:
- Full description + rich text
- All linked items
- Complete properties
- Edit capabilities
- History/timeline
- Related items grid
```

### 3.2 Visual Density Comparison

```
LOW DENSITY (Collapsed):
┌─────────┐
│ 📦 Item │
└─────────┘
1 line height


MEDIUM DENSITY (Expanded Pill):
┌──────────────────────┐
│ ▼ 📦 Item            │
│ 🟢 Ready | ← 2 | 3 → │
│ Owner: @dev          │
└──────────────────────┘
3-4 lines height


HIGH DENSITY (Side Panel):
┌──────────────────────┐
│ Header with badges   │
│ Quick stats (2 cols) │
├──────────────────────┤
│ [Tabs: 4 options]    │
├──────────────────────┤
│ Scrollable content:  │
│ - Description        │
│ - Metadata (8 items) │
│ - Hierarchy          │
│ - Timestamps         │
│ - Link groups (5+)   │
├──────────────────────┤
│ Footer actions       │
└──────────────────────┘
~380-480px wide
Multiple tabs


ULTRA HIGH DENSITY (Full Page):
Complete information space with:
- Hero section (title, badges)
- Multi-panel layout
- Tabs + nested content
- Full edit capabilities
- Related items grid
- Timeline view
- Detailed metadata
```

---

## 4. Keyboard Navigation Flow Diagram

### 4.1 State Transitions via Keyboard

```
┌──────────────────────────────────────────┐
│ GRAPH CANVAS FOCUSED                     │
│ (no node selected)                       │
└──────────────────────────────────────────┘
           │
           │ ArrowUp/Down/Left/Right
           ↓
┌──────────────────────────────────────────┐
│ NODE FOCUSED                             │
│ (node has focus ring, not selected)      │
├──────────────────────────────────────────┤
│ Available actions:                       │
│ • ArrowKeys: Move between nodes          │
│ • Home: Jump to first                    │
│ • End: Jump to last                      │
│ • Enter/Space: Select & expand node      │
│ • Escape: Return to canvas               │
└──────────────────────────────────────────┘
           │
           │ Enter or Space
           ↓
┌──────────────────────────────────────────┐
│ NODE SELECTED + PILL EXPANDED            │
│ (inline details visible)                 │
├──────────────────────────────────────────┤
│ Available actions:                       │
│ • Ctrl+Enter: Open side panel            │
│ • ArrowUp/Down: Move to next node        │
│ • Tab: Move to links within pill         │
│ • Escape: Deselect & collapse pill       │
└──────────────────────────────────────────┘
           │
           │ Ctrl+Enter or double-click
           ↓
┌──────────────────────────────────────────┐
│ SIDE PANEL OPEN                          │
│ (focus moved to panel)                   │
├──────────────────────────────────────────┤
│ Available actions:                       │
│ • Tab/Shift+Tab: Navigate within panel   │
│ • ArrowUp/Down: Scroll or nav lists      │
│ • Enter: Navigate to linked item         │
│ • Escape: Close panel                    │
└──────────────────────────────────────────┘
           │
           │ Escape
           ↓
┌──────────────────────────────────────────┐
│ NODE SELECTED (PILL SHOWN)               │
│ (panel closed, pill remains visible)     │
└──────────────────────────────────────────┘
```

### 4.2 Breadcrumb Keyboard Navigation

```
Home / Project / [Current Item]

Navigation sequence:
1. User presses Tab to reach breadcrumbs
2. Focus moves to first breadcrumb (Home)
3. Arrow Right moves to next breadcrumb
4. Arrow Left moves to previous
5. Enter navigates to that level
6. Shift+Tab returns focus to previous element
```

---

## 5. Edit Affordances Examples

### 5.1 Quick Edit (Status Update)

```
BEFORE (hover state):
┌────────────────────────────┐
│ Status: To Do         [✎]  │  ← Pencil icon on hover
└────────────────────────────┘

AFTER (click):
┌────────────────────────────┐
│ Status: [To Do ▼]          │
│ ├─ To Do                   │
│ ├─ In Progress             │
│ ├─ Review                  │
│ └─ Done                    │
└────────────────────────────┘

AFTER SELECTION:
┌────────────────────────────┐
│ Status: In Progress        │
│ (updated immediately)      │
└────────────────────────────┘

Keyboard: Tab to field, Space to open dropdown, arrows to select, Enter to confirm
```

### 5.2 Modal Edit (Complex Field)

```
BEFORE (click "Edit Description"):
┌─────────────────────────────────┐
│ Description                [✎]  │  ← Click or Cmd+Shift+E
│ "Login form for authentication" │
└─────────────────────────────────┘

AFTER (modal opens):
┌──────────────────────────────────┐
│ ✕ Edit Description               │
├──────────────────────────────────┤
│ [Rich text editor toolbar]       │
│                                  │
│ Login form for authentication    │
│ with email and password fields.  │
│ Supports both stacked and        │
│ horizontal layouts.              │
│                                  │
│ Format: Bold | Italic | Code     │
│                                  │
│ [Cancel] [Save Changes]          │
└──────────────────────────────────┘

Keyboard: Tab through controls, Escape to cancel, Ctrl+S to save
```

### 5.3 Agent Action Affordances

```
AGENT SECTION IN DETAIL PANEL:
┌──────────────────────────────────┐
│ 🤖 AI Suggestions                │
├──────────────────────────────────┤
│ ⚡ Analyze dependencies          │
│    Find circular refs & improve  │
│                                  │
│ ✨ Generate test cases           │
│    Create test scenarios         │
│                                  │
│ 🔍 Suggest optimizations        │
│    Component structure & perf    │
│                                  │
│ Powered by Claude                │
└──────────────────────────────────┘

ON CLICK:
┌──────────────────────────────────┐
│ 🤖 Analyzing dependencies...     │
│ ⏳ (loading state with spinner)  │
└──────────────────────────────────┘

AFTER COMPLETION:
┌──────────────────────────────────┐
│ 🤖 Analysis Complete             │
│ ✓ Found 2 opportunities          │
│                                  │
│ 1. Extract shared Button logic   │
│ 2. Consolidate theme references  │
│                                  │
│ [Review Details] [Apply Changes] │
└──────────────────────────────────┘

Visual distinction:
- Icon badge (sparkle) + blue background
- Distinguishes from instant edits
- Tooltip: "Requires AI processing"
```

---

## 6. Deep Hierarchy Navigation Example

### 6.1 Project Structure Tree (5+ levels)

```
INITIAL STATE (2 levels expanded):
Dashboard
├─ Projects (4)
│  ├─ Web App
│  ├─ Mobile App ← User clicked here
│  │  ├─ Navigation (2) ← Auto-expanded to show children
│  │  ├─ Screens (5)
│  │  └─ Components (12)
│  └─ Design System
└─ Settings

AFTER EXPANDING "Screens":
Dashboard
├─ Projects (4)
│  ├─ Web App
│  ├─ Mobile App
│  │  ├─ Navigation (2)
│  │  ├─ Screens (5) ← User clicked expand
│  │  │  ├─ Home Screen ← Auto-selected
│  │  │  ├─ Details Screen
│  │  │  ├─ Settings Screen
│  │  │  ├─ Profile Screen
│  │  │  └─ Search Screen
│  │  └─ Components (12)
│  └─ Design System
└─ Settings

BREADCRUMB UPDATES:
Home > Projects > Mobile App > Screens > [Home Screen]

KEYBOARD NAVIGATION:
Down arrow → Next screen (Details)
Up arrow → Previous screen (back to Mobile App > Screens level)
Right arrow → Expand screen if children exist
Left arrow → Collapse this screen's children
Enter → Select and show detail panel
```

### 6.2 Lazy-Loaded Hierarchy

```
INITIAL (only loaded items):
Dashboard (1/3 loaded)
├─ Projects ⋯ (load 3)
│  ├─ Web App ⋯ (load 5)
│  └─ Mobile App ⋯ (load 8)
└─ Settings

AFTER HOVERING/FOCUSING "Projects":
Dashboard
├─ Projects (loading...)
│  ├─ Web App ⋯ (load 5)
│  ├─ Mobile App ⋯ (load 8)
│  ├─ Design System
│  └─ Docs
└─ Settings

AFTER CLICKING "Mobile App":
Dashboard
├─ Projects
│  ├─ Web App ⋯ (load 5)
│  ├─ Mobile App (loading...)
│  │  ├─ Navigation
│  │  ├─ Screens (load 5)
│  │  ├─ Components
│  │  └─ Assets
│  ├─ Design System
│  └─ Docs
└─ Settings
```

---

## 7. Responsive Behavior Examples

### 7.1 Desktop (1920px)

```
┌──────────────────────────────────────────────────────────────┐
│ Breadcrumbs: Home > Project > Item Type > Item Name         │
├───────────────────────────────────────────┬──────────────────┤
│ Graph Canvas (70%)                        │ Detail Panel     │
│                                            │ (30%, 560px)     │
│ ┌──────────┐      ┌──────────┐           │ ┌──────────────┐ │
│ │ 📦       │  →   │ 📦       │  →  ...   │ │ Header (35px)│ │
│ │ Comp 1   │      │ Comp 2   │           │ │ Tabs (40px)  │ │
│ └──────────┘      └──────────┘           │ │              │ │
│                                            │ │ Content area │ │
│ ┌──────────┐      ┌──────────┐           │ │ (scrollable)  │ │
│ │ 🎨       │  →   │ 📄       │  →  ...   │ │              │ │
│ │ Theme    │      │ Page     │           │ │              │ │
│ └──────────┘      └──────────┘           │ │ Footer (48px)│ │
│                                            │ └──────────────┘ │
└───────────────────────────────────────────┴──────────────────┘
```

### 7.2 Tablet (1024px)

```
┌──────────────────────────────────────────────────────────────┐
│ Breadcrumbs: Home > ... > Item Type > Item Name             │
├───────────────────────────────────────────┬──────────────────┤
│ Graph Canvas (60%)                        │ Detail Panel     │
│                                            │ (40%, 380px)     │
│ ┌──────────┐      ┌──────────┐           │ ┌──────────────┐ │
│ │ 📦       │  →   │ 📦       │           │ │ Header       │ │
│ │ Comp 1   │      │ Comp 2   │           │ │ [Tabs]       │ │
│ └──────────┘      └──────────┘           │ │              │ │
│                                            │ │ Content area │ │
│ (Fewer nodes visible due to space)       │ │              │ │
│                                            │ │ Footer       │ │
│                                            │ └──────────────┘ │
└───────────────────────────────────────────┴──────────────────┘
```

### 7.3 Mobile (375px)

```
┌──────────────────────────────┐
│ Breadcrumbs: Home / Item ... │ ← Truncated
├──────────────────────────────┤
│ Graph Canvas                 │
│ (Full width, stacked nodes)  │
│                              │
│ ┌────────────────┐           │
│ │ 📦 Component   │           │
│ │ (Larger taps)  │           │
│ └────────────────┘           │
│          │                   │
│          ↓                   │
│ ┌────────────────┐           │
│ │ 📦 Component   │           │
│ └────────────────┘           │
│                              │
├──────────────────────────────┤
│ Detail Panel (Full Screen)   │
│ (Overlaid as modal)          │
│ ┌────────────────┐           │
│ │ Header [X]     │           │
│ │ [Tabs]         │           │
│ │                │           │
│ │ Content area   │           │
│ │ (scrollable)   │           │
│ │                │           │
│ │ Footer         │           │
│ └────────────────┘           │
└──────────────────────────────┘
```

---

## 8. Accessibility Examples

### 8.1 Screen Reader Announcements

```
NAVIGATION ANNOUNCEMENT:
Narrator: "Graph navigation list. Press arrow keys to move between nodes."

AFTER ARROW DOWN:
Narrator: "Component Button, type component, status in progress,
           3 incoming links, 5 outgoing links. Press Enter to select."

AFTER ENTER:
Narrator: "Component Button selected. Details panel opened.
           Navigation list with Details, Links, Preview, Code tabs.
           Use Tab to navigate through panel content."

AFTER BREADCRUMB CLICK:
Narrator: "You are in Mobile App screen. Back to Projects level."

AFTER ESCAPE:
Narrator: "Details panel closed. Component Button still focused.
           Press Enter to open again."
```

### 8.2 Focus Indicators

```
Node Focus (no selection):
┌──────────────────┐
┃ 📦 Component     ┃  ← 3px solid border with primary color
┃                  ┃     and focus glow (box-shadow)
└──────────────────┘

Node Selected (pill expanded):
┌──────────────────────────┐
┃ ▼ 📦 Component Button    ┃  ← Same border + highlight
┃ 🟢 In Review | ← 3 | 5 → ┃
┃ Owner: @dev              ┃
┃                          ┃
┃ [Collapse] [Open Panel]  ┃
└──────────────────────────┘

Focus within breadcrumbs:
Home / Project[focus indicator]  / Item

Focus within link list (in panel):
┌──────────────────────┐
│ Incoming (3)         │
│ ├─ Related (2)       │
│   ├─ Theme System [focused with box highlight]
│   └─ Color Palette   │
│ └─ Uses (1)          │
│   └─ Typography      │
└──────────────────────┘
```

---

## 9. Comparison: Different Tool Approaches

### 9.1 Pattern Comparison Matrix (Visual)

```
                  Figma    Miro     Linear   React Flow   Trace(Now)  Trace(Proposed)
Inline Pills      -        ✓        ✓        Custom       ✓           ✓✓ (enhanced)
Side Panel        ✓        -        ✓        Panel        ✓           ✓
Full Page         -        ✓        ✓        Custom       ✓           ✓
Keyboard Nav      ⚠️        ⚠️        ✓✓       Limited      ⚠️          ✓✓ (new)
Breadcrumbs       -        -        ✓        -            -           ✓ (new)
Deep Hierarchy    ✓        ✓        ✓        Limited      Limited     ✓ (enhanced)
Edit In-Place     ✓✓       -        ✓        Limited      -           ✓ (new)
Agent Actions     -        -        -        -            -           ✓ (new)
Accessibility     ✓        ⚠️        ✓        ⚠️           ⚠️          ✓✓ (new)

Legend:
✓✓ = Full featured
✓  = Supported
⚠️  = Partial/needs work
-  = Not supported
```

---

## 10. Decision Tree: When to Use Each Pattern

```
User Action: Click on node
    │
    ├─ Is this the first interaction with this node?
    │  ├─ YES: Show expanded inline pill (quick preview)
    │  │       └─ Content: Type, status, counts, owner
    │  │
    │  └─ NO: Is the side panel already open?
    │         ├─ YES: Update panel content (same node)
    │         │       └─ Keep panel open
    │         │
    │         └─ NO: User intends to explore
    │                 └─ Show expanded pill + offer panel

User Action: Double-click or press Ctrl+Enter
    │
    └─ Open side panel
       └─ Content: Full details with tabs
       └─ Keep graph visible
       └─ Allow continued navigation

User Action: Click breadcrumb
    │
    └─ Navigate to that level
       └─ Focus on breadcrumb item
       └─ Close side panel
       └─ Update all navigation state

User Action: Press Escape
    │
    ├─ Is side panel open?
    │  ├─ YES: Close panel, keep node focused
    │  │
    │  └─ NO: Deselect node, close expanded pill
    │
    └─ Return focus to graph canvas

User Action: Press Right arrow (expand node tree)
    │
    └─ Does this node have children?
       ├─ YES: Expand to show children (1 level)
       │       └─ Load children if lazy-loaded
       │
       └─ NO: Move focus to next sibling or adjacent node
```

---

## 11. Performance Indicators

### 11.1 Loading States

```
Expanding node with many links:
┌─────────────────────────────┐
│ 📦 Component Button         │
│ Status: In Progress         │
│ Links: [⏳ Loading...]      │
└─────────────────────────────┘

Opening side panel (data loading):
┌──────────────────────────────────┐
│ ⏳ Loading component details...   │
│                                  │
│ [Skeleton screens or spinner]    │
└──────────────────────────────────┘

After completion:
┌──────────────────────────────────┐
│ ✓ Component Button               │
│ Details | Links | Preview | Code │
│ [Full content visible]           │
└──────────────────────────────────┘
```

### 11.2 Error States

```
Failed to load panel:
┌──────────────────────────────────┐
│ ✕ Component Button               │
│                                  │
│ ⚠️ Failed to load details        │
│ (check your connection)          │
│                                  │
│ [Retry] [Close]                  │
└──────────────────────────────────┘

Partial data failure:
┌──────────────────────────────────┐
│ Component Button                 │
│ Details | Links | Preview | Code │
│                                  │
│ ✓ Loaded                         │
│ ✓ Loaded                         │
│ ✕ Failed to load preview         │
│ ✓ Loaded                         │
│                                  │
│ [Retry Failed Items]             │
└──────────────────────────────────┘
```

---

## 12. Recommended Implementation Order

### Priority 1 (High Impact, Moderate Effort)
1. **Keyboard Navigation** (arrow keys, Enter, Escape)
   - Immediate UX improvement
   - Enables power users
   - Required for accessibility

2. **Breadcrumb Navigation** (location awareness)
   - Solves deep hierarchy problem
   - Improves discoverability
   - Simple to implement

### Priority 2 (Medium Impact, Low Effort)
3. **Enhanced Node Pills** (status badges, counts)
   - Better visual hierarchy
   - Reduces clicks to detail
   - Leverages existing components

4. **Edit Affordances** (instant status update)
   - Quick wins for common tasks
   - Visible distinction for complex edits
   - Reduces friction

### Priority 3 (High Impact, High Effort)
5. **Deep Hierarchy Support** (tree view, lazy loading)
   - Handles complex projects
   - Improves performance
   - Requires refactoring

---

## Quick Reference: Keyboard Shortcuts

| Action | Keys | Context | Result |
|--------|------|---------|--------|
| Focus next node | `↓` or `→` | Graph | Move focus to adjacent node |
| Focus prev node | `↑` or `←` | Graph | Move focus to adjacent node |
| Expand/Select | `Enter` or `Space` | Focused node | Open side panel |
| Quick edit | `Ctrl+Enter` | Expanded pill | Focus on edit field |
| Go to first | `Home` | Graph | Focus on first node |
| Go to last | `End` | Graph | Focus on last node |
| Close panel | `Esc` | Any | Close all open overlays |
| Tab through | `Tab` | Panel | Navigate between controls |
| Expand all | `*` | Graph | Expand all visible nodes |
| Collapse all | `/` | Graph | Collapse all nodes |
| Navigate breadcrumb | `→` / `←` | Breadcrumbs | Move between levels |
| Jump to level | `Enter` | Breadcrumb | Navigate to that level |

---

**Last Updated:** January 24, 2026
**Document Status:** Ready for Design & Implementation
