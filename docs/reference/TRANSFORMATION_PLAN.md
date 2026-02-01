# TraceRTM v2 Transformation Plan

## Executive Summary

Transform TraceRTM from simple CRUD list/detail views into a **Specification-Driven Development (SDD)** system with **BDD+TDD integration**, **visual UI focus**, **MCP-native CLI**, and **Agentic PM capabilities**.

---

## Research Synthesis (January 2026)

### Key Industry Insights

Based on comprehensive research across 6 domains:

1. **Agentic PM is Mainstream**:
   - Gartner: 33% of enterprise software will include agentic AI by 2028
   - ClickUp, Notion, Linear all offer autonomous project management features
   - MetaGPT simulates entire software companies with PM→Architect→Engineer→QA agents

2. **Specification-Driven Development (SDD) is a 2025 Top Practice**:
   - ThoughtWorks identified SDD as one of the most important practices to emerge
   - Pattern: Intent → Spec → Plan → Execution
   - Tools: GitHub Spec Kit, Amazon Kiro, Cursor Plan Mode

3. **MCP is the Universal Interface**:
   - Donated to Linux Foundation (AAIF) by Anthropic, Block, OpenAI
   - MCP Apps (Jan 2026): Interactive UI components in conversations
   - 50+ enterprise MCP servers available (GitHub, Notion, Zapier, etc.)

4. **Graph Databases for Requirements are Mature**:
   - Neo4j Infinigraph: Operational + analytical with ACID compliance
   - LLM-based traceability recovery achieving 99% validation accuracy
   - Knowledge graphs with RAG providing 300-320% ROI

5. **Design Systems Are Token-First**:
   - W3C DTCG v1.0 specification (October 2025)
   - Three-tier architecture: Primitive → Semantic → Component tokens
   - shadcn/ui pattern: copy-paste code ownership

6. **SysML v2 is Production Ready**:
   - OMG formally adopted July 2025
   - Tools: SysON (open source), PTC Modeler 10.2, Enterprise Architect

---

## Current State Analysis

### What We Have (Strengths)

**Backend (Hexagonal Architecture)**
- 65+ specialized services with clear separation
- Comprehensive domain models: Items, Links, Problems, Processes, TestCases, TestSuites, TestRuns, Coverage
- Graph analysis services: impact analysis, cycle detection, shortest path, critical path
- External integrations: GitHub, Linear, webhooks, CI/CD
- Async FastAPI with SQLAlchemy 2.0

**Frontend (React + TanStack)**
- 27 views with data-driven patterns
- Graph visualization infrastructure (UnifiedGraphView, FlowGraphView)
- React Query for server state
- Component library with shadcn/ui
- Comprehensive testing (Vitest + Playwright)

**Types (Already Defined)**
- Problem management with RCA support
- Process management with BPMN
- Test cases with steps, automation status
- Coverage tracking with traceability matrix
- Webhook and external integration types

### What We're Adding

1. **ADR (Architecture Decision Records)** - MADR 4.0 format with compliance tracking
2. **Contracts (Design by Contract)** - Formal specifications with pre/post conditions
3. **BDD Features & Scenarios** - Gherkin-based behavior specifications
4. **Visual-First UI** - Graph-centric views, heat maps, dashboards
5. **MCP Native CLI** - FastMCP 2.14+ server with 40+ tools
6. **Agentic Capabilities** - AI-powered task decomposition, impact analysis, story generation
7. **Requirements Quality AI** - Smell detection, ambiguity checking, completeness validation

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 0: AGENTIC ORCHESTRATION                            │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────────┐ │
│  │ Task Decomposer │  │ Impact Analyzer  │  │ Story/ADR Generator         │ │
│  │ LangGraph FSM   │  │ Graph Traversal  │  │ LLM + RAG                   │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 1: SPECIFICATION ENGINE                             │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────────┐ │
│  │ ADR Management  │  │ Formal Contracts │  │ Requirements Quality AI     │ │
│  │ MADR 4.0 Format │  │ Pre/Post Conds   │  │ Smell/Ambiguity Detection   │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 2: BDD SCENARIO ENGINE                              │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────────┐ │
│  │ Gherkin Parser  │  │ Feature Store    │  │ Step Definition Registry    │ │
│  │ Given-When-Then │  │ Scenario Mgmt    │  │ Auto-Generation             │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 3: VISUAL UI ENGINE                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────────┐ │
│  │ Graph Canvas    │  │ Coverage Heatmap │  │ Compliance Dashboard        │ │
│  │ ADR Timeline    │  │ Gap Analysis     │  │ Impact Visualizer           │ │
│  │ Node-Based Edit │  │ Health Score     │  │ MADR Swimlanes              │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 4: MCP NATIVE CLI                                   │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────────┐ │
│  │ FastMCP 2.14+   │  │ Tools (50+)      │  │ Resources & Prompts         │ │
│  │ MCP Apps UI     │  │ Agent Handoffs   │  │ Context Provider            │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│               EXISTING: TraceRTM Core (Preserved)                            │
│  Items │ Links │ Graphs │ TestCases │ Projects │ Problems │ Processes │ ... │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Enhanced Features from Research

