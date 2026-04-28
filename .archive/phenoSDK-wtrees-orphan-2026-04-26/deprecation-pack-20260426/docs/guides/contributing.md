# Contributor Workflow

This guide supplements the root `CONTRIBUTING.md` file with practical steps for working across Pheno-SDK’s many kits.

## Before You Start
- Pick an issue or create one describing the change you plan to make.
- Identify which kits are affected and skim their manuals in `docs/kits/`.
- Set up your environment following [Getting Started](getting-started.md).

## Development Flow
1. **Create a Branch** – `git checkout -b feature/<short-description>`.
2. **Update Documentation First** – Adjust the relevant concept or kit manual as you shape the API. Writing docs early keeps intent clear.
3. **Implement Changes** – Keep commits scoped per kit; large refactors should be split into reviewable pieces.
4. **Add Tests** – Unit tests with in-memory adapters, plus integration or contract tests when adapters/providers are touched.
5. **Run the Quality Suite**:
   - `pytest` (or kit-specific invocation)
   - `ruff check .` or configured linter
   - `mypy` / `pyright`
   - `build-analyzer-kit` if dependencies or cross-kit APIs changed
   - `python scripts/checks/verify_pheno_docs.py --update` whenever public capabilities or optional extras change (CI enforces the fingerprint)
   - Optional: `./pheno schema check` to confirm Supabase schema drift; `./pheno deploy --target vercel` for deployment readiness; `./pheno embeddings --entity-types …` for backfill validation
6. **Update Changelog** – Each kit manual has a *Change Log* section. Add a short entry.
7. **Submit Pull Request** – Include:
   - Summary of changes
   - Impacted kits and docs
   - Testing evidence (commands + outcome)
   - Migration notes if the change is breaking

## Review Expectations
- Reviewers prioritize correctness, backwards compatibility, and documentation updates.
- Expect feedback on naming, dependency injection patterns, and observability coverage.
- Respond to comments within two business days; keep discussions in the PR thread.

## After Merge
- Verify the change appears in nightly builds or staging deployments.
- Update any runbooks affected by the change.
- Ensure `llms.txt` remains synchronized for AI assistant support.

## Becoming a Maintainer
- Consistently contribute high-quality changes across multiple kits.
- Review PRs and help triage issues.
- Participate in release planning sessions.
- Maintain at least one kit end-to-end (code, docs, CI, releases).

## Community Standards
- Follow the project’s Code of Conduct (TBD: add `CODE_OF_CONDUCT.md`).
- Respect release schedules and backwards compatibility guarantees.
- Document every public API; undocumented APIs are considered internal.

For more detail on coding conventions, consult the module-level guides in `docs/kits/` and the lint/type configs present in each package.
