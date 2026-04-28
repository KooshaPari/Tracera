/**
 * Example integrations for usePredictivePrefetch hook
 *
 * This file demonstrates how to integrate predictive prefetching
 * with existing graph components and caching systems.
 */

import type { ReactElement, UIEvent } from 'react';

import { useCallback, useEffect, useMemo, useState } from 'react';

import type { GraphCacheNode } from '../lib/graphCache';
import type { PredictedViewport, Viewport } from './usePredictivePrefetch';

import { graphCache, setCache } from '../lib/graphCache';
import { logger } from '../lib/logger';
import { usePredictivePrefetch, viewportToCacheKey } from './usePredictivePrefetch';

const ZERO = 0;
const DEFAULT_VIEWPORT_HEIGHT = 900;
const DEFAULT_VIEWPORT_WIDTH = 1200;
const DEFAULT_ZOOM = 1;

const PREDICTION_HORIZON_DEFAULT_MS = 500;
const PREDICTION_HORIZON_REACTFLOW_MS = 600;
const PREDICTION_HORIZON_LOW_FPS_MS = 300;
const PREDICTION_HORIZON_HIGH_FPS_MS = 700;
const PREDICTION_HORIZON_NEAR_MS = 300;
const PREDICTION_HORIZON_FAR_MS = 800;

const VELOCITY_THRESHOLD_DEFAULT = 15;
const VELOCITY_THRESHOLD_REACTFLOW = 20;
const VELOCITY_THRESHOLD_FAR = 20;

const DEBOUNCE_REACTFLOW_MS = 150;

const FPS_SAMPLE_INTERVAL_MS = 1000;
const FPS_DEFAULT = 60;
const FPS_LOW_THRESHOLD = 30;
const FPS_HIGH_THRESHOLD = 50;

const SPEED_DECIMALS = 2;
const FPS_DECIMALS = 1;
const COORDINATE_DECIMALS = 0;

const DIRECTIONAL_EXPANSION_PX = 200;

const LABEL_PREDICTING_YES = 'Yes';
const LABEL_PREDICTING_NO = 'No';
const LABEL_PREFETCH_ACTIVE = 'Active';
const LABEL_PREFETCH_IDLE = 'Idle';

const DEFAULT_VIEWPORT: Viewport = {
  height: DEFAULT_VIEWPORT_HEIGHT,
  width: DEFAULT_VIEWPORT_WIDTH,
  x: ZERO,
  y: ZERO,
  zoom: DEFAULT_ZOOM,
};

const EMPTY_VIEWPORT: Viewport = {
  height: ZERO,
  width: ZERO,
  x: ZERO,
  y: ZERO,
  zoom: DEFAULT_ZOOM,
};

interface ReactFlowViewport {
  x: number;
  y: number;
  zoom: number;
}

interface ReactFlowBounds {
  height: number;
  width: number;
}

interface ReactFlowInstance {
  getViewport: () => ReactFlowViewport;
  getBounds: () => ReactFlowBounds;
  on: (event: 'move', handler: () => void) => void;
  off: (event: 'move', handler: () => void) => void;
}

function formatPredictingLabel(isPredicting: boolean): string {
  if (isPredicting) {
    return LABEL_PREDICTING_YES;
  }
  return LABEL_PREDICTING_NO;
}

function formatPrefetchStatus(isPredicting: boolean): string {
  if (isPredicting) {
    return LABEL_PREFETCH_ACTIVE;
  }
  return LABEL_PREFETCH_IDLE;
}

function buildPredictedInfo(
  predictedViewport?: PredictedViewport | null,
): ReactElement | undefined {
  if (!predictedViewport) {
    return undefined;
  }

  return (
    <p>
      Predicted: ({predictedViewport.minX.toFixed(COORDINATE_DECIMALS)},{' '}
      {predictedViewport.minY.toFixed(COORDINATE_DECIMALS)})
    </p>
  );
}

function expandBounds(predicted: PredictedViewport, viewport: Viewport): PredictedViewport {
  const {
    maxX: predictedMaxX,
    maxY: predictedMaxY,
    minX: predictedMinX,
    minY: predictedMinY,
    zoom,
  } = predicted;
  const deltaX = predictedMinX - viewport.x;
  const deltaY = predictedMinY - viewport.y;

  let minX = predictedMinX;
  let maxX = predictedMaxX;
  let minY = predictedMinY;
  let maxY = predictedMaxY;

  if (deltaX > ZERO) {
    maxX += DIRECTIONAL_EXPANSION_PX;
  } else {
    minX -= DIRECTIONAL_EXPANSION_PX;
  }

  if (deltaY > ZERO) {
    maxY += DIRECTIONAL_EXPANSION_PX;
  } else {
    minY -= DIRECTIONAL_EXPANSION_PX;
  }

  return {
    maxX,
    maxY,
    minX,
    minY,
    zoom,
  };
}

