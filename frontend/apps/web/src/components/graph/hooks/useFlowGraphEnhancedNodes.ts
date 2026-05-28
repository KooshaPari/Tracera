import { useCallback, useEffect, useMemo, useState } from 'react';

import type { Item, Link, LinkType } from '@tracertm/types';

import {
  EMPTY_CONNECTIONS,
  GRAPH_EMPTY_LABEL,
  LEGEND_TYPE_LIMIT,
  MAX_ITEM_DEPTH,
  MAX_RENDERED_NODES,
  NODES_PER_BATCH,
} from '../flow-graph-view/flowGraphConstants';
import {
  PERSPECTIVE_CONFIGS,
  TYPE_TO_PERSPECTIVE,
  type EnhancedNodeData,
  type GraphPerspective,
} from '../types';

export function useFlowGraphEnhancedNodes(
  items: Item[],
  links: Link[],
  perspective: GraphPerspective,
) {
  const parentMap = useMemo(() => {
    const map = new Map<string, Set<string>>();
    items.forEach((item) => {
      const parentId = item.parentId;
      if (typeof parentId === 'string' && parentId.length > 0) {
        if (!map.has(parentId)) {
          map.set(parentId, new Set());
        }
        const childSet = map.get(parentId);
        if (childSet !== undefined) {
          childSet.add(item.id);
        }
      }
    });
    return map;
  }, [items]);

  const createNodeData = useCallback(
    (
      item: Item,
      itemMap: Map<string, Item>,
      incomingCount: Map<string, number>,
      outgoingCount: Map<string, number>,
      connectionsByType: Map<string, Record<LinkType, number>>,
    ): EnhancedNodeData => {
      const itemType = (item.type || item.view || 'item').toLowerCase();
      const perspectives = TYPE_TO_PERSPECTIVE[itemType] ?? ['all'];
      const incoming = incomingCount.get(item.id) ?? 0;
      const outgoing = outgoingCount.get(item.id) ?? 0;
      const hasChildren = parentMap.has(item.id);

      let depth = 0;
      let currentId = item.parentId;
      while (typeof currentId === 'string' && currentId.length > 0 && depth < MAX_ITEM_DEPTH) {
        depth += 1;
        const parent = itemMap.get(currentId);
        currentId = parent?.parentId;
      }

      const screenshotUrlRaw = item.metadata?.['screenshotUrl'];
      const screenshotUrl =
        typeof screenshotUrlRaw === 'string' && screenshotUrlRaw.length > 0
          ? screenshotUrlRaw
          : undefined;
      const codeRaw = item.metadata?.['code'];
      const interactiveUrlRaw = item.metadata?.['interactiveUrl'];
      const thumbnailUrlRaw = item.metadata?.['thumbnailUrl'];

      return {
        connections: {
          byType: connectionsByType.get(item.id) ?? EMPTY_CONNECTIONS,
          incoming,
          outgoing,
          total: incoming + outgoing,
        },
        depth,
        hasChildren,
        id: item.id,
        item,
        label: item.title ?? GRAPH_EMPTY_LABEL,
        parentId: item.parentId,
        perspective: perspectives,
        status: item.status,
        type: itemType,
        uiPreview:
          screenshotUrl !== undefined
            ? {
                componentCode: typeof codeRaw === 'string' ? codeRaw : undefined,
                interactiveWidgetUrl:
                  typeof interactiveUrlRaw === 'string' ? interactiveUrlRaw : undefined,
                screenshotUrl,
                thumbnailUrl: typeof thumbnailUrlRaw === 'string' ? thumbnailUrlRaw : undefined,
              }
            : undefined,
      } as EnhancedNodeData;
    },
    [parentMap],
  );

  const enhancedNodes = useMemo((): EnhancedNodeData[] => {
    const itemMap = new Map(items.map((item) => [item.id, item]));

    const incomingCount = new Map<string, number>();
    const outgoingCount = new Map<string, number>();
    const connectionsByType = new Map<string, Record<LinkType, number>>();
    const ensureConnectionBucket = (itemId: string): Record<LinkType, number> => {
      const existing = connectionsByType.get(itemId);
      if (existing !== undefined) {
        return existing;
      }
      const created = {} as Record<LinkType, number>;
      connectionsByType.set(itemId, created);
      return created;
    };

    for (const link of links) {
      incomingCount.set(link.targetId, (incomingCount.get(link.targetId) ?? 0) + 1);
      outgoingCount.set(link.sourceId, (outgoingCount.get(link.sourceId) ?? 0) + 1);

      const targetTypes = ensureConnectionBucket(link.targetId);
      targetTypes[link.type] = (targetTypes[link.type] || 0) + 1;

      const sourceTypes = ensureConnectionBucket(link.sourceId);
      sourceTypes[link.type] = (sourceTypes[link.type] || 0) + 1;
    }

    return items.map((item) =>
      createNodeData(item, itemMap, incomingCount, outgoingCount, connectionsByType),
    );
  }, [items, links, createNodeData]);

  const nodeMap = useMemo(() => new Map(enhancedNodes.map((n) => [n.id, n])), [enhancedNodes]);

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

  const visibleTypes = useMemo(() => {
    const types = new Set<string>();
    for (const node of filteredNodes) {
      types.add(node.type);
      if (types.size >= LEGEND_TYPE_LIMIT) {
        break;
      }
    }
    return types;
  }, [filteredNodes]);

  const [renderedNodeBatch, setRenderedNodeBatch] = useState(0);

  useEffect(() => {
    if (filteredNodes.length === 0) {
      setRenderedNodeBatch(0);
      return undefined;
    }

    const maxBatches = Math.ceil(MAX_RENDERED_NODES / NODES_PER_BATCH);
    const totalBatches = Math.min(Math.ceil(filteredNodes.length / NODES_PER_BATCH), maxBatches);
    if (renderedNodeBatch < totalBatches) {
      const timerId = requestAnimationFrame((): void => {
        setRenderedNodeBatch((prev) => prev + 1);
      });
      return (): void => {
        cancelAnimationFrame(timerId);
      };
    }
    return undefined;
  }, [filteredNodes.length, renderedNodeBatch]);

  const visibleNodes = useMemo(() => {
    const maxVisible = Math.min((renderedNodeBatch + 1) * NODES_PER_BATCH, MAX_RENDERED_NODES);
    return filteredNodes.slice(0, maxVisible);
  }, [filteredNodes, renderedNodeBatch]);

  const visibleLinks = useMemo(() => {
    const visibleNodeIds = new Set(visibleNodes.map((n) => n.id));
    return filteredLinks.filter(
      (link) => visibleNodeIds.has(link.sourceId) && visibleNodeIds.has(link.targetId),
    );
  }, [filteredLinks, visibleNodes]);

  return {
    enhancedNodes,
    filteredLinks,
    filteredNodes,
    nodeMap,
    visibleLinks,
    visibleNodes,
    visibleTypes,
  };
}
