# Contributing to Tracera

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository and clone your fork.
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install dependencies (see README.md for project-specific requirements).
4. Copy `.env.example` to `.env` and configure as needed.

## Building

```bash
# List available build recipes
just list

# Build release artifacts
just build
```

## Testing

```bash
# Run the test suite
just test
```

## Submitting Changes

1. Make your changes with clear, focused commits.
2. Ensure tests pass locally.
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to your fork (`git push origin feature/amazing-feature`)
5. Open a **Pull Request** against `main`.
6. Fill out the PR description with context and motivation.

## Commit Message Format

We follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Tests
- `chore:` Maintenance

## Code Review

All submissions require review. Please ensure:
- CI checks pass
- Code is documented
- Tests cover new functionality

## Governance

Project-wide rules live under `docs/governance/`. The canonical
background-agent policy that this repository and sibling repos
(such as `thegent` and `thegent-clean`) point at is:

- [`docs/governance/background_agent_policy.md`](./docs/governance/background_agent_policy.md)

When changing fleet composition, dispatch patterns, or
failure-handling expectations, update that file in the same PR and
reference the governance worklog entry.

## Code of Conduct

Be respectful and constructive in all interactions.
