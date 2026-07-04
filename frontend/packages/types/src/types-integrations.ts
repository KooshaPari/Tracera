// Webhook Integration Types
export type WebhookProvider =
  | 'github_actions'
  | 'gitlab_ci'
  | 'jenkins'
  | 'azure_devops'
  | 'circleci'
  | 'travis_ci'
  | 'custom';

export type WebhookStatus = 'active' | 'paused' | 'disabled';

export interface WebhookIntegration {
  id: string;
  projectId: string;
  name: string;
  description?: string | undefined;
  provider: WebhookProvider;
  status: WebhookStatus;
  webhookSecret: string;
  apiKey?: string | undefined;
  enabledEvents?: string[] | undefined;
  eventFilters?: Record<string, unknown> | undefined;
  callbackUrl?: string | undefined;
  callbackHeaders?: Record<string, string> | undefined;
  defaultSuiteId?: string | undefined;
  rateLimitPerMinute: number;
  autoCreateRun: boolean;
  autoCompleteRun: boolean;
  verifySignatures: boolean;
  // Statistics
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  lastRequestAt?: string | undefined;
  lastSuccessAt?: string | undefined;
  lastFailureAt?: string | undefined;
  lastErrorMessage?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface WebhookLog {
  id: string;
  webhookId: string;
  requestId: string;
  eventType?: string | undefined;
  httpMethod: string;
  sourceIp?: string | undefined;
  userAgent?: string | undefined;
  requestHeaders?: Record<string, unknown> | undefined;
  requestBodyPreview?: string | undefined;
  payloadSizeBytes?: number | undefined;
  success: boolean;
  statusCode: number;
  errorMessage?: string | undefined;
  processingTimeMs?: number | undefined;
  testRunId?: string | undefined;
  resultsSubmitted: number;
  createdAt: string;
}

export interface WebhookStats {
  projectId: string;
  total: number;
  byStatus: Record<string, number>;
  byProvider: Record<string, number>;
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
}

// External Integration Types
export type IntegrationProvider = 'github' | 'github_projects' | 'linear';

export type CredentialType = 'oauth' | 'pat' | 'api_key';

export type CredentialStatus = 'active' | 'expired' | 'revoked' | 'invalid' | 'pending_reauth';

export type MappingDirection = 'pull' | 'push' | 'bidirectional';

export type MappingStatus = 'active' | 'paused' | 'error' | 'pending';

export type SyncQueueStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

export type ConflictResolutionStrategy =
  | 'local_wins'
  | 'external_wins'
  | 'manual'
  | 'merge'
  | 'skip';

export interface IntegrationCredential {
  id: string;
  projectId?: string | undefined;
  provider: IntegrationProvider;
  credentialType: CredentialType;
  status: CredentialStatus;
  scopes: string[];
  providerUserId?: string | undefined;
  providerMetadata?: Record<string, unknown> | undefined;
  lastValidatedAt?: string | undefined;
  validationError?: string | undefined;
  expiresAt?: string | undefined;
  createdAt: string;
  updatedAt: string;
}

export interface IntegrationMapping {
  id: string;
  credentialId: string;
  provider: IntegrationProvider;
  direction: MappingDirection;
  localItemId: string;
  localItemType: string;
  externalId: string;
  externalType: string;
  externalUrl?: string | undefined;
  externalKey?: string | undefined;
  mappingMetadata?: Record<string, unknown> | undefined;
  status: MappingStatus;
  syncEnabled: boolean;
  lastSyncedAt?: string | undefined;
  lastSyncStatus?: string | undefined;
  lastSyncError?: string | undefined;
  fieldMappings?: Record<string, string> | undefined;
  fieldResolutionRules?: Record<string, ConflictResolutionStrategy> | undefined;
  localVersion?: number | undefined;
  externalVersion?: string | undefined;
  createdAt: string;
  updatedAt: string;
}

export interface SyncQueueItem {
  id: string;
  credentialId?: string | undefined;
  mappingId?: string | undefined;
  provider: IntegrationProvider;
  eventType: string;
  direction: string;
  status: SyncQueueStatus;
  priority: number;
  retryCount: number;
  maxRetries: number;
  errorMessage?: string | undefined;
  scheduledAt?: string | undefined;
  startedAt?: string | undefined;
  completedAt?: string | undefined;
  createdAt: string;
}

export interface SyncLog {
  id: string;
  credentialId?: string | undefined;
  mappingId?: string | undefined;
  provider: IntegrationProvider;
  eventType: string;
  direction: string;
  status: string;
  itemsProcessed: number;
  itemsFailed: number;
  itemsSkipped: number;
  errorMessage?: string | undefined;
  startedAt?: string | undefined;
  completedAt?: string | undefined;
  durationMs?: number | undefined;
  createdAt: string;
}

export interface WorkflowRun {
  id: string;
  projectId?: string | undefined;
  graphId?: string | undefined;
  workflowName: string;
  status: string;
  externalRunId?: string | undefined;
  payload?: Record<string, unknown> | undefined;
  result?: Record<string, unknown> | undefined;
  errorMessage?: string | undefined;
  createdByUserId?: string | undefined;
  startedAt?: string | undefined;
  completedAt?: string | undefined;
  createdAt?: string | undefined;
  updatedAt?: string | undefined;
}

export interface WorkflowSchedule {
  id?: string | undefined;
  cronName?: string | undefined;
  expression?: string | undefined;
  workflowName?: string | undefined;
  additionalMetadata?: Record<string, unknown> | undefined;
  [key: string]: unknown;
}

export interface SyncConflict {
  id: string;
  mappingId: string;
  provider: IntegrationProvider;
  conflictType: string;
  fieldName?: string | undefined;
  localValue?: unknown | undefined;
  externalValue?: unknown | undefined;
  localModifiedAt?: string | undefined;
  externalModifiedAt?: string | undefined;
  status: 'pending' | 'resolved' | 'skipped';
  resolution?: string | undefined;
  resolvedValue?: unknown | undefined;
  resolvedBy?: string | undefined;
  resolvedAt?: string | undefined;
  createdAt: string;
}

export interface IntegrationStats {
  projectId: string;
  providers: {
    provider: IntegrationProvider;
    status: CredentialStatus;
    credentialType: CredentialType;
  }[];
  mappings: {
    total: number;
    active: number;
    byProvider: Record<string, number>;
  };
  sync: {
    queuePending: number;
    recentSyncs: number;
    successRate: number;
  };
  conflicts: {
    pending: number;
    resolved: number;
  };
}

export interface SyncStatusSummary {
  projectId: string;
  queue: {
    pending: number;
    processing: number;
    failed: number;
    completed: number;
  };
  recentSyncs: SyncLog[];
  providers: {
    provider: IntegrationProvider;
    status: CredentialStatus;
    lastValidated?: string | undefined;
  }[];
}

// GitHub-specific types
export interface GitHubRepo {
  id: number;
  name: string;
  fullName: string;
  description?: string | undefined;
  htmlUrl: string;
  private: boolean;
  owner: {
    login: string;
    avatarUrl: string;
  };
  defaultBranch: string;
  updatedAt?: string | undefined;
}

export interface GitHubIssue {
  id: number;
  number: number;
  title: string;
  state: string;
  htmlUrl: string;
  body?: string | undefined;
  user: {
    login: string;
    avatarUrl: string;
  };
  labels: string[];
  assignees: string[];
  createdAt: string;
  updatedAt: string;
}

export interface GitHubPullRequest {
  id: number;
  number: number;
  title: string;
  state: string;
  htmlUrl: string;
  body?: string | undefined;
  user: {
    login: string;
    avatarUrl: string;
  };
  labels: string[];
  assignees: string[];
  draft: boolean;
  merged: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface GitHubProject {
  id: string;
  title: string;
  description?: string | undefined;
  url: string;
  closed: boolean;
  public: boolean;
  createdAt?: string | undefined;
  updatedAt?: string | undefined;
}

// Linear-specific types
export interface LinearTeam {
  id: string;
  name: string;
  key: string;
  description?: string | undefined;
  icon?: string | undefined;
  color?: string | undefined;
}

export interface LinearIssue {
  id: string;
  identifier: string;
  title: string;
  description?: string | undefined;
  state?: string | undefined;
  priority?: number | undefined;
  url: string;
  assignee?: string | undefined;
  labels: string[];
  createdAt?: string | undefined;
  updatedAt?: string | undefined;
}

export interface LinearProject {
  id: string;
  name: string;
  description?: string | undefined;
  state?: string | undefined;
  progress?: number | undefined;
  url: string;
  startDate?: string | undefined;
  targetDate?: string | undefined;
}

// API Response types
export interface PaginatedResponse<TItem> {
  items: TItem[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown> | undefined;
}
