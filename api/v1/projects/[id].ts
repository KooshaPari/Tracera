import type { VercelRequest, VercelResponse } from "@vercel/node";
import { handleCors, notImplemented, requireMethod } from "../../_shared";

export default function handler(req: VercelRequest, res: VercelResponse) {
  if (handleCors(req, res)) return;
  if (!requireMethod(req, res, ["GET", "PUT", "DELETE"])) return;
  // Single-resource CRUD on /projects/{id}. The frontend also calls
  // /projects/{id}/export and /projects/{id}/import which live in the
  // sibling [id]/ subdirectory.
  notImplemented(res, "project-stub");
}
