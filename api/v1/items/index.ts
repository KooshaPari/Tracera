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
  // List/create/update/delete parity for items. Frontend tolerates 501
  // for mutations because the dashboards are read-heavy.
  if (req.method === "GET") {
    res.status(200).json({ total: 0, items: [] });
    return;
  }
  notImplemented(res);
}
