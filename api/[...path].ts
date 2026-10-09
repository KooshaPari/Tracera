import type { VercelRequest, VercelResponse } from "@vercel/node";

// Same-origin gateway to the Rust source of truth. An absent or unreachable
// backend is unavailable, never an empty project or a synthetic healthy service.
const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-CSRF-Token",
  "Access-Control-Max-Age": "86400",
} as const;

function handleCors(req: VercelRequest, res: VercelResponse): boolean {
  if (req.method === "OPTIONS") {
    for (const [k, v] of Object.entries(CORS_HEADERS)) res.setHeader(k, v);
    res.status(204).end();
    return true;
  }
  for (const [k, v] of Object.entries(CORS_HEADERS)) res.setHeader(k, v);
  return false;
}

// Parse /api/<segments> out of the original request URL (query stripped).
function segmentsFromRequestUrl(req: VercelRequest): string[] {
  const url = req.url ?? "";
  const q = url.indexOf("?");
  const pathOnly = (q >= 0 ? url.slice(0, q) : url).replace(/^\/+/, "");
  const withoutPrefix = pathOnly.startsWith("api/")
    ? pathOnly.slice("api/".length)
    : pathOnly;
  return withoutPrefix.split("/").filter(Boolean);
}

// `path` is the catch-all under /api/, e.g. ["v1", "projects", "abc", "export"].
// We normalize: empty segments, query, etc.
async function route(req: VercelRequest, res: VercelResponse): Promise<void> {
  if (handleCors(req, res)) return;

  // Segments come from the REQUEST URL first. Filesystem-routed requests
  // populate req.query.path, but requests that arrive via the vercel.json
  // rewrite (/api/:path* -> /api/[...path]) do NOT carry the catch-all
  // param (observed live: every multi-segment route fell through to
  // notFound with an empty/foreign path param). req.url is the original
  // request path in both cases, so it is the single source of truth.
  const fromUrl = segmentsFromRequestUrl(req);
  const queryPath = req.query.path;
  const rawSegments =
    fromUrl.length > 0
      ? fromUrl
      : Array.isArray(queryPath)
        ? (queryPath as string[])
        : typeof queryPath === "string" && queryPath.length > 0
          ? [queryPath]
          : [];

  const segs = rawSegments.map((s) => decodeURIComponent(s)).filter(Boolean);

  await tryProxy(req, res, segs);
}

function unavailable(res: VercelResponse, reason: string): void {
  res.setHeader("Cache-Control", "no-store");
  res.setHeader("X-Tracera-Gateway-Mode", "unavailable");
  res.status(503).json({ status: "unavailable", reason });
}

const BACKEND_URL = process.env.TRACERA_BACKEND_URL?.replace(/\/$/, "") ?? "";
// Optional server-only service authentication to the already configured Access
// application. These names are project scoped; browser headers cannot replace
// them. Configuring them does not grant policy permissions or Rust authorization.
const ACCESS_CLIENT_ID = process.env.TRACERA_CF_ACCESS_CLIENT_ID ?? "";
const ACCESS_CLIENT_SECRET = process.env.TRACERA_CF_ACCESS_CLIENT_SECRET ?? "";
const BACKEND_TIMEOUT_MS = 8_000;

function accessConfigurationValid(): boolean {
  if (!ACCESS_CLIENT_ID && !ACCESS_CLIENT_SECRET) return true;
  if (!ACCESS_CLIENT_ID.trim() || !ACCESS_CLIENT_SECRET.trim()
      || /[\r\n]/.test(ACCESS_CLIENT_ID + ACCESS_CLIENT_SECRET)) return false;
  try {
    const backend = new URL(BACKEND_URL);
    return backend.protocol === "https:" && !backend.username && !backend.password
      && !backend.search && !backend.hash;
  } catch {
    return false;
  }
}

// Headers we forward from the incoming request to the backend. Everything
// else is either hop-by-hop (host, content-length) or set by fetch itself.
const FORWARDED_REQUEST_HEADERS = [
  "authorization",
  "content-type",
  "cookie",
  // The Rust CSRF middleware requires a browser Origin or Referer in addition
  // to x-csrf-token on mutations. Forward both headers unchanged.
  "origin",
  "referer",
  "x-csrf-token",
  "x-request-id",
  "x-tracera-workspace",
  "accept",
  "accept-language",
  "user-agent",
] as const;

// Headers we copy from the backend response to the Vercel response.
// We deliberately skip transfer-encoding, content-encoding (Vercel handles
// compression), and connection.
const FORWARDED_RESPONSE_HEADERS = [
  "content-type",
  "cache-control",
  "etag",
  "x-tracera-deprecated",
  "x-tracera-trace-id",
] as const;

