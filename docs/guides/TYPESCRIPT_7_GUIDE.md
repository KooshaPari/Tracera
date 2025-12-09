# TypeScript 7 Native Preview - Quick Reference

## What Changed?

TraceRTM now uses **TypeScript 7.0.0-dev.20251201.1** - a Rust-based native compiler (tsgo) that's significantly faster than the JavaScript-based TypeScript 5.x.

## Quick Commands

```bash
# Check TypeScript version
node node_modules/typescript/bin/tsgo.js --version
# Output: Version 7.0.0-dev.20251201.1

# Type check the project
bun run typecheck

# After installing dependencies
bun install
# The postinstall script automatically sets up tsc wrappers
```

## New TypeScript 7 Features

### Enabled in tsconfig.json
```json
{
  "compilerOptions": {
    "noUncheckedSideEffectImports": true
  }
}
```

This checks for side-effect imports that might not execute as expected.

## Binary Names

| Command | What It Does |
|---------|-------------|
| `tsgo` | The native TypeScript 7 compiler (primary) |
| `tsc` | Wrapper that calls `tsgo` (backward compatibility) |
| `tsserver` | Wrapper that calls `tsgo` (backward compatibility) |

## VSCode Integration

VSCode will automatically detect and use TypeScript 7 from `node_modules`. Check the status bar to confirm it shows "TypeScript 7.0.0-dev".

### If VSCode doesn't detect it:
1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "TypeScript: Select TypeScript Version"
3. Choose "Use Workspace Version"

## Performance Benefits

TypeScript 7 native preview is a **Rust-based compiler**, making it:
- Much faster at type checking
- More memory efficient
- Better suited for large codebases

## Troubleshooting

### "tsc: command not found" after install
Run the wrapper setup script:
```bash
bash scripts/setup-typescript-wrapper.sh
```

### VSCode showing old TypeScript version
1. Reload the VSCode window: `Cmd+Shift+P` → "Developer: Reload Window"
2. Or restart VSCode entirely

### Type errors after upgrade
The upgrade itself doesn't introduce new errors. Any errors shown are pre-existing issues that TypeScript is now catching more strictly with features like:
- `exactOptionalPropertyTypes: true`
- `noUncheckedSideEffectImports: true`
- `verbatimModuleSyntax: true`

## Package.json Configuration

All TypeScript dependencies now use the alias pattern:
```json
{
  "devDependencies": {
    "typescript": "npm:@typescript/native-preview@^7.0.0-dev"
  }
}
```

## Further Reading

- [TypeScript Go Repository](https://github.com/microsoft/typescript-go)
- [TypeScript 7 Release Notes](https://github.com/microsoft/typescript-go/releases)

---

For the complete upgrade summary, see: `.sessions/typescript-7-upgrade-summary.md`
