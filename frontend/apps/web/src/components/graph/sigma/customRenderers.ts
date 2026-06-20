import type { EdgeDisplayData, NodeDisplayData } from 'sigma/types';

const DEFAULT_COLOR = '#64748b';
const DEFAULT_STATUS_COLOR = '#10b981';
const EDGE_COLOR = '#94a3b8';
const LABEL_COLOR = '#ffffff';
const LABEL_BG = 'rgba(26, 26, 46, 0.9)';

const BORDER_WIDTH = 2;
const HIGHLIGHT_WIDTH = 3;
const EDGE_HIGHLIGHT_WIDTH = 2;
const DASH_SEGMENT = 5;
const FULL_CIRCLE = Math.PI * 2;
const HALF_DIVISOR = 2;
const DEFAULT_EDGE_SIZE = 1;
const LABEL_FONT_SIZE = 10;
const ZERO = 0;
const FULL_OPACITY = 1;

const STATUS_SCALE = 0.3;
const STATUS_OFFSET_SCALE = 0.7;
const ICON_FONT_SCALE = 0.6;
const LABEL_FONT_SCALE = 0.5;
const LABEL_MIN_SIZE = 10;
const LABEL_MAX_LENGTH = 20;
const LABEL_OFFSET = 10;
const LABEL_PADDING = 8;
const LABEL_HEIGHT = 20;
const LABEL_HALF_HEIGHT = 10;

const ZOOM_ICON_THRESHOLD = 0.3;
const ZOOM_LABEL_THRESHOLD = 0.5;
const ZOOM_EDGE_LABEL_THRESHOLD = 0.7;
const EDGE_ALPHA = 0.3;

// Import type colors from existing types
const ENHANCED_TYPE_COLORS: Record<string, string> = {
  default: DEFAULT_COLOR,
  defect: '#ef4444',
  epic: '#8b5cf6',
  feature: '#ec4899',
  requirement: '#3b82f6',
  story: '#06b6d4',
  task: '#f59e0b',
  test: '#10b981',
};

const ICONS: Record<string, string> = {
  default: '●',
  defect: '🐛',
  epic: '🎯',
  feature: '⭐',
  requirement: '📋',
  story: '📖',
  task: '📝',
  test: '✓',
};

const readNumber = (obj: Record<string, unknown>, key: string): number | undefined => {
  const value = obj[key];
  return typeof value === 'number' ? value : undefined;
};

const readString = (obj: Record<string, unknown>, key: string): string | undefined => {
  const value = obj[key];
  return typeof value === 'string' ? value : undefined;
};

const getZoomRatio = (settings: Record<string, unknown>): number => {
  const value = settings['zoomRatio'];
  return typeof value === 'number' ? value : ZERO;
};

const getTypeColor = (typeValue: unknown): string => {
  const out = typeof typeValue === 'string' ? ENHANCED_TYPE_COLORS[typeValue] : undefined;
  return out ?? ENHANCED_TYPE_COLORS['default'] ?? '#6b7280';
};

const drawNodeBase = (
  context: CanvasRenderingContext2D,
  x: number,
  y: number,
  size: number,
  color: string,
): void => {
  context.beginPath();
  context.arc(x, y, size, ZERO, FULL_CIRCLE);
  context.fillStyle = `${color}40`;
  context.fill();
  context.strokeStyle = color;
  context.lineWidth = BORDER_WIDTH;
  context.stroke();
};

const drawStatusIndicator = (
  context: CanvasRenderingContext2D,
  x: number,
  y: number,
  size: number,
  statusColor: string,
): void => {
  const statusSize = size * STATUS_SCALE;
  context.beginPath();
  context.arc(
    x + size * STATUS_OFFSET_SCALE,
    y - size * STATUS_OFFSET_SCALE,
    statusSize,
    ZERO,
    FULL_CIRCLE,
  );
  context.fillStyle = statusColor;
  context.fill();
};

const drawNodeIcon = (
  context: CanvasRenderingContext2D,
  x: number,
  y: number,
  size: number,
  color: string,
  icon: string,
): void => {
  context.fillStyle = color;
  context.font = `${size * ICON_FONT_SCALE}px sans-serif`;
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  context.fillText(icon, x, y);
};

const drawNodeLabel = (
  context: CanvasRenderingContext2D,
  x: number,
  y: number,
  size: number,
  label: string,
): void => {
  context.fillStyle = LABEL_COLOR;
  context.font = `${Math.max(LABEL_MIN_SIZE, size * LABEL_FONT_SCALE)}px sans-serif`;
  context.textAlign = 'center';
  context.textBaseline = 'middle';

  const displayLabel =
    label.length > LABEL_MAX_LENGTH ? `${label.slice(0, LABEL_MAX_LENGTH)}...` : label;

  context.fillText(displayLabel, x, y + size + LABEL_OFFSET);
};

