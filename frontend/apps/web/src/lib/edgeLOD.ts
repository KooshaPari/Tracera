export type EdgeLODLevel = 'detailed' | 'medium' | 'simple' | 'hidden';

export interface EdgeLODTier {
  level: EdgeLODLevel;
  distanceThreshold: number;
  pathType: 'bezier' | 'straight';
  strokeWidth: number;
  showLabel: boolean;
  showArrow: boolean;
  opacity: number;
}

export const EDGE_LOD_TIERS: EdgeLODTier[] = [
  {
    level: 'detailed',
    distanceThreshold: 0,
    pathType: 'bezier',
    strokeWidth: 2,
    showLabel: true,
    showArrow: true,
    opacity: 1.0,
  },
  {
    level: 'medium',
    distanceThreshold: 300,
    pathType: 'bezier',
    strokeWidth: 1.5,
    showLabel: false,
    showArrow: true,
    opacity: 0.8,
  },
  {
    level: 'simple',
    distanceThreshold: 600,
    pathType: 'straight',
    strokeWidth: 1,
    showLabel: false,
    showArrow: false,
    opacity: 0.5,
  },
  {
    level: 'hidden',
    distanceThreshold: 1200,
    pathType: 'straight',
    strokeWidth: 0,
    showLabel: false,
    showArrow: false,
    opacity: 0,
  },
];

export function getEdgeLODTier(
  edgeMidpoint: { x: number; y: number },
  viewportCenter: { x: number; y: number },
  zoom: number,
): EdgeLODTier {
  const distance = Math.sqrt(
    Math.pow(edgeMidpoint.x - viewportCenter.x, 2) + Math.pow(edgeMidpoint.y - viewportCenter.y, 2),
  );

  const zoomFactor = Math.max(0.5, Math.min(2, zoom));

  for (let i = EDGE_LOD_TIERS.length - 1; i >= 0; i--) {
    const tier = EDGE_LOD_TIERS[i];
    if (tier && distance >= tier.distanceThreshold / zoomFactor) {
      return tier;
    }
  }

  // Fallback to most detailed tier (should never reach here)
  return EDGE_LOD_TIERS[0]!;
}

// Helper to calculate edge midpoint
export function calculateEdgeMidpoint(
  sourcePos: { x: number; y: number },
  targetPos: { x: number; y: number },
): { x: number; y: number } {
  return {
    x: (sourcePos.x + targetPos.x) / 2,
    y: (sourcePos.y + targetPos.y) / 2,
  };
}

// Helper to apply LOD to edge style
export function applyEdgeLOD(baseStyle: any, lodTier: EdgeLODTier): any {
  return {
    ...baseStyle,
    strokeWidth: lodTier.strokeWidth,
    opacity: lodTier.opacity,
    ...(lodTier.pathType === 'straight' && { type: 'default' }),
    ...(lodTier.pathType === 'bezier' && { type: 'smoothstep' }),
  };
}
