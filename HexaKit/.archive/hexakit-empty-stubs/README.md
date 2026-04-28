# HexaKit Empty Stubs — Archived

**Status**: DEPRECATED (Tier 2 empty stubs)  
**Archive Date**: April 24, 2026

This directory contains 10 zero-LOC or minimal-LOC projects archived during HexaKit products promotion (Phase 1). These were scaffolding placeholders with no production code.

## Archived Projects

| Project | LOC | Reason |
|---------|-----|--------|
| phenotype-observability | 0 | WIP stub; no code |
| phenotype-guard | 0 | Unused abstraction |
| pheno-guard | 0 | Duplicate stub |
| phenotype-crypto | 1 | Placeholder only |
| phenotype-git-core | 1 | Placeholder only |
| phenotype-http-client-core | 1 | Placeholder only |
| phenotype-process | 1 | Placeholder only |
| phenotype-mcp | 1 | Placeholder only |
| agileplus-dashboard | 0 | Framework scaffolding only |
| agileplus-dashboard-server | 0 | Framework scaffolding only |

## Usage

These are NOT to be used. They are retained in `.archive/` for historical reference only.

If you need a feature from any of these, refer to the corresponding production crate:
- **Observability** → Use HexaKit/crates/phenotype-telemetry
- **Guard patterns** → Use HexaKit/crates/phenotype-contract
- **Crypto** → Use HexaKit/crates/cipher
- **Git operations** → Use HexaKit/crates/phenotype-ports-canonical
- **HTTP client** → Use HexaKit/crates/phenotype-http-client
- **Process management** → Implement per-use case (no generic abstraction)
- **MCP integration** → Use HexaKit/agileplus-mcp
- **Dashboard** → Use canonical AgilePlus repo (agileplus-dashboard crate)

## Migration Path

Do not depend on these. Remove any references from Cargo.toml files in the workspace root.
