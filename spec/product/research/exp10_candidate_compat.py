"""Research-only candidate/certificate reuse model for Tracera EXP-10."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    source: str
    lock: str
    toolchain: str
    flag: bool
    api: int
    db: int
    artifact: str
    env: str


@dataclass(frozen=True)
class Criterion:
    id: str
    rev: int
    deps: frozenset[str]
    operation: str


@dataclass(frozen=True)
class Cert:
    id: str
    issuer: str
    domain: str
    src: object
    dst: object
    criteria: frozenset[tuple]
    operations: frozenset[str]
    envs: frozenset[str]
    direction: str = "forward"
    transitive: bool = False
    active: bool = True


TRUSTED = {"release-authority", "schema-owner"}


def cert_covers(cert, criterion, field, source, destination, target):
    return (
        cert.active
        and cert.issuer in TRUSTED
        and cert.domain == field
        and cert.src == source
        and cert.dst == destination
        and (criterion.id, criterion.rev) in cert.criteria
        and criterion.operation in cert.operations
        and target.env in cert.envs
    )


def reusable(evidence, target, criterion, certs=()):
    for field in criterion.deps:
        source = getattr(evidence, field)
        destination = getattr(target, field)
        if source == destination:
            continue
        if any(
            cert_covers(cert, criterion, field, source, destination, target)
            for cert in certs
        ):
            continue
        return False
    return True


base = Candidate("gitA", "lock1", "rust1", False, 12, 18, "imgA", "prod")
crit = Criterion(
    "api-users",
    1,
    frozenset({"source", "lock", "flag", "api", "env"}),
    "GET /users",
)
good = Cert(
    "c1",
    "schema-owner",
    "api",
    12,
    13,
    frozenset({("api-users", 1)}),
    frozenset({"GET /users"}),
    frozenset({"prod"}),
)
cases = [
    ("exact", base, crit, (), True),
    (
        "api scoped cert",
        Candidate("gitA", "lock1", "rust1", False, 13, 18, "imgB", "prod"),
        crit,
        (good,),
        True,
    ),
    (
        "wrong operation",
        Candidate("gitA", "lock1", "rust1", False, 13, 18, "imgB", "prod"),
        Criterion("api-users", 1, crit.deps, "POST /payments"),
        (good,),
        False,
    ),
    (
        "criterion revision",
        Candidate("gitA", "lock1", "rust1", False, 13, 18, "imgB", "prod"),
        Criterion("api-users", 2, crit.deps, "GET /users"),
        (good,),
        False,
    ),
    (
        "untrusted issuer",
        Candidate("gitA", "lock1", "rust1", False, 13, 18, "imgB", "prod"),
        crit,
        (
            Cert(
                "c2",
                "agent",
                "api",
                12,
                13,
                good.criteria,
                good.operations,
                good.envs,
            ),
        ),
        False,
    ),
    (
        "revoked",
        Candidate("gitA", "lock1", "rust1", False, 13, 18, "imgB", "prod"),
        crit,
        (
            Cert(
                "c3",
                "schema-owner",
                "api",
                12,
                13,
                good.criteria,
                good.operations,
                good.envs,
                active=False,
            ),
        ),
        False,
    ),
    (
        "changed lock",
        Candidate("gitA", "lock2", "rust1", False, 12, 18, "imgB", "prod"),
        crit,
        (),
        False,
    ),
    (
        "changed flag",
        Candidate("gitA", "lock1", "rust1", True, 12, 18, "imgB", "prod"),
        crit,
        (),
        False,
    ),
    (
        "artifact irrelevant to criterion",
        Candidate("gitA", "lock1", "rust1", False, 12, 18, "imgB", "prod"),
        crit,
        (),
        True,
    ),
    (
        "environment sensitive",
        Candidate("gitA", "lock1", "rust1", False, 12, 18, "imgB", "staging"),
        crit,
        (),
        False,
    ),
]

rows = []
for name, target, criterion, certs, expected in cases:
    actual = reusable(base, target, criterion, certs)
    rows.append((name, actual, expected, actual == expected))

# Demonstrate source-only mutant.
mutants = []
for name, target, _criterion, _certs, expected in cases:
    if expected:
        continue
    bad = base.source == target.source
    mutants.append((name, bad, bad != expected))

print(
    {
        "checks": len(rows),
        "passed": sum(row[3] for row in rows),
        "source_only_negative_cases": len(mutants),
        "source_only_false_reuse": sum(row[1] for row in mutants),
        "all_source_only_mutants_detected": all(row[2] for row in mutants),
    }
)
for row in rows:
    print(row)
