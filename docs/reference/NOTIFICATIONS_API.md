# Notifications API

**Purpose:** In-app notifications for the current user (list, mark as read). Served by the **Python** backend; reachable via the gateway at `/api/v1/notifications`.

---

## Gateway routing

- **URL:** `GET/POST http://localhost:4000/api/v1/notifications/...` (via Caddy :4000)
- **Backend:** Python (port 8000). Caddy routes `/api/v1/notifications` and `/api/v1/notifications/*` to Python; all other `/api/v1/*` goes to Go.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/notifications/` | List notifications for the authenticated user (JWT `Authorization: Bearer <token>`). Returns `[]` if the `notifications` table does not exist. |
| POST | `/api/v1/notifications/{id}/read` | Mark one notification as read. |
| POST | `/api/v1/notifications/read-all` | Mark all notifications for the user as read. |

---

## Auth

- All endpoints require `Authorization: Bearer <token>` (WorkOS JWT or dev token). User ID is taken from `claims["sub"]`.

---

## Response shape (list)

Each notification object:

- `id`: string (UUID)
- `type`: `"info"` \| `"success"` \| `"warning"` \| `"error"`
- `title`: string
- `message`: string
- `link`: string \| null
- `read_at`: ISO 8601 string \| null
- `created_at`: ISO 8601 string

---

## Database

- **Table:** `notifications` (PostgreSQL)
- **Migration:** `alembic/versions/029_add_notifications.py` — run `uv run alembic upgrade head` (or `./scripts/run_python_migrations.sh`) so the table exists.
- **RLS:** Row-level security so users only see/update their own rows (`user_id` from JWT).

---

## Frontend

- **Hook:** `frontend/apps/web/src/hooks/useNotifications.ts` — fetches list, `markAsRead(id)`, `markAllRead()`. Uses `VITE_API_URL` (gateway :4000). If the backend returns 404 (e.g. old gateway config), the hook treats it as an empty list.
