# Pheno-SDK Documentation Hub

This directory hosts the consolidated documentation set for Pheno-SDK. The structure below keeps a single source of truth for the platform overview, cross-cutting concepts, contribution guidance, and module-level (kit) manuals.

```
docs/
├── index.md                  # High-level overview and navigation
├── guides/
│   ├── getting-started.md    # Installation and first project walkthroughs
│   ├── operations.md         # Deployment, observability, and runtime guidance
│   └── contributing.md       # Contributor workflow, coding standards, review process
├── concepts/
│   ├── architecture.md       # Core architectural principles and system design
│   ├── patterns.md           # Common paradigms, best practices, and usage patterns
│   └── testing-quality.md    # Testing strategy, QA tooling, and validation guidance
└── kits/
    ├── adapter-kit.md        # One manual per kit (generated below)
    ├── api-gateway-kit.md
    ├── ...
    └── workflow-kit.md
```

Each kit manual follows the same sections:

1. **At a Glance** – Purpose, when to use, and key building blocks.
2. **Core Capabilities** – Primary abstractions with links into the code base.
3. **Getting Started** – Installation, scaffolding, and minimal example.
4. **How It Works** – Architecture, lifecycle, and integration points.
5. **Usage Recipes** – Opinionated patterns for real workloads.
6. **Interoperability** – How the kit cooperates with the rest of Pheno-SDK.
7. **Operations & Observability** – Configuration, tuning, metrics, logging.
8. **Testing & QA** – Recommended fixtures, in-memory adapters, contract tests.
9. **Troubleshooting** – Common failure modes and remediation steps.
10. **API Surface** – The handful of entry points developers should know first.

Maintaining the structure:

- Every kit README in the repository points to its dedicated manual in `docs/kits/`.
- Cross-cutting information (e.g. dependency injection, tenant isolation, tracing) lives under `concepts/` and is referenced from the kit manuals instead of being duplicated.
- Contributor and release workflows are described in `guides/contributing.md` and augment the root `CONTRIBUTING.md`.
- LLM-friendly summary stays in `llms.txt`, mirroring the new outline for tool ingestion.

When a new kit is added, copy `docs/kits/_template.md`, fill in the sections, and update the global index (`docs/index.md`).