const ExampleBasicGraphView = (): ReactElement => {
  const [viewport, setViewport] = useState<Viewport>(DEFAULT_VIEWPORT);

  const handleScroll = useCallback((event: UIEvent<HTMLDivElement>): void => {
    const target = event.currentTarget;
    setViewport((prev) => ({
      ...prev,
      x: target.scrollLeft,
      y: target.scrollTop,
    }));
  }, []);

  const loadViewportData = useCallback(async (predicted: PredictedViewport): Promise<void> => {
    const cacheKey = viewportToCacheKey(predicted);
    const cached = graphCache.get(cacheKey);

    if (cached) {
      logger.info('Using cached data for predicted viewport');
      return;
    }

    logger.info('Prefetching data for:', predicted);
    const data = await fetchGraphData(predicted);

    cacheNodes(cacheKey, data);
  }, []);

  const { isPredicting, speed, predictedViewport } = usePredictivePrefetch({
    enabled: true,
    loadViewport: loadViewportData,
    predictionHorizon: PREDICTION_HORIZON_DEFAULT_MS,
    velocityThreshold: VELOCITY_THRESHOLD_DEFAULT,
    viewport,
  });

  const predictingLabel = useMemo(() => formatPredictingLabel(isPredicting), [isPredicting]);
  const predictedInfo = useMemo(() => buildPredictedInfo(predictedViewport), [predictedViewport]);

  return (
    <div>
      <div className='debug-info'>
        <p>Speed: {speed.toFixed(SPEED_DECIMALS)} px/frame</p>
        <p>Predicting: {predictingLabel}</p>
        {predictedInfo}
      </div>

      <div className='graph-container' onScroll={handleScroll}>
        <div>Graph content</div>
      </div>
    </div>
  );
};

const ExampleReactFlowIntegration = (): ReactElement => {
  const [reactFlowInstance, _setReactFlowInstance] = useState<ReactFlowInstance | undefined>();
  const [viewport, _setViewport] = useState<Viewport>(EMPTY_VIEWPORT);

  useEffect((): void | (() => void) => {
    if (!reactFlowInstance) {
      return;
    }

    const updateViewport = (): void => {
      const rfViewport = reactFlowInstance.getViewport();
      const bounds = reactFlowInstance.getBounds();
      const { height, width } = bounds;
      const { x, y, zoom } = rfViewport;

      _setViewport({
        height,
        width,
        x: -x / zoom,
        y: -y / zoom,
        zoom,
      });
    };

    updateViewport();
    reactFlowInstance.on('move', updateViewport);

    return () => {
      reactFlowInstance.off('move', updateViewport);
    };
  }, [reactFlowInstance]);

  const loadViewportNodes = useCallback(async (predicted: PredictedViewport): Promise<void> => {
    const cacheKey = viewportToCacheKey(predicted);

    if (graphCache.has(cacheKey)) {
      return;
    }

    const nodes = await fetchNodesInBounds(predicted);
    cacheNodes(cacheKey, nodes);

    await preloadNodeAssets(nodes);
  }, []);

  usePredictivePrefetch({
    debounceDelay: DEBOUNCE_REACTFLOW_MS,
    enabled: true,
    loadViewport: loadViewportNodes,
    predictionHorizon: PREDICTION_HORIZON_REACTFLOW_MS,
    velocityThreshold: VELOCITY_THRESHOLD_REACTFLOW,
    viewport,
  });

  return <div>ReactFlow integration example</div>;
};

