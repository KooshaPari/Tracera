type RequirementType =
  | 'ubiquitous'
  | 'event_driven'
  | 'state_driven'
  | 'optional'
  | 'complex'
  | 'unwanted';

type ConstraintType = 'hard' | 'soft' | 'optimizable';

type VerificationStatus = 'unverified' | 'pending' | 'verified' | 'failed' | 'expired';

type RiskLevel = 'critical' | 'high' | 'medium' | 'low' | 'minimal';

type TestType =
  | 'unit'
  | 'integration'
  | 'e2e'
  | 'performance'
  | 'security'
  | 'accessibility'
  | 'contract'
  | 'mutation'
  | 'fuzz'
  | 'property';

type TestResultStatus = 'passed' | 'failed' | 'skipped' | 'blocked' | 'flaky' | 'timeout' | 'error';

type EpicStatus = 'backlog' | 'in_progress' | 'completed' | 'archived';

type UserStoryStatus = 'backlog' | 'ready' | 'in_progress' | 'review' | 'done' | 'archived';

type TaskStatus = 'todo' | 'in_progress' | 'review' | 'done' | 'blocked';

type DefectSeverity = 'critical' | 'major' | 'minor' | 'trivial';

type DefectStatus =
  | 'new'
  | 'assigned'
  | 'in_progress'
  | 'resolved'
  | 'verified'
  | 'closed'
  | 'reopened';

interface QualityIssue {
  dimension: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
  suggestion?: string | undefined;
}

export type {
  RequirementType,
  ConstraintType,
  VerificationStatus,
  RiskLevel,
  TestType,
  TestResultStatus,
  EpicStatus,
  UserStoryStatus,
  TaskStatus,
  DefectSeverity,
  DefectStatus,
  QualityIssue,
};
