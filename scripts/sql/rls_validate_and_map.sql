-- RLS validation and data mapping for tracertm
-- Run with: psql $DATABASE_URL -f scripts/rls_validate_and_map.sql
-- Or set variables first, then \i scripts/rls_validate_and_map.sql
--
-- To map data to your account, set (replace with your IDs from auth):
--   \set my_user_id 'user_01xxxx'   -- from JWT "sub" claim
--   \set my_account_id 'acct_01xxxx'  -- existing account id, or leave unset to create one

\echo '=== 1. RLS status per table ==='
SELECT
  c.relname AS table_name,
  c.relrowsecurity AS rls_enabled,
  c.relforcerowsecurity AS rls_forced
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relkind = 'r'
  AND c.relname IN (
    'account_users', 'accounts', 'projects', 'items', 'links', 'notifications'
  )
ORDER BY c.relname;

\echo ''
\echo '=== 2. RLS policies (definition) ==='
SELECT
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual::text AS using_expr,
  with_check::text AS with_check_expr
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN (
    'account_users', 'accounts', 'projects', 'items', 'links', 'notifications'
  )
ORDER BY tablename, policyname;

\echo ''
\echo '=== 3. Current data summary ==='
\echo '-- Accounts'
SELECT id, name, slug, account_type FROM accounts ORDER BY created_at LIMIT 20;

\echo ''
\echo '-- Account members (account_id, user_id, role)'
SELECT account_id, user_id, role FROM account_users ORDER BY account_id, user_id LIMIT 30;

\echo ''
\echo '-- Projects: with vs without account_id'
SELECT
  COUNT(*) FILTER (WHERE account_id IS NOT NULL) AS with_account,
  COUNT(*) FILTER (WHERE account_id IS NULL) AS without_account
FROM projects;

\echo ''
\echo '-- Sample project account_ids'
SELECT id, name, account_id FROM projects ORDER BY created_at LIMIT 10;

\echo ''
\echo '=== 4. Validate RLS as a specific user ==='
\echo 'Run these in the same session to test RLS (replace YOUR_JWT_SUB with your auth sub):'
\echo "  SELECT set_config('app.current_user_id', 'YOUR_JWT_SUB', false);"
\echo "  SELECT 'account_users' AS tbl, COUNT(*) FROM account_users"
\echo "  UNION ALL SELECT 'accounts', COUNT(*) FROM accounts"
\echo "  UNION ALL SELECT 'projects', COUNT(*) FROM projects"
\echo "  UNION ALL SELECT 'items', COUNT(*) FROM items"
\echo "  UNION ALL SELECT 'links', COUNT(*) FROM links"
\echo "  UNION ALL SELECT 'notifications', COUNT(*) FROM notifications;"
\echo 'Then: SELECT * FROM projects; (should only list projects in accounts you belong to.)'

-- ========== DATA MAPPING (optional) ==========
-- Uncomment and set :my_user_id / :my_account_id to map data to your account.
-- Requires running with a role that can bypass RLS (e.g. migration/superuser)
-- or run each block separately after setting session role.

\echo ''
\echo '=== 5. Data mapping (optional) ==='
\echo 'Set variables for mapping:'
\echo '  \set my_user_id '''your_jwt_sub''''
\echo '  \set my_account_id '''existing_account_id''''
\echo 'Then run the mapping block below (uncomment in script if needed).'

/*
-- 5a. Ensure account exists and user is member (run with RLS bypass or as owner)
INSERT INTO accounts (id, name, slug, account_type, metadata, created_at, updated_at)
VALUES (
  :'my_account_id',
  'My Account',
  'my-account',
  'personal',
  '{}',
  NOW(),
  NOW()
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO account_users (id, account_id, user_id, role, joined_at, created_at, updated_at)
VALUES (
  gen_random_uuid()::text,
  :'my_account_id',
  :'my_user_id',
  'owner',
  NOW(),
  NOW(),
  NOW()
)
ON CONFLICT (account_id, user_id) DO NOTHING;

-- 5b. Assign all orphan projects to your account
UPDATE projects
SET account_id = :'my_account_id'
WHERE account_id IS NULL;

-- Or assign specific project IDs:
-- UPDATE projects SET account_id = :'my_account_id' WHERE id IN ('proj-uuid-1', 'proj-uuid-2');

-- 5c. Verify
SELECT 'Projects now under account:' AS step, COUNT(*) FROM projects WHERE account_id = :'my_account_id';
*/

\echo ''
\echo 'Done. To run mapping, edit this file: uncomment the block in section 5 and set my_user_id / my_account_id.'
