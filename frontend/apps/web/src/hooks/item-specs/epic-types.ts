import type { EpicStatus, RiskLevel } from './shared-types';

interface EpicSpec {
  id: string;
  item_id: string;
  epic_name: string;
  business_value: number;
  target_release?: string | undefined;
  status: EpicStatus;
  start_date?: string | undefined;
  end_date?: string | undefined;
  dependencies: string[];
  child_stories_count: number;
  user_stories: string[];
  objectives: string[];
  success_criteria: string[];
  stakeholders: string[];
  acceptance_criteria: Record<string, unknown>;
  scope_statement?: string | undefined;
  out_of_scope?: string[] | undefined;
  constraints: string[];
  assumptions: string[];
  risks: {
    description: string;
    mitigation: string;
    impact: RiskLevel;
  }[];
  themes: string[];
  metrics: Record<string, number>;
  spec_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface EpicSpecCreate {
  item_id: string;
  epic_name: string;
  business_value: number;
  target_release?: string | undefined;
  status: EpicStatus;
  start_date?: string | undefined;
  end_date?: string | undefined;
  dependencies?: string[] | undefined;
  objectives?: string[] | undefined;
  success_criteria?: string[] | undefined;
  stakeholders?: string[] | undefined;
  acceptance_criteria?: Record<string, unknown> | undefined;
  scope_statement?: string | undefined;
  out_of_scope?: string[] | undefined;
  constraints?: string[] | undefined;
  assumptions?: string[] | undefined;
  risks?: {
    description: string;
    mitigation: string;
    impact: RiskLevel;
  }[];
  themes?: string[] | undefined;
  metrics?: Record<string, number> | undefined;
  spec_metadata?: Record<string, unknown> | undefined;
}

interface EpicSpecUpdate {
  epic_name?: string | undefined;
  business_value?: number | undefined;
  target_release?: string | undefined;
  status?: EpicStatus | undefined;
  start_date?: string | undefined;
  end_date?: string | undefined;
  dependencies?: string[] | undefined;
  objectives?: string[] | undefined;
  success_criteria?: string[] | undefined;
  stakeholders?: string[] | undefined;
  acceptance_criteria?: Record<string, unknown> | undefined;
  scope_statement?: string | undefined;
  out_of_scope?: string[] | undefined;
  constraints?: string[] | undefined;
  assumptions?: string[] | undefined;
  risks?: {
    description: string;
    mitigation: string;
    impact: RiskLevel;
  }[];
  themes?: string[] | undefined;
  metrics?: Record<string, number> | undefined;
  spec_metadata?: Record<string, unknown> | undefined;
}

export type { EpicSpec, EpicSpecCreate, EpicSpecUpdate };
