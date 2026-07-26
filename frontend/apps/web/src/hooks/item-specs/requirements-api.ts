import type {
  RequirementSpec,
  RequirementSpecCreate,
  RequirementSpecUpdate,
  RequirementType,
  RiskLevel,
  VerificationStatus,
} from './types';

import {
  API_URL,
  DEFAULT_REQUIREMENT_LIMIT,
  appendParam,
  getAuthHeaders,
  getBulkHeaders,
  getJsonAuthHeaders,
  readJson,
} from './constants';

async function fetchRequirementSpecs(
  projectId: string,
  options?: {
    requirementType?: RequirementType;
    riskLevel?: RiskLevel;
    verificationStatus?: VerificationStatus;
    limit?: number;
    offset?: number;
  },
): Promise<{ specs: RequirementSpec[]; total: number }> {
  const params = new URLSearchParams();
  appendParam(params, 'requirement_type', options?.requirementType);
  appendParam(params, 'risk_level', options?.riskLevel);
  appendParam(params, 'verification_status', options?.verificationStatus);
  appendParam(params, 'limit', options?.limit);
  appendParam(params, 'offset', options?.offset);

  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/requirements?${params}`,
    { headers: getBulkHeaders() },
  );
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch requirement specs: ${res.status} ${errorText}`);
  }
  return readJson<{ specs: RequirementSpec[]; total: number }>(res);
}

async function fetchRequirementSpec(projectId: string, specId: string): Promise<RequirementSpec> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/${specId}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch requirement spec');
  }
  return readJson<RequirementSpec>(res);
}

async function fetchRequirementSpecByItem(
  projectId: string,
  itemId: string,
): Promise<RequirementSpec> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/by-item/${itemId}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch requirement spec by item');
  }
  return readJson<RequirementSpec>(res);
}

async function fetchUnverifiedRequirements(
  projectId: string,
  limit = DEFAULT_REQUIREMENT_LIMIT,
): Promise<{ specs: RequirementSpec[]; total: number }> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/unverified?limit=${limit}`,
    { headers: getBulkHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch unverified requirements');
  }
  return readJson<{ specs: RequirementSpec[]; total: number }>(res);
}

async function fetchHighRiskRequirements(
  projectId: string,
  limit = DEFAULT_REQUIREMENT_LIMIT,
): Promise<{ specs: RequirementSpec[]; total: number }> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/high-risk?limit=${limit}`,
    { headers: getBulkHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch high-risk requirements');
  }
  return readJson<{ specs: RequirementSpec[]; total: number }>(res);
}

async function createRequirementSpec(
  projectId: string,
  data: RequirementSpecCreate,
): Promise<RequirementSpec> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/requirements`, {
    body: JSON.stringify(data),
    headers: getJsonAuthHeaders(),
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create requirement spec');
  }
  return readJson<RequirementSpec>(res);
}

async function updateRequirementSpec(
  projectId: string,
  specId: string,
  data: RequirementSpecUpdate,
): Promise<RequirementSpec> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/${specId}`,
    {
      body: JSON.stringify(data),
      headers: getJsonAuthHeaders(),
      method: 'PATCH',
    },
  );
  if (!res.ok) {
    throw new Error('Failed to update requirement spec');
  }
  return readJson<RequirementSpec>(res);
}

async function deleteRequirementSpec(projectId: string, specId: string): Promise<void> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/${specId}`,
    { headers: getAuthHeaders(), method: 'DELETE' },
  );
  if (!res.ok) {
    throw new Error('Failed to delete requirement spec');
  }
}

async function analyzeRequirementQuality(
  projectId: string,
  specId: string,
): Promise<RequirementSpec> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/${specId}/analyze-quality`,
    { headers: getAuthHeaders(), method: 'POST' },
  );
  if (!res.ok) {
    throw new Error('Failed to analyze requirement quality');
  }
  return readJson<RequirementSpec>(res);
}

async function analyzeRequirementImpact(
  projectId: string,
  specId: string,
): Promise<RequirementSpec> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/${specId}/analyze-impact`,
    { headers: getAuthHeaders(), method: 'POST' },
  );
  if (!res.ok) {
    throw new Error('Failed to analyze requirement impact');
  }
  return readJson<RequirementSpec>(res);
}

async function verifyRequirement(
  projectId: string,
  specId: string,
  evidenceType: string,
  evidenceReference: string,
  description: string,
): Promise<RequirementSpec> {
  const params = new URLSearchParams({
    description,
    evidence_reference: evidenceReference,
    evidence_type: evidenceType,
  });
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/requirements/${specId}/verify?${params}`,
    { headers: getAuthHeaders(), method: 'POST' },
  );
  if (!res.ok) {
    throw new Error('Failed to verify requirement');
  }
  return readJson<RequirementSpec>(res);
}

export {
  fetchRequirementSpecs,
  fetchRequirementSpec,
  fetchRequirementSpecByItem,
  fetchUnverifiedRequirements,
  fetchHighRiskRequirements,
  createRequirementSpec,
  updateRequirementSpec,
  deleteRequirementSpec,
  analyzeRequirementQuality,
  analyzeRequirementImpact,
  verifyRequirement,
};
