import type { VercelRequest, VercelResponse } from "@vercel/node";
import { handleCors, notImplemented, requireMethod } from "../../../_shared";

// Graph endpoints are read-heavy in the frontend and have many aliases.
// All routes share this stub until a real graph backend is wired in.
export default function handler(req: VercelRequest, res: VercelResponse) {
  if (handleCors(req, res)) return;
  if (!requireMethod(req, res, ["GET", "POST", "DELETE"])) return;
  notImplemented(res, "graph-stub");
}
