// Temporal Dimension Types
// Supports versioning, branching, and futures for multi-dimensional traceability
// Enables navigation across time (past/present/future) and variation (alternatives, forks, experiments)

// =============================================================================
// VERSION BRANCH TYPES
// =============================================================================

/**
 * Branch type classification - similar to git branch naming conventions
 */
export type BranchType =
  | 'main' // Primary production branch
  | 'release' // Release candidate
  | 'feature' // Feature development
  | 'experiment' // A/B testing, "what if" scenarios
  | 'hotfix' // Emergency fixes
  | 'archive'; // Historical reference only

/**
 * Branch lifecycle status
 */
export type BranchStatus =
  | 'active' // Being actively worked on
  | 'review' // Under review for merge
  | 'merged' // Successfully merged into target
  | 'abandoned' // Discarded, not completed
  | 'archived'; // Kept for historical reference

/**
 * A version branch represents a parallel line of development
 * Similar to git branches but for traceability items
 */
export interface VersionBranch {
  id: string;
  projectId: string;

  // Identity
  name: string; // "main", "feature/new-payment", "experiment/ai-routing"
  slug: string; // URL-safe: "feature-new-payment"
  description?: string | undefined;

  // Branch type classification
  branchType: BranchType;

  // Tree structure
  parentBranchId?: string | undefined; // What branch this was created from
  baseVersionId?: string | undefined; // Which version it forked from

  // State
  status: BranchStatus;
  isDefault: boolean; // Is this the "main" branch
  isProtected: boolean; // Prevent direct edits (require merge)

  // Merge tracking
  mergedAt?: string | undefined; // When merged back
  mergedInto?: string | undefined; // Which branch it merged into
  mergedBy?: string | undefined; // Who performed the merge

  // Statistics
  versionCount: number; // Number of versions in this branch
  itemCount: number; // Current number of items

  // Metadata
  metadata?: Record<string, unknown> | undefined;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

// =============================================================================
// VERSION TYPES
// =============================================================================

/**
 * Version status - lifecycle of a version/commit
 */
export type VersionStatus =
  | 'draft' // Work in progress, not finalized
  | 'pending_review' // Submitted for review/approval
  | 'approved' // Approved and ready for use
  | 'rejected' // Failed review, needs changes
  | 'superseded'; // Replaced by a newer version

/**
 * A version represents a point-in-time snapshot of items
 * Similar to a git commit
 */
export interface Version {
  id: string;
  branchId: string;
  projectId: string;

  // Sequence
  versionNumber: number; // Sequential within branch: 1, 2, 3...

  // Tree structure
  parentVersionId?: string | undefined; // Previous version (linear history)
  childVersionIds?: string[] | undefined; // Branches from this point

  // Snapshot reference
  snapshotId: string; // Reference to full state snapshot
  changesetId?: string | undefined; // Delta from parent (for efficiency)

  // Identity
  tag?: string | undefined; // Human-readable tag: "v1.0.0", "MVP", "Q1-Release"
  message: string; // Commit-style message describing changes

  // Statistics
  itemCount: number; // Number of items in this version
  changeCount: number; // Number of changes from parent

  // Quality gates
  status: VersionStatus;
  approvedBy?: string | undefined;
  approvedAt?: string | undefined;
  rejectionReason?: string | undefined;

  // Metadata
  metadata?: Record<string, unknown> | undefined;
  createdBy: string;
  createdAt: string;
}

/**
 * Version changeset - delta between two versions
 */
export interface VersionChangeset {
  id: string;
  versionId: string;
  parentVersionId: string;

  // Changes
  addedItemIds: string[]; // Items added in this version
  removedItemIds: string[]; // Items removed in this version
  modifiedItemIds: string[]; // Items modified in this version

  // Statistics
  addedCount: number;
  removedCount: number;
  modifiedCount: number;
  totalChanges: number;

  // Detailed changes (optional, for diff view)
  modifications?: ItemModification[] | undefined;

