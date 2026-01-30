# Problem Management & Process Modeling: Best Practices Research Report

**Research Date:** January 27, 2026
**Research Analyst:** Claude Code
**Focus Areas:** Problem management patterns, process modeling, data entity design, root cause analysis, and UI/UX patterns

---

## Executive Summary

This comprehensive research synthesizes best practices from ITIL, business process management (BPM), and modern software design patterns for modeling problems and processes. Key findings include:

1. **Dual Approach Required**: Effective problem management requires both reactive (incident-driven) and proactive (trend analysis) methodologies working in tandem.

2. **Structured Entity Model**: Problem entities need core fields (status, category, priority, impact), relationships to incidents/tasks/knowledge base, and state lifecycle management with clear transitions.

3. **Root Cause Analysis Integration**: Systematic RCA frameworks (5 Whys, Fishbone, Kepner-Tregoe) should be built into the problem workflow, with clear categorization distinguishing between causes and categories.

4. **Process Visualization Critical**: Standard notation (BPMN, flowcharts, swimlanes) enables cross-team understanding; visualization clarifies roles, handoffs, and decision points.

5. **Knowledge Integration Essential**: Known Error Database (KEDB) creates the feedback loop that transforms problems into reusable organizational knowledge.

---

## 1. Problem Management Framework (ITIL Foundation)

### 1.1 Core Objective

Problem Management aims to:
- Prevent incidents from happening
- Minimize the impact of incidents that cannot be prevented
- Eliminate recurring incidents through root cause analysis

