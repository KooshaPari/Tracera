// Node Data Transformers - Convert Item to type-specific node data
// Implements type-aware node system for the graph view

import type {
	EpicItem,
	Item,
	RequirementItem,
	TestItem,
} from "@tracertm/types";
import type { EpicNodeData } from "../nodes/EpicNode";
import type { RequirementNodeData } from "../nodes/RequirementNode";
import type { TestNodeData } from "../nodes/TestNode";
import type { RichNodeData } from "../RichNodePill";

/**
 * Type guards
 */
function isTestItem(item: Item): item is TestItem {
	return (
		item.type === "test" ||
		item.type === "test_case" ||
		item.type === "test_suite"
	);
}

function isRequirementItem(item: Item): item is RequirementItem {
	return item.type === "requirement";
}

function isEpicItem(item: Item): item is EpicItem {
	return item.type === "epic";
}

/**
 * Transform a test item to TestNodeData
 */
function transformTestItem(item: TestItem): Partial<TestNodeData> {
	// Extract test-specific metadata
	const metadata = item.metadata || {};

	return {
		testType: item.testType,
		framework: metadata.framework as string | undefined,
		flakinessScore: metadata.flakinessScore as number | undefined,
		coveragePercent: metadata.coveragePercent as number | undefined,
		safetyLevel: metadata.safetyLevel as
			| "safe"
			| "quarantined"
			| "disabled"
			| undefined,
		lastRunStatus: item.lastExecutionResult,
	};
}

/**
 * Transform a requirement item to RequirementNodeData
 */
function transformRequirementItem(
	item: RequirementItem,
): Partial<RequirementNodeData> {
	const metadata = item.metadata || {};
	const qualityMetrics = item.qualityMetrics;

	return {
		earsPatternType: metadata.earsPatternType as
			| "ubiquitous"
			| "event_driven"
			| "state_driven"
			| "optional"
			| "unwanted"
			| undefined,
		riskLevel: metadata.riskLevel as
			| "low"
			| "medium"
			| "high"
			| "critical"
			| undefined,
		wsjfScore: metadata.wsjfScore as number | undefined,
		verifiabilityScore: qualityMetrics?.completenessScore,
		verificationStatus: metadata.verificationStatus as
			| "not_verified"
			| "partially_verified"
			| "verified"
			| undefined,
	};
}

/**
 * Transform an epic item to EpicNodeData
 */
function transformEpicItem(item: EpicItem): Partial<EpicNodeData> {
	const metadata = item.metadata || {};

	return {
		businessValue: item.businessValue
			? (item.businessValue.toLowerCase() as
					| "low"
					| "medium"
					| "high"
					| "critical")
			: (metadata.businessValue as
					| "low"
					| "medium"
					| "high"
					| "critical"
					| undefined),
		timelineProgress: metadata.timelineProgress as number | undefined,
		storyCount: metadata.storyCount as number | undefined,
		completedStoryCount: metadata.completedStoryCount as number | undefined,
	};
}

/**
 * Main transformer: Convert any Item to appropriate node data
 * Returns RichNodeData with type-specific fields merged in
 */
export function itemToNodeData(
	item: Item,
	connections = { incoming: 0, outgoing: 0, total: 0 },
): RichNodeData | TestNodeData | RequirementNodeData | EpicNodeData {
	// Base node data (common to all types)
	const baseData: RichNodeData = {
		id: item.id,
		item,
		type: item.type,
		status: item.status,
		label: item.title,
		description: item.description,
		connections,
	};

	// Type-specific transformations
	if (isTestItem(item)) {
		return {
			...baseData,
			...transformTestItem(item),
		} as TestNodeData;
	}

	if (isRequirementItem(item)) {
		return {
			...baseData,
			...transformRequirementItem(item),
		} as RequirementNodeData;
	}

	if (isEpicItem(item)) {
		return {
			...baseData,
			...transformEpicItem(item),
		} as EpicNodeData;
	}

	// Default: return as RichNodeData
	return baseData;
}

/**
 * Batch transform items to node data
 */
export function itemsToNodeData(
	items: Item[],
	connectionMap?: Map<
		string,
		{ incoming: number; outgoing: number; total: number }
	>,
): Array<RichNodeData | TestNodeData | RequirementNodeData | EpicNodeData> {
	return items.map((item) => {
		const connections = connectionMap?.get(item.id) || {
			incoming: 0,
			outgoing: 0,
			total: 0,
		};
		return itemToNodeData(item, connections);
	});
}
