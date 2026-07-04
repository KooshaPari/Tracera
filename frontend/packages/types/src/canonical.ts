// Canonical Concepts and Multi-Dimensional Traceability Types
// Implements the Three-Layer Equivalence Model:
// 1. Canonical Concepts (abstract, view-agnostic entities)
// 2. View Projections (perspective-specific manifestations)
// 3. Inferred Equivalence (detected relationships)

// =============================================================================
// EQUIVALENCE DETECTION STRATEGIES
// =============================================================================

/**
 * Strategy used to detect equivalence between items
 * Each strategy has a default confidence score
 */
export type EquivalenceStrategy =
  | 'explicit_annotation' // @trace-implements, @canonical - confidence: 1.0
  | 'manual_link' // User-created link - confidence: 1.0
  | 'api_contract' // Frontend fetch → backend route - confidence: 0.9
  | 'shared_canonical' // Same canonical concept - confidence: 0.9
  | 'naming_pattern' // CamelCase/snake_case matching - confidence: 0.7
  | 'semantic_similarity' // Embedding cosine similarity - confidence: 0.6
  | 'structural' // Similar structure/hierarchy - confidence: 0.5
  | 'temporal' // Created/modified together - confidence: 0.4
  | 'co_occurrence'; // Frequently appear together - confidence: 0.3

/**
 * Default confidence scores for each strategy
 */
export const STRATEGY_CONFIDENCE: Record<EquivalenceStrategy, number> = {
  api_contract: 0.9,
  co_occurrence: 0.3,
  explicit_annotation: 1,
  manual_link: 1,
  naming_pattern: 0.7,
  semantic_similarity: 0.6,
  shared_canonical: 0.9,
  structural: 0.5,
  temporal: 0.4,
};

// =============================================================================
// CANONICAL CONCEPTS
// =============================================================================

/**
 * A Canonical Concept is an abstract, view-agnostic entity that represents
 * a single business/technical concept that may manifest differently across
 * perspectives (e.g., "User Authentication" appears as a requirement in
 * business view, an API endpoint in technical view, a login form in UI view)
 */
export interface CanonicalConcept {
  id: string;
  projectId: string;

  // Identity
  name: string; // Human-readable name: "User Authentication"
  slug: string; // URL-safe identifier: "user-authentication"
  description?: string | undefined; // Detailed description

  // Classification
  domain: string; // Business domain: "security", "payments", "users"
  category?: string | undefined; // Sub-category within domain
  tags?: string[] | undefined; // Additional classification tags

  // Semantic Embedding
  embedding?: number[] | undefined; // Vector embedding for similarity search
  embeddingModel?: string | undefined; // Model used: "text-embedding-3-small"
  embeddingUpdatedAt?: string | undefined; // When embedding was last computed

  // Projections (items that represent this concept in different views)
  projectionCount: number; // Number of linked items
  projectionIds?: string[] | undefined; // IDs of linked items (lazy loaded)

  // Relationships to other canonical concepts
  relatedConceptIds?: string[] | undefined; // Related concepts
  parentConceptId?: string | undefined; // Hierarchical parent
  childConceptIds?: string[] | undefined; // Hierarchical children

  // Metadata
  confidence: number; // 0-1, how confident we are this is a valid concept
  source: 'manual' | 'inferred' | 'imported';
  createdBy?: string | undefined;

  // Timestamps
  createdAt: string;
  updatedAt: string;
  version: number;
}

/**
 * A projection links an Item to a CanonicalConcept
 * Multiple items can project the same concept (one per perspective)
 */
export interface CanonicalProjection {
  id: string;
  canonicalId: string; // The canonical concept
  itemId: string; // The item that manifests this concept
  projectId: string;

  // Perspective context
  perspective: string; // Which perspective this projection belongs to

  // Confidence and provenance
  confidence: number; // 0-1, how confident is this mapping
  strategy: EquivalenceStrategy; // How was this detected

  // Manual override
  isConfirmed: boolean; // User confirmed this mapping
  isRejected: boolean; // User rejected this mapping
  confirmedBy?: string | undefined;
  confirmedAt?: string | undefined;

  // Metadata
  metadata?: Record<string, unknown> | undefined;
  createdAt: string;
  updatedAt: string;
}

// =============================================================================
// EQUIVALENCE LINKS
// =============================================================================

