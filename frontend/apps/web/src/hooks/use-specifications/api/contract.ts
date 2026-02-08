import type * as Types from '@tracertm/types';

import * as base from './base';
import * as decoders from './decoders';

// =============================================================================
// Transform
// =============================================================================

function transformContract(data: Record<string, unknown>): Types.Contract {
  return {
    contractNumber: decoders.asString(data['contract_number']),
    contractType: decoders.asContractType(data['contract_type']),
    createdAt: decoders.asString(data['created_at']),
    description: decoders.asOptionalString(data['description']),
    executableSpec: decoders.asOptionalString(data['executable_spec']),
    id: decoders.asString(data['id']),
    initialState: decoders.asOptionalString(data['initial_state']),
    invariants: decoders.asContractConditions(data['invariants']),
    itemId: decoders.asString(data['item_id']),
    lastVerifiedAt: decoders.asOptionalString(data['last_verified_at']),
    metadata: decoders.asRecord(data['metadata']),
    postconditions: decoders.asContractConditions(data['postconditions']),
    preconditions: decoders.asContractConditions(data['preconditions']),
    projectId: decoders.asString(data['project_id']),
    specLanguage: decoders.asSpecLanguage(data['spec_language']),
    states: decoders.asOptionalStringArray(data['states']),
    status: decoders.asContractStatus(data['status']),
    tags: decoders.asOptionalStringArray(data['tags']),
    title: decoders.asString(data['title']),
    transitions: decoders.asContractTransitions(data['transitions']),
    updatedAt: decoders.asString(data['updated_at']),
    verificationResult: decoders.buildVerificationResult(data['verification_result']),
    version: decoders.asNumber(data['version']),
  };
}

// =============================================================================
// API - Contracts
// =============================================================================

interface ContractFilters {
  projectId: string;
  status?: Types.ContractStatus;
  contractType?: Types.ContractType;
  search?: string;
}

async function fetchContracts(
  filters: ContractFilters,
): Promise<{ contracts: Types.Contract[]; total: number }> {
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

  const res = await fetch(`${base.API_URL}/api/v1/contracts?${params}`, {
    headers: { 'X-Bulk-Operation': 'true', ...base.getAuthHeaders() },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch contracts: ${res.status} ${errorText}`);
  }
  const data = decoders.toApiRecord(await res.json());
  return {
    contracts: decoders
      .asRecordArray(data['contracts'])
      .map((entry) => transformContract(entry)),
    total: decoders.asNumber(data['total']),
  };
}

async function fetchContract(id: string): Promise<Types.Contract> {
  const res = await fetch(`${base.API_URL}/api/v1/contracts/${id}`, {
    headers: base.getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch contract');
  }
  const data = decoders.toApiRecord(await res.json());
  return transformContract(data);
}

interface CreateContractData {
  projectId: string;
  itemId: string;
  title: string;
  description?: string;
  contractType: Types.ContractType;
  preconditions: unknown[];
  postconditions: unknown[];
  invariants: unknown[];
  tags?: string[];
  metadata?: Record<string, unknown>;
}

async function createContract(
  data: CreateContractData,
): Promise<{ id: string; contractNumber: string }> {
  const res = await fetch(`${base.API_URL}/api/v1/contracts`, {
    body: JSON.stringify({
      contract_type: data['contractType'],
      description: data['description'],
      invariants: data['invariants'],
      item_id: data['itemId'],
      metadata: base.withFallback(data['metadata'], {}),
      postconditions: data['postconditions'],
      preconditions: data['preconditions'],
      project_id: data['projectId'],
      tags: data['tags'],
      title: data['title'],
    }),
    headers: { 'Content-Type': 'application/json', ...base.getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create contract');
  }
  const result = decoders.toApiRecord(await res.json());
  return {
    contractNumber: decoders.asString(result['contract_number']),
    id: decoders.asString(result['id']),
  };
}

interface UpdateContractData {
  title?: string;
  description?: string;
  status?: Types.ContractStatus;
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
  base.assignDefined(body, [
    ['title', data['title']],
    ['description', data['description']],
    ['status', data['status']],
    ['preconditions', data['preconditions']],
    ['postconditions', data['postconditions']],
    ['invariants', data['invariants']],
    ['tags', data['tags']],
    ['metadata', data['metadata']],
  ]);

  const res = await fetch(`${base.API_URL}/api/v1/contracts/${id}`, {
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json', ...base.getAuthHeaders() },
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update contract');
  }
  const result = decoders.toApiRecord(await res.json());
  return {
    id: decoders.asString(result['id']),
    version: decoders.asNumber(result['version']),
  };
}

async function deleteContract(id: string): Promise<void> {
  const res = await fetch(`${base.API_URL}/api/v1/contracts/${id}`, {
    headers: base.getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete contract');
  }
}

async function verifyContract(id: string): Promise<{
  id: string;
  status: Types.ContractStatus;
  verificationResult: {
    status: string;
    passedConditions: number;
    failedConditions: number;
  };
}> {
  const res = await fetch(`${base.API_URL}/api/v1/contracts/${id}/verify`, {
    body: JSON.stringify({}),
    headers: { 'Content-Type': 'application/json', ...base.getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to verify contract');
  }
  const result = decoders.toApiRecord(await res.json());
  const verificationResult = decoders.toApiRecord(result['verification_result']);
  return {
    id: decoders.asString(result['id']),
    status: decoders.asContractStatus(result['status']),
    verificationResult: {
      status: decoders.asString(verificationResult['status']),
      passedConditions: decoders.asNumber(verificationResult['passed_conditions']),
      failedConditions: decoders.asNumber(verificationResult['failed_conditions']),
    },
  };
}

async function fetchContractActivities(contractId: string): Promise<Types.ContractActivity[]> {
  const res = await fetch(`${base.API_URL}/api/v1/contracts/${contractId}/activities`, {
    headers: base.getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch contract activities');
  }
  const data = decoders.toApiRecord(await res.json());
  const activities = decoders.asRecordArray(data['activities']);
  return activities.map((activity) => ({
    activityType: decoders.asString(activity['activity_type']),
    contractId: decoders.asString(activity['contract_id']),
    createdAt: decoders.asString(activity['created_at']),
    description: decoders.asOptionalString(activity['description']),
    fromValue: decoders.asOptionalString(activity['from_value']),
    id: decoders.asString(activity['id']),
    performedBy: decoders.asOptionalString(activity['performed_by']),
    toValue: decoders.asOptionalString(activity['to_value']),
  }));
}

async function fetchContractStats(projectId: string): Promise<Types.ContractStats> {
  const res = await fetch(`${base.API_URL}/api/v1/projects/${projectId}/contracts/stats`, {
    headers: base.getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch contract stats');
  }
  const data = decoders.toApiRecord(await res.json());
  return {
    byStatus: decoders.asNumberRecord(data['by_status']),
    byType: decoders.asNumberRecord(data['by_type']),
    projectId: decoders.asString(data['project_id']),
    total: decoders.asNumber(data['total']),
    verificationRate: decoders.asNumber(data['verification_rate']),
    violationCount: decoders.asNumber(data['violation_count']),
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
