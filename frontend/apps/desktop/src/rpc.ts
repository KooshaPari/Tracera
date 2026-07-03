/**
 * Shared RPC schema for Tracera desktop.
 *
 * Pure type definitions — no runtime imports — safe to import from both the
 * Bun main process and the webview without pulling in platform-specific code.
 *
 * Tracera's desktop shell is intentionally thin: it loads the Tracera web UI
 * at an external URL and exposes only a minimal diagnostic API so the UI can
 * query which target URL the shell is using and the shell version.
 */

import type { RPCSchema } from "electrobun/bun";

// Requests the webview sends TO the bun main process.
export type BunRequests = RPCSchema<{
  requests: {
    /** Returns the URL the desktop shell is currently loading. */
    getTargetUrl: { params: Record<string, never>; response: string };
    /** Returns the shell version (matches package.json). */
    getVersion: { params: Record<string, never>; response: string };
    /** Reloads the current page in the webview. */
    reload: { params: Record<string, never>; response: void };
  };
}>;

// Requests the bun main process sends TO the webview (currently none).
export type WebviewRequests = RPCSchema<Record<string, never>>;
