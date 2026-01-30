/**
 * Specification Components Barrel Export
 * Comprehensive collection of components for ADR, BDD, Contracts, and Specification Dashboard
 * Part of Layer 3: Visual UI Engine (ADR-0001)
 */

// ============================================================================
// ADR (Architecture Decision Records) Components
// ============================================================================
export {
	ADRCard,
	ADREditor,
	ADRTimeline,
	ADRGraph,
	DecisionMatrix,
	ComplianceGauge,
} from "./adr";

// ============================================================================
// BDD (Behavior-Driven Development) Components
// ============================================================================
export {
	FeatureCard,
	ScenarioCard,
	GherkinEditor,
	type ValidationError,
	GherkinViewer,
	StepBadge,
	ExamplesTable,
	type TableExample,
} from "./bdd";

// ============================================================================
// Contract Components
// ============================================================================
export {
	ContractCard,
	ContractEditor,
	ConditionList,
	StateMachineViewer,
	VerificationBadge,
	PassVerificationBadge,
	FailVerificationBadge,
	PendingVerificationBadge,
	UnverifiedBadge,
} from "./contracts";

// ============================================================================
// Specification Dashboard Components
// ============================================================================
export {
	SpecificationDashboard,
	HealthScoreRing,
	CoverageHeatmap,
	GapAnalysis,
	ComplianceGaugeFull,
} from "./dashboard";

// ============================================================================
// Quality Components
// ============================================================================
export { SmellIndicator } from "./quality/SmellIndicator";

// ============================================================================
// Analytics Components (Blockchain/NFT-like)
// ============================================================================
export {
	EARSPatternBadge,
	EARSPatternDetail,
	QualityDimensionRadar,
	QualityDimensionBars,
	QualityIssueList,
	QualityIssueItem,
	QualityIssueSummary,
	FlakinessIndicator,
	FlakinessDetailCard,
	ODCClassificationCard,
	ODCBadge,
	ODCTriggerBadge,
	CVSSScoreBadge,
	CVSSScoreGauge,
	CVSSDetailCard,
	ImpactAnalysisGraph,
	ImpactSummaryBadge,
} from "./analytics";

// ============================================================================
// Blockchain Components
// ============================================================================
export {
	VersionChainTimeline,
	VersionChainBadge,
	MerkleProofViewer,
	MerkleVerificationBadge,
	ContentAddressCard,
	ContentAddressBadge,
	ContentHashComparison,
	DigitalSignatureBadge,
	SignatureVerificationStatus,
	SignatureHistory,
} from "./blockchain";

// ============================================================================
// Prioritization Components
// ============================================================================
export {
	WSJFCalculator,
	WSJFScoreBadge,
	RICEScoreCard,
	RICEScoreBadge,
	RICEBreakdown,
	PriorityMatrix,
	ValueEffortMatrix,
	MoSCoWBadge,
	PrioritizationSummary,
} from "./prioritization";

// ============================================================================
// Item Specification Components
// ============================================================================
export {
	RequirementSpecCard,
	TestSpecCard,
	EpicSpecCard,
	UserStorySpecCard,
	TaskSpecCard,
	DefectSpecCard,
	QualityScoreGauge,
	SpecMetadataPanel,
	ItemSpecTabs,
	ItemSpecsOverview,
} from "./items";
