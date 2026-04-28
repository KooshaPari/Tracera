# Session Overview

- Goal: add a root `Taskfile.yml` with common `build`, `test`, `lint`, and `clean` tasks.
- Approach: detect repository language/tooling from manifests and only run the matching commands.
- Validation: inspect the repo tree, update the taskfile, and verify the new file exists in the clone.
