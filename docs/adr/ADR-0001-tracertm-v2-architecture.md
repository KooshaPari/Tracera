# ADR-0001: TraceRTM v2 - Advanced Requirements & Specification-Driven Architecture

**Status:** Proposed
**Date:** 2026-01-28
**Deciders:** Development Team

---

## Context and Problem Statement

TraceRTM currently operates as a CRUD-based traceability system with simple list/detail views. While functional, it lacks:

1. **Formal Specifications**: No executable contracts or invariants
2. **ADR Integration**: No structured decision documentation
3. **BDD/TDD Patterns**: Limited Given-When-Then scenario support
4. **Smart Contracts**: No formal requirement verification
5. **Advanced CLI**: Basic commands, not MCP-native
6. **Visual-First UI**: Simple data tables vs rich interactive graphs

To position TraceRTM as an industry-leading tool, we need to transform it into a **Specification-Driven Development (SDD)** system with **BDD+TDD integration** and **MCP-native CLI**.

---

## Decision Drivers

1. Modern teams expect executable specifications
2. ADRs are becoming standard practice
3. FastMCP 2.14+ provides production-ready MCP infrastructure
4. Visual traceability graphs outperform tabular RTMs
5. AI assistants require structured tool interfaces

---

## Considered Options

### Option 1: Incremental Enhancement (NOT chosen)
- Add features to existing architecture
- **Cons**: Technical debt accumulates, no clean break

### Option 2: Full Rewrite (NOT chosen)
- Rebuild from scratch
- **Cons**: Loses existing work, too risky

### Option 3: Layered Transformation (CHOSEN)
- Add new layers on top of existing models
- Migrate views progressively
- Introduce MCP server alongside existing API
- **Pros**: Preserves existing functionality while enabling new patterns

---

## Decision Outcome

Chosen option: **Layered Transformation**

We will add the following layers to TraceRTM:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER 1: SPECIFICATION ENGINE                     │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
│  │ ADR Management  │  │ Formal Contracts │  │ Invariant Engine   │  │
│  │ MADR Format     │  │ Pre/Post Conds   │  │ Constraint Checker │  │
│  └─────────────────┘  └──────────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER 2: BDD SCENARIO ENGINE                      │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
│  │ Gherkin Parser  │  │ Scenario Store   │  │ Step Definition    │  │
│  │ Given-When-Then │  │ Feature Files    │  │ Registry           │  │
│  └─────────────────┘  └──────────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER 3: VISUAL UI ENGINE                         │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
│  │ Graph Canvas    │  │ RTM Heat Maps    │  │ Coverage Dashboard │  │
│  │ Force-Directed  │  │ Interactive      │  │ Impact Analysis    │  │
│  └─────────────────┘  └──────────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER 4: MCP NATIVE CLI                           │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
│  │ FastMCP 2.14+   │  │ Rich Tools       │  │ AI Conversation    │  │
│  │ MCP Server      │  │ Resources        │  │ Context Provider   │  │
│  └─────────────────┘  └──────────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│               EXISTING: TraceRTM Core (Models, Services, API)        │
│  Items │ Links │ Graphs │ TestCases │ Projects │ Events │ ...       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Architecture

### Layer 1: Specification Engine

#### ADR Management
- **MADR Format**: Standardized ADR templates
- **Linking**: ADRs ↔ Requirements ↔ Code ↔ Tests
- **Compliance Scoring**: Automated ADR-to-code verification

```python
# New Model: ArchitectureDecisionRecord
class ADR(Base, TimestampMixin):
    id: Mapped[str]
    project_id: Mapped[str]
    adr_number: Mapped[str]  # ADR-0001, ADR-0002...
    title: Mapped[str]
    status: Mapped[ADRStatus]  # proposed, accepted, deprecated, superseded
    context: Mapped[str]  # Problem statement
    decision: Mapped[str]  # What we decided
    consequences: Mapped[str]  # Good/bad outcomes

    # Traceability Links
    related_requirements: Mapped[list[str]]  # [REQ-001, REQ-002]
    related_adrs: Mapped[list[str]]  # [ADR-002, ADR-003]
    superseded_by: Mapped[str | None]  # ADR-0010

    # Verification
    compliance_score: Mapped[float]  # 0.0 - 10.0
    last_verified_at: Mapped[datetime | None]
```