**Source:** [Problem Management - IT Process Wiki](https://wiki.en.it-processmaps.com/index.php/Problem_Management), [ITIL Problem Management Best Practices - ServiceNow Community](https://www.servicenow.com/community/itsm-articles/itil-problem-management-best-practices/ta-p/2299572)

### 1.2 Reactive vs. Proactive Problem Management

#### Reactive Approach
- **Trigger**: Existing incidents that have occurred
- **Focus**: Service Desk teams notice patterns in incident data
- **Timeline**: Initiated after service degradation
- **Benefit**: Addresses immediate, critical issues

#### Proactive Approach
- **Trigger**: Trend analysis of incident data
- **Focus**: Identifying potential issues before they impact users
- **Timeline**: Preventative, forward-looking
- **Benefit**: Reduces overall incident frequency

**Key Insight**: Organizations should implement both approaches in parallel. Reactive problem management addresses urgent needs while proactive analysis builds organizational resilience.

**Source:** [ITIL Basics: How Problem Management minimizes downtime - Xurrent Blog](https://www.xurrent.com/blog/itil-problem-management-guide-reactive-proactive)

### 1.3 Problem Management Lifecycle

The standard ITIL problem management lifecycle includes:

1. **Problem Detection** (Reactive from incidents, Proactive from trends)
2. **Problem Logging** (Create problem record with incident linkage)
3. **Investigation & Diagnosis** (Root cause analysis)
4. **Classification & Categorization** (Organize by type/impact)
5. **Trend Analysis** (Identify patterns)
6. **Solution Development** (Permanent fix or workaround)
7. **Change & Release** (Implement solution)
8. **Closure & Review** (Document lessons learned)

---

## 2. Problem Entity Data Model

### 2.1 Core Problem Attributes

A well-designed problem entity should include:

#### Primary Identifiers
- `problem_id`: Unique identifier
- `problem_title`: Brief description of the problem
- `problem_description`: Detailed explanation of the issue
- `creation_date`: When problem was first logged
- `last_modified_date`: Most recent update

#### Classification & Categorization
- `category`: Problem type (e.g., Hardware, Software, Network, Process)
- `sub_category`: More specific classification
- `impact_level`: Severity classification (Critical, High, Medium, Low)
- `urgency`: How quickly resolution is needed
- `priority`: Calculated from impact × urgency (Executive/High/Medium/Low)

#### Status & Lifecycle
- `status`: Current state in workflow (Open, In Progress, Pending Workaround, Known Error, Closed)
- `status_reason`: Why problem is in current state
- `resolution_type`: How problem was resolved (Permanent Fix, Workaround, Deferred, Closed As Designed)

#### Root Cause Analysis
- `root_cause_identified`: Boolean flag
- `root_cause_description`: The identified underlying cause
- `root_cause_category`: Classification of cause type (System/Human/Environmental)
- `rca_method_used`: Which analysis technique was applied (5 Whys, Fishbone, Kepner-Tregoe, etc.)

#### Relationships & Links
- `related_incidents[]`: Array of incident IDs that led to this problem
- `related_problems[]`: Array of linked problem IDs
- `related_changes[]`: Change records implementing the fix
- `knowledge_article_id`: Link to Known Error Database article
- `affected_ci[]`: Configuration items (systems, services) impacted

#### Assignment & Ownership
- `assigned_to`: Problem owner/resolver
- `assigned_team`: Team responsible for resolution
- `assigned_date`: When problem was assigned
- `resolution_target_date`: Expected completion date

#### Metadata
- `created_by`: User who logged the problem
- `updated_by`: User who made most recent change
- `tags[]`: Flexible categorization tags
- `custom_fields{}`: Extensible field map for domain-specific data

**Source:** [Issue Tracking System ER Diagram - Academic Projects](https://www.freeprojectz.com/entity-relationship/issue-tracking-system-er-diagram), [Incident (case) entities - Microsoft Learn](https://learn.microsoft.com/en-us/dynamics365/customerengagement/on-premises/developer/incident-case-entities)

### 2.2 Recommended Data Relationships

```
Problem Entity Relationships:

Problem ←→ Incidents (1-to-Many)
  └─ Links root cause investigation back to triggering incidents

Problem ←→ Changes (1-to-Many)
  └─ Tracks which changes implement the problem solution

Problem ←→ Known Errors (1-to-1)
  └─ When a problem is diagnosed, create known error record
  └─ Known Error becomes organizational knowledge asset

Problem ←→ Tasks/Work Items (1-to-Many)
  └─ Breaks down complex problems into actionable work
  └─ Tracks implementation effort

Problem ←→ Knowledge Articles (1-to-1)
  └─ Problem resolution documented in knowledge base
  └─ Workarounds and permanent fixes recorded

Problem ←→ Related Problems (Many-to-Many)
  └─ Indicates problems with shared root causes
  └─ Helps identify systemic issues

Problem ←→ Configuration Items (Many-to-Many)
  └─ Which systems/services are affected
  └─ Supports impact analysis
```

### 2.3 Status State Machine

Recommended problem status workflow:

```
┌─────────────────────────────────────────────────────────────┐
│                    Problem Status Lifecycle                  │
└─────────────────────────────────────────────────────────────┘

    [Open]
      │
      ├─→ [In Progress]  (RCA actively underway)
      │      │
      │      ├─→ [Pending Workaround]  (Temporary fix deployed)
      │      │      │
      │      │      └─→ [Known Error]  (Diagnosed, solution identified)
      │      │           │
      │      │           └─→ [Closed]  (Permanent fix deployed)
      │      │
      │      └─→ [Known Error]  (Diagnosis complete)
      │           │
      │           └─→ [Closed]
      │
      └─→ [Closed]  (Deferred/Cannot Reproduce/Designed Behavior)

Key Constraints:
- Problems with identified root cause → Known Error state
- Known Errors must transition through "awaiting change" before closure
- Cannot skip directly from Open to Closed (except design decisions)
- Reopening allowed if new information emerges
```

**Source:** [Jira Status Types](https://www.herocoders.com/blog/understanding-jira-issue-statuses), [Workflow state categories - Azure Boards](https://learn.microsoft.com/en-us/azure/devops/boards/work-items/workflow-and-state-categories)

---

## 3. Root Cause Analysis (RCA) Patterns

### 3.1 RCA Framework Selection

#### The 5 Whys Method
**Structure**: Sequential questioning technique
- Ask "Why?" at each level to drill down
- Typically 5 levels of questioning
- **Best for**: Simple, linear cause-and-effect relationships
- **Time**: Quick (15-30 minutes)
- **Limitation**: Oversimplifies complex problems with multiple root causes

#### Fishbone Diagram (Ishikawa Diagram)
**Structure**: Visual categorization of potential causes
- Problem displayed as "fish head"
- Major causes as "ribs", root causes as "sub-branches"
- **Kaoru Ishikawa's 6 M's**:
  1. Manpower (People)
  2. Methods (Processes)
  3. Materials (Resources)
  4. Machines (Equipment/Systems)
  5. Mother Nature (Environment)
  6. Measurement (Data/Metrics)
- **Best for**: Complex problems with multiple potential causes
- **Time**: Moderate (45-120 minutes)
- **Benefit**: Forces systematic exploration of all categories
- **Customization**: Teams should adapt M categories to their domain

#### Kepner-Tregoe (KT) Analysis
**Structure**: Disciplined, rational approach with 4 processes
1. **Situation Appraisal**: Clarify complex situations, prioritize issues
2. **Problem Analysis**: Structured root cause investigation
3. **Decision Analysis**: Rational decision-making framework
4. **Potential Problem Analysis**: Risk mitigation and contingency planning

**Distinctive Feature**: "Is/Is Not" analysis
- What IS happening? (Observations, facts)
- What IS NOT happening? (Boundaries, negations)
- Distinctions between observed problem and non-problem situations
- Hypotheses derived from distinction analysis

- **Best for**: Complex, high-stakes problems requiring documented reasoning
- **Time**: Comprehensive (2-4 hours)
- **Rigor**: High accountability, documented decision rationale

#### FMEA (Failure Mode and Effects Analysis)
**Structure**: Systematic assessment of failure modes
- Identifies failure modes and their effects
- Calculates Risk Priority Number (RPN) = Severity × Occurrence × Detection
- **Best for**: Engineering, design, systematic risk assessment

#### Pareto Analysis (80/20 Rule)
**Structure**: Prioritization of problems by impact
- Identifies vital few problems causing majority of issues
- Focuses effort on high-impact items
- **Best for**: Portfolio-level problem prioritization

**Source:** [ITIL Root Cause Analysis - Freshworks](https://www.freshworks.com/explore-it/guide-to-itil-root-cause-analysis-rca/), [Kepner Tregoe Method - Toolshero](https://www.toolshero.com/problem-solving/kepner-tregoe-method/), [Fishbone Diagram - ASQ](https://asq.org/quality-resources/fishbone)

### 3.2 Critical Distinction: Categories vs. Causes

**Key Insight**: Categories don't cause problems—causes do.

Categories are organizational labels for grouping similar things. When classifying a problem:
- Category: "Software Bug" (organizational label)
- Root Cause: "Memory leak in database connection pool causing out-of-memory exception" (actual cause)

**Implications for Data Model**:
```
Problem
├─ category: "Software" (organizational label)
├─ sub_category: "Application Error" (classification)
└─ root_cause_category: "System" (the actual causal category)
    └─ root_cause_description: "Specific technical mechanism causing problem"
```

Never confuse categorization (for organization) with causation (actual mechanism).

**Source:** [Root Cause Analysis - ServiceNow Community](https://www.servicenow.com/community/virtual-agent-forum/problem-management-and-root-cause-categorization/td-p/2854373)

### 3.3 Cause Categorization Framework

Problems can be categorized by causal origin:

#### Systematic Causes (Process/System Origin)
- Arise from established processes, policies, or system design
- Examples: Configuration issues, architectural flaws, outdated procedures
- Resolution often requires process redesign or architectural changes

#### Human Causes (People Origin)
- Originate from human error or oversight
- Examples: Misconfiguration, missed step in procedure, inadequate training
- Resolution may involve training, documentation, or procedural controls

#### Environmental Causes (External Origin)
- External factors beyond direct system control
- Examples: Third-party service outages, resource constraints, hardware failure
- Resolution may involve mitigation, redundancy, or vendor management

**Data Model Representation**:
```
problem {
  root_cause_category: enum ["Systematic", "Human", "Environmental"],
  root_cause_description: string,
  root_cause_origin: string  // System name, team name, external system
}
```

---

## 4. Problem-to-Knowledge Integration

### 4.1 Known Error Database (KEDB) Role

The Known Error Database is the organizational memory system that transforms problem investigations into reusable knowledge.

#### Problem → Known Error → Knowledge Article Lifecycle

```
1. PROBLEM INVESTIGATION
   └─ Problem logged from incident(s)
   └─ RCA conducted
   └─ Root cause identified

2. KNOWN ERROR STATE
   └─ When root cause discovered AND
   └─ Either workaround OR permanent fix identified
   └─ Problem transitions to "Known Error" status
   └─ Create Known Error record (KEDB entry)

3. KNOWLEDGE DOCUMENTATION
   └─ Document problem description
   └─ Record identified root cause
   └─ Document workaround (if applicable)
   └─ Document permanent fix (implementation method)
   └─ Create knowledge article for organization-wide access

4. REUSE & AUTOMATION
   └─ Incidents matching KEDB criteria auto-linked to problem
   └─ Service Desk can apply known workarounds immediately
   └─ Future incidents resolved faster (lower MTTR)
   └─ Organizational knowledge grows
```

#### Known Error Database Fields

A KEDB entry should contain:

```
KnownError {
  known_error_id: string,
  related_problem_id: string,  // Link back to Problem
  description: string,
  root_cause: string,

  workaround: {
    available: boolean,
    description: string,
    effectiveness_level: enum ["Permanent Fix", "Partial Workaround", "Temporary Relief"],
    steps: string[]
  },

  permanent_fix: {
    available: boolean,
    description: string,
    change_id: string,
    implementation_date: date
  },

  affected_ci: string[],  // Configuration items
  affected_users_count: integer,
  impact_description: string,

  detection_criteria: {
    symptoms: string[],
    error_messages: string[],
    log_patterns: string[]
  },

  created_date: date,
  last_updated_date: date,
  created_by: string,

  search_keywords: string[],  // For knowledge search
  related_articles: string[]   // Links to related knowledge
}
```

**Source:** [Known Error Knowledge Base - ServiceNow](https://www.servicenow.com/community/member-feedback-forum/knowledge-management-known-error-knowledge-base/td-p/3109394), [Problem Management and Knowledge Management - Global Knowledge](https://www.globalknowledge.com/ca-en/resources/resource-library/articles/problem-management-and-knowledge-management/)

### 4.2 Knowledge Integration Points

**Point 1: During RCA**
- Search knowledge base for similar problems
- Leverage past solutions and workarounds
- Avoid re-solving known problems

**Point 2: Problem Resolution**
- Document permanent fix in knowledge article
- Record workaround details for immediate team access
- Create searchable KEDB entry

**Point 3: Incident Management Integration**
- Incidents matching KEDB criteria auto-link to Known Error
- Service Desk can immediately apply known workarounds
- Reduces mean time to recovery (MTTR)

**Source:** [Knowledge Management integration with Problem Management - Micro Focus](https://docs.microfocus.com/ITSMA/2018.08/NG/SM_H/Content/knowledgemgmt/concepts/knowledge_management_integration_with_problem_management.htm)

---

## 5. Process Modeling Best Practices

### 5.1 Process Modeling Standards

#### BPMN 2.0 (Business Process Model and Notation)
- International standard for process documentation
- Provides consistent visual language across organizations
- Enables modeling of complex workflows with decision branches

#### Key Components in Every Process Model
```
Required Elements:
├─ Tasks (Activities)
│  └─ Verb-based naming: "Perform RCA", "Approve Change"
│  └─ Not vague: "Manage", "Review", "Handle"
├─ Roles (Actors)
│  └─ Who performs each task
│  └─ Define clear ownership
├─ Documents/Artifacts
│  └─ What information is created/consumed
│  └─ Decision criteria
└─ Applications/Systems
   └─ Tools used in workflow
   └─ System touchpoints
```

#### Best Practice: Process Length
- **Ideal process**: 5-20 tasks
- Rationale: Too few tasks oversimplify; too many tasks become unmaintainable
- For larger workflows: Break into sub-processes

#### Best Practice: Task Naming
- Use clear, active verbs
- Example: "Perform Root Cause Analysis" vs. "Analyze Problem"
- Avoid high-level verbs: "Manage", "Review", "Process"
- Include object: "Verb + Noun + Context"

**Source:** [BPMS Watch: Ten Tips for Effective Process Modeling - BPMInstitute.org](https://www.bpminstitute.org/resources/articles/bpms-watch-ten-tips-effective-process-modeling), [Business Process Modeling - Wikipedia](https://en.wikipedia.org/wiki/Business_process_modeling)

### 5.2 Process Visualization Techniques

#### Swimlane Diagram (Recommended for Problem Management)
**Structure**: Horizontal or vertical lanes by role/team/system

**Advantages**:
- Clarifies who does what at each step
- Makes handoffs and dependencies visible
- Identifies bottlenecks and parallel work
- Excellent for multi-team processes

**Problem Management Example**:
```
┌──────────────────────────────────────────────────────────────┐
│                    Problem Management Swimlanes              │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│ Service Desk │ Problem Mgmt  │  Engineering │  Knowledge Mgmt │
├──────────────┼──────────────┼──────────────┼─────────────────┤
│              │              │              │                 │
│  Detect      │              │              │                 │
│  Incident    │              │              │                 │
│  (Reactive)  │              │              │                 │
│     │        │              │              │                 │
│     └───────→│              │              │                 │
│              │              │              │                 │
│              │  Log Problem │              │                 │
│              │  Search KEDB │              │                 │
│              │     │        │              │                 │
│              │     └───────→│ Perform RCA  │                 │
│              │              │   & Analysis │                 │
│              │              │     │        │                 │
│              │              │     └───────→│ Document Known  │
│              │              │              │ Error           │
│              │              │              │     │           │
│              │              │  ←───────────┤─────┘           │
│              │ ←────────────┤              │                 │
│ Apply        │              │              │                 │
│ Workaround   │              │              │                 │
│              │              │              │                 │
└──────────────┴──────────────┴──────────────┴─────────────────┘
```

#### Flowchart Visualization
- **Best for**: Simple, linear processes
- **Components**: Boxes (tasks), diamonds (decisions), arrows (flow)
- **Limitation**: Doesn't show role responsibilities

#### Value Stream Map
- **Best for**: Understanding flow, identifying waste
- **Focus**: Time, resource utilization, bottlenecks
- **Useful for**: Problem management optimization

#### Journey Map
- **Best for**: Understanding user experience perspective
- **Useful for**: Problem impact on users

**Source:** [Process Mapping Guide - Lucidchart](https://www.lucidchart.com/pages/tutorial/process-mapping-guide-and-symbols), [Process Visualization - AI Multiple](https://research.aimultiple.com/process-visualization/)

### 5.3 Exception Handling in Processes

**Critical Best Practice**: Exception handling must be explicitly modeled and consistent.

```
Problem Management Exception Patterns:

1. Cannot Reproduce Problem
   └─ Decision: Close or Monitor for recurrence?
   └─ Path: Transition to "Cannot Reproduce" state

2. Problem Deferred
   └─ Decision: Workaround sufficient for now?
   └─ Path: Document decision, defer permanent fix

3. External Dependency
   └─ Decision: Vendor fix required?
   └─ Path: Track with vendor, link to change management

4. Duplicate Problem
   └─ Decision: Merge with existing problem?
   └─ Path: Link related problems, consolidate records

5. Root Cause Unknown After Extended Analysis
   └─ Decision: Escalate, defer, or close?
   └─ Path: Document uncertainty, plan continued investigation
```

Learn specific diagram patterns for each exception type and use them consistently across all processes.

**Source:** [6 Best Practices for Business Process Modelling - PRIME BPM](https://www.primebpm.com/6-best-practices-business-process-modelling)

### 5.4 BPM Reference Architecture for Software

Key architectural components for problem management systems:

```
BPM Reference Architecture Components:

┌─────────────────────────────────────────────┐
│  Portal/User Interface Layer                │
│  (Problem Dashboard, RCA Views, KEDB Search)│
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│  Workflow Engine Layer                      │
│  (State management, task routing, escalation)
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│  Business Rules Engine                      │
│  (Priority calculation, assignment rules,   │
│   notification rules, escalation criteria)  │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│  Integration Services                       │
│  (Incident system, Change Mgmt, Ticketing,  │
│   ITSM platform integration)                │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│  Data & Analytics Layer                     │
│  (Problem metrics, trend analysis, KPIs,    │
│   reporting, audit trails)                  │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│  Data Persistence Layer                     │
│  (Problems, Known Errors, audit history,    │
│   analytics data warehouse)                 │
└─────────────────────────────────────────────┘
```

**Design Goals** (per BPMInstitute standards):
- Service-oriented architecture
- Event-based triggers
- Leverage existing technology investments
- Integration with current systems (ITSM, ticketing, HR, etc.)
- No-code/low-code process modification capability

**Source:** [Developing a BPM Reference Architecture - BPMInstitute.org](https://www.bpminstitute.org/resources/articles/developing-bpm-reference-architecture)

---

## 6. Problem Tracking UI/UX Patterns

### 6.1 Dashboard Design for Problem Management

#### Layout Principles
```
Visual Hierarchy & Priority Positioning:

┌─────────────────────────────────────────────┐
│  TOP-LEFT (Most Attention)                  │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ Critical     │  │ Open Problems│        │
│  │ Open Issues  │  │ by Priority  │        │
│  └──────────────┘  └──────────────┘        │
├─────────────────────────────────────────────┤
│  MIDDLE (Secondary Information)             │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ RCA Status   │  │ Known Errors │        │
│  │ (% Complete) │  │ In System    │        │
│  └──────────────┘  └──────────────┘        │
├─────────────────────────────────────────────┤
│  BOTTOM (Supporting Details)                │
│  ┌──────────────────────────────┐          │
│  │ Problem Trend (30 days)      │          │
│  │ Mean Time to Resolution      │          │
│  └──────────────────────────────┘          │
└─────────────────────────────────────────────┘
```

#### Key Dashboard Metrics
```
Critical KPIs (Top-Left Priority):
├─ Total Open Problems: [Count] (with trend arrow)
├─ Critical Priority Problems: [Count] (red indicator)
├─ Overdue RCA (>SLA): [Count] (warning indicator)
├─ Average Time in Investigation: [Days]
└─ Known Errors Awaiting Permanent Fix: [Count]

Secondary Metrics (Middle):
├─ Problems by Status: (Visual breakdown)
│  └─ Open | In Progress | Awaiting Fix | Closed
├─ Problems by Priority: (Stacked bar)
│  └─ Critical | High | Medium | Low
├─ RCA Method Usage: (Pie chart)
│  └─ 5 Whys | Fishbone | Kepner-Tregoe | Other
└─ Root Cause Category Distribution:
   └─ Systematic | Human | Environmental

Trend Indicators (Bottom):
├─ Problem Volume Trend (30-day line chart)
├─ Mean Time to Resolution (MTTR) trend
├─ KEDB Article Coverage (% of problems documented)
└─ Incident Prevention Success (% resolved before escalation)
```

#### Color Coding Strategy
```
Status Indicators:
├─ RED: Critical/Urgent (Open, SLA breached, Critical priority)
├─ ORANGE: High importance (In Progress, Medium priority, Pending)
├─ YELLOW: Caution (Overdue RCA, Awaiting external dependency)
├─ GREEN: Healthy (Closed on time, Known Errors documented)
└─ GRAY: Informational (Deferred, Duplicate, Cannot Reproduce)

Legend Requirement:
  Always include visual legend on dashboard
  Consistent with organizational color conventions
```

**Source:** [Dashboard Design UX Patterns - Pencil & Paper](https://www.pencilandpaper.io/articles/ux-pattern-analysis-data-dashboards), [Effective Dashboard Design - UXPin](https://www.uxpin.com/studio/blog/dashboard-design-principles/)

### 6.2 Problem List View Patterns

#### Recommended Columns
```
Problem Tracking Table:

| Priority | ID | Title | Status | Owner | Impact | MTTR | Root Cause |
|----------|----|----|--------|-------|--------|------|-----------|
| [Red]    |P001|DB Pool|In Prog |Team A | High  | 4h  | Code leak |
|          |    | Memory|       |      |        |     |           |
| [Orange] |P002|Login  |Known  | Team B| Medium| 8h  | Config    |
|          |    | Timeout|Error  |      |       |     | issue     |
```

#### Filtering & Sorting Features
```
Essential Filters:
├─ Status: [Open | In Progress | Known Error | Closed]
├─ Priority: [Critical | High | Medium | Low]
├─ Owner/Team: [Dropdown with team list]
├─ Impact Level: [Critical | High | Medium | Low]
├─ Category: [Software | Hardware | Network | Process]
├─ Root Cause Found: [Yes | No | Unknown]
├─ Date Range: [Custom date picker]
└─ My Problems: [Yes | No]

Sorting Options:
├─ Priority (High → Low)
├─ Created Date (Newest first)
├─ Last Modified (Recently updated)
├─ Time in Progress (Oldest first - identify long-stalled)
└─ Impact (Highest impact first)

Saved Views:
├─ "Critical Open Problems"
├─ "Awaiting My RCA"
├─ "Known Errors Needing Documentation"
└─ "Recently Closed"
```

### 6.3 Problem Detail View

#### Key Sections
```
Problem Detail Page Layout:

┌─ HEADER ────────────────────────────────────┐
│ Problem ID | Title | Status Badge           │
│ Priority Badge | Impact Level Badge         │
└────────────────────────────────────────────┘

┌─ QUICK INFO BAR ────────────────────────────┐
│ Owner: [Name] | Team: [Team] | Created: [Date]│
│ Last Updated: [Date] | Time in Status: [Duration]│
└────────────────────────────────────────────┘

┌─ MAIN CONTENT (Tabs) ────────────────────────┐
│ ┌─ Summary ───┬─ Incidents ──┬─ RCA ─┬─ Timeline─┐
│ │             │              │       │          │
│ │ Description │ Related      │ Method│ Activity │
│ │ Category    │ Incidents    │ Found │ Log      │
│ │ Impact      │ Count        │ Root  │          │
│ │ Urgency     │ List         │ Cause │          │
│ └─────────────┴──────────────┴───────┴──────────┘
│
│ ┌─ Known Error / Solution ─────────────────┐
│ │ Known Error Record (if exists)           │
│ │ Workaround Steps (if available)          │
│ │ Permanent Fix Details (if available)     │
│ │ Knowledge Article Link                   │
│ └─────────────────────────────────────────┘
│
│ ┌─ Related Items ──────────────────────────┐
│ │ Related Problems | Changes | Tasks       │
│ └─────────────────────────────────────────┘
└────────────────────────────────────────────┘

┌─ RIGHT SIDEBAR ─────────────────────────────┐
│ ┌─ Assignment ──────────────┐             │
│ │ Owner: [Dropdown]         │             │
│ │ Team: [Dropdown]          │             │
│ │ Target Resolution Date    │             │
│ └──────────────────────────┘              │
│                                           │
│ ┌─ Classification ──────────┐             │
│ │ Category: [Dropdown]      │             │
│ │ Sub-Category: [Dropdown]  │             │
│ │ Tags: [Multi-select]      │             │
│ └──────────────────────────┘              │
│                                           │
│ ┌─ Status Management ───────┐             │
│ │ Current Status: [Badge]   │             │
│ │ [Change Status] [Button]  │             │
│ │ Close Problem [Button]    │             │
│ └──────────────────────────┘              │
└────────────────────────────────────────────┘
```

### 6.4 RCA Workflow UI

#### RCA Step-by-Step Interface
```
Problem RCA Interface:

┌─ RCA Method Selection ──────────────────────┐
│ ◯ 5 Whys         ◯ Fishbone              │
│ ◯ Kepner-Tregoe  ◯ FMEA                  │
│ ◯ Pareto         ◯ Other                 │
│ [Next Step]                              │
└────────────────────────────────────────────┘

IF "Fishbone" Selected:
┌─ Fishbone Diagram Builder ──────────────────┐
│ Defect/Problem: [Text Input]               │
│                                            │
│ Major Categories (Editable):               │
│ ┌─────────────────────────────────────┐   │
│ │ Manpower    Methods    Materials    │   │
│ │ [Input]     [Input]    [Input]      │   │
│ │                                     │   │
│ │ Machines    Measurement Environment│   │
│ │ [Input]     [Input]    [Input]      │   │
│ │                                     │   │
│ │ [Add Sub-causes]                    │   │
│ │ [Visual Preview]                    │   │
│ └─────────────────────────────────────┘   │
│ [Save RCA] [Export Diagram]              │
└────────────────────────────────────────────┘

IF "5 Whys" Selected:
┌─ 5 Whys Analysis ──────────────────────────┐
│ Level 1 - Why? [Input] → [Root Cause]     │
│ Level 2 - Why? [Input] → [Root Cause]     │
│ Level 3 - Why? [Input] → [Root Cause]     │
│ Level 4 - Why? [Input] → [Root Cause]     │
│ Level 5 - Why? [Input] → [Root Cause]     │
│ [Save RCA] [Generate Summary]             │
└────────────────────────────────────────────┘
```

**Source:** [Guide to task dashboards - Atlassian](https://www.atlassian.com/agile/project-management/task-management-dashboard), [Dashboard UI Design Guide - ANODA UX](https://www.anoda.mobi/ux-blog/dashboard-ui-design-guide-best-practices/)

---

## 7. Problem-Task-Feature Relationships in Product Management

### 7.1 Structural Hierarchy

```
User Problems ─→ Product Features ─→ Project Tasks

Problem (User-centric)
  ├─ "Users cannot reset forgotten passwords"
  ├─ "Mobile app crashes when syncing large files"
  └─ "Search results are slow (>2s latency)"

Feature (Solution)
  ├─ "Password Reset Flow via Email"
  ├─ "Incremental File Sync with Progress Tracking"
  └─ "Full-Text Search Index Optimization"

Tasks (Implementation)
  ├─ [Design] Email template for reset link
  ├─ [Backend] Implement token generation
  ├─ [Frontend] Build reset form UI
  ├─ [Test] Verify token expiration
  └─ [Deploy] Database schema updates
```

### 7.2 Problem Management vs. Project Management

**Problem Managers** (Product/Service focus):
- Why do users have problems?
- How can features solve those problems?
- What patterns emerge in user complaints?
- Focus: Understanding root causes and preventing recurrence

**Project Managers** (Delivery focus):
- How do we deliver solutions?
- What tasks need to be broken down from features?
- When will solutions be available?
- Focus: Coordinating resources, managing timelines, tracking progress

**Organizational Integration**: Problems inform features, features are delivered through project tasks.

**Source:** [Product manager vs. project manager - Atlassian](https://www.atlassian.com/agile/project-management/product-vs-project-management)

---

## 8. Recommended Implementation Patterns

### 8.1 Integration with Existing Systems

```
Problem Management System Integration Points:

┌─────────────────────────────────────────────┐
│        Problem Management Platform          │
└────────┬──────────────────────────┬─────────┘
         │                          │
    ┌────▼────┐              ┌─────▼────┐
    │ Incident │              │ Knowledge │
    │ Mgmt     │              │ Base      │
    │ System   │              │           │
    └────┬─────┘              └─────┬─────┘
         │                          │
    Problem Detection        Problem Resolution
    Root Cause Analysis      Known Error Database
    Impact Assessment        Workaround Distribution
         │                          │
    ┌────▼────┐              ┌─────▼────┐
    │ Change  │              │ Service   │
    │ Mgmt    │              │ Desk      │
    │         │              │           │
    └─────────┘              └───────────┘

Fix Implementation         Faster Incident Resolution
```

### 8.2 Workflow Automation Opportunities

```
Automation Rules for Problem Management:

1. Auto-Detection & Categorization
   Trigger: New problem logged
   Action: Apply ML to categorize impact/urgency
   Action: Suggest related incidents/problems

2. Escalation Rules
   Trigger: Problem in "In Progress" > 24 hours
   Action: Notify owner
   Action: Escalate to manager if no activity

3. RCA Triggering
   Trigger: Problem priority = Critical
   Action: Automatically suggest RCA method
   Action: Notify assigned team
   Action: Set target RCA completion time

4. Known Error Distribution
   Trigger: Problem transitions to Known Error
   Action: Create knowledge article draft
   Action: Notify Service Desk of workaround
   Action: Link incidents to known error

5. SLA Enforcement
   Trigger: Problem status change
   Action: Calculate time remaining in SLA
   Action: Warn if approaching breach
   Action: Alert if SLA breached

6. Closure Validation
   Trigger: User attempts to close problem
   Action: Verify RCA documented
   Action: Verify Knowledge article created
   Action: Verify all related incidents resolved
```

### 8.3 Metrics & KPIs to Track

```
Problem Management Effectiveness Metrics:

Outcome Metrics:
├─ Mean Time to Resolution (MTTR)
│  └─ Target: Reduce by 20% per quarter
├─ Problem Prevention Rate
│  └─ % of similar incidents prevented by known errors
├─ Known Error Database Coverage
│  └─ % of closed problems with documented errors
└─ First-Time Fix Rate
   └─ % of problems solved without escalation

Process Metrics:
├─ RCA Completion Rate
│  └─ % of problems with root cause identified
├─ Time to RCA Completion
│  └─ Days from detection to root cause found
├─ Workaround Availability
│  └─ % of known errors with workarounds
└─ Re-open Rate
   └─ % of closed problems that re-open

Quality Metrics:
├─ RCA Quality Score
│  └─ Based on completeness of documentation
├─ Knowledge Article Usefulness
│  └─ Self-service resolution rate
└─ False Positives
   └─ Problems that didn't actually have identified root cause
```

---

## 9. Concrete Field Recommendations Summary

### 9.1 Minimal Viable Problem Entity (MVP)

```
problem {
  // Core Identification
  id: UUID,
  title: string (max 200 chars),
  description: string (unbounded),

  // Status Tracking
  status: enum ["Open", "In Progress", "Known Error", "Closed"],
  status_updated_at: timestamp,
  status_updated_by: UserRef,

  // Classification
  category: enum ["Software", "Hardware", "Network", "Process"],
  impact_level: enum ["Critical", "High", "Medium", "Low"],
  priority: enum ["Critical", "High", "Medium", "Low"],

  // Assignment
  assigned_to: UserRef,
  assigned_team: TeamRef,

  // RCA
  root_cause_identified: boolean,
  root_cause_description: string,
  rca_method_used: enum ["5 Whys", "Fishbone", "Kepner-Tregoe", "FMEA", "Other"],

  // Relationships
  incident_ids: UUID[],
  knowledge_article_id: UUID (nullable),

  // Metadata
  created_at: timestamp,
  created_by: UserRef,
  updated_at: timestamp,
  updated_by: UserRef
}
```

### 9.2 Extended Problem Entity (Full Feature)

```
problem {
  // Core Identification
  id: UUID,
  problem_number: string (human-readable sequential),
  title: string (max 200 chars),
  description: string (unbounded),

  // Lifecycle Status
  status: enum [
    "Open",
    "In Investigation",
    "Pending Workaround",
    "Known Error",
    "Awaiting Fix",
    "Closed"
  ],
  status_history: {
    timestamp: timestamp,
    from_status: string,
    to_status: string,
    changed_by: UserRef,
    reason: string
  }[],
  resolution_type: enum [
    "Permanent Fix",
    "Workaround Only",
    "Cannot Reproduce",
    "Deferred",
    "By Design"
  ],

  // Classification & Categorization
  category: enum [
    "Software Bug",
    "Configuration",
    "Performance",
    "Hardware Failure",
    "Network",
    "Process",
    "Documentation",
    "Other"
  ],
  sub_category: string,
  tags: string[],

  // Impact Assessment
  impact_level: enum ["Critical", "High", "Medium", "Low"],
  affected_systems: string[],
  affected_users_estimated: integer,
  business_impact_description: string,

  // Urgency & Priority
  urgency: enum ["Immediate", "High", "Medium", "Low"],
  priority: enum ["Critical", "High", "Medium", "Low"],
  priority_justification: string,
  target_resolution_date: date,

  // Root Cause Analysis
  rca_performed: boolean,
  rca_method_used: enum [
    "5 Whys",
    "Fishbone Diagram",
    "Kepner-Tregoe",
    "FMEA",
    "Pareto Analysis",
    "Other"
  ],
  rca_notes: string,

  root_cause_identified: boolean,
  root_cause_description: string,
  root_cause_category: enum ["Systematic", "Human", "Environmental"],
  root_cause_confidence: enum ["High", "Medium", "Low"],
  rca_completed_date: date (nullable),
  rca_completed_by: UserRef,

  // Solutions & Workarounds
  workaround_available: boolean,
  workaround_description: string,
  workaround_effectiveness: enum [
    "Permanent Fix",
    "Partial Workaround",
    "Temporary Relief"
  ],

  permanent_fix_available: boolean,
  permanent_fix_description: string,
  permanent_fix_implementation_date: date (nullable),
  permanent_fix_change_id: UUID (nullable),

  // Known Error Integration
  known_error_id: UUID (nullable),
  knowledge_article_id: UUID (nullable),
  knowledge_article_title: string,
  knowledge_article_created_date: date (nullable),

  // Relationships
  related_incident_ids: UUID[],
  related_problem_ids: UUID[],
  related_change_ids: UUID[],
  related_task_ids: UUID[],
  related_configuration_items: {
    ci_id: UUID,
    ci_name: string,
    impact_type: enum ["Direct", "Indirect"]
  }[],

  // Assignment & Ownership
  assigned_to: UserRef,
  assigned_team: TeamRef,
  assigned_date: timestamp,

  // Stakeholders
  created_by: UserRef,
  created_from_incident_id: UUID (nullable),
  created_date: timestamp,

  updated_by: UserRef,
  updated_date: timestamp,

  closed_by: UserRef (nullable),
  closed_date: timestamp (nullable),

  // Timeline & SLA
  days_in_investigation: integer,
  days_in_status: integer,
  sla_target_hours: integer,
  sla_remaining_hours: integer (calculated),
  sla_breached: boolean,

  // Quality & Audit
  review_notes: string (nullable),
  reviewed_by: UserRef (nullable),
  review_date: timestamp (nullable),

  custom_fields: {
    [key: string]: unknown
  }
}
```

---

## 10. Implementation Recommendations

### 10.1 Phase 1: MVP (Months 1-2)
- Core problem entity with basic status workflow
- Incident linkage
- Basic RCA documentation fields
- Simple dashboard with critical metrics
- Status state machine enforcement

### 10.2 Phase 2: RCA Enhancement (Months 2-3)
- Integrated RCA method tools (5 Whys, Fishbone)
- Root cause categorization
- Known Error entity creation
- RCA workflow integration

### 10.3 Phase 3: Knowledge Integration (Months 3-4)
- Knowledge Base integration
- Auto-linking of incidents to known errors
- Workaround distribution to Service Desk
- KEDB search functionality

### 10.4 Phase 4: Advanced Analytics (Months 4-5)
- Problem trend analysis
- Trend-based proactive problem detection
- Dashboard analytics
- SLA management
- Escalation automation

### 10.5 Phase 5: Process Automation (Months 5-6)
- Workflow automation rules
- Auto-categorization via ML
- Escalation rules
- Integration with Change Management
- Integration with Incident Management

---

## 11. Key Takeaways & Design Decisions

1. **Dual Status Models**:
   - `status` field (workflow state): Open → In Progress → Known Error → Closed
   - `resolution_type` field (how resolved): Permanent Fix, Workaround, Cannot Reproduce, etc.

2. **RCA as First-Class Citizen**:
   - Store RCA method, findings, and confidence level
   - Link to specific root cause vs. problem category
   - Create audit trail of RCA evolution

3. **Known Error as Bridge**:
   - Problem record → Known Error record → Knowledge Article
   - Each transition represents progress toward organizational learning
   - Missing any step indicates incomplete problem resolution

4. **Process Clarity Through Swimlanes**:
   - Use swimlane diagrams to show multi-team problem management
   - Make handoffs explicit
   - Show parallel RCA activities

5. **Dashboard Hierarchy**:
   - Top-left: Critical problems needing immediate attention
   - Middle: Status breakdown and process health
   - Bottom: Trends and organizational metrics

6. **Flexible Categorization**:
   - Allow both standard categories and custom tags
   - Distinguish "problem category" (organizational) from "root cause category" (causal)

---

## References

### ITIL & Problem Management
- [Problem Management - IT Process Wiki](https://wiki.en.it-processmaps.com/index.php/Problem_Management)
- [Problem Management in ITIL: Process & Implementation Guide - Atlassian](https://www.atlassian.com/itsm/problem-management)
- [ITIL Problem Management Best Practices - ServiceNow Community](https://www.servicenow.com/community/itsm-articles/itil-problem-management-best-practices/ta-p/2299572)
- [ITIL Basics: How Problem Management minimizes downtime - Xurrent Blog](https://www.xurrent.com/blog/itil-problem-management-guide-reactive-proactive)

### Root Cause Analysis
- [ITIL Root Cause Analysis - Freshworks](https://www.freshworks.com/explore-it/guide-to-itil-root-cause-analysis-rca/)
- [Kepner Tregoe Method - Toolshero](https://www.toolshero.com/problem-solving/kepner-tregoe-method/)
- [Fishbone Diagram - ASQ](https://asq.org/quality-resources/fishbone)
- [Root Cause Analysis - ServiceNow Community](https://www.servicenow.com/community/virtual-agent-forum/problem-management-and-root-cause-categorization/td-p/2854373)

### Process Modeling
- [BPMS Watch: Ten Tips for Effective Process Modeling - BPMInstitute.org](https://www.bpminstitute.org/resources/articles/bpms-watch-ten-tips-effective-process-modeling)
- [Process Mapping Guide - Lucidchart](https://www.lucidchart.com/pages/tutorial/process-mapping-guide-and-symbols)
- [Process Visualization - AI Multiple](https://research.aimultiple.com/process-visualization/)
- [6 Best Practices for Business Process Modelling - PRIME BPM](https://www.primebpm.com/6-best-practices-business-process-modelling)

### Data Modeling
- [Issue Tracking System ER Diagram - Academic Projects](https://www.freeprojectz.com/entity-relationship/issue-tracking-system-er-diagram)
- [Incident (case) entities - Microsoft Learn](https://learn.microsoft.com/en-us/dynamics365/customerengagement/on-premises/developer/incident-case-entities)

### Knowledge Integration
- [Known Error Knowledge Base - ServiceNow](https://www.servicenow.com/community/member-feedback-forum/knowledge-management-known-error-knowledge-base/td-p/3109394)
- [Problem Management and Knowledge Management - Global Knowledge](https://www.globalknowledge.com/ca-en/resources/resource-library/articles/problem-management-and-knowledge-management/)

### UI/UX & Dashboard Design
- [Dashboard Design UX Patterns - Pencil & Paper](https://www.pencilandpaper.io/articles/ux-pattern-analysis-data-dashboards)
- [Effective Dashboard Design - UXPin](https://www.uxpin.com/studio/blog/dashboard-design-principles/)
- [Guide to task dashboards - Atlassian](https://www.atlassian.com/agile/project-management/task-management-dashboard)

### Product & Project Management Integration
- [Product manager vs. project manager - Atlassian](https://www.atlassian.com/agile/project-management/product-vs-project-management)

---

**Document Version:** 1.0
**Last Updated:** January 27, 2026
**Status:** Research Complete
