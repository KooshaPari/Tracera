import type { ADR, Contract, Feature, SpecificationSummary, TypedItem } from '@tracertm/types';

export interface TypeDistributionRow {
  type: string;
  count: number;
}

export interface CoverageDataItem {
  id: string;
  label: string;
  coverage: number;
  testCases?: number;
  adrs?: number;
  contracts?: number;
  linked?: boolean;
}

export interface GapItem {
  id: string;
  label: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  gapType: 'no_tests' | 'no_adr' | 'no_contract' | 'orphaned';
  affectedItems?: number;
  impact?: string;
  suggestion?: string;
  linkedResources?: { type: 'test_case' | 'adr' | 'contract'; id: string; label: string }[];
}

const ONE_HUNDRED = Number('100');
const TWO = Number('2');
const PASS_RATE_GAP_THRESHOLD = Number('80');
const MAX_GAP_ITEMS = Number('5');
const MAX_TYPE_DISTRIBUTION_ROWS = Number('8');
const MAX_ADR_COVERAGE_ITEMS = Number('5');

const ADR_WEIGHT = Number('0.3');
const CONTRACT_WEIGHT = Number('0.35');
const FEATURE_WEIGHT = Number('0.35');

function normalizeItemType(type: string): string {
  const normalized = type.trim().toLowerCase();
  if (normalized.length > 0) {
    return normalized;
  }
  return 'unknown';
}

function clampToPercentage(value: number): number {
  if (value < 0) {
    return 0;
  }
  if (value > ONE_HUNDRED) {
    return ONE_HUNDRED;
  }
  return value;
}

export function calculatePercent(count: number, total: number): number {
  if (total <= 0) {
    return 0;
  }
  return Math.round((count / total) * ONE_HUNDRED);
}

export function buildTypeDistribution(items: TypedItem[]): TypeDistributionRow[] {
  if (items.length === 0) {
    return [];
  }

  const counts = new Map<string, number>();
  for (const item of items) {
    const type = normalizeItemType(item.type);
    const prev = counts.get(type);
    if (prev === undefined) {
      counts.set(type, 1);
      continue;
    }
    counts.set(type, prev + 1);
  }

  const rows = [...counts.entries()].map(([type, count]) => ({ count, type }));
  rows.sort((a, b) => b.count - a.count);
  return rows.slice(0, MAX_TYPE_DISTRIBUTION_ROWS);
}

function buildAdrMetrics(adrs: ADR[]): SpecificationSummary['adrs'] {
  const total = adrs.length;
  let accepted = 0;
  let proposed = 0;
  let complianceSum = 0;

  for (const adr of adrs) {
    if (adr.status === 'accepted') {
      accepted += 1;
    }
    if (adr.status === 'proposed') {
      proposed += 1;
    }
    complianceSum += adr.complianceScore ?? 0;
  }

  let averageCompliance = 0;
  if (total > 0) {
    averageCompliance = complianceSum / total;
  }

  return { accepted, averageCompliance, proposed, total };
}

function buildContractMetrics(contracts: Contract[]): SpecificationSummary['contracts'] {
  const total = contracts.length;
  let active = 0;
  let verified = 0;
  let violated = 0;

  for (const contract of contracts) {
    if (contract.status === 'active') {
      active += 1;
    }
    if (contract.status === 'verified') {
      verified += 1;
    }
    if (contract.status === 'violated') {
      violated += 1;
    }
  }

  return { active, total, verified, violated };
}

function buildFeatureMetrics(features: Feature[]): SpecificationSummary['features'] {
  const total = features.length;
  let totalScenarios = 0;
  let passedScenarios = 0;

  for (const feature of features) {
    totalScenarios += feature.scenarioCount;
    passedScenarios += feature.passedScenarios;
  }

  let passRate = 0;
  if (totalScenarios > 0) {
    passRate = (passedScenarios / totalScenarios) * ONE_HUNDRED;
  }

  let coverage = 0;
  if (total > 0) {
    coverage = passRate;
  }

  return { coverage, passRate, scenarios: totalScenarios, total };
}

function computeFeaturePassRate(feature: Feature): number {
  if (feature.scenarioCount <= 0) {
    return 0;
  }
  return (feature.passedScenarios / feature.scenarioCount) * ONE_HUNDRED;
}

function computeHealthScore(summary: SpecificationSummary): number {
  let adrHealth = ONE_HUNDRED;
  if (summary.adrs.total > 0) {
    adrHealth = summary.adrs.averageCompliance;
  }

  let contractHealth = ONE_HUNDRED;
  if (summary.contracts.total > 0) {
    if (summary.contracts.active > 0) {
      contractHealth = (summary.contracts.verified / summary.contracts.active) * ONE_HUNDRED;
    } else {
      contractHealth = 0;
    }
  }

  let featureHealth = ONE_HUNDRED;
  if (summary.features.total > 0) {
    featureHealth = summary.features.passRate;
  }

  const weighted =
    adrHealth * ADR_WEIGHT + contractHealth * CONTRACT_WEIGHT + featureHealth * FEATURE_WEIGHT;
  return clampToPercentage(weighted);
}

