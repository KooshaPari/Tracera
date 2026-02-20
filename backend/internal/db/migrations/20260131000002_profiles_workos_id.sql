-- One-time fix for profiles: old schema had workos_id NOT NULL; app uses workos_user_id.
-- Run with: psql $DATABASE_URL -f migrations/20260131_profiles_workos_id.sql
-- (Or: psql -h localhost -U postgres -d your_db -f backend/migrations/20260131_profiles_workos_id.sql)
-- Safe to run multiple times; no-op if table/columns already in target state.

-- Target public.profiles explicitly (search_path may be tracertm).
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'workos_id'
  ) THEN
    BEGIN
      ALTER TABLE public.profiles RENAME COLUMN workos_id TO workos_user_id;
    EXCEPTION
      WHEN duplicate_column THEN
        ALTER TABLE public.profiles DROP COLUMN workos_id;
      WHEN undefined_column THEN
        NULL;
    END;
  END IF;
END $$;
