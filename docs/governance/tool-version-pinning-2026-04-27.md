# Tool-Version Pinning Audit — 2026-04-27

API-only audit (read-only) of tool-version pin files across all 71 non-archived, non-fork repos under `KooshaPari/*`. Probed via GitHub Contents API.

## Method

For each repo, probed presence of:

- Pin files: `.nvmrc`, `.node-version`, `.python-version`, `.ruby-version`, `.tool-versions`, `rust-toolchain.toml`, `rust-toolchain`
- Manifest files: `package.json`, `pyproject.toml`, `Cargo.toml`, `Gemfile`, `go.mod`

Cross-referenced manifest presence vs. pin presence. Velocity measured as commits in the trailing 30 days (since 2026-03-27).

## Pin Inventory (org-wide totals across 71 repos)

| Pin file | Count |
|---|---|
| `.nvmrc` | 0 |
| `.node-version` | 0 |
| `.python-version` | 1 |
| `.ruby-version` | 0 |
| `.tool-versions` | 0 |
| `rust-toolchain.toml` | 25 |
| `rust-toolchain` | 0 |

**Headline:** Rust toolchain pinning is healthy (~83% of Rust repos pinned). **Node, Python, and asdf/mise (`.tool-versions`) pinning is effectively absent.**

## Manifest Coverage

| Manifest | Repos |
|---|---|
| `package.json` | 23 |
| `pyproject.toml` | 11 |
| `Cargo.toml` | 30 |
| `go.mod` | 7 |
| `Gemfile` | 0 |

## Gap Analysis

### Node gaps (package.json, no pin) — 23 repos (100% gap)

agent-devops-setups, agileplus-landing, byteport-landing, Dino, heliosApp, heliosCLI, hwledger-landing, phenoDesign, nanovms, PhenoCompose, PhenoHandbook, phenodocs, PhenoLang, phenokits-landing, PhenoMCP, PhenoRuntime, phenotype-auth-ts, phenoShared, projects-landing, PolicyStack, thegent-landing, thegent, Tracera

### Python gaps (pyproject.toml, no pin) — 10 repos (~91% gap)

AuthKit, heliosBench, Httpora, heliosCLI, McpKit, PhenoMCP, PhenoRuntime, PolicyStack, thegent, Tracera

### Rust gaps (Cargo.toml, no pin) — 5 repos (~17% gap)

BytePort, eyetracker, PhenoPlugins, PhenoProc, PhenoKits

### Go gaps (go.mod, no pin) — 7 repos (100% gap)

argis-extensions, BytePort, DevHex, nanovms, PhenoCompose, PhenoMCP, PhenoRuntime

### Ruby gaps — 0 (no Ruby projects)

## Top-10 Highest-Velocity Unpinned Repos (30-day commits)

| Rank | Repo | Commits (30d) | Stack | Missing pin |
|---|---|---|---|---|
| 1 | thegent | 100+ | TS+Python | `.nvmrc`, `.python-version` |
| 2 | PhenoLang | 100+ | TS | `.nvmrc` |
| 3 | heliosApp | 100+ | TS | `.nvmrc` |
| 4 | Tracera | 91 | TS+Python | `.nvmrc`, `.python-version` |
| 5 | heliosCLI | 75 | TS+Python | `.nvmrc`, `.python-version` |
| 6 | BytePort | 51 | Rust+Go | `rust-toolchain.toml`, Go pin |
| 7 | PhenoKits | 46 | Rust | `rust-toolchain.toml` |
| 8 | phenotype-infra | 43 | (mixed) | `.tool-versions` |
| 9 | PhenoProc | 43 | Rust | `rust-toolchain.toml` |
| 10 | AuthKit | 39 | Python | `.python-version` |

(Runner-ups 11–15: PhenoMCP, PhenoHandbook, PhenoRuntime, PhenoPlugins, PolicyStack — all multi-stack and unpinned.)

## Recommendations

### P0 — Add Node pinning org-wide

Zero Node pin files org-wide is a reproducibility risk. Add `.nvmrc` (or unify under `.tool-versions`) to all 23 Node repos. Highest velocity targets first: thegent, PhenoLang, heliosApp, Tracera, heliosCLI.

Suggested baseline: Node 22 LTS (`v22`) unless project-specific.

### P1 — Add Python pinning to all pyproject.toml repos

Only 1 of 11 Python repos pins. Add `.python-version` (pyenv/uv compatible) to the 10 gap repos. Top velocity: thegent, Tracera, heliosCLI, AuthKit.

Suggested baseline: Python 3.13.

### P2 — Add `.tool-versions` (asdf/mise) to multi-stack repos

For repos spanning Node + Python + Rust + Go (thegent, heliosCLI, PhenoMCP, PhenoRuntime, PolicyStack, Tracera, BytePort), prefer a single `.tool-versions` file over per-language pins.

### P3 — Close Rust toolchain gaps

5 Rust repos remain unpinned: BytePort, eyetracker, PhenoPlugins, PhenoProc, PhenoKits. Two are top-10 velocity (PhenoKits, PhenoProc). Use the org-standard `rust-toolchain.toml` already adopted by 25 sibling repos.

### P4 — Close Go toolchain gaps

`go.mod` already declares a Go version, but a `.tool-versions` (or `.go-version`) makes local-dev toolchain match CI explicitly. 7 Go repos: argis-extensions, BytePort, DevHex, nanovms, PhenoCompose, PhenoMCP, PhenoRuntime.

### Suggested execution

Single multi-repo PR sweep: add `.tool-versions` to top-10 highest-velocity unpinned repos first (covers Node + Python + Rust + Go in one file each), then expand to remaining 35 unpinned repos in a follow-up wave.

## Raw data

- `/tmp/pinaudit/repos.tsv` — repo,language,pushed_at,size
- `/tmp/pinaudit/probes.tsv` — repo + 12 binary columns (pin/manifest presence)

## References

- 71 non-archived non-fork repos audited
- Read-only Contents API probes (no writes, no clones)
- Velocity window: trailing 30 days from 2026-04-27
