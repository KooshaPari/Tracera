# Frontend performance budget

CI checks the production web bundle after each frontend build. This is a
regression guard, not a replacement for browser profiling or field telemetry.

| Metric | Limit |
| --- | ---: |
| Combined JavaScript | 250 KiB |
| Combined CSS | 100 KiB |
| JavaScript + CSS | 400 KiB |
| gzip-compressed JavaScript + CSS | 125 KiB |

`npm run test:bundle` discovers hashed Vite assets under `dist`, and fails on
missing output, missing JS/CSS assets, or any limit breach. The limits leave
room for the current 154.8 KiB JS and 8.6 KiB CSS output while exposing major
dependency or styling regressions in review.
