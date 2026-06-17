---
description: Run repository quality gates (lint, format, type checks, risk checks).
---

# tracertm-quality

Run the official quality workflow before handing off changes.

## Command

```pwsh
cd E:/Dev/Tracera
task quality
```

## Includes

- Python lint + format
- static type check (`ty`)
- architecture/security checks configured in project tasks
- tests

If scope is local, run `ruff check .` and `ruff format --check .` directly first, then target tests.
