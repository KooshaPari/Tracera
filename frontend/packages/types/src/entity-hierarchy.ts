// Enhanced Entity Hierarchy Types
// Supports deep hierarchical breakdown: Page → Layout → Section → Component → Element
// And domain hierarchies: Epic → Story → Task, Test Suite → Test Case → Assertion

// ============================================================================
// ENTITY TYPE TAXONOMY
// ============================================================================

/**
 * UI/Visual Entity Types - Physical map of the site/app
 * Follows atomic design + page architecture pattern
 */
export type UIEntityType =
  | 'site' // Root: entire application
  | 'page' // Top-level route/view
  | 'layout' // Page structure (header, sidebar, main, footer)
  | 'section' // Major content area
  | 'subsection' // Nested content grouping
  | 'component' // Reusable UI component
  | 'subcomponent' // Nested component
  | 'element' // Atomic element (button, input, text)
  | 'modal' // Overlay component
  | 'popup' // Temporary overlay
  | 'toast' // Notification
  | 'drawer'; // Slide-in panel

/**
 * Product/Requirements Entity Types
 * Follows agile/product hierarchy
 */
export type ProductEntityType =
  | 'initiative' // Strategic goal
  | 'epic' // Large feature
  | 'feature' // Deliverable capability
  | 'user_story' // User-facing requirement
  | 'acceptance_criteria' // Story validation
  | 'task' // Implementation unit
  | 'subtask'; // Granular work item

/**
 * Technical/Code Entity Types
 */
export type TechnicalEntityType =
  | 'service' // Backend service/microservice
  | 'module' // Code module/package
  | 'class' // Class definition
  | 'function' // Function/method
  | 'api_endpoint' // REST/GraphQL endpoint
  | 'database_table' // DB table/collection
  | 'database_field' // Column/field
  | 'config'; // Configuration

/**
 * Testing Entity Types
 */
export type TestEntityType =
  | 'test_suite' // Collection of tests
  | 'test_case' // Individual test
  | 'test_step' // Test action
  | 'assertion' // Validation check
  | 'fixture' // Test data setup
  | 'mock'; // Mock/stub

/**
 * Design/UX Entity Types
 */
export type DesignEntityType =
  | 'wireframe' // Lo-fi design
  | 'mockup' // Hi-fi design
  | 'prototype' // Interactive design
  | 'design_token' // Design system token
  | 'style_guide'; // Style documentation

/**
 * Documentation Entity Types
 */
export type DocEntityType =
  | 'doc_root' // Documentation root
  | 'doc_section' // Major section
  | 'doc_page' // Single doc page
  | 'doc_block'; // Content block

/**
 * All entity types combined
 */
export type EntityType =
  | UIEntityType
  | ProductEntityType
  | TechnicalEntityType
  | TestEntityType
  | DesignEntityType
  | DocEntityType;

// ============================================================================
// ENTITY HIERARCHY CONFIGURATION
// ============================================================================

/**
 * Defines valid parent-child relationships for each entity type
 */
export const ENTITY_HIERARCHY: Record<EntityType, EntityType[]> = {
  // UI Hierarchy: site → page → layout → section → component → element
  site: ['page'],
  page: ['layout', 'section', 'component', 'modal', 'drawer'],
  layout: ['section', 'component'],
  section: ['subsection', 'component'],
  subsection: ['component', 'subcomponent'],
  component: ['subcomponent', 'element'],
  subcomponent: ['element'],
  element: [],
  modal: ['section', 'component'],
  popup: ['component', 'element'],
  toast: ['element'],
  drawer: ['section', 'component'],

  // Product Hierarchy: initiative → epic → feature → story → task
  initiative: ['epic'],
  epic: ['feature', 'user_story'],
  feature: ['user_story', 'task'],
  user_story: ['acceptance_criteria', 'task'],
  acceptance_criteria: [],
  task: ['subtask'],
  subtask: [],

  // Technical Hierarchy
  service: ['module', 'api_endpoint', 'database_table'],
  module: ['class', 'function'],
  class: ['function'],
  function: [],
  api_endpoint: [],
  database_table: ['database_field'],
  database_field: [],
  config: [],

  // Test Hierarchy
  test_suite: ['test_case'],
  test_case: ['test_step', 'assertion'],
  test_step: ['assertion'],
  assertion: [],
  fixture: [],
  mock: [],

  // Design Hierarchy
  wireframe: [],
  mockup: [],
  prototype: [],
  design_token: [],
  style_guide: [],

  // Doc Hierarchy
  doc_root: ['doc_section'],
  doc_section: ['doc_page'],
  doc_page: ['doc_block'],
  doc_block: [],
};

