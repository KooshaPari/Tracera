#!/usr/bin/env python3
"""Bounded SFD reference checks. Not an evaluator, authority service or product certifier."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

def load(path: Path) -> dict[str, Any]:
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"Duplicate JSON key: {key}")
            out[key] = value
        return out
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"Non-finite JSON: {x}")))

def timestamp(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("Timestamp must include an offset")
    return dt

def unique_ids(rows: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    result = {r["id"]: r for r in rows}
    if len(result) != len(rows):
        raise ValueError(f"Duplicate {label} ID")
    return result

def validate(doc: dict[str, Any]) -> None:
    schema = load(ROOT / "schemas/snapshot.schema.json")
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(doc)
    if doc["snapshot_id"] == doc["previous_snapshot_id"]:
        raise ValueError("A snapshot cannot be its own predecessor")
    as_of = timestamp(doc["as_of"])
    evidence = unique_ids(doc["evidence"], "evidence")
    unique_ids(doc["leaves"], "leaf")
    for ev in evidence.values():
        if timestamp(ev["observed_at"]) > as_of:
            raise ValueError("Future evidence cannot support this snapshot")
        if ev["valid_until"] and timestamp(ev["valid_until"]) < timestamp(ev["observed_at"]):
            raise ValueError("Evidence expires before it was observed")
        if doc["record_class"] == "ILLUSTRATIVE" and ev["kind"] != "ILLUSTRATIVE_SCENARIO":
            raise ValueError("Illustrative records cannot contain claimed executed-product evidence")
    for leaf in doc["leaves"]:
        if not math.isfinite(leaf["weight"]) or leaf["weight"] <= 0:
            raise ValueError("Leaf weight must be finite and positive")
        if any(ref not in evidence for ref in leaf["evidence_ids"]):
            raise ValueError("Missing evidence reference")
        if leaf["applicability"] == "EXCLUDED" and not leaf["exclusion_authority"]:
            raise ValueError("Exclusion requires authority and rationale")
        if doc["record_class"] == "ILLUSTRATIVE" and leaf["review"] != "PROPOSED":
            raise ValueError("Illustrative observations must remain proposed")
        if doc["record_class"] == "OPERATIONAL" and leaf["status"] in {"PASS", "FAIL"} and leaf["review"] == "ACCEPTED":
            if not leaf["evidence_ids"]:
                raise ValueError("Accepted operational result lacks evidence")
            for ref in leaf["evidence_ids"]:
                ev = evidence[ref]
                if ev["subject_id"] != doc["subject_id"]:
                    raise ValueError("Evidence subject does not match the snapshot")
                if ev["kind"] != "EXECUTED_PRODUCT" or not ev["sha256"] or not ev["locator"]:
                    raise ValueError("Accepted operational results need bound executed-product evidence")


def admitted(doc: dict[str, Any], leaf: dict[str, Any], scenario: bool) -> bool:
    if scenario:
        return leaf["status"] in {"PASS", "FAIL"}
    if leaf["review"] != "ACCEPTED" or not leaf["evidence_ids"]:
        return False
    evidence = {e["id"]: e for e in doc["evidence"]}
    for ref in leaf["evidence_ids"]:
        ev = evidence[ref]
        if ev["kind"] != "EXECUTED_PRODUCT" or ev["subject_id"] != doc["subject_id"] or not ev["sha256"]:
            return False
        if ev["valid_until"] and timestamp(ev["valid_until"]) <= timestamp(doc["as_of"]):
            return False
    return leaf["status"] in {"PASS", "FAIL"}


def fractions(p: float, f: float, u: float) -> dict[str, float | None]:
    return {"assessed_pass_rate": p/(p+f) if p+f else None,
            "assessment_coverage": (p+f)/(p+f+u) if p+f+u else None,
            "verified_satisfaction": p/(p+f+u) if p+f+u else None}


def rollup(doc: dict[str, Any]) -> dict[str, Any]:
    validate(doc)
    if doc["record_class"] == "TEMPLATE":
        return {"record_class": "TEMPLATE", "operational": None, "scenario": None, "gate_status": "UNASSESSED"}
    scenario = doc["record_class"] == "ILLUSTRATIVE"
    axes = {}
    for axis in sorted({l["axis"] for l in doc["leaves"]}):
        p = f = u = unresolved = excluded = 0.0
        for leaf in [l for l in doc["leaves"] if l["axis"] == axis]:
            weight = leaf["weight"]
            if leaf["applicability"] == "EXCLUDED":
                excluded += weight
            elif leaf["applicability"] == "UNRESOLVED":
                unresolved += weight
            elif admitted(doc, leaf, scenario) and leaf["status"] == "PASS":
                p += weight
            elif admitted(doc, leaf, scenario) and leaf["status"] == "FAIL":
                f += weight
            else:
                u += weight
        axes[axis] = {"pass": p, "fail": f, "unknown": u, "applicable": p+f+u,
                      "unresolved_applicability": unresolved, "excluded": excluded, **fractions(p, f, u)}
    critical = [l for l in doc["leaves"] if l["critical"] and l["applicability"] != "EXCLUDED"]
    clear = bool(critical) and all(l["applicability"] == "APPLICABLE" and l["status"] == "PASS" and admitted(doc,l,scenario) for l in critical)
    gate = "CLEAR" if clear else "BLOCKED" if critical else "UNASSESSED"
    return {"record_class": doc["record_class"], "operational": None if scenario else axes,
            "scenario": axes if scenario else None, "gate_status": ("SCENARIO_" if scenario else "")+gate}


def delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    old, new = rollup(before), rollup(after)
    for key in ("product_id", "baseline_id", "record_class"):
        if before[key] != after[key]:
            raise ValueError(f"Unlike {key}; use an explicit scope/identity restatement, not an unqualified delta")
    if after["previous_snapshot_id"] != before["snapshot_id"]:
        raise ValueError("Predecessor mismatch")
    if timestamp(after["as_of"]) <= timestamp(before["as_of"]):
        raise ValueError("Delta time must move forward")
    def membership(d):
        return sorted((l["id"],l["axis"],l["weight"],l["applicability"],l["critical"]) for l in d["leaves"])
    if membership(before) != membership(after):
        raise ValueError("Membership/weight/applicability changed without a new baseline")
    kind = "scenario" if before["record_class"] == "ILLUSTRATIVE" else "operational"
    old_axes, new_axes = old[kind], new[kind]
    if old_axes is None or new_axes is None:
        raise ValueError("Template snapshots have no scored delta")
    result = {"kind": kind, "baseline_id": before["baseline_id"], "axes": {}, "gate_status": new["gate_status"]}
    for axis in old_axes:
        a,b = old_axes[axis]["verified_satisfaction"],new_axes[axis]["verified_satisfaction"]
        result["axes"][axis] = {"before": a, "after": b, "percentage_points": (b-a)*100 if a is not None and b is not None else None}
    prev = {l["id"]:l for l in before["leaves"]}
    result["changed_leaf_ids"] = [l["id"] for l in after["leaves"] if l != prev[l["id"]]]
    return result


def deduplicate_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = {}
    for event in events:
        key = event["id"]
        if key in out and out[key] != event:
            raise ValueError("Conflicting payload for one event ID")
        out[key] = event
    return list(out.values())


def critical_path(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Unconstrained interval lower bound; not a resource-aware or probabilistic forecast."""
    items = unique_ids(tasks, "task")
    memo, visiting = {}, set()
    def end(key):
        if key not in items: raise ValueError("Unknown dependency")
        if key in visiting: raise ValueError("Dependency cycle")
        if key in memo: return memo[key]
        visiting.add(key); task=items[key]; lo,hi=task["minutes"]
        if not all(isinstance(x,(int,float)) and math.isfinite(x) for x in (lo,hi)) or lo<0 or hi<lo:
            raise ValueError("Invalid duration interval")
        deps=[end(d) for d in task["depends_on"]]
        memo[key]=(max((d[0] for d in deps),default=0)+lo,max((d[1] for d in deps),default=0)+hi)
        visiting.remove(key); return memo[key]
    for key in items: end(key)
    return {"effort_minutes": [sum(t["minutes"][i] for t in tasks) for i in (0,1)],
            "unconstrained_critical_path_minutes": [max((v[i] for v in memo.values()),default=0) for i in (0,1)],
            "external_wait": None,"probabilistic_forecast": False,"resource_constraints_modeled": False}