### Agentic PM Capabilities (from MetaGPT, CrewAI, LangGraph research)

```typescript
// Agent-powered task decomposition
interface AgentWorkflow {
  // Decompose epics → stories automatically
  decomposeEpic(epicId: string): Promise<UserStory[]>;

  // Auto-generate acceptance criteria
  generateAcceptanceCriteria(storyId: string): Promise<Criteria[]>;

  // Detect dependencies between stories
  detectDependencies(storyIds: string[]): Promise<DependencyGraph>;

  // Calculate critical path with AI estimation
  calculateCriticalPath(projectId: string): Promise<CriticalPath>;

  // Generate BDD scenarios from requirements
  generateScenarios(requirementId: string): Promise<Scenario[]>;

  // Create ADR from architectural discussion
  generateADR(context: string): Promise<ADR>;
}
```

### Requirements Quality AI (from smell detection research)

```typescript
interface RequirementsQualityService {
  // Multi-label smell detection (ISO 29148)
  detectSmells(requirement: string): Promise<{
    superlative: boolean;
    comparative: boolean;
    subjective: boolean;
    loopholes: boolean;
    ambiguousAdverbs: boolean;
    negativeStatements: boolean;
    vaguePronouns: boolean;
    openEnded: boolean;
    incompleteReferences: boolean;
  }>;

  // Ambiguity detection with LLM
  detectAmbiguity(requirement: string): Promise<AmbiguityReport>;

  // Completeness checking
  checkCompleteness(requirements: Requirement[]): Promise<CompletenessReport>;

  // Semantic similarity for duplicate detection
  findSimilar(requirement: string): Promise<SimilarRequirement[]>;
}
```

### AI-Powered Impact Analysis (from graph DB research)

```typescript
interface ImpactAnalysisService {
  // Live blast radius visualization
  calculateBlastRadius(itemId: string): Promise<BlastRadius>;

  // Risk propagation modeling (Bayesian)
  modelRiskPropagation(changeId: string): Promise<RiskModel>;

  // LLM-based traceability recovery
  recoverTraceLinks(codeChange: string): Promise<TraceLink[]>;

  // Compliance impact assessment
  assessComplianceImpact(changeId: string): Promise<ComplianceImpact>;
}
```

---

## Phase 1: Data Structures & Types (Week 1)

### 1.1 New TypeScript Types (DONE - specification.ts)

```typescript
// ADR Types (MADR 4.0 Format)
interface ADR {
  id, projectId, adrNumber, title, status
  context, decision, consequences  // MADR format
  decisionDrivers, consideredOptions
  relatedRequirements, relatedAdrs, supersededBy
  complianceScore, lastVerifiedAt

  // Enhanced from research
  stakeholders: string[];
  tags: string[];
  date: string;
  supersedes?: string;
}

// Contract Types (Design by Contract)
interface Contract {
  id, projectId, itemId, contractType, status
  preconditions, postconditions, invariants  // Formal specs
  states, transitions  // State machine
  executableSpec, specLanguage
  verificationResult
}

// BDD Types
interface Feature {
  id, featureNumber, name
  asA, iWant, soThat  // User story format
  scenarios, passRate, coverage

  // Enhanced
  tags: string[];
  background?: ScenarioStep[];
}

interface Scenario {
  id, featureId, title, gherkinText
  givenSteps, whenSteps, thenSteps
  status, passRate, executionCount

  // Enhanced
  examples?: DataTable;  // For scenario outlines
  tags: string[];
}

// Requirements Quality (from research)
interface RequirementSmells {
  requirementId: string;
  smells: SmellType[];
  ambiguityScore: number;
  completenessScore: number;
  suggestions: string[];
}
```

### 1.2 Backend Models (To Create)

