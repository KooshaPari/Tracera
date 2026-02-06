import type { UserStoryStatus } from './shared-types';

interface UserStorySpec {
  id: string;
  item_id: string;
  story_points?: number;
  status: UserStoryStatus;
  as_a: string;
  i_want: string;
  so_that: string;
  acceptance_criteria: {
    criterion: string;
    completed: boolean;
    verified_at?: string;
  }[];
  definition_of_done: string[];
  edge_cases: string[];
  dependencies: string[];
  related_tasks: string[];
  parent_epic?: string;
  priority: number;
  estimation_confidence?: number;
  test_scenarios: string[];
  ui_mockups?: string[];
  api_specs?: string[];
  database_changes?: Record<string, unknown>;
  spec_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface UserStorySpecCreate {
  item_id: string;
  story_points?: number;
  status: UserStoryStatus;
  as_a: string;
  i_want: string;
  so_that: string;
  acceptance_criteria?: {
    criterion: string;
    completed: boolean;
  }[];
  definition_of_done?: string[];
  edge_cases?: string[];
  dependencies?: string[];
  related_tasks?: string[];
  parent_epic?: string;
  priority: number;
  estimation_confidence?: number;
  test_scenarios?: string[];
  ui_mockups?: string[];
  api_specs?: string[];
  database_changes?: Record<string, unknown>;
  spec_metadata?: Record<string, unknown>;
}

interface UserStorySpecUpdate {
  story_points?: number;
  status?: UserStoryStatus;
  as_a?: string;
  i_want?: string;
  so_that?: string;
  acceptance_criteria?: {
    criterion: string;
    completed: boolean;
    verified_at?: string;
  }[];
  definition_of_done?: string[];
  edge_cases?: string[];
  dependencies?: string[];
  related_tasks?: string[];
  parent_epic?: string;
  priority?: number;
  estimation_confidence?: number;
  test_scenarios?: string[];
  ui_mockups?: string[];
  api_specs?: string[];
  database_changes?: Record<string, unknown>;
  spec_metadata?: Record<string, unknown>;
}

export type { UserStorySpec, UserStorySpecCreate, UserStorySpecUpdate };
