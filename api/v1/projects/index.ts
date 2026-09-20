import type { VercelRequest, VercelResponse } from "@vercel/node";
import {
  handleCors,
  notImplemented,
  requireMethod,
} from "../../_shared";

export default function handler(req: VercelRequest, res: VercelResponse) {
  if (handleCors(req, res)) return;
  if (
    !requireMethod(req, res, ["GET", "POST"]) ||
    req.method === undefined
  ) {
    return;
  }
  if (req.method === "GET") {
    // List parity stub: empty project list keeps the dashboard rendering.
    res.status(200).json({ total: 0, projects: [] });
    return;
  }
  notImplemented(res);
}
