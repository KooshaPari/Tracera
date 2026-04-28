# Wireframe Traceability Diagram

Visual representation of how wireframes integrate into the TraceRTM traceability matrix.

## Full Traceability Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REQUIREMENTS LAYER                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    EPIC-001: User Authentication System
    │
    ├─── STORY-001: Login Page
    │    ├─── implements
    │    │
    │    └─── STORY-002: Signup Page
         ├─── implements
         │
         ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│                          DESIGN LAYER (NEW)                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    WF-001: Login Screen Wireframe
    │
    ├─── wireframe_for ──────► STORY-001: Login Page
    │
    ├─── wireframe_for ──────► STORY-002: Signup Page
    │
    ├─── Figma Integration
    │    ├── figma_url: https://figma.com/file/abc123/...?node-id=1:42
    │    ├── figma_file_key: abc123
    │    └── figma_node_id: 1:42
    │
    ├─── Components:
    │    ├── Button (primary variant)
    │    ├── InputField (email, password)
    │    ├── Card (elevated)
    │    └── Logo
    │
    ├─── Screens:
    │    ├── LoginScreen
    │    └── SignupScreen
    │
    └─── implemented_in
         │
         ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│                         IMPLEMENTATION LAYER                                 │
└─────────────────────────────────────────────────────────────────────────────┘

    src/components/LoginForm.tsx
    │
    ├─── implemented_in ◄──── WF-001
    │
    └─── Uses components:
         ├── src/components/Button.tsx
         │    └─── designed_by ──────► WF-001
         │
         ├── src/components/InputField.tsx
         │    └─── designed_by ──────► WF-001
         │
         └── src/components/Card.tsx
              └─── designed_by ──────► WF-001

         ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│                           TESTING LAYER                                      │
└─────────────────────────────────────────────────────────────────────────────┘

    TEST-001: Login Form Tests
    │
    └─── tested_by ◄──────── STORY-001
```

## Link Type Relationships

### 1. wireframe_for (Wireframe → Story/Epic)

```
WF-001 ────wireframe_for────► STORY-001
       │
       └───wireframe_for────► STORY-002
```

**Purpose:** Link design artifacts to requirements they implement

**Example:**
```yaml
- source: WF-001
  target: STORY-001
  type: wireframe_for
```

### 2. implemented_in (Wireframe → Code)

```
WF-001 ────implemented_in────► src/components/LoginForm.tsx
       │
       └───implemented_in────► src/components/SignupForm.tsx
```

**Purpose:** Track which code files implement the design

**Example:**
```yaml
- source: WF-001
  target: src/components/LoginForm.tsx
  type: implemented_in
```

### 3. designed_by (Component → Wireframe)

```
src/components/Button.tsx ────designed_by────► WF-001
src/components/InputField.tsx ────designed_by────► WF-001
src/components/Card.tsx ────designed_by────► WF-001
```

**Purpose:** Track which components are based on a design

**Example:**
```yaml
- source: src/components/Button.tsx
  target: WF-001
  type: designed_by
```

## Complete Traceability Example

### Epic to Code Path

```
EPIC-001 (User Authentication)
  │
  ├─ implements
  │
  └─► STORY-001 (Login Page)
       │
       ├─ wireframe_for
       │
       └─► WF-001 (Login Wireframe)
            │
            ├─ Figma: https://figma.com/file/abc123/...
            │
            ├─ implemented_in
            │
            └─► src/components/LoginForm.tsx
                 │
                 ├─ Uses Button (designed_by WF-001)
                 │
                 ├─ Uses InputField (designed_by WF-001)
                 │
                 └─ tested_by
                    │
                    └─► TEST-001 (Login Tests)
```

### Reverse Traceability (Code to Requirements)

```
src/components/Button.tsx
  │
  ├─ designed_by
  │
  └─► WF-001 (Login Wireframe)
       │
       ├─ Figma: View design
       │
       ├─ wireframe_for
       │
       └─► STORY-001 (Login Page)
            │
            ├─ implements
            │
            └─► EPIC-001 (User Authentication)
```

## Multi-Wireframe Scenario

```
EPIC-001: User Authentication
  │
  ├─► STORY-001: Login Page
  │    └─► WF-001: Login Wireframe
  │         ├── Desktop version
  │         └── implemented_in: LoginForm.tsx
  │
  ├─► STORY-002: Mobile Login
  │    └─► WF-002: Mobile Login Wireframe
  │         ├── Mobile version
  │         └── implemented_in: MobileLoginForm.tsx
  │
  └─► STORY-003: Password Reset
       └─► WF-003: Password Reset Wireframe
            ├── Reset flow
            └── implemented_in: PasswordReset.tsx
```

## Component Reuse Tracking

```
WF-001: Login Wireframe
  │
  ├── Components:
  │    ├── Button ───────┐
  │    ├── InputField ───┤
  │    └── Card ─────────┤
  │                      │