```python
# src/tracertm/models/adr.py
class ADR(Base, TimestampMixin):
    id: Mapped[str]
    project_id: Mapped[str]
    adr_number: Mapped[str]  # ADR-0001
    title: Mapped[str]
    status: Mapped[ADRStatus]
    context: Mapped[str]
    decision: Mapped[str]
    consequences: Mapped[str]
    decision_drivers: Mapped[list[str]]
    considered_options: Mapped[list[dict]]
    related_requirements: Mapped[list[str]]
    related_adrs: Mapped[list[str]]
    supersedes: Mapped[str | None]
    superseded_by: Mapped[str | None]
    compliance_score: Mapped[float]
    last_verified_at: Mapped[datetime | None]
    stakeholders: Mapped[list[str]]
    tags: Mapped[list[str]]
    date: Mapped[date]

# src/tracertm/models/contract.py
class Contract(Base, TimestampMixin):
    id: Mapped[str]
    project_id: Mapped[str]
    item_id: Mapped[str]
    contract_type: Mapped[ContractType]
    status: Mapped[ContractStatus]
    preconditions: Mapped[list[dict]]
    postconditions: Mapped[list[dict]]
    invariants: Mapped[list[dict]]
    states: Mapped[list[str]]
    transitions: Mapped[list[dict]]
    executable_spec: Mapped[str | None]
    verification_result: Mapped[dict | None]

# src/tracertm/models/feature.py
class Feature(Base, TimestampMixin):
    id: Mapped[str]
    project_id: Mapped[str]
    feature_number: Mapped[str]
    name: Mapped[str]
    as_a: Mapped[str | None]
    i_want: Mapped[str | None]
    so_that: Mapped[str | None]
    status: Mapped[FeatureStatus]
    file_path: Mapped[str | None]
    background: Mapped[list[dict]]
    tags: Mapped[list[str]]

# src/tracertm/models/scenario.py
class Scenario(Base, TimestampMixin):
    id: Mapped[str]
    feature_id: Mapped[str]
    scenario_number: Mapped[str]
    title: Mapped[str]
    gherkin_text: Mapped[str]
    given_steps: Mapped[list[dict]]
    when_steps: Mapped[list[dict]]
    then_steps: Mapped[list[dict]]
    is_outline: Mapped[bool]
    examples: Mapped[dict | None]
    tags: Mapped[list[str]]
    requirement_ids: Mapped[list[str]]
    test_case_ids: Mapped[list[str]]
    status: Mapped[ScenarioStatus]
    pass_rate: Mapped[float]

# NEW: Requirements quality tracking
# src/tracertm/models/requirement_quality.py
class RequirementQuality(Base, TimestampMixin):
    id: Mapped[str]
    item_id: Mapped[str]
    smells: Mapped[list[str]]  # ISO 29148 smell types
    ambiguity_score: Mapped[float]
    completeness_score: Mapped[float]
    suggestions: Mapped[list[str]]
    last_analyzed_at: Mapped[datetime]
```

### 1.3 Database Migrations

```sql
-- Alembic migration: add_specifications.py

CREATE TABLE adrs (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) REFERENCES projects(id),
    adr_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'proposed',
    context TEXT NOT NULL,
    decision TEXT NOT NULL,
    consequences TEXT NOT NULL,
    decision_drivers JSONB DEFAULT '[]',
    considered_options JSONB DEFAULT '[]',
    related_requirements JSONB DEFAULT '[]',
    related_adrs JSONB DEFAULT '[]',
    supersedes VARCHAR(50),
    superseded_by VARCHAR(50),
    compliance_score FLOAT DEFAULT 0.0,
    last_verified_at TIMESTAMP WITH TIME ZONE,
    stakeholders JSONB DEFAULT '[]',
    tags JSONB DEFAULT '[]',
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE contracts (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) REFERENCES projects(id),
    item_id VARCHAR(255) REFERENCES items(id),
    contract_number VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    contract_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    preconditions JSONB DEFAULT '[]',
    postconditions JSONB DEFAULT '[]',
    invariants JSONB DEFAULT '[]',
    states JSONB DEFAULT '[]',
    transitions JSONB DEFAULT '[]',
    executable_spec TEXT,
    spec_language VARCHAR(50),
    verification_result JSONB,
    last_verified_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE features (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) REFERENCES projects(id),
    feature_number VARCHAR(50) NOT NULL,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    as_a VARCHAR(500),
    i_want VARCHAR(500),
    so_that VARCHAR(500),
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    file_path VARCHAR(500),
    background JSONB DEFAULT '[]',
    tags JSONB DEFAULT '[]',
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE scenarios (
    id VARCHAR(255) PRIMARY KEY,
    feature_id VARCHAR(255) REFERENCES features(id),
    scenario_number VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    gherkin_text TEXT NOT NULL,
    given_steps JSONB DEFAULT '[]',
    when_steps JSONB DEFAULT '[]',
    then_steps JSONB DEFAULT '[]',
    is_outline BOOLEAN DEFAULT FALSE,
    examples JSONB,
    tags JSONB DEFAULT '[]',
    requirement_ids JSONB DEFAULT '[]',
    test_case_ids JSONB DEFAULT '[]',
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    last_run_at TIMESTAMP WITH TIME ZONE,
    last_run_result VARCHAR(50),
    execution_count INTEGER DEFAULT 0,
    pass_rate FLOAT DEFAULT 0.0,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE step_definitions (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) REFERENCES projects(id),
    step_type VARCHAR(20) NOT NULL,
    pattern VARCHAR(500) NOT NULL,
    regex_pattern VARCHAR(500),
    implementation_path VARCHAR(500),
    implementation_code TEXT,
    parameters JSONB DEFAULT '[]',
    documentation TEXT,
    examples JSONB DEFAULT '[]',
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- NEW: Requirements quality tracking
CREATE TABLE requirement_quality (
    id VARCHAR(255) PRIMARY KEY,
    item_id VARCHAR(255) REFERENCES items(id) ON DELETE CASCADE,
    smells JSONB DEFAULT '[]',
    ambiguity_score FLOAT DEFAULT 0.0,
    completeness_score FLOAT DEFAULT 0.0,
    suggestions JSONB DEFAULT '[]',
    last_analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_adrs_project ON adrs(project_id);
CREATE INDEX idx_adrs_status ON adrs(status);
CREATE INDEX idx_adrs_date ON adrs(date);
CREATE INDEX idx_contracts_project ON contracts(project_id);
CREATE INDEX idx_contracts_item ON contracts(item_id);
CREATE INDEX idx_features_project ON features(project_id);
CREATE INDEX idx_scenarios_feature ON scenarios(feature_id);
CREATE INDEX idx_scenarios_status ON scenarios(status);
CREATE INDEX idx_step_definitions_project ON step_definitions(project_id);
CREATE INDEX idx_requirement_quality_item ON requirement_quality(item_id);
```