/**
 * An equivalence link connects two items that represent the same concept
 * This is the inferred layer - detected relationships between items
 */
export interface EquivalenceLink {
  id: string;
  projectId: string;

  // The two items being linked
  sourceItemId: string;
  targetItemId: string;

  // Equivalence details
  equivalenceType: EquivalenceLinkType;
  confidence: number; // Aggregated confidence from all strategies

  // Detection provenance
  strategies: EquivalenceEvidence[];

  // Canonical concept (if both items share one)
  canonicalId?: string | undefined;

  // User actions
  status: 'suggested' | 'confirmed' | 'rejected' | 'auto_confirmed';
  confirmedBy?: string | undefined;
  confirmedAt?: string | undefined;
  rejectedReason?: string | undefined;

  // Timestamps
  createdAt: string;
  updatedAt: string;
}

/**
 * Types of equivalence relationships
 */
export type EquivalenceLinkType =
  | 'same_as' // Exact same concept in different views
  | 'represents' // One item represents another (code implements requirement)
  | 'manifests_as' // Abstract concept manifests as concrete item
  | 'derived_from' // One item derived from another
  | 'alternative_to'; // Alternative implementation/approach

/**
 * Evidence for an equivalence detection
 */
export interface EquivalenceEvidence {
  strategy: EquivalenceStrategy;
  confidence: number;
  details: string; // Human-readable explanation
  detectedAt: string;
  metadata?: Record<string, unknown> | undefined;
}

// =============================================================================
// DIMENSIONS (Orthogonal Cross-Cutting Concerns)
// =============================================================================

/**
 * Dimensions are orthogonal to perspectives - they represent the STATE
 * of items rather than WHO sees them. Every item can have dimension values
 * regardless of which perspective it belongs to.
 */

/**
 * Maturity dimension - how complete/stable is this item
 */
export type MaturityLevel =
  | 'idea' // Just an idea, not fleshed out
  | 'draft' // Initial draft, incomplete
  | 'defined' // Well-defined but not implemented
  | 'implemented' // Implemented but not verified
  | 'verified' // Verified/tested
  | 'stable' // Stable, in production
  | 'deprecated'; // Marked for removal

/**
 * Complexity dimension - how complex is this item
 */
export type ComplexityLevel =
  | 'trivial' // Very simple, obvious
  | 'simple' // Simple, straightforward
  | 'moderate' // Some complexity
  | 'complex' // Significant complexity
  | 'very_complex'; // High complexity, needs decomposition

/**
 * Coverage dimension - how well is this item covered by tests/docs
 */
export interface CoverageMetrics {
  testCoverage: number; // 0-100, percentage of test coverage
  docCoverage: number; // 0-100, percentage of documentation coverage
  traceCoverage: number; // 0-100, percentage of traceability links
  overallCoverage: number; // Weighted average
}

/**
 * Risk dimension - risk level of this item
 */
export type RiskLevel = 'none' | 'low' | 'medium' | 'high' | 'critical';

/**
 * All dimensions for an item
 */
export interface ItemDimensions {
  maturity?: MaturityLevel | undefined;
  complexity?: ComplexityLevel | undefined;
  coverage?: CoverageMetrics | undefined;
  risk?: RiskLevel | undefined;

  // Custom dimensions (project-specific)
  custom?: Record<string, string | number | boolean> | undefined;
}

/**
 * Dimension filter configuration for UI
 */
export interface DimensionFilter {
  dimension: keyof ItemDimensions | string;
  operator: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'not_in';
  value: string | number | boolean | string[] | number[];
}

/**
 * Dimension display mode in the graph
 */
export type DimensionDisplayMode =
  | 'filter' // Hide items that don't match
  | 'highlight' // Highlight matching items, dim others
  | 'color' // Color-code by dimension value
  | 'size'; // Size nodes by dimension value

// =============================================================================
// CODE & DOCUMENTATION REFERENCES
// =============================================================================

/**
 * Reference to a code entity (function, class, file, etc.)
 */
export interface CodeReference {
  id: string;

  // Location
  repositoryUrl?: string | undefined; // GitHub/GitLab URL
  filePath: string; // Path within repo
  startLine?: number | undefined; // Start line number
  endLine?: number | undefined; // End line number

  // Symbol information
  symbolName: string; // Function/class/variable name
  symbolType: CodeSymbolType; // Type of symbol
  language: string; // Programming language

