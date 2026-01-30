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
  | "explicit_annotation"   // @trace-implements, @canonical - confidence: 1.0
  | "manual_link"           // User-created link - confidence: 1.0
  | "api_contract"          // Frontend fetch → backend route - confidence: 0.9
  | "shared_canonical"      // Same canonical concept - confidence: 0.9
  | "naming_pattern"        // CamelCase/snake_case matching - confidence: 0.7
  | "semantic_similarity"   // Embedding cosine similarity - confidence: 0.6
  | "structural"            // Similar structure/hierarchy - confidence: 0.5
  | "temporal"              // Created/modified together - confidence: 0.4
  | "co_occurrence";        // Frequently appear together - confidence: 0.3

/**
 * Default confidence scores for each strategy
 */
export const STRATEGY_CONFIDENCE: Record<EquivalenceStrategy, number> = {
  explicit_annotation: 1.0,
  manual_link: 1.0,
  api_contract: 0.9,
  shared_canonical: 0.9,
  naming_pattern: 0.7,
  semantic_similarity: 0.6,
  structural: 0.5,
  temporal: 0.4,
  co_occurrence: 0.3,
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
  name: string;                    // Human-readable name: "User Authentication"
  slug: string;                    // URL-safe identifier: "user-authentication"
  description?: string;            // Detailed description
  
  // Classification
  domain: string;                  // Business domain: "security", "payments", "users"
  category?: string;               // Sub-category within domain
  tags?: string[];                 // Additional classification tags
  
  // Semantic Embedding
  embedding?: number[];            // Vector embedding for similarity search
  embeddingModel?: string;         // Model used: "text-embedding-3-small"
  embeddingUpdatedAt?: string;     // When embedding was last computed
  
  // Projections (items that represent this concept in different views)
  projectionCount: number;         // Number of linked items
  projectionIds?: string[];        // IDs of linked items (lazy loaded)
  
  // Relationships to other canonical concepts
  relatedConceptIds?: string[];    // Related concepts
  parentConceptId?: string;        // Hierarchical parent
  childConceptIds?: string[];      // Hierarchical children
  
  // Metadata
  confidence: number;              // 0-1, how confident we are this is a valid concept
  source: "manual" | "inferred" | "imported";
  createdBy?: string;
  
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
  canonicalId: string;             // The canonical concept
  itemId: string;                  // The item that manifests this concept
  projectId: string;
  
  // Perspective context
  perspective: string;             // Which perspective this projection belongs to
  
  // Confidence and provenance
  confidence: number;              // 0-1, how confident is this mapping
  strategy: EquivalenceStrategy;   // How was this detected
  
  // Manual override
  isConfirmed: boolean;            // User confirmed this mapping
  isRejected: boolean;             // User rejected this mapping
  confirmedBy?: string;
  confirmedAt?: string;
  
  // Metadata
  metadata?: Record<string, unknown>;
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
  confidence: number;              // Aggregated confidence from all strategies
  
  // Detection provenance
  strategies: EquivalenceEvidence[];
  
  // Canonical concept (if both items share one)
  canonicalId?: string;
  
  // User actions
  status: "suggested" | "confirmed" | "rejected" | "auto_confirmed";
  confirmedBy?: string;
  confirmedAt?: string;
  rejectedReason?: string;
  
  // Timestamps
  createdAt: string;
  updatedAt: string;
}

/**
 * Types of equivalence relationships
 */
export type EquivalenceLinkType =
  | "same_as"           // Exact same concept in different views
  | "represents"        // One item represents another (code implements requirement)
  | "manifests_as"      // Abstract concept manifests as concrete item
  | "derived_from"      // One item derived from another
  | "alternative_to";   // Alternative implementation/approach

/**
 * Evidence for an equivalence detection
 */
export interface EquivalenceEvidence {
  strategy: EquivalenceStrategy;
  confidence: number;
  details: string;                 // Human-readable explanation
  detectedAt: string;
  metadata?: Record<string, unknown>;
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
  | "idea"              // Just an idea, not fleshed out
  | "draft"             // Initial draft, incomplete
  | "defined"           // Well-defined but not implemented
  | "implemented"       // Implemented but not verified
  | "verified"          // Verified/tested
  | "stable"            // Stable, in production
  | "deprecated";       // Marked for removal

/**
 * Complexity dimension - how complex is this item
 */
export type ComplexityLevel =
  | "trivial"           // Very simple, obvious
  | "simple"            // Simple, straightforward
  | "moderate"          // Some complexity
  | "complex"           // Significant complexity
  | "very_complex";     // High complexity, needs decomposition

/**
 * Coverage dimension - how well is this item covered by tests/docs
 */
export interface CoverageMetrics {
  testCoverage: number;            // 0-100, percentage of test coverage
  docCoverage: number;             // 0-100, percentage of documentation coverage
  traceCoverage: number;           // 0-100, percentage of traceability links
  overallCoverage: number;         // Weighted average
}

/**
 * Risk dimension - risk level of this item
 */
export type RiskLevel =
  | "none"
  | "low"
  | "medium"
  | "high"
  | "critical";

/**
 * All dimensions for an item
 */
export interface ItemDimensions {
  maturity?: MaturityLevel;
  complexity?: ComplexityLevel;
  coverage?: CoverageMetrics;
  risk?: RiskLevel;

