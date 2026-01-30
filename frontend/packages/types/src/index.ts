// Core domain types matching TraceRTM backend

// Import multi-dimensional traceability types
import type {
	ItemDimensions,
	CodeReference,
	DocReference,
} from "./canonical";

export type ViewType =
	| "FEATURE"
	| "feature"
	| "CODE"
	| "code"
	| "TEST"
	| "test"
	| "API"
	| "api"
	| "DATABASE"
	| "database"
	| "WIREFRAME"
	| "wireframe"
	| "DOCUMENTATION"
	| "documentation"
	| "DEPLOYMENT"
	| "deployment"
	| "architecture"
	| "configuration"
	| "dataflow"
	| "dependency"
	| "domain"
	| "infrastructure"
	| "journey"
	| "monitoring"
	| "performance"
	| "security";

export type ItemStatus =
	| "todo"
	| "in_progress"
	| "done"
	| "blocked"
	| "cancelled";

export type Priority = "low" | "medium" | "high" | "critical";

export type LinkType =
	// Original link types
	| "implements"
	| "tests"
	| "depends_on"
	| "related_to"
	| "blocks"
	| "parent_of"
	// Multi-dimensional traceability link types
	| "same_as"           // Equivalence: same concept in different views
	| "represents"        // Code/UI represents a requirement
	| "manifests_as"      // Abstract concept manifests as concrete item
	| "documents"         // Documentation describes an item
	| "mentions"          // Documentation mentions an item
	| "calls"             // Code calls another code entity
	| "imports"           // Code imports another module
	| "derives_from"      // Derived requirement/item
	| "alternative_to"    // Alternative approach
	| "conflicts_with"    // Conflicting items
	| "supersedes"        // Newer version supersedes older
	| "validates"         // Test validates requirement
	| "traces_to";        // General traceability link

export interface Project {
	id: string;
	name: string;
	description?: string;
	createdAt: string;
	updatedAt: string;
	metadata?: Record<string, unknown>;
}

export interface Item {
	id: string;
	projectId: string;
	view: ViewType;
	type: string;
	title: string;
	description?: string;
	status: ItemStatus;
	priority: Priority;
	parentId?: string;
	owner?: string;
	metadata?: Record<string, unknown>;
	version: number;
	createdAt: string;
	updatedAt: string;

	// Multi-Dimensional Traceability Extensions
	// Canonical concept this item represents (if any)
	canonicalId?: string;

	// Dimensions (orthogonal cross-cutting concerns)
	dimensions?: ItemDimensions;

	// Code reference (if this item is linked to code)
	codeRef?: CodeReference;

	// Documentation reference (if this item is linked to docs)
	docRef?: DocReference;

	// Perspective this item primarily belongs to
	perspective?: string;

	// Equivalence links to other items
	equivalentItemIds?: string[];
}

export interface Link {
	id: string;
	projectId: string;
	sourceId: string;
	targetId: string;
	type: LinkType;
	description?: string;
	metadata?: Record<string, unknown>;
	createdAt: string;

	// Multi-dimensional traceability extensions
	// Confidence score for inferred links (0-1)
	confidence?: number;

	// How this link was detected/created
	provenance?: LinkProvenance;

	// For equivalence links: the canonical concept they share
	canonicalId?: string;

	// User confirmation status
	status?: "suggested" | "confirmed" | "rejected" | "auto";
}

/**
 * How a link was created/detected
 */
export type LinkProvenance =
	| "manual"              // User created
	| "imported"            // Imported from external system
	| "inferred_naming"     // Inferred from naming patterns
	| "inferred_semantic"   // Inferred from semantic similarity
	| "inferred_structural" // Inferred from code structure
	| "inferred_api"        // Inferred from API contracts
	| "annotation";         // From code annotations

export interface Agent {
	id: string;
	name: string;
	type: string;
	status: "active" | "idle" | "offline";
	lastSeen: string;
}

export interface Mutation {
	id: string;
	agentId: string;
	itemId: string;
	operation: "create" | "update" | "delete";
	data: Record<string, unknown>;
	timestamp: string;
	synced: boolean;
}

// Problem Management Types
export type ProblemStatus =
	| "open"
	| "in_investigation"
	| "pending_workaround"
	| "known_error"
	| "awaiting_fix"
	| "closed";

export type ResolutionType =
	| "permanent_fix"
	| "workaround_only"
	| "cannot_reproduce"
	| "deferred"
	| "by_design";

