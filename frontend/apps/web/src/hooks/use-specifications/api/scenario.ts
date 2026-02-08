import type { Scenario, ScenarioActivity, ScenarioStatus, ScenarioStep } from '@tracertm/types';

import { API_URL, assignDefined, getAuthHeaders, setOptionalParam, setOptionalStringParam, withFallback } from './base';
import {
  asBoolean,
  asExamples,
  asNumber,
  asOptionalNumber,
  asOptionalScenarioSteps,
  asOptionalString,
  asOptionalStringArray,
  asRecord,
  asRecordArray,
  asRunResult,
  asScenarioStatus,
  asScenarioSteps,
  asString,
  toApiRecord,
} from './decoders';

// =============================================================================
// Transform
// =============================================================================

function transformScenario(data: Record<string, unknown>): Scenario {
  return {
    background: asOptionalScenarioSteps(data['background']),
    createdAt: asString(data['created_at']),
    description: asOptionalString(data['description']),
    examples: asExamples(data['examples']),
    executionCount: asNumber(data['execution_count']),
    featureId: asString(data['feature_id']),
    gherkinText: asString(data['gherkin_text']),
    givenSteps: asScenarioSteps(data['given_steps']),
    id: asString(data['id']),
    isOutline: asBoolean(data['is_outline']),
    lastRunAt: asOptionalString(data['last_run_at']),
    lastRunDurationMs: asOptionalNumber(data['last_run_duration_ms']),
    lastRunResult: asRunResult(data['last_run_result']),
    metadata: asRecord(data['metadata']),
    passRate: asNumber(data['pass_rate']),
    requirementIds: asOptionalStringArray(data['requirement_ids']),
    scenarioNumber: asString(data['scenario_number']),
    status: asScenarioStatus(data['status']),
    tags: asOptionalStringArray(data['tags']),
    testCaseIds: asOptionalStringArray(data['test_case_ids']),
    thenSteps: asScenarioSteps(data['then_steps']),
    title: asString(data['title']),
    updatedAt: asString(data['updated_at']),
    version: asNumber(data['version']),
    whenSteps: asScenarioSteps(data['when_steps']),
  };
}

// =============================================================================
// API - Scenarios
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
    scenarios: asRecordArray(data['scenarios']).map((entry) => transformScenario(entry)),
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
    scenarios: asRecordArray(data['scenarios']).map((entry) => transformScenario(entry)),
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

export {
  createScenario,
  deleteScenario,
  fetchProjectScenarioActivities,
  fetchProjectScenarios,
  fetchScenario,
  fetchScenarioActivities,
  fetchScenarios,
  runScenario,
  updateScenario,
  type CreateScenarioData,
  type UpdateScenarioData,
};

