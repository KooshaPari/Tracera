# User Journeys & Wireframes - TraceRTM

**Date**: 2025-11-22  
**Version**: 1.0  
**Status**: APPROVED

---

## USER JOURNEY 1: PROJECT MANAGER WORKFLOW

### Journey: "Plan and Track Project"

**User**: Sarah (Project Manager)  
**Goal**: Create project structure and track progress  
**Duration**: 30 minutes

### Step 1: Login
```
Sarah opens TraceRTM
→ Sees login page
→ Clicks "Sign in with WorkOS"
→ Authenticates with company SSO
→ Redirected to dashboard
```

### Step 2: Create Project Structure
```
Sarah clicks "New Item"
→ Sees item creation form
→ Enters title: "Q1 2025 Project"
→ Selects type: "REQUIREMENT"
→ Enters description
→ Clicks "Create"
→ Item appears in dashboard
```

### Step 3: Create Sub-Items
```
Sarah clicks "Add Sub-Item"
→ Creates "Design Phase"
→ Creates "Implementation Phase"
→ Creates "Testing Phase"
→ Creates "Deployment Phase"
```

### Step 4: Create Links
```
Sarah clicks "Create Link"
→ Selects "Design Phase" as source
→ Selects "Implementation Phase" as target
→ Selects link type: "DEPENDS_ON"
→ Clicks "Create"
→ Link appears in graph
```

### Step 5: View Graph
```
Sarah clicks "Graph View"
→ Sees all items and links
→ Zooms to see full structure
→ Hovers over nodes to see details
→ Sees circular dependency warning
```

### Step 6: Assign Agents
```
Sarah clicks "Assign Agent"
→ Selects "Design Phase"
→ Selects agent "Alice"
→ Clicks "Assign"
→ Agent receives notification
```

### Step 7: Monitor Progress
```
Sarah views "Dashboard"
→ Sees 4 items total
→ Sees 1 item ACTIVE (Design Phase)
→ Sees 3 items DRAFT
→ Sees agent "Alice" is WORKING
→ Sees real-time updates
```

---

## USER JOURNEY 2: DEVELOPER WORKFLOW

### Journey: "Implement Feature"

**User**: Bob (Developer)  
**Goal**: Implement feature and track progress  
**Duration**: 2 hours

### Step 1: Login
```
Bob opens TraceRTM
→ Sees login page
→ Clicks "Sign in with WorkOS"
→ Authenticates
→ Redirected to dashboard
```

### Step 2: Find Work
```
Bob clicks "Items View"
→ Sees all items
→ Filters by status: "DRAFT"
→ Filters by type: "IMPLEMENTATION"
→ Sees 5 items to work on
```

### Step 3: Claim Work
```
Bob clicks on "Implement User Auth"
→ Sees item details
→ Clicks "Claim Work"
→ Item status changes to ACTIVE
→ Bob's status changes to WORKING
→ Bob receives confirmation
```

### Step 4: View Dependencies
```
Bob clicks "View Dependencies"
→ Sees "Design User Auth" must be done first
→ Sees "Design User Auth" is ACTIVE
→ Sees "Test User Auth" depends on this
```

### Step 5: Write Code
```
Bob clicks "Code Editor"
→ Sees code editor with syntax highlighting
→ Writes implementation code
→ Sees auto-completion suggestions
→ Clicks "Format Code"
→ Code is formatted
```

### Step 6: Preview Code
```
Bob clicks "Live Preview"
→ Sees code execution in iframe
→ Sees console output
→ Sees any errors
→ Fixes errors
```

### Step 7: Run Quality Checks
```
Bob clicks "Quality Checks"
→ Sees completeness check: PASS
→ Sees consistency check: PASS
→ Sees performance check: PASS
→ Sees security check: PASS
```

### Step 8: Complete Work
```
Bob clicks "Complete Work"
→ Item status changes to ACTIVE (done)
→ Bob's status changes to IDLE
→ Next item "Test User Auth" is notified
→ Bob receives confirmation
```

---

## USER JOURNEY 3: REAL-TIME COLLABORATION

### Journey: "Collaborate on Design"

**User**: Alice & Charlie (Designers)  
**Goal**: Collaborate on design in real-time  
**Duration**: 1 hour

### Step 1: Both Login
```
Alice opens TraceRTM
→ Sees "Design Phase" item
→ Clicks to open

Charlie opens TraceRTM
→ Sees "Design Phase" item
→ Clicks to open
```

### Step 2: See Presence
```
Alice sees Charlie is online
→ Sees Charlie's cursor position
→ Sees Charlie's selection
→ Sees "Charlie is editing"
```

### Step 3: Collaborate
```
Alice updates item description
→ Charlie sees update in real-time
→ Charlie adds comment
→ Alice sees comment in real-time
→ No conflicts detected
```

### Step 4: Offline Work
```
Charlie loses internet connection
→ Charlie continues editing
→ Changes are queued locally
→ Charlie sees "Offline" indicator

Alice continues editing
→ Alice's changes sync normally
```

### Step 5: Sync When Online
```
Charlie regains internet connection
→ Changes sync automatically
→ Conflicts are resolved
→ Charlie sees "Synced" indicator
→ Alice sees Charlie's changes
```

---

## WIREFRAME 1: DASHBOARD VIEW

