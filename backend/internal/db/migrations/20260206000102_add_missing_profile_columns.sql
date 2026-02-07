-- Add missing columns to profiles table to match the Profile model
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS auth_id TEXT,
ADD COLUMN IF NOT EXISTS workos_org_id TEXT,
ADD COLUMN IF NOT EXISTS full_name TEXT,
ADD COLUMN IF NOT EXISTS avatar_url TEXT,
ADD COLUMN IF NOT EXISTS workos_ids JSONB,
ADD COLUMN IF NOT EXISTS metadata JSONB,
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
