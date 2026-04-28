# Changelog

All notable changes to this project will be documented in this file.

## 📚 Documentation
- Docs: add deprecation - merged into HexaKit/python (`3945449`)
## ✨ Features
- Feat: complete phenoSDK decomposition - move final core files

Moved remaining phenoSDK files to pheno-core:
- correlation_id.py → pheno_core/correlation_id.py
- stream.py → pheno_core/stream.py
- __init__.py → updated pheno_core/__init__.py with proper exports

phenoSDK/src/pheno/ now contains only documentation:
- README.md
- NAMING_CANONICALIZATION_MAP.md

phenoSDK is effectively retired. All 305,000+ LOC now lives in:
- PhenoLang/python/ (32 packages)
- PhenoProc/python/ (17 packages)

2026-04-05 (`c523501`)
- Feat: remove all 48 extracted modules from phenoSDK

Deleted modules (all moved to workspace packages):
- PhenoLang workspace: 31 packages (adapters, application, auth, caching, config, core, credentials, database, dev, domain, errors, events, exceptions, integration, logging, patterns, plugins, ports, resilience, resources, security, shared, storage, tools, tui, ui, utilities, vector, web, + async, architecture)
- PhenoProc workspace: 17 packages (analytics, cicd, cli, clink, deployment, infra, infrastructure, kits, llm, mcp, observability, optimization, process, providers, quality, testing, workflow)

Remaining in phenoSDK:
- __init__.py (package init)
- correlation_id.py (1,463 bytes)
- stream.py (9,021 bytes)
- NAMING_CANONICALIZATION_MAP.md
- README.md (documentation)

Total removed: ~305,000 LOC from 1,775 Python files
Modules are now standalone packages in:
- /PhenoLang/python/ (31 packages)
- /PhenoProc/python/ (17 packages)

2026-04-04 (`295b6b5`)
## 🔨 Other
- Chore(governance): adopt CLAUDE.md + governance framework

Enable AgilePlus spec tracking, FR traceability, and standard project conventions. Wave-5 governance push.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com> (`41a97a0`)
- Chore(ci): adopt phenotype-tooling workflows (wave-3) (`2575591`)
- Chore(pre-commit): add legacy tooling anti-pattern scanner hook

Adds legacy-tooling-scan hook to pre-commit configuration per CLAUDE.md.

Refs: tooling/legacy-enforcement/README.md (`d9de349`)
- Ci(legacy-enforcement): add strict mode anti-pattern gate workflow

Adds legacy-tooling-gate.yml enforcing Phenotype Technology Adoption Philosophy:
- Downloads central policy from phenotype/repos
- Executes production scanner on PR/push
- Generates JSON/Markdown/SARIF reports
- Uploads to GitHub Security (SARIF)
- Comments PR with findings summary
- STRICT MODE: Fails on critical/high violations

Policy enforced:
- Python: uv primary; pip/poetry/pipenv/setup.py banned
- JavaScript: Bun primary; npm/yarn/pnpm/tsc/jest as legacy
- General: makefiles banned; file size limits (350/400 LOC)

Refs: CLAUDE.md lines 18-67 (Technology Adoption Philosophy) (`c04f42c`)