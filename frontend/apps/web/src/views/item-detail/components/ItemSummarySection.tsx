import type { ItemStatus, Priority } from '@tracertm/types';

import { Card } from '@tracertm/ui';

import { CanonicalParentCard } from './CanonicalParentCard';
import { ItemBadgesRow } from './ItemBadgesRow';
import { ItemMetaLine } from './ItemMetaLine';
import { ItemTitleSection } from './ItemTitleSection';
import { OwnerCard } from './OwnerCard';
import { StatusPriorityCard } from './StatusPriorityCard';
import { VersionPerspectiveCard } from './VersionPerspectiveCard';

interface ItemSummarySectionProps {
  itemId: string;
  viewLabel: string;
  typeLabel: string;
  subtitle: string;

  isEditing: boolean;
  title: string;
  description: string;
  owner: string;
  status: ItemStatus;
  priority: Priority;

  createdAtLabel: string;
  updatedAtLabel: string;
  totalLinks: number;

  version: number;
  perspective: string | null | undefined;
  canonicalId: string | null | undefined;
  parentId: string | null | undefined;

  onChangeTitle: (value: string) => void;
  onChangeDescription: (value: string) => void;
  onChangeOwner: (value: string) => void;
  onChangeStatus: (value: ItemStatus) => void;
  onChangePriority: (value: Priority) => void;
}

export function ItemSummarySection(props: ItemSummarySectionProps): JSX.Element {
  const {
    canonicalId,
    createdAtLabel,
    description,
    isEditing,
    itemId,
    onChangeDescription,
    onChangeOwner,
    onChangePriority,
    onChangeStatus,
    onChangeTitle,
    owner,
    parentId,
    perspective,
    priority,
    status,
    subtitle,
    title,
    totalLinks,
    typeLabel,
    updatedAtLabel,
    version,
    viewLabel,
  } = props;

  return (
    <Card className='bg-card/60 shadow-primary/10 overflow-hidden border-0 shadow-xl backdrop-blur-sm'>
      <div className='space-y-6 p-8'>
        <ItemBadgesRow
          viewLabel={viewLabel}
          typeLabel={typeLabel}
          status={status}
          priority={priority}
          itemId={itemId}
        />

        <div className='grid grid-cols-1 gap-8 lg:grid-cols-[1.4fr_1fr]'>
          <div className='space-y-4'>
            <ItemTitleSection
              isEditing={isEditing}
              subtitle={subtitle}
              title={title}
              description={description}
              onChangeTitle={onChangeTitle}
              onChangeDescription={onChangeDescription}
            />
            <ItemMetaLine
              createdAtLabel={createdAtLabel}
              updatedAtLabel={updatedAtLabel}
              totalLinks={totalLinks}
            />
          </div>

          <div className='grid gap-3'>
            <StatusPriorityCard
              isEditing={isEditing}
              status={status}
              priority={priority}
              onChangeStatus={onChangeStatus}
              onChangePriority={onChangePriority}
            />
            <OwnerCard isEditing={isEditing} owner={owner} onChangeOwner={onChangeOwner} />
            <VersionPerspectiveCard version={version} perspective={perspective} />
            <CanonicalParentCard canonicalId={canonicalId} parentId={parentId} />
          </div>
        </div>
      </div>
    </Card>
  );
}
