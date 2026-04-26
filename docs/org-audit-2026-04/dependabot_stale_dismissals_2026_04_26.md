# Dependabot STALE-DEP Batch Dismissals — 2026-04-26

**Source:** `dependabot_tier2_triage_2026_04_26.md` STALE-DEP category (21 alerts).
**Action:** Dismissed via GitHub REST API (`PATCH /repos/{owner}/{repo}/dependabot/alerts/{n}`).
**Reason code:** `not_used` (deps live exclusively in archived / legacy paths and are not part of the active build/runtime).
**Comment:** "Dep in archived/dead-code path (ARCHIVE/CONFIG/ or kvirtualstage-legacy/) — see audit 2026-04-26 (dependabot_stale_dismissals_2026_04_26.md)"

## Verification

- **Tracera `ARCHIVE/CONFIG/default/`** — verified present on `main` via Contents API; vendored snapshot of historical npm package.json files. Not consumed by active build (no root manifest references), no CI uses these paths.
- **KDesktopVirt `kvirtualstage-legacy/`** — verified present on `main`; superseded by eco-011 rebuild (per memory `reference_device_automation_repos.md`). KaskMan/KVirtualStage rebuild in progress; legacy tree retained for reference only.

## Dismissals — Tracera (13)

| Alert # | Package | Severity | Manifest |
|---|---|---|---|
| 338 | srvx | medium | `ARCHIVE/CONFIG/default/srvx@0.8.16@@@1/package.json` |
| 305 | rollup | high | `ARCHIVE/CONFIG/default/should-format@3.0.3@@@1/package.json` |
| 304 | rollup | high | `ARCHIVE/CONFIG/default/should-format@3.0.3@@@1/package.json` |
| 225 | libxmljs2 | **critical** | `ARCHIVE/CONFIG/default/xmlbuilder2@3.1.1@@@1/package.json` |
| 224 | libxmljs2 | **critical** | `ARCHIVE/CONFIG/default/xmlbuilder2@3.1.1@@@1/package.json` |
| 182 | esbuild | medium | `ARCHIVE/CONFIG/default/storybook@10.1.2@@@1/package.json` |
| 180 | grunt | high | `ARCHIVE/CONFIG/default/sprintf-js@1.0.3@@@1/package.json` |
| 179 | grunt | medium | `ARCHIVE/CONFIG/default/sprintf-js@1.0.3@@@1/package.json` |
| 178 | grunt | high | `ARCHIVE/CONFIG/default/sprintf-js@1.0.3@@@1/package.json` |
| 21  | chromedriver | high | `ARCHIVE/CONFIG/default/axe-core@4.11.0@@@1/package.json` |
| 19  | chromedriver | medium | `ARCHIVE/CONFIG/default/axe-core@4.11.0@@@1/package.json` |
| 18  | chromedriver | high | `ARCHIVE/CONFIG/default/axe-core@4.10.2@@@1/package.json` |
| 16  | chromedriver | medium | `ARCHIVE/CONFIG/default/axe-core@4.10.2@@@1/package.json` |

## Dismissals — KDesktopVirt (8)

| Alert # | Package | Severity | Manifest |
|---|---|---|---|
| 29 | google.golang.org/protobuf | medium | `kvirtualstage-legacy/kvirtualstage-go/go.mod` |
| 28 | github.com/docker/docker | high | `kvirtualstage-legacy/kvirtualdesktop/go.mod` |
| 27 | github.com/docker/docker | medium | `kvirtualstage-legacy/kvirtualdesktop/go.mod` |
| 26 | github.com/docker/docker | low | `kvirtualstage-legacy/kvirtualdesktop/go.mod` |
| 23 | github.com/docker/docker | **critical** | `kvirtualstage-legacy/kvirtualdesktop/go.mod` |
| 21 | github.com/docker/docker | medium | `kvirtualstage-legacy/kvirtualdesktop/go.mod` |
| 18 | ring | medium | `kvirtualstage-legacy/credential_manager/Cargo.toml` |
| 17 | sqlx | medium | `kvirtualstage-legacy/credential_manager/Cargo.toml` |

## Aggregate impact

- **Total dismissed:** 21 (13 Tracera + 8 KDesktopVirt).
- **Critical alerts closed:** 3 (libxmljs2 ×2, github.com/docker/docker ×1).
- **High alerts closed:** 6 (rollup ×2, grunt ×2, chromedriver ×2, docker ×1 — note: 1 high among KDV docker).
- **Org-wide open Dependabot count:** 119 → 98 (-17.6%).
- **False positives:** 0 — all 21 alerts verified resident in archived/legacy paths confirmed present on `main` via Contents API.

## Follow-up (separate ops)

1. Add `dependabot.yml` `paths-ignore` for `ARCHIVE/CONFIG/**` in Tracera so future advisories on that snapshot don't re-open.
2. Add `dependabot.yml` `paths-ignore` for `kvirtualstage-legacy/**` in KDesktopVirt, or delete the legacy tree once eco-011 rebuild lands.
3. Both ignore directives should be tracked under the same audit reference.

## Re-run / verify

```bash
gh api 'repos/KooshaPari/Tracera/dependabot/alerts?state=open&per_page=100' --jq 'length'
gh api 'repos/KooshaPari/KDesktopVirt/dependabot/alerts?state=open&per_page=100' --jq 'length'
# Expected: Tracera 28→15, KDesktopVirt 24→16
```