  // Custom dimensions (project-specific)
  custom?: Record<string, string | number | boolean>;
}

/**
 * Dimension filter configuration for UI
 */
export interface DimensionFilter {
  dimension: keyof ItemDimensions | string;
  operator: "eq" | "neq" | "gt" | "gte" | "lt" | "lte" | "in" | "not_in";
  value: string | number | boolean | string[] | number[];
}

/**
 * Dimension display mode in the graph
 */
export type DimensionDisplayMode =
  | "filter"            // Hide items that don't match
  | "highlight"         // Highlight matching items, dim others
  | "color"             // Color-code by dimension value
  | "size";             // Size nodes by dimension value

// =============================================================================
// CODE & DOCUMENTATION REFERENCES
// =============================================================================

/**
 * Reference to a code entity (function, class, file, etc.)
 */
export interface CodeReference {
  id: string;

  // Location
  repositoryUrl?: string;          // GitHub/GitLab URL
  filePath: string;                // Path within repo
  startLine?: number;              // Start line number
  endLine?: number;                // End line number

  // Symbol information
  symbolName: string;              // Function/class/variable name
  symbolType: CodeSymbolType;      // Type of symbol
  language: string;                // Programming language

  // AST information
  signature?: string;              // Function signature
  parentSymbol?: string;           // Parent class/module

  // Semantic
  embedding?: number[];            // Code embedding for similarity

  // Metadata
  lastSyncedAt?: string;
  commitSha?: string;
}

export type CodeSymbolType =
  | "file"
  | "module"
  | "class"
  | "interface"
  | "function"
  | "method"
  | "variable"
  | "constant"
  | "type"
  | "enum"
  | "component"                    // React/Vue component
  | "hook"                         // React hook
  | "route"                        // API route
  | "handler"                      // Request handler
  | "middleware"
  | "model"
  | "schema"
  | "migration"
  | "test"
  | "fixture";

/**
 * Reference to a documentation entity (document, section, chunk)
 */
export interface DocReference {
  id: string;

  // Location
  documentPath: string;            // Path to document
  documentTitle: string;           // Document title

  // Hierarchy
  sectionPath?: string[];          // Path of section headings
  sectionTitle?: string;           // Current section title
  chunkIndex?: number;             // Index within section

  // Content
  contentPreview?: string;         // First ~200 chars
  contentType: DocContentType;     // Type of content

  // Semantic
  embedding?: number[];            // Content embedding

  // Extracted references
  codeReferences?: string[];       // Code symbols mentioned
  itemReferences?: string[];       // Item IDs mentioned

  // Metadata
  lastSyncedAt?: string;
}

export type DocContentType =
  | "heading"
  | "paragraph"
  | "code_block"
  | "list"
  | "table"
  | "blockquote"
  | "image"
  | "link"
  | "mixed";

// =============================================================================
// PERSPECTIVE CONFIGURATION
// =============================================================================

/**
 * Available perspective types
 * Perspectives represent WHO sees the data (stakeholder views)
 */
export type PerspectiveType =
  | "product"       // Product managers, UX designers
  | "business"      // Business analysts, stakeholders
  | "technical"     // Developers, architects
  | "ui"            // UI/UX designers, frontend devs
  | "security"      // Security engineers, auditors
  | "performance"   // Performance engineers
  | "test"          // QA engineers, testers
  | "operations"    // DevOps, SRE
  | "data"          // Data engineers, analysts
  | "compliance"    // Compliance officers
  | "all"           // All perspectives combined
  | string;         // Custom perspectives

/**
 * Project-level perspective configuration
 * Allows customization of how perspectives are displayed and filtered
 */
export interface PerspectiveConfig {
  id: string;
  projectId: string;

  // Identity
  perspectiveType: PerspectiveType;
  name: string;                    // Display name
  description?: string;

  // Visual
  icon: string;                    // Icon name (Lucide icon)
  color: string;                   // Hex color
  order: number;                   // Display order

  // Filtering
  includeTypes: string[];          // Item types to include
  excludeTypes: string[];          // Item types to exclude
  includeViews: string[];          // Views to include
  excludeViews: string[];          // Views to exclude

  // Entity type mappings
  entityTypeMappings: EntityTypeMapping[];

  // Layout preferences
  layoutPreference: LayoutType;
  defaultExpansionLevel: number;   // How deep to expand by default

  // Dimension defaults
  defaultDimensionFilters?: DimensionFilter[];

