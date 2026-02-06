import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type {
  TestSuite,
  TestSuiteActivity,
  TestSuiteStats,
  TestSuiteStatus,
  TestSuiteTestCase,
} from '@tracertm/types';

import { client } from '@/api/client';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

// Transform API response (snake_case) to frontend format (camelCase)
function transformTestSuite(data: Record<string, unknown>): TestSuite {
  const payload = data as Record<string, any>;
  return {
    automatedCount: payload['automated_count'],
    category: payload['category'],
    createdAt: payload['created_at'],
    description: payload['description'],
    environmentVariables: payload['environment_variables'],
    estimatedDurationMinutes: payload['estimated_duration_minutes'],
    id: payload['id'],
    isParallelExecution: payload['is_parallel_execution'],
    lastRunAt: payload['last_run_at'],
    lastRunStatus: payload['last_run_status'],
    manualCount: payload['manual_count'],
    metadata: payload['suite_metadata'],
    name: payload['name'],
    objective: payload['objective'],
    orderIndex: payload['order_index'],
    owner: payload['owner'],
    parentId: payload['parent_id'],
    passRate: payload['pass_rate'],
    projectId: payload['project_id'],
    requiredEnvironment: payload['required_environment'],
    responsibleTeam: payload['responsible_team'],
    setupInstructions: payload['setup_instructions'],
    status: payload['status'],
    suiteNumber: payload['suite_number'],
    tags: payload['tags'],
    teardownInstructions: payload['teardown_instructions'],
    totalTestCases: payload['total_test_cases'],
    updatedAt: payload['updated_at'],
    version: payload['version'],
  };
}

function transformTestSuiteTestCase(data: Record<string, unknown>): TestSuiteTestCase {
  const payload = data as Record<string, any>;
  return {
    createdAt: payload['created_at'],
    customParameters: payload['custom_parameters'],
    id: payload['id'],
    isMandatory: payload['is_mandatory'],
    orderIndex: payload['order_index'],
    skipReason: payload['skip_reason'],
    suiteId: payload['suite_id'],
    testCaseId: payload['test_case_id'],
  };
}

