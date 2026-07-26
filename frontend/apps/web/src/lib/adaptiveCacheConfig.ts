/**
 * Adaptive Cache Configuration
 *
 * Provides intelligent cache TTL management based on:
 * - Data size (larger datasets → shorter TTL)
 * - Update frequency (frequently updated → shorter TTL)
 * - Access patterns (hot data → longer TTL)
 * - Time of day (peak hours → shorter TTL)
 */

import type { DefaultError, UseQueryOptions } from '@tanstack/react-query';

import { logger } from '@/lib/logger';

const SECOND_IN_MS = Number('1000');
const MINUTE_IN_MS = Number('60') * SECOND_IN_MS;
const HOUR_IN_MS = Number('60') * MINUTE_IN_MS;

const KILOBYTE = Number('1024');
const HUNDRED_KILOBYTES = Number('100') * KILOBYTE;
const MEGABYTE = KILOBYTE * KILOBYTE;
const TEN_MEGABYTES = Number('10') * MEGABYTE;

const ONE_PER_HOUR = Number('1');
const FIVE_PER_HOUR = Number('5');
const TEN_PER_HOUR = Number('10');
const TWENTY_PER_HOUR = Number('20');
const HUNDRED_PER_HOUR = Number('100');

const PEAK_START_HOUR = Number('9');
const PEAK_END_HOUR = Number('18');
const NIGHT_START_HOUR = Number('23');
const NIGHT_END_HOUR = Number('6');

const MULTIPLIER_TINY = Number('1.5');
const MULTIPLIER_SMALL = Number('1.2');
const MULTIPLIER_BASELINE = Number('1.0');
const MULTIPLIER_LARGE = Number('0.7');
const MULTIPLIER_HUGE = Number('0.4');
const MULTIPLIER_RARELY = Number('1.8');
const MULTIPLIER_FREQUENT = Number('0.6');
const MULTIPLIER_VERY_FREQUENT = Number('0.3');
const MULTIPLIER_COLD = Number('0.8');
const MULTIPLIER_HOT = Number('1.3');
const MULTIPLIER_VERY_HOT = Number('1.5');

const REALTIME_REFETCH_INTERVAL_MS = Number('5') * SECOND_IN_MS;

export interface CacheMetrics {
  /** Size of the data in bytes */
  dataSize: number;
  /** Number of updates per hour */
  updateFrequency: number;
  /** Number of accesses per hour */
  accessFrequency: number;
  /** Timestamp of last metric collection */
  timestamp: number;
}

export interface CacheConfig {
  staleTime: number;
  gcTime: number;
  refetchOnMount?: boolean;
  refetchOnWindowFocus?: boolean;
  refetchOnReconnect?: boolean;
  refetchInterval?: number;
}

/**
 * Minimum and maximum TTL values (in milliseconds)
 */
export const TTL_BOUNDS = {
  MAX_GC_TIME: HOUR_IN_MS,
  MAX_STALE_TIME: Number('30') * MINUTE_IN_MS,
  MIN_GC_TIME: ONE_PER_HOUR * MINUTE_IN_MS,
  MIN_STALE_TIME: Number('30') * SECOND_IN_MS,
};

/**
 * Size categories for data-aware caching
 */
export enum DataSizeCategory {
  TINY = 'tiny', // < 1 KB
  SMALL = 'small', // 1 KB - 100 KB
  MEDIUM = 'medium', // 100 KB - 1 MB
  LARGE = 'large', // 1 MB - 10 MB
  HUGE = 'huge', // > 10 MB
}

/**
 * Determine data size category
 */
export const getDataSizeCategory = (sizeBytes: number): DataSizeCategory => {
  if (sizeBytes < KILOBYTE) return DataSizeCategory.TINY;
  if (sizeBytes < HUNDRED_KILOBYTES) return DataSizeCategory.SMALL;
  if (sizeBytes < MEGABYTE) return DataSizeCategory.MEDIUM;
  if (sizeBytes < TEN_MEGABYTES) return DataSizeCategory.LARGE;
  return DataSizeCategory.HUGE;
};

/**
 * Size-based TTL multipliers
 * Larger datasets have more computational overhead, deserving shorter TTL
 */
const SIZE_MULTIPLIERS: Record<DataSizeCategory, number> = {
  [DataSizeCategory.HUGE]: MULTIPLIER_HUGE, // Large graphs, keep fresh
  [DataSizeCategory.LARGE]: MULTIPLIER_LARGE,
  [DataSizeCategory.MEDIUM]: MULTIPLIER_BASELINE, // Baseline
  [DataSizeCategory.SMALL]: MULTIPLIER_SMALL,
  [DataSizeCategory.TINY]: MULTIPLIER_TINY, // Small overhead, cache longer
};

/**
 * Update frequency categories
 */
export enum UpdateFrequencyCategory {
  RARELY = 'rarely', // < 1 update/hour
  INFREQUENT = 'infrequent', // 1-5 updates/hour
  MODERATE = 'moderate', // 5-20 updates/hour
  FREQUENT = 'frequent', // 20-100 updates/hour
  VERY_FREQUENT = 'veryFrequent', // > 100 updates/hour
}

