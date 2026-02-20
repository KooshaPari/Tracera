import type { FC } from 'react';

import { CheckCircle2, Shield, ShieldAlert, ShieldCheck } from 'lucide-react';
import { useMemo } from 'react';

import type { Contract } from '@tracertm/types';

import { Card } from '@tracertm/ui';

interface VerificationSummaryCardsProps {
  contracts: readonly Contract[];
}

export const VerificationSummaryCards: FC<VerificationSummaryCardsProps> = ({ contracts }) => {
  const { passRate, total, verified, violated } = useMemo(() => {
    const totalVal = contracts.length;
    const verifiedVal = contracts.filter((contract) => contract.status === 'verified').length;
    const violatedVal = contracts.filter((contract) => contract.status === 'violated').length;
    let passRateVal = '0';
    if (totalVal > 0) {
      const percentageMultiplier = 100;
      passRateVal = ((verifiedVal / totalVal) * percentageMultiplier).toFixed(1);
    }
    return {
      passRate: passRateVal,
      total: totalVal,
      verified: verifiedVal,
      violated: violatedVal,
    };
  }, [contracts]);

  return (
    <div className='grid gap-4 md:grid-cols-4'>
      <Card className='border-none bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-950/20 dark:to-blue-900/20'>
        <div className='space-y-2 p-4'>
          <div className='flex items-center justify-between'>
            <span className='text-muted-foreground text-xs font-medium'>Total Contracts</span>
            <Shield className='h-4 w-4 text-blue-600' />
          </div>
          <div className='text-2xl font-bold'>{total}</div>
        </div>
      </Card>

      <Card className='border-none bg-gradient-to-br from-green-50 to-green-100/50 dark:from-green-950/20 dark:to-green-900/20'>
        <div className='space-y-2 p-4'>
          <div className='flex items-center justify-between'>
            <span className='text-muted-foreground text-xs font-medium'>Verified</span>
            <ShieldCheck className='h-4 w-4 text-green-600' />
          </div>
          <div className='text-2xl font-bold'>{verified}</div>
        </div>
      </Card>

      <Card className='border-none bg-gradient-to-br from-red-50 to-red-100/50 dark:from-red-950/20 dark:to-red-900/20'>
        <div className='space-y-2 p-4'>
          <div className='flex items-center justify-between'>
            <span className='text-muted-foreground text-xs font-medium'>Violated</span>
            <ShieldAlert className='h-4 w-4 text-red-600' />
          </div>
          <div className='text-2xl font-bold'>{violated}</div>
        </div>
      </Card>

      <Card className='border-none bg-gradient-to-br from-purple-50 to-purple-100/50 dark:from-purple-950/20 dark:to-purple-900/20'>
        <div className='space-y-2 p-4'>
          <div className='flex items-center justify-between'>
            <span className='text-muted-foreground text-xs font-medium'>Pass Rate</span>
            <CheckCircle2 className='h-4 w-4 text-purple-600' />
          </div>
          <div className='text-2xl font-bold'>{passRate}%</div>
        </div>
      </Card>
    </div>
  );
};
