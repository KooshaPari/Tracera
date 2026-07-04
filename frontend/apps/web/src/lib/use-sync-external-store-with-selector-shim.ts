/**
 * ESM shim for use-sync-external-store/shim/with-selector (CJS).
 * Provides a default export so zustand/esm/traditional.mjs can default-import.
 *
 * The original package uses CommonJS (module.exports) but zustand needs ESM default import.
 * This shim re-exports properly with a default export.
 *
 * Imports the real "use-sync-external-store/shim/with-selector.js" entry directly from the
 * npm package (not a relative node_modules path, which is fragile across hoisting layouts
 * and breaks the Rollup production build). This does NOT recurse into this shim: the alias
 * for the bare specifier "use-sync-external-store/shim/with-selector" (without the .js
 * extension) is the one redirected to this file in vite.config.mjs; the extensioned
 * specifier used here resolves straight to the real package via normal node resolution.
 */

// Import the real implementation directly from the npm package.
// @ts-expect-error - CJS module with no TypeScript types
import real from 'use-sync-external-store/shim/with-selector.js';

export const useSyncExternalStoreWithSelector = real?.useSyncExternalStoreWithSelector ?? real;

export default real;
