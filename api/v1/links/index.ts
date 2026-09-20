import type { VercelRequest, VercelResponse } from "@vercel/node";
import { handleCors, notImplemented, requireMethod } from "../../_shared";

export default function handler(req: VercelRequest, res: VercelResponse) {
  if (handleCors(req, res)) return;
  if (
    !requireMethod(req, res, ["GET", "POST", "PUT", "DELETE"]) ||
    req.method === undefined
  ) {
    return;
  }
  if (req.method === "GET") {
    res.status(200).json([]);
    return;
  }
  notImplemented(res);
}
