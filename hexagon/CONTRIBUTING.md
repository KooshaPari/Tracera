# Contributing to Hexagon

Thank you for your interest in contributing to Hexagon! This document provides guidelines for contributing to the project.

## Ways to Contribute

- **Bug Reports**: Report issues with templates
- **Feature Requests**: Suggest new languages or features
- **Documentation**: Improve guides and references
- **Code**: Fix bugs or implement features
- **Templates**: Add new language templates
- **Reviews**: Review pull requests

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/hexagon.git`
3. Create a branch: `git checkout -b feature/my-feature`
4. Make changes
5. Run verification: `./scripts/verify.sh`
6. Commit: `git commit -m "feat: add feature"`
7. Push: `git push origin feature/my-feature`
8. Open a pull request

## Development Setup

### Prerequisites

- Git 2.30+
- Make (optional)
- Language toolchains for templates you work on

### Repository Structure

```
hexagon/
├── templates/          # Language-specific templates
│   ├── go/
│   ├── rust/
│   ├── zig/
│   ├── elixir/
│   ├── kotlin/
│   ├── mojo/
│   └── swift/
├── docs/               # Documentation
│   ├── adr/            # Architecture decisions
│   └── research/       # SOTA research
├── scripts/            # Utility scripts
└── README.md           # Project overview
```

## Contribution Guidelines

### Commit Messages

Follow conventional commits:

```
<type>: <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Test changes
- `chore`: Maintenance tasks

Examples:
```
feat: add swift template support
fix: correct rust trait bounds in ports
docs: update SOTA with new patterns
test: add elixir integration tests
```

### Pull Request Process

1. **Before submitting**:
   - Run `./scripts/verify.sh`
   - Update documentation
   - Add tests if applicable
   - Ensure traceability markers present

2. **PR Description**:
   - Clear description of changes
   - Related issue numbers
   - Screenshots if relevant
   - Checklist completion

3. **Review**:
   - Address reviewer feedback
   - Keep discussion focused
   - Be respectful

### Code Standards

**All Languages:**
- Follow existing patterns
- Include traceability markers: `/// @trace HEXAGON-XXX`
- Document public APIs
- Handle errors explicitly

**Documentation:**
- Use UTF-8 encoding
- Follow nanovms-style format
- Include tables for comparisons
- Add code examples

### Adding a New Language Template

1. **Proposal**:
   - Open an issue with `template-proposal` label
   - Describe language and target use cases
   - Reference existing similar templates

2. **Structure**:
   ```
   templates/{language}/
   ├── README.md
   ├── SPEC.md
   ├── domain/
   ├── application/
   ├── ports/
   ├── infrastructure/
   ├── tests/
   └── docs/
   ```

3. **Required Elements**:
   - [ ] Domain layer with entities
   - [ ] Application layer with use cases
   - [ ] Ports with interfaces
   - [ ] Infrastructure with adapters
   - [ ] Unit tests
   - [ ] Integration tests
   - [ ] Documentation (README, SPEC)
   - [ ] ADR for language-specific decisions

4. **Review**:
   - Architecture review
   - Code review
   - Documentation review

### Documentation Contributions

**SOTA.md updates:**
- Research-based additions
- Cite sources
- Include code examples

**ADR additions:**
- Follow ADR template
- Include decision drivers
- Document consequences

**README updates:**
- Clear and concise
- Working code examples
- Accurate information

## Testing

### Template Verification

```bash
# Verify all templates
./scripts/verify.sh

# Verify specific language
./scripts/verify.sh templates/go/
```

### Language-Specific Tests

```bash
# Go
cd templates/go && go test ./...

# Rust
cd templates/rust && cargo test

# Elixir
cd templates/elixir && mix test
```

### Documentation Tests

```bash
# Link checking
./scripts/check-links.sh

# Traceability verification
./scripts/check-traceability.sh
```

## Architecture Decisions

Significant changes require an ADR:

1. Create `docs/adr/ADR-XXX-title.md`
2. Follow existing ADR format
3. Update `docs/adr/index.md`
4. Include in PR

When is an ADR required?
- New language templates
- Structural changes to templates
- Changes to hexagonal pattern implementation
- Tooling architecture changes
- Breaking changes

## Community

- **Issues**: GitHub issue tracker
- **Discussions**: GitHub Discussions
- **Discord**: Phenotype community

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in relevant documentation

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

## Questions?

- Check [FAQ.md](FAQ.md)
- Open a discussion
- Ask in Discord

## Traceability

/// @trace HEXAGON-CONTRIBUTING-001
/// @trace HEXAGON-SPEC-001
