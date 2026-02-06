import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type {
  ADR,
  ADRActivity,
  ADRStats,
  ADRStatus,
  Contract,
  ContractActivity,
  ContractStats,
  ContractStatus,
  ContractType,
  Feature,
  FeatureActivity,
  FeatureStats,
  FeatureStatus,
  Scenario,
  ScenarioActivity,
  ScenarioStatus,
  ScenarioStep,
  SpecificationSummary,
} from '@tracertm/types';

import { logger } from '@/lib/logger';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

const asNumber = (value: unknown, fallback = 0): number =>
  typeof value === 'number' ? value : fallback;
const asBoolean = (value: unknown, fallback = false): boolean =>
  typeof value === 'boolean' ? value : fallback;

// Helper to get auth token for fetch requests (object so it can be spread into headers)
function getAuthHeaders(): Record<string, string> {
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null;
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

// =============================================================================
// Transform Functions
// =============================================================================

function transformADR(data: Record<string, unknown>): ADR {
  const payload = data as Record<string, any>;
  return {
    adrNumber: payload['adr_number'],
    complianceScore: payload['compliance_score'],
    consequences: payload['consequences'],
    consideredOptions: payload['considered_options'],
    context: payload['context'],
    createdAt: payload['created_at'],
    date: payload['date'],
    deciders: payload['deciders'],
    decision: payload['decision'],
    decisionDrivers: payload['decision_drivers'],
    id: payload['id'],
    lastVerifiedAt: payload['last_verified_at'],
    metadata: payload['metadata'],
    projectId: payload['project_id'],
    relatedAdrs: payload['related_adrs'],
    relatedRequirements: payload['related_requirements'],
    stakeholders: payload['stakeholders'],
    status: payload['status'],
    supersededBy: payload['superseded_by'],
    supersedes: payload['supersedes'],
    tags: payload['tags'],
    title: payload['title'],
    updatedAt: payload['updated_at'],
    verificationNotes: payload['verification_notes'],
    version: payload['version'],
  };
}

function transformContract(data: Record<string, unknown>): Contract {
  const payload = data as Record<string, any>;
  return {
    contractNumber: payload['contract_number'],
    contractType: payload['contract_type'],
    createdAt: payload['created_at'],
    description: payload['description'],
    executableSpec: payload['executable_spec'],
    id: payload['id'],
    initialState: payload['initial_state'],
    invariants: payload['invariants'],
    itemId: payload['item_id'],
    lastVerifiedAt: payload['last_verified_at'],
    metadata: payload['metadata'],
    postconditions: payload['postconditions'],
    preconditions: payload['preconditions'],
    projectId: payload['project_id'],
    specLanguage: payload['spec_language'],
    states: payload['states'],
    status: payload['status'],
    tags: payload['tags'],
    title: payload['title'],
    transitions: payload['transitions'],
    updatedAt: payload['updated_at'],
    verificationResult: payload['verification_result'],
    version: payload['version'],
  };
}

function transformFeature(data: Record<string, unknown>): Feature {
  const payload = data as Record<string, any>;
  return {
    asA: payload['as_a'],
    createdAt: payload['created_at'],
    description: payload['description'],
    failedScenarios: asNumber(payload['failed_scenarios']),
    featureNumber: payload['feature_number'],
    filePath: payload['file_path'],
    iWant: payload['i_want'],
    id: payload['id'],
    metadata: payload['metadata'],
    name: payload['name'],
    passedScenarios: asNumber(payload['passed_scenarios']),
    pendingScenarios: asNumber(payload['pending_scenarios']),
    projectId: payload['project_id'],
    relatedAdrs: payload['related_adrs'],
    relatedRequirements: payload['related_requirements'],
    scenarioCount: asNumber(payload['scenario_count']),
    soThat: payload['so_that'],
    status: payload['status'],
    tags: payload['tags'],
    updatedAt: payload['updated_at'],
    version: payload['version'],
  };
}

function transformScenario(data: Record<string, unknown>): Scenario {
  const payload = data as Record<string, any>;
  return {
    background: payload['background'],
    createdAt: payload['created_at'],
    description: payload['description'],
    examples: payload['examples'],
    executionCount: asNumber(payload['execution_count']),
    featureId: payload['feature_id'],
    gherkinText: payload['gherkin_text'],
    givenSteps: (payload['given_steps'] as ScenarioStep[] | undefined) ?? [],
    id: payload['id'],
    isOutline: asBoolean(payload['is_outline']),
    lastRunAt: payload['last_run_at'],
    lastRunDurationMs: payload['last_run_duration_ms'],
    lastRunResult: payload['last_run_result'],
    metadata: payload['metadata'],
    passRate: asNumber(payload['pass_rate']),
    requirementIds: payload['requirement_ids'],
    scenarioNumber: payload['scenario_number'],
    status: payload['status'],
    tags: payload['tags'],
    testCaseIds: payload['test_case_ids'],
    thenSteps: (payload['then_steps'] as ScenarioStep[] | undefined) ?? [],
    title: payload['title'],
    updatedAt: payload['updated_at'],
    version: payload['version'],
    whenSteps: (payload['when_steps'] as ScenarioStep[] | undefined) ?? [],
  };
}

// =============================================================================
// API Fetch Functions - ADRs
// =============================================================================

interface ADRFilters {
  projectId: string;
  status?: ADRStatus;
  search?: string;
  tags?: string[];
}

async function fetchADRs(filters: ADRFilters): Promise<{ adrs: ADR[]; total: number }> {
  const params = new URLSearchParams();
  params.set('project_id', filters.projectId);
  if (filters.status) {
    params.set('status', filters.status);
  }
  if (filters.search) {
    params.set('search', filters.search);
  }
  if (filters.tags?.length) {
    params.set('tags', filters.tags.join(','));
  }

  const res = await fetch(`${API_URL}/api/v1/adrs?${params}`, {
    headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch ADRs: ${res.status} ${errorText}`);
  }
  const data = await res.json();
  return {
    adrs: (data['adrs'] || []).map(transformADR),
    total: data['total'] || 0,
  };
}

async function fetchADR(id: string): Promise<ADR> {
  const res = await fetch(`${API_URL}/api/v1/adrs/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch ADR');
  }
  const data = await res.json();
  return transformADR(data);
}

interface CreateADRData {
  projectId: string;
  title: string;
  context: string;
  decision: string;
  consequences: string;
  decisionDrivers?: string[];
  deciders?: string[];
  stakeholders?: string[];
  tags?: string[];
  metadata?: Record<string, unknown>;
}

async function createADR(data: CreateADRData): Promise<{ id: string; adrNumber: string }> {
  const res = await fetch(`${API_URL}/api/v1/adrs`, {
    body: JSON.stringify({
      consequences: data['consequences'],
      context: data['context'],
      deciders: data['deciders'],
      decision: data['decision'],
      decision_drivers: data['decisionDrivers'],
      metadata: data['metadata'] || {},
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
  const result = await res.json();
  return { adrNumber: result['adr_number'], id: result['id'] };
}

interface UpdateADRData {
  title?: string;
  context?: string;
  decision?: string;
  consequences?: string;
  status?: ADRStatus;
  decisionDrivers?: string[];
  deciders?: string[];
  stakeholders?: string[];
  tags?: string[];
  metadata?: Record<string, unknown>;
}

async function updateADR(
  id: string,
  data: UpdateADRData,
): Promise<{ id: string; version: number }> {
  const body: Record<string, unknown> = {};
  if (data['title'] !== undefined) {
    body['title'] = data['title'];
  }
  if (data['context'] !== undefined) {
    body['context'] = data['context'];
  }
  if (data['decision'] !== undefined) {
    body['decision'] = data['decision'];
  }
  if (data['consequences'] !== undefined) {
    body['consequences'] = data['consequences'];
  }
  if (data['status'] !== undefined) {
    body['status'] = data['status'];
  }
  if (data['decisionDrivers'] !== undefined) {
    body['decision_drivers'] = data['decisionDrivers'];
  }
  if (data['deciders'] !== undefined) {
    body['deciders'] = data['deciders'];
  }
  if (data['stakeholders'] !== undefined) {
    body['stakeholders'] = data['stakeholders'];
  }
  if (data['tags'] !== undefined) {
    body['tags'] = data['tags'];
  }
  if (data['metadata'] !== undefined) {
    body['metadata'] = data['metadata'];
  }

  const res = await fetch(`${API_URL}/api/v1/adrs/${id}`, {
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update ADR');
  }
  return res.json();
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
  const result = await res.json();
  return {
    complianceScore: result['compliance_score'],
    id: result['id'],
    lastVerifiedAt: result['last_verified_at'],
  };
}

async function fetchADRActivities(adrId: string): Promise<ADRActivity[]> {
  const res = await fetch(`${API_URL}/api/v1/adrs/${adrId}/activities`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch ADR activities');
  }
  const data = await res.json();
  return (data['activities'] || []).map((a: Record<string, any>) => ({
    activityType: a['activity_type'],
    adrId: a['adr_id'],
    createdAt: a['created_at'],
    description: a['description'],
    fromValue: a['from_value'],
    id: a['id'],
    performedBy: a['performed_by'],
    toValue: a['to_value'],
  }));
}

async function fetchContractActivities(contractId: string): Promise<ContractActivity[]> {
  const res = await fetch(`${API_URL}/api/v1/contracts/${contractId}/activities`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch contract activities');
  }
  const data = await res.json();
  return (data['activities'] || []).map((a: Record<string, any>) => ({
    activityType: a['activity_type'],
    contractId: a['contract_id'],
    createdAt: a['created_at'],
    description: a['description'],
    fromValue: a['from_value'],
    id: a['id'],
    performedBy: a['performed_by'],
    toValue: a['to_value'],
  }));
}

async function fetchFeatureActivities(featureId: string): Promise<FeatureActivity[]> {
  const res = await fetch(`${API_URL}/api/v1/features/${featureId}/activities`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch feature activities');
  }
  const data = await res.json();
  return (data['activities'] || []).map((a: Record<string, any>) => ({
    activityType: a['activity_type'],
    createdAt: a['created_at'],
    description: a['description'],
    featureId: a['feature_id'],
    fromValue: a['from_value'],
    id: a['id'],
    performedBy: a['performed_by'],
    toValue: a['to_value'],
  }));
}

async function fetchScenarioActivities(
  scenarioId: string,
  options: { limit?: number; offset?: number } = {},
): Promise<{ activities: ScenarioActivity[]; total: number }> {
  const params = new URLSearchParams();
  if (options.limit !== undefined) {
    params.set('limit', String(options.limit));
  }
  if (options.offset !== undefined) {
    params.set('offset', String(options.offset));
  }
  const res = await fetch(
    `${API_URL}/api/v1/specifications/scenarios/${scenarioId}/activities?${params}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch scenario activities');
  }
  const data = await res.json();
  return {
    activities: (data['activities'] || []).map((a: Record<string, any>) => ({
      activityType: a['activity_type'],
      createdAt: a['created_at'],
      description: a['description'],
      fromValue: a['from_value'],
      id: a['id'],
      performedBy: a['performed_by'],
      scenarioId: a['scenario_id'],
      toValue: a['to_value'],
    })),
    total: data['total'] || 0,
  };
}

async function fetchProjectScenarios(
  projectId: string,
  status?: string,
): Promise<{ scenarios: Scenario[]; total: number }> {
  const params = new URLSearchParams();
  if (status) {
    params.set('status', status);
  }
  const res = await fetch(
    `${API_URL}/api/v1/specifications/projects/${projectId}/scenarios?${params}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch scenarios: ${res.status} ${errorText}`);
  }
  const data = await res.json();
  return {
    scenarios: (data['scenarios'] || []).map(transformScenario),
    total: data['total'] || 0,
  };
}

async function fetchProjectScenarioActivities(
  projectId: string,
  options: {
    limit?: number;
    offset?: number;
    eventType?: string;
    since?: string;
    until?: string;
  } = {},
): Promise<ScenarioActivity[]> {
  const params = new URLSearchParams();
  if (options.limit !== undefined) {
    params.set('limit', String(options.limit));
  }
  if (options.offset !== undefined) {
    params.set('offset', String(options.offset));
  }
  if (options.eventType) {
    params.set('event_type', options.eventType);
  }
  if (options.since) {
    params.set('since', options.since);
  }
  if (options.until) {
    params.set('until', options.until);
  }
  const res = await fetch(
    `${API_URL}/api/v1/specifications/projects/${projectId}/scenarios/activities?${params}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch scenario activities');
  }
  const data = await res.json();
  return (data['activities'] || []).map((a: Record<string, any>) => ({
    activityType: a['activity_type'],
    createdAt: a['created_at'],
    description: a['description'],
    fromValue: a['from_value'],
    id: a['id'],
    performedBy: a['performed_by'],
    scenarioId: a['scenario_id'],
    toValue: a['to_value'],
  }));
}

async function fetchADRStats(projectId: string): Promise<ADRStats> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/adrs/stats`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch ADR stats');
  }
  const data = await res.json();
  return {
    averageComplianceScore: data['average_compliance_score'] || 0,
    byStatus: data['by_status'] || {},
    pendingVerification: data['pending_verification'] || 0,
    projectId: data['project_id'],
    requirementsLinked: data['requirements_linked'] || 0,
    total: data['total'] || 0,
  };
}

// =============================================================================
// API Fetch Functions - Contracts
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
  if (filters.status) {
    params.set('status', filters.status);
  }
  if (filters.contractType) {
    params.set('contract_type', filters.contractType);
  }
  if (filters.search) {
    params.set('search', filters.search);
  }

  const res = await fetch(`${API_URL}/api/v1/contracts?${params}`, {
    headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch contracts: ${res.status} ${errorText}`);
  }
  const data = await res.json();
  return {
    contracts: (data['contracts'] || []).map(transformContract),
    total: data['total'] || 0,
  };
}

async function fetchContract(id: string): Promise<Contract> {
  const res = await fetch(`${API_URL}/api/v1/contracts/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch contract');
  }
  const data = await res.json();
  return transformContract(data);
}

interface CreateContractData {
  projectId: string;
  itemId: string;
  title: string;
  description?: string;
  contractType: ContractType;
  preconditions: any[];
  postconditions: any[];
  invariants: any[];
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
      metadata: data['metadata'] || {},
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
  const result = await res.json();
  return { contractNumber: result['contract_number'], id: result['id'] };
}

interface UpdateContractData {
  title?: string;
  description?: string;
  status?: ContractStatus;
  preconditions?: any[];
  postconditions?: any[];
  invariants?: any[];
  tags?: string[];
  metadata?: Record<string, unknown>;
}

async function updateContract(
  id: string,
  data: UpdateContractData,
): Promise<{ id: string; version: number }> {
  const body: Record<string, unknown> = {};
  if (data['title'] !== undefined) {
    body['title'] = data['title'];
  }
  if (data['description'] !== undefined) {
    body['description'] = data['description'];
  }
  if (data['status'] !== undefined) {
    body['status'] = data['status'];
  }
  if (data['preconditions'] !== undefined) {
    body['preconditions'] = data['preconditions'];
  }
  if (data['postconditions'] !== undefined) {
    body['postconditions'] = data['postconditions'];
  }
  if (data['invariants'] !== undefined) {
    body['invariants'] = data['invariants'];
  }
  if (data['tags'] !== undefined) {
    body['tags'] = data['tags'];
  }
  if (data['metadata'] !== undefined) {
    body['metadata'] = data['metadata'];
  }

  const res = await fetch(`${API_URL}/api/v1/contracts/${id}`, {
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update contract');
  }
  return res.json();
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
  return res.json();
}

async function fetchContractStats(projectId: string): Promise<ContractStats> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/contracts/stats`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch contract stats');
  }
  const data = await res.json();
  return {
    byStatus: data['by_status'] || {},
    byType: data['by_type'] || {},
    projectId: data['project_id'],
    total: data['total'] || 0,
    verificationRate: data['verification_rate'] || 0,
    violationCount: data['violation_count'] || 0,
  };
}

// =============================================================================
// API Fetch Functions - Features
// =============================================================================

interface FeatureFilters {
  projectId: string;
  status?: FeatureStatus;
  search?: string;
}

async function fetchFeatures(
  filters: FeatureFilters,
): Promise<{ features: Feature[]; total: number }> {
  const params = new URLSearchParams();
  params.set('project_id', filters.projectId);
  if (filters.status) {
    params.set('status', filters.status);
  }
  if (filters.search) {
    params.set('search', filters.search);
  }

  const res = await fetch(`${API_URL}/api/v1/features?${params}`, {
    headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch features: ${res.status} ${errorText}`);
  }
  const data = await res.json();
  return {
    features: (data['features'] || []).map(transformFeature),
    total: data['total'] || 0,
  };
}

async function fetchFeature(id: string): Promise<Feature> {
  const res = await fetch(`${API_URL}/api/v1/features/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch feature');
  }
  const data = await res.json();
  return transformFeature(data);
}

interface CreateFeatureData {
  projectId: string;
  name: string;
  description?: string;
  asA?: string;
  iWant?: string;
  soThat?: string;
  filePath?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
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
      metadata: data['metadata'] || {},
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
  const result = await res.json();
  return { featureNumber: result['feature_number'], id: result['id'] };
}

interface UpdateFeatureData {
  name?: string;
  description?: string;
  asA?: string;
  iWant?: string;
  soThat?: string;
  status?: FeatureStatus;
  filePath?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
}

async function updateFeature(
  id: string,
  data: UpdateFeatureData,
): Promise<{ id: string; version: number }> {
  const body: Record<string, unknown> = {};
  if (data['name'] !== undefined) {
    body['name'] = data['name'];
  }
  if (data['description'] !== undefined) {
    body['description'] = data['description'];
  }
  if (data['asA'] !== undefined) {
    body['as_a'] = data['asA'];
  }
  if (data['iWant'] !== undefined) {
    body['i_want'] = data['iWant'];
  }
  if (data['soThat'] !== undefined) {
    body['so_that'] = data['soThat'];
  }
  if (data['status'] !== undefined) {
    body['status'] = data['status'];
  }
  if (data['filePath'] !== undefined) {
    body['file_path'] = data['filePath'];
  }
  if (data['tags'] !== undefined) {
    body['tags'] = data['tags'];
  }
  if (data['metadata'] !== undefined) {
    body['metadata'] = data['metadata'];
  }

  const res = await fetch(`${API_URL}/api/v1/features/${id}`, {
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update feature');
  }
  return res.json();
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

async function fetchFeatureStats(projectId: string): Promise<FeatureStats> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/features/stats`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch feature stats');
  }
  const data = await res.json();
  return {
    byStatus: data['by_status'] || {},
    coverage: {
      percentage: data['coverage']?.percentage || 0,
      requirementsCovered: data['coverage']?.requirements_covered || 0,
      totalRequirements: data['coverage']?.total_requirements || 0,
    },
    passRate: data['pass_rate'] || 0,
    projectId: data['project_id'],
    totalFeatures: data['total_features'] || 0,
    totalScenarios: data['total_scenarios'] || 0,
  };
}

// =============================================================================
// API Fetch Functions - Scenarios
// =============================================================================

async function fetchScenarios(
  featureId: string,
): Promise<{ scenarios: Scenario[]; total: number }> {
  const params = new URLSearchParams();
  params.set('feature_id', featureId);

  const res = await fetch(`${API_URL}/api/v1/scenarios?${params}`, {
    headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch scenarios: ${res.status} ${errorText}`);
  }
  const data = await res.json();
  return {
    scenarios: (data['scenarios'] || []).map(transformScenario),
    total: data['total'] || 0,
  };
}

async function fetchScenario(id: string): Promise<Scenario> {
  const res = await fetch(`${API_URL}/api/v1/scenarios/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch scenario');
  }
  const data = await res.json();
  return transformScenario(data);
}

interface CreateScenarioData {
  featureId: string;
  title: string;
  description?: string;
  gherkinText: string;
  givenSteps: ScenarioStep[];
  whenSteps: ScenarioStep[];
  thenSteps: ScenarioStep[];
  tags?: string[];
  requirementIds?: string[];
  metadata?: Record<string, unknown>;
}

async function createScenario(
  data: CreateScenarioData,
): Promise<{ id: string; scenarioNumber: string }> {
  const res = await fetch(`${API_URL}/api/v1/scenarios`, {
    body: JSON.stringify({
      description: data['description'],
      feature_id: data['featureId'],
      gherkin_text: data['gherkinText'],
      given_steps: data['givenSteps'],
      metadata: data['metadata'] || {},
      requirement_ids: data['requirementIds'],
      tags: data['tags'],
      then_steps: data['thenSteps'],
      title: data['title'],
      when_steps: data['whenSteps'],
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create scenario');
  }
  const result = await res.json();
  return { id: result['id'], scenarioNumber: result['scenario_number'] };
}

interface UpdateScenarioData {
  title?: string;
  description?: string;
  gherkinText?: string;
  givenSteps?: ScenarioStep[];
  whenSteps?: ScenarioStep[];
  thenSteps?: ScenarioStep[];
  tags?: string[];
  requirementIds?: string[];
  metadata?: Record<string, unknown>;
}

async function updateScenario(
  id: string,
  data: UpdateScenarioData,
): Promise<{ id: string; version: number }> {
  const body: Record<string, unknown> = {};
  if (data['title'] !== undefined) {
    body['title'] = data['title'];
  }
  if (data['description'] !== undefined) {
    body['description'] = data['description'];
  }
  if (data['gherkinText'] !== undefined) {
    body['gherkin_text'] = data['gherkinText'];
  }
  if (data['givenSteps'] !== undefined) {
    body['given_steps'] = data['givenSteps'];
  }
  if (data['whenSteps'] !== undefined) {
    body['when_steps'] = data['whenSteps'];
  }
  if (data['thenSteps'] !== undefined) {
    body['then_steps'] = data['thenSteps'];
  }
  if (data['tags'] !== undefined) {
    body['tags'] = data['tags'];
  }
  if (data['requirementIds'] !== undefined) {
    body['requirement_ids'] = data['requirementIds'];
  }
  if (data['metadata'] !== undefined) {
    body['metadata'] = data['metadata'];
  }

  const res = await fetch(`${API_URL}/api/v1/scenarios/${id}`, {
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update scenario');
  }
  return res.json();
}

async function deleteScenario(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/scenarios/${id}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete scenario');
  }
}

async function runScenario(id: string): Promise<{
  id: string;
  status: ScenarioStatus;
  lastRunAt: string;
  lastRunResult: string;
  executionCount: number;
}> {
  const res = await fetch(`${API_URL}/api/v1/scenarios/${id}/run`, {
    body: JSON.stringify({}),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to run scenario');
  }
  const result = await res.json();
  return {
    executionCount: asNumber(result['execution_count']),
    id: result['id'],
    lastRunAt: result['last_run_at'],
    lastRunResult: result['last_run_result'],
    status: result['status'],
  };
}

async function fetchSpecificationSummary(projectId: string): Promise<SpecificationSummary> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/specifications/summary`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch specification summary');
  }
  return res.json();
}

// =============================================================================
// React Query Hooks - ADRs
// =============================================================================

export function useADRs(filters: ADRFilters) {
  return useQuery({
    enabled: Boolean(filters.projectId),
    queryFn: () => fetchADRs(filters),
    queryKey: ['adrs', JSON.stringify(filters)],
  });
}

export function useADR(id: string) {
  return useQuery({
    enabled: Boolean(id),
    queryFn: () => fetchADR(id),
    queryKey: ['adrs', id],
  });
}

export function useCreateADR() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createADR,
    onSuccess: (_, variables) => {
      void queryClient.invalidateQueries({ queryKey: ['adrs'] });
      void queryClient.invalidateQueries({ queryKey: ['adrStats'] });
      return queryClient.invalidateQueries({
        queryKey: ['specificationSummary', variables.projectId],
      });
    },
  });
}

export function useUpdateADR() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateADRData }) => updateADR(id, data),
    onSuccess: (_, { id }) => {
      void queryClient.invalidateQueries({ queryKey: ['adrs', id] });
      void queryClient.invalidateQueries({ queryKey: ['adrs'] });
      return queryClient.invalidateQueries({ queryKey: ['adrStats'] });
    },
  });
}

