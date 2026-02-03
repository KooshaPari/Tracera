# Revive vs Other Go Linters – Comparison and Evaluation

Comparison of **Revive** ([mgechev/revive](https://github.com/mgechev/revive)) with the listed tools, plus a short evaluation of each category (General Purpose platforms, Code Formatting, Complexity, Style, Bugs, Unused, Performance, Reports, Misc, Helper Tools).

---

## 1. What Revive Is

| Aspect | Revive |
|--------|--------|
| **Role** | Go style/pattern linter; drop-in replacement for **golint** (which is deprecated/frozen). |
| **Scope** | Style and patterns: naming, exports, comments, complexity, error handling, redundancy, some bug-adjacent rules (e.g. unhandled-error, range-val-in-closure). |
| **Config** | TOML; enable/disable rules, severity, confidence, per-rule args and file excludes. |
| **Speed** | ~2× faster than golint with same rules; up to ~6× faster if type-checking rules are disabled. |
| **Integration** | Standalone CLI; **golangci-lint** (enable `revive` in config); editors (VS Code, GoLand, vim, Neovim); CI/GitHub Actions. |
| **Extensibility** | Custom rules and formatters (library usage); rule-level file excludes. |

**Revive does not:** format code (no gofmt/gofumpt), fix imports (no goimports), run other linters (it’s one linter, not an aggregator), or focus on security (no gosec/gas). It overlaps with **style + some correctness**; for bugs and security you combine it with errcheck, staticcheck, go vet, gosec, etc.

---

## 2. Revive vs Categories (Comparison)

### 2.1 General-Purpose Platforms (CodeClimate, CodeFactor, HoundCI, etc.)

| Tool | Type | Relation to Revive |
|------|------|--------------------|
| **CodeClimate** | SaaS, multi-language | Can run Revive (or golangci-lint with revive) as an “engine”; Revive is a linter they can invoke. |
| **CodeFactor** | SaaS, automated analysis | Same idea: runs analyses on PRs; Go analysis often uses Go linters (e.g. golangci-lint/revive). |
| **HoundCI** | PR comment bot | Runs linters and comments on PRs; can run Revive or golangci-lint. |
| **QuantifiedCode** | Automated review/repair | Alternative platform; not Go-specific; would use Go linters under the hood. |
| **Scrutinizer** | Proprietary quality checker | Integrates with GitHub; can run custom/Go linters. |
| **SideCI** | Automated code review | Same pattern: runs linters and reports. |

**Comparison:** Revive is a **linter**. These are **platforms** that run linters (and tests, coverage, etc.). Revive doesn’t replace them; it’s something you run *inside* them or in CI. Use Revive (or golangci-lint with revive) for Go style/pattern rules; use these platforms for workflow, PR comments, and dashboards.

---

### 2.2 Code Formatting

| Tool | Purpose | vs Revive |
|------|--------|-----------|
| **gofmt** | Canonical formatting | Different job: Revive doesn’t format; use gofmt (or gofumpt) for formatting. |
| **gofumpt** | Stricter gofmt | Same: formatting only; use with Revive (Revive = lint, gofumpt = format). |
| **goimports** | gofmt + import fix | Formatting + imports; no overlap with Revive. |
| **dedupimport** | Fix duplicate imports | Niche; often covered by goimports or golangci-lint. |
| **unindent** | Report unnecessary indent | Style; Revive has style rules but not “unindent”; complementary. |

**Verdict:** No overlap. Use **gofumpt** (or gofmt) + **goimports** for format/imports; use **Revive** for style and pattern rules.

---

### 2.3 Code Complexity

| Tool | Purpose | vs Revive |
|------|--------|-----------|
| **gocyclo** | Cyclomatic complexity | Revive has **cyclomatic** and **cognitive-complexity** rules; overlap. Prefer Revive if using golangci-lint + revive to avoid duplicate reports. |
| **funlen** | Long functions | Revive has **function-length**; overlap. |
| **nakedret** | Naked returns in long functions | Revive has **bare-return**; similar idea. |
| **depth** | Max depth of functions | Revive has **max-control-nesting**; related. |
| **abcgo** | ABC metrics | No direct Revive equivalent; niche. |
| **splint** | Long functions / too many params | Overlaps with Revive’s **argument-limit**, **function-length**. |

**Verdict:** Revive covers the common complexity checks (cyclomatic, cognitive, function-length, argument-limit, bare-return, max-control-nesting). Use Revive for these; add standalone tools only if you need something Revive doesn’t have (e.g. ABC).

---

### 2.4 Style and Patterns

| Tool | Purpose | vs Revive |
|------|--------|-----------|
| **GoLint (golint)** | Style for Go (frozen) | **Revive is the replacement.** Same spirit, more rules, configurable, faster. |
| **gosimple** | Simplify code | Different: gosimple is simplification; Revive is style/naming/structure. Use both (e.g. via golangci-lint). |
| **go-critic** | Many style/bug/performance checks | Overlap in style; go-critic is broader and more opinionated. Use both: Revive for naming/export/context/style, go-critic for its checks. |
| **goconst** | Repeated strings → constants | Revive has **add-constant**; overlap. |
| **predeclared** | Shadowing builtins | Revive has **redefines-builtin-id**; overlap. |
| **misspell** | Spelling | Revive doesn’t do spelling; use misspell (or golangci-lint’s misspell) alongside. |
| **lll** | Line length | Revive has **line-length-limit**; overlap. |
| **whitespace** | Newlines in blocks | Revive has **empty-lines**; overlap. |
| **nofuncflags** | Boolean “flag” params | Revive has **flag-parameter**; overlap. |
| **dogsled** | Too many `_` in assignments | No direct rule; use dogsled (e.g. via golangci-lint). |
| **impi** | Import grouping/order | Revive has **duplicated-imports**, **blank-imports**, **redundant-import-alias**; not full import-order. Use impi if you care about order. |
| **go-printf-func-name** | Printf-like names | Revive doesn’t duplicate this; use if needed. |
| **go-consistent** | Consistency | Revive enforces many style consistencies; overlap in spirit. |
| **go-namecheck** | Naming conventions | Revive **var-naming**, **receiver-naming**, **error-naming**, **time-naming** cover a lot. |
| **go-checkstyle** | Java-checkstyle-like | Revive is more Go-idiomatic; prefer Revive. |
| **go-cleanarch** | Clean Architecture rules | Niche; no Revive equivalent. |
| **go-ruleguard** | Pattern-based rules | Different: custom rules; Revive is built-in rules + optional custom. Can use both. |
| **unconvert** | Unnecessary conversions | Revive doesn’t do this; use unconvert (e.g. via golangci-lint). |
| **usedexports** | Exported that could be unexported | Revive has **exported** (comments/naming); not “could be unexported”. Use usedexports if needed. |

**Verdict:** Revive replaces **golint** and covers a large part of “style and patterns.” Use **Revive** as the main style linter; add **gosimple**, **go-critic**, **misspell**, **unconvert**, **dogsled**, **impi** where they add value (e.g. via golangci-lint).

---

### 2.5 Bugs

| Tool | Purpose | vs Revive |
|------|--------|-----------|
| **errcheck** | Unchecked errors | Revive has **unhandled-error** (configurable); errcheck is more complete. Use **errcheck** (or golangci-lint) for errors; Revive’s rule as extra. |
| **go vet** | Suspicious constructs | No overlap; Revive doesn’t replace go vet. Always use **go vet**. |
| **staticcheck** | “go vet on steroids” | No overlap; use **staticcheck** for bugs/correctness. |
| **bodyclose** | HTTP response body closed | No Revive equivalent; use **bodyclose**. |
| **rowserrcheck** | sql.Rows.Err checked | No Revive equivalent; use **rowserrcheck**. |
| **apicompat** | Breaking API changes | Niche; no Revive equivalent. |
| **badtime** / **durcheck** | time / duration misuse | Revive has **time-naming**, **time-equal**, **time-date**; not full replacement. |
| **enumcase** / **exhaustive** | Switch exhaustiveness | No Revive equivalent; use exhaustive (e.g. via golangci-lint). |
| **gas / gosec** | Security | No overlap; use **gosec** for security. |
| **scopelint** | Loop variable capture | Largely superseded by Go 1.22+; govet/staticcheck cover similar. |
| **safesql** | SQL injection | Niche; gosec also has SQL rules. |

**Verdict:** Revive is **not** a bug/security linter. Use **go vet**, **errcheck**, **staticcheck**, **bodyclose**, **rowserrcheck**, **gosec** (or golangci-lint’s set) for bugs and security; use Revive for style and the few correctness rules it has (e.g. unhandled-error, range-val-in-closure).

---

### 2.6 Unused Code

| Tool | Purpose | vs Revive |
|------|--------|-----------|
| **unused** | Unused consts/vars/funcs/types | Revive has **unused-parameter**, **unused-receiver**; not full “unused” analysis. Use **unused** (e.g. golangci-lint). |
| **ineffassign** | Ineffective assignments | No Revive equivalent; use ineffassign. |
| **unparam** | Unused params | Revive has **unused-parameter**; overlap. Can use one or the other. |
| **deadcode** / **structcheck** / **varcheck** | Unused code | No Revive equivalent; use staticcheck/unused. |

**Verdict:** Revive only touches unused parameters/receivers. Rely on **unused**, **ineffassign**, **unparam** (or golangci-lint) for unused-code.

---

### 2.7 Performance

| Tool | Purpose | vs Revive |
|------|--------|-----------|
| **prealloc** | Slice preallocation | Revive has **inefficient-map-lookup** (map only); no prealloc. Use **prealloc**. |
| **maligned** / **aligncheck** | Struct alignment | No Revive equivalent; use if needed (govet fieldalignment in newer Go). |
| **Copyfighter** | Large struct by value | No Revive equivalent. |
| **rangerdanger** | Range over addressable array | Related to Revive **range-val-address**; not the same. Use both if needed. |

**Verdict:** Revive is not a performance linter. Use **prealloc**, **govet fieldalignment**, and similar for performance.

---

### 2.8 Reports / Misc

| Tool | Purpose | vs Revive |
|------|--------|-----------|
| **flen** | Function length report | Informational; Revive **function-length** enforces limits. |
| **GoReporter** / **golinters** | Quality/HTML reports | Aggregate many tools; can include Revive. |
| **godox** | TODO/FIXME | Revive doesn’t do this; use godox if needed. |
| **go-mnd** | Magic numbers | Revive has **add-constant**; overlap. |
| **megacheck** | staticcheck+gosimple+unused | Superseded by golangci-lint; use golangci-lint + Revive. |
| **tarp** | Functions without tests | No Revive equivalent. |
| **gocheckit** | Deprecated modules | No Revive equivalent. |

**Verdict:** Revive doesn’t replace report/misc tools; use them separately or via golangci-lint.

---

### 2.9 Linter Helper Tools

| Tool | Purpose | vs Revive |
|------|--------|-----------|
| **golangci-lint** | Run many linters (including Revive) | **Use this.** Enable `revive` in golangci-lint; one config, one command. Revive runs as one of the linters. |
| **gometalinter** | Old aggregator | Deprecated; use **golangci-lint**. |
| **reviewdog** | Post linter results to PRs | Runs any linter (Revive, golangci-lint); use for PR comments. |
| **revgrep** | Only recently changed lines | Use with Revive output to focus on new code. |
| **lint** (surullabs) | Run linters in go test | Alternative to CI; can run Revive. |
| **zb** | Cache gometalinter | Legacy; golangci-lint has its own caching. |
| **golintui** | TUI for linters | Optional UX; can run Revive. |

**Verdict:** **golangci-lint** is the main helper: run Revive plus errcheck, staticcheck, go vet, gosec, etc. from one config. Use **reviewdog** if you want PR annotations.

---

## 3. Evaluation Summary by Category

| Category | Use Revive? | Prefer / Combine with |
|----------|-------------|------------------------|
| **General Purpose** | N/A (platforms run Revive) | CodeClimate/CodeFactor/etc. can run golangci-lint with revive. |
| **Code Formatting** | No | **gofumpt** + **goimports**; Revive for lint only. |
| **Code Complexity** | Yes | Revive’s cyclomatic, cognitive-complexity, function-length, argument-limit; drop standalone gocyclo/funlen if using Revive. |
| **Style and Patterns** | Yes (primary) | **Revive** as golint replacement; add **gosimple**, **go-critic**, **misspell**, **unconvert**, **impi** as needed. |
| **Bugs** | Partially (few rules) | **go vet**, **errcheck**, **staticcheck**, **bodyclose**, **rowserrcheck**, **gosec**; Revive for unhandled-error/range gotchas. |
| **Unused Code** | Partially (params/receivers) | **unused**, **ineffassign**, **unparam** (e.g. via golangci-lint). |
| **Performance** | No | **prealloc**, govet **fieldalignment**, etc. |
| **Reports / Misc** | No | flen, godox, go-mnd, etc. as needed. |
| **Helper Tools** | Yes (as a plugin) | **golangci-lint** (enable revive); **reviewdog** for PRs. |

---

## 4. Practical Recommendation

- **Formatting:** **gofumpt** (and optionally goimports); not Revive.
- **Linting:** **golangci-lint** with:
  - **revive** enabled (main style/pattern linter, golint replacement).
  - Defaults: **errcheck**, **govet**, **staticcheck**, **unused**, **ineffassign**.
  - Add as needed: **gosec**, **bodyclose**, **rowserrcheck**, **go-critic**, **misspell**, **exhaustive**, **prealloc**, etc.
- **Revive config:** Use a TOML (or golangci-lint’s `linters.settings.revive`) with a strict-but-manageable set (e.g. recommended rules from Revive’s README), and tune complexity/line-length as needed.
- **CI:** Run golangci-lint (with revive) in one job; optionally use reviewdog to comment on PRs.
- **Platforms:** CodeClimate, CodeFactor, HoundCI, etc. are where you run this stack (or their built-in Go support); Revive is one of the linters in that stack.

Revive is the right choice for **style and patterns** in Go; combine it with **gofumpt**, **golangci-lint**, and the bug/security/unused/performance linters above for a complete setup.
