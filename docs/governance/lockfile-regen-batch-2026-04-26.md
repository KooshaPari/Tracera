# Lockfile Regen Batch — 2026-04-26

**Purpose:** Single-agent worktree-capable batch script for regenerating lockfiles to close Dependabot alert clusters surfaced in this loop.

**Constraint:** Read-only planning artifact. Execution requires a separate worktree pass with disk + FD pre-flight (df -h ≥30Gi, ulimit -n ≥4096).

**Total alerts addressable by lockfile regen:** 205
**Repos in scope:** 8

---

## Impact Ranking (highest first)

| Rank | Repo | Alerts | Type | Direct-dep bump? |
|------|------|--------|------|------------------|
| 1 | thegent | 60 | mixed (pnpm/uv/go/npm) | No — pure regen |
| 2 | heliosCLI | 52 | mixed (uv/pnpm/cargo) | Mostly regen; handlebars may need parent bump |
| 3 | PhenoLang | 30 | mixed (cargo/npm/uv) | No — pure regen |
| 4 | pheno | 24 | mixed (cargo/npm/uv) | vitepress transitive — pure regen |
| 5 | BytePort | 16 | mixed (cargo/npm/yarn) | No — pure regen |
| 6 | Tracera | 15 | mixed (uv/go) | **YES** — testcontainers-go parent bump for docker indirect |
| 7 | hwLedger | 7 | mixed (cargo/uv) | No — pure regen |
| 8 | cliproxyapi-plusplus | 1 | go | No — pure regen (pgx/v5 5.9.1→5.9.2) |

---

## Top-3 Highest-Impact Targets

1. **thegent (60 alerts)** — pnpm-lock.yaml=31, uv.lock=14, go.mod=9, byteport-docs npm=3, byteport-web npm=3. Pure regen across 5 lockfiles.
2. **heliosCLI (52 alerts)** — uv.lock + pnpm-lock.yaml + codex-rs/Cargo.lock + Cargo.lock. 1 CRIT (handlebars) + 15 HIGH. Handlebars may require parent crate bump if pinned transitively.
3. **PhenoLang (30 alerts)** — Cargo.lock (rand/openssl), docs/package-lock.json, python/uv.lock, agileplus-mcp/uv.lock. Pure regen.

Top-3 alone closes **142 / 205 alerts (~69%)**.

---

## Per-Repo Regen Commands

### 1. thegent (60)
```bash
# Root pnpm
pnpm install --lockfile-only
# Root uv
uv lock --upgrade
# Root go
go mod tidy
# byteport-docs
( cd byteport-docs && npm install --package-lock-only )
# byteport-web
( cd byteport-web && npm install --package-lock-only )
```

### 2. heliosCLI (52)
```bash
uv lock --upgrade
pnpm install --lockfile-only
cargo update
( cd codex-rs && cargo update )
# If handlebars CRIT remains, bump parent: cargo update -p handlebars --precise <safe-ver>
```

### 3. PhenoLang (30)
```bash
cargo update -p rand -p openssl
( cd docs && npm install --package-lock-only )
( cd python && uv lock --upgrade-package <pkgs> )
( cd agileplus-mcp && uv lock --upgrade )
```

### 4. pheno (24)
```bash
cargo update -p openssl
# vitepress transitive npm
( cd <docs-dir> && npm install --package-lock-only )
uv lock --upgrade
```

### 5. BytePort (16)
```bash
cargo update
( cd frontend/web/src-tauri && cargo update )
( cd frontend/web && npm install --package-lock-only )
( cd frontend/web && yarn install --mode update-lockfile )
( cd .github/frontend && npm install --package-lock-only )
```

### 6. Tracera (15) — **PARENT BUMP REQUIRED**
```bash
uv lock --upgrade
# Direct-dep bump for docker indirect via testcontainers-go:
( cd backend && go get github.com/testcontainers/testcontainers-go@latest && go mod tidy )
( cd tests && go get github.com/testcontainers/testcontainers-go@latest && go mod tidy )
( cd tests/benchmarks && go get github.com/testcontainers/testcontainers-go@latest && go mod tidy )
```

### 7. hwLedger (7)
```bash
cargo update
( cd apps/streamlit && uv lock --upgrade )
```

### 8. cliproxyapi-plusplus (1)
```bash
go get github.com/jackc/pgx/v5@v5.9.2 && go mod tidy
```

---

## Execution Pre-flight Checklist

- [ ] `df -h` shows ≥30 GiB free on volume
- [ ] `ulimit -n` ≥ 4096 (FD floor; cap concurrent cargo at 2)
- [ ] Per repo: spawn worktree under `repos/<repo>-wtrees/lockfile-regen-2026-04-26/`
- [ ] One commit per repo, MODE 1 provenance
- [ ] After regen: `cargo build` / `pnpm install` / `go build ./...` smoke test
- [ ] Open PR per repo; do NOT batch-merge without local quality run

## Estimated Closure

**~205 alerts closable on a single worktree run** assuming clean regen. Tracera parent-bump (15 alerts) is the only non-trivial item; remainder are pure lockfile regen.
