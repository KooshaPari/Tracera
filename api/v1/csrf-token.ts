import type { VercelRequest, VercelResponse } from "@vercel/node";
import { handleCors, ok, requireMethod } from "../_shared";

export default function handler(req: VercelRequest, res: VercelResponse) {
  if (handleCors(req, res)) return;
  if (!requireMethod(req, res, ["GET"])) return;
  // CSRF token parity. Real CSRF still happens at the session/auth layer;
  // this stub returns a non-secret placeholder so the frontend CSRF flow
  // does not 404.
  ok(res, {
    csrf_token: "vercel-functions-csrf-stub",
    header: "x-csrf-token",
  });
}