#### Formal Contracts
```python
# New Model: Contract
class Contract(Base, TimestampMixin):
    id: Mapped[str]
    item_id: Mapped[str]  # Linked to requirement/feature
    contract_type: Mapped[ContractType]  # api, function, invariant

    # Contract Definition
    preconditions: Mapped[list[dict]]  # [{condition, description}]
    postconditions: Mapped[list[dict]]
    invariants: Mapped[list[dict]]

    # State Machine (optional)
    states: Mapped[list[str]]
    transitions: Mapped[list[dict]]  # [{from, to, trigger, guards}]

    # Verification
    executable_spec: Mapped[str]  # Python/TypeScript code
    last_verified_at: Mapped[datetime | None]
    verification_result: Mapped[dict]
```

### Layer 2: BDD Scenario Engine

#### Gherkin Parser
```python
# New Model: Scenario
class Scenario(Base, TimestampMixin):
    id: Mapped[str]
    feature_id: Mapped[str]
    title: Mapped[str]
    gherkin_text: Mapped[str]  # Full Gherkin scenario

    # Parsed Structure
    given_steps: Mapped[list[dict]]  # [{text, data_table, doc_string}]
    when_steps: Mapped[list[dict]]
    then_steps: Mapped[list[dict]]

    # Traceability
    requirement_ids: Mapped[list[str]]  # Linked requirements
    test_case_ids: Mapped[list[str]]  # Generated/linked test cases

    # Execution
    last_run_at: Mapped[datetime | None]
    last_run_result: Mapped[str]  # pass, fail, pending
    execution_count: Mapped[int]
    pass_rate: Mapped[float]

# New Model: Feature (groups Scenarios)
class Feature(Base, TimestampMixin):
    id: Mapped[str]
    project_id: Mapped[str]
    name: Mapped[str]
    description: Mapped[str]
    file_path: Mapped[str | None]  # features/auth.feature
    tags: Mapped[list[str]]
```

#### Step Definition Registry
```python
# New Model: StepDefinition
class StepDefinition(Base, TimestampMixin):
    id: Mapped[str]
    project_id: Mapped[str]
    step_type: Mapped[str]  # given, when, then
    pattern: Mapped[str]  # "a user {name} exists"
    implementation_path: Mapped[str]  # path to step definition file
    parameters: Mapped[list[dict]]  # [{name, type, description}]
    documentation: Mapped[str]
```

### Layer 3: Visual UI Engine

#### Graph Canvas Components
```typescript
// React Components for Visual Traceability
interface TraceabilityGraphProps {
  projectId: string;
  graphType: 'dependency' | 'coverage' | 'impact' | 'adr';
  selectedNodes?: string[];
  onNodeClick: (node: GraphNode) => void;
  onLinkClick: (link: GraphLink) => void;
  layout: 'force' | 'dagre' | 'elk' | 'hierarchical';
}

// Coverage Heat Map
interface CoverageHeatMapProps {
  requirements: Requirement[];
  testCases: TestCase[];
  matrix: CoverageMatrix;
  colorScale: 'red-green' | 'spectral' | 'viridis';
}

// Impact Analysis View
interface ImpactAnalysisProps {
  sourceItem: Item;
  impactDepth: number;
  showADRs: boolean;
  showTests: boolean;
  showCode: boolean;
}
```