/**
 * Entity depth levels for indentation and styling
 */
export const ENTITY_DEPTH_LEVELS: Record<EntityType, number> = {
  // UI: 0-6 depth
  site: 0,
  page: 1,
  layout: 2,
  section: 3,
  subsection: 4,
  component: 5,
  subcomponent: 6,
  element: 7,
  modal: 2,
  popup: 3,
  toast: 2,
  drawer: 2,

  // Product: 0-5 depth
  initiative: 0,
  epic: 1,
  feature: 2,
  user_story: 3,
  acceptance_criteria: 4,
  task: 4,
  subtask: 5,

  // Technical
  service: 0,
  module: 1,
  class: 2,
  function: 3,
  api_endpoint: 2,
  database_table: 1,
  database_field: 2,
  config: 1,

  // Test
  test_suite: 0,
  test_case: 1,
  test_step: 2,
  assertion: 3,
  fixture: 1,
  mock: 1,

  // Design
  wireframe: 1,
  mockup: 1,
  prototype: 1,
  design_token: 2,
  style_guide: 1,

  // Doc
  doc_root: 0,
  doc_section: 1,
  doc_page: 2,
  doc_block: 3,
};

// ============================================================================
// ENHANCED LINK TYPES
// ============================================================================

/**
 * Relationship types with semantic meaning
 */
export type EnhancedLinkType =
  // Hierarchical
  | 'parent_of' // Direct parent-child
  | 'contains' // Composition
  | 'part_of' // Inverse of contains

  // Traceability
  | 'implements' // Code implements requirement
  | 'tests' // Test validates requirement
  | 'verifies' // Verification link
  | 'satisfies' // Requirement satisfaction
  | 'derives_from' // Derived requirement
  | 'refines' // More detailed version

  // Dependencies
  | 'depends_on' // Hard dependency
  | 'uses' // Soft dependency
  | 'imports' // Code import
  | 'calls' // Function call
  | 'blocks' // Blocking relationship

  // UI Flow
  | 'navigates_to' // Page navigation
  | 'triggers' // Action trigger
  | 'opens' // Opens modal/drawer
  | 'closes' // Closes overlay
  | 'renders' // Component renders child
  | 'includes' // Component inclusion

  // Semantic
  | 'related_to' // General relation
  | 'similar_to' // Similarity
  | 'conflicts_with' // Conflict
  | 'alternative_to' // Alternative option
  | 'duplicates'; // Duplicate

/**
 * Link metadata per type
 */
export interface LinkMetadata {
  // For navigates_to
  trigger?: 'click' | 'hover' | 'programmatic' | 'redirect' | undefined;

  // For implements/tests
  coverage?: number | undefined; // 0-100%

  // For depends_on
  dependency_type?: 'required' | 'optional' | 'conditional' | undefined;

  // For UI connections
  interaction?: 'click' | 'hover' | 'focus' | 'blur' | 'submit' | undefined;

  // For aggregation
  is_aggregated?: boolean | undefined;
  aggregation_count?: number | undefined;

  // Common
  confidence?: 'high' | 'medium' | 'low' | undefined;
  automated?: boolean | undefined;
}

// ============================================================================
// AGGREGATION NODES
// ============================================================================

/**
 * Aggregation node for reducing visual complexity
 * E.g., "Common Error Handlers" aggregates 50 error code connections
 */
export interface AggregationNode {
  id: string;
  type: 'aggregation';
  label: string;
  description?: string | undefined;

  // What this aggregates
  aggregatedType: EntityType;
  aggregatedCount: number;
  aggregatedIds: string[];

  // Aggregation criteria
  criteria: {
    type: 'common_parent' | 'same_type' | 'shared_dependency' | 'custom';
    pattern?: string | undefined; // Regex for custom matching
    threshold?: number | undefined; // Min items to aggregate
  };

  // Visual
  color?: string | undefined;
  icon?: string | undefined;
  collapsed?: boolean | undefined;
}

// ============================================================================
// ENHANCED ENTITY WITH HIERARCHY
// ============================================================================

/**
 * Entity expansion state for UI
 */
