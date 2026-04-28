# TraceRTM UX Design Specification

_Created on 2025-11-20 by BMad_
_Generated using BMad Method - Create UX Design Workflow v1.0_

---

## Executive Summary

TraceRTM is an agent-native, multi-view requirements traceability and project management system designed for AI-augmented solo developers managing multiple complex, rapidly evolving projects. The system enables instant project state comprehension through 8 core views (expanding to 32), seamless perspective switching (Feature → Code → Wireframe → Test → API), and coordination of 1-1000 AI agents working concurrently across projects.

The UX challenge is unique: creating an exceptional developer experience in a CLI/TUI environment that handles explosive complexity (10→500+ features, 100→10,000+ files) while maintaining sub-second response times and zero cognitive overhead.

**Project Understanding Confirmed:**
- Agent-first architecture for coordinating 1-1000 concurrent AI agents
- Multi-view system treating projects as multi-dimensional state spaces
- CLI-first with Rich terminal output, future TUI (Textual) interface
- Expert developer user managing 5-10 projects simultaneously
- Handles explosive scope changes (add 100 features today, cut 50 tomorrow)
- Local-first, PostgreSQL backend, Python 3.12+ with Typer CLI framework

---

## 1. Project Context & Users

### 1.1 Project Vision

TraceRTM is wider and deeper than traditional project management - it's a **complete project model manipulation system**. The vision is to make the entire mental model of a product tangible, queryable, and malleable for both humans and AI agents.

**Core Philosophy:**
- The project model IS the source of truth
- Every component is graspable, editable, and traceable
- Edits, additions, and removals are trivial operations
- Project identity and state are locked to robust requirements and validation criteria
- Both user and agents can intuitively play with and manipulate this model
- All integrations and features serve this central model

### 1.2 Target Users

**Primary User: AI-Augmented Expert Developer (You)**
- Managing 5-10 complex projects simultaneously
- Orchestrating 1-1000 AI agents across projects
- Expert-level technical skills (Python, SQL, CLI, APIs)
- Values speed, clarity, and control over visual polish
- Needs instant context switching without cognitive overhead

**Secondary User: AI Agent Swarms**
- 1-1000 agents per user
- Need structured, queryable, programmatic access
- Must understand project state to work effectively
- Concurrent operations require conflict detection
- Agent-friendly interfaces (CLI, Python API, JSON/YAML)

---

## 2. Core User Experience

### 2.1 Defining Experience

**The Core Experience: "Intuitive Model Manipulation"**

TraceRTM's defining experience is the ability to **intuitively and immediately grasp AND play with the entire model of a product**. This is not just viewing or editing - it's **model manipulation** where:

1. **Instant Comprehension**: The entire project model is graspable from any angle (8+ views)
2. **Effortless Manipulation**: Making edits, additions, removals is trivial
3. **Robust Truth**: Project identity/state/source of truth locked to requirements and validation
4. **Universal Access**: Both human and agents can play with the model equally well
5. **Deep Integration**: All features serve the central model manipulation experience

**What Users Should FEEL:**
- ✅ **Empowered and in control of chaos** - "I can handle 500 features because I can see and manipulate the whole model"
- ✅ **Efficient and productive (flow state)** - "Edits are so fast I don't break flow"
- ✅ **Calm despite complexity** - "The model is my anchor - I always know the truth"
- ✅ **Playful exploration** - "I can experiment with the model without fear"

**The "Tell a Friend" Moment:**
"You can see your ENTIRE project as a manipulable model - every feature, every file, every test, every API - all connected, all queryable, all editable in seconds. And your 100 agents can work with it just as easily as you can."

### 2.2 Critical User Actions (Most Frequent)

Based on this core experience, the most critical actions are:

1. **Model Exploration** - View switching, querying, relationship navigation
2. **Model Manipulation** - Create/update/delete items, bulk operations, linking
3. **Agent Orchestration** - Assign work, monitor progress, resolve conflicts
4. **Context Switching** - Jump between projects, restore mental state instantly
5. **Truth Validation** - Verify state, check progress, identify blockers

**What Must Be Absolutely Effortless:**
- Switching views (Feature → Code → Test) in <500ms
- Querying 10,000+ items in <1 second
- Creating/editing items without ceremony
- Understanding project state at a glance
- Agents accessing and updating the model programmatically

## 3. Platform & Inspiration Analysis

### 3.1 Platform Requirements

**Primary Platform: CLI (Command-Line Interface)**
- Python 3.12+ with Typer framework
- Rich library for beautiful terminal output (tables, colors, progress bars, panels)
- Sub-second response times critical for flow state
- Keyboard-driven, scriptable, automatable
- Works in standard terminals (Terminal.app, iTerm2, GNOME Terminal)

**Future Platform: TUI (Terminal User Interface)**
- Textual framework for interactive terminal UI
- Mouse support, real-time updates, visual dashboards
- Phase 2 enhancement for visual learners
- Maintains CLI speed with visual richness

**Platform Constraints:**
- No web browser, no mobile app (MVP)
- Terminal-native experience
- Local-first, no cloud dependency
- Must work offline

### 3.2 Inspiration Analysis

**Best-in-Class CLI/TUI Tools:**

1. **k9s** (Kubernetes TUI)
   - Real-time cluster monitoring in terminal
   - Multiple views (pods, services, logs) with instant switching
   - Keyboard shortcuts for power users
   - **UX Lessons**: View switching, real-time updates, keyboard-first navigation

2. **lazygit** (Git TUI)
   - Complex Git operations made simple
   - Panel-based layout showing multiple contexts
   - Intuitive keyboard navigation
   - **UX Lessons**: Multi-panel layouts, contextual actions, visual feedback

3. **GitHub CLI (gh)**
   - Natural language-like commands (`gh pr create`)
   - Rich table output with colors
   - Interactive prompts when needed
   - **UX Lessons**: Conversational commands, smart defaults, progressive disclosure

4. **Textual Framework Examples**
   - Modern TUI with CSS-like styling
   - Reactive updates, smooth animations
   - Widget composition
   - **UX Lessons**: Component-based design, responsive layouts, visual hierarchy

