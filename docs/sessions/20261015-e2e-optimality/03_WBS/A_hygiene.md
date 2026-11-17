# A. Hygiene: Build Stability, 501 Stubs, Silent Failure Elimination

**Phase:** P1 (Hygiene)  
**Task Prefix:** H-001..H-135  
**Goal:** Unblock CI, eliminate 501 routes, remove unused code, fail-loud on errors  
**Depends On:** —  
**Unlocks:** P2 Registry, P3 AgilePlus

---

## H-001..H-020: Case-Sensitive Build & Duplicate Ingest

| Task | Description | Depends On | Est | Surface | Acceptance |
|------|-------------|-----------|-----|---------|-----------|
| H-001 | Find all `ingest.rs` files in workspace | — | 10m | rg "ingest\.rs$" | List all matches, count |
| H-002 | Identify duplicate ingest.rs vs ingest/mod.rs in crates/tracera-server | H-001 | 10m | crates/tracera-server/src | Both files exist, show paths |
| H-003 | Check upstream fix status | H-002 | 10m | GitHub upstream repo | Link to upstream fix |
| H-004 | Determine which file is canonical | H-002 | 10m | Git blame, upstream docs | Decision + rationale |
| H-005 | Port upstream fix to local | H-004 | 20m | crates/tracera-server/src | Duplicate removed |
| H-006 | Validate case-sensitive build on macOS | H-005 | 10m | cargo build --workspace | Build passes |
| H-007 | Validate case-sensitive build on Linux | H-005 | 10m | Docker build | Build passes |
| H-008 | Add pre-commit hook | H-005 | 10m | .git/hooks/pre-commit | Hook blocks case-collision |
| H-009 | Test hook rejection | H-008 | 10m | git add test.RS | Pre-commit rejects |
| H-010 | Update CONTRIBUTING.md | H-005 | 10m | docs/CONTRIBUTING.md | Case-sensitivity documented |
| H-011 | Verify Cargo.toml mod declarations | H-005 | 10m | rg "mod ingest" crates/ | All match actual filenames |
| H-012 | Run cargo check --workspace | H-005 | 10m | cargo check --workspace | 0 errors |
| H-013 | Create case-collision linter | H-005 | 20m | crates/tracera-lint/src/case_check.rs | Linter detects collisions |
| H-014 | Integrate linter in CI | H-013 | 10m | .github/workflows/lint.yml | CI runs case-linter |
| H-015 | Document in ADR | H-005 | 10m | docs/governance/ADR-BUILD-001.md | ADR explains fix |
| H-016 | Find other case-collisions | H-005 | 10m | find . -type f (case check) | No other duplicates |
| H-017 | Update Cargo.lock | H-005 | 10m | cargo update | Cargo.lock updated |
| H-018 | Re-run full test suite | H-005 | 20m | cargo test --workspace | All pass |
| H-019 | Commit fix | H-018 | 10m | git commit | Commit landed, CI green |
| H-020 | Tag release candidate | H-019 | 10m | git tag v0.0.0-rc-hygiene-1 | Tag created |

---

## H-021..H-070: 501 Route Stubs & Handlers

