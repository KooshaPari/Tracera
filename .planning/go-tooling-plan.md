# Go project tooling overhaul – plan

**Status:** planning  
**Scope:** backend (Go); formatting, linting, optional security/maintainability linters.  
**Depends on:** backend directory and `go.mod` present (referenced by Makefile/CI).

---

## 1. Current state

| Area | Current | Location |
|------|--------|----------|
| Format | `gofmt -s` (simplify) | Makefile: `format`, `go-format`, `lint-go` |
| Lint | `go vet ./...` + `gofmt -s -l` | Makefile: `lint-go` |
| CI | `golangci/golangci-lint-action@v6`, `version: latest`, `args: --timeout=5m` | `.github/workflows/ci.yml` |
| Install | air, staticcheck, govulncheck, protoc-gen-go, protoc-gen-go-grpc | Makefile: `install-tools` |
| Config | No `.golangci*`; no gofumpt | — |

So: CI already runs golangci-lint with defaults; local Makefile uses only `go vet` and `gofmt`. No shared strict config, no gofumpt.

---

## 2. Research summary

**Sources:** [awesome-go-linters](https://github.com/golangci/awesome-go-linters), [golangci-lint linters](https://golangci-lint.run/usage/linters/).

- **Formatting**
  - **gofumpt** – Stricter than gofmt, backward compatible; de facto standard for “strict format”.
  - **goimports** – gofmt + fix imports; often used with gofumpt (e.g. `gofumpt -w` then imports).
- **Linting**
  - **golangci-lint** – Single entry point; runs many linters (errcheck, govet, staticcheck, unused on by default; revive, gocritic, gosec, bodyclose, etc. optional).
  - **revive** – Style/pattern replacement for golint; configurable, many rules.
  - **staticcheck** – Already installed; also run via golangci-lint.
  - **gocritic** – Extra style/bugs/performance checks.
  - **gosec** – Security-focused.
- **Helper**
  - One config (`.golangci.yml` or `.golangci.yaml`) in `backend/` keeps CI and local in sync and allows strict presets.

---

## 3. Recommended stack

| Tool | Role | Where |
|------|------|--------|
| **gofumpt** | Stricter formatting (replace `gofmt -s` for format + lint check) | Makefile, CI optional |
| **golangci-lint** | Single lint runner with shared config | `backend/.golangci.yml` |
| **govulncheck** | Vulnerability check | Keep as-is (Makefile / security-scan) |
| **staticcheck** | Keep for direct use if desired; also via golangci-lint | Optional in install-tools |

No separate revive binary: use golangci-lint’s `revive` linter and configure it in `.golangci.yml` if you want revive-style rules.

---

## 4. Phased WBS (DAG)

| Phase | Task ID | Description | Depends on |
|-------|---------|-------------|------------|
| 1 | T1 | Add `backend/.golangci.yml` with strict-but-reasonable linters and timeouts | — |
| 1 | T2 | Add gofumpt to `install-tools`; use gofumpt in `format` / `go-format` and `lint-go` (replace gofmt for backend) | — |
| 2 | T3 | Add golangci-lint to `install-tools` and `lint-go` target (run from backend) | T1 |
| 2 | T4 | CI: ensure job uses same config (working-directory: backend; config is auto-discovered) | T1 |
| 3 | T5 | Optional: tighten linter set (e.g. enable revive, gocritic, gosec, bodyclose) and fix existing issues | T3 |
| 3 | T6 | Docs: update README/checklists to mention gofumpt + golangci-lint | T4 |

**Dependencies:** T3, T4 depend on T1. T5 depends on T3. T6 depends on T4. T2 is independent.

---

## 5. Task details

### T1 – `backend/.golangci.yml`

- **run:** timeout ~5m, path `./...`, exclude generated/vendor as needed.
- **linters:** start from golangci-lint “default” (errcheck, govet, ineffassign, staticcheck, unused); optionally enable:
  - **revive** (style, drop-in for golint).
  - **gocritic** (optional; can enable a subset of checks).
  - **gosec** (security; optional or exclude noisy rules).
  - **bodyclose**, **rowserrcheck** (HTTP/DB correctness).
- **linters-settings:** e.g. revive severity, gocyclo/gocognit limits; errcheck exclusions if required.
- **issues:** exclude some generated dirs if present (e.g. `.*\\.pb\\.go`, `/vendor/`).

### T2 – Gofumpt in Makefile

- **install-tools:** `go install mvdan.cc/gofumpt@latest`.
- **format / go-format:** in backend, run `gofumpt -w .` instead of `gofmt -s -w .`.
- **lint-go:** run `gofumpt -l .` (list unformatted files) and fail if any; keep `go vet ./...`; add `golangci-lint run` after T3.

### T3 – golangci-lint in Makefile

- **install-tools:** `go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest` (or fixed v1.xx).
- **lint-go:** `cd backend && golangci-lint run` (uses `backend/.golangci.yml`).

### T4 – CI

- Keep `golangci/golangci-lint-action@v6`, `working-directory: backend`, `args: --timeout=5m`.
- No code change if config path is `backend/.golangci.yml`; action discovers it. Optionally pin `version: v1.xx.x` for reproducibility.

### T5 – Optional strictness

- Enable more linters in `backend/.golangci.yml` (revive, gocritic, gosec, bodyclose, etc.).
- Run `golangci-lint run ./...` and fix or exclude rules until baseline is clean.

### T6 – Docs

- README / FIRST_RUN_CHECKLIST: “Go: gofumpt + golangci-lint”; “install-tools” list; how to run `make lint-go` / `make go-format`.

---

## 6. Example `.golangci.yml` sketch (backend)

```yaml
run:
  timeout: 5m
  modules-download-mode: readonly

linters:
  enable:
    - errcheck
    - govet
    - ineffassign
    - staticcheck
    - unused
    - bodyclose
    - revive
    # optional: gocritic, gosec, rowerrcheck
  disable:
    - exhaustivestruct  # often noisy

linters-settings:
  revive:
    severity: warning
  gocyclo:
    min-complexity: 15
  gocognit:
    min-complexity: 20

issues:
  exclude-rules:
    - path: _test\.go
      linters: [gocognit, gocyclo, funlen]
    - path: \.pb\.go$
      linters: [all]
```

(Exact linter list and excludes to be tuned when backend exists.)

---

## 7. Out of scope (for this plan)

- Pre-commit hook config (reference only: “run gofumpt + golangci-lint”).
- Buf/grpc codegen (already in Makefile).
- Go version / module path (assumed set in backend).

---

## 8. Execution notes (agent-led)

- **Effort:** T1+T2 ~1 config + 1 Makefile edit; T3+T4 ~2 edits; T5 variable; T6 ~1 doc pass.
- **Order:** Implement T1 → T2 in parallel with T1 if desired; then T3 → T4; then T5 (optional), then T6.
- **Validation:** After T2: `make go-format` and `make lint-go` (with gofumpt only) succeed. After T3/T4: `make lint-go` runs golangci-lint; CI job runs same config.
