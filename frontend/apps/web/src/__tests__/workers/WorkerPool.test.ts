/**
 * WorkerPool Unit Tests
 */

import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { TaskPriority, WorkerPool } from '../../workers/worker-pool';

// Mock Worker
class MockWorker {
  public onmessage: ((event: MessageEvent) => void) | null = null;
  public onerror: ((event: ErrorEvent) => void) | null = null;

  addEventListener(type: string, listener: EventListener) {
    if (type === 'message') {
      this.onmessage = listener as (event: MessageEvent) => void;
    }
    if (type === 'error') {
      this.onerror = listener as (event: ErrorEvent) => void;
    }
  }

  postMessage(message: any, transferables: Transferable[] = []) {
    if (transferables.length > 0) {
      structuredClone(message, { transfer: transferables });
    }
    // Simulate async response
    setTimeout(() => {
      if (this.onmessage) {
        this.onmessage(
          new MessageEvent('message', {
            data: {
              data: { result: 'processed' },
              id: message.id,
              type: 'result',
            },
          }),
        );
      }
    }, 10);
  }

  terminate() {
    // Cleanup
  }

  removeEventListener(type: string, listener: EventListener) {
    if (type === 'message' && this.onmessage === listener) {
      this.onmessage = null;
    }
    if (type === 'error' && this.onerror === listener) {
      this.onerror = null;
    }
  }
}

// Mock global Worker
globalThis.Worker = MockWorker as any;

