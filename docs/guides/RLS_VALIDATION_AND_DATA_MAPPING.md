# RLS Validation and Data Mapping Guide

This guide explains how to **validate Row Level Security (RLS) policies** and **map existing data to your account** using `psql` and the project SQL scripts.

## Prerequisites

- PostgreSQL database (RLS is used only with PostgreSQL).
- Your **user id** = JWT `sub` claim from your auth provider (WorkOS/auth).
- Optional: an existing **account id** (UUID), or a new UUID to create an account.

## Quick reference

| Task | Command |
|------|--------|
| List RLS status and policies, show data summary | `psql $DATABASE_URL -f scripts/rls_validate_and_map.sql` |
| Check row visibility for a user | `psql $DATABASE_URL -v rls_user_id='YOUR_JWT_SUB' -f scripts/rls_validate_as_user.sql` |
| Map all orphan projects to your account | `psql $DATABASE_URL -v map_user_id='YOUR_JWT_SUB' -v map_account_id='acct_uuid' -f scripts/rls_map_data_to_account.sql` |

## 1. Validate RLS policies

Run the main validation script to see:

- Which tables have RLS enabled (`account_users`, `accounts`, `projects`, `items`, `links`, `notifications`).
- The exact policy names and expressions (USING / WITH CHECK).
- A summary of accounts, account members, and projects (with/without `account_id`).

```bash
psql "$DATABASE_URL" -f scripts/rls_validate_and_map.sql
```

## 2. Validate RLS as a specific user

To confirm that a given user only sees rows allowed by RLS, set `app.current_user_id` and run counts and a sample query:

```bash
psql "$DATABASE_URL" -v rls_user_id='YOUR_JWT_SUB' -f scripts/rls_validate_as_user.sql
```

Replace `YOUR_JWT_SUB` with your auth subject (e.g. `user_01abc`). The script sets the session variable and then queries each RLS table; you should only see counts/rows the policies allow for that user.

## 3. Map data to your account

To attach **all projects that currently have no account** to an account you own, and ensure you are a member of that account:

1. Choose or create an account id (e.g. a new UUID).
2. Run the mapping script with a role that can bypass RLS (e.g. `postgres` or your migration user):

```bash
psql "$DATABASE_URL" -v map_user_id='YOUR_JWT_SUB' -v map_account_id='YOUR_ACCOUNT_UUID' -f scripts/rls_map_data_to_account.sql
```

This will:

- Insert or update an **account** row for `map_account_id` (name/slug created if new).
- Insert an **account_users** row so `map_user_id` is an `owner` of that account (if not already).
- Set **projects.account_id** to `map_account_id` for every project where `account_id` is NULL.

Items and links are tied to projects; they do not have their own `account_id`. Once projects are under your account, RLS makes items and links visible to you through the existing policies.

## RLS policy summary

| Table | Scoping | Notes |
|-------|--------|--------|
| `account_users` | User sees rows for accounts they belong to; can insert self or into their accounts. | SELECT/INSERT/UPDATE/DELETE policies. |
| `accounts` | User sees accounts they are a member of; can create account (bootstrap). | INSERT allowed when `app.current_user_id` set. |
| `projects` | User sees projects whose `account_id` is in their accounts. | FOR ALL. |
| `items` | User sees items in visible projects. | Via `project_id` → projects → account. |
| `links` | User sees links in visible projects. | Via `project_id` → projects → account. |
| `notifications` | User sees notifications where `user_id` = `app.current_user_id`. | SELECT/UPDATE/DELETE/INSERT by user. |

RLS context is set in the app by `get_mcp_session()`: it runs `set_config('app.current_user_id', user_id, false)` for PostgreSQL when the user is authenticated.

## Troubleshooting

- **No rows visible**: Ensure `app.current_user_id` is set and that your user is in `account_users` for the account that owns the projects.
- **Mapping script fails (permission)**: Run it as a superuser or the table owner (e.g. migration user) so RLS can be bypassed for the UPDATE/INSERT.
- **Duplicate key on account**: Use an existing `account_id` or a new UUID; the script uses `ON CONFLICT (id) DO UPDATE` for accounts and `ON CONFLICT (account_id, user_id) DO NOTHING` for account_users.