/**
 * Determine update frequency category
 */
export const getUpdateFrequencyCategory = (updatesPerHour: number): UpdateFrequencyCategory => {
  if (updatesPerHour < ONE_PER_HOUR) return UpdateFrequencyCategory.RARELY;
  if (updatesPerHour < FIVE_PER_HOUR) return UpdateFrequencyCategory.INFREQUENT;
  if (updatesPerHour < TWENTY_PER_HOUR) return UpdateFrequencyCategory.MODERATE;
  if (updatesPerHour < HUNDRED_PER_HOUR) return UpdateFrequencyCategory.FREQUENT;
  return UpdateFrequencyCategory.VERY_FREQUENT;
};

/**
 * Update frequency TTL multipliers
 * Frequently updated data needs shorter TTL to avoid stale data
 */
const UPDATE_FREQUENCY_MULTIPLIERS: Record<UpdateFrequencyCategory, number> = {
  [UpdateFrequencyCategory.FREQUENT]: MULTIPLIER_FREQUENT,
  [UpdateFrequencyCategory.INFREQUENT]: MULTIPLIER_TINY,
  [UpdateFrequencyCategory.MODERATE]: MULTIPLIER_BASELINE, // Baseline
  [UpdateFrequencyCategory.RARELY]: MULTIPLIER_RARELY, // Rarely changes, cache much longer
  [UpdateFrequencyCategory.VERY_FREQUENT]: MULTIPLIER_VERY_FREQUENT, // Very frequently updated, keep fresh
};

/**
 * Access frequency categories
 */
export enum AccessFrequencyCategory {
  COLD = 'cold', // < 1 access/hour
  WARM = 'warm', // 1-10 accesses/hour
  HOT = 'hot', // 10-100 accesses/hour
  VERY_HOT = 'veryHot', // > 100 accesses/hour
}

/**
 * Determine access frequency category
 */
export const getAccessFrequencyCategory = (accessesPerHour: number): AccessFrequencyCategory => {
  if (accessesPerHour < ONE_PER_HOUR) return AccessFrequencyCategory.COLD;
  if (accessesPerHour < TEN_PER_HOUR) return AccessFrequencyCategory.WARM;
  if (accessesPerHour < HUNDRED_PER_HOUR) return AccessFrequencyCategory.HOT;
  return AccessFrequencyCategory.VERY_HOT;
};

/**
 * Access frequency TTL multipliers
 * Hot data that's accessed frequently can have longer TTL
 */
const ACCESS_FREQUENCY_MULTIPLIERS: Record<AccessFrequencyCategory, number> = {
  [AccessFrequencyCategory.COLD]: MULTIPLIER_COLD, // Cold data, shorter TTL
  [AccessFrequencyCategory.HOT]: MULTIPLIER_HOT, // Hot data, cache longer
  [AccessFrequencyCategory.VERY_HOT]: MULTIPLIER_VERY_HOT, // Very hot, much longer TTL
  [AccessFrequencyCategory.WARM]: MULTIPLIER_BASELINE, // Baseline
};

/**
 * Time-of-day based adjustments
 * During peak hours, use shorter TTLs to reduce cache staleness
 */
const getTimeOfDayMultiplier = (): number => {
  const hour = new Date().getHours();

  // Peak hours: 9 AM - 6 PM
  if (hour >= PEAK_START_HOUR && hour < PEAK_END_HOUR) {
    return MULTIPLIER_COLD; // Shorter TTL during peak hours
  }

  // Night hours: 11 PM - 6 AM
  if (hour >= NIGHT_START_HOUR || hour < NIGHT_END_HOUR) {
    return MULTIPLIER_HOT; // Longer TTL at night
  }

  return MULTIPLIER_BASELINE; // Normal hours
};

/**
 * Calculate adaptive TTL based on data characteristics
 *
 * The calculation considers:
 * 1. Data size (larger = shorter TTL)
 * 2. Update frequency (frequent = shorter TTL)
 * 3. Access frequency (hot = longer TTL)
 * 4. Time of day (peak hours = shorter TTL)
 *
 * @param metrics - Current cache metrics
 * @param baseConfig - Base cache configuration
 * @returns Adapted cache configuration
 */
