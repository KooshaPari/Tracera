/**
 * Data Transformation Worker
 *
 * Handles CPU-intensive data operations:
 * - Large dataset filtering and sorting
 * - Complex data aggregations
 * - Data normalization and transformation
 * - Statistical computations
 */

import { expose } from "comlink";

export interface TransformOptions {
	type: "filter" | "sort" | "aggregate" | "normalize" | "deduplicate";
	field?: string;
	predicate?: string; // Serialized function
	direction?: "asc" | "desc";
	groupBy?: string;
	aggregation?: "sum" | "avg" | "min" | "max" | "count";
}

export type ProgressCallback = (progress: number) => void;

/**
 * Filter large dataset
 */
function filterData<T extends Record<string, any>>(
	data: T[],
	field: string,
	predicate: (value: any) => boolean,
	onProgress?: ProgressCallback,
): T[] {
	const result: T[] = [];
	const chunkSize = 1000;

	for (let i = 0; i < data.length; i += chunkSize) {
		const chunk = data.slice(i, Math.min(i + chunkSize, data.length));

		for (const item of chunk) {
			if (predicate(item[field])) {
				result.push(item);
			}
		}

		onProgress?.(((i + chunkSize) / data.length) * 100);
	}

	onProgress?.(100);
	return result;
}

/**
 * Sort large dataset
 */
function sortData<T extends Record<string, any>>(
	data: T[],
	field: string,
	direction: "asc" | "desc" = "asc",
	onProgress?: ProgressCallback,
): T[] {
	onProgress?.(0);

	const sorted = [...data].toSorted((a, b) => {
		const aVal = a[field];
		const bVal = b[field];

		if (aVal === bVal) {
			return 0;
		}

		const comparison = aVal < bVal ? -1 : 1;
		return direction === "asc" ? comparison : -comparison;
	});

	onProgress?.(100);
	return sorted;
}

/**
 * Aggregate data by field
 */
function aggregateData<T extends Record<string, any>>(
	data: T[],
	groupByField: string,
	aggregateField: string,
	aggregationType: "sum" | "avg" | "min" | "max" | "count",
	onProgress?: ProgressCallback,
): Record<string, number> {
	onProgress?.(0);

	const groups = new Map<string, number[]>();

	// Group data
	for (let i = 0; i < data.length; i += 1) {
		const item = data[i];
		const groupKey = String(item[groupByField]);

		if (!groups.has(groupKey)) {
			groups.set(groupKey, []);
		}

		const value = Number(item[aggregateField]);
		if (!isNaN(value)) {
			groups.get(groupKey)!.push(value);
		}

		if (i % 1000 === 0) {
			onProgress?.((i / data.length) * 50);
		}
	}

	onProgress?.(50);

	// Perform aggregation
	const result: Record<string, number> = {};
	let processed = 0;

	for (const [key, values] of groups) {
		if (values.length === 0) {
			result[key] = 0;
			continue;
		}

		switch (aggregationType) {
			case "sum": {
				result[key] = values.reduce((a, b) => a + b, 0);
				break;
			}
			case "avg": {
				result[key] = values.reduce((a, b) => a + b, 0) / values.length;
				break;
			}
			case "min": {
				result[key] = Math.min(...values);
				break;
			}
			case "max": {
				result[key] = Math.max(...values);
				break;
			}
			case "count": {
				result[key] = values.length;
				break;
			}
		}

		processed += 1;
		onProgress?.(50 + (processed / groups.size) * 50);
	}

	onProgress?.(100);
	return result;
}

/**
 * Normalize data (scale to 0-1 range)
 */
function normalizeData<T extends Record<string, any>>(
	data: T[],
	field: string,
	onProgress?: ProgressCallback,
): T[] {
	onProgress?.(0);

	// Find min and max
	let min = Infinity;
	let max = -Infinity;

	for (const item of data) {
		const value = Number(item[field]);
		if (!isNaN(value)) {
			min = Math.min(min, value);
			max = Math.max(max, value);
		}
	}

	onProgress?.(30);

	// Normalize
	const range = max - min || 1;
	const result = data.map((item, i) => {
		const value = Number(item[field]);
		const normalized = isNaN(value) ? 0 : (value - min) / range;

		if (i % 1000 === 0) {
			onProgress?.(30 + (i / data.length) * 70);
		}

		return {
			...item,
			[`${field}_normalized`]: normalized,
		};
	});

	onProgress?.(100);
	return result;
}

/**
 * Deduplicate data by field
 */
