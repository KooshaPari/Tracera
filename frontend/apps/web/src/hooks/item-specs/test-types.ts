import type { TestResultStatus, TestType } from './shared-types';

interface TestSpec {
  id: string;
  item_id: string;
  test_type: TestType;
  test_framework?: string | undefined;
  test_file_path?: string | undefined;
  test_function_name?: string | undefined;
  preconditions: string[];
  setup_commands: string[];
  teardown_commands: string[];
  environment_requirements: Record<string, unknown>;
  test_data_schema: Record<string, unknown>;
  fixtures: string[];
  parameterized_cases: unknown[];
  total_runs: number;
  pass_count: number;
  fail_count: number;
  skip_count: number;
  last_run_at?: string | undefined;
  last_run_status?: TestResultStatus | undefined;
  last_run_duration_ms?: number | undefined;
  last_run_error?: string | undefined;
  run_history: unknown[];
  flakiness_score?: number | undefined;
  flakiness_window_runs: number;
  flaky_patterns: string[];
  is_quarantined: boolean;
  quarantine_reason?: string | undefined;
  quarantined_at?: string | undefined;
  avg_duration_ms?: number | undefined;
  p50_duration_ms?: number | undefined;
  p95_duration_ms?: number | undefined;
  p99_duration_ms?: number | undefined;
  duration_trend?: string | undefined;
  performance_baseline_ms?: number | undefined;
  performance_threshold_ms?: number | undefined;
  line_coverage?: number | undefined;
  branch_coverage?: number | undefined;
  mutation_score?: number | undefined;
  mcdc_coverage?: number | undefined;
  verifies_requirements: string[];
  verifies_contracts: string[];
  assertions: string[];
  depends_on_tests: string[];
  required_services: string[];
  mocked_dependencies: string[];
  maintenance_score?: number | undefined;
  suggested_actions: string[];
  spec_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface TestSpecCreate {
  item_id: string;
  test_type: TestType;
  test_framework?: string | undefined;
  test_file_path?: string | undefined;
  test_function_name?: string | undefined;
  preconditions?: string[] | undefined;
  setup_commands?: string[] | undefined;
  teardown_commands?: string[] | undefined;
  environment_requirements?: Record<string, unknown> | undefined;
  test_data_schema?: Record<string, unknown> | undefined;
  fixtures?: string[] | undefined;
  parameterized_cases?: unknown[] | undefined;
  required_services?: string[] | undefined;
  mocked_dependencies?: string[] | undefined;
  spec_metadata?: Record<string, unknown> | undefined;
}

interface TestSpecUpdate {
  test_framework?: string | undefined;
  test_file_path?: string | undefined;
  test_function_name?: string | undefined;
  preconditions?: string[] | undefined;
  setup_commands?: string[] | undefined;
  teardown_commands?: string[] | undefined;
  environment_requirements?: Record<string, unknown> | undefined;
  test_data_schema?: Record<string, unknown> | undefined;
  fixtures?: string[] | undefined;
  parameterized_cases?: unknown[] | undefined;
  maintenance_score?: number | undefined;
  suggested_actions?: string[] | undefined;
  spec_metadata?: Record<string, unknown> | undefined;
}

export type { TestSpec, TestSpecCreate, TestSpecUpdate };