async function tryProxy(
  req: VercelRequest,
  res: VercelResponse,
  segs: string[],
): Promise<void> {
  if (!BACKEND_URL) {
    unavailable(res, "backend_not_configured");
    return;
  }
  if (!accessConfigurationValid()) {
    unavailable(res, "backend_access_configuration_invalid");
    return;
  }

  const path = segs.join("/");
  const qs = originalQueryString(req);
  // Rust exposes liveness/readiness at the origin root, while canonical API
  // requests use the configured /api base. Do not append /ready to /api.
  const rootProbe = segs.length === 1 && ["health", "healthz", "ready", "readyz"].includes(segs[0]);
  const base = rootProbe ? BACKEND_URL.replace(/\/api$/, "") : BACKEND_URL;
  const target = `${base}/${path}${qs}`;

  const headers: Record<string, string> = {};
  for (const name of FORWARDED_REQUEST_HEADERS) {
    const v = req.headers[name];
    if (typeof v === "string" && v.length > 0) headers[name] = v;
    else if (Array.isArray(v) && v.length > 0) headers[name] = v.join(", ");
  }
  if (ACCESS_CLIENT_ID && ACCESS_CLIENT_SECRET) {
    headers["cf-access-client-id"] = ACCESS_CLIENT_ID;
    headers["cf-access-client-secret"] = ACCESS_CLIENT_SECRET;
  }
  // Body forward: Vercel may have parsed it; for raw fidelity we prefer
  // the raw body when present.
  const rawBody = await readRawBody(req);
  const init: RequestInit = {
    method: req.method ?? "GET",
    headers,
    redirect: "manual",
  };
  if (rawBody && req.method !== "GET" && req.method !== "HEAD") {
    // Buffer is a Uint8Array; fetch accepts it directly.
    init.body = new Uint8Array(rawBody);
  }

  const ac = new AbortController();
  const timer = setTimeout(() => ac.abort(), BACKEND_TIMEOUT_MS);
  try {
    const upstream = await fetch(target, { ...init, signal: ac.signal });
    // Read the entire response before committing a status. A broken response
    // stream is just as unavailable as a connection failure.
    const buf = Buffer.from(await upstream.arrayBuffer());
    const readiness = (segs.length === 1 && ["health", "healthz", "ready", "readyz"].includes(segs[0]))
      || segs.join("/") === "v1/health" || segs.join("/") === "v1/search/health";
    if (readiness && upstream.ok) {
      const expected = segs[0] === "ready" || segs[0] === "readyz" ? "ready" : "ok";
      let payload: { status?: unknown; service?: unknown } | undefined;
      try { payload = JSON.parse(buf.toString()); } catch { /* Access HTML is not health. */ }
      if (!upstream.headers.get("content-type")?.includes("application/json")
          || payload?.status !== expected
          || (segs.join("/") !== "v1/search/health" && payload?.service !== "tracera-server")) {
        unavailable(res, "backend_health_invalid");
        return;
      }
    }
    for (const name of FORWARDED_RESPONSE_HEADERS) {
      const v = upstream.headers.get(name);
      if (v !== null) res.setHeader(name, v);
    }
    res.setHeader("X-Tracera-Gateway-Mode", "proxy");
    res.status(upstream.status).send(buf);
  } catch {
    unavailable(res, ac.signal.aborted ? "backend_timeout" : "backend_unreachable");
  } finally {
    clearTimeout(timer);
  }
}

// Vercel hands us the URL in `req.url` as the path-with-query. We pull
// the query string out so we can re-attach it to the upstream request.
function originalQueryString(req: VercelRequest): string {
  const url = req.url ?? "";
  const q = url.indexOf("?");
  return q >= 0 ? url.slice(q) : "";
}

// Read the raw body if any. Vercel may have already parsed JSON, but for
// proxy fidelity we want bytes.
async function readRawBody(req: VercelRequest): Promise<Buffer | undefined> {
  // Vercel exposes the raw body in non-JSON scenarios; for content-type
  // application/json the parsed body is on `req.body`, which we re-stringify
  // here. That preserves the same wire shape the backend expects.
  const ctype = (req.headers["content-type"] ?? "").toString();
  if (typeof req.body === "string") return Buffer.from(req.body);
  if (Buffer.isBuffer(req.body)) return req.body;
  if (req.body !== undefined && req.body !== null) {
    if (ctype.includes("application/json")) {
      return Buffer.from(JSON.stringify(req.body));
    }
    return Buffer.from(String(req.body));
  }
  return undefined;
}

export default route;

