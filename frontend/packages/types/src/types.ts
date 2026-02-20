// Core domain types matching TraceRTM backend

// Import multi-dimensional traceability types
import type { CodeReference, DocReference, ItemDimensions } from './canonical';

export type ViewType =
  | 'FEATURE'
  | 'feature'
  | 'CODE'
  | 'code'
  | 'TEST'
  | 'test'
  | 'API'
  | 'api'
  | 'DATABASE'
  | 'database'
  | 'WIREFRAME'
  | 'wireframe'
  | 'DOCUMENTATION'
  | 'documentation'
  | 'DEPLOYMENT'
  | 'deployment'
  | 'architecture'
  | 'configuration'
  | 'dataflow'
  | 'dependency'
  | 'domain'
  | 'infrastructure'
  | 'journey'
  | 'monitoring'
  | 'performance'
  | 'security';

export type ItemStatus = 'todo' | 'in_progress' | 'done' | 'blocked' | 'cancelled';

export type Priority = 'low' | 'medium' | 'high' | 'critical';

export type LinkType =
  // Original link types
  | 'implements'
  | 'tests'
  | 'depends_on'
  | 'related_to'
  | 'blocks'
  | 'parent_of'
  // Multi-dimensional traceability link types
  | 'same_as' // Equivalence: same concept in different views
  | 'represents' // Code/UI represents a requirement
  | 'manifests_as' // Abstract concept manifests as concrete item
  | 'documents' // Documentation describes an item
  | 'mentions' // Documentation mentions an item
  | 'calls' // Code calls another code entity
  | 'imports' // Code imports another module
  | 'derives_from' // Derived requirement/item
  | 'alternative_to' // Alternative approach
  | 'conflicts_with' // Conflicting items
  | 'supersedes' // Newer version supersedes older
  | 'validates' // Test validates requirement
  | 'traces_to'; // General traceability link

export interface Project {
  id: string;
  name: string;
  description?: string | undefined;
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, unknown> | undefined;
}

export interface Item {
  id: string;
  projectId: string;
  view: ViewType;
  type: string;
  title: string;
  description?: string | undefined;
  status: ItemStatus;
  priority: Priority;
  parentId?: string | undefined;
  owner?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
  version: number;
  createdAt: string;
  updatedAt: string;

  // Multi-Dimensional Traceability Extensions
  // Canonical concept this item represents (if any)
  canonicalId?: string | undefined;

  // Dimensions (orthogonal cross-cutting concerns)
  dimensions?: ItemDimensions | undefined;

  // Code reference (if this item is linked to code)
  codeRef?: CodeReference | undefined;

  // Documentation reference (if this item is linked to docs)
  docRef?: DocReference | undefined;

  // Perspective this item primarily belongs to
  perspective?: string | undefined;

  // Equivalence links to other items
  equivalentItemIds?: string[] | undefined;
}

// =============================================================================
// Type-Aware Node System - Discriminated Unions
// =============================================================================

/**
 * Requirement-specific properties (imported from specification.ts)
 */
export interface RequirementItem extends Item {
  type: 'requirement';
  // Specification-specific fields
  adrId?: string | undefined; // Link to ADR
  contractId?: string | undefined; // Link to Contract
  qualityMetrics?: {
    ambiguityScore: number;
    completenessScore: number;
    smells: string[];
  };
}

/**
 * Test-specific properties
 */
export interface TestItem extends Item {
  type: 'test' | 'test_case' | 'test_suite';
  testType?: TestCaseType | undefined;
  automationStatus?: AutomationStatus | undefined;
  testSteps?: TestStep[] | undefined;
  expectedResult?: string | undefined;
  lastExecutionResult?: TestResultStatus | undefined;
}

/**
 * Epic-specific properties
 */
export interface EpicItem extends Item {
  type: 'epic';
  acceptanceCriteria?: string[] | undefined;
  businessValue?: string | undefined;
  targetRelease?: string | undefined;
}

/**
 * User Story-specific properties
 */
export interface UserStoryItem extends Item {
  type: 'user_story' | 'story';
  asA?: string | undefined; // As a [role]
  iWant?: string | undefined; // I want [capability]
  soThat?: string | undefined; // So that [benefit]
  acceptanceCriteria?: string[] | undefined;
  storyPoints?: number | undefined;
}

/**
 * Task-specific properties
 */
