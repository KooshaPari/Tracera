// Component Library and Design System Types
// Supports integration with Storybook, Figma, and design token systems

import type { CodeReference } from './canonical';
import type { DesignTokenType } from './ui-entities';

// =============================================================================
// COMPONENT LIBRARY
// =============================================================================

/**
 * A component library represents a design system or UI component collection
 * Can be synced from Storybook, Figma, or manually defined
 */
export interface ComponentLibrary {
  id: string;
  projectId: string;

  // Identity
  name: string; // e.g., "Acme Design System"
  slug: string; // URL-safe: "acme-design-system"
  description?: string;
  version: string; // Semantic version

  // Source
  source: ComponentLibrarySource;
  sourceUrl?: string; // Storybook URL, Figma file URL, etc.
  sourceConfig?: Record<string, unknown>;

  // Sync status
  lastSyncedAt?: string;
  syncStatus: 'synced' | 'syncing' | 'error' | 'never';
  syncError?: string;

  // Statistics
  componentCount: number;
  tokenCount: number;

  // Metadata
  tags?: string[];
  metadata?: Record<string, unknown>;

  // Timestamps
  createdAt: string;
  updatedAt: string;
}

export type ComponentLibrarySource =
  | 'storybook' // Synced from Storybook
  | 'figma' // Synced from Figma
  | 'manual' // Manually defined
  | 'chromatic' // Synced from Chromatic
  | 'zeroheight' // Synced from Zeroheight
  | 'supernova' // Synced from Supernova
  | 'custom'; // Custom integration

// =============================================================================
// LIBRARY COMPONENT
// =============================================================================

/**
 * A component within a component library
 */
export interface LibraryComponent {
  id: string;
  libraryId: string;
  projectId: string;

  // Identity
  name: string; // e.g., "Button"
  displayName: string; // e.g., "Primary Button"
  description?: string;

  // Classification
  category: ComponentCategory;
  subcategory?: string;
  tags?: string[];

  // Hierarchy
  parentId?: string; // For compound components
  childIds?: string[];

  // Code reference
  codeRef?: CodeReference;

  // Storybook integration
  storybookId?: string; // Storybook story ID
  storybookUrl?: string; // Direct link to story

  // Figma integration
  figmaNodeId?: string; // Figma node ID
  figmaUrl?: string; // Direct link to Figma

  // Props/API
  props?: ComponentProp[];
  slots?: ComponentSlot[];
  events?: ComponentEvent[];

  // Variants
  variants?: ComponentVariant[];

  // Visual
  thumbnailUrl?: string;
  previewUrl?: string;

  // Usage statistics
  usageCount: number; // How many times used in project
  usageLocations?: string[]; // Where it's used (item IDs)

  // Design tokens used
  tokenRefs?: string[]; // Token IDs used by this component

  // Status
  status: 'stable' | 'beta' | 'deprecated' | 'experimental';
  deprecationMessage?: string;

  // Timestamps
  createdAt: string;
  updatedAt: string;
}

/**
 * Component categories following atomic design
 */
export type ComponentCategory =
  | 'atom' // Basic building blocks (Button, Input, Icon)
  | 'molecule' // Simple combinations (SearchBar, FormField)
  | 'organism' // Complex combinations (Header, Card, Form)
  | 'template' // Page layouts
  | 'page' // Full page components
  | 'utility' // Utility components (Portal, ErrorBoundary)
  | 'layout' // Layout components (Grid, Stack, Container)
  | 'navigation' // Navigation components (Menu, Tabs, Breadcrumb)
  | 'feedback' // Feedback components (Alert, Toast, Progress)
  | 'overlay' // Overlay components (Modal, Drawer, Popover)
  | 'data-display' // Data display (Table, List, Tree)
  | 'data-entry' // Data entry (Form, Select, DatePicker)
  | 'other';

/**
 * Component prop definition
 */
export interface ComponentProp {
  name: string;
  type: string; // TypeScript type
  description?: string;
  required: boolean;
  defaultValue?: unknown;
  options?: unknown[]; // For enum/union types
}

/**
 * Component slot definition (for Vue/Web Components)
 */
export interface ComponentSlot {
  name: string;
  description?: string;
  required: boolean;
}

/**
 * Component event definition
 */
export interface ComponentEvent {
  name: string;
  description?: string;
  payload?: string; // TypeScript type of payload
}

/**
 * Component variant
 */
export interface ComponentVariant {
  name: string;
  description?: string;
  props: Record<string, unknown>;
  thumbnailUrl?: string;
}

// =============================================================================
// DESIGN TOKENS
// =============================================================================

/**
 * A design token from the design system
 */
export interface DesignToken {
  id: string;
  libraryId: string;
  projectId: string;

  // Identity
  name: string; // e.g., "colors.primary.500"
  path: string[]; // e.g., ["colors", "primary", "500"]
  description?: string;

  // Value
  type: DesignTokenType;
  value: string; // Raw value
  resolvedValue?: string; // Resolved value (if references other tokens)

  // References
  referencesTokenId?: string; // If this token references another
  referencedByIds?: string[]; // Tokens that reference this one

  // Figma integration
  figmaStyleId?: string;
  figmaVariableId?: string;

  // Usage
  usageCount: number;
  usedByComponentIds?: string[];

  // Metadata
  tags?: string[];
  metadata?: Record<string, unknown>;

  // Timestamps
  createdAt: string;
  updatedAt: string;
}

// =============================================================================
// COMPONENT USAGE TRACKING
// =============================================================================

/**
 * Tracks where a library component is used in the project
 */
export interface ComponentUsage {
  id: string;
  projectId: string;

  // What component
  libraryId: string;
  componentId: string;

  // Where it's used
  usedInItemId: string; // The UI item that uses this component
  usedInFilePath?: string; // File path where it's imported
  usedInLine?: number; // Line number

  // How it's used
  propsUsed?: Record<string, unknown>;
  variantUsed?: string;

  // Timestamps
  detectedAt: string;
}

// =============================================================================
// FIGMA SYNC STATE
// =============================================================================

/**
 * Tracks Figma sync state for a component library
 */
export interface FigmaSyncState {
  id: string;
  libraryId: string;
  projectId: string;

  // Figma file info
  figmaFileKey: string;
  figmaFileName: string;
  figmaFileUrl: string;

  // Sync status
  lastSyncedAt?: string;
  lastSyncVersion?: string;
  syncStatus: 'synced' | 'syncing' | 'error' | 'outdated';
  syncError?: string;

  // What was synced
  componentsSynced: number;
  tokensSynced: number;
  stylesSynced: number;

  // Timestamps
  createdAt: string;
  updatedAt: string;
}
