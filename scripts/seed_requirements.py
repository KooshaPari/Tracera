"""Seed FR/NFR catalogs into the Tracera traceability graph.

Reads six cross-repo Markdown catalogs and builds:

* A :class:`~tracertm.models.trace_link.Requirement` per FR/NFR entry.
* An :class:`~tracertm.models.trace_link.Artifact` per cited PR/test.
* A :class:`~tracertm.models.trace_link.TraceLink` from Requirement→Artifact
  (``SATISFIES`` for PR artifacts, ``VERIFIES`` for test artifacts).

All writes are idempotent: deterministic UUIDs are derived from the
catalog's (project_key, req_id) / (project_key, artifact_external_id)
pair using ``uuid.uuid5(NAMESPACE, key)`` so re-runs produce the same IDs
and the Neo4j ``MERGE`` in the writer never duplicates nodes.

Usage::

    python scripts/seed_requirements.py [--dry-run] [--neo4j-uri NEO4J_URI]

    NEO4J_URI defaults to ``bolt://localhost:7687`` (or the ``NEO4J_URI``
    environment variable).  ``--dry-run`` prints the records without writing.

Functional Requirements: FR-TRC-003 (Neo4j writer), FR-TRC-004 (impact API
queryable after seeding).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

# ---------------------------------------------------------------------------
# Seed namespace — stable UUID5 base for deterministic IDs
# ---------------------------------------------------------------------------

#: All IDs derived from this namespace are stable and reproducible.
SEED_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # URL namespace

# One shared synthetic project for the seed data (dog-food project in Tracera).
SEED_PROJECT_ID = uuid.uuid5(SEED_NAMESPACE, "tracera:seed-project")

# ---------------------------------------------------------------------------
# Catalog path definitions
# ---------------------------------------------------------------------------

_BASE = Path(__file__).resolve().parent.parent  # E:/Dev/Tracera

CATALOGS: list[tuple[str, Path]] = [
    ("TRC", _BASE / "docs" / "requirements" / "tracera-frnfr.md"),
    ("AGP", Path("C:/Users/koosh/Dev/AgilePlus/docs/requirements/agileplus-frnfr.md")),
    (
        "VOXEL",
        Path(
            "C:/Users/koosh/Dev/phenotype-voxel/docs/requirements/phenotype-voxel-frnfr.md"
        ),
    ),
    (
        "AUTHV",
        Path("C:/Users/koosh/Dev/Authvault/docs/requirements/authvault-frnfr.md"),
    ),
    (
        "PMCP",
        Path("C:/Users/koosh/Dev/PhenoMCP/docs/requirements/phenomcp-frnfr.md"),
    ),
    (
        "OBS",
        Path(
            "C:/Users/koosh/Dev/PhenoObservability/docs/requirements/phenoobservability-frnfr.md"
        ),
    ),
]


# ---------------------------------------------------------------------------
# Parsed data structures (plain dataclasses — no ORM)
# ---------------------------------------------------------------------------


@dataclass
class ParsedRequirement:
    """A single FR/NFR entry extracted from a catalog."""

    req_id: str  # e.g. "FR-TRC-001"
    title: str
    description: str
    kind: str  # "functional" | "non-functional"
    status: str  # "shipped" | "planned" | "partial"
    acceptance_criteria: list[str] = field(default_factory=list)
    prs: list[str] = field(default_factory=list)  # e.g. ["#458", "#460"]
    tests: list[str] = field(default_factory=list)  # e.g. ["tests/unit/..."]


@dataclass
class ParsedArtifact:
    """A PR or test artifact cited in a catalog entry."""

    external_id: str  # e.g. "PR#458" or "tests/unit/repositories/test_link_repository.py"
    kind: str  # "pr" | "test"
    title: str
    req_id: str  # back-reference to the requirement it was found under


# ---------------------------------------------------------------------------
# Catalog parser
# ---------------------------------------------------------------------------

_FR_HEADING = re.compile(r"###\s+(FR-[A-Z]+-\d+)\s+[—–-]\s+(.+)")
_NFR_HEADING = re.compile(r"###\s+(NFR-[A-Z]+-\d+)\s+[—–-]\s+(.+)")
_PR_REF = re.compile(r"#(\d+)")
_TEST_REF = re.compile(r"(tests?/[^\s,;|`\"']+\.(?:py|tsx|rs|go))")
_STATUS_SHIPPED = re.compile(r"\bSHIPPED\b", re.IGNORECASE)
_STATUS_PLANNED = re.compile(r"\bPLANNED\b", re.IGNORECASE)
_STATUS_PARTIAL = re.compile(r"\bPARTIAL\b", re.IGNORECASE)


def _infer_status(text: str) -> str:
    if _STATUS_PARTIAL.search(text):
        return "partial"
    if _STATUS_SHIPPED.search(text):
        return "shipped"
    if _STATUS_PLANNED.search(text):
        return "planned"
    return "shipped"


def _extract_description(lines: list[str]) -> str:
    """Return the text under a **Description** heading (or the first prose block)."""
    desc_lines: list[str] = []
    in_desc = False
    for ln in lines:
        stripped = ln.strip()
        if re.match(r"\*\*Description\*\*", stripped) or stripped.lower().startswith(
            "**description"
        ):
            in_desc = True
            # The description may follow on the same line or the next.
            rest = re.sub(r"\*\*[Dd]escription[*\*]*[:：]?\s*", "", stripped)
            if rest:
                desc_lines.append(rest)
            continue
        if in_desc:
            if stripped.startswith("**") and stripped.endswith("**"):
                # Hit the next bold heading.
                break
            if stripped.startswith("###"):
                break
            desc_lines.append(stripped)
    if not desc_lines:
        # Fall back: grab first non-empty prose line.
        for ln in lines:
            stripped = ln.strip()
            if stripped and not stripped.startswith(("#", "|", "-", "*", ">")):
                desc_lines.append(stripped)
                break
    return " ".join(desc_lines).strip() or "(no description)"


def _extract_acceptance_criteria(lines: list[str]) -> list[str]:
    """Return AC bullet points."""
    criteria: list[str] = []
    in_ac = False
    for ln in lines:
        stripped = ln.strip()
        if re.search(r"acceptance.criteria", stripped, re.IGNORECASE):
            in_ac = True
            continue
        if in_ac:
            if stripped.startswith("**") or stripped.startswith("###"):
                break
            if stripped.startswith(("-", "*", "•")) or re.match(r"^\d+\.", stripped):
                criteria.append(re.sub(r"^[-*•\d.]\s+", "", stripped))
    return criteria


def _extract_prs(block: str) -> list[str]:
    """Return PR numbers from a traceability block, e.g. ['#458', '#460']."""
    return [f"#{n}" for n in _PR_REF.findall(block)]


def _extract_tests(block: str) -> list[str]:
    """Return test file references."""
    return list(dict.fromkeys(_TEST_REF.findall(block)))  # deduplicate, preserve order


def parse_catalog(project_key: str, path: Path) -> list[ParsedRequirement]:
    """Parse a single FR/NFR Markdown catalog into :class:`ParsedRequirement` records.

    Strategy:
    1. Split on ``###`` headings that match FR/NFR patterns.
    2. Within each block extract title, description, AC, traceability refs.
    """
    if not path.exists():
        print(f"[WARN] catalog not found, skipping: {path}", file=sys.stderr)
        return []

    text = path.read_text(encoding="utf-8")
    # Split on level-3 headings (FR-*/NFR-* entries).
    sections = re.split(r"(?=^###\s+(?:FR|NFR)-)", text, flags=re.MULTILINE)

    requirements: list[ParsedRequirement] = []

    for section in sections:
        m_fr = _FR_HEADING.match(section.strip())
        m_nfr = _NFR_HEADING.match(section.strip())
        m = m_fr or m_nfr
        if not m:
            continue

        req_id = m.group(1)
        title = m.group(2).strip()
        kind = "functional" if m_fr else "non-functional"
        lines = section.splitlines()

        description = _extract_description(lines)
        ac = _extract_acceptance_criteria(lines)

        # Traceability / Evidence / How Met sections for PR + test refs.
        trace_block = ""
        for marker in (
            "**Traceability**",
            "**Evidence**",
            "**How Met**",
            "**Traceability:**",
            "Traceability:",
        ):
            idx = section.find(marker)
            if idx != -1:
                # Take text up to the next bold heading or end of section.
                chunk = section[idx:]
                end = re.search(r"\n##", chunk)
                trace_block += (chunk[: end.start()] if end else chunk) + "\n"

        prs = _extract_prs(trace_block or section)
        tests = _extract_tests(trace_block or section)
        status = _infer_status(section)

        requirements.append(
            ParsedRequirement(
                req_id=req_id,
                title=title,
                description=description,
                kind=kind,
                status=status,
                acceptance_criteria=ac,
                prs=prs,
                tests=tests,
            )
        )

    return requirements


# ---------------------------------------------------------------------------
# Deterministic ID generation
# ---------------------------------------------------------------------------


def req_uuid(project_key: str, req_id: str) -> uuid.UUID:
    """Derive a stable UUID5 for a requirement node."""
    return uuid.uuid5(SEED_NAMESPACE, f"{project_key}:{req_id}")


def artifact_uuid(project_key: str, external_id: str) -> uuid.UUID:
    """Derive a stable UUID5 for an artifact node (PR or test)."""
    return uuid.uuid5(SEED_NAMESPACE, f"{project_key}:artifact:{external_id}")


def link_uuid(source_id: uuid.UUID, target_id: uuid.UUID, link_type: str) -> uuid.UUID:
    """Derive a stable UUID5 for a trace-link edge."""
    return uuid.uuid5(SEED_NAMESPACE, f"{source_id}:{target_id}:{link_type}")


# ---------------------------------------------------------------------------
# Domain object construction
# ---------------------------------------------------------------------------


def _status_to_requirement_status(status: str) -> str:
    """Map seed status → RequirementStatus value."""
    mapping = {
        "shipped": "verified",
        "planned": "proposed",
        "partial": "implemented",
    }
    return mapping.get(status, "draft")


def build_domain_objects(
    project_key: str, parsed: list[ParsedRequirement]
) -> tuple[list, list, list]:
    """Convert parsed requirements into domain objects.

    Returns (requirements, artifacts, links) — all as plain dicts suitable
    for constructing Pydantic models without importing them here (so this
    function is independently testable).
    """
    requirements: list[dict] = []
    artifacts: list[dict] = []
    links: list[dict] = []

    seen_artifact_ids: set[uuid.UUID] = set()

    for pr in parsed:
        r_id = req_uuid(project_key, pr.req_id)

        requirements.append(
            {
                "id": r_id,
                "project_id": SEED_PROJECT_ID,
                "kind": "requirement",
                "title": f"[{pr.req_id}] {pr.title}",
                "description": pr.description,
                "external_id": pr.req_id,
                "status": _status_to_requirement_status(pr.status),
                "acceptance_criteria": pr.acceptance_criteria,
                "metadata": {
                    "kind": pr.kind,
                    "catalog_status": pr.status,
                    "project_key": project_key,
                },
            }
        )

        # PR artifacts → SATISFIES links
        for pr_ref in pr.prs:
            ext_id = f"PR{pr_ref}"
            a_id = artifact_uuid(project_key, ext_id)
            if a_id not in seen_artifact_ids:
                seen_artifact_ids.add(a_id)
                artifacts.append(
                    {
                        "id": a_id,
                        "project_id": SEED_PROJECT_ID,
                        "kind": "code",
                        "title": f"PR {pr_ref} ({project_key})",
                        "external_id": ext_id,
                        "metadata": {"project_key": project_key},
                    }
                )
            l_id = link_uuid(a_id, r_id, "SATISFIES")
            links.append(
                {
                    "id": l_id,
                    "project_id": SEED_PROJECT_ID,
                    "source_artifact_id": a_id,
                    "target_artifact_id": r_id,
                    "link_type": "SATISFIES",
                    "confidence": 1.0,
                    "rationale": f"PR {pr_ref} satisfies {pr.req_id} per catalog",
                }
            )

        # Test artifacts → VERIFIES links
        for test_ref in pr.tests:
            a_id = artifact_uuid(project_key, test_ref)
            if a_id not in seen_artifact_ids:
                seen_artifact_ids.add(a_id)
                artifacts.append(
                    {
                        "id": a_id,
                        "project_id": SEED_PROJECT_ID,
                        "kind": "test",
                        "title": test_ref,
                        "external_id": test_ref,
                        "metadata": {"project_key": project_key},
                    }
                )
            l_id = link_uuid(a_id, r_id, "VERIFIES")
            links.append(
                {
                    "id": l_id,
                    "project_id": SEED_PROJECT_ID,
                    "source_artifact_id": a_id,
                    "target_artifact_id": r_id,
                    "link_type": "VERIFIES",
                    "confidence": 1.0,
                    "rationale": f"{test_ref} verifies {pr.req_id} per catalog",
                }
            )

    return requirements, artifacts, links


# ---------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------


def write_to_neo4j(
    uri: str,
    auth: tuple[str, str],
    requirements: list[dict],
    artifacts: list[dict],
    links: list[dict],
    dry_run: bool = False,
) -> None:
    """Write all records to Neo4j using the canonical writer."""
    if dry_run:
        print(
            f"[DRY-RUN] Would write {len(requirements)} requirements, "
            f"{len(artifacts)} artifacts, {len(links)} links"
        )
        return

    try:
        import neo4j  # noqa: PLC0415
    except ImportError:
        print(
            "[WARN] neo4j driver not installed; skipping DB write. "
            "Install with: pip install neo4j",
            file=sys.stderr,
        )
        return

    from tracertm.models.trace_link import (  # noqa: PLC0415
        Artifact,
        ArtifactKind,
        Requirement,
        RequirementStatus,
        TraceLink,
        TraceLinkType,
    )
    from tracertm.storage.neo4j_trace_link_writer import (  # noqa: PLC0415
        apply_schema,
        write_artifact,
        write_link,
        write_requirement,
    )

    driver = neo4j.GraphDatabase.driver(uri, auth=auth)
    try:
        apply_schema(driver)

        for r_dict in requirements:
            req = Requirement(
                id=r_dict["id"],
                project_id=r_dict["project_id"],
                title=r_dict["title"],
                description=r_dict["description"],
                external_id=r_dict["external_id"],
                status=RequirementStatus(r_dict["status"]),
                acceptance_criteria=r_dict["acceptance_criteria"],
                metadata=r_dict["metadata"],
            )
            write_requirement(driver, req)

        for a_dict in artifacts:
            art = Artifact(
                id=a_dict["id"],
                project_id=a_dict["project_id"],
                kind=ArtifactKind(a_dict["kind"]),
                title=a_dict["title"],
                external_id=a_dict.get("external_id"),
                metadata=a_dict.get("metadata", {}),
            )
            write_artifact(driver, art)

        for l_dict in links:
            lnk = TraceLink(
                id=l_dict["id"],
                project_id=l_dict["project_id"],
                source_artifact_id=l_dict["source_artifact_id"],
                target_artifact_id=l_dict["target_artifact_id"],
                link_type=TraceLinkType(l_dict["link_type"]),
                confidence=l_dict["confidence"],
                rationale=l_dict.get("rationale"),
            )
            write_link(driver, lnk)

        print(
            f"[OK] Wrote {len(requirements)} requirements, "
            f"{len(artifacts)} artifacts, {len(links)} links to {uri}"
        )
    finally:
        driver.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    """Parse catalogs and seed the Neo4j graph."""
    parser = argparse.ArgumentParser(
        description="Seed FR/NFR catalogs into Tracera's traceability graph"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print records without writing to Neo4j",
    )
    parser.add_argument(
        "--neo4j-uri",
        default=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
        help="Neo4j bolt URI (default: bolt://localhost:7687)",
    )
    parser.add_argument(
        "--neo4j-user",
        default=os.environ.get("NEO4J_USER", "neo4j"),
    )
    parser.add_argument(
        "--neo4j-password",
        default=os.environ.get("NEO4J_PASSWORD", "password"),
    )
    args = parser.parse_args(argv)

    all_requirements: list[dict] = []
    all_artifacts: list[dict] = []
    all_links: list[dict] = []

    for project_key, catalog_path in CATALOGS:
        parsed = parse_catalog(project_key, catalog_path)
        reqs, arts, lnks = build_domain_objects(project_key, parsed)
        all_requirements.extend(reqs)
        all_artifacts.extend(arts)
        all_links.extend(lnks)
        print(
            f"[{project_key}] {len(reqs)} requirements, "
            f"{len(arts)} artifacts, {len(lnks)} links"
        )

    # De-duplicate artifacts across catalogs (same test may appear in multiple).
    seen: set[uuid.UUID] = set()
    unique_artifacts: list[dict] = []
    for a in all_artifacts:
        if a["id"] not in seen:
            seen.add(a["id"])
            unique_artifacts.append(a)

    print(
        f"[TOTAL] {len(all_requirements)} requirements, "
        f"{len(unique_artifacts)} unique artifacts, {len(all_links)} links"
    )

    write_to_neo4j(
        uri=args.neo4j_uri,
        auth=(args.neo4j_user, args.neo4j_password),
        requirements=all_requirements,
        artifacts=unique_artifacts,
        links=all_links,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
