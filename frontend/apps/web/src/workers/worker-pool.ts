const DEFAULT_MAX_WORKERS = 4;
const DEFAULT_MIN_WORKERS = 1;
const DEFAULT_IDLE_TIMEOUT_MS = 30_000;
const DEFAULT_TASK_TIMEOUT_MS = 60_000;
const CLEANUP_INTERVAL_MS = 5_000;
const TASK_ID_RANDOM_BASE = 36;
const TASK_ID_RANDOM_LENGTH = 9;

const TASK_PRIORITY = {
	CRITICAL: 3,
	HIGH: 2,
	LOW: 0,
	NORMAL: 1,
} as const;

type TaskPriority = (typeof TASK_PRIORITY)[keyof typeof TASK_PRIORITY];

type WorkerTask<T = unknown, R = unknown> = {
	data: T;
	id: string;
	onProgress?: (progress: number) => void;
	priority: TaskPriority;
	reject: (error: Error) => void;
	resolve: (result: R) => void;
	timeout?: number;
	transferables?: Transferable[];
	type: string;
};

type WorkerInstance = {
	busy: boolean;
	currentTaskId?: string;
	lastUsed: number;
	taskCount: number;
	timeoutId?: ReturnType<typeof setTimeout>;
	worker: Worker;
};

type WorkerPoolConfig = {
	idleTimeout?: number;
	maxWorkers?: number;
	minWorkers?: number;
	taskTimeout?: number;
	workerFactory: () => Worker;
};

type WorkerMessage<T = unknown> = {
	data?: T;
	error?: string;
	id: string;
	progress?: number;
	type: "result" | "error" | "progress";
};

class WorkerPool {
	public static readonly TaskPriority = TASK_PRIORITY;

	private cleanupInterval?: ReturnType<typeof setInterval>;
	private config: Required<WorkerPoolConfig>;
	private isShuttingDown = false;
	private taskQueue: WorkerTask[] = [];
	private workers: WorkerInstance[] = [];

	public constructor(config: WorkerPoolConfig) {
		const maxWorkers =
			config.maxWorkers ?? navigator.hardwareConcurrency ?? DEFAULT_MAX_WORKERS;
		const minWorkers = config.minWorkers ?? DEFAULT_MIN_WORKERS;
		const idleTimeout = config.idleTimeout ?? DEFAULT_IDLE_TIMEOUT_MS;
		const taskTimeout = config.taskTimeout ?? DEFAULT_TASK_TIMEOUT_MS;

		this.config = {
			idleTimeout,
			maxWorkers,
			minWorkers,
			taskTimeout,
			workerFactory: config.workerFactory,
		};

		let index = 0;
		while (index < this.config.minWorkers) {
			this.createWorker();
			index += 1;
		}

		this.startCleanup();
	}

	public async executeTask<T = unknown, R = unknown>(
		type: string,
		data: T,
		options: {
			onProgress?: (progress: number) => void;
			priority?: TaskPriority;
			timeout?: number;
			transferables?: Transferable[];
		} = {},
	): Promise<R> {
		if (this.isShuttingDown) {
			throw new Error("Worker pool is shutting down");
		}

		return new Promise<R>((resolve, reject) => {
			const randomSuffix = Math.random()
				.toString(TASK_ID_RANDOM_BASE)
				.slice(2, 2 + TASK_ID_RANDOM_LENGTH);
			const timeout = options.timeout ?? this.config.taskTimeout;
			const priority = options.priority ?? TASK_PRIORITY.NORMAL;

			const task: WorkerTask<T, R> = {
				data,
				id: `task-${Date.now()}-${randomSuffix}`,
				onProgress: options.onProgress,
				priority,
				reject,
				resolve,
				timeout,
				transferables: options.transferables,
				type,
			};

			this.taskQueue.push(task);
			this.taskQueue.sort((first, second) => second.priority - first.priority);
			this.processQueue();
		});
	}

	public getStats() {
		const busyWorkers = this.workers.filter((worker) => worker.busy).length;
		const idleWorkers = this.workers.filter((worker) => !worker.busy).length;
		const totalTasksProcessed = this.workers.reduce(
			(sum, worker) => sum + worker.taskCount,
			0,
		);

		return {
			busyWorkers,
			idleWorkers,
			queuedTasks: this.taskQueue.length,
			totalTasksProcessed,
			totalWorkers: this.workers.length,
		};
	}

	public terminate(): void {
		this.isShuttingDown = true;

		if (this.cleanupInterval) {
			clearInterval(this.cleanupInterval);
			this.cleanupInterval = void 0;
		}

		for (const task of this.taskQueue) {
			task.reject(new Error("Worker pool terminated"));
		}

		this.taskQueue = [];

		for (const worker of this.workers) {
			try {
				worker.worker.terminate();
			} catch {
				void 0;
			}
		}

		this.workers = [];
	}