| Task | Description | Depends On | Est | Surface | Acceptance |
|------|-------------|-----------|-----|---------|-----------|
| H-021 | Audit 83 backend 501 routes | — | 20m | crates/tracera-server (grep 501) | List 83 routes |
| H-022 | Categorize by domain | H-021 | 15m | Spreadsheet | Items, links, graph, search, import, export, journey, equivalence, AI |
| H-023 | Identify critical vs optional | H-022 | 10m | Dependency analysis | Critical (A1/A2/A3 path), optional (exploratory) |
| H-024 | Stub items routes (10: list, get, create, update, delete, search, export, import, batch, history) | H-023 | 30m | crates/tracera-server/src/routes/items.rs | 10 stubs, 501 responses |
| H-025 | Test items stubs | H-024 | 20m | tests/ | 10 unit tests pass |
| H-026 | Wire items routes | H-024 | 10m | crates/tracera-server/src/main.rs | Routes registered |
| H-027 | Stub links routes (8: list, get, create, delete, batch, export, import, history) | H-023 | 30m | crates/tracera-server/src/routes/links.rs | 8 stubs |
| H-028 | Stub graph routes (10: query, traverse, pattern, diff, export, import, validate, stats, batch-update, history) | H-023 | 35m | crates/tracera-server/src/routes/graph.rs | 10 stubs |
| H-029 | Stub search routes (6: global, items, links, graph, advanced, export) | H-023 | 25m | crates/tracera-server/src/routes/search.rs | 6 stubs |
| H-030 | Stub import routes (8: validate, preview, ingest-github, ingest-jira, ingest-agileplus, ingest-custom, status, history) | H-023 | 30m | crates/tracera-server/src/routes/import.rs | 8 stubs |
| H-031 | Stub export routes (7: items-csv, items-json, graph-neo4j, graph-scip, journey, evidence, attestation) | H-023 | 30m | crates/tracera-server/src/routes/export.rs | 7 stubs |
| H-032 | Stub journey routes (5: list, get, create, execute, delete) | H-023 | 20m | crates/tracera-server/src/routes/journey.rs | 5 stubs |
| H-033 | Stub equivalence routes (6: query, propose, vote, merge, export, import) | H-023 | 20m | crates/tracera-server/src/routes/equivalence.rs | 6 stubs |
| H-034 | Stub AI routes (5: predict-gap, explain-evidence, suggest-test, generate-journey, classify-issue) | H-023 | 20m | crates/tracera-server/src/routes/ai.rs | 5 stubs |
| H-035 | Wire all stubs into router | H-024..H-034 | 15m | crates/tracera-server/src/main.rs | 83 routes registered |
| H-036 | Add integration tests for all stubs | H-035 | 30m | tests/integration/routes.rs | 83 tests pass |
| H-037 | Verify HTTP 501 status (not 404 or 500) | H-035 | 10m | curl integration test | All return 501 |
| H-038 | Audit edge worker (14 routes 501, 2 live) | — | 15m | crates/tracera-edge-worker/src | List routes |
| H-039 | Stub edge worker routes (8 critical: proxy, rate-limit, cache, auth, validate, redirect, throttle, fallback) | H-038 | 25m | crates/tracera-edge-worker/src/routes.rs | 8 stubs |
| H-040 | Test edge worker stubs | H-039 | 15m | wrangler publish | Edge stubs return 501 |
| H-041 | Create 501 documentation | H-035..H-040 | 20m | docs/governance/STUB-ROUTES.md | Document all stubs |
| H-042 | Add stub deprecation policy | H-041 | 10m | docs/governance/STUB-DEPRECATION.md | Policy: stub → WP → impl → test → deploy |
| H-043 | Test UI error on 501 (not fake data) | H-035 | 10m | frontend test | UI shows "not implemented" |
| H-044 | Test CLI error on 501 (not fake data) | H-035 | 10m | cli test | CLI shows "not implemented" |
| H-045 | Test MCP error on 501 (not fake result) | H-035 | 10m | tracera-mcp test | MCP returns error |
| H-046 | Verify CI passes with stubs | H-035 | 10m | cargo test --workspace | All tests green |
| H-047 | Document stub pattern in ARCHITECTURE.md | H-041 | 10m | docs/ARCHITECTURE.md | Section on stub pattern |
| H-048 | Create "convert stub to real" issue template | H-041 | 10m | .github/ISSUE_TEMPLATE/stub-to-impl.md | Template created |
| H-049 | Tag post-stub release | H-046 | 10m | git tag v0.0.0-rc-hygiene-2 | Tag created |
| H-050 | Verify project create/update/delete return 501 (not silent 200 success) | H-035 | 10m | POST /v1/projects → 501 | Returns 501, not fake 200 |

