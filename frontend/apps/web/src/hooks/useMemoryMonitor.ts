import { useEffect, useState } from 'react';

export interface MemoryStats {
  usedJSHeapSize: number; // MB
  totalJSHeapSize: number; // MB
  jsHeapSizeLimit: number; // MB
  usage: number; // 0-1
}

export function useMemoryMonitor(
  enabled: boolean = true,
  interval: number = 1000
): MemoryStats | null {
  const [stats, setStats] = useState<MemoryStats | null>(null);

  useEffect(() => {
    if (!enabled) return;

    // Check if performance.memory is available (Chrome only)
    if (!('memory' in performance)) {
      return;
    }

    function measureMemory() {
      const memory = (performance as any).memory;
      setStats({
        usedJSHeapSize: memory.usedJSHeapSize / 1024 / 1024,
        totalJSHeapSize: memory.totalJSHeapSize / 1024 / 1024,
        jsHeapSizeLimit: memory.jsHeapSizeLimit / 1024 / 1024,
        usage: memory.usedJSHeapSize / memory.jsHeapSizeLimit,
      });
    }

    measureMemory();
    const intervalId = setInterval(measureMemory, interval);

    return () => clearInterval(intervalId);
  }, [enabled, interval]);

  return stats;
}
