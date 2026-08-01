/**
 * Resolve the desktop webview origin without coupling the app to a hosted site.
 *
 * The installed app talks to the canonical rich-dashboard gateway by default
 * at 127.0.0.1:18000. Gateway/hosted targets are explicit overrides.
 */
export const DEFAULT_TARGET_URL = "http://127.0.0.1:18000";
export const LEGACY_BUNDLE_PORT = "18081";
export const LEGACY_BUNDLE_OVERRIDE = "TRACERA_ALLOW_LEGACY_BUNDLE";
const DEFAULT_LOCAL_PORT = "18000";

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
  const legacyAllowed = env[LEGACY_BUNDLE_OVERRIDE]?.trim() === "1";
  const requestedPort = env.TRACERA_LOCAL_PORT?.trim();
  if (!legacyAllowed && requestedPort === LEGACY_BUNDLE_PORT) {
    return `http://127.0.0.1:${DEFAULT_LOCAL_PORT}/`;
  }

  const port = requestedPort || DEFAULT_LOCAL_PORT;
  return `http://127.0.0.1:${port}/`;
}
