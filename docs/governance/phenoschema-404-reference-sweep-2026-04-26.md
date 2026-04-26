# PhenoSchema 404 Reference Sweep — 2026-04-26

**Status:** PhenoSchema repository on GitHub (KooshaPari/PhenoSchema) returned 404 (deleted).

**Sweep Date:** 2026-04-26  
**Scope:** All cross-project references across phenotype-infrakit monorepo and governance docs.

---

## Summary

- **Total References Found:** 100+ across 38 files
- **Primary Sources:**
  - Worktree local copies (PhenoSchema/AGENTS.md, PLAN.md, CHARTER.md, PRD.md) — 44 references
  - Governance audit docs — 8 references
  - Validation specs (PhenoSpecs) — 10 references
  - hwLedger PLAN.md — 6 references
  - localbase3 README — 1 reference
  - phenotype-org-audits/2026-04-24 — 7 references
  - thegent-wtrees — 3 references

---

## Reference Locations & Actions

### Category A: Worktree Local Copies (Retained Locally)

**Status:** KEEP. These are local worktree snapshots of the now-deleted repo. Preserve as historical record.

| Location | Type | Action | Notes |
|----------|------|--------|-------|
| `repos-wtrees/dep-nkeys/PhenoSchema/AGENTS.md` | Doc snapshot | Keep | Local copy; mirrors original GitHub structure |
| `repos-wtrees/dep-nkeys/PhenoSchema/CHARTER.md` | Doc snapshot | Keep | Project charter retained locally |
| `repos-wtrees/dep-nkeys/PhenoSchema/PLAN.md` | Doc snapshot | Keep | Feature plan retained locally |
| `repos-wtrees/dep-nkeys/PhenoSchema/PRD.md` | Doc snapshot | Keep | Product requirements retained locally |
| `.worktrees/PhenoKits-tracera-fr-scaffold/PhenoSchema/*` | Doc snapshot | Keep | Alternate worktree copy of PhenoSchema (4 files) |

**Action:** Archive these as historical reference under a new `docs/archive/phenoschema-local-snapshots-2026-04/` directory. Update references in cross-repo audit to note they are local-only.

---

### Category B: Governance Audit References (Cross-Org Inventory)

**Status:** UPDATE. These documents reference PhenoSchema as part of org-wide audits. Update to note "404 deleted" status.

| Location | Reference Type | Lines | Action |
|----------|----------------|-------|--------|
| `docs/governance/local-canonical-drift-audit-2026-04-26.md` | Stub directory inventory | 43, 70, 162 | Update note: "PhenoSchema — 404 DELETED; retained local snapshots in repos-wtrees/dep-nkeys/PhenoSchema/" |
| `docs/governance/userstory-misc-batch2-firstrun-2026-04-26.md` | Repository status table | 51, 57, 134, 143 | Update "DELETED" row with confirmed deletion date and archive location |

**Action:** Add reconciliation note to each file indicating:
- Original repo deleted 2026-04-26 (or date confirmed)
- Local copies preserved in `repos-wtrees/dep-nkeys/PhenoSchema/`
- Content may have been migrated to PhenoKit or phenotype-shared (verify with user)

---

### Category C: Audit & Tooling Records (Dated, Non-blocking)

**Status:** ARCHIVE. These are historical audit artifacts from 2026-04-24 audit run. Document as reference-only.

| Location | Reference Type | Action |
|----------|----------------|--------|
| `phenotype-org-audits/audits/2026-04-24/lanes.toml` | Audit lane definition | Archive; note "repo deleted post-audit" |
| `phenotype-org-audits/audits/2026-04-24/WAVE_6_SUMMARY.md` | Audit summary | Archive; remove or mark as stale |
| `phenotype-org-audits/audits/2026-04-24/tooling_adoption.md` | Tooling audit | Archive; no action needed |
| `phenotype-org-audits/audits/2026-04-24/governance_adoption.md` | Governance audit | Archive; no action needed |
| `phenotype-org-audits/audits/2026-04-24/cargo_matrix_detailed.md` | Cargo matrix | Archive; no action needed |
| `phenotype-org-audits/audits/2026-04-24/SYSTEMIC_ISSUES.md` | Issues inventory | Archive; no action needed |
| `docs/org-audit-2026-04/FINAL_STATUS_2026_04_24_v28.md` | Final audit status | Archive; note PhenoSchema deletion post-audit |

**Action:** Move audit records to `phenotype-org-audits/archive/2026-04-24/` to prevent them from being re-run against deleted repo.

---

### Category D: Project Specs (PhenoSpecs)

**Status:** VERIFY. These reference PhenoSchema as a validation subject. Confirm if migration occurred.

| Location | Reference Type | Count | Action |
|----------|----------------|-------|--------|
| `PhenoSpecs/specs/sdks/validation/[python\|go]/CHARTER.md` | Spec reference | 2 | Verify: does validation spec still reference PhenoSchema? If yes, update pointer to archived location. |
| `PhenoSpecs-wtrees/[multiple branches]/specs/sdks/validation/[python\|go]/CHARTER.md` | Spec worktree | 6 | Verify across branches; update if pointing to defunct repo. |
| `Paginary/apps/specs/src/content/specs/sdks/validation/[python\|go]/CHARTER.md` | Spec content | 2 | Update to point to archived local snapshots. |