**Key UX Patterns to Adopt:**
- **Multi-view switching** (like k9s) - instant context changes
- **Panel-based layouts** (like lazygit) - see multiple dimensions simultaneously
- **Keyboard shortcuts** - power user efficiency
- **Rich visual feedback** - colors, tables, progress indicators
- **Smart defaults** - minimize required input
- **Progressive disclosure** - simple by default, powerful when needed

---

## 4. Design System Foundation

### 4.1 Design System Choice

**Selected: Custom CLI/TUI Design System**

**Rationale:**
TraceRTM is a terminal-native tool, so traditional web design systems (Material UI, shadcn/ui) don't apply. Instead, we're building on proven CLI/TUI frameworks:

**CLI Foundation (MVP):**
- **Typer** - Modern Python CLI framework with type hints
- **Rich** - Beautiful terminal formatting library
  - Tables with borders, colors, alignment
  - Progress bars and spinners
  - Panels and syntax highlighting
  - Tree views for hierarchies
  - Console markup for colors/styles

**TUI Foundation (Phase 2):**
- **Textual** - Modern Python TUI framework
  - CSS-like styling system
  - Reactive widgets and layouts
  - Built-in components (DataTable, Tree, Input, Button)
  - Mouse and keyboard support
  - Responsive layouts

**Component Strategy:**
- **CLI Components**: Tables, trees, panels, progress bars, prompts
- **TUI Components**: DataTable, Tree, ListView, Input, Button, Modal, Tabs
- **Custom Components**: Multi-view navigator, relationship graph, agent monitor

**Why Custom:**
- Terminal environment requires specialized components
- Rich/Textual provide primitives, we compose them for TraceRTM's unique needs
- Full control over model manipulation UX
- Optimized for expert developer workflow

---

## 5. Visual Foundation

### 5.1 Color System

**Terminal Color Palette (16-color safe + 256-color enhanced)**

**Semantic Colors:**
- **Primary (Cyan/Blue)**: `#00D7FF` - Main actions, navigation, focus
- **Secondary (Purple)**: `#AF87FF` - Supporting actions, metadata
- **Success (Green)**: `#00FF87` - Completed items, success states
- **Warning (Yellow)**: `#FFD700` - Blocked items, warnings
- **Error (Red)**: `#FF5F5F` - Failed items, errors, destructive actions
- **Info (Blue)**: `#5FAFFF` - Informational messages, help text

**Neutral Grayscale:**
- **Text Primary**: `#E4E4E4` (bright white) - Main content
- **Text Secondary**: `#A8A8A8` (gray) - Metadata, timestamps
- **Text Tertiary**: `#6C6C6C` (dim gray) - Disabled, inactive
- **Background**: Terminal default (usually black/dark)
- **Borders**: `#444444` (dark gray) - Table borders, panels

**Status Colors:**
- **Todo**: `#808080` (gray) - Not started
- **In Progress**: `#00D7FF` (cyan) - Active work
- **Blocked**: `#FFD700` (yellow) - Waiting/blocked
- **Complete**: `#00FF87` (green) - Done
- **Cancelled**: `#6C6C6C` (dim gray) - Cancelled

**Agent Activity Colors:**
- **Agent Active**: `#00D7FF` (cyan) - Agent working
- **Agent Idle**: `#808080` (gray) - Agent waiting
- **Agent Error**: `#FF5F5F` (red) - Agent failed
- **Agent Success**: `#00FF87` (green) - Agent completed

**Color Psychology:**
- **Cyan/Blue**: Trust, clarity, technology (primary brand)
- **Purple**: Creativity, innovation (agent intelligence)
- **Green**: Growth, success, completion
- **Yellow**: Attention, caution (blockers)
- **Red**: Urgency, errors, destructive actions

**Accessibility: High-Contrast Mode (Phase 2)**

For users with visual impairments or terminals with limited color support, TraceRTM provides a high-contrast mode that meets WCAG AAA standards (7:1 contrast ratio).

**High-Contrast Color Palette:**
- **Primary (Bright Cyan)**: `#00FFFF` - Main actions, navigation, focus (7.5:1 contrast on black)
- **Secondary (Bright Magenta)**: `#FF00FF` - Supporting actions, metadata (6.8:1 contrast on black)
- **Success (Bright Green)**: `#00FF00` - Completed items, success states (8.6:1 contrast on black)
- **Warning (Bright Yellow)**: `#FFFF00` - Blocked items, warnings (9.2:1 contrast on black)
- **Error (Bright Red)**: `#FF0000` - Failed items, errors (5.3:1 contrast on black, use bold for 7:1)
- **Info (Bright Blue)**: `#0000FF` - Informational messages (4.8:1 contrast on black, use bold for 7:1)

**High-Contrast Neutral Grayscale:**
- **Text Primary**: `#FFFFFF` (pure white) - Main content (21:1 contrast on black)
- **Text Secondary**: `#CCCCCC` (light gray) - Metadata, timestamps (12.6:1 contrast on black)
- **Text Tertiary**: `#999999` (medium gray) - Disabled, inactive (7.4:1 contrast on black)
- **Background**: `#000000` (pure black) - Maximum contrast
- **Borders**: `#666666` (medium-dark gray) - Table borders, panels (5.7:1 contrast on black)

**High-Contrast Status Colors:**
- **Todo**: `#CCCCCC` (light gray) - Not started (12.6:1 contrast)
- **In Progress**: `#00FFFF` (bright cyan) - Active work (7.5:1 contrast)
- **Blocked**: `#FFFF00` (bright yellow) - Waiting/blocked (9.2:1 contrast)
- **Complete**: `#00FF00` (bright green) - Done (8.6:1 contrast)
- **Cancelled**: `#999999` (medium gray) - Cancelled (7.4:1 contrast)

**High-Contrast Mode Toggle:**

**Configuration:**
```yaml
# ~/.tracertm/config.yaml
ui:
  theme: "high-contrast"  # Options: "developer-focus" (default), "high-contrast"
  force_bold: true        # Force bold text for better contrast
  use_symbols: true       # Use symbols + colors for status (not just colors)
```

