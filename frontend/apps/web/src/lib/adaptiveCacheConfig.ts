/**
 * Adaptive Cache Configuration
 *
 * Provides intelligent cache TTL management based on:
 * - Data size (larger datasets → shorter TTL)
 * - Update frequency (frequently updated → shorter TTL)
 * - Access patterns (hot data → longer TTL)
 * - Time of day (peak hours → shorter TTL)
 */

import type { DefaultError, UseQueryOptions } from "@tanstack/react-query";

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
	MIN_STALE_TIME: 30 * 1000, // 30 seconds
	MAX_STALE_TIME: 30 * 60 * 1000, // 30 minutes
	MIN_GC_TIME: 1 * 60 * 1000, // 1 minute
	MAX_GC_TIME: 60 * 60 * 1000, // 1 hour
};

/**
 * Size categories for data-aware caching
 */
export enum DataSizeCategory {
	TINY = "tiny", // < 1 KB
	SMALL = "small", // 1 KB - 100 KB
	MEDIUM = "medium", // 100 KB - 1 MB
	LARGE = "large", // 1 MB - 10 MB
	HUGE = "huge", // > 10 MB
}

/**
 * Determine data size category
 */
export function getDataSizeCategory(sizeBytes: number): DataSizeCategory {
	if (sizeBytes < 1024) return DataSizeCategory.TINY;
	if (sizeBytes < 100 * 1024) return DataSizeCategory.SMALL;
	if (sizeBytes < 1024 * 1024) return DataSizeCategory.MEDIUM;
	if (sizeBytes < 10 * 1024 * 1024) return DataSizeCategory.LARGE;
	return DataSizeCategory.HUGE;
}

/**
 * Size-based TTL multipliers
 * Larger datasets have more computational overhead, deserving shorter TTL
 */
const SIZE_MULTIPLIERS: Record<DataSizeCategory, number> = {
	[DataSizeCategory.TINY]: 1.5, // Small overhead, cache longer
	[DataSizeCategory.SMALL]: 1.2,
	[DataSizeCategory.MEDIUM]: 1.0, // Baseline
	[DataSizeCategory.LARGE]: 0.7,
	[DataSizeCategory.HUGE]: 0.4, // Large graphs, keep fresh
};

/**
 * Update frequency categories
 */
export enum UpdateFrequencyCategory {
	RARELY = "rarely", // < 1 update/hour
	INFREQUENT = "infrequent", // 1-5 updates/hour
	MODERATE = "moderate", // 5-20 updates/hour
	FREQUENT = "frequent", // 20-100 updates/hour
	VERY_FREQUENT = "veryFrequent", // > 100 updates/hour
}

/**
 * Determine update frequency category
 */
export function getUpdateFrequencyCategory(
	updatesPerHour: number,
): UpdateFrequencyCategory {
	if (updatesPerHour < 1) return UpdateFrequencyCategory.RARELY;
	if (updatesPerHour < 5) return UpdateFrequencyCategory.INFREQUENT;
	if (updatesPerHour < 20) return UpdateFrequencyCategory.MODERATE;
	if (updatesPerHour < 100) return UpdateFrequencyCategory.FREQUENT;
	return UpdateFrequencyCategory.VERY_FREQUENT;
}

/**
 * Update frequency TTL multipliers
 * Frequently updated data needs shorter TTL to avoid stale data
 */
const UPDATE_FREQUENCY_MULTIPLIERS: Record<UpdateFrequencyCategory, number> = {
	[UpdateFrequencyCategory.RARELY]: 1.8, // Rarely changes, cache much longer
	[UpdateFrequencyCategory.INFREQUENT]: 1.5,
	[UpdateFrequencyCategory.MODERATE]: 1.0, // Baseline
	[UpdateFrequencyCategory.FREQUENT]: 0.6,
	[UpdateFrequencyCategory.VERY_FREQUENT]: 0.3, // Very frequently updated, keep fresh
};

/**
 * Access frequency categories
 */
export enum AccessFrequencyCategory {
	COLD = "cold", // < 1 access/hour
	WARM = "warm", // 1-10 accesses/hour
	HOT = "hot", // 10-100 accesses/hour
	VERY_HOT = "veryHot", // > 100 accesses/hour
}

/**
 * Determine access frequency category
 */
export function getAccessFrequencyCategory(
	accessesPerHour: number,
): AccessFrequencyCategory {
	if (accessesPerHour < 1) return AccessFrequencyCategory.COLD;
	if (accessesPerHour < 10) return AccessFrequencyCategory.WARM;
	if (accessesPerHour < 100) return AccessFrequencyCategory.HOT;
	return AccessFrequencyCategory.VERY_HOT;
}

/**
 * Access frequency TTL multipliers
 * Hot data that's accessed frequently can have longer TTL
 */
const ACCESS_FREQUENCY_MULTIPLIERS: Record<AccessFrequencyCategory, number> = {
	[AccessFrequencyCategory.COLD]: 0.8, // Cold data, shorter TTL
	[AccessFrequencyCategory.WARM]: 1.0, // Baseline
	[AccessFrequencyCategory.HOT]: 1.3, // Hot data, cache longer
	[AccessFrequencyCategory.VERY_HOT]: 1.5, // Very hot, much longer TTL
};

