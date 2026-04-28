# Legacy Cleanup Dependency Impact

## Overview

The February 2025 cleanup removes the final auth shims, registry compat layer, Temporal compat helpers, and shared model aliases. This report summarises the dependency impact across the four affected domains.

## Auth Stack

- **Removed modules:** `src/pheno/auth/mfa/*`, `src/pheno/auth/providers/*`, `src/pheno/auth/core/*`, `src/pheno/auth/setup.py`, `src/pheno/auth/example.py`.
- **Replacement:** Import adapters and registries from `pheno.adapters.auth.*`.
- **Affected consumers:** CLI auth flows, QA harnesses, docs examples.
- **Mitigation:** `pheno.auth` continues to re-export the canonical API; warnings only fire when legacy aliases are imported (no longer possible after deletion).

## Provider Registry

- **Removed module:** `src/pheno/providers/registry/compat.py`.
- **Replacement:** `pheno.providers.registry` now exports catalog classes (`OpenAIModelCatalog`, etc.), with legacy aliases mapped to new names.
- **Tests updated:** `tests/providers/test_model_registries.py` now uses the catalog API.
- **External impact:** Any out-of-tree code referencing `pheno.providers.registry.compat` must update imports before 31 Mar 2025.

## Service Infrastructure

- **Current state:** Legacy aliases (`start_tunnel`, `get_service_url`) remain but now log warnings mentioning the 31 Mar 2025 removal date.
- **Outstanding work:** Call sites in service manager/orchestrator packages will be migrated during Infrastructure Canonicalization (Work Package 2).
- **Risk:** High if callers ignore warnings; the communication plan captures follow-up actions.

## HTTP Utilities

- **Status:** `pheno.dev.http.HTTPClient` persists for compatibility but now emits a deprecation warning with the same 31 Mar 2025 deadline.
- **Plan:** Update examples (`examples/stack/fastapi_pheno_example.py`) and infra helpers (`src/pheno/infra/utils/httpx_otel.py`) to the httpx helpers ahead of removal.

## Next Steps

1. Track warning counts in staging environments to ensure consumers are migrating.
2. Complete the remaining migration work per Work Package 2 and 3.
3. Lock-in removal PR for the first April 2025 release, pending stakeholder sign-off.
