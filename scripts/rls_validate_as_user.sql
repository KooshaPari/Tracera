-- Validate RLS row visibility for a given user (app.current_user_id).
-- Usage: psql $DATABASE_URL -v rls_user_id='YOUR_JWT_SUB' -f scripts/rls_validate_as_user.sql
-- Example: psql postgresql://localhost/trace -v rls_user_id='user_01abc' -f scripts/rls_validate_as_user.sql

SELECT set_config('app.current_user_id', COALESCE(:'rls_user_id', ''), false) AS set_rls_context;

\echo 'Row counts visible under RLS for user:'
SELECT 'account_users' AS table_name, COUNT(*) AS row_count FROM account_users
UNION ALL SELECT 'accounts', COUNT(*) FROM accounts
UNION ALL SELECT 'projects', COUNT(*) FROM projects
UNION ALL SELECT 'items', COUNT(*) FROM items
UNION ALL SELECT 'links', COUNT(*) FROM links;

\echo ''
\echo 'Projects visible (id, name, account_id):'
SELECT id, name, account_id FROM projects LIMIT 20;
