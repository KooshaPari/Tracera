# FUNCTIONAL_REQUIREMENTS — template-domain-webapp

## FR-STRUCT-001: Directory Layout
**SHALL** generate the directory tree: `src/domain/`, `src/application/use-cases/`, `src/adapters/`, `src/ports/`, `src/ui/`, `src/config/`.
Traces to: E1.1

## FR-STRUCT-002: API Layer
**SHALL** generate a typed API router with at least one example endpoint using the project stack (e.g. Hono, Fastify, Express).
Traces to: E1.2

## FR-STRUCT-003: UI Scaffold
**SHALL** generate a frontend scaffold with Radix UI or shadcn/ui components, Tailwind CSS, and dark mode enabled by default.
Traces to: E1.3

## FR-AUTH-001: Auth Port
**SHALL** generate an `AuthPort` interface and an `InMemoryAuthAdapter` stub implementing it.
Traces to: E2.1

## FR-AUTH-002: Route Guards
**SHALL** generate at least one protected route example using the auth port.
Traces to: E2.2

## FR-DX-001: Task Commands
**SHALL** include `Taskfile.yml` with: `dev`, `lint`, `test`, `build`, `scaffold` tasks.
Traces to: E3.1

## FR-DX-002: Pre-Configured Tooling
**SHALL** include oxlint config, TypeScript strict config, Prettier/oxfmt config with zero-error baseline.
Traces to: E3.2

## FR-CI-001: GitHub Actions
**SHALL** include `.github/workflows/ci.yml` with lint, test, and build jobs on pull_request.
Traces to: E4.1

## FR-CI-002: Docker Compose
**SHALL** include `docker-compose.yml` with at least a database service and example env variables.
Traces to: E4.2
