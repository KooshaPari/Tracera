import type { UserStoryStatus } from './shared-types';

interface UserStorySpec {
  id: string;
  item_id: string;
  story_points?: number | undefined;
  status: UserStoryStatus;
  as_a: string;
  i_want: string;
  so_that: string;
  acceptance_criteria: {
    criterion: string;
    completed: boolean;
    verified_at?: string | undefined;
  }[];
  definition_of_done: string[];
  edge_cases: string[];
  dependencies: string[];
  related_tasks: string[];
  parent_epic?: string | undefined;
  priority: number;
  estimation_confidence?: number | undefined;
  test_scenarios: string[];
  ui_mockups?: string[] | undefined;
  api_specs?: string[] | undefined;
  database_changes?: Record<string, unknown> | undefined;
  spec_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface UserStorySpecCreate {
  item_id: string;
  story_points?: number | undefined;
  status: UserStoryStatus;
  as_a: string;
  i_want: string;
  so_that: string;
  acceptance_criteria?: {
    criterion: string;
    completed: boolean;
  }[];
  definition_of_done?: string[] | undefined;
  edge_cases?: string[] | undefined;
  dependencies?: string[] | undefined;
  related_tasks?: string[] | undefined;
  parent_epic?: string | undefined;
  priority: number;
  estimation_confidence?: number | undefined;
  test_scenarios?: string[] | undefined;
  ui_mockups?: string[] | undefined;
  api_specs?: string[] | undefined;
  database_changes?: Record<string, unknown> | undefined;
  spec_metadata?: Record<string, unknown> | undefined;
}

interface UserStorySpecUpdate {
  story_points?: number | undefined;
  status?: UserStoryStatus | undefined;
  as_a?: string | undefined;
  i_want?: string | undefined;
  so_that?: string | undefined;
  acceptance_criteria?: {
    criterion: string;
    completed: boolean;
    verified_at?: string | undefined;
  }[];
  definition_of_done?: string[] | undefined;
  edge_cases?: string[] | undefined;
  dependencies?: string[] | undefined;
  related_tasks?: string[] | undefined;
  parent_epic?: string | undefined;
  priority?: number | undefined;
  estimation_confidence?: number | undefined;
  test_scenarios?: string[] | undefined;
  ui_mockups?: string[] | undefined;
  api_specs?: string[] | undefined;
  database_changes?: Record<string, unknown> | undefined;
  spec_metadata?: Record<string, unknown> | undefined;
}

export type { UserStorySpec, UserStorySpecCreate, UserStorySpecUpdate };
