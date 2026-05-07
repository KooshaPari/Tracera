# Architecture

## Overview

Agent-native requirements traceability and project management system. Go backend for high-performance API and business logic; Python services for workflow and tooling; React/TypeScript frontend for the dashboard. Manages requirements-to-code-to-deployment traceability matrices.

## Components

### Go Backend (`backend/`)
High-performance REST API with JWT auth. PostgreSQL for structured data, Redis for caching, S3-compatible storage for artifacts. Modules: `cmd/` (entry points), `internal/` (business logic), `pkg/` (reusable packages).

### Python Services (`src/tracertm/`)
FastAPI routes, business logic services, SQLAlchemy repositories, file/markdown storage, MCP server tools, agent coordination, Textual TUI. NATS for messaging, Temporal for workflow orchestration.

### React Frontend (`frontend/`)
Turbo monorepo with multiple apps: `web/` (main dashboard), `docs/` (VitePress), `storybook/` (component library), `desktop/` (Electron). TanStack Router, Zustand state, Tailwind CSS.

## Data Flow

React dashboard (frontend) -> Go REST API -> PostgreSQL (data) + Redis (cache) + S3 (artifacts). Python services handle async workflows via Temporal; NATS for real-time events. Requirements link to code via MCP tools and agent coordination.

## Key Files

- `backend/` — Go API server (`cmd/api`)
- `frontend/` — React Turbo monorepo (`apps/web`, `packages/`)
- `src/tracertm/` — Python services (FastAPI, MCP, TUI)
- `go.mod` — Go module
- `pyproject.toml` — Python package
- `frontend/package.json` — TS workspace
- `turbo.json` — Turbo build config