export type ImpactLevel = "critical" | "high" | "medium" | "low";

export type RCAMethod =
	| "five_whys"
	| "fishbone"
	| "kepner_tregoe"
	| "fmea"
	| "pareto"
	| "other";

export type RootCauseCategory =
	| "systematic"
	| "human"
	| "environmental"
	| "process"
	| "technology";

export interface Problem {
	id: string;
	problemNumber: string;
	projectId: string;
	title: string;
	description?: string;
	status: ProblemStatus;
	resolutionType?: ResolutionType;
	category?: string;
	subCategory?: string;
	tags?: string[];
	impactLevel: ImpactLevel;
	urgency: ImpactLevel;
	priority: ImpactLevel;
	affectedSystems?: string[];
	affectedUsersEstimated?: number;
	businessImpactDescription?: string;
	rcaPerformed: boolean;
	rcaMethod?: RCAMethod;
	rcaNotes?: string;
	rcaData?: Record<string, unknown>;
	rootCauseIdentified: boolean;
	rootCauseDescription?: string;
	rootCauseCategory?: RootCauseCategory;
	rootCauseConfidence?: "high" | "medium" | "low";
	rcaCompletedAt?: string;
	rcaCompletedBy?: string;
	workaroundAvailable: boolean;
	workaroundDescription?: string;
	workaroundEffectiveness?: "permanent_fix" | "partial" | "temporary";
	permanentFixAvailable: boolean;
	permanentFixDescription?: string;
	permanentFixImplementedAt?: string;
	permanentFixChangeId?: string;
	knownErrorId?: string;
	knowledgeArticleId?: string;
	assignedTo?: string;
	assignedTeam?: string;
	owner?: string;
	closedBy?: string;
	closedAt?: string;
	closureNotes?: string;
	targetResolutionDate?: string;
	metadata?: Record<string, unknown>;
	version: number;
	createdAt: string;
	updatedAt: string;
}

export interface ProblemActivity {
	id: string;
	problemId: string;
	activityType: string;
	fromValue?: string;
	toValue?: string;
	description?: string;
	performedBy?: string;
	metadata?: Record<string, unknown>;
	createdAt: string;
}

// Process Management Types
export type ProcessStatus =
	| "draft"
	| "active"
	| "deprecated"
	| "retired"
	| "archived";

export type ProcessCategory =
	| "operational"
	| "support"
	| "management"
	| "development"
	| "integration"
	| "compliance"
	| "other";

export interface ProcessStage {
	id: string;
	name: string;
	description?: string;
	order: number;
	required?: boolean;
	estimatedDurationMinutes?: number;
	assignedRole?: string;
}

export interface ProcessSwimlane {
	id: string;
	name: string;
	role?: string;
	description?: string;
}

export interface ProcessInput {
	name: string;
	type: string;
	required?: boolean;
	description?: string;
}

export interface ProcessOutput {
	name: string;
	type: string;
	description?: string;
}

export interface ProcessTrigger {
	type: string;
	name: string;
	description?: string;
	condition?: string;
}

export interface Process {
	id: string;
	processNumber: string;
	projectId: string;
	name: string;
	description?: string;
	purpose?: string;
	status: ProcessStatus;
	category?: ProcessCategory;
	tags?: string[];
	versionNumber: number;
	isActiveVersion: boolean;
	parentVersionId?: string;
	versionNotes?: string;
	stages?: ProcessStage[];
	swimlanes?: ProcessSwimlane[];
	inputs?: ProcessInput[];
	outputs?: ProcessOutput[];
	triggers?: ProcessTrigger[];
	exitCriteria?: string[];
	bpmnXml?: string;
	bpmnDiagramUrl?: string;
	owner?: string;
	responsibleTeam?: string;
	expectedDurationHours?: number;
	slaHours?: number;
	activatedAt?: string;
	activatedBy?: string;
	deprecatedAt?: string;
	deprecatedBy?: string;
	deprecationReason?: string;
	relatedProcessIds?: string[];
	metadata?: Record<string, unknown>;
	version: number;
	createdAt: string;
	updatedAt: string;
}

export type ExecutionStatus =
	| "pending"
	| "in_progress"
	| "completed"
	| "failed"
	| "cancelled";

