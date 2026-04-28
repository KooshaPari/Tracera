# Repo Atlas Prompts

**When to use:** You need a high-fidelity map of a vibecoded codebase, including ownership, hotspots, and pheno-sdk overlap, before planning changes.

## Quick Start
1. Gather path ownership notes, tooling access, and recent repo snapshots.
2. Choose the prompt version that matches your time box (full atlas, quick snapshot, or delta update).
3. Paste the prompt block into your assistant and provide repo-specific details as needed.

## Variations
- **Full Atlas (default)** – exhaustive inventory with tables, graphs, and next-step guidance.
- **Quick Snapshot** – condensed report for leadership syncs or morning standups.
- **Delta Update** – compare current state against a previous atlas to surface drift.

### Quick Snapshot Prompt
```
Produce a lightweight repo map for <REPO>. Include: top-level directories with LOC/file counts, the three hottest files (LOC + churn), key pheno-sdk touchpoints, and biggest ownership gaps. Finish with three recommended immediate actions.
```

### Delta Update Prompt
```
Using the previous atlas dated <DATE>, highlight what changed: new/removed directories, LOC shifts, dependency deltas, pheno-sdk integration changes, and ownership updates. Call out regressions (tests removed, new large files) and suggest mitigation steps.
```

## Full Atlas Prompt
```
You’re the mapper-in-chief for a vibecoded Python SDK monorepo packed with frameworks, utilities, and half-documented experiments. You must produce a copy-pasteable ASCII atlas that anyone can use to navigate, contribute, or refactor. Minimal hand-waving; maximum transparency. Whenever you describe reusable scaffolding or shared patterns, call out when they should come from ~/temp-PRODVERCEL/kush/pheno-sdk instead of being rebuilt. Also note spots that already mirror pheno-sdk and can be consolidated.

Confirm or call out missing inputs first:
- Snapshot of the root tree (packages, data/config, docs, tooling, experiments), with LOC and file counts.
- `git` access for churn stats, `cloc`, or equivalent. If tools are blocked, note it and propose a workaround.
- Known ownership map (even if it’s “probably this person”), release targets, significant consumers.
- Build scripts (`Makefile`, `tasks.py`, `./zen`, etc.), CI workflow files, dependency lockfiles.
- Where binaries/generated stuff live, path exclusions (secrets, huge data), and how pheno-sdk is integrated today.

If something is unknown, write it down, explain why you need it, and mark assumptions in the diagram with `?`.

Analysis steps (record metrics with commands/snippets):
1. Top-level layout table: for each directory/file at the root, log type (pkg/infra/docs/etc.), LOC, file count, largest file, owner, primary language, last commit date, and notes. Flag anything oversized or weird (binary piles, hidden dirs). Identify directories that should be replaced by or merged into pheno-sdk.
2. Package map: each package → purpose, layer (domain, adapter, infra, shared, CLI, experimental), public module names, key dependencies, tests location, release artifact, docs status. Highlight any package that could be replaced by or depends heavily on pheno-sdk components.
3. Internal dependency mesh: ASCII DAG (or adjacency list) showing package import relations. Mark cycles, heavy hubs, cross-layer calls, optional dependencies. Note where pheno-sdk sits in the graph (or should sit) and any direct forks of its functionality.
4. External dependencies: mini table with package → pinned version → reason → notes (duplication, vendored, optional). Highlight mismatched versions, vendored copies, and cases where pheno-sdk might already wrap the same dependency.
5. Config surfaces: list all config files/directories, env var prefixes, CLI flags, feature toggles, default logic. Mention collisions or confusing precedence rules. Point at pheno-sdk config utilities whenever they exist.
6. Testing & CI map: packages → test folders → frameworks → average runtime → coverage status → associated CI jobs/workflows → flaky markers. Note missing tests or manual-only checks, and whether pheno-sdk supplies shared test helpers or fixtures.
7. File hotspots: top 10 largest Python files with LOC and biggest contributors; highest churn files (past 6–12 months) and who touched them; modules with high complexity but no typing. Flag suspicious “put everything here” modules and indicate if pheno-sdk offers cleaner abstractions.
8. Docs & ADR coverage: what README/guide files exist, where ADRs/live docs live, packages without docs, stale docs. Note if pheno-sdk already maintains central docs that can be referenced instead of duplicating.
9. Ownership overlay: for each major directory, note owner/maintainer/on-call or “unowned.” Flag overlapping or conflicting ownership, single-person bus factors, abandoned experiments. Mention if pheno-sdk team owns relevant shared bits.
10. Automation & guardrails: note existing linters/formatters/pre-commit, excluded paths, architecture scripts, doc builds. Highlight where shared automation from pheno-sdk should be reused.

Output order (each section separated by `---`):
1. Summary – 6–8 sentences describing structure, hotspots, unknowns, and how serious the drift is. Mention how pheno-sdk reuse factors into the diagnosis.
2. Repo Overview Table – ASCII table with columns (Path | Type | LOC | Files | Largest File | Owner | Last Commit | Notes | pheno-sdk overlap?).
3. Package Map – bullet list or table for each package with purpose, layer, dependencies, tests, docs state, and “pheno-sdk leverage” (reuse, extend, migrate).
4. Dependency DAG & Build Outputs – ASCII graph plus list of build artifacts (wheels, CLIs, containers) and where they come from. Show how pheno-sdk is consumed or should be.
5. Config & Flags Inventory – table listing files/env prefixes/CLI commands, notes on defaults/fallbacks, and whether pheno-sdk config helpers exist.
6. Testing & CI Matrix – table linking packages to test suites to CI jobs with runtimes/coverage/gaps and references to shared test utilities.
7. Hotspots & Notables – bullet list highlighting biggest files, highest churn, policy deviations, orphaned directories, with hints on pheno-sdk replacements.
8. Docs & Ownership Notes – where docs live, who owns what, any gaps, and how pheno-sdk docs tie in.
9. Risks & Unknowns – missing data, suspicious directories, unmaintained sections, pheno-sdk integration risks requiring manual review.
10. Next Steps / Required Inputs – everything to do after the atlas: confirm ownership, fix biggest hotspots, adopt pheno-sdk components to reduce duplication, set automation to regenerate map, gather missing info, propose a cadence for atlas refresh.

Ground rules:
- Include the command used for each metric (e.g., `cloc`, `git log --stat`, `du -sh`). Mention if it’s a shared script from pheno-sdk.
- Keep diagrams/tables under 120 columns, ASCII only.
- Use the same names for components across sections (no alias confusion).
- Highlight optional modules or uncertain items with `(opt)` or `?`.
- Stay clear and conversational—this is for hackers and maintainers, not execs.
- Call out every chance to drop custom code in favor of the shared `pheno-sdk` library or other tried-and-true tooling.
```
