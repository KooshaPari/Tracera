import type { TaskStatus } from './shared-types';

interface TaskSpec {
  id: string;
  item_id: string;
  task_title: string;
  description?: string | undefined;
  status: TaskStatus;
  assigned_to?: string | undefined;
  due_date?: string | undefined;
  estimated_hours?: number | undefined;
  actual_hours?: number | undefined;
  priority: number;
  parent_story?: string | undefined;
  subtasks: {
    id: string;
    title: string;
    completed: boolean;
  }[];
  dependencies: string[];
  blocking: string[];
  labels: string[];
  completion_percentage?: number | undefined;
  notes?: string | undefined;
  spec_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface TaskSpecCreate {
  item_id: string;
  task_title: string;
  description?: string | undefined;
  status: TaskStatus;
  assigned_to?: string | undefined;
  due_date?: string | undefined;
  estimated_hours?: number | undefined;
  actual_hours?: number | undefined;
  priority: number;
  parent_story?: string | undefined;
  subtasks?: {
    id: string;
    title: string;
    completed: boolean;
  }[];
  dependencies?: string[] | undefined;
  completion_percentage?: number | undefined;
  notes?: string | undefined;
  spec_metadata?: Record<string, unknown> | undefined;
}

interface TaskSpecUpdate {
  task_title?: string | undefined;
  description?: string | undefined;
  status?: TaskStatus | undefined;
  assigned_to?: string | undefined;
  due_date?: string | undefined;
  estimated_hours?: number | undefined;
  actual_hours?: number | undefined;
  priority?: number | undefined;
  parent_story?: string | undefined;
  subtasks?: {
    id: string;
    title: string;
    completed: boolean;
  }[];
  dependencies?: string[] | undefined;
  completion_percentage?: number | undefined;
  notes?: string | undefined;
  spec_metadata?: Record<string, unknown> | undefined;
}

export type { TaskSpec, TaskSpecCreate, TaskSpecUpdate };
