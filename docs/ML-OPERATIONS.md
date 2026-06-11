# ML Operations

This guide defines the operating model for Tracera's machine-learning-adjacent
traceability features: requirement mining, agreement scoring, semantic matching,
quality analytics, and future embedding/VLM scorers. The current implementation
is intentionally hybrid: deterministic heuristics are production paths, while
embedding and VLM strategies are pluggable scorer ports.

## Operating Principles

- Keep trace decisions explainable. Every automated link or verdict must carry a
  normalized `confidence` in `[0.0, 1.0]` and a human-readable `rationale`.
- Prefer deterministic baselines before ML. Heuristic miners and lexical scorers
  are the control group for every learned model.
- Treat models as replaceable strategy implementations behind `ScorerPort`; API,
  graph, and persistence callers should not depend on model-specific packages.
- Promote only measured improvements. No scorer becomes default without offline
  evaluation, regression checks, and rollback instructions.

## Data Pipeline

Primary inputs:

- Requirements and specs from `docs/requirements/`, imported documents, and API
  payloads.
- Trace artifacts: code references, tests, evidence captures, risks, rationales,
  and graph nodes.
- Existing curated links from the `links` table, including `confidence` and
  `rationale`, used as labels and review evidence.
- Generated candidates from `src/tracertm/services/requirement_miner.py`.

Pipeline stages:

1. Ingest raw text or file paths through the requirement miner or API ingestion
   routes.
2. Normalize text, source references, artifact kinds, project IDs, and explicit
   FR/NFR/REQ tags.
3. Generate candidate requirements or links with source provenance.
4. Score each candidate with the active strategy: heuristic modal/tag matching,
   lexical similarity, embedding similarity, visual evidence matching, or VLM
   verdict.
5. Persist only candidates that meet the configured threshold; retain rejected
   examples for evaluation sampling when possible.
6. Project accepted links into the trace graph for impact, coverage, and quality
   analytics.

Operational controls:

- Never train or evaluate on unlabeled production data without preserving source
  provenance and project boundaries.
- Keep human-curated links separate from model-generated links in metadata.
- Snapshot evaluation datasets before scorer changes so old and new strategies
  can be compared on identical inputs.

## Training and Calibration

Tracera does not currently require online model training. Scorer work should be
handled as offline calibration:

- Build labeled datasets from reviewed requirement-artifact pairs and rejected
  false positives.
- Include negative pairs from unrelated projects, stale links, and conflict or
  duplicate detections.
- Calibrate confidence thresholds per scorer. Heuristic miner defaults are:
  explicit tags `0.95`, `shall/must` `0.90`, `should/will` `0.70`,
  TODO/SPEC markers `0.60`, and `may/can` `0.50`.
- Record scorer version, model name, embedding dimensions, threshold, dataset
  snapshot, and evaluation output for every candidate promotion.

For optional learned scorers, prefer dependencies already declared under
`pyproject.toml` extras such as `ml` (`sentence-transformers`, `numpy`, `torch`)
and keep imports lazy so non-ML installs still run.

## Evaluation

Evaluate every scorer against a fixed validation snapshot before deployment.

Required metrics:

- Precision, recall, and F1 for accepted trace links.
- False-positive rate for links above the production threshold.
- Confidence calibration by bucket, especially around review thresholds.
- Coverage lift: additional requirements with valid test/code/evidence links.
- Latency and memory per scored pair or batch.

Acceptance gates:

- New default scorer must beat the deterministic baseline on precision or F1
  without increasing high-confidence false positives.
- Link confidence must remain within database and application constraints.
- Evaluation artifacts must include rationale samples for true positives, false
  positives, and false negatives.
- API and graph consumers must receive the same response schema after the change.

Recommended checks:

```bash
uv run pytest tests/unit/services/test_requirement_miner.py
uv run pytest tests/unit -q
cargo test
npm test
```

Use narrower commands when only documentation or isolated scoring behavior
changes, but record skipped suites and why.

## Deployment

Deploy scorer changes as configuration or strategy swaps, not caller rewrites.

1. Ship the scorer behind `ScorerPort` with lazy optional dependencies.
2. Run offline evaluation and targeted unit tests.
3. Enable in staging with shadow scoring: persist current production decisions
   while logging new scorer outputs separately.
4. Review drift, false positives, and latency for at least one representative
   import or mining run.
5. Promote by changing the configured default scorer and threshold.
6. Keep rollback simple: restore the previous scorer name and threshold.

Production monitoring:

- Candidate volume by project and artifact kind.
- Accepted/rejected ratio by scorer and threshold.
- High-confidence false-positive reports from review workflows.
- Scoring latency, batch size, memory, and optional model load failures.
- Coverage and impact-score changes after accepted links are projected.

## Ownership

ML operations changes affect trace integrity. Treat scorer defaults, thresholds,
and model dependencies as product behavior changes: document the dataset,
evaluation result, rollout plan, and rollback path in the relevant session docs
or PR before promotion.
