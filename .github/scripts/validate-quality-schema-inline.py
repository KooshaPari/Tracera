#!/usr/bin/env python3
"""Fallback quality schema validator (used when schemas/quality-governance.schema.json is absent)."""
import json
import sys

path = ".claude/quality.json"
data = json.load(open(path, "r", encoding="utf-8"))
required = {
    "version", "project", "stacks", "coverage_threshold", "line_length",
    "test_pyramid", "traceability", "criticality_tier", "governance",
}
missing = sorted(required - set(data.keys()))
if missing:
    print(f"quality schema validation failed: missing top-level keys: {','.join(missing)}")
    sys.exit(2)
gov = data.get("governance")
if not isinstance(gov, dict):
    print("quality schema validation failed: governance must be an object")
    sys.exit(2)
for k in (
    "delivery_model", "probabilistic", "reliability", "rolling_wave",
    "assurance_case", "privacy_preserving", "playbooks",
    "artifact_quality", "debt_registry", "onchain", "formal",
    "toolchains", "health",
):
    if k not in gov:
        print(f"quality schema validation failed: governance.{k} missing")
        sys.exit(2)
print("quality schema validation passed")
