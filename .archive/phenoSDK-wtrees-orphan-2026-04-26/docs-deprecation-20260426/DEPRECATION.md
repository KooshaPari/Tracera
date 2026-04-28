# phenoSDK Deprecation Notice

## Status: ARCHIVED (2026-04-05)

**phenoSDK has been decomposed.** All 305,000+ lines of code have been extracted to specialized repositories. This repository now serves as **documentation and historical reference only**.

---

## What Moved & Where

### Authentication & Authorization

**If you were using phenoSDK auth modules:**

All auth code has been consolidated into **AuthKit** (canonical authentication SDK):

- **Repository:** `/repos/AuthKit`
- **Protocols:** OAuth 2.0, OIDC, SAML 2.0, WebAuthn/Passkeys
- **Languages:** Rust, TypeScript/Node.js, Python, Go
- **Usage:** `cargo add authkit` | `npm install @authkit/sdk` | `pip install authkit`

**Migration:** See `docs/migrations/phenoSDK_to_AuthKit.md` for detailed consolidation plan.

### All Other Modules

phenoSDK's 48 modules were distributed across two workspace packages:

| Workspace | Packages | Purpose |
|-----------|----------|---------|
| **PhenoLang** | 31 packages | Language-specific utilities, adapters, patterns |
| **PhenoProc** | 17 packages | Process orchestration, CI/CD, DevOps |

See `README-ARCHIVED.md` for the full mapping.

---

## Do I Need to Migrate?

**Check:** Does your code import from phenoSDK?

```bash
# Search your codebase
grep -r "phenoSDK\|from phenoSDK" . --include="*.py" --include="*.rs" --include="*.go" --include="*.ts"
```

**If you find imports:**
1. Identify which module (auth, cli, config, etc.)
2. Find its new location (see README-ARCHIVED.md)
3. Update imports and migrate to the new repo's API

**If you find nothing:**
- No action needed
- Your codebase never depended on phenoSDK
- Proceed as normal

---

## How to Find Decomposed Code

### Full Archive (Read-Only Historical Reference)

Complete phenoSDK pre-decomposition code (2,052 files, 230 MB):

```bash
/repos/archive/phenoSDK-deprecated-2026-04-05/
```

Use this for:
- Auditing auth patterns from Q1 2026
- Understanding design decisions from git history
- Reference implementations (adapters, DI patterns)

### Active Development

Use the package-specific repos for current work:
- **AuthKit** → for all new auth implementation
- **PhenoLang** → for patterns/utilities from old phenoSDK
- **PhenoProc** → for orchestration/CI/CD from old phenoSDK

---

## Questions?

- **Migration path:** `docs/migrations/phenoSDK_to_AuthKit.md`
- **Archive manifest:** `/repos/archive/phenoSDK-deprecated-2026-04-05/ARCHIVE_MANIFEST.md`
- **Original architecture docs:** `docs/adr/`, `docs/research/`

---

**Archived:** 2026-04-05  
**Documentation migrated to:** AuthKit, PhenoLang, PhenoProc  
**This repo purpose:** Git history + design reference