  // Access control
  isDefault: boolean;              // Is this a default perspective
  isCustom: boolean;               // Is this a custom perspective
  createdBy?: string;

  // Timestamps
  createdAt: string;
  updatedAt: string;
}

/**
 * Maps entity types to perspectives
 */
export interface EntityTypeMapping {
  entityType: string;              // The entity type
  displayName?: string;            // Override display name
  icon?: string;                   // Override icon
  color?: string;                  // Override color
  isHidden?: boolean;              // Hide in this perspective
}

/**
 * Layout types for graph visualization
 */
export type LayoutType =
  | "cose"           // Force-directed (Cytoscape)
  | "breadthfirst"   // Hierarchical top-down
  | "circle"         // Circular layout
  | "grid"           // Grid layout
  | "elk"            // ELK layered layout
  | "dagre"          // Directed graph layout
  | "cola"           // Constraint-based layout
  | "concentric";    // Concentric circles

/**
 * Default perspective configurations
 */
export const DEFAULT_PERSPECTIVES: Omit<PerspectiveConfig, "id" | "projectId" | "createdAt" | "updatedAt">[] = [
  {
    perspectiveType: "all",
    name: "All Items",
    description: "Complete traceability graph showing all items and relationships",
    icon: "Network",
    color: "#64748b",
    order: 0,
    includeTypes: [],
    excludeTypes: [],
    includeViews: [],
    excludeViews: [],
    entityTypeMappings: [],
    layoutPreference: "cose",
    defaultExpansionLevel: 2,
    isDefault: true,
    isCustom: false,
  },
  {
    perspectiveType: "product",
    name: "Product View",
    description: "User-facing features, journeys, and experiences",
    icon: "Users",
    color: "#9333ea",
    order: 1,
    includeTypes: ["requirement", "feature", "user_story", "story", "journey", "wireframe", "page"],
    excludeTypes: [],
    includeViews: ["FEATURE", "feature", "WIREFRAME", "wireframe", "journey"],
    excludeViews: [],
    entityTypeMappings: [],
    layoutPreference: "breadthfirst",
    defaultExpansionLevel: 3,
    isDefault: true,
    isCustom: false,
  },
  {
    perspectiveType: "business",
    name: "Business View",
    description: "Requirements, epics, stories, and project deliverables",
    icon: "Briefcase",
    color: "#3b82f6",
    order: 2,
    includeTypes: ["requirement", "feature", "epic", "user_story", "story", "task", "bug"],
    excludeTypes: [],
    includeViews: ["FEATURE", "feature"],
    excludeViews: [],
    entityTypeMappings: [],
    layoutPreference: "breadthfirst",
    defaultExpansionLevel: 3,
    isDefault: true,
    isCustom: false,
  },
  {
    perspectiveType: "technical",
    name: "Technical View",
    description: "Architecture, APIs, databases, and code structure",
    icon: "Code",
    color: "#22c55e",
    order: 3,
    includeTypes: ["api", "database", "code", "architecture", "infrastructure", "configuration", "dependency", "test"],
    excludeTypes: [],
    includeViews: ["CODE", "code", "API", "api", "DATABASE", "database", "architecture"],
    excludeViews: [],
    entityTypeMappings: [],
    layoutPreference: "elk",
    defaultExpansionLevel: 2,
    isDefault: true,
    isCustom: false,
  },
  {
    perspectiveType: "ui",
    name: "UI View",
    description: "Components, wireframes, and UI interactions",
    icon: "Layout",
    color: "#ec4899",
    order: 4,
    includeTypes: ["wireframe", "ui_component", "page", "component", "layout", "section", "element"],
    excludeTypes: [],
    includeViews: ["WIREFRAME", "wireframe"],
    excludeViews: [],
    entityTypeMappings: [],
    layoutPreference: "breadthfirst",
    defaultExpansionLevel: 4,
    isDefault: true,
    isCustom: false,
  },
  {
    perspectiveType: "security",
    name: "Security View",
    description: "Security requirements, audits, and vulnerabilities",
    icon: "Shield",
    color: "#ef4444",
    order: 5,
    includeTypes: ["security", "vulnerability", "audit"],
    excludeTypes: [],
    includeViews: ["security"],
    excludeViews: [],
    entityTypeMappings: [],
    layoutPreference: "cose",
    defaultExpansionLevel: 2,
    isDefault: true,
    isCustom: false,
  },
  {
    perspectiveType: "test",
    name: "Test View",
    description: "Test cases, suites, and coverage",
    icon: "TestTube",
    color: "#10b981",
    order: 6,
    includeTypes: ["test", "test_case", "test_suite", "test_step", "assertion"],
    excludeTypes: [],
    includeViews: ["TEST", "test"],
    excludeViews: [],
    entityTypeMappings: [],
    layoutPreference: "breadthfirst",
    defaultExpansionLevel: 3,
    isDefault: true,
    isCustom: false,
  },
];

// Import DimensionFilter from above (already defined in this file)
