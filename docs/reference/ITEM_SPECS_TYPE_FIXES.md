# item_specs and related type-check fixes

Reference for fixing `missing-argument`, `invalid-argument-type`, `unknown-argument`, and related errors in `item_specs.py`, MCP query_optimizer, tracertm, token_manager, auth_config_db, and bmm_workflows.

**Current workspace:** All these fixes are already applied; `ty check` passes. Use this doc if you're on a branch/copy that still has the old code.

---

## 1. item_specs.py

### VersionChainResponse
- **Required:** `spec_id`, `chain_valid`, `generated_at`.
- **Rename:** `is_valid` → `chain_valid`.
- **Type:** `chain_head` must be `str` (use `(chain_index.chain_head_id or "") if chain_index else ""`).
- **Entries:** Build `entries` as `list[VersionChainEntry]` (import `VersionChainEntry`); each entry: `version_hash`, `version_number`, `content_hash`, `previous_hash`, `created_at`, `created_by`, `change_summary`.

### MerkleProofResponse
- **Schema fields:** `spec_id`, `root`, `proof` (list), `leaf_index`, `leaf_hash`, `verified`, `verification_path`, `tree_size`, `generated_at`.
- **Map:** `root_hash` → `root`, `proof_path` → `proof` and `verification_path`, remove `item_id`, `baseline_id`, `message`. Always pass `spec_id`, `root`, `proof`, `leaf_index`, `leaf_hash`, `verified`, `verification_path`, `tree_size`, `algorithm="sha256"`, `generated_at`.

### ContentAddressResponse
- **Schema fields:** `spec_id`, `content_hash`, `content_cid`, `created_at`, `last_modified_at`.
- **Map:** `cid` → `content_hash` and `content_cid`; do not use `algorithm`, `size_bytes`, `content_type`.

### Optional request bodies
- Use `Body(None)` and union type: `request: AnalyzeFlakinessRequest | None = Body(None)` (same for AnalyzeODCRequest, AnalyzeCVSSRequest). Do not use `= None` alone.

### FlakinessAnalysisResponse
- **Required:** `spec_id`, `probability`, `entropy`, `analyzed_at`.
- **Map:** `flakiness_score` → `probability`, `entropy_score` → `entropy`; use schema fields: `pattern`, `pattern_confidence`, `quarantine_recommended`, `recent_runs`, `flaky_runs`, `pass_rate`, etc.

### ODCClassificationResponse
- **Required:** `spec_id`, `defect_type`, `trigger`, `impact`, `confidence`, `defect_type_confidence`, `trigger_confidence`, `impact_confidence`, `analyzed_at`.
- Remove `qualifier`, `age`, `source` (not in schema). Use enum values for `defect_type`, `trigger`, `impact`.

### CVSSScoreResponse
- **Required:** `spec_id`, `base_score`, `severity` (use `CVSSSeverity.NONE` enum), `vector`, `breakdown` (`CVSSBreakdown`), `analyzed_at`.
- **Map:** `vector_string` → `vector`; put granular metrics in `breakdown=CVSSBreakdown(...)`.

### analyze_test_flakiness / classify_defect
- Ensure `run_history` is `list[dict[str, Any]]` and `window_size` is `int` (e.g. `run_history_list`, `window_size_int`).
- For `classify_defect`, pass `description: str`, `trigger_context: str | None`, `impact_description: str | None`; use `cast(str | None, ...)` if needed.

### analyze_change_impact
- Pass `adjacency=cast(dict[str, list[str]], adjacency)` and `item_metadata=cast(dict[str, dict[str, Any]] | None, item_metadata)`.

### RICEScore
- Use `impact=int(rice_score.impact)` so type is `int`.

### analyze_coverage_gaps
- Pass `safety_level=cast(ServiceSafetyLevel | None, safety)` where `safety` is built from `request.safety_level` with `isinstance(..., (ServiceSafetyLevel, type(None)))`.

---

## 2. query_optimizer.py
- Replace `Item.source_links`, `Item.target_links`, `Link.source_item`, `Link.target_item`, `Project.items`, `Item.parent`, `Item.children` with `getattr(Item, "source_links")`, etc., so the type checker does not require these attributes on the model classes.

---

## 3. tracertm.py (MCP resources)
- **Project** model has no `deleted_at`. Remove `.filter(Project.deleted_at.is_(None))` or use a conditional only if your Project model actually has `deleted_at`.

---

## 4. token_manager.py
- Use `(self.scopes or [])` so `in` is not used with `None`: `return scope in (self.scopes or [])` and `return all(s in (self.scopes or []) for s in scopes)`.

---

## 5. auth_config_db.py
- Import: `from typing import Any, cast`.
- Use `config_dict: dict[str, Any] = cast(dict[str, Any], raw) if isinstance(raw, dict) else {}`.

---

## 6. bmm_workflows.py
- Use a narrowed dict for `.get()`: `_data = name_result.data if isinstance(name_result.data, dict) else {}` then `project_name = _data.get("value", "MyProject") if isinstance(name_result, AcceptedElicitation) else "MyProject"`.