#### New Views
1. **Specification View**: Contract definitions with state machine diagrams
2. **Scenario View**: Gherkin features with execution status
3. **ADR Timeline**: Chronological decision history
4. **Compliance Dashboard**: ADR coverage and verification status
5. **Coverage Matrix**: Interactive RTM with drill-down

### Layer 4: MCP Native CLI

#### FastMCP 2.14+ Server
```python
# src/tracertm/mcp/server.py
from fastmcp import FastMCP

mcp = FastMCP("TraceRTM", version="2.0.0")

# =============================================================================
# TOOLS: Actions the AI can perform
# =============================================================================

@mcp.tool
def create_requirement(
    title: str,
    description: str,
    priority: str = "medium",
    parent_id: str | None = None,
) -> dict:
    """Create a new requirement with traceability metadata."""
    ...

@mcp.tool
def create_adr(
    title: str,
    context: str,
    decision: str,
    consequences: str,
    related_requirements: list[str] = [],
) -> dict:
    """Create an Architecture Decision Record following MADR format."""
    ...

@mcp.tool
def create_scenario(
    feature: str,
    title: str,
    given: list[str],
    when: list[str],
    then: list[str],
    requirement_ids: list[str] = [],
) -> dict:
    """Create a BDD scenario in Gherkin format."""
    ...

@mcp.tool
def analyze_impact(
    item_id: str,
    depth: int = 3,
    include_adrs: bool = True,
    include_tests: bool = True,
) -> dict:
    """Analyze the impact of changing an item across the traceability graph."""
    ...

@mcp.tool
def verify_contract(
    contract_id: str,
) -> dict:
    """Execute contract verification and return compliance results."""
    ...

@mcp.tool
def calculate_coverage(
    project_id: str,
    requirement_filter: str | None = None,
) -> dict:
    """Calculate test coverage percentage for requirements."""
    ...

@mcp.tool
def check_adr_compliance(
    adr_id: str,
) -> dict:
    """Check if implementation matches ADR decision."""
    ...

# =============================================================================
# RESOURCES: Data the AI can access
# =============================================================================

@mcp.resource("tracertm://projects/{project_id}/requirements")
def get_requirements(project_id: str) -> str:
    """Get all requirements for a project."""
    ...

@mcp.resource("tracertm://projects/{project_id}/adrs")
def get_adrs(project_id: str) -> str:
    """Get all ADRs for a project."""
    ...

@mcp.resource("tracertm://projects/{project_id}/coverage")
def get_coverage_report(project_id: str) -> str:
    """Get coverage report for a project."""
    ...

@mcp.resource("tracertm://projects/{project_id}/graph/{graph_type}")
def get_graph(project_id: str, graph_type: str) -> str:
    """Get traceability graph in JSON format."""
    ...

# =============================================================================
# PROMPTS: Reusable prompt templates
# =============================================================================

@mcp.prompt
def create_adr_prompt(context: str) -> str:
    """Prompt template for creating an ADR from context."""
    return f"""
    Create an Architecture Decision Record (ADR) based on the following context:

    {context}

    Use the MADR format:
    1. Title
    2. Status (Proposed)
    3. Context and Problem Statement
    4. Considered Options (at least 3)
    5. Decision Outcome (with rationale)
    6. Consequences (Good and Bad)
    """

@mcp.prompt
def coverage_analysis_prompt(project_id: str) -> str:
    """Prompt for analyzing test coverage gaps."""
    ...
```

---

## Database Schema Changes

### New Tables

