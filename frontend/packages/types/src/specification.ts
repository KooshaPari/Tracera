// Specification Engine Types - ADR, Contracts, BDD Scenarios
// Layer 1 & 2 of TraceRTM v2 Architecture (ADR-0001)

// =============================================================================
// ADR (Architecture Decision Record) Types
// =============================================================================

export type ADRStatus = 'proposed' | 'accepted' | 'deprecated' | 'superseded' | 'rejected';

export interface ADR {
  id: string;
  projectId: string;
  adrNumber: string; // ADR-0001, ADR-0002...
  title: string;
  status: ADRStatus;

  // MADR Format Fields
  context: string; // Problem statement
  decision: string; // What we decided
  consequences: string; // Good/bad outcomes

  // Decision Drivers
  decisionDrivers?: string[] | undefined;

  // Considered Options
  consideredOptions?: ADROption[] | undefined;

  // Traceability Links
  relatedRequirements?: string[] | undefined; // [REQ-001, REQ-002]
  relatedAdrs?: string[] | undefined; // [ADR-002, ADR-003]
  supersededBy?: string | undefined; // ADR-0010
  supersedes?: string | undefined; // ADR-0005

  // Verification & Compliance
  complianceScore?: number | undefined; // 0.0 - 100.0
  lastVerifiedAt?: string | undefined;
  verificationNotes?: string | undefined;

  // Metadata
  deciders?: string[] | undefined;
  stakeholders?: string[] | undefined;
  date?: string | undefined;
  tags?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;

  // Timestamps
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface ADROption {
  id: string;
  title: string;
  description: string;
  pros?: string[] | undefined;
  cons?: string[] | undefined;
  isChosen: boolean;
}

export interface ADRActivity {
  id: string;
  adrId: string;
  activityType: string;
  fromValue?: string | undefined;
  toValue?: string | undefined;
  description?: string | undefined;
  performedBy?: string | undefined;
  createdAt: string;
}

export interface ADRStats {
  projectId: string;
  total: number;
  byStatus: Record<string, number>;
  averageComplianceScore: number;
  requirementsLinked: number;
  pendingVerification: number;
}

// =============================================================================
// Requirement Quality Types (ISO 29148)
// =============================================================================

export type SmellType =
  | 'superlative'
  | 'comparative'
  | 'subjective'
  | 'loopholes'
  | 'ambiguous_adverbs'
  | 'negative_statements'
  | 'vague_pronouns'
  | 'open_ended'
  | 'incomplete_references';

export interface RequirementQuality {
  id: string;
  itemId: string; // Linked to the requirement Item
  smells: SmellType[];
  ambiguityScore: number; // 0.0 - 1.0 (higher is more ambiguous)
  completenessScore: number; // 0.0 - 1.0 (higher is more complete)
  suggestions: string[];
  lastAnalyzedAt: string;
  version: number;
  createdAt: string;
  updatedAt: string;
}

// =============================================================================
// Contract Types (Design by Contract)
// =============================================================================

export type ContractType = 'api' | 'function' | 'invariant' | 'data' | 'integration';

export type ContractStatus = 'draft' | 'active' | 'verified' | 'violated' | 'deprecated';

export interface ContractCondition {
  id: string;
  description: string;
  expression?: string | undefined; // Formal expression (can be pseudo-code or actual)
  isRequired: boolean;
  lastVerifiedResult?: 'pass' | 'fail' | 'skip' | undefined;
}

export interface ContractTransition {
  id: string;
  fromState: string;
  toState: string;
  trigger: string;
  guards?: string[] | undefined;
  actions?: string[] | undefined;
}

export interface Contract {
  id: string;
  projectId: string;
  itemId: string; // Linked to requirement/feature
  contractNumber: string; // CONTRACT-001
  title: string;
  description?: string | undefined;
  contractType: ContractType;
  status: ContractStatus;

  // Contract Definition
  preconditions: ContractCondition[];
  postconditions: ContractCondition[];
  invariants: ContractCondition[];

  // State Machine (optional)
  states?: string[] | undefined;
  initialState?: string | undefined;
  transitions?: ContractTransition[] | undefined;

  // Executable Specification
  executableSpec?: string | undefined; // Code for verification
  specLanguage?: 'typescript' | 'python' | 'gherkin' | undefined;

  // Verification
  lastVerifiedAt?: string | undefined;
  verificationResult?:
    | {
        status: 'pass' | 'fail' | 'error';
        passedConditions: number;
        failedConditions: number;
        details?: string | undefined;
      }
    | undefined;

  // Metadata
  tags?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface ContractStats {
  projectId: string;
  total: number;
  byType: Record<string, number>;
  byStatus: Record<string, number>;
  verificationRate: number;
  violationCount: number;
}

export interface ContractActivity {
  id: string;
  contractId: string;
  activityType: string;
  fromValue?: string | undefined;
  toValue?: string | undefined;
  description?: string | undefined;
  performedBy?: string | undefined;
  createdAt: string;
}

// =============================================================================
// BDD Feature & Scenario Types
// =============================================================================

export type FeatureStatus = 'draft' | 'active' | 'deprecated' | 'archived';

export interface Feature {
  id: string;
  projectId: string;
  featureNumber: string; // FEAT-001
  name: string;
  description?: string | undefined;
  asA?: string | undefined; // As a [role]
  iWant?: string | undefined; // I want [capability]
  soThat?: string | undefined; // So that [benefit]

