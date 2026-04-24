#!/usr/bin/env python3
"""Validate seeded data is in the DB and kooshapari@gmail.com can access it.

- Checks account, projects, items, links, events, milestones, sprints for the seed account.
- Ensures the seed account exists (creates it if missing).
- Optional: --link-user USER_ID or --link-email EMAIL adds that user to the seed account so they see the project in the list.

Usage:
  DATABASE_URL="postgresql://tracertm:PASSWORD@localhost:5432/tracertm" uv run python scripts/validate_seed_and_access.py
  ... validate_seed_and_access.py --link-email kooshapari@gmail.com   # lookup user from tracertm.users and link
  ... validate_seed_and_access.py --link-user user_01abc...            # or pass user id from /api/v1/auth/me

If DB connection fails, set DATABASE_URL to your Postgres URL (user must exist, e.g. tracertm).
"""

import argparse
import os
import sys
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

SEED_ACCOUNT_ID = "7f3c8d2a-1b4e-4a9c-9e2d-6f1a8b0c3d4e"
SEED_ACCOUNT_NAME = "Seed account (Platform In-Progress)"
SEED_ACCOUNT_SLUG = "seed-platform"


def get_engine() -> Engine:
    """Get engine."""
    url = os.getenv("DATABASE_URL", "postgresql://tracertm:tracertm_password@localhost:5432/tracertm")
    if url.startswith("postgresql+asyncpg"):
        url = url.replace("postgresql+asyncpg", "postgresql", 1)
    return create_engine(url, pool_pre_ping=True)


def ensure_account(conn: Any) -> bool:
    """Ensure seed account exists; create if not. Returns True if created."""
    r = conn.execute(
        text("SELECT 1 FROM tracertm.accounts WHERE id = :id"),
        {"id": SEED_ACCOUNT_ID},
    )
    if r.scalar() is not None:
        return False
    conn.execute(
        text("""
            INSERT INTO tracertm.accounts (id, name, slug, account_type, metadata, created_at, updated_at)
            VALUES (:id, :name, :slug, 'personal', '{}', NOW(), NOW())
        """),
        {"id": SEED_ACCOUNT_ID, "name": SEED_ACCOUNT_NAME, "slug": SEED_ACCOUNT_SLUG},
    )
    conn.commit()
    return True


def link_user(conn: Any, user_id: str) -> bool:
    """Add user to seed account as owner. Returns True if inserted."""
    r = conn.execute(
        text("SELECT 1 FROM tracertm.account_users WHERE account_id = :aid AND user_id = :uid"),
        {"aid": SEED_ACCOUNT_ID, "uid": user_id},
    )
    if r.scalar() is not None:
        return False
    conn.execute(
        text("""
            INSERT INTO tracertm.account_users (id, account_id, user_id, role, joined_at)
            VALUES (gen_random_uuid()::text, :aid, :uid, 'owner', NOW())
        """),
        {"aid": SEED_ACCOUNT_ID, "uid": user_id},
    )
    conn.commit()
    return True


def lookup_user_id_by_email(conn: Any, email: str) -> str | None:
    """Return user id from users table by email (tries tracertm.users then public.users)."""
    import logging

    logger = logging.getLogger(__name__)
    for schema_table in ("tracertm.users", "public.users"):
        try:
            r = conn.execute(
                text(f"SELECT id FROM {schema_table} WHERE email = :email"),
                {"email": email},
            )
            row = r.fetchone()
            if row:
                return row[0]
        except Exception as e:
            logger.debug("lookup_user_id_by_email %s: %s", schema_table, e)
            continue
    return None


def resolve_user_id(conn: Any, link_email: str | None, link_user_id: str | None) -> str | None:
    """Resolve user ID from email if provided."""
    if not link_email or link_user_id:
        return link_user_id

    resolved_id = lookup_user_id_by_email(conn, link_email)
    if not resolved_id:
        return None

    return resolved_id


