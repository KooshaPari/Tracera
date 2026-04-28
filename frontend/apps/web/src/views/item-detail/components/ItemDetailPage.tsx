import type { DimensionEntry, ItemLink, TimelineEvent } from '@/views/item-detail/types';
import type { Item, ItemStatus, Priority } from '@tracertm/types';

import { descriptionOrDefault, formatViewTypeLabel } from '@/views/item-detail/format';

import { ActivityTimelineCard } from './ActivityTimelineCard';
import { ChangeLogCard } from './ChangeLogCard';
import { DimensionsCard } from './DimensionsCard';
import { InsightCard } from './InsightCard';
import { ItemSummarySection } from './ItemSummarySection';
import { PageShell } from './PageShell';
import { ReferencesCard } from './ReferencesCard';
import { SignalStackCard } from './SignalStackCard';
import { TopBar } from './TopBar';
import { TraceabilitySection } from './TraceabilitySection';

interface ItemDetailPageProps {
  itemId: string;
  item: Item;

  projectId: string | undefined;

  isEditing: boolean;
  draftTitle: string;
  draftDescription: string;
  draftOwner: string;
  displayStatus: ItemStatus;
  displayPriority: Priority;

  createdAtLabel: string;
  updatedAtLabel: string;

  upstreamCount: number;
  downstreamCount: number;
  metadataCount: number;

  targetLinks: ItemLink[];
  sourceLinks: ItemLink[];

  metadataSearch: string;
  setMetadataSearch: (value: string) => void;
  integrationMetadata: readonly [string, unknown][];
  generalMetadata: readonly [string, unknown][];

  dimensionEntries: DimensionEntry[];
  timelineEvents: TimelineEvent[];

  buildLinkToItem: (id: string) => string;

  onBack: () => void;
  onStartEdit: () => void;
  onCancelEdit: () => void;
  onSave: () => void;
  onDelete: () => void;
  onShare: () => void;
  onOpenNewTab: () => void;

  onRunAnalysis: () => void;
  onOpenImpactAnalysis: () => void;
  onCreateSpec: (specType: string) => void;

  onChangeTitle: (value: string) => void;
  onChangeDescription: (value: string) => void;
  onChangeOwner: (value: string) => void;
  onChangeStatus: (value: ItemStatus) => void;
  onChangePriority: (value: Priority) => void;
}

function buildViewLabel(view: unknown): string {
  if (typeof view !== 'string') {
    return 'general';
  }
  const trimmed = view.trim();
  if (trimmed.length === 0) {
    return 'general';
  }
  return trimmed.toLowerCase();
}

function buildTypeLabel(type: unknown): string {
  if (typeof type !== 'string') {
    return 'unknown';
  }
  const trimmed = type.trim();
  if (trimmed.length === 0) {
    return 'unknown';
  }
  return trimmed;
}

function buildCodeReference(item: Item): string {
  const ref = item.codeRef;
  if (ref === null || ref === undefined) {
    return 'No code reference attached';
  }
  return `${ref.filePath} · ${ref.symbolName}`;
}

function buildDocReference(item: Item): string {
  const ref = item.docRef;
  if (ref === null || ref === undefined) {
    return 'No doc reference attached';
  }
  const section = ref.sectionTitle;
  if (typeof section === 'string' && section.trim().length > 0) {
    return `${ref.documentTitle} · ${section}`;
  }
  return `${ref.documentTitle} · ${ref.documentPath}`;
}

export function ItemDetailPage(props: ItemDetailPageProps): JSX.Element {
  const {
    buildLinkToItem,
    createdAtLabel,
    dimensionEntries,
    displayPriority,
    displayStatus,
    downstreamCount,
    draftDescription,
    draftOwner,
    draftTitle,
    generalMetadata,
    integrationMetadata,
    isEditing,
    item,
    itemId,
    metadataCount,
    metadataSearch,
    onBack,
    onCancelEdit,
    onChangeDescription,
    onChangeOwner,
    onChangePriority,
    onChangeStatus,
    onChangeTitle,
    onCreateSpec,
    onDelete,
    onOpenImpactAnalysis,
    onOpenNewTab,
    onRunAnalysis,
    onSave,
    onShare,
    onStartEdit,
    projectId,
    setMetadataSearch,
    sourceLinks,
    targetLinks,
    timelineEvents,
    updatedAtLabel,
    upstreamCount,
  } = props;

  const viewLabel = buildViewLabel(item.view);
  const typeLabel = buildTypeLabel(item.type);
  const subtitle = formatViewTypeLabel(item.view, typeLabel);

  let displayDescription = descriptionOrDefault(item.description);
  if (isEditing) {
    displayDescription = draftDescription;
  }

  const totalLinks = upstreamCount + downstreamCount;

  return (
    <PageShell>
      <TopBar
        isEditing={isEditing}
        onBack={onBack}
        onStartEdit={onStartEdit}
        onCancelEdit={onCancelEdit}
        onSave={onSave}
        onDelete={onDelete}
        onShare={onShare}
        onOpenNewTab={onOpenNewTab}
      />

      <main className='min-h-0 flex-1 overflow-auto pt-6 md:pt-8'>
        <ItemSummarySection
          itemId={itemId}
          viewLabel={viewLabel}
          typeLabel={typeLabel}
          subtitle={subtitle}
          isEditing={isEditing}
          title={draftTitle}
          description={displayDescription}
          owner={draftOwner}
          status={displayStatus}
          priority={displayPriority}
          createdAtLabel={createdAtLabel}
          updatedAtLabel={updatedAtLabel}
          totalLinks={totalLinks}
          version={Number(item.version)}
          perspective={item.perspective}
          canonicalId={item.canonicalId}
          parentId={item.parentId}
          onChangeTitle={onChangeTitle}
          onChangeDescription={onChangeDescription}
          onChangeOwner={onChangeOwner}
          onChangeStatus={onChangeStatus}
          onChangePriority={onChangePriority}
        />

        <div className='grid grid-cols-1 gap-8 pt-8 lg:grid-cols-[1.6fr_1fr]'>
          <div className='space-y-8'>
            <TraceabilitySection
              upstreamCount={upstreamCount}
              downstreamCount={downstreamCount}
              metadataCount={metadataCount}
              onRunAnalysis={onRunAnalysis}
              itemId={itemId}
              projectId={projectId}
              itemType={typeLabel}
              onCreateSpec={onCreateSpec}
              targetLinks={targetLinks}
              sourceLinks={sourceLinks}
              buildLinkToItem={buildLinkToItem}
              metadataSearch={metadataSearch}
              setMetadataSearch={setMetadataSearch}
              integrationMetadata={integrationMetadata}
              generalMetadata={generalMetadata}
            />
          </div>

          <div className='space-y-6'>
            <SignalStackCard
              connectedCount={upstreamCount + downstreamCount}
              onOpenImpactAnalysis={onOpenImpactAnalysis}
            />
            <DimensionsCard entries={dimensionEntries} />
            <ReferencesCard
              codeReference={buildCodeReference(item)}
              docReference={buildDocReference(item)}
            />
            <ChangeLogCard events={timelineEvents} />
            <ActivityTimelineCard createdAtLabel={createdAtLabel} updatedAtLabel={updatedAtLabel} />
            <InsightCard
              downstreamCount={downstreamCount}
              upstreamCount={upstreamCount}
              metadataCount={metadataCount}
            />
          </div>
        </div>
      </main>
    </PageShell>
  );
}
