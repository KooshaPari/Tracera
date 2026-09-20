/** Single browser origin for the approved Tracera gateway. */
export const DEFAULT_API_ORIGIN = "http://127.0.0.1:18000";

/**
 * Resolve the configured `VITE_API_URL` to an absolute URL.
 *
 * `openapi-fetch` and the browser fetch both treat relative URLs as invalid base
 * strings, so a same-origin deploy that sets `VITE_API_URL=/api` must be
 * resolved against the page origin before it can be used as a base URL.
 *
 * - Browser: resolve against `window.location.origin` (so `/api` becomes
 *   `https://tracera.example.com/api` on the live dashboard).
 * - Test/Node: jsdom exposes `window.location.origin`, so the same path works.
 * - Empty / unconfigured: fall back to the local gateway default.
 */
const resolveAbsoluteApiOrigin = (configured: string): string => {
  const trimmed = configured.trim().replace(/\/$/, "");
  if (trimmed === "") {
    return DEFAULT_API_ORIGIN;
  }
  if (/^https?:\/\//i.test(trimmed)) {
    return trimmed;
  }
  const browserOrigin =
    typeof globalThis !== "undefined" &&
    typeof (globalThis as { window?: { location?: { origin?: string } } }).window?.location
      ?.origin === "string"
      ? (globalThis as { window: { location: { origin: string } } }).window.location.origin
      : "http://localhost";
  // Normalise accidental double slashes when joining origin + path.
  return `${browserOrigin.replace(/\/$/, "")}/${trimmed.replace(/^\//, "")}`;
};

export const API_ORIGIN = resolveAbsoluteApiOrigin(
  import.meta.env.VITE_API_URL ?? DEFAULT_API_ORIGIN,
);

export const WS_ORIGIN = (import.meta.env.VITE_WS_URL ?? API_ORIGIN.replace(/^http/, "ws")).replace(
  /\/$/,
  "",
);
