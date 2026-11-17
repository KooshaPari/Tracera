# Known Issues & Blockers: Pre-Execution State

Blockers identified during P0 planning, organized by severity. All are targeted for closure by end of execution (P8).

## Blocker-Severity Issues (Must Fix Before Gate Closure)

| Issue | Area | Mitigation | Depends On |
|-------|------|-----------|-----------|
| 83 backend routes return 501 | P1 | Stub routes with clear 501 responses | H-021..H-050 |
| Duplicate ingest.rs breaks case-sensitive builds | P1 | Apply upstream fix, add pre-commit hook | H-001..H-020 |
| AgilePlus spec-009 remains Draft | P3 | Lock spec-009 as v1.0, unblock WP import | AP-001..AP-040 |
| Four WP taxonomies unreconciled | P3 | Create explicit crosswalk (WP-00↔WP-T↔WP-000↔phase) | AP-041..AP-090 |
| Registry excludes Tracera/AgilePlus (archived status) | P2 | Mark Tracera active, add AgilePlus, remove duplicates | R-001..R-070 |
| Frontend fake-healthy fallbacks hide outages (#1121) | P1, P4 | Add explicit error display, fail-loud on 501 | H-043..H-045, PW-* |
| UI calls unregistered routes (#1119) | P1, P4 | All routes either real or stub returning 501 | H-035, PW-* |

## Major-Severity Issues (Close During Execution)

| Issue | Area | Task Range |
|-------|------|-----------|
| Unused clients (Cache, Neo4j, R2) | P1 | H-051..H-070 |
| OpenTelemetry not instrumented (ADR-OBS-001) | P1 (deferred) | H-066..H-068 |
| Vercel deploy failing | P1 | H-080..H-084 |
| agileplus-mcpd binary missing | P3 | AP-101..AP-105 |
| agileplus list crash (timestamp parsing) | P3 | AP-099..AP-100 |
| Paperclip daemon crashed (SIGTERM 2026-10-14) | P5 | PC-001..PC-015 |
| Portal /parent/ 15-min refresh only updates timestamp (no refetch) | P6 | PO-082..PO-086 |
| No Cloudflare Worker proxy for /api/parent/* | P6 | PO-001..PO-040 |
| Herdr pane state does not reach Paperclip | P5 | PC-096 |
| CI.yml TypeScript jobs end in `|| true` (silent failures) | P1 | H-073..H-075 |

## Minor-Severity Issues (Track, May Defer Post-Gate)

- docs/WBS.md is 0 bytes (populate in P1)
- 7 fragile postinstall patches (document in P1)
- 12 open PRs with 3 conflicting (review/resolve)
- 13 worktrees, several dirty (clean up)
- ~100 intent/boundary doc stubs (populate critical ones in P2)
- Stylelint mutates source in CI (fix in P1)
- Typecheck uses repeated -p flags (optimize in P1)
- Visual accessibility contrast failures in Portal (fix in P6)

## Issues to Carry Forward (Out of Scope for This Delivery)

- tracera-graphql, tracera-ml, tracera-neo4j modules (outside workspace; assess in future)
- Second Atlas copy (consolidate in future audit)
- Duplicate Onboarding project vs. multiple cockpit projects (assess org model post-delivery)

## Known Uncertainties (Will Clarify During Execution)

- **Q: Which Paperclip tools are real vs. stubs?** A: Determined in P5 (PC-049..PC-058)
- **Q: How many false negatives will the load check have after fixes?** A: Measured in P3 (AP-112..AP-114)
- **Q: Can independent operator be recruited for A3 witness?** A: Confirmed in P4 (PW-105)
- **Q: Will AgilePlus ingest pipeline complete bidirectional federation?** A: Tested in P8 (AD-089..AD-092)

All blockers closed → gate certified → Tracera delivery complete.