export type EntityExpansionState = 'collapsed' | 'preview' | 'panel' | 'full_page';

/**
 * Edit capability for an entity
 */
export interface EditCapability {
  canEdit: boolean;
  editType: 'instant' | 'agent_required' | 'manual';
  editableFields: string[];
  agentType?: string | undefined; // Which agent handles edits
  automationId?: string | undefined; // Automation script ID
}

/**
 * UI Preview data for visual entities
 */
export interface UIPreview {
  // Screenshot/thumbnail
  thumbnailUrl?: string | undefined;
  screenshotUrl?: string | undefined;

  // Live preview data
  componentPath?: string | undefined; // Path to Storybook/component
  propsSchema?: Record<string, unknown> | undefined; // Component props
  defaultProps?: Record<string, unknown> | undefined;

  // Dimensions
  width?: number | undefined;
  height?: number | undefined;

  // Variants
  variants?: {
    name: string;
    props: Record<string, unknown>;
    thumbnailUrl?: string | undefined;
  }[];
}

/**
 * Enhanced Item with full hierarchy support
 */
export interface HierarchicalEntity {
  // Identity
  id: string;
  projectId: string;
  externalId?: string | undefined; // Legacy/external system ID

  // Type system
  entityType: EntityType;

  // Hierarchy
  parentId?: string | undefined;
  path: string[]; // Full path from root: ["site-1", "page-2", "layout-3", ...]
  depth: number;
  hasChildren: boolean;
  childCount: number;
  childTypes?: EntityType[] | undefined; // Types of immediate children

  // Content
  name: string;
  title: string;
  description?: string | undefined;

  // Status
  status: 'draft' | 'active' | 'deprecated' | 'archived';
  priority?: 'low' | 'medium' | 'high' | 'critical' | undefined;

  // UI State
  expansionState: EntityExpansionState;
  isSelected: boolean;
  isHovered: boolean;

  // Visual/Preview
  icon?: string | undefined;
  color?: string | undefined;
  preview?: UIPreview | undefined;

  // Edit capabilities
  editCapability: EditCapability;

  // Aggregation
  isAggregation?: boolean | undefined;
  aggregationData?: AggregationNode | undefined;

  // Relationships
  incomingLinkCount: number;
  outgoingLinkCount: number;

  // Metadata
  tags?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;

  // Timestamps
  createdAt: string;
  updatedAt: string;
  createdBy?: string | undefined;
  updatedBy?: string | undefined;
  version: number;
}

/**
 * Enhanced Link with metadata
 */
export interface HierarchicalLink {
  id: string;
  projectId: string;

  // Endpoints
  sourceId: string;
  targetId: string;
  sourceType: EntityType;
  targetType: EntityType;

  // Link semantics
  linkType: EnhancedLinkType;
  metadata: LinkMetadata;

  // Display
  label?: string | undefined;
  description?: string | undefined;

  // Aggregation
  isAggregated?: boolean | undefined;
  aggregationId?: string | undefined; // Points to AggregationNode

  // Validation
  confidence: 'high' | 'medium' | 'low' | 'unknown';
  validationStatus: 'validated' | 'pending' | 'failed' | 'not_required';

  // Timestamps
  createdAt: string;
  updatedAt?: string | undefined;
}

// ============================================================================
// NODE DISPLAY CONFIGURATION
// ============================================================================

/**
 * Block pill configuration for graph nodes
 */
export interface NodeDisplayConfig {
  // Size variants
  size: 'compact' | 'normal' | 'expanded' | 'full';

  // Content visibility
  showIcon: boolean;
  showType: boolean;
  showStatus: boolean;
  showPreview: boolean;
  showChildCount: boolean;
  showLinkCount: boolean;
  showDescription: boolean;
  showActions: boolean;

  // Dimensions
  minWidth: number;
  maxWidth: number;
  minHeight: number;
  maxHeight: number;

  // Preview area
  previewHeight?: number | undefined;
  previewPosition?: 'top' | 'bottom' | 'inline' | undefined;
}

/**
 * Default display configs per expansion state
 */