**CLI Flag:**
```bash
# Enable high-contrast mode for single command
rtm view FEATURE --theme high-contrast

# Enable high-contrast mode globally
rtm config set ui.theme high-contrast

# Disable high-contrast mode
rtm config set ui.theme developer-focus
```

**Environment Variable:**
```bash
# Enable high-contrast mode via environment variable
export TRACERTM_THEME=high-contrast
rtm view FEATURE
```

**Automatic Detection:**
TraceRTM can auto-detect limited color support and switch to high-contrast mode:
```python
# Auto-detect terminal color support
import os
if os.environ.get('TERM') in ['linux', 'vt100', 'xterm']:
    # Limited color support detected, use high-contrast mode
    theme = 'high-contrast'
```

**High-Contrast Mode Features:**
- ✅ WCAG AAA compliance (7:1 contrast ratio minimum)
- ✅ Symbols + colors for status (not just colors) - e.g., `✓ Complete`, `⚠ Blocked`, `○ Todo`
- ✅ Bold text for critical information
- ✅ Increased border thickness for tables and panels
- ✅ No subtle color variations (only high-contrast colors)
- ✅ Works on terminals with limited color support (16-color, 8-color)

**High-Contrast Mode Example:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ FEATURE VIEW - Project: auth-system                    [50 items]  │
├══════╪═════════════════════════╪══════════╪══════════╪═════════════┤
│ ID   │ Title                   │ Status   │ Progress │ Owner       │
├══════╪═════════════════════════╪══════════╪══════════╪═════════════┤
│ F-01 │ User Authentication     │ ⚡ PROG  │ 75%      │ team-alpha  │
│ F-02 │ OAuth Integration       │ ⚡ PROG  │ 40%      │ agent-12    │
│ F-03 │ Password Reset          │ ✓ DONE   │ 100%     │ COMPLETE    │
└══════╧═════════════════════════╧══════════╧══════════╧═════════════┘
```

**Color Blindness Support:**
TraceRTM's high-contrast mode also supports color blindness:
- **Symbols + Colors**: Status uses both symbols and colors (not just colors)
- **Protanopia/Deuteranopia (Red-Green)**: Use cyan/yellow/magenta instead of red/green
- **Tritanopia (Blue-Yellow)**: Use red/cyan/magenta instead of blue/yellow
- **Monochromacy**: Symbols only, no color dependency

**Testing:**
- Test with color blindness simulators (Coblis, Color Oracle)
- Test on terminals with limited color support (Linux console, xterm)
- Test with screen readers (VoiceOver, NVDA)

### 5.2 Typography System

**Terminal Fonts (User-Controlled):**
- Users choose their terminal font (Menlo, Monaco, Fira Code, JetBrains Mono)
- TraceRTM respects terminal font settings
- Monospace required for table alignment

**Text Hierarchy (via Rich markup):**
- **H1 (View Titles)**: `[bold cyan]` - Large, bold, primary color
- **H2 (Section Headers)**: `[bold white]` - Bold white
- **H3 (Subsections)**: `[bold]` - Bold default color
- **Body Text**: Default terminal color
- **Metadata**: `[dim]` - Dimmed text for timestamps, IDs
- **Emphasis**: `[bold]` or `[italic]` - Important terms
- **Code/IDs**: `[cyan]` - Item IDs, file paths
- **Links**: `[blue underline]` - Clickable links (if terminal supports)

**Text Styles:**
- **Bold**: Headers, important actions, current selection
- **Dim**: Metadata, secondary information, disabled items
- **Italic**: Emphasis, descriptions
- **Underline**: Links, keyboard shortcuts
- **Strikethrough**: Cancelled items, deprecated features

### 5.3 Spacing & Layout System

**Spacing Scale (Character-Based):**
- **xs**: 1 space - Tight spacing within elements
- **sm**: 2 spaces - Default spacing between elements
- **md**: 4 spaces - Section spacing
- **lg**: 1 blank line - Major section separation
- **xl**: 2 blank lines - View separation

**Layout Grid:**
- Terminal width-aware (typically 80-120 characters)
- Responsive to terminal resize
- Tables auto-adjust column widths
- Panels use available width intelligently

**Container Widths:**
- **Full Width**: Tables, lists, panels (use full terminal width)
- **Centered**: Prompts, confirmations (centered in terminal)
- **Sidebar**: 30% width for navigation (TUI mode)
- **Main Content**: 70% width for content (TUI mode)

## 6. Design Direction & Layout Patterns

### 6.1 CLI Design Direction (MVP)

**Chosen Direction: "Dense Information Dashboard"**

**Layout Philosophy:**
- **Information-rich**: Show maximum relevant data without overwhelming
- **Scannable**: Tables and lists for quick visual parsing
- **Hierarchical**: Clear visual hierarchy through indentation and colors
- **Contextual**: Always show current view, project, and navigation hints

**Primary Layout Patterns:**

**1. Table View (Default for Lists)**
```
┌─────────────────────────────────────────────────────────────────────┐
│ FEATURE VIEW - Project: auth-system                    [50 items]  │
├──────┬─────────────────────────┬──────────┬──────────┬─────────────┤
│ ID   │ Title                   │ Status   │ Progress │ Owner       │
├──────┼─────────────────────────┼──────────┼──────────┼─────────────┤
│ F-01 │ User Authentication     │ ●●●●○    │ 75%      │ team-alpha  │
│ F-02 │ OAuth Integration       │ ●●○○○    │ 40%      │ agent-12    │
│ F-03 │ Password Reset          │ ●●●●●    │ 100%     │ COMPLETE    │
└──────┴─────────────────────────┴──────────┴──────────┴─────────────┘
```

**2. Tree View (Hierarchies)**
```
📦 Epic: User Management
├── 📋 Feature: Authentication
│   ├── ✓ Story: Login Flow
│   ├── ⚡ Story: OAuth Integration (in progress)
│   └── ○ Story: 2FA Support
├── 📋 Feature: User Profiles
│   └── ✓ Story: Profile CRUD
└── 📋 Feature: Permissions
    └── ○ Story: RBAC System
