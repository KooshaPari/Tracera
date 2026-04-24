"""Fix RLS policies for practical usage (teams, creation).

Revision ID: 026_fix_rls_policies
Revises: 025_enable_rls
Create Date: 2026-01-29 01:00:00.000000
"""

from alembic import op

revision = "026_fix_rls_policies"
down_revision = "025_enable_rls"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    # 1. account_users
    op.execute("DROP POLICY IF EXISTS account_users_isolation_policy ON account_users")

    # Select: See all members in my accounts
    op.execute("""
        CREATE POLICY account_users_select_policy ON account_users FOR SELECT
        USING (
            account_id IN (
                SELECT account_id FROM account_users
                WHERE user_id = current_setting('app.current_user_id', true)
            )
        )
    """)

    # Insert: Can insert myself (new account) OR insert others into my accounts (invite)
    op.execute("""
        CREATE POLICY account_users_insert_policy ON account_users FOR INSERT
        WITH CHECK (
            user_id = current_setting('app.current_user_id', true)
            OR
            account_id IN (
                SELECT account_id FROM account_users
                WHERE user_id = current_setting('app.current_user_id', true)
            )
        )
    """)

    # Update/Delete: Can manage my accounts
    op.execute("""
        CREATE POLICY account_users_write_policy ON account_users FOR UPDATE
        USING (
            account_id IN (
                SELECT account_id FROM account_users
                WHERE user_id = current_setting('app.current_user_id', true)
            )
        )
    """)
    op.execute("""
        CREATE POLICY account_users_delete_policy ON account_users FOR DELETE
        USING (
            account_id IN (
                SELECT account_id FROM account_users
                WHERE user_id = current_setting('app.current_user_id', true)
            )
        )
    """)

    # 2. accounts
    op.execute("DROP POLICY IF EXISTS accounts_isolation_policy ON accounts")

    # Select: My accounts
    op.execute("""
        CREATE POLICY accounts_select_policy ON accounts FOR SELECT
        USING (
            id IN (
                SELECT account_id FROM account_users
                WHERE user_id = current_setting('app.current_user_id', true)
            )
        )
    """)

    # Insert: Allow authenticated creation (bootstrap)
    op.execute("""
        CREATE POLICY accounts_insert_policy ON accounts FOR INSERT
        WITH CHECK (current_setting('app.current_user_id', true) IS NOT NULL)
    """)

    # Update/Delete: My accounts
    op.execute("""
        CREATE POLICY accounts_write_policy ON accounts FOR UPDATE
        USING (
            id IN (
                SELECT account_id FROM account_users
                WHERE user_id = current_setting('app.current_user_id', true)
            )
        )
    """)
    op.execute("""
        CREATE POLICY accounts_delete_policy ON accounts FOR DELETE
        USING (
            id IN (
                SELECT account_id FROM account_users
                WHERE user_id = current_setting('app.current_user_id', true)
            )
        )
    """)


def downgrade() -> None:
    """Downgrade."""
    # Revert to strict isolation (or just drop the new ones and recreate old)
    # Dropping new ones
    op.execute("DROP POLICY IF EXISTS account_users_select_policy ON account_users")
    op.execute("DROP POLICY IF EXISTS account_users_insert_policy ON account_users")
    op.execute("DROP POLICY IF EXISTS account_users_write_policy ON account_users")
    op.execute("DROP POLICY IF EXISTS account_users_delete_policy ON account_users")

    op.execute("DROP POLICY IF EXISTS accounts_select_policy ON accounts")
    op.execute("DROP POLICY IF EXISTS accounts_insert_policy ON accounts")
    op.execute("DROP POLICY IF EXISTS accounts_write_policy ON accounts")
    op.execute("DROP POLICY IF EXISTS accounts_delete_policy ON accounts")

    # Recreate original restrictive policies
    op.execute("""
        CREATE POLICY account_users_isolation_policy ON account_users
        USING (user_id = current_setting('app.current_user_id', true))
    """)
    op.execute("""
        CREATE POLICY accounts_isolation_policy ON accounts
        USING (
            id IN (
                SELECT account_id FROM account_users
                WHERE user_id = current_setting('app.current_user_id', true)
            )
        )
    """)
