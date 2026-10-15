# Cockpit Takeover — session record

**Date:** 2026-10-14 (17:17 PDT takeover, 18:22 PDT doc written)
**Taken over from:** `session_pawprint_1789589862380_3f143f0ff67ff234` — CockPit / VP-Eng orchestrator
**Current cockpit session:** `session_rabbit_1792023467050_5be12ef1045add15`

---

## 1. Why takeover was needed

The prior cockpit ran 26 days (2026-09-19 → 2026-10-15T00:17Z), accumulating 10,674 messages
across a 22 MB transcript. It died mid-tool during a server reload at 17:17:30. Its last
operator signal was `proc`, and it was mid-build of work item **w7:p1R** (the session viewer) —
it had copied the session-metadata DB and stopped.

The transcript was never loaded whole. Four read-only subagents mined it in slices.

## 2. Runtime state at takeover (verified)

| Check                                    | Result                                                                     |
| ---------------------------------------- | -------------------------------------------------------------------------- |
| Orphaned processes targeting pawprint    | **none**                                                                   |
| Armed scheduled tasks targeting pawprint | **none** (old ticks consumed)                                              |
| Armed scheduled tasks overall            | 3 — `sched_99904994` (HeliosLite streak-18), two weekly memory-maintenance |
| Ambient queue location                   | `~/.jcode/ambient/queue.json`                                              |
| Live herdr panes                         | 16, all owned by other sessions                                            |
| Live `jcode --resume` TUI processes      | 19                                                                         |

No cleanup was required. The old tick loop drained cleanly before the reload.

## 3. What was shipped in the takeover

**w7:p1R session viewer — complete.**

- `~/.jcode/session-viewer/build.py` — stdlib-only generator
- `~/.jcode/session-viewer/index.html` — **4,341 sessions**, 1.17 MB
- Opened for the operator in Safari via `open location "file:///Users/kooshapari/.jcode/session-viewer/index.html"`

Feature set: text search across title/dir/id, working-dir facet, sortable columns, expandable
rows, per-row and bulk session-id copy. Zero external requests — verified no `<link>`, `src=`,
`fetch(`, or `import(` in the output. Works offline from `file://`.

Refresh: `python3 ~/.jcode/session-viewer/build.py` (~12 s).

**Root cause of the original stall (worth keeping):** the session-metadata DB is in WAL mode.
A plain read-only sqlite URI `file:…?mode=ro` **fails** with `unable to open database file`
because it tries to create `-shm`/`-wal` sidecars. The working form is
`file:…?mode=ro&immutable=1`, which skips WAL entirely and reads the main DB instantly.

**This also answers the operator's original blocker.** The prior session spent many turns failing
to find a "URI" to open in Safari for the w7:p1R investigation. The finding: **jcode has no web
UI at all** — no TCP listener, UNIX sockets only (`/var/folders/wl/…/jcode.sock`,
`jcode-debug.sock`), and the TUI resume picker is interactive-TTY only. The sessions were never
missing (4,341 in the metadata DB, 7,640+ transcript JSONs on disk, all `saved=0`). The static
page is the correct surface.

## 4. Loss-prevention performed

The 8-file cockpit docset (`docs/sessions/2026-10-12-cockpit-refresh/`) is **untracked** in
Tracera, and Tracera is **2 ahead / 77 behind** origin/main. A second reload would destroy it.

Copied to a location outside any git repo, verified byte-identical:

```
/Users/kooshapari/CodeProjects/docs/_archive/cockpit-refresh-backup-20261014/
```

All 8 canonical `.md` files (`00`–`06`, `MANIFEST`) confirmed matching via `cmp`. The `.bak-*`
working backups were deliberately not copied.

**Still open:** whether to actually commit the docset to git. That needs operator authorization
(standing rule: no autonomous commits without a signal).

## 5. Verified repo state

