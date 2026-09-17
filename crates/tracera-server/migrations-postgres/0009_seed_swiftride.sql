-- 0009_seed_swiftride.sql (Postgres)
--
-- Seeds the "SwiftRide" project (referenced by the frontend e2e suite:
-- `frontend/apps/web/e2e/dashboard-live-data.spec.ts`) with a real problem
-- dataset. The e2e spec describes "5,686 items", so this migration generates
-- 5,686 problems owned by `project_id='SwiftRide'` using `generate_series`.
--
-- Column contract mirrors `migrations-postgres/0006_create_problems.sql` +
-- `0008_problems_project_id.sql` (the schema actually applied by PgStore):
--   id, title, description, severity, status, assignee_id, related_ids,
--   created_at, updated_at, project_id, deleted_at
--
-- Guarded so it is a no-op if SwiftRide data is already present (idempotent).

INSERT INTO problems (
    id, title, description, severity, status, assignee_id, related_ids,
    created_at, updated_at, project_id, deleted_at
)
SELECT
    'swiftride-' || g,
    CASE (g % 5)
        WHEN 0 THEN 'Driver onboarding flow stalls on empty queue'
        WHEN 1 THEN 'Fare estimate drifts from final charge'
        WHEN 2 THEN 'Rider map fails to render on cold start'
        WHEN 3 THEN 'Surge pricing does not persist to checkout'
        ELSE 'Trip history pagination skips records'
    END,
    'Auto-seeded SwiftRide problem #' || g,
    CASE (g % 4)
        WHEN 0 THEN 'high'
        WHEN 1 THEN 'medium'
        WHEN 2 THEN 'low'
        ELSE 'critical'
    END,
    CASE (g % 4)
        WHEN 0 THEN 'open'
        WHEN 1 THEN 'in_progress'
        WHEN 2 THEN 'resolved'
        ELSE 'closed'
    END,
    NULL,
    '[]'::jsonb,
    now() - (g * interval '1 minute'),
    now() - (g * interval '1 minute'),
    'SwiftRide',
    NULL
FROM generate_series(1, 5686) AS g
WHERE NOT EXISTS (
    SELECT 1 FROM problems WHERE project_id = 'SwiftRide' LIMIT 1
);