import type * as Types from '@tracertm/types';

import * as base from './base';
import * as decoders from './decoders';

// =============================================================================
// Transform
// =============================================================================

function transformScenario(data: Record<string, unknown>): Types.Scenario {
  return {
    background: decoders.asOptionalScenarioSteps(data['background']),
    createdAt: decoders.asString(data['created_at']),
    description: decoders.asOptionalString(data['description']),
    examples: decoders.asExamples(data['examples']),
    executionCount: decoders.asNumber(data['execution_count']),
    featureId: decoders.asString(data['feature_id']),
    gherkinText: decoders.asString(data['gherkin_text']),
    givenSteps: decoders.asScenarioSteps(data['given_steps']),
    id: decoders.asString(data['id']),
    isOutline: decoders.asBoolean(data['is_outline']),
    lastRunAt: decoders.asOptionalString(data['last_run_at']),
    lastRunDurationMs: decoders.asOptionalNumber(data['last_run_duration_ms']),
    lastRunResult: decoders.asRunResult(data['last_run_result']),
    metadata: decoders.asRecord(data['metadata']),
    passRate: decoders.asNumber(data['pass_rate']),
    requirementIds: decoders.asOptionalStringArray(data['requirement_ids']),
    scenarioNumber: decoders.asString(data['scenario_number']),
    status: decoders.asScenarioStatus(data['status']),
    tags: decoders.asOptionalStringArray(data['tags']),
    testCaseIds: decoders.asOptionalStringArray(data['test_case_ids']),
    thenSteps: decoders.asScenarioSteps(data['then_steps']),
    title: decoders.asString(data['title']),
    updatedAt: decoders.asString(data['updated_at']),
    version: decoders.asNumber(data['version']),
    whenSteps: decoders.asScenarioSteps(data['when_steps']),
  };
}

// =============================================================================
// API - Scenarios
// =============================================================================

