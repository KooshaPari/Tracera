// Type-based styling utilities for graph nodes
// Maps entity types to icons and colors

import type { LucideIcon } from 'lucide-react';

import {
  Box,
  Boxes,
  Bug,
  Check,
  CheckSquare,
  Circle,
  CircleDot,
  Code,
  Cog,
  Component,
  Database,
  File,
  FileCode,
  FileText,
  FolderTree,
  GitBranch,
  Globe,
  Grid,
  Hash,
  Image,
  Layers,
  Layout,
  LayoutGrid,
  Link2,
  List,
  ListChecks,
  Loader,
  Maximize,
  MessageSquare,
  Monitor,
  Palette,
  PanelBottom,
  PanelLeft,
  Play,
  Puzzle,
  Server,
  Settings,
  Shapes,
  Square,
  Star,
  Target,
  TestTube,
  Type,
  User,
  Workflow,
  Zap,
} from 'lucide-react';

const DEFAULT_TYPE = 'default';

// ============================================================================
// TYPE TO ICON MAPPING
// ============================================================================

const TYPE_ICONS = new Map<string, LucideIcon>([
  // UI Entity Types
  ['component', Component],
  ['drawer', PanelLeft],
  ['element', Square],
  ['layout', Layout],
  ['modal', Maximize],
  ['page', FileText],
  ['popup', MessageSquare],
  ['section', Grid],
  ['site', Globe],
  ['subcomponent', Puzzle],
  ['subsection', LayoutGrid],
  ['toast', PanelBottom],

  // Product Entity Types
  ['acceptance_criteria', Check],
  ['epic', Layers],
  ['feature', Zap],
  ['initiative', Star],
  ['requirement', Target],
  ['story', User],
  ['subtask', List],
  ['task', CheckSquare],
  ['user_story', User],

  // Technical Entity Types
  ['api', Link2],
  ['api_endpoint', Link2],
  ['class', Boxes],
  ['code', FileCode],
  ['config', Settings],
  ['database_field', Hash],
  ['database_table', Database],
  ['function', Code],
  ['module', FolderTree],
  ['service', Server],

  // Test Entity Types
  ['assertion', CircleDot],
  ['fixture', Box],
  ['mock', Circle],
  ['test', TestTube],
  ['test_case', TestTube],
  ['test_step', Play],
  ['test_suite', ListChecks],

  // Design Entity Types
  ['design', Image],
  ['design_token', Palette],
  ['mockup', Image],
  ['prototype', Monitor],
  ['style_guide', Type],
  ['ui', Monitor],
  ['wireframe', Shapes],

  // Documentation Types
  ['doc_block', Grid],
  ['doc_page', FileText],
  ['doc_root', FileText],
  ['doc_section', File],
  ['documentation', FileText],

  // Other common types
  ['bug', Bug],
  ['database', Database],
  ['default', Cog],
  ['deployment', Server],
  ['integration', Link2],
  ['issue', Bug],
  ['loading', Loader],
  ['process', GitBranch],
  ['workflow', Workflow],
]);

// ============================================================================
// TYPE TO COLOR MAPPING
// ============================================================================

