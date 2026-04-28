import type { LayoutConfig, LayoutType } from './types';

const LAYOUT_CONFIGS: LayoutConfig[] = [
  {
    algorithm: 'elk',
    bestFor: ['Requirements traceability', 'Linear flows', 'Waterfall processes'],
    description: 'Top-to-bottom directed flow',
    icon: 'ArrowDown',
    id: 'flow-chart',
    label: 'Flow Chart',
  },
  {
    algorithm: 'elk',
    bestFor: ['Process flows', 'User journeys', 'Sequential tasks'],
    description: 'Left-to-right progression',
    icon: 'ArrowRight',
    id: 'timeline',
    label: 'Timeline',
  },
  {
    algorithm: 'elk',
    bestFor: ['Component trees', 'Org charts', 'File systems'],
    description: 'Hierarchical tree structure',
    icon: 'GitBranch',
    id: 'tree',
    label: 'Tree',
  },
  {
    algorithm: 'd3-force',
    bestFor: ['Exploratory analysis', 'Relationship discovery', 'Unknown structures'],
    description: 'Natural clustering by relationships',
    icon: 'Network',
    id: 'organic-network',
    label: 'Organic Network',
  },
  {
    algorithm: 'd3-radial',
    bestFor: ['Brainstorming', 'Centered exploration', 'Topic mapping'],
    description: 'Radial layout from center',
    icon: 'CircleDot',
    id: 'mind-map',
    label: 'Mind Map',
  },
  {
    algorithm: 'grid',
    bestFor: ['Quick overview', 'Many items', 'Visual scanning'],
    description: 'Grid for quick overview',
    icon: 'LayoutGrid',
    id: 'gallery',
    label: 'Gallery',
  },
  {
    algorithm: 'circular',
    bestFor: ['Cyclic processes', 'Stakeholder maps', 'Peer relationships'],
    description: 'Circular arrangement',
    icon: 'Circle',
    id: 'wheel',
    label: 'Wheel',
  },
  {
    algorithm: 'grid',
    bestFor: ['Large datasets', 'Dense views', 'Minimized space'],
    description: 'Dense space-efficient grid',
    icon: 'Minimize2',
    id: 'compact',
    label: 'Compact',
  },
];

function getLayoutConfig(layout: LayoutType): LayoutConfig {
  const match = LAYOUT_CONFIGS.find((config) => config.id === layout);
  if (match) {
    return match;
  }
  // Default to first config (always exists since LAYOUT_CONFIGS is a const array)
  return LAYOUT_CONFIGS[0]!;
}

export { LAYOUT_CONFIGS, getLayoutConfig };
