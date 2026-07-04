import type { DefectSeverity, DefectStatus } from './shared-types';

interface DefectSpec {
  id: string;
  item_id: string;
  title: string;
  description: string;
  severity: DefectSeverity;
  status: DefectStatus;
  discovered_by?: string | undefined;
  assigned_to?: string | undefined;
  discovered_at?: string | undefined;
  resolved_at?: string | undefined;
  resolution?: string | undefined;
  steps_to_reproduce: string[];
  expected_behavior: string;
  actual_behavior: string;
  affected_components: string[];
  affected_versions?: string[] | undefined;
  regression_risk?: 'low' | 'medium' | 'high' | 'critical' | undefined;
  reproducible?: boolean | undefined;
  environment?: string | undefined;
  root_cause?: string | undefined;
  verification_notes?: string | undefined;
  attachments?: { type: string; url: string; description?: string }[] | undefined;
  related_requirements?: string[] | undefined;
  related_defects?: string[] | undefined;
  time_to_fix_estimate?: string | undefined;
  reported_by?: string | undefined;
  tags: string[];
  regressions: string[];
  spec_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface DefectSpecCreate {
  item_id: string;
  title: string;
  description: string;
  severity: DefectSeverity;
  status: DefectStatus;
  discovered_by?: string | undefined;
  assigned_to?: string | undefined;
  discovered_at?: string | undefined;
  resolved_at?: string | undefined;
  resolution?: string | undefined;
  steps_to_reproduce?: string[] | undefined;
  expected_behavior: string;
  actual_behavior: string;
  affected_components?: string[] | undefined;
  tags?: string[] | undefined;
  regressions?: string[] | undefined;
  spec_metadata?: Record<string, unknown> | undefined;
}

interface DefectSpecUpdate {
  title?: string | undefined;
  description?: string | undefined;
  severity?: DefectSeverity | undefined;
  status?: DefectStatus | undefined;
  discovered_by?: string | undefined;
  assigned_to?: string | undefined;
  discovered_at?: string | undefined;
  resolved_at?: string | undefined;
  resolution?: string | undefined;
  steps_to_reproduce?: string[] | undefined;
  expected_behavior?: string | undefined;
  actual_behavior?: string | undefined;
  affected_components?: string[] | undefined;
  tags?: string[] | undefined;
  regressions?: string[] | undefined;
  spec_metadata?: Record<string, unknown> | undefined;
}

export type { DefectSpec, DefectSpecCreate, DefectSpecUpdate };
