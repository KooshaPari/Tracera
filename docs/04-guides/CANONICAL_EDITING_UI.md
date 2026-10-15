# Canonical graph editing UI

The project item table's create modal saves title, description, view, type, status and explicit project scope. The item detail editor saves title, description and status; Kanban moves save status. Item deletion includes project scope and refreshes item, relationship and graph queries to reflect incident-link deletion.

Owner and priority controls are disabled and identify that graph editing does not save them. Parent, metadata and specification creation are not supported by the canonical CRUD contract. Direct callers supplying unsupported attributes receive a client error before a request; attributes are not silently dropped.

Traceability Links now requires selecting a project, then **Create Connection** opens the existing source/target/type form. Item IDs may be arbitrary imported identifiers rather than UUIDs. Relationship descriptions are explicitly unavailable. Create responses retain the backend's opaque link identity; deletion supplies that identity and the selected project. Changing project closes the connection modal and uses a distinct query cache key.

New canonical item responses do not contain per-item timestamps. Their normalized timestamp strings are empty, which the detail selectors display as Unknown. Existing detail responses may still contain the project timestamp approximation; this UI patch does not establish per-item creation or update times.

The rich `CreateItemDialog` component has no production caller in this source snapshot; it is referenced by its example and tests. Its specification forms and the alternate legacy API stacks remain outside this bounded canonical editing flow.

## Validation

- `node --test frontend/apps/web/src/lib/__tests__/canonical-editing/contract.test.mjs`: five executable project-scope/payload/provenance guard checks.
- `frontend/apps/web/src/__tests__/hooks/canonical-editing.test.tsx`: six hook integration checks for actual request bodies, CSRF/cookies, canonical response normalization and same imported ID across project changes. Run with the frontend Vitest toolchain.
- Local TypeScript transpilation syntax audit and `git diff --check`.

The exact frozen frontend dependency lock was restored using an existing cached Bun runtime. The six new hook checks and the four affected legacy hook files pass together (78 tests). Full frontend workspace typechecking passes (web and six packages), and the normal Turbo web build passes all five tasks. A final web typecheck and build were rerun after narrow read-query compatibility and accessible-name repairs. No live browser or human acceptance is claimed by these checks.
