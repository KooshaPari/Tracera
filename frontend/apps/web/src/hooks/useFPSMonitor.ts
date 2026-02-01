import { useEffect, useRef, useState } from 'react';

export interface FPSStats {
  current: number;
  average: number;
  min: number;
  max: number;
}

export function useFPSMonitor(enabled: boolean = true): FPSStats {
  const [stats, setStats] = useState<FPSStats>({
    current: 60,
    average: 60,
    min: 60,
    max: 60,
  });

  const frameTimesRef = useRef<number[]>([]);
  const lastFrameTimeRef = useRef<number>(performance.now());
  const rafIdRef = useRef<number>();

  useEffect(() => {
    if (!enabled) {
      if (rafIdRef.current) {
        cancelAnimationFrame(rafIdRef.current);
      }
      return;
    }

    function measureFPS() {
      const now = performance.now();
      const delta = now - lastFrameTimeRef.current;
      lastFrameTimeRef.current = now;

      const fps = 1000 / delta;

      // Keep last 60 frames
      frameTimesRef.current.push(fps);
      if (frameTimesRef.current.length > 60) {
        frameTimesRef.current.shift();
      }

      // Calculate stats
      const average = frameTimesRef.current.reduce((a, b) => a + b, 0) / frameTimesRef.current.length;
      const min = Math.min(...frameTimesRef.current);
      const max = Math.max(...frameTimesRef.current);

      setStats({
        current: fps,
        average,
        min,
        max,
      });

      rafIdRef.current = requestAnimationFrame(measureFPS);
    }

    rafIdRef.current = requestAnimationFrame(measureFPS);

    return () => {
      if (rafIdRef.current) {
        cancelAnimationFrame(rafIdRef.current);
      }
    };
  }, [enabled]);

  return stats;
}
