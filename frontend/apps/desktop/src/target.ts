/**
 * Resolve the desktop webview origin without coupling the app to a hosted site.
 *
 * The installed app talks to the canonical rich-dashboard gateway by default
 * at 127.0.0.1:18000. Gateway/hosted targets are explicit overrides.
 */
export const DEFAULT_TARGET_URL = "http://127.0.0.1:18000";

export function resolveTargetUrl(env: Record<string, string | undefined>): string {
  // Hosted/staging deployments are opt-in. A packaged app must remain local by default.
  const explicit = env.TRACERA_GATEWAY_URL?.trim()
    || env.TRACERA_URL?.trim()
    || env.TRACERA_HOSTED_URL?.trim();
  if (explicit) return explicit;
  const development = env.TRACERA_DEV_URL?.trim();
  if (development) return development;
  // The rich dashboard gateway is the only implicit local target. The legacy
  // bundled frontend remains available only through an explicit override.
  const port = env.TRACERA_LOCAL_PORT?.trim() || "18000";
  return `http://127.0.0.1:${port}/`;
}
