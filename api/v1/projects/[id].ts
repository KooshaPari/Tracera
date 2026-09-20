import type { VercelRequest, VercelResponse } from "@vercel/node";
import { handleCors, notImplemented, requireMethod } from "../../_shared";

export default function handler(req: VercelRequest, res: VercelResponse) {
  if (handleCors(req, res)) return;
  if (
    !requireMethod(req, res, ["GET", "PUT", "DELETE"]) ||
    req.method === undefined
  ) {
    return;
  }
  // Project detail is read-only parity for now; mutations remain a stub
  // until the API tier settles. Frontend tolerates 501 by re-rendering.
  if (req.method === "GET") notImplemented(res, "project-get-stub");
  else notImplemented(res);
}