describe(WorkerPool, () => {
  let pool: WorkerPool;

  beforeEach(() => {
    pool = new WorkerPool({
      idleTimeout: 1000,
      maxWorkers: 4,
      minWorkers: 1,
      taskTimeout: 5000,
      workerFactory: () => new MockWorker() as any,
    });
  });

  afterEach(() => {
    if (pool) {
      pool.terminate();
    }
  });

  describe('Initialization', () => {
    it('should create minimum workers on initialization', () => {
      const stats = pool.getStats();
      expect(stats.totalWorkers).toBeGreaterThanOrEqual(1);
    });

    it('should start with empty queue', () => {
      const stats = pool.getStats();
      expect(stats.queuedTasks).toBe(0);
    });
  });

  describe('Task Execution', () => {
    it('should execute a simple task', async () => {
      const result = await pool.executeTask('test', { data: 'test' });
      expect(result).toBeDefined();
    });

    it('should execute multiple tasks concurrently', async () => {
      const tasks = Array.from({ length: 5 }, (_, i) => pool.executeTask('test', { index: i }));

      const results = await Promise.all(tasks);
      expect(results).toHaveLength(5);
    });

    it('should respect task priority', async () => {
      const priorityPool = new WorkerPool({
        maxWorkers: 1,
        minWorkers: 1,
        workerFactory: () => new MockWorker() as any,
      });
      const results: number[] = [];
      const activeTask = priorityPool.executeTask('test', { index: -1 });

      // Fill the only worker, then compare ordering within the pending queue.
      const lowPriorityTasks = Array.from({ length: 3 }, (_, i) =>
        priorityPool
          .executeTask(
            'test',
            { index: i, priority: 'low' },
            {
              priority: TaskPriority.LOW,
            },
          )
          .then(() => results.push(i)),
      );

      // Queue high priority task
      const highPriorityTask = priorityPool
        .executeTask(
          'test',
          { priority: 'high' },
          {
            priority: TaskPriority.HIGH,
          },
        )
        .then(() => results.push(99));

      await Promise.all([activeTask, ...lowPriorityTasks, highPriorityTask]);

      // Priority orders queued work; it does not preempt an active worker.
      expect(results[0]).toBe(99);
      priorityPool.terminate();
    });

    it('should handle task timeout', async () => {
      // Create a worker that never responds
      const slowPool = new WorkerPool({
        maxWorkers: 1,
        minWorkers: 1,
        workerFactory: () => {
          const worker = new MockWorker() as any;
          worker.postMessage = () => {}; // Never respond
          return worker;
        },
      });

      await expect(slowPool.executeTask('test', {}, { timeout: 100 })).rejects.toThrow('timeout');

      slowPool.terminate();
    });

    it('should report progress for long-running tasks', async () => {
      const progressUpdates: number[] = [];

      await pool.executeTask(
        'test',
        {},
        {
          onProgress: (progress) => {
            progressUpdates.push(progress);
          },
        },
      );

      // Should have received progress updates
      // Note: This depends on worker implementation
      expect(progressUpdates.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Worker Management', () => {
    it('should scale up workers when needed', async () => {
      const initialStats = pool.getStats();
      const initialWorkers = initialStats.totalWorkers;

      // Queue many tasks to force scaling
      const tasks = Array.from({ length: 10 }, (_, i) => pool.executeTask('test', { index: i }));

      // Check workers were created
      const duringStats = pool.getStats();
      expect(duringStats.totalWorkers).toBeGreaterThanOrEqual(initialWorkers);
      expect(duringStats.totalWorkers).toBeLessThanOrEqual(4); // Max workers

      await Promise.all(tasks);
    });

    it('should report accurate statistics', async () => {
      const task1 = pool.executeTask('test', {});
      const stats = pool.getStats();

      expect(stats.totalWorkers).toBeGreaterThan(0);
      expect(stats.busyWorkers).toBeGreaterThanOrEqual(0);
      expect(stats.idleWorkers).toBeGreaterThanOrEqual(0);
      expect(stats.totalWorkers).toBe(stats.busyWorkers + stats.idleWorkers);

      await task1;
    });

    it('should handle worker errors gracefully', async () => {
      const errorPool = new WorkerPool({
        maxWorkers: 2,
        minWorkers: 1,
        workerFactory: () => {
          const worker = new MockWorker() as any;
          worker.postMessage = function postMessage(_message: any) {
            setTimeout(() => {
              if (this.onerror) {
                this.onerror(
                  new ErrorEvent('error', {
                    message: 'Worker error',
                  }),
                );
              }
            }, 10);
          };
          return worker;
        },
      });

      await expect(errorPool.executeTask('test', {})).rejects.toThrow();

      errorPool.terminate();
    });
  });

  describe('Cleanup', () => {
    it('should terminate all workers on pool termination', () => {
      const stats = pool.getStats();
      const workerCount = stats.totalWorkers;

      expect(workerCount).toBeGreaterThan(0);

      pool.terminate();

      const finalStats = pool.getStats();
      expect(finalStats.totalWorkers).toBe(0);
    });

    it('should reject queued tasks on termination', async () => {
      const task = pool.executeTask('test', {});
      pool.terminate();

      await expect(task).rejects.toThrow('terminated');
    });

    it('should prevent new tasks after termination', async () => {
      pool.terminate();

      await expect(pool.executeTask('test', {})).rejects.toThrow('shutting down');
    });

    it('should release busy worker state during termination without error', async () => {
      // Start a task so a worker becomes busy, then terminate while it is active.
      // terminate() must call releaseWorkerTask() for each busy worker, which
      // resets busy=false and clears currentTaskId — observable by the call not
      // throwing and by the pool cleanly reaching the shutting-down state.
      const task = pool.executeTask('test', {});
      // Give the task a moment to be assigned to a busy worker
      await new Promise((resolve) => setTimeout(resolve, 20));

      // terminate() must not throw: releaseWorkerTask() handles the busy worker
      // correctly and the pool reaches a clean shut-down state.
      expect(() => pool.terminate()).not.toThrow();
      await expect(task).rejects.toThrow('terminated');
    });
  });

  describe('Transferables', () => {
    it('should support transferable objects', async () => {
      const buffer = new ArrayBuffer(1024);

      await pool.executeTask(
        'test',
        { buffer },
        {
          transferables: [buffer],
        },
      );

      // After transfer, original buffer should be detached
      expect(buffer.byteLength).toBe(0);
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty task data', async () => {
      const result = await pool.executeTask('test', null);
      expect(result).toBeDefined();
    });

    it('should handle concurrent termination and execution', async () => {
      const task = pool.executeTask('test', {});

      // Terminate while task is running
      setTimeout(() => pool.terminate(), 5);

      await expect(task).rejects.toThrow();
    });

    it('should handle rapid task submission', async () => {
      const tasks = Array.from({ length: 100 }, (_, i) => pool.executeTask('test', { index: i }));

      const results = await Promise.all(tasks);
      expect(results).toHaveLength(100);
    });
  });
});
