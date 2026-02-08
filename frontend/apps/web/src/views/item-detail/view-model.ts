import { useCallback, useEffect, useMemo, useState } from 'react';

import type { Item, ItemStatus, Priority } from '@tracertm/types';

import { useItem } from '@/hooks/useItems';
import { useLinks } from '@/hooks/useLinks';

import {
  reportAnalysisComplete,
  reportDeleteFailure,
  reportImpactComplete,
  reportNoImpact,
  reportNoRelationships,
  reportSaveFailure,
} from './actions';
import { useItemMutations } from './item-mutations';
import {
  buildItemLink,
  buildTimelineEvents,
  createdAtLabel,
  defaultViewTypeFromParams,
  dimensionEntries,
  filterMetadata,
  metadataEntries,
  readLinksFromResponse,
  splitMetadata,
  updatedAtLabel,
} from './selectors';
import { useSpecActions } from './spec-actions';
import { EMPTY_STRING, type DraftState, type ItemQueryState } from './types';

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

  sourceLinks: ReturnType<typeof readLinksFromResponse>;
  targetLinks: ReturnType<typeof readLinksFromResponse>;

  metadataSearch: string;
  setMetadataSearch: (value: string) => void;
  filteredMetadata: ReturnType<typeof filterMetadata>;
  integrationMetadata: ReturnType<typeof splitMetadata>['integration'];
  generalMetadata: ReturnType<typeof splitMetadata>['general'];

  dimensionEntries: ReturnType<typeof dimensionEntries>;
  timelineEvents: ReturnType<typeof buildTimelineEvents>;

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
  sourceLinks: ReturnType<typeof readLinksFromResponse>;
  targetLinks: ReturnType<typeof readLinksFromResponse>;
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

  const sourceLinks = useMemo(() => readLinksFromResponse(sourceLinksData), [sourceLinksData]);
  const targetLinks = useMemo(() => readLinksFromResponse(targetLinksData), [targetLinksData]);

  return useMemo(() => {
    const upstreamCount = targetLinks.length;
    const downstreamCount = sourceLinks.length;
    return { sourceLinks, targetLinks, upstreamCount, downstreamCount };
  }, [sourceLinks, targetLinks]);
}

interface MetadataState {
  metadataSearch: string;
  setMetadataSearch: (value: string) => void;
  filteredMetadata: ReturnType<typeof filterMetadata>;
  integrationMetadata: ReturnType<typeof splitMetadata>['integration'];
  generalMetadata: ReturnType<typeof splitMetadata>['general'];
  metadataCount: number;
}

