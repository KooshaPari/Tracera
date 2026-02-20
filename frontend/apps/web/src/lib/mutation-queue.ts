/**
 * Mutation Queue System
 *
 * Stores failed mutations in localStorage for retry on reconnect.
 * Useful when network goes down mid-operation.
 */

export interface QueuedMutation {
  id: string;
  type: string; // e.g., 'create_item', 'update_item', 'delete_item'
  data: unknown;
  createdAt: string;
  failedAttempts: number;
  lastError?: string | undefined;
}

const STORAGE_KEY = 'pending_mutations';

/**
 * Get all queued mutations from localStorage
 */
export function getQueuedMutations(): QueuedMutation[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return [];
    }
    return JSON.parse(stored) as QueuedMutation[];
  } catch {
    return [];
  }
}

/**
 * Add a mutation to the queue
 */
export function queueMutation(mutation: Omit<QueuedMutation, 'id'>): string {
  const mutations = getQueuedMutations();
  const id = `mutation_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;

  mutations.push({
    ...mutation,
    id,
  });

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(mutations));
  } catch (error) {
    // LocalStorage quota exceeded
    console.error('Failed to queue mutation:', error);
  }

  return id;
}

/**
 * Remove a mutation from the queue
 */
export function removeMutationFromQueue(id: string): void {
  const mutations = getQueuedMutations();
  const filtered = mutations.filter((m) => m.id !== id);

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
  } catch (error) {
    console.error('Failed to remove queued mutation:', error);
  }
}

/**
 * Update failed attempts count and error for a mutation
 */
export function updateMutationError(id: string, error: string, attempts: number): void {
  const mutations = getQueuedMutations();
  const mutation = mutations.find((m) => m.id === id);

  if (!mutation) {
    return;
  }

  mutation.lastError = error;
  mutation.failedAttempts = attempts;

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(mutations));
  } catch (error) {
    console.error('Failed to update queued mutation:', error);
  }
}

/**
 * Clear all queued mutations
 */
export function clearMutationQueue(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear mutation queue:', error);
  }
}

/**
 * Get count of pending mutations
 */
export function getPendingMutationCount(): number {
  return getQueuedMutations().length;
}

/**
 * Hook to watch for changes to mutation queue
 * (manual polling since localStorage doesn't have events)
 */
export function useMutationQueueWatcher(
  onCountChange?: (count: number) => void,
  interval: number = 1000,
): () => void {
  let lastCount = getPendingMutationCount();
  const intervalId = setInterval(() => {
    const newCount = getPendingMutationCount();
    if (newCount !== lastCount) {
      lastCount = newCount;
      onCountChange?.(newCount);
    }
  }, interval);

  return () => clearInterval(intervalId);
}
