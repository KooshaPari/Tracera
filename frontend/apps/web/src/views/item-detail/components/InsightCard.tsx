import { Sparkles } from 'lucide-react';

import { Card } from '@tracertm/ui';

interface InsightCardProps {
  downstreamCount: number;
  upstreamCount: number;
  metadataCount: number;
}

export function InsightCard({
  downstreamCount,
  metadataCount,
  upstreamCount,
}: InsightCardProps): JSX.Element {
  return (
    <Card className='bg-primary text-primary-foreground shadow-primary/20 space-y-3 border-0 p-6 shadow-lg'>
      <div className='flex items-center gap-2 text-xs font-black tracking-widest uppercase opacity-80'>
        <Sparkles className='h-4 w-4' />
        Insight snapshot
      </div>
      <p className='text-sm leading-relaxed font-medium italic'>
        &quot;This item touches {downstreamCount} downstream links, {upstreamCount} upstream
        dependencies, and {metadataCount} metadata signals. Lock a baseline before major
        edits.&quot;
      </p>
    </Card>
  );
}
