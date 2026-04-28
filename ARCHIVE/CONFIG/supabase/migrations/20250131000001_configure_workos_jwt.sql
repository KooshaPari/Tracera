-- Configure Supabase to accept WorkOS JWTs
-- This sets up JWT verification for WorkOS tokens

-- Create a function to verify WorkOS JWT tokens
-- Note: Supabase uses JWT_SECRET from environment, but we need to configure it to accept WorkOS tokens
-- WorkOS uses HS256 algorithm with the JWT secret from WorkOS dashboard

-- Function to extract WorkOS user ID from JWT claims
-- This is used by RLS policies and functions
CREATE OR REPLACE FUNCTION public.get_workos_user_id()
RETURNS TEXT AS $$
DECLARE
    token_claims JSONB;
    workos_user_id TEXT;
BEGIN
    -- Get JWT claims from current request
    -- Supabase automatically provides current_setting('request.jwt.claims', true)::jsonb
    token_claims := current_setting('request.jwt.claims', true)::jsonb;
    
    -- Extract WorkOS user ID from 'sub' claim (WorkOS standard)
    workos_user_id := token_claims->>'sub';
    
    RETURN workos_user_id;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Function to extract WorkOS org ID from JWT claims
CREATE OR REPLACE FUNCTION public.get_workos_org_id()
RETURNS TEXT AS $$
DECLARE
    token_claims JSONB;
    workos_org_id TEXT;
BEGIN
    token_claims := current_setting('request.jwt.claims', true)::jsonb;
    workos_org_id := token_claims->>'org_id';
    RETURN workos_org_id;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Enable RLS on profiles table
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own profile
CREATE POLICY "Users can read own profile"
ON public.profiles
FOR SELECT
USING (
    workos_user_id = public.get_workos_user_id()
);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update own profile"
ON public.profiles
FOR UPDATE
USING (
    workos_user_id = public.get_workos_user_id()
)
WITH CHECK (
    workos_user_id = public.get_workos_user_id()
);

-- Policy: Allow service role to manage all profiles (for backend)
CREATE POLICY "Service role can manage all profiles"
ON public.profiles
FOR ALL
USING (true)
WITH CHECK (true);

-- Note: To configure Supabase to accept WorkOS JWTs, you need to:
-- 1. Set SUPABASE_JWT_SECRET to your WorkOS JWT secret in Supabase dashboard
-- 2. Or use environment variable: SUPABASE_JWT_SECRET=<workos_jwt_secret>
-- 3. The JWT secret should match the one configured in WorkOS AuthKit
-- 
-- In Supabase dashboard:
-- - Go to Project Settings > API
-- - Set "JWT Secret" to your WorkOS JWT secret
-- - Or use: supabase secrets set SUPABASE_JWT_SECRET=<workos_jwt_secret>