---

## H-051..H-100: Unused Code Removal & Client Cleanup

| Task | Description | Depends On | Est | Surface | Acceptance |
|------|-------------|-----------|-----|---------|-----------|
| H-051 | Audit Cache client usage | — | 10m | rg "Cache::" crates/tracera-server/src | Find all references |
| H-052 | Verify Cache client never called | H-051 | 10m | rg "\.cache\." crates/ | No .cache() calls found |
| H-053 | Remove Cache client init | H-052 | 10m | crates/tracera-server/src/main.rs | Init removed |
| H-054 | Remove Cache dependency | H-053 | 10m | Cargo.toml | Dependency removed |
| H-055 | Verify startup time post-Cache removal | H-053 | 10m | time cargo build && time ./server | No increase |
| H-056 | Audit Neo4j client usage | — | 10m | rg "Neo4j::" crates/ | Find references |
| H-057 | Verify Neo4j client never called | H-056 | 10m | rg "\.neo4j\." crates/ | No calls found |
| H-058 | Remove Neo4j client init | H-057 | 10m | crates/tracera-server/src/main.rs | Init removed |
| H-059 | Remove Neo4j dependency | H-058 | 10m | Cargo.toml | Removed |
| H-060 | Audit R2 (Cloudflare) client usage | — | 10m | rg "R2::|cloudflare.*storage" crates/ | Find references |
| H-061 | Verify R2 client never called | H-060 | 10m | rg "\.r2\." crates/ | No calls found |
| H-062 | Remove R2 client init | H-061 | 10m | crates/tracera-server/src/main.rs | Init removed |
| H-063 | Remove R2 dependency | H-062 | 10m | Cargo.toml | Removed |
| H-064 | Verify startup post-triple cleanup | H-053, H-058, H-062 | 10m | cargo build && run server | No missing-client errors |
| H-065 | Use cargo tree for transitive deps | H-064 | 10m | cargo tree --duplicates | List unused transitive deps |
| H-066 | Audit OpenTelemetry calls | — | 10m | rg "tracer\.|span\.|trace\(" crates/tracera-server/src | Find OTel usage |
| H-067 | Verify OpenTelemetry not called | H-066 | 10m | rg "tracer\.|span\.|trace\(" (negate) | No OTel calls found |
| H-068 | Document OpenTelemetry as deferred | H-067 | 10m | docs/governance/ADR-OBS-001-amendment.md | Note: instrumentation deferred to P4 |
| H-069 | Run cargo clippy after cleanup | H-064 | 10m | cargo clippy --workspace | No new warnings |
| H-070 | Commit cleanup | H-064 | 10m | git commit | Commit landed |

---

## H-071..H-120: Silent Failure Elimination

