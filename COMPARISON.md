# Comparison Matrix

## Feature Comparison

This document compares **TracerTM (trace)** with similar tools in the requirements traceability and project management space.

| Repository | Purpose | Key Features | Language/Framework | Maturity | Comparison |
|------------|---------|--------------|-------------------|----------|------------|
| **TracerTM (this repo)** | Requirements traceability | Multi-view, Agent-native, Real-time sync, Graph visualization | Go/Python/React | Stable | RTM system |
| [Jira](https://www.atlassian.com/software/jira) | Project tracking | Issues, Workflows, Boards | Java | Stable | Enterprise standard |
| [Linear](https://linear.app) | Issue tracking | Speed, Design, GitHub sync | TypeScript | Stable | Modern issue tracking |
| [Azure DevOps](https://learn.microsoft.com/en-us/azure/devops/) | DevOps platform | Boards, Pipelines, Repos | Various | Stable | Microsoft ecosystem |
| [OpenProject](https://github.com/opf/openproject) | Project management | Gantt, Wiki, Forums | Ruby | Stable | Open source PM |
| [Redmine](https://github.com/redmine/redmine) | Project management | Issues, Time tracking, Wiki | Ruby | Stable | Classic open source |
| [Meistertask](https://www.meistertask.com) | Task management | Boards, Automations, Integrations | Node.js | Stable | Visual task mgmt |

## Detailed Feature Comparison

### Traceability

| Feature | TracerTM | Jira | Linear | Azure DevOps |
|---------|----------|------|--------|--------------|
| Requirements Trace | ✅ | ✅ | ❌ | ✅ |
| Multi-View | ✅ (Code, API, DB, Deploy, Docs) | ❌ | ❌ | ❌ |
| Impact Analysis | ✅ | ✅ | ❌ | ✅ |
| Trace Matrix | ✅ | ✅ | ❌ | ✅ |
| Agent-Native | ✅ | ❌ | ❌ | ❌ |

### Architecture

| Component | TracerTM | Jira | Linear |
|-----------|----------|------|--------|
| Backend | Go | Java | TypeScript |
| Frontend | React/TS | React | React |
| Graph DB | Neo4j | Proprietary | ❌ |
| Cache | Redis | Proprietary | Redis |
| Messaging | NATS | Proprietary | Azure |

### Observability

| Feature | TracerTM | Azure DevOps |
|---------|----------|--------------|
| Prometheus | ✅ | ✅ |
| Loki (Logs) | ✅ | ✅ |
| Tempo (Traces) | ✅ | ✅ |
| Grafana | ✅ | ✅ |

## Unique Value Proposition

TracerTM provides:

1. **Multi-View Traceability**: Code, API, DB, deployment, docs lenses
2. **Agent-Native Design**: AI-assisted analysis and automated maintenance
3. **Graph Visualization**: Neo4j-powered dependency graphs
4. **Hardened Governance**: SLSA provenance, signed attestations

## Quick Start

```bash
task install        # Install dependencies
task db:migrate     # Run migrations
task dev:tui        # Start with TUI dashboard
# Access: http://localhost:4000
```

## References

- Jira: [atlassian/jira](https://www.atlassian.com/software/jira)
- Linear: [linearapp/linear](https://github.com/linearapp/linear)
- Azure DevOps: [Microsoft/azure-devops-yaml-schema](https://learn.microsoft.com/en-us/azure/devops/)