  createdAt: string;
}

/**
 * Detailed modification record for an item
 */
export interface ItemModification {
  itemId: string;
  itemTitle: string;

  // Field-level changes
  fieldChanges: FieldChange[];

  // Summary
  changeType: 'content' | 'metadata' | 'status' | 'relationships' | 'mixed';
}

/**
 * Single field change
 */
export interface FieldChange {
  field: string;
  oldValue: unknown;
  newValue: unknown;
  changeType: 'added' | 'removed' | 'modified';
}

// =============================================================================
// ITEM VERSION MAPPING
// =============================================================================

/**
 * Maps an item to a specific version
 * Stores the item's state at that point in time
 */
export interface ItemVersion {
  id: string;
  itemId: string;
  versionId: string;
  branchId: string;
  projectId: string;

  // Item state at this version (snapshot)
  state: ItemSnapshot;

  // Lifecycle
  lifecycle: ItemLifecycle;

  // Version tracking
  introducedInVersionId: string; // First appeared in this version
  lastModifiedInVersionId: string; // Last changed in this version

  // Metadata
  createdAt: string;
}

/**
 * Snapshot of an item's state at a point in time
 */
export interface ItemSnapshot {
  // Core fields
  title: string;
  description?: string | undefined;
  type: string;
  status: string;
  priority?: string | undefined;

  // Hierarchy
  parentId?: string | undefined;

  // Dimensions
  dimensions?: Record<string, unknown> | undefined;

  // References
  canonicalId?: string | undefined;
  codeRef?: Record<string, unknown> | undefined;
  docRef?: Record<string, unknown> | undefined;

  // Full metadata
  metadata?: Record<string, unknown> | undefined;
}

// =============================================================================
// ITEM LIFECYCLE
// =============================================================================

/**
 * Item lifecycle - progression through development stages
 */
export type ItemLifecycle =
  | 'idea' // Just an idea, no commitment
  | 'proposed' // Formally proposed for consideration
  | 'planned' // Scheduled for implementation
  | 'in_progress' // Being actively worked on
  | 'implemented' // Code/content complete
  | 'verified' // Tested/validated
  | 'released' // In production/published
  | 'deprecated' // Being phased out
  | 'retired'; // No longer active

/**
 * Lifecycle transition rules
 */
export const LIFECYCLE_TRANSITIONS: Record<ItemLifecycle, ItemLifecycle[]> = {
  deprecated: ['retired', 'released'],
  idea: ['proposed', 'retired'],
  implemented: ['verified', 'in_progress', 'retired'],
  in_progress: ['implemented', 'planned', 'retired'],
  planned: ['in_progress', 'retired'],
  proposed: ['planned', 'retired'],
  released: ['deprecated'],
  retired: [],
  verified: ['released', 'implemented', 'retired'],
};

// =============================================================================
// ITEM ALTERNATIVES (VARIATIONS/EXPERIMENTS)
// =============================================================================

/**
 * Relationship between alternative items
 */
export type AlternativeRelationship =
  | 'alternative_to' // Alternative approach to same problem
  | 'supersedes' // Newer version replacing older
  | 'experiment_of'; // Experimental variation

/**
 * Tracks alternative implementations or approaches
 */
export interface ItemAlternative {
  id: string;
  projectId: string;

  // The items being compared
  baseItemId: string; // Original/base item
  alternativeItemId: string; // Alternative item

  // Relationship
  relationship: AlternativeRelationship;
  description?: string | undefined;

  // Selection tracking
  isChosen: boolean; // Was this alternative selected
  chosenAt?: string | undefined;
  chosenBy?: string | undefined;
  chosenReason?: string | undefined;

  // Comparison metrics
  metrics?: {
    effort?: number | undefined; // Estimated effort (story points, hours)
    risk?: 'low' | 'medium' | 'high' | undefined;
    coverage?: number | undefined; // How well it addresses the need
    complexity?: number | undefined;
  };