	private assignTaskToWorker(
		workerInstance: WorkerInstance,
		task: WorkerTask,
	): void {
		workerInstance.busy = true;
		workerInstance.currentTaskId = task.id;
		workerInstance.lastUsed = Date.now();
		workerInstance.taskCount += 1;

		const timeoutId = setTimeout(() => {
			this.handleTaskTimeout(workerInstance, task);
		}, task.timeout ?? this.config.taskTimeout);

		workerInstance.timeoutId = timeoutId;

		try {
			const payload = {
				data: task.data,
				id: task.id,
				type: task.type,
			};

			workerInstance.worker.postMessage(payload, task.transferables ?? []);
		} catch (error) {
			clearTimeout(timeoutId);
			workerInstance.timeoutId = void 0;
			workerInstance.busy = false;
			workerInstance.currentTaskId = void 0;

			if (error instanceof Error) {
				task.reject(error);
			} else {
				task.reject(new Error(String(error)));
			}

			this.processQueue();
		}
	}

	private cleanupIdleWorkers(): void {
		const now = Date.now();
		const workersToRemove: WorkerInstance[] = [];

		for (const worker of this.workers) {
			if (this.workers.length <= this.config.minWorkers) {
				break;
			}

			if (!worker.busy && now - worker.lastUsed > this.config.idleTimeout) {
				workersToRemove.push(worker);
			}
		}

		for (const worker of workersToRemove) {
			const index = this.workers.indexOf(worker);
			if (index >= 0) {
				try {
					worker.worker.terminate();
				} catch {
					void 0;
				}
				this.workers.splice(index, 1);
			}
		}
	}

	private createWorker(): WorkerInstance {
		const worker = this.config.workerFactory();
		const instance: WorkerInstance = {
			busy: false,
			currentTaskId: void 0,
			lastUsed: Date.now(),
			taskCount: 0,
			timeoutId: void 0,
			worker,
		};

		worker.addEventListener("message", (event: MessageEvent<WorkerMessage>) => {
			this.handleWorkerMessage(instance, event.data);
		});

		worker.addEventListener("error", (error: ErrorEvent) => {
			this.handleWorkerError(instance, error);
		});

		this.workers.push(instance);
		return instance;
	}

	private findTaskById(taskId: string): WorkerTask | void {
		const queuedTask = this.taskQueue.find((task) => task.id === taskId);
		if (queuedTask) {
			return queuedTask;
		}

		return void 0;
	}

	private getAvailableWorker(): WorkerInstance | void {
		return this.workers.find((worker) => !worker.busy);
	}

	private handleTaskTimeout(
		workerInstance: WorkerInstance,
		task: WorkerTask,
	): void {
		task.reject(
			new Error(
				`Task timeout after ${task.timeout ?? this.config.taskTimeout}ms`,
			),
		);
		this.restartWorker(workerInstance);
	}

	private handleWorkerError(
		workerInstance: WorkerInstance,
		error: ErrorEvent,
	): void {
		const taskId = workerInstance.currentTaskId;

		if (taskId) {
			const task = this.findTaskById(taskId);
			if (task) {
				task.reject(new Error(`Worker error: ${error.message}`));
			}
		}

		this.restartWorker(workerInstance);
	}

	private handleWorkerMessage(
		workerInstance: WorkerInstance,
		message: WorkerMessage,
	): void {
		const task = this.findTaskById(message.id);

		if (!task) {
			return;
		}

		if (workerInstance.timeoutId) {
			clearTimeout(workerInstance.timeoutId);
			workerInstance.timeoutId = void 0;
		}

		if (message.type === "result") {
			workerInstance.busy = false;
			workerInstance.currentTaskId = void 0;
			workerInstance.lastUsed = Date.now();
			task.resolve(message.data as unknown);
			this.processQueue();
			return;
		}

		if (message.type === "error") {
			workerInstance.busy = false;
			workerInstance.currentTaskId = void 0;
			workerInstance.lastUsed = Date.now();
			task.reject(new Error(message.error ?? "Worker task failed"));
			this.processQueue();
			return;
		}

		if (message.type === "progress") {
			if (task.onProgress && typeof message.progress === "number") {
				task.onProgress(message.progress);
			}
		}
	}

	private processQueue(): void {
		while (this.taskQueue.length > 0) {
			const availableWorker = this.getAvailableWorker();

			if (!availableWorker) {
				if (this.workers.length < this.config.maxWorkers) {
					this.createWorker();
					continue;
				}
				break;
			}

			const task = this.taskQueue.shift();
			if (task) {
				this.assignTaskToWorker(availableWorker, task);
			}
		}
	}

	private restartWorker(workerInstance: WorkerInstance): void {
		const index = this.workers.indexOf(workerInstance);
		if (index < 0) {
			return;
		}

		try {
			workerInstance.worker.terminate();
		} catch {
			void 0;
		}

		this.workers[index] = this.createWorker();
		this.processQueue();
	}

	private startCleanup(): void {
		this.cleanupInterval = setInterval(() => {
			this.cleanupIdleWorkers();
		}, CLEANUP_INTERVAL_MS);
	}
}

export default WorkerPool;