| Task | Description | Depends On | Est | Surface | Acceptance |
|------|-------------|-----------|-----|---------|-----------|
| H-071 | Audit CI.yml for "|| true" | — | 15m | .github/workflows/ci.yml | List silent failures |
| H-072 | Analyze each "|| true" (intentional vs bug) | H-071 | 20m | Code review | Categorized |
| H-073 | Remove "|| true" from TypeScript job | H-072 | 15m | .github/workflows/ci.yml | TS job fails on tsc error |
| H-074 | Add explicit error handling | H-073 | 15m | .github/workflows/ci.yml | Logs describe failure |
| H-075 | Verify CI fails hard on TS errors | H-073 | 10m | github.com: push TS error | CI red |
| H-076 | Audit stylelint (does it mutate?) | — | 10m | stylelint run | Document behavior |
| H-077 | Fix stylelint to NOT mutate (--check, no --fix in CI) | H-076 | 15m | CI config | Stylelint reports only |
| H-078 | Verify stylelint job fails on issues | H-077 | 10m | github.com: style issues | CI red |
| H-079 | Document CI failure expectations | H-075, H-078 | 10m | docs/CONTRIBUTING.md | CI expectations listed |
| H-080 | Audit Vercel deploy config | — | 15m | vercel.json, .vercelignore | Review config |
| H-081 | Check Vercel build logs | H-080 | 10m | Vercel logs | Error messages noted |
| H-082 | Fix Vercel config | H-081 | 20m | vercel.json | Build succeeds locally |
| H-083 | Test Vercel deploy locally | H-082 | 10m | vercel dev | Local preview works |
| H-084 | Verify Vercel deploy succeeds | H-082 | 10m | github.com: push → Vercel | Deploy green |
| H-085 | Audit docs/WBS.md (0 bytes?) | — | 10m | ls -la docs/WBS.md | Confirm 0 bytes |
| H-086 | Populate docs/WBS.md | H-085 | 15m | docs/WBS.md | File has content |
| H-087 | Audit postinstall patches (7 fragile) | — | 20m | patch-package or .patchrc | List 7 patches |
| H-088 | Verify patch necessity | H-087 | 15m | npm list patch-package | Document brittle patches |
| H-089 | Create issue per fragile patch | H-088 | 10m | .github/ISSUE_TEMPLATE | 7 issues (if needed) |
| H-090 | Test clean install (patches apply) | H-087 | 20m | rm node_modules && npm install | All patches apply |
| H-091 | Document postinstall strategy | H-087 | 10m | docs/CONTRIBUTING.md | Patch policy |
| H-092 | Audit typecheck strategy | — | 10m | CI config (grep typecheck) | Find command |
| H-093 | Fix typecheck (single -p, all projects) | H-092 | 15m | npm scripts or CI | Typecheck covers all |
| H-094 | Verify typecheck coverage | H-093 | 10m | Run typecheck | All .ts checked |
| H-095 | Add typecheck results to CI summary | H-093 | 10m | CI job summary | Fails show which projects |
| H-096 | Test typecheck failure propagation | H-093 | 10m | github.com: push TS error | CI fails |
| H-097 | Audit linter config (consistency) | — | 15m | ruff.toml, eslint.config.js, stylelint.config.js | Review rules |
| H-098 | Verify linter enforced in CI | H-097 | 10m | .github/workflows/lint.yml | Linter runs, blocks merge |
| H-099 | Add linter results to CI summary | H-098 | 10m | CI config | Displays failing files |
| H-100 | Commit silent-failure fixes | H-075, H-078, H-084, H-091, H-094, H-099 | 10m | git commit | Commit landed |

---

## H-101..H-135: Dirty Tree & Completion

