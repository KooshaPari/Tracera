import { BookOpen, FileText, Shield } from 'lucide-react';

import { Button } from '@tracertm/ui';

export interface SpecificationsDashboardHeaderProps {
  onNavigateADRs: () => void;
  onNavigateContracts: () => void;
  onNavigateFeatures: () => void;
}

export function SpecificationsDashboardHeader({
  onNavigateADRs,
  onNavigateContracts,
  onNavigateFeatures,
}: SpecificationsDashboardHeaderProps): JSX.Element {
  return (
    <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
      <div>
        <h1 className='text-2xl font-black tracking-tight uppercase'>Specifications Hub</h1>
        <p className='text-muted-foreground text-sm font-medium'>
          Unified view of all architecture, contract, and feature specifications.
        </p>
      </div>
      <div className='flex gap-2'>
        <Button variant='outline' size='sm' onClick={onNavigateADRs} className='gap-2'>
          <FileText className='h-4 w-4' /> ADRs
        </Button>
        <Button variant='outline' size='sm' onClick={onNavigateContracts} className='gap-2'>
          <Shield className='h-4 w-4' /> Contracts
        </Button>
        <Button variant='outline' size='sm' onClick={onNavigateFeatures} className='gap-2'>
          <BookOpen className='h-4 w-4' /> Features
        </Button>
      </div>
    </div>
  );
}
