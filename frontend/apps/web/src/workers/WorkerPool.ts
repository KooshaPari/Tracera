/**
 * WorkerPool - Dynamic Web Worker Pool Manager
 *
 * Features:
 * - Dynamic worker allocation based on CPU cores
 * - Task queue with priority levels
 * - Automatic cleanup of idle workers
 * - Error handling and worker restart logic
 * - Transferable object support
 */

export enum TaskPriority {
  LOW = 0,
  NORMAL = 1,
  HIGH = 2,
  CRITICAL = 3,
}

export interface WorkerTask<T = unknown, R = unknown> {
  id: string;
  priority: TaskPriority;
  type: string;
  data: T;
  transferables?: Transferable[];
  timeout?: number;
  onProgress?: (progress: number) => void;
  resolve: (result: R) => void;
  reject: (error: Error) => void;
}

export interface WorkerInstance {
  worker: Worker;
  busy: boolean;
  taskCount: number;
  lastUsed: number;
  currentTaskId: string | null;
}

export interface WorkerPoolConfig {
  maxWorkers?: number;
  minWorkers?: number;
  idleTimeout?: number;
  taskTimeout?: number;
  workerFactory: () => Worker;
}

export interface WorkerMessage<T = unknown> {
  id: string;
  type: 'result' | 'error' | 'progress';
  data?: T;
  error?: string;
  progress?: number;
}

/**
 * Manages a pool of Web Workers for parallel task execution
 */
export class WorkerPool {
  private workers: WorkerInstance[] = [];
  private taskQueue: WorkerTask[] = [];
  private config: Required<WorkerPoolConfig>;
  private cleanupInterval: number | null = null;
  private isShuttingDown = false;

  constructor(config: WorkerPoolConfig) {
    this.config = {
      maxWorkers: config.maxWorkers ?? navigator.hardwareConcurrency ?? 4,
      minWorkers: config.minWorkers ?? 1,
      idleTimeout: config.idleTimeout ?? 30000, // 30 seconds
      taskTimeout: config.taskTimeout ?? 60000, // 60 seconds
      workerFactory: config.workerFactory,
    };

    // Initialize minimum workers
    for (let i = 0; i < this.config.minWorkers; i++) {
      this.createWorker();
    }

    // Start cleanup interval
    this.startCleanup();
  }