```

**3. Panel View (Multi-Context)**
```
┌─ Current Item ──────────────┐ ┌─ Relationships ─────────┐
│ Feature: OAuth Integration  │ │ Implements:             │
│ Status: In Progress (40%)   │ │  → code/oauth.py        │
│ Owner: agent-12             │ │  → code/oauth_handler.py│
│ Created: 2025-11-15         │ │ Tests:                  │
│ Updated: 2025-11-20         │ │  → test_oauth.py        │
└─────────────────────────────┘ │ Designs:                │
                                │  → wireframe/login.md   │
                                └─────────────────────────┘
```

**4. Progress Dashboard**
```
PROJECT OVERVIEW - auth-system
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Progress: ████████████░░░░░░░░ 60% (30/50 features)

By Status:
  Complete:     ████████████████████ 20 items (40%)
  In Progress:  ██████░░░░░░░░░░░░░░ 10 items (20%)
  Blocked:      ██░░░░░░░░░░░░░░░░░░  3 items (6%)
  Todo:         ████████████████░░░░ 17 items (34%)

Agent Activity:
  team-alpha:   ████████░░░░░░░░░░░░  8 items active
  agent-12:     ████░░░░░░░░░░░░░░░░  4 items active
  agent-23:     ██░░░░░░░░░░░░░░░░░░  2 items active
```

**Visual Hierarchy Principles:**
- **Bold + Color**: Current selection, primary actions
- **Dim**: Metadata, timestamps, IDs
- **Borders**: Group related information
- **Indentation**: Show hierarchy (2-4 spaces per level)
- **Icons/Symbols**: Quick visual scanning (✓ ● ○ ⚡ 📦 📋)
- **Progress Bars**: Visual completion status

**Density Level: Balanced**
- Not too sparse (wasted terminal space)
- Not too dense (overwhelming)
- ~20-30 items visible per screen
- Smart pagination for large lists

### 6.2 TUI Design Direction (Phase 2)

**Chosen Direction: "Multi-Panel Explorer"**

**Layout Philosophy:**
- **Panel-based**: Multiple views visible simultaneously
- **Keyboard-driven**: Vim-like navigation (hjkl, tab switching)
- **Real-time**: Live updates as agents work
- **Responsive**: Adapts to terminal size

**Primary Layout Pattern:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ TraceRTM - auth-system                              [F1: Help]      │
├──────────────┬──────────────────────────────────────────────────────┤
│ VIEWS        │ FEATURE VIEW                                         │
│              │ ┌────────────────────────────────────────────────┐   │
│ ● Feature    │ │ ID    Title              Status      Progress  │   │
│   Code       │ │ F-01  User Auth          ●●●●○       75%       │   │
│   Wireframe  │ │ F-02  OAuth Integration  ●●○○○       40%       │   │
│   API        │ │ F-03  Password Reset     ●●●●●       100%      │   │
│   Test       │ └────────────────────────────────────────────────┘   │
│   Database   │                                                      │
│   Roadmap    │ DETAILS - F-02: OAuth Integration                   │
│   Progress   │ Status: In Progress | Owner: agent-12               │
│              │ Created: 2025-11-15 | Updated: 2025-11-20           │
├──────────────┤                                                      │
│ PROJECTS     │ Relationships:                                       │
│              │  → code/oauth.py (implements)                        │
│ ● auth-sys   │  → test_oauth.py (tests)                            │
│   payment    │  → wireframe/login.md (designs)                     │
│   analytics  │                                                      │
├──────────────┴──────────────────────────────────────────────────────┤
│ [Tab] Switch View | [/] Search | [?] Help | [q] Quit               │
└─────────────────────────────────────────────────────────────────────┘
```

**Panel Zones:**
1. **Left Sidebar (20%)**: View switcher + Project switcher
2. **Main Content (60%)**: Current view (table, tree, details)
3. **Right Panel (20%)**: Context (relationships, metadata, agent activity)
4. **Top Bar**: Project name, global actions
5. **Bottom Bar**: Keyboard shortcuts, status

**Interaction Patterns:**
- **Tab/Shift+Tab**: Cycle through panels
- **hjkl or Arrow Keys**: Navigate within panel
- **Enter**: Select/drill down
- **Esc**: Go back/cancel
- **/ (slash)**: Search/filter
- **? (question)**: Help overlay
- **Number keys (1-8)**: Quick view switching

---

## 7. User Journey Flows

### 7.1 Critical User Journeys

**Journey 1: Daily Project Check-In**

**User Goal:** Understand current state of all projects and decide what to work on

**Flow:**
1. **Launch**: `rtm dashboard --all-projects`
   - User sees: Multi-project overview with progress, blockers, agent activity
   - User does: Scan for blockers, check progress
   - System responds: Highlights blockers in yellow, shows agent activity

2. **Drill Down**: Select project with blockers
   - User sees: Project-specific dashboard
   - User does: Identify blocked items
   - System responds: Shows blocked items with reasons

3. **Take Action**: Unblock items or reassign
   - User sees: Item details and blocking relationships
   - User does: `rtm update F-02 --status in_progress` or `rtm assign F-02 --agent team-beta`
   - System responds: Updates status, notifies agents, recalculates progress

**Journey 2: Multi-View Model Exploration**

**User Goal:** Understand a feature from all angles (code, tests, wireframes, APIs)

**Flow:**
1. **Start in Feature View**: `rtm view feature`
   - User sees: Table of features
   - User does: Select feature F-02 (OAuth Integration)
   - System responds: Shows feature details + relationships

2. **Navigate to Code**: `rtm show F-02 --related code`
   - User sees: All code files implementing this feature
   - User does: Select code/oauth.py
   - System responds: Shows file details, can view content

3. **Check Tests**: `rtm show F-02 --related test`
   - User sees: All tests validating this feature
   - User does: Check test coverage
   - System responds: Shows test status, coverage %

4. **View Wireframe**: `rtm show F-02 --related wireframe`
   - User sees: Design mockups for this feature
   - User does: Review UX design
   - System responds: Shows wireframe content or link

