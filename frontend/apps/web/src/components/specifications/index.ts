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
	ADRGraph,
	ADRTimeline,
	ComplianceGauge,
	DecisionMatrix,
} from "./adr";
// ============================================================================
// Analytics Components (Blockchain/NFT-like)
// ============================================================================
export {
	CVSSDetailCard,
	CVSSScoreBadge,
	CVSSScoreGauge,
	EARSPatternBadge,
	EARSPatternDetail,
	FlakinessDetailCard,
	FlakinessIndicator,
	ImpactAnalysisGraph,
	ImpactSummaryBadge,
	ODCBadge,
	ODCClassificationCard,
	ODCTriggerBadge,
	QualityDimensionBars,
	QualityDimensionRadar,
	QualityIssueItem,
	QualityIssueList,
	QualityIssueSummary,
} from "./analytics";
// ============================================================================
// BDD (Behavior-Driven Development) Components
// ============================================================================
export {
	ExamplesTable,
	FeatureCard,
	GherkinEditor,
	GherkinViewer,
	ScenarioCard,
	StepBadge,
	type TableExample,
	type ValidationError,
} from "./bdd";
// ============================================================================
// Blockchain Components
// ============================================================================
export {
	ContentAddressBadge,
	ContentAddressCard,
	ContentHashComparison,
	DigitalSignatureBadge,
	MerkleProofViewer,
	MerkleVerificationBadge,
	SignatureHistory,
	SignatureVerificationStatus,
	VersionChainBadge,
	VersionChainTimeline,
} from "./blockchain";
// ============================================================================
// Contract Components
// ============================================================================
export {
	ConditionList,
	ContractCard,
	ContractEditor,
	FailVerificationBadge,
	PassVerificationBadge,
	PendingVerificationBadge,
	StateMachineViewer,
	UnverifiedBadge,
	VerificationBadge,
} from "./contracts";
// ============================================================================
// Specification Dashboard Components
// ============================================================================
export {
	ComplianceGaugeFull,
	CoverageHeatmap,
	GapAnalysis,
	HealthScoreRing,
	SpecificationDashboard,
} from "./dashboard";
// ============================================================================
// Item Specification Components
// ============================================================================
export {
	DefectSpecCard,
	EpicSpecCard,
	ItemSpecsOverview,
	ItemSpecTabs,
	QualityScoreGauge,
	RequirementSpecCard,
	SpecMetadataPanel,
	TaskSpecCard,
	TestSpecCard,
	UserStorySpecCard,
} from "./items";

// ============================================================================
// Prioritization Components
// ============================================================================
export {
	MoSCoWBadge,
	PrioritizationSummary,
	PriorityMatrix,
	RICEBreakdown,
	RICEScoreBadge,
	RICEScoreCard,
	ValueEffortMatrix,
	WSJFCalculator,
	WSJFScoreBadge,
} from "./prioritization";
// ============================================================================
// Quality Components
// ============================================================================
export { SmellIndicator } from "./quality/SmellIndicator";