const TYPE_COLORS = new Map<string, string>([
  // UI Entity Types - Blue spectrum
  ['component', '#6366f1'], // Indigo-500
  ['drawer', '#4f46e5'], // Indigo-600
  ['element', '#a5b4fc'], // Indigo-300
  ['layout', '#2563eb'], // Blue-600
  ['modal', '#4f46e5'], // Indigo-600
  ['page', '#60a5fa'], // Blue-400
  ['popup', '#6366f1'], // Indigo-500
  ['section', '#3b82f6'], // Blue-500
  ['site', '#3b82f6'], // Blue-500
  ['subcomponent', '#818cf8'], // Indigo-400
  ['subsection', '#60a5fa'], // Blue-400
  ['toast', '#818cf8'], // Indigo-400

  // Product Entity Types - Purple spectrum
  ['acceptance_criteria', '#e879f9'], // Fuchsia-400
  ['epic', '#8b5cf6'], // Violet-500
  ['feature', '#a78bfa'], // Violet-400
  ['initiative', '#7c3aed'], // Violet-600
  ['requirement', '#a855f7'], // Purple-500
  ['story', '#c4b5fd'], // Violet-300
  ['subtask', '#f0abfc'], // Fuchsia-300
  ['task', '#d946ef'], // Fuchsia-500
  ['user_story', '#c4b5fd'], // Violet-300

  // Technical Entity Types - Green spectrum
  ['api', '#2dd4bf'], // Teal-400
  ['api_endpoint', '#2dd4bf'], // Teal-400
  ['class', '#059669'], // Emerald-600
  ['code', '#4ade80'], // Green-400
  ['config', '#22c55e'], // Green-500
  ['database_field', '#0d9488'], // Teal-600
  ['database_table', '#0d9488'], // Teal-600
  ['function', '#14b8a6'], // Teal-500
  ['module', '#34d399'], // Emerald-400
  ['service', '#10b981'], // Emerald-500

  // Test Entity Types - Orange spectrum
  ['assertion', '#fed7aa'], // Orange-200
  ['fixture', '#ea580c'], // Orange-600
  ['mock', '#dc2626'], // Red-600
  ['test', '#fb923c'], // Orange-400
  ['test_case', '#fb923c'], // Orange-400
  ['test_step', '#fdba74'], // Orange-300
  ['test_suite', '#f97316'], // Orange-500

  // Design Entity Types - Pink spectrum
  ['design', '#ec4899'], // Pink-500
  ['design_token', '#be185d'], // Pink-700
  ['mockup', '#f472b6'], // Pink-400
  ['prototype', '#f9a8d4'], // Pink-300
  ['style_guide', '#db2777'], // Pink-600
  ['ui', '#f472b6'], // Pink-400
  ['wireframe', '#ec4899'], // Pink-500

  // Documentation Types - Yellow spectrum
  ['doc_block', '#fef08a'], // Yellow-200
  ['doc_page', '#fde047'], // Yellow-300
  ['doc_root', '#eab308'], // Yellow-500
  ['doc_section', '#facc15'], // Yellow-400
  ['documentation', '#eab308'], // Yellow-500

  // Other common types
  ['bug', '#ef4444'], // Red-500
  ['database', '#0d9488'], // Teal-600
  ['default', '#64748b'], // Slate-500
  ['deployment', '#0284c7'], // Sky-600
  ['drawer', '#4f46e5'], // Indigo-600
  ['integration', '#7dd3fc'], // Sky-300
  ['issue', '#f87171'], // Red-400
  ['process', '#38bdf8'], // Sky-400
  ['workflow', '#0ea5e9'], // Sky-500
]);

// ============================================================================
// CATEGORY COLORS
// ============================================================================

export const CATEGORY_COLORS = new Map<string, string>([
  ['default', '#64748b'], // Slate-500
  ['design', '#ec4899'], // Pink-500
  ['documentation', '#eab308'], // Yellow-500
  ['product', '#8b5cf6'], // Violet-500
  ['technical', '#10b981'], // Emerald-500
  ['test', '#f97316'], // Orange-500
  ['ui', '#3b82f6'], // Blue-500
]);

const CATEGORY_TYPES = {
  design: new Set(['design', 'design_token', 'mockup', 'prototype', 'style_guide', 'wireframe']),
  documentation: new Set(['doc_block', 'doc_page', 'doc_root', 'doc_section', 'documentation']),
  product: new Set([
    'acceptance_criteria',
    'epic',
    'feature',
    'initiative',
    'requirement',
    'story',
    'subtask',
    'task',
    'user_story',
  ]),
  technical: new Set([
    'api',
    'api_endpoint',
    'class',
    'code',
    'config',
    'database',
    'database_field',
    'database_table',
    'deployment',
    'function',
    'integration',
    'module',
    'process',
    'service',
    'workflow',
  ]),
  test: new Set(['assertion', 'fixture', 'mock', 'test', 'test_case', 'test_step', 'test_suite']),
  ui: new Set([
    'component',
    'drawer',
    'element',
    'layout',
    'mockup',
    'modal',
    'page',
    'popup',
    'section',
    'site',
    'subcomponent',
    'subsection',
    'toast',
    'ui',
    'wireframe',
  ]),
} as const;

