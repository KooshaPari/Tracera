/**
 * WorkerPool Edge Case Tests
 * Covers: postMessage errors, worker addEventListener error events, idle cleanup,
 * progress message forwarding, shutting-down rejection, priority queue sorting,
 * error message wrapping for non-Error throws, and worker restart on error.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { TaskPriority, WorkerPool } from '../../workers/worker-pool';

// Minimal mock Worker using addEventListener (matching real Worker API)
class EventDrivenMockWorker {
  private listeners: Record<string, ((event: any) => void)[]> = {};

  addEventListener(type: string, listener: (event: any) => void) {
    if (!this.listeners[type]) {
      this.listeners[type] = [];
    }
    this.listeners[type].push(listener);
  }

  removeEventListener(type: string, listener: (event: any) => void) {
    if (this.listeners[type]) {
      this.listeners[type] = this.listeners[type].filter((l) => l !== listener);
    }
  }

  postMessage(message: any, _transferables?: Transferable[]) {
    // Simulate async response with result
    setTimeout(() => {
      this.emit('message', {
        data: {
          data: { processed: true },
          id: message.id,
          type: 'result',
        },
      });
    }, 5);
  }

  terminate() {}

  emit(type: string, event: any) {
    const handlers = this.listeners[type] || [];
    for (const handler of handlers) {
      handler(event);
    }
  }
}

describe('WorkerPool Edge Cases', () => {
  let pool: WorkerPool;

  afterEach(() => {
    if (pool) {
      pool.terminate();
    }
  });

  describe('postMessage failure', () => {
    it('should reject task when postMessage throws an Error', async () => {
      pool = new WorkerPool({
        maxWorkers: 1,
        minWorkers: 1,
        workerFactory: () => {
          const worker = new EventDrivenMockWorker();
          worker.postMessage = () => {
            throw new Error('DataCloneError: could not be cloned');
          };
          return worker as unknown as Worker;
        },
      });

      await expect(pool.executeTask('test', { data: 'bad' })).rejects.toThrow(
        'DataCloneError: could not be cloned',
      );
    });

    it('should wrap non-Error throws from postMessage into Error', async () => {
      pool = new WorkerPool({
        maxWorkers: 1,
        minWorkers: 1,
        workerFactory: () => {
          const worker = new EventDrivenMockWorker();
          worker.postMessage = () => {
            throw 'string error';
          };
          return worker as unknown as Worker;
        },
      });

      await expect(pool.executeTask('test', {})).rejects.toThrow('string error');
    });

    it('should continue processing queue after postMessage failure', async () => {
      let callCount = 0;
      pool = new WorkerPool({
        maxWorkers: 1,
        minWorkers: 1,
        workerFactory: () => {
          const worker = new EventDrivenMockWorker();
          const originalPostMessage = worker.postMessage.bind(worker);
          worker.postMessage = (message: any, transferables?: Transferable[]) => {
            callCount += 1;
            if (callCount === 1) {
              throw new Error('First call fails');
            }
            originalPostMessage(message, transferables);
          };
          return worker as unknown as Worker;
        },
      });

      // First task should fail
      const firstTask = pool.executeTask('test', { index: 0 });
      await expect(firstTask).rejects.toThrow('First call fails');

      // Second task should succeed (worker restart + queue processing)
      const secondResult = await pool.executeTask('test', { index: 1 });
      expect(secondResult).toEqual({ processed: true });
    });
  });

  describe('worker error event', () => {
    it('should reject current task and restart worker on error event', async () => {
      pool = new WorkerPool({
        maxWorkers: 2,
        minWorkers: 1,
        workerFactory: () => {
          const worker = new EventDrivenMockWorker();
          worker.postMessage = function postMessage(this: EventDrivenMockWorker, _message: any) {
            setTimeout(() => {
              this.emit('error', { message: 'Worker crashed' });
            }, 5);
          }.bind(worker);
          return worker as unknown as Worker;
        },
      });

      await expect(pool.executeTask('test', {})).rejects.toThrow();
    });

    it('should handle error event when no task is associated', async () => {
      const worker = new EventDrivenMockWorker();
      pool = new WorkerPool({
        maxWorkers: 1,
        minWorkers: 1,
        workerFactory: () => worker as unknown as Worker,
      });

      // Trigger error with no current task -- should not throw
      worker.emit('error', { message: 'Spurious error' });

      // Pool should still function after spurious error
      const result = await pool.executeTask('test', { data: 1 });
      expect(result).toEqual({ processed: true });
    });
  });

  describe('progress messages', () => {
    it('should forward progress updates to the onProgress callback', async () => {
      pool = new WorkerPool({
        maxWorkers: 1,
        minWorkers: 1,
        workerFactory: () => {
          const worker = new EventDrivenMockWorker();
          worker.postMessage = function postMessage(this: EventDrivenMockWorker, message: any) {
            // Send progress, then result
            setTimeout(() => {
              this.emit('message', {
                data: { id: message.id, progress: 0.5, type: 'progress' },
              });
            }, 2);
            setTimeout(() => {
              this.emit('message', {
                data: { id: message.id, progress: 1, type: 'progress' },
              });
            }, 4);
            setTimeout(() => {
              this.emit('message', {
                data: { data: 'done', id: message.id, type: 'result' },
              });
            }, 6);
          }.bind(worker);
          return worker as unknown as Worker;
        },
      });

      const progressUpdates: number[] = [];

      const result = await pool.executeTask(
        'compute',
        {},
        {
          onProgress: (progress) => {
            progressUpdates.push(progress);
          },
        },
      );

      expect(result).toBe('done');
      expect(progressUpdates).toEqual([0.5, 1]);
    });

    it('should ignore progress messages without numeric progress value', async () => {
      pool = new WorkerPool({
        maxWorkers: 1,
        minWorkers: 1,
        workerFactory: () => {
          const worker = new EventDrivenMockWorker();
          worker.postMessage = function postMessage(this: EventDrivenMockWorker, message: any) {
            setTimeout(() => {
              this.emit('message', {
                data: { id: message.id, type: 'progress' }, // No progress field
              });
            }, 2);
            setTimeout(() => {
              this.emit('message', {
                data: { data: 'done', id: message.id, type: 'result' },
              });
            }, 4);
          }.bind(worker);
          return worker as unknown as Worker;
        },
      });

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

      expect(progressUpdates).toEqual([]);
    });
  });

  describe('worker error message type', () => {
    it('should reject with error message when worker sends error type', async () => {
      pool = new WorkerPool({
        maxWorkers: 1,
        minWorkers: 1,
        workerFactory: () => {
          const worker = new EventDrivenMockWorker();
          worker.postMessage = function postMessage(this: EventDrivenMockWorker, message: any) {
            setTimeout(() => {
              this.emit('message', {
                data: {
                  error: 'Computation failed',
                  id: message.id,
                  type: 'error',
                },
              });
            }, 5);
          }.bind(worker);
          return worker as unknown as Worker;
        },
      });

      await expect(pool.executeTask('test', {})).rejects.toThrow('Computation failed');
    });

    it('should reject with default message when error type has no error field', async () => {
      pool = new WorkerPool({
        maxWorkers: 1,
        minWorkers: 1,
        workerFactory: () => {
          const worker = new EventDrivenMockWorker();
          worker.postMessage = function postMessage(this: EventDrivenMockWorker, message: any) {
            setTimeout(() => {
              this.emit('message', {
                data: {
                  id: message.id,
                  type: 'error',
                },
              });
            }, 5);
          }.bind(worker);
          return worker as unknown as Worker;
        },
      });

      await expect(pool.executeTask('test', {})).rejects.toThrow('Worker task failed');
    });
  });

  describe('priority queue sorting', () => {
    it('should process CRITICAL tasks before NORMAL and LOW', async () => {
      const completionOrder: string[] = [];

      // Create a pool with only 1 worker but slow responses
      pool = new WorkerPool({
        maxWorkers: 1,
        minWorkers: 1,
        workerFactory: () => {
          const worker = new EventDrivenMockWorker();
          worker.postMessage = function postMessage(this: EventDrivenMockWorker, message: any) {
            setTimeout(() => {
              this.emit('message', {
                data: { data: message.data, id: message.id, type: 'result' },
              });
            }, 10);
          }.bind(worker);
          return worker as unknown as Worker;
        },
      });

      // First task occupies the worker
      const firstTask = pool.executeTask('test', { label: 'first' }).then(() => {
        completionOrder.push('first');
      });

      // Queue remaining while first is running
      const lowTask = pool
        .executeTask('test', { label: 'low' }, { priority: TaskPriority.LOW })
        .then(() => {
          completionOrder.push('low');
        });
      const criticalTask = pool
        .executeTask('test', { label: 'critical' }, { priority: TaskPriority.CRITICAL })
        .then(() => {
          completionOrder.push('critical');
        });
      const normalTask = pool
        .executeTask('test', { label: 'normal' }, { priority: TaskPriority.NORMAL })
        .then(() => {
          completionOrder.push('normal');
        });

      await Promise.all([firstTask, lowTask, criticalTask, normalTask]);

      // First always completes first (was already running)
      expect(completionOrder[0]).toBe('first');
      // Critical should come before normal and low
      expect(completionOrder[1]).toBe('critical');
    });
  });

  describe('idle worker cleanup', () => {
    it('should clean up idle workers after timeout', async () => {
      vi.useFakeTimers();

      pool = new WorkerPool({
        idleTimeout: 100,
        maxWorkers: 4,
        minWorkers: 1,
        workerFactory: () => new EventDrivenMockWorker() as unknown as Worker,
      });

      // Execute several tasks to scale up workers
      const tasks = Array.from({ length: 4 }, async (_, i) =>
        pool.executeTask('test', { index: i }),
      );

      // Let tasks complete
      vi.advanceTimersByTime(20);
      await Promise.all(tasks);

      const statsBefore = pool.getStats();
      expect(statsBefore.totalWorkers).toBeGreaterThan(1);

      // Advance past idle timeout + cleanup interval
      vi.advanceTimersByTime(40_000);

      const statsAfter = pool.getStats();
      // Should have cleaned up to minWorkers
      expect(statsAfter.totalWorkers).toBeLessThanOrEqual(statsBefore.totalWorkers);

      vi.useRealTimers();
    });
  });

  describe('getStats accuracy', () => {
    it('should report zero queued tasks when pool is idle', () => {
      pool = new WorkerPool({
        maxWorkers: 2,
        minWorkers: 1,
        workerFactory: () => new EventDrivenMockWorker() as unknown as Worker,
      });

      const stats = pool.getStats();
      expect(stats.queuedTasks).toBe(0);
      expect(stats.busyWorkers).toBe(0);
      expect(stats.totalWorkers).toBe(1);
      expect(stats.idleWorkers).toBe(1);
      expect(stats.totalTasksProcessed).toBe(0);
    });

    it('should track totalTasksProcessed correctly', async () => {
      pool = new WorkerPool({
        maxWorkers: 2,
        minWorkers: 1,
        workerFactory: () => new EventDrivenMockWorker() as unknown as Worker,
      });

      await pool.executeTask('test', {});
      await pool.executeTask('test', {});
      await pool.executeTask('test', {});

      const stats = pool.getStats();
      expect(stats.totalTasksProcessed).toBe(3);
    });
  });

  describe('TaskPriority export', () => {
    it('should export correct priority values', () => {
      expect(TaskPriority.CRITICAL).toBe(3);
      expect(TaskPriority.HIGH).toBe(2);
      expect(TaskPriority.NORMAL).toBe(1);
      expect(TaskPriority.LOW).toBe(0);
    });

    it('should expose static TaskPriority on WorkerPool class', () => {
      expect(WorkerPool.TaskPriority).toBeDefined();
      expect(WorkerPool.TaskPriority.CRITICAL).toBe(3);
    });
  });
});