export function useDeleteADR() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteADR,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['adrs'] });
      void queryClient.invalidateQueries({ queryKey: ['adrStats'] });
      return queryClient.invalidateQueries({ queryKey: ['specificationSummary'] });
    },
  });
}

export function useVerifyADR() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, notes }: { id: string; notes: string }) => verifyADR(id, notes),
    onSuccess: (_, { id }) => {
      void queryClient.invalidateQueries({ queryKey: ['adrs', id] });
      void queryClient.invalidateQueries({ queryKey: ['adrs'] });
      void queryClient.invalidateQueries({ queryKey: ['adrStats'] });
      return queryClient.invalidateQueries({ queryKey: ['specificationSummary'] });
    },
  });
}

export function useADRActivities(adrId: string) {
  return useQuery({
    enabled: Boolean(adrId),
    queryFn: () => fetchADRActivities(adrId),
    queryKey: ['adrActivities', adrId],
  });
}

export function useContractActivities(contractId: string) {
  return useQuery({
    enabled: Boolean(contractId),
    queryFn: () => fetchContractActivities(contractId),
    queryKey: ['contractActivities', contractId],
  });
}

export function useFeatureActivities(featureId: string) {
  return useQuery({
    enabled: Boolean(featureId),
    queryFn: () => fetchFeatureActivities(featureId),
    queryKey: ['featureActivities', featureId],
  });
}

