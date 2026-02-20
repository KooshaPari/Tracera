import { ArrowRight } from 'lucide-react';

import type { SpecificationSummary } from '@tracertm/types';

import { Card, CardContent, CardHeader, CardTitle } from '@tracertm/ui';

export interface SpecificationsDashboardQuickNavigationCardsProps {
  summary: SpecificationSummary;
  onNavigateADRs: () => void;
  onNavigateContracts: () => void;
  onNavigateFeatures: () => void;
}

export function SpecificationsDashboardQuickNavigationCards({
  summary,
  onNavigateADRs,
  onNavigateContracts,
  onNavigateFeatures,
}: SpecificationsDashboardQuickNavigationCardsProps): JSX.Element {
  return (
    <div className='grid gap-4 md:grid-cols-3'>
      <button type='button' onClick={onNavigateADRs} className='group text-left'>
        <Card className='border-none bg-gradient-to-br from-blue-50 to-blue-100/50 transition-all hover:shadow-md dark:from-blue-950/20 dark:to-blue-900/20'>
          <CardHeader className='pb-3'>
            <div className='flex items-center justify-between'>
              <CardTitle className='text-sm'>Architecture Decisions</CardTitle>
              <ArrowRight className='text-muted-foreground h-4 w-4 transition-transform group-hover:translate-x-1' />
            </div>
          </CardHeader>
          <CardContent className='space-y-3'>
            <div className='text-3xl font-bold text-blue-600'>{summary.adrs.total}</div>
            <div className='grid grid-cols-2 gap-2 text-xs'>
              <div>
                <div className='text-muted-foreground'>Accepted</div>
                <div className='font-bold text-blue-600'>{summary.adrs.accepted}</div>
              </div>
              <div>
                <div className='text-muted-foreground'>Compliance</div>
                <div className='font-bold text-blue-600'>
                  {Math.round(summary.adrs.averageCompliance)}%
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </button>

      <button type='button' onClick={onNavigateContracts} className='group text-left'>
        <Card className='border-none bg-gradient-to-br from-green-50 to-green-100/50 transition-all hover:shadow-md dark:from-green-950/20 dark:to-green-900/20'>
          <CardHeader className='pb-3'>
            <div className='flex items-center justify-between'>
              <CardTitle className='text-sm'>API Contracts</CardTitle>
              <ArrowRight className='text-muted-foreground h-4 w-4 transition-transform group-hover:translate-x-1' />
            </div>
          </CardHeader>
          <CardContent className='space-y-3'>
            <div className='text-3xl font-bold text-green-600'>{summary.contracts.total}</div>
            <div className='grid grid-cols-2 gap-2 text-xs'>
              <div>
                <div className='text-muted-foreground'>Active</div>
                <div className='font-bold text-green-600'>{summary.contracts.active}</div>
              </div>
              <div>
                <div className='text-muted-foreground'>Verified</div>
                <div className='font-bold text-green-600'>{summary.contracts.verified}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </button>

      <button type='button' onClick={onNavigateFeatures} className='group text-left'>
        <Card className='border-none bg-gradient-to-br from-purple-50 to-purple-100/50 transition-all hover:shadow-md dark:from-purple-950/20 dark:to-purple-900/20'>
          <CardHeader className='pb-3'>
            <div className='flex items-center justify-between'>
              <CardTitle className='text-sm'>BDD Features</CardTitle>
              <ArrowRight className='text-muted-foreground h-4 w-4 transition-transform group-hover:translate-x-1' />
            </div>
          </CardHeader>
          <CardContent className='space-y-3'>
            <div className='text-3xl font-bold text-purple-600'>{summary.features.total}</div>
            <div className='grid grid-cols-2 gap-2 text-xs'>
              <div>
                <div className='text-muted-foreground'>Scenarios</div>
                <div className='font-bold text-purple-600'>{summary.features.scenarios}</div>
              </div>
              <div>
                <div className='text-muted-foreground'>Pass Rate</div>
                <div className='font-bold text-purple-600'>
                  {Math.round(summary.features.passRate)}%
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </button>
    </div>
  );
}
