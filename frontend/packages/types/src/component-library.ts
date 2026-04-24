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
  name: string; // E.g., "Acme Design System"
  slug: string; // URL-safe: "acme-design-system"
  description?: string | undefined;
  version: string; // Semantic version

  // Source
  source: ComponentLibrarySource;
  sourceUrl?: string | undefined; // Storybook URL, Figma file URL, etc.
  sourceConfig?: Record<string, unknown> | undefined;

  // Sync status
  lastSyncedAt?: string | undefined;
  syncStatus: 'synced' | 'syncing' | 'error' | 'never';
  syncError?: string | undefined;

  // Statistics
  componentCount: number;
  tokenCount: number;

  // Metadata
  tags?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;

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
  name: string; // E.g., "Button"
  displayName: string; // E.g., "Primary Button"
  description?: string | undefined;

  // Classification
  category: ComponentCategory;
  subcategory?: string | undefined;
  tags?: string[] | undefined;

  // Hierarchy
  parentId?: string | undefined; // For compound components
  childIds?: string[] | undefined;

  // Code reference
  codeRef?: CodeReference | undefined;

  // Storybook integration
  storybookId?: string | undefined; // Storybook story ID
  storybookUrl?: string | undefined; // Direct link to story

  // Figma integration
  figmaNodeId?: string | undefined; // Figma node ID
  figmaUrl?: string | undefined; // Direct link to Figma

  // Props/API
  props?: ComponentProp[] | undefined;
  slots?: ComponentSlot[] | undefined;
  events?: ComponentEvent[] | undefined;

  // Variants
  variants?: ComponentVariant[] | undefined;

  // Visual
  thumbnailUrl?: string | undefined;
  previewUrl?: string | undefined;

  // Usage statistics
  usageCount: number; // How many times used in project
  usageLocations?: string[] | undefined; // Where it's used (item IDs)

  // Design tokens used
  tokenRefs?: string[] | undefined; // Token IDs used by this component

  // Status
  status: 'stable' | 'beta' | 'deprecated' | 'experimental';
  deprecationMessage?: string | undefined;

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
  description?: string | undefined;
  required: boolean;
  defaultValue?: unknown | undefined;
  options?: unknown[] | undefined; // For enum/union types
}

/**
 * Component slot definition (for Vue/Web Components)
 */
export interface ComponentSlot {
  name: string;
  description?: string | undefined;
  required: boolean;
}

/**
 * Component event definition
 */
export interface ComponentEvent {
  name: string;
  description?: string | undefined;
  payload?: string | undefined; // TypeScript type of payload
}

/**
 * Component variant
 */
export interface ComponentVariant {
  name: string;
  description?: string | undefined;
  props: Record<string, unknown>;
  thumbnailUrl?: string | undefined;
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
  name: string; // E.g., "colors.primary.500"
  path: string[]; // E.g., ["colors", "primary", "500"]
  description?: string | undefined;

  // Value
  type: DesignTokenType;
  value: string; // Raw value
  resolvedValue?: string | undefined; // Resolved value (if references other tokens)

  // References
  referencesTokenId?: string | undefined; // If this token references another
  referencedByIds?: string[] | undefined; // Tokens that reference this one

  // Figma integration
  figmaStyleId?: string | undefined;
  figmaVariableId?: string | undefined;

  // Usage
  usageCount: number;
  usedByComponentIds?: string[] | undefined;

  // Metadata
  tags?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;

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
  usedInFilePath?: string | undefined; // File path where it's imported
  usedInLine?: number | undefined; // Line number

  // How it's used
  propsUsed?: Record<string, unknown> | undefined;
  variantUsed?: string | undefined;

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
  lastSyncedAt?: string | undefined;
  lastSyncVersion?: string | undefined;
  syncStatus: 'synced' | 'syncing' | 'error' | 'outdated';
  syncError?: string | undefined;

  // What was synced
  componentsSynced: number;
  tokensSynced: number;
  stylesSynced: number;

  // Timestamps
  createdAt: string;
  updatedAt: string;
}
