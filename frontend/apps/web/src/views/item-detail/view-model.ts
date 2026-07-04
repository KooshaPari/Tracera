import { useCallback, useEffect, useMemo, useState } from 'react';

import type { Item, ItemStatus, Priority } from '@tracertm/types';

import { useItem } from '@/hooks/useItems';
import { useLinks } from '@/hooks/useLinks';

import type { DraftState, ItemQueryState } from './types';

import { itemDetailSelectors as selectors } from './selectors-facade';
import { EMPTY_STRING } from './types';
import { useItemDetailViewModelActions } from './view-model-actions';

const DEFAULT_STATUS: ItemStatus = 'todo';
const DEFAULT_PRIORITY: Priority = 'medium';

interface Params {
  itemId: string | undefined;
  projectId: string | undefined;
  viewTypeParam: string | undefined;
}

interface ItemDetailViewModel {
  query: ItemQueryState;

  itemId: string | undefined;
  projectId: string | undefined;
  viewType: string;

  isEditing: boolean;
  draft: DraftState;

  upstreamCount: number;
  downstreamCount: number;
  metadataCount: number;

  displayStatus: ItemStatus;
  displayPriority: Priority;

  createdAtLabel: string;
  updatedAtLabel: string;

  sourceLinks: ReturnType<typeof selectors.readLinksFromResponse>;
  targetLinks: ReturnType<typeof selectors.readLinksFromResponse>;

  metadataSearch: string;
  setMetadataSearch: (value: string) => void;
  filteredMetadata: ReturnType<typeof selectors.filterMetadata>;
  integrationMetadata: ReturnType<typeof selectors.splitMetadata>['integration'];
  generalMetadata: ReturnType<typeof selectors.splitMetadata>['general'];

  dimensionEntries: ReturnType<typeof selectors.dimensionEntries>;
  timelineEvents: ReturnType<typeof selectors.buildTimelineEvents>;

  buildLinkToItem: (id: string) => string;

  startEditing: () => void;
  cancelEditing: () => void;

  setDraftTitle: (value: string) => void;
  setDraftDescription: (value: string) => void;
  setDraftOwner: (value: string) => void;
  setDraftStatus: (value: ItemStatus) => void;
  setDraftPriority: (value: Priority) => void;

  handleBack: () => void;
  handleDelete: () => void;
  handleSave: () => void;
  handleRunAnalysis: () => void;
  handleOpenImpactAnalysis: () => void;

  createSpec: (specType: string) => void;
}

function draftFromItem(item: Item): DraftState {
  return {
    title: item.title ?? EMPTY_STRING,
    description: item.description ?? EMPTY_STRING,
    owner: item.owner ?? EMPTY_STRING,
    status: item.status ?? DEFAULT_STATUS,
    priority: item.priority ?? DEFAULT_PRIORITY,
  };
}

function buildQueryState(
  itemId: string | undefined,
  item: Item | undefined,
  isLoading: boolean,
  error: unknown,
): ItemQueryState {
  if (itemId === undefined) {
    return { kind: 'not_found', message: 'Item Not Found' };
  }
  if (isLoading) {
    return { kind: 'loading' };
  }
  if (error !== null && error !== undefined) {
    return { kind: 'not_found', message: 'Item Not Found' };
  }
  if (!item) {
    return { kind: 'not_found', message: 'Item Not Found' };
  }
  return { kind: 'ready', item };
}

function buildDisplayStatus(
  isEditing: boolean,
  draft: DraftState,
  item: Item | undefined,
): ItemStatus {
  if (isEditing) {
    return draft.status;
  }
  return item?.status ?? DEFAULT_STATUS;
}

function buildDisplayPriority(
  isEditing: boolean,
  draft: DraftState,
  item: Item | undefined,
): Priority {
  if (isEditing) {
    return draft.priority;
  }
  return item?.priority ?? DEFAULT_PRIORITY;
}

interface LinksState {
  sourceLinks: ReturnType<typeof selectors.readLinksFromResponse>;
  targetLinks: ReturnType<typeof selectors.readLinksFromResponse>;
  upstreamCount: number;
  downstreamCount: number;
}

