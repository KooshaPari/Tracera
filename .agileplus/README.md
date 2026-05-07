# Tracera ↔ AgilePlus

Tracera does not own an AgilePlus runtime. The canonical AgilePlus instance lives at:

- Repo: `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`
- Specs: `AgilePlus/kitty-specs/<feature-id>/`
- Runtime DB: `AgilePlus/.agileplus/agileplus.db` (local; not portable)

## Tracera-bound AgilePlus specs

Use this directory to record which AgilePlus specs are realized in Tracera.
Add a single-line pointer per spec under `specs/`:

```
specs/<feature-id>.md   # one line: link to AgilePlus/kitty-specs/<feature-id>/spec.md
```

Do not copy the AgilePlus database here — it is local-runtime state.

## Conventions

- All Tracera work that maps to an AgilePlus spec MUST reference its ID in the PR description (e.g. `Refs: FR-CORE-014`, `AgilePlus 003-agileplus-platform-completion`).
- The GitHub Issue templates link to AgilePlus IDs in the "AgilePlus Linkage" section.
