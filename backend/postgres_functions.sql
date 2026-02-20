-- PostgreSQL Functions for WorkOS Integration
-- These functions handle WorkOS user profile management (no Supabase dependency)

-- Function to create or update a profile from WorkOS JWT claims
-- Called after successful AuthKit/WorkOS authentication
CREATE OR REPLACE FUNCTION public.handle_workos_auth(
    p_auth_id UUID,
    p_email VARCHAR,
    p_full_name VARCHAR,
    p_workos_user_id TEXT,
    p_workos_org_id TEXT,
    p_workos_ids JSONB DEFAULT '{}'::JSONB
)
RETURNS TABLE (
    id UUID,
    auth_id UUID,
    workos_user_id TEXT,
    workos_org_id TEXT,
    email VARCHAR,
    full_name VARCHAR
) AS $$
BEGIN
    -- Insert or update profile
    INSERT INTO public.profiles (
        auth_id,
        email,
        full_name,
        workos_user_id,
        workos_org_id,
        workos_ids
    ) VALUES (
        p_auth_id,
        p_email,
        p_full_name,
        p_workos_user_id,
        p_workos_org_id,
        p_workos_ids
    )
    ON CONFLICT (auth_id) DO UPDATE SET
        email = EXCLUDED.email,
        full_name = EXCLUDED.full_name,
        workos_user_id = EXCLUDED.workos_user_id,
        workos_org_id = EXCLUDED.workos_org_id,
        workos_ids = EXCLUDED.workos_ids,
        updated_at = CURRENT_TIMESTAMP
    RETURNING
        profiles.id,
        profiles.auth_id,
        profiles.workos_user_id,
        profiles.workos_org_id,
        profiles.email,
        profiles.full_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get profile by WorkOS user ID
CREATE OR REPLACE FUNCTION public.get_profile_by_workos_user(
    p_workos_user_id TEXT
)
RETURNS TABLE (
    id UUID,
    auth_id UUID,
    workos_user_id TEXT,
    workos_org_id TEXT,
    email VARCHAR,
    full_name VARCHAR,
    avatar_url TEXT,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        profiles.id,
        profiles.auth_id,
        profiles.workos_user_id,
        profiles.workos_org_id,
        profiles.email,
        profiles.full_name,
        profiles.avatar_url,
        profiles.metadata
    FROM public.profiles
    WHERE profiles.workos_user_id = p_workos_user_id
    AND profiles.deleted_at IS NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get profile by auth_id (legacy UUID, deprecated)
CREATE OR REPLACE FUNCTION public.get_profile_by_auth_id(
    p_auth_id UUID
)
RETURNS TABLE (
    id UUID,
    auth_id UUID,
    workos_user_id TEXT,
    workos_org_id TEXT,
    email VARCHAR,
    full_name VARCHAR,
    avatar_url TEXT,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        profiles.id,
        profiles.auth_id,
        profiles.workos_user_id,
        profiles.workos_org_id,
        profiles.email,
        profiles.full_name,
        profiles.avatar_url,
        profiles.metadata
    FROM public.profiles
    WHERE profiles.auth_id = p_auth_id
    AND profiles.deleted_at IS NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update WorkOS IDs for a profile
CREATE OR REPLACE FUNCTION public.update_workos_ids(
    p_auth_id UUID,
    p_workos_user_id TEXT,
    p_workos_org_id TEXT,
    p_additional_ids JSONB DEFAULT '{}'::JSONB
)
RETURNS TABLE (
    id UUID,
    workos_user_id TEXT,
    workos_org_id TEXT,
    workos_ids JSONB
) AS $$
BEGIN
    RETURN QUERY
    UPDATE public.profiles
    SET
        workos_user_id = COALESCE(p_workos_user_id, workos_user_id),
        workos_org_id = COALESCE(p_workos_org_id, workos_org_id),
        workos_ids = CASE
            WHEN p_additional_ids IS NOT NULL AND p_additional_ids != '{}'::JSONB
            THEN workos_ids || p_additional_ids
            ELSE workos_ids
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE auth_id = p_auth_id
    RETURNING
        profiles.id,
        profiles.workos_user_id,
        profiles.workos_org_id,
        profiles.workos_ids;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

