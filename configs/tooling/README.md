# Tooling Configs

Parameterized configurations for linters, formatters, and IDEs.

## Purpose
Standardize code quality tools across all projects.

## Tools Covered
| Tool | Language | Config File |
|------|----------|-------------|
| Ruff | Python | `ruff.toml` |
| Prettier | TypeScript/JS | `.prettierrc*` |
| ESLint | TypeScript/JS | `.eslintrc*` |
| golangci-lint | Go | `.golangci.yml` |
| rustfmt | Rust | `rustfmt.toml` |
| clippy | Rust | `clippy.toml` |
| shellcheck | Shell | `.shellcheckrc` |

## Structure
```
configs/tooling/
├── ruff.toml
├── pre-commit/
│   ├── basic.yaml      # Minimal checks
│   ├── comprehensive.yaml  # Full checks
│   └── security.yaml   # Security-focused
├── pyproject.toml
├── eslint/
├── golangci-lint/
├── prettier/
└── editorconfig/
```

## Usage
Apply to project:
```bash
# Copy tooling configs
cp configs/tooling/* <project>/

# Or reference via pre-commit
cp configs/tooling/pre-commit/comprehensive.yaml <project>/.pre-commit-config.yaml
```

## Agent Pattern
Agents read tooling configs to understand project standards and enforce during code review.
