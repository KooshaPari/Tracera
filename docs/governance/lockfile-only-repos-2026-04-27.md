# Lockfile-Only Dependabot Blockers — API Inventory 2026-04-27

**Method:** API-only. `gh api users/KooshaPari/repos --paginate` (82 active) → per-repo `dependabot/alerts?state=open` → classify manifest_paths against lockfile regex (`Cargo.lock|package-lock.json|pnpm-lock.yaml|yarn.lock|go.sum|uv.lock|bun.lock|Pipfile.lock|composer.lock|Gemfile.lock|poetry.lock`). A repo is **lockfile-only-blocked** iff *every* alert manifest_path is a lockfile.

## Lockfile-Only Blocked (14 repos, 191 alerts addressable via lockfile-regen alone)

| Rank | Repo | Open Alerts | Lockfile Manifests |
|------|------|-------------|-------------------|
| 1 | heliosCLI | 51 | codex-rs/Cargo.lock, pnpm-lock.yaml, uv.lock |
| 2 | PhenoLang | 36 | Cargo.lock, agileplus-mcp/uv.lock, docs/package-lock.json, python/uv.lock |
| 3 | PhenoProject | 31 | rust/Planify/pnpm-lock.yaml |
| 4 | agentapi-plusplus | 21 | 4× package-lock.json/pnpm-lock.yaml |
| 5 | BytePort | 16 | Cargo.lock (×2), package-lock.json (×2), yarn.lock |
| 6 | AgilePlus | 8 | Cargo.lock, uv.lock (×2), docs/package-lock.json |
| 7 | hwLedger | 7 | Cargo.lock, apps/streamlit/uv.lock |
| 8 | PhenoRuntime | 6 | Cargo.lock |
| 9 | Dino | 5 | package-lock.json (×2) |
| 10 | phenotype-auth-ts | 3 | package-lock.json |
| 11 | PolicyStack | 2 | package-lock.json |
| 12 | phenoDesign | 2 | package-lock.json |
| 13 | helios-cli | 2 | codex-rs/Cargo.lock |
| 14 | PhenoObservability | 1 | Cargo.lock |

**Total addressable via single worktree lockfile-regen wave: 191 alerts across 14 repos.**

## Mixed (NOT lockfile-only — require manifest bumps)

thegent (60), HexaKit (48), pheno (29), Tracera (15), phenotype-ops-mcp (3), HeliosLab (3), DevHex (3), PlatformKit (2), cliproxyapi-plusplus (1), argis-extensions (1). Total: **165 alerts** requiring `Cargo.toml`/`go.mod`/`package.json` edits.

## Wave Plan Implication

- **Wave 1 (lockfile-regen, mechanical):** 14 repos / 191 alerts. Single sweep: `cargo update`, `pnpm up --latest`, `uv lock --upgrade`, `npm i`. Top-3 (heliosCLI + PhenoLang + PhenoProject) = 118 alerts (62%).
- **Wave 2 (manifest-bump, per-repo):** 10 repos / 165 alerts. Requires version pinning review.
