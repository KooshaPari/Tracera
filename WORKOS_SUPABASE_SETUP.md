# WorkOS + Supabase Authentication Setup

## Overview

This project uses **WorkOS AuthKit** for authentication, with Supabase as the database backend. Supabase's auth schema is **completely unused** - we only use WorkOS JWTs and store user data in `public.profiles` table.

## Key Points

1. **No Supabase Auth**: The `auth.users` table is unused
2. **WorkOS Only**: All authentication is handled by WorkOS AuthKit
3. **Text IDs**: WorkOS user IDs and org IDs are stored as TEXT (not UUIDs)
4. **JWT Mapping**: Supabase accepts WorkOS JWTs via JWT secret configuration

## Database Schema

The `profiles` table uses WorkOS identifiers as primary keys:

```sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY,
    workos_user_id TEXT NOT NULL UNIQUE,  -- Primary identifier from WorkOS
    workos_org_id TEXT,                    -- Organization ID from WorkOS
    workos_ids JSONB DEFAULT '{}',        -- Additional WorkOS metadata
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255),
    -- ... other fields
    auth_id UUID  -- Unused, kept for compatibility
);
```

## Migration Files

1. **20250131000000_fix_workos_profiles.sql**
   - Updates profiles table to use `workos_user_id` and `workos_org_id` as TEXT
   - Removes dependency on `auth_id` UUID
   - Updates `handle_workos_auth()` function to use WorkOS IDs directly

2. **20250131000001_configure_workos_jwt.sql**
   - Configures RLS policies for WorkOS-based access
   - Creates helper functions to extract WorkOS user/org IDs from JWT claims
   - Sets up security policies

## Backend Integration

The `AuthKitAdapter` in `backend/internal/auth/authkit_adapter.go`:
- Validates WorkOS JWT tokens
- Calls `handle_workos_auth()` to create/update profiles
- Uses `workos_user_id` as the primary identifier (not UUID)

## Supabase JWT Configuration

To configure Supabase to accept WorkOS JWTs:

### Option 1: Supabase Dashboard
1. Go to **Project Settings > API**
2. Set **JWT Secret** to your WorkOS JWT secret
3. The secret should match `AUTHKIT_JWT_SECRET` in your backend

### Option 2: Environment Variable
```bash
# In Supabase dashboard or via CLI
supabase secrets set SUPABASE_JWT_SECRET=<your_workos_jwt_secret>
```

### Option 3: Local Development
If using local Supabase:
```bash
# In .env or supabase/.env
SUPABASE_JWT_SECRET=<your_workos_jwt_secret>
```

## Environment Variables

### Backend (.env)
```bash
AUTH_PROVIDER=authkit
AUTHKIT_JWT_SECRET=<workos_jwt_secret>  # From WorkOS dashboard
WORKOS_CLIENT_ID=<workos_client_id>
WORKOS_API_KEY=<workos_api_key>
```

### Supabase
```bash
SUPABASE_JWT_SECRET=<workos_jwt_secret>  # Same as AUTHKIT_JWT_SECRET
```

## How It Works

1. **User logs in via WorkOS AuthKit** (frontend)
2. **WorkOS issues JWT token** with claims:
   - `sub`: WorkOS user ID
   - `org_id`: WorkOS organization ID
   - `email`: User email
   - `name`: User name
3. **Frontend sends JWT** to backend API in `Authorization: Bearer <token>` header
4. **Backend validates JWT** using WorkOS secret
5. **Backend calls `handle_workos_auth()`** to sync profile to `public.profiles`
6. **Profile is created/updated** with WorkOS IDs as TEXT fields

## Mapping Function

The `handle_workos_auth()` function:
- Takes WorkOS user ID, org ID, email, and name
- Creates or updates profile in `public.profiles`
- Uses `workos_user_id` as the unique identifier (ON CONFLICT)
- Returns profile data with WorkOS IDs

## RLS Policies

Row Level Security is configured to:
- Allow users to read/update their own profile (by `workos_user_id`)
- Allow service role to manage all profiles (for backend operations)

## Testing

To test the setup:

1. **Login via WorkOS AuthKit** in the frontend
2. **Check `public.profiles` table** - should see user with `workos_user_id` populated
3. **Verify JWT validation** - backend should accept WorkOS tokens
4. **Test RLS policies** - users should only see their own profile

## Troubleshooting

### Issue: "JWT validation failed"
- Check that `SUPABASE_JWT_SECRET` matches `AUTHKIT_JWT_SECRET`
- Verify WorkOS JWT secret is correct in WorkOS dashboard

### Issue: "Profile not created"
- Check `handle_workos_auth()` function exists and is callable
- Verify database migrations have run
- Check backend logs for SQL errors

### Issue: "RLS policy blocking access"
- Verify `get_workos_user_id()` function works correctly
- Check JWT claims contain `sub` field with WorkOS user ID
- Ensure service role is used for backend operations

## Port Configuration

- **Web App**: `http://localhost:3000` (vite dev server)
- **Storybook**: `http://localhost:6006` (storybook dev server)
- **Backend API**: `http://localhost:8000`

Make sure you're accessing the correct port for the web app, not Storybook!
