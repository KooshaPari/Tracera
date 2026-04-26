# template-domain-webapp

Domain template layer for web applications. Composes shared commons and language layers.

## Stack

- Template layer for: Web application domains
- Build orchestration: Taskfile

## Structure

- `templates/` - Domain-specific web app templates
- `contracts/` - Interface contracts
- `scripts/` - Automation scripts
- `docs/` - Documentation

## Phenotype Org Rules

- UTF-8 encoding only in all text files. No Windows-1252 smart quotes or special characters.
- Worktree discipline: canonical repo stays on `main`; feature work in worktrees.
- CI completeness: fix all CI failures on PRs, including pre-existing ones.
- Never commit agent directories (`.claude/`, `.codex/`, `.gemini/`, `.cursor/`).
