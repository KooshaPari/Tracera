-- One-off: apply accounts schema (021) + RLS (025, 026) for DBs that are on a different migration head.
-- Idempotent where possible.

-- 021: accounts table
CREATE TABLE IF NOT EXISTS accounts (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    account_type VARCHAR(50) NOT NULL DEFAULT 'personal',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_accounts_name ON accounts (name);
CREATE INDEX IF NOT EXISTS ix_accounts_slug ON accounts (slug);

-- 021: account_users table
CREATE TABLE IF NOT EXISTS account_users (
    id VARCHAR(36) PRIMARY KEY,
    account_id VARCHAR(36) NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (account_id, user_id)
);
CREATE INDEX IF NOT EXISTS ix_account_users_user_id ON account_users (user_id);

-- 021: add account_id to projects if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'projects' AND column_name = 'account_id'
    ) THEN
        ALTER TABLE projects ADD COLUMN account_id VARCHAR(36) REFERENCES accounts(id) ON DELETE CASCADE;
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS ix_projects_account_id ON projects (account_id);

-- 025: Enable RLS
ALTER TABLE account_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE links ENABLE ROW LEVEL SECURITY;

-- 025: Initial policies (026 will replace account_users + accounts)
DROP POLICY IF EXISTS account_users_isolation_policy ON account_users;
CREATE POLICY account_users_isolation_policy ON account_users FOR ALL
    USING (user_id = current_setting('app.current_user_id', true));

DROP POLICY IF EXISTS accounts_isolation_policy ON accounts;
CREATE POLICY accounts_isolation_policy ON accounts FOR ALL
    USING (id IN (SELECT account_id FROM account_users WHERE user_id = current_setting('app.current_user_id', true)));

DROP POLICY IF EXISTS projects_isolation_policy ON projects;
CREATE POLICY projects_isolation_policy ON projects FOR ALL
    USING (account_id IN (SELECT account_id FROM account_users WHERE user_id = current_setting('app.current_user_id', true)));

DROP POLICY IF EXISTS items_isolation_policy ON items;
CREATE POLICY items_isolation_policy ON items FOR ALL
    USING (project_id IN (
        SELECT id FROM projects
        WHERE account_id IN (SELECT account_id FROM account_users WHERE user_id = current_setting('app.current_user_id', true))
    ));

DROP POLICY IF EXISTS links_isolation_policy ON links;
CREATE POLICY links_isolation_policy ON links FOR ALL
    USING (project_id IN (
        SELECT id FROM projects
        WHERE account_id IN (SELECT account_id FROM account_users WHERE user_id = current_setting('app.current_user_id', true))
    ));

-- 026: Replace account_users + accounts policies
DROP POLICY IF EXISTS account_users_isolation_policy ON account_users;
CREATE POLICY account_users_select_policy ON account_users FOR SELECT
    USING (account_id IN (SELECT account_id FROM account_users WHERE user_id = current_setting('app.current_user_id', true)));
CREATE POLICY account_users_insert_policy ON account_users FOR INSERT
    WITH CHECK (
        user_id = current_setting('app.current_user_id', true)
        OR account_id IN (SELECT account_id FROM account_users WHERE user_id = current_setting('app.current_user_id', true))
    );
CREATE POLICY account_users_write_policy ON account_users FOR UPDATE
    USING (account_id IN (SELECT account_id FROM account_users WHERE user_id = current_setting('app.current_user_id', true)));
CREATE POLICY account_users_delete_policy ON account_users FOR DELETE
    USING (account_id IN (SELECT account_id FROM account_users WHERE user_id = current_setting('app.current_user_id', true)));

DROP POLICY IF EXISTS accounts_isolation_policy ON accounts;
CREATE POLICY accounts_select_policy ON accounts FOR SELECT
    USING (id IN (SELECT account_id FROM account_users WHERE user_id = current_setting('app.current_user_id', true)));
CREATE POLICY accounts_insert_policy ON accounts FOR INSERT
    WITH CHECK (current_setting('app.current_user_id', true) IS NOT NULL);
CREATE POLICY accounts_write_policy ON accounts FOR UPDATE
    USING (id IN (SELECT account_id FROM account_users WHERE user_id = current_setting('app.current_user_id', true)));
CREATE POLICY accounts_delete_policy ON accounts FOR DELETE
    USING (id IN (SELECT account_id FROM account_users WHERE user_id = current_setting('app.current_user_id', true)));