export function useScenarioActivities(
  scenarioId: string,
  options?: { limit?: number; offset?: number },
) {
  return useQuery({
    enabled: Boolean(scenarioId),
    queryFn: () => fetchScenarioActivities(scenarioId, options),
    queryKey: ['scenarioActivities', scenarioId, JSON.stringify(options)],
  });
}

export function useProjectScenarios(projectId: string, status?: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: () => fetchProjectScenarios(projectId, status),
    queryKey: ['projectScenarios', projectId, status],
  });
}

export function useProjectScenarioActivities(
  projectId: string,
  options?: {
    limit?: number;
    offset?: number;
    eventType?: string;
    since?: string;
    until?: string;
  },
) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: () => fetchProjectScenarioActivities(projectId, options),
    queryKey: ['projectScenarioActivities', projectId, JSON.stringify(options)],
  });
}

export function useADRStats(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: () => fetchADRStats(projectId),
    queryKey: ['adrStats', projectId],
  });
}

// =============================================================================
// React Query Hooks - Contracts
// =============================================================================

export function useContracts(filters: ContractFilters) {
  return useQuery({
    enabled: Boolean(filters.projectId),
    queryFn: () => fetchContracts(filters),
    queryKey: ['contracts', JSON.stringify(filters)],
  });
}

