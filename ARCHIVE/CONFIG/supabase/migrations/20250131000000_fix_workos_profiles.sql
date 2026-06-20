-- Fix profiles table to use WorkOS IDs as primary identifiers
-- Remove auth_id dependency, use workos_user_id and workos_org_id as TEXT

-- Drop existing profiles table if it exists (in development)
-- In production, use ALTER TABLE instead
DO $$ 
BEGIN
    -- Check if the old schema exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'profiles' AND column_name = 'workos_id'
    ) THEN
        -- Migrate from old schema (workos_id) to new schema (workos_user_id, workos_org_id)
        ALTER TABLE profiles 
        RENAME COLUMN workos_id TO workos_user_id;
        
        ALTER TABLE profiles 
        ALTER COLUMN workos_user_id TYPE TEXT;
        
        -- Add workos_org_id column
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS workos_org_id TEXT;
        
        -- Add workos_ids JSONB column
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS workos_ids JSONB DEFAULT '{}'::JSONB;
        
        -- Add auth_id column (for compatibility, but will be unused)
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS auth_id UUID;
        
        -- Add full_name column
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);
        
        -- Rename name to full_name if name exists
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'profiles' AND column_name = 'name'
        ) THEN
            ALTER TABLE profiles 
            RENAME COLUMN name TO full_name;
        END IF;
        
        -- Add other missing columns
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS avatar_url TEXT;
        
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::JSONB;
        
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
        
        -- Update indexes
        DROP INDEX IF EXISTS idx_workos_id;
        CREATE INDEX IF NOT EXISTS idx_profiles_workos_user_id ON profiles(workos_user_id);
        CREATE INDEX IF NOT EXISTS idx_profiles_workos_org_id ON profiles(workos_org_id) WHERE workos_org_id IS NOT NULL;
        
    ELSIF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'profiles' AND column_name = 'workos_user_id'
    ) THEN
        -- Schema already updated, just ensure all columns exist
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS workos_org_id TEXT;
        
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS workos_ids JSONB DEFAULT '{}'::JSONB;
        
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS auth_id UUID;
        
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);
        
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS avatar_url TEXT;
        
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::JSONB;
        
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
        
        -- Ensure indexes exist
        CREATE INDEX IF NOT EXISTS idx_profiles_workos_user_id ON profiles(workos_user_id);
        CREATE INDEX IF NOT EXISTS idx_profiles_workos_org_id ON profiles(workos_org_id) WHERE workos_org_id IS NOT NULL;
    ELSE
        -- Create new profiles table with WorkOS-first schema
        CREATE TABLE IF NOT EXISTS profiles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            -- WorkOS identifiers (primary)
            workos_user_id TEXT NOT NULL UNIQUE,
            workos_org_id TEXT,
            workos_ids JSONB DEFAULT '{}'::JSONB,
            -- User profile information
            email VARCHAR(255) NOT NULL UNIQUE,
            full_name VARCHAR(255),
            avatar_url TEXT,
            -- Metadata
            metadata JSONB DEFAULT '{}'::JSONB,
            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP,
            -- Legacy auth_id (unused, for compatibility)
            auth_id UUID
        );
        
        CREATE INDEX idx_profiles_workos_user_id ON profiles(workos_user_id);
        CREATE INDEX idx_profiles_workos_org_id ON profiles(workos_org_id) WHERE workos_org_id IS NOT NULL;
        CREATE INDEX idx_profiles_email ON profiles(email);
        CREATE INDEX idx_profiles_deleted_at ON profiles(deleted_at) WHERE deleted_at IS NOT NULL;
    END IF;
END $$;

-- Update handle_workos_auth to use workos_user_id as primary identifier
-- Make auth_id optional (can be NULL since we're not using Supabase auth)
CREATE OR REPLACE FUNCTION public.handle_workos_auth(
    p_email VARCHAR,
    p_full_name VARCHAR,
    p_workos_user_id TEXT,
    p_workos_org_id TEXT,
    p_workos_ids JSONB DEFAULT '{}'::JSONB
)
RETURNS TABLE (
    id UUID,
    workos_user_id TEXT,
    workos_org_id TEXT,
    email VARCHAR,
    full_name VARCHAR
) AS $$
BEGIN
    INSERT INTO public.profiles (
        email,
        full_name,
        workos_user_id,
        workos_org_id,
        workos_ids,
        auth_id  -- Set to NULL since we don't use Supabase auth
    ) VALUES (
        p_email,
        p_full_name,
        p_workos_user_id,
        p_workos_org_id,
        p_workos_ids,
        NULL  -- auth_id is unused
    )
    ON CONFLICT (workos_user_id) DO UPDATE SET
        email = EXCLUDED.email,
        full_name = EXCLUDED.full_name,
        workos_org_id = EXCLUDED.workos_org_id,
        workos_ids = EXCLUDED.workos_ids,
        updated_at = CURRENT_TIMESTAMP
    RETURNING
        profiles.id,
        profiles.workos_user_id,
        profiles.workos_org_id,
        profiles.email,
        profiles.full_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
