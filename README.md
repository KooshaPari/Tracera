![Build Status](https://github.com/Phenotype-Enterprise/trace/actions/workflows/quality-gate.yml/badge.svg)
![Security Audit](https://github.com/Phenotype-Enterprise/trace/actions/workflows/security-guard.yml/badge.svg)
![Policy Compliance](https://github.com/Phenotype-Enterprise/trace/actions/workflows/policy-gate.yml/badge.svg)

# TracerTM 🚀

[![Go Report Card](https://goreportcard.com/badge/github.com/kooshapari/tracertm)](https://goreportcard.com/report/github.com/kooshapari/tracertm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Agent-native, multi-view requirements traceability and project management system.**

TracerTM is a comprehensive requirements traceability matrix (RTM) system designed for modern software development workflows. It provides a "Defense in Depth" approach to project governance, linking requirements to code, tests, and deployments across multiple architectural lenses.

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Quick Start](#quick-start)
- [Observability & APM](#-observability--apm)
- [Governance & Hardening](#-governance--hardening)
- [Testing & Quality](#-testing--quality)
- [Documentation](#-documentation)
- [Docs Deploy](#-docs-deploy)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Key Features

- 🔍 **Multi-View Traceability**: View projects through code, API, database, deployment, and documentation lenses.
- 🤖 **Agent-Native Design**: Built-in support for AI-assisted analysis and automated traceability maintenance.
- ⚡ **Real-Time Sync**: WebSocket-based live updates across all management interfaces.
- 📊 **Graph Visualization**: Interactive dependency graphs and impact analysis powered by Neo4j.
- 🛡 **Hardened Governance**: SLSA provenance, signed attestations, and automated quality gates.
- 📈 **Full Observability**: Integrated metrics (Prometheus), logs (Loki), and tracing through the shared Phenotype OTLP collector.

---

## 🏗 Architecture

TracerTM uses a high-performance, polyglot architecture:

- **Backend (Go)**: High-performance API server managing core business logic and integrations.
- **Python Services**: Specialized services for data analysis, CLI/TUI tools, and background processing.
- **Frontend (React/TS)**: Modern SPA with TanStack Router, Zustand, and interactive visualizations.
- **Persistence**: PostgreSQL (Relational), Neo4j (Graph), Dragonfly (Redis-compatible cache), and NATS (Messaging).

---

## 🚀 Getting Started

### Prerequisites
- Go 1.21+, Python 3.11+, Node.js/Bun
- PostgreSQL 17+, Dragonfly latest, Neo4j 5.0+, NATS 2.9+
- [Task](https://taskfile.dev/) (Task runner) and [Process Compose](https://github.com/F_S_A/process-compose)

### Quick Start (Native Environment)

```bash
# 1. Install all dependencies
task install

# 2. Run database migrations
task db:migrate

# 3. Start all services with interactive TUI dashboard
task dev:tui

# 4. Access the Unified Gateway
# http://localhost:4000 (Frontend, API, and Docs)
```

---

## 📊 Observability & APM

TracerTM includes enterprise-grade monitoring out of the box. The default
local trace path is the shared Phenotype collector contract through Grafana
Alloy and Tempo.
- **Metrics**: http://localhost:3000 (Grafana) / http://localhost:9090 (Prometheus)
- **Tracing**: http://localhost:3000 (Grafana/Tempo) - Track requests across Go and Python.
- **Logs**: Centralized log aggregation via Grafana Alloy and Loki.

---

## 🛡 Governance & Hardening

TracerTM operates at a **critical** quality tier:
1. **Automated Quality Gates**: Ruff, Go build/vet, golangci-lint, TSC, and Tach boundaries.
2. **Provenance**: All builds generate SLSA attestations with digital signatures.
3. **Verification Policy**: Defined dispute workflows for quality gate decisions in `VERIFICATION_POLICY.md`.
4. **Security Scanning**: Automated `govulncheck`, `bandit`, and security audits.

### Review-Traceability Rule

- PR review comments that block requirements, API contracts, or architecture are treated as traceability events.
- For each closed PR in a stacked flow, record at least one of:
  - resolved comment thread, or
  - explicit follow-up PR reference with dependency order and trace matrix impact.
- PRD references and trace entries should include review-thread outcomes before promoting to `beta/rc`.

---

## 🧪 Testing & Quality

We maintain a rigorous multi-layer testing strategy:
- **Unit & Integration**: `go test ./...` and `pytest tests/`
- **Frontend**: `bun test` and E2E via Playwright.
- **Complexity Audit**: Automated tracking of code complexity (Radon) and naming conventions.
- **Path Protection**: Architectural boundary enforcement via `tach`.

---

## 📚 Documentation

- **[Docsets](./docs/docsets/)** — Role-specific technical docsets.
  - [Developer (Internal)](./docs/docsets/developer/internal/)
  - [Developer (External)](./docs/docsets/developer/external/)
  - [Technical User](./docs/docsets/user/)
  - [Agent Operator](./docs/docsets/agent/)
- **[First Run Checklist](./docs/checklists/FIRST_RUN_CHECKLIST.md)** — New clone setup.
- **[Changelog Process](./docs/guides/CHANGELOG_PROCESS.md)** — How entries are added and released.
- **[Changelog Entry Template](./docs/reference/CHANGELOG_ENTRY_TEMPLATE.md)** — Copy/paste snippet for new entries.
- **[Project Setup Style](./docs/guides/PROJECT_SETUP_STYLE.md)** — Standardized repo command/process baseline.
- **[API Documentation](http://localhost:4000/docs)** — Interactive API explorer.
- **[Architecture Overview](./docs/reference/ARCHITECTURE_LAYERS.md)** — Deep dive into internals.
- **[Verification Policy](VERIFICATION_POLICY.md)** — Quality standards and dispute workflows.

### Documentation Hub

For a unified view of all Kush ecosystem projects, visit the [Docs Hub](../docs-hub/index.md).

---

## 🚢 Docs Deploy

Local VitePress docs site:

```bash
cd docs
npm install
npm run docs:dev
npm run docs:build
```

GitHub Pages:

- Workflow: `.github/workflows/vitepress-pages.yml`
- URL convention: `https://<owner>.github.io/trace/`

---

## 🤝 Contributing

We welcome community contributions! Please see **[CONTRIBUTING.md](CONTRIBUTING.md)** (coming soon) for details on our development workflow and quality requirements.

---

## 📜 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

---

<p align="center">
  Built with ❤️ by the community
</p>
