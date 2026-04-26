# CodeQL Org-Wide Open Alert Inventory — 2026-04-26

**Method:** API-only (`gh api repos/<r>/code-scanning/alerts?state=open --paginate`). No clones. Archived repos pre-filtered via `gh api repos/<r> --jq .archived`. Inventory only — no triage.

## Coverage Summary

| Metric | Count |
|---|---|
| Non-archived KooshaPari repos probed | 82 |
| CodeQL-active (200 + ≥1 open alert) | 68 |
| CodeQL-active with zero open alerts | 0 |
| `no analysis found` (CodeQL not enabled / no successful analysis) | 14 |
| 403 (billing-blocked) | 0 |
| Total open alerts (all severities) | 3,223 |

## Severity Distribution (all open alerts)

| `security_severity_level` | Count |
|---|---|
| critical | 56 |
| high | 1,006 |
| medium | 1,797 |
| low | 142 |
| none (rule has no security_severity) | 222 |

## Top 10 Repos by `critical + high`

| Rank | Repo | crit+high | critical | high |
|---:|---|---:|---:|---:|
| 1 | thegent | 288 | 13 | 275 |
| 2 | Tracera | 104 | 0 | 104 |
| 3 | cliproxyapi-plusplus | 64 | 4 | 60 |
| 4 | agentapi-plusplus | 36 | 2 | 34 |
| 5 | Dino | 31 | 0 | 31 |
| 6 | AuthKit | 26 | 26 | 0 |
| 7 | Tokn | 26 | 0 | 26 |
| 8 | FocalPoint | 22 | 0 | 22 |
| 9 | PolicyStack | 21 | 0 | 21 |
| 10 | heliosApp | 20 | 1 | 19 |

**Notable critical-only ranking (top 5):** AuthKit (26), thegent (13), AgilePlus (5), cliproxyapi-plusplus (4), agentapi-plusplus (2).

## CodeQL Coverage Gaps (`no analysis found`)

These 14 active repos have no CodeQL analyses and were excluded from alert counts. Most are landing pages or small docs/test repos:

`Agentora`, `agileplus-landing`, `AgentMCP`, `byteport-landing`, `Conft`, `eyetracker`, `helios-cli`, `hwledger-landing`, `ObservabilityKit`, `phenokits-landing`, `projects-landing`, `portage`, `TestingKit`, `thegent-landing`.

## Blockers

- None observed in this run. All non-archived repos returned 200 or `404 / no analysis found`. No 403 (billing) responses on `/code-scanning/alerts` endpoints during the audit window.
- Note: 8 repos hit the 100/page CodeQL API cap and required `--paginate` re-fetch (handled in this run): `thegent` (383), `cliproxyapi-plusplus` (415), `Tracera` (138), `agentapi-plusplus` (127), `Dino` (123), `Planify` (117), `PolicyStack` (107), `Tokn` (107).

## Raw Data

- Per-repo status: `/tmp/codeql_status.tsv`
- Per-alert rows (repo, sev, severity, rule, path): `/tmp/codeql_alerts_final.tsv` (3,223 rows)
