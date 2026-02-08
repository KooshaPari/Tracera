import type {
  ADR,
  ADRActivity,
  ADRStats,
  ADRStatus,
  ADROption,
  Contract,
  ContractActivity,
  ContractCondition,
  ContractStats,
  ContractStatus,
  ContractTransition,
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

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:4000';

type ApiRecord = Record<string, unknown>;

const asNumber = (value: unknown, fallback = 0): number => {
  if (typeof value === 'number') {
    return value;
  }
  return fallback;
};

const asBoolean = (value: unknown, fallback = false): boolean => {
  if (typeof value === 'boolean') {
    return value;
  }
  return fallback;
};

const isApiRecord = (value: unknown): value is ApiRecord =>
  typeof value === 'object' && Object.prototype.toString.call(value) !== '[object Null]';

const toApiRecord = (value: unknown): ApiRecord => {
  if (!isApiRecord(value)) {
    return {};
  }
  return value;
};

const asRecord = (value: unknown): ApiRecord | undefined => {
  if (!isApiRecord(value)) {
    return;
  }
  return value;
};

const asString = (value: unknown): string => {
  if (typeof value === 'string') {
    return value;
  }
  return '';
};

const asOptionalString = (value: unknown): string | undefined => {
  if (typeof value !== 'string') {
    return;
  }
  return value;
};

const asOptionalNumber = (value: unknown): number | undefined => {
  if (typeof value !== 'number') {
    return;
  }
  return value;
};

const asStringArray = (value: unknown): string[] => {
  if (!Array.isArray(value)) {
    return [];
  }
  const result: string[] = [];
  for (const entry of value) {
    if (typeof entry === 'string') {
      result.push(entry);
    }
  }
  return result;
};

const asOptionalStringArray = (value: unknown): string[] | undefined => {
  if (!Array.isArray(value)) {
    return;
  }
  const result: string[] = [];
  for (const entry of value) {
    if (typeof entry === 'string') {
      result.push(entry);
    }
  }
  return result;
};

const asNumberRecord = (value: unknown): Record<string, number> => {
  if (!isApiRecord(value)) {
    return {};
  }
  const result: Record<string, number> = {};
  for (const [key, entry] of Object.entries(value)) {
    if (typeof entry === 'number') {
      result[key] = entry;
    }
  }
  return result;
};

const asStringTable = (value: unknown): string[][] | undefined => {
  if (!Array.isArray(value)) {
    return;
  }
  const rows: string[][] = [];
  for (const row of value) {
    if (Array.isArray(row)) {
      const rowValues: string[] = [];
      for (const cell of row) {
        if (typeof cell === 'string') {
          rowValues.push(cell);
        }
      }
      rows.push(rowValues);
    }
  }
  return rows;
};

const asScenarioStepKeyword = (value: unknown): ScenarioStep['keyword'] => {
  const text = asString(value);
  switch (text) {
    case 'Given': {
      return text;
    }
    case 'When': {
      return text;
    }
    case 'Then': {
      return text;
    }
    case 'And': {
      return text;
    }
    case 'But': {
      return text;
    }
    default: {
      return 'Given';
    }
  }
};

const asScenarioSteps = (value: unknown): ScenarioStep[] => {
  if (!Array.isArray(value)) {
    return [];
  }
  const steps: ScenarioStep[] = [];
  for (const entry of value) {
    if (isApiRecord(entry) && typeof entry['text'] === 'string') {
      let stepNumberValue = entry['step_number'];
      if (stepNumberValue === undefined) {
        stepNumberValue = entry['stepNumber'];
      }
      let dataTableValue = entry['data_table'];
      if (dataTableValue === undefined) {
        dataTableValue = entry['dataTable'];
      }
      steps.push({
        stepNumber: asNumber(stepNumberValue),
        keyword: asScenarioStepKeyword(entry['keyword']),
        text: asString(entry['text']),
        dataTable: asStringTable(dataTableValue),
        docString: asOptionalString(entry['doc_string']),
        stepDefinitionId: asOptionalString(entry['step_definition_id']),
      });
    }
  }
  return steps;
};

const asOptionalScenarioSteps = (value: unknown): ScenarioStep[] | undefined => {
  if (!Array.isArray(value)) {
    return;
  }
  return asScenarioSteps(value);
};

const asExamples = (value: unknown): Record<string, string[]> | undefined => {
  if (!isApiRecord(value)) {
    return;
  }
  const result: Record<string, string[]> = {};
  for (const [key, entry] of Object.entries(value)) {
    if (Array.isArray(entry)) {
      result[key] = asStringArray(entry);
    }
  }
  return result;
};

const asADROptions = (value: unknown): ADROption[] | undefined => {
  if (!Array.isArray(value)) {
    return;
  }
  const options: ADROption[] = [];
  for (const entry of value) {
    if (isApiRecord(entry)) {
      let chosenValue = entry['is_chosen'];
      if (chosenValue === undefined) {
        chosenValue = entry['isChosen'];
      }
      options.push({
        id: asString(entry['id']),
        title: asString(entry['title']),
        description: asString(entry['description']),
        pros: asOptionalStringArray(entry['pros']),
        cons: asOptionalStringArray(entry['cons']),
        isChosen: asBoolean(chosenValue),
      });
    }
  }
  return options;
};

const asContractConditionResult = (value: unknown): ContractCondition['lastVerifiedResult'] => {
  const text = asOptionalString(value);
  switch (text) {
    case 'pass': {
      return text;
    }
    case 'fail': {
      return text;
    }
    case 'skip': {
      return text;
    }
    default: {
      return;
    }
  }
};

const asContractConditions = (value: unknown): ContractCondition[] => {
  if (!Array.isArray(value)) {
    return [];
  }
  const conditions: ContractCondition[] = [];
  for (const entry of value) {
    if (isApiRecord(entry)) {
      let requiredValue = entry['is_required'];
      if (requiredValue === undefined) {
        requiredValue = entry['isRequired'];
      }
      let lastResultValue = entry['last_verified_result'];
      if (lastResultValue === undefined) {
        lastResultValue = entry['lastVerifiedResult'];
      }
      conditions.push({
        id: asString(entry['id']),
        description: asString(entry['description']),
        expression: asOptionalString(entry['expression']),
        isRequired: asBoolean(requiredValue),
        lastVerifiedResult: asContractConditionResult(lastResultValue),
      });
    }
  }
  return conditions;
};

const asContractTransitions = (value: unknown): ContractTransition[] | undefined => {
  if (!Array.isArray(value)) {
    return;
  }
  const transitions: ContractTransition[] = [];
  for (const entry of value) {
    if (isApiRecord(entry)) {
      let fromStateValue = entry['from_state'];
      if (fromStateValue === undefined) {
        fromStateValue = entry['fromState'];
      }
      let toStateValue = entry['to_state'];
      if (toStateValue === undefined) {
        toStateValue = entry['toState'];
      }
      transitions.push({
        id: asString(entry['id']),
        fromState: asString(fromStateValue),
        toState: asString(toStateValue),
        trigger: asString(entry['trigger']),
        guards: asOptionalStringArray(entry['guards']),
        actions: asOptionalStringArray(entry['actions']),
      });
    }
  }
  return transitions;
};

const asSpecLanguage = (value: unknown): Contract['specLanguage'] => {
  const text = asOptionalString(value);
  if (text === 'typescript' || text === 'python' || text === 'gherkin') {
    return text;
  }
  return;
};

const asScenarioStatus = (value: unknown): ScenarioStatus => {
  const text = asString(value);
  switch (text) {
    case 'draft': {
      return text;
    }
    case 'pending': {
      return text;
    }
    case 'passed': {
      return 'passing';
    }
    case 'failed': {
      return 'failing';
    }
    case 'passing': {
      return text;
    }
    case 'failing': {
      return text;
    }
    case 'skipped': {
      return text;
    }
    default: {
      return 'draft';
    }
  }
};

const asRunResult = (value: unknown): Scenario['lastRunResult'] => {
  const text = asOptionalString(value);
  switch (text) {
    case 'pass': {
      return text;
    }
    case 'fail': {
      return text;
    }
    case 'pending': {
      return text;
    }
    case 'error': {
      return text;
    }
    default: {
      return;
    }
  }
};

const asADRStatus = (value: unknown): ADRStatus | undefined => {
  const text = asOptionalString(value);
  if (text === undefined) {
    return;
  }
  switch (text) {
    case 'proposed': {
      return text;
    }
    case 'accepted': {
      return text;
    }
    case 'deprecated': {
      return text;
    }
    case 'superseded': {
      return text;
    }
    case 'rejected': {
      return text;
    }
    default: {
      return;
    }
  }
};

const asADRStatusRequired = (value: unknown): ADRStatus => {
  const status = asADRStatus(value);
  if (status !== undefined) {
    return status;
  }
  return 'proposed';
};

const asContractType = (value: unknown): ContractType => {
  const text = asString(value);
  switch (text) {
    case 'api': {
      return text;
    }
    case 'function': {
      return text;
    }
    case 'invariant': {
      return text;
    }
    case 'data': {
      return text;
    }
    case 'integration': {
      return text;
    }
    default: {
      return 'api';
    }
  }
};

const asContractStatus = (value: unknown): ContractStatus => {
  const text = asString(value);
  switch (text) {
    case 'draft': {
      return text;
    }
    case 'active': {
      return text;
    }
    case 'verified': {
      return text;
    }
    case 'violated': {
      return text;
    }
    case 'deprecated': {
      return text;
    }
    default: {
      return 'draft';
    }
  }
};

const asFeatureStatus = (value: unknown): FeatureStatus => {
  const text = asString(value);
  switch (text) {
    case 'draft': {
      return text;
    }
    case 'active': {
      return text;
    }
    case 'deprecated': {
      return text;
    }
    case 'archived': {
      return text;
    }
    default: {
      return 'draft';
    }
  }
};

const asVerificationStatus = (value: unknown): 'pass' | 'fail' | 'error' => {
  const text = asString(value);
  switch (text) {
    case 'pass': {
      return text;
    }
    case 'fail': {
      return text;
    }
    case 'error': {
      return text;
    }
    default: {
      return 'error';
    }
  }
};

const setOptionalParam = (
  params: URLSearchParams,
  key: string,
  value: number | undefined,
): void => {
  if (value !== undefined) {
    params.set(key, String(value));
  }
};

const setOptionalStringParam = (
  params: URLSearchParams,
  key: string,
  value: string | undefined,
): void => {
  if (value !== undefined && value.length > 0) {
    params.set(key, value);
  }
};

const asRecordArray = (value: unknown): ApiRecord[] => {
  if (Array.isArray(value)) {
    return value.filter(isApiRecord);
  }
  return [];
};

// Helper to get auth token for fetch requests (object so it can be spread into headers)
function getAuthHeaders(): Record<string, string> {
  if (typeof localStorage === 'undefined') {
    return {};
  }
  const token = withFallback(localStorage.getItem('auth_token'), '');
  const headers: Record<string, string> = {};
  if (token.length > 0) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

// =============================================================================
// Transform Functions
// =============================================================================

function transformADR(data: Record<string, unknown>): ADR {
  const payload: ApiRecord = data;
  return {
    adrNumber: asString(payload['adr_number']),
    complianceScore: asOptionalNumber(payload['compliance_score']),
    consequences: asString(payload['consequences']),
    consideredOptions: asADROptions(payload['considered_options']),
    context: asString(payload['context']),
    createdAt: asString(payload['created_at']),
    date: asOptionalString(payload['date']),
    deciders: asOptionalStringArray(payload['deciders']),
    decision: asString(payload['decision']),
    decisionDrivers: asOptionalStringArray(payload['decision_drivers']),
    id: asString(payload['id']),
    lastVerifiedAt: asOptionalString(payload['last_verified_at']),
    metadata: asRecord(payload['metadata']),
    projectId: asString(payload['project_id']),
    relatedAdrs: asOptionalStringArray(payload['related_adrs']),
    relatedRequirements: asOptionalStringArray(payload['related_requirements']),
    stakeholders: asOptionalStringArray(payload['stakeholders']),
    status: asADRStatusRequired(payload['status']),
    supersededBy: asOptionalString(payload['superseded_by']),
    supersedes: asOptionalString(payload['supersedes']),
    tags: asOptionalStringArray(payload['tags']),
    title: asString(payload['title']),
    updatedAt: asString(payload['updated_at']),
    verificationNotes: asOptionalString(payload['verification_notes']),
    version: asNumber(payload['version']),
  };
}

function transformContract(data: Record<string, unknown>): Contract {
  const payload: ApiRecord = data;
  return {
    contractNumber: asString(payload['contract_number']),
    contractType: asContractType(payload['contract_type']),
    createdAt: asString(payload['created_at']),
    description: asOptionalString(payload['description']),
    executableSpec: asOptionalString(payload['executable_spec']),
    id: asString(payload['id']),
    initialState: asOptionalString(payload['initial_state']),
    invariants: asContractConditions(payload['invariants']),
    itemId: asString(payload['item_id']),
    lastVerifiedAt: asOptionalString(payload['last_verified_at']),
    metadata: asRecord(payload['metadata']),
    postconditions: asContractConditions(payload['postconditions']),
    preconditions: asContractConditions(payload['preconditions']),
    projectId: asString(payload['project_id']),
    specLanguage: asSpecLanguage(payload['spec_language']),
    states: asOptionalStringArray(payload['states']),
    status: asContractStatus(payload['status']),
    tags: asOptionalStringArray(payload['tags']),
    title: asString(payload['title']),
    transitions: asContractTransitions(payload['transitions']),
    updatedAt: asString(payload['updated_at']),
    verificationResult: buildVerificationResult(payload['verification_result']),
    version: asNumber(payload['version']),
  };
}

function transformFeature(data: Record<string, unknown>): Feature {
  const payload: ApiRecord = data;
  return {
    asA: asOptionalString(payload['as_a']),
    createdAt: asString(payload['created_at']),
    description: asOptionalString(payload['description']),
    failedScenarios: asNumber(payload['failed_scenarios']),
    featureNumber: asString(payload['feature_number']),
    filePath: asOptionalString(payload['file_path']),
    iWant: asOptionalString(payload['i_want']),
    id: asString(payload['id']),
    metadata: asRecord(payload['metadata']),
    name: asString(payload['name']),
    passedScenarios: asNumber(payload['passed_scenarios']),
    pendingScenarios: asNumber(payload['pending_scenarios']),
    projectId: asString(payload['project_id']),
    relatedAdrs: asOptionalStringArray(payload['related_adrs']),
    relatedRequirements: asOptionalStringArray(payload['related_requirements']),
    scenarioCount: asNumber(payload['scenario_count']),
    soThat: asOptionalString(payload['so_that']),
    status: asFeatureStatus(payload['status']),
    tags: asOptionalStringArray(payload['tags']),
    updatedAt: asString(payload['updated_at']),
    version: asNumber(payload['version']),
  };
}

function transformScenario(data: Record<string, unknown>): Scenario {
  const payload: ApiRecord = data;
  return {
    background: asOptionalScenarioSteps(payload['background']),
    createdAt: asString(payload['created_at']),
    description: asOptionalString(payload['description']),
    examples: asExamples(payload['examples']),
    executionCount: asNumber(payload['execution_count']),
    featureId: asString(payload['feature_id']),
    gherkinText: asString(payload['gherkin_text']),
    givenSteps: asScenarioSteps(payload['given_steps']),
    id: asString(payload['id']),
    isOutline: asBoolean(payload['is_outline']),
    lastRunAt: asOptionalString(payload['last_run_at']),
    lastRunDurationMs: asOptionalNumber(payload['last_run_duration_ms']),
    lastRunResult: asRunResult(payload['last_run_result']),
    metadata: asRecord(payload['metadata']),
    passRate: asNumber(payload['pass_rate']),
    requirementIds: asOptionalStringArray(payload['requirement_ids']),
    scenarioNumber: asString(payload['scenario_number']),
    status: asScenarioStatus(payload['status']),
    tags: asOptionalStringArray(payload['tags']),
    testCaseIds: asOptionalStringArray(payload['test_case_ids']),
    thenSteps: asScenarioSteps(payload['then_steps']),
    title: asString(payload['title']),
    updatedAt: asString(payload['updated_at']),
    version: asNumber(payload['version']),
    whenSteps: asScenarioSteps(payload['when_steps']),
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
    adrs: asRecordArray(data['adrs']).map(transformADR),
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
  decisionDrivers?: string[];
  deciders?: string[];
  stakeholders?: string[];
  tags?: string[];
  metadata?: Record<string, unknown>;
}

const withFallback = <Value>(value: Value | undefined, fallback: Value): Value => {
  if (value !== undefined) {
    return value;
  }
  return fallback;
};

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

function assignDefined(body: ApiRecord, entries: [string, unknown | undefined][]): void {
  for (const [key, value] of entries) {
    if (value !== undefined) {
      body[key] = value;
    }
  }
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

async function fetchScenarioActivities(
  scenarioId: string,
  options: { limit?: number; offset?: number } = {},
): Promise<{ activities: ScenarioActivity[]; total: number }> {
  const params = new URLSearchParams();
  setOptionalParam(params, 'limit', options.limit);
  setOptionalParam(params, 'offset', options.offset);
  const res = await fetch(
    `${API_URL}/api/v1/specifications/scenarios/${scenarioId}/activities?${params}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch scenario activities');
  }
  const data = toApiRecord(await res.json());
  const activities = asRecordArray(data['activities']);
  return {
    activities: activities.map((activity) => ({
      activityType: asString(activity['activity_type']),
      createdAt: asString(activity['created_at']),
      description: asOptionalString(activity['description']),
      fromValue: asOptionalString(activity['from_value']),
      id: asString(activity['id']),
      performedBy: asOptionalString(activity['performed_by']),
      scenarioId: asString(activity['scenario_id']),
      toValue: asOptionalString(activity['to_value']),
    })),
    total: asNumber(data['total']),
  };
}

async function fetchProjectScenarios(
  projectId: string,
  status?: string,
): Promise<{ scenarios: Scenario[]; total: number }> {
  const params = new URLSearchParams();
  if (status !== undefined && status.length > 0) {
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
  const data = toApiRecord(await res.json());
  return {
    scenarios: asRecordArray(data['scenarios']).map(transformScenario),
    total: asNumber(data['total']),
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
  setOptionalParam(params, 'limit', options.limit);
  setOptionalParam(params, 'offset', options.offset);
  setOptionalStringParam(params, 'event_type', options.eventType);
  setOptionalStringParam(params, 'since', options.since);
  setOptionalStringParam(params, 'until', options.until);
  const res = await fetch(
    `${API_URL}/api/v1/specifications/projects/${projectId}/scenarios/activities?${params}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch scenario activities');
  }
  const data = toApiRecord(await res.json());
  const activities = asRecordArray(data['activities']);
  return activities.map((activity) => ({
    activityType: asString(activity['activity_type']),
    createdAt: asString(activity['created_at']),
    description: asOptionalString(activity['description']),
    fromValue: asOptionalString(activity['from_value']),
    id: asString(activity['id']),
    performedBy: asOptionalString(activity['performed_by']),
    scenarioId: asString(activity['scenario_id']),
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
    contracts: asRecordArray(data['contracts']).map(transformContract),
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
    features: asRecordArray(data['features']).map(transformFeature),
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
  const data = toApiRecord(await res.json());
  return {
    scenarios: asRecordArray(data['scenarios']).map(transformScenario),
    total: asNumber(data['total']),
  };
}

async function fetchScenario(id: string): Promise<Scenario> {
  const res = await fetch(`${API_URL}/api/v1/scenarios/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch scenario');
  }
  const data = toApiRecord(await res.json());
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
      metadata: withFallback(data['metadata'], {}),
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
  const result = toApiRecord(await res.json());
  return { id: asString(result['id']), scenarioNumber: asString(result['scenario_number']) };
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
  assignDefined(body, [
    ['title', data['title']],
    ['description', data['description']],
    ['gherkin_text', data['gherkinText']],
    ['given_steps', data['givenSteps']],
    ['when_steps', data['whenSteps']],
    ['then_steps', data['thenSteps']],
    ['tags', data['tags']],
    ['requirement_ids', data['requirementIds']],
    ['metadata', data['metadata']],
  ]);

  const res = await fetch(`${API_URL}/api/v1/scenarios/${id}`, {
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update scenario');
  }
  const result = toApiRecord(await res.json());
  return { id: asString(result['id']), version: asNumber(result['version']) };
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
  const result = toApiRecord(await res.json());
  return {
    executionCount: asNumber(result['execution_count']),
    id: asString(result['id']),
    lastRunAt: asString(result['last_run_at']),
    lastRunResult: asString(result['last_run_result']),
    status: asScenarioStatus(result['status']),
  };
}

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
  const itemsData = toApiRecord(await itemsRes.json());
  const items = asRecordArray(itemsData['items'])
    .map((item) => asString(item['id']))
    .filter((itemId) => itemId.length > 0);

  // Then fetch quality for each item (only items that have quality analysis)
  const qualityPromises = items.map(async (itemId) => {
    try {
      const qualityRes = await fetch(`${API_URL}/api/v1/quality/items/${itemId}`, {
        headers: authHeaders,
      });
      if (qualityRes.ok) {
        const qualityData = toApiRecord(await qualityRes.json());
        return {
          ambiguityScore: asNumber(qualityData['ambiguity_score']),
          completenessScore: asNumber(qualityData['completeness_score']),
          createdAt: asString(qualityData['created_at']),
          id: asString(qualityData['id']),
          itemId: asString(qualityData['item_id']),
          lastAnalyzedAt: asString(qualityData['last_analyzed_at']),
          smells: withFallback(asOptionalStringArray(qualityData['smells']), []),
          suggestions: withFallback(asOptionalStringArray(qualityData['suggestions']), []),
          updatedAt: asString(qualityData['updated_at']),
          version: asNumber(qualityData['version']),
        };
      }
      // If quality doesn't exist for this item, skip it (404 is expected)
      return;
    } catch (error) {
      logger.warn(`Failed to fetch quality for item ${itemId}:`, error);
      return;
    }
  });

  const results = await Promise.all(qualityPromises);
  return results.filter((report): report is QualityReport => report !== undefined);
}

export {
  fetchADRs,
  fetchADR,
  createADR,
  updateADR,
  deleteADR,
  verifyADR,
  fetchADRActivities,
  fetchContractActivities,
  fetchFeatureActivities,
  fetchScenarioActivities,
  fetchProjectScenarios,
  fetchProjectScenarioActivities,
  fetchADRStats,
  fetchContracts,
  fetchContract,
  createContract,
  updateContract,
  deleteContract,
  verifyContract,
  fetchContractStats,
  fetchFeatures,
  fetchFeature,
  createFeature,
  updateFeature,
  deleteFeature,
  fetchFeatureStats,
  fetchScenarios,
  fetchScenario,
  createScenario,
  updateScenario,
  deleteScenario,
  runScenario,
  fetchSpecificationSummary,
  fetchQualityReports,
  type ADRFilters,
  type CreateADRData,
  type UpdateADRData,
  type ContractFilters,
  type CreateContractData,
  type UpdateContractData,
  type FeatureFilters,
  type CreateFeatureData,
  type UpdateFeatureData,
  type CreateScenarioData,
  type UpdateScenarioData,
  type QualityReport,
};
