---
description: Frontend loop command pack for React/TypeScript stack.
---

# tracertm-frontend

Frontend build/test helper for Tracera web UI.

## Command

```pwsh
cd E:/Dev/Tracera/frontend
bun install      # once per environment
bun run dev
bun run build
bun run lint
bun run typecheck
bun test
```

- `bun run dev`: local web loop
- `bun run build`: production artifact check
- `bun run lint` + `bun run typecheck`: gate before UI changes
- `bun test`: frontend test suite