export function useContract(id: string) {
  return useQuery({
    enabled: Boolean(id),
    queryFn: () => fetchContract(id),
    queryKey: ['contracts', id],
  });
}

export function useCreateContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createContract,
    onSuccess: (_, variables) => {
      void queryClient.invalidateQueries({ queryKey: ['contracts'] });
      void queryClient.invalidateQueries({ queryKey: ['contractStats'] });
      return queryClient.invalidateQueries({
        queryKey: ['specificationSummary', variables.projectId],
      });
    },
  });
}

export function useUpdateContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateContractData }) =>
      updateContract(id, data),
    onSuccess: (_, { id }) => {
      void queryClient.invalidateQueries({ queryKey: ['contracts', id] });
      return queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });
}

export function useDeleteContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteContract,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['contracts'] });
      void queryClient.invalidateQueries({ queryKey: ['contractStats'] });
      return queryClient.invalidateQueries({ queryKey: ['specificationSummary'] });
    },
  });
}

export function useVerifyContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => verifyContract(id),
    onSuccess: (_, id) => {
      void queryClient.invalidateQueries({ queryKey: ['contracts', id] });
      void queryClient.invalidateQueries({ queryKey: ['contracts'] });
      void queryClient.invalidateQueries({ queryKey: ['contractStats'] });
      return queryClient.invalidateQueries({ queryKey: ['specificationSummary'] });
    },
  });
}

