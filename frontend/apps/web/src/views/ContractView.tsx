import { useParams } from '@tanstack/react-router';
import { Plus } from 'lucide-react';

import { ContractCard } from '@/components/specifications/contracts/ContractCard';
import { useContracts } from '@/hooks/useSpecifications';
import { Button } from '@tracertm/ui';

export const ContractView = () => {
  const { projectId } = useParams({ strict: false });
  const { data: contractsData } = useContracts({ projectId: projectId ?? '' });
  const contracts = contractsData?.contracts ?? [];

  return (
    <div className='space-y-6 p-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-2xl font-bold'>Contracts</h1>
          <p className='text-muted-foreground'>
            Formal specifications and design-by-contract definitions.
          </p>
        </div>
        <Button>
          <Plus className='mr-2 h-4 w-4' />
          New Contract
        </Button>
      </div>

      <div className='grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3'>
        {contracts.map((contract) => (
          <ContractCard key={contract.id} contract={contract} />
        ))}
      </div>
    </div>
  );
};