function deduplicateData<T extends Record<string, any>>(
	data: T[],
	field: string,
	onProgress?: ProgressCallback,
): T[] {
	onProgress?.(0);

	const seen = new Set<any>();
	const result: T[] = [];

	for (let i = 0; i < data.length; i += 1) {
		const item = data[i];
		const value = item[field];

		if (!seen.has(value)) {
			seen.add(value);
			result.push(item);
		}

		if (i % 1000 === 0) {
			onProgress?.((i / data.length) * 100);
		}
	}

	onProgress?.(100);
	return result;
}

/**
 * Calculate statistics for a numeric field
 */
function calculateStatistics(
	data: Record<string, any>[],
	field: string,
	onProgress?: ProgressCallback,
): {
	count: number;
	sum: number;
	mean: number;
	median: number;
	stdDev: number;
	min: number;
	max: number;
} {
	onProgress?.(0);

	const values: number[] = [];

	for (const item of data) {
		const value = Number(item[field]);
		if (!isNaN(value)) {
			values.push(value);
		}
	}

	onProgress?.(30);

	if (values.length === 0) {
		return {
			count: 0,
			max: 0,
			mean: 0,
			median: 0,
			min: 0,
			stdDev: 0,
			sum: 0,
		};
	}

	const count = values.length;
	const sum = values.reduce((a, b) => a + b, 0);
	const mean = sum / count;

	onProgress?.(50);

	// Median
	const sorted = [...values].toSorted((a, b) => a - b);
	const median =
		count % 2 === 0
			? (sorted[count / 2 - 1] + sorted[count / 2]) / 2
			: sorted[Math.floor(count / 2)];

	onProgress?.(70);

	// Standard deviation
	const squaredDiffs = values.map((v) => Math.pow(v - mean, 2));
	const variance = squaredDiffs.reduce((a, b) => a + b, 0) / count;
	const stdDev = Math.sqrt(variance);

	onProgress?.(90);

	const min = Math.min(...values);
	const max = Math.max(...values);

	onProgress?.(100);

	return {
		count,
		max,
		mean,
		median,
		min,
		stdDev,
		sum,
	};
}

/**
 * Pivot data (transform rows to columns)
 */
function pivotData<T extends Record<string, any>>(
	data: T[],
	rowField: string,
	columnField: string,
	valueField: string,
	onProgress?: ProgressCallback,
): Record<string, Record<string, any>> {
	onProgress?.(0);

	const result: Record<string, Record<string, any>> = {};

	for (let i = 0; i < data.length; i += 1) {
		const item = data[i];
		const rowKey = String(item[rowField]);
		const colKey = String(item[columnField]);
		const value = item[valueField];

		if (!result[rowKey]) {
			result[rowKey] = {};
		}

		result[rowKey][colKey] = value;

		if (i % 1000 === 0) {
			onProgress?.((i / data.length) * 100);
		}
	}

	onProgress?.(100);
	return result;
}

/**
 * Join two datasets
 */
function joinData<T extends Record<string, any>, U extends Record<string, any>>(
	left: T[],
	right: U[],
	leftKey: string,
	rightKey: string,
	joinType: "inner" | "left" | "right" | "outer" = "inner",
	onProgress?: ProgressCallback,
): (T & U)[] {
	onProgress?.(0);

	// Build index for right table
	const rightIndex = new Map<any, U[]>();
	for (const item of right) {
		const key = item[rightKey];
		if (!rightIndex.has(key)) {
			rightIndex.set(key, []);
		}
		rightIndex.get(key)!.push(item);
	}

	onProgress?.(30);

	const result: (T & U)[] = [];

	// Join
	for (let i = 0; i < left.length; i += 1) {
		const leftItem = left[i];
		const key = leftItem[leftKey];
		const rightItems = rightIndex.get(key) || [];

		if (rightItems.length > 0) {
			for (const rightItem of rightItems) {
				result.push({ ...leftItem, ...rightItem });
			}
		} else if (joinType === "left" || joinType === "outer") {
			result.push({ ...leftItem } as T & U);
		}

		if (i % 1000 === 0) {
			onProgress?.(30 + (i / left.length) * 70);
		}
	}

	onProgress?.(100);
	return result;
}

// Worker API
const api = {
	aggregateData,
	calculateStatistics,
	deduplicateData,
	filterData,
	joinData,
	normalizeData,
	pivotData,
	sortData,
};

expose(api);

export type DataTransformWorkerAPI = typeof api;