| Task | Description | Depends On | Est | Surface | Acceptance |
|------|-------------|-----------|-----|---------|-----------|
| H-101 | List 26 modified files | — | 10m | git status --short | Document all 26 |
| H-102 | Categorize 26 mods | H-101 | 15m | Spreadsheet | Docs, config, SDK, deployment, etc. |
| H-103 | Identify safe-to-leave mods | H-102 | 10m | Git diff review | Safe list identified |
| H-104 | Stash or branch 26 mods | H-103 | 10m | git stash or branch | P1 isolated from pre-existing |
| H-105 | Create clean P1 branch | H-104 | 10m | git checkout -b p1-hygiene-2026-10-15 main | Branch created |
| H-106 | Apply H-001..H-100 fixes | H-105 | — | Branch contains all H-* | All commits on p1-hygiene branch |
| H-107 | Run full test suite | H-106 | 20m | cargo test --workspace | All pass |
| H-108 | Simulate CI locally | H-106 | 20m | Local CI workflow | All steps green |
| H-109 | Create PR p1-hygiene → main | H-108 | 10m | gh pr create | PR created |
| H-110 | Verify PR CI passes | H-109 | 10m | github.com: check CI | All checks green |
| H-111 | Request code review | H-109 | 5m | gh pr comment "Ready for review" | Reviewers pinged |
| H-112 | Address review feedback | H-111 | varies | git push (feedback commits) | PR feedback addressed |
| H-113 | Merge P1 PR | H-110, H-112 | 10m | gh pr merge -m -d | PR merged, branch deleted |
| H-114 | Verify main clean post-merge | H-113 | 10m | github.com: main CI status | All checks pass |
| H-115 | Restore pre-P1 mods | H-114 | 15m | git stash pop or rebase | 26 pre-existing mods restored |
| H-116 | Create PR for pre-existing mods | H-115 | 10m | gh pr create | Separate from P1 |
| H-117 | Document P1 completion | H-114 | 10m | docs/sessions/.../P1_COMPLETION.md | Checklist complete |
| H-118 | Tag main post-P1 | H-114 | 10m | git tag v0.0.0-rc-hygiene-complete | Tag created |
| H-119 | Verify P1 outputs (P2/P3 unblock gate) | H-118 | 10m | Confirm: clean CI, stubs, no unused code | P1 unlocks P2/P3 |
| H-120 | Create P2 kickoff issue | H-119 | 10m | gh issue create "P2 Registry Repair" | Issue created |
| H-121 | Document P1 lessons learned | H-119 | 10m | docs/sessions/.../P1_RETRO.md | Retro notes |
| H-122 | Verify all 83+14 routes callable (no crash) | H-035, H-040 | 10m | Integration test | No panics |
| H-123 | Measure code coverage baseline | H-107 | 15m | cargo tarpaulin | Coverage % documented |
| H-124 | Document P1 architecture improvements | H-119 | 10m | docs/governance/P1-IMPROVEMENTS.md | Design benefits noted |
| H-125 | Prepare P1 summary for operator | H-119 | 10m | docs/sessions/.../P1_SUMMARY.md | Summary complete |
| H-126 | Await operator sign-off | H-125 | — | Operator review | "P1 green, proceed" |
| H-127 | Create P1→P2 dependency link | H-126 | 10m | Issue tracker | P2 depends on P1 complete |
| H-128 | Archive P1 artifacts | H-113 | 10m | Session folder | Branch, PR, logs preserved |
| H-129 | Validate no 501 in A1/A2/A3 critical path | H-119 | 10m | Code review | Critical surfaces have real impl |
| H-130 | Confirm dirty tree state (26 mods isolated) | H-115 | 10m | git status --short | 26 mods pending, isolated |
| H-131 | Update 03_DAG_WBS.md with actual P1 duration | H-119 | 10m | docs/sessions/.../03_DAG_WBS.md | Actual est replaces range |
| H-132 | Link P1 to phase gates | H-126 | 10m | 03_DAG_WBS.md | Gate: P1 COMPLETE → P2/P3 start |
| H-133 | Verify CI green on origin/main | H-114 | 10m | github.com: main status | All checks green |
| H-134 | Transition to P2 owner | H-126 | 10m | Handoff memo | P2 owner reads summary |
| H-135 | P1 sign-off | H-134 | 5m | Operator approval | P1 done ✓, P2 begin |

---

## Summary

**P1 Hygiene: 135 leaf tasks**

- Case-sensitivity & duplicate ingest: 20 tasks (H-001..H-020)
- 501 route stubs: 30 tasks (H-021..H-050)
- Unused code & client cleanup: 20 tasks (H-051..H-070)
- Silent failure elimination: 30 tasks (H-071..H-100)
- Dirty tree & completion: 35 tasks (H-101..H-135)

**Deliverables:**
✓ Green CI (no 501 panics, no silent || true)  
✓ 83 backend + 8 edge stubs callable, 501 responses  
✓ Cache/Neo4j/R2 removed, OpenTelemetry deferred  
✓ Duplicate ingest resolved, case-sensitive build passes  
✓ Vercel deploys unblocked, docs/WBS.md populated

**Unlocks:** P2, P3