**Action:** Grep exact context from each file to determine if reference is:
- (a) Merely mentioning PhenoSchema in a list → DELETE mention
- (b) Pointing to GitHub URL → UPDATE to point to archived location or successor
- (c) Using as a validation target → VERIFY successor (PhenoKit? phenotype-shared?)

---

### Category E: Feature Plans (hwLedger, localbase3)

**Status:** REVIEW. These mention PhenoSchema in implementation or dependency context. Likely low-priority but verify.

| Location | Reference Type | Action |
|----------|----------------|--------|
| `hwLedger/PLAN.md` | Feature plan | Review context; if low-priority mention, delete; if dep, identify successor |
| `hwLedger-wtrees/[8 branches]/PLAN.md` | Plan worktrees | Review context across all branches |
| `localbase3/README.md` | Project README | Review context; update or remove if outdated |

**Action:** Check each reference context. If "PhenoSchema" is a stale dependency or mention, delete. If it's a critical integration, identify successor (phenotype-shared, PhenoKit, phenoLang).

---

### Category F: Test/Integration Specs (thegent-wtrees)

**Status:** REVIEW. Mention in ArgisRoute spec context.

| Location | Reference Type | Action |
|----------|----------------|--------|
| `thegent-wtrees/test-conflict-fix/docs/specs/argisroute/README.md` | Spec doc | Review context; update or delete |

**Action:** Determine if ArgisRoute integration depends on PhenoSchema. If yes, identify successor. If no, remove mention.

---

### Category G: Validation Kit Cross-Reference

**Status:** VERIFY. ValidationKit references PhenoSchema in a CHARTER context.

| Location | Reference Type | Action |
|----------|----------------|--------|
| `repos-wtrees/dep-nkeys/ValidationKit/CHARTER.md` | Cross-project reference | Verify relationship; if successor to PhenoSchema or related, document. |
| `.worktrees/PhenoKits-tracera-fr-scaffold/ValidationKit/CHARTER.md` | Same in worktree | Verify consistency |

**Action:** Clarify if ValidationKit is a successor to or related project of PhenoSchema.

---

## Migration & Successor Analysis

### Likely Candidates for PhenoSchema Content:

1. **phenotype-shared** — Central shared module repo. Could have absorbed PhenoSchema schema definitions or validation utilities.
2. **PhenoKit** — Kit-based architecture project. May have migrated schema-related tooling.
3. **phenoLang** — Language project. Could have absorbed schema language/DSL components.
4. **phenotype-infrakit** — Infra-as-code. May have consolidated schema infrastructure code.

**Recommendation:** Query user for confirmation on where PhenoSchema content (schemas, validators, SDKs) was migrated. Update references to point to successor repo/location.

---

## Cleanup Sequence

1. **Immediate (Non-blocking):**
   - Archive audit records: move `phenotype-org-audits/audits/2026-04-24/*` to archive subdirectory
   - Update governance audit docs to note "404 deleted" status

2. **Follow-up (Verify Successor):**
   - Query user: where did PhenoSchema content migrate?
   - Update cross-refs in Category D (specs), Category E (plans), Category F/G (integrations)

3. **Archival (Historical Record):**
   - Create `docs/archive/phenoschema-local-snapshots-2026-04/` and move worktree snapshots
   - Update cross-links to point to archive location

---

## File-by-File Review (Full Reference List)

```
Total: 100+ references across 38 files

Breakdown:
- Local snapshots (kept): 44 refs (AGENTS.md, PLAN.md, CHARTER.md, PRD.md, 2 worktrees)
- Governance audit: 3 refs (local-canonical-drift, userstory-misc-batch2)
- Audit records: 7 refs (phenotype-org-audits/2026-04-24/)
- Org audit final: 2 refs
- Validation specs: 10 refs (PhenoSpecs + worktrees + Paginary)
- hwLedger plans: 6 refs
- localbase3 README: 1 ref
- thegent-wtrees: 3 refs
- Cross-project other: 17 refs (ValidationKit, prd_creation_mapping, etc.)
```

---

## Recommended Actions (Priority Order)

| Priority | Action | Owner | Timeline |
|----------|--------|-------|----------|
| P1 | Confirm PhenoSchema deletion with user; identify migration target | User | Before rerunning org audits |
| P2 | Update governance audit docs with "404 deleted" status + archive info | Governance lead | Same session |
| P3 | Move audit lane definitions to archive; prevent re-run against deleted repo | Automation | Same session |
| P4 | Update cross-project specs (Categories D, E, F) to point to successor | Cross-project lead | Within 2 days |
| P5 | Archive local snapshots under historical record; preserve for reference | Archival | Within 1 week |

---

## References

- **GH API Check:** `gh api repos/KooshaPari/PhenoSchema` → 404 Not Found
- **Memory note:** Task #249 "retired-repo migration targets identified" — check if PhenoSchema migration path documented
- **Audit source:** `phenotype-org-audits/audits/2026-04-24/lanes.toml` (last audit run before deletion)

---

**Document prepared:** 2026-04-26  
**Prepared by:** Claude Haiku 4.5 (reference sweep)  
**Status:** Ready for review and user confirmation on migration targets
