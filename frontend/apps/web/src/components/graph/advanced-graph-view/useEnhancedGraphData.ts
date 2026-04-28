import { useMemo } from 'react';

import type { EnhancedNodeData, GraphPerspective } from '@/components/graph/types';
import type { Item, Link, LinkType } from '@tracertm/types';

import { PERSPECTIVE_CONFIGS, TYPE_TO_PERSPECTIVE } from '@/components/graph/types';

const EMPTY_LINK_TYPE_COUNTS: Record<LinkType, number> = {
  implements: 0,
  tests: 0,
  depends_on: 0,
  related_to: 0,
  blocks: 0,
  parent_of: 0,
  same_as: 0,
  represents: 0,
  manifests_as: 0,
  documents: 0,
  mentions: 0,
  calls: 0,
  imports: 0,
  derives_from: 0,
  alternative_to: 0,
  conflicts_with: 0,
  supersedes: 0,
  validates: 0,
  traces_to: 0,
};

function computeDepth(item: Item, itemMap: Map<string, Item>): number {
  let depth = 0;
  let currentId: string | undefined = item.parentId;
  while (typeof currentId === 'string' && currentId.length > 0 && depth < 10) {
    depth += 1;
    const parent = itemMap.get(currentId);
    currentId = parent?.parentId;
  }
  return depth;
}

function getStringMetadata(
  metadata: Record<string, unknown> | undefined,
  key: string,
): string | undefined {
  const value = metadata?.[key];
  return typeof value === 'string' ? value : undefined;
}

interface UseEnhancedGraphDataArgs {
  items: Item[];
  links: Link[];
  perspective: GraphPerspective;
  selectedNodeId: string | null;
}

interface EnhancedGraphDataResult {
  enhancedNodes: EnhancedNodeData[];
  filteredLinks: Link[];
  filteredNodes: EnhancedNodeData[];
  incomingLinks: Link[];
  outgoingLinks: Link[];
  perspectiveCounts: Record<GraphPerspective, number>;
  relatedItems: Item[];
  selectedNode: EnhancedNodeData | null;
}

export function useEnhancedGraphData({
  items,
  links,
  perspective,
  selectedNodeId,
}: UseEnhancedGraphDataArgs): EnhancedGraphDataResult {
  const enhancedNodes = useMemo((): EnhancedNodeData[] => {
    const itemMap = new Map(items.map((item) => [item.id, item]));

    // Count connections for each item
    const incomingCount = new Map<string, number>();
    const outgoingCount = new Map<string, number>();
    const connectionsByType = new Map<string, Record<LinkType, number>>();

    const getOrInitCounts = (itemId: string): Record<LinkType, number> => {
      const existing = connectionsByType.get(itemId);
      if (existing) {
        return existing;
      }
      const initial: Record<LinkType, number> = { ...EMPTY_LINK_TYPE_COUNTS };
      connectionsByType.set(itemId, initial);
      return initial;
    };

    for (const link of links) {
      // Incoming
      incomingCount.set(link.targetId, (incomingCount.get(link.targetId) ?? 0) + 1);
      // Outgoing
      outgoingCount.set(link.sourceId, (outgoingCount.get(link.sourceId) ?? 0) + 1);

      // By type
      const targetTypes = getOrInitCounts(link.targetId);
      targetTypes[link.type] += 1;

      const sourceTypes = getOrInitCounts(link.sourceId);
      sourceTypes[link.type] += 1;
    }

    return items.map((item) => {
      const itemType = item.type.toLowerCase();
      const perspectives = TYPE_TO_PERSPECTIVE[itemType] ?? ['all'];
      const incoming = incomingCount.get(item.id) ?? 0;
      const outgoing = outgoingCount.get(item.id) ?? 0;

      // Check if has children
      const hasChildren = items.some((i) => i.parentId === item.id);

      const depth = computeDepth(item, itemMap);

      const screenshotUrl = getStringMetadata(item.metadata, 'screenshotUrl');
      const componentCode = getStringMetadata(item.metadata, 'code');
      const interactiveWidgetUrl = getStringMetadata(item.metadata, 'interactiveUrl');

      const label = item.title.length > 0 ? item.title : 'Untitled';

      const nodeData: EnhancedNodeData = {
        connections: {
          byType: connectionsByType.get(item.id) ?? { ...EMPTY_LINK_TYPE_COUNTS },
          incoming,
          outgoing,
          total: incoming + outgoing,
        },
        depth,
        hasChildren,
        id: item.id,
        item,
        label,
        parentId: item.parentId,
        perspective: perspectives,
        status: item.status,
        type: itemType,
        uiPreview:
          typeof screenshotUrl === 'string' && screenshotUrl.length > 0
            ? {
                componentCode,
                interactiveWidgetUrl,
                screenshotUrl,
              }
            : undefined,
      };

      return nodeData;
    });
  }, [items, links]);

  const filteredNodes = useMemo(() => {
    if (perspective === 'all') {
      return enhancedNodes;
    }

    const config = PERSPECTIVE_CONFIGS.find((c) => c.id === perspective);
    if (!config || config.includeTypes.length === 0) {
      return enhancedNodes;
    }

    return enhancedNodes.filter((node) => {
      const nodeType = node.type.toLowerCase();
      // Check if type is in includeTypes or if node has this perspective
      return (
        config.includeTypes.some((t) => nodeType.includes(t) || t.includes(nodeType)) ||
        node.perspective.includes(perspective)
      );
    });
  }, [enhancedNodes, perspective]);

  const filteredLinks = useMemo(() => {
    const nodeIds = new Set(filteredNodes.map((n) => n.id));
    return links.filter((link) => nodeIds.has(link.sourceId) && nodeIds.has(link.targetId));
  }, [links, filteredNodes]);

  const perspectiveCounts = useMemo(() => {
    const counts: Record<GraphPerspective, number> = {
      all: enhancedNodes.length,
      business: 0,
      performance: 0,
      product: 0,
      security: 0,
      technical: 0,
      ui: 0,
    };

    for (const node of enhancedNodes) {
      for (const p of node.perspective) {
        if (p !== 'all') {
          counts[p] = (counts[p] ?? 0) + 1;
        }
      }
    }

    return counts;
  }, [enhancedNodes]);

  const selectedNode = useMemo(() => {
    if (selectedNodeId === null) {
      return null;
    }
    return filteredNodes.find((n) => n.id === selectedNodeId) ?? null;
  }, [filteredNodes, selectedNodeId]);

  const { incomingLinks, outgoingLinks, relatedItems } = useMemo(() => {
    if (selectedNodeId === null) {
      return { incomingLinks: [], outgoingLinks: [], relatedItems: [] };
    }

    const incoming = links.filter((l) => l.targetId === selectedNodeId);
    const outgoing = links.filter((l) => l.sourceId === selectedNodeId);

    const relatedIds = new Set([
      ...incoming.map((l) => l.sourceId),
      ...outgoing.map((l) => l.targetId),
    ]);

    return {
      incomingLinks: incoming,
      outgoingLinks: outgoing,
      relatedItems: items.filter((i) => relatedIds.has(i.id)),
    };
  }, [selectedNodeId, links, items]);

  return {
    enhancedNodes,
    filteredNodes,
    filteredLinks,
    incomingLinks,
    outgoingLinks,
    perspectiveCounts,
    relatedItems,
    selectedNode,
  };
}
