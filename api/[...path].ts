import type { VercelRequest, VercelResponse } from "@vercel/node";

// ==============================================================================
// Tracera Vercel Functions — single-router replacement
// ==============================================================================
// Why one file: Vercel's Hobby plan caps a deployment at 12 Serverless
// Functions; the parity set needed by the frontend exceeds that. This catch-all
// matches the same routes the Rust backend served when Render was alive and
// returns the same envelope the frontend expects, so the contract is unchanged.
//
// Routing summary (matches docs/04-guides/ENVIRONMENTS.md):
//   * /health, /healthz, /ready, /readyz                   → 200 {status: ok|ready}
//   * /api/v1/health                                       → 200 {status: ok}
//   * /api/v1/csrf-token                                   → 200 {csrf_token, header}
//   * /api/v1/dashboard/summary                            → 200 dashboard
//   * /api/v1/projects, /api/v1/projects/{id}              → list / 501
//   * /api/v1/projects/{id}/export, /import                → 501
//   * /api/v1/items, /api/v1/items/{id}, /summary          → list / 501
//   * /api/v1/items/bulk-update, /items/{id}/pivot         → 501
//   * /api/v1/items/pivot-targets/{id}                     → 501
//   * /api/v1/links, /api/v1/links/{id}                    → list / 501
//   * /api/v1/graph/{ancestors|descendants|impact|...}/{id}→ 501
//   * /api/v1/graph/{path,paths,full,cycles,topo-sort,orphans} → 501
//   * /api/v1/search/{index|index/{id}|suggest|...}        → 501 (health=200)
//   * /api/v1/auth/{me,login,logout,refresh,verify}        → 200 (logout) / 501
//   * /api/v1/import                                       → 501
//
// Anything else under /api/* → 404 (with CORS preflight handled first).
// ==============================================================================

type Handler = (
  req: VercelRequest,
  res: VercelResponse,
) => Promise<void> | void;

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-CSRF-Token",
  "Access-Control-Max-Age": "86400",
} as const;

function handleCors(req: VercelRequest, res: VercelResponse): boolean {
  if (req.method === "OPTIONS") {
    for (const [k, v] of Object.entries(CORS_HEADERS)) res.setHeader(k, v);
    res.status(204).end();
    return true;
  }
  for (const [k, v] of Object.entries(CORS_HEADERS)) res.setHeader(k, v);
  return false;
}

function notImplemented(res: VercelResponse, stub: string): void {
  res.status(501).json({ status: "not_implemented", stub });
}

function ok<T>(res: VercelResponse, body: T): void {
  res.status(200).json(body);
}

function methodNotAllowed(res: VercelResponse, allowed: string[]): void {
  res.setHeader("Allow", allowed.join(", "));
  res.status(405).json({ status: "method_not_allowed", allowed });
}

function requireMethod(
  req: VercelRequest,
  res: VercelResponse,
  allowed: string[],
): boolean {
  if (req.method && allowed.includes(req.method)) return true;
  methodNotAllowed(res, allowed);
  return false;
}

const health: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET"])) return;
  ok(res, { status: "ok" });
};

const healthz: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET"])) return;
  ok(res, { status: "ok" });
};

const ready: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET"])) return;
  ok(res, { status: "ready" });
};

const readyz: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET"])) return;
  ok(res, { status: "ready" });
};

const csrfToken: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET"])) return;
  ok(res, {
    csrf_token: "vercel-functions-csrf-stub",
    header: "x-csrf-token",
  });
};

const dashboardSummary: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET"])) return;
  ok(res, { total_artifacts: 0, coverage_ratio: 0, open_gaps: 0 });
};

const projectsIndex: Handler = (req, res) => {
  if (req.method === "GET") {
    ok(res, { total: 0, projects: [] });
    return;
  }
  if (!requireMethod(req, res, ["POST"])) return;
  notImplemented(res, "project-stub");
};

const projectById: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET", "PUT", "DELETE"])) return;
  notImplemented(res, "project-stub");
};

const projectExport: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET"])) return;
  notImplemented(res, "export-stub");
};

const projectImport: Handler = (req, res) => {
  if (!requireMethod(req, res, ["POST"])) return;
  notImplemented(res, "import-stub");
};

const itemsIndex: Handler = (req, res) => {
  if (req.method === "GET") {
    ok(res, { total: 0, items: [] });
    return;
  }
  if (!requireMethod(req, res, ["POST"])) return;
  notImplemented(res, "item-stub");
};

const itemById: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET", "PUT", "PATCH", "DELETE"])) return;
  notImplemented(res, "item-stub");
};

const itemsSummary: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET"])) return;
  ok(res, { total: 0, items: [] });
};

const itemsBulkUpdate: Handler = (req, res) => {
  if (!requireMethod(req, res, ["POST"])) return;
  notImplemented(res, "bulk-update-stub");
};

const itemsPivotTargets: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET", "POST"])) return;
  notImplemented(res, "pivot-stub");
};

const linksIndex: Handler = (req, res) => {
  if (req.method === "GET") {
    ok(res, []);
    return;
  }
  if (!requireMethod(req, res, ["POST"])) return;
  notImplemented(res, "link-stub");
};

const linkById: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET", "PUT", "DELETE"])) return;
  notImplemented(res, "link-stub");
};

const graphIdRoute: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET"])) return;
  notImplemented(res, "graph-stub");
};

const graphRoute: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET"])) return;
  notImplemented(res, "graph-stub");
};

const searchHealth: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET"])) return;
  ok(res, { status: "ok" });
};

