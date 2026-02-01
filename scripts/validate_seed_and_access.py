#!/usr/bin/env python3
"""
Validate seeded data is in the DB and kooshapari@gmail.com can access it.

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
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

SEED_ACCOUNT_ID = "7f3c8d2a-1b4e-4a9c-9e2d-6f1a8b0c3d4e"
SEED_ACCOUNT_NAME = "Seed account (Platform In-Progress)"
SEED_ACCOUNT_SLUG = "seed-platform"


def get_engine() -> Engine:
    url = os.getenv("DATABASE_URL", "postgresql://tracertm:tracertm_password@localhost:5432/tracertm")
    if url.startswith("postgresql+asyncpg"):
        url = url.replace("postgresql+asyncpg", "postgresql", 1)
    return create_engine(url, pool_pre_ping=True)


def ensure_account(conn) -> bool:
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


def link_user(conn, user_id: str) -> bool:
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


def lookup_user_id_by_email(conn, email: str) -> str | None:
    """Return user id from users table by email (tries tracertm.users then public.users)."""
    for schema_table in ("tracertm.users", "public.users"):
        try:
            r = conn.execute(
                text(f"SELECT id FROM {schema_table} WHERE email = :email"),
                {"email": email},
            )
            row = r.fetchone()
            if row:
                return row[0]
        except Exception:
            continue
    return None


def run(link_user_id: str | None, link_email: str | None) -> int:
    engine = get_engine()
    ok = True
    if link_email and not link_user_id:
        with engine.connect() as conn:
            link_user_id = lookup_user_id_by_email(conn, link_email)
            if not link_user_id:
                print(f"User not found for email {link_email} (log in once so tracertm.users is synced, or use --link-user)", file=sys.stderr)
                return 2
            print(f"Resolved email {link_email} -> user_id {link_user_id}")

    with engine.connect() as conn:
        # Ensure account exists
        try:
            created = ensure_account(conn)
            if created:
                print(f"Created account {SEED_ACCOUNT_ID} ({SEED_ACCOUNT_SLUG})")
            else:
                print(f"Account {SEED_ACCOUNT_ID} exists")
        except Exception as e:
            print(f"Account check/create failed: {e}", file=sys.stderr)
            ok = False

        # Counts for seed account
        projects = []
        try:
            r = conn.execute(
                text("SELECT id, name FROM tracertm.projects WHERE account_id = :aid"),
                {"aid": SEED_ACCOUNT_ID},
            )
            projects = list(r.fetchall())
        except Exception as e:
            print(f"Projects check failed: {e}", file=sys.stderr)
            ok = False
        if not projects:
            print("No projects found for seed account (run scripts/seed_rich_single_project.py first)")
            ok = False
        else:
            print(f"Projects in seed account: {len(projects)}")
            for pid, pname in projects[:5]:
                print(f"  - {pid}  {pname}")
            if len(projects) > 5:
                print(f"  ... and {len(projects) - 5} more")

        if not projects:
            print("\nRun: DATABASE_URL=... uv run python scripts/seed_rich_single_project.py")
            return 2

        # Totals across all projects in seed account
        project_ids = [str(r[0]) for r in projects]
        print()
        for label, sql, params in [
            ("Items", "SELECT COUNT(*) FROM tracertm.items i JOIN tracertm.projects p ON p.id = i.project_id WHERE p.account_id = :aid", {"aid": SEED_ACCOUNT_ID}),
            ("Links", "SELECT COUNT(*) FROM tracertm.links l JOIN tracertm.items i ON i.id = l.source_id JOIN tracertm.projects p ON p.id = i.project_id WHERE p.account_id = :aid", {"aid": SEED_ACCOUNT_ID}),
            ("Events", "SELECT COUNT(*) FROM tracertm.events e JOIN tracertm.projects p ON p.id = e.project_id WHERE p.account_id = :aid", {"aid": SEED_ACCOUNT_ID}),
            ("Milestones", "SELECT COUNT(*) FROM tracertm.milestones m JOIN tracertm.projects p ON p.id = m.project_id WHERE p.account_id = :aid", {"aid": SEED_ACCOUNT_ID}),
            ("Sprints", "SELECT COUNT(*) FROM tracertm.sprints s JOIN tracertm.projects p ON p.id = s.project_id WHERE p.account_id = :aid", {"aid": SEED_ACCOUNT_ID}),
        ]:
            try:
                r = conn.execute(text(sql), params)
                n = r.scalar()
                print(f"{label}: {n}")
            except Exception as e:
                print(f"{label}: error - {e}", file=sys.stderr)
                ok = False

        # Optional: link user to account
        if link_user_id:
            try:
                inserted = link_user(conn, link_user_id)
                if inserted:
                    print(f"Linked user {link_user_id} to seed account as owner")
                else:
                    print(f"User {link_user_id} already in seed account")
            except Exception as e:
                print(f"Link user failed: {e}", file=sys.stderr)
                ok = False

    print()
    print("kooshapari@gmail.com access:")
    print("  - With TRACERTM_SYSTEM_ADMIN_EMAILS=kooshapari@gmail.com you can access any project by ID (bypass RLS).")
    print("  - To see the seeded project in the project list, link your user to the seed account:")
    print("    uv run python scripts/validate_seed_and_access.py --link-email kooshapari@gmail.com")
    print("    (or --link-user YOUR_USER_ID from GET /api/v1/auth/me if not in tracertm.users)")
    print()
    if projects:
        print(f"  Seeded project IDs: {', '.join(project_ids[:3])}{' ...' if len(project_ids) > 3 else ''}")
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description="Validate seed data and optionally link kooshapari@gmail.com to seed account")
    p.add_argument("--link-user", metavar="USER_ID", help="Add this user to seed account as owner (from /api/v1/auth/me)")
    p.add_argument("--link-email", metavar="EMAIL", help="Look up user by email in tracertm.users and link to seed account (e.g. kooshapari@gmail.com)")
    args = p.parse_args()
    if args.link_email and args.link_user:
        print("Use only one of --link-user or --link-email", file=sys.stderr)
        return 2
    return run(args.link_user, args.link_email)


if __name__ == "__main__":
    sys.exit(main())
