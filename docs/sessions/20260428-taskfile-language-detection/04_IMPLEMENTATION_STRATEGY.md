# Implementation Strategy

- Keep the Taskfile simple and manifest-driven.
- Use one shell block per task so command selection stays easy to audit.
- Avoid introducing repo-specific helper scripts unless the task matrix grows again.