interface TestSuiteFilters {
  projectId: string;
  status?: TestSuiteStatus;
  category?: string;
  parentId?: string;
  owner?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

async function fetchTestSuites(
  filters: TestSuiteFilters,
): Promise<{ testSuites: TestSuite[]; total: number }> {
  const params = new URLSearchParams();
  params.set('project_id', filters.projectId);
  if (filters.status) {
    params.set('status', filters.status);
  }
  if (filters.category) {
    params.set('category', filters.category);
  }
  if (filters.parentId !== undefined) {
    params.set('parent_id', filters.parentId);
  }
  if (filters.owner) {
    params.set('owner', filters.owner);
  }
  if (filters.search) {
    params.set('search', filters.search);
  }
  if (filters.skip !== undefined) {
    params.set('skip', String(filters.skip));
  }
  if (filters.limit !== undefined) {
    params.set('limit', String(filters.limit));
  }

  const res = await fetch(`${API_URL}/api/v1/test-suites?${params}`, {
    headers: {
      'X-Bulk-Operation': 'true',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch test suites: ${res.status} ${errorText}`);
  }
  const data = await res.json();
  return {
    testSuites: (data['test_suites'] || []).map(transformTestSuite),
    total: data['total'] || 0,
  };
}

async function fetchTestSuite(id: string): Promise<TestSuite> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch test suite');
  }
  const data = await res.json();
  return transformTestSuite(data);
}

interface CreateTestSuiteData {
  projectId: string;
  name: string;
  description?: string;
  objective?: string;
  parentId?: string;
  orderIndex?: number;
  category?: string;
  tags?: string[];
  isParallelExecution?: boolean;
  estimatedDurationMinutes?: number;
  requiredEnvironment?: string;
  environmentVariables?: Record<string, string>;
  setupInstructions?: string;
  teardownInstructions?: string;
  owner?: string;
  responsibleTeam?: string;
  metadata?: Record<string, unknown>;
}

async function createTestSuite(
  data: CreateTestSuiteData,
): Promise<{ id: string; suiteNumber: string }> {
  const res = await fetch(`${API_URL}/api/v1/test-suites?project_id=${data['projectId']}`, {
    body: JSON.stringify({
      category: data['category'],
      description: data['description'],
      environment_variables: data['environmentVariables'],
      estimated_duration_minutes: data['estimatedDurationMinutes'],
      is_parallel_execution: data['isParallelExecution'] || false,
      metadata: data['metadata'] || {},
      name: data.name,
      objective: data['objective'],
      order_index: data['orderIndex'] || 0,
      owner: data['owner'],
      parent_id: data['parentId'],
      required_environment: data['requiredEnvironment'],
      responsible_team: data['responsibleTeam'],
      setup_instructions: data['setupInstructions'],
      tags: data['tags'],
      teardown_instructions: data['teardownInstructions'],
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create test suite');
  }
  const result = await res.json();
  return { id: result['id'], suiteNumber: result['suite_number'] };
}

async function updateTestSuite(
  id: string,
  data: Partial<CreateTestSuiteData>,
): Promise<{ id: string; version: number }> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${id}`, {
    body: JSON.stringify({
      category: data['category'],
      description: data['description'],
      environment_variables: data['environmentVariables'],
      estimated_duration_minutes: data['estimatedDurationMinutes'],
      is_parallel_execution: data['isParallelExecution'],
      metadata: data['metadata'],
      name: data.name,
      objective: data['objective'],
      order_index: data['orderIndex'],
      owner: data['owner'],
      parent_id: data['parentId'],
      required_environment: data['requiredEnvironment'],
      responsible_team: data['responsibleTeam'],
      setup_instructions: data['setupInstructions'],
      tags: data['tags'],
      teardown_instructions: data['teardownInstructions'],
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PUT',
  });
  if (!res.ok) {
    throw new Error('Failed to update test suite');
  }
  return res.json();
}

async function transitionTestSuiteStatus(
  id: string,
  newStatus: TestSuiteStatus,
  reason?: string,
): Promise<{ id: string; status: string; version: number }> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${id}/status`, {
    body: JSON.stringify({
      new_status: newStatus,
      reason,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to transition status: ${errorText}`);
  }
  return res.json();
}

async function deleteTestSuite(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${id}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete test suite');
  }
}

// Test case management within suites
async function addTestCaseToSuite(
  suiteId: string,
  testCaseId: string,
  orderIndex?: number,
  isMandatory?: boolean,
  skipReason?: string,
  customParameters?: Record<string, unknown>,
): Promise<TestSuiteTestCase> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${suiteId}/test-cases`, {
    body: JSON.stringify({
      custom_parameters: customParameters,
      is_mandatory: isMandatory !== false,
      order_index: orderIndex || 0,
      skip_reason: skipReason,
      test_case_id: testCaseId,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to add test case to suite');
  }
  const data = await res.json();
  return transformTestSuiteTestCase(data);
}

async function removeTestCaseFromSuite(suiteId: string, testCaseId: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${suiteId}/test-cases/${testCaseId}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to remove test case from suite');
  }
}

async function fetchSuiteTestCases(suiteId: string): Promise<TestSuiteTestCase[]> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${suiteId}/test-cases`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch suite test cases');
  }
  const data = await res.json();
  return (data['test_cases'] || []).map(transformTestSuiteTestCase);
}

async function reorderSuiteTestCases(suiteId: string, testCaseIds: string[]): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${suiteId}/test-cases/reorder`, {
    body: JSON.stringify({
      ordered_test_case_ids: testCaseIds,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to reorder test cases');
  }
}

async function fetchTestSuiteActivities(
  suiteId: string,
  limit = 50,
): Promise<{ suiteId: string; activities: TestSuiteActivity[] }> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${suiteId}/activities?limit=${limit}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch activities');
  }
  const data = await res.json();
  return {
    activities: (data['activities'] || []).map((a: Record<string, any>) => ({
      activityType: a['activity_type'],
      createdAt: a['created_at'],
      description: a['description'],
      fromValue: a['from_value'],
      id: a['id'],
      metadata: a['activity_metadata'],
      performedBy: a['performed_by'],
      suiteId: a['suite_id'],
      toValue: a['to_value'],
    })),
    suiteId: data['suite_id'],
  };
}

async function fetchTestSuiteStats(projectId: string): Promise<TestSuiteStats> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/test-suites/stats`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch test suite stats');
  }
  const data = await res.json();
  return {
    automatedTestCases: data['automated_test_cases'] || 0,
    byCategory: data['by_category'] || {},
    byStatus: data['by_status'] || {},
    projectId: data['project_id'],
    total: data['total'] || 0,
    totalTestCases: data['total_test_cases'] || 0,
  };
}

