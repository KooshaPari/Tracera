/** Single browser origin for the approved Tracera gateway. */
export const DEFAULT_API_ORIGIN = "http://127.0.0.1:18000";

/**
 * Resolve the configured `VITE_API_URL` to an absolute origin.
 *
 * `openapi-fetch` and the browser fetch both reject relative baseUrl strings,
 * so a same-origin deploy that sets `VITE_API_URL=/api` must be resolved before
 * it reaches the client.
 *
 * The semantics depend on whether `VITE_API_URL` is relative or absolute:
 *
 * - **Relative** (e.g. `/api`, `/api/v1`): treated as a same-origin path hint.
 *   Resolved against `window.location.origin` (browser + jsdom) so the result
 *   is the absolute origin only — `https://tracera.example.com` for `/api`.
 *   The trailing path is *dropped* on purpose: every call site already prefixes
 *   its own `/api/v1/...` segment, and keeping the path would produce double
 *   prefixes that the catch-all router rejects.
 * - **Absolute** (e.g. `https://api.example.com`, `https://api.example.com/v2`):
 *   used verbatim so cross-origin deploys preserve any path prefix they ship.
 * - **Empty**: fall back to the local gateway default.
 */
const resolveAbsoluteApiOrigin = (configured: string): string => {
  const trimmed = configured.trim();
  if (trimmed === "") {
    return DEFAULT_API_ORIGIN;
  }
  if (/^https?:\/\//i.test(trimmed)) {
    return trimmed.replace(/\/$/, "");
  }
  const browserOrigin =
    typeof globalThis !== "undefined" &&
    typeof (globalThis as { window?: { location?: { origin?: string } } }).window?.location
      ?.origin === "string"
      ? (globalThis as { window: { location: { origin: string } } }).window.location.origin
      : "http://localhost";
  return browserOrigin.replace(/\/$/, "");
};

export const API_ORIGIN = resolveAbsoluteApiOrigin(
  import.meta.env.VITE_API_URL ?? DEFAULT_API_ORIGIN,
);

export const WS_ORIGIN = (import.meta.env.VITE_WS_URL ?? API_ORIGIN.replace(/^http/, "ws")).replace(
  /\/$/,
  "",
);