export interface ProcessExecution {
	id: string;
	processId: string;
	executionNumber: string;
	status: ExecutionStatus;
	currentStageId?: string;
	completedStages?: string[];
	startedAt?: string;
	completedAt?: string;
	initiatedBy?: string;
	completedBy?: string;
	triggerItemId?: string;
	contextData?: Record<string, unknown>;
	resultSummary?: string;
	outputItemIds?: string[];
	createdAt: string;
	updatedAt: string;
}

// Quality Engineering (Test Case) Types
export type TestCaseStatus =
	| "draft"
	| "review"
	| "approved"
	| "deprecated"
	| "archived";

export type TestCaseType =
	| "functional"
	| "integration"
	| "unit"
	| "e2e"
	| "performance"
	| "security"
	| "accessibility"
	| "regression"
	| "smoke"
	| "exploratory";

export type TestCasePriority = "critical" | "high" | "medium" | "low";

export type AutomationStatus =
	| "not_automated"
	| "in_progress"
	| "automated"
	| "cannot_automate";

export type TestResultStatus =
	| "passed"
	| "failed"
	| "skipped"
	| "blocked"
	| "error";

export interface TestStep {
	stepNumber: number;
	action: string;
	expectedResult?: string;
	testData?: string;
}

export interface TestCase {
	id: string;
	testCaseNumber: string;
	projectId: string;
	title: string;
	description?: string;
	objective?: string;
	status: TestCaseStatus;
	testType: TestCaseType;
	priority: TestCasePriority;
	category?: string;
	tags?: string[];
	preconditions?: string;
	testSteps?: TestStep[];
	expectedResult?: string;
	postconditions?: string;
	testData?: Record<string, unknown>;
	automationStatus: AutomationStatus;
	automationScriptPath?: string;
	automationFramework?: string;
	automationNotes?: string;
	estimatedDurationMinutes?: number;
	createdBy?: string;
	assignedTo?: string;
	reviewedBy?: string;
	approvedBy?: string;
	reviewedAt?: string;
	approvedAt?: string;
	deprecatedAt?: string;
	deprecationReason?: string;
	lastExecutedAt?: string;
	lastExecutionResult?: TestResultStatus;
	totalExecutions: number;
	passCount: number;
	failCount: number;
	metadata?: Record<string, unknown>;
	version: number;
	createdAt: string;
	updatedAt: string;
}

