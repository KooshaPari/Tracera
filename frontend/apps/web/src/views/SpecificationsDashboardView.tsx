import type { JSX } from 'react';

import { SpecificationDashboard } from '@/components/specifications/dashboard/SpecificationDashboard';

import { useSpecificationsDashboardViewModel } from './specifications-dashboard/useSpecificationsDashboardViewModel';
import { SpecificationsDashboardHeader } from './SpecificationsDashboardHeader';
import { SpecificationsDashboardLoadingSkeleton } from './SpecificationsDashboardLoadingSkeleton';
import { SpecificationsDashboardQuickNavigationCards } from './SpecificationsDashboardQuickNavigationCards';
import { SpecificationsDashboardTypeDistributionCard } from './SpecificationsDashboardTypeDistributionCard';

interface SpecificationsDashboardViewProps {
  projectId: string;
}

export function SpecificationsDashboardView({
  projectId,
}: SpecificationsDashboardViewProps): JSX.Element {
  const {
    coverageData,
    gapItems,
    isLoading,
    onCreateNew,
    onNavigate,
    onNavigateADRs,
    onNavigateContracts,
    onNavigateFeatures,
    summary,
    totalItems,
    typeDistribution,
  } = useSpecificationsDashboardViewModel(projectId);

  if (isLoading) {
    return <SpecificationsDashboardLoadingSkeleton />;
  }

  return (
    <div className='animate-in fade-in mx-auto max-w-[1600px] space-y-8 p-6 pb-20 duration-500'>
      <SpecificationsDashboardHeader
        onNavigateADRs={onNavigateADRs}
        onNavigateContracts={onNavigateContracts}
        onNavigateFeatures={onNavigateFeatures}
      />
      <SpecificationsDashboardTypeDistributionCard
        totalItems={totalItems}
        typeDistribution={typeDistribution}
      />
      <SpecificationsDashboardQuickNavigationCards
        summary={summary}
        onNavigateADRs={onNavigateADRs}
        onNavigateContracts={onNavigateContracts}
        onNavigateFeatures={onNavigateFeatures}
      />

      {/* Main Dashboard Component */}
      <SpecificationDashboard
        summary={summary}
        coverageData={coverageData}
        gapItems={gapItems}
        onNavigate={onNavigate}
        onCreateNew={onCreateNew}
      />
    </div>
  );
}
