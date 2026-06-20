import { useMemo, useState } from 'react';

import type { Item, Link } from '@tracertm/types';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';

import { UnifiedGraphView } from '../components/graph/UnifiedGraphView';
import { useGraphProjection, useGraphs } from '../hooks/useGraphs';

interface GraphViewProps {
  projectId: string;
}

type SafeRecord = Record<string, unknown>;

interface GraphOption {
  id: string;
  name: string;
  graphType: string;
}

interface NormalizedNode extends SafeRecord {
  id: string;
  title: string;
  type: string;
  view: string;
}

interface NormalizedLink extends SafeRecord {
  id: string;
  sourceId: string;
  targetId: string;
  type: string;
}

const DEFAULT_ITEM_VIEW: Item['view'] = 'feature';
const DEFAULT_ITEM_TYPE = 'item';
const DEFAULT_ITEM_TITLE = 'Untitled';
const DEFAULT_ITEM_STATUS: Item['status'] = 'todo';
const DEFAULT_ITEM_PRIORITY: Item['priority'] = 'medium';
const DEFAULT_LINK_TYPE: Link['type'] = 'related_to';
const DEFAULT_VERSION = 1;
const DEFAULT_TIMESTAMP = '1970-01-01T00:00:00.000Z';

const VIEW_TYPES = new Set<Item['view']>([
  'FEATURE',
  'feature',
  'CODE',
  'code',
  'TEST',
  'test',
  'API',
  'api',
  'DATABASE',
  'database',
  'WIREFRAME',
  'wireframe',
  'DOCUMENTATION',
  'documentation',
  'DEPLOYMENT',
  'deployment',
  'architecture',
  'configuration',
  'dataflow',
  'dependency',
  'domain',
  'infrastructure',
  'journey',
  'monitoring',
  'performance',
  'security',
]);

const LINK_TYPES = new Set<Link['type']>([
  'implements',
  'tests',
  'depends_on',
  'related_to',
  'blocks',
  'parent_of',
  'same_as',
  'represents',
  'manifests_as',
  'documents',
  'mentions',
  'calls',
  'imports',
  'derives_from',
  'alternative_to',
  'conflicts_with',
  'supersedes',
  'validates',
  'traces_to',
]);

const isSafeRecord = (value: unknown): value is SafeRecord =>
  typeof value === 'object' && value !== null;

const asSafeRecordArray = (value: unknown): SafeRecord[] =>
  Array.isArray(value) ? value.filter((entry) => isSafeRecord(entry)) : [];

const asOptionalString = (value: unknown): string | undefined =>
  typeof value === 'string' ? value : undefined;

const asString = (value: unknown, fallback = ''): string => asOptionalString(value) ?? fallback;

const toViewType = (value: string): Item['view'] =>
  VIEW_TYPES.has(value as Item['view']) ? (value as Item['view']) : DEFAULT_ITEM_VIEW;

const toLinkType = (value: string): Link['type'] =>
  LINK_TYPES.has(value as Link['type']) ? (value as Link['type']) : DEFAULT_LINK_TYPE;

const normalizeGraph = (graph: SafeRecord): GraphOption => ({
  ...graph,
  id: asString(graph['id']),
  name: asString(graph['name']),
  graphType: asString(graph['graphType']),
});

const normalizeNode = (node: SafeRecord): NormalizedNode =>
  ({
    ...node,
    id: asString(node['id']),
    title: asString(node['title']),
    type: asString(node['item_type']) || asString(node['itemType']) || asString(node['view']),
    view: asString(node['view']),
  }) as NormalizedNode;

const normalizeLink = (link: SafeRecord): NormalizedLink =>
  ({
    ...link,
    id: asString(link['id']),
    sourceId: asString(link['source_item_id']) || asString(link['sourceId']),
    targetId: asString(link['target_item_id']) || asString(link['targetId']),
    type: asString(link['link_type']) || asString(link['type']),
  }) as NormalizedLink;

const toItem = (node: NormalizedNode, projectId: string): Item => {
  const description = asOptionalString(node['description']);
  const parentId = asOptionalString(node['parentId']);
  const owner = asOptionalString(node['owner']);

  return {
    id: node.id,
    projectId,
    view: toViewType(node.view),
    type: node.type.length > 0 ? node.type : DEFAULT_ITEM_TYPE,
    title: node.title.length > 0 ? node.title : DEFAULT_ITEM_TITLE,
    status: DEFAULT_ITEM_STATUS,
    priority: DEFAULT_ITEM_PRIORITY,
    metadata: node,
    version: DEFAULT_VERSION,
    createdAt: asString(node['createdAt'], DEFAULT_TIMESTAMP),
    updatedAt: asString(node['updatedAt'], DEFAULT_TIMESTAMP),
    ...(description !== undefined ? { description } : {}),
    ...(parentId !== undefined ? { parentId } : {}),
    ...(owner !== undefined ? { owner } : {}),
  };
};

