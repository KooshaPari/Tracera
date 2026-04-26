![Build Status](https://github.com/Phenotype-Enterprise/trace/actions/workflows/quality-gate.yml/badge.svg)
![Security Audit](https://github.com/Phenotype-Enterprise/trace/actions/workflows/security-guard.yml/badge.svg)
![Policy Compliance](https://github.com/Phenotype-Enterprise/trace/actions/workflows/policy-gate.yml/badge.svg)

# TracerTM 🚀

[![Go Report Card](https://goreportcard.com/badge/github.com/kooshapari/tracertm)](https://goreportcard.com/report/github.com/kooshapari/tracertm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Agent-native requirements traceability and project management dashboard.**

TracerTM is a modern requirements traceability matrix (RTM) and project management system designed for agent-driven development workflows. It provides a unified dashboard and control plane for linking requirements to code, tests, and deployments—built on a Go backend with a TypeScript/React Turbo frontend.

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Quick Start](#quick-start)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Testing & Quality](#-testing--quality)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Key Features

- 🔍 **Multi-View Traceability**: Navigate projects through requirements, code, tests, and deployment lenses.
- 🤖 **Agent-Native Design**: Built-in support for AI-assisted analysis and automated traceability maintenance.
- ⚡ **Real-Time Updates**: Live synchronization across dashboard and backend.
- 📊 **Interactive Visualization**: Dependency graphs and impact analysis for requirements and code.
- 🛡 **Hardened Governance**: SLSA provenance, signed attestations, and automated quality gates.
- 📈 **Integrated Observability**: Metrics (Prometheus), logs (Loki), and tracing through Phenotype OTLP collector.

---

## 🏗 Architecture

TracerTM uses a polyglot architecture optimized for requirements traceability:

**Backend (Go 1.25)**
- High-performance API server managing core business logic, data persistence, and integrations.
- RESTful API with JWT authentication.
- PostgreSQL for structured data, Redis for caching.
- S3-compatible storage integration (AWS SDK v2).

**Frontend (TypeScript/React 19 + Turbo)**
- Modern React application with TanStack Router for client-side routing.
- Turbo monorepo with multiple workspace apps (web dashboard, documentation, Storybook, desktop).
- Tailwind CSS + Geist design system for consistent UI.
- Build tooling: Vite, Bun, Turbo with oxlint/oxfmt for code quality.

---

## 🚀 Getting Started

### Prerequisites

- **Go 1.25+** (for backend)
- **Node.js 22+ / Bun 1.1+** (for frontend)
- **PostgreSQL 14+** (for data storage)
- **Redis 6+** (for caching)

### Quick Start

#### Backend (Go API)

```bash
cd backend
go build -o tracertm ./cmd/api
./tracertm
```

The API server starts on `http://localhost:8080`.

#### Frontend (TypeScript/React)

```bash
cd frontend
bun install
bun run dev
```

The web dashboard opens on `http://localhost:3000`.

---

## 📁 Project Structure

```
.
├── backend/                   # Go API server
│   ├── cmd/                   # CLI entry points
│   ├── internal/              # Business logic (unexported)
│   ├── pkg/                   # Reusable packages
│   ├── configs/               # Configuration templates
│   ├── tests/                 # Integration & E2E tests
│   ├── e2e/                   # End-to-end test scenarios
│   ├── benchmarks/            # Performance benchmarks
│   └── go.mod                 # Go module definition
│
├── frontend/                  # TypeScript/React dashboard
│   ├── apps/                  # Turbo workspace apps
│   │   ├── web/               # Main React dashboard
│   │   ├── docs/              # VitePress documentation
│   │   ├── storybook/         # Component library showcase
│   │   └── desktop/           # Electron desktop app
│   ├── packages/              # Shared packages
│   ├── tsconfig.json          # TypeScript configuration
│   ├── package.json           # Root workspace config
│   └── turbo.json             # Turbo build orchestration
│
└── .github/workflows/         # CI/CD pipelines
```

---

## 🔧 Development

### Backend Commands

```bash
cd backend

# Run tests
go test ./...

# Run with hot-reload (requires air or similar)
go run ./cmd/api

# Build release binary
go build -ldflags="-X main.Version=$(git describe --tags)" -o tracertm ./cmd/api
```

### Frontend Commands

```bash
cd frontend

# Development server with hot reload
bun run dev

# Type checking
bun run typecheck

# Linting with oxlint
bun run lint

# Format with oxfmt
bun run format

# Build all apps
bun run build

# Run tests
bun run test
```

---

## ✅ Testing & Quality

### Backend Testing
```bash
cd backend
go test -v -cover ./...
```

### Frontend Testing
```bash
cd frontend
bun run test
bun run quality  # Full lint + type + format + build + test
```

### Quality Gates
Both backend and frontend enforce strict quality standards:
- **Linting**: clippy (Rust-based backend checks), oxlint (frontend)
- **Type Safety**: Go strict typing, TypeScript strict mode
- **Code Coverage**: Minimum 80% target
- **Security**: SAST, dependency scanning, secret detection

---

## 📚 Documentation

- **API Documentation**: See `backend/README.md`
- **Frontend Architecture**: See `frontend/README.md`
- **Design System**: `frontend/apps/storybook/`
- **Contributing**: See `CONTRIBUTING.md`

---

## 🤝 Contributing

TracerTM welcomes contributions. Please:

1. Check [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit with clear messages and reference any related issues.
4. Push and open a pull request.
5. Ensure all quality checks pass (CI/CD pipeline).

---

## 📄 License

Licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

**Built with 🛠 for agent-driven development**
