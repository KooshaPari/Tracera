-- Change profiles text columns from character varying to text
-- This matches the expected schema in the tests
ALTER TABLE profiles
ALTER COLUMN workos_user_id TYPE text,
ALTER COLUMN workos_org_id TYPE text,
ALTER COLUMN email TYPE text,
ALTER COLUMN full_name TYPE text,
ALTER COLUMN avatar_url TYPE text,
ALTER COLUMN auth_id TYPE text;