**Journey 3: Bulk Model Manipulation**

**User Goal:** Add 50 new features from brainstorming session

**Flow:**
1. **Prepare YAML**: Create features.yaml with 50 features
   - User does: Edit YAML file with feature definitions
   - Format: Standard schema (title, description, status, owner)

2. **Import**: `rtm import features.yaml --view feature`
   - User sees: Preview of items to be created
   - User does: Confirm import
   - System responds: Creates 50 features, shows summary

3. **Validate**: `rtm view feature --filter created:today`
   - User sees: All newly created features
   - User does: Spot-check for errors
   - System responds: Shows items, allows quick edits

4. **Assign to Agents**: `rtm assign --filter created:today --agents team-alpha,team-beta`
   - User sees: Assignment preview
   - User does: Confirm assignments
   - System responds: Distributes work to agents, updates status

**Journey 4: Agent Orchestration**

**User Goal:** Monitor 100 agents working across 3 projects

**Flow:**
1. **Agent Dashboard**: `rtm agents --all-projects`
   - User sees: Table of all agents, their status, current work
   - User does: Scan for errors or idle agents
   - System responds: Highlights errors in red, idle in gray

2. **Drill into Agent**: Select agent-12
   - User sees: Agent's work history, current assignments, performance
   - User does: Check what agent is working on
   - System responds: Shows current item, progress, blockers

3. **Resolve Conflict**: Agent reports conflict on F-02
   - User sees: Conflict details (two agents edited same item)
   - User does: Choose resolution (keep version A, merge, manual edit)
   - System responds: Resolves conflict, notifies agents, updates item

4. **Reassign Work**: Move work from slow agent to fast agent
   - User sees: Agent workload comparison
   - User does: `rtm reassign --from agent-12 --to agent-23 --items F-02,F-03`
   - System responds: Transfers assignments, notifies agents

**Journey 5: Context Switching Between Projects**

**User Goal:** Switch from auth-system to payment-system project

**Flow:**
1. **Current State**: Working in auth-system, Feature view
   - User does: `rtm project switch payment-system`
   - System responds: <500ms switch, shows payment-system Feature view
   - User sees: Instant context - last view used in payment-system

2. **Restore Mental State**: What was I working on?
   - User does: `rtm diff --since yesterday`
   - System responds: Shows all changes since yesterday
   - User sees: Recent edits, agent activity, new items

3. **Resume Work**: Continue where left off
   - User does: Navigate to last edited item
   - System responds: Shows item details, relationships
   - User sees: Full context restored, ready to work

**Flow Approach: Hybrid (CLI + TUI)**
- **CLI**: Fast, scriptable, automatable (primary for MVP)
- **TUI**: Visual, real-time, multi-panel (Phase 2 for complex monitoring)
- **Seamless**: Same commands work in both modes

## 8. Component Library Strategy

### 8.1 CLI Components (MVP - Rich Library)

**Core Components from Rich:**

1. **Table**
   - Purpose: Display lists of items (features, files, tests, etc.)
   - Variants: Bordered, borderless, compact, expanded
   - States: Default, highlighted row, sorted column
   - Usage: Primary view for all list-based views

2. **Tree**
   - Purpose: Display hierarchical relationships (epic→feature→story→task)
   - Variants: Expanded, collapsed, with icons
   - States: Default, highlighted node, expanded/collapsed
   - Usage: Hierarchical navigation, relationship visualization

3. **Panel**
   - Purpose: Group related information with borders
   - Variants: Titled, borderless, colored border
   - States: Default, highlighted, dimmed
   - Usage: Item details, context panels, help text

4. **Progress Bar**
   - Purpose: Show completion percentage
   - Variants: Bar, spinner, percentage text
   - States: Active, complete, indeterminate
   - Usage: Item progress, bulk operations, agent activity

5. **Prompt**
   - Purpose: Interactive user input
   - Variants: Text input, yes/no, choice selection
   - States: Default, error, success
   - Usage: Confirmations, data entry, interactive commands

6. **Console Markup**
   - Purpose: Styled text output
   - Variants: Bold, dim, italic, colored, underlined
   - States: N/A (styling only)
   - Usage: All text output, emphasis, status indicators

### 8.2 TUI Components (Phase 2 - Textual Framework)

**Core Components from Textual:**

1. **DataTable**
   - Purpose: Interactive table with sorting, filtering, selection
   - Variants: Single-select, multi-select, read-only
   - States: Default, row selected, cell focused, sorted
   - Usage: All list views with interaction

2. **Tree (Interactive)**
   - Purpose: Expandable/collapsible hierarchy
   - Variants: Single-select, multi-select, checkboxes
   - States: Expanded, collapsed, selected, focused
   - Usage: Hierarchical navigation with interaction

3. **ListView**
   - Purpose: Scrollable list of items
   - Variants: Single-select, multi-select
   - States: Item selected, item focused, scrolling
   - Usage: Simple lists, menus, navigation

4. **Input**
   - Purpose: Text input field
   - Variants: Single-line, multi-line, password
   - States: Default, focused, error, disabled
   - Usage: Search, filters, data entry

5. **Button**
   - Purpose: Clickable action trigger
   - Variants: Primary, secondary, destructive
   - States: Default, hover, active, disabled
   - Usage: Actions, confirmations, navigation

6. **Modal/Dialog**
   - Purpose: Overlay for focused interaction
   - Variants: Small, medium, large, full-screen
   - States: Open, closed, loading
   - Usage: Confirmations, detailed forms, help

7. **Tabs**
   - Purpose: Switch between view panels
   - Variants: Top tabs, side tabs
   - States: Active tab, inactive tab, focused
   - Usage: View switching, multi-context display

### 8.3 Custom Components (TraceRTM-Specific)

**1. MultiViewNavigator**
- **Purpose**: Quick switching between 8 views
- **Anatomy**:
  - View list (Feature, Code, Wireframe, API, Test, Database, Roadmap, Progress)
  - Active view indicator
  - Keyboard shortcuts (1-8)