// React Query hooks

export function useTestSuites(filters: TestSuiteFilters) {
  return useQuery({
    enabled: Boolean(filters.projectId),
    queryFn: () => fetchTestSuites(filters),
    queryKey: ['testSuites', JSON.stringify(filters)],
  });
}

export function useTestSuite(id: string) {
  return useQuery({
    enabled: Boolean(id),
    queryFn: () => fetchTestSuite(id),
    queryKey: ['testSuites', id],
  });
}

export function useCreateTestSuite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createTestSuite,
    onSuccess: (_, variables) => {
      void queryClient.invalidateQueries({ queryKey: ['testSuites'] });
      return queryClient.invalidateQueries({
        queryKey: ['testSuiteStats', variables.projectId],
      });
    },
  });
}

export function useUpdateTestSuite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateTestSuiteData> }) =>
      updateTestSuite(id, data),
    onSuccess: (_, { id }) => {
      void queryClient.invalidateQueries({ queryKey: ['testSuites', id] });
      return queryClient.invalidateQueries({ queryKey: ['testSuites'] });
    },
  });
}

export function useTransitionTestSuiteStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      newStatus,
      reason,
    }: {
      id: string;
      newStatus: TestSuiteStatus;
      reason?: string;
    }) => transitionTestSuiteStatus(id, newStatus, reason),
    onSuccess: (_, { id }) => {
      void queryClient.invalidateQueries({ queryKey: ['testSuites', id] });
      void queryClient.invalidateQueries({ queryKey: ['testSuites'] });
      return queryClient.invalidateQueries({ queryKey: ['testSuiteStats'] });
    },
  });
}

export function useDeleteTestSuite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteTestSuite,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['testSuites'] });
      return queryClient.invalidateQueries({ queryKey: ['testSuiteStats'] });
    },
  });
}

export function useAddTestCaseToSuite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      suiteId,
      testCaseId,
      orderIndex,
      isMandatory,
      skipReason,
      customParameters,
    }: {
      suiteId: string;
      testCaseId: string;
      orderIndex?: number;
      isMandatory?: boolean;
      skipReason?: string;
      customParameters?: Record<string, unknown>;
    }) =>
      addTestCaseToSuite(
        suiteId,
        testCaseId,
        orderIndex,
        isMandatory,
        skipReason,
        customParameters,
      ),
    onSuccess: (_, { suiteId }) => {
      queryClient.invalidateQueries({ queryKey: ['suiteTestCases', suiteId] });
      queryClient.invalidateQueries({ queryKey: ['testSuites', suiteId] });
    },
  });
}

export function useRemoveTestCaseFromSuite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ suiteId, testCaseId }: { suiteId: string; testCaseId: string }) =>
      removeTestCaseFromSuite(suiteId, testCaseId),
    onSuccess: (_, { suiteId }) => {
      queryClient.invalidateQueries({ queryKey: ['suiteTestCases', suiteId] });
      queryClient.invalidateQueries({ queryKey: ['testSuites', suiteId] });
    },
  });
}

export function useSuiteTestCases(suiteId: string) {
  return useQuery({
    enabled: Boolean(suiteId),
    queryFn: () => fetchSuiteTestCases(suiteId),
    queryKey: ['suiteTestCases', suiteId],
  });
}

export function useReorderSuiteTestCases() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ suiteId, testCaseIds }: { suiteId: string; testCaseIds: string[] }) =>
      reorderSuiteTestCases(suiteId, testCaseIds),
    onSuccess: (_, { suiteId }) => {
      queryClient.invalidateQueries({ queryKey: ['suiteTestCases', suiteId] });
    },
  });
}

export function useTestSuiteActivities(suiteId: string, limit = 50) {
  return useQuery({
    enabled: Boolean(suiteId),
    queryFn: () => fetchTestSuiteActivities(suiteId, limit),
    queryKey: ['testSuiteActivities', suiteId, limit],
  });
}

export function useTestSuiteStats(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: () => fetchTestSuiteStats(projectId),
    queryKey: ['testSuiteStats', projectId],
  });
}
