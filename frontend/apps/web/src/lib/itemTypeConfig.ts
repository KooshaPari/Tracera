/**
 * Type-Aware Node System - Configuration Registry
 *
 * Provides centralized configuration for item types including:
 * - Visual styling (icons, colors)
 * - Type metadata (labels, descriptions)
 * - View-specific behavior
 */

import type { ViewType } from '@tracertm/types';

// Icon mapping for each item type
export type ItemTypeIcon =
  | 'requirement'
  | 'test'
  | 'epic'
  | 'story'
  | 'task'
  | 'bug'
  | 'feature'
  | 'api'
  | 'database'
  | 'code'
  | 'wireframe'
  | 'document'
  | 'architecture'
  | 'security'
  | 'performance'
  | 'generic';

export interface ItemTypeConfig {
  type: string;
  label: string;
  description: string;
  icon: ItemTypeIcon;
  color: string;
  allowedViews: ViewType[];
  requiresSpec?: boolean; // Whether this type should have spec validation
  defaultPriority?: 'low' | 'medium' | 'high' | 'critical' | undefined;
}

/**
 * Centralized registry of item type configurations
 */
export const ITEM_TYPE_CONFIGS: Record<string, ItemTypeConfig> = {
  // Requirements & Specifications
  requirement: {
    type: 'requirement',
    label: 'Requirement',
    description: 'Functional or non-functional requirement',
    icon: 'requirement',
    color: '#9333ea', // purple-600
    allowedViews: ['FEATURE', 'feature', 'DOCUMENTATION', 'documentation'],
    requiresSpec: true,
    defaultPriority: 'high',
  },

  // Epics & Stories
  epic: {
    type: 'epic',
    label: 'Epic',
    description: 'Large body of work that can be broken down into stories',
    icon: 'epic',
    color: '#7c3aed', // violet-600
    allowedViews: ['FEATURE', 'feature'],
    defaultPriority: 'medium',
  },

  user_story: {
    type: 'user_story',
    label: 'User Story',
    description: 'User-focused feature description',
    icon: 'story',
    color: '#8b5cf6', // violet-500
    allowedViews: ['FEATURE', 'feature'],
    defaultPriority: 'medium',
  },

  story: {
    type: 'story',
    label: 'Story',
    description: 'User-focused feature description',
    icon: 'story',
    color: '#8b5cf6', // violet-500
    allowedViews: ['FEATURE', 'feature'],
    defaultPriority: 'medium',
  },

  // Tasks
  task: {
    type: 'task',
    label: 'Task',
    description: 'Actionable work item',
    icon: 'task',
    color: '#64748b', // slate-500
    allowedViews: ['FEATURE', 'feature', 'CODE', 'code'],
    defaultPriority: 'medium',
  },

  // Defects
  bug: {
    type: 'bug',
    label: 'Bug',
    description: 'Software defect or issue',
    icon: 'bug',
    color: '#ef4444', // red-500
    allowedViews: ['FEATURE', 'feature', 'TEST', 'test'],
    defaultPriority: 'high',
  },

  defect: {
    type: 'defect',
    label: 'Defect',
    description: 'Software defect or issue',
    icon: 'bug',
    color: '#ef4444', // red-500
    allowedViews: ['FEATURE', 'feature', 'TEST', 'test'],
    defaultPriority: 'high',
  },

  // Testing
  test: {
    type: 'test',
    label: 'Test',
    description: 'Test case or scenario',
    icon: 'test',
    color: '#22c55e', // green-500
    allowedViews: ['TEST', 'test'],
    defaultPriority: 'medium',
  },

  test_case: {
    type: 'test_case',
    label: 'Test Case',
    description: 'Detailed test case with steps',
    icon: 'test',
    color: '#16a34a', // green-600
    allowedViews: ['TEST', 'test'],
    defaultPriority: 'medium',
  },

  test_suite: {
    type: 'test_suite',
    label: 'Test Suite',
    description: 'Collection of test cases',
    icon: 'test',
    color: '#15803d', // green-700
    allowedViews: ['TEST', 'test'],
    defaultPriority: 'low',
  },

  // Features
  feature: {
    type: 'feature',
    label: 'Feature',
    description: 'Product feature or capability',
    icon: 'feature',
    color: '#a855f7', // purple-500
    allowedViews: ['FEATURE', 'feature'],
    defaultPriority: 'medium',
  },

  // Technical
  api: {
    type: 'api',
    label: 'API',
    description: 'API endpoint or interface',
    icon: 'api',
    color: '#f59e0b', // amber-500
    allowedViews: ['API', 'api', 'CODE', 'code'],
    defaultPriority: 'medium',
  },

  database: {
    type: 'database',
    label: 'Database',
    description: 'Database schema or entity',
    icon: 'database',
    color: '#8b5cf6', // violet-500
    allowedViews: ['DATABASE', 'database', 'architecture'],
    defaultPriority: 'medium',
  },

  code: {
    type: 'code',
    label: 'Code',
    description: 'Code component or module',
    icon: 'code',
    color: '#3b82f6', // blue-500
    allowedViews: ['CODE', 'code'],
    defaultPriority: 'low',
  },

  architecture: {
    type: 'architecture',
    label: 'Architecture',
    description: 'Architectural component or decision',
    icon: 'architecture',
    color: '#6366f1', // indigo-500
    allowedViews: ['architecture', 'DOCUMENTATION', 'documentation'],
    defaultPriority: 'high',
  },

  infrastructure: {
    type: 'infrastructure',
    label: 'Infrastructure',
    description: 'Infrastructure component',
    icon: 'architecture',
    color: '#06b6d4', // cyan-500
    allowedViews: ['infrastructure', 'DEPLOYMENT', 'deployment'],
    defaultPriority: 'medium',
  },

  configuration: {
    type: 'configuration',
    label: 'Configuration',
    description: 'Configuration item',
    icon: 'generic',
    color: '#64748b', // slate-500
    allowedViews: ['configuration', 'DEPLOYMENT', 'deployment'],
    defaultPriority: 'low',
  },

  // UI/UX
  wireframe: {
    type: 'wireframe',
    label: 'Wireframe',
    description: 'UI wireframe or mockup',
    icon: 'wireframe',
    color: '#ec4899', // pink-500
    allowedViews: ['WIREFRAME', 'wireframe'],
    defaultPriority: 'medium',
  },

  ui_component: {
    type: 'ui_component',
    label: 'UI Component',
    description: 'User interface component',
    icon: 'wireframe',
    color: '#f472b6', // pink-400
    allowedViews: ['WIREFRAME', 'wireframe', 'CODE', 'code'],
    defaultPriority: 'medium',
  },

  page: {
    type: 'page',
    label: 'Page',
    description: 'Application page or view',
    icon: 'wireframe',
    color: '#db2777', // pink-600
    allowedViews: ['WIREFRAME', 'wireframe'],
    defaultPriority: 'medium',
  },

  component: {
    type: 'component',
    label: 'Component',
    description: 'Reusable component',
    icon: 'wireframe',
    color: '#f472b6', // pink-400
    allowedViews: ['WIREFRAME', 'wireframe', 'CODE', 'code'],
    defaultPriority: 'low',
  },

  // Security & Performance
  security: {
    type: 'security',
    label: 'Security',
    description: 'Security requirement or control',
    icon: 'security',
    color: '#ef4444', // red-500
    allowedViews: ['security', 'DOCUMENTATION', 'documentation'],
    defaultPriority: 'critical',
  },

  vulnerability: {
    type: 'vulnerability',
    label: 'Vulnerability',
    description: 'Security vulnerability',
    icon: 'security',
    color: '#dc2626', // red-600
    allowedViews: ['security'],
    defaultPriority: 'critical',
  },

  performance: {
    type: 'performance',
    label: 'Performance',
    description: 'Performance requirement or metric',
    icon: 'performance',
    color: '#10b981', // emerald-500
    allowedViews: ['performance', 'monitoring'],
    defaultPriority: 'medium',
  },

  monitoring: {
    type: 'monitoring',
    label: 'Monitoring',
    description: 'Monitoring or observability item',
    icon: 'performance',
    color: '#14b8a6', // teal-500
    allowedViews: ['monitoring'],
    defaultPriority: 'medium',
  },

  // Documentation
  document: {
    type: 'document',
    label: 'Document',
    description: 'Documentation item',
    icon: 'document',
    color: '#6b7280', // gray-500
    allowedViews: ['DOCUMENTATION', 'documentation'],
    defaultPriority: 'low',
  },

  // Domain modeling
  domain: {
    type: 'domain',
    label: 'Domain',
    description: 'Domain model or entity',
    icon: 'generic',
    color: '#a855f7', // purple-500
    allowedViews: ['domain', 'architecture'],
    defaultPriority: 'medium',
  },

  dependency: {
    type: 'dependency',
    label: 'Dependency',
    description: 'External dependency',
    icon: 'generic',
    color: '#84cc16', // lime-500
    allowedViews: ['dependency', 'CODE', 'code'],
    defaultPriority: 'low',
  },

  journey: {
    type: 'journey',
    label: 'Journey',
    description: 'User journey or flow',
    icon: 'generic',
    color: '#f97316', // orange-500
    allowedViews: ['journey', 'WIREFRAME', 'wireframe'],
    defaultPriority: 'medium',
  },

  // Generic fallback
  generic: {
    type: 'generic',
    label: 'Item',
    description: 'Generic item',
    icon: 'generic',
    color: '#6b7280', // gray-500
    allowedViews: [],
    defaultPriority: 'medium',
  },
};

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get configuration for a specific item type
 * Falls back to generic config if type not found
 */
export function getItemTypeConfig(type: string): ItemTypeConfig {
  return ITEM_TYPE_CONFIGS[type] ?? ITEM_TYPE_CONFIGS['generic']!;
}

/**
 * Get all item types that are valid for a specific view
 */
export function getItemTypesForView(view: ViewType): ItemTypeConfig[] {
  return Object.values(ITEM_TYPE_CONFIGS).filter((config) => config.allowedViews.includes(view));
}

/**
 * Check if an item type is valid for a specific view
 */
export function isTypeValidForView(type: string, view: ViewType): boolean {
  const config = getItemTypeConfig(type);
  return config.allowedViews.length === 0 || config.allowedViews.includes(view);
}

/**
 * Get the icon for an item type
 */
export function getItemTypeIcon(type: string): ItemTypeIcon {
  return getItemTypeConfig(type).icon;
}

/**
 * Get the color for an item type
 */
export function getItemTypeColor(type: string): string {
  return getItemTypeConfig(type).color;
}

/**
 * Get the label for an item type
 */
export function getItemTypeLabel(type: string): string {
  return getItemTypeConfig(type).label;
}
