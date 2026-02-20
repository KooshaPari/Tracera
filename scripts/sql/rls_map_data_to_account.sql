-- Map existing data to an account: ensure account + membership, assign projects.
-- Run with a role that can bypass RLS (e.g. postgres or the app migration user).
--
-- Usage:
--   psql $DATABASE_URL -v map_user_id='YOUR_JWT_SUB' -v map_account_id='acct_uuid_or_new' -f scripts/rls_map_data_to_account.sql
--
-- If map_account_id is a new UUID, an account and account_user row will be created.
-- Or use an existing account_id; then only account_user (if missing) and project updates run.

-- Ensure account exists
INSERT INTO accounts (id, name, slug, account_type, metadata, created_at, updated_at)
VALUES (
  :'map_account_id',
  'My Account',
  'account-' || REPLACE(:'map_account_id', '-', ''),
  'personal',
  '{}',
  NOW(),
  NOW()
)
ON CONFLICT (id) DO UPDATE SET updated_at = NOW();

-- Ensure user is member of account
INSERT INTO account_users (id, account_id, user_id, role, joined_at, created_at, updated_at)
VALUES (
  gen_random_uuid()::text,
  :'map_account_id',
  :'map_user_id',
  'owner',
  NOW(),
  NOW(),
  NOW()
)
ON CONFLICT (account_id, user_id) DO NOTHING;

-- Assign all projects that have no account to this account
UPDATE projects
SET account_id = :'map_account_id'
WHERE account_id IS NULL;

\echo 'Mapping complete.'
SELECT 'account' AS entity, id AS id, name AS name FROM accounts WHERE id = :'map_account_id'
UNION ALL
SELECT 'member', account_id, user_id || ' (' || role || ')' FROM account_users WHERE account_id = :'map_account_id' LIMIT 1;
SELECT COUNT(*) AS projects_now_under_account FROM projects WHERE account_id = :'map_account_id';
