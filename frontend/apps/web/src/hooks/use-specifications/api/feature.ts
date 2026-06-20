import type { Feature, FeatureActivity, FeatureStats, FeatureStatus } from '@tracertm/types';

import { API_URL, assignDefined, getAuthHeaders, withFallback } from './base';
import {
  asFeatureStatus,
  asNumber,
  asNumberRecord,
  asOptionalString,
  asOptionalStringArray,
  asRecord,
  asRecordArray,
  asString,
  toApiRecord,
} from './decoders';

// =============================================================================
// Transform
// =============================================================================

function transformFeature(data: Record<string, unknown>): Feature {
  return {
    asA: asOptionalString(data['as_a']),
    createdAt: asString(data['created_at']),
    description: asOptionalString(data['description']),
    failedScenarios: asNumber(data['failed_scenarios']),
    featureNumber: asString(data['feature_number']),
    filePath: asOptionalString(data['file_path']),
    iWant: asOptionalString(data['i_want']),
    id: asString(data['id']),
    metadata: asRecord(data['metadata']),
    name: asString(data['name']),
    passedScenarios: asNumber(data['passed_scenarios']),
    pendingScenarios: asNumber(data['pending_scenarios']),
    projectId: asString(data['project_id']),
    relatedAdrs: asOptionalStringArray(data['related_adrs']),
    relatedRequirements: asOptionalStringArray(data['related_requirements']),
    scenarioCount: asNumber(data['scenario_count']),
    soThat: asOptionalString(data['so_that']),
    status: asFeatureStatus(data['status']),
    tags: asOptionalStringArray(data['tags']),
    updatedAt: asString(data['updated_at']),
    version: asNumber(data['version']),
  };
}

// =============================================================================
// API - Features
// =============================================================================

interface FeatureFilters {
  projectId: string;
  status?: FeatureStatus | undefined;
  search?: string | undefined;
}

async function fetchFeatures(
  filters: FeatureFilters,
): Promise<{ features: Feature[]; total: number }> {
  const params = new URLSearchParams();
  params.set('project_id', filters.projectId);
  if (filters.status !== undefined) {
    params.set('status', filters.status);
  }
  if (filters.search !== undefined && filters.search.length > 0) {
    params.set('search', filters.search);
  }

  const res = await fetch(`${API_URL}/api/v1/features?${params}`, {
    headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch features: ${res.status} ${errorText}`);
  }
  const data = toApiRecord(await res.json());
  return {
    features: asRecordArray(data['features']).map((entry) => transformFeature(entry)),
    total: asNumber(data['total']),
  };
}

async function fetchFeature(id: string): Promise<Feature> {
  const res = await fetch(`${API_URL}/api/v1/features/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch feature');
  }
  const data = toApiRecord(await res.json());
  return transformFeature(data);
}

interface CreateFeatureData {
  projectId: string;
  name: string;
  description?: string | undefined;
  asA?: string | undefined;
  iWant?: string | undefined;
  soThat?: string | undefined;
  filePath?: string | undefined;
  tags?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;
}

async function createFeature(
  data: CreateFeatureData,
): Promise<{ id: string; featureNumber: string }> {
  const res = await fetch(`${API_URL}/api/v1/features`, {
    body: JSON.stringify({
      as_a: data['asA'],
      description: data['description'],
      file_path: data['filePath'],
      i_want: data['iWant'],
      metadata: withFallback(data['metadata'], {}),
      name: data.name,
      project_id: data['projectId'],
      so_that: data['soThat'],
      tags: data['tags'],
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create feature');
  }
  const result = toApiRecord(await res.json());
  return {
    featureNumber: asString(result['feature_number']),
    id: asString(result['id']),
  };
}

interface UpdateFeatureData {
  name?: string | undefined;
  description?: string | undefined;
  asA?: string | undefined;
  iWant?: string | undefined;
  soThat?: string | undefined;
  status?: FeatureStatus | undefined;
  filePath?: string | undefined;
  tags?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;
}

async function updateFeature(
  id: string,
  data: UpdateFeatureData,
): Promise<{ id: string; version: number }> {
  const body: Record<string, unknown> = {};
  assignDefined(body, [
    ['name', data['name']],
    ['description', data['description']],
    ['as_a', data['asA']],
    ['i_want', data['iWant']],
    ['so_that', data['soThat']],
    ['status', data['status']],
    ['file_path', data['filePath']],
    ['tags', data['tags']],
    ['metadata', data['metadata']],
  ]);

  const res = await fetch(`${API_URL}/api/v1/features/${id}`, {
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update feature');
  }
  const result = toApiRecord(await res.json());
  return { id: asString(result['id']), version: asNumber(result['version']) };
}

async function deleteFeature(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/features/${id}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete feature');
  }
}

async function fetchFeatureActivities(featureId: string): Promise<FeatureActivity[]> {
  const res = await fetch(`${API_URL}/api/v1/features/${featureId}/activities`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch feature activities');
  }
  const data = toApiRecord(await res.json());
  const activities = asRecordArray(data['activities']);
  return activities.map((activity) => ({
    activityType: asString(activity['activity_type']),
    createdAt: asString(activity['created_at']),
    description: asOptionalString(activity['description']),
    featureId: asString(activity['feature_id']),
    fromValue: asOptionalString(activity['from_value']),
    id: asString(activity['id']),
    performedBy: asOptionalString(activity['performed_by']),
    toValue: asOptionalString(activity['to_value']),
  }));
}

async function fetchFeatureStats(projectId: string): Promise<FeatureStats> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/features/stats`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch feature stats');
  }
  const data = toApiRecord(await res.json());
  const coverage = toApiRecord(data['coverage']);
  return {
    byStatus: asNumberRecord(data['by_status']),
    coverage: {
      percentage: asNumber(coverage?.['percentage']),
      requirementsCovered: asNumber(coverage?.['requirements_covered']),
      totalRequirements: asNumber(coverage?.['total_requirements']),
    },
    passRate: asNumber(data['pass_rate']),
    projectId: asString(data['project_id']),
    totalFeatures: asNumber(data['total_features']),
    totalScenarios: asNumber(data['total_scenarios']),
  };
}

export {
  createFeature,
  deleteFeature,
  fetchFeature,
  fetchFeatureActivities,
  fetchFeatures,
  fetchFeatureStats,
  updateFeature,
  type CreateFeatureData,
  type FeatureFilters,
  type UpdateFeatureData,
};
