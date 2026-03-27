#!/usr/bin/env python3
"""Fallback smart contract gate (used when scripts/qa-smart-contract-gate.py is absent)."""
import json
import os
import re
import pathlib
import datetime
import sys

root = pathlib.Path(".")
q = root / ".claude/quality.json"
fr = "FUNCTIONAL_REQUIREMENTS.md"
if q.exists():
    try:
        fr = json.loads(q.read_text(encoding="utf-8")).get("traceability", {}).get("fr_source", fr)
    except Exception:
        pass
fr_path = root / fr
out = root / ".claude/verification/smart-contract-gate.json"
out.parent.mkdir(parents=True, exist_ok=True)
if not fr_path.exists():
    payload = {
        "generated_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "not_applicable",
        "pass": True,
        "reason": f"missing_fr_source:{fr}",
        "fr_source": fr,
        "total_frs": 0,
        "covered_frs": 0,
        "fr_coverage_percent": 0.0,
        "orphan_frs": [],
        "orphan_tests": [],
    }
else:
    text = fr_path.read_text(encoding="utf-8", errors="ignore")
    fr_ids = sorted(set(re.findall(r"\bFR-[A-Z]+-[0-9]+\b", text)))
    payload = {
        "generated_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "advisory",
        "pass": True,
        "reason": "fallback_advisory",
        "fr_source": fr,
        "total_frs": len(fr_ids),
        "covered_frs": 0,
        "fr_coverage_percent": 0.0,
        "orphan_frs": fr_ids,
        "orphan_tests": [],
    }
out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print("smart-contract fallback report generated:", out)
