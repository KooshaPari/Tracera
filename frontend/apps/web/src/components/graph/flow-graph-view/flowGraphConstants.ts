import type { LinkType } from '@tracertm/types';

/** Stable noop for optional callbacks (A1 perf). */
export const flowGraphNoop = (): void => {};

export const DEFAULT_VIEWPORT = { x: 0, y: 0, zoom: 1 };
export const LEGEND_TYPE_LIMIT = 8;
export const SCALE_NODE_THRESHOLD = 500;
export const MAX_ANIMATED_EDGE_COUNT = 20;
export const INITIAL_VIEWPORT_SYNC_DELAY_MS = 300;
export const AUTO_FIT_DELAY_MS = 100;
export const FPS_GOOD_THRESHOLD = 55;
export const FPS_WARN_THRESHOLD = 30;
export const CANVAS_LAYER_Z_INDEX = 5;
export const GRAPH_EMPTY_LABEL = 'Untitled';
export const MAX_ITEM_DEPTH = 10;
export const VIEWPORT_WINDOW_THRESHOLD = 100;
export const VIEWPORT_WINDOW_PADDING = 200;
export const CANVAS_LOD_NODE_THRESHOLD = 50;
export const MAX_RENDERED_NODES = 400;
export const NODES_PER_BATCH = 100;
export const DEV_MODE = process.env['NODE_ENV'] === 'development';

export const EMPTY_CONNECTIONS: Partial<Record<LinkType, number>> = {};
