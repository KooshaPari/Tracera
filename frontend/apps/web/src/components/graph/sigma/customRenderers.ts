import type { NodeDisplayData, EdgeDisplayData } from 'sigma/types';

// Import type colors from existing types
const ENHANCED_TYPE_COLORS: Record<string, string> = {
  requirement: '#3b82f6',
  test: '#10b981',
  defect: '#ef4444',
  epic: '#8b5cf6',
  story: '#06b6d4',
  task: '#f59e0b',
  feature: '#ec4899',
  default: '#64748b',
};

/**
 * Custom node renderer matching TraceRTM node styles
 * Renders simplified nodes for WebGL performance
 *
 * IMPORTANT: WebGL mode sacrifices rich interactivity for scale:
 * - No embedded images (placeholder icons only)
 * - No progress bars (status color indicator)
 * - No interactive buttons (use detail panel on click)
 * - Text labels remain (zoom-dependent)
 */
export function customNodeRenderer(
  context: CanvasRenderingContext2D,
  data: NodeDisplayData,
  settings: any
): void {
  const { x, y, size, label, type = 'default' } = data;
  const typeColor = ENHANCED_TYPE_COLORS[type as string] || ENHANCED_TYPE_COLORS.default;

  // Draw node circle with border
  context.beginPath();
  context.arc(x, y, size, 0, Math.PI * 2);

  // Fill with 25% opacity background
  context.fillStyle = typeColor + '40';
  context.fill();

  // Border
  context.strokeStyle = typeColor;
  context.lineWidth = 2;
  context.stroke();

  // Draw status indicator (replaces progress bar for performance)
  if ((data as any).status) {
    const statusSize = size * 0.3;
    context.beginPath();
    context.arc(x + size * 0.7, y - size * 0.7, statusSize, 0, Math.PI * 2);
    context.fillStyle = (data as any).statusColor || '#10b981';
    context.fill();
  }

  // Draw type icon (replaces embedded image for performance)
  // Only show when zoomed in enough
  if (settings.zoomRatio > 0.3) {
    context.fillStyle = typeColor;
    context.font = `${size * 0.6}px sans-serif`;
    context.textAlign = 'center';
    context.textBaseline = 'middle';

    // Icon mapping
    const icons: Record<string, string> = {
      requirement: '📋',
      test: '✓',
      defect: '🐛',
      epic: '🎯',
      story: '📖',
      task: '📝',
      feature: '⭐',
      default: '●',
    };

    const icon = icons[type as string] || icons.default;
    context.fillText(icon, x, y);
  }

  // Draw label (only if zoomed in)
  if (settings.zoomRatio > 0.5 && label) {
    context.fillStyle = '#ffffff';
    context.font = `${Math.max(10, size * 0.5)}px sans-serif`;
    context.textAlign = 'center';
    context.textBaseline = 'middle';

    // Truncate long labels
    const maxLength = 20;
    const displayLabel = (label as string).length > maxLength
      ? (label as string).substring(0, maxLength) + '...'
      : label;

    context.fillText(displayLabel as string, x, y + size + 10);
  }

  // Highlight on hover
  if ((data as any).highlighted) {
    context.beginPath();
    context.arc(x, y, size + 3, 0, Math.PI * 2);
    context.strokeStyle = typeColor;
    context.lineWidth = 3;
    context.setLineDash([5, 5]);
    context.stroke();
    context.setLineDash([]);
  }
}

/**
 * Custom edge renderer matching TraceRTM edge styles
 * Simplified for WebGL performance
 */
export function customEdgeRenderer(
  context: CanvasRenderingContext2D,
  data: EdgeDisplayData,
  settings: any
): void {
  const { x1, y1, x2, y2, color = '#94a3b8', size = 1, label } = data;

  // Draw edge line
  context.beginPath();
  context.moveTo(x1, y1);
  context.lineTo(x2, y2);
  context.strokeStyle = color as string;
  context.lineWidth = size;
  context.globalAlpha = 0.3;
  context.stroke();
  context.globalAlpha = 1.0;

  // Draw edge label (only if zoomed in very close)
  if (settings.zoomRatio > 0.7 && label) {
    const midX = (x1 + x2) / 2;
    const midY = (y1 + y2) / 2;

    // Background
    context.fillStyle = 'rgba(26, 26, 46, 0.9)';
    const labelWidth = context.measureText(label as string).width + 8;
    context.fillRect(midX - labelWidth / 2, midY - 10, labelWidth, 20);

    // Text
    context.fillStyle = color as string;
    context.font = '10px sans-serif';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(label as string, midX, midY);
  }

  // Highlight on hover
  if ((data as any).highlighted) {
    context.beginPath();
    context.moveTo(x1, y1);
    context.lineTo(x2, y2);
    context.strokeStyle = color as string;
    context.lineWidth = size + 2;
    context.stroke();
  }
}

// Export renderer configuration for Sigma
export const sigmaRenderers = {
  node: customNodeRenderer,
  edge: customEdgeRenderer,
};