- **States**: Active view (highlighted), inactive views (dim)
- **Behavior**: Click or press number to switch views
- **Accessibility**: Keyboard navigation, screen reader announces view

**2. RelationshipGraph**
- **Purpose**: Visualize item relationships across views
- **Anatomy**:
  - Central item (current focus)
  - Related items grouped by relationship type (implements, tests, designs, depends_on, blocks)
  - Connection lines (ASCII art in CLI, visual in TUI)
- **States**: Default, relationship type highlighted, item selected
- **Behavior**: Navigate through relationships, drill into related items
- **Accessibility**: Keyboard navigation, relationship type announced

**3. AgentActivityMonitor**
- **Purpose**: Real-time agent status and work tracking with conflict detection
- **Anatomy**:
  - Agent list with status indicators
  - Current work item per agent
  - Activity timeline
  - Error/conflict indicators with counts
  - Conflict rate per agent (conflicts/operations)
- **States**:
  - Agent active (cyan)
  - Agent idle (gray)
  - Agent error (red)
  - Agent success (green)
  - Agent conflict (yellow) - optimistic locking conflict detected
- **Behavior**:
  - Auto-refresh every 5 seconds
  - Click to drill into agent details
  - Show conflict history and retry attempts
  - Alert when conflict rate >5% for any agent
- **Conflict Display**:
  - `⚠ agent-456: 3 conflicts (2% rate) - retrying...`
  - `✓ agent-123: 0 conflicts (0% rate) - healthy`
- **Accessibility**: Status announced, keyboard navigation, conflict alerts

**4. ProgressDashboard**
- **Purpose**: Multi-dimensional progress visualization
- **Anatomy**:
  - Overall progress bar
  - Progress by status (complete, in_progress, blocked, todo)
  - Progress by view (feature, code, test completion)
  - Agent activity summary
- **States**: Real-time updating, historical comparison
- **Behavior**: Auto-refresh, drill down into categories
- **Accessibility**: Progress percentages announced

**5. BulkOperationPreview**
- **Purpose**: Preview bulk changes before applying
- **Anatomy**:
  - Summary of changes (X items to create/update/delete)
  - Sample items (first 10)
  - Validation warnings/errors
  - Confirm/cancel actions
- **States**: Preview, validating, confirmed, cancelled
- **Behavior**: Show preview, allow review, confirm to apply
- **Accessibility**: Change count announced, keyboard confirmation

---

## 9. UX Pattern Decisions

### 9.1 Consistency Rules

**Button Hierarchy:**
- **Primary Action**: Bold cyan text, `[bold cyan]` - Main action (create, update, confirm)
- **Secondary Action**: Normal white text - Supporting action (cancel, back)
- **Tertiary Action**: Dim text, `[dim]` - Optional action (help, advanced)
- **Destructive Action**: Bold red text, `[bold red]` - Delete, remove, destructive

**Feedback Patterns:**
- **Success**: Green checkmark + message, `✓ [green]Success message[/green]`
- **Error**: Red X + message, `✗ [red]Error message[/red]`
- **Warning**: Yellow exclamation + message, `⚠ [yellow]Warning message[/yellow]`
- **Info**: Blue info icon + message, `ℹ [blue]Info message[/blue]`
- **Loading**: Spinner or progress bar, `[cyan]Processing...[/cyan]`

**Conflict Feedback Patterns (Optimistic Locking):**
- **Conflict Detected**: Yellow warning with retry indicator
  - `⚠ [yellow]Item updated by another agent. Retrying... (attempt 2/3)[/yellow]`
- **Retry in Progress**: Cyan spinner with backoff indicator
  - `[cyan]↻ Retrying in 200ms...[/cyan]`
- **Retry Success**: Green checkmark with recovery message
  - `✓ [green]Retry successful after 2 attempts[/green]`
- **Retry Failed**: Red X with manual resolution prompt
  - `✗ [red]Update failed after 3 retries. Item was modified by agent-456.[/red]`
  - `[dim]Options: (r)etry manually, (v)iew current state, (c)ancel[/dim]`
- **Conflict Details**: Show conflicting agent and timestamp
  - `[dim]Last modified by: agent-456 at 2025-11-21 14:32:15 UTC[/dim]`

**Conflict Resolution UI (Manual Intervention):**

When automatic retries fail, present conflict resolution options:

```
⚠ Conflict Resolution Required

Item: "User Authentication" (feature-123)
Your change: status = "in_progress"
Current state: status = "complete" (modified by agent-456 at 14:32:15)

Options:
  [r] Retry with current state (overwrite agent-456's change)
  [m] Merge changes (keep both if possible)
  [v] View full diff
  [c] Cancel your change
  [i] Ignore and continue

Choice:
```

**Conflict Prevention Patterns:**
- **Agent Coordination**: Show which agents are working on which items
  - `[dim]⚠ agent-456 is currently editing this item[/dim]`
- **Lock Indicator**: Visual indicator when item is being edited
  - `🔒 [yellow]Locked by agent-456[/yellow]`
- **Stale Data Warning**: Warn when viewing old data
  - `⚠ [yellow]This data is 5 minutes old. Refresh to see latest.[/yellow]`

**Form Patterns:**
- **Label Position**: Above input (terminal constraint)
- **Required Field**: Asterisk after label, `Field Name*:`
- **Validation Timing**: On submit (CLI), on blur (TUI)
- **Error Display**: Inline below field, red text
- **Help Text**: Dim text below field, `[dim]Help text[/dim]`

**Modal Patterns (TUI):**
- **Size Variants**: Small (40% width), Medium (60%), Large (80%), Full-screen (100%)
- **Dismiss Behavior**: Escape key, click outside (TUI), explicit close button
- **Focus Management**: Auto-focus first input, trap focus in modal
- **Stacking**: Only one modal at a time (simplicity)

**Navigation Patterns:**
- **Active State**: Bold cyan text, `[bold cyan]● Active View[/bold cyan]`
- **Breadcrumb**: Show current path, `Project > View > Item`
- **Back Button**: Escape key or `b` key, browser back not applicable
- **Deep Linking**: Support item IDs in commands, `rtm show F-02`