export function useContractStats(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: () => fetchContractStats(projectId),
    queryKey: ['contractStats', projectId],
  });
}

// =============================================================================
// React Query Hooks - Features
// =============================================================================

export function useFeatures(filters: FeatureFilters) {
  return useQuery({
    enabled: Boolean(filters.projectId),
    queryFn: () => fetchFeatures(filters),
    queryKey: ['features', JSON.stringify(filters)],
  });
}

export function useFeature(id: string) {
  return useQuery({
    enabled: Boolean(id),
    queryFn: () => fetchFeature(id),
    queryKey: ['features', id],
  });
}

export function useCreateFeature() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createFeature,
    onSuccess: (_, variables) => {
      void queryClient.invalidateQueries({ queryKey: ['features'] });
      void queryClient.invalidateQueries({ queryKey: ['featureStats'] });
      return queryClient.invalidateQueries({
        queryKey: ['specificationSummary', variables.projectId],
      });
    },
  });
}

export function useUpdateFeature() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateFeatureData }) => updateFeature(id, data),
    onSuccess: (_, { id }) => {
      void queryClient.invalidateQueries({ queryKey: ['features', id] });
      return queryClient.invalidateQueries({ queryKey: ['features'] });
    },
  });
}

export function useDeleteFeature() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteFeature,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['features'] });
      void queryClient.invalidateQueries({ queryKey: ['featureStats'] });
      return queryClient.invalidateQueries({ queryKey: ['specificationSummary'] });
    },
  });
}