export function buildSpecificationSummary(params: {
  projectId: string;
  adrs: ADR[];
  contracts: Contract[];
  features: Feature[];
}): SpecificationSummary {
  const adrMetrics = buildAdrMetrics(params.adrs);
  const contractMetrics = buildContractMetrics(params.contracts);
  const featureMetrics = buildFeatureMetrics(params.features);

  const summary: SpecificationSummary = {
    adrs: adrMetrics,
    contracts: contractMetrics,
    features: featureMetrics,
    healthDetails: [],
    healthScore: 0,
    projectId: params.projectId,
  };

  summary.healthScore = computeHealthScore(summary);

  const healthDetails: SpecificationSummary['healthDetails'] = [];

  // Architecture Decisions
  const adrIssues: string[] = [];
  if (adrMetrics.total === 0) {
    adrIssues.push('No ADRs created yet');
  } else {
    if (adrMetrics.accepted < adrMetrics.total / TWO) {
      adrIssues.push('Less than 50% ADRs accepted');
    }
  }
  healthDetails.push({
    category: 'Architecture Decisions',
    issues: adrIssues,
    score: Math.round(adrMetrics.averageCompliance),
  });

  // API Contracts
  const contractIssues: string[] = [];
  if (contractMetrics.total === 0) {
    contractIssues.push('No contracts defined');
  } else {
    if (contractMetrics.verified < contractMetrics.active) {
      contractIssues.push(
        `${contractMetrics.active - contractMetrics.verified} contracts unverified`,
      );
    }
  }
  let contractScore = ONE_HUNDRED;
  if (contractMetrics.total > 0) {
    if (contractMetrics.active > 0) {
      contractScore = Math.round((contractMetrics.verified / contractMetrics.active) * ONE_HUNDRED);
    } else {
      contractScore = 0;
    }
  }
  healthDetails.push({
    category: 'API Contracts',
    issues: contractIssues,
    score: contractScore,
  });

  // Feature Testing
  const featureIssues: string[] = [];
  if (featureMetrics.total === 0) {
    featureIssues.push('No features defined');
  } else {
    if (featureMetrics.passRate < PASS_RATE_GAP_THRESHOLD) {
      featureIssues.push('Pass rate below 80%');
      featureIssues.push('Pending scenarios detected');
    }
  }
  healthDetails.push({
    category: 'Feature Testing',
    issues: featureIssues,
    score: Math.round(featureMetrics.passRate),
  });

  summary.healthDetails = healthDetails;
  return summary;
}

export function buildCoverageData(features: Feature[], adrs: ADR[]): CoverageDataItem[] {
  const items: CoverageDataItem[] = [];

  for (const feature of features) {
    let coverage = 0;
    if (feature.scenarioCount > 0) {
      const numerator = feature.passedScenarios + feature.pendingScenarios;
      coverage = (numerator / feature.scenarioCount) * ONE_HUNDRED;
    }
    items.push({
      coverage,
      id: feature.id,
      label: feature.name,
      linked: true,
      testCases: feature.scenarioCount,
    });
  }

  const adrSlice = adrs.slice(0, MAX_ADR_COVERAGE_ITEMS);
  for (const adr of adrSlice) {
    items.push({
      adrs: 1,
      coverage: adr.complianceScore ?? 0,
      id: adr.id,
      label: adr.title,
      linked: true,
    });
  }

  return items;
}

export function buildGapItems(features: Feature[], contracts: Contract[]): GapItem[] {
  const gaps: GapItem[] = [];

  for (const feature of features) {
    const passRate = computeFeaturePassRate(feature);
    if (feature.scenarioCount > 0 && passRate < PASS_RATE_GAP_THRESHOLD) {
      gaps.push({
        affectedItems: 1,
        gapType: 'no_tests',
        id: `gap-${feature.id}`,
        impact: `${feature.failedScenarios} failing scenarios`,
        label: feature.name,
        priority: 'high',
        suggestion: 'Review and fix failing test scenarios',
      });
    }
  }

  for (const contract of contracts) {
    if (contract.status === 'violated') {
      gaps.push({
        affectedItems: 1,
        gapType: 'no_tests',
        id: `gap-${contract.id}`,
        impact: 'Contract verification failed',
        label: contract.title,
        priority: 'critical',
        suggestion: 'Run tests and fix contract violations',
      });
    }
  }

  return gaps.slice(0, MAX_GAP_ITEMS);
}
