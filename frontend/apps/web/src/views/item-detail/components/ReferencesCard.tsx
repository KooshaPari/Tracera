import { BookText, Code2 } from 'lucide-react';

import { Card } from '@tracertm/ui';

interface ReferencesCardProps {
  codeReference: string;
  docReference: string;
}

export function ReferencesCard({ codeReference, docReference }: ReferencesCardProps): JSX.Element {
  return (
    <Card className='bg-card/60 space-y-4 border-0 p-6 shadow-lg shadow-slate-950/5'>
      <div className='flex items-center justify-between'>
        <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
          References
        </h3>
        <BookText className='h-4 w-4 text-emerald-500' />
      </div>
      <div className='space-y-3 text-xs'>
        <div className='flex items-start gap-2'>
          <Code2 className='h-4 w-4 text-slate-500' />
          <div>
            <p className='font-bold'>Code reference</p>
            <p className='text-muted-foreground'>{codeReference}</p>
          </div>
        </div>
        <div className='flex items-start gap-2'>
          <BookText className='h-4 w-4 text-slate-500' />
          <div>
            <p className='font-bold'>Documentation</p>
            <p className='text-muted-foreground'>{docReference}</p>
          </div>
        </div>
      </div>
    </Card>
  );
}
