import { useNavigate, useParams } from '@tanstack/react-router';
import { format } from 'date-fns';
import { ArrowLeft } from 'lucide-react';

import { ConditionList } from '@/components/specifications/contracts/ConditionList';
import { ContractCard } from '@/components/specifications/contracts/ContractCard';
import { StateMachineViewer } from '@/components/specifications/contracts/StateMachineViewer';
import { useContract, useContractActivities } from '@/hooks/useSpecifications';
import { Button, Card, CardContent, CardHeader, CardTitle } from '@tracertm/ui';

export function ContractDetailView() {
  const params = useParams({ strict: false });
  const navigate = useNavigate();
  const contractId = params.contractId ?? '';
  const { data: contract, isLoading } = useContract(contractId);
  const { data: contractActivities } = useContractActivities(contractId);

  if (isLoading) {
    return (
      <div className='space-y-6 p-6'>
        <div className='bg-muted/40 h-8 w-40 rounded' />
        <div className='bg-muted/30 h-32 rounded-xl' />
        <div className='bg-muted/20 h-64 rounded-xl' />
      </div>
    );
  }

  if (!contract) {
    return (
      <div className='space-y-4 p-6'>
        <Button
          variant='ghost'
          onClick={async () =>
            navigate({
              params: { projectId: params.projectId ?? '' },
              search: { tab: 'contracts' },
              to: '/projects/$projectId/specifications',
            })
          }
        >
          <ArrowLeft className='mr-2 h-4 w-4' />
          Back to Contracts
        </Button>
        <Card className='bg-muted/20 border-none'>
          <CardHeader>
            <CardTitle>Contract not found</CardTitle>
          </CardHeader>
          <CardContent className='text-muted-foreground text-sm'>
            This contract may have been deleted or you don’t have access.
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className='space-y-6 p-6'>
      <div className='flex items-center justify-between'>
        <Button
          variant='ghost'
          onClick={async () =>
            navigate({
              params: { projectId: params.projectId ?? '' },
              search: { tab: 'contracts' },
              to: '/projects/$projectId/specifications',
            })
          }
        >
          <ArrowLeft className='mr-2 h-4 w-4' />
          Back to Contracts
        </Button>
      </div>

      <ContractCard contract={contract} className='cursor-default' />

      <Card className='bg-card/50 border-none'>
        <CardHeader>
          <CardTitle className='text-base'>Activity</CardTitle>
        </CardHeader>
        <CardContent className='text-muted-foreground space-y-3 text-sm'>
          {contractActivities && contractActivities.length > 0
            ? contractActivities.map((activity) => (
                <div
                  key={activity.id}
                  className='border-border/50 flex items-center justify-between border-b pb-2 last:border-0'
                >
                  <div>
                    <div className='text-foreground font-medium'>{activity.activityType}</div>
                    <div className='text-muted-foreground text-xs'>
                      {activity.description ?? 'Contract updated'}
                    </div>
                  </div>
                  <div className='text-muted-foreground text-xs'>
                    {activity.createdAt
                      ? format(new Date(activity.createdAt), 'MMM d, yyyy HH:mm')
                      : '—'}
                  </div>
                </div>
              ))
            : [
                contract.createdAt
                  ? {
                      date: contract.createdAt,
                      detail: `Contract ${contract.contractNumber}`,
                      label: 'Created',
                    }
                  : null,
                contract.updatedAt
                  ? {
                      date: contract.updatedAt,
                      detail: 'Metadata updated',
                      label: 'Updated',
                    }
                  : null,
                contract.lastVerifiedAt
                  ? {
                      date: contract.lastVerifiedAt,
                      detail:
                        contract.verificationResult?.status === 'pass'
                          ? 'All conditions passed'
                          : contract.verificationResult?.status === 'fail'
                            ? 'Verification failed'
                            : 'Verification run',
                      label: 'Verified',
                    }
                  : null,
              ]
                .filter(Boolean)
                .map((entry: any) => (
                  <div
                    key={`${entry.label}-${entry.date}`}
                    className='border-border/50 flex items-center justify-between border-b pb-2 last:border-0'
                  >
                    <div>
                      <div className='text-foreground font-medium'>{entry.label}</div>
                      <div className='text-muted-foreground text-xs'>{entry.detail}</div>
                    </div>
                    <div className='text-muted-foreground text-xs'>
                      {format(new Date(entry.date), 'MMM d, yyyy HH:mm')}
                    </div>
                  </div>
                ))}
          {(!contractActivities || contractActivities.length === 0) &&
            !contract.createdAt &&
            !contract.updatedAt &&
            !contract.lastVerifiedAt && <div>No activity yet.</div>}
        </CardContent>
      </Card>

      <ConditionList
        preconditions={contract.preconditions}
        postconditions={contract.postconditions}
        invariants={contract.invariants}
      />

      {contract.states && contract.states.length > 0 && (
        <Card className='bg-card/50 border-none'>
          <CardHeader>
            <CardTitle className='text-base'>State Machine</CardTitle>
          </CardHeader>
          <CardContent>
            <StateMachineViewer
              states={contract.states}
              transitions={contract.transitions ?? []}
              initialState={contract.initialState}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