  // AST information
  signature?: string | undefined; // Function signature
  parentSymbol?: string | undefined; // Parent class/module

  // Semantic
  embedding?: number[] | undefined; // Code embedding for similarity

  // Metadata
  lastSyncedAt?: string | undefined;
  commitSha?: string | undefined;
}

export type CodeSymbolType =
  | 'file'
  | 'module'
  | 'class'
  | 'interface'
  | 'function'
  | 'method'
  | 'variable'
  | 'constant'
  | 'type'
  | 'enum'
  | 'component' // React/Vue component
  | 'hook' // React hook
  | 'route' // API route
  | 'handler' // Request handler
  | 'middleware'
  | 'model'
  | 'schema'
  | 'migration'
  | 'test'
  | 'fixture';

/**
 * Reference to a documentation entity (document, section, chunk)
 */
export interface DocReference {
  id: string;

  // Location
  documentPath: string; // Path to document
  documentTitle: string; // Document title

  // Hierarchy
  sectionPath?: string[] | undefined; // Path of section headings
  sectionTitle?: string | undefined; // Current section title
  chunkIndex?: number | undefined; // Index within section

  // Content
  contentPreview?: string | undefined; // First ~200 chars
  contentType: DocContentType; // Type of content

  // Semantic
  embedding?: number[] | undefined; // Content embedding

  // Extracted references
  codeReferences?: string[] | undefined; // Code symbols mentioned
  itemReferences?: string[] | undefined; // Item IDs mentioned

  // Metadata
  lastSyncedAt?: string | undefined;
}

export type DocContentType =
  | 'heading'
  | 'paragraph'
  | 'code_block'
  | 'list'
  | 'table'
  | 'blockquote'
  | 'image'
  | 'link'
  | 'mixed';

// =============================================================================
// PERSPECTIVE CONFIGURATION
// =============================================================================

/**
 * Available perspective types
 * Perspectives represent WHO sees the data (stakeholder views)
 */
export type PerspectiveType =
  | 'product' // Product managers, UX designers
  | 'business' // Business analysts, stakeholders
  | 'technical' // Developers, architects
  | 'ui' // UI/UX designers, frontend devs
  | 'security' // Security engineers, auditors
  | 'performance' // Performance engineers
  | 'test' // QA engineers, testers
  | 'operations' // DevOps, SRE
  | 'data' // Data engineers, analysts
  | 'compliance' // Compliance officers
  | 'all' // All perspectives combined
  | string; // Custom perspectives

/**
 * Project-level perspective configuration
 * Allows customization of how perspectives are displayed and filtered
 */
export interface PerspectiveConfig {
  id: string;
  projectId: string;

  // Identity
  perspectiveType: PerspectiveType;
  name: string; // Display name
  description?: string | undefined;

  // Visual
  icon: string; // Icon name (Lucide icon)
  color: string; // Hex color
  order: number; // Display order

  // Filtering
  includeTypes: string[]; // Item types to include
  excludeTypes: string[]; // Item types to exclude
  includeViews: string[]; // Views to include
  excludeViews: string[]; // Views to exclude

  // Entity type mappings
  entityTypeMappings: EntityTypeMapping[];

  // Layout preferences
  layoutPreference: LayoutType;
  defaultExpansionLevel: number; // How deep to expand by default

  // Dimension defaults
  defaultDimensionFilters?: DimensionFilter[] | undefined;

  // Access control
  isDefault: boolean; // Is this a default perspective
  isCustom: boolean; // Is this a custom perspective
  createdBy?: string | undefined;

  // Timestamps
  createdAt: string;
  updatedAt: string;
}

/**
 * Maps entity types to perspectives
 */
export interface EntityTypeMapping {
  entityType: string; // The entity type
  displayName?: string | undefined; // Override display name
  icon?: string | undefined; // Override icon
  color?: string | undefined; // Override color
  isHidden?: boolean | undefined; // Hide in this perspective
}

/**
 * Layout types for graph visualization
 */
export type LayoutType =
  | 'cose' // Force-directed (Cytoscape)
  | 'breadthfirst' // Hierarchical top-down
  | 'circle' // Circular layout
  | 'grid' // Grid layout
  | 'elk' // ELK layered layout
  | 'dagre' // Directed graph layout
  | 'cola' // Constraint-based layout
  | 'concentric'; // Concentric circles

