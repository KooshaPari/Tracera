## 2. Endpoint Preservation as Regression Oracle

## Status
Accepted

## Context
The router inventory shows many historical files disappeared on main while capabilities consolidated into fewer routers. A filename-based diff appears to imply large regression (61→11), but capability checks show ~24 endpoints were preserved and rehomed.

## Decision
- Treat the **24-endpoint contract** on main as the non-regression oracle for migration.
- Validate each migration step by **capability contract verification** (endpoint path and request/response schema), not by file/module names.
- Require explicit, approved exceptions only when endpoint capabilities are intentionally removed or replaced.

## Consequences
- Prevents false regression conclusions during refactors and consolidations.
- Keeps endpoint behavior continuity as the primary acceptance criterion across language rewrites.
- Makes migration review actionable: diffs must preserve interface contracts, or clearly document and approve intentional deviations.
