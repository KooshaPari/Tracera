import { useEffect, useState } from 'react';

const BYTES_PER_KB = 1024;
const BYTES_PER_MB = BYTES_PER_KB * BYTES_PER_KB;

export interface MemoryStats {
  usedJSHeapSize: number; // MB
  totalJSHeapSize: number; // MB
  jsHeapSizeLimit: number; // MB
  usage: number; // 0-1
}

export function useMemoryMonitor(enabled = true, interval = 1000): MemoryStats | null {
  const [stats, setStats] = useState<MemoryStats | null>(null);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    // Check if performance.memory is available (Chrome only)
    if (!('memory' in performance)) {
      return;
    }

    function measureMemory() {
      const { memory } = performance as any;
      setStats({
        jsHeapSizeLimit: memory.jsHeapSizeLimit / BYTES_PER_MB,
        totalJSHeapSize: memory.totalJSHeapSize / BYTES_PER_MB,
        usage: memory.usedJSHeapSize / memory.jsHeapSizeLimit,
        usedJSHeapSize: memory.usedJSHeapSize / BYTES_PER_MB,
      });
    }

    measureMemory();
    const intervalId = setInterval(measureMemory, interval);

    return () => {
      clearInterval(intervalId);
    };
  }, [enabled, interval]);

  return stats;
}