/**
 * Default perspective configurations
 */
export const DEFAULT_PERSPECTIVES: Omit<
  PerspectiveConfig,
  'id' | 'projectId' | 'createdAt' | 'updatedAt'
>[] = [
  {
    color: '#64748b',
    defaultExpansionLevel: 2,
    description: 'Complete traceability graph showing all items and relationships',
    entityTypeMappings: [],
    excludeTypes: [],
    excludeViews: [],
    icon: 'Network',
    includeTypes: [],
    includeViews: [],
    isCustom: false,
    isDefault: true,
    layoutPreference: 'cose',
    name: 'All Items',
    order: 0,
    perspectiveType: 'all',
  },
  {
    color: '#9333ea',
    defaultExpansionLevel: 3,
    description: 'User-facing features, journeys, and experiences',
    entityTypeMappings: [],
    excludeTypes: [],
    excludeViews: [],
    icon: 'Users',
    includeTypes: ['requirement', 'feature', 'user_story', 'story', 'journey', 'wireframe', 'page'],
    includeViews: ['FEATURE', 'feature', 'WIREFRAME', 'wireframe', 'journey'],
    isCustom: false,
    isDefault: true,
    layoutPreference: 'breadthfirst',
    name: 'Product View',
    order: 1,
    perspectiveType: 'product',
  },
  {
    color: '#3b82f6',
    defaultExpansionLevel: 3,
    description: 'Requirements, epics, stories, and project deliverables',
    entityTypeMappings: [],
    excludeTypes: [],
    excludeViews: [],
    icon: 'Briefcase',
    includeTypes: ['requirement', 'feature', 'epic', 'user_story', 'story', 'task', 'bug'],
    includeViews: ['FEATURE', 'feature'],
    isCustom: false,
    isDefault: true,
    layoutPreference: 'breadthfirst',
    name: 'Business View',
    order: 2,
    perspectiveType: 'business',
  },
  {
    color: '#22c55e',
    defaultExpansionLevel: 2,
    description: 'Architecture, APIs, databases, and code structure',
    entityTypeMappings: [],
    excludeTypes: [],
    excludeViews: [],
    icon: 'Code',
    includeTypes: [
      'api',
      'database',
      'code',
      'architecture',
      'infrastructure',
      'configuration',
      'dependency',
      'test',
    ],
    includeViews: ['CODE', 'code', 'API', 'api', 'DATABASE', 'database', 'architecture'],
    isCustom: false,
    isDefault: true,
    layoutPreference: 'elk',
    name: 'Technical View',
    order: 3,
    perspectiveType: 'technical',
  },
  {
    color: '#ec4899',
    defaultExpansionLevel: 4,
    description: 'Components, wireframes, and UI interactions',
    entityTypeMappings: [],
    excludeTypes: [],
    excludeViews: [],
    icon: 'Layout',
    includeTypes: [
      'wireframe',
      'ui_component',
      'page',
      'component',
      'layout',
      'section',
      'element',
    ],
    includeViews: ['WIREFRAME', 'wireframe'],
    isCustom: false,
    isDefault: true,
    layoutPreference: 'breadthfirst',
    name: 'UI View',
    order: 4,
    perspectiveType: 'ui',
  },
  {
    color: '#ef4444',
    defaultExpansionLevel: 2,
    description: 'Security requirements, audits, and vulnerabilities',
    entityTypeMappings: [],
    excludeTypes: [],
    excludeViews: [],
    icon: 'Shield',
    includeTypes: ['security', 'vulnerability', 'audit'],
    includeViews: ['security'],
    isCustom: false,
    isDefault: true,
    layoutPreference: 'cose',
    name: 'Security View',
    order: 5,
    perspectiveType: 'security',
  },
  {
    color: '#10b981',
    defaultExpansionLevel: 3,
    description: 'Test cases, suites, and coverage',
    entityTypeMappings: [],
    excludeTypes: [],
    excludeViews: [],
    icon: 'TestTube',
    includeTypes: ['test', 'test_case', 'test_suite', 'test_step', 'assertion'],
    includeViews: ['TEST', 'test'],
    isCustom: false,
    isDefault: true,
    layoutPreference: 'breadthfirst',
    name: 'Test View',
    order: 6,
    perspectiveType: 'test',
  },
];

// Import DimensionFilter from above (already defined in this file)