---

## Phase 2: Visual UI Components (Week 2-3)

### 2.1 Component Architecture (shadcn/ui pattern)

Following the W3C DTCG token standard and shadcn/ui copy-paste ownership pattern:

```
frontend/apps/web/src/components/specifications/
├── index.ts                    # Barrel exports
│
├── adr/
│   ├── ADRCard.tsx            # Visual ADR card with status badge
│   ├── ADRTimeline.tsx        # Chronological ADR history (swimlanes)
│   ├── ADRGraph.tsx           # ADR dependency visualization
│   ├── ADREditor.tsx          # MADR 4.0 format editor
│   ├── ComplianceGauge.tsx    # Compliance score visualization
│   ├── DecisionMatrix.tsx     # Options comparison table
│   └── ADRDiff.tsx            # Version comparison view
│
├── contracts/
│   ├── ContractCard.tsx       # Contract summary card
│   ├── ContractEditor.tsx     # Visual contract builder
│   ├── StateMachineViewer.tsx # Interactive state diagram
│   ├── ConditionList.tsx      # Pre/post/invariant display
│   └── VerificationBadge.tsx  # Pass/fail status
│
├── bdd/
│   ├── FeatureCard.tsx        # Feature summary with stats
│   ├── ScenarioCard.tsx       # Scenario with step display
│   ├── GherkinEditor.tsx      # Monaco-based Gherkin editor
│   ├── GherkinViewer.tsx      # Formatted Gherkin display
│   ├── StepBadge.tsx          # Given/When/Then badge
│   ├── StepLibrary.tsx        # Reusable step browser
│   ├── ScenarioRunner.tsx     # Execute and view results
│   └── ExamplesTable.tsx      # Data table for outlines
│
├── quality/                    # NEW: Requirements quality
│   ├── SmellIndicator.tsx     # Visual smell warning
│   ├── QualityScore.tsx       # Quality gauge
│   ├── SmellDetails.tsx       # Detailed smell breakdown
│   └── SuggestionList.tsx     # AI suggestions
│
└── dashboard/
    ├── SpecificationDashboard.tsx  # Combined overview
    ├── HealthScoreRing.tsx         # Health score visualization
    ├── CoverageHeatmap.tsx         # Requirement coverage heatmap
    ├── GapAnalysis.tsx             # Uncovered items list
    └── AgentActivityFeed.tsx       # NEW: Agent action feed
```

### 2.2 New Views (To Create)

```
frontend/apps/web/src/views/
├── ADRView.tsx                 # ADR management dashboard
├── ADRDetailView.tsx           # Single ADR detail + editing
├── ContractView.tsx            # Contracts overview
├── ContractDetailView.tsx      # Contract detail + state machine
├── FeatureView.tsx             # BDD features list
├── FeatureDetailView.tsx       # Feature with scenarios
├── ScenarioView.tsx            # Scenario execution view
├── SpecificationDashboard.tsx  # Combined specs overview
├── ComplianceView.tsx          # Compliance tracking dashboard
├── RequirementQualityView.tsx  # NEW: Quality analysis view
└── AgentWorkflowView.tsx       # NEW: Agent task decomposition
```

### 2.3 Visual Design Principles (Enhanced)

1. **Graph-First**: Default to graph visualizations over tables
2. **Progressive Disclosure**: Details on hover/click, not upfront
3. **Real-Time Validation**: Contracts verified as you type
4. **Coverage Overlay**: Show coverage status on all views
5. **ADR Context**: Link to ADRs from anywhere
6. **Color-Coded Status**: Consistent status colors across all specs
7. **Animated Transitions**: framer-motion for smooth state changes
8. **Token-Based Theming**: W3C DTCG tokens for consistency
9. **Accessibility-First**: WCAG 2.1 AA compliance, keyboard navigation
10. **Agent Awareness**: Visual indicators when AI is active

---

## Phase 3: Backend Services & API (Week 3-4)

### 3.1 New Services (Enhanced)

