# DOCKER - Container Configurations (DEPRECATED)

⚠️ **STATUS: MIGRATION IN PROGRESS**

This directory contains Docker-based container configurations that are being phased out in favor of **native services and containers** managed by the OS/platform.

## Files

- `docker-compose.yml` - Base production compose file
- `docker-compose.prod.yml` - Production environment overrides
- `docker-compose.dev.yml` - Development environment
- `docker-compose.local.yml` - Local development with live reloading
- `docker-compose.neo4j.yml` - Neo4j graph database configuration
- `Dockerfile` - Container image definition

## Migration Plan

### Phase 1: Native Database Services (IMMEDIATE)
- [ ] PostgreSQL → Replace with native PostgreSQL service
- [ ] Neo4j → Replace with native Neo4j service
- [ ] Redis → Replace with native Redis service

### Phase 2: Native Message Brokers (IMMEDIATE)
- [ ] NATS → Replace with native NATS service

### Phase 3: Native Web Services (IMMEDIATE)
- [ ] FastAPI → Run directly via Python (no container wrapper)
- [ ] Typer CLI → Run directly via Python (no container)
- [ ] Textual TUI → Run directly via Python (no container)

### Phase 4: Development Environment (IMMEDIATE)
- [ ] Development tools → Replace with native local development setup
- [ ] Testing → Run pytest directly without container
- [ ] Database migrations (Alembic) → Run directly

## Benefits of Native Services

✅ **Performance**: No container overhead
✅ **Debugging**: Direct access to processes, logs, debugger
✅ **Development**: Hot reload, instant feedback
✅ **Simplicity**: Fewer abstractions, easier troubleshooting
✅ **OS Integration**: Proper signal handling, resource management
✅ **Scripts**: Leverage Makefile, shell scripts directly

## Why We're Removing Docker

1. **Not needed for single-machine development** - We develop locally, not in containers
2. **Adds complexity** - Extra layer of abstraction during development
3. **Slows iteration** - Build times, container startup overhead
4. **Makes debugging harder** - Need to exec into containers
5. **Overkill for this project** - We're not running distributed systems

## What Remains

These files are kept for **reference only** in case Docker deployment is needed in the future. They are NOT part of the active development workflow.

## Related

- **Production Deployment**: When deploying to production, use platform-specific deployment files (e.g., systemd, supervisor, or cloud platform native services)
- **Development Setup**: See root Makefile and scripts/ directory for native development commands
- **Architecture**: See ARCHITECTURE/ directory for service topology

---

**Last Updated**: December 10, 2025
**Status**: Files consolidated, migration documentation created, native service implementation pending