def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""): h.update(block)
    return h.hexdigest()


def manifest(root: Path) -> dict[str, Any]:
    root=root.resolve(); files=[]
    for path in sorted(root.rglob("*")):
        if path.is_symlink(): raise ValueError("Manifest refuses symlink inputs")
        if not path.is_file(): continue
        rel=path.relative_to(root)
        if any(x in {".git","__pycache__",".venv",".pytest_cache","publication"} for x in rel.parts) or path.name=="MANIFEST.json": continue
        files.append({"path":rel.as_posix(),"bytes":path.stat().st_size,"sha256":digest(path)})
    return {"schema_version":"1.0.0","self_excluded":True,"publication_receipts_excluded":True,"files":files}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=["validate","delta","manifest","verify-manifest"])
    parser.add_argument("paths",nargs="+",type=Path)
    args=parser.parse_args()
    try:
        if args.command=="validate":
            if len(args.paths)!=1: raise ValueError("validate requires one snapshot")
            result={"structurally_valid":True,"not_product_acceptance":True,**rollup(load(args.paths[0]))}
        elif args.command=="delta":
            if len(args.paths)!=2: raise ValueError("delta requires before and after")
            result=delta(load(args.paths[0]),load(args.paths[1]))
        else:
            if len(args.paths)!=1: raise ValueError("manifest commands require one root")
            root=args.paths[0]; result=manifest(root)
            if args.command=="manifest":
                (root/"MANIFEST.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
                result={"manifest_written":True,"file_count":len(result["files"])}
            elif load(root/"MANIFEST.json")!=result:
                raise ValueError("Manifest differs from current exact file set/bytes")
            else: result={"manifest_verified":True,"file_count":len(result["files"])}
        print(json.dumps(result,indent=2,allow_nan=False))
    except Exception as exc:
        parser.exit(1,f"SFD check failed: {exc}\n")

if __name__=="__main__": main()