```sql
-- ADR Management
CREATE TABLE adrs (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) REFERENCES projects(id),
    adr_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'proposed',
    context TEXT NOT NULL,
    decision TEXT NOT NULL,
    consequences TEXT NOT NULL,
    related_requirements JSONB DEFAULT '[]',
    related_adrs JSONB DEFAULT '[]',
    superseded_by VARCHAR(255),
    compliance_score FLOAT DEFAULT 0.0,
    last_verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Contracts
CREATE TABLE contracts (
    id VARCHAR(255) PRIMARY KEY,
    item_id VARCHAR(255) REFERENCES items(id),
    contract_type VARCHAR(50) NOT NULL,
    preconditions JSONB DEFAULT '[]',
    postconditions JSONB DEFAULT '[]',
    invariants JSONB DEFAULT '[]',
    states JSONB DEFAULT '[]',
    transitions JSONB DEFAULT '[]',
    executable_spec TEXT,
    last_verified_at TIMESTAMP WITH TIME ZONE,
    verification_result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- BDD Features
CREATE TABLE features (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) REFERENCES projects(id),
    name VARCHAR(500) NOT NULL,
    description TEXT,
    file_path VARCHAR(500),
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- BDD Scenarios
CREATE TABLE scenarios (
    id VARCHAR(255) PRIMARY KEY,
    feature_id VARCHAR(255) REFERENCES features(id),
    title VARCHAR(500) NOT NULL,
    gherkin_text TEXT NOT NULL,
    given_steps JSONB DEFAULT '[]',
    when_steps JSONB DEFAULT '[]',
    then_steps JSONB DEFAULT '[]',
    requirement_ids JSONB DEFAULT '[]',
    test_case_ids JSONB DEFAULT '[]',
    last_run_at TIMESTAMP WITH TIME ZONE,
    last_run_result VARCHAR(50),
    execution_count INT DEFAULT 0,
    pass_rate FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step Definitions
CREATE TABLE step_definitions (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) REFERENCES projects(id),
    step_type VARCHAR(20) NOT NULL,
    pattern VARCHAR(500) NOT NULL,
    implementation_path VARCHAR(500),
    parameters JSONB DEFAULT '[]',
    documentation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## Frontend Architecture Changes

### New React Components

```
frontend/apps/web/src/
├── components/
│   ├── specifications/
│   │   ├── ContractEditor.tsx       # Visual contract builder
│   │   ├── ContractViewer.tsx       # Contract display with validation
│   │   ├── StateMachineEditor.tsx   # Visual state machine designer
│   │   └── InvariantChecker.tsx     # Real-time invariant validation
│   │
│   ├── bdd/
│   │   ├── GherkinEditor.tsx        # Monaco-based Gherkin editor
│   │   ├── ScenarioBuilder.tsx      # Visual scenario builder
│   │   ├── FeatureTree.tsx          # Feature/scenario hierarchy
│   │   ├── StepLibrary.tsx          # Reusable step definitions
│   │   └── ScenarioRunner.tsx       # Execute and view results
│   │
│   ├── adr/
│   │   ├── ADREditor.tsx            # MADR template editor
│   │   ├── ADRTimeline.tsx          # Chronological ADR view
│   │   ├── ADRGraph.tsx             # ADR dependency graph
│   │   ├── ComplianceScorer.tsx     # ADR compliance dashboard
│   │   └── DecisionLog.tsx          # Executive summary view
│   │
│   └── visualization/
│       ├── TraceabilityGraph.tsx    # Main graph canvas (xyflow)
│       ├── CoverageHeatMap.tsx      # Interactive coverage matrix
│       ├── ImpactAnalysis.tsx       # What-if analysis view
│       ├── DependencyTree.tsx       # Hierarchical dependency view
│       └── MetricsDashboard.tsx     # Coverage/quality metrics
│
├── views/
│   ├── SpecificationView.tsx        # Combined spec view
│   ├── ScenarioView.tsx             # BDD feature management
│   ├── ADRView.tsx                  # ADR management
│   ├── ComplianceView.tsx           # Compliance dashboard
│   └── CoverageMatrixView.tsx       # Interactive RTM
│
└── hooks/
    ├── useSpecifications.ts
    ├── useScenarios.ts
    ├── useADRs.ts
    └── useCoverage.ts
