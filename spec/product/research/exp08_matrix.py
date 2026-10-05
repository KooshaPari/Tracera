"""Synthetic Tracera EXP-08 configuration/evidence reuse experiment.

Research model only. It does not execute Tracera, prove real compatibility,
or authorize production evidence reuse.
"""

import json
from itertools import product

CONFIGS = [
    {
        "platform": p,
        "browser": b,
        "browser_version": v,
        "feature_flag": f,
        "api_schema": a,
        "db_schema": d,
        "dependency_version": dep,
        "environment": e,
        "region": r,
    }
    for p, b, v, f, a, d, dep, e, r in product(
        ["linux", "windows"],
        ["chromium", "firefox"],
        [140, 141],
        [False, True],
        [12, 13],
        [18, 19],
        ["2.4", "2.5"],
        ["staging", "prod"],
        ["US", "EU"],
    )
]

CRITERIA = {
    "ui_search": {"platform", "browser", "browser_version", "feature_flag"},
    "api_read": {"api_schema", "feature_flag"},
    "db_read": {"db_schema", "dependency_version"},
    "auth_flow": {"browser", "browser_version", "api_schema", "environment"},
    "regional_copy": {"region", "feature_flag"},
    "deploy_health": {"platform", "environment", "dependency_version"},
}
DEFAULT = {
    "platform": "linux",
    "browser": "chromium",
    "browser_version": 140,
    "feature_flag": False,
    "api_schema": 12,
    "db_schema": 18,
    "dependency_version": "2.4",
    "environment": "staging",
    "region": "US",
}
DOMAINS = {
    "platform": ["linux", "windows"],
    "browser": ["chromium", "firefox"],
    "browser_version": [140],
    "feature_flag": [False, True],
    "api_schema": [12],
    "db_schema": [18],
    "dependency_version": ["2.4", "2.5"],
    "environment": ["staging", "prod"],
    "region": ["US", "EU"],
}


def seeds():
    out = []
    for crit, rel in CRITERIA.items():
        keys = sorted(rel)
        for vals in product(*[DOMAINS[k] for k in keys]):
            pred = dict(zip(keys, vals, strict=True))
            if "browser_version" in pred:
                pred["browser_version"] = (140, 141)
            concrete = DEFAULT.copy()
            for key, value in pred.items():
                concrete[key] = value[0] if isinstance(value, tuple) else value
            out.append((crit, pred, concrete))
    return out


def intended(pred, target):
    for key, value in pred.items():
        target_value = target[key]
        if key == "browser_version":
            if not value[0] <= target_value <= value[1]:
                return False
        elif (
            key == "api_schema" and value == 12 and target_value in (12, 13)
        ) or (
            key == "db_schema" and value == 18 and target_value in (18, 19)
        ):
            continue
        elif value != target_value:
            return False
    return True


def typed(pred, target, certificates):
    unknown = False
    for key, value in pred.items():
        target_value = target[key]
        if key == "browser_version":
            if not value[0] <= target_value <= value[1]:
                return False
        elif key in ("api_schema", "db_schema") and value != target_value:
            ok = certificates and (
                (key == "api_schema" and value == 12 and target_value == 13)
                or (key == "db_schema" and value == 18 and target_value == 19)
            )
            if not ok:
                unknown = True
        elif value != target_value:
            return False
    return None if unknown else True


def evaluate(mode, evidence):
    covered = unsafe = unknown = 0
    for crit in CRITERIA:
        criterion_evidence = [row for row in evidence if row[0] == crit]
        for target in CONFIGS:
            truth = any(intended(pred, target) for _, pred, _ in criterion_evidence)
            if mode == "exact":
                decision = any(
                    concrete == target for _, _, concrete in criterion_evidence
                )
            else:
                decisions = [
                    typed(pred, target, mode == "certified")
                    for _, pred, _ in criterion_evidence
                ]
                decision = (
                    True
                    if True in decisions
                    else (None if None in decisions else False)
                )
            if decision is True:
                covered += 1
                unsafe += not truth
            elif decision is None:
                unknown += 1
    total = len(CRITERIA) * len(CONFIGS)
    return {
        "targets": total,
        "reused": covered,
        "unsafe_reuse": unsafe,
        "unknown": unknown,
        "forced_rechecks": total - covered,
    }


def mutations(evidence):
    rows = []
    for crit, required in CRITERIA.items():
        pred = next(p for c, p, _ in evidence if c == crit)
        for missing in sorted(required):
            malformed = {key: value for key, value in pred.items() if key != missing}
            # Correct admission rejects/unknowns this evidence because a required
            # dimension is absent. A missing-as-wildcard mutant evaluates the
            # remaining predicate and would admit these targets.
            accepted = sum(intended(malformed, target) for target in CONFIGS)
            rows.append(
                {
                    "criterion": crit,
                    "omitted_required_dimension": missing,
                    "wildcard_mutant_false_admissions": accepted,
                    "detected": accepted > 0,
                }
            )
    return rows


evidence = seeds()
report = {
    "experiment": "TRC-EXP-08-MATRIX-01",
    "research_only": True,
    "configurations": len(CONFIGS),
    "criteria": len(CRITERIA),
    "evidence_seeds": len(evidence),
    "models": {
        mode: evaluate(mode, evidence) for mode in ("exact", "typed", "certified")
    },
    "mutation_controls": mutations(evidence),
    "limitations": [
        "Compatibility truth is constructed, not empirically measured.",
        "Only conjunctive typed dimensions are modeled.",
        "Certificates are assumed admitted/trusted.",
        "No candidate-artifact equivalence or criterion-version compatibility.",
        "No Tracera runtime code is executed.",
    ],
}
print(json.dumps(report, indent=2, sort_keys=True))
