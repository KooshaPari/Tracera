---
description: Run Python/Go/frontend tests using the project matrix.
---

# tracertm-test

Run the project test matrix at the scope requested by the user.

## Command

```pwsh
cd E:/Dev/Tracera
task test
# or
pytest
```

## Scoped variants

- Unit only: `pytest -m unit`
- Integration only: `pytest -m integration`
- Go: `go test ./...`
- Frontend: `cd frontend && bun test`

Start with `task test` when no explicit scope is given.
