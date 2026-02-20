// Node Data Transformers - Convert Item to type-specific node data
// Implements type-aware node system for the graph view

import type { EpicItem, Item, RequirementItem, TestItem } from '@tracertm/types';

import type { EpicNodeData } from '../nodes/EpicNode';
import type { RequirementNodeData } from '../nodes/RequirementNode';
import type { TestNodeData } from '../nodes/TestNode';
import type { RichNodeData } from '../RichNodePill';

type NormalizedTestStatus = TestNodeData['lastRunStatus'];

function normalizeTestStatus(status: TestItem['lastExecutionResult']): NormalizedTestStatus {
  switch (status) {
    case 'passed':
    case 'failed':
    case 'skipped':
    case 'error': {
      return status;
    }
    case 'blocked': {
      return 'failed';
    }
    default: {
      return undefined;
    }
  }
}

/**
 * Type guards
 */
function isTestItem(item: Item): item is TestItem {
  return item['type'] === 'test' || item['type'] === 'test_case' || item['type'] === 'test_suite';
}

function isRequirementItem(item: Item): item is RequirementItem {
  return item['type'] === 'requirement';
}

function isEpicItem(item: Item): item is EpicItem {
  return item['type'] === 'epic';
}

/**
 * Transform a test item to TestNodeData
 */
function transformTestItem(item: TestItem): Partial<TestNodeData> {
  // Extract test-specific metadata
  const metadata = item['metadata'] ?? {};
  const result: Partial<TestNodeData> = {};

  const coveragePercent = metadata['coveragePercent'] as number | undefined;
  if (coveragePercent !== undefined) result.coveragePercent = coveragePercent;
  const flakinessScore = metadata['flakinessScore'] as number | undefined;
  if (flakinessScore !== undefined) result.flakinessScore = flakinessScore;
  const framework = metadata['framework'] as string | undefined;
  if (framework !== undefined) result.framework = framework;
  const lastRunStatus = normalizeTestStatus(item['lastExecutionResult']);
  if (lastRunStatus !== undefined) result.lastRunStatus = lastRunStatus;
  const safetyLevel = metadata['safetyLevel'] as 'safe' | 'quarantined' | 'disabled' | undefined;
  if (safetyLevel !== undefined) result.safetyLevel = safetyLevel;
  if (item['testType'] !== undefined) result.testType = item['testType'];

  return result;
}

/**
 * Transform a requirement item to RequirementNodeData
 */
function transformRequirementItem(item: RequirementItem): Partial<RequirementNodeData> {
  const metadata = item['metadata'] ?? {};
  const { qualityMetrics } = item;
  const result: Partial<RequirementNodeData> = {};

  const earsPatternType = metadata['earsPatternType'] as
    | 'ubiquitous'
    | 'event_driven'
    | 'state_driven'
    | 'optional'
    | 'unwanted'
    | undefined;
  if (earsPatternType !== undefined) result.earsPatternType = earsPatternType;
  const riskLevel = metadata['riskLevel'] as 'low' | 'medium' | 'high' | 'critical' | undefined;
  if (riskLevel !== undefined) result.riskLevel = riskLevel;
  if (qualityMetrics?.completenessScore !== undefined)
    result.verifiabilityScore = qualityMetrics.completenessScore;
  const verificationStatus = metadata['verificationStatus'] as
    | 'not_verified'
    | 'partially_verified'
    | 'verified'
    | undefined;
  if (verificationStatus !== undefined) result.verificationStatus = verificationStatus;
  const wsjfScore = metadata['wsjfScore'] as number | undefined;
  if (wsjfScore !== undefined) result.wsjfScore = wsjfScore;

  return result;
}

/**
 * Transform an epic item to EpicNodeData
 */
function transformEpicItem(item: EpicItem): Partial<EpicNodeData> {
  const metadata = item['metadata'] ?? {};
  const result: Partial<EpicNodeData> = {};

  const businessValue = item['businessValue']
    ? (item['businessValue'].toLowerCase() as 'low' | 'medium' | 'high' | 'critical')
    : (metadata['businessValue'] as 'low' | 'medium' | 'high' | 'critical' | undefined);
  if (businessValue !== undefined) result.businessValue = businessValue;
  const completedStoryCount = metadata['completedStoryCount'] as number | undefined;
  if (completedStoryCount !== undefined) result.completedStoryCount = completedStoryCount;
  const storyCount = metadata['storyCount'] as number | undefined;
  if (storyCount !== undefined) result.storyCount = storyCount;
  const timelineProgress = metadata['timelineProgress'] as number | undefined;
  if (timelineProgress !== undefined) result.timelineProgress = timelineProgress;

  return result;
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
    description: item['description'],
    id: item['id'],
    item,
    label: item['title'],
    status: item['status'],
    type: item['type'],
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
  connectionMap?: Map<string, { incoming: number; outgoing: number; total: number }>,
): (RichNodeData | TestNodeData | RequirementNodeData | EpicNodeData)[] {
  return items.map((item) => {
    const connections = connectionMap?.get(item['id']) ?? {
      incoming: 0,
      outgoing: 0,
      total: 0,
    };
    return itemToNodeData(item, connections);
  });
}
