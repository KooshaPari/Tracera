-- Migration: Decouple from Supabase
-- Creates profiles if missing; otherwise makes workos_user_id the primary identifier and auth_id optional.

-- Step 0: Create public.profiles if it does not exist (e.g. DB bootstrapped without init migration)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id UUID UNIQUE,
    workos_user_id TEXT NOT NULL UNIQUE,
    workos_org_id TEXT,
    workos_ids JSONB DEFAULT '{}',
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255),
    avatar_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'auth_id') THEN
        CREATE INDEX IF NOT EXISTS idx_profiles_auth_id ON public.profiles(auth_id);
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'workos_user_id') THEN
        CREATE INDEX IF NOT EXISTS idx_profiles_workos_user_id ON public.profiles(workos_user_id);
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'workos_org_id') THEN
        CREATE INDEX IF NOT EXISTS idx_profiles_workos_org_id ON public.profiles(workos_org_id);
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'email') THEN
        CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'deleted_at') THEN
        CREATE INDEX IF NOT EXISTS idx_profiles_deleted_at ON public.profiles(deleted_at);
    END IF;
END $$;

-- Steps 1–4: Only run when table already existed (has auth_id column) to migrate from old schema
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'auth_id'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'workos_user_id'
    ) THEN
        -- Ensure all existing profiles have workos_user_id
        UPDATE public.profiles
        SET workos_user_id = COALESCE(workos_user_id, 'legacy_' || auth_id::text)
        WHERE workos_user_id IS NULL OR workos_user_id = '';

        -- Make workos_user_id NOT NULL
        ALTER TABLE public.profiles
            ALTER COLUMN workos_user_id SET NOT NULL;

        -- Make auth_id nullable
        ALTER TABLE public.profiles
            ALTER COLUMN auth_id DROP NOT NULL;

        -- Ensure unique constraint on workos_user_id exists
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conname = 'profiles_workos_user_id_key'
        ) THEN
            ALTER TABLE public.profiles
                ADD CONSTRAINT profiles_workos_user_id_key UNIQUE (workos_user_id);
        END IF;
    END IF;
END $$;

-- Step 5: Create or replace function
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
        workos_user_id,
        workos_org_id,
        email,
        full_name,
        workos_ids,
        created_at,
        updated_at
    ) VALUES (
        p_workos_user_id,
        p_workos_org_id,
        p_email,
        p_full_name,
        p_workos_ids,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (workos_user_id) DO UPDATE SET
        workos_org_id = EXCLUDED.workos_org_id,
        email = EXCLUDED.email,
        full_name = EXCLUDED.full_name,
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
