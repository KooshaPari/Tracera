# Tracera: competitor comparison, gap analysis and redesign wireframes

Status: proposed documentation, draft 2026-10-14. Builds on Tracera #1132 (gap inventory, 21 gaps + 44 Unknown views), #1128 (holistic product dossier) and #1126 (canonical graph persistence). It claims no implementation. Competitor claims come only from vendor pages listed in Sources; anything not on those pages is marked UNVERIFIED.

## 1. Where Tracera is today (from #1132 / #1128, not re-probed)

- Most views render lists of items, not the artifact the view name implies (journey is not a map, gantt is not a timeline).
- Gateway turns unimplemented GET routes into HTTP 200 empty stub envelopes (GAP-021); frontend wrappers turn failures into `[]`, `{}` or a fabricated "healthy" (GAP-002/003/004/006). The UI cannot tell "empty" from "broken".
- Traceability baseline file is zero bytes (GAP-020); item/link collection routes return 501 (GAP-005).
- 284 frontend API references: 44 explicit Rust stubs, 6 mapped handlers, 234 unresolved owners.
- Product intent (#1128): a persistent, editable multi-view product/project graph, RTM for everything across software, hardware and other domains, spanning ALM/PLM/SDLC.

## 2. Competitor comparison

Columns: what the vendor page says it has, and what Tracera has now. "Tracera now" is based on #1132/#1128 only.

| Capability                | Polarion (Siemens)                                                                                    | Jama Connect                                                                                        | ATOMS (atoms.tech)                                   | Trace.Space                                               | Linear / Plane                                                                              | Tracera now                                                    |
| ------------------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Structured spec documents | LiveDocs: online structured specs, linked to work items                                               | Requirements authoring, real-time collaboration                                                     | Requirements that live in AI agents (Claude, Cursor) | Requirements as graph nodes                               | n/a (issues/docs)                                                                           | No document view; list of items                                |
| Live traceability         | Traceability matrix, impact and traceability analysis (edition-gated per Polarion 2404 feature sheet) | Live Traceability, Live Trace Explorer (auto-detects risk), upstream/downstream tracing, allocation | Trace requirements, tests, code, evidence            | Single graph of requirements, tests, parameters, variants | Issue relations only                                                                        | Empty baseline, 501 on item/link routes, matrix hook not wired |
| Baselines / reuse         | Baselines in feature sheet (UNVERIFIED detail)                                                        | Reuse and baseline management                                                                       | UNVERIFIED                                           | Variants/configurations in one structure                  | Cycles, milestones                                                                          | Baselines pluggable in design only                             |
| Review / approval         | Document workflow                                                                                     | Review Center                                                                                       | UNVERIFIED                                           | UNVERIFIED                                                | PR-style n/a                                                                                | None                                                           |
| Test and quality          | Requirements to test to release                                                                       | Test and quality management, AI test case generation                                                | Tests and evidence tracing                           | Tests as nodes                                            | n/a                                                                                         | None                                                           |
| Risk / hazard             | UNVERIFIED                                                                                            | Risk and hazard analysis                                                                            | Medical device / aircraft domains named              | Regulated domains named                                   | n/a                                                                                         | None                                                           |
| AI / agent integration    | UNVERIFIED                                                                                            | Requirements quality (AI), test generation (AI)                                                     | MCP server, Polarion integration extension           | "Agentic" platform, REST API                              | Plane and Linear have APIs                                                                  | Rust MCP exists (rmcp); agent pane live                        |
| Planning                  | Release, coding, testing in one ALM                                                                   | n/a                                                                                                 | n/a                                                  | n/a                                                       | Projects, initiatives, cycles, saved shared views (Linear); cycles, roadmap, triage (Plane) | Gantt/timeline views not rendering artifact                    |
| Domain span               | Software ALM                                                                                          | Hardware/software product dev                                                                       | Hardware                                             | Hardware R&D, also regulated software                     | Software                                                                                    | Intent: all domains; shipped: RTM list                         |

Reading: incumbents win on document-centric specs, baselines, review and compliance evidence. New entrants (ATOMS, Trace.Space) win on graph + agent/API-first. Linear/Plane win on speed and saved views. Tracera's stated differentiator (one editable graph across RTM/ALM/PLM/PM, agent-native) matches the entrants' direction but currently has none of the rendering, and its fallbacks hide that.

## 3. Gap analysis (ordered by what blocks "mature MVP")

P0 - truth before polish

1. Make empty, error and stub distinct states in every API wrapper (GAP-002/003/004/006/021). A view must say "unavailable" rather than show zero.
2. Real traceability data: land #1126 canonical graph, replace the zero-byte baseline (GAP-020), serve item/link routes (GAP-005).
3. Retire the gateway stub-200 behavior for GETs; return 501 with a typed body so the UI can show "not implemented".

P1 - core RTM parity 4. Traceability matrix and upstream/downstream trace explorer driven by real links, with suspect-link flags. 5. Structured spec document view (LiveDocs-style) with inline item links. 6. Baselines and diff between baselines. 7. Review/approval flow with comments and signed state.

P2 - the differentiators 8. Graph canvas with rich pill nodes (see 4.3), editable in place. 9. Multi-domain item types (requirement, test, part, task, decision, evidence) with domain packs. 10. Agent surface: MCP read/write with audit log, and an agents pane tied to graph items. 11. Saved shared views (Linear model) over the same graph.

P3 - integrations 12. GitHub Actions, git hooks, harness MCP hooks feeding evidence nodes; AgilePlus as work authority (per dossier; do not duplicate AgilePlus #1124).

## 4. Redesign: information architecture and wireframes

### 4.1 Principles

- One graph, many lenses. Every page is a lens over the same items and links; no page owns private data.
- A view renders its artifact: matrix = grid, journey = map, gantt = timeline, spec = document.
- Honest states: loading, empty, error, not-implemented, stale are visually distinct.
- Every node shows provenance (source, commit, time) and a trace badge.

### 4.2 Shell

```
+--------------------------------------------------------------------------------+
| [Tracera]  Project: TRACERA v   Baseline: live v   [Search / command  Ctrl-K]  |
|                                                          [Agents 3] [User]      |
+----------+---------------------------------------------------------------------+
| Home     |  Lens tabs:  Graph | Matrix | Spec | Timeline | Board | Evidence      |
| Projects |  ----------------------------------------------------------------   |
| Graph    |                                                                     |
| Matrix   |                       ACTIVE LENS CANVAS                            |
| Specs    |                                                                     |
| Plan     |                                                                     |
| Evidence |                                                                     |
| Agents   |  ----------------------------------------------------------------   |
| Settings |  Detail drawer: selected item, links, history, comments, provenance  |
+----------+---------------------------------------------------------------------+
| status: API ok | graph rev 4821 | baseline: live | 0 suspect links            |
+--------------------------------------------------------------------------------+
```

### 4.3 Graph lens with pill nodes

```
   ( REQ-12  Login via SSO )-----verifies----->( TEST-31  SSO e2e )
   | status: approved      |                    | last run: pass 2h ago |
   | [thumb: login.png]    |                    | [GIF: sso-flow]       |
   | owner: koosha  v3     |                    | CI #5521 -> evidence  |
   +----------+------------+                    +-----------+-----------+
              |implements                                   |
              v                                             v
   ( CODE  auth/sso.rs@a1b2c3 )                  ( EVID  run-5521.json )
   | suspect: no |                               | hash ok |
```

Pill = title, type chip, status chip, one rich preview (screenshot/GIF/diagram), owner, version, suspect flag. Zoom levels: dot, pill, card, full detail.

### 4.4 Matrix lens

```
              | TEST-31 | TEST-32 | CODE-8 | EVID-2 |
 REQ-12       |   V     |         |   I    |   E    |
 REQ-13       |         |   V     |        |        |   <- row has gap: no code
 REQ-14       |  (!)susp|         |   I    |        |
 coverage: reqs with test 2/3   with code 2/3   with evidence 1/3
 cell click -> link detail; empty cell -> create link / ask agent
```

### 4.5 Spec lens (document)

```
 3. Authentication                         [Baseline: live v] [Review: 2 open]
 3.1 [REQ-12] The system shall allow login via SSO.        -> TEST-31, CODE-8
 3.2 [REQ-13] The system shall lock after 5 failures.      -> (no test)  (!)
 margin: comments | suspect | change since baseline
```

### 4.6 Timeline lens

```
 Milestone    Oct 14        Oct 16 (MVP)        Oct 23
 Graph        [=====|=======]
 Matrix              [=====]
 Spec                  [========]
 deps drawn as arrows; items link back to graph nodes; slip shown in red
```

### 4.7 Agent pane

```
 Agents (herdr)   desk: 6 panes   mac: 2 panes
 tracera-ci   working   item REQ-12  last tool: matrix.build
 [open pane] [assign item] [audit log]
```

## 5. Acceptance gates for the redesign (proposed)

1. No view shows data from a stub or a swallowed error; every state is labeled.
2. Matrix, spec, graph and timeline each render from real graph data for the TRACERA project.
3. Baseline create/diff works on live data.
4. Screenshot receipts per lens, from an authenticated session (not yet captured; Access blocks this author).

## 6. Not verified

- Live UI behavior behind Cloudflare Access was not inspected by the author of this doc; page-level critique relies on #1132/#1128.
- Competitor capability depth beyond vendor marketing pages; edition limits (Polarion) unverified except where the feature sheet cited.

## Sources

- https://www.siemens.com/en-us/products/polarion/requirements/ (LiveDocs)
- https://www.polarsoft.fr/Public/Fichiers/Fichier/11/Polarion-2404-Feature.pdf (traceability matrix, edition table)
- https://www.jamasoftware.com/platform/jama-connect/features/
- https://help.jamasoftware.com/ah/en/getting-to-know-jama-connect-features/traceability-from-requirements-to-test.html
- https://www.jamasoftware.com/blog/jama-connect-features-in-five-live-trace-explorer/
- https://atoms.tech/ , https://atoms.tech/polarion
- https://www.trace.space/ , https://www.trace.space/product
- https://linear.app/features , https://linear.app/docs/custom-views
- https://docs.plane.so/introduction/core-concepts
- Tracera PRs #1132, #1128, #1126
