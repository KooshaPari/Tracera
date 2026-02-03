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
		item["type"] === "test" ||
		item["type"] === "test_case" ||
		item["type"] === "test_suite"
	);
}

function isRequirementItem(item: Item): item is RequirementItem {
	return item["type"] === "requirement";
}

function isEpicItem(item: Item): item is EpicItem {
	return item["type"] === "epic";
}

/**
 * Transform a test item to TestNodeData
 */
function transformTestItem(item: TestItem): Partial<TestNodeData> {
	// Extract test-specific metadata
	const metadata = item["metadata"] || {};

	return {
		coveragePercent: metadata["coveragePercent"] as number | undefined,
		flakinessScore: metadata["flakinessScore"] as number | undefined,
		framework: metadata["framework"] as string | undefined,
		lastRunStatus: item["lastExecutionResult"],
		safetyLevel: metadata["safetyLevel"] as
			| "safe"
			| "quarantined"
			| "disabled"
			| undefined,
		testType: item["testType"],
	};
}

/**
 * Transform a requirement item to RequirementNodeData
 */
function transformRequirementItem(
	item: RequirementItem,
): Partial<RequirementNodeData> {
	const metadata = item["metadata"] || {};
	const { qualityMetrics } = item;

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
		verifiabilityScore: qualityMetrics?.completenessScore,
		verificationStatus: metadata.verificationStatus as
			| "not_verified"
			| "partially_verified"
			| "verified"
			| undefined,
		wsjfScore: metadata.wsjfScore as number | undefined,
	};
}

/**
 * Transform an epic item to EpicNodeData
 */
function transformEpicItem(item: EpicItem): Partial<EpicNodeData> {
	const metadata = item["metadata"] || {};

	return {
		businessValue: item["businessValue"]
			? (item["businessValue"].toLowerCase() as
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
		completedStoryCount: metadata.completedStoryCount as number | undefined,
		storyCount: metadata.storyCount as number | undefined,
		timelineProgress: metadata.timelineProgress as number | undefined,
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
		connections,
		description: item["description"],
		id: item["id"],
		item,
		label: item["title"],
		status: item["status"],
		type: item["type"],
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
): (RichNodeData | TestNodeData | RequirementNodeData | EpicNodeData)[] {
	return items.map((item) => {
		const connections = connectionMap?.get(item["id"]) || {
			incoming: 0,
			outgoing: 0,
			total: 0,
		};
		return itemToNodeData(item, connections);
	});
}