function useLinksState(item: Item | undefined, itemId: string | undefined): LinksState {
  const { data: sourceLinksData } = useLinks({
    projectId: item?.projectId,
    sourceId: itemId,
  });
  const { data: targetLinksData } = useLinks({
    projectId: item?.projectId,
    targetId: itemId,
  });

  const sourceLinks = useMemo(
    () => selectors.readLinksFromResponse(sourceLinksData),
    [sourceLinksData],
  );
  const targetLinks = useMemo(
    () => selectors.readLinksFromResponse(targetLinksData),
    [targetLinksData],
  );

  return useMemo(() => {
    const upstreamCount = targetLinks.length;
    const downstreamCount = sourceLinks.length;
    return { sourceLinks, targetLinks, upstreamCount, downstreamCount };
  }, [sourceLinks, targetLinks]);
}

interface MetadataState {
  metadataSearch: string;
  setMetadataSearch: (value: string) => void;
  filteredMetadata: ReturnType<typeof selectors.filterMetadata>;
  integrationMetadata: ReturnType<typeof selectors.splitMetadata>['integration'];
  generalMetadata: ReturnType<typeof selectors.splitMetadata>['general'];
  metadataCount: number;
}

function useMetadataState(item: Item | undefined): MetadataState {
  const [metadataSearch, setMetadataSearchState] = useState<string>(EMPTY_STRING);

  const setMetadataSearch = useCallback((value: string): void => {
    setMetadataSearchState(value);
  }, []);

  const allMetadataEntries = useMemo(() => selectors.metadataEntries(item), [item]);
  const metadataCount = allMetadataEntries.length;

  const filteredMetadata = useMemo(
    () => selectors.filterMetadata(allMetadataEntries, metadataSearch),
    [allMetadataEntries, metadataSearch],
  );

  const { integration: integrationMetadata, general: generalMetadata } = useMemo(
    () => selectors.splitMetadata(filteredMetadata),
    [filteredMetadata],
  );

  return useMemo(
    () => ({
      metadataSearch,
      setMetadataSearch,
      filteredMetadata,
      integrationMetadata,
      generalMetadata,
      metadataCount,
    }),
    [
      filteredMetadata,
      generalMetadata,
      integrationMetadata,
      metadataCount,
      metadataSearch,
      setMetadataSearch,
    ],
  );
}

interface DraftActions {
  draft: DraftState;
  setDraftTitle: (value: string) => void;
  setDraftDescription: (value: string) => void;
  setDraftOwner: (value: string) => void;
  setDraftStatus: (value: ItemStatus) => void;
  setDraftPriority: (value: Priority) => void;
  resetDraft: () => void;
}

function useDraftState(item: Item | undefined): DraftActions {
  const [draft, setDraft] = useState<DraftState>({
    title: EMPTY_STRING,
    description: EMPTY_STRING,
    owner: EMPTY_STRING,
    status: DEFAULT_STATUS,
    priority: DEFAULT_PRIORITY,
  });

  useEffect(() => {
    if (!item) {
      return;
    }
    setDraft(draftFromItem(item));
  }, [item]);

  const resetDraft = useCallback((): void => {
    if (!item) {
      return;
    }
    setDraft(draftFromItem(item));
  }, [item]);

  const setDraftTitle = useCallback((value: string): void => {
    setDraft((prev) => ({ ...prev, title: value }));
  }, []);
  const setDraftDescription = useCallback((value: string): void => {
    setDraft((prev) => ({ ...prev, description: value }));
  }, []);
  const setDraftOwner = useCallback((value: string): void => {
    setDraft((prev) => ({ ...prev, owner: value }));
  }, []);
  const setDraftStatus = useCallback((value: ItemStatus): void => {
    setDraft((prev) => ({ ...prev, status: value }));
  }, []);
  const setDraftPriority = useCallback((value: Priority): void => {
    setDraft((prev) => ({ ...prev, priority: value }));
  }, []);

  return useMemo(
    () => ({
      draft,
      setDraftTitle,
      setDraftDescription,
      setDraftOwner,
      setDraftStatus,
      setDraftPriority,
      resetDraft,
    }),
    [
      draft,
      resetDraft,
      setDraftDescription,
      setDraftOwner,
      setDraftPriority,
      setDraftStatus,
      setDraftTitle,
    ],
  );
}

