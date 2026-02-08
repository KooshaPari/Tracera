import { Card } from '@tracertm/ui';

interface TraceabilityStatsProps {
  downstreamCount: number;
  metadataCount: number;
  upstreamCount: number;
}

export function TraceabilityStats({
  downstreamCount,
  metadataCount,
  upstreamCount,
}: TraceabilityStatsProps): JSX.Element {
  return (
    <div className='grid grid-cols-1 gap-4 sm:grid-cols-3'>
      <Card className='bg-muted/40 space-y-2 border-0 p-4'>
        <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
          Upstream
        </p>
        <p className='text-2xl font-black'>{upstreamCount}</p>
        <p className='text-muted-foreground text-xs'>Dependencies tied in</p>
      </Card>
      <Card className='bg-muted/40 space-y-2 border-0 p-4'>
        <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
          Downstream
        </p>
        <p className='text-2xl font-black'>{downstreamCount}</p>
        <p className='text-muted-foreground text-xs'>Impacted items</p>
      </Card>
      <Card className='bg-muted/40 space-y-2 border-0 p-4'>
        <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
          Metadata
        </p>
        <p className='text-2xl font-black'>{metadataCount}</p>
        <p className='text-muted-foreground text-xs'>Context signals</p>
      </Card>
    </div>
  );
}
