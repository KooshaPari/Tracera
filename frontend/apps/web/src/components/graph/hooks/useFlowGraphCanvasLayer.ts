import { useEffect, type RefObject } from 'react';
import type { Node } from '@xyflow/react';

import type { RichNodeData } from '../RichNodePill';

interface ViewportBounds {
  zoom: number;
  x: number;
  y: number;
}

export function useFlowGraphCanvasLayer(
  canvasLayerRef: RefObject<HTMLCanvasElement | null>,
  canvasNodes: Node<RichNodeData>[],
  viewportBounds: ViewportBounds | null,
): void {
  useEffect((): void => {
    if (canvasNodes.length === 0 || !viewportBounds) {
      return;
    }
    const canvas = canvasLayerRef.current;
    if (!canvas) {
      return;
    }
    const container = canvas.parentElement;
    if (!container) {
      return;
    }
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    if (containerWidth <= 0 || containerHeight <= 0) {
      return;
    }
    canvas.width = containerWidth;
    canvas.height = containerHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      return;
    }
    const { zoom, x, y } = viewportBounds;
    ctx.clearRect(0, 0, containerWidth, containerHeight);
    const radius = 3;
    canvasNodes.forEach((node) => {
      const screenX = node.position.x * zoom + x;
      const screenY = node.position.y * zoom + y;
      ctx.beginPath();
      ctx.arc(screenX, screenY, radius, 0, Math.PI * 2);
      ctx.fillStyle = '#64748b';
      ctx.fill();
    });
  }, [canvasLayerRef, canvasNodes, viewportBounds]);
}
