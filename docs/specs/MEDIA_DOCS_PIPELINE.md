# Reusable Agent-Media + Docs-Proof Pipeline

> Applies to all **BLOCK A** apps.

## 1. Purpose

This spec defines a reusable documentation and media production pipeline for BLOCK A apps.
The pipeline combines:

- **Automated media generation** (rendered and recorded artifacts)
- **Intent validation** via phenotype-journeys (base goal)
- **VitePress docs/wiki proof publishing**

Every artifact must serve as executable proof that the app works as intended.

## 2. Core Principle (Non-Negotiable)

Every media artifact (screenshot, gif, recording, video, trace) must be produced to validate the agent’s stated `INTENT` for the app, using phenotype-journeys as the acceptance check.

In practice:

- Generate artifact.
- Replay the same flow as the documented intent.
- Assert completion using phenotype-journeys.
- Only then embed artifact in docs/tutorials.

If intent validation fails, media is discarded and regenerated.

## 3. Media Stack (Reusable Across BLOCK A)

### 3.1 Blender (2D/3D Graphics)

- Use for hero assets, diagrams, 3D scene stills, animated UI concepts.
- Output formats:
  - `.png` / `.webp` for static docs assets
  - `.mp4` for short explainer clips
  - Source `.blend` retained for reproducibility
- Version rule:
  - One canonical render config per app feature.
  - Re-render only when source `.blend`, camera setup, lighting, or intended intent changes.

### 3.2 VHS (Terminal Recordings + GIF)

- Use for CLI/terminal workflows.
- Record canonical command journeys used in tutorials.
- Outputs:
  - `.gif` for quick visual embed
  - `.mp4`/`.webm` for high quality proof artifacts
- Every recording is linked to the command-level phenotype-journey that demonstrates the same intent.

### 3.3 Playwright (Web Screenshots, Video, Traces)

- Use for browser/UI web apps.
- For each documented flow:
  - capture screenshot(s) for each major state
  - capture failure-free demo video
  - capture trace for debugability and reviewability
- Outputs:
  - `.png` and `.jpg` for stills
  - `.webm` (or `.mp4` depending infra) for recorded runs
  - Playwright trace bundle (`.zip`) for agent-side QA

### 3.4 Desktop Recorder (TBD)

- Reserved for native desktop apps when no browser/terminal equivalent exists.
- Must support:
  - timeline recording
  - still export
  - optional audio sync
- Until standardized, each team may use an approved internal recorder, but the contract remains:
  - deterministic session launch
  - fixed viewport and quality profile
  - replayable evidence bundle

### 3.5 Remotion (Rich Video Editing)

- Use to compose final tutorial videos from raw captures.
- Compose clips from Playwright/VHS/desktop outputs.
- Normalize branding, captions, and timing.
- Output final publishable artifacts for landing pages and deeper docs.
- Remotion renders are also proof artifacts if they encode validated steps.

## 4. Validation Contract: Phenotype-Journeys as Proof Gate

For every app and every tutorial page:

1. Document intent in clear goal language.
2. Derive one or more phenotype-journeys representing the user action path.
3. Execute journey while capturing media.
4. Evaluate journey outcome against expected state changes.
5. Only mark media as `ready` when intent assertion passes.

### 4.1 Validation Data Contract

- `intent`: human-level goal sentence.
- `journey_id`: stable journey identifier.
- `entry_state`: baseline assumptions.
- `actions`: ordered steps with tool outputs.
- `assertions`: success criteria derived from goal.
- `media_links`: artifact paths referenced in docs.
- `validated_at`: timestamp + tool/version metadata.

### 4.2 Failure Modes

- **Mismatch intent** → regenerate media with corrected flow.
- **Flaky capture** → lock deterministic environment settings and rerun 2+ times.
- **Missing steps** → extend journey and retake captures.

## 5. Docs/Wiki Workflow (VitePress)

