import type { Contract, ContractActivity, ContractStats, ContractStatus, ContractType } from '@tracertm/types';

import { API_URL, assignDefined, getAuthHeaders, withFallback } from './base';
import {
  asContractConditions,
  asContractStatus,
  asContractTransitions,
  asContractType,
  asNumber,
  asNumberRecord,
  asOptionalString,
  asOptionalStringArray,
  asRecord,
  asRecordArray,
  asSpecLanguage,
  asString,
  buildVerificationResult,
  toApiRecord,
} from './decoders';

// =============================================================================
// Transform
// =============================================================================

function transformContract(data: Record<string, unknown>): Contract {
  return {
    contractNumber: asString(data['contract_number']),
    contractType: asContractType(data['contract_type']),
    createdAt: asString(data['created_at']),
    description: asOptionalString(data['description']),
    executableSpec: asOptionalString(data['executable_spec']),
    id: asString(data['id']),
    initialState: asOptionalString(data['initial_state']),
    invariants: asContractConditions(data['invariants']),
    itemId: asString(data['item_id']),
    lastVerifiedAt: asOptionalString(data['last_verified_at']),
    metadata: asRecord(data['metadata']),
    postconditions: asContractConditions(data['postconditions']),
    preconditions: asContractConditions(data['preconditions']),
    projectId: asString(data['project_id']),
    specLanguage: asSpecLanguage(data['spec_language']),
    states: asOptionalStringArray(data['states']),
    status: asContractStatus(data['status']),
    tags: asOptionalStringArray(data['tags']),
    title: asString(data['title']),
    transitions: asContractTransitions(data['transitions']),
    updatedAt: asString(data['updated_at']),
    verificationResult: buildVerificationResult(data['verification_result']),
    version: asNumber(data['version']),
  };
}

// =============================================================================
// API - Contracts
// =============================================================================

interface ContractFilters {
  projectId: string;
  status?: ContractStatus;
  contractType?: ContractType;
  search?: string;
}

async function fetchContracts(
  filters: ContractFilters,
): Promise<{ contracts: Contract[]; total: number }> {
  const params = new URLSearchParams();
  params.set('project_id', filters.projectId);
  if (filters.status !== undefined) {
    params.set('status', filters.status);
  }
  if (filters.contractType !== undefined) {
    params.set('contract_type', filters.contractType);
  }
  if (filters.search !== undefined && filters.search.length > 0) {
    params.set('search', filters.search);
  }

  const res = await fetch(`${API_URL}/api/v1/contracts?${params}`, {
    headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch contracts: ${res.status} ${errorText}`);
  }
  const data = toApiRecord(await res.json());
  return {
    contracts: asRecordArray(data['contracts']).map((entry) => transformContract(entry)),
    total: asNumber(data['total']),
  };
}

async function fetchContract(id: string): Promise<Contract> {
  const res = await fetch(`${API_URL}/api/v1/contracts/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch contract');
  }
  const data = toApiRecord(await res.json());
  return transformContract(data);
}

interface CreateContractData {
  projectId: string;
  itemId: string;
  title: string;
  description?: string;
  contractType: ContractType;
  preconditions: unknown[];
  postconditions: unknown[];
  invariants: unknown[];
  tags?: string[];
  metadata?: Record<string, unknown>;
}

async function createContract(
  data: CreateContractData,
): Promise<{ id: string; contractNumber: string }> {
  const res = await fetch(`${API_URL}/api/v1/contracts`, {
    body: JSON.stringify({
      contract_type: data['contractType'],
      description: data['description'],
      invariants: data['invariants'],
      item_id: data['itemId'],
      metadata: withFallback(data['metadata'], {}),
      postconditions: data['postconditions'],
      preconditions: data['preconditions'],
      project_id: data['projectId'],
      tags: data['tags'],
      title: data['title'],
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create contract');
  }
  const result = toApiRecord(await res.json());
  return {
    contractNumber: asString(result['contract_number']),
    id: asString(result['id']),
  };
}

interface UpdateContractData {
  title?: string;
  description?: string;
  status?: ContractStatus;
  preconditions?: unknown[];
  postconditions?: unknown[];
  invariants?: unknown[];
  tags?: string[];
  metadata?: Record<string, unknown>;
}

async function updateContract(
  id: string,
  data: UpdateContractData,
): Promise<{ id: string; version: number }> {
  const body: Record<string, unknown> = {};
  assignDefined(body, [
    ['title', data['title']],
    ['description', data['description']],
    ['status', data['status']],
    ['preconditions', data['preconditions']],
    ['postconditions', data['postconditions']],
    ['invariants', data['invariants']],
    ['tags', data['tags']],
    ['metadata', data['metadata']],
  ]);

  const res = await fetch(`${API_URL}/api/v1/contracts/${id}`, {
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update contract');
  }
  const result = toApiRecord(await res.json());
  return { id: asString(result['id']), version: asNumber(result['version']) };
}

async function deleteContract(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/contracts/${id}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete contract');
  }
}

async function verifyContract(id: string): Promise<{
  id: string;
  status: ContractStatus;
  verificationResult: {
    status: string;
    passedConditions: number;
    failedConditions: number;
  };
}> {
  const res = await fetch(`${API_URL}/api/v1/contracts/${id}/verify`, {
    body: JSON.stringify({}),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to verify contract');
  }
  const result = toApiRecord(await res.json());
  const verificationResult = toApiRecord(result['verification_result']);
  return {
    id: asString(result['id']),
    status: asContractStatus(result['status']),
    verificationResult: {
      status: asString(verificationResult['status']),
      passedConditions: asNumber(verificationResult['passed_conditions']),
      failedConditions: asNumber(verificationResult['failed_conditions']),
    },
  };
}

async function fetchContractActivities(contractId: string): Promise<ContractActivity[]> {
  const res = await fetch(`${API_URL}/api/v1/contracts/${contractId}/activities`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch contract activities');
  }
  const data = toApiRecord(await res.json());
  const activities = asRecordArray(data['activities']);
  return activities.map((activity) => ({
    activityType: asString(activity['activity_type']),
    contractId: asString(activity['contract_id']),
    createdAt: asString(activity['created_at']),
    description: asOptionalString(activity['description']),
    fromValue: asOptionalString(activity['from_value']),
    id: asString(activity['id']),
    performedBy: asOptionalString(activity['performed_by']),
    toValue: asOptionalString(activity['to_value']),
  }));
}

async function fetchContractStats(projectId: string): Promise<ContractStats> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/contracts/stats`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch contract stats');
  }
  const data = toApiRecord(await res.json());
  return {
    byStatus: asNumberRecord(data['by_status']),
    byType: asNumberRecord(data['by_type']),
    projectId: asString(data['project_id']),
    total: asNumber(data['total']),
    verificationRate: asNumber(data['verification_rate']),
    violationCount: asNumber(data['violation_count']),
  };
}

export {
  createContract,
  deleteContract,
  fetchContract,
  fetchContractActivities,
  fetchContracts,
  fetchContractStats,
  updateContract,
  verifyContract,
  type ContractFilters,
  type CreateContractData,
  type UpdateContractData,
};