def validate_account(conn: Any) -> bool:
    """Ensure account exists and report status."""
    try:
        created = ensure_account(conn)
        if created:
            pass
        return True
    except Exception:
        return False


def get_and_display_projects(conn: Any) -> tuple[list, bool]:
    """Get projects for seed account and display them."""
    try:
        r = conn.execute(
            text("SELECT id, name FROM tracertm.projects WHERE account_id = :aid"),
            {"aid": SEED_ACCOUNT_ID},
        )
        projects = list(r.fetchall())
    except Exception:
        return [], False

    if not projects:
        return [], False

    for _pid, _pname in projects[:5]:
        pass
    if len(projects) > 5:
        pass

    return projects, True


def display_entity_counts(conn: Any) -> bool:
    """Display counts for various entities in seed account."""
    queries = [
        (
            "Items",
            "SELECT COUNT(*) FROM tracertm.items i JOIN tracertm.projects p ON p.id = i.project_id WHERE p.account_id = :aid",
        ),
        (
            "Links",
            "SELECT COUNT(*) FROM tracertm.links l JOIN tracertm.items i ON i.id = l.source_id JOIN tracertm.projects p ON p.id = i.project_id WHERE p.account_id = :aid",
        ),
        (
            "Events",
            "SELECT COUNT(*) FROM tracertm.events e JOIN tracertm.projects p ON p.id = e.project_id WHERE p.account_id = :aid",
        ),
        (
            "Milestones",
            "SELECT COUNT(*) FROM tracertm.milestones m JOIN tracertm.projects p ON p.id = m.project_id WHERE p.account_id = :aid",
        ),
        (
            "Sprints",
            "SELECT COUNT(*) FROM tracertm.sprints s JOIN tracertm.projects p ON p.id = s.project_id WHERE p.account_id = :aid",
        ),
    ]

    ok = True
    for _label, sql in queries:
        try:
            r = conn.execute(text(sql), {"aid": SEED_ACCOUNT_ID})
            r.scalar()
        except Exception:
            ok = False

    return ok


def link_user_to_account(conn: Any, link_user_id: str) -> bool:
    """Link a user to the seed account."""
    try:
        inserted = link_user(conn, link_user_id)
        if inserted:
            pass
        return True
    except Exception:
        return False


def print_access_instructions(projects: list) -> None:
    """Print instructions for accessing the seed data."""
    if projects:
        [str(r[0]) for r in projects]


def run(link_user_id: str | None, link_email: str | None) -> int:
    """Validate seed data and optionally link user to account."""
    engine = get_engine()
    ok = True

    # Resolve user ID from email if needed
    if link_email and not link_user_id:
        with engine.connect() as conn:
            link_user_id = resolve_user_id(conn, link_email, link_user_id)
            if not link_user_id:
                return 2

    with engine.connect() as conn:
        # Validate account
        ok = validate_account(conn) and ok

        # Get and display projects
        projects, projects_ok = get_and_display_projects(conn)
        ok = ok and projects_ok

        if not projects:
            return 2

        # Display entity counts
        ok = display_entity_counts(conn) and ok

        # Link user if requested
        if link_user_id:
            ok = link_user_to_account(conn, link_user_id) and ok

    # Print access instructions
    print_access_instructions(projects)

    return 0 if ok else 1


def main() -> int:
    """Main."""
    p = argparse.ArgumentParser(
        description="Validate seed data and optionally link kooshapari@gmail.com to seed account",
    )
    p.add_argument(
        "--link-user",
        metavar="USER_ID",
        help="Add this user to seed account as owner (from /api/v1/auth/me)",
    )
    p.add_argument(
        "--link-email",
        metavar="EMAIL",
        help="Look up user by email in tracertm.users and link to seed account (e.g. kooshapari@gmail.com)",
    )
    args = p.parse_args()
    if args.link_email and args.link_user:
        return 2
    return run(args.link_user, args.link_email)


if __name__ == "__main__":
    sys.exit(main())