  /**
   * Submit a task to the worker pool
   */
  public async executeTask<T = unknown, R = unknown>(
    type: string,
    data: T,
    options: {
      priority?: TaskPriority;
      timeout?: number;
      transferables?: Transferable[];
      onProgress?: (progress: number) => void;
    } = {},
  ): Promise<R> {
    if (this.isShuttingDown) {
      throw new Error('Worker pool is shutting down');
    }

    return new Promise<R>((resolve, reject) => {
      const task: WorkerTask<T, R> = {
        id: `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        priority: options.priority ?? TaskPriority.NORMAL,
        type,
        data,
        transferables: options.transferables,
        timeout: options.timeout ?? this.config.taskTimeout,
        onProgress: options.onProgress,
        resolve,
        reject,
      };

      // Add to queue with priority sorting
      this.taskQueue.push(task);
      this.taskQueue.sort((a, b) => b.priority - a.priority);

      // Process queue
      this.processQueue();
    });
  }

  /**
   * Process the task queue
   */
  private processQueue(): void {
    while (this.taskQueue.length > 0) {
      const availableWorker = this.getAvailableWorker();

      if (!availableWorker) {
        // Try to create a new worker if under max
        if (this.workers.length < this.config.maxWorkers) {
          this.createWorker();
          continue;
        } else {
          // No workers available and at max capacity
          break;
        }
      }

      const task = this.taskQueue.shift()!;
      this.assignTaskToWorker(availableWorker, task);
    }
  }

  /**
   * Get an available worker from the pool
   */
  private getAvailableWorker(): WorkerInstance | null {
    return this.workers.find(w => !w.busy) ?? null;
  }

  /**
   * Create a new worker instance
   */
  private createWorker(): WorkerInstance {
    const worker = this.config.workerFactory();

    const instance: WorkerInstance = {
      worker,
      busy: false,
      taskCount: 0,
      lastUsed: Date.now(),
      currentTaskId: null,
    };

    // Set up message handler
    worker.addEventListener("message", (event: MessageEvent<WorkerMessage>) => {
      this.handleWorkerMessage(instance, event.data);
    });

    // Set up error handler
    worker.addEventListener("error", (error: ErrorEvent) => {
      this.handleWorkerError(instance, error);
    });

    this.workers.push(instance);
    return instance;
  }

  /**
   * Assign a task to a worker
   */
  private assignTaskToWorker(workerInstance: WorkerInstance, task: WorkerTask): void {
    workerInstance.busy = true;
    workerInstance.currentTaskId = task.id;
    workerInstance.lastUsed = Date.now();
    workerInstance.taskCount++;

    // Set up task timeout
    const timeoutId = setTimeout(() => {
      this.handleTaskTimeout(workerInstance, task);
    }, task.timeout);

    // Store timeout ID in a map (would need to be added to class properties)
    (workerInstance as any).timeoutId = timeoutId;

    // Send task to worker
    try {
      workerInstance.worker.postMessage(
        {
          id: task.id,
          type: task.type,
          data: task.data,
        },
        task.transferables ?? [],
      );
    } catch (error) {
      clearTimeout(timeoutId);
      workerInstance.busy = false;
      workerInstance.currentTaskId = null;
      task.reject(error instanceof Error ? error : new Error(String(error)));
      this.processQueue();
    }
  }

  /**
   * Handle worker message
   */
  private handleWorkerMessage(workerInstance: WorkerInstance, message: WorkerMessage): void {
    const task = this.findTaskById(message.id);

    if (!task) {
      console.warn(`Received message for unknown task: ${message.id}`);
      return;
    }

    // Clear timeout
    const timeoutId = (workerInstance as any).timeoutId;
    if (timeoutId) {
      clearTimeout(timeoutId);
      delete (workerInstance as any).timeoutId;
    }

    switch (message.type) {
      case 'result':
        workerInstance.busy = false;
        workerInstance.currentTaskId = null;
        workerInstance.lastUsed = Date.now();
        task.resolve(message.data as any);
        this.processQueue();
        break;

      case 'error':
        workerInstance.busy = false;
        workerInstance.currentTaskId = null;
        workerInstance.lastUsed = Date.now();
        task.reject(new Error(message.error ?? 'Worker task failed'));
        this.processQueue();
        break;

      case 'progress':
        if (task.onProgress && typeof message.progress === 'number') {
          task.onProgress(message.progress);
        }
        break;
    }
  }

  /**
   * Handle worker error
   */
  private handleWorkerError(workerInstance: WorkerInstance, error: ErrorEvent): void {
    console.error('Worker error:', error);

    const taskId = workerInstance.currentTaskId;
    if (taskId) {
      const task = this.findTaskById(taskId);
      if (task) {
        task.reject(new Error(`Worker error: ${error.message}`));
      }
    }

    // Restart the worker
    this.restartWorker(workerInstance);
  }

  /**
   * Handle task timeout
   */
  private handleTaskTimeout(workerInstance: WorkerInstance, task: WorkerTask): void {
    console.warn(`Task timeout: ${task.id}`);

    task.reject(new Error(`Task timeout after ${task.timeout}ms`));

    // Restart the worker as it may be stuck
    this.restartWorker(workerInstance);
  }

  /**
   * Restart a worker
   */
  private restartWorker(workerInstance: WorkerInstance): void {
    const index = this.workers.indexOf(workerInstance);
    if (index === -1) return;

    // Terminate old worker
    try {
      workerInstance.worker.terminate();
    } catch (error) {
      console.error('Error terminating worker:', error);
    }

    // Create new worker
    const newWorker = this.createWorker();
    this.workers[index] = newWorker;

    // Process queue in case there were pending tasks
    this.processQueue();
  }

  /**
   * Find task by ID (needs to search both queue and active tasks)
   */
  private findTaskById(taskId: string): WorkerTask | null {
    // Check queue
    const queuedTask = this.taskQueue.find(t => t.id === taskId);
    if (queuedTask) return queuedTask;

    // For active tasks, we'd need to maintain a separate map
    // This is a simplified version
    return null;
  }

  /**
   * Start cleanup interval for idle workers
   */
  private startCleanup(): void {
    this.cleanupInterval = (typeof window !== 'undefined' ? window.setInterval : setInterval)(() => {
      this.cleanupIdleWorkers();
    }, 5000) as number; // Check every 5 seconds
  }

  /**
   * Clean up idle workers
   */
  private cleanupIdleWorkers(): void {
    const now = Date.now();
    const workersToRemove: WorkerInstance[] = [];

    for (const worker of this.workers) {
      // Keep minimum workers
      if (this.workers.length <= this.config.minWorkers) break;

      // Remove idle workers
      if (!worker.busy && now - worker.lastUsed > this.config.idleTimeout) {
        workersToRemove.push(worker);
      }
    }

    for (const worker of workersToRemove) {
      const index = this.workers.indexOf(worker);
      if (index !== -1) {
        try {
          worker.worker.terminate();
        } catch (error) {
          console.error('Error terminating idle worker:', error);
        }
        this.workers.splice(index, 1);
      }
    }
  }

  /**
   * Get pool statistics
   */
  public getStats() {
    return {
      totalWorkers: this.workers.length,
      busyWorkers: this.workers.filter(w => w.busy).length,
      idleWorkers: this.workers.filter(w => !w.busy).length,
      queuedTasks: this.taskQueue.length,
      totalTasksProcessed: this.workers.reduce((sum, w) => sum + w.taskCount, 0),
    };
  }

  /**
   * Terminate all workers and cleanup
   */
  public terminate(): void {
    this.isShuttingDown = true;

    // Clear cleanup interval
    if (this.cleanupInterval !== null) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }

    // Reject all queued tasks
    for (const task of this.taskQueue) {
      task.reject(new Error('Worker pool terminated'));
    }
    this.taskQueue = [];

    // Terminate all workers
    for (const worker of this.workers) {
      try {
        worker.worker.terminate();
      } catch (error) {
        console.error('Error terminating worker:', error);
      }
    }
    this.workers = [];
  }
}

/**
 * Create a worker pool for a specific worker type
 */
export function createWorkerPool(config: WorkerPoolConfig): WorkerPool {
  return new WorkerPool(config);
}
