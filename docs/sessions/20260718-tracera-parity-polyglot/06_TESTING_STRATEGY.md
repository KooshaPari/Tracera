# Testing strategy

Validated in this session:

```text
cd frontend && npm run test:unit && npm run build && npm run smoke:parity \
  && npm run smoke:post && npm run typecheck
cd sidecar/go && go test ./... && go build ./cmd/tracera-sidecar
```

Future integration tests should exercise the sidecar against a disposable
Tracera instance, verify disabled-mode behavior, and enforce no writes unless a
separate reviewed contract explicitly authorizes them.
