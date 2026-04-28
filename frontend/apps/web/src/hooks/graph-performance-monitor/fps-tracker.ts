import type { FPSMetrics } from './metrics';

import { FPS_SAMPLE_LIMIT, MS_PER_SECOND, ZERO } from './constants';

class FPSTracker {
  private frames: number[] = [];
  private lastFrameTime: number = performance.now();
  private rafId: number | undefined;
  private isRunning = false;

  start(): void {
    if (this.isRunning) {
      return;
    }
    this.isRunning = true;
    this.tick();
  }

  stop(): void {
    this.isRunning = false;
    if (this.rafId !== undefined) {
      cancelAnimationFrame(this.rafId);
      this.rafId = undefined;
    }
  }

  private tick = (): void => {
    if (!this.isRunning) {
      return;
    }

    const now = performance.now();
    const delta = now - this.lastFrameTime;
    this.lastFrameTime = now;

    if (delta > ZERO) {
      const fps = MS_PER_SECOND / delta;
      this.frames.push(fps);
      if (this.frames.length > FPS_SAMPLE_LIMIT) {
        this.frames.shift();
      }
    }

    this.rafId = requestAnimationFrame(this.tick);
  };

  getMetrics(): FPSMetrics {
    if (this.frames.length === ZERO) {
      return { average: ZERO, current: ZERO, max: ZERO, min: ZERO, samples: ZERO };
    }

    const lastIndex = this.frames.length - 1;
    let current = ZERO;
    if (lastIndex >= ZERO) {
      current = this.frames[lastIndex] ?? ZERO;
    }
    const average = this.frames.reduce((sum, fps) => sum + fps, ZERO) / this.frames.length;
    const min = Math.min(...this.frames);
    const max = Math.max(...this.frames);

    return {
      average: Math.round(average),
      current: Math.round(current),
      max: Math.round(max),
      min: Math.round(min),
      samples: this.frames.length,
    };
  }

  reset(): void {
    this.frames = [];
    this.lastFrameTime = performance.now();
  }
}

export { FPSTracker };