const toLink = (link: NormalizedLink, projectId: string): Link => {
  const description = asOptionalString(link['description']);

  return {
    id:
      link.id.length > 0
        ? link.id
        : `${link.sourceId}:${link.targetId}:${toLinkType(asString(link.type, DEFAULT_LINK_TYPE))}`,
    projectId,
    sourceId: link.sourceId,
    targetId: link.targetId,
    type: toLinkType(link.type),
    metadata: link,
    createdAt: asString(link['createdAt'], DEFAULT_TIMESTAMP),
    updatedAt: asString(link['updatedAt'], DEFAULT_TIMESTAMP),
    version: DEFAULT_VERSION,
    ...(description !== undefined ? { description } : {}),
  };
};

const handleNavigateToItem = (_itemId: string): void => {};

export function GraphView({ projectId }: GraphViewProps): JSX.Element {
  const { data: graphsData } = useGraphs(projectId);
  const [selectedGraphId, setSelectedGraphId] = useState<string | undefined>();
  const [overlayMode, setOverlayMode] = useState('off');
  const overlayMapping = overlayMode === 'on';

  const graphs = useMemo(
    () => asSafeRecordArray(graphsData).map((graph) => normalizeGraph(graph)),
    [graphsData],
  );

  const selectedGraph = useMemo(() => {
    if (graphs.length === 0) {
      return;
    }
    if (selectedGraphId !== undefined && selectedGraphId.length > 0) {
      return graphs.find((graph) => graph.id === selectedGraphId);
    }
    return graphs[0];
  }, [graphs, selectedGraphId]);

  const { data: graphData, isLoading: graphLoading } = useGraphProjection(
    projectId,
    selectedGraph?.id,
  );

  const mappingGraph = useMemo(
    () => graphs.find((graph) => graph.graphType === 'mapping'),
    [graphs],
  );

  const { data: mappingData } = useGraphProjection(
    projectId,
    overlayMapping ? mappingGraph?.id : undefined,
  );

  const items = useMemo(() => {
    const graphProjection = isSafeRecord(graphData) ? graphData : undefined;
    const nodes = asSafeRecordArray(graphProjection?.nodes);
    return nodes.map((node) => toItem(normalizeNode(node), projectId));
  }, [graphData, projectId]);

  const links = useMemo(() => {
    const graphProjection = isSafeRecord(graphData) ? graphData : undefined;
    const baseLinks = asSafeRecordArray(graphProjection?.links).map((link) =>
      toLink(normalizeLink(link), projectId),
    );
    const mappingProjection = isSafeRecord(mappingData) ? mappingData : undefined;
    const mappingLinks = asSafeRecordArray(mappingProjection?.links);

    if (!overlayMapping || mappingLinks.length === 0) {
      return baseLinks;
    }

    const itemIds = new Set(items.map((item) => item.id));
    const overlayLinks = mappingLinks
      .map((link) => toLink(normalizeLink(link), projectId))
      .filter((link) => itemIds.has(link.sourceId) && itemIds.has(link.targetId));

    return [...baseLinks, ...overlayLinks];
  }, [graphData, mappingData, overlayMapping, items, projectId]);

  const canLoadMore = false;

  return (
    <div className='animate-in-fade-up space-y-4'>
      <div className='flex flex-wrap items-center gap-4'>
        <div className='min-w-[220px]'>
          <Select value={selectedGraph?.id ?? ''} onValueChange={setSelectedGraphId}>
            <SelectTrigger>
              <SelectValue placeholder='Select graph' />
            </SelectTrigger>
            <SelectContent>
              {graphs.map((graph) => (
                <SelectItem key={graph.id} value={graph.id}>
                  {graph.name} ({graph.graphType})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className='min-w-[220px]'>
          <Select value={overlayMode} onValueChange={setOverlayMode}>
            <SelectTrigger>
              <SelectValue placeholder='Mapping overlay' />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='off'>Mapping overlay: Off</SelectItem>
              <SelectItem value='on'>Mapping overlay: On</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <UnifiedGraphView
        items={items}
        links={links}
        isLoading={graphLoading}
        projectId={projectId}
        onNavigateToItem={handleNavigateToItem}
        canLoadMore={canLoadMore}
        visibleEdges={links.length}
        totalEdges={links.length}
      />
    </div>
  );
}
