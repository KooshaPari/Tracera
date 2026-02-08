import { useCallback } from 'react';

import type { Item } from '@tracertm/types';

import type { DraftState } from './types';

import {
  reportAnalysisComplete,
  reportImpactComplete,
  reportNoImpact,
  reportNoRelationships,
} from './actions';
import { useItemMutations } from './item-mutations';
import { itemDetailSelectors as selectors } from './selectors-facade';
import { useSpecActions } from './spec-actions';

interface ViewModelActions {
  buildLinkToItem: (id: string) => string;
  handleBack: () => void;
  startEditing: () => void;
  cancelEditing: () => void;
  handleDelete: () => void;
  handleSave: () => void;
  handleRunAnalysis: () => void;
  handleOpenImpactAnalysis: () => void;
  createSpec: (specType: string) => void;
}

interface Inputs {
  itemId: string | undefined;
  projectId: string | undefined;
  viewType: string;
  item: Item | undefined;
  draft: DraftState;
  resetDraft: () => void;
  setIsEditing: (value: boolean) => void;
  sourceLinks: { length: number };
  targetLinks: { length: number };
  upstreamCount: number;
  downstreamCount: number;
}

export function useItemDetailViewModelActions(inputs: Inputs): ViewModelActions {
  const {
    itemId,
    projectId,
    viewType,
    item,
    draft,
    resetDraft,
    setIsEditing,
    sourceLinks,
    targetLinks,
    upstreamCount,
    downstreamCount,
  } = inputs;

  const buildLinkToItem = useCallback(
    (id: string): string => selectors.buildItemLink(projectId, viewType, id),
    [projectId, viewType],
  );

  const handleBack = useCallback((): void => {
    globalThis.history.back();
  }, []);

  const startEditing = useCallback((): void => {
    setIsEditing(true);
  }, [setIsEditing]);

  const cancelEditing = useCallback((): void => {
    if (item) {
      resetDraft();
    }
    setIsEditing(false);
  }, [item, resetDraft, setIsEditing]);

  const { deleteItem, saveItem } = useItemMutations(item);
  const { createSpec: createSpecAsync } = useSpecActions(item?.projectId);

  const handleDelete = useCallback((): void => {
    if (itemId === undefined) {
      return;
    }
    deleteItem(itemId, handleBack);
  }, [deleteItem, handleBack, itemId]);

  const handleSave = useCallback((): void => {
    if (itemId === undefined || item === undefined) {
      return;
    }
    saveItem(
      {
        id: itemId,
        title: draft.title,
        description: draft.description,
        owner: draft.owner,
        status: draft.status,
        priority: draft.priority,
      },
      () => {
        setIsEditing(false);
      },
    );
  }, [draft, item, itemId, saveItem, setIsEditing]);

  const handleRunAnalysis = useCallback((): void => {
    if (sourceLinks.length === 0 && targetLinks.length === 0) {
      reportNoRelationships();
      return;
    }
    reportAnalysisComplete(sourceLinks.length + targetLinks.length);
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
      createSpecAsync(specType, itemId);
    },
    [createSpecAsync, itemId],
  );

  return {
    buildLinkToItem,
    handleBack,
    startEditing,
    cancelEditing,
    handleDelete,
    handleSave,
    handleRunAnalysis,
    handleOpenImpactAnalysis,
    createSpec,
  };
}