export interface TaskItem extends Item {
  type: 'task';
  estimatedHours?: number | undefined;
  actualHours?: number | undefined;
  assignee?: string | undefined;
  dueDate?: string | undefined;
}

/**
 * Defect/Bug-specific properties
 */
export interface DefectItem extends Item {
  type: 'bug' | 'defect';
  severity?: 'critical' | 'high' | 'medium' | 'low' | undefined;
  reproducible?: boolean | undefined;
  stepsToReproduce?: string[] | undefined;
  environment?: string | undefined;
  foundInVersion?: string | undefined;
  fixedInVersion?: string | undefined;
}

/**
 * Generic item for other types
 */
export interface GenericItem extends Item {
  type: string; // Any other type not covered above
}

/**
 * Discriminated union of all typed items
 */
export type TypedItem =
  | RequirementItem
  | TestItem
  | EpicItem
  | UserStoryItem
  | TaskItem
  | DefectItem
  | GenericItem;

// =============================================================================
// Type Guards
// =============================================================================

export function isRequirementItem(item: Item): item is RequirementItem {
  return item.type === 'requirement';
}

export function isTestItem(item: Item): item is TestItem {
  return item.type === 'test' || item.type === 'test_case' || item.type === 'test_suite';
}

export function isEpicItem(item: Item): item is EpicItem {
  return item.type === 'epic';
}

export function isUserStoryItem(item: Item): item is UserStoryItem {
  return item.type === 'user_story' || item.type === 'story';
}

export function isTaskItem(item: Item): item is TaskItem {
  return item.type === 'task';
}

export function isDefectItem(item: Item): item is DefectItem {
  return item.type === 'bug' || item.type === 'defect';
}

/**
 * Type guard for items that have specification-related properties
 */
export function hasSpec(item: Item): item is RequirementItem {
  return isRequirementItem(item);
}

export interface Link {
  id: string;
  projectId: string;
  sourceId: string;
  targetId: string;
  type: LinkType;
  description?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
  createdAt: string;
  updatedAt: string;
  version: number;

  // Multi-dimensional traceability extensions
  // Confidence score for inferred links (0-1)
  confidence?: number | undefined;

  // How this link was detected/created
  provenance?: LinkProvenance | undefined;

  // For equivalence links: the canonical concept they share
  canonicalId?: string | undefined;

  // User confirmation status
  status?: 'suggested' | 'confirmed' | 'rejected' | 'auto' | undefined;
}

/**
 * How a link was created/detected
 */
export type LinkProvenance =
  | 'manual' // User created
  | 'imported' // Imported from external system
  | 'inferred_naming' // Inferred from naming patterns
  | 'inferred_semantic' // Inferred from semantic similarity
  | 'inferred_structural' // Inferred from code structure
  | 'inferred_api' // Inferred from API contracts
  | 'annotation'; // From code annotations

export interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'idle' | 'offline';
  lastSeen: string;
}

export interface Mutation {
  id: string;
  agentId: string;
  itemId: string;
  operation: 'create' | 'update' | 'delete';
  data: Record<string, unknown>;
  timestamp: string;
  synced: boolean;
}

// Problem Management Types
export type ProblemStatus =
  | 'open'
  | 'in_investigation'
  | 'pending_workaround'
  | 'known_error'
  | 'awaiting_fix'
  | 'closed';

export type ResolutionType =
  | 'permanent_fix'
  | 'workaround_only'
  | 'cannot_reproduce'
  | 'deferred'
  | 'by_design';

export type ImpactLevel = 'critical' | 'high' | 'medium' | 'low';

export type RCAMethod = 'five_whys' | 'fishbone' | 'kepner_tregoe' | 'fmea' | 'pareto' | 'other';

export type RootCauseCategory = 'systematic' | 'human' | 'environmental' | 'process' | 'technology';