**Empty State Patterns:**
- **First Use**: Helpful message + CTA, `No items yet. Create your first: rtm create feature "Title"`
- **No Results**: Suggestion, `No results found. Try: rtm query --filter status:todo`
- **Cleared Content**: Undo option if applicable, `All items deleted. Undo: rtm undo`

**Confirmation Patterns:**
- **Delete**: Always confirm, `Delete F-02? [y/N]` (default No)
- **Leave Unsaved**: Warn if changes, `Unsaved changes. Continue? [y/N]`
- **Irreversible Actions**: Double confirmation for bulk deletes, `Delete 50 items? Type 'DELETE' to confirm:`

**Notification Patterns:**
- **Placement**: Inline in output (CLI), top-right corner (TUI)
- **Duration**: Persist until dismissed (CLI), 5s auto-dismiss (TUI)
- **Stacking**: Queue messages (CLI), stack up to 3 (TUI)
- **Priority**: Critical (red, persistent), Important (yellow, 10s), Info (blue, 5s)

**Search Patterns:**
- **Trigger**: `/` key (TUI), `rtm query` command (CLI)
- **Results Display**: Instant as you type (TUI), on enter (CLI)
- **Filters**: `--filter` flag with structured syntax, `status:blocked AND owner:agent-12`
- **No Results**: Helpful message, suggest alternatives

**Date/Time Patterns:**
- **Format**: Relative for recent (`2 hours ago`), absolute for old (`2025-11-15`)
- **Timezone**: User's local timezone
- **Pickers**: Text input with format hint (CLI), calendar picker (TUI)

### 9.2 Keyboard Shortcuts (Power User Efficiency)

**Global Shortcuts:**
- `?` - Help overlay
- `/` - Search/filter
- `q` - Quit
- `Esc` - Back/cancel
- `Tab` - Next panel/field
- `Shift+Tab` - Previous panel/field

**View Switching:**
- `1` - Feature view
- `2` - Code view
- `3` - Wireframe view
- `4` - API view
- `5` - Test view
- `6` - Database view
- `7` - Roadmap view
- `8` - Progress view

**Navigation:**
- `j/k` or `↓/↑` - Move down/up in list
- `h/l` or `←/→` - Move left/right in panels
- `g` - Go to top
- `G` - Go to bottom
- `Enter` - Select/drill down
- `Backspace` - Go back

**Actions:**
- `c` - Create new item
- `e` - Edit selected item
- `d` - Delete selected item
- `a` - Assign to agent
- `r` - Refresh view
- `s` - Save changes

**Filters:**
- `f` - Open filter dialog
- `Ctrl+f` - Advanced filter
- `Esc` - Clear filter

---

## 10. Responsive Design & Accessibility

### 10.1 Responsive Strategy

**Terminal Width Adaptation:**

**Narrow Terminals (< 80 columns):**
- Single-column layouts
- Abbreviated column headers
- Hide less critical columns
- Vertical stacking of panels
- Simplified navigation

**Standard Terminals (80-120 columns):**
- Multi-column tables (4-6 columns)
- Full headers and labels
- Side-by-side panels (2 columns)
- Standard navigation

**Wide Terminals (> 120 columns):**
- Maximum columns (6-8)
- Three-column layouts
- Additional metadata visible
- Expanded panels

**Terminal Height Adaptation:**
- Auto-pagination based on terminal height
- Show N-5 items (reserve 5 lines for header/footer)
- Scrollable content in TUI mode
- Smart truncation in CLI mode

**Responsive Patterns:**
- **Tables**: Hide columns progressively (least important first)
- **Panels**: Stack vertically on narrow terminals
- **Navigation**: Collapse to icons on narrow terminals
- **Text**: Truncate with ellipsis, show full on hover/select

### 10.2 Accessibility Strategy

**WCAG Compliance Target: Level AA**

**Rationale:**
- Developer tool, but accessibility still important
- Keyboard-only navigation is native to CLI/TUI
- Screen reader support for visually impaired developers
- Color contrast for color blindness

**Key Requirements:**

**Color Contrast:**
- Text vs Background: 4.5:1 minimum (AA standard)
- Large Text (headers): 3:1 minimum
- Status colors distinguishable without color (icons + text)
- Test with color blindness simulators

**Keyboard Navigation:**
- All interactive elements accessible via keyboard (native to terminal)
- Visible focus indicators (bold, underline, or color change)
- Logical tab order
- Keyboard shortcuts documented and consistent

**Screen Reader Support:**
- ARIA labels for TUI components (Textual supports this)
- Meaningful text alternatives for visual elements
- Status announcements (item created, error occurred)
- Progress updates announced

**Visual Clarity:**
- Minimum font size: User's terminal font (user-controlled)
- Touch target size: N/A (keyboard-driven)
- Clear visual hierarchy (bold, colors, spacing)
- Icons paired with text labels

**Error Handling:**
- Clear, descriptive error messages
- Suggest fixes when possible
- Error location clearly indicated
- Recovery options provided

**Testing Strategy:**
- **Automated**: Terminal accessibility linters (if available)
- **Manual**: Keyboard-only navigation testing
- **Screen Reader**: Test with terminal screen readers (if available)
- **Color Blindness**: Test with color blindness simulators

**Accessibility Features:**
- High contrast mode option (user terminal setting)
- Reduced motion option (disable animations in TUI)
- Text-only mode (CLI is inherently text-only)
- Customizable keyboard shortcuts

## 11. Implementation Guidance

### 11.1 Completion Summary

**✅ UX Design Specification Complete!**

**What We Created:**

1. **Design System Foundation**
   - Custom CLI/TUI design system based on Rich (MVP) and Textual (Phase 2)
   - 5 custom TraceRTM-specific components (MultiViewNavigator, RelationshipGraph, AgentActivityMonitor, ProgressDashboard, BulkOperationPreview)
   - Component strategy balancing framework primitives with custom needs

2. **Visual Foundation**
   - Developer Focus color theme (cyan primary, purple secondary, semantic status colors)
   - Terminal-optimized typography system with Rich markup
   - Character-based spacing scale and responsive layout grid
   - Interactive color theme visualizer: `docs/ux-color-themes.html`