```python
# src/tracertm/services/

# ADR Services
adr_service.py              # ADR CRUD and management
adr_compliance_service.py   # Compliance verification
adr_linking_service.py      # ADR-to-requirement linking
adr_generation_service.py   # NEW: LLM-based ADR generation

# Contract Services
contract_service.py         # Contract CRUD
contract_verification_service.py  # Formal verification
state_machine_service.py    # State machine execution

# BDD Services
feature_service.py          # Feature management
scenario_service.py         # Scenario CRUD
gherkin_parser_service.py   # Parse Gherkin text
step_registry_service.py    # Step definition management
scenario_runner_service.py  # Execute scenarios
scenario_generation_service.py  # NEW: AI scenario generation

# Quality Services (NEW from research)
requirement_quality_service.py   # Smell detection, completeness
ambiguity_detection_service.py   # LLM-based ambiguity checking
similarity_service.py            # Semantic deduplication

# Agentic Services (NEW from research)
task_decomposition_service.py    # Epic → stories breakdown
impact_analysis_service.py       # Enhanced with LLM
traceability_recovery_service.py # LLM-based link recovery
agent_orchestration_service.py   # LangGraph FSM

# Dashboard Services
specification_dashboard_service.py  # Aggregate metrics
health_score_service.py     # Calculate health scores
```

### 3.2 Agent Orchestration (LangGraph Pattern from Research)

```python
# src/tracertm/services/agent_orchestration_service.py
from langgraph.graph import StateGraph
from langgraph.prebuilt import interrupt

class AgentOrchestrationService:
    def __init__(self):
        self.workflow = StateGraph(AgentState)
        self._build_workflow()

    def _build_workflow(self):
        # Define agent nodes
        self.workflow.add_node("plan", self._plan_step)
        self.workflow.add_node("decompose", self._decompose_step)
        self.workflow.add_node("generate", self._generate_step)
        self.workflow.add_node("review", self._review_step)

        # Define edges
        self.workflow.add_edge("plan", "decompose")
        self.workflow.add_conditional_edges(
            "decompose",
            self._should_generate,
            {"generate": "generate", "review": "review"}
        )
        self.workflow.add_edge("generate", "review")

    async def decompose_epic(self, epic_id: str) -> list[dict]:
        """Decompose epic into user stories using LLM."""
        state = {"epic_id": epic_id, "stories": []}
        result = await self.workflow.ainvoke(state)
        return result["stories"]

    async def generate_scenarios(self, requirement_id: str) -> list[dict]:
        """Generate BDD scenarios from a requirement."""
        # Uses LLM with project context via RAG
        ...

    async def generate_adr(self, context: str) -> dict:
        """Generate ADR from architectural discussion."""
        # MADR 4.0 format with decision drivers
        ...
```

### 3.3 New API Endpoints (Enhanced)

```python
# ADR Endpoints
GET    /api/v1/projects/{projectId}/adrs
GET    /api/v1/adrs/{adrId}
POST   /api/v1/projects/{projectId}/adrs
PUT    /api/v1/adrs/{adrId}
DELETE /api/v1/adrs/{adrId}
POST   /api/v1/adrs/{adrId}/verify
GET    /api/v1/adrs/{adrId}/compliance
POST   /api/v1/adrs/generate              # NEW: AI generation

# Contract Endpoints
GET    /api/v1/projects/{projectId}/contracts
GET    /api/v1/contracts/{contractId}
POST   /api/v1/projects/{projectId}/contracts
PUT    /api/v1/contracts/{contractId}
POST   /api/v1/contracts/{contractId}/verify

# Feature/Scenario Endpoints
GET    /api/v1/projects/{projectId}/features
GET    /api/v1/features/{featureId}
POST   /api/v1/projects/{projectId}/features
GET    /api/v1/features/{featureId}/scenarios
POST   /api/v1/features/{featureId}/scenarios
POST   /api/v1/scenarios/{scenarioId}/run
POST   /api/v1/scenarios/generate          # NEW: AI generation

# Quality Endpoints (NEW)
GET    /api/v1/items/{itemId}/quality
POST   /api/v1/items/{itemId}/analyze-quality
GET    /api/v1/projects/{projectId}/quality-report

# Agentic Endpoints (NEW)
POST   /api/v1/epics/{epicId}/decompose
POST   /api/v1/requirements/{reqId}/generate-scenarios
POST   /api/v1/projects/{projectId}/generate-adr
POST   /api/v1/items/{itemId}/analyze-impact

# Dashboard Endpoints
GET    /api/v1/projects/{projectId}/specifications/summary
GET    /api/v1/projects/{projectId}/specifications/health
GET    /api/v1/projects/{projectId}/specifications/coverage
```

---

## Phase 4: MCP Native CLI (Week 4-5)

### 4.1 FastMCP 2.14+ Server Structure (Enhanced)

Based on MCP ecosystem research, implementing with MCP Apps support:

