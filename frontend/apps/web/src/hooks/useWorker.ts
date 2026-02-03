/**
 * UseWorker Hook
 *
 * React hook for using Web Workers with Comlink integration
 * Provides type-safe worker communication with automatic cleanup
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { proxy, wrap } from "comlink";
import type { Remote } from "comlink";

export interface UseWorkerOptions {
	autoTerminate?: boolean;
	terminateTimeout?: number;
}

export interface WorkerStatus {
	isLoading: boolean;
	isReady: boolean;
	error: Error | null;
	progress: number;
}

/**
 * Hook for using a Web Worker with Comlink
 *
 * @param workerFactory - Function that creates the worker
 * @param options - Worker options
 * @returns Worker API, status, and control functions
 */
export function useWorker<T extends object>(
	workerFactory: () => Worker,
	options: UseWorkerOptions = {},
): {
	worker: Remote<T> | null;
	status: WorkerStatus;
	terminate: () => void;
	reset: () => void;
} {
	const workerRef = useRef<Worker | null>(null);
	const apiRef = useRef<Remote<T> | null>(null);
	const terminateTimeoutRef = useRef<number | null>(null);

	const [status, setStatus] = useState<WorkerStatus>({
		error: null,
		isLoading: true,
		isReady: false,
		progress: 0,
	});

	const { autoTerminate = true, terminateTimeout = 30_000 } = options;

	// Initialize worker
	useEffect(() => {
		let mounted = true;

		const initWorker = async () => {
			try {
				setStatus((prev) => ({ ...prev, isLoading: true, error: null }));

				// Create worker
				const worker = workerFactory();
				workerRef.current = worker;

				// Wrap with Comlink
				const api = wrap<T>(worker);
				apiRef.current = api;

				if (mounted) {
					setStatus({
						error: null,
						isLoading: false,
						isReady: true,
						progress: 0,
					});
				}
			} catch (error) {
				if (mounted) {
					setStatus({
						error: error instanceof Error ? error : new Error(String(error)),
						isLoading: false,
						isReady: false,
						progress: 0,
					});
				}
			}
		};

		undefined;

		return () => {
			mounted = false;
			if (workerRef.current) {
				workerRef.current.terminate();
				workerRef.current = null;
				apiRef.current = null;
			}
			if (terminateTimeoutRef.current) {
				clearTimeout(terminateTimeoutRef.current);
			}
		};
	}, [workerFactory]);

	// Auto-terminate on inactivity
	useEffect(() => {
		if (!autoTerminate || !workerRef.current) {
			return;
		}

		// Reset timeout on any activity
		if (terminateTimeoutRef.current) {
			clearTimeout(terminateTimeoutRef.current);
		}

		terminateTimeoutRef.current = globalThis.setTimeout(() => {
			if (workerRef.current) {
				workerRef.current.terminate();
				workerRef.current = null;
				apiRef.current = null;
				setStatus((prev) => ({ ...prev, isReady: false }));
			}
		}, terminateTimeout);

		return () => {
			if (terminateTimeoutRef.current) {
				clearTimeout(terminateTimeoutRef.current);
			}
		};
	}, [autoTerminate, terminateTimeout, status.isReady]);

	// Terminate worker
	const terminate = useCallback(() => {
		if (workerRef.current) {
			workerRef.current.terminate();
			workerRef.current = null;
			apiRef.current = null;
			setStatus((prev) => ({ ...prev, isReady: false }));
		}
	}, []);

	// Reset worker (terminate and reinitialize)
	const reset = useCallback(() => {
		terminate();
		// Reinitialize will happen via useEffect
	}, [terminate]);

	return {
		reset,
		status,
		terminate,
		worker: apiRef.current,
	};
}

/**
 * Hook for using a worker with progress tracking
 */
export function useWorkerWithProgress<T extends object>(
	workerFactory: () => Worker,
	options: UseWorkerOptions = {},
) {
	const { worker, status, terminate, reset } = useWorker<T>(
		workerFactory,
		options,
	);
	const [progress, setProgress] = useState(0);

	// Create progress callback proxy
	const createProgressCallback = useCallback(
		() =>
			proxy((value: number) => {
				setProgress(value);
			}),
		[],
	);

	return {
		createProgressCallback,
		reset,
		status: { ...status, progress },
		terminate,
		worker,
	};
}

/**
 * Hook for feature detection
 */
export function useWorkerSupport() {
	const [supported, setSupported] = useState(false);
	const [checked, setChecked] = useState(false);

	useEffect(() => {
		const checkSupport = () => {
			const hasWorker = typeof Worker !== "undefined";
			//       Const _hasSharedArrayBuffer = typeof SharedArrayBuffer !== 'undefined';

			setSupported(hasWorker);
			setChecked(true);

			if (!hasWorker) {
			}
		};

		checkSupport();
	}, []);

	return { checked, supported };
}

/**
 * Factory functions for specific workers
 * Types are imported directly so the worker module namespace is resolved.
 */

import type { GraphLayoutWorkerAPI } from "../workers/graph-layout.worker";
import type { DataTransformWorkerAPI } from "../workers/data-transform.worker";
import type { ExportImportWorkerAPI } from "../workers/export-import.worker";
import type { SearchIndexWorkerAPI } from "../workers/search-index.worker";

export function useGraphLayoutWorker(options?: UseWorkerOptions) {
	return useWorkerWithProgress<GraphLayoutWorkerAPI>(
		() =>
			new Worker(
				new URL("../workers/graph-layout.worker.ts", import.meta.url),
				{ type: "module" },
			),
		options,
	);
}

export function useDataTransformWorker(options?: UseWorkerOptions) {
	return useWorkerWithProgress<DataTransformWorkerAPI>(
		() =>
			new Worker(
				new URL("../workers/data-transform.worker.ts", import.meta.url),
				{ type: "module" },
			),
		options,
	);
}

export function useExportImportWorker(options?: UseWorkerOptions) {
	return useWorkerWithProgress<ExportImportWorkerAPI>(
		() =>
			new Worker(
				new URL("../workers/export-import.worker.ts", import.meta.url),
				{ type: "module" },
			),
		options,
	);
}

export function useSearchIndexWorker(options?: UseWorkerOptions) {
	return useWorkerWithProgress<SearchIndexWorkerAPI>(
		() =>
			new Worker(
				new URL("../workers/search-index.worker.ts", import.meta.url),
				{ type: "module" },
			),
		options,
	);
}
