# Frequently Asked Questions (FAQ)

## General Questions

### What is Hexagon?

Hexagon is a unified template registry for hexagonal architecture implementations across multiple programming languages. It provides production-ready templates for Go, Rust, Zig, Elixir, Kotlin, Mojo, and Swift.

### Why hexagonal architecture?

Hexagonal architecture (Ports and Adapters) provides:
- Clear separation of concerns
- Testability at all layers
- Framework independence
- Domain logic isolation
- Easy infrastructure swapping

### Which languages are supported?

Currently: Go, Rust, Zig, Elixir, Kotlin, Mojo, Swift

Planned: TypeScript, Python, C#, Java, C++

### Is Hexagon a framework?

No. Hexagon provides project templates and scaffolding tools. It is not a runtime dependency.

## Usage Questions

### How do I use a template?

```bash
# Clone the repository
git clone https://github.com/KooshaPari/hexagon.git

# Copy template for your language
cp -r hexagon/templates/go my-project

# Customize and build
cd my-project
# Follow language-specific README.md
```

### Can I customize the templates?

Yes. Templates are starting points. Modify them to fit your needs while maintaining hexagonal principles.

### How do I add a new language template?

See [Contributing Guide](CONTRIBUTING.md). The process involves:

1. Proposal issue
2. Architecture review
3. Template implementation
4. Documentation
5. Review and merge

### Can I use multiple templates together?

Each template is for a single service. For polyglot systems, use appropriate templates for each service.

## Architecture Questions

### Do I have to follow the four-layer structure?

The four layers (Domain, Application, Ports, Infrastructure) are the core value proposition. Deviating significantly reduces the benefits.

### Can I skip the Ports layer?

No. Ports define the boundaries that make hexagonal architecture work. They enable testing and implementation swapping.

### How do I handle cross-cutting concerns?

Use:
- Context propagation (Go)
- Middleware (Rust, Kotlin)
- Plug (Elixir)
- Interceptors (Swift)

### What about microservices?

Hexagonal architecture works well with microservices. Each service uses a template; services communicate via their ports.

## Technical Questions

### What dependencies do templates require?

Templates minimize dependencies. Required dependencies typically include:
- UUID generation
- Testing framework
- Optional: database driver, web framework

### How are templates tested?

Each template includes:
- Unit tests for domain logic
- Integration tests for adapters
- CI/CD configurations

### Are templates production-ready?

Yes. Templates include:
- Error handling
- Logging integration points
- Security-conscious defaults
- Performance considerations

### How do I update my project when templates change?

Templates follow semantic versioning. Updates require manual review as they affect your codebase.

Future tooling may assist with automated updates.

## Contributing Questions

### How can I contribute?

See [ContributING.md](CONTRIBUTING.md). Ways to contribute:
- Bug reports
- Feature suggestions
- Documentation improvements
- New language templates
- Tooling enhancements

### What's the code review process?

1. Open a pull request
2. Automated checks run
3. Maintainers review
4. Address feedback
5. Merge upon approval

### How are decisions made?

Significant decisions use the ADR (Architecture Decision Record) process documented in `docs/adr/`.

## Troubleshooting

### Template structure validation fails

Run the verification script:
```bash
./scripts/verify.sh templates/{language}/
```

### Tests fail after generation

Ensure all dependencies are installed:
```bash
# Go
go mod tidy

# Rust
cargo build

# Elixir
mix deps.get
```

### IDE doesn't recognize structure

Some IDEs may need configuration for hexagonal layouts. See language-specific READMEs for IDE setup.

## Comparison Questions

### Hexagon vs Cookiecutter

| Aspect | Hexagon | Cookiecutter |
|--------|---------|--------------|
| Focus | Hexagonal architecture | General templates |
| Languages | Multi, specialized | Any, generic |
| Patterns | Enforced | User-defined |
| Tooling | Planned | CLI only |

### Hexagon vs Copier

| Aspect | Hexagon | Copier |
|--------|---------|--------|
| Architecture | Enforced hexagonal | None |
| Updates | Planned | Built-in |
| Scope | Full project structure | File generation |
| Languages | Multi with consistency | Any |

### Hexagon vs Framework Generators

| Aspect | Hexagon | Framework Generators |
|--------|---------|----------------------|
| Pattern | Hexagonal | Framework-specific |
| Portability | High | Tied to framework |
| Testability | Designed for | Varies |
| Flexibility | High | Limited |

## Getting Help

- **Documentation**: See `docs/` directory
- **Issues**: GitHub issue tracker
- **Discussions**: GitHub Discussions
- **Discord**: Phenotype community server

## Traceability

/// @trace HEXAGON-FAQ-001
/// @trace HEXAGON-SPEC-001
