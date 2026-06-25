## 3. Absent Capabilities Treatment

## Status
Accepted

## Context
Cross-branch endpoint reconciliation on main identified three likely deliberate omissions (blockchain, chat, codex) and two likely undesired gaps (adrs, linear). Phase-0 inventory requests explicit decisions before broad migration.

## Decision
- Mark **`adrs`** as `REVIEW` and treat it as a likely regression that should be restored unless intentionally retired.
- Mark **`linear`** as `REVIEW` and treat it as a likely regression for planned restoration.
- Confirm **`blockchain`**, **`chat`**, and **`codex`** as **intentional cuts** only if product scope explicitly removes them.

## Consequences
- Prevents accidental drift in endpoint expectations for core traceability governance areas.
- Establishes an explicit restoration path for `adrs` and `linear`.
- Avoids accidental reintroduction of experimental capabilities if they were intentionally removed from scope.
