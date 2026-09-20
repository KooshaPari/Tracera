import type { VercelRequest, VercelResponse } from "@vercel/node";
import { handleCors, notImplemented, requireMethod } from "../../_shared";

export default function handler(req: VercelRequest, res: VercelResponse) {
  if (handleCors(req, res)) return;
  if (!requireMethod(req, res, ["GET", "POST"])) return;
  notImplemented(res, "search-stub");
}