export interface Problem {
  id: string;
  problemNumber: string;
  projectId: string;
  title: string;
  description?: string | undefined;
  status: ProblemStatus;
  resolutionType?: ResolutionType | undefined;
  category?: string | undefined;
  subCategory?: string | undefined;
  tags?: string[] | undefined;
  impactLevel: ImpactLevel;
  urgency: ImpactLevel;
  priority: ImpactLevel;
  affectedSystems?: string[] | undefined;
  affectedUsersEstimated?: number | undefined;
  businessImpactDescription?: string | undefined;
  rcaPerformed: boolean;
  rcaMethod?: RCAMethod | undefined;
  rcaNotes?: string | undefined;
  rcaData?: Record<string, unknown> | undefined;
  rootCauseIdentified: boolean;
  rootCauseDescription?: string | undefined;
  rootCauseCategory?: RootCauseCategory | undefined;
  rootCauseConfidence?: 'high' | 'medium' | 'low' | undefined;
  rcaCompletedAt?: string | undefined;
  rcaCompletedBy?: string | undefined;
  workaroundAvailable: boolean;
  workaroundDescription?: string | undefined;
  workaroundEffectiveness?: 'permanent_fix' | 'partial' | 'temporary' | undefined;
  permanentFixAvailable: boolean;
  permanentFixDescription?: string | undefined;
  permanentFixImplementedAt?: string | undefined;
  permanentFixChangeId?: string | undefined;
  knownErrorId?: string | undefined;
  knowledgeArticleId?: string | undefined;
  assignedTo?: string | undefined;
  assignedTeam?: string | undefined;
  owner?: string | undefined;
  closedBy?: string | undefined;
  closedAt?: string | undefined;
  closureNotes?: string | undefined;
  targetResolutionDate?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface ProblemActivity {
  id: string;
  problemId: string;
  activityType: string;
  fromValue?: string | undefined;
  toValue?: string | undefined;
  description?: string | undefined;
  performedBy?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
  createdAt: string;
}

// Process Management Types
export type ProcessStatus = 'draft' | 'active' | 'deprecated' | 'retired' | 'archived';

export type ProcessCategory =
  | 'operational'
  | 'support'
  | 'management'
  | 'development'
  | 'integration'
  | 'compliance'
  | 'other';

export interface ProcessStage {
  id: string;
  name: string;
  description?: string | undefined;
  order: number;
  required?: boolean | undefined;
  estimatedDurationMinutes?: number | undefined;
  assignedRole?: string | undefined;
}

export interface ProcessSwimlane {
  id: string;
  name: string;
  role?: string | undefined;
  description?: string | undefined;
}

export interface ProcessInput {
  name: string;
  type: string;
  required?: boolean | undefined;
  description?: string | undefined;
}

export interface ProcessOutput {
  name: string;
  type: string;
  description?: string | undefined;
}

export interface ProcessTrigger {
  type: string;
  name: string;
  description?: string | undefined;
  condition?: string | undefined;
}

export interface Process {
  id: string;
  processNumber: string;
  projectId: string;
  name: string;
  description?: string | undefined;
  purpose?: string | undefined;
  status: ProcessStatus;
  category?: ProcessCategory | undefined;
  tags?: string[] | undefined;
  versionNumber: number;
  isActiveVersion: boolean;
  parentVersionId?: string | undefined;
  versionNotes?: string | undefined;
  stages?: ProcessStage[] | undefined;
  swimlanes?: ProcessSwimlane[] | undefined;
  inputs?: ProcessInput[] | undefined;
  outputs?: ProcessOutput[] | undefined;
  triggers?: ProcessTrigger[] | undefined;
  exitCriteria?: string[] | undefined;
  bpmnXml?: string | undefined;
  bpmnDiagramUrl?: string | undefined;
  owner?: string | undefined;
  responsibleTeam?: string | undefined;
  expectedDurationHours?: number | undefined;
  slaHours?: number | undefined;
  activatedAt?: string | undefined;
  activatedBy?: string | undefined;
  deprecatedAt?: string | undefined;
  deprecatedBy?: string | undefined;
  deprecationReason?: string | undefined;
  relatedProcessIds?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export type ExecutionStatus = 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled';

export interface ProcessExecution {
  id: string;
  processId: string;
  executionNumber: string;
  status: ExecutionStatus;
  currentStageId?: string | undefined;
  completedStages?: string[] | undefined;
  startedAt?: string | undefined;
  completedAt?: string | undefined;
  initiatedBy?: string | undefined;
  completedBy?: string | undefined;
  triggerItemId?: string | undefined;
  contextData?: Record<string, unknown> | undefined;
  resultSummary?: string | undefined;
  outputItemIds?: string[] | undefined;
  createdAt: string;
  updatedAt: string;
}

// Quality Engineering (Test Case) Types
export type TestCaseStatus = 'draft' | 'review' | 'approved' | 'deprecated' | 'archived';

export type TestCaseType =
  | 'functional'
  | 'integration'
  | 'unit'
  | 'e2e'
  | 'performance'
  | 'security'
  | 'accessibility'
  | 'regression'
  | 'smoke'
  | 'exploratory';

export type TestCasePriority = 'critical' | 'high' | 'medium' | 'low';

export type AutomationStatus = 'not_automated' | 'in_progress' | 'automated' | 'cannot_automate';

export type TestResultStatus = 'passed' | 'failed' | 'skipped' | 'blocked' | 'error';

export interface TestStep {
  stepNumber: number;
  action: string;
  expectedResult?: string | undefined;
  testData?: string | undefined;
}

export interface TestCase {
  id: string;
  testCaseNumber: string;
  projectId: string;
  title: string;
  description?: string | undefined;
  objective?: string | undefined;
  status: TestCaseStatus;
  testType: TestCaseType;
  priority: TestCasePriority;
  category?: string | undefined;
  tags?: string[] | undefined;
  preconditions?: string | undefined;
  testSteps?: TestStep[] | undefined;
  expectedResult?: string | undefined;
  postconditions?: string | undefined;
  testData?: Record<string, unknown> | undefined;
  automationStatus: AutomationStatus;
  automationScriptPath?: string | undefined;
  automationFramework?: string | undefined;
  automationNotes?: string | undefined;
  estimatedDurationMinutes?: number | undefined;
  createdBy?: string | undefined;
  assignedTo?: string | undefined;
  reviewedBy?: string | undefined;
  approvedBy?: string | undefined;
  reviewedAt?: string | undefined;
  approvedAt?: string | undefined;
  deprecatedAt?: string | undefined;
  deprecationReason?: string | undefined;
  lastExecutedAt?: string | undefined;
  lastExecutionResult?: TestResultStatus | undefined;
  totalExecutions: number;
  passCount: number;
  failCount: number;
  metadata?: Record<string, unknown> | undefined;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface TestCaseActivity {
  id: string;
  testCaseId: string;
  activityType: string;
  fromValue?: string | undefined;
  toValue?: string | undefined;
  description?: string | undefined;
  performedBy?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
  createdAt: string;
}

export interface TestCaseStats {
  projectId: string;
  total: number;
  byStatus: Record<string, number>;
  byType: Record<string, number>;
  byPriority: Record<string, number>;
  byAutomationStatus: Record<string, number>;
  executionSummary: {
    totalRuns: number;
    totalPassed: number;
    totalFailed: number;
  };
}

// Test Suite Types
export type TestSuiteStatus = 'draft' | 'active' | 'deprecated' | 'archived';

export interface TestSuite {
  id: string;
  suiteNumber: string;
  projectId: string;
  name: string;
  description?: string | undefined;
  objective?: string | undefined;
  status: TestSuiteStatus;
  parentId?: string | undefined;
  orderIndex: number;
  category?: string | undefined;
  tags?: string[] | undefined;
  isParallelExecution: boolean;
  estimatedDurationMinutes?: number | undefined;
  requiredEnvironment?: string | undefined;
  environmentVariables?: Record<string, string> | undefined;
  setupInstructions?: string | undefined;
  teardownInstructions?: string | undefined;
  owner?: string | undefined;
  responsibleTeam?: string | undefined;
  totalTestCases: number;
  automatedCount: number;
  manualCount: number;
  passRate?: number | undefined;
  lastRunAt?: string | undefined;
  lastRunStatus?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface TestSuiteTestCase {
  id: string;
  suiteId: string;
  testCaseId: string;
  orderIndex: number;
  isMandatory: boolean;
  skipReason?: string | undefined;
  customParameters?: Record<string, unknown> | undefined;
  createdAt: string;
}

export interface TestSuiteActivity {
  id: string;
  suiteId: string;
  activityType: string;
  fromValue?: string | undefined;
  toValue?: string | undefined;
  description?: string | undefined;
  performedBy?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
  createdAt: string;
}

export interface TestSuiteStats {
  projectId: string;
  total: number;
  byStatus: Record<string, number>;
  byCategory: Record<string, number>;
  totalTestCases: number;
  automatedTestCases: number;
}

// Test Run Types
export type TestRunStatus = 'pending' | 'running' | 'passed' | 'failed' | 'blocked' | 'cancelled';

export type TestRunType = 'manual' | 'automated' | 'ci_cd' | 'scheduled';

export interface TestRun {
  id: string;
  runNumber: string;
  projectId: string;
  suiteId?: string | undefined;
  name: string;
  description?: string | undefined;
  status: TestRunStatus;
  runType: TestRunType;
  environment?: string | undefined;
  buildNumber?: string | undefined;
  buildUrl?: string | undefined;
  branch?: string | undefined;
  commitSha?: string | undefined;
  scheduledAt?: string | undefined;
  startedAt?: string | undefined;
  completedAt?: string | undefined;
  durationSeconds?: number | undefined;
  initiatedBy?: string | undefined;
  executedBy?: string | undefined;
  totalTests: number;
  passedCount: number;
  failedCount: number;
  skippedCount: number;
  blockedCount: number;
  errorCount: number;
  passRate?: number | undefined;
  notes?: string | undefined;
  failureSummary?: string | undefined;
  tags?: string[] | undefined;
  externalRunId?: string | undefined;
  webhookId?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface TestResult {
  id: string;
  runId: string;
  testCaseId: string;
  status: TestResultStatus;
  startedAt?: string | undefined;
  completedAt?: string | undefined;
  durationSeconds?: number | undefined;
  executedBy?: string | undefined;
  actualResult?: string | undefined;
  failureReason?: string | undefined;
  errorMessage?: string | undefined;
  stackTrace?: string | undefined;
  screenshots?: string[] | undefined;
  logsUrl?: string | undefined;
  attachments?: string[] | undefined;
  stepResults?:
    | Array<{
        stepNumber: number;
        status: TestResultStatus;
        actualResult?: string | undefined;
        notes?: string | undefined;
      }>
    | undefined;
  linkedDefectIds?: string[] | undefined;
  createdDefectId?: string | undefined;
  retryCount: number;
  isFlaky: boolean;
  notes?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
  createdAt: string;
  updatedAt: string;
}

export interface TestRunActivity {
  id: string;
  runId: string;
  activityType: string;
  fromValue?: string | undefined;
  toValue?: string | undefined;
  description?: string | undefined;
  performedBy?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
  createdAt: string;
}

export interface TestRunStats {
  projectId: string;
  totalRuns: number;
  byStatus: Record<string, number>;
  byType: Record<string, number>;
  averagePassRate: number;
  averageDurationSeconds: number;
  recentRuns: TestRun[];
}

// Test Coverage Types
export type CoverageType = 'direct' | 'partial' | 'indirect' | 'regression';
export type CoverageStatus = 'active' | 'deprecated' | 'needs_review';

export interface TestCoverage {
  id: string;
  projectId: string;
  testCaseId: string;
  requirementId: string;
  coverageType: CoverageType;
  status: CoverageStatus;
  coveragePercentage?: number | undefined;
  rationale?: string | undefined;
  notes?: string | undefined;
  lastVerifiedAt?: string | undefined;
  verifiedBy?: string | undefined;
  lastTestResult?: string | undefined;
  lastTestedAt?: string | undefined;
  createdBy?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface CoverageActivity {
  id: string;
  coverageId: string;
  activityType: string;
  fromValue?: string | undefined;
  toValue?: string | undefined;
  description?: string | undefined;
  performedBy?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
  createdAt: string;
}

export interface TraceabilityMatrixItem {
  requirementId: string;
  requirementTitle: string;
  requirementView: string;
  requirementStatus: string;
  isCovered: boolean;
  testCount: number;
  testCases: Array<{
    testCaseId: string;
    coverageType: CoverageType;
    coveragePercentage?: number | undefined;
    lastTestResult?: string | undefined;
    lastTestedAt?: string | undefined;
  }>;
  overallStatus: string;
}

export interface TraceabilityMatrix {
  projectId: string;
  totalRequirements: number;
  coveredRequirements: number;
  uncoveredRequirements: number;
  coveragePercentage: number;
  matrix: TraceabilityMatrixItem[];
}

export interface CoverageGap {
  requirementId: string;
  requirementTitle: string;
  requirementView: string;
  requirementStatus: string;
  priority?: string | undefined;
}

export interface CoverageGapsResponse {
  projectId: string;
  totalRequirements: number;
  uncoveredCount: number;
  coveragePercentage: number;
  gaps: CoverageGap[];
}

export interface CoverageStats {
  projectId: string;
  totalMappings: number;
  byType: Record<string, number>;
  byStatus: Record<string, number>;
  uniqueTestCases: number;
  uniqueRequirements: number;
}

// Webhook Integration Types
export type WebhookProvider =
  | 'github_actions'
  | 'gitlab_ci'
  | 'jenkins'
  | 'azure_devops'
  | 'circleci'
  | 'travis_ci'
  | 'custom';

export type WebhookStatus = 'active' | 'paused' | 'disabled';

export interface WebhookIntegration {
  id: string;
  projectId: string;
  name: string;
  description?: string | undefined;
  provider: WebhookProvider;
  status: WebhookStatus;
  webhookSecret: string;
  apiKey?: string | undefined;
  enabledEvents?: string[] | undefined;
  eventFilters?: Record<string, unknown> | undefined;
  callbackUrl?: string | undefined;
  callbackHeaders?: Record<string, string> | undefined;
  defaultSuiteId?: string | undefined;
  rateLimitPerMinute: number;
  autoCreateRun: boolean;
  autoCompleteRun: boolean;
  verifySignatures: boolean;
  // Statistics
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  lastRequestAt?: string | undefined;
  lastSuccessAt?: string | undefined;
  lastFailureAt?: string | undefined;
  lastErrorMessage?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface WebhookLog {
  id: string;
  webhookId: string;
  requestId: string;
  eventType?: string | undefined;
  httpMethod: string;
  sourceIp?: string | undefined;
  userAgent?: string | undefined;
  requestHeaders?: Record<string, unknown> | undefined;
  requestBodyPreview?: string | undefined;
  payloadSizeBytes?: number | undefined;
  success: boolean;
  statusCode: number;
  errorMessage?: string | undefined;
  processingTimeMs?: number | undefined;
  testRunId?: string | undefined;
  resultsSubmitted: number;
  createdAt: string;
}

export interface WebhookStats {
  projectId: string;
  total: number;
  byStatus: Record<string, number>;
  byProvider: Record<string, number>;
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
}

// External Integration Types
export type IntegrationProvider = 'github' | 'github_projects' | 'linear';

export type CredentialType = 'oauth' | 'pat' | 'api_key';

export type CredentialStatus = 'active' | 'expired' | 'revoked' | 'invalid' | 'pending_reauth';

export type MappingDirection = 'pull' | 'push' | 'bidirectional';

export type MappingStatus = 'active' | 'paused' | 'error' | 'pending';

export type SyncQueueStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

export type ConflictResolutionStrategy =
  | 'local_wins'
  | 'external_wins'
  | 'manual'
  | 'merge'
  | 'skip';

export interface IntegrationCredential {
  id: string;
  projectId?: string | undefined;
  provider: IntegrationProvider;
  credentialType: CredentialType;
  status: CredentialStatus;
  scopes: string[];
  providerUserId?: string | undefined;
  providerMetadata?: Record<string, unknown> | undefined;
  lastValidatedAt?: string | undefined;
  validationError?: string | undefined;
  expiresAt?: string | undefined;
  createdAt: string;
  updatedAt: string;
}

export interface IntegrationMapping {
  id: string;
  credentialId: string;
  provider: IntegrationProvider;
  direction: MappingDirection;
  localItemId: string;
  localItemType: string;
  externalId: string;
  externalType: string;
  externalUrl?: string | undefined;
  externalKey?: string | undefined;
  mappingMetadata?: Record<string, unknown> | undefined;
  status: MappingStatus;
  syncEnabled: boolean;
  lastSyncedAt?: string | undefined;
  lastSyncStatus?: string | undefined;
  lastSyncError?: string | undefined;
  fieldMappings?: Record<string, string> | undefined;
  fieldResolutionRules?: Record<string, ConflictResolutionStrategy> | undefined;
  localVersion?: number | undefined;
  externalVersion?: string | undefined;
  createdAt: string;
  updatedAt: string;
}

export interface SyncQueueItem {
  id: string;
  credentialId?: string | undefined;
  mappingId?: string | undefined;
  provider: IntegrationProvider;
  eventType: string;
  direction: string;
  status: SyncQueueStatus;
  priority: number;
  retryCount: number;
  maxRetries: number;
  errorMessage?: string | undefined;
  scheduledAt?: string | undefined;
  startedAt?: string | undefined;
  completedAt?: string | undefined;
  createdAt: string;
}

export interface SyncLog {
  id: string;
  credentialId?: string | undefined;
  mappingId?: string | undefined;
  provider: IntegrationProvider;
  eventType: string;
  direction: string;
  status: string;
  itemsProcessed: number;
  itemsFailed: number;
  itemsSkipped: number;
  errorMessage?: string | undefined;
  startedAt?: string | undefined;
  completedAt?: string | undefined;
  durationMs?: number | undefined;
  createdAt: string;
}

export interface WorkflowRun {
  id: string;
  projectId?: string | undefined;
  graphId?: string | undefined;
  workflowName: string;
  status: string;
  externalRunId?: string | undefined;
  payload?: Record<string, unknown> | undefined;
  result?: Record<string, unknown> | undefined;
  errorMessage?: string | undefined;
  createdByUserId?: string | undefined;
  startedAt?: string | undefined;
  completedAt?: string | undefined;
  createdAt?: string | undefined;
  updatedAt?: string | undefined;
}

export interface WorkflowSchedule {
  id?: string | undefined;
  cronName?: string | undefined;
  expression?: string | undefined;
  workflowName?: string | undefined;
  additionalMetadata?: Record<string, unknown> | undefined;
  [key: string]: unknown;
}

export interface SyncConflict {
  id: string;
  mappingId: string;
  provider: IntegrationProvider;
  conflictType: string;
  fieldName?: string | undefined;
  localValue?: unknown | undefined;
  externalValue?: unknown | undefined;
  localModifiedAt?: string | undefined;
  externalModifiedAt?: string | undefined;
  status: 'pending' | 'resolved' | 'skipped';
  resolution?: string | undefined;
  resolvedValue?: unknown | undefined;
  resolvedBy?: string | undefined;
  resolvedAt?: string | undefined;
  createdAt: string;
}

export interface IntegrationStats {
  projectId: string;
  providers: Array<{
    provider: IntegrationProvider;
    status: CredentialStatus;
    credentialType: CredentialType;
  }>;
  mappings: {
    total: number;
    active: number;
    byProvider: Record<string, number>;
  };
  sync: {
    queuePending: number;
    recentSyncs: number;
    successRate: number;
  };
  conflicts: {
    pending: number;
    resolved: number;
  };
}

export interface SyncStatusSummary {
  projectId: string;
  queue: {
    pending: number;
    processing: number;
    failed: number;
    completed: number;
  };
  recentSyncs: SyncLog[];
  providers: Array<{
    provider: IntegrationProvider;
    status: CredentialStatus;
    lastValidated?: string | undefined;
  }>;
}

// GitHub-specific types
export interface GitHubRepo {
  id: number;
  name: string;
  fullName: string;
  description?: string | undefined;
  htmlUrl: string;
  private: boolean;
  owner: {
    login: string;
    avatarUrl: string;
  };
  defaultBranch: string;
  updatedAt?: string | undefined;
}

export interface GitHubIssue {
  id: number;
  number: number;
  title: string;
  state: string;
  htmlUrl: string;
  body?: string | undefined;
  user: {
    login: string;
    avatarUrl: string;
  };
  labels: string[];
  assignees: string[];
  createdAt: string;
  updatedAt: string;
}

export interface GitHubPullRequest {
  id: number;
  number: number;
  title: string;
  state: string;
  htmlUrl: string;
  body?: string | undefined;
  user: {
    login: string;
    avatarUrl: string;
  };
  labels: string[];
  assignees: string[];
  draft: boolean;
  merged: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface GitHubProject {
  id: string;
  title: string;
  description?: string | undefined;
  url: string;
  closed: boolean;
  public: boolean;
  createdAt?: string | undefined;
  updatedAt?: string | undefined;
}

// Linear-specific types
export interface LinearTeam {
  id: string;
  name: string;
  key: string;
  description?: string | undefined;
  icon?: string | undefined;
  color?: string | undefined;
}

export interface LinearIssue {
  id: string;
  identifier: string;
  title: string;
  description?: string | undefined;
  state?: string | undefined;
  priority?: number | undefined;
  url: string;
  assignee?: string | undefined;
  labels: string[];
  createdAt?: string | undefined;
  updatedAt?: string | undefined;
}

export interface LinearProject {
  id: string;
  name: string;
  description?: string | undefined;
  state?: string | undefined;
  progress?: number | undefined;
  url: string;
  startDate?: string | undefined;
  targetDate?: string | undefined;
}

// API Response types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown> | undefined;
}

// Re-export multi-dimensional traceability types
export * from './canonical';
export * from './component-library';
export * from './entity-hierarchy';
// Temporal dimension types
export * from './progress';
// Re-export specification types
export * from './specification';
// Re-export temporal types
export * from './temporal';
export * from './ui-entities';