export const calculateAdaptiveTTL = (
  metrics: CacheMetrics,
  baseConfig: CacheConfig,
): CacheConfig => {
  const sizeCategory = getDataSizeCategory(metrics.dataSize);
  const updateCategory = getUpdateFrequencyCategory(metrics.updateFrequency);
  const accessCategory = getAccessFrequencyCategory(metrics.accessFrequency);
  const timeMultiplier = getTimeOfDayMultiplier();

  // Calculate combined multiplier
  const sizeMultiplier = SIZE_MULTIPLIERS[sizeCategory];
  const updateMultiplier = UPDATE_FREQUENCY_MULTIPLIERS[updateCategory];
  const accessMultiplier = ACCESS_FREQUENCY_MULTIPLIERS[accessCategory];

  // Combine multipliers (geometric mean for balanced impact)
  const combinedMultiplier =
    Math.cbrt(sizeMultiplier * updateMultiplier * accessMultiplier) * timeMultiplier;

  // Apply bounds to prevent excessive caching or under-caching
  const newStaleTime = Math.max(
    TTL_BOUNDS.MIN_STALE_TIME,
    Math.min(TTL_BOUNDS.MAX_STALE_TIME, Math.round(baseConfig.staleTime * combinedMultiplier)),
  );

  const newGcTime = Math.max(
    TTL_BOUNDS.MIN_GC_TIME,
    Math.min(TTL_BOUNDS.MAX_GC_TIME, Math.round(baseConfig.gcTime * combinedMultiplier)),
  );

  return {
    ...baseConfig,
    gcTime: newGcTime,
    staleTime: newStaleTime,
  };
};

/**
 * Predefined adaptive configurations for common scenarios
 */
export const ADAPTIVE_CONFIGS = {
  /**
   * Adaptive dynamic data (frequently changes)
   * Base: 30 seconds stale, 5 minutes GC
   * Adjusts based on update frequency
   */
  dynamicAdaptive: (metrics: CacheMetrics): CacheConfig => {
    const base: CacheConfig = {
      gcTime: Number('5') * MINUTE_IN_MS,
      refetchOnMount: true,
      refetchOnReconnect: true,
      refetchOnWindowFocus: false,
      staleTime: Number('30') * SECOND_IN_MS,
    };
    return calculateAdaptiveTTL(metrics, base);
  },

  /**
   * Adaptive graph data (computationally expensive)
   * Base: 5 minutes stale, 15 minutes GC
   * Adjusts based on graph size and edit frequency
   */
  graphAdaptive: (metrics: CacheMetrics): CacheConfig => {
    const base: CacheConfig = {
      gcTime: Number('15') * MINUTE_IN_MS,
      refetchOnMount: false,
      refetchOnReconnect: false,
      refetchOnWindowFocus: false,
      staleTime: Number('5') * MINUTE_IN_MS,
    };
    return calculateAdaptiveTTL(metrics, base);
  },

  /**
   * Real-time data (always fresh)
   * Base: No stale time, minimal GC
   * Does not adapt (must stay fresh)
   */
  realtime: (): CacheConfig => ({
    gcTime: MINUTE_IN_MS,
    refetchInterval: REALTIME_REFETCH_INTERVAL_MS,
    refetchOnMount: true,
    refetchOnReconnect: true,
    refetchOnWindowFocus: true,
    staleTime: 0,
  }),

  /**
   * Adaptive static data (rarely changes)
   * Base: 10 minutes stale, 30 minutes GC
   * Adjusts based on size and access patterns
   */
  staticAdaptive: (metrics: CacheMetrics): CacheConfig => {
    const base: CacheConfig = {
      gcTime: Number('30') * MINUTE_IN_MS,
      refetchOnMount: false,
      refetchOnReconnect: false,
      refetchOnWindowFocus: false,
      staleTime: Number('10') * MINUTE_IN_MS,
    };
    return calculateAdaptiveTTL(metrics, base);
  },
};

/**
 * Helper to create adaptive query options
 */
export const createAdaptiveQueryOptions = <TData = unknown, TError = DefaultError>(
  metrics: CacheMetrics,
  configType: 'static' | 'dynamic' | 'graph',
  overrides?: Partial<CacheConfig>,
): UseQueryOptions<TData, TError> => {
  let config: CacheConfig;

  switch (configType) {
    case 'static':
      config = ADAPTIVE_CONFIGS.staticAdaptive(metrics);
      break;
    case 'dynamic':
      config = ADAPTIVE_CONFIGS.dynamicAdaptive(metrics);
      break;
    case 'graph':
      config = ADAPTIVE_CONFIGS.graphAdaptive(metrics);
      break;
  }

  return {
    ...config,
    ...overrides,
  } as UseQueryOptions<TData, TError>;
};

/**
 * Log adaptive cache decision for debugging
 */
export const logAdaptiveCacheDecision = (
  metrics: CacheMetrics,
  config: CacheConfig,
  reason: string,
): void => {
  if (process.env['NODE_ENV'] === 'development') {
    const sizeCategory = getDataSizeCategory(metrics.dataSize);
    const updateCategory = getUpdateFrequencyCategory(metrics.updateFrequency);
    const accessCategory = getAccessFrequencyCategory(metrics.accessFrequency);

    logger.debug('[AdaptiveCache]', {
      accessFrequency: `${metrics.accessFrequency}/hour`,
      dataSize: `${(metrics.dataSize / KILOBYTE).toFixed(1)}KB`,
      gcTime: `${(config.gcTime / MINUTE_IN_MS).toFixed(1)}m`,
      reason,
      staleTime: `${(config.staleTime / SECOND_IN_MS).toFixed(1)}s`,
      sizeCategory,
      updateCategory,
      updateFrequency: `${metrics.updateFrequency}/hour`,
    });
  }
};
