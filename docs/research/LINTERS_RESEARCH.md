# Linters research: Stylelint and others

**Date:** 2026-02-01  
**Context:** Do we need/want Stylelint and other linters in the frontend?

---

## Current stack

| Tool | Role | Where |
|------|------|--------|
| **oxlint** | Primary JS/TS/React linter + type-aware (tsgolint) | Root: `lint`, `lint:fix`, `typecheck` |
| **Biome** | Formatter (and optional lint via `lint:biome`) | Root: `format`, `format:check`; web: `lint:biome` |
| **Next.js lint** | ESLint-based lint for docs app | `apps/docs`: `lint` (next lint) |
| **vite-plugin-checker** | Oxlint in dev overlay/terminal | `apps/web` Vite config |
| **Stylelint** | CSS linter (Tailwind-aware) | Root: `lint:stylelint`, `lint:stylelint:fix`; in CI and `quality` |

No root ESLint config. `eslint-plugin-react` and `eslint-plugin-react-hooks` are in root `package.json` but not referenced by any config (unused).

---

## Stylelint

**What it is:** CSS linter (100+ rules, auto-fix, plugins, shareable configs). Good for raw CSS, SCSS, Less, and can target embedded styles / Tailwind `@apply` with the right setup.

**Do we need it?**

- **Project reality:** Only **3 CSS files** (`apps/web/src/index.css`, `apps/docs/app/global.css`, `apps/storybook/src/styles.css`). Styling is **Tailwind-first** (utility classes, `@layer base`, design tokens). Custom CSS is small and structured.
- **Common practice:** On Tailwind-heavy projects many teams **skip Stylelint** or use it only with a Tailwind-aware config (e.g. `stylelint-config-tailwind`) to avoid noise on Tailwind directives.
- **Alternatives:** Biome can lint **CSS** as part of `biome check` (when you run `lint:biome`). So you already have an option for CSS lint without adding Stylelint.

**Recommendation:** Added on a "want" basis. Stylelint is set up with `stylelint-config-recommended` + `stylelint-config-tailwindcss`, `stylelint.config.js`, `.stylelintignore`, and scripts `lint:stylelint` / `lint:stylelint:fix`. It runs in CI and in `bun run quality`.

---

## Other linters

### ESLint

- **Oxlint** covers ESLint-style rules (650+ rules, React, Jest, Unicorn, etc.) and is the primary linter. Type-aware checks use tsgolint.
- **Next.js** (docs app) uses its own ESLint via `next lint`; that’s appropriate for that app.
- **Root:** No ESLint config or `eslint` script. `eslint-plugin-react` and `eslint-plugin-react-hooks` in root `package.json` are **unused** (no `.eslintrc*` or `eslint.config.*` referencing them).

**Recommendation:** **Remove** `eslint-plugin-react` and `eslint-plugin-react-hooks` from frontend root `package.json` to avoid unused dependencies. Keep `next lint` in docs.

### Biome

- Used for **format** (and optionally for **lint** via `lint:biome`). It can format and lint JS/TS/JSX/**CSS**/GraphQL.
- Running both oxlint and Biome lint can duplicate some rules; typical setup is **oxlint for lint**, **Biome for format only**, or use Biome for both and drop oxlint (we’ve standardized on oxlint + type-aware).

**Recommendation:** **Keep Biome for formatting.** Keep `lint:biome` as an optional command if you want extra/alternative checks (including CSS); no need to run it in CI if oxlint is the source of truth for lint.

### HTML / other

- No dedicated HTML or other linters in the stack. Not necessary unless you introduce strict HTML/Markdown requirements.

---

## Summary

| Linter | Need? | Action |
|--------|--------|--------|
| **Stylelint** | Yes (added) | Tailwind-aware config; `lint:stylelint`, `lint:stylelint:fix`; in CI and `quality`. |
| **ESLint (root)** | No | Remove unused `eslint-plugin-react` and `eslint-plugin-react-hooks` from frontend. |
| **Biome** | Yes (format) | Keep for format; optional for lint (`lint:biome`) and CSS. |
| **Oxlint** | Yes | Keep as primary lint + type-aware. |
| **Next lint** | Yes (docs) | Keep for docs app only. |

---

## References

- [Stylelint](https://stylelint.io/)
- [Biome](https://biomejs.dev/) (format + lint, including CSS)
- [Oxlint](https://oxc-project.github.io/docs/guide/usage/linter.html) (JS/TS/React, type-aware)
- [Tailwind + Prettier class sorting](https://github.com/tailwindlabs/prettier-plugin-tailwindcss) (Biome handles formatting; class sorting can be a separate concern if desired)
