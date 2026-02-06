import type { TestResultStatus, TestType } from './shared-types';

interface TestSpec {
  id: string;
  item_id: string;
  test_type: TestType;
  test_framework?: string;
  test_file_path?: string;
  test_function_name?: string;
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
  last_run_at?: string;
  last_run_status?: TestResultStatus;
  last_run_duration_ms?: number;
  last_run_error?: string;
  run_history: unknown[];
  flakiness_score?: number;
  flakiness_window_runs: number;
  flaky_patterns: string[];
  is_quarantined: boolean;
  quarantine_reason?: string;
  quarantined_at?: string;
  avg_duration_ms?: number;
  p50_duration_ms?: number;
  p95_duration_ms?: number;
  p99_duration_ms?: number;
  duration_trend?: string;
  performance_baseline_ms?: number;
  performance_threshold_ms?: number;
  line_coverage?: number;
  branch_coverage?: number;
  mutation_score?: number;
  mcdc_coverage?: number;
  verifies_requirements: string[];
  verifies_contracts: string[];
  assertions: string[];
  depends_on_tests: string[];
  required_services: string[];
  mocked_dependencies: string[];
  maintenance_score?: number;
  suggested_actions: string[];
  spec_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface TestSpecCreate {
  item_id: string;
  test_type: TestType;
  test_framework?: string;
  test_file_path?: string;
  test_function_name?: string;
  preconditions?: string[];
  setup_commands?: string[];
  teardown_commands?: string[];
  environment_requirements?: Record<string, unknown>;
  test_data_schema?: Record<string, unknown>;
  fixtures?: string[];
  parameterized_cases?: unknown[];
  required_services?: string[];
  mocked_dependencies?: string[];
  spec_metadata?: Record<string, unknown>;
}

interface TestSpecUpdate {
  test_framework?: string;
  test_file_path?: string;
  test_function_name?: string;
  preconditions?: string[];
  setup_commands?: string[];
  teardown_commands?: string[];
  environment_requirements?: Record<string, unknown>;
  test_data_schema?: Record<string, unknown>;
  fixtures?: string[];
  parameterized_cases?: unknown[];
  maintenance_score?: number;
  suggested_actions?: string[];
  spec_metadata?: Record<string, unknown>;
}

export type { TestSpec, TestSpecCreate, TestSpecUpdate };
