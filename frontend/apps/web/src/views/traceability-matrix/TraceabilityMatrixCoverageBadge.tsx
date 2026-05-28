import { CheckCircle2, Circle, MinusCircle } from 'lucide-react';

export type CoverageStatus = 'covered' | 'partial' | 'uncovered';

interface TraceabilityMatrixCoverageBadgeProps {
  status: CoverageStatus;
  coveredCount: number;
  totalFeatures: number;
}

export function TraceabilityMatrixCoverageBadge({
  status,
  coveredCount,
  totalFeatures,
}: TraceabilityMatrixCoverageBadgeProps) {
  if (status === 'covered') {
    return (
      <span className='badge-covered'>
        <CheckCircle2 className='h-2.5 w-2.5' />
        COVERED {coveredCount}/{totalFeatures}
      </span>
    );
  }
  if (status === 'partial') {
    return (
      <span className='badge-partial'>
        <MinusCircle className='h-2.5 w-2.5' />
        PARTIAL {coveredCount}/{totalFeatures}
      </span>
    );
  }
  return (
    <span className='badge-uncovered'>
      <Circle className='h-2.5 w-2.5' />
      UNCOVERED
    </span>
  );
}
