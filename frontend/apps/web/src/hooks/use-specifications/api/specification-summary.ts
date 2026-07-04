import type { SpecificationSummary } from '@tracertm/types';

import { API_URL, getAuthHeaders } from './base';
import { asNumber, asRecordArray, asString, asStringArray, toApiRecord } from './decoders';

async function fetchSpecificationSummary(projectId: string): Promise<SpecificationSummary> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/specifications/summary`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch specification summary');
  }
  const data = toApiRecord(await res.json());
  const adrs = toApiRecord(data['adrs']);
  const contracts = toApiRecord(data['contracts']);
  const features = toApiRecord(data['features']);
  return {
    projectId: asString(data['project_id']),
    adrs: {
      total: asNumber(adrs['total']),
      accepted: asNumber(adrs['accepted']),
      proposed: asNumber(adrs['proposed']),
      averageCompliance: asNumber(adrs['average_compliance']),
    },
    contracts: {
      total: asNumber(contracts['total']),
      active: asNumber(contracts['active']),
      verified: asNumber(contracts['verified']),
      violated: asNumber(contracts['violated']),
    },
    features: {
      total: asNumber(features['total']),
      scenarios: asNumber(features['scenarios']),
      passRate: asNumber(features['pass_rate']),
      coverage: asNumber(features['coverage']),
    },
    healthScore: asNumber(data['health_score']),
    healthDetails: asRecordArray(data['health_details']).map((entry) => ({
      category: asString(entry['category']),
      score: asNumber(entry['score']),
      issues: asStringArray(entry['issues']),
    })),
  };
}

export { fetchSpecificationSummary };