export interface TestCaseActivity {
	id: string;
	testCaseId: string;
	activityType: string;
	fromValue?: string;
	toValue?: string;
	description?: string;
	performedBy?: string;
	metadata?: Record<string, unknown>;
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
export type TestSuiteStatus = "draft" | "active" | "deprecated" | "archived";

export interface TestSuite {
	id: string;
	suiteNumber: string;
	projectId: string;
	name: string;
	description?: string;
	objective?: string;
	status: TestSuiteStatus;
	parentId?: string;
	orderIndex: number;
	category?: string;
	tags?: string[];
	isParallelExecution: boolean;
	estimatedDurationMinutes?: number;
	requiredEnvironment?: string;
	environmentVariables?: Record<string, string>;
	setupInstructions?: string;
	teardownInstructions?: string;
	owner?: string;
	responsibleTeam?: string;
	totalTestCases: number;
	automatedCount: number;
	manualCount: number;
	passRate?: number;
	lastRunAt?: string;
	lastRunStatus?: string;
	metadata?: Record<string, unknown>;
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
	skipReason?: string;
	customParameters?: Record<string, unknown>;
	createdAt: string;
}

export interface TestSuiteActivity {
	id: string;
	suiteId: string;
	activityType: string;
	fromValue?: string;
	toValue?: string;
	description?: string;
	performedBy?: string;
	metadata?: Record<string, unknown>;
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
export type TestRunStatus =
	| "pending"
	| "running"
	| "passed"
	| "failed"
	| "blocked"
	| "cancelled";

export type TestRunType = "manual" | "automated" | "ci_cd" | "scheduled";

export interface TestRun {
	id: string;
	runNumber: string;
	projectId: string;
	suiteId?: string;
	name: string;
	description?: string;
	status: TestRunStatus;
	runType: TestRunType;
	environment?: string;
	buildNumber?: string;
	buildUrl?: string;
	branch?: string;
	commitSha?: string;
	scheduledAt?: string;
	startedAt?: string;
	completedAt?: string;
	durationSeconds?: number;
	initiatedBy?: string;
	executedBy?: string;
	totalTests: number;
	passedCount: number;
	failedCount: number;
	skippedCount: number;
	blockedCount: number;
	errorCount: number;
	passRate?: number;
	notes?: string;
	failureSummary?: string;
	tags?: string[];
	externalRunId?: string;
	webhookId?: string;
	metadata?: Record<string, unknown>;
	version: number;
	createdAt: string;
	updatedAt: string;
}

export interface TestResult {
	id: string;
	runId: string;
	testCaseId: string;
	status: TestResultStatus;
	startedAt?: string;
	completedAt?: string;
	durationSeconds?: number;
	executedBy?: string;
	actualResult?: string;
	failureReason?: string;
	errorMessage?: string;
	stackTrace?: string;
	screenshots?: string[];
	logsUrl?: string;
	attachments?: string[];
	stepResults?: Array<{
		stepNumber: number;
		status: TestResultStatus;
		actualResult?: string;
		notes?: string;
	}>;
	linkedDefectIds?: string[];
	createdDefectId?: string;
	retryCount: number;
	isFlaky: boolean;
	notes?: string;
	metadata?: Record<string, unknown>;
	createdAt: string;
	updatedAt: string;
}

export interface TestRunActivity {
	id: string;
	runId: string;
	activityType: string;
	fromValue?: string;
	toValue?: string;
	description?: string;
	performedBy?: string;
	metadata?: Record<string, unknown>;
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
export type CoverageType = "direct" | "partial" | "indirect" | "regression";
export type CoverageStatus = "active" | "deprecated" | "needs_review";

export interface TestCoverage {
	id: string;
	projectId: string;
	testCaseId: string;
	requirementId: string;
	coverageType: CoverageType;
	status: CoverageStatus;
	coveragePercentage?: number;
	rationale?: string;
	notes?: string;
	lastVerifiedAt?: string;
	verifiedBy?: string;
	lastTestResult?: string;
	lastTestedAt?: string;
	createdBy?: string;
	metadata?: Record<string, unknown>;
	version: number;
	createdAt: string;
	updatedAt: string;
}

export interface CoverageActivity {
	id: string;
	coverageId: string;
	activityType: string;
	fromValue?: string;
	toValue?: string;
	description?: string;
	performedBy?: string;
	metadata?: Record<string, unknown>;
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
		coveragePercentage?: number;
		lastTestResult?: string;
		lastTestedAt?: string;
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
	priority?: string;
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
	| "github_actions"
	| "gitlab_ci"
	| "jenkins"
	| "azure_devops"
	| "circleci"
	| "travis_ci"
	| "custom";

export type WebhookStatus = "active" | "paused" | "disabled";

export interface WebhookIntegration {
	id: string;
	projectId: string;
	name: string;
	description?: string;
	provider: WebhookProvider;
	status: WebhookStatus;
	webhookSecret: string;
	apiKey?: string;
	enabledEvents?: string[];
	eventFilters?: Record<string, unknown>;
	callbackUrl?: string;
	callbackHeaders?: Record<string, string>;
	defaultSuiteId?: string;
	rateLimitPerMinute: number;
	autoCreateRun: boolean;
	autoCompleteRun: boolean;
	verifySignatures: boolean;
	// Statistics
	totalRequests: number;
	successfulRequests: number;
	failedRequests: number;
	lastRequestAt?: string;
	lastSuccessAt?: string;
	lastFailureAt?: string;
	lastErrorMessage?: string;
	metadata?: Record<string, unknown>;
	version: number;
	createdAt: string;
	updatedAt: string;
}

export interface WebhookLog {
	id: string;
	webhookId: string;
	requestId: string;
	eventType?: string;
	httpMethod: string;
	sourceIp?: string;
	userAgent?: string;
	requestHeaders?: Record<string, unknown>;
	requestBodyPreview?: string;
	payloadSizeBytes?: number;
	success: boolean;
	statusCode: number;
	errorMessage?: string;
	processingTimeMs?: number;
	testRunId?: string;
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
export type IntegrationProvider = "github" | "github_projects" | "linear";

export type CredentialType = "oauth" | "pat" | "api_key";

export type CredentialStatus =
	| "active"
	| "expired"
	| "revoked"
	| "invalid"
	| "pending_reauth";

export type MappingDirection = "pull" | "push" | "bidirectional";

export type MappingStatus = "active" | "paused" | "error" | "pending";

export type SyncQueueStatus =
	| "pending"
	| "processing"
	| "completed"
	| "failed"
	| "cancelled";

export type ConflictResolutionStrategy =
	| "local_wins"
	| "external_wins"
	| "manual"
	| "merge"
	| "skip";

export interface IntegrationCredential {
	id: string;
	projectId?: string;
	provider: IntegrationProvider;
	credentialType: CredentialType;
	status: CredentialStatus;
	scopes: string[];
	providerUserId?: string;
	providerMetadata?: Record<string, unknown>;
	lastValidatedAt?: string;
	validationError?: string;
	expiresAt?: string;
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
	externalUrl?: string;
	externalKey?: string;
	mappingMetadata?: Record<string, unknown>;
	status: MappingStatus;
	syncEnabled: boolean;
	lastSyncedAt?: string;
	lastSyncStatus?: string;
	lastSyncError?: string;
	fieldMappings?: Record<string, string>;
	fieldResolutionRules?: Record<string, ConflictResolutionStrategy>;
	localVersion?: number;
	externalVersion?: string;
	createdAt: string;
	updatedAt: string;
}

export interface SyncQueueItem {
	id: string;
	credentialId?: string;
	mappingId?: string;
	provider: IntegrationProvider;
	eventType: string;
	direction: string;
	status: SyncQueueStatus;
	priority: number;
	retryCount: number;
	maxRetries: number;
	errorMessage?: string;
	scheduledAt?: string;
	startedAt?: string;
	completedAt?: string;
	createdAt: string;
}

export interface SyncLog {
	id: string;
	credentialId?: string;
	mappingId?: string;
	provider: IntegrationProvider;
	eventType: string;
	direction: string;
	status: string;
	itemsProcessed: number;
	itemsFailed: number;
	itemsSkipped: number;
	errorMessage?: string;
	startedAt?: string;
	completedAt?: string;
	durationMs?: number;
	createdAt: string;
}

export interface WorkflowRun {
	id: string;
	projectId?: string;
	graphId?: string;
	workflowName: string;
	status: string;
	externalRunId?: string;
	payload?: Record<string, unknown>;
	result?: Record<string, unknown>;
	errorMessage?: string;
	createdByUserId?: string;
	startedAt?: string;
	completedAt?: string;
	createdAt?: string;
	updatedAt?: string;
}

export interface WorkflowSchedule {
	id?: string;
	cronName?: string;
	expression?: string;
	workflowName?: string;
	additionalMetadata?: Record<string, unknown>;
	[key: string]: unknown;
}

export interface SyncConflict {
	id: string;
	mappingId: string;
	provider: IntegrationProvider;
	conflictType: string;
	fieldName?: string;
	localValue?: unknown;
	externalValue?: unknown;
	localModifiedAt?: string;
	externalModifiedAt?: string;
	status: "pending" | "resolved" | "skipped";
	resolution?: string;
	resolvedValue?: unknown;
	resolvedBy?: string;
	resolvedAt?: string;
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
		lastValidated?: string;
	}>;
}

// GitHub-specific types
export interface GitHubRepo {
	id: number;
	name: string;
	fullName: string;
	description?: string;
	htmlUrl: string;
	private: boolean;
	owner: {
		login: string;
		avatarUrl: string;
	};
	defaultBranch: string;
	updatedAt?: string;
}

export interface GitHubIssue {
	id: number;
	number: number;
	title: string;
	state: string;
	htmlUrl: string;
	body?: string;
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
	body?: string;
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
	description?: string;
	url: string;
	closed: boolean;
	public: boolean;
	createdAt?: string;
	updatedAt?: string;
}

// Linear-specific types
export interface LinearTeam {
	id: string;
	name: string;
	key: string;
	description?: string;
	icon?: string;
	color?: string;
}

export interface LinearIssue {
	id: string;
	identifier: string;
	title: string;
	description?: string;
	state?: string;
	priority?: number;
	url: string;
	assignee?: string;
	labels: string[];
	createdAt?: string;
	updatedAt?: string;
}

export interface LinearProject {
	id: string;
	name: string;
	description?: string;
	state?: string;
	progress?: number;
	url: string;
	startDate?: string;
	targetDate?: string;
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
	details?: Record<string, unknown>;
}

// Re-export specification types
export * from "./specification";

// Re-export temporal types
export * from "./temporal";

// Temporal dimension types
export * from "./progress";

// Re-export multi-dimensional traceability types
export * from "./canonical";
export * from "./ui-entities";
export * from "./component-library";
export * from "./entity-hierarchy";
