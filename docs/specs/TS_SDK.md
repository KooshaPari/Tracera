# Tracera TypeScript SDK — Client Fill Spec

## Status

**Draft** 2026-06-24 · **Lane:** composer · **Scope:** spec only (no implementation in this PR)

## Purpose

Define how to fill the empty/stub methods in `@tracertm/api-client` so the frontend TypeScript SDK exposes a **fully typed client for all 24 surviving main-branch REST endpoints**. This spec is the migration oracle companion to `_tracera_feature_inventory.md`: zero net capability loss across Py→Rust/Go or TS→Bun migrations unless explicitly approved.

## Current state

| Package | Role | State |
|---------|------|-------|
| `@tracertm/types` | Shared request/response types | Partial — traceability + evidence types exist; pillar/unmounted endpoint types missing |
| `@tracertm/api-client` | `TraceraApiClient` + `fetchCoverageMatrix` | **7 / 24** endpoints implemented (traceability + evidence only) |

**Implemented today** (`frontend/packages/api-client/src/index.ts`):

- `POST /api/v1/coverage-matrix` → `buildCoverageMatrix` / `roundTripTraceLink`
- `POST /api/v1/impact` → `analyzeImpact`
- `POST /api/v1/governance/spec-check` → `specCheck`
- `POST /api/v1/confidence` → `computeConfidence`
- `GET /api/v1/evidence` → `listEvidence`
- `POST /api/v1/evidence` → `createEvidence`

**Missing:** auth, org-intel (3), sdlc-pm (4), code-trace, blast-radius, ingest (2), graph impact (2), comments (3).

## Target architecture

```
FastAPI routers (SSOT for paths + Pydantic schemas)
        │
        ▼
  OpenAPI 3.1 (exported from running app or CI artifact)
        │
        ├── openapi-typescript  →  generated path/types map
        │
        └── @tracertm/types     →  hand-curated public types (re-export generated where stable)
                │
                ▼
        @tracertm/api-client
          TraceraApiClient        thin facade: auth headers, baseUrl, errors
          createTraceraApiClient  factory
          fetch* helpers          optional standalone functions per endpoint group
```

### Design principles

1. **Contract fidelity** — Method, path, and JSON shapes must match `src/tracertm/api/routers/*.py` on `main`, not historical deleted routers.
2. **Types are the oracle** — Every endpoint row below must have a named TS request/response type in `@tracertm/types` (or `never` / `void` for empty bodies).
3. **No runtime magic** — Plain `fetch`; injectable `fetchImpl` for tests (existing pattern).
4. **Auth is explicit** — `Authorization: Bearer <token>` via client options; unauthenticated calls only where the router has no `auth_guard` dependency.
5. **Mount-aware** — SDK covers all 24 router-defined endpoints even when `main.py` has not yet `include_router()`'d them (see §Mount gaps).

---

## Generated-client approach

### Pipeline (recommended)