WF-002: Dashboard        │
  │                      │
  ├── Components:        │ (Shared components)
  │    ├── Button ───────┤
  │    ├── Card ─────────┤
  │    └── Table ────────┤
  │                      │
WF-003: Settings         │
  │                      │
  └── Components:        │
       ├── Button ───────┘
       └── Form
```

### Query: "Which wireframes use Button component?"

```sql
SELECT * FROM wireframes
WHERE 'Button' IN components
```

Result:
- WF-001: Login Wireframe
- WF-002: Dashboard Wireframe
- WF-003: Settings Wireframe

## Status Flow Diagram

```
┌─────────┐   Designer creates   ┌─────────┐
│  draft  │ ──────────────────► │ review  │
└─────────┘                      └─────────┘
                                      │
                                      │ Team approves
                                      ▼
                                 ┌──────────┐
                                 │ approved │
                                 └──────────┘
                                      │
                                      │ Developer implements
                                      ▼
                                 ┌──────────────┐
                                 │ implemented  │
                                 └──────────────┘
```

### Status Workflow

1. **draft** - Designer creating wireframe
2. **review** - Team reviewing design
3. **approved** - Design approved for implementation
4. **implemented** - Code implements the design

## Figma Integration Flow

```
                    ┌─────────────────────────────────┐
                    │        Figma Cloud              │
                    │                                 │
                    │  File: abc123                   │
                    │  Node: 1:42 (Login Screen)      │
                    └─────────────────────────────────┘
                              │
                              │ Figma URL
                              ▼
                    ┌─────────────────────────────────┐
                    │   WF-001.md (Wireframe File)    │
                    │                                 │
                    │  figma_url: https://...         │
                    │  figma_file_key: abc123         │
                    │  figma_node_id: 1:42            │
                    └─────────────────────────────────┘
                              │
                              │ Auto-sync (optional)
                              ▼
                    ┌─────────────────────────────────┐
                    │    Figma API Integration        │
                    │                                 │
                    │  - Fetch latest design          │
                    │  - Extract components           │
                    │  - Export images                │
                    └─────────────────────────────────┘
```

## Directory Structure Visualization

```
.trace/
├── epics/
│   └── EPIC-001.md ────────┐
│                           │ (implements)
├── stories/                │
│   ├── STORY-001.md ◄──────┘
│   └── STORY-002.md ◄──────┐
│                           │ (wireframe_for)
├── wireframes/             │
│   ├── WF-001.md ──────────┴─► Links to STORY-001, STORY-002
│   │   ├── figma_url           Implements requirements
│   │   ├── components          Components: [Button, InputField]
│   │   └── screens             Screens: [LoginScreen, SignupScreen]
│   │
│   ├── WF-002.md ──────────┐
│   └── WF-003.md           │
│                           │ (implemented_in)
└── .meta/                  │
    └── links.yaml          │
        ├── wireframe_for   │
        ├── implemented_in ─┘
        └── designed_by

src/components/
├── LoginForm.tsx ◄─────────── implemented_in ◄── WF-001
├── Button.tsx ─────────────── designed_by ────────► WF-001
├── InputField.tsx ─────────── designed_by ────────► WF-001
└── Card.tsx ───────────────── designed_by ────────► WF-001
```

## Query Examples

### Find all wireframes for a story
```
INPUT: STORY-001
QUERY: links WHERE target = STORY-001 AND type = wireframe_for
RESULT: [WF-001]
```

### Find all code implementing a wireframe
```
INPUT: WF-001
QUERY: links WHERE source = WF-001 AND type = implemented_in
RESULT: [src/components/LoginForm.tsx]
```

### Find wireframe that designed a component
```
INPUT: src/components/Button.tsx
QUERY: links WHERE source = Button.tsx AND type = designed_by
RESULT: [WF-001]
```

### Find all wireframes using a component
```
INPUT: Button
QUERY: wireframes WHERE 'Button' IN components
RESULT: [WF-001, WF-002, WF-003]
```

## Benefits Visualization

```
Traditional Workflow:
Requirements ──────► Code
                     (Design in separate tools, no traceability)

With Wireframes:
Requirements ──► Wireframe ──► Code
     │              │              │
     │              │              │
     └──────────────┴──────────────┘
            Full Traceability
```

### Impact Analysis Example

**Question:** "If STORY-001 changes, what needs updating?"

```
STORY-001 (Changed)
  │
  ├─ Related wireframes:
  │   └─► WF-001 ──► Needs design review
  │
  └─ Related code:
      └─► LoginForm.tsx ──► Needs implementation update
          │
          └─ Related tests:
              └─► TEST-001 ──► Needs test update
```

## Summary

Wireframes create complete design-to-code traceability:

1. **Requirements → Design**: wireframe_for links
2. **Design → Code**: implemented_in links
3. **Components → Design**: designed_by links
4. **Design → Figma**: Direct URL integration

This enables:
- Impact analysis across design changes
- Component usage tracking
- Design-code consistency verification
- Complete audit trail from requirements to implementation
