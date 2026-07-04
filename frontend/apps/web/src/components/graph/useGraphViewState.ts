import type { ChangeEvent } from 'react';

import { Network } from 'lucide-react';
import { useCallback, useMemo, useState } from 'react';

import type { GraphViewMode, ViewConfig } from './GraphViewConfig';
import type { GraphPerspective } from './types';

import { VIEW_CONFIGS } from './GraphViewConfig';
import { PERSPECTIVE_CONFIGS } from './types';

interface GraphViewLists {
  diagramViews: ViewConfig[];
  graphViews: ViewConfig[];
  perspectiveViews: ViewConfig[];
}

interface UseGraphViewStateInput {
  defaultView: GraphViewMode;
}

interface UseGraphViewStateOutput {
  currentConfig: ViewConfig;
  filteredDiagramViews: ViewConfig[];
  filteredGraphViews: ViewConfig[];
  filteredPerspectiveViews: ViewConfig[];
  getPerspective: (mode: GraphViewMode) => GraphPerspective | undefined;
  handleSelectChange: (mode: string) => void;
  handleViewTypeSearchChange: (event: ChangeEvent<HTMLInputElement>) => void;
  perspectiveColor: string | undefined;
  viewMode: GraphViewMode;
  viewTypeSearch: string;
}

const DEFAULT_PERSPECTIVE_COLOR = '#64748b';
const DEFAULT_SEARCH = '';

const PROJECT_VIEW_CONFIG: ViewConfig = {
  category: 'graph',
  description: '',
  icon: Network,
  id: 'traceability',
  label: '',
};

function filterViewsBySearch(list: ViewConfig[], searchLower: string): ViewConfig[] {
  if (!searchLower) {
    return list;
  }

  return list.filter(
    (config) =>
      config.label.toLowerCase().includes(searchLower) ||
      config.description.toLowerCase().includes(searchLower),
  );
}

function getPerspectiveColor(perspective: GraphPerspective | undefined): string | undefined {
  if (!perspective) {
    return undefined;
  }

  const config = PERSPECTIVE_CONFIGS.find((entry) => entry.id === perspective);
  return config?.color ?? DEFAULT_PERSPECTIVE_COLOR;
}

function getPerspectiveFromMode(mode: GraphViewMode): GraphPerspective | undefined {
  const config = VIEW_CONFIGS.find((entry) => entry.id === mode);
  return config?.perspective;
}

function getCurrentConfig(viewMode: GraphViewMode): ViewConfig {
  return VIEW_CONFIGS.find((entry) => entry.id === viewMode) ?? PROJECT_VIEW_CONFIG;
}

const GRAPH_VIEW_LISTS: GraphViewLists = {
  diagramViews: VIEW_CONFIGS.filter((entry) => entry.category === 'diagram'),
  graphViews: VIEW_CONFIGS.filter((entry) => entry.category === 'graph'),
  perspectiveViews: VIEW_CONFIGS.filter((entry) => entry.category === 'perspective'),
};

function useGraphViewState({ defaultView }: UseGraphViewStateInput): UseGraphViewStateOutput {
  const [viewMode, setViewMode] = useState<GraphViewMode>(defaultView);
  const [viewTypeSearch, setViewTypeSearch] = useState(DEFAULT_SEARCH);

  const currentConfig = useMemo(() => getCurrentConfig(viewMode), [viewMode]);

  const perspectiveColor = useMemo(
    () => getPerspectiveColor(currentConfig?.perspective),
    [currentConfig],
  );

  const handleViewTypeSearchChange = useCallback((event: ChangeEvent<HTMLInputElement>): void => {
    setViewTypeSearch(event.target.value);
  }, []);

  const handleSelectChange = useCallback((mode: string): void => {
    setViewMode(mode as GraphViewMode);
    setViewTypeSearch(DEFAULT_SEARCH);
  }, []);

  const getPerspective = useCallback(
    (mode: GraphViewMode): GraphPerspective | undefined => getPerspectiveFromMode(mode),
    [],
  );

  const searchLower = useMemo(() => viewTypeSearch.trim().toLowerCase(), [viewTypeSearch]);

  const filteredGraphViews = useMemo(
    () => filterViewsBySearch(GRAPH_VIEW_LISTS.graphViews, searchLower),
    [searchLower],
  );
  const filteredDiagramViews = useMemo(
    () => filterViewsBySearch(GRAPH_VIEW_LISTS.diagramViews, searchLower),
    [searchLower],
  );
  const filteredPerspectiveViews = useMemo(
    () => filterViewsBySearch(GRAPH_VIEW_LISTS.perspectiveViews, searchLower),
    [searchLower],
  );

  return {
    currentConfig,
    filteredDiagramViews,
    filteredGraphViews,
    filteredPerspectiveViews,
    getPerspective,
    handleSelectChange,
    handleViewTypeSearchChange,
    perspectiveColor,
    viewMode,
    viewTypeSearch,
  };
}

export { useGraphViewState };
