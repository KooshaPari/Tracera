// Node Registry - Maps item types to React Flow node components
// Implements Phase 5 of Type-Aware Node System + B3 LOD (simplePill at scale)
// Phase 2 Task 2.4: Enhanced LOD-aware node type selection

import type { NodeTypes } from '@xyflow/react';

import { MediumPill } from './MediumPill';
import { NodeErrorSkeleton } from './NodeErrorSkeleton';
import { NodeLoadingSkeleton } from './NodeLoadingSkeleton';
import { EpicNode } from './nodes/EpicNode';
import { RequirementNode } from './nodes/RequirementNode';
import { TestNode } from './nodes/TestNode';
import { QAEnhancedNode } from './QAEnhancedNode';
import { RichNodePill } from './RichNodePill';
import { SimpleNodePill } from './SimpleNodePill';
import { SimplePill } from './SimplePill';
import { SkeletonPill } from './SkeletonPill';
import { LOD_NODE_COUNT_THRESHOLD } from './utils/lod';

/**
 * Context for LOD-aware node type selection
 * Used to determine which level of detail to render based on viewport state
 */
export interface NodeTypeContext {
  /** Total number of nodes in the graph */
  totalNodeCount: number;
  /** Current viewport zoom level */
  zoom: number;
  /** Whether this node is currently selected */
  isSelected: boolean;
  /** Whether this node is currently focused */
  isFocused: boolean;
  /** Loading or error state (if applicable) */
  loadingState?: 'loading' | 'error';
  /** Distance from viewport center (in pixels, optional) */
  distance?: number;
}

/**
 * Node types registry for React Flow
 * Maps node type strings to their component implementations
 */
export const nodeTypes: NodeTypes = {
  // Legacy nodes (for backward compatibility)
  richPill: RichNodePill,
  qaEnhanced: QAEnhancedNode,

  // LOD nodes (Level of Detail)
  simplePill: SimpleNodePill,
  simple: SimplePill,
  medium: MediumPill,
  skeleton: SkeletonPill,

  // Loading/error skeletons (Phase 3, 2.1 / 2.2) — LOD-shaped
  nodeLoading: NodeLoadingSkeleton,
  nodeError: NodeErrorSkeleton,

  // Type-specific nodes (Phase 5)
  test: TestNode,
  test_case: TestNode,
  test_suite: TestNode,
  requirement: RequirementNode,
  epic: EpicNode,

  // Default fallback
  default: RichNodePill,
};

/**
 * Get the appropriate node type for an item (legacy version without context)
 * Maps item.type -> React Flow node type string
 *
 * @deprecated Use getNodeTypeWithContext for LOD-aware selection
 * @param itemType - The type of the item (e.g., "test", "requirement", "epic")
 * @returns The React Flow node type to use
 */
export function getNodeTypeLegacy(itemType: string): string {
  // Type-specific mappings
  const typeMap: Record<string, string> = {
    // Test types
    test: 'test',
    test_case: 'test_case',
    test_suite: 'test_suite',

    // Requirement types
    requirement: 'requirement',

    // Epic types
    epic: 'epic',

    // QA enhanced for certain types (if they have preview data)
    // This will be determined at runtime based on node data
  };

  // Return mapped type or default to richPill
  return typeMap[itemType] ?? 'default';
}

/**
 * Get the appropriate node type based on context (LOD-aware)
 * Selects node representation based on zoom, node count, selection state, and loading state
 *
 * Priority order:
 * 1. Loading/Error state -> skeleton
 * 2. Selected/Focused -> full detail (type-specific)
 * 3. High node count OR low zoom OR far distance -> simple
 * 4. Medium conditions -> medium
 * 5. Default -> type-specific or default
 *
 * @param itemType - The type of the item (e.g., "test", "requirement", "epic")
 * @param context - Viewport and node context for LOD decisions
 * @returns The React Flow node type to use
 */
export function getNodeType(itemType: string, context: NodeTypeContext): string {
  // Priority 1: Loading or error states
  if (context.loadingState) {
    return 'skeleton';
  }

  // Priority 2: Always show full detail for selected or focused nodes
  if (context.isSelected || context.isFocused) {
    return getNodeTypeLegacy(itemType);
  }

  const { totalNodeCount, zoom, distance = 0 } = context;

  // Priority 3: Use simple representation for high scale or low zoom
  // Thresholds: >5000 nodes OR zoom < 0.5 OR distance > 800px
  if (totalNodeCount > 5000 || zoom < 0.5 || distance > 800) {
    return 'simple';
  }

  // Priority 4: Use medium representation for moderate scale
  // Thresholds: >2000 nodes OR zoom < 0.8 OR distance > 400px
  if (totalNodeCount > 2000 || zoom < 0.8 || distance > 400) {
    return 'medium';
  }

  // Priority 5: Default to type-specific or default
  return getNodeTypeLegacy(itemType);
}

/**
 * Determine if a node should use the QA enhanced type based on its data
 * QA enhanced nodes are used when preview/artifact data is available
 *
 * @param nodeData - The node data object
 * @returns True if node should use qaEnhanced type
 */
export function shouldUseQAEnhancedNode(nodeData: Record<string, unknown>): boolean {
  return Boolean(nodeData['preview'] ?? nodeData['artifacts'] ?? nodeData['metrics']);
}

/**
 * Get the final node type, considering both item type and available data
 * This is the recommended function to use when creating nodes (legacy version without context)
 *
 * @param itemType - The type of the item
 * @param nodeData - The complete node data
 * @returns The React Flow node type to use
 */
export function getNodeTypeForItem(itemType: string, nodeData: Record<string, unknown>): string {
  // Check if QA enhanced should be used
  if (shouldUseQAEnhancedNode(nodeData)) {
    return 'qaEnhanced';
  }

  // Otherwise use type-specific or default
  return getNodeTypeLegacy(itemType);
}

/**
 * Get node type with LOD: when node count is high (or zoom low), use simplified node (B3).
 * Use this when building nodes in the graph so at scale we render simplePill instead of full type.
 *
 * @param itemType - The type of the item
 * @param nodeData - The complete node data (for QA enhanced check when not simplified)
 * @param options - LOD options: nodeCount (and optionally zoom for future zoom-based LOD)
 * @returns The React Flow node type to use ("simplePill" when simplified, else getNodeTypeForItem).
 * Also returns "nodeLoading" / "nodeError" when nodeData.loading or nodeData.error (2.3).
 */
export function getNodeTypeWithLOD(
  itemType: string,
  nodeData: Record<string, unknown>,
  options: { nodeCount: number; zoom?: number },
): string {
  if (nodeData['loading'] === true) {
    return 'nodeLoading';
  }
  if (nodeData['error'] != null && nodeData['error'] !== false) {
    return 'nodeError';
  }
  const { nodeCount } = options;
  if (nodeCount >= LOD_NODE_COUNT_THRESHOLD) {
    return 'simplePill';
  }
  return getNodeTypeForItem(itemType, nodeData);
}
