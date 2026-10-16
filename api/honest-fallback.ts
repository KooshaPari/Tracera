import type { VercelRequest, VercelResponse } from "@vercel/node";

/** Local gateway liveness is separate from unavailable backend readiness. */
export function honestFallback(req: VercelRequest, res: VercelResponse): void {
  const route = new URL(req.url ?? "/", "http://localhost").pathname;
  res.setHeader("x-tracera-source", "vercel-gateway");
  if (req.method === "GET" && ["/health", "/healthz"].includes(route)) {
    res.status(200).json({ status: "ok", source: "vercel-gateway", backend: "unavailable" });
    return;
  }
  if (req.method === "GET" && ["/ready", "/readyz", "/api/v1/health"].includes(route)) {
    res
      .status(503)
      .json({ error: "unavailable", route, source: "vercel-gateway", backend: "unavailable" });
    return;
  }
  res.setHeader("x-tracera-not-implemented", "true");
  res.status(501).json({ error: "not_implemented", route, since: "2026-10-16" });
}
