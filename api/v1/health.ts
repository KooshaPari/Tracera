import type { VercelRequest, VercelResponse } from "@vercel/node";
import { handleCors, ok, requireMethod } from "../_shared";

export default function handler(req: VercelRequest, res: VercelResponse) {
  if (handleCors(req, res)) return;
  if (!requireMethod(req, res, ["GET"])) return;
  ok(res, { status: "ok" });
}
