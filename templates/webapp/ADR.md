# ADR — template-domain-webapp

## ADR-001: Hexagonal Architecture as Default
**Status:** Accepted
**Context:** Web apps often start as scripts and accumulate coupling. A template should enforce clean boundaries from day one.
**Decision:** All generated projects use hexagonal architecture with explicit `ports/` and `adapters/` directories.
**Rationale:** Enforces testability and replaceability of infrastructure from the first line of code.

## ADR-002: Frontend Stack
**Status:** Accepted
**Context:** UI must be rich and modern per Phenotype mandate.
**Decision:** Default frontend stack: React + Vite + Tailwind CSS + shadcn/ui (Radix-based). Dark mode as default theme.
**Rationale:** shadcn/ui provides accessible, customizable components; Vite provides fast HMR; Tailwind is utility-first.

## ADR-003: API Framework
**Status:** Accepted
**Context:** Multiple TypeScript HTTP frameworks exist; the template should pick one with type safety.
**Decision:** Default API framework is Hono (edge-compatible, typed routes, zero-dep core). Fastify as a documented alternative.
**Rationale:** Hono works on all runtimes (Node, Bun, Deno, edge); typed routes match hexagonal port contracts.

## ADR-004: Auth as Stub, Not Implementation
**Status:** Accepted
**Context:** Auth requirements vary per project; baking in a specific auth library creates tight coupling.
**Decision:** The template provides an `AuthPort` interface and `InMemoryAuthAdapter`. Consumers replace the adapter with their chosen auth solution.
**Rationale:** Hexagonal principle: auth is an adapter, not a domain concern.

## ADR-005: Taskfile over Makefile
**Status:** Accepted
**Context:** Per Phenotype standards, new projects use Taskfile.
**Decision:** All developer commands are in `Taskfile.yml`. No Makefile generated.
**Rationale:** Taskfile is more readable, cross-platform, and supports includes.
