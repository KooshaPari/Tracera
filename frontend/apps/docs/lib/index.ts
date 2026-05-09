/**
 * Docs lib barrel — intentionally empty.
 *
 * The search worker is instantiated directly in use-search-worker.ts via:
 *   new Worker(new URL('./search.worker.ts', import.meta.url), { type: 'module' })
 *
 * Do NOT use Vite's `?worker` suffix here — Next.js does not support it.
 */
