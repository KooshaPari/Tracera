# C. AgilePlus: Schema Lock, WP Integration, Ingest Pipeline

**Phase:** P3 (AgilePlus Repair)  
**Task Prefix:** AP-001..AP-100  
**Goal:** Lock spec-009, reconcile WP taxonomies, wire ingest pipeline, fix agileplus-mcpd  
**Depends On:** P1, P2  
**Unlocks:** P4 Product Witness

---

## AgilePlus Tasks (100 Leaf Tasks)

| Task | Description | Depends On | Est | Surface | Acceptance |
|------|-------------|-----------|-----|---------|-----------|
| AP-001 | Read spec-009 (current Draft version) | — | 10m | docs/agileplus/spec-009.md | Doc loaded, version noted |
| AP-002 | Identify all undefined fields in spec-009 Draft | AP-001 | 10m | spec-009 | List of undefined fields |
| AP-003 | Audit all WP-* references in spec-009 | AP-001 | 10m | spec-009 grep "WP-" | Count and list WPs |
| AP-004 | Create spec-009 v1.0 stabilization checklist | AP-002, AP-003 | 10m | docs/SPEC-009-STABILIZATION.md | Checklist created |
| AP-005 | Define missing WP schema fields (required/optional/default) | AP-002 | 15m | spec-009 | Schema completeness >80% |
| AP-006 | Lock spec-009 as v1.0 (move from Draft) | AP-005 | 10m | spec-009 YAML | version: "1.0" set |
| AP-007 | Create spec-009 changelog (v1.0 release notes) | AP-006 | 10m | docs/SPEC-009-CHANGELOG.md | Changelog created |
| AP-008 | Audit WP-00..25 taxonomy (Tracera internal) | — | 10m | repo WP docs | List all WPs |
| AP-009 | Audit WP-T01..T11 taxonomy (docs-5 canonical) | — | 10m | docs-5 WBS.md | List all WP-Ts |
| AP-010 | Audit WP-000..018 taxonomy (spec-014 AgilePlus) | — | 10m | spec-014 | List all WP-000s |
| AP-011 | Audit phase taxonomy (cockpit phases P0–P8) | — | 10m | 00_SESSION_OVERVIEW.md | List all phases |
| AP-012 | Create 4-taxonomy crosswalk table (WP-00 ↔ WP-T ↔ WP-000 ↔ phase) | AP-008..AP-011 | 20m | docs/TAXONOMY-CROSSWALK.md | Crosswalk table with mappings |
| AP-013 | Mark "unknown" cells in crosswalk for resolution | AP-012 | 10m | TAXONOMY-CROSSWALK | Unknown cells identified |
| AP-014 | Resolve unknown cells via spec/code audit | AP-013 | 30m | various specs | Unknown cells mapped or marked deferred |
| AP-015 | Create taxonomy reconciliation ADR | AP-014 | 10m | docs/ADR-TAX-001.md | ADR documents decisions |
| AP-016 | Locate agileplus-mcpd source (binary missing) | — | 10m | crates/, scripts/ | Source code found or listed as external |
| AP-017 | Check agileplus-mcpd build status (CI) | AP-016 | 10m | .github/workflows/ | CI job status reviewed |
| AP-018 | Build agileplus-mcpd locally (test build) | AP-016 | 15m | cargo build | Binary produced |
| AP-019 | Verify agileplus-mcpd binary is reproducible | AP-018 | 10m | dist/ or target/ | Binary checksum consistent |
| AP-020 | Create agileplus-mcpd release CI job | AP-019 | 10m | .github/workflows/ | Release job defined |
| AP-021 | Test agileplus-mcpd release artifact | AP-020 | 10m | CI | Artifact created and downloaded |
| AP-022 | Document agileplus-mcpd installation for users | AP-021 | 10m | docs/AGILEPLUS-MCPD-INSTALL.md | Installation guide created |
| AP-023 | Audit agileplus list command implementation | — | 10m | CLI code | Source reviewed |
| AP-024 | Reproduce SQLite timestamp crash | AP-023 | 15m | local test | Crash reproduced |
| AP-025 | Identify root cause: SQLite timestamp parsing | AP-024 | 10m | code analysis | Issue confirmed |
| AP-026 | Create fix: timestamp parsing in SQLite adapter | AP-025 | 15m | crates/agileplus-db/ | Fix implemented |
| AP-027 | Test fix: agileplus list with various timestamps | AP-026 | 10m | unit tests | Tests pass |
| AP-028 | Test fix: edge cases (null timestamps, future dates) | AP-026 | 10m | edge case tests | Edge cases handled |
| AP-029 | Update SQLite crate version (if needed for timestamp support) | AP-025 | 10m | Cargo.toml | Version updated |
| AP-030 | Run full test suite (agileplus) | AP-029 | 10m | cargo test agileplus | All tests pass |
| AP-031 | Audit false negatives in agileplus load (190 count) | — | 15m | CLI output analysis | Root causes identified |
| AP-032 | Audit false positives in agileplus load (14 count) | — | 15m | CLI output analysis | Root causes identified |
| AP-033 | Create false-negative reduction task list | AP-031 | 10m | docs/FALSE-NEG-REDUCTION.md | Task list for AP-034+ |
| AP-034 | Reduce false negatives by 50% (to <95) | AP-033 | 30m | agileplus code | Load check improved |
| AP-035 | Reduce false positives by 50% (to <7) | AP-032 | 30m | agileplus code | Load check improved |
| AP-036 | Create agileplus load test (measure false neg/pos) | AP-034, AP-035 | 10m | tests/load.rs | Test measures false neg/pos |
| AP-037 | Document false negatives remaining (post-fix) | AP-034 | 10m | docs/FALSE-NEG-KNOWN-ISSUES.md | Remaining issues listed |
| AP-038 | Document false positives remaining (post-fix) | AP-035 | 10m | docs/FALSE-POS-KNOWN-ISSUES.md | Remaining issues listed |
| AP-039 | Verify agileplus CLI API matches spec-009 contract | — | 10m | spec-009 vs CLI | Contract comparison |
| AP-040 | Create agileplus CLI contract test | AP-039 | 10m | tests/cli-contract.rs | Contract test created |
| AP-041 | Audit ingest pipeline (GitHub source) | — | 10m | crates/agileplus-ingest/ | Status reviewed |
| AP-042 | Audit ingest pipeline (Jira source) | — | 10m | crates/agileplus-ingest/ | Status reviewed |
| AP-043 | Audit ingest pipeline (AgilePlus source) | — | 10m | crates/agileplus-ingest/ | Status reviewed |
| AP-044 | Implement GitHub ingest pipeline stub | AP-041 | 20m | crates/agileplus-ingest/src/github.rs | Stub created |
| AP-045 | Implement Jira ingest pipeline stub | AP-042 | 20m | crates/agileplus-ingest/src/jira.rs | Stub created |
| AP-046 | Implement AgilePlus→Tracera ingest stub (federation) | AP-043 | 20m | crates/agileplus-ingest/src/federation.rs | Stub created |
| AP-047 | Test GitHub ingest with sample repo | AP-044 | 15m | tests/ingest/github.rs | Test passes |
| AP-048 | Test Jira ingest with sample issue tracker | AP-045 | 15m | tests/ingest/jira.rs | Test passes |
| AP-049 | Test AgilePlus↔Tracera federation ingest | AP-046 | 15m | tests/ingest/federation.rs | Test passes |
| AP-050 | Document ingest pipeline architecture | AP-046 | 10m | docs/AGILEPLUS-INGEST-ARCHITECTURE.md | Architecture doc |
| AP-051 | Create .agileplus config stub for Tracera | — | 10m | .agileplus (Tracera root) | Config file created |
| AP-052 | Create .agileplus config stub for AgilePlus | — | 10m | .agileplus (AgilePlus root) | Config file created |
| AP-053 | Create .agileplus config stub for Paperclip | — | 10m | .agileplus (Paperclip root) | Config file created |
| AP-054 | Create .agileplus config stub for Portal | — | 10m | .agileplus (Portal root) | Config file created |
| AP-055 | Document .agileplus config schema | AP-051..AP-054 | 10m | docs/AGILEPLUS-CONFIG-SCHEMA.md | Schema documented |
| AP-056 | Add kitty-specs directory structure for Tracera | — | 10m | kitty-specs/tracera/ | Directory created |
| AP-057 | Add kitty-specs directory structure for AgilePlus | — | 10m | kitty-specs/agileplus/ | Directory created |
| AP-058 | Add kitty-specs directory structure for Paperclip | — | 10m | kitty-specs/paperclip/ | Directory created |
| AP-059 | Add kitty-specs directory structure for Portal | — | 10m | kitty-specs/portal/ | Directory created |
| AP-060 | Document kitty-specs structure | AP-056..AP-059 | 10m | docs/KITTY-SPECS-STRUCTURE.md | Structure documented |
| AP-061 | Create docs/agileplus directory for Tracera AgilePlus docs | — | 10m | docs/agileplus/ (Tracera) | Directory created |
| AP-062 | Add Tracera AgilePlus onboarding guide to docs | AP-061 | 10m | docs/agileplus/TRACERA-ONBOARDING.md | Guide created |
| AP-063 | Create AgilePlus-specific CI job for Tracera | AP-062 | 10m | .github/workflows/agileplus.yml | Job defined |
| AP-064 | Create integration test: AgilePlus ↔ Tracera sync | AP-062 | 15m | tests/integration/agileplus_tracera_sync.rs | Test created |
| AP-065 | Implement AgilePlus sync automation script | AP-064 | 15m | scripts/agileplus-sync.sh | Script created |
| AP-066 | Document AgilePlus sync procedure | AP-065 | 10m | docs/AGILEPLUS-SYNC-PROCEDURE.md | Procedure documented |
| AP-067 | Audit legacy CI endpoints referenced in ingest | — | 10m | CI docs / code | Legacy endpoints listed |
| AP-068 | Create migration plan: legacy CI → new CI | AP-067 | 10m | docs/LEGACY-CI-MIGRATION.md | Plan documented |
| AP-069 | Implement new CI endpoints (stub 3–5 endpoints) | AP-068 | 20m | crates/agileplus-server/src/ | Endpoints created |
| AP-070 | Test new CI endpoints | AP-069 | 10m | tests/ | Endpoints respond correctly |
| AP-071 | Deprecate legacy CI endpoints | AP-070 | 10m | docs/CI-DEPRECATION.md | Deprecation notice |
| AP-072 | Audit spec-014 WP assignments (WP-000..018) | — | 10m | spec-014 | All WPs reviewed |
| AP-073 | Create spec-014 reconciliation task list | AP-072 | 10m | docs/SPEC-014-RECONCILIATION.md | List created |
| AP-074 | Verify spec-009 WP schema covers all spec-014 WPs | AP-006, AP-072 | 10m | comparison | Coverage >95% |
| AP-075 | Create WP boundary document (which WPs in which workstreams) | AP-074 | 10m | docs/WP-BOUNDARIES.md | Boundaries documented |
| AP-076 | Run cargo check on all agileplus crates | — | 10m | cargo check | 0 errors |
| AP-077 | Run cargo test on all agileplus crates | — | 10m | cargo test | All tests pass |
| AP-078 | Create agileplus release candidate (v1.0-rc.1) | AP-077 | 10m | git tag | Tag created |
| AP-079 | Build agileplus Docker image for P3 verification | AP-078 | 10m | Dockerfile | Image built successfully |
| AP-080 | Test agileplus Docker image locally | AP-079 | 10m | docker run | Container runs, CLI works |
| AP-081 | Push agileplus release candidate to registry | AP-080 | 10m | docker push | Image pushed |
| AP-082 | Create agileplus changelog for P3 | AP-081 | 10m | CHANGELOG.md | Changelog entry added |
| AP-083 | Document agileplus post-P3 roadmap | AP-082 | 10m | docs/AGILEPLUS-ROADMAP-POST-P3.md | Roadmap created |
| AP-084 | Create P3 completion gate checklist | AP-083 | 10m | docs/P3-GATE-CHECKLIST.md | Checklist created |
| AP-085 | Verify all P1 + P2 tasks complete (hygiene + registry) | — | 10m | Gate review | P1 + P2 complete |
| AP-086 | Run full CI on P3 deliverables | AP-084 | 10m | CI | All checks pass |
| AP-087 | Create P3→P4 dependency link | AP-086 | 10m | docs/03_DAG_WBS.md | P3 unlocks P4 noted |
| AP-088 | Commit all AgilePlus P3 changes | AP-087 | 10m | git commit | Changes committed |
| AP-089 | Push to origin/main (or feature branch) | AP-088 | 10m | git push | Pushed successfully |
| AP-090 | Create P3 PR with AgilePlus repair summary | AP-089 | 10m | GitHub PR | PR created |
| AP-091 | Review P3 PR and prepare for merge | AP-090 | 10m | PR review | Ready for merge |
| AP-092 | Merge P3 PR to main | AP-091 | 10m | git merge | Merged successfully |
| AP-093 | Tag P3 release on main | AP-092 | 10m | git tag | Release tag created |
| AP-094 | Verify P3 artifacts are available for P4 | AP-093 | 10m | artifact check | Artifacts accessible |
| AP-095 | Create cross-team handoff document (P3→P4) | AP-094 | 10m | docs/P3-P4-HANDOFF.md | Handoff doc created |
| AP-096 | Notify team of P3 completion and P4 readiness | AP-095 | 10m | Internal comms | Notification sent |
| AP-097 | Archive P3 session artifacts | AP-096 | 10m | docs/sessions/20261015-*/archive/ | Artifacts archived |
| AP-098 | Create post-P3 retrospective notes | AP-097 | 10m | docs/sessions/20261015-*/RETROSPECTIVE-P3.md | Notes created |
| AP-099 | P3 AgilePlus Phase Complete: sign-off and unlock P4 | AP-098 | 10m | gate review | P4 unblocked |
| AP-100 | Reserve: additional AgilePlus tasks post-P3 | AP-099 | 0m | — | Reserved |
