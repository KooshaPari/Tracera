/**
 * Resolve the desktop webview origin without coupling the app to a hosted site.
 *
 * The installed app talks to the bundled local stack by default (the frontend
 * nginx on $TRACERA_LOCAL_PORT, default 18081, which proxies to the Rust
 * server on 8080 inside the bundle's compose network). TRACERA_URL /
 * TRACERA_HOSTED_URL opt into staging; TRACERA_DEV_URL is the legacy dev
 * override.
 */
export const DEFAULT_TARGET_URL = "http://127.0.0.1:18081";

export function resolveTargetUrl(env: Record<string, string | undefined>): string {
  // Hosted/staging deployments are opt-in. A packaged app must remain local by default.
  const explicit = env.TRACERA_URL?.trim() || env.TRACERA_HOSTED_URL?.trim();
  if (explicit) return explicit;
  const development = env.TRACERA_DEV_URL?.trim();
  if (development) return development;
  const port = env.TRACERA_LOCAL_PORT?.trim() || "18081";
  return `http://127.0.0.1:${port}/`;
}
