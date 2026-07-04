import type {
  Contract,
  ContractActivity,
  ContractStats,
  ContractStatus,
  ContractType,
} from '@tracertm/types';

import { API_URL, assignDefined, getAuthHeaders, withFallback } from './base';
import { contractApiDecoders } from './contract-api-deps';

// =============================================================================
// Transform
// =============================================================================

function transformContract(data: Record<string, unknown>): Contract {
  return {
    contractNumber: contractApiDecoders.asString(data['contract_number']),
    contractType: contractApiDecoders.asContractType(data['contract_type']),
    createdAt: contractApiDecoders.asString(data['created_at']),
    description: contractApiDecoders.asOptionalString(data['description']),
    executableSpec: contractApiDecoders.asOptionalString(data['executable_spec']),
    id: contractApiDecoders.asString(data['id']),
    initialState: contractApiDecoders.asOptionalString(data['initial_state']),
    invariants: contractApiDecoders.asContractConditions(data['invariants']),
    itemId: contractApiDecoders.asString(data['item_id']),
    lastVerifiedAt: contractApiDecoders.asOptionalString(data['last_verified_at']),
    metadata: contractApiDecoders.asRecord(data['metadata']),
    postconditions: contractApiDecoders.asContractConditions(data['postconditions']),
    preconditions: contractApiDecoders.asContractConditions(data['preconditions']),
    projectId: contractApiDecoders.asString(data['project_id']),
    specLanguage: contractApiDecoders.asSpecLanguage(data['spec_language']),
    states: contractApiDecoders.asOptionalStringArray(data['states']),
    status: contractApiDecoders.asContractStatus(data['status']),
    tags: contractApiDecoders.asOptionalStringArray(data['tags']),
    title: contractApiDecoders.asString(data['title']),
    transitions: contractApiDecoders.asContractTransitions(data['transitions']),
    updatedAt: contractApiDecoders.asString(data['updated_at']),
    verificationResult: contractApiDecoders.buildVerificationResult(data['verification_result']),
    version: contractApiDecoders.asNumber(data['version']),
  };
}

// =============================================================================
// API - Contracts
// =============================================================================

interface ContractFilters {
  projectId: string;
  status?: ContractStatus | undefined;
  contractType?: ContractType | undefined;
  search?: string | undefined;
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
  const data = contractApiDecoders.toApiRecord(await res.json());
  return {
    contracts: contractApiDecoders
      .asRecordArray(data['contracts'])
      .map((entry) => transformContract(entry)),
    total: contractApiDecoders.asNumber(data['total']),
  };
}

async function fetchContract(id: string): Promise<Contract> {
  const res = await fetch(`${API_URL}/api/v1/contracts/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch contract');
  }
  const data = contractApiDecoders.toApiRecord(await res.json());
  return transformContract(data);
}

interface CreateContractData {
  projectId: string;
  itemId: string;
  title: string;
  description?: string | undefined;
  contractType: ContractType;
  preconditions: unknown[];
  postconditions: unknown[];
  invariants: unknown[];
  tags?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;
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
  const result = contractApiDecoders.toApiRecord(await res.json());
  return {
    contractNumber: contractApiDecoders.asString(result['contract_number']),
    id: contractApiDecoders.asString(result['id']),
  };
}

interface UpdateContractData {
  title?: string | undefined;
  description?: string | undefined;
  status?: ContractStatus | undefined;
  preconditions?: unknown[] | undefined;
  postconditions?: unknown[] | undefined;
  invariants?: unknown[] | undefined;
  tags?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;
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
  const result = contractApiDecoders.toApiRecord(await res.json());
  return {
    id: contractApiDecoders.asString(result['id']),
    version: contractApiDecoders.asNumber(result['version']),
  };
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
  const result = contractApiDecoders.toApiRecord(await res.json());
  const verificationResult = contractApiDecoders.toApiRecord(result['verification_result']);
  return {
    id: contractApiDecoders.asString(result['id']),
    status: contractApiDecoders.asContractStatus(result['status']),
    verificationResult: {
      status: contractApiDecoders.asString(verificationResult['status']),
      passedConditions: contractApiDecoders.asNumber(verificationResult['passed_conditions']),
      failedConditions: contractApiDecoders.asNumber(verificationResult['failed_conditions']),
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
  const data = contractApiDecoders.toApiRecord(await res.json());
  const activities = contractApiDecoders.asRecordArray(data['activities']);
  return activities.map((activity) => ({
    activityType: contractApiDecoders.asString(activity['activity_type']),
    contractId: contractApiDecoders.asString(activity['contract_id']),
    createdAt: contractApiDecoders.asString(activity['created_at']),
    description: contractApiDecoders.asOptionalString(activity['description']),
    fromValue: contractApiDecoders.asOptionalString(activity['from_value']),
    id: contractApiDecoders.asString(activity['id']),
    performedBy: contractApiDecoders.asOptionalString(activity['performed_by']),
    toValue: contractApiDecoders.asOptionalString(activity['to_value']),
  }));
}

async function fetchContractStats(projectId: string): Promise<ContractStats> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/contracts/stats`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch contract stats');
  }
  const data = contractApiDecoders.toApiRecord(await res.json());
  return {
    byStatus: contractApiDecoders.asNumberRecord(data['by_status']),
    byType: contractApiDecoders.asNumberRecord(data['by_type']),
    projectId: contractApiDecoders.asString(data['project_id']),
    total: contractApiDecoders.asNumber(data['total']),
    verificationRate: contractApiDecoders.asNumber(data['verification_rate']),
    violationCount: contractApiDecoders.asNumber(data['violation_count']),
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
