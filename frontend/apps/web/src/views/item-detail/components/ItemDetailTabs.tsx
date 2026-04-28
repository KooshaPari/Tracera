import type { ItemLink } from '@/views/item-detail/types';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui';

import { LinksPanel } from './LinksPanel';
import { MetadataPanel } from './MetadataPanel';
import { SpecificationsPanel } from './SpecificationsPanel';

type MetadataEntry = readonly [key: string, value: unknown];

interface ItemDetailTabsProps {
  itemId: string;
  projectId: string | undefined;
  itemType: string;
  onCreateSpec: (specType: string) => void;

  targetLinks: ItemLink[];
  sourceLinks: ItemLink[];
  buildLinkToItem: (id: string) => string;

  metadataSearch: string;
  setMetadataSearch: (value: string) => void;
  integrationMetadata: readonly MetadataEntry[];
  generalMetadata: readonly MetadataEntry[];
}

export function ItemDetailTabs(props: ItemDetailTabsProps): JSX.Element {
  const {
    buildLinkToItem,
    generalMetadata,
    integrationMetadata,
    itemId,
    itemType,
    metadataSearch,
    onCreateSpec,
    projectId,
    setMetadataSearch,
    sourceLinks,
    targetLinks,
  } = props;

  return (
    <Tabs defaultValue='specs' className='w-full'>
      <TabsList className='bg-muted/60 rounded-xl p-1'>
        <TabsTrigger value='specs' className='rounded-lg'>
          Specifications
        </TabsTrigger>
        <TabsTrigger value='links' className='rounded-lg'>
          Relationships
        </TabsTrigger>
        <TabsTrigger value='metadata' className='rounded-lg'>
          Metadata
        </TabsTrigger>
      </TabsList>

      <TabsContent value='specs' className='space-y-4 pt-6'>
        <SpecificationsPanel
          projectId={projectId}
          itemId={itemId}
          itemType={itemType}
          onCreateSpec={onCreateSpec}
        />
      </TabsContent>

      <TabsContent value='links' className='space-y-6 pt-6'>
        <LinksPanel
          targetLinks={targetLinks}
          sourceLinks={sourceLinks}
          buildLinkToItem={buildLinkToItem}
        />
      </TabsContent>

      <TabsContent value='metadata' className='space-y-6 pt-6'>
        <MetadataPanel
          metadataSearch={metadataSearch}
          setMetadataSearch={setMetadataSearch}
          integrationMetadata={integrationMetadata}
          generalMetadata={generalMetadata}
        />
      </TabsContent>
    </Tabs>
  );
}
