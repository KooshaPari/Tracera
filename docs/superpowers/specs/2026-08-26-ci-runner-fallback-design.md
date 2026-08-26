# CI Runner Fallback Design

## Goal

Keep Tracera CI runnable when the external Blacksmith runner pool is unavailable, while allowing operators to opt into Blacksmith for manual or reusable workflow executions.

## Scope

- Change `.github/workflows/ci.yml` and `.github/workflows/infisical.yml` only.
- Add a static contract test that verifies the default runner and override wiring.
- Preserve job names, dependency graph, permissions, caching, and branch-protection contexts.
- Do not change application/runtime code or deployment-secret policy.

## Design

`ci.yml` will expose a `workflow_dispatch` input named `runner` with choices `ubuntu-latest` and the two existing Blacksmith labels. Language jobs will select `${{ inputs.runner || 'ubuntu-latest' }}` directly (the `runs-on` context does not permit the `env` context), so ordinary CI cannot remain indefinitely queued when Blacksmith is down while operators can explicitly request Blacksmith.

`infisical.yml` will expose the same manual/reusable `runner` input and use `${{ inputs.runner || 'ubuntu-latest' }}`, defaulting to `ubuntu-latest` for push and reusable calls. Pull requests skip secret synchronization because repository secrets are intentionally unavailable to forked/untrusted PRs; secret values and the five-minute timeout remain unchanged for events that execute the job.

The contract test will parse both workflow files and assert: (1) the supported input choices are present, (2) the default is `ubuntu-latest`, (3) every former Blacksmith language job uses the selector, and (4) no hard-coded Blacksmith runner remains in either workflow job definition. It will not contact GitHub or Infisical.

## Failure handling

If an operator selects Blacksmith while no Blacksmith runner is registered, that run may queue; this is an explicit choice and is visible in the workflow input. Default push/PR runs remain runnable on GitHub-hosted infrastructure. Vercel credentials and Scorecard failures remain independent gates.

## Validation

- Run the new contract test locally.
- Run `actionlint` against both workflows.
- Parse YAML with the repository's existing tooling if available.
- Run the repository's focused workflow-contract tests.
- Inspect the final diff for unchanged job dependencies and permissions.
