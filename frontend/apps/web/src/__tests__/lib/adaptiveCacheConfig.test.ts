import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  AccessFrequencyCategory,
  ADAPTIVE_CONFIGS,
  type CacheConfig,
  type CacheMetrics,
  calculateAdaptiveTTL,
  DataSizeCategory,
  getAccessFrequencyCategory,
  getDataSizeCategory,
  getUpdateFrequencyCategory,
  logAdaptiveCacheDecision,
  TTL_BOUNDS,
  UpdateFrequencyCategory,
} from '@/lib/adaptiveCacheConfig';
import { logger } from '@/lib/logger';

describe('Adaptive Cache Configuration', () => {
  describe('getDataSizeCategory', () => {
    it('should categorize tiny data correctly', () => {
      expect(getDataSizeCategory(512)).toBe(DataSizeCategory.TINY);
      expect(getDataSizeCategory(1000)).toBe(DataSizeCategory.TINY);
    });

    it('should categorize small data correctly', () => {
      expect(getDataSizeCategory(2048)).toBe(DataSizeCategory.SMALL);
      expect(getDataSizeCategory(50 * 1024)).toBe(DataSizeCategory.SMALL);
    });

    it('should categorize medium data correctly', () => {
      expect(getDataSizeCategory(200 * 1024)).toBe(DataSizeCategory.MEDIUM);
      expect(getDataSizeCategory(500 * 1024)).toBe(DataSizeCategory.MEDIUM);
    });

    it('should categorize large data correctly', () => {
      expect(getDataSizeCategory(2 * 1024 * 1024)).toBe(DataSizeCategory.LARGE);
      expect(getDataSizeCategory(5 * 1024 * 1024)).toBe(DataSizeCategory.LARGE);
    });

    it('should categorize huge data correctly', () => {
      expect(getDataSizeCategory(15 * 1024 * 1024)).toBe(DataSizeCategory.HUGE);
      expect(getDataSizeCategory(100 * 1024 * 1024)).toBe(DataSizeCategory.HUGE);
    });
  });

  describe('getUpdateFrequencyCategory', () => {
    it('should categorize rare updates correctly', () => {
      expect(getUpdateFrequencyCategory(0)).toBe(UpdateFrequencyCategory.RARELY);
      expect(getUpdateFrequencyCategory(0.5)).toBe(UpdateFrequencyCategory.RARELY);
    });

    it('should categorize infrequent updates correctly', () => {
      expect(getUpdateFrequencyCategory(2)).toBe(UpdateFrequencyCategory.INFREQUENT);
      expect(getUpdateFrequencyCategory(4)).toBe(UpdateFrequencyCategory.INFREQUENT);
    });

    it('should categorize moderate updates correctly', () => {
      expect(getUpdateFrequencyCategory(10)).toBe(UpdateFrequencyCategory.MODERATE);
      expect(getUpdateFrequencyCategory(15)).toBe(UpdateFrequencyCategory.MODERATE);
    });

    it('should categorize frequent updates correctly', () => {
      expect(getUpdateFrequencyCategory(50)).toBe(UpdateFrequencyCategory.FREQUENT);
      expect(getUpdateFrequencyCategory(80)).toBe(UpdateFrequencyCategory.FREQUENT);
    });

    it('should categorize very frequent updates correctly', () => {
      expect(getUpdateFrequencyCategory(150)).toBe(UpdateFrequencyCategory.VERY_FREQUENT);
      expect(getUpdateFrequencyCategory(500)).toBe(UpdateFrequencyCategory.VERY_FREQUENT);
    });
  });

  describe('getAccessFrequencyCategory', () => {
    it('should categorize cold access correctly', () => {
      expect(getAccessFrequencyCategory(0)).toBe(AccessFrequencyCategory.COLD);
      expect(getAccessFrequencyCategory(0.5)).toBe(AccessFrequencyCategory.COLD);
    });

    it('should categorize warm access correctly', () => {
      expect(getAccessFrequencyCategory(5)).toBe(AccessFrequencyCategory.WARM);
      expect(getAccessFrequencyCategory(9)).toBe(AccessFrequencyCategory.WARM);
    });

    it('should categorize hot access correctly', () => {
      expect(getAccessFrequencyCategory(50)).toBe(AccessFrequencyCategory.HOT);
      expect(getAccessFrequencyCategory(99)).toBe(AccessFrequencyCategory.HOT);
    });

    it('should categorize very hot access correctly', () => {
      expect(getAccessFrequencyCategory(100)).toBe(AccessFrequencyCategory.VERY_HOT);
      expect(getAccessFrequencyCategory(500)).toBe(AccessFrequencyCategory.VERY_HOT);
    });
  });

  describe('calculateAdaptiveTTL', () => {
    const baseConfig: CacheConfig = {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 15 * 60 * 1000, // 15 minutes
    };

    it('should reduce TTL for large datasets', () => {
      const largeData: CacheMetrics = {
        dataSize: 10 * 1024 * 1024, // 10 MB (HUGE)
        updateFrequency: 5, // Moderate
        accessFrequency: 20, // Hot
        timestamp: Date.now(),
      };

      const result = calculateAdaptiveTTL(largeData, baseConfig);
      expect(result.staleTime).toBeLessThan(baseConfig.staleTime);
    });

    it('should increase TTL for small datasets', () => {
      const smallData: CacheMetrics = {
        dataSize: 500, // TINY
        updateFrequency: 0.5, // Rarely updated
        accessFrequency: 5, // Warm
        timestamp: Date.now(),
      };

      const result = calculateAdaptiveTTL(smallData, baseConfig);
      expect(result.staleTime).toBeGreaterThan(baseConfig.staleTime);
    });

    it('should reduce TTL for frequently updated data', () => {
      const frequentUpdates: CacheMetrics = {
        dataSize: 500 * 1024, // MEDIUM
        updateFrequency: 100, // Very frequent
        accessFrequency: 50, // Hot
        timestamp: Date.now(),
      };

      const result = calculateAdaptiveTTL(frequentUpdates, baseConfig);
      expect(result.staleTime).toBeLessThan(baseConfig.staleTime);
    });

    it('should increase TTL for rarely updated data', () => {
      const rareUpdates: CacheMetrics = {
        dataSize: 500 * 1024, // MEDIUM
        updateFrequency: 0.5, // Rarely updated
        accessFrequency: 50, // Hot
        timestamp: Date.now(),
      };

      const result = calculateAdaptiveTTL(rareUpdates, baseConfig);
      expect(result.staleTime).toBeGreaterThan(baseConfig.staleTime);
    });

    it('should respect TTL bounds', () => {
      const extremeSmall: CacheMetrics = {
        dataSize: 100, // TINY
        updateFrequency: 0.1, // Rarely updated
        accessFrequency: 100, // Very hot
        timestamp: Date.now(),
      };

      const result = calculateAdaptiveTTL(extremeSmall, baseConfig);
      expect(result.staleTime).toBeLessThanOrEqual(TTL_BOUNDS.MAX_STALE_TIME);
      expect(result.staleTime).toBeGreaterThanOrEqual(TTL_BOUNDS.MIN_STALE_TIME);
      expect(result.gcTime).toBeLessThanOrEqual(TTL_BOUNDS.MAX_GC_TIME);
      expect(result.gcTime).toBeGreaterThanOrEqual(TTL_BOUNDS.MIN_GC_TIME);
    });

    it('should maintain configuration structure', () => {
      const metrics: CacheMetrics = {
        dataSize: 500 * 1024,
        updateFrequency: 5,
        accessFrequency: 50,
        timestamp: Date.now(),
      };

      const result = calculateAdaptiveTTL(metrics, baseConfig);
      expect(result).toHaveProperty('staleTime');
      expect(result).toHaveProperty('gcTime');
      expect(typeof result.staleTime).toBe('number');
      expect(typeof result.gcTime).toBe('number');
    });
  });

  describe('ADAPTIVE_CONFIGS', () => {
    const metrics: CacheMetrics = {
      dataSize: 500 * 1024,
      updateFrequency: 5,
      accessFrequency: 50,
      timestamp: Date.now(),
    };

    it('should provide staticAdaptive configuration', () => {
      const config = ADAPTIVE_CONFIGS.staticAdaptive(metrics);
      expect(config).toHaveProperty('staleTime');
      expect(config).toHaveProperty('gcTime');
      expect(config.refetchOnMount).toBe(false);
      expect(config.refetchOnWindowFocus).toBe(false);
    });

    it('should provide dynamicAdaptive configuration', () => {
      const config = ADAPTIVE_CONFIGS.dynamicAdaptive(metrics);
      expect(config).toHaveProperty('staleTime');
      expect(config).toHaveProperty('gcTime');
      expect(config.refetchOnMount).toBe(true);
      expect(config.refetchOnReconnect).toBe(true);
    });

    it('should provide graphAdaptive configuration', () => {
      const config = ADAPTIVE_CONFIGS.graphAdaptive(metrics);
      expect(config).toHaveProperty('staleTime');
      expect(config).toHaveProperty('gcTime');
      expect(config.refetchOnMount).toBe(false);
      expect(config.refetchOnWindowFocus).toBe(false);
    });

    it('should provide realtime configuration', () => {
      const config = ADAPTIVE_CONFIGS.realtime();
      expect(config.staleTime).toBe(0);
      expect(config.refetchInterval).toBe(5000);
      expect(config.refetchOnMount).toBe(true);
    });
  });

  describe('logAdaptiveCacheDecision', () => {
    beforeEach(() => {
      vi.spyOn(console, 'debug').mockImplementation(() => {});
    });

    afterEach(() => {
      vi.restoreAllMocks();
    });

    it('should not log in production', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      const metrics: CacheMetrics = {
        dataSize: 500 * 1024,
        updateFrequency: 5,
        accessFrequency: 50,
        timestamp: Date.now(),
      };

      const config: CacheConfig = {
        staleTime: 300000,
        gcTime: 900000,
      };

      logAdaptiveCacheDecision(metrics, config, 'test');
      expect(console.debug).not.toHaveBeenCalled();

      process.env.NODE_ENV = originalEnv;
    });

    it('should log in development', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      const metrics: CacheMetrics = {
        dataSize: 500 * 1024,
        updateFrequency: 5,
        accessFrequency: 50,
        timestamp: Date.now(),
      };

      const config: CacheConfig = {
        staleTime: 300000,
        gcTime: 900000,
      };

      logAdaptiveCacheDecision(metrics, config, 'test reason');
      expect(console.debug).toHaveBeenCalledWith(
        '[AdaptiveCache]',
        expect.objectContaining({
          reason: 'test reason',
          sizeCategory: DataSizeCategory.MEDIUM,
          updateCategory: UpdateFrequencyCategory.MODERATE,
          accessCategory: AccessFrequencyCategory.HOT,
        }),
      );

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('Edge cases', () => {
    it('should handle zero metrics', () => {
      const metrics: CacheMetrics = {
        dataSize: 0,
        updateFrequency: 0,
        accessFrequency: 0,
        timestamp: Date.now(),
      };

      const baseConfig: CacheConfig = {
        staleTime: 5 * 60 * 1000,
        gcTime: 15 * 60 * 1000,
      };

      const result = calculateAdaptiveTTL(metrics, baseConfig);
      expect(result.staleTime).toBeGreaterThanOrEqual(TTL_BOUNDS.MIN_STALE_TIME);
      expect(result.staleTime).toBeLessThanOrEqual(TTL_BOUNDS.MAX_STALE_TIME);
    });

    it('should handle very large metrics', () => {
      const metrics: CacheMetrics = {
        dataSize: 1000 * 1024 * 1024, // 1 GB
        updateFrequency: 10000,
        accessFrequency: 10000,
        timestamp: Date.now(),
      };

      const baseConfig: CacheConfig = {
        staleTime: 5 * 60 * 1000,
        gcTime: 15 * 60 * 1000,
      };

      const result = calculateAdaptiveTTL(metrics, baseConfig);
      expect(result.staleTime).toBeGreaterThanOrEqual(TTL_BOUNDS.MIN_STALE_TIME);
      expect(result.staleTime).toBeLessThanOrEqual(TTL_BOUNDS.MAX_STALE_TIME);
    });
  });
});