```python
# src/tracertm/mcp/
├── __init__.py
├── server.py              # Main FastMCP server
│
├── tools/
│   ├── __init__.py
│   ├── items.py           # Item CRUD tools
│   ├── links.py           # Link management
│   ├── adrs.py            # ADR management
│   ├── contracts.py       # Contract verification
│   ├── scenarios.py       # BDD scenario tools
│   ├── coverage.py        # Coverage analysis
│   ├── impact.py          # Impact analysis
│   ├── quality.py         # NEW: Quality analysis
│   └── agents.py          # NEW: Agent orchestration
│
├── resources/
│   ├── __init__.py
│   ├── projects.py        # Project resources
│   ├── graphs.py          # Graph data
│   ├── reports.py         # Report resources
│   └── specifications.py  # Spec resources
│
├── prompts/
│   ├── __init__.py
│   ├── adr_prompts.py     # ADR creation prompts
│   ├── bdd_prompts.py     # Scenario generation
│   └── analysis_prompts.py # Analysis prompts
│
└── apps/                   # NEW: MCP Apps (Jan 2026)
    ├── __init__.py
    ├── coverage_dashboard.py  # Interactive coverage view
    ├── impact_visualizer.py   # Impact analysis UI
    └── quality_report.py      # Quality analysis UI
```

### 4.2 MCP Server Implementation (50+ Tools)

```python
# src/tracertm/mcp/server.py
from fastmcp import FastMCP

mcp = FastMCP("TraceRTM", version="2.0.0")

# =============================================================================
# TOOLS: Actions the AI can perform (50+ tools)
# =============================================================================

# Item Management (10 tools)
@mcp.tool(tags={"items", "crud"})
async def create_item(...) -> dict: ...

@mcp.tool(tags={"items", "crud"})
async def update_item(...) -> dict: ...

@mcp.tool(tags={"items", "bulk"})
async def bulk_create_items(...) -> dict: ...

# ADR Management (8 tools)
@mcp.tool(tags={"adrs", "documentation"})
async def create_adr(
    project_id: str,
    title: str,
    context: str,
    decision: str,
    consequences: str,
    decision_drivers: list[str] = [],
    considered_options: list[dict] = [],
    related_requirements: list[str] = [],
) -> dict:
    """Create an Architecture Decision Record following MADR 4.0 format."""
    ...

@mcp.tool(tags={"adrs", "ai"})
async def generate_adr(context: str) -> dict:
    """Generate an ADR from an architectural discussion using AI."""
    ...

@mcp.tool(tags={"adrs", "verification"})
async def verify_adr_compliance(adr_id: str) -> dict:
    """Verify ADR compliance against related requirements."""
    ...

# Contract Management (6 tools)
@mcp.tool(tags={"contracts", "verification"})
async def verify_contract(contract_id: str) -> dict:
    """Execute contract verification and return compliance results."""
    ...

@mcp.tool(tags={"contracts", "state-machine"})
async def execute_transition(contract_id: str, event: str) -> dict:
    """Execute a state machine transition."""
    ...

# BDD/Scenario Management (8 tools)
@mcp.tool(tags={"bdd", "scenarios"})
async def create_scenario(
    feature_id: str,
    title: str,
    given: list[str],
    when: list[str],
    then: list[str],
    requirement_ids: list[str] = [],
) -> dict:
    """Create a BDD scenario in Gherkin format."""
    ...

@mcp.tool(tags={"bdd", "ai"})
async def generate_scenarios(requirement_id: str, count: int = 3) -> list[dict]:
    """Generate BDD scenarios from a requirement using AI."""
    ...

@mcp.tool(tags={"bdd", "execution"})
async def run_scenario(scenario_id: str) -> dict:
    """Execute a scenario and return results."""
    ...

# Analysis Tools (10 tools)
@mcp.tool(tags={"analysis", "impact"})
async def analyze_impact(
    item_id: str,
    depth: int = 3,
    include_adrs: bool = True,
    include_tests: bool = True,
) -> dict:
    """Analyze the impact of changing an item across the traceability graph."""
    ...

@mcp.tool(tags={"analysis", "blast-radius"})
async def calculate_blast_radius(item_id: str) -> dict:
    """Calculate blast radius for a change (downstream services affected)."""
    ...

@mcp.tool(tags={"coverage", "analysis"})
async def calculate_coverage(
    project_id: str,
    requirement_filter: str | None = None,
) -> dict:
    """Calculate test coverage percentage for requirements."""
    ...

@mcp.tool(tags={"coverage", "gaps"})
async def find_coverage_gaps(project_id: str) -> list[dict]:
    """Find requirements without test coverage."""
    ...

# Quality Tools (NEW - 6 tools)
@mcp.tool(tags={"quality", "smells"})
async def detect_requirement_smells(requirement_text: str) -> dict:
    """Detect ISO 29148 requirement smells (ambiguity, incompleteness, etc.)."""
    ...

@mcp.tool(tags={"quality", "similarity"})
async def find_similar_requirements(requirement_id: str) -> list[dict]:
    """Find semantically similar requirements (potential duplicates)."""
    ...

# Agent/Agentic Tools (NEW - 8 tools)
@mcp.tool(tags={"agents", "decomposition"})
async def decompose_epic(epic_id: str) -> list[dict]:
    """Decompose an epic into user stories using AI."""
    ...

@mcp.tool(tags={"agents", "criteria"})
async def generate_acceptance_criteria(story_id: str) -> list[str]:
    """Generate acceptance criteria for a user story."""
    ...

@mcp.tool(tags={"agents", "dependencies"})
async def detect_dependencies(story_ids: list[str]) -> dict:
    """Detect dependencies between stories."""
    ...

@mcp.tool(tags={"agents", "critical-path"})
async def calculate_critical_path(project_id: str) -> dict:
    """Calculate critical path with AI-powered estimation."""
    ...

# =============================================================================
# RESOURCES: Data the AI can access
# =============================================================================

@mcp.resource("tracertm://projects/{project_id}/items")
async def get_project_items(project_id: str) -> str:
    """Get all items for a project."""
    ...

@mcp.resource("tracertm://projects/{project_id}/adrs")
async def get_project_adrs(project_id: str) -> str:
    """Get all ADRs for a project in MADR format."""
    ...

@mcp.resource("tracertm://projects/{project_id}/coverage")
async def get_coverage_report(project_id: str) -> str:
    """Get coverage report including gaps and metrics."""
    ...

@mcp.resource("tracertm://projects/{project_id}/graph/{graph_type}")
async def get_graph(project_id: str, graph_type: str) -> str:
    """Get traceability graph (dependency, coverage, impact, adr)."""
    ...

@mcp.resource("tracertm://projects/{project_id}/quality")
async def get_quality_report(project_id: str) -> str:
    """Get requirements quality analysis report."""
    ...

# =============================================================================
# PROMPTS: Reusable prompt templates
# =============================================================================

@mcp.prompt("create_adr")
def create_adr_prompt(context: str) -> str:
    """Prompt template for creating an ADR from context."""
    return f"""Create an Architecture Decision Record based on:

{context}

Use MADR 4.0 format:
1. Title (short, representative)
2. Status: Proposed
3. Context and Problem Statement (2-3 sentences)
4. Decision Drivers (what influences the decision)
5. Considered Options (at least 3 with pros/cons)
6. Decision Outcome (chosen option with rationale)
7. Consequences (positive and negative)
"""

@mcp.prompt("coverage_analysis")
def coverage_analysis_prompt(project_id: str) -> str:
    """Prompt for analyzing test coverage gaps."""
    ...

@mcp.prompt("scenario_generation")
def scenario_generation_prompt(requirement: str) -> str:
    """Prompt for generating BDD scenarios from requirements."""
    return f"""Generate BDD scenarios for this requirement:

{requirement}

Create 3-5 scenarios covering:
1. Happy path
2. Edge cases
3. Error conditions
4. Boundary values

Use Gherkin format with Given/When/Then steps.
"""

@mcp.prompt("requirement_quality")
def requirement_quality_prompt(requirement: str) -> str:
    """Prompt for analyzing requirement quality."""
    ...

# =============================================================================
# MCP APPS: Interactive UI components (NEW - Jan 2026)
# =============================================================================

@mcp.app("coverage_dashboard")
def coverage_dashboard_app(project_id: str) -> dict:
    """Interactive coverage dashboard with heatmap."""
    return {
        "type": "dashboard",
        "components": [
            {"type": "heatmap", "data": get_coverage_data(project_id)},
            {"type": "gauge", "value": get_coverage_percentage(project_id)},
            {"type": "list", "items": get_uncovered_items(project_id)},
        ]
    }
```