export function useFeatureStats(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: () => fetchFeatureStats(projectId),
    queryKey: ['featureStats', projectId],
  });
}

// =============================================================================
// React Query Hooks - Scenarios
// =============================================================================

export function useScenarios(featureId: string) {
  return useQuery({
    enabled: Boolean(featureId),
    queryFn: () => fetchScenarios(featureId),
    queryKey: ['scenarios', featureId],
  });
}

export function useScenario(id: string) {
  return useQuery({
    enabled: Boolean(id),
    queryFn: () => fetchScenario(id),
    queryKey: ['scenarios', id],
  });
}

export function useCreateScenario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createScenario,
    onSuccess: (_, variables) => {
      void queryClient.invalidateQueries({ queryKey: ['scenarios'] });
      void queryClient.invalidateQueries({ queryKey: ['projectScenarios'] });
      void queryClient.invalidateQueries({ queryKey: ['featureStats'] });
      return queryClient.invalidateQueries({ queryKey: ['specificationSummary'] });
    },
  });
}

export function useUpdateScenario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateScenarioData }) =>
      updateScenario(id, data),
    onSuccess: (_, { id }) => {
      void queryClient.invalidateQueries({ queryKey: ['scenarios', id] });
      void queryClient.invalidateQueries({ queryKey: ['scenarios'] });
      return queryClient.invalidateQueries({ queryKey: ['featureStats'] });
    },
  });
}