```
┌─────────────────────────────────────────────────────────┐
│ TraceRTM                                    [User] [Menu]│
├─────────────────────────────────────────────────────────┤
│ Dashboard                                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐  ┌──────────────────┐             │
│  │ Items by Status  │  │ Agent Status     │             │
│  │ ┌──────────────┐ │  │ ┌──────────────┐ │             │
│  │ │ DRAFT: 10    │ │  │ │ IDLE: 3      │ │             │
│  │ │ ACTIVE: 5    │ │  │ │ WORKING: 2   │ │             │
│  │ │ ARCHIVED: 2  │ │  │ │ ERROR: 0     │ │             │
│  │ └──────────────┘ │  │ └──────────────┘ │             │
│  └──────────────────┘  └──────────────────┘             │
│                                                          │
│  ┌──────────────────┐  ┌──────────────────┐             │
│  │ Recent Changes   │  │ Quality Metrics  │             │
│  │ ┌──────────────┐ │  │ ┌──────────────┐ │             │
│  │ │ Item 1 updated│ │  │ │ Completeness:│ │             │
│  │ │ Item 2 created│ │  │ │ 85%          │ │             │
│  │ │ Link 1 created│ │  │ │ Consistency: │ │             │
│  │ └──────────────┘ │  │ │ 92%          │ │             │
│  └──────────────────┘  └──────────────────┘             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## WIREFRAME 2: ITEMS VIEW

```
┌─────────────────────────────────────────────────────────┐
│ TraceRTM                                    [User] [Menu]│
├─────────────────────────────────────────────────────────┤
│ Items                                                    │
├─────────────────────────────────────────────────────────┤
│ [New Item] [Filter ▼] [Search ___________]              │
├─────────────────────────────────────────────────────────┤
│ Title          │ Type           │ Status    │ Updated    │
├────────────────┼────────────────┼───────────┼────────────┤
│ Item 1         │ REQUIREMENT    │ DRAFT     │ 2h ago     │
│ Item 2         │ DESIGN         │ ACTIVE    │ 1h ago     │
│ Item 3         │ IMPLEMENTATION │ DRAFT     │ 30m ago    │
│ Item 4         │ TEST           │ DRAFT     │ 1d ago     │
│ Item 5         │ DEPLOYMENT     │ ARCHIVED  │ 1w ago     │
├────────────────┼────────────────┼───────────┼────────────┤
│ [< 1 2 3 >]                                              │
└─────────────────────────────────────────────────────────┘
```

---

## WIREFRAME 3: GRAPH VIEW

```
┌─────────────────────────────────────────────────────────┐
│ TraceRTM                                    [User] [Menu]│
├─────────────────────────────────────────────────────────┤
│ Graph                                                    │
├─────────────────────────────────────────────────────────┤
│ [Filter ▼] [Search ___________] [Zoom +] [Zoom -]       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│                    ┌─────────┐                           │
│                    │ Item 1  │                           │
│                    └────┬────┘                           │
│                         │ DEPENDS_ON                     │
│                    ┌────▼────┐                           │
│                    │ Item 2  │                           │
│                    └────┬────┘                           │
│                         │ DEPENDS_ON                     │
│                    ┌────▼────┐                           │
│                    │ Item 3  │                           │
│                    └─────────┘                           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## WIREFRAME 4: NODE EDITOR VIEW

```
┌─────────────────────────────────────────────────────────┐
│ TraceRTM                                    [User] [Menu]│
├─────────────────────────────────────────────────────────┤
│ Node Editor                                              │
├─────────────────────────────────────────────────────────┤
│ [New Node ▼] [Undo] [Redo] [Save] [Auto-Save: ON]       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐       │
│  │ Input    │─────▶│ Process  │─────▶│ Output   │       │
│  └──────────┘      └──────────┘      └──────────┘       │
│                                                          │
│                    ┌──────────┐                          │
│                    │ Decision │                          │
│                    └────┬─────┘                          │
│                         │                                │
│                    ┌────▼─────┐                          │
│                    │ Process 2 │                          │
│                    └──────────┘                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## WIREFRAME 5: CODE EDITOR VIEW

```
┌─────────────────────────────────────────────────────────┐
│ TraceRTM                                    [User] [Menu]│
├─────────────────────────────────────────────────────────┤
│ Code Editor                                              │
├─────────────────────────────────────────────────────────┤
│ [Format] [Run] [Preview] [Save]                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 1  function hello() {                                    │
│ 2    console.log("Hello, World!");                       │
│ 3  }                                                     │
│ 4                                                        │
│ 5  hello();                                              │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ Console Output:                                          │
│ Hello, World!                                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## WIREFRAME 6: KANBAN VIEW

```
┌─────────────────────────────────────────────────────────┐
│ TraceRTM                                    [User] [Menu]│
├─────────────────────────────────────────────────────────┤
│ Kanban                                                   │
├─────────────────────────────────────────────────────────┤
│ [Filter ▼] [Search ___________]                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ DRAFT          │ ACTIVE         │ ARCHIVED               │
│ ┌────────────┐ │ ┌────────────┐ │ ┌────────────┐        │
│ │ Item 1     │ │ │ Item 2     │ │ │ Item 5     │        │
│ └────────────┘ │ └────────────┘ │ └────────────┘        │
│ ┌────────────┐ │ ┌────────────┐ │                       │
│ │ Item 3     │ │ │ Item 4     │ │                       │
│ └────────────┘ │ └────────────┘ │                       │
│ ┌────────────┐ │                │                       │
│ │ Item 6     │ │                │                       │
│ └────────────┘ │                │                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```


