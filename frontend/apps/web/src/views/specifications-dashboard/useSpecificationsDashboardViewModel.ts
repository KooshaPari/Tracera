import { useNavigate } from '@tanstack/react-router';
import { useCallback, useMemo } from 'react';

import type {
  CoverageDataItem,
  GapItem,
  TypeDistributionRow,
} from '@/views/SpecificationsDashboardView.data';
import type { ADR, Contract, Feature, SpecificationSummary, TypedItem } from '@tracertm/types';

import { useItems } from '@/hooks/useItems';
import { useADRs, useContracts, useFeatures } from '@/hooks/useSpecifications';
import {
  buildCoverageData,
  buildGapItems,
  buildSpecificationSummary,
  buildTypeDistribution,
} from '@/views/SpecificationsDashboardView.data';

type SpecificationsTab = 'adrs' | 'contracts' | 'features';
type CreateNewType = 'adr' | 'contract' | 'feature';

type ViewModel = Readonly<{
  coverageData: CoverageDataItem[];
  gapItems: GapItem[];
  isLoading: boolean;
  onCreateNew: (type: string) => void;
  onNavigate: (section: string, id?: string) => void;
  onNavigateADRs: () => void;
  onNavigateContracts: () => void;
  onNavigateFeatures: () => void;
  summary: SpecificationSummary;
  totalItems: number;
  typeDistribution: TypeDistributionRow[];
}>;

const EMPTY_ADRS: ADR[] = [];
const EMPTY_CONTRACTS: Contract[] = [];
const EMPTY_FEATURES: Feature[] = [];
const EMPTY_ITEMS: TypedItem[] = [];
const ITEMS_LIMIT = Number('500');

const CREATE_TYPE_TO_TAB: Readonly<Record<CreateNewType, SpecificationsTab>> = {
  adr: 'adrs',
  contract: 'contracts',
  feature: 'features',
} as const;

function isSpecificationsTab(value: string): value is SpecificationsTab {
  return value === 'adrs' || value === 'contracts' || value === 'features';
}

function isCreateNewType(value: string): value is CreateNewType {
  return value === 'adr' || value === 'contract' || value === 'feature';
}

function navigateToTab(
  navigate: ReturnType<typeof useNavigate>,
  projectId: string,
  tab: SpecificationsTab,
): void {
  // Note: In this codebase, navigate calls are used without awaiting.
  const result = navigate({
    params: { projectId },
    search: { tab },
    to: '/projects/$projectId/specifications',
  });

  if (result instanceof Promise) {
    // Avoid floating promise without using `void` (disallowed by `no-void`).
    result.catch(() => {
      // Router-level error boundaries should handle navigation errors.
    });
  }
}

function computeIsLoading(values: readonly boolean[]): boolean {
  return values.includes(true);
}

export function useSpecificationsDashboardViewModel(projectId: string): ViewModel {
  const navigate = useNavigate();

  const { data: adrsData, isLoading: adrsLoading } = useADRs({ projectId });
  const { data: contractsData, isLoading: contractsLoading } = useContracts({ projectId });
  const { data: featuresData, isLoading: featuresLoading } = useFeatures({ projectId });
  const { data: itemsData } = useItems({ limit: ITEMS_LIMIT, projectId });

  const adrs = adrsData?.adrs ?? EMPTY_ADRS;
  const contracts = contractsData?.contracts ?? EMPTY_CONTRACTS;
  const features = featuresData?.features ?? EMPTY_FEATURES;
  const items = itemsData?.items ?? EMPTY_ITEMS;

  const isLoading = computeIsLoading([adrsLoading, contractsLoading, featuresLoading]);

  const typeDistribution = useMemo(() => buildTypeDistribution(items), [items]);
  const totalItems = items.length;

  const summary = useMemo(
    () => buildSpecificationSummary({ adrs, contracts, features, projectId }),
    [adrs, contracts, features, projectId],
  );

  const coverageData = useMemo(() => buildCoverageData(features, adrs), [features, adrs]);
  const gapItems = useMemo(() => buildGapItems(features, contracts), [features, contracts]);

  const handleNavigateTab = useCallback(
    function handleNavigateTab(tab: SpecificationsTab): void {
      navigateToTab(navigate, projectId, tab);
    },
    [navigate, projectId],
  );

  const onNavigateADRs = useCallback(
    function onNavigateADRs(): void {
      handleNavigateTab('adrs');
    },
    [handleNavigateTab],
  );

  const onNavigateContracts = useCallback(
    function onNavigateContracts(): void {
      handleNavigateTab('contracts');
    },
    [handleNavigateTab],
  );

  const onNavigateFeatures = useCallback(
    function onNavigateFeatures(): void {
      handleNavigateTab('features');
    },
    [handleNavigateTab],
  );

  const onCreateNew = useCallback(
    function onCreateNew(type: string): void {
      if (!isCreateNewType(type)) {
        throw new Error(`Unknown create type: ${type}`);
      }
      const tab = CREATE_TYPE_TO_TAB[type];
      handleNavigateTab(tab);
    },
    [handleNavigateTab],
  );

  const onNavigate = useCallback(
    function onNavigate(section: string, _id?: string): void {
      if (!isSpecificationsTab(section)) {
        throw new Error(`Unknown dashboard section: ${section}`);
      }
      handleNavigateTab(section);
    },
    [handleNavigateTab],
  );

  return {
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
  };
}
