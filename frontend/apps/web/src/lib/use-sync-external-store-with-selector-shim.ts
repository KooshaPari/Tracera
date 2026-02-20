/**
 * ESM shim for use-sync-external-store/shim/with-selector (CJS).
 * Provides a default export so zustand/esm/traditional.mjs can default-import.
 *
 * The original package uses CommonJS (module.exports) but zustand needs ESM default import.
 * This shim re-exports properly with a default export.
 *
 * Uses "use-sync-external-store-with-selector-real" alias to import the real package
 * and avoid circular dependency (alias for .../with-selector.js points to this file).
 */

// Import the real implementation via alias so we don't resolve to this shim (circular)
// @ts-expect-error - CJS module with no TypeScript types
import real from 'use-sync-external-store-with-selector-real';

export const useSyncExternalStoreWithSelector = real?.useSyncExternalStoreWithSelector ?? real;

export default real;
