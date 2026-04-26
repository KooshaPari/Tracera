# phenoSDK GitHub 404 Reconciliation

**Date:** 2026-04-26
**Trigger:** Round-34 badge agent flagged local `repos/phenoSDK/` has its own `.git/` but `gh api repos/KooshaPari/phenoSDK` returns 404.

## Verdict

**B + C hybrid: CONSOLIDATED into AuthKit, then HARD-DELETED on GitHub.** The local `repos/phenoSDK/` is now an **orphan working copy** whose `origin` (`https://github.com/KooshaPari/phenoSDK.git`) no longer exists.

## Evidence

1. **GitHub API:** `gh api repos/KooshaPari/phenoSDK` -> `{"message":"Not Found","status":"404"}`. HTTP `https://github.com/KooshaPari/phenoSDK` -> `404` with no `Location` redirect (a rename would 301-redirect).
2. **Local remote:** `origin = https://github.com/KooshaPari/phenoSDK.git` (still pointing to the deleted repo).
3. **Local commit history (`master` branch, last commit `1536c55`, 2026-04-25):**
   - `dc84453 docs(deprecation): add DEPRECATION.md directing to AuthKit consolidation`
   - `c523501 feat: complete phenoSDK decomposition - move final core files`
   - `295b6b5 feat: remove all 48 extracted modules from phenoSDK`
4. **Local `DEPRECATION.md`** explicitly redirects users to **AuthKit**.
5. **AuthKit exists on GitHub** (`gh api repos/KooshaPari/AuthKit` -> active, pushed 2026-04-26) and locally at `repos/AuthKit/` with full structure (Go + Python SDKs, FRs, docs).
6. **Case variants ruled out:**
   - `pheno-sdk` exists but is **archived** since 2025-10-15, described as "ATOMS-PHENO SDK for infrastructure migration" — unrelated lineage (older atoms-pheno work, not the consolidated SDK).
   - No other `*sdk*` / `*Sdk*` / `*SDK*` repos under `KooshaPari/`.
7. **Archive folder:** `.archive/phenoSDK-deprecated-2026-04-05/` contains an earlier deprecation snapshot (pre-AuthKit final consolidation).
8. **Local content size:** 23M, mostly docs (README, CHANGELOG, DEPRECATION, CLAUDE, governance scaffolding). 48 modules already extracted; only deprecation/governance shell remains.

## What happened (timeline reconstruction)

1. **2026-04-05:** First deprecation pass — copied to `.archive/phenoSDK-deprecated-2026-04-05/`.
2. **Wave-2/3 hygiene (2026-04 mid):** Decomposition completed (48 modules removed, final core files moved out, presumably into AuthKit / phenoShared / phenoUtils / phenotype-auth-ts).
3. **2026-04-25:** Worklog scaffolding + DEPRECATION.md added pointing to AuthKit.
4. **Between 2026-04-25 and 2026-04-26:** GitHub repo `KooshaPari/phenoSDK` **hard-deleted** (no rename redirect). Local working copy orphaned.

## Recommended action

**Archive the local copy, do not re-clone, do not delete yet.**

Rationale: the local `phenoSDK/` still has 4 unmerged local branches (`chore/phenosdk-deprecation-docs-20260426`, `chore/phenosdk-deprecation-pack-20260426`, `chore/phenosdk-docs-deprecation-20260426`, `chore/add-reusable-workflows`) whose commits never reached origin (origin gone). Their content — DEPRECATION.md variants and a deprecation pack — is governance audit trail.

### Steps (deferred, do not execute in this commit)

1. `mv repos/phenoSDK repos/.archive/phenoSDK-orphan-2026-04-26` (preserve all 4 branches + reflog).
2. `mv repos/phenoSDK-wtrees repos/.archive/phenoSDK-wtrees-orphan-2026-04-26` if it has no live work.
3. Verify any remaining content (DEPRECATION pack, worklog) is mirrored into AuthKit's `docs/` or `phenotype-org-audits/`.
4. Update `docs/org-audit-2026-04/active-repos-20260426.tsv` to remove phenoSDK from active list.
5. Update `docs/governance/nested_workspaces.md` — mark item 1 (phenoSDK GitHub state) as RESOLVED.
6. Round-34 badge agent: skip phenoSDK going forward (no upstream to badge).

### Do NOT

- Do **not** re-create `KooshaPari/phenoSDK` on GitHub. Consolidation into AuthKit is final per `DEPRECATION.md`.
- Do **not** consolidate with the archived `pheno-sdk` (different lineage).
- Do **not** push from the orphaned local copy — origin is dead.

## Cross-references

- Memory: `feedback_repo_identity_verification.md` — exemplifies "verify repo identity before trusting README/CLAUDE/memory."
- Memory: `reference_phenoshared_alias.md` — different pattern (rename redirect preserved); phenoSDK is a true delete, not a rename.
- Local: `repos/phenoSDK/DEPRECATION.md` — canonical redirect to AuthKit.
- GitHub: `KooshaPari/AuthKit` — consolidation target, active.
- Archive: `.archive/phenoSDK-deprecated-2026-04-05/` — earlier deprecation snapshot.
