# Session Overview

- Goal: make the repo Taskfile detect the language stack from root manifests and expose common tasks.
- Scope: `Taskfile.yml` plus a minimal session record.
- Success: `build`, `test`, `lint`, and `clean` run the right commands when the matching manifests exist.