---

## Phase 5: Integration & Polish (Week 5-6)

### 5.1 Route Configuration

```typescript
// New routes to add
/projects/$projectId/adrs                    # ADR list
/projects/$projectId/adrs/$adrId             # ADR detail
/projects/$projectId/contracts               # Contracts list
/projects/$projectId/contracts/$contractId   # Contract detail
/projects/$projectId/features                # BDD features
/projects/$projectId/features/$featureId     # Feature detail
/projects/$projectId/specifications          # Unified dashboard
/projects/$projectId/compliance              # Compliance view
/projects/$projectId/quality                 # NEW: Quality view
/projects/$projectId/agents                  # NEW: Agent workflows
```

### 5.2 Navigation Updates

```typescript
// Sidebar navigation additions
{
  title: "Specifications",
  icon: FileCode,
  items: [
    { title: "ADRs", href: "/projects/$projectId/adrs" },
    { title: "Contracts", href: "/projects/$projectId/contracts" },
    { title: "Features", href: "/projects/$projectId/features" },
    { title: "Compliance", href: "/projects/$projectId/compliance" },
  ]
},
{
  title: "Quality",  // NEW
  icon: ShieldCheck,
  items: [
    { title: "Requirement Quality", href: "/projects/$projectId/quality" },
    { title: "Smell Detection", href: "/projects/$projectId/quality/smells" },
  ]
},
{
  title: "AI Agents",  // NEW
  icon: Bot,
  items: [
    { title: "Task Decomposition", href: "/projects/$projectId/agents/decompose" },
    { title: "Scenario Generation", href: "/projects/$projectId/agents/scenarios" },
    { title: "ADR Generation", href: "/projects/$projectId/agents/adrs" },
  ]
}
```

