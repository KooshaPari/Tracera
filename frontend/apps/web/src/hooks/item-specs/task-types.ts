import type { TaskStatus } from './shared-types';

interface TaskSpec {
  id: string;
  item_id: string;
  task_title: string;
  description?: string;
  status: TaskStatus;
  assigned_to?: string;
  due_date?: string;
  estimated_hours?: number;
  actual_hours?: number;
  priority: number;
  parent_story?: string;
  subtasks: {
    id: string;
    title: string;
    completed: boolean;
  }[];
  dependencies: string[];
  blocking: string[];
  labels: string[];
  completion_percentage?: number;
  notes?: string;
  spec_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface TaskSpecCreate {
  item_id: string;
  task_title: string;
  description?: string;
  status: TaskStatus;
  assigned_to?: string;
  due_date?: string;
  estimated_hours?: number;
  actual_hours?: number;
  priority: number;
  parent_story?: string;
  subtasks?: {
    id: string;
    title: string;
    completed: boolean;
  }[];
  dependencies?: string[];
  completion_percentage?: number;
  notes?: string;
  spec_metadata?: Record<string, unknown>;
}

interface TaskSpecUpdate {
  task_title?: string;
  description?: string;
  status?: TaskStatus;
  assigned_to?: string;
  due_date?: string;
  estimated_hours?: number;
  actual_hours?: number;
  priority?: number;
  parent_story?: string;
  subtasks?: {
    id: string;
    title: string;
    completed: boolean;
  }[];
  dependencies?: string[];
  completion_percentage?: number;
  notes?: string;
  spec_metadata?: Record<string, unknown>;
}

export type { TaskSpec, TaskSpecCreate, TaskSpecUpdate };
