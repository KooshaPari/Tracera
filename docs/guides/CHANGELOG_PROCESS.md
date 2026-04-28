# Changelog Process

Use this process for every PR or direct merge.

## Rules
- Add user-visible changes to `CHANGELOG.md` under `## [Unreleased]`.
- Group entries by Keep a Changelog categories (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`).
- Keep entries short and outcome-focused.
- Release cut: move `Unreleased` items into a new SemVer heading `## [X.Y.Z] - YYYY-MM-DD`.

## Workflow
1. Copy the template from `docs/reference/CHANGELOG_ENTRY_TEMPLATE.md`.
2. Fill only relevant categories.
3. Place entries under `## [Unreleased]`.
4. During release, create version heading and clear `Unreleased` back to placeholders.
