import { useParams } from '@tanstack/react-router';
import { useCallback, useMemo, useState } from 'react';

import { UnifiedGraphView } from '../components/graph/UnifiedGraphView';
import { useGraphProjection, useGraphs } from '../hooks/useGraphs';

const MAX_EDGES_INITIAL = 500;
const EDGES_LOAD_MORE = 500;

function deriveItems(graphData: { nodes?: unknown[] } | undefined) {
  const nodes = graphData?.nodes ?? [];
  return nodes.map((node: any) =>
    Object.assign(node, {
      id: node.id,
      title: node.title,
      type: node.item_type ?? node.itemType ?? node.view,
      view: node.view,
    }),
  );
}

function deriveLinks(graphData: { links?: unknown[] } | undefined) {
  return (graphData?.links ?? []).map((link: any) =>
    Object.assign(link, {
      sourceId: link.source_item_id ?? link.sourceId,
      targetId: link.target_item_id ?? link.targetId,
      type: link.link_type ?? link.type,
    }),
  );
}

export const ProjectMappingGraphView = () => {
  const { projectId } = useParams({ strict: false });
  const [visibleEdgeCount, setVisibleEdgeCount] = useState(MAX_EDGES_INITIAL);

  const { data: graphsData } = useGraphs(projectId);
  const mappingGraph = useMemo(
    () => graphsData?.find((g) => g.graphType === 'mapping') ?? graphsData?.[0],
    [graphsData],
  );
  const { data: graphData, isLoading } = useGraphProjection(projectId, mappingGraph?.id);

  const items = useMemo(() => deriveItems(graphData), [graphData]);
  const links = useMemo(() => deriveLinks(graphData), [graphData]);

  const visibleLinks = links.slice(0, visibleEdgeCount);
  const canLoadMore = visibleEdgeCount < links.length;
  const handleLoadMoreEdges = useCallback(() => {
    setVisibleEdgeCount((prev) => Math.min(prev + EDGES_LOAD_MORE, links.length));
  }, [links.length]);

  const handleNavigateToItem = useCallback((_itemId: string) => {}, []);

  return (
    <UnifiedGraphView
      items={items}
      links={visibleLinks}
      isLoading={isLoading}
      projectId={projectId ?? ''}
      onNavigateToItem={handleNavigateToItem}
      defaultView='components'
      canLoadMore={canLoadMore}
      visibleEdges={visibleLinks.length}
      totalEdges={links.length}
      onLoadMore={handleLoadMoreEdges}
    />
  );
};
