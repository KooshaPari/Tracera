import type { ComponentType } from 'react';

import {
  ArrowDown,
  CircleDot,
  Component,
  FileStack,
  GitBranch,
  LayoutGrid,
  Lock,
  MapPin,
  Monitor,
  Network,
  Route,
  Share2,
  Shield,
  ShoppingCart,
  Workflow,
  Zap,
} from 'lucide-react';

import type { LayoutType } from './layouts/useDagLayout';
import type { GraphPerspective } from './types';

// View types: graph/diagram styles + perspectives
type GraphViewMode =
  | 'traceability'
  | 'flow-chart'
  | 'dependency-graph'
  | 'hierarchy'
  | 'impact-map'
  | 'journey-map'
  | 'mind-map'
  | 'gallery'
  | 'page-flow'
  | 'components'
  | 'perspective-product'
  | 'perspective-business'
  | 'perspective-technical'
  | 'perspective-ui'
  | 'perspective-security'
  | 'perspective-performance';

interface ViewConfig {
  id: GraphViewMode;
  label: string;
  description: string;
  icon: ComponentType<{ className?: string }>;
  category: 'graph' | 'diagram' | 'perspective';
  perspective?: GraphPerspective;
  /** Layout to use when this view is a graph (traceability-style) view. */
  layoutPreference?: LayoutType;
}

const VIEW_CONFIGS: ViewConfig[] = [
  // ---- Graph & diagram views (same data, different layout or visualization) ----
  {
    category: 'graph',
    description: 'Full node graph with all connections',
    icon: Network,
    id: 'traceability',
    label: 'Traceability Graph',
    layoutPreference: 'organic-network',
  },
  {
    category: 'graph',
    description: 'Top-to-bottom directed flow',
    icon: ArrowDown,
    id: 'flow-chart',
    label: 'Flow Chart',
    layoutPreference: 'flow-chart',
  },
  {
    category: 'graph',
    description: 'Dependencies and relationships',
    icon: Share2,
    id: 'dependency-graph',
    label: 'Dependency Graph',
    layoutPreference: 'flow-chart',
  },
  {
    category: 'graph',
    description: 'Tree structure and parent-child',
    icon: GitBranch,
    id: 'hierarchy',
    label: 'Hierarchy / Tree',
    layoutPreference: 'tree',
  },
  {
    category: 'graph',
    description: 'Impact and downstream effects',
    icon: MapPin,
    id: 'impact-map',
    label: 'Impact Map',
    layoutPreference: 'organic-network',
  },
  {
    category: 'graph',
    description: 'User flows and sequences',
    icon: Route,
    id: 'journey-map',
    label: 'Journey Map',
    layoutPreference: 'timeline',
  },
  {
    category: 'graph',
    description: 'Radial layout from center',
    icon: CircleDot,
    id: 'mind-map',
    label: 'Mind Map',
    layoutPreference: 'mind-map',
  },
  {
    category: 'graph',
    description: 'Grid for quick overview',
    icon: LayoutGrid,
    id: 'gallery',
    label: 'Gallery / Grid',
    layoutPreference: 'gallery',
  },
  // ---- Diagram views (different visualization) ----
  {
    category: 'diagram',
    description: 'UI page interactions and navigation',
    icon: Workflow,
    id: 'page-flow',
    label: 'Page Flow',
  },
  {
    category: 'diagram',
    description: 'UI component tree and hierarchy',
    icon: Component,
    id: 'components',
    label: 'Component Library',
  },
  // ---- Perspectives (filtered by type) ----
  {
    category: 'perspective',
    description: 'Features, epics, and user stories',
    icon: ShoppingCart,
    id: 'perspective-product',
    label: 'Product View',
    perspective: 'product',
  },
  {
    category: 'perspective',
    description: 'Business rules and requirements',
    icon: FileStack,
    id: 'perspective-business',
    label: 'Business View',
    perspective: 'business',
  },
  {
    category: 'perspective',
    description: 'Architecture and implementation',
    icon: GitBranch,
    id: 'perspective-technical',
    label: 'Technical View',
    perspective: 'technical',
  },
  {
    category: 'perspective',
    description: 'Wireframes, mockups, and screens',
    icon: Monitor,
    id: 'perspective-ui',
    label: 'UI/UX View',
    perspective: 'ui',
  },
  {
    category: 'perspective',
    description: 'Security controls and compliance',
    icon: Shield,
    id: 'perspective-security',
    label: 'Security View',
    perspective: 'security',
  },
  {
    category: 'perspective',
    description: 'Performance metrics and bottlenecks',
    icon: Zap,
    id: 'perspective-performance',
    label: 'Performance View',
    perspective: 'performance',
  },
];

export { VIEW_CONFIGS, type GraphViewMode, type ViewConfig };