3. **Design Direction**
   - Dense Dashboard approach (information-rich, scannable, hierarchical)
   - Table, Tree, Panel, and Progress Dashboard layout patterns
   - Multi-Panel TUI design for Phase 2
   - Interactive design direction mockups: `docs/ux-design-directions.html`

4. **User Journey Flows**
   - 5 critical journeys designed: Daily Check-In, Multi-View Exploration, Bulk Manipulation, Agent Orchestration, Context Switching
   - Hybrid CLI + TUI approach for flexibility
   - Progressive disclosure and smart defaults throughout

5. **UX Pattern Decisions**
   - 10 consistency rule categories established (buttons, feedback, forms, modals, navigation, empty states, confirmations, notifications, search, date/time)
   - Comprehensive keyboard shortcuts for power users (global, view switching, navigation, actions, filters)
   - Vim-like navigation patterns (hjkl, g/G, Tab, Esc)

6. **Responsive & Accessibility Strategy**
   - Terminal width adaptation (narrow <80, standard 80-120, wide >120 columns)
   - WCAG Level AA compliance target
   - Keyboard-first navigation (native to terminal)
   - Color contrast and screen reader support

**Core UX Principles:**

- **Speed**: Sub-second responses, keyboard-driven, no ceremony
- **Clarity**: Instant project state comprehension from any angle
- **Flexibility**: Handles chaos, rapid changes, explosive growth
- **Accessibility**: Keyboard-only, screen reader support, color-blind friendly
- **Playfulness**: Experiment with model without fear

**Deliverables:**

- ✅ UX Design Specification: `docs/ux-design-specification.md`
- ✅ Color Theme Visualizer: `docs/ux-color-themes.html`
- ✅ Design Direction Mockups: `docs/ux-design-directions.html`

### 11.2 Implementation Priorities

**Phase 1 (MVP - CLI with Rich):**

1. **Core CLI Framework**
   - Typer command structure with verb-noun pattern
   - Rich table, tree, panel, progress bar components
   - Color theme implementation (Developer Focus)
   - Keyboard shortcuts and shell completion

2. **Essential Views**
   - Feature, Code, Test views (highest priority)
   - Table and tree layout patterns
   - View switching commands (rtm view <name>)

3. **Critical Components**
   - MultiViewNavigator (view switching)
   - ProgressDashboard (project overview)
   - Basic relationship display

4. **UX Patterns**
   - Button hierarchy (primary, secondary, destructive)
   - Feedback patterns (success, error, warning, info, loading)
   - Search and filter patterns

**Phase 2 (TUI with Textual):**

1. **TUI Framework**
   - Textual multi-panel layout
   - Interactive DataTable, Tree, ListView
   - Real-time updates and live monitoring

2. **Advanced Components**
   - RelationshipGraph (visual relationship navigation)
   - AgentActivityMonitor (real-time agent tracking)
   - BulkOperationPreview (preview before apply)

3. **Enhanced Interactions**
   - Mouse support
   - Modal dialogs
   - Drag-and-drop (if Textual supports)

### 11.3 Developer Handoff Notes

**For Frontend/CLI Developers:**

- Use Rich library for all terminal output (tables, panels, progress bars, markup)
- Follow color theme exactly (hex codes in Visual Foundation section)
- Implement keyboard shortcuts as specified (global, view switching, navigation, actions)
- Respect terminal width adaptation rules (narrow/standard/wide)
- Test with color blindness simulators (symbols + colors for status)

**For UX Designers (if creating high-fidelity mockups):**

- Terminal constraints: monospace font, character-based layout, limited colors
- Focus on information hierarchy through bold, dim, color, indentation
- Design for keyboard-first interaction (no mouse in CLI mode)
- Consider real-time updates for TUI mode (agent activity, progress)

**For QA/Testing:**

- Test keyboard-only navigation (no mouse)
- Verify color contrast ratios (4.5:1 minimum for text)
- Test with screen readers (if terminal supports)
- Validate responsive behavior at different terminal widths (80, 100, 120, 140 columns)
- Test with color blindness simulators (status should be clear without color)

**For Documentation:**

- Document all keyboard shortcuts in help system
- Create interactive tutorial for first-time users
- Provide examples for common workflows (view switching, querying, bulk operations)
- Include ASCII art diagrams for layout patterns

---

## Appendix

### Related Documents

- **Product Requirements**: `docs/PRD.md`
- **Product Brief**: `docs/product-brief-TraceRTM-2025-11-20.md`

### Core Interactive Deliverables

This UX Design Specification was created through visual collaboration:

- **Color Theme Visualizer**: `docs/ux-color-themes.html`
  - Interactive HTML showing Developer Focus color theme
  - Live UI component examples in theme colors
  - Semantic color usage and psychology

- **Design Direction Mockups**: `docs/ux-design-directions.html`
  - Interactive HTML with 3 complete design approaches
  - Full-screen mockups of key screens (Feature View, Agent Activity)
  - Design philosophy and rationale for each direction

### Next Steps & Follow-Up Workflows

This UX Design Specification serves as input to:

- **Solution Architecture Workflow** - Define technical architecture with UX context (RECOMMENDED NEXT)
- **Component Showcase Workflow** - Create interactive component library
- **Wireframe Generation Workflow** - Create detailed wireframes from user flows
- **Interactive Prototype Workflow** - Build clickable HTML prototypes

### Version History

| Date       | Version | Changes                         | Author |
| ---------- | ------- | ------------------------------- | ------ |
| 2025-11-20 | 1.0     | Initial UX Design Specification | BMad   |

---

_This UX Design Specification was created through collaborative design facilitation using the BMad Method. All decisions were made with deep understanding of TraceRTM's unique value proposition: intuitive model manipulation for both humans and AI agents._

_The core insight - that TraceRTM is a **project model manipulation system**, not just a project management tool - shaped every UX decision from color choices to keyboard shortcuts to layout patterns._

_Ready for architecture design and implementation._