const normalizeType = (type: string): string => type.toLowerCase().replaceAll(/[_-]/g, '_');

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get icon component for an entity type
 */
export const getTypeIcon = (type: string): LucideIcon => {
  const normalizedType = normalizeType(type);
  return TYPE_ICONS.get(normalizedType) ?? TYPE_ICONS.get(DEFAULT_TYPE)!;
};

/**
 * Get color for an entity type
 */
export const getTypeColor = (type: string): string => {
  const normalizedType = normalizeType(type);
  return TYPE_COLORS.get(normalizedType) ?? TYPE_COLORS.get(DEFAULT_TYPE)!;
};

/**
 * Get category for an entity type
 */
export const getTypeCategory = (
  type: string,
): 'ui' | 'product' | 'technical' | 'test' | 'design' | 'documentation' | 'default' => {
  const normalizedType = normalizeType(type);

  if (CATEGORY_TYPES.ui.has(normalizedType)) {
    return 'ui';
  }
  if (CATEGORY_TYPES.product.has(normalizedType)) {
    return 'product';
  }
  if (CATEGORY_TYPES.technical.has(normalizedType)) {
    return 'technical';
  }
  if (CATEGORY_TYPES.test.has(normalizedType)) {
    return 'test';
  }
  if (CATEGORY_TYPES.design.has(normalizedType)) {
    return 'design';
  }
  if (CATEGORY_TYPES.documentation.has(normalizedType)) {
    return 'documentation';
  }

  return 'default';
};

/**
 * Get category color
 */
export const getCategoryColor = (
  category: 'ui' | 'product' | 'technical' | 'test' | 'design' | 'documentation' | 'default',
): string => CATEGORY_COLORS.get(category) ?? CATEGORY_COLORS.get('default')!;

const STATUS_COLOR_MAP = new Map<string, string>([
  ['active', '#3b82f6'], // Blue-500
  ['approved', '#22c55e'], // Green-500
  ['archived', '#6b7280'], // Gray-500
  ['blocked', '#ef4444'], // Red-500
  ['cancelled', '#6b7280'], // Gray-500
  ['complete', '#22c55e'], // Green-500
  ['completed', '#22c55e'], // Green-500
  ['done', '#22c55e'], // Green-500
  ['draft', '#94a3b8'], // Slate-400
  ['error', '#ef4444'], // Red-500
  ['failed', '#ef4444'], // Red-500
  ['in_progress', '#3b82f6'], // Blue-500
  ['pending', '#94a3b8'], // Slate-400
  ['running', '#3b82f6'], // Blue-500
  ['todo', '#94a3b8'], // Slate-400
]);

const PRIORITY_COLOR_MAP = new Map<string, string>([
  ['critical', '#ef4444'], // Red-500
  ['high', '#f97316'], // Orange-500
  ['highest', '#ef4444'], // Red-500
  ['low', '#22c55e'], // Green-500
  ['lowest', '#3b82f6'], // Blue-500
  ['medium', '#eab308'], // Yellow-500
  ['normal', '#eab308'], // Yellow-500
  ['p0', '#ef4444'], // Red-500
  ['p1', '#f97316'], // Orange-500
  ['p2', '#eab308'], // Yellow-500
  ['p3', '#22c55e'], // Green-500
  ['p4', '#3b82f6'], // Blue-500
]);

/**
 * Get status color
 */
export const getStatusColor = (status: string): string => {
  const normalizedStatus = status.toLowerCase();
  return STATUS_COLOR_MAP.get(normalizedStatus) ?? '#94a3b8';
};

/**
 * Get priority color
 */
export const getPriorityColor = (priority: string): string => {
  const normalizedPriority = priority.toLowerCase();
  return PRIORITY_COLOR_MAP.get(normalizedPriority) ?? '#64748b';
};
