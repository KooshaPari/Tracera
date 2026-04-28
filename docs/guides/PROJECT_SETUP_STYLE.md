# Project Setup Style (Vercel/ai Inspired)

This repository follows a setup style optimized for fast feedback and reliable releases.

## Canonical Commands
- `task build`
- `task test`
- `task lint`
- `task quality`
- `task check` (full gate)
- `task release:prep` (release-readiness gate)

## Working Rules
- Keep changelog entries current under `## [Unreleased]`.
- Keep docs/examples aligned with behavior changes.
- Use scoped checks while iterating; run `task quality` before push.

## Release-Prep Gate
1. `task changelog:check`
2. `task check`
3. `task ci:quality`
