# Dependabot Enable Batch — 2026-04-26

**Scope:** 5 non-archived repos flagged by alerts-disabled audit.
**Method:** GitHub REST API (`gh api`). No clones.

## Pre-flight

All 5 verified `archived=false`. All 5 are forks (parents listed); no fork was
skipped because each can hold its own alert state independent of upstream.
Upstream `has_vulnerability_alerts` is not externally observable without admin
scope on the parent — assumption: upstreams (openai/codex, nanovms/ops-mcp,
isaacphi/mcp-language-server, blackboardsh/colab, jundot/omlx) are presumed to
maintain their own posture; enabling on the fork is non-destructive.

| Repo | Parent | Archived | Fork |
|---|---|---|---|
| KooshaPari/HeliosLab | blackboardsh/colab | false | true |
| KooshaPari/helios-cli | openai/codex | false | true |
| KooshaPari/phenotype-ops-mcp | nanovms/ops-mcp | false | true |
| KooshaPari/MCPForge | isaacphi/mcp-language-server | false | true |
| KooshaPari/phenotype-omlx | jundot/omlx | false | true |

## Enable Results

All `PUT` calls returned `HTTP 204 No Content` (success).

| Repo | vulnerability-alerts | automated-security-fixes | verify GET |
|---|---|---|---|
| HeliosLab | 204 | 204 | 204 |
| helios-cli | 204 | 204 | 204 |
| phenotype-ops-mcp | 204 | 204 | 204 |
| MCPForge | 204 | 204 | 204 |
| phenotype-omlx | 204 | 204 | 204 |

## Newly-Surfaced Alerts (post-enable, ~60s wait)

| Repo | Critical | High | Medium | Low | Total open |
|---|---|---|---|---|---|
| HeliosLab | 0 | 0 | 0 | 0 | 0 |
| helios-cli | 0 | 0 | 0 | 0 | 0 |
| phenotype-ops-mcp | 0 | 0 | 0 | 0 | 0 |
| MCPForge | 0 | 0 | 0 | 0 | 0 |
| phenotype-omlx | 0 | 0 | 0 | 0 | 0 |

No open Dependabot alerts surfaced within the initial scan window. Dependabot
may continue to surface alerts asynchronously as it completes manifest
ingestion; re-poll in 24h via:

```bash
for r in HeliosLab helios-cli phenotype-ops-mcp MCPForge phenotype-omlx; do
  gh api "repos/KooshaPari/$r/dependabot/alerts" \
    -q '.[] | select(.state=="open") | .security_vulnerability.severity' \
    | sort | uniq -c
done
```

## Commands Used

```bash
gh api -X PUT repos/KooshaPari/<r>/vulnerability-alerts        # enable alerts
gh api -X PUT repos/KooshaPari/<r>/automated-security-fixes    # enable PRs
gh api    repos/KooshaPari/<r>/vulnerability-alerts -i         # verify (204)
gh api    repos/KooshaPari/<r>/dependabot/alerts               # enumerate
```
