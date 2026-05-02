#!/usr/bin/env python3
"""Fallback quality schema validator (used when schemas/quality-governance.schema.json is absent)."""
import json
import logging
import pathlib
import sys

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

path = ".claude/quality.json"
data = json.load(pathlib.Path(path).open(encoding="utf-8"))
required = {
    "version", "project", "stacks", "coverage_threshold", "line_length",
    "test_pyramid", "traceability", "criticality_tier", "governance",
}
missing = sorted(required - set(data.keys()))
if missing:
    logger.error(f"quality schema validation failed: missing top-level keys: {','.join(missing)}")
    sys.exit(2)
gov = data.get("governance")
if not isinstance(gov, dict):
    logger.error("quality schema validation failed: governance must be an object")
    sys.exit(2)
for k in (
    "delivery_model", "probabilistic", "reliability", "rolling_wave",
    "assurance_case", "privacy_preserving", "playbooks",
    "artifact_quality", "debt_registry", "onchain", "formal",
    "toolchains", "health",
):
    if k not in gov:
        logger.error("quality schema validation failed: governance.%s missing", k)
        sys.exit(2)
logger.info("quality schema validation passed")