const ExampleAdaptivePrefetching = (): ReactElement => {
  const [viewport, _setViewport] = useState<Viewport>(DEFAULT_VIEWPORT);
  const [predictionHorizon, setPredictionHorizon] = useState(PREDICTION_HORIZON_DEFAULT_MS);
  const [fps, setFps] = useState(FPS_DEFAULT);

  useEffect((): (() => void) => {
    let lastTime = performance.now();
    let frames = ZERO;

    const measureFps = (): void => {
      frames += 1;
      const now = performance.now();
      const elapsed = now - lastTime;

      if (elapsed >= FPS_SAMPLE_INTERVAL_MS) {
        const currentFps = (frames * FPS_SAMPLE_INTERVAL_MS) / elapsed;
        setFps(currentFps);
        frames = ZERO;
        lastTime = now;

        if (currentFps < FPS_LOW_THRESHOLD) {
          setPredictionHorizon(PREDICTION_HORIZON_LOW_FPS_MS);
        } else if (currentFps > FPS_HIGH_THRESHOLD) {
          setPredictionHorizon(PREDICTION_HORIZON_HIGH_FPS_MS);
        } else {
          setPredictionHorizon(PREDICTION_HORIZON_DEFAULT_MS);
        }
      }

      requestAnimationFrame(measureFps);
    };

    const rafId = requestAnimationFrame(measureFps);
    return () => {
      cancelAnimationFrame(rafId);
    };
  }, []);

  const loadViewportData = useCallback(async (predicted: PredictedViewport): Promise<void> => {
    const cacheKey = viewportToCacheKey(predicted);

    if (!graphCache.has(cacheKey)) {
      const data = await fetchGraphData(predicted);
      cacheNodes(cacheKey, data);
    }
  }, []);

  const { isPredicting } = usePredictivePrefetch({
    enabled: true,
    loadViewport: loadViewportData,
    predictionHorizon: predictionHorizon,
    velocityThreshold: VELOCITY_THRESHOLD_DEFAULT,
    viewport,
  });

  const prefetchStatus = useMemo(() => formatPrefetchStatus(isPredicting), [isPredicting]);

  return (
    <div>
      <div className='performance-info'>
        <p>FPS: {fps.toFixed(FPS_DECIMALS)}</p>
        <p>Prediction Horizon: {predictionHorizon}ms</p>
        <p>Prefetching: {prefetchStatus}</p>
      </div>
    </div>
  );
};

const ExampleMultiLayerPrefetching = (): ReactElement => {
  const [viewport, _setViewport] = useState<Viewport>(DEFAULT_VIEWPORT);

  const loadNearData = useCallback(async (predicted: PredictedViewport): Promise<void> => {
    const cacheKey = `near:${viewportToCacheKey(predicted)}`;

    if (!graphCache.has(cacheKey)) {
      const nodeDetails = await fetchDetailedNodeData(predicted);
      cacheNodes(cacheKey, nodeDetails);
    }
  }, []);

  const loadFarData = useCallback(async (predicted: PredictedViewport): Promise<void> => {
    const cacheKey = `far:${viewportToCacheKey(predicted)}`;

    if (!graphCache.has(cacheKey)) {
      const basicNodes = await fetchBasicNodeData(predicted);
      cacheNodes(cacheKey, basicNodes);
    }
  }, []);

  usePredictivePrefetch({
    loadViewport: loadNearData,
    predictionHorizon: PREDICTION_HORIZON_NEAR_MS,
    velocityThreshold: VELOCITY_THRESHOLD_DEFAULT,
    viewport,
  });

  usePredictivePrefetch({
    loadViewport: loadFarData,
    predictionHorizon: PREDICTION_HORIZON_FAR_MS,
    velocityThreshold: VELOCITY_THRESHOLD_FAR,
    viewport,
  });

  return <div>Graph content</div>;
};

const ExampleDirectionalPrefetching = (): ReactElement => {
  const [viewport, _setViewport] = useState<Viewport>(DEFAULT_VIEWPORT);

  const loadDirectionalData = useCallback(
    async (predicted: PredictedViewport): Promise<void> => {
      const expandedBounds = expandBounds(predicted, viewport);
      const cacheKey = viewportToCacheKey(expandedBounds);

      if (!graphCache.has(cacheKey)) {
        const data = await fetchGraphData(expandedBounds);
        cacheNodes(cacheKey, data);
      }
    },
    [viewport],
  );

  usePredictivePrefetch({
    loadViewport: loadDirectionalData,
    predictionHorizon: PREDICTION_HORIZON_DEFAULT_MS,
    velocityThreshold: VELOCITY_THRESHOLD_DEFAULT,
    viewport,
  });

  return <div>Graph content</div>;
};

async function fetchGraphData(_predicted: PredictedViewport): Promise<GraphCacheNode[]> {
  await Promise.resolve();
  return [];
}

async function fetchNodesInBounds(_bounds: PredictedViewport): Promise<GraphCacheNode[]> {
  await Promise.resolve();
  return [];
}

async function preloadNodeAssets(_nodes: GraphCacheNode[]): Promise<void> {
  await Promise.resolve();
}

function cacheNodes(cacheKey: string, nodes: GraphCacheNode[]): void {
  setCache(cacheKey, {
    nodes,
    timestamp: Date.now(),
  });
}

async function fetchDetailedNodeData(_predicted: PredictedViewport): Promise<GraphCacheNode[]> {
  await Promise.resolve();
  return [];
}

async function fetchBasicNodeData(_predicted: PredictedViewport): Promise<GraphCacheNode[]> {
  await Promise.resolve();
  return [];
}

export {
  ExampleAdaptivePrefetching,
  ExampleBasicGraphView,
  ExampleDirectionalPrefetching,
  ExampleMultiLayerPrefetching,
  ExampleReactFlowIntegration,
};
