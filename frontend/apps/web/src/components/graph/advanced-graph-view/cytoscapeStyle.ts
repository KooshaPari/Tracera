import type { EdgeSingular, NodeSingular, StylesheetJson } from 'cytoscape';

import { ENHANCED_TYPE_COLORS, LINK_STYLES, STATUS_OPACITY } from '@/components/graph/types';

function getStringData(ele: NodeSingular | EdgeSingular, key: string): string | undefined {
  const value: unknown = ele.data(key);
  return typeof value === 'string' ? value : undefined;
}

export function createEnhancedCytoscapeStyle(highlightColor = '#fff'): StylesheetJson {
  return [
    {
      selector: 'node',
      style: {
        // Block pill shape (rounded rectangle)
        shape: 'round-rectangle',
        width: (ele: NodeSingular) => {
          const label = getStringData(ele, 'label') ?? '';
          return Math.max(100, Math.min(180, label.length * 6 + 40));
        },
        height: 50,
        'background-color': (ele: NodeSingular) => {
          const type = getStringData(ele, 'type');
          if (typeof type !== 'string' || type.length === 0) {
            return '#64748b';
          }
          return ENHANCED_TYPE_COLORS[type] ?? '#64748b';
        },
        'background-opacity': (ele: NodeSingular) => {
          const status = getStringData(ele, 'status');
          if (typeof status !== 'string' || status.length === 0) {
            return 1;
          }
          return STATUS_OPACITY[status] ?? 1;
        },
        // Label styling
        label: 'data(label)',
        color: '#fff',
        'text-outline-color': (ele: NodeSingular) => {
          const type = getStringData(ele, 'type');
          if (typeof type !== 'string' || type.length === 0) {
            return '#64748b';
          }
          return ENHANCED_TYPE_COLORS[type] ?? '#64748b';
        },
        'text-outline-width': 2,
        'font-size': 11,
        'font-weight': 'bold',
        'text-valign': 'center',
        'text-halign': 'center',
        'text-wrap': 'ellipsis',
        'text-max-width': '140px',
        // Border for visual depth
        'border-width': 2,
        'border-color': (ele: NodeSingular) => {
          const type = getStringData(ele, 'type');
          if (typeof type !== 'string' || type.length === 0) {
            return '#64748b';
          }
          return ENHANCED_TYPE_COLORS[type] ?? '#64748b';
        },
        'border-opacity': 0.3,
      },
    },
    {
      selector: 'edge',
      style: {
        width: 2,
        'line-color': (ele: EdgeSingular) => {
          const type = getStringData(ele, 'type');
          if (typeof type !== 'string' || type.length === 0) {
            return '#94a3b8';
          }
          return LINK_STYLES[type]?.color ?? '#94a3b8';
        },
        'target-arrow-color': (ele: EdgeSingular) => {
          const type = getStringData(ele, 'type');
          if (typeof type !== 'string' || type.length === 0) {
            return '#94a3b8';
          }
          return LINK_STYLES[type]?.color ?? '#94a3b8';
        },
        'target-arrow-shape': (ele: EdgeSingular) => {
          const type = getStringData(ele, 'type');
          if (typeof type !== 'string' || type.length === 0) {
            return 'none';
          }
          return LINK_STYLES[type]?.arrow ? 'triangle' : 'none';
        },
        'line-style': (ele: EdgeSingular) => {
          const type = getStringData(ele, 'type');
          if (typeof type !== 'string' || type.length === 0) {
            return 'solid';
          }
          return LINK_STYLES[type]?.dashed ? 'dashed' : 'solid';
        },
        'curve-style': 'bezier',
        opacity: 0.6,
        // Edge labels
        label: 'data(label)',
        'font-size': 9,
        'text-rotation': 'autorotate',
        'text-margin-y': -10,
        color: '#94a3b8',
        'text-background-color': '#1a1a2e',
        'text-background-opacity': 0.8,
        'text-background-padding': '2px',
      },
    },
    {
      selector: 'node:selected',
      style: {
        'border-color': '#fff',
        'border-opacity': 1,
        'border-width': 4,
        'overlay-color': '#fff',
        'overlay-opacity': 0.1,
      },
    },
    {
      selector: 'edge:selected',
      style: {
        opacity: 1,
        width: 4,
      },
    },
    {
      selector: 'node.highlighted',
      style: {
        'border-color': highlightColor,
        'border-opacity': 1,
        'border-width': 3,
      },
    },
    {
      selector: 'edge.highlighted',
      style: {
        opacity: 1,
        width: 3,
      },
    },
    {
      selector: 'node.faded',
      style: {
        opacity: 0.3,
      },
    },
    {
      selector: 'edge.faded',
      style: {
        opacity: 0.15,
      },
    },
  ];
}
