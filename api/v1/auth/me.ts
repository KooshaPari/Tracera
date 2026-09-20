import type { VercelRequest, VercelResponse } from "@vercel/node";
import { handleCors, notImplemented, requireMethod } from "../../_shared";

export default function handler(req: VercelRequest, res: VercelResponse) {
  if (handleCors(req, res)) return;
  if (!requireMethod(req, res, ["GET"])) return;
  // Frontend tolerates this 501 — it routes to its workos shim. The real
  // Vercel auth surface is delivered by the WorkOS AuthKit hosted UI and
  // does not need this stub in production.
  notImplemented(res, "auth-me-stub");
}
