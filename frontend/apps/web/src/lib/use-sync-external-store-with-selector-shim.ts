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

// Import the real implementation from the non-shim subpath (exists at the
// package root in `exports`); the shim subpath is the alias target so we
// must not import from it (circular).
// @ts-expect-error - module has no types; we forward via default
import real from 'use-sync-external-store/with-selector';

export const useSyncExternalStoreWithSelector = real?.useSyncExternalStoreWithSelector ?? real;
export default real;