  // Metadata
  createdAt: string;
  updatedAt: string;
}

// =============================================================================
// TEMPORAL ITEM EXTENSION
// =============================================================================

/**
 * Temporal metadata that can be added to any Item
 */
export interface TemporalMetadata {
  // Version tracking
  versionId: string; // Which version this item exists in
  branchId: string; // Which branch
  introducedInVersion: string; // First appeared
  lastModifiedVersion: string; // Last change

  // Lifecycle
  lifecycle: ItemLifecycle;
  lifecycleChangedAt?: string | undefined;
  lifecycleChangedBy?: string | undefined;

  // Alternatives
  alternatives?: {
    itemId: string;
    relationship: AlternativeRelationship;
    isChosen?: boolean | undefined;
    chosenAt?: string | undefined;
  }[];

  // Future planning
  plannedFor?: {
    targetVersion?: string | undefined; // Which version it's planned for
    targetDate?: string | undefined; // Target completion date
    probability?: number | undefined; // 0-1 likelihood of inclusion
    dependencies?: string[] | undefined; // Item IDs that must complete first
  };
}

// =============================================================================
// VERSION COMPARISON & DIFF
// =============================================================================

/**
 * Type of change in a diff
 */
export type DiffChangeType = 'added' | 'removed' | 'modified';

/**
 * Significance level of a change
 */
export type DiffSignificance = 'minor' | 'moderate' | 'major' | 'breaking';

/**
 * Single field change
 */
export interface FieldDiffChange {
  field: string;
  oldValue: unknown;
  newValue: unknown;
  changeType: 'added' | 'removed' | 'modified';
}

/**
 * Item in a diff result
 */
export interface DiffItem {
  itemId: string;
  type: string;
  title: string;
  changeType: DiffChangeType;

  // For modified items - field-level changes
  fieldChanges?: FieldDiffChange[] | undefined;

  // Severity/impact
  significance: DiffSignificance;
}

/**
 * Statistics about a diff
 */
export interface DiffStatistics {
  totalChanges: number;
  addedCount: number;
  removedCount: number;
  modifiedCount: number;
  unchangedCount: number;
}

/**
 * Result of comparing two versions
 */
export interface VersionDiff {
  versionA: string; // Source version ID
  versionB: string; // Target version ID
  versionANumber: number;
  versionBNumber: number;

  // Changes
  added: DiffItem[]; // New in B
  removed: DiffItem[]; // Gone in B
  modified: DiffItem[]; // Changed between A and B
  unchanged: number; // Count of unchanged items

  // Statistics
  stats: DiffStatistics;

  // Computed at
  computedAt: string;
}

/**
 * Diff view configuration
 */
export interface DiffViewConfig {
  showUnchanged: boolean;
  expandModified: boolean;
  filterByType?: string | undefined;
  sortBy?: 'title' | 'changeType' | 'significance' | undefined;
}

/**
 * Options for diff export
 */
export interface DiffExportOptions {
  format: 'json' | 'csv' | 'markdown' | 'html';
  includeUnchanged: boolean;
  includeFieldChanges: boolean;
}

/**
 * Diff export result
 */
export interface DiffExportResult {
  filename: string;
  mimeType: string;
  content: string | Blob;
}

/**
 * UI state for diff viewer
 */
export interface DiffViewerState {
  expandedItems: Set<string>;
  selectedItems: Set<string>;
  activeTab: 'added' | 'removed' | 'modified';
  searchQuery: string;
}

// =============================================================================
// MERGE OPERATIONS
// =============================================================================

/**
 * Merge request - proposal to merge one branch into another
 */
export interface MergeRequest {
  id: string;
  projectId: string;

  // Branches
  sourceBranchId: string;
  targetBranchId: string;

  // Versions
  sourceVersionId: string; // Head of source branch
  baseVersionId: string; // Common ancestor

  // Status
  status: 'open' | 'approved' | 'merged' | 'closed' | 'conflict';

  // Details
  title: string;
  description?: string | undefined;

  // Diff
  diff?: VersionDiff | undefined;

  // Conflicts (if any)
  conflicts?: MergeConflict[] | undefined;