export function useDeleteScenario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteScenario,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['scenarios'] });
      void queryClient.invalidateQueries({ queryKey: ['projectScenarios'] });
      void queryClient.invalidateQueries({ queryKey: ['featureStats'] });
      return queryClient.invalidateQueries({ queryKey: ['specificationSummary'] });
    },
  });
}

export function useRunScenario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: runScenario,
    onSuccess: (_, id) => {
      void queryClient.invalidateQueries({ queryKey: ['scenarios', id] });
      void queryClient.invalidateQueries({ queryKey: ['scenarios'] });
      void queryClient.invalidateQueries({ queryKey: ['featureStats'] });
      return queryClient.invalidateQueries({ queryKey: ['specificationSummary'] });
    },
  });
}

// =============================================================================
// React Query Hooks - Summary
// =============================================================================

export function useSpecificationSummary(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: () => fetchSpecificationSummary(projectId),
    queryKey: ['specificationSummary', projectId],
  });
}

// =============================================================================
// React Query Hooks - Quality Reports
// =============================================================================

interface QualityReport {
  id: string;
  itemId: string;
  smells: string[];
  ambiguityScore: number;
  completenessScore: number;
  suggestions: string[];
  lastAnalyzedAt: string;
  version: number;
  createdAt: string;
  updatedAt: string;
}