Use this sequence for every tutorial page, changelog entry, or feature page that implies runtime behavior:

### 5.1 Step 1: Add Skeleton/Stub Placeholders

- Insert placeholders where media will be embedded:
  - `gfx`
  - `screenshots`
  - `recordings`
  - `gif`
- Include explicit “intent being demonstrated” labels in the markdown.

Example placeholder fields:

- `<!-- MEDIA_PLACEHOLDER: gfx intent=<intent-id> -->`
- `<!-- MEDIA_PLACEHOLDER: screenshot intent=<intent-id> -->`
- `<!-- MEDIA_PLACEHOLDER: recording intent=<intent-id> -->`

### 5.2 Step 2: Fill All Wiki/Docs Pages

- Replace placeholders with finalized links/components.
- Include short context section:
  - _What is demonstrated_
  - _Expected result_
  - _Validation signal (journey id / assertion summary)_

### 5.3 Step 3: Embed Agent-Generated Media as Tutorials

- Embed only artifacts marked `validated`.
- Media must show the app working as a tutorial, not a static showcase.
- Each embed must include nearby text mapping to the exact journey and assertion.

### 5.4 Docs-Wise VitePress Conventions

- Store media in docs-asset friendly paths (see section 6).
- Use deterministic, stable filenames.
- Prefer lazy-loaded media for heavy assets.
- Keep markdown text concise and goal-oriented.

## 6. Per-App Checklist + Artifact Locations

Use this checklist for each BLOCK A app.

### 6.1 Setup

- [ ] Define `APP_NAME` and base `INTENT` statements.
- [ ] Assign media owner and validator owner per media type.
- [ ] Select primary recorder path (Playwright/VHS/Blender/Desktop/Remotion).

### 6.2 Capture Readiness

- [ ] Verify reproducible environment.
- [ ] Pin tool versions and config.
- [ ] Prepare deterministic input fixtures where needed.

### 6.3 Capture & Validate

- [ ] Generate skeleton placeholders in target docs page.
- [ ] Record each journey in staging.
- [ ] Validate intent with phenotype-journeys.
- [ ] Attach assertion artifacts to media metadata.

### 6.4 Publish to Docs

- [ ] Replace placeholders with final media embeds.
- [ ] Add one-sentence validation note per asset.
- [ ] Run docs build checks if applicable.
- [ ] Merge only when every embed is verified with passing intent validation.

### 6.5 Artifact Inventory and Paths

Store artifacts for each app in consistent locations:

- `docs/public/media/<app-slug>/gfx/`
- `docs/public/media/<app-slug>/screenshots/`
- `docs/public/media/<app-slug>/recordings/`
- `docs/public/media/<app-slug>/traces/`
- `docs/public/media/<app-slug>/videos/`
- `docs/public/media/<app-slug>/proofs/`
- `docs/specs/media/<app-slug>/media-log.md`

Optional metadata and audit trail:

- `docs/specs/media/<app-slug>/journeys/<journey-id>.md`
- `docs/specs/media/<app-slug>/validation/<date>-<run-id>.json`

## 7. Reusability Rules

- Do not invent one-off folder structures per app.
- Do not publish unvalidated media.
- Do not replace placeholders with placeholder-like fake media.
- Do not mix tutorial evidence with marketing-only renders unless explicitly tagged `marketing`.
- Keep this pipeline identical for all BLOCK A apps; only payload details vary.

## 8. Acceptance Criteria

A BLOCK A app is compliant when all above steps are met and:

- every intent has at least one validated artifact;
- every docs page with functional claims includes media plus a validation note;
- every `media` path is versioned and discoverable under VitePress paths.

---

## 9. Delivery Pattern for This Spec

This spec is authored for content-safe automation and can be copied unchanged across BLOCK A repos with:

- app slug replacement,
- tool substitutions in Section 3.4,
- and app-specific `INTENT` statements.
