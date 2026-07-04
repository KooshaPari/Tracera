import { ShieldAlert, Target } from 'lucide-react';

import { Button, Card } from '@tracertm/ui';

interface SignalStackCardProps {
  connectedCount: number;
  onOpenImpactAnalysis: () => void;
}

export function SignalStackCard({
  connectedCount,
  onOpenImpactAnalysis,
}: SignalStackCardProps): JSX.Element {
  return (
    <Card className='bg-card/60 space-y-4 border-0 p-6 shadow-lg shadow-slate-950/5'>
      <div className='flex items-center justify-between'>
        <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
          Signal stack
        </h3>
        <ShieldAlert className='h-4 w-4 text-orange-500' />
      </div>
      <div className='flex items-center gap-3'>
        <div className='flex h-10 w-10 items-center justify-center rounded-2xl bg-amber-500/15'>
          <Target className='h-4 w-4 text-amber-600' />
        </div>
        <div>
          <p className='text-2xl font-black'>{connectedCount}</p>
          <p className='text-muted-foreground text-xs'>Connected items affecting delivery</p>
        </div>
      </div>
      <Button variant='outline' size='sm' className='w-full gap-2' onClick={onOpenImpactAnalysis}>
        <Target className='h-4 w-4' />
        Open impact analysis
      </Button>
    </Card>
  );
}