export const NODE_DISPLAY_CONFIGS: Record<EntityExpansionState, NodeDisplayConfig> = {
  collapsed: {
    maxHeight: 48,
    maxWidth: 200,
    minHeight: 32,
    minWidth: 120,
    showActions: false,
    showChildCount: true,
    showDescription: false,
    showIcon: true,
    showLinkCount: false,
    showPreview: false,
    showStatus: false,
    showType: false,
    size: 'compact',
  },
  full_page: {
    maxHeight: 800,
    maxWidth: 1200,
    minHeight: 400,
    minWidth: 600,
    previewHeight: 300,
    previewPosition: 'top',
    showActions: true,
    showChildCount: true,
    showDescription: true,
    showIcon: true,
    showLinkCount: true,
    showPreview: true,
    showStatus: true,
    showType: true,
    size: 'full',
  },
  panel: {
    maxHeight: 400,
    maxWidth: 480,
    minHeight: 240,
    minWidth: 320,
    previewHeight: 160,
    previewPosition: 'top',
    showActions: true,
    showChildCount: true,
    showDescription: true,
    showIcon: true,
    showLinkCount: true,
    showPreview: true,
    showStatus: true,
    showType: true,
    size: 'expanded',
  },
  preview: {
    maxHeight: 200,
    maxWidth: 320,
    minHeight: 120,
    minWidth: 200,
    previewHeight: 80,
    previewPosition: 'top',
    showActions: false,
    showChildCount: true,
    showDescription: true,
    showIcon: true,
    showLinkCount: true,
    showPreview: true,
    showStatus: true,
    showType: true,
    size: 'normal',
  },
};

// ============================================================================
// TYPE GUARDS
// ============================================================================

export function isUIEntityType(type: EntityType): type is UIEntityType {
  return [
    'site',
    'page',
    'layout',
    'section',
    'subsection',
    'component',
    'subcomponent',
    'element',
    'modal',
    'popup',
    'toast',
    'drawer',
  ].includes(type);
}

export function isProductEntityType(type: EntityType): type is ProductEntityType {
  return [
    'initiative',
    'epic',
    'feature',
    'user_story',
    'acceptance_criteria',
    'task',
    'subtask',
  ].includes(type);
}

export function isTechnicalEntityType(type: EntityType): type is TechnicalEntityType {
  return [
    'service',
    'module',
    'class',
    'function',
    'api_endpoint',
    'database_table',
    'database_field',
    'config',
  ].includes(type);
}

export function isTestEntityType(type: EntityType): type is TestEntityType {
  return ['test_suite', 'test_case', 'test_step', 'assertion', 'fixture', 'mock'].includes(type);
}

export function isDesignEntityType(type: EntityType): type is DesignEntityType {
  return ['wireframe', 'mockup', 'prototype', 'design_token', 'style_guide'].includes(type);
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get valid child types for an entity
 *
 * @param {EntityType} entityType - Parent entity type.
 * @returns {EntityType[]} List of allowed child entity types.
 */
export function getValidChildTypes(entityType: EntityType): EntityType[] {
  return ENTITY_HIERARCHY[entityType] || [];
}

/**
 * Check if a parent-child relationship is valid
 *
 * @param {EntityType} parentType - Proposed parent entity type.
 * @param {EntityType} childType - Proposed child entity type.
 * @returns {boolean} True when the child type is allowed under the parent.
 */
export function isValidParentChild(parentType: EntityType, childType: EntityType): boolean {
  const validChildren = ENTITY_HIERARCHY[parentType];
  return validChildren?.includes(childType) ?? false;
}

/**
 * Get depth level for an entity type
 *
 * @param {EntityType} entityType - Entity type to resolve.
 * @returns {number} Numeric depth level in the hierarchy.
 */
export function getEntityDepth(entityType: EntityType): number {
  return ENTITY_DEPTH_LEVELS[entityType] ?? 0;
}

/**
 * Get perspective for entity type
 *
 * @param {EntityType} entityType - Entity type to evaluate.
 * @returns {'ui' | 'product' | 'technical' | 'test' | 'design' | 'doc'} Perspective bucket.
 */
export function getEntityPerspective(
  entityType: EntityType,
): 'ui' | 'product' | 'technical' | 'test' | 'design' | 'doc' {
  if (isUIEntityType(entityType)) {
    return 'ui';
  }
  if (isProductEntityType(entityType)) {
    return 'product';
  }
  if (isTechnicalEntityType(entityType)) {
    return 'technical';
  }
  if (isTestEntityType(entityType)) {
    return 'test';
  }
  if (isDesignEntityType(entityType)) {
    return 'design';
  }
  return 'doc';
}