| Step | Tool | Output |
|------|------|--------|
| 1. Export spec | `curl $BASE/openapi.json` or FastAPI `app.openapi()` in CI | `frontend/packages/api-client/openapi/tracera.openapi.json` |
| 2. Generate types | [`openapi-typescript`](https://github.com/drwpow/openapi-typescript) | `src/generated/schema.d.ts` |
| 3. Optional client shell | [`openapi-fetch`](https://github.com/drwpow/openapi-typescript/tree/main/packages/openapi-fetch) | typed `client.GET/POST` with path literals |
| 4. Curate public API | Hand-written `TraceraApiClient` | Stable method names; hides OpenAPI path string drift |

**CI gate:** Regenerate when any file under `src/tracertm/api/routers/` changes. Diff `openapi/tracera.openapi.json`; fail if the 24 paths disappear.

**Alternative (fallback):** If OpenAPI export is blocked, maintain types manually in `@tracertm/types` mirroring Pydantic models — but still run spectral validation against a checked-in spec stub.

### Client options (extend existing)

```typescript
export interface TraceraApiClientOptions {
  baseUrl: string;
  fetchImpl?: typeof fetch;
  /** Bearer token or async provider (refresh before each request). */
  getAccessToken?: () => string | Promise<string | undefined>;
  /** Echo X-Request-Id for correlation (matches RequestIdMiddleware). */
  requestId?: string | (() => string);
}
```

### Error model

```typescript
export class TraceraApiError extends Error {
  constructor(
    readonly status: number,
    readonly path: string,
    readonly body?: unknown,
  ) {
    super(`${path} failed (${status})`);
  }
}
```

Replace bare `throw new Error(\`… failed (${status})\`)` with `TraceraApiError` in the fill PR.

---

## Endpoint catalog (24)

Paths are **canonical** as composed by each router's `APIRouter(prefix=…)` plus `app.include_router(..., prefix="/api/v1")`. Where a router embeds a full `/api/v1/...` prefix, mount that router at `""` in `main.py` to avoid double-prefix bugs (noted in §Mount gaps).

| # | FR | Method | Path | SDK method | Request type | Response type | Auth |
|---|-----|--------|------|------------|--------------|---------------|------|
| 1 | B4 / Auth | `GET` | `/api/v1/auth/me` | `getCurrentUser()` | — | `MeResponse` | Bearer |
| 2 | FR-TRC-014 | `POST` | `/api/v1/coverage-matrix` | `buildCoverageMatrix()` | `CoverageMatrixRequest` | `CoverageMatrixResponse` | — |
| 3 | Governance | `POST` | `/api/v1/governance/spec-check` | `specCheck()` | `GovernanceCheckRequest` | `GovernanceReport` | — |
| 4 | Impact (in-mem) | `POST` | `/api/v1/impact` | `analyzeImpact()` | `ImpactRequest` | `ImpactResponse` | — |
| 5 | FR-TRC-019 | `POST` | `/api/v1/confidence` | `computeConfidence()` | `ConfidenceRequest` | `ConfidenceResponse` | — |
| 6 | Org-intel | `GET` | `/api/v1/org-intel/health` | `orgIntelHealth()` | — | `PillarHealthResponse` | — |
| 7 | Org-intel | `GET` | `/api/v1/org-intel/metrics` | `getOrgMetrics()` | — | `MetricsResponse` | — |
| 8 | Org-intel | `GET` | `/api/v1/org-intel/teams` | `listTeams()` | — | `TeamResponse[]` | — |
| 9 | SDLC-PM | `GET` | `/api/v1/sdlc-pm/health` | `sdlcPmHealth()` | — | `PillarHealthResponse` | — |
| 10 | SDLC-PM | `GET` | `/api/v1/sdlc-pm/sprints` | `listSprints()` | — | `SprintResponse[]` | — |
| 11 | SDLC-PM | `GET` | `/api/v1/sdlc-pm/stories` | `listStories()` | — | `StoryResponse[]` | — |
| 12 | SDLC-PM | `POST` | `/api/v1/sdlc-pm/sprints` | `createSprint()` | `SprintCreate` | `SprintResponse` | — |
| 13 | Evidence | `GET` | `/api/v1/evidence/health` | `evidenceHealth()` | — | `PillarHealthResponse` | — |
| 14 | Evidence | `GET` | `/api/v1/evidence` | `listEvidence()` | — | `EvidenceResponse[]` | — |
| 15 | Evidence | `POST` | `/api/v1/evidence` | `createEvidence()` | `EvidenceCreate` | `EvidenceResponse` | — |
| 16 | Code trace | `GET` | `/api/v1/analysis/code-trace/{componentId}` | `getCodeTrace()` | `CodeTraceParams` | `CodeTraceChainResponse` | Bearer |
| 17 | FR-TRC-015 | `POST` | `/api/v1/impact/blast-radius` | `computeBlastRadius()` | `BlastRadiusRequest` | `BlastRadiusResult` | Bearer |
| 18 | FR-TRC-013 | `POST` | `/api/v1/ingest/github` | `ingestGitHubIssues()` | `GitHubIssueIngestRequest` | `BulkIngestionResult` | Bearer |
| 19 | FR-TRC-013 | `POST` | `/api/v1/ingest/jira` | `ingestJiraIssues()` | `JiraIssueIngestRequest` | `BulkIngestionResult` | Bearer |
| 20 | FR-TRACE-003 | `GET` | `/api/v1/impact/forward/{artifactId}` | `forwardImpact()` | `ImpactGraphParams` | `ForwardImpactResponse` | Bearer |
| 21 | FR-TRACE-003 | `GET` | `/api/v1/impact/reverse/{artifactId}` | `reverseImpact()` | `ImpactGraphParams` | `ReverseImpactResponse` | Bearer |
| 22 | Comments | `GET` | `/api/v1/items/{itemId}/comments` | `listComments()` | `CommentListParams` | `CommentResponse[]` | Bearer |
| 23 | Comments | `POST` | `/api/v1/items/{itemId}/comments` | `createComment()` | `CreateCommentBody` | `CommentResponse` | Bearer |
| 24 | Comments | `DELETE` | `/api/v1/items/{itemId}/comments/{commentId}` | `deleteComment()` | `CommentDeleteParams` | `void` (204) | Bearer |

> **Note:** `POST /api/v1/impact` (row 4, in-memory graph impact) and `GET /api/v1/impact/forward|reverse` (rows 20–21, Neo4j traversal) share the `/impact` path prefix but differ in method and semantics. The SDK must not collapse them into one method.

### Type definitions to add in `@tracertm/types`

Types marked **exists** are already in `frontend/packages/types/src/index.ts`.

#### Shared / pillar

```typescript
export interface PillarHealthResponse {
  pillar: string;
  status: 'ok' | string;
}

export interface MeResponse {
  user: Record<string, unknown>;
  claims: Record<string, unknown>;
  account: { id: string; name?: string } | null;
}
```

#### Org-intel

```typescript
export interface MetricsResponse {
  total_artifacts: number;
  coverage_ratio: number;
  open_gaps: number;
}

export interface TeamResponse {
  id: string;
  name: string;
  description: string;
  members: string[];
  created_at: string;
  updated_at: string;
}
```

#### SDLC-PM

```typescript
export interface SprintCreate {
  name: string;
  goal: string;
  start_date: string;
  end_date: string;
}

export interface SprintResponse {
  id: string;
  name: string;
  goal: string;
  start_date: string;
  end_date: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface StoryResponse {
  id: string;
  sprint_id: string | null;
  title: string;
  description: string;
  status: string;
  story_points: number | null;
  created_at: string;
  updated_at: string;
}
```

#### Code trace (`code_trace.py` → UICodeTraceChain)

```typescript
export interface CodeRef {
  symbolName: string;
  symbolType: string;
  filePath?: string;
  startLine?: number;
  endLine?: number;
  signature?: string;
}

export interface TraceLevel {
  id: string;
  type: 'ui' | 'code' | 'requirement' | 'concept' | string;
  title: string;
  description?: string | null;
  confidence: number;
  strategy: string;
  isConfirmed: boolean;
  componentName?: string;
  componentPath?: string;
  screenshot?: string;
  codeRef?: CodeRef;
  requirementId?: string;
  businessValue?: string;
}

export interface CodeTraceChainResponse {
  id: string;
  name: string;
  description?: string | null;
  levels: TraceLevel[];
  overallConfidence: number;
  lastUpdated: string;
}

export interface CodeTraceParams {
  componentId: string;
  projectId?: string;
}
```

#### Blast radius (FR-TRC-015)

```typescript
export type ArtifactKind =
  | 'requirement' | 'design' | 'code' | 'test'
  | 'evidence' | 'risk' | 'rationale';

export type TraceLinkType =
  | 'IMPLEMENTS' | 'VERIFIES' | 'DUPLICATES' | 'SATISFIES'
  | 'DERIVES_FROM' | 'CONFLICTS_WITH' | 'REFINES';

export interface Artifact {
  id: string;
  project_id: string;
  kind: ArtifactKind;
  title: string;
  description?: string | null;
  external_id?: string | null;
  metadata?: Record<string, unknown>;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface TraceLink {
  id?: string | null;
  project_id: string;
  source_artifact_id: string;
  target_artifact_id: string;
  link_type: TraceLinkType;
  confidence?: number;
  rationale?: string | null;
  metadata?: Record<string, unknown>;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface BlastRadiusRequest {
  artifact_id: string;
  artifacts?: Artifact[];
  links?: TraceLink[];
  depth?: number;
}

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface BlastRadiusResult {
  artifact_id: string;
  blast_radius_score: number;
  affected_artifacts: string[];
  critical_path: string[];
  risk_level: RiskLevel;
}
```

#### Bulk ingest (FR-TRC-013)

```typescript
export interface GitHubIssueIngestRequest {
  repo: string;
  issues?: Record<string, unknown>[];
}

export interface JiraIssueIngestRequest {
  issues?: Record<string, unknown>[];
}

export interface BulkIngestionResult {
  total_processed: number;
  requirements_created: number;
  trace_links_created: number;
  errors: string[];
}
```

#### Graph impact (FR-TRACE-003)

```typescript
export interface ImpactArtifactNode {
  id: string;
  project_id: string;
  kind: string;
  title: string;
  external_id: string | null;
  link_types: string[];
}

export interface ForwardImpactResponse {
  artifact_id: string;
  direction: 'forward';
  total: number;
  affected: ImpactArtifactNode[];
}

export interface ReverseImpactResponse {
  artifact_id: string;
  direction: 'reverse';
  total: number;
  upstream: ImpactArtifactNode[];
}

export interface ImpactGraphParams {
  artifactId: string;
}
```

#### Comments

```typescript
export interface CommentResponse {
  id: string;
  item_id: string;
  author_id: string;
  author: string;
  content: string;
  edited: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateCommentBody {
  content: string;
}

export interface CommentListParams {
  itemId: string;
}

export interface CommentDeleteParams {
  itemId: string;
  commentId: string;
}
```

#### Traceability (exists — re-export)

`TraceLinkInput`, `CoverageMatrixRequest`, `CoverageMatrixResponse`, `ImpactRequest`, `ImpactResponse`, `GovernanceCheckRequest`, `GovernanceReport`, `ConfidenceRequest`, `ConfidenceResponse`, `EvidenceCreate`, `EvidenceResponse` — **no schema changes** unless OpenAPI diff says otherwise.

---

## Trace-link round-trip (acceptance test plan)

There is no dedicated `POST /trace-links` CRUD endpoint on main. **Trace links are submitted via the coverage matrix** (`POST /api/v1/coverage-matrix`) and echoed back in `cells[].links`. The SDK's existing `roundTripTraceLink()` is the correct abstraction.

### Unit test (mock fetch) — required in fill PR

**File:** `frontend/packages/api-client/src/index.test.ts`  
**Name:** `roundTripTraceLink creates and reads back a trace link`

```typescript
it('roundTripTraceLink creates and reads back a trace link', async () => {
  const link: TraceLinkInput = {
    source_id: 'req-42',
    target_id: 'code-99',
    relationship: 'satisfies',
    confidence: 0.95,
  };

  const responseBody: CoverageMatrixResponse = {
    generated_at: '2026-06-24T12:00:00Z',
    link_count: 1,
    cell_count: 1,
    stale_links: 0,
    cells: [
      {
        source_id: 'req-42',
        target_id: 'code-99',
        coverage: 'covered',
        links: [link],
      },
    ],
  };

  const fetchImpl = vi.fn(async () =>
    jsonResponse(responseBody),
  );

  const client = new TraceraApiClient({
    baseUrl: 'https://api.example.test',
    fetchImpl: fetchImpl as unknown as typeof fetch,
  });

  const result = await client.roundTripTraceLink(link);

  expect(fetchImpl).toHaveBeenCalledOnce();
  const [url, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
  expect(url).toBe('https://api.example.test/api/v1/coverage-matrix');
  expect(init.method).toBe('POST');
  expect(JSON.parse(init.body as string)).toEqual({ links: [link] });

  expect(result.link_count).toBe(1);
  expect(result.cells[0].links).toEqual([link]);
  expect(result.cells[0].coverage).toBe('covered');
  expectTypeOf(result).toEqualTypeOf<CoverageMatrixResponse>();
});
```

### Integration test (optional, CI with API)

**Precondition:** Tracera API running; `POST /api/v1/coverage-matrix` mounted.

1. `POST` with `{ links: [{ source_id, target_id, relationship: "satisfies" }] }`.
2. Assert `200`, `link_count === 1`, `cells[0].links[0].source_id === source_id`.
3. Assert `cells[0].coverage` is one of `covered | partial | missing | stale | conflict`.

**Pass criteria:** Request link round-trips byte-identical in `cells[0].links[0]` (modulo server-defaulted `confidence` if omitted).

---

## Implementation checklist (fill PR, not this spec)

- [ ] Add missing types to `@tracertm/types` (§Type definitions)
- [ ] Export all types from `@tracertm/api-client` (re-export pattern)
- [ ] Implement 17 new `TraceraApiClient` methods
- [ ] Wire `getAccessToken` → `Authorization` header for auth-guarded routes
- [ ] Add `openapi-typescript` generate script + CI diff gate
- [ ] Extend `index.test.ts`: one vitest per endpoint (mirror existing 7 tests)
- [ ] Add `roundTripTraceLink` acceptance test (§Trace-link round-trip)
- [ ] Document mount gaps below in CHANGELOG when backend re-mounts routers

---

## Mount gaps (backend, out of SDK scope but affects integration tests)

Six router modules exist on `main` but are **not** `include_router()`'d in `src/tracertm/api/main.py` today:

| Router | Endpoints | SDK still implements? |
|--------|-----------|----------------------|
| `code_trace` | 1 | Yes — prefix `/api/v1/analysis`; mount at `""` or fix prefix to `/analysis` |
| `impact` | 2 | Yes |
| `impact_scoring` | 1 | Yes — `POST …/impact/blast-radius` |
| `ingest` | 2 | Yes |
| `comments` | 3 | Yes — prefix already includes `/api/v1/items/...`; mount at `""` |

SDK authors implement all 24 methods now; integration tests for unmounted routes are `test.skip` until backend PR lands.

---

## References

- `_tracera_feature_inventory.md` — 24-endpoint oracle rule
- `docs/FEATURE_INVENTORY.md` — full migration safety catalog
- `frontend/packages/api-client/src/index.ts` — current stub
- `frontend/packages/types/src/index.ts` — current types
- `src/tracertm/api/routers/*.py` — path + schema SSOT