function useMetadataState(item: Item | undefined): MetadataState {
  const [metadataSearch, setMetadataSearchState] = useState<string>(EMPTY_STRING);

  const setMetadataSearch = useCallback((value: string): void => {
    setMetadataSearchState(value);
  }, []);

  const allMetadataEntries = useMemo(() => metadataEntries(item), [item]);
  const metadataCount = allMetadataEntries.length;

  const filteredMetadata = useMemo(
    () => filterMetadata(allMetadataEntries, metadataSearch),
    [allMetadataEntries, metadataSearch],
  );

  const { integration: integrationMetadata, general: generalMetadata } = useMemo(
    () => splitMetadata(filteredMetadata),
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

export function useItemDetailViewModel(params: Params): ItemDetailViewModel {
  const { itemId, projectId, viewTypeParam } = params;
  const itemQuery = useItem(itemId ?? EMPTY_STRING);
  const item = itemQuery.data;

  const query = useMemo(
    () => buildQueryState(itemId, item, itemQuery.isLoading, itemQuery.error),
    [item, itemId, itemQuery.error, itemQuery.isLoading],
  );

  const viewType = useMemo(
    () => defaultViewTypeFromParams(viewTypeParam, item?.view),
    [item?.view, viewTypeParam],
  );

  const [isEditing, setIsEditing] = useState<boolean>(false);

  const {
    draft,
    resetDraft,
    setDraftTitle,
    setDraftDescription,
    setDraftOwner,
    setDraftStatus,
    setDraftPriority,
  } = useDraftState(item);

  const {
    metadataSearch,
    setMetadataSearch,
    filteredMetadata,
    integrationMetadata,
    generalMetadata,
    metadataCount,
  } = useMetadataState(item);

  const { sourceLinks, targetLinks, upstreamCount, downstreamCount } = useLinksState(item, itemId);

  const dims = useMemo(() => dimensionEntries(item), [item]);
  const events = useMemo(
    () => buildTimelineEvents(item, integrationMetadata),
    [integrationMetadata, item],
  );

  const createdLabel = useMemo(() => createdAtLabel(item), [item]);
  const updatedLabel = useMemo(() => updatedAtLabel(item), [item]);

  const displayStatus = useMemo(
    () => buildDisplayStatus(isEditing, draft, item),
    [draft, isEditing, item],
  );
  const displayPriority = useMemo(
    () => buildDisplayPriority(isEditing, draft, item),
    [draft, isEditing, item],
  );

  const buildLinkToItem = useCallback(
    (id: string): string => buildItemLink(projectId, viewType, id),
    [projectId, viewType],
  );

  const handleBack = useCallback((): void => {
    globalThis.history.back();
  }, []);

  const startEditing = useCallback((): void => {
    setIsEditing(true);
  }, []);

  const cancelEditing = useCallback((): void => {
    if (item) {
      resetDraft();
    }
    setIsEditing(false);
  }, [item, resetDraft]);

  const { deleteItem, saveItem } = useItemMutations(item);
  const { createSpec: createSpecAsync } = useSpecActions(item?.projectId);

  const handleDelete = useCallback((): void => {
    if (itemId === undefined) {
      return;
    }
    const task = async (): Promise<void> => {
      try {
        await deleteItem(itemId);
        handleBack();
      } catch {
        reportDeleteFailure();
      }
    };
    task().catch(() => {});
  }, [deleteItem, handleBack, itemId]);

  const handleSave = useCallback((): void => {
    if (itemId === undefined || item === undefined) {
      return;
    }
    const task = async (): Promise<void> => {
      try {
        await saveItem({
          id: itemId,
          title: draft.title,
          description: draft.description,
          owner: draft.owner,
          status: draft.status,
          priority: draft.priority,
        });
        setIsEditing(false);
      } catch {
        reportSaveFailure();
      }
    };
    task().catch(() => {});
  }, [draft, item, itemId, saveItem]);

  const handleRunAnalysis = useCallback((): void => {
    if (sourceLinks.length === 0 && targetLinks.length === 0) {
      reportNoRelationships();
      return;
    }
    const total = sourceLinks.length + targetLinks.length;
    reportAnalysisComplete(total);
  }, [sourceLinks.length, targetLinks.length]);

  const handleOpenImpactAnalysis = useCallback((): void => {
    const impactCount = upstreamCount + downstreamCount;
    if (impactCount === 0) {
      reportNoImpact();
      return;
    }
    reportImpactComplete(impactCount);
  }, [downstreamCount, upstreamCount]);

  const createSpec = useCallback(
    (specType: string): void => {
      const task = async (): Promise<void> => {
        await createSpecAsync(specType, itemId);
      };
      task().catch(() => {});
    },
    [createSpecAsync, itemId],
  );

  return {
    query,
    itemId,
    projectId,
    viewType,

    isEditing,
    draft,

    upstreamCount,
    downstreamCount,
    metadataCount,

    displayStatus,
    displayPriority,

    createdAtLabel: createdLabel,
    updatedAtLabel: updatedLabel,

    sourceLinks,
    targetLinks,

    metadataSearch,
    setMetadataSearch,
    filteredMetadata,
    integrationMetadata,
    generalMetadata,

    dimensionEntries: dims,
    timelineEvents: events,

    buildLinkToItem,

    startEditing,
    cancelEditing,

    setDraftTitle,
    setDraftDescription,
    setDraftOwner,
    setDraftStatus,
    setDraftPriority,

    handleBack,
    handleDelete,
    handleSave,
    handleRunAnalysis,
    handleOpenImpactAnalysis,

    createSpec,
  };
}

export type { ItemDetailViewModel };
