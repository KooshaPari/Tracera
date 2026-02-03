# Oxc Quick Reference

Short reference for [Oxc](https://oxc.rs/) (JavaScript Oxidation Compiler) usage in this project: **parser**, **resolver**, and **oxlint** (linter). Official docs: <https://oxc.rs/docs/guide/usage/>.

## Setup (this project)

| Component   | Status | Notes |
|------------|--------|--------|
| **Parser** | ✅ Via oxlint | No separate install; oxlint uses OXC parser internally. |
| **Resolver** | ✅ Via oxlint | No separate install; oxlint uses OXC resolver for multi-file/import rules. |
| **Linter** | ✅ Configured | `frontend/.oxlintrc.json`, `frontend/apps/web/.oxlintrc.json`. |
| **Type-aware** | ✅ Configured | `oxlint-tsgolint` in frontend devDependencies. |

**Commands (from `frontend/`):**

- **Lint**: `bun run lint` → `oxlint .`
- **Format**: `bun run format` → `oxfmt .`
- **Typecheck**: `bun run typecheck` → `oxlint --type-check --type-aware .`

Optional standalone parser/resolver only if you need them for custom tooling (e.g. AST transforms or custom resolution scripts); see [Parser](#parser) and [Resolver](#resolver) install options below.

### Implementation checklist

Use [docs/checklists/OXC_IMPLEMENTATION_CHECKLIST.md](../checklists/OXC_IMPLEMENTATION_CHECKLIST.md) to verify and maintain the full setup. Quick verification from repo root:

| Step | Command |
|------|--------|
| Lint (no type-aware) | `make lint-frontend` or `cd frontend && bun run lint` |
| Typecheck (type-aware + TS errors) | `make quality-fe-type` or `cd frontend && bun run typecheck` |
| Type-aware only (no TS errors) | `cd frontend && bun run typecheck:type-aware-only` |
| Format check | `cd frontend && bun run format:check` |
| Full frontend quality | `make quality-frontend` or `cd frontend && bun run quality` |
| Report unused disable comments | `cd frontend && bun run lint:report-unused-disable` or `bun run typecheck:report-unused-disable` |

---

## Parser

**Docs:** <https://oxc.rs/docs/guide/usage/parser.html>

**Review (from official docs):**

- **Status:** Production ready.
- **Features:** Parses `.js(x)` and `.ts(x)`; ~3× faster than swc in benchmarks; passes Test262 and 99% of Babel/TypeScript parser tests; returns ESM information directly (no separate es-module-lexer).
- **Used by:** oxlint (built-in). No separate parser setup needed for linting in this repo.

**Installation (only if using standalone):**

| Environment | Package / crate |
|-------------|------------------|
| Node.js     | [oxc-parser](https://www.npmjs.com/package/oxc-parser) |
| Rust        | [oxc](https://docs.rs/oxc) or [oxc_parser](https://docs.rs/oxc_parser) |

Example (Node): `import { parseSync } from 'oxc-parser'; const { program } = parseSync('file.js', source);`

---

## Resolver

**Docs:** <https://oxc.rs/docs/guide/usage/resolver.html>

**Review (from official docs):**

- **Purpose:** Node.js CJS and ESM path resolution.
- **Features:** Aligned with [webpack/enhanced-resolve](https://github.com/webpack/enhanced-resolve); ~28× faster in benchmarks; see [oxc-resolver README](https://github.com/oxc-project/oxc-resolver).
- **Used by:** oxlint for multi-file and import analysis (e.g. `import/no-cycle`). No separate resolver setup needed for linting in this repo.

**Installation (only if using standalone):**

| Environment | Package / crate |
|-------------|------------------|
| Node.js     | [oxc-resolver](https://www.npmjs.com/package/oxc-resolver) |
| Rust        | [oxc_resolver](https://docs.rs/oxc_resolver) |

---

## Linter (oxlint)

- **Docs**: <https://oxc.rs/docs/guide/usage/linter.html>
- **Config**: `.oxlintrc.json` (recommended). Enable plugins and rules there.
- **Plugins** (built-in): <https://oxc.rs/docs/guide/usage/linter/plugins.html>
  - Default: `eslint`, `typescript`, `unicorn`, `oxc`.
  - Optional: `react`, `react-perf`, `import`, `jsx-a11y`, `jest`, `vitest`, etc.
  - Enable in config: `"plugins": ["import", "react"]` (this **replaces** the default set; list all plugins you want).
- **CLI**: `oxlint [paths]`, `oxlint --fix`, `oxlint --type-check --type-aware` (with `oxlint-tsgolint` installed).

## Multi-file analysis

**Docs:** <https://oxc.rs/docs/guide/usage/linter/multi-file-analysis.html>

Multi-file analysis lets rules use **project-wide information** (e.g. module dependency graph) instead of analyzing each file alone.

### Performance and architecture

- **ESLint:** Rules are per-file; no built-in project graph. Plugins like `eslint-plugin-import` rebuild resolution and the module graph outside ESLint, so `import/no-cycle` can take tens of seconds or over a minute on large repos.
- **Oxlint:** Multi-file analysis is in the core: lint and module graph are built in parallel, parsing and resolution are shared across rules; comparable `import/no-cycle` runs in a few seconds.

### Enable

1. Enable the **import** plugin.
2. Configure at least one `import/*` rule (e.g. `import/no-cycle`).

Example `.oxlintrc.json`:

```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["import"],
  "rules": {
    "import/no-cycle": ["error", { "maxDepth": 3 }]
  }
}
```

### Detect cycles: `import/no-cycle`

Rule: [import/no-cycle](https://oxc.rs/docs/guide/usage/linter/rules/import/no-cycle). Import cycles:

- Obscure dependency direction
- Make refactors harder
- Can cause imported values to be `undefined` due to evaluation order

### TypeScript path aliases

When running `import/*` rules, Oxlint **automatically discovers** `tsconfig.json` and resolves TypeScript path aliases (e.g. `compilerOptions.paths`). No extra setup.

---

## Type-aware linting

**Docs:** <https://oxc.rs/docs/guide/usage/linter/type-aware.html>

Type-aware linting enables rules that use **TypeScript’s type system** (e.g. unhandled promises, unsafe assignments). In Oxlint it’s provided by [tsgolint](https://github.com/oxc-project/tsgolint) and wired into the CLI and config.

**Status:** **Alpha.** Rule coverage, performance, and compatibility are still improving.

### Overview

- **Oxlint (Rust):** File traversal, ignore logic, config, non–type-aware rules, reporting.
- **tsgolint (Go):** Builds TypeScript programs via [typescript-go](https://github.com/microsoft/typescript-go), runs type-aware rules, returns diagnostics to Oxlint.

### Installation

```bash
bun add -D oxlint-tsgolint@latest
```

(Already in this repo’s frontend.)

### Running

- **Lint only:** `oxlint --type-aware` — runs standard rules plus type-aware rules in the `typescript/*` namespace. Opt-in; does not run without the flag.
- **Lint + type errors:** `oxlint --type-aware --type-check` — reports TypeScript errors too; can replace `tsc --noEmit` in CI.
- **Editors:** In LSP/VS Code integrations, set `typeAware: true` (see [Editors](https://oxc.rs/docs/guide/usage/linter/editors)).

### Monorepos and build outputs

Type-aware linting needs **resolved types**. In monorepos:

- Build dependent packages so `.d.ts` files exist.
- Install dependencies before running, e.g. `pnpm install && pnpm -r build && oxlint --type-aware`.

### Configuring type-aware rules

Same `.oxlintrc.json`; rules under `typescript/*`:

```json
{
  "plugins": ["typescript"],
  "rules": {
    "typescript/no-floating-promises": ["error", { "ignoreVoid": true }],
    "typescript/no-unsafe-assignment": "warn"
  }
}
```

Options match the `typescript-eslint` equivalents.

### Disable comments

- Inline: `// oxlint-disable-next-line typescript/no-floating-promises`
- Report unused disables: `oxlint --type-aware --report-unused-disable-directives`

### TypeScript compatibility

- Powered by **typescript-go**; **TypeScript 7.0+** required.
- Some legacy tsconfig options are not supported (e.g. `baseUrl`).
- Deprecated/removed options must be migrated; invalid options are reported when `--type-check` is enabled.
- See [TypeScript migration guide](https://github.com/microsoft/TypeScript/issues/62508#issuecomment-3348649259) and [ts5to6](https://github.com/andrewbranch/ts5to6).

### Stability notes (alpha)

- Rule coverage is incomplete.
- Very large codebases may see high memory use.
- Performance is still improving.

### Next steps (from docs)

- [Implemented rules](https://github.com/oxc-project/tsgolint/tree/main?tab=readme-ov-file#implemented-rules)
- Report issues: [tsgolint](https://github.com/oxc-project/tsgolint)

### Where tsgo.log shows you hang

If you run `OXC_LOG=debug bunx oxlint --type-aware` from the **repo root** and capture to `tsgo.log`:

- **File assignment** (~9s in a typical run): `Starting to assign files to programs. Total files: 1263` → files get assigned to 9 programs.
- **Program 1** (`frontend/apps/web/tsconfig.json`): Logs `Program created with 2716 source files`, then many per-file lines. That program is large but completes.
- **Program 2** (`frontend/tsconfig.json`): Log shows only `[2/9] Running linter on program: .../frontend/tsconfig.json` and then **no** `Program created with N source files` and **no** per-file lines. The process appears to **hang** during **program creation** for the root frontend tsconfig (resolving project references and building the TypeScript program).

So the hang is **at program 2/9**: tsgolint is stuck creating the program for `frontend/tsconfig.json`, which has `references` to five packages (`packages/types`, `state`, `ui`, `api-client`, `config`). That can mean very slow or stuck resolution/composite build, or a tsgolint bug with that layout.

**Quick mitigations:**

1. **Run type-aware only under `frontend`** so the root walk doesn’t pick up the whole repo: `cd frontend && OXC_LOG=debug bunx oxlint --type-aware .` (you may still see program 2; see below).
2. **Narrow scope** so the root `frontend/tsconfig.json` isn’t used for type-aware: run `oxlint --type-aware ./apps/web` (or other subpaths) from `frontend/`, or adjust which tsconfigs are discovered.
3. **Build packages first**: from `frontend/`, run `bun run build` (or build the referenced packages) so `.d.ts` exist; then retry type-aware.
4. If it still hangs at program 2, **report to [tsgolint issues](https://github.com/oxc-project/tsgolint/issues)** with: log snippet showing `[2/9]` and nothing after, `frontend/tsconfig.json` (with references), and that the hang is during program creation.

### Type-aware: performance and troubleshooting (deep)

Type-aware linting is **alpha**. Very large codebases can hit **slow runs** or **high memory usage** (OOM). Use the steps below to diagnose and fix.

#### 1. Keep tools updated

- Update both: `oxlint` and `oxlint-tsgolint` (e.g. `bun add -d oxlint@latest oxlint-tsgolint@latest`).
- Performance and memory improvements are ongoing; newer versions often help.

#### 2. Enable debug logging

```bash
OXC_LOG=debug oxlint --type-aware .
```

**What to look for:**

- **File assignment** (`Starting to assign files...` → `Done assigning files...`): Maps source files to tsconfig projects. Should be fast (e.g. &lt; 1s). If slow, report to [tsgolint issues](https://github.com/oxc-project/tsgolint/issues).
- **Program linting** (`[N/M] Running linter on program: .../tsconfig.json`): Each TypeScript project is linted separately. One program taking much longer than others → expensive type resolution or an oversized project.
- **Program size**: `Program created with 26140 source files` → far too many files in one program. Usually caused by tsconfig `include`/`exclude`.
- **Per-file gaps**: Each logged file path is when that file is linted. Large time gaps between files → expensive type resolution for specific files.

#### 3. Fix tsconfig so programs stay small

**Root cause of many perf issues:** a single tsconfig pulling in thousands of files (e.g. build output, tests, or the whole repo).

**Bad (pulls in everything):**

```json
{
  "include": ["**/*"]
}
```

**Good (source only, explicit exclude):**

```json
{
  "include": ["src/**/*", "apps/**/*", "packages/**/*"],
  "exclude": ["node_modules", "dist", "build", "coverage", ".turbo", "**/*.test.ts", "**/*.spec.ts"]
}
```

**Monorepos:** Prefer a root tsconfig that does **not** include source directly; use references only:

```json
{
  "files": [],
  "references": [{ "path": "./packages/a" }, { "path": "./apps/web" }]
}
```

Then each `packages/*` and `apps/*` has its own tsconfig with scoped `include`/`exclude`. That way type-aware linting runs one program per package/app instead of one giant program.

**Check:** After changing tsconfig, run again with `OXC_LOG=debug` and look for “Program created with N source files”. N should be in the hundreds, not tens of thousands.

#### 4. Monorepos: build before type-aware

- Type-aware linting needs resolved types; workspace packages need built `.d.ts`.
- Install and build before linting, e.g. `bun install && bun run build` (or `turbo build`), then `oxlint --type-aware .`.
- If you don’t build, resolution can be slow or fail and look like “perf” issues.

#### 5. TypeScript 7 and tsconfig compatibility

- Type-aware linting uses **typescript-go** (TypeScript 7). Requires TypeScript 7+.
- Legacy options (e.g. `baseUrl`) are not supported and can cause errors or odd behavior.
- Invalid or deprecated tsconfig options are reported when using `--type-check`. Fix those first; see [TypeScript migration guide](https://github.com/microsoft/TypeScript/issues/62508#issuecomment-3348649259) and [ts5to6](https://github.com/andrewbranch/ts5to6) for tsconfig upgrades.

#### 6. Reduce scope temporarily

- Run type-aware only on a subset to confirm it’s a scale issue: `oxlint --type-aware ./apps/web ./packages/ui`.
- If that’s fast, the problem is likely one of: a single huge program (tsconfig), too many programs, or memory. Narrow by adjusting tsconfig and re-running with debug.

#### 7. Report issues

- **OOM or severe slowness:** [tsgolint issues](https://github.com/oxc-project/tsgolint/issues). Include: repo size (file count), tsconfig layout (references, include/exclude), and if possible `OXC_LOG=debug` output.
- **Oxlint CLI / config:** [oxc issues](https://github.com/oxc-project/oxc/issues).

#### 8. Optional: disable type-aware in CI until fixed

- If type-aware is blocking CI, you can run only non–type-aware lint in CI: `oxlint .` (no `--type-aware`).
- Re-enable `oxlint --type-aware` (or `--type-check --type-aware`) after tsconfig and tooling are optimized.

## Plugins (enable, disable, add)

**Docs:** <https://oxc.rs/docs/guide/usage/linter/plugins.html>

### Enable / disable

- **Config:** In `.oxlintrc.json`, set `"plugins": ["import", "react", ...]`. This **overwrites** the default set—list every plugin you want (including defaults like `eslint`, `typescript`, `unicorn`, `oxc` if you keep them).
- **CLI:** `oxlint --import-plugin` (enable), `oxlint --disable-unicorn-plugin` (disable a default). Category flags (e.g. `-Dcorrectness -Wsuspicious`) control which rules run. Run `oxlint --help` for all plugin flags.
- **Disable all defaults:** `"plugins": []` in config, or use the CLI disable flags.

### Supported built-in plugins (from docs)

| Plugin       | Default | Source |
|-------------|---------|--------|
| eslint      | Yes     | ESLint core |
| typescript  | Yes     | typescript-eslint; type-aware in [type-aware mode](https://oxc.rs/docs/guide/usage/linter/type-aware) |
| unicorn     | Yes     | eslint-plugin-unicorn |
| oxc         | Yes     | Oxc-specific + deepscan-style rules |
| react       | No      | eslint-plugin-react + react-hooks |
| react-perf  | No      | eslint-plugin-react-perf |
| nextjs      | No      | @next/eslint-plugin-next |
| import      | No      | eslint-plugin-import / import-x |
| jsdoc       | No      | eslint-plugin-jsdoc |
| jsx-a11y    | No      | eslint-plugin-jsx-a11y |
| node        | No      | eslint-plugin-n |
| promise     | No      | eslint-plugin-promise |
| jest        | No      | eslint-plugin-jest |
| vitest      | No      | @vitest/eslint-plugin |
| vue         | No      | eslint-plugin-vue (script tags) |

Rule coverage: [linter product plan](https://github.com/oxc-project/oxc/issues/481).

### Adding new plugins

**Docs:** <https://oxc.rs/docs/guide/usage/linter/plugins.html#adding-new-plugins>

- **New rules in existing built-in plugins:** Contribute via [adding rules](https://oxc.rs/docs/contribute/linter/adding-rules). Contributions to existing plugins are encouraged.
- **New built-in plugin (new rule set):** Open a [GitHub discussion](https://github.com/oxc-project/oxc/discussions/new?category=feature-request) first; do not open a PR for a new plugin without prior discussion.
- **JS plugins (ESLint-compatible):** [JS Plugins](https://oxc.rs/docs/guide/usage/linter/js-plugins) (experimental).

## Useful links

| Topic           | URL                                                                 |
|----------------|---------------------------------------------------------------------|
| Parser         | <https://oxc.rs/docs/guide/usage/parser.html>                       |
| Resolver       | <https://oxc.rs/docs/guide/usage/resolver.html>                     |
| Linter         | <https://oxc.rs/docs/guide/usage/linter.html>                       |
| Plugins        | <https://oxc.rs/docs/guide/usage/linter/plugins.html>                |
| Multi-file     | <https://oxc.rs/docs/guide/usage/linter/multi-file-analysis.html>  |
| Type-aware     | <https://oxc.rs/docs/guide/usage/linter/type-aware.html>            |
