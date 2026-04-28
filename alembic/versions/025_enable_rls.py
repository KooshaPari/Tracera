"""Enable RLS and add policies.

Revision ID: 025_enable_rls
Revises: 024_linear_app_installations
Create Date: 2026-01-29 00:00:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "025_enable_rls"
down_revision = "024_linear_app_installations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    # 1. Enable RLS
    op.execute("ALTER TABLE account_users ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE accounts ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE projects ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE items ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE links ENABLE ROW LEVEL SECURITY")

    # 2. Create Policies

    # account_users: Users can see rows where they are the user
    op.execute("""
        CREATE POLICY account_users_isolation_policy ON account_users
        FOR ALL
        USING (user_id = current_setting('app.current_user_id', true))
    """)

    # accounts: Users can see accounts they are a member of
    op.execute("""
        CREATE POLICY accounts_isolation_policy ON accounts
        FOR ALL
        USING (
            id IN (
                SELECT account_id FROM account_users
                WHERE user_id = current_setting('app.current_user_id', true)
            )
        )
    """)

    # projects: Users can see projects belonging to accounts they are a member of
    op.execute("""
        CREATE POLICY projects_isolation_policy ON projects
        FOR ALL
        USING (
            account_id IN (
                SELECT account_id FROM account_users
                WHERE user_id = current_setting('app.current_user_id', true)
            )
        )
    """)

    # items: Users can see items belonging to visible projects
    op.execute("""
        CREATE POLICY items_isolation_policy ON items
        FOR ALL
        USING (
            project_id IN (
                SELECT id FROM projects
                WHERE account_id IN (
                    SELECT account_id FROM account_users
                    WHERE user_id = current_setting('app.current_user_id', true)
                )
            )
        )
    """)

    # links: Users can see links belonging to visible projects
    op.execute("""
        CREATE POLICY links_isolation_policy ON links
        FOR ALL
        USING (
            project_id IN (
                SELECT id FROM projects
                WHERE account_id IN (
                    SELECT account_id FROM account_users
                    WHERE user_id = current_setting('app.current_user_id', true)
                )
            )
        )
    """)


def downgrade() -> None:
    """Downgrade."""
    op.execute("DROP POLICY IF EXISTS links_isolation_policy ON links")
    op.execute("DROP POLICY IF EXISTS items_isolation_policy ON items")
    op.execute("DROP POLICY IF EXISTS projects_isolation_policy ON projects")
    op.execute("DROP POLICY IF EXISTS accounts_isolation_policy ON accounts")
    op.execute("DROP POLICY IF EXISTS account_users_isolation_policy ON account_users")

    op.execute("ALTER TABLE links DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE items DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE projects DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE accounts DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE account_users DISABLE ROW LEVEL SECURITY")
