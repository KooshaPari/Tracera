# Ralph Controller

This directory is only an orchestration controller for the Phenotype shelf.

Operational rules:
- Target work lives under `/Users/kooshapari/CodeProjects/Phenotype/repos`, not in this controller.
- Do not treat the shelf root as a single project.
- Before mutating a child project, verify its own `.git`, remote, branch, and local dirty state.
- Prefer GitHub PR merges, issue triage, and narrow repo-specific work over broad parent-repo commits.
- Preserve all existing user and agent edits. Never reset or revert unrelated files.
- Run with `--no-commit`; do not commit controller state unless explicitly asked.
- Stop if `/Users/kooshapari/CodeProjects/Phenotype/repos/.ralph-controller/STOP` exists.