| Repo               | State                                                                                                                                                                        |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Tracera`          | `main` — 2 ahead, 77 behind origin. Docset untracked.                                                                                                                        |
| `koosha-phenotype` | current site source for `dash.kooshapari.com`; nav confirmed `Work \| Resume \| Contact`; `scripts/views/parent.js` does **not** exist yet (that is the Phase 1 deliverable) |
| `HeliosLab`        | 1 unpushed commit (`2071c9c3`), **91 behind**, 13 uncommitted mods including 27 `<REDACTED>` username substitutions (working tree only, never committed)                     |
| `PhenoShared`      | 1 untracked session folder (`docs/sessions/2026-10-12-cleanup-and-release/`, 6 files)                                                                                        |

## 6. Branch loss (new finding, not previously recorded)

All four branches referenced by the cockpit docset are **absent from origin**:

- `feature/cockpit-parent-view` — the consolidated Phase 1 branch
- `feature/cockpit-appshell`
- `feat/dimensional-layering`
- `agent/cockpit-refresh`

**Repo correction (2026-10-14T18:45 PDT):** these are spread across two repos, and an earlier
version of this record implied they were all in one. Phase 1's branch,
`feature/cockpit-parent-view`, belongs to **`koosha-phenotype`** (the site source), not Tracera.

**Resolved:** `feature/cockpit-parent-view` has been recreated in `koosha-phenotype` and pushed
to origin at `e5f2a03`, based on an exact `origin/main` match with a clean working tree — so it
inherits none of the operator's in-flight WIP, which is what `05_BLOCKERS.md` requires. Phase 1
is no longer blocked on branch availability. `scripts/views/parent.js` is still absent, so no
Phase 1 code exists yet.

The remaining three names (`feature/cockpit-appshell`, `feat/dimensional-layering`,
`agent/cockpit-refresh`) were not all superseded the same way. Correction to an earlier
draft of this record, which wrongly implied that: `feat/dimensional-layering` is **not** a
superseded cockpit branch — it is the operator's independent visual-novelty work (a 4-step
elevation ladder utility), as `02_CURRENT_STATE.md` and `05_BLOCKERS.md` B6 already record
correctly. It is absent from origin only because it has landed or been dropped on the
operator's side; it is not part of this plan and is not being recreated here.
`feature/cockpit-appshell` and `agent/cockpit-refresh` **were** superseded by revision 3's
single-branch decision and are likewise not being recreated.

## 7. Operator directives — still binding

From `01_OPERATOR_DIRECTIVES.md` (verbatim signal 2026-10-12T22:33Z), 9 directives:

1. `dash.kooshapari.com` lands on `/parent/` **first**
2. **NOT** the naive 4-tab default
3. Replace naive tabs with a richer unified platform design
4. MCP server agent surface (Tracera `crates/tracera-mcp`)
5. CLI agent surface (Tracera `crates/tracera-cli`)
6. Skill/plugin agent surface
7. Tracera/Paperclip for **personal** use, not just jobs
8. Keep 15-min refresh + per-agent state
9. Plan first; no force-push; everything behind Cloudflare Access

**Amendment 4:48 PM (D14):** the `[Instinct]` title prefix is **title-scoped only** — heavy and
architecture PRs use plain titles. The `Authored by Instinct` PR-body first line still applies
to **all** PRs. Standing instruction "do NOT invent" remains in force for unstated specifics.

## 8. Config directive — verified applied

Operator directive 2026-10-14: set default model to openai-compatible MiniMax-M3; compaction
trigger at `min(80% of ctx, 512k)`; resulting compressed context at 40% of that.

Verified in `~/.jcode/config.toml`:

- `[provider] default_provider = "openai-compatible"`, `default_model = "MiniMax-M3.1-Flash-Preview"`
- `[compaction] max_context_tokens = 640000` — encodes the trigger exactly, since
  `0.8 × min(ctx, 640k) == min(0.8·ctx, 512k)`
- The 40% target has **no config key**. It is emergent from the summary prompt plus
  `RECENT_TURNS_TO_KEEP`. This is documented in the config comments rather than silently assumed.

## 9. Open items awaiting the operator

**Blocking all of Phase 1** — the 7 design decisions P1–P7, double-sourced in
`05_BLOCKERS.md` and `06_DECISION_LOG.md`: `/parent/` visual design, personal-mode issue fields,
MCP exposure target, 15-min refresh source, `/parent/` as landing route, 9-agent data source,
bundle budget (measured 212.3 KB against a ≤230 KB convention; the earlier 228.7 KB figure in
this line was stale and contradicted the correction already recorded in this same file below).

**Other open items:**

- Deploy secrets never supplied: `RESEND_WEBHOOK_SECRET`, `DISCORD_BRIDGE_HMAC_SECRET`,
  `DISCORD_WEBHOOK_URL`
- Commit the cockpit docset to git?
- HeliosLab redactions / 1-ahead-91-behind disposition
- Retime `sched_99904994` (HeliosLite streak-18 wake fires 14:15Z but the workflow cron is
  `30 6 * * *`, so it lands ~8h stale-by-design)
- Persistent scheduled-task delivery delay — 4 consecutive late fires
  (9h49m, 7h17m, 8h29m, 9h13m); see `~/.jcode/scratch/sched_delivery_audit_20261012.md`

## 10. Recommended defaults if the operator does not answer

Stated in the MCQ delivered 2026-10-14T17:51 PDT so that non-answered items still have a sane
value and are recorded as decisions rather than left dangling:

P1 design from constitution · P2 tag/label only · P3 reuse `:8081` · P4 `setInterval` ·
P5 redirect `/` → `/parent/` · P6 live `/api/agents` with static fallback · P7 lazy-load.

**P7 was subsequently corrected by measurement, so the recommendation above no longer stands as
given.** The real bundle is **212.3 KB** (`bundled/app.bundle.*.js`, measured 2026-10-14 with
zero source changes since that build), not 228.7 KB — so there is ~17.7 KB of headroom rather
than a shortfall, and the premise that `/parent/` "will likely push over budget" is not
supported. Lazy-load is still defensible for code-splitting and first paint, but it is no longer
_required_ by the budget, and the operator may reasonably prefer to spend the headroom instead.
The 230 KB figure is a documented convention; no CI check enforces it. Corrected in `00`, `02`,
`05`, and `06`.

These are recommendations, not operator decisions. They must be labelled as such in
`06_DECISION_LOG.md` if adopted.