### 5.3 Command Palette Extensions

```typescript
// Add specification commands
{
  id: "create-adr",
  title: "Create ADR",
  shortcut: ["alt", "a"],
  action: () => navigate("/projects/$projectId/adrs?action=create")
},
{
  id: "create-scenario",
  title: "Create Scenario",
  shortcut: ["alt", "s"],
  action: () => navigate("/projects/$projectId/features?action=create-scenario")
},
{
  id: "decompose-epic",
  title: "AI: Decompose Epic",
  shortcut: ["alt", "d"],
  action: () => openAgentModal("decompose")
},
{
  id: "generate-scenarios",
  title: "AI: Generate Scenarios",
  shortcut: ["alt", "g"],
  action: () => openAgentModal("generate-scenarios")
},
{
  id: "analyze-quality",
  title: "Analyze Requirement Quality",
  shortcut: ["alt", "q"],
  action: () => analyzeSelectedRequirements()
}
```

---

## Success Metrics

### Quantitative
- [ ] 100% type coverage for new entities
- [ ] <200ms response time for specification queries
- [ ] 80%+ test coverage for new components
- [ ] 50+ MCP tools implemented
- [ ] 90%+ requirements quality detection accuracy

### Qualitative
- [ ] Visual-first: Every entity has graph/visual representation
- [ ] Bidirectional traceability: Navigate between all spec types
- [ ] Real-time: Changes reflected immediately in UI
- [ ] AI-native: All operations accessible via MCP
- [ ] Agent-powered: Task decomposition, scenario generation working

---

## Dependencies

### Frontend (Already Available)
- React 18+, TanStack Router, TanStack Query
- Tailwind CSS, shadcn/ui
- Recharts (charts)
- framer-motion (animations)
- Monaco Editor (for Gherkin editing)

### Backend (To Add)
```bash
pip install fastmcp>=2.14.0     # MCP server
pip install gherkin-official    # Gherkin parser
pip install langgraph>=1.0.0    # Agent orchestration
pip install anthropic>=0.40.0   # LLM integration
pip install sentence-transformers  # Semantic similarity
```

### Environment Variables
```bash
# MCP Server
MCP_SERVER_PORT=9000
MCP_SERVER_HOST=0.0.0.0

# LLM Integration
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...  # Optional

# Feature Flags
ENABLE_SPECIFICATIONS=true
ENABLE_MCP_SERVER=true
ENABLE_AGENT_WORKFLOWS=true
ENABLE_QUALITY_ANALYSIS=true
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Performance with large graphs | Pagination, lazy loading, WebGL rendering, Neo4j integration |
| Type duplication (TS/Python) | Code generation from shared OpenAPI schema |
| Learning curve for BDD | Guided wizards, templates, AI-assisted generation |
| MCP client compatibility | Test with Claude, Cursor, VS Code, Windsurf |
| LLM cost management | Caching, rate limiting, usage monitoring |
| Agent reliability | Human-in-the-loop checkpoints (LangGraph interrupt()) |

---

## Timeline Summary

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1 | Data Structures | Types, Models, Migrations |
| 2 | UI Components (ADR) | ADRCard, Timeline, Graph, Editor |
| 3 | UI Components (BDD) | Feature, Scenario, Gherkin components |
| 3-4 | Backend Services | Repositories, Services, API endpoints |
| 4-5 | MCP Server | FastMCP tools, resources, prompts |
| 5-6 | Integration | Routes, Navigation, Polish, Agent workflows |

---

## Research Sources

### Agentic PM
- MetaGPT: ICLR 2024/2025 papers, 85.9% Pass@1
- CrewAI: 60% Fortune 500 adoption, $18M Series A
- LangGraph: 2.2x faster than CrewAI, FSM-based

### Requirements Quality
- ISO 29148 smell detection with LSTM/Bi-LSTM
- LLM-based ambiguity detection
- Paska tool for smell recommendations

### Graph Databases
- Neo4j Infinigraph: ACID + analytical
- 99% validation accuracy with RAG
- Knowledge graphs: 300-320% ROI

### MCP Ecosystem
- Linux Foundation AAIF (Dec 2025)
- MCP Apps for interactive UI (Jan 2026)
- 50+ enterprise servers available

### Design Systems
- W3C DTCG v1.0 (Oct 2025)
- shadcn/ui pattern: code ownership
- Figma MCP Server for dev mode

---

## Next Steps

1. **Immediate**: Review and approve this enhanced plan
2. **Week 1**: Create backend models and migrations
3. **Week 2**: Build ADR UI components
4. **Parallel**: Develop MCP server alongside UI work
5. **Ongoing**: Integrate agentic capabilities incrementally
