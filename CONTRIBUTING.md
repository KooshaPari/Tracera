# Contributing to TracerTM 🚀

Thank you for your interest in contributing to **TracerTM**! We are building a world-class requirements traceability system, and your contributions are essential.

## 📋 Code of Conduct

By participating, you agree to uphold a professional and respectful environment for all contributors.

## 🛠️ Development Setup

TracerTM is a polyglot system (Go, Python, TypeScript). We use `Task` and `Process Compose` for unified orchestration.

1. **Clone and Install**:
   ```bash
   git clone https://github.com/kooshapari/tracertm.git
   cd tracertm
   task install
   ```

2. **Database Setup**:
   ```bash
   task db:migrate
   ```

3. **Start Development Environment**:
   ```bash
   task dev:tui  # Interactive TUI dashboard
   ```

## 🧪 Testing & Quality Standards

This project operates at a **critical** quality tier. All PRs must pass the following:

- **Backend (Go)**: `go test ./...` and `golangci-lint` must be green.
- **Backend (Python)**: `pytest` and `ruff` (lint/format) must be green.
- **Frontend**: `bun test` and TypeScript type-checking must pass.
- **Architecture**: `tach` boundary checks must be satisfied.
- **Security**: `govulncheck` and `bandit` must report zero vulnerabilities.

## 📜 Coding Guidelines

- **Traceability First**: Every significant feature should be linked to a requirement in the RTM.
- **Observability**: Add structured logging and OpenTelemetry spans to new logic.
- **Hardening**: Follow the patterns defined in `VERIFICATION_POLICY.md` for quality gate compliance.

## 🚀 Pull Request Process

1. **Branching**: Use `feature/` or `fix/` prefixes.
2. **Attestation**: Your PR will trigger automated quality gates that generate signed SLSA attestations.
3. **Disputes**: If you believe a quality gate decision is incorrect, refer to the workflow in `VERIFICATION_POLICY.md`.
4. **Review**: All PRs require at least one approval from a maintainer.

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---
Thank you for helping us build the future of traceability!
