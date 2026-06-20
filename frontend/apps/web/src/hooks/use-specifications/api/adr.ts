import type { ADR, ADRActivity, ADRStats, ADRStatus } from '@tracertm/types';

import { API_URL, assignDefined, getAuthHeaders, withFallback } from './base';
import {
  asADROptions,
  asADRStatusRequired,
  asNumber,
  asNumberRecord,
  asOptionalNumber,
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

function transformADR(data: Record<string, unknown>): ADR {
  return {
    adrNumber: asString(data['adr_number']),
    complianceScore: asOptionalNumber(data['compliance_score']),
    consequences: asString(data['consequences']),
    consideredOptions: asADROptions(data['considered_options']),
    context: asString(data['context']),
    createdAt: asString(data['created_at']),
    date: asOptionalString(data['date']),
    deciders: asOptionalStringArray(data['deciders']),
    decision: asString(data['decision']),
    decisionDrivers: asOptionalStringArray(data['decision_drivers']),
    id: asString(data['id']),
    lastVerifiedAt: asOptionalString(data['last_verified_at']),
    metadata: asRecord(data['metadata']),
    projectId: asString(data['project_id']),
    relatedAdrs: asOptionalStringArray(data['related_adrs']),
    relatedRequirements: asOptionalStringArray(data['related_requirements']),
    stakeholders: asOptionalStringArray(data['stakeholders']),
    status: asADRStatusRequired(data['status']),
    supersededBy: asOptionalString(data['superseded_by']),
    supersedes: asOptionalString(data['supersedes']),
    tags: asOptionalStringArray(data['tags']),
    title: asString(data['title']),
    updatedAt: asString(data['updated_at']),
    verificationNotes: asOptionalString(data['verification_notes']),
    version: asNumber(data['version']),
  };
}

// =============================================================================
// API - ADRs
// =============================================================================

interface ADRFilters {
  projectId: string;
  status?: ADRStatus | undefined;
  search?: string | undefined;
  tags?: string[] | undefined;
}

async function fetchADRs(filters: ADRFilters): Promise<{ adrs: ADR[]; total: number }> {
  const params = new URLSearchParams();
  params.set('project_id', filters.projectId);
  if (filters.status !== undefined) {
    params.set('status', filters.status);
  }
  if (filters.search !== undefined && filters.search.length > 0) {
    params.set('search', filters.search);
  }
  if (filters.tags !== undefined && filters.tags.length > 0) {
    params.set('tags', filters.tags.join(','));
  }

  const res = await fetch(`${API_URL}/api/v1/adrs?${params}`, {
    headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch ADRs: ${res.status} ${errorText}`);
  }
  const data = toApiRecord(await res.json());
  return {
    adrs: asRecordArray(data['adrs']).map((entry) => transformADR(entry)),
    total: asNumber(data['total']),
  };
}

async function fetchADR(id: string): Promise<ADR> {
  const res = await fetch(`${API_URL}/api/v1/adrs/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch ADR');
  }
  const data = toApiRecord(await res.json());
  return transformADR(data);
}

interface CreateADRData {
  projectId: string;
  title: string;
  context: string;
  decision: string;
  consequences: string;
  decisionDrivers?: string[] | undefined;
  deciders?: string[] | undefined;
  stakeholders?: string[] | undefined;
  tags?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;
}

async function createADR(data: CreateADRData): Promise<{ id: string; adrNumber: string }> {
  const res = await fetch(`${API_URL}/api/v1/adrs`, {
    body: JSON.stringify({
      consequences: data['consequences'],
      context: data['context'],
      deciders: data['deciders'],
      decision: data['decision'],
      decision_drivers: data['decisionDrivers'],
      metadata: withFallback(data['metadata'], {}),
      project_id: data['projectId'],
      stakeholders: data['stakeholders'],
      tags: data['tags'],
      title: data['title'],
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create ADR');
  }
  const result = toApiRecord(await res.json());
  return { adrNumber: asString(result['adr_number']), id: asString(result['id']) };
}

interface UpdateADRData {
  title?: string | undefined;
  context?: string | undefined;
  decision?: string | undefined;
  consequences?: string | undefined;
  status?: ADRStatus | undefined;
  decisionDrivers?: string[] | undefined;
  deciders?: string[] | undefined;
  stakeholders?: string[] | undefined;
  tags?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;
}

async function updateADR(
  id: string,
  data: UpdateADRData,
): Promise<{ id: string; version: number }> {
  const body: Record<string, unknown> = {};
  assignDefined(body, [
    ['title', data['title']],
    ['context', data['context']],
    ['decision', data['decision']],
    ['consequences', data['consequences']],
    ['status', data['status']],
    ['decision_drivers', data['decisionDrivers']],
    ['deciders', data['deciders']],
    ['stakeholders', data['stakeholders']],
    ['tags', data['tags']],
    ['metadata', data['metadata']],
  ]);

  const res = await fetch(`${API_URL}/api/v1/adrs/${id}`, {
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update ADR');
  }
  const result = toApiRecord(await res.json());
  return { id: asString(result['id']), version: asNumber(result['version']) };
}

async function deleteADR(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/adrs/${id}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete ADR');
  }
}

async function verifyADR(
  id: string,
  notes: string,
): Promise<{ id: string; complianceScore: number; lastVerifiedAt: string }> {
  const res = await fetch(`${API_URL}/api/v1/adrs/${id}/verify`, {
    body: JSON.stringify({ verification_notes: notes }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to verify ADR');
  }
  const result = toApiRecord(await res.json());
  return {
    complianceScore: asNumber(result['compliance_score']),
    id: asString(result['id']),
    lastVerifiedAt: asString(result['last_verified_at']),
  };
}

async function fetchADRActivities(adrId: string): Promise<ADRActivity[]> {
  const res = await fetch(`${API_URL}/api/v1/adrs/${adrId}/activities`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch ADR activities');
  }
  const data = toApiRecord(await res.json());
  const activities = asRecordArray(data['activities']);
  return activities.map((activity) => ({
    activityType: asString(activity['activity_type']),
    adrId: asString(activity['adr_id']),
    createdAt: asString(activity['created_at']),
    description: asOptionalString(activity['description']),
    fromValue: asOptionalString(activity['from_value']),
    id: asString(activity['id']),
    performedBy: asOptionalString(activity['performed_by']),
    toValue: asOptionalString(activity['to_value']),
  }));
}

async function fetchADRStats(projectId: string): Promise<ADRStats> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/adrs/stats`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch ADR stats');
  }
  const data = toApiRecord(await res.json());
  return {
    averageComplianceScore: asNumber(data['average_compliance_score']),
    byStatus: asNumberRecord(data['by_status']),
    pendingVerification: asNumber(data['pending_verification']),
    projectId: asString(data['project_id']),
    requirementsLinked: asNumber(data['requirements_linked']),
    total: asNumber(data['total']),
  };
}

export {
  createADR,
  deleteADR,
  fetchADR,
  fetchADRActivities,
  fetchADRs,
  fetchADRStats,
  updateADR,
  verifyADR,
  type ADRFilters,
  type CreateADRData,
  type UpdateADRData,
};