```

### Visual Design Principles

1. **Graph-First**: Default to graph visualizations over tables
2. **Progressive Disclosure**: Details on hover/click, not upfront
3. **Real-Time Validation**: Contracts verified as you type
4. **Coverage Overlay**: Show coverage status on all views
5. **ADR Context**: Link to ADRs from anywhere

---

## CLI Architecture (FastMCP 2.14+)

### Directory Structure
```
src/tracertm/mcp/
├── __init__.py
├── server.py              # Main FastMCP server
├── tools/
│   ├── __init__.py
│   ├── requirements.py    # Requirement CRUD tools
│   ├── adrs.py            # ADR management tools
│   ├── scenarios.py       # BDD scenario tools
│   ├── contracts.py       # Contract verification tools
│   ├── coverage.py        # Coverage analysis tools
│   └── impact.py          # Impact analysis tools
├── resources/
│   ├── __init__.py
│   ├── projects.py        # Project resources
│   ├── graphs.py          # Graph resources
│   └── reports.py         # Report resources
└── prompts/
    ├── __init__.py
    ├── adr_prompts.py     # ADR-related prompts
    ├── bdd_prompts.py     # BDD scenario prompts
    └── analysis_prompts.py # Analysis prompts
```

### CLI Commands
```bash
# Start MCP server
fastmcp run src/tracertm/mcp/server.py --transport http --port 9000

# Or via CLI wrapper
tracertm mcp serve --port 9000

# Development mode with hot reload
fastmcp run src/tracertm/mcp/server.py --reload

# With specific Python version and dependencies
fastmcp run src/tracertm/mcp/server.py --python 3.12 --with anthropic
```

---

## Implementation Phases

### Phase 1: Foundation (2-3 weeks)
- [ ] Add ADR, Contract, Feature, Scenario models
- [ ] Create Alembic migrations
- [ ] Implement basic CRUD services
- [ ] Add FastMCP server skeleton

### Phase 2: Specification Engine (2-3 weeks)
- [ ] MADR template parser
- [ ] Contract definition schema
- [ ] Invariant checker engine
- [ ] ADR compliance scorer

### Phase 3: BDD Engine (2-3 weeks)
- [ ] Gherkin parser integration
- [ ] Step definition registry
- [ ] Scenario execution engine
- [ ] Coverage calculation

### Phase 4: Visual UI (3-4 weeks)
- [ ] TraceabilityGraph component
- [ ] CoverageHeatMap component
- [ ] ADR management views
- [ ] BDD scenario views

### Phase 5: MCP Integration (2-3 weeks)
- [ ] Full tool implementation
- [ ] Resource providers
- [ ] Prompt templates
- [ ] AI chat integration

### Phase 6: Polish (1-2 weeks)
- [ ] Performance optimization
- [ ] Documentation
- [ ] Testing
- [ ] Migration guides

---

## Consequences

### Good
- Industry-leading specification-driven traceability
- AI-native CLI via MCP
- Visual-first UI differentiates from competitors
- ADR integration provides decision documentation
- BDD scenarios create living documentation

### Bad
- Significant development effort
- Learning curve for specification patterns
- Migration complexity for existing users
- Performance considerations for large graphs

### Mitigations
- Phased rollout with feature flags
- Comprehensive documentation
- Migration tools and guides
- Graph rendering optimization

---

## Related ADRs
- ADR-0002: FastMCP 2.14 Integration
- ADR-0003: Gherkin Parser Selection
- ADR-0004: Graph Visualization Library

## Related Requirements
- REQ-SPEC-001: Executable Specifications
- REQ-ADR-001: ADR Management
- REQ-BDD-001: BDD Scenario Support
- REQ-VIS-001: Visual Traceability

---

## References

- [FastMCP 2.14+ Documentation](https://gofastmcp.com)
- [MADR Format](https://adr.github.io/madr/)
- [Gherkin Reference](https://cucumber.io/docs/gherkin/)
- [Spec-Driven Development](https://github.com/github/spec-kit)