  // Review
  reviewers?: string[] | undefined;
  approvedBy?: string[] | undefined;

  // Timestamps
  createdBy: string;
  createdAt: string;
  mergedAt?: string | undefined;
  mergedBy?: string | undefined;
  closedAt?: string | undefined;
}

/**
 * Conflict during merge
 */
export interface MergeConflict {
  itemId: string;
  itemTitle: string;

  // Conflicting values
  sourceValue: unknown;
  targetValue: unknown;
  baseValue?: unknown | undefined; // Value in common ancestor

  // Resolution
  resolution?: 'source' | 'target' | 'manual' | 'both' | undefined;
  resolvedValue?: unknown | undefined;
  resolvedBy?: string | undefined;
  resolvedAt?: string | undefined;
}

// =============================================================================
// TEMPORAL NAVIGATION
// =============================================================================

/**
 * Temporal navigation mode
 */
export type TemporalViewMode =
  | 'timeline' // Horizontal timeline with version markers
  | 'branches' // Tree visualization of branches
  | 'comparison' // Side-by-side diff of two versions
  | 'progress'; // Milestone/sprint tracking dashboard

/**
 * Temporal filter for querying items at a point in time
 */
export interface TemporalFilter {
  // Time-based
  atVersion?: string | undefined; // Specific version ID
  atDate?: string | undefined; // Point in time
  afterVersion?: string | undefined; // After this version
  beforeVersion?: string | undefined; // Before this version

  // Branch-based
  branchId?: string | undefined; // Specific branch
  includeMerged?: boolean | undefined; // Include merged branches

  // Lifecycle-based
  lifecycle?: ItemLifecycle[] | undefined; // Filter by lifecycle stages

  // Status-based
  versionStatus?: VersionStatus[] | undefined; // Filter by version status
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Check if a lifecycle transition is valid
 *
 * @param {ItemLifecycle} from - Current lifecycle stage.
 * @param {ItemLifecycle} to - Target lifecycle stage.
 * @returns {boolean} True when transition from `from` to `to` is allowed.
 */
export function isValidLifecycleTransition(from: ItemLifecycle, to: ItemLifecycle): boolean {
  return LIFECYCLE_TRANSITIONS[from]?.includes(to) ?? false;
}

/**
 * Get display color for branch type
 *
 * @param {BranchType} branchType - Branch type to map.
 * @returns {string} Hex color for branch type.
 */
export function getBranchTypeColor(branchType: BranchType): string {
  const colors: Record<BranchType, string> = {
    main: '#22c55e', // Green
    release: '#3b82f6', // Blue
    feature: '#a855f7', // Purple
    experiment: '#f59e0b', // Amber
    hotfix: '#ef4444', // Red
    archive: '#6b7280', // Gray
  };
  return colors[branchType];
}

/**
 * Get display color for lifecycle stage
 *
 * @param {ItemLifecycle} lifecycle - Lifecycle stage to map.
 * @returns {string} Hex color for lifecycle stage.
 */
export function getLifecycleColor(lifecycle: ItemLifecycle): string {
  const colors: Record<ItemLifecycle, string> = {
    idea: '#94a3b8', // Slate
    proposed: '#a78bfa', // Violet
    planned: '#60a5fa', // Blue
    in_progress: '#fbbf24', // Amber
    implemented: '#34d399', // Emerald
    verified: '#22c55e', // Green
    released: '#10b981', // Emerald dark
    deprecated: '#f97316', // Orange
    retired: '#6b7280', // Gray
  };
  return colors[lifecycle];
}

/**
 * Get display icon for branch type
 *
 * @param {BranchType} branchType - Branch type to map.
 * @returns {string} Icon name for branch type.
 */
export function getBranchTypeIcon(branchType: BranchType): string {
  const icons: Record<BranchType, string> = {
    archive: 'Archive',
    experiment: 'Flask',
    feature: 'Sparkles',
    hotfix: 'Zap',
    main: 'GitBranch',
    release: 'Tag',
  };
  return icons[branchType];
}