function useItemDetailViewModel(params: Params): ItemDetailViewModel {
  const { itemId, projectId, viewTypeParam } = params;
  const itemQuery = useItem(itemId ?? EMPTY_STRING);
  const item = itemQuery.data;

  const query = useMemo(
    () => buildQueryState(itemId, item, itemQuery.isLoading, itemQuery.error),
    [item, itemId, itemQuery.error, itemQuery.isLoading],
  );

  const viewType = useMemo(
    () => selectors.defaultViewTypeFromParams(viewTypeParam, item?.view),
    [item?.view, viewTypeParam],
  );

  const [isEditing, setIsEditing] = useState<boolean>(false);

  const draftState = useDraftState(item);
  const metadataState = useMetadataState(item);
  const linksState = useLinksState(item, itemId);

  const dims = useMemo(() => selectors.dimensionEntries(item), [item]);
  const events = useMemo(
    () => selectors.buildTimelineEvents(item, metadataState.integrationMetadata),
    [metadataState.integrationMetadata, item],
  );
  const createdLabel = useMemo(() => selectors.createdAtLabel(item), [item]);
  const updatedLabel = useMemo(() => selectors.updatedAtLabel(item), [item]);

  const displayStatus = useMemo(
    () => buildDisplayStatus(isEditing, draftState.draft, item),
    [draftState.draft, isEditing, item],
  );
  const displayPriority = useMemo(
    () => buildDisplayPriority(isEditing, draftState.draft, item),
    [draftState.draft, isEditing, item],
  );

  const vmActions = useItemDetailViewModelActions({
    itemId,
    projectId,
    viewType,
    item,
    draft: draftState.draft,
    resetDraft: draftState.resetDraft,
    setIsEditing,
    sourceLinks: linksState.sourceLinks,
    targetLinks: linksState.targetLinks,
    upstreamCount: linksState.upstreamCount,
    downstreamCount: linksState.downstreamCount,
  });

  return {
    query,
    itemId,
    projectId,
    viewType,
    isEditing,
    draft: draftState.draft,
    upstreamCount: linksState.upstreamCount,
    downstreamCount: linksState.downstreamCount,
    metadataCount: metadataState.metadataCount,
    displayStatus,
    displayPriority,
    createdAtLabel: createdLabel,
    updatedAtLabel: updatedLabel,
    sourceLinks: linksState.sourceLinks,
    targetLinks: linksState.targetLinks,
    metadataSearch: metadataState.metadataSearch,
    setMetadataSearch: metadataState.setMetadataSearch,
    filteredMetadata: metadataState.filteredMetadata,
    integrationMetadata: metadataState.integrationMetadata,
    generalMetadata: metadataState.generalMetadata,
    dimensionEntries: dims,
    timelineEvents: events,
    buildLinkToItem: vmActions.buildLinkToItem,
    startEditing: vmActions.startEditing,
    cancelEditing: vmActions.cancelEditing,
    setDraftTitle: draftState.setDraftTitle,
    setDraftDescription: draftState.setDraftDescription,
    setDraftOwner: draftState.setDraftOwner,
    setDraftStatus: draftState.setDraftStatus,
    setDraftPriority: draftState.setDraftPriority,
    handleBack: vmActions.handleBack,
    handleDelete: vmActions.handleDelete,
    handleSave: vmActions.handleSave,
    handleRunAnalysis: vmActions.handleRunAnalysis,
    handleOpenImpactAnalysis: vmActions.handleOpenImpactAnalysis,
    createSpec: vmActions.createSpec,
  };
}

export { useItemDetailViewModel, type ItemDetailViewModel };