/**
 * Time-of-day based adjustments
 * During peak hours, use shorter TTLs to reduce cache staleness
 */
function getTimeOfDayMultiplier(): number {
	const hour = new Date().getHours();

	// Peak hours: 9 AM - 6 PM
	if (hour >= 9 && hour < 18) {
		return 0.8; // Shorter TTL during peak hours
	}

	// Night hours: 11 PM - 6 AM
	if (hour >= 23 || hour < 6) {
		return 1.3; // Longer TTL at night
	}

	return 1.0; // Normal hours
}

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
export function calculateAdaptiveTTL(
	metrics: CacheMetrics,
	baseConfig: CacheConfig,
): CacheConfig {
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
		Math.cbrt(sizeMultiplier * updateMultiplier * accessMultiplier) *
		timeMultiplier;

	// Apply bounds to prevent excessive caching or under-caching
	const newStaleTime = Math.max(
		TTL_BOUNDS.MIN_STALE_TIME,
		Math.min(
			TTL_BOUNDS.MAX_STALE_TIME,
			Math.round(baseConfig.staleTime * combinedMultiplier),
		),
	);

	const newGcTime = Math.max(
		TTL_BOUNDS.MIN_GC_TIME,
		Math.min(
			TTL_BOUNDS.MAX_GC_TIME,
			Math.round(baseConfig.gcTime * combinedMultiplier),
		),
	);

	return {
		...baseConfig,
		staleTime: newStaleTime,
		gcTime: newGcTime,
	};
}

/**
 * Predefined adaptive configurations for common scenarios
 */
export const ADAPTIVE_CONFIGS = {
	/**
	 * Adaptive static data (rarely changes)
	 * Base: 10 minutes stale, 30 minutes GC
	 * Adjusts based on size and access patterns
	 */
	staticAdaptive: (metrics: CacheMetrics): CacheConfig => {
		const base: CacheConfig = {
			staleTime: 10 * 60 * 1000,
			gcTime: 30 * 60 * 1000,
			refetchOnMount: false,
			refetchOnWindowFocus: false,
			refetchOnReconnect: false,
		};
		return calculateAdaptiveTTL(metrics, base);
	},

	/**
	 * Adaptive dynamic data (frequently changes)
	 * Base: 30 seconds stale, 5 minutes GC
	 * Adjusts based on update frequency
	 */
	dynamicAdaptive: (metrics: CacheMetrics): CacheConfig => {
		const base: CacheConfig = {
			staleTime: 30 * 1000,
			gcTime: 5 * 60 * 1000,
			refetchOnMount: true,
			refetchOnWindowFocus: false,
			refetchOnReconnect: true,
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
			staleTime: 5 * 60 * 1000,
			gcTime: 15 * 60 * 1000,
			refetchOnMount: false,
			refetchOnWindowFocus: false,
			refetchOnReconnect: false,
		};
		return calculateAdaptiveTTL(metrics, base);
	},

	/**
	 * Real-time data (always fresh)
	 * Base: No stale time, minimal GC
	 * Does not adapt (must stay fresh)
	 */
	realtime: (): CacheConfig => ({
		staleTime: 0,
		gcTime: 1 * 60 * 1000,
		refetchInterval: 5000,
		refetchOnMount: true,
		refetchOnWindowFocus: true,
		refetchOnReconnect: true,
	}),
};

/**
 * Helper to create adaptive query options
 */
export function createAdaptiveQueryOptions<
	TData = unknown,
	TError = DefaultError,
>(
	metrics: CacheMetrics,
	configType: "static" | "dynamic" | "graph",
	overrides?: Partial<CacheConfig>,
): UseQueryOptions<TData, TError> {
	let config: CacheConfig;

	switch (configType) {
		case "static":
			config = ADAPTIVE_CONFIGS.staticAdaptive(metrics);
			break;
		case "dynamic":
			config = ADAPTIVE_CONFIGS.dynamicAdaptive(metrics);
			break;
		case "graph":
			config = ADAPTIVE_CONFIGS.graphAdaptive(metrics);
			break;
	}

	return {
		...config,
		...overrides,
	} as UseQueryOptions<TData, TError>;
}

/**
 * Log adaptive cache decision for debugging
 */
export function logAdaptiveCacheDecision(
	metrics: CacheMetrics,
	config: CacheConfig,
	reason: string,
): void {
	if (process.env.NODE_ENV === "development") {
		const sizeCategory = getDataSizeCategory(metrics.dataSize);
		const updateCategory = getUpdateFrequencyCategory(metrics.updateFrequency);
		const accessCategory = getAccessFrequencyCategory(metrics.accessFrequency);

		console.debug("[AdaptiveCache]", {
			reason,
			sizeCategory,
			updateCategory,
			accessCategory,
			staleTime: `${(config.staleTime / 1000).toFixed(1)}s`,
			gcTime: `${(config.gcTime / 60000).toFixed(1)}m`,
			dataSize: `${(metrics.dataSize / 1024).toFixed(1)}KB`,
			updateFrequency: `${metrics.updateFrequency}/hour`,
			accessFrequency: `${metrics.accessFrequency}/hour`,
		});
	}
}
