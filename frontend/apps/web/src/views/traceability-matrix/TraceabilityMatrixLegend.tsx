import { CheckCircle2, Circle, MinusCircle } from 'lucide-react';

export function TraceabilityMatrixLegend() {
  return (
    <div className='flex flex-wrap justify-center gap-6 py-2'>
      <div className='flex items-center gap-2'>
        <div className='flex h-4 w-4 items-center justify-center rounded-full bg-green-500/15 text-green-500 ring-1 ring-green-500/20'>
          <CheckCircle2 className='h-2.5 w-2.5' />
        </div>
        <span className='mono-label'>Linked</span>
      </div>
      <div className='flex items-center gap-2'>
        <div className='bg-muted-foreground/20 h-1.5 w-1.5 rounded-full' />
        <span className='mono-label'>Not linked</span>
      </div>
      <div className='flex items-center gap-2'>
        <span className='badge-covered'>
          <CheckCircle2 className='h-2.5 w-2.5' />
          COVERED
        </span>
        <span className='mono-label'>All features linked</span>
      </div>
      <div className='flex items-center gap-2'>
        <span className='badge-partial'>
          <MinusCircle className='h-2.5 w-2.5' />
          PARTIAL
        </span>
        <span className='mono-label'>Some features linked</span>
      </div>
      <div className='flex items-center gap-2'>
        <span className='badge-uncovered'>
          <Circle className='h-2.5 w-2.5' />
          UNCOVERED
        </span>
        <span className='mono-label'>No features linked</span>
      </div>
    </div>
  );
}
