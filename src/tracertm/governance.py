"""Spec-first governance checks for Tracera planning workflows."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

TraceKind = Literal["implementation", "test", "evidence", "decision"]
GateStatus = Literal["pass", "fail"]


class GovernanceTrace(BaseModel):
    """Trace from a specification item to downstream work."""

    spec_id: str = Field(..., min_length=1)
    target_id: str = Field(..., min_length=1)
    kind: TraceKind


class GovernanceSpec(BaseModel):
    """Specification metadata required before execution starts."""

    spec_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    owner: str = Field(..., min_length=1)
    acceptance_criteria: list[str] = Field(default_factory=list)
    evidence_links: list[str] = Field(default_factory=list)
    status: Literal["draft", "approved", "implemented"] = "draft"


class GovernanceViolation(BaseModel):
    """One spec-first governance violation."""

    spec_id: str
    code: str
    message: str


class GovernanceReport(BaseModel):
    """Result of a spec-first governance gate."""

    status: GateStatus
    spec_count: int
    trace_count: int
    violations: list[GovernanceViolation]


def evaluate_spec_first_governance(
    specs: list[GovernanceSpec],
    traces: list[GovernanceTrace],
) -> GovernanceReport:
    """Evaluate whether work is backed by approved specs, tests, and evidence."""
    traces_by_spec: dict[str, list[GovernanceTrace]] = {}
    for trace in traces:
        traces_by_spec.setdefault(trace.spec_id, []).append(trace)

    known_spec_ids = {spec.spec_id for spec in specs}
    violations: list[GovernanceViolation] = []
    seen_spec_ids: set[str] = set()

    for spec in specs:
        violations.extend(_validate_spec(spec, traces_by_spec, seen_spec_ids))

    violations.extend(
        _violation(trace.spec_id, "orphan_trace", f"Trace target {trace.target_id} has no spec")
        for trace in traces
        if trace.spec_id not in known_spec_ids
    )

    return GovernanceReport(
        status="fail" if violations else "pass",
        spec_count=len(specs),
        trace_count=len(traces),
        violations=violations,
    )


def _violation(spec_id: str, code: str, message: str) -> GovernanceViolation:
    return GovernanceViolation(spec_id=spec_id, code=code, message=message)


def _validate_spec(
    spec: GovernanceSpec,
    traces_by_spec: dict[str, list[GovernanceTrace]],
    seen_spec_ids: set[str],
) -> list[GovernanceViolation]:
    violations: list[GovernanceViolation] = []
    if spec.spec_id in seen_spec_ids:
        return [_violation(spec.spec_id, "duplicate_spec", "Duplicate spec id")]
    seen_spec_ids.add(spec.spec_id)

    if spec.status != "approved":
        violations.append(_violation(spec.spec_id, "not_approved", "Spec must be approved"))
    if not spec.acceptance_criteria:
        violations.append(_violation(spec.spec_id, "missing_acceptance", "Acceptance criteria required"))
    if not spec.evidence_links:
        violations.append(_violation(spec.spec_id, "missing_evidence", "Evidence links required"))

    trace_kinds = {trace.kind for trace in traces_by_spec.get(spec.spec_id, [])}
    if "implementation" not in trace_kinds:
        violations.append(
            _violation(spec.spec_id, "missing_implementation", "Implementation trace required")
        )
    if "test" not in trace_kinds:
        violations.append(_violation(spec.spec_id, "missing_test", "Test trace required"))
    return violations


__all__ = [
    "GovernanceReport",
    "GovernanceSpec",
    "GovernanceTrace",
    "GovernanceViolation",
    "evaluate_spec_first_governance",
]
