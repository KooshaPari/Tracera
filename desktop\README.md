# Tracera Electrobun Desktop Client (Step-1)

This is a **separate** desktop shell from the Tracera web app. It is intentionally small and focuses on:

- Electrobun runtime bootstrap in `src/index.ts`
- A self-contained local UI under `src/views/`
- Live service calls to Tracera:
  - `/coverage-matrix`
  - `/governance`
- Configurable service base URL from Settings in the UI
- Lightweight offline cache fallback (local browser storage) for failed network calls

## Build script

From `desktop/`:

```bash
bun install
bun run build
```

The build script is defined in `package.json` and uses the Electrobun CLI.

## Architecture notes

- Electrobun is the **STEP-1 shell** to unblock desktop delivery quickly.
- **END-STATE native plan:** WinUI-rs (Windows), SwiftUI (Apple), and Linux-native (ADR-defined approach) to replace this shell later.

## Repository layout

- `desktop/package.json` — Electrobun dependency and scripts
- `desktop/bunfig.toml` — Bun project config
- `desktop/src/index.ts` — Desktop entrypoint + window bootstrap
- `desktop/src/views/index.html` — UI shell
- `desktop/src/views/app.js` — settings + endpoint calls + offline cache

## Notes

- This scaffold intentionally avoids changing existing web-client code.
- It is intentionally minimal and currently does not execute validation/build in this draft.
