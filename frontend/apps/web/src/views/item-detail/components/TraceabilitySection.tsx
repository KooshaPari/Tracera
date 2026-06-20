import { Sparkles } from 'lucide-react';

import type { ItemLink } from '@/views/item-detail/types';

import { Button, Card, Separator } from '@tracertm/ui';

import { ItemDetailTabs } from './ItemDetailTabs';
import { TraceabilityStats } from './TraceabilityStats';

type MetadataEntry = readonly [key: string, value: unknown];

interface TraceabilitySectionProps {
  upstreamCount: number;
  downstreamCount: number;
  metadataCount: number;
  onRunAnalysis: () => void;

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

export function TraceabilitySection(props: TraceabilitySectionProps): JSX.Element {
  const {
    buildLinkToItem,
    downstreamCount,
    generalMetadata,
    integrationMetadata,
    itemId,
    itemType,
    metadataCount,
    metadataSearch,
    onCreateSpec,
    onRunAnalysis,
    projectId,
    setMetadataSearch,
    sourceLinks,
    targetLinks,
    upstreamCount,
  } = props;

  return (
    <Card className='bg-card/50 border-0 shadow-lg shadow-slate-950/5'>
      <div className='space-y-6 p-6'>
        <div className='flex items-center justify-between'>
          <div className='space-y-1'>
            <p className='text-muted-foreground text-[10px] font-black tracking-[0.3em] uppercase'>
              Traceability
            </p>
            <h2 className='text-lg font-black tracking-tight'>Relationship map</h2>
          </div>
          <Button size='sm' className='gap-2 rounded-full' onClick={onRunAnalysis}>
            <Sparkles className='h-4 w-4' />
            Run analysis
          </Button>
        </div>

        <TraceabilityStats
          upstreamCount={upstreamCount}
          downstreamCount={downstreamCount}
          metadataCount={metadataCount}
        />

        <Separator />

        <ItemDetailTabs
          projectId={projectId}
          itemId={itemId}
          itemType={itemType}
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
    </Card>
  );
}
