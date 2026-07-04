import type { InteractionMetrics } from './metrics';

import { ZERO } from './constants';

class InteractionTracker {
  private isPanning = false;
  private isZooming = false;
  private panStartTime = ZERO;
  private zoomStartTime = ZERO;
  private lastInteractionType: InteractionMetrics['lastInteractionType'] = 'idle';

  startPan(): void {
    if (!this.isPanning) {
      this.isPanning = true;
      this.panStartTime = performance.now();
      this.lastInteractionType = 'pan';
    }
  }

  endPan(): void {
    this.isPanning = false;
  }

  startZoom(): void {
    if (!this.isZooming) {
      this.isZooming = true;
      this.zoomStartTime = performance.now();
      this.lastInteractionType = 'zoom';
    }
  }

  endZoom(): void {
    this.isZooming = false;
  }

  getMetrics(): InteractionMetrics {
    const now = performance.now();

    let panDuration = ZERO;
    if (this.isPanning) {
      panDuration = now - this.panStartTime;
    }

    let zoomDuration = ZERO;
    if (this.isZooming) {
      zoomDuration = now - this.zoomStartTime;
    }

    return {
      isPanning: this.isPanning,
      isZooming: this.isZooming,
      lastInteractionType: this.lastInteractionType,
      panDuration,
      zoomDuration,
    };
  }

  reset(): void {
    this.isPanning = false;
    this.isZooming = false;
    this.panStartTime = ZERO;
    this.zoomStartTime = ZERO;
    this.lastInteractionType = 'idle';
  }
}

export { InteractionTracker };