  status: FeatureStatus;
  filePath?: string | undefined; // Features/auth.feature
  tags?: string[] | undefined;

  // Aggregated stats
  scenarioCount: number;
  passedScenarios: number;
  failedScenarios: number;
  pendingScenarios: number;

  // Traceability
  relatedRequirements?: string[] | undefined;
  relatedAdrs?: string[] | undefined;

  metadata?: Record<string, unknown> | undefined;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export type ScenarioStatus = 'draft' | 'pending' | 'passing' | 'failing' | 'skipped';

export interface ScenarioStep {
  stepNumber: number;
  keyword: 'Given' | 'When' | 'Then' | 'And' | 'But';
  text: string;
  dataTable?: string[][] | undefined; // Table data
  docString?: string | undefined; // Multi-line string
  stepDefinitionId?: string | undefined; // Link to step definition
}

export interface Scenario {
  id: string;
  featureId: string;
  scenarioNumber: string; // SCEN-001
  title: string;
  description?: string | undefined;
  gherkinText: string; // Full Gherkin scenario text

  // Parsed Structure
  background?: ScenarioStep[] | undefined;
  givenSteps: ScenarioStep[];
  whenSteps: ScenarioStep[];
  thenSteps: ScenarioStep[];

  // Scenario type
  isOutline: boolean;
  examples?: Record<string, string[]> | undefined; // For Scenario Outline

  // Tags
  tags?: string[] | undefined;

  // Traceability
  requirementIds?: string[] | undefined;
  testCaseIds?: string[] | undefined;

  // Execution Status
  status: ScenarioStatus;
  lastRunAt?: string | undefined;
  lastRunResult?: 'pass' | 'fail' | 'pending' | 'error' | undefined;
  lastRunDurationMs?: number | undefined;
  executionCount: number;
  passRate: number;

  metadata?: Record<string, unknown> | undefined;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface ScenarioActivity {
  id: string;
  scenarioId: string;
  activityType: string;
  fromValue?: string | undefined;
  toValue?: string | undefined;
  description?: string | undefined;
  performedBy?: string | undefined;
  createdAt: string;
}

export interface ScenarioResult {
  id: string;
  scenarioId: string;
  runId: string;
  status: 'pass' | 'fail' | 'pending' | 'error';
  startedAt: string;
  completedAt?: string | undefined;
  durationMs?: number | undefined;

  // Step results
  stepResults: {
    stepNumber: number;
    status: 'pass' | 'fail' | 'pending' | 'error' | 'skipped';
    error?: string | undefined;
    durationMs?: number | undefined;
  }[];

  // Error details
  errorMessage?: string | undefined;
  errorStack?: string | undefined;
  screenshot?: string | undefined;

  // For scenario outlines
  exampleRow?: Record<string, string> | undefined;

  createdAt: string;
}

export type StepType = 'given' | 'when' | 'then';

export interface StepDefinition {
  id: string;
  projectId: string;
  stepType: StepType;
  pattern: string; // "a user {name:string} exists"
  regexPattern?: string | undefined; // Compiled regex
  implementationPath?: string | undefined;
  implementationCode?: string | undefined;

  // Parameters extracted from pattern
  parameters: {
    name: string;
    type: 'string' | 'number' | 'table' | 'docString';
    description?: string | undefined;
  }[];

  documentation?: string | undefined;
  examples?: string[] | undefined;

  // Usage stats
  usageCount: number;
  lastUsedAt?: string | undefined;

  metadata?: Record<string, unknown> | undefined;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface FeatureStats {
  projectId: string;
  totalFeatures: number;
  totalScenarios: number;
  byStatus: Record<string, number>;
  passRate: number;
  coverage: {
    requirementsCovered: number;
    totalRequirements: number;
    percentage: number;
  };
}

export interface FeatureActivity {
  id: string;
  featureId: string;
  activityType: string;
  fromValue?: string | undefined;
  toValue?: string | undefined;
  description?: string | undefined;
  performedBy?: string | undefined;
  createdAt: string;
}

// =============================================================================
// Specification Dashboard Types
// =============================================================================

export interface SpecificationSummary {
  projectId: string;

  adrs: {
    total: number;
    accepted: number;
    proposed: number;
    averageCompliance: number;
  };

  contracts: {
    total: number;
    active: number;
    verified: number;
    violated: number;
  };

  features: {
    total: number;
    scenarios: number;
    passRate: number;
    coverage: number;
  };

  // Combined Health Score
  healthScore: number; // 0-100
  healthDetails: {
    category: string;
    score: number;
    issues: string[];
  }[];
}

// =============================================================================
// Traceability Types for Specifications
// =============================================================================

export interface SpecificationLink {
  id: string;
  projectId: string;
  sourceType: 'adr' | 'contract' | 'feature' | 'scenario';
  sourceId: string;
  targetType: 'item' | 'adr' | 'contract' | 'feature' | 'scenario' | 'test_case';
  targetId: string;
  linkType: 'implements' | 'verifies' | 'depends_on' | 'supersedes' | 'related_to';
  description?: string | undefined;
  createdAt: string;
}

export interface SpecificationGraph {
  nodes: {
    id: string;
    type: 'adr' | 'contract' | 'feature' | 'scenario' | 'requirement' | 'test';
    label: string;
    status: string;
    metadata?: Record<string, unknown> | undefined;
  }[];
  edges: {
    id: string;
    source: string;
    target: string;
    type: string;
    label?: string | undefined;
  }[];
}