const drawNodeHighlight = (
  context: CanvasRenderingContext2D,
  x: number,
  y: number,
  size: number,
  color: string,
): void => {
  context.beginPath();
  context.arc(x, y, size + HIGHLIGHT_WIDTH, ZERO, FULL_CIRCLE);
  context.strokeStyle = color;
  context.lineWidth = HIGHLIGHT_WIDTH;
  context.setLineDash([DASH_SEGMENT, DASH_SEGMENT]);
  context.stroke();
  context.setLineDash([]);
};

const drawEdgeLine = (
  context: CanvasRenderingContext2D,
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  color: string,
  lineWidth: number,
): void => {
  context.beginPath();
  context.moveTo(x1, y1);
  context.lineTo(x2, y2);
  context.strokeStyle = color;
  context.lineWidth = lineWidth;
  context.globalAlpha = EDGE_ALPHA;
  context.stroke();
  context.globalAlpha = FULL_OPACITY;
};

const drawEdgeLabel = (
  context: CanvasRenderingContext2D,
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  label: string,
  color: string,
): void => {
  const midX = (x1 + x2) / HALF_DIVISOR;
  const midY = (y1 + y2) / HALF_DIVISOR;
  const labelWidth = context.measureText(label).width + LABEL_PADDING;

  context.fillStyle = LABEL_BG;
  context.fillRect(
    midX - labelWidth / HALF_DIVISOR,
    midY - LABEL_HALF_HEIGHT,
    labelWidth,
    LABEL_HEIGHT,
  );

  context.fillStyle = color;
  context.font = `${LABEL_FONT_SIZE}px sans-serif`;
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  context.fillText(label, midX, midY);
};

const drawEdgeHighlight = (
  context: CanvasRenderingContext2D,
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  color: string,
  lineWidth: number,
): void => {
  context.beginPath();
  context.moveTo(x1, y1);
  context.lineTo(x2, y2);
  context.strokeStyle = color;
  context.lineWidth = lineWidth + EDGE_HIGHLIGHT_WIDTH;
  context.stroke();
};

/**
 * Custom node renderer matching TraceRTM node styles
 * Renders simplified nodes for WebGL performance
 */
const customNodeRenderer = (
  context: CanvasRenderingContext2D,
  data: NodeDisplayData,
  settings: Record<string, unknown>,
): void => {
  const { x, y, size, label, type } = data;
  const extra = data as unknown as Record<string, unknown>;
  const zoomRatio = getZoomRatio(settings);
  const typeColor = getTypeColor(type);

  drawNodeBase(context, x, y, size, typeColor);

  const status = readString(extra, 'status');
  if (status) {
    const statusColor = readString(extra, 'statusColor') ?? DEFAULT_STATUS_COLOR;
    drawStatusIndicator(context, x, y, size, statusColor);
  }

  if (zoomRatio > ZOOM_ICON_THRESHOLD) {
    const iconKey = typeof type === 'string' ? type : 'default';
    const icon = ICONS[iconKey] ?? ICONS['default'] ?? '';
    drawNodeIcon(context, x, y, size, typeColor, icon);
  }

  if (zoomRatio > ZOOM_LABEL_THRESHOLD && typeof label === 'string') {
    drawNodeLabel(context, x, y, size, label);
  }

  if (extra['highlighted'] === true) {
    drawNodeHighlight(context, x, y, size, typeColor);
  }
};

/**
 * Custom edge renderer matching TraceRTM edge styles
 * Simplified for WebGL performance
 */
const customEdgeRenderer = (
  context: CanvasRenderingContext2D,
  data: EdgeDisplayData,
  settings: Record<string, unknown>,
): void => {
  const extra = data as unknown as Record<string, unknown>;
  const x1 = readNumber(extra, 'x1');
  const y1 = readNumber(extra, 'y1');
  const x2 = readNumber(extra, 'x2');
  const y2 = readNumber(extra, 'y2');

  if (x1 === undefined || y1 === undefined || x2 === undefined || y2 === undefined) {
    return;
  }

  const color = readString(extra, 'color') ?? EDGE_COLOR;
  const size = readNumber(extra, 'size') ?? DEFAULT_EDGE_SIZE;
  const label = readString(extra, 'label');
  const zoomRatio = getZoomRatio(settings);

  drawEdgeLine(context, x1, y1, x2, y2, color, size);

  if (zoomRatio > ZOOM_EDGE_LABEL_THRESHOLD && label) {
    drawEdgeLabel(context, x1, y1, x2, y2, label, color);
  }

  if (extra['highlighted'] === true) {
    drawEdgeHighlight(context, x1, y1, x2, y2, color, size);
  }
};

// Export renderer configuration for Sigma
const sigmaRenderers = {
  edge: customEdgeRenderer,
  node: customNodeRenderer,
};

export { customEdgeRenderer, customNodeRenderer, sigmaRenderers };
