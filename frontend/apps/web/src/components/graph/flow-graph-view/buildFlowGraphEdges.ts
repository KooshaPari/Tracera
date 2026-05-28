import type { Edge } from '@xyflow/react';

import { calculateEdgeMidpoint, getEdgeLODTier } from '@/lib/edgeLOD';
import type { Link } from '@tracertm/types';

import {
  EDGE_LABEL_BG_STYLE,
  getCachedEdgeStyle,
  MAX_ANIMATED_EDGE_COUNT,
  SCALE_NODE_THRESHOLD,
} from './flowGraphEdgeStyles';

interface NodePosition {
  x: number;
  y: number;
}

interface BuildFlowGraphEdgesInput {
  dagreLaidoutNodes: Array<{ id: string; position: NodePosition }>;
  edgesForRendering: Link[];
  getViewport?: (() => { x: number; y: number; zoom: number }) | undefined;
}

export function buildFlowGraphInitialEdges({
  dagreLaidoutNodes,
  edgesForRendering,
  getViewport,
}: BuildFlowGraphEdgesInput): Edge[] {
  const viewport = getViewport?.() ?? { x: 0, y: 0, zoom: 1 };
  const viewportCenter = {
    x: -viewport.x + window.innerWidth / 2 / viewport.zoom,
    y: -viewport.y + window.innerHeight / 2 / viewport.zoom,
  };

  const nodePositions = new Map(dagreLaidoutNodes.map((n) => [n.id, n.position]));

  const atScale =
    dagreLaidoutNodes.length >= SCALE_NODE_THRESHOLD || edgesForRendering.length >= 1000;
  const maxAnimatedEdges = atScale ? 0 : MAX_ANIMATED_EDGE_COUNT;
  const animatedEdgeIds = new Set(
    edgesForRendering
      .filter((link) => link.type === 'depends_on' || link.type === 'blocks')
      .slice(0, maxAnimatedEdges)
      .map((link) => link.id),
  );

  return edgesForRendering
    .map((link) => {
      const cached = getCachedEdgeStyle(link.type);

      const sourcePos = nodePositions.get(link.sourceId);
      const targetPos = nodePositions.get(link.targetId);
      if (!sourcePos || !targetPos) {
        return null;
      }

      const edgeMidpoint = calculateEdgeMidpoint(sourcePos, targetPos);
      const lodTier = getEdgeLODTier(edgeMidpoint, viewportCenter, viewport.zoom);
      if (lodTier.level === 'hidden') {
        return null;
      }

      const showLabel = !atScale && lodTier.showLabel;
      return {
        id: link.id,
        source: link.sourceId,
        target: link.targetId,
        type: lodTier.pathType === 'bezier' ? 'smoothstep' : 'default',
        animated: lodTier.level === 'detailed' && animatedEdgeIds.has(link.id),
        style: {
          ...cached.style,
          strokeWidth: lodTier.strokeWidth,
          opacity: lodTier.opacity,
        },
        ...(showLabel && {
          label: cached.label,
          labelBgStyle: EDGE_LABEL_BG_STYLE,
          labelStyle: cached.labelStyle,
        }),
        ...(lodTier.showArrow && cached.markerEnd && { markerEnd: cached.markerEnd }),
      };
    })
    .filter(Boolean) as Edge[];
}
