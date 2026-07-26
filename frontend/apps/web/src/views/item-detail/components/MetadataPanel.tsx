import { Hash, ShieldAlert } from 'lucide-react';
import { useCallback } from 'react';

import { Input, Separator } from '@tracertm/ui';

import { MetadataCategoryCard } from './MetadataCategoryCard';

type MetadataEntry = readonly [key: string, value: unknown];

interface MetadataPanelProps {
  metadataSearch: string;
  setMetadataSearch: (value: string) => void;
  integrationMetadata: readonly MetadataEntry[];
  generalMetadata: readonly MetadataEntry[];
}

export function MetadataPanel({
  generalMetadata,
  integrationMetadata,
  metadataSearch,
  setMetadataSearch,
}: MetadataPanelProps): JSX.Element {
  const handleChangeSearch = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>): void => {
      setMetadataSearch(event.target.value);
    },
    [setMetadataSearch],
  );

  return (
    <div className='space-y-6'>
      <div className='space-y-2'>
        <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
          Search metadata
        </p>
        <Input
          value={metadataSearch}
          onChange={handleChangeSearch}
          placeholder='Filter key/value pairs...'
          className='bg-background/70'
        />
      </div>

      <Separator />

      <div className='grid grid-cols-1 gap-6 md:grid-cols-2'>
        <MetadataCategoryCard
          title='Integration'
          Icon={ShieldAlert}
          iconClassName='h-4 w-4 text-orange-500'
          entries={integrationMetadata}
          emptyMessage='No integration metadata found.'
        />
        <MetadataCategoryCard
          title='General'
          Icon={Hash}
          iconClassName='h-4 w-4 text-sky-500'
          entries={generalMetadata}
          emptyMessage='No metadata found.'
        />
      </div>
    </div>
  );
}