async function fetchQualityReports(projectId: string): Promise<QualityReport[]> {
  // First, fetch all items for the project
  const authHeaders = getAuthHeaders();
  const itemsRes = await fetch(`${API_URL}/api/v1/items?project_id=${projectId}&limit=1000`, {
    headers: { 'X-Bulk-Operation': 'true', ...authHeaders },
  });
  if (!itemsRes.ok) {
    throw new Error(`Failed to fetch items: ${itemsRes.status}`);
  }
  const itemsData = await itemsRes.json();
  const items = itemsData.items || [];

  // Then fetch quality for each item (only items that have quality analysis)
  const qualityPromises = items.map(async (item: any) => {
    try {
      const qualityRes = await fetch(`${API_URL}/api/v1/quality/items/${item.id}`, {
        headers: authHeaders,
      });
      if (qualityRes.ok) {
        const qualityData = await qualityRes.json();
        return {
          ambiguityScore: qualityData.ambiguity_score || 0,
          completenessScore: qualityData.completeness_score || 0,
          createdAt: qualityData.created_at,
          id: qualityData.id,
          itemId: qualityData.item_id,
          lastAnalyzedAt: qualityData.last_analyzed_at,
          smells: qualityData.smells || [],
          suggestions: qualityData.suggestions || [],
          updatedAt: qualityData.updated_at,
          version: qualityData.version || 0,
        };
      }
      // If quality doesn't exist for this item, skip it (404 is expected)
      return null;
    } catch (error) {
      logger.warn(`Failed to fetch quality for item ${item.id}:`, error);
      return null;
    }
  });

  const results = await Promise.all(qualityPromises);
  return results.filter((r): r is QualityReport => r !== null);
}

export function useQualityReport(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: () => fetchQualityReports(projectId),
    queryKey: ['qualityReports', projectId],
  });
}
