import { useParams } from '@tanstack/react-router';
import { useCallback } from 'react';
import { toast } from 'sonner';

import { ItemDetailPage } from '@/views/item-detail/components/ItemDetailPage';
import { LoadingView } from '@/views/item-detail/components/LoadingView';
import { NotFoundView } from '@/views/item-detail/components/NotFoundView';
import { useItemDetailViewModel } from '@/views/item-detail/view-model';

type ParamsRecord = Record<string, unknown>;

function isRecord(value: unknown): value is ParamsRecord {
  if (value === null) {
    return false;
  }
  return typeof value === 'object';
}

function readParam(params: unknown, key: string): string | undefined {
  if (!isRecord(params)) {
    return;
  }
  const value = params[key];
  if (typeof value !== 'string') {
    return;
  }
  const trimmed = value.trim();
  if (trimmed.length === 0) {
    return;
  }
  return trimmed;
}

export function ItemDetailView(): JSX.Element {
  const params = useParams({ strict: false });
  const itemId = readParam(params, 'itemId');
  const projectId = readParam(params, 'projectId');
  const viewTypeParam = readParam(params, 'viewType');

  const model = useItemDetailViewModel({ itemId, projectId, viewTypeParam });

  const handleShare = useCallback((): void => {
    toast.info(globalThis.location.href);
  }, []);

  const handleOpenNewTab = useCallback((): void => {
    globalThis.open(globalThis.location.href, '_blank', 'noopener,noreferrer');
  }, []);

  const handleStartEdit = useCallback((): void => {
    model.startEditing();
  }, [model]);

  const handleCancelEdit = useCallback((): void => {
    model.cancelEditing();
  }, [model]);

  const handleCreateSpec = useCallback(
    (specType: string): void => {
      model.createSpec(specType);
    },
    [model],
  );

  const handleChangeTitle = useCallback(
    (value: string): void => {
      model.setDraftTitle(value);
    },
    [model],
  );

  const handleChangeDescription = useCallback(
    (value: string): void => {
      model.setDraftDescription(value);
    },
    [model],
  );

  const handleChangeOwner = useCallback(
    (value: string): void => {
      model.setDraftOwner(value);
    },
    [model],
  );

  const handleChangeStatus = useCallback(
    (value: Parameters<typeof model.setDraftStatus>[0]): void => {
      model.setDraftStatus(value);
    },
    [model],
  );

  const handleChangePriority = useCallback(
    (value: Parameters<typeof model.setDraftPriority>[0]): void => {
      model.setDraftPriority(value);
    },
    [model],
  );

  const { query } = model;
  if (query.kind === 'loading') {
    return <LoadingView />;
  }

  if (query.kind === 'not_found') {
    return <NotFoundView message={query.message} onBack={model.handleBack} />;
  }

  return (
    <ItemDetailPage
      itemId={model.itemId ?? query.item.id}
      item={query.item}
      projectId={query.item.projectId}
      isEditing={model.isEditing}
      draftTitle={model.draft.title}
      draftDescription={model.draft.description}
      draftOwner={model.draft.owner}
      displayStatus={model.displayStatus}
      displayPriority={model.displayPriority}
      createdAtLabel={model.createdAtLabel}
      updatedAtLabel={model.updatedAtLabel}
      upstreamCount={model.upstreamCount}
      downstreamCount={model.downstreamCount}
      metadataCount={model.metadataCount}
      targetLinks={model.targetLinks}
      sourceLinks={model.sourceLinks}
      metadataSearch={model.metadataSearch}
      setMetadataSearch={model.setMetadataSearch}
      integrationMetadata={model.integrationMetadata}
      generalMetadata={model.generalMetadata}
      dimensionEntries={model.dimensionEntries}
      timelineEvents={model.timelineEvents}
      buildLinkToItem={model.buildLinkToItem}
      onBack={model.handleBack}
      onStartEdit={handleStartEdit}
      onCancelEdit={handleCancelEdit}
      onSave={model.handleSave}
      onDelete={model.handleDelete}
      onShare={handleShare}
      onOpenNewTab={handleOpenNewTab}
      onRunAnalysis={model.handleRunAnalysis}
      onOpenImpactAnalysis={model.handleOpenImpactAnalysis}
      onCreateSpec={handleCreateSpec}
      onChangeTitle={handleChangeTitle}
      onChangeDescription={handleChangeDescription}
      onChangeOwner={handleChangeOwner}
      onChangeStatus={handleChangeStatus}
      onChangePriority={handleChangePriority}
    />
  );
}