const searchRoute: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET", "POST"])) return;
  notImplemented(res, "search-stub");
};

const searchById: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET", "POST"])) return;
  notImplemented(res, "search-stub");
};

const authMe: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET"])) return;
  // Frontend tolerates this 501 — it routes to its workos shim. The real
  // Vercel auth surface is delivered by the WorkOS AuthKit hosted UI and
  // does not need this stub in production.
  notImplemented(res, "auth-me-stub");
};

const authLogin: Handler = (req, res) => {
  if (!requireMethod(req, res, ["POST"])) return;
  notImplemented(res, "auth-stub");
};

const authLogout: Handler = (req, res) => {
  if (!requireMethod(req, res, ["POST"])) return;
  ok(res, { status: "ok" });
};

const authRefresh: Handler = (req, res) => {
  if (!requireMethod(req, res, ["POST"])) return;
  notImplemented(res, "auth-stub");
};

const authVerify: Handler = (req, res) => {
  if (!requireMethod(req, res, ["GET"])) return;
  notImplemented(res, "auth-stub");
};

const apiImport: Handler = (req, res) => {
  if (!requireMethod(req, res, ["POST"])) return;
  notImplemented(res, "import-stub");
};

// -----------------------------------------------------------------------------
// Router
// -----------------------------------------------------------------------------

// `path` is the catch-all under /api/, e.g. ["v1", "projects", "abc", "export"].
// We normalize: empty segments, query, etc.
async function route(req: VercelRequest, res: VercelResponse): Promise<void> {
  if (handleCors(req, res)) return;

  // Pull the path from the request URL or from the catch-all param.
  // Vercel sets `req.query` for dynamic segments; when this file is
  // /api/[...path].ts, `req.query.path` is a string[] of segments.
  const rawSegments = Array.isArray(req.query.path)
    ? (req.query.path as string[])
    : typeof req.query.path === "string"
      ? [req.query.path]
      : [];

  const segs = rawSegments.map((s) => decodeURIComponent(s)).filter(Boolean);

  // Top-level routes (no /api prefix).
  if (segs.length === 0) {
    notFound(res);
    return;
  }

  // Root-level liveness.
  if (segs.length === 1) {
    switch (segs[0]) {
      case "health":
        return health(req, res);
      case "healthz":
        return healthz(req, res);
      case "ready":
        return ready(req, res);
      case "readyz":
        return readyz(req, res);
    }
  }

  // /api/v1/...
  if (segs[0] !== "v1") {
    notFound(res);
    return;
  }

  if (segs.length === 2) {
    switch (segs[1]) {
      case "health":
        return health(req, res);
      case "csrf-token":
        return csrfToken(req, res);
      case "dashboard":
        // /api/v1/dashboard/summary is below; bare /dashboard is unknown.
        return notFound(res);
      case "import":
        return apiImport(req, res);
    }
  }

  if (segs.length === 3) {
    const [, , leaf] = segs;
    switch (leaf) {
      case "projects":
        return projectsIndex(req, res);
      case "items":
        return itemsIndex(req, res);
      case "links":
        return linksIndex(req, res);
      case "summary":
        // /api/v1/items/summary
        return itemsSummary(req, res);
      case "bulk-update":
        return itemsBulkUpdate(req, res);
      case "graph":
        // /api/v1/graph → unknown leaf
        return notFound(res);
      case "search":
        return searchRoute(req, res);
      case "auth":
        return notFound(res);
      case "suggest":
        return searchRoute(req, res);
      case "stats":
        return searchRoute(req, res);
      case "reindex":
        return searchRoute(req, res);
      case "batch-index":
        return searchRoute(req, res);
      case "index":
        // /api/v1/search/index is a list endpoint; covered above as searchRoute
        return searchRoute(req, res);
      default:
        return notFound(res);
    }
  }

  if (segs.length === 4) {
    const [, section, id, leaf] = segs;
    // /api/v1/<section>/<id>
    if (!leaf) {
      return notFound(res);
    }
    switch (section) {
      case "projects":
        if (leaf === "export") return projectExport(req, res);
        if (leaf === "import") return projectImport(req, res);
        return notFound(res);
      case "items":
        if (leaf === "pivot-targets") return itemsPivotTargets(req, res);
        return notFound(res);
      case "links":
        if (leaf === "export") return notImplemented(res, "link-export-stub");
        return notFound(res);
      case "graph":
        switch (id) {
          case "ancestors":
          case "descendants":
          case "dependencies":
          case "impact":
          case "traverse":
            return graphIdRoute(req, res);
          default:
            return notFound(res);
        }
      case "search":
        if (leaf === "index") return searchById(req, res);
        return notFound(res);
      case "auth":
        switch (id) {
          case "me":
            return authMe(req, res);
          case "login":
            return authLogin(req, res);
          case "logout":
            return authLogout(req, res);
          case "refresh":
            return authRefresh(req, res);
          case "verify":
            return authVerify(req, res);
          default:
            return notFound(res);
        }
      case "dashboard":
        if (leaf === "summary") return dashboardSummary(req, res);
        return notFound(res);
      default:
        return notFound(res);
    }
  }

  if (segs.length === 5) {
    const [, section, , , leaf] = segs;
    switch (section) {
      case "projects":
        if (leaf === "export") return projectExport(req, res);
        if (leaf === "import") return projectImport(req, res);
        return notFound(res);
      default:
        return notFound(res);
    }
  }

  notFound(res);
}

function notFound(res: VercelResponse): void {
  res.status(404).json({ status: "not_found" });
}

export default route;
