// Shared helpers for Tracera Vercel Serverless Functions.
//
// These functions are the API tier replacement for the previous Render
// Python/Node service. They are deliberately thin: parity stubs that
// return the shape the frontend already expects. Real handlers can be
// added later route-by-route without changing the frontend contract.
//
// ADR: api-vercel-functions-001

import type { VercelRequest, VercelResponse } from "@vercel/node";

export const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Authorization, Content-Type, x-csrf-token",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "no-referrer",
} as const;

export function handleCors(req: VercelRequest, res: VercelResponse): boolean {
  // Preflight answers must be cheap and predictable.
  if (req.method === "OPTIONS") {
    for (const [k, v] of Object.entries(CORS_HEADERS)) res.setHeader(k, v);
    res.status(204).end();
    return true;
  }
  for (const [k, v] of Object.entries(CORS_HEADERS)) res.setHeader(k, v);
  return false;
}

export function notImplemented(res: VercelResponse, hint = "ADR-VERCEL-001"): void {
  res.status(501).json({
    error: "not_implemented",
    message: hint,
  });
}

export function unauthorized(res: VercelResponse): void {
  res.status(401).json({ error: "unauthorized" });
}

export function ok<T>(res: VercelResponse, body: T): void {
  res.status(200).json(body);
}

export function methodNotAllowed(
  res: VercelResponse,
  allowed: string[],
): void {
  res.setHeader("Allow", allowed.join(", "));
  res.status(405).json({ error: "method_not_allowed", allowed });
}

export function requireMethod(
  req: VercelRequest,
  res: VercelResponse,
  allowed: string[],
): boolean {
  if (req.method === undefined || !allowed.includes(req.method)) {
    methodNotAllowed(res, allowed);
    return false;
  }
  return true;
}
