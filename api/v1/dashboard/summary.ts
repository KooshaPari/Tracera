import type { VercelRequest, VercelResponse } from "@vercel/node";
import { handleCors, notImplemented, requireMethod } from "../../_shared";

export default function handler(req: VercelRequest, res: VercelResponse) {
  if (handleCors(req, res)) return;
  if (!requireMethod(req, res, ["GET"])) return;
  // Dashboard summary parity. The frontend prefers this endpoint over
  // the per-resource lists; an empty-but-valid payload keeps the page
  // from erroring.
  ok(res, {
    total_artifacts: 0,
    coverage_ratio: 0,
    open_gaps: 0,
  });
}

// Helper import kept inline so this file stays a single export.
function ok<T>(res: VercelResponse, body: T): void {
  res.status(200).json(body);
}
