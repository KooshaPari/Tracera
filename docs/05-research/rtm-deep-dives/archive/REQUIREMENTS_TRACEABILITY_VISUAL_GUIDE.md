# Requirements Traceability System - Visual Reference Guide

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interfaces                         │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │   CLI        │   TUI        │   MCP        │   IDE Plugin │  │
│  │  (Typer)     │  (Textual)   │  (Protocol)  │  (VSCode)    │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                              │
│  ┌──────────────┬──────────────┬──────────────┐                │
│  │ Requirement  │   Linking    │  Versioning  │                │
│  │   Service    │   Service    │   Service    │                │
│  └──────────────┴──────────────┴──────────────┘                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Core Layer                                 │
│  ┌──────────────┬──────────────┬──────────────┐                │
│  │  Pydantic    │   Graph      │  Validators  │                │
│  │   Models     │   Engine     │              │                │
│  └──────────────┴──────────────┴──────────────┘                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Storage Layer                                │
│  ┌──────────────┬──────────────┬──────────────┐                │
│  │   SQLite     │   Neo4j      │   File-based │                │
│  │   Adapter    │   Adapter    │   Adapter    │                │
│  └──────────────┴──────────────┴──────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

## Requirement Hierarchy

```
Epic (Business Objective)
├── Feature (Deliverable Capability)
│   ├── User Story (User-facing Requirement)
│   │   ├── Task (Implementation Unit)
│   │   ├── Test Case (Validation)
│   │   └── Code Artifact (Implementation)
│   └── Technical Spec (Implementation Spec)
│       ├── Database Schema
│       ├── API Contract
│       └── Service Spec
└── Non-Functional Requirement
    ├── Performance Spec
    ├── Security Spec
    └── Compliance Spec
```

## Traceability Link Types

```
Epic
  ├─ decomposes_to ──→ Feature
  │                      ├─ decomposes_to ──→ Story
  │                      │                      ├─ implements ──→ Code
  │                      │                      ├─ tests ──→ TestCase
  │                      │                      └─ validates ──→ Code
  │                      └─ references ──→ TechnicalSpec
  │
  └─ depends_on ──→ Epic (cross-epic dependency)
```

## Data Model Relationships

```
┌──────────────────┐
│  Requirement     │
├──────────────────┤
│ id (PK)          │
│ type             │
│ title            │
│ description      │
│ status           │
│ priority         │
│ owner            │
│ created_at       │
│ updated_at       │
│ version          │
└──────────────────┘
        ↑
        │ 1:N
        │
┌──────────────────┐         ┌──────────────────┐
│  Link            │         │  Version         │
├──────────────────┤         ├──────────────────┤
│ id (PK)          │         │ id (PK)          │
│ source_id (FK)   │         │ requirement_id   │
│ target_id (FK)   │         │ version_num      │
│ link_type        │         │ valid_from       │
│ created_at       │         │ valid_to         │
└──────────────────┘         │ data_snapshot    │
                             └──────────────────┘
```

## CLI Command Flow

```
User Input
    ↓
Typer Parser
    ↓
Command Handler
    ↓
Service Layer
    ↓
Storage Adapter
    ↓
SQLite Database
    ↓
Result Formatting (Rich)
    ↓
Terminal Output
```

## Graph Query Patterns

### Pattern 1: Transitive Closure (Find All Descendants)
```
Epic-1
  ├─ Feature-1
  │   ├─ Story-1
  │   │   ├─ Task-1
  │   │   └─ Test-1
  │   └─ Story-2
  └─ Feature-2
      └─ Story-3
```

### Pattern 2: Impact Analysis (Find All Dependents)
```
Change to Story-1
    ↓
Find all links where Story-1 is source
    ↓
Find all dependent requirements
    ↓
Identify affected tests
    ↓
Identify regression tests needed
```

### Pattern 3: Coverage Analysis (Find Gaps)
```
All Stories
    ↓
Filter: Stories without test links
    ↓
Identify untested requirements
    ↓
Generate coverage report
```

## Temporal Versioning Timeline

```
Timeline: ─────────────────────────────────────────→ Time

Requirement-1 (v1)
  valid_from: 2025-01-01
  valid_to: 2025-03-15
  ├─ Requirement-1 (v2)
  │   valid_from: 2025-03-15
  │   valid_to: 2025-06-30
  │   └─ Requirement-1 (v3)
  │       valid_from: 2025-06-30
  │       valid_to: NULL (current)
```

## Integration Points

```
┌─────────────────┐
│   Source Code   │
└────────┬────────┘
         │ Extract @req annotations
         ↓
┌─────────────────┐
│  RTM System     │
└────────┬────────┘
         │ Link to requirements
         ↓
┌─────────────────┐
│   Test Cases    │
└────────┬────────┘
         │ Run tests
         ↓
┌─────────────────┐
│  Coverage Report│
└─────────────────┘
```

## Multi-Language Support

```
Python CLI (Primary)
    ↓
Go CLI Wrapper ←─ Shared Graph DB
    ↓
Rust CLI Wrapper ←─ Shared Graph DB
    ↓
TypeScript CLI Wrapper ←─ Shared Graph DB
    ↓
Unified Query Engine
```

## MCP Integration

```
AI Agent (Claude/Copilot)
    ↓
MCP Client
    ↓
MCP Protocol
    ↓
RTM MCP Server
    ├─ create_requirement
    ├─ link_requirements
    ├─ query_graph
    ├─ get_coverage
    └─ export_rtm
    ↓
Service Layer
    ↓
Storage Layer
```

## Implementation Phases

```
Phase 1: Foundation (Weeks 1-2)
├─ SQLite Schema
├─ Pydantic Models
└─ Storage Adapter

Phase 2: Core Features (Weeks 3-4)
├─ Linking System
├─ Versioning
└─ CLI Commands

Phase 3: Integration (Weeks 5-6)
├─ Code Extraction
├─ Test Linking
└─ Export

Phase 4: Advanced (Weeks 7-8)
├─ TUI
├─ Multi-language
└─ Smart Contracts

Phase 5: Polish (Weeks 9-10)
├─ Testing
├─ Documentation
└─ Release v1.0
```

## Success Metrics Dashboard

```
┌─────────────────────────────────────────┐
│  Traceability Coverage: 95%             │
│  Test Coverage: 87%                     │
│  Query Performance: 45ms avg            │
│  Requirement Completeness: 100%         │
│  Orphaned Requirements: 0               │
│  Unlinked Code: 2%                      │
└─────────────────────────────────────────┘
```