async function fetchScenarios(
  featureId: string,
): Promise<{ scenarios: Types.Scenario[]; total: number }> {
  const params = new URLSearchParams();
  params.set('feature_id', featureId);

  const res = await fetch(`${base.API_URL}/api/v1/scenarios?${params}`, {
    headers: { 'X-Bulk-Operation': 'true', ...base.getAuthHeaders() },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch scenarios: ${res.status} ${errorText}`);
  }
  const data = decoders.toApiRecord(await res.json());
  return {
    scenarios: decoders.asRecordArray(data['scenarios']).map((entry) => transformScenario(entry)),
    total: decoders.asNumber(data['total']),
  };
}

async function fetchScenario(id: string): Promise<Types.Scenario> {
  const res = await fetch(`${base.API_URL}/api/v1/scenarios/${id}`, {
    headers: base.getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch scenario');
  }
  const data = decoders.toApiRecord(await res.json());
  return transformScenario(data);
}

interface CreateScenarioData {
  featureId: string;
  title: string;
  description?: string | undefined;
  gherkinText: string;
  givenSteps: Types.ScenarioStep[];
  whenSteps: Types.ScenarioStep[];
  thenSteps: Types.ScenarioStep[];
  tags?: string[] | undefined;
  requirementIds?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;
}

async function createScenario(
  data: CreateScenarioData,
): Promise<{ id: string; scenarioNumber: string }> {
  const res = await fetch(`${base.API_URL}/api/v1/scenarios`, {
    body: JSON.stringify({
      description: data['description'],
      feature_id: data['featureId'],
      gherkin_text: data['gherkinText'],
      given_steps: data['givenSteps'],
      metadata: base.withFallback(data['metadata'], {}),
      requirement_ids: data['requirementIds'],
      tags: data['tags'],
      then_steps: data['thenSteps'],
      title: data['title'],
      when_steps: data['whenSteps'],
    }),
    headers: { 'Content-Type': 'application/json', ...base.getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create scenario');
  }
  const result = decoders.toApiRecord(await res.json());
  return {
    id: decoders.asString(result['id']),
    scenarioNumber: decoders.asString(result['scenario_number']),
  };
}

interface UpdateScenarioData {
  title?: string | undefined;
  description?: string | undefined;
  gherkinText?: string | undefined;
  givenSteps?: Types.ScenarioStep[] | undefined;
  whenSteps?: Types.ScenarioStep[] | undefined;
  thenSteps?: Types.ScenarioStep[] | undefined;
  tags?: string[] | undefined;
  requirementIds?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;
}

async function updateScenario(
  id: string,
  data: UpdateScenarioData,
): Promise<{ id: string; version: number }> {
  const body: Record<string, unknown> = {};
  base.assignDefined(body, [
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

  const res = await fetch(`${base.API_URL}/api/v1/scenarios/${id}`, {
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json', ...base.getAuthHeaders() },
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update scenario');
  }
  const result = decoders.toApiRecord(await res.json());
  return {
    id: decoders.asString(result['id']),
    version: decoders.asNumber(result['version']),
  };
}

async function deleteScenario(id: string): Promise<void> {
  const res = await fetch(`${base.API_URL}/api/v1/scenarios/${id}`, {
    headers: base.getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete scenario');
  }
}

async function runScenario(id: string): Promise<{
  id: string;
  status: Types.ScenarioStatus;
  lastRunAt: string;
  lastRunResult: string;
  executionCount: number;
}> {
  const res = await fetch(`${base.API_URL}/api/v1/scenarios/${id}/run`, {
    body: JSON.stringify({}),
    headers: { 'Content-Type': 'application/json', ...base.getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to run scenario');
  }
  const result = decoders.toApiRecord(await res.json());
  return {
    executionCount: decoders.asNumber(result['execution_count']),
    id: decoders.asString(result['id']),
    lastRunAt: decoders.asString(result['last_run_at']),
    lastRunResult: decoders.asString(result['last_run_result']),
    status: decoders.asScenarioStatus(result['status']),
  };
}

async function fetchScenarioActivities(
  scenarioId: string,
  options: { limit?: number; offset?: number } = {},
): Promise<{ activities: Types.ScenarioActivity[]; total: number }> {
  const params = new URLSearchParams();
  base.setOptionalParam(params, 'limit', options.limit);
  base.setOptionalParam(params, 'offset', options.offset);
  const res = await fetch(
    `${base.API_URL}/api/v1/specifications/scenarios/${scenarioId}/activities?${params}`,
    { headers: base.getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch scenario activities');
  }
  const data = decoders.toApiRecord(await res.json());
  const activities = decoders.asRecordArray(data['activities']);
  return {
    activities: activities.map((activity) => ({
      activityType: decoders.asString(activity['activity_type']),
      createdAt: decoders.asString(activity['created_at']),
      description: decoders.asOptionalString(activity['description']),
      fromValue: decoders.asOptionalString(activity['from_value']),
      id: decoders.asString(activity['id']),
      performedBy: decoders.asOptionalString(activity['performed_by']),
      scenarioId: decoders.asString(activity['scenario_id']),
      toValue: decoders.asOptionalString(activity['to_value']),
    })),
    total: decoders.asNumber(data['total']),
  };
}

async function fetchProjectScenarios(
  projectId: string,
  status?: string,
): Promise<{ scenarios: Types.Scenario[]; total: number }> {
  const params = new URLSearchParams();
  if (status !== undefined && status.length > 0) {
    params.set('status', status);
  }
  const res = await fetch(
    `${base.API_URL}/api/v1/specifications/projects/${projectId}/scenarios?${params}`,
    { headers: base.getAuthHeaders() },
  );
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch scenarios: ${res.status} ${errorText}`);
  }
  const data = decoders.toApiRecord(await res.json());
  return {
    scenarios: decoders.asRecordArray(data['scenarios']).map((entry) => transformScenario(entry)),
    total: decoders.asNumber(data['total']),
  };
}

async function fetchProjectScenarioActivities(
  projectId: string,
  options: {
    limit?: number | undefined;
    offset?: number | undefined;
    eventType?: string | undefined;
    since?: string | undefined;
    until?: string | undefined;
  } = {},
): Promise<Types.ScenarioActivity[]> {
  const params = new URLSearchParams();
  base.setOptionalParam(params, 'limit', options.limit);
  base.setOptionalParam(params, 'offset', options.offset);
  base.setOptionalStringParam(params, 'event_type', options.eventType);
  base.setOptionalStringParam(params, 'since', options.since);
  base.setOptionalStringParam(params, 'until', options.until);
  const res = await fetch(
    `${base.API_URL}/api/v1/specifications/projects/${projectId}/scenarios/activities?${params}`,
    { headers: base.getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch scenario activities');
  }
  const data = decoders.toApiRecord(await res.json());
  const activities = decoders.asRecordArray(data['activities']);
  return activities.map((activity) => ({
    activityType: decoders.asString(activity['activity_type']),
    createdAt: decoders.asString(activity['created_at']),
    description: decoders.asOptionalString(activity['description']),
    fromValue: decoders.asOptionalString(activity['from_value']),
    id: decoders.asString(activity['id']),
    performedBy: decoders.asOptionalString(activity['performed_by']),
    scenarioId: decoders.asString(activity['scenario_id']),
    toValue: decoders.asOptionalString(activity['to_value']),
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